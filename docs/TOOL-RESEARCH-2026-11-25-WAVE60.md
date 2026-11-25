# Wave 60 research — Steam game discovery

Date: 2026-11-25
Repository: https://github.com/Nolane-x/Nolane-search

## Product intent

Add practical game discovery for ordinary users rather than another developer-only processor. The two tools search the Steam Store and retrieve public details using a selected regional storefront. They do not download games, play games, bypass age gates or claim that a title is available on every account or region.

## Sources reviewed

- Steam Store search endpoint: https://store.steampowered.com/api/storesearch/
- Steam Store app details endpoint: https://store.steampowered.com/api/appdetails
- Steamworks API overview: https://partner.steamgames.com/doc/webapi/overview
- Steam User Reviews Service: https://partner.steamgames.com/doc/webapi/IUserReviewsService?l=english

The store search and app-details endpoints are public web-store endpoints used without a Steam API key. Their response shape is not presented here as a stable, formally versioned partner API contract; upstream changes or anti-automation/rate limiting may affect results. We request only a small bounded response and do not crawl the Steam catalogue.

## Implemented tools

### `search_steam_games`

- Search terms are normalized and constrained to 2–100 printable characters.
- Limit is 1–10 (default 8).
- Country is a two-letter storefront code (default VN); language is chosen from a finite allowlist (default Vietnamese).
- Results include Steam app ID, title, item type, regional formatted price/currency, discount percentage, Metacritic score when supplied, a safe thumbnail URL and a canonical Steam Store link.
- Store search may return non-game catalogue items such as DLC or soundtracks. The tool returns the source-provided type instead of silently relabelling them as games.

### `get_steam_game_details`

- Accepts a numeric app ID (1–2,147,483,647), country and language.
- Returns public description, developers, publishers, genres, categories, release date, platforms, regional price, Metacritic score, recommendation count, age requirement, supported-language text, header image, bounded screenshots and canonical Store link.
- Image URLs are retained only from a small HTTPS Steam static-asset host allowlist.
- Missing values remain null/empty rather than being invented. Age-restricted or unavailable records may return no public details.

## Reliability and safety

- Requests go only to fixed Steam HTTPS API origins; user-provided URLs are not fetched.
- Redirects are rejected, requests have a 12-second timeout and a descriptive User-Agent.
- Response bodies are bounded (350 KiB for search; 800 KiB for details).
- HTTP 429 is surfaced as a back-off response; there is no retry loop.
- Store links are constructed from validated numeric IDs rather than trusting external URLs returned in a record.
- Store image URLs require HTTPS, exact approved Steam static-asset hosts, no credentials and no nonstandard port.
- Regional pricing and catalogue availability can change; the linked Steam page is the final source of truth.
- The tools do not provide reviews or a recommendation score. Steam's User Reviews Service is a different endpoint and was not mixed with the older appreviews route; use its current documentation if reviews are added later.

## Verification boundary

Tests stub Steam responses and verify parsing, country/language parameters, bounds, safe image handling, input validation, rate-limit handling and AI-tool dispatch. Passing tests do not prove live Steam availability, catalogue completeness or pricing freshness. A separate connected-runtime smoke test is required before claiming live-provider verification.
