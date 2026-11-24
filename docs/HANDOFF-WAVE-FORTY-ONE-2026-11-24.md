# Wave 41 — daily-life planning tools

Date: 2026-11-24  
Status: implementation branch; PR/CI/deployment pending.  
Branch: \`feat/wave-forty-one-daily-life-planning-tools\`  
Production baseline: **483 processors**.  
Branch target: **494 processors** (+11).

## User direction

Keep expanding useful tools for ordinary people, with less emphasis on specialist developer audits. Prioritize household, travel, money, device, event and delivery tasks.

## Added tools

1. Water bill from meter readings and a user-entered unit price.
2. Mobile data duration and daily budget before renewal.
3. Solar panel energy estimate using panel specs and user-entered peak-sun hours.
4. Wallpaper roll/drop estimator with pattern-repeat support.
5. Curtain fabric estimator with fullness, hems and pattern repeat.
6. Moving box count from packed volume and fill ratio.
7. Event food and drink quantities per guest.
8. Fuel economy and cost per kilometre.
9. Gas cylinder runtime using user-entered consumption.
10. Shipping volumetric weight versus actual weight.
11. Photos/video/documents storage capacity estimate.

## Changed implementation points

- \`tools/wave41.py\`: standard-library Python calculators.
- \`tools/test_wave41.py\`: 14 focused Python tests.
- \`tools/runner.py\`: Wave 41 imports, allowlist and handler mappings.
- \`src/tools.ts\`: 11 new utility catalog entries.
- \`src/daily-life-tools.ts\`: direct AI JSON calculator implementations.
- \`src/agent-tools.ts\`: Wave 41 IDs and JSON schema examples for AI calls.
- \`tests/tools.test.ts\`: current catalog count and registration checks.
- \`tests/agent-tools.test.ts\`: direct AI tests for all 11 new tools.
- \`tests/telegram.test.ts\`: Tool Center count updated from 483 to 494.
- \`docs/TOOL-RESEARCH-2026-11-24-WAVE41.md\`: product-research context.

## Scope and data handling

- All tariff, carrier divisor, energy yield, average file size, fuel use and prices are supplied by the user.
- No live tariff, ISP or carrier quote is fetched.
- No new paid API, secret, Cloudflare product, D1 schema migration or persistent file store.
- Python implementations use the standard library only.
- Existing ephemeral runner, upload limits and output validation are unchanged.

## Remaining verification

1. Pass TypeScript type-check and all Vitest tests.
2. Pass the full Python runner suite and catalog/runner/docs parity test.
3. Pass Cloudflare Worker build.
4. Merge only after green PR CI, then verify main CI, Worker export/health smoke and Cloudflare deployment.
5. Confirm the production catalog is 494 after deployment.
6. Owner-side smoke test: try selected calculator commands in the private Telegram bot and a non-sensitive JSON upload. CI cannot prove client-side Telegram interaction.

Until verification and deployment finish, **494 is the branch target; production remains 483**.
