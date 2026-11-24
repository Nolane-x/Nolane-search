# Wave 57 handoff — anime and manga discovery

Date: 2026-11-24
Branch: feat/wave-57-anime-manga-discovery
Base: 1418ef83fa1c76452cc2ed69b61e0f821009c85a
Release status: implementation branch; not yet merged or deployed.

## New AI-callable tools

- `search_anime_titles` — search MyAnimeList-backed anime catalog with SFW filter and optional format filter.
- `get_anime_details` — fetch full anime details by numeric MyAnimeList ID.
- `search_manga_titles` — search manga/novel/manhwa/manhua catalog with SFW filter and optional format filter.
- `get_manga_details` — fetch full manga details by numeric MyAnimeList ID.

## Returned catalog data

- Anime: title variants, cover, episodes, format, airing status, year/season, score/rank, synopsis, studios, genres and original MyAnimeList link.
- Manga: title variants, cover, chapters/volumes, publication status/date, score/rank, synopsis, authors, serialization, genres and original MyAnimeList link.
- Text and result arrays are bounded. MyAnimeList links and cover image hosts are validated.
- SFW filtering is always enabled. No parameter disables it.

## Architecture

- New provider adapter: `src/anime-catalog-tools.ts`.
- New focused tests: `tests/anime-catalog-tools.test.ts`.
- AI schemas/dispatcher: `src/agent-tools.ts`.
- Main exact schema-list assertion: `tests/agent-tools.test.ts`.
- Research: `docs/TOOL-RESEARCH-2026-11-24-WAVE57.md`.

No new package, API key, D1 migration, Worker binding or 534-file processor change.

## Source limitations and safety

- Jikan is an unofficial API that scrapes public MyAnimeList pages; source data may be delayed, incomplete or unavailable.
- Scores, status and release metadata can change; use the original catalog link to verify.
- This feature does not contain episode/video streaming links, manga reading or download links, torrent links or access-control bypasses.
- The feature is a catalog, not a source of current legal streaming availability.

## Acceptance gates

1. PR CI passes TypeScript, Vitest, deployment-script checks, Python runner tests and Cloudflare Worker build.
2. Main CI and Cloudflare deployment/health checks pass after merge.
3. Live Jikan query availability remains a separate check because the upstream API depends on its own parser and public MyAnimeList.
