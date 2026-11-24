# Wave 50 — media and academic discovery handoff

Date: 2026-11-24
Branch: feat/wave-50-media-academic-discovery
Base main commit: 3244da33d64d2ca366bced502d4ce6b3af8e918b
PR: https://github.com/Nolane-x/Nolane-search/pull/106
Squash merge commit: 5e423c98cc1c5a28aae558468c03d6f375e07bf4
Status: merged into main and deployed to production on 2026-11-24.

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

## Production verification

- PR #106 merged into `main` on 2026-11-24.
- PR CI [45382180134](https://github.com/Nolane-x/Nolane-search/actions/runs/45382180134) passed.
- Main CI [45382454398](https://github.com/Nolane-x/Nolane-search/actions/runs/45382454398) passed TypeScript, 29 Vitest files / 303 tests, deployment-script checks, 449 Python runner tests and Worker build.
- Cloudflare deployment [45382454250](https://github.com/Nolane-x/Nolane-search/actions/runs/45382454250) succeeded; Worker Version ID `366f58b7-abb7-4ce4-9857-5997e48b2a66`; Telegram webhook and command-menu registration succeeded.
- Worker export and public health smoke [45382454329](https://github.com/Nolane-x/Nolane-search/actions/runs/45382454329) passed.
- No D1 migration was needed; no new dependency or credential was added.
- The 534 file-processor catalog is unchanged.

## Owner-level acceptance checklist

1. TypeScript type-check succeeds.
2. New API mock tests and all existing Vitest tests pass.
3. Model tool schemas and dispatch integration test pass.
4. GitHub Actions deployment-script checks, Python runner tests and Worker bundle build pass.
5. Real user-level examples are separately tried in Telegram/Web Chat; CI mocks and health checks do not prove each live upstream search.

Research: docs/TOOL-RESEARCH-2026-11-24-WAVE50.md
