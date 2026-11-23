# Wave 39 — everyday-user utilities

Date: 2026-11-23  
Status: implementation branch opened; PR/CI/deployment verification pending.  
Branch: \`feat/wave-thirty-nine-everyday-life-tools\`  
Production baseline remains Wave 38: **462 processors**.  
Branch target: **472 processors** (+10).

## User direction

Favor tools ordinary people immediately understand and can use. Avoid filling the catalog with specialist developer, infrastructure, ML or repository checks just to increase the count.

## Added tools

1. Bill splitting with tax, tip and exact final-share rounding.
2. Loan payment estimate with extra monthly payment and an amortization CSV.
3. Date arithmetic, elapsed days and weekday count.
4. IANA timezone conversion with daylight-saving gap and ambiguity handling.
5. Recipe serving and ingredient scaler.
6. Weighted grade calculator with a target score for unfinished components.
7. Paint coverage estimate for walls/ceiling, doors/windows and coats.
8. Fuel trip consumption/cost and per-passenger split.
9. Sequential discount and tax calculator.
10. Unit-price comparison across compatible weight, volume, length and count units.

## Changed integration points

- \`tools/wave39.py\`: standard-library-only calculation implementations.
- \`tools/test_wave39.py\`: focused Python fixtures.
- \`tools/runner.py\`: imports, allowlist and handler map.
- \`src/tools.ts\`: ten ready catalog definitions in the utility category.
- \`src/everyday-tools.ts\`: bounded direct text/JSON calculator implementations for the AI chat.
- \`src/agent-tools.ts\`: adds calculator IDs to the AI callable allowlist, dispatches to the calculator module and updates the tool-discovery count to 472.
- \`tests/agent-tools.test.ts\`: checks the 472-item paginated catalog and exercises all ten direct AI calculators.
- Existing CI auto-discovers \`tools/test_wave39.py\`; no new CI dependency is required.

## Resource and privacy impact

- No new API key, paid service, Cloudflare product, D1 migration or database table.
- No package install required for the new Python processors.
- Calculations are deterministic/offline and only process user-supplied JSON.
- File jobs continue to use ephemeral GitHub Actions runners and existing size/output bounds.
- No bank, lender, fuel-price or mapping integration is implied by these calculators.

## Upstream research

See [TOOL-RESEARCH-2026-11-23-WAVE39.md](TOOL-RESEARCH-2026-11-23-WAVE39.md). Reviewed MIT-licensed OmniTools, PrivaTools and LifeHack Toolbox repositories as product/category references, without copying source code. Also reviewed Czkawka as a candidate for a future duplicate/similar-file utility.

## Remaining verification

1. Confirm Python unit tests, TypeScript type-check/tests and Worker build all pass in PR CI.
2. Fix any failures before merge.
3. Merge only after green PR checks, then confirm main CI and Cloudflare deployment.
4. Verify production catalog returns 472 and health remains green.
5. Owner-side smoke test: exercise selected calculator commands and one JSON-file upload/result via the real private Telegram account; GitHub CI cannot validate the owner's Telegram account interaction.

Until those checks complete, **472 is the branch catalog count, not a production count**.
