# Wave 31 handoff — PRONOM file format identification (2026-11-23)

## Current checkpoint

- Repository: `Nolane-x/Nolane-search`
- Production baseline: **437 tools**, latest deployed Worker Version ID `8f9ca4bf-21ac-4fb7-9e11-fcaaaa3f3d2b`.
- Candidate branch: `feat/wave-thirty-one-pronom-file-identification`
- Candidate processors: 1; candidate catalog **438** (437 production + 1 unmerged).
- PR is not yet open. Run CI on the exact latest head before opening/merging.
- No D1 schema change, secret, provider or paid Cloudflare resource is expected.

## Wave 31 processor

- ID: `file-format-identify`
- Name: PRONOM/Siegfried file format identification.
- Purpose: detect a file format from signatures when the uploaded extension/MIME does not select an existing specialist tool. Explicit use via `/tool file-format-identify` accepts any uploaded file.
- Output: PUID, format label/version and MIME; separates identified, unknown and ambiguous results.
- Not a malware scanner, authenticity verifier or file-content safety validator.

## Pinned upstream assets

- Upstream: [richardlehane/siegfried](https://github.com/richardlehane/siegfried), Apache-2.0.
- Release: [v1.11.9](https://github.com/richardlehane/siegfried/releases/tag/v1.11.9), published 2026-09-27.
- Static Linux binary: `siegfried_1-11-9_linux64_static.zip`, SHA-256 `c8cb3ec3c536863bd477cea7cd1b1213843b4bcad7e9d64bcea4d131e2bb9a01`.
- Signature-data archive: `data_1-11-9.zip`, SHA-256 `1a284a57d102996ab99e393dc40e7e213039ab44e1573c55fa9d9935840515cf`.
- Installer: `scripts/install-siegfried.sh`. It downloads only these fixed release assets, verifies both checksums, locates `sf` and `default.sig`, verifies engine version and writes paths into `GITHUB_ENV`. No `sf -update` network signature refresh is run.
- Runner install is conditional on selected tool ID. CI installs same pinned assets for a real ZIP fixture test.

## Implementation files

- `tools/wave31.py`: JSON validation, privacy-reduced report and local Siegfried subprocess wrapper.
- `tools/test_wave31.py`: parser, unknown/ambiguous results, filename/path/error redaction, size/match bounds and real engine integration.
- `scripts/install-siegfried.sh`: pinned binary/signature installer with SHA-256 checks.
- `src/tools.ts`: catalog, pipeline transition and unknown-upload fallback.
- `tools/runner.py`: allowlist, handler and text-output routing.
- `.github/workflows/ci.yml`: installs pinned engine for integration tests.
- `.github/workflows/tool-runner.yml`: installs engine only when selected.
- `tests/tools.test.ts`, `tests/telegram.test.ts`: registry count, fallback and UI count.
- `docs/NOLANE-TOOLS.md`, `docs/STATUS.md`, `docs/TOOL-RESEARCH-2026-11-22.md`, `README.md`: candidate docs.

## Safety and limits

- One uploaded local file only; no recursive archive scanning.
- Existing 20 MiB per-file input cap and 30-second process timeout.
- Siegfried JSON output cap 1 MiB; maximum 128 match records.
- Report returns PUID/format/version/MIME only. No filename, filesystem path, file modified time, raw stderr, file bytes, raw signature basis or arbitrary diagnostic values.
- Unknown files stay unknown; no format is inferred from extension alone by this processor.
- Existing dedicated PDF/image/audio/video/scientific parsers retain precedence. Fallback changes from `file-hash` to `file-format-identify`; `file-hash` stays available explicitly.
- The PRONOM signature database is a frozen v1.11.9 release snapshot. Updating it requires an intentional version/hash change and a refreshed real-engine test.

## Release gates

1. Open PR and run CI on the exact latest head.
2. Confirm the pinned asset download, SHA checks and `sf -version` succeed in CI.
3. Confirm type-check, Vitest, deployment scripts, full Python suite and Worker build pass.
4. Confirm catalog/runner/handler/pipeline parity is 438 unique IDs and upload fallback tests preserve specialist parser precedence.
5. Merge only when current-head CI passes.
6. Confirm main CI, Worker export/health smoke and Cloudflare deployment.
7. Owner acceptance after deployment: send a synthetic ZIP, an unknown binary and a known document through the private bot; confirm PUID/format/MIME results, unknown handling, no path/filename leakage, and `/tool_retry`.

## Production checkpoint

- Wave 30 main code commit: `44dc33b71f7317d54e9fa9ae1ac6a48b84a06797`
- Worker deploy: [45124586883](https://github.com/Nolane-x/Nolane-search/actions/runs/45124586883)
- Worker export/health: [45124586793](https://github.com/Nolane-x/Nolane-search/actions/runs/45124586793)
- Main CI: [45124586861](https://github.com/Nolane-x/Nolane-search/actions/runs/45124586861)
- Latest Worker Version ID: `8f9ca4bf-21ac-4fb7-9e11-fcaaaa3f3d2b`

Use this file as the continuation checkpoint; inspect current branch/PR/CI before any merge.
