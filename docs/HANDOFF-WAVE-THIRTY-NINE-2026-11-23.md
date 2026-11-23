# Wave 39 — everyday-user utilities

Date: 2026-11-23  
Status: **merged and deployed to production**.  
PR: [#92](https://github.com/Nolane-x/Nolane-search/pull/92)  
Merge commit: `b81dfde15bf5d63846cac0d92378cb62eefcb2ec`  
Production catalog: **472 tools** (+10 from Wave 38).  
Worker Version ID: `10cdb714-b7f7-464b-9b75-f6390dde0b4c`  
Worker: https://nolane-search.nolane-file.workers.dev

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

- `tools/wave39.py`: standard-library-only calculation implementations.
- `tools/test_wave39.py`: 12 focused Python fixtures.
- `tools/runner.py`: imports, allowlist and handler map.
- `src/tools.ts`: ten ready catalog definitions in the utility category.
- `src/everyday-tools.ts`: bounded direct text/JSON calculator implementations for AI chat.
- `src/agent-tools.ts`: calculator IDs in the AI callable allowlist, direct dispatch and documented JSON input shapes.
- `tests/agent-tools.test.ts`, `tests/tools.test.ts`, `tests/telegram.test.ts`: test direct AI use, catalog size and the current Tool Center total.
- `docs/TOOL-RESEARCH-2026-11-23-WAVE39.md`: upstream product-category research and license review.
- `docs/NOLANE-TOOLS.md`, `README.md`, `docs/STATUS.md`: updated release state and inventory.

## Validation and deployment — passed

- PR CI [45201821609](https://github.com/Nolane-x/Nolane-search/actions/runs/45201821609) passed type-check, **25 Vitest files / 261 tests**, deployment-script validation, **366 Python runner tests**, and Worker build.
- Main CI [45202094613](https://github.com/Nolane-x/Nolane-search/actions/runs/45202094613) passed the same checks after merge.
- Worker export and production health smoke [45202094578](https://github.com/Nolane-x/Nolane-search/actions/runs/45202094578) passed.
- Cloudflare deploy [45202094802](https://github.com/Nolane-x/Nolane-search/actions/runs/45202094802) passed required-secret validation, bundle validation and Worker upload.
- The live `/health` smoke check reported success.
- Telegram webhook was verified for `message` and `callback_query`; bot commands were registered.
- D1 migration was skipped because there are no schema changes.
- All 472 catalog IDs match the runner allowlist and handler map; the docs parity test checks the exact registered IDs.

## Resource and privacy impact

- No new API key, paid service, Cloudflare product, D1 migration or database table.
- No package install required for the new Python processors.
- Calculations are deterministic/offline and only process user-supplied JSON.
- File jobs continue to use ephemeral GitHub Actions runners and existing size/output bounds.
- No bank, lender, fuel-price or mapping integration is implied by these calculators.

## Upstream research

See [TOOL-RESEARCH-2026-11-23-WAVE39.md](TOOL-RESEARCH-2026-11-23-WAVE39.md). Reviewed MIT-licensed OmniTools, PrivaTools and LifeHack Toolbox repositories as product/category references, without copying source code. Also reviewed Czkawka as a candidate for a future duplicate/similar-file utility.

## Remaining owner-level acceptance

Exercise selected calculator commands and one non-sensitive JSON-file upload/result using the actual private Telegram account. The CI and webhook checks verify deployment/configuration but cannot prove the owner client's end-to-end upload experience.
