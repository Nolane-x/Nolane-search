# Wave 49 — implementation handoff

Date: 2026-11-24
Branch: feat/wave-49-learning-art-world
Base main commit: 06135aee23663d3b5eeec7e0e41ac4cb4bc6fc8a
Status: implementation committed; PR/CI/deployment pending.

## Scope

Five directly AI-callable everyday learning/discovery functions:

- define_english_word
- search_public_domain_books
- search_museum_artworks
- get_natural_events
- get_local_time

The file-processor catalog remains 534.

## Files

- src/live-everyday-tools.ts — dictionary, Gutendex, Art Institute, NASA EONET and local-time adapters.
- src/agent-tools.ts — five model-facing JSON schemas, dispatch and system guidance.
- tests/learning-discovery-tools.test.ts — mocked provider tests and boundary checks.
- tests/agent-tools.test.ts — schema exposure and dispatch integration.
- docs/TOOL-RESEARCH-2026-11-24-WAVE49.md — provider/API review and usage limitations.

## Boundaries

- Fixed HTTPS hosts only, shared 12-second timeout, redirect rejection and 500 KB JSON cap.
- Dictionary API is English-only, on-demand and self-throttled; the maintainer has disclosed operating-cost pressure.
- Gutendex public-domain flag is U.S.-law based only; no book files are downloaded.
- Art Institute search includes only records marked public domain and requires the requested AIC User-Agent header.
- NASA EONET records are curated metadata, not warnings or emergency instructions.
- Local time is calculated with the geocoded IANA zone and server clock.

## Acceptance

1. Full CI must pass.
2. Merge, Worker export/health and Cloudflare deployment must pass.
3. Real Telegram/Web Chat checks remain useful for one definition, public-domain book query, artwork search, NASA event query and city-time query.
