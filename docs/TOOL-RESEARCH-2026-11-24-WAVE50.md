# Wave 50 — media and academic discovery

Date: 2026-11-24
Status: merged into main and deployed to production.
Branch: feat/wave-50-media-academic-discovery (merged)
Base main commit: 3244da33d64d2ca366bced502d4ce6b3af8e918b
Squash merge commit: 5e423c98cc1c5a28aae558468c03d6f375e07bf4

## Production verification — 2026-11-24

- [PR #106](https://github.com/Nolane-x/Nolane-search/pull/106) merged to `main` as `5e423c98cc1c5a28aae558468c03d6f375e07bf4`.
- PR CI [45382180134](https://github.com/Nolane-x/Nolane-search/actions/runs/45382180134) and main CI [45382454398](https://github.com/Nolane-x/Nolane-search/actions/runs/45382454398) succeeded. Main CI passed TypeScript, 29 Vitest files / 303 tests, deployment-script checks, 449 Python runner tests and Worker build.
- Cloudflare deployment [45382454250](https://github.com/Nolane-x/Nolane-search/actions/runs/45382454250) succeeded. Worker Version ID: `366f58b7-abb7-4ce4-9857-5997e48b2a66`; runtime secrets uploaded, triggers deployed, Telegram webhook and command menu registered.
- Worker export/build and public health smoke [45382454329](https://github.com/Nolane-x/Nolane-search/actions/runs/45382454329) succeeded.
- No D1 migration was required. Existing 534 file processors were not changed.
- Real Telegram/Web Chat feature acceptance remains a separate owner-level check; mocked provider tests and health smoke do not establish live success for every provider.

Scope: five directly model-callable discovery functions. The 534 file processors and the D1 schema are unchanged. These features return compact metadata and authoritative source/store links; they do not stream, download, reproduce or redistribute copyrighted media or research papers.

## New functions

| Function | Purpose | Data source |
| --- | --- | --- |
| search_tv_shows | Search television series metadata: title, language, genres, original dates, schedule, rating, network/channel, short cleaned synopsis and source link | [TVmaze public API](https://www.tvmaze.com/api) |
| get_tv_show_episodes | Retrieve episode-guide metadata by the TVmaze numeric show ID; optional season filter and specials | [TVmaze public API](https://www.tvmaze.com/api) |
| search_apple_media | Search Apple storefront metadata for movies, TV shows, podcasts, music, music videos, audiobooks, short films and ebooks; country defaults to VN | [Apple iTunes Search API](https://performance-partners.apple.com/search-api) |
| search_music_metadata | Search artist, recording and release-group identifiers/credits | [MusicBrainz Web Service](https://musicbrainz.org/doc/MusicBrainz_API) |
| search_scholarly_works | Search scholarly bibliographic metadata with optional publication-year bounds, DOI, authors, journal and publisher | [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) |

## Provider obligations and limits

### TVmaze
- The public API describes a limit of at least 20 calls per 10 seconds per IP and asks clients to back off after HTTP 429.
- Data is licensed under CC BY-SA. Results keep the TVmaze page/source link and attribution in the response.
- TVmaze is a metadata catalog, not a territorial streaming-availability service. A network or channel label does not confirm that a show can be watched in a user's country or subscription.
- The implementation uses a 600 ms per-warm-isolate throttle and bounded response parsing. This is not a globally coordinated per-IP quota.

Official source: https://www.tvmaze.com/api

### Apple iTunes Search API
- Apple documents approximately 20 search calls per minute (subject to change) and recommends limiting result count and caching.
- The implementation waits at least 3.1 seconds between calls per warm Worker isolate. This is deliberately conservative but is not a global limiter across Worker isolates.
- Search is country/storefront scoped (default VN) and incomplete as a global catalog.
- Apple promotional artwork and previews have restrictions: previews and promotional assets may only be used to promote store content, and audio samples/assets must be proximate to a store badge. To avoid ambiguous reuse, this tool returns text metadata and official store links only; no artwork or audio-preview URLs are surfaced.
- A store link does not prove current availability, subscription eligibility or regional playback rights.

Official source: https://performance-partners.apple.com/search-api

### MusicBrainz
- No API key is required for public searches, but a meaningful User-Agent is required.
- The service asks each application to make no more than one call per second; the source IP is also throttled at an average of one request per second.
- The implementation waits 1.1 seconds between calls per warm Worker isolate. Cloudflare isolates do not share this in-memory clock, so this does not guarantee a global source-IP quota.
- MusicBrainz core data is CC0; supplementary data can have separate CC BY-NC-SA terms. MusicBrainz says non-commercial use of its web service is free; commercial use requires a separate plan/license. No audio recording is returned.

Official sources:
- https://musicbrainz.org/doc/MusicBrainz_API
- https://musicbrainz.org/doc/MusicBrainz_API/Rate_Limiting
- https://musicbrainz.org/doc/About/Data_License

### Crossref
- The public REST API requires no signup or API key. For public query/list searches, Crossref currently documents one request per second; requests can return 429 when limits are exceeded.
- The implementation waits 1.1 seconds per warm Worker isolate, uses a meaningful User-Agent and requests a small result page. This is not a global cross-isolate limiter. No contact email was invented for a mailto parameter.
- Records are publisher/depositor metadata and may be incomplete. Citation counts are not research-quality scores. A DOI can lead to a paywall or a page without full text.
- The tool returns bibliographic fields only, not abstract/body text and not an open-access guarantee.

Official sources:
- https://www.crossref.org/documentation/retrieve-metadata/rest-api/access-and-authentication/
- https://www.crossref.org/blog/announcing-changes-to-rest-api-rate-limits/

## Safety and implementation choices

- All provider requests use fixed HTTPS origins, GET, redirect rejection, a 12-second timeout and a 500 KB JSON response cap via the existing shared helper.
- Search text and enum values are bounded/validated before network requests.
- Result URLs are constructed from fixed provider origins or filtered against explicit official host allow-lists.
- TVmaze HTML summaries are stripped to plain text and length-bounded.
- No API keys, new dependencies, D1 migrations, scraping, media downloads, audio previews, artwork downloads, or article full-text downloads are added.
- Provider throttles are in-memory per warm Worker isolate, not globally distributed. If actual multi-isolate usage grows, replace these with a shared rate limiter/cache before expanding throughput.

## Validation plan

- Unit tests mock each upstream API and assert hostname, endpoint, request parameters, response shaping, URL allow-lists, attribution/limitations and invalid-input rejection.
- Integration tests assert all five functions are registered with the model and that the actual dispatcher routes requests.
- Before merge: type-check, all Vitest suites, deployment-script checks, Python runner tests and Worker build must pass.
- After merge: main CI, Cloudflare deployment, Worker export and public health smoke must pass.
- Real Telegram/Web Chat feature acceptance remains distinct from mocked upstream tests and Worker health; verify one example per source after deployment.
