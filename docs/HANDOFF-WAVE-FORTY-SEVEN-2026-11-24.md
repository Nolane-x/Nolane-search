# Wave 47 — implementation handoff

Date: 2026-11-24
Branch: feat/wave-47-live-everyday-information
Base main commit: 9f8d4ea0972299d7f09d59889d68557cbacbedf5
Status: implementation committed; PR, CI and deployment pending.

## Scope

Five AI-callable live-information functions, separate from the unchanged 534 file processors:

- get_weather_forecast
- check_air_quality
- convert_currency
- get_public_holidays
- find_long_weekends

## Files

- src/live-everyday-tools.ts — bounded public API adapters and deterministic calendar calculation.
- src/agent-tools.ts — model-facing function schemas, dispatch and model guidance.
- tests/live-everyday-tools.test.ts — mocked API, validation and boundary tests.
- tests/agent-tools.test.ts — model-tool exposure and dispatch integration.
- docs/TOOL-RESEARCH-2026-11-24-WAVE47.md — upstream research, API terms and limits.

## Important boundaries

- Fixed HTTPS hosts only, redirect rejection, 12-second timeout and 500 KB JSON response cap.
- Weather and air-quality figures are model data with timestamps; air quality is not a station reading.
- Currency conversion includes its rate date and is only a daily reference calculation.
- Public holidays are national and first-level subdivision records. No city/employer/school closure claims.
- Long-weekend results are candidate calendar clusters; substitute days and employer leave are not inferred.
- Open-Meteo's free API is non-commercial only and each response includes CC BY 4.0 attribution.
- No API credentials, D1 migration, dependencies, persistent user profile or upstream copied source.

## Acceptance still pending

1. CI type-check, complete Vitest suite, Python runner tests and Worker build.
2. Merge to main and verify Cloudflare deployment/health.
3. Record actual main-branch deployment run and Worker version.
4. Test live Telegram/Web Chat requests for one weather lookup, one currency conversion and one country holiday lookup.
