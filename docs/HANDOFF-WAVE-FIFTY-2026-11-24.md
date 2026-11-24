# Wave 50 — media and academic discovery handoff

Date: 2026-11-24
Branch: feat/wave-50-media-academic-discovery
Base main commit: 3244da33d64d2ca366bced502d4ce6b3af8e918b
Status: implementation and mocked tests prepared; PR/CI/merge/deployment pending.

## Changes

Five direct AI-callable functions are being added outside the 534 file-processor catalog:
- search_tv_shows
- get_tv_show_episodes
- search_apple_media
- search_music_metadata
- search_scholarly_works

Files changed:
- src/live-everyday-tools.ts
- src/agent-tools.ts
- tests/agent-tools.test.ts
- tests/media-academic-tools.test.ts

No package/dependency update or D1 migration is needed.

## Important review notes

- Apple Search API: approximate 20 calls/minute, enforced as at least 3.1 seconds per warm Worker isolate; not globally coordinated. Metadata and official store links only.
- MusicBrainz: requires a meaningful User-Agent and one request/sec per IP; in-memory throttle is not globally coordinated. Commercial usage requires a separate license/plan.
- Crossref public bibliographic queries: public pool rate limit of one request/sec; in-memory throttle is not globally coordinated. No mailto email was invented.
- TVmaze: CC BY-SA attribution retained and response includes original show link; metadata is not streaming availability.
- Crossref DOI is not an open-access guarantee; citation counts are not quality scores.
- Existing API helper enforces HTTPS, redirect rejection, timeout and bounded JSON response size.

## Acceptance checklist

1. TypeScript type-check succeeds.
2. New API mock tests and all existing Vitest tests pass.
3. Model tool schemas and dispatch integration test pass.
4. GitHub Actions deployment-script checks, Python runner tests and Worker bundle build pass.
5. PR merged into main only after passing checks.
6. Main CI, Cloudflare deploy, Worker export and public health smoke pass.
7. Real user-level examples are separately tried in Telegram/Web Chat; CI mocks and health checks do not prove each live upstream search.

Research: docs/TOOL-RESEARCH-2026-11-24-WAVE50.md
