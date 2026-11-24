# Wave 57 research — anime and manga discovery

Date: 2026-11-24
Repository: https://github.com/Nolane-x/Nolane-search
Branch: feat/wave-57-anime-manga-discovery

## Product intent

Add a recognizable entertainment category for ordinary users: find anime and manga by title, compare scores/status/type, see episode/chapter counts and authors/studios, then open the original catalog page. This is catalog discovery, not a video streaming, reading or download service.

## Provider

Jikan API v4: https://jikan.moe/
API base: https://api.jikan.moe/v4
Official REST/OpenAPI specification: https://github.com/jikan-me/jikan-rest/blob/master/storage/api-docs/api-docs.json
Source project route definitions: https://github.com/jikan-me/jikan-rest/blob/master/routes/web.v4.php

Jikan describes itself as an unofficial, open-source API for MyAnimeList and says it scrapes public MyAnimeList pages. Its public API exposes anime and manga search endpoints and full item details endpoints. The API data therefore depends on Jikan's parser and MyAnimeList's public catalog; it is not an official MyAnimeList API or a live streaming-rights provider.

## New AI-callable tools

Anime:
- `search_anime_titles` — title search, optional type filter (TV, OVA, Movie, Special, ONA, Music, CM, PV, TV Special), small bounded result count.
- `get_anime_details` — full SFW details by a numeric MyAnimeList anime ID returned from search.

Manga:
- `search_manga_titles` — title search, optional type filter (manga, novel, lightnovel, oneshot, doujin, manhwa, manhua).
- `get_manga_details` — full SFW details by numeric MyAnimeList manga ID.

All list searches send `sfw=true` to the documented Jikan API to filter adult entries. The integration does not expose an option to disable that protection.

## Returned data

Anime search/detail:
- MAL ID, primary/English/Japanese title, original catalog link and cover image.
- Format, airing status, episode count, duration, audience rating, score/rank/popularity and synopsis.
- Season/year, date range, studios, genres, themes and demographic labels when present.

Manga search/detail:
- MAL ID, primary/English/Japanese title, original catalog link and cover image.
- Type, publication status, chapter/volume counts, score/rank/popularity and synopsis.
- Publication date range, authors, serialization magazines, genres, themes and demographic labels when present.

Data normalization bounds text and list lengths, drops malformed entries, validates numeric IDs and links, accepts MyAnimeList pages only from `myanimelist.net` and cover images only from `cdn.myanimelist.net`.

## Reliability and boundaries

- Fixed HTTPS API origin: `api.jikan.moe`; no user-controlled URL or path.
- Descriptive User-Agent, 12-second timeout, redirect rejection and bounded JSON response bodies.
- One request per tool call, small page/result caps, no retry loop. HTTP 429 is reported as a back-off response; 503/504 are surfaced as upstream availability errors.
- SFW filtering is always enabled.
- Jikan is unofficial and can lag, fail when its MyAnimeList source is unavailable or return incomplete records. Scores and status can change; verify important details on the linked MyAnimeList entry.
- The integration does not provide streaming links, scanlation links, episode downloads, torrent links or access-control bypasses.
- No user API key, new dependency, D1 migration, Cloudflare binding or change to the 534 file-processor catalog.

## Validation

Mocked tests cover anime/manga search, format filters, SFW parameter, score/cover/title normalization, full details, authors/studios/chapters/episodes, invalid IDs/types, HTTP 429, malformed entries and AI function registration/dispatch. CI verifies type-check, Vitest, deployment scripts, Python tool runner and Cloudflare Worker build. Live query availability remains separate from mocked tests.

## Sources
- Jikan project and provider description: https://jikan.moe/
- Jikan API v4 OpenAPI spec: https://github.com/jikan-me/jikan-rest/blob/master/storage/api-docs/api-docs.json
- Jikan route map: https://github.com/jikan-me/jikan-rest/blob/master/routes/web.v4.php
