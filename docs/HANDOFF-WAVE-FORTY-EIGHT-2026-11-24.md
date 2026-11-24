# Wave 48 — implementation handoff

Date: 2026-11-24
Branch: feat/wave-48-marine-earthquake-books-postal
Base main commit: bdab89165ccdd068efe14aefe386b5082011c220
Status: implementation committed; PR/CI/deployment pending.

## Scope

Four AI-callable services, separate from the 534 file processors:

- get_marine_forecast
- get_earthquake_activity
- search_books
- lookup_postal_code

## Files

- src/live-everyday-tools.ts — bounded adapters for marine, USGS, Open Library and Zippopotam.us APIs.
- src/agent-tools.ts — four model-facing schemas, direct dispatch and system guidance.
- tests/live-world-tools.test.ts — mocked provider tests.
- tests/agent-tools.test.ts — tool exposure and AI-dispatch integration.
- docs/TOOL-RESEARCH-2026-11-24-WAVE48.md — API review and limits.

## Boundaries

- Fixed HTTPS hosts, redirect rejection, 12-second timeout and 500 KB JSON response cap.
- Marine data is model-derived and not a navigation/safety guarantee; nearest sea-grid distance is included.
- Earthquake results are USGS catalog events, not an early-warning service.
- Open Library is low-volume, human-initiated search, max 10 records and one request/sec per warm isolate, with descriptive User-Agent.
- Postal lookup is GeoNames-derived; coverage/accuracy varies and it is not proof of delivery.
- Open-Meteo free API remains non-commercial only.
- Open Food Facts was intentionally excluded because its usage form and provider restrictions require separate review.
- No D1 migration, API secrets, dependencies, paid services or copied source assets.

## Acceptance

1. Full CI must pass.
2. Merge and Cloudflare deployment/health must pass.
3. Owner-side Telegram/Web Chat acceptance should include a coastal forecast, nearby earthquake lookup, book search and postcode query. Mocked CI tests do not replace these real-user checks.
