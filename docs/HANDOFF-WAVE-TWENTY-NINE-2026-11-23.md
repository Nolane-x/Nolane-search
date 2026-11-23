# Wave 29 handoff — Telegram archive index backup and recovery (2026-11-23)

## Current checkpoint

- Repository: Nolane-x/Nolane-search
- Production baseline: **434 tools**, Wave 28 deployed on main commit 61f389df0f9d797af74b27130cfaeb9e5662c47a.
- Candidate branch: feat/wave-twenty-nine-archive-index-backup
- Candidate goal: add an owner-only JSON metadata backup for Telegram archive snapshots so a lost D1 index can be rebuilt while original files remain in the private Telegram archive channel.
- No D1 schema migration is intended. Existing uniqueness on (archive_chat_id, archive_message_id) enables idempotent re-import.
- No new secret, provider or paid resource is required.

## Commands

- /archive_export: create a versioned JSON file for the authenticated owner and current archive channel, then send it to the owner's private Telegram chat.
- /archive_import: show instructions. The owner sends the JSON file with caption exactly /archive_import.
- Existing /archive, /archive_page and /archive_restore remain unchanged.
- Import accepts only a JSON document, not photos/audio/video or general uploads.

## Backup format and constraints

- Format ID: nolane-telegram-archive-index; version: 1.
- Envelope binds ownerUserId, archiveChatId, export timestamp, record count and snapshot metadata.
- Each record stores watch ID, Telegram archive message ID, Telegram file references, file name/size, source URL and normalized URL, title, SHA-256, capture kind/time and original creation time.
- Snapshot page bodies and file bytes are deliberately absent. D1 remains an index; Telegram continues to store original snapshot documents.
- Maximum export/import: 2,000 rows and 5 MiB. Export reads 200 rows per D1 page; import writes batches of 100.
- Imports require the same owner ID and the same currently configured archive-channel ID. Existing (archive_chat_id, archive_message_id) pairs are ignored, so re-import is safe and repeatable.
- D1 internal row IDs are regenerated during restore. /archive_restore uses the regenerated ID to resolve the same Telegram message.
- Telegram getFile paths are validated before download; actual bytes are streamed with a hard 5 MiB cap. Telegram Bot API file references are opaque and must not be logged.
- HTTPS URL shape, owner/channel binding, hash format, timestamps, field lengths, message IDs, duplicate IDs and record counts are validated before any writes.

## Known recovery limits

- This restores the D1 snapshot index only. It cannot recreate deleted Telegram archive messages, the watch definitions, provider credentials, crawler state, D1 FTS site-index rows or other unrelated database tables.
- If the Telegram archive channel changes, the backup is rejected rather than silently retargeted. A separate explicit channel migration would be required.
- Export refuses more than 2,000 rows rather than produce an incomplete backup. A future version can add paginated/chunked exports if this limit becomes insufficient.
- Batch import may complete in earlier batches before a later database error; repeat the same import to finish safely because duplicates are ignored.
- Backup JSON contains private source URLs, titles, Telegram message/file references and capture timestamps. Keep it private; it is metadata, not a redacted public report.
- No file content is placed in D1 or the backup.

## Changed files

- src/archive.ts: backup payload schema, strict parser, paginated metadata export, batched idempotent import.
- src/telegram.ts: private document send helper and bounded getFile/file download.
- src/index.ts: owner-only commands and JSON-document import caption handling.
- scripts/set-commands.mjs: register archive_export and archive_import.
- docs/TELEGRAM-ARCHIVE.md, README.md: user-facing recovery instructions.
- tests/archive.test.ts, tests/telegram-archive.test.ts: export/import validation, idempotence and download bounds.

## Release gates

1. Open/update PR against main and wait for CI on the latest exact head SHA.
2. Verify type-check, all Vitest files, deployment-script syntax, full Python runner suite and Worker build.
3. Inspect any type/runtime/test failure and fix the underlying issue before merge.
4. Merge only after current-head CI passes.
5. Verify main CI, Worker export/health smoke and Cloudflare deployment. Telegram webhook and command menu should be re-verified because commands changed.
6. Owner-level E2E after deployment:
   - run /archive_export in private chat and download the JSON;
   - confirm it contains metadata only (no page body);
   - import the same backup with caption /archive_import and confirm all existing references are skipped;
   - test on an empty/staging D1 copy if available to verify inserted rows and /archive_restore;
   - test wrong owner, wrong archive channel and oversized input rejection;
   - confirm the original Telegram documents remain restorable.
7. Keep production documentation at 434 tools; this Wave 29 task is a reliability improvement, not a new tool-count increase.

## Existing production checkpoint

- Wave 28 main commit: 61f389df0f9d797af74b27130cfaeb9e5662c47a
- Main CI: https://github.com/Nolane-x/Nolane-search/actions/runs/45040057467 — 25 Vitest files / 238 tests and 270 Python runner tests passed.
- Worker export/health: https://github.com/Nolane-x/Nolane-search/actions/runs/45040057426 — passed, health ok: true, database reachable.
- Cloudflare deployment: https://github.com/Nolane-x/Nolane-search/actions/runs/45040057437 — passed, webhook and command menu registered.
- Worker Version ID: 34fad733-fef3-4b93-bc58-e480bb3c082f

Use this file as the next continuation checkpoint; inspect current PR/branch state before making more changes.
