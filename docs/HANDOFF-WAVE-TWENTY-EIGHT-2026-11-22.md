# Wave 28 handoff — 2026-11-22

## Final release checkpoint — deployed 2026-11-23\n\n- PR #80 merged as `61f389df0f9d797af74b27130cfaeb9e5662c47a`.\n- Production catalog is **434 tools**, deployed Worker Version ID `34fad733-fef3-4b93-bc58-e480bb3c082f`.\n- Main CI [45040057467](https://github.com/Nolane-x/Nolane-search/actions/runs/45040057467) passed 25 Vitest files / 238 tests and 270 Python runner tests.\n- Worker export/health smoke [45040057426](https://github.com/Nolane-x/Nolane-search/actions/runs/45040057426) passed; health confirmed `ok: true`, database `reachable`, archive enabled.\n- Cloudflare deploy [45040057437](https://github.com/Nolane-x/Nolane-search/actions/runs/45040057437) passed; Telegram webhook (message + callback_query) and command menu verified. D1 migration skipped correctly.\n- Wave 28 is closed. Remaining owner-level acceptance: send representative synthetic/non-sensitive files through the private Telegram bot, check reports/downloads and test `/tool_retry`.\n\n## Current checkpoint

- Repository: `Nolane-x/Nolane-search`
- Production baseline: **426 tools**, after Wave 27.
- Candidate branch: `feat/wave-twenty-eight-scientific-format-tools`
- Pull request: [#80 — Wave 28: scientific, medical imaging and spatial data auditors](https://github.com/Nolane-x/Nolane-search/pull/80)
- Candidate catalog: **434 tools** (426 production + 8 new).
- CI is tied to the latest source commit; verify the latest check run before merge. Do not treat a queued, cancelled or older-head run as proof of success.
- No schema migration is expected. Wave 28 does not intentionally change D1 structure or secrets.

## Wave 28 processor IDs

1. `ocfl-object-audit` — OCFL root/version inventory, state/manifest references, content fixity and every inventory digest sidecar, including BLAKE2b-512.
2. `zarr-store-audit` — Zarr v2/v3 group/array metadata and hierarchy, not chunk data.
3. `nifti-header-audit` — NIfTI-1/2 header-only validation, including bounded .nii.gz header reads.
4. `dicom-privacy-audit` — limited DICOM header identifier/private-tag risk screen, not de-identification.
5. `las-pointcloud-audit` — LAS 1.0–1.4 header and point-record byte-range checks; LAZ is unsupported.
6. `jp2-box-audit` — JPEG 2000 JP2 box framing using offsets, not codestream decoding or payload reads.
7. `netcdf-classic-audit` — seek-based NetCDF CDF-1/CDF-2 header parser that skips variable-array payload bytes; NetCDF-4/CDF-5 are unsupported.
8. `nwb-structure-audit` — HDF5/NWB metadata hierarchy; no dataset values.

Implementations: `tools/wave28.py`; tests: `tools/test_wave28.py`. The current test file has 19 synthetic regression cases. Catalog/dispatch changes touch `src/tools.ts`, `tools/runner.py`, `.github/workflows/ci.yml`, `.github/workflows/tool-runner.yml`, and `tests/tools.test.ts` / `tests/telegram.test.ts`.

## Release gates

1. Run the latest PR #80 CI against the latest head SHA. Inspect every job, including TypeScript type-check, all Vitest files, Python runner tests, deployment-script checks and Worker build.
2. Fix all failures and wait for a new run tied to the exact current head SHA.
3. Verify registry parity: TypeScript catalog IDs, Python RUNNERS, handler dispatch and explicit pipeline transition edges; verify upload inference for all eight new formats.
4. Merge only after current-head CI passes.
5. Confirm main CI, Worker export/build and production health smoke.
6. Confirm Cloudflare deployment and Telegram webhook/command registration. If Telegram registration times out, inspect the exact failed step and rerun that job; do not count a partially completed deployment as release success.
7. Update production count/version only after the deployment finishes successfully.
8. Owner-level E2E remains separate: send synthetic/non-sensitive examples through the private Telegram bot, inspect delivered reports and exercise `/tool_retry`. Automated CI and webhook registration do not prove the whole user upload journey.

## Safety constraints

- No medical diagnosis, clinical decision support, patient-data anonymization or guarantee of DICOM confidentiality.
- Do not print DICOM tag values, patient identifiers, image pixels, NIfTI voxels, point-cloud coordinates, Zarr chunks, NetCDF arrays, NWB time-series, metadata values or archive paths.
- No remote URL dereferencing. ZIP members are not extracted to disk; size/member/path/link bounds remain mandatory.
- The input is still processed on a GitHub-hosted ephemeral runner. Hiding values in output does not de-identify the original file.
- Document unsupported cases honestly: LAZ compression, NetCDF-4/HDF5, NetCDF-CDF-5 and full JPEG 2000 decoding are outside these processors.

## Recovered Telegram snapshot archive model

This section recovers the architecture documented in `docs/TELEGRAM-ARCHIVE.md`, `src/archive.ts`, `src/watch.ts` and `src/telegram.ts`.

- A successful website watch capture is turned into a text document and sent to the private Telegram archive channel using `sendDocument`.
- The message reference and searchable metadata are then stored in Cloudflare D1: owner/origin chat, watch ID, archive channel/message IDs, Telegram file IDs, filename, size, URL/normalized URL, title, capture type/time and SHA-256 of captured text. D1 is an index and recovery pointer, not the file store.
- `/archive` and `/archive query` show five entries per page; `/archive_page PAGE [query]` can navigate up to page 1001 (the query layer caps the offset at 5,000 rows).
- `/archive_restore ID` calls Telegram `copyMessage` to copy the original archive-channel document back to the user's private chat.
- Disabling/deleting a watch does not delete historical snapshots. Restoring a snapshot does not rebuild the watch, its provider credentials, D1 state or personal website-index rows.
- A snapshot cannot be restored if its Telegram source message was deleted or the bot no longer has access to the archive channel.
- If the D1 snapshot index is lost, Telegram's Bot API does not let the bot enumerate all old channel history for automatic index reconstruction. A separate export/backup is required for a complete rebuild; otherwise the index can only be repopulated from new captures.
- SHA-256 here is integrity metadata for the captured text payload, not a signature or proof that the source website was trustworthy.
- Crawler snapshots are owner-triggered and bounded; they are not a whole-web archive. The system checks robots.txt, keeps a bounded page extract in D1 for its separate site index, and can send full text snapshots to the Telegram archive channel when that feature is configured.

## Existing production checkpoint before Wave 28

Wave 27 is deployed on main commit `408beb47bf3eeceeb4f0bb5a33f8e3bb23d9ad1d` with 426 tools.

- Main CI: [45037484505](https://github.com/Nolane-x/Nolane-search/actions/runs/45037484505)
- Worker export/build and health smoke: [45037484786](https://github.com/Nolane-x/Nolane-search/actions/runs/45037484786)
- Cloudflare deploy: [45037484485](https://github.com/Nolane-x/Nolane-search/actions/runs/45037484485), successful on rerun attempt 2
- Deployed Worker Version ID: `3f0d1279-321b-4438-8a93-28960781dddf`
- Telegram webhook for `message` and `callback_query`, plus command menu, confirmed registered.

Use this file as the next continuation checkpoint; inspect current PR/branch state before making further changes.
