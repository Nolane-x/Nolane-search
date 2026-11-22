# Wave 25 handoff — 2026-11-22

## Release status — deployed 2026-11-22

- PR: [#77](https://github.com/Nolane-x/Nolane-search/pull/77), merged into `main`.
- Production commit: `bd5b51cd119d049dd14a654147d03a4303fa7e2c`.
- Catalog: **406 production tools**, up from 395; +11 processors.
- Main CI [45017239242](https://github.com/Nolane-x/Nolane-search/actions/runs/45017239242): success; 25 Vitest files and 206 Python runner tests passed.
- Worker export/production health smoke [45017239294](https://github.com/Nolane-x/Nolane-search/actions/runs/45017239294): success.
- Cloudflare deployment [45017239222](https://github.com/Nolane-x/Nolane-search/actions/runs/45017239222): success; Telegram webhook/command registration passed; D1 migration skipped (no schema change).
- Cloudflare confirms Worker Version 82 (`22378573-aa24-444d-96b0-59e8df345b75`) receives 100% traffic; deployment ID `1479f8fc-5c7c-4615-a3af-abe1fbb895f5`.

## Scope

The 406-tool production catalog now includes the following 11 Wave 25 processors.

## Added processors

| ID | Format/domain | Primary checks |
|---|---|---|
| `wasm-module-audit` | WebAssembly binary v1 | Magic/version, section IDs/lengths, LEB128 bounds, semantic section order, function/code/import/export counts; no instruction decoding or execution. |
| `sarif-report-audit` | SARIF 2.1 JSON | Runs/rules/results, levels, suppressions, locations, fixes and undeclared rule references; withhold all report content/paths. |
| `sbom-audit` | CycloneDX JSON/XML and SPDX 2.x JSON/XML | Component/package/file/service/vulnerability/license counts, dependency/relationship edges, duplicate IDs and missing refs. |
| `junit-xml-audit` | JUnit XML | Suites/cases, failure/error/skipped/flaky results, declared count mismatch and suite durations; suppress names/messages/stdout. |
| `coverage-xml-audit` | Cobertura and JaCoCo XML | Global line/branch percentages, aggregate counters and structural counts; no source paths or per-line details. |
| `fits-audit` | FITS astronomy data | 2880-byte blocks, 80-byte cards, HDUs, BITPIX/NAXIS and declared data-unit byte boundaries; no image decoding. |
| `step-cad-audit` | STEP Part 21 | HEADER/DATA/ENDSEC, entity IDs/references, duplicate IDs, dangling refs and delimiters; no geometry validation. |
| `otel-collector-audit` | OpenTelemetry YAML | Receiver/processor/exporter/connector/extension declarations, service pipeline refs, public bind and literal secret field presence. |
| `godot-project-audit` | Godot project.godot | Sections/settings, autoloads, enabled editor plugin references, res:// and remote URI counts, secret-bearing keys. |
| `unity-package-audit` | Unity .unitypackage | gzip/tar members, GUID folder groups, asset/asset.meta/pathname, missing members, duplicate roles and unsafe archive paths. |
| `unreal-project-audit` | Unreal .uproject | FileVersion, modules/plugins/target platform counts, duplicate identifiers and secret-bearing descriptor keys. |

## Implementation map

- New processor module: `tools/wave25.py`.
- New isolated test suite: `tools/test_wave25.py` (17 tests).
- Python import, RUNNERS allowlist, handler, TEXT_OUTPUT_TOOLS and pipeline transitions: `tools/runner.py`.
- TypeScript catalog, pipeline transitions and upload inference: `src/tools.ts`.
- Registry/inference tests and Telegram Tool Center count: `tests/tools.test.ts`, `tests/telegram.test.ts`.
- Conditional PyYAML install for OTel Collector config: `.github/workflows/tool-runner.yml`.
- Research/licensing rationale: `docs/TOOL-RESEARCH-2026-11-22.md`.
- Candidate scope/status: `docs/STATUS.md`, `docs/NOLANE-TOOLS.md`.

## Safety and bounds

- No uploaded WASM instruction, test, build, shell command, collector, game-engine project, CAD model or plugin is executed.
- No package vulnerability lookup, remote package fetch, FITS pixel decoding, STEP geometry-kernel operation, scene loading or engine compilation occurs.
- SARIF messages/paths/snippets, SBOM package IDs/URLs/names, JUnit testcase names/messages/stdout, coverage source paths/per-line counters, FITS observation fields/pixel data, STEP strings/entity IDs and game-engine project/module/plugin identifiers are withheld.
- All uploaded data stays under the existing 20 MiB input limit; report output stays under the existing runner output boundary. Text/XML/JSON tools use stricter 10 MiB limits; Unity tar archives cap at 10,000 members and 180 MiB expanded.
- PyYAML is already part of the runner dependency set and is installed conditionally only for `otel-collector-audit`.
- Structural diagnostics are not full WebAssembly validation, a vulnerability verdict, legal license advice, test execution, full coverage validation, astronomy rendering, CAD geometry certification or game-engine project verification.

## Release gates

1. Confirm 406 unique TypeScript catalog IDs, 406 Python allowlist IDs and 406 handlers.
2. Type-check, Vitest, Python compile and full unittest discovery.
3. Worker build/export and deployed `/health` smoke.
4. Cloudflare deployment, runtime secret upload, webhook and command registration.
5. Owner-level Telegram E2E with representative files and `/tool_retry`.

Wave 25 is production. Remaining validation is owner-level Telegram E2E: upload representative samples, inspect delivered reports and test `/tool_retry`. Do not infer this from CI or deployment evidence.
