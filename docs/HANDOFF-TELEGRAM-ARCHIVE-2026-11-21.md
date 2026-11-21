# Telegram archive index and restore handoff

Date: 2026-11-21
Repository: https://github.com/Nolane-x/Nolane-search
Branch: feat/telegram-archive-index-restore
Base: e4dd14f4d965f557e684b0ec3eb14789769d64f8

## Goal

Make Telegram website snapshots discoverable and restorable without storing snapshot bodies or binary files in Cloudflare D1.

## Implementation

- sendArchiveDocument returns Telegram's successful message_id, file_id, file_unique_id, file name and optional file size.
- archive_snapshots stores owner-scoped metadata, a SHA-256 page-text hash and the channel message/file references.
- /archive [query] lists recent snapshots or searches title/URL.
- /archive_restore ID uses Telegram copyMessage to copy the original file from the archive channel into the owner's private chat.
- Disabling/removing a watch does not remove historical archive snapshots.
- D1 stores no snapshot body; Telegram remains the binary/document store.

## Validation gates

1. New D1 migration applies after existing migrations 0001–0004.
2. TypeScript type-check, unit tests and Cloudflare Worker build pass.
3. Telegram command menu is updated with /archive and /archive_restore.
4. Owner E2E uploads at least one first-capture and one change snapshot, finds them by title/URL, restores both, and confirms the restored document matches the archive message.
5. Explicitly test a manually deleted archive message: /archive must still show the indexed entry and /archive_restore must report that the source message is unavailable without exposing internal errors.

## Claim boundary

A successful CI run verifies code and D1 migration construction, not live Telegram channel permissions or owner-level restore. Production is not updated by this branch until the PR is merged and deployment succeeds.
