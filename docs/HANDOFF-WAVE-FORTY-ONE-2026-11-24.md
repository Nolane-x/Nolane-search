# Wave 41 — daily-life planning tools

Date: 2026-11-24  
Status: **merged and deployed to production**.  
PR: [#94](https://github.com/Nolane-x/Nolane-search/pull/94)  
Merge commit: `38e6c4a81b147f5445c23682c8e75b138ccf1c60`  
Production catalog: **494 tools** (+11 from Wave 40).  
Worker Version ID: `4d48b314-4548-4a78-8059-2215027cc989`  
Worker: https://nolane-search.nolane-file.workers.dev

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

- `tools/wave41.py`: standard-library Python calculators.
- `tools/test_wave41.py`: 14 focused Python tests.
- `tools/runner.py`: Wave 41 imports, allowlist and handler mappings.
- `src/tools.ts`: 11 new utility catalog entries.
- `src/daily-life-tools.ts`: direct AI JSON calculator implementations.
- `src/agent-tools.ts`: Wave 41 IDs and JSON schema examples for AI calls.
- `tests/tools.test.ts`, `tests/agent-tools.test.ts`, `tests/telegram.test.ts`: registry, AI access and Tool Center count checks.
- `docs/TOOL-RESEARCH-2026-11-24-WAVE41.md`: product research and use-case references.
- README, verified status and tool inventory updated for production.

## Validation and deployment — passed

- PR CI [45299967122](https://github.com/Nolane-x/Nolane-search/actions/runs/45299967122) passed type-check, **25 Vitest files / 265 tests**, Python runner tests and Worker build.
- Main CI [45300211124](https://github.com/Nolane-x/Nolane-search/actions/runs/45300211124) passed TypeScript, **25 Vitest files / 265 tests**, deployment-script checks, **394 Python runner tests** and Worker build.
- Worker export/build and live `/health` smoke [45300211171](https://github.com/Nolane-x/Nolane-search/actions/runs/45300211171) passed.
- Cloudflare deployment [45300211092](https://github.com/Nolane-x/Nolane-search/actions/runs/45300211092) passed secret validation, bundle validation, Worker upload, Telegram webhook verification and bot command registration.
- Telegram webhook was verified for `message` and `callback_query`; bot commands were registered.
- D1 migration was skipped because there are no schema changes.
- The 494 catalog IDs match the runner allowlist and handler map; the documentation parity check covers all registered `/tool` IDs.
- Worker Version ID: `4d48b314-4548-4a78-8059-2215027cc989`.

## Scope and data handling

- All tariffs, energy yields, plan allowances, rates, prices, volumetric divisors, dimensions and average file sizes are user-supplied.
- No live utility, mobile carrier, solar installer, retailer or shipping quote is implied.
- No new paid API, secret, Cloudflare resource, D1 schema change or persistent file store.
- Python implementations use the standard library only; existing ephemeral runner, upload limits and output validation are unchanged.
- Estimates state their assumptions and known omissions.

## Remaining owner-level acceptance

Try selected calculator commands in the actual private Telegram bot and one non-sensitive JSON file upload. CI, deployment and webhook checks verify production integration but do not prove client-side interaction in the owner's Telegram account.
