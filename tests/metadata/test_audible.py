import requests

from shelfmark.core.cache import get_metadata_cache
from shelfmark.metadata_providers import MetadataSearchOptions, SearchType, get_provider
from shelfmark.metadata_providers.audible import AudibleProvider


ASIN = "B012345678"


def _product(**updates):
    product = {
        "asin": ASIN,
        "title": "Le Petit Prince (Narrated by Camille Example)",
        "subtitle": "Édition intégrale",
        "authors": [{"asin": "A012345678", "name": "Antoine de Saint-Exupéry"}],
        "narrators": [{"name": "Camille Example"}],
        "isbn": "9782070612758",
        "release_date": "2018-04-18",
        "language": "French",
        "publisher_name": "Gallimard Audio",
        "publisher_summary": "Une histoire de voyage.",
        "product_images": {
            "100": "https://m.media-amazon.com/images/I/example.jpg",
        },
        "runtime_length_min": 98,
        "rating": {"overall_distribution": {"display_average_rating": "4.7"}},
        "series": [{"title": "Les classiques", "sequence": "2"}],
        "category_ladders": [{"ladder": [{"name": "Littérature"}, {"name": "Classiques"}]}],
    }
    product.update(updates)
    return product


class _Response:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class _Session:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if isinstance(self.payload, Exception):
            raise self.payload
        return _Response(self.payload)


def _allow_requests(monkeypatch):
    from shelfmark.metadata_providers import audible

    monkeypatch.setattr(audible, "get_proxies", lambda _url: None)
    monkeypatch.setattr(audible, "get_ssl_verify", lambda _url: True)


def test_audible_provider_is_registered_and_opt_in_without_account_credentials():
    provider = get_provider("audible")

    assert isinstance(provider, AudibleProvider)
    assert provider.is_available() is True
    assert provider.requires_auth is False


def test_parse_product_maps_french_audiobook_metadata():
    book = AudibleProvider._parse_product(_product())

    assert book is not None
    assert book.provider == "audible"
    assert book.provider_id == ASIN
    assert book.title == "Le Petit Prince"
    assert book.subtitle == "Édition intégrale"
    assert book.authors == ["Antoine de Saint-Exupéry"]
    assert book.isbn_13 == "9782070612758"
    assert book.language == "fr"
    assert book.publish_year == 2018
    assert book.publisher == "Gallimard Audio"
    assert book.cover_url == "https://m.media-amazon.com/images/I/example.jpg"
    assert book.source_url == f"https://www.audible.fr/pd/{ASIN}"
    assert book.series_name == "Les classiques"
    assert book.series_position == 2
    assert [field.label for field in book.display_fields] == ["Rating", "Narrator", "Length"]


def test_search_uses_capped_paged_catalog_query_and_maps_results(monkeypatch):
    _allow_requests(monkeypatch)
    get_metadata_cache().clear()
    provider = AudibleProvider()
    session = _Session({"total_results": 120, "products": [_product()]})
    provider.session = session

    result = provider.search_paginated(
        MetadataSearchOptions(
            query="Le Petit Prince",
            search_type=SearchType.TITLE,
            limit=80,
            page=2,
            language="fr",
        )
    )

    assert len(result.books) == 1
    assert result.total_found == 120
    assert result.has_more is True
    assert result.books[0].provider_id == ASIN
    url, kwargs = session.calls[0]
    assert url == "https://api.audible.fr/1.0/catalog/products"
    assert kwargs["params"]["title"] == "Le Petit Prince"
    assert kwargs["params"]["num_results"] == 50
    assert kwargs["params"]["page"] == 2
    assert kwargs["params"]["language"] == "fr"
    assert kwargs["timeout"] == 15


def test_get_book_rejects_invalid_asin_without_network_request():
    provider = AudibleProvider()
    session = _Session({"product": _product()})
    provider.session = session

    assert provider.get_book("https://example.org/") is None
    assert session.calls == []


def test_isbn_lookup_requires_exact_match(monkeypatch):
    _allow_requests(monkeypatch)
    get_metadata_cache().clear()
    provider = AudibleProvider()
    provider.session = _Session({"products": [_product(isbn="9782070612758")]})

    result = provider.search_by_isbn("978-2-07-061275-8")

    assert result is not None
    assert result.provider_id == ASIN


def test_request_failures_return_empty_search_results(monkeypatch):
    _allow_requests(monkeypatch)
    get_metadata_cache().clear()
    provider = AudibleProvider()
    provider.session = _Session(requests.Timeout("timed out"))

    assert provider.search(MetadataSearchOptions(query="test")) == []

