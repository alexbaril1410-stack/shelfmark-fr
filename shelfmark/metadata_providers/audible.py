"""Audible.fr catalog metadata provider.

Uses the unauthenticated catalog endpoint referenced by the user's Audible API
0.6.4 tag-source archive. Audible does not publish a stable API contract, so
this provider is opt-in, caches searches, limits request volume, and links each
result back to its Audible.fr product page.
"""

import re
import threading
import time
from collections import deque
from contextlib import suppress
from dataclasses import replace
from typing import Any, ClassVar

import requests

from shelfmark.core.cache import cacheable
from shelfmark.core.config import config as app_config
from shelfmark.core.languages import normalize_language
from shelfmark.core.logger import setup_logger
from shelfmark.core.settings_registry import (
    ActionButton,
    CheckboxField,
    HeadingField,
    SettingsField,
    register_settings,
)
from shelfmark.download.network import get_proxies, get_ssl_verify
from shelfmark.metadata_providers import (
    BookMetadata,
    DisplayField,
    MetadataProvider,
    MetadataSearchOptions,
    SearchField,
    SearchResult,
    SearchType,
    SortOrder,
    TextSearchField,
    register_provider,
)

logger = setup_logger(__name__)

AUDIBLE_API_BASE_URL = "https://api.audible.fr/1.0"
AUDIBLE_PRODUCT_BASE_URL = "https://www.audible.fr/pd"
MAX_RESULTS_PER_REQUEST = 50
REQUEST_TIMEOUT_SECONDS = 15
ISBN_DIGITS_RE = re.compile(r"[^0-9Xx]")
NARRATED_TITLE_RE = re.compile(r"\s+\(Narrated by [^)]*\)$", re.IGNORECASE)


class _RequestLimiter:
    """Small process-wide sliding-window guard for the undocumented endpoint."""

    def __init__(self, max_requests: int = 30, window_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.timestamps: deque[float] = deque()
        self.lock = threading.Lock()

    def wait(self) -> None:
        while True:
            with self.lock:
                now = time.monotonic()
                cutoff = now - self.window_seconds
                while self.timestamps and self.timestamps[0] <= cutoff:
                    self.timestamps.popleft()
                if len(self.timestamps) < self.max_requests:
                    self.timestamps.append(now)
                    return
                delay = self.timestamps[0] + self.window_seconds - now
            time.sleep(max(delay, 0.01))


_request_limiter = _RequestLimiter()


class _AudibleRequestError(Exception):
    """Raised internally so transient failures are not cached as empty results."""


def _text(value: object) -> str | None:
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return None


def _people(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    return [name for item in values if isinstance(item, dict) if (name := _text(item.get("name")))]


def _clean_isbn(value: object) -> str:
    return ISBN_DIGITS_RE.sub("", str(value or "")).upper()


def _parse_year(value: object) -> int | None:
    if not isinstance(value, str):
        return None
    with suppress(ValueError):
        year = int(value[:4])
        if 1400 <= year <= 2100:
            return year
    return None


def _category_names(value: object) -> list[str]:
    names: list[str] = []
    if not isinstance(value, list):
        return names
    for category in value:
        if not isinstance(category, dict):
            continue
        ladder = category.get("ladder")
        if isinstance(ladder, list):
            for item in ladder:
                if isinstance(item, dict) and (name := _text(item.get("name"))) and name not in names:
                    names.append(name)
    return names[:8]


def _cover_url(value: object) -> str | None:
    if not isinstance(value, dict):
        return None
    for size in ("2400", "1000", "700", "500", 2400, 1000, 700, 500, "100", 100):
        candidate = _text(value.get(size))
        if candidate and candidate.startswith("https://"):
            return candidate
    return None


def _test_audible_connection() -> dict[str, Any]:
    """Check the catalog endpoint with one small, cached-friendly query."""
    try:
        provider = AudibleProvider()
        data = provider._request(
            "/catalog/products",
            {
                "keywords": "test",
                "num_results": 1,
                "page": 1,
                "products_sort_by": "Relevance",
                "response_groups": "media",
            },
        )
    except _AudibleRequestError:
        return {"success": False, "message": "Audible.fr catalog API is not reachable"}
    if isinstance(data, dict) and isinstance(data.get("products"), list):
        return {"success": True, "message": "Connected to the Audible.fr catalog"}
    return {"success": False, "message": "Audible.fr returned an unexpected catalog response"}


@register_provider("audible")
class AudibleProvider(MetadataProvider):
    """Opt-in metadata lookup against Audible.fr's public catalog endpoint."""

    name = "audible"
    display_name = "Audible.fr"
    requires_auth = False
    supported_sorts: ClassVar[tuple[SortOrder, ...]] = (SortOrder.RELEVANCE,)
    search_fields: ClassVar[tuple[SearchField, ...]] = (
        TextSearchField(key="author", label="Author", description="Search by author name"),
        TextSearchField(key="title", label="Title", description="Search by audiobook title"),
    )

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": "Shelfmark Audible.fr catalog provider (+https://github.com/alexbaril1410-stack/shelfmark-fr)",
            }
        )

    def is_available(self) -> bool:
        """No account credentials are required by the catalog search endpoint."""
        return True

    def search(self, options: MetadataSearchOptions) -> list[BookMetadata]:
        if options.search_type == SearchType.ISBN:
            book = self.search_by_isbn(options.query)
            return [book] if book else []
        return self.search_paginated(options).books

    def search_paginated(self, options: MetadataSearchOptions) -> SearchResult:
        page_size = max(1, min(options.limit, MAX_RESULTS_PER_REQUEST))
        page = max(1, options.page)
        options = replace(options, limit=page_size, page=page)
        fields_key = ":".join(f"{key}={value}" for key, value in sorted(options.fields.items()))
        cache_key = (
            f"{options.query}:{options.search_type.value}:{options.language}:"
            f"{page_size}:{page}:{fields_key}"
        )
        try:
            books, total = self._search_cached(cache_key, options)
        except _AudibleRequestError:
            return SearchResult(books=[], page=page)
        return SearchResult(
            books=books,
            page=page,
            total_found=total,
            has_more=(page * page_size < total) if total else len(books) == page_size,
        )

    @cacheable(
        ttl_key="METADATA_CACHE_SEARCH_TTL",
        ttl_default=900,
        # Bump the key prefix so empty results cached from the old, invalid
        # title/author query parameters are not served after upgrading.
        key_prefix="audible:search:v2",
    )
    def _search_cached(
        self, cache_key: str, options: MetadataSearchOptions
    ) -> tuple[list[BookMetadata], int]:
        params: dict[str, Any] = {
            "num_results": options.limit,
            "page": options.page,
            "response_groups": "contributors,media,product_desc,product_attrs,product_extended_attrs,series",
            "image_sizes": "100",
            "products_sort_by": "Relevance",
        }
        author = _text(options.fields.get("author"))
        title = _text(options.fields.get("title"))
        if author or title:
            query = " ".join(value for value in (author, title) if value)
        elif options.search_type == SearchType.TITLE:
            query = options.query
        elif options.search_type == SearchType.AUTHOR:
            query = options.query
        else:
            query = options.query

        # Audible's catalog endpoint searches through `keywords`; it does not use
        # the title/author parameters exposed by some third-party API clients.
        params["keywords"] = query

        data = self._request("/catalog/products", params)
        products = data.get("products") if isinstance(data, dict) else None
        if not isinstance(products, list):
            raise _AudibleRequestError("Audible returned an invalid product list")
        books = [book for product in products if (book := self._parse_product(product))]
        try:
            total = max(0, int(data.get("total_results", 0)))
        except (TypeError, ValueError):
            total = 0
        return books, total

    def get_book(self, book_id: str) -> BookMetadata | None:
        """Fetch one Audible product by its ASIN."""
        asin = book_id.strip().upper()
        if not re.fullmatch(r"[A-Z0-9]{10}", asin):
            return None
        try:
            return self._get_book_cached(asin)
        except _AudibleRequestError:
            return None

    @cacheable(
        ttl_key="METADATA_CACHE_BOOK_TTL",
        ttl_default=3600,
        key_prefix="audible:book",
    )
    def _get_book_cached(self, asin: str) -> BookMetadata | None:
        """Fetch and cache the product details after validating the ASIN."""
        data = self._request(
            f"/catalog/products/{asin}",
            {
                "response_groups": "category_ladders,contributors,media,product_desc,product_attrs,product_extended_attrs,rating,series,product_details",
                "image_sizes": "2400,1000,700,500",
            },
        )
        product = data.get("product") if isinstance(data, dict) else None
        return self._parse_product(product) if isinstance(product, dict) else None

    def search_by_isbn(self, isbn: str) -> BookMetadata | None:
        clean_isbn = _clean_isbn(isbn)
        if len(clean_isbn) not in (10, 13):
            return None
        try:
            return self._search_by_isbn_cached(clean_isbn)
        except _AudibleRequestError:
            return None

    @cacheable(
        ttl_key="METADATA_CACHE_BOOK_TTL",
        ttl_default=900,
        key_prefix="audible:isbn",
    )
    def _search_by_isbn_cached(self, clean_isbn: str) -> BookMetadata | None:
        data = self._request(
            "/catalog/products",
            {
                "keywords": clean_isbn,
                "num_results": 10,
                "page": 1,
                "response_groups": "contributors,media,product_attrs,product_extended_attrs,series",
                "image_sizes": "700",
            },
        )
        products = data.get("products") if isinstance(data, dict) else None
        if not isinstance(products, list):
            return None
        for product in products:
            book = self._parse_product(product)
            if book and clean_isbn in {_clean_isbn(book.isbn_10), _clean_isbn(book.isbn_13)}:
                return book
        return None

    def _request(self, endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
        url = f"{AUDIBLE_API_BASE_URL}{endpoint}"
        _request_limiter.wait()
        try:
            response = self.session.get(
                url,
                params=params,
                timeout=REQUEST_TIMEOUT_SECONDS,
                proxies=get_proxies(url),
                verify=get_ssl_verify(url),
            )
            response.raise_for_status()
            data = response.json()
        except requests.Timeout as exc:
            logger.warning("Audible.fr catalog request timed out")
            raise _AudibleRequestError from exc
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else "unknown"
            logger.warning("Audible.fr catalog returned HTTP %s", status)
            raise _AudibleRequestError from exc
        except (requests.RequestException, ValueError) as exc:
            logger.warning("Audible.fr catalog request failed: %s", exc)
            raise _AudibleRequestError from exc
        if not isinstance(data, dict):
            raise _AudibleRequestError("Audible returned a non-object JSON response")
        return data

    @staticmethod
    def _parse_product(product: object) -> BookMetadata | None:
        if not isinstance(product, dict):
            return None
        asin = _text(product.get("asin"))
        raw_title = _text(product.get("title"))
        if not asin or not re.fullmatch(r"[A-Z0-9]{10}", asin.upper()) or not raw_title:
            return None

        title = NARRATED_TITLE_RE.sub("", raw_title).strip()
        authors = _people(product.get("authors"))
        narrators = _people(product.get("narrators"))
        isbn = _clean_isbn(product.get("isbn"))
        isbn_10 = isbn if len(isbn) == 10 else None
        isbn_13 = isbn if len(isbn) == 13 else None
        series = product.get("series")
        first_series = series[0] if isinstance(series, list) and series and isinstance(series[0], dict) else {}
        series_name = _text(first_series.get("title"))
        sequence = first_series.get("sequence")
        try:
            series_position = float(sequence) if sequence not in (None, "") else None
        except (TypeError, ValueError):
            series_position = None

        display_fields: list[DisplayField] = []
        rating = product.get("rating")
        if isinstance(rating, dict):
            distribution = rating.get("overall_distribution")
            if isinstance(distribution, dict):
                average = distribution.get("display_average_rating")
                if average not in (None, ""):
                    display_fields.append(
                        DisplayField(label="Rating", value=str(average), icon="star")
                    )
        if narrators:
            display_fields.append(
                DisplayField(label="Narrator", value=", ".join(narrators[:3]), icon="microphone")
            )
        runtime = product.get("runtime_length_min")
        if isinstance(runtime, (int, float)) and runtime > 0:
            hours, minutes = divmod(int(runtime), 60)
            length = f"{hours} h {minutes} min" if hours else f"{minutes} min"
            display_fields.append(DisplayField(label="Length", value=length, icon="clock"))

        return BookMetadata(
            provider="audible",
            provider_id=asin.upper(),
            title=title,
            provider_display_name="Audible.fr",
            authors=authors,
            isbn_10=isbn_10,
            isbn_13=isbn_13,
            cover_url=_cover_url(product.get("product_images")),
            description=_text(product.get("publisher_summary")),
            publisher=_text(product.get("publisher_name")),
            publish_year=_parse_year(product.get("release_date")),
            language=normalize_language(product.get("language")),
            genres=_category_names(product.get("category_ladders")),
            source_url=f"{AUDIBLE_PRODUCT_BASE_URL}/{asin.upper()}",
            subtitle=_text(product.get("subtitle")),
            search_title=title,
            search_author=authors[0] if authors else None,
            display_fields=display_fields,
            series_name=series_name,
            series_position=series_position,
        )


@register_settings("audible", "Audible.fr", icon="library", order=56, group="metadata_providers")
def audible_settings() -> list[SettingsField]:
    """Settings for the optional Audible.fr catalog metadata provider."""
    return [
        HeadingField(
            key="audible_heading",
            title="Audible.fr",
            description=(
                "Audiobook metadata from Audible.fr's catalog search endpoint. This endpoint is "
                "undocumented and may change; only search requests are made, results are cached, "
                "and each item links back to Audible.fr. No Audible account is required."
            ),
            link_url="https://www.audible.fr",
            link_text="audible.fr",
        ),
        CheckboxField(
            key="AUDIBLE_ENABLED",
            label="Enable Audible.fr",
            description="Allow Audible.fr to be selected as a metadata provider for audiobook searches.",
            default=False,
        ),
        ActionButton(
            key="test_connection",
            label="Test Connection",
            description="Check whether the Audible.fr catalog endpoint responds.",
            style="primary",
            callback=_test_audible_connection,
        ),
    ]
