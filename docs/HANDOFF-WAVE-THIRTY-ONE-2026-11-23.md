# Wave 31 handoff — PRONOM file format identification (2026-11-23)

## Final production checkpoint — deployed 2026-11-23

- PR [#84](https://github.com/Nolane-x/Nolane-search/pull/84) merged into `main` as `bfc107d1f299b9ae4b7c557fbe4fea0e3eee6599`.
- Production catalog: **438 tools** (437 before Wave 31 + 1 PRONOM file-format processor).
- Latest Worker Version ID: `679e4cfc-08a8-4832-92cc-459e79df6763`.
- Main CI [45127497703](https://github.com/Nolane-x/Nolane-search/actions/runs/45127497703) passed type-check, 25 Vitest files / 253 tests, deployment-script checks, 293 Python runner tests and Worker build.
- Worker export/health [45127497583](https://github.com/Nolane-x/Nolane-search/actions/runs/45127497583) passed; live health returned `ok: true`, D1 `reachable`, archive enabled.
- Cloudflare deployment [45127497651](https://github.com/Nolane-x/Nolane-search/actions/runs/45127497651) passed; Telegram webhook (message + callback_query) and bot command menu registered successfully.
- No D1 migration, new secret, provider or paid Cloudflare resource. Siegfried binary and PRONOM signatures are pinned by SHA-256 and installed only for the selected tool.
- Owner-level Telegram acceptance remains manual: upload synthetic ZIP, an unknown binary and a known document; inspect PUID/format/MIME, unknown behaviour, privacy and `/tool_retry`.

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

## Remaining owner-level acceptance

Automated CI, pinned asset verification, real-engine ZIP identification, Worker health and production deployment all passed. The remaining checks require sending files through the private Telegram bot:

1. Upload a synthetic ZIP with a misleading filename and confirm the content signature is identified independently of the extension.
2. Upload an unknown binary and confirm the report says unknown without inventing a format.
3. Upload a known document (for example PDF) with a neutral filename and confirm PUID/format/MIME are reported.
4. Confirm the generated report and Telegram message do not reveal the submitted filename or runner path.
5. Exercise `/tool_job` and `/tool_retry` on the new processor.

These checks were not performed in the user's live Telegram session. Do not describe them as owner-verified until tested.

## Production checkpoint

- Wave 31 main code commit: `bfc107d1f299b9ae4b7c557fbe4fea0e3eee6599`
- PR: [#84](https://github.com/Nolane-x/Nolane-search/pull/84)
- Main CI: [45127497703](https://github.com/Nolane-x/Nolane-search/actions/runs/45127497703) — 25 Vitest files / 253 tests and 293 Python runner tests.
- Worker export/health: [45127497583](https://github.com/Nolane-x/Nolane-search/actions/runs/45127497583)
- Cloudflare deploy: [45127497651](https://github.com/Nolane-x/Nolane-search/actions/runs/45127497651)
- Production Tool Center: 438 tools.
- Latest Worker Version ID: `679e4cfc-08a8-4832-92cc-459e79df6763`

Use this file as the continuation checkpoint; inspect current branch/PR/CI before any merge.
