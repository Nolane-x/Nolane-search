# Wave 40 — household and travel utilities

Date: 2026-11-24  
Status: implementation branch; PR/CI/deployment pending.  
Branch: \`feat/wave-forty-everyday-household-tools\`  
Production baseline: **472 processors**.  
Branch target: **483 processors** (+11).

## User direction

Continue expanding the catalog for everyday people. Prioritize useful household, money, travel, device and media/file tasks; do not inflate the catalog with specialist developer checks.

## Added tools

1. Appliance electricity use and monthly cost.
2. Floor tile quantity, boxes and material cost.
3. Concrete volume and optional bag estimate.
4. Soil/mulch volume and optional bag estimate.
5. Household monthly budget and remaining cash.
6. Savings goal timeline under an explicit constant-rate assumption.
7. Travel budget, contingency buffer and per-person split.
8. Download time with correct bit/byte conversions.
9. Work hours, breaks, overnight shifts and estimated gross pay.
10. Battery runtime from Wh or mAh/voltage.
11. Rectangular/cylindrical water tank capacity and fill level.

## Changed implementation points

- \`tools/wave40.py\`: standard-library Python processors.
- \`tools/test_wave40.py\`: fixtures for each processor plus validation edge cases.
- \`tools/runner.py\`: Wave 40 imports, allowlist entries and handler registrations.
- \`src/tools.ts\`: 11 new utility catalog entries.
- \`src/household-tools.ts\`: direct AI JSON processors with bounded validation and user-facing summaries.
- \`src/agent-tools.ts\`: Wave 40 IDs added to the AI callable text processor and model-facing JSON shape documentation.
- \`tests/tools.test.ts\`: catalog count and Wave 40 registration checks.
- \`tests/agent-tools.test.ts\`: direct AI call test for all 11 tools.
- \`tests/telegram.test.ts\`: Tool Center count updated from 472 to 483.
- Research: \`docs/TOOL-RESEARCH-2026-11-24-WAVE40.md\`.

## Scope and data handling

- Offline calculations only; every rate, material price, power rating and network speed is user-supplied.
- No external API, new secret, new database table, D1 migration or Cloudflare resource.
- Standard-library-only Python processors. Existing ephemeral runner, upload limits and output validation are unchanged.
- Estimates are labelled with relevant assumptions. No current utility tariff, exchange rate, building-supply price or ISP performance is implied.

## Remaining verification

1. Pass TypeScript type-check and all Vitest tests.
2. Pass all Python runner tests and catalog/handler/docs parity.
3. Pass Cloudflare Worker build.
4. Merge only after green PR CI, then verify main CI, Worker export/health smoke and Cloudflare deploy.
5. Confirm production catalog count is 483 after deploy.
6. Owner-side smoke test: run selected commands in the private Telegram bot and, separately, test one non-sensitive JSON file upload. CI does not prove the user's private Telegram client interaction.

Until those checks complete, **483 is only the branch count; production remains at 472**.
