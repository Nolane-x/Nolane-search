# Wave 49 — learning, art and world discovery

Date: 2026-11-24
Status: merged and deployed to production on 2026-11-24.
Pull request: https://github.com/Nolane-x/Nolane-search/pull/104
Merge commit: 56793e4b01ce985b90c4f78f3ec1e4c7269cdc9
Scope: five directly model-callable functions aimed at everyday learning and discovery. Existing 534 file processors remain unchanged.

## Why this wave

Wave 47–48 added weather, air quality, exchange rates, holidays, marine conditions, earthquake catalog data, books and postcodes. Wave 49 intentionally moves into other everyday interests: English vocabulary, public-domain reading, museum art, global natural-event browsing and local clock times.

## Provider and upstream project review

| Project / provider | What was reviewed | Decision |
|---|---|---|
| https://github.com/meetDeveloper/freeDictionaryAPI | Current README, v2 single-word endpoint, phonetics, definitions/examples/synonyms and maintainer warning about running costs and 10M+ requests/month. | Use only on-demand single-word lookups, one request/second per warm isolate, bound output and never scrape/export dictionary contents. Upstream availability is not guaranteed. |
| https://github.com/garethbjohnson/gutendex | README, metadata model, search/language/topic/copyright filters and 32-record page response. | Use Gutendex's independent catalog API. Return only records with `copyright=false` (U.S. public-domain flag) and only a Gutenberg landing-page link; do not download books. |
| https://github.com/art-institute-of-chicago/api-data | Official API docs, anonymous 60 requests/minute limit, AIC-User-Agent guidance, public-domain search filtering, CC0 metadata and IIIF image URL pattern. | Search only museum records where `is_public_domain=true` and a valid image ID exists; use small pages and per-isolate self-throttling. |
| https://eonet.gsfc.nasa.gov/docs/v3 | NASA EONET v3 API docs: events, category/status/days/limit filters and GeoJSON geometry. | Read curated natural-event metadata only; not alerts, warning systems or exhaustive sensor observations. |
| Open-Meteo Geocoding API | Existing Wave 47–48 integration and geocoding response time_zone field. | Reuse location resolution; calculate local time in Worker with the returned IANA time zone and current UTC clock. |

## Functions

| Function | User outcome | Provider |
|---|---|---|
| define_english_word | English phonetics, pronunciation links, meanings, examples, synonyms and antonyms | Free Dictionary API |
| search_public_domain_books | Filtered search for classic/free titles, language and subject, with author and download-count metadata | Gutendex / Project Gutenberg catalog |
| search_museum_artworks | Discover Art Institute artworks that are explicitly marked public domain and have an image | Art Institute of Chicago |
| get_natural_events | Recent curated NASA natural-event records filtered by category, status and days | NASA EONET v3 |
| get_local_time | Current local date, time, weekday, UTC offset and IANA time zone for a named city | Open-Meteo geocoding + Worker clock |

## Safety and data limits

- Every API uses a fixed HTTPS host, 12-second timeout, redirect rejection and the shared 500 KB decoded JSON response cap.
- Free Dictionary is an English-only community API; its maintainer notes substantial hosting costs. Calls are human-triggered, one word at a time and self-throttled; no bulk dictionary ingestion.
- Gutendex's `copyright=false` denotes U.S. public-domain status. It does not establish public-domain status in Vietnam or any other country. The function returns catalog metadata and a human landing-page link only; it never downloads or redistributes the text.
- Art Institute searches send `AIC-User-Agent`, cap result counts at eight, and filter `is_public_domain=true` before returning an image URL. The museum's per-object copyright notice and terms still govern reuse.
- NASA EONET is curated metadata; event locations can be approximate/delayed. It is not an emergency alert or official hazard warning.
- Local time is computed from the current server clock and geocoder-supplied IANA time zone. It is not business opening-hours data.
- No API key, paid service, new dependency, D1 migration, data dump, scraper or copied upstream code/assets are introduced.

## Validation plan

Mocked API tests cover word definition/404 handling, trusted audio URL filtering, public-domain-only book results, museum public-domain filtering and IIIF URLs, NASA category/status parsing and event locations, local time-zone conversion, invalid-input rejection and AI tool dispatch. CI must pass type-check, all Vitest tests, deployment scripts, Python runner tests and Worker build before merge.


## Production verification

- PR #104 merged on 2026-11-24.
- PR CI: https://github.com/Nolane-x/Nolane-search/actions/runs/45343427454 — passed TypeScript, Vitest, deployment scripts, Python runner tests and Worker build.
- Main CI: https://github.com/Nolane-x/Nolane-search/actions/runs/45343582511 — passed the full same pipeline on the merge commit.
- Cloudflare deployment: https://github.com/Nolane-x/Nolane-search/actions/runs/45343582467 — passed required-secret checks, source verification, production bundle validation, Worker/runtime-secret upload and Telegram webhook/command registration.
- Worker export and smoke test: https://github.com/Nolane-x/Nolane-search/actions/runs/45343582462 — passed build/export and public `/health` smoke test.
- No D1 migration was required. The visible deployment summary did not expose a Worker version ID.
- Feature-level real Telegram/Web Chat acceptance is still recommended; successful mocked tests and public health checks are not evidence that every upstream API is reachable from every user request.
