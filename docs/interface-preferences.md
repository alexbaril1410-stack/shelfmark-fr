# Interface Preferences

## Display language

Choose **English** or **Français** from the account menu in the header. The choice is saved in the current browser and applies on the next visit. The French dictionary covers common navigation, search, and release-filter labels; provider supplied titles and metadata remain in their original language.

## Zero-seeder search results

In the release results filter menu, enable **Show results with 0 seeders** to include torrents with a reported seeder count of zero. It is enabled by default, which preserves the existing search behavior. When disabled, only releases whose seeder count is explicitly `0` are hidden; releases without a reported count remain visible. This choice is saved in the current browser.

## Audible.fr metadata

An optional Audible.fr provider is available for audiobook catalog searches. Enable **Audible.fr** in Settings → Metadata Providers, then select it as the audiobook metadata provider in Search Mode settings. It uses the catalog endpoint referenced by the supplied Audible API 0.6.4 tag-source archive; the endpoint is undocumented and may change. Searches are user initiated, limited to the API's 50-result page size, rate limited, and cached. Shelfmark does not crawl categories or enumerate the catalog, and each result links back to its Audible.fr product page. No Audible account credentials are requested or stored. The separate [`audible.cr` project](https://github.com/omarroth/audible.cr) is a client for Audible's internal authenticated API and is not required for this catalog lookup.

This integration is experimental. Use it in accordance with Audible's [Conditions of Use](https://www.audible.fr/legal/conditions-of-use); Audible does not publish a supported catalog API contract.

