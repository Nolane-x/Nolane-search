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


## Production rollout — 2026-11-21

- PR #51 merged: https://github.com/Nolane-x/Nolane-search/pull/51
- Main commit: `4c822d8e779d468b304c1ed504b481ddd0d0e7a8`.
- CI run #247 (`44887163239`) passed TypeScript type-check, 199 unit tests, deployment-script checks, 96 Python runner tests and Worker build.
- The first deploy run #104 (`44887246691`) stopped at D1 migrations because GitHub Actions secret `CLOUDFLARE_D1_API_TOKEN` was not configured. The exact log says to add that repository secret with Account > D1 > Edit permission. It did not fail due to the migration SQL or source build.
- To avoid leaving production schema behind, migration `0005_archive_snapshots.sql` was applied through the authenticated Cloudflare D1 session. Readback confirmed migrations `0001`–`0005` and table `archive_snapshots`. The migration only creates a metadata table/indexes; no website snapshot bodies or file bytes were copied into D1.
- PR #52 merged the follow-up archive-list integrity display: https://github.com/Nolane-x/Nolane-search/pull/52
- Latest main commit: `6ab8b45e6c85e9b861bbe481eae439f1874fe381`.
- CI run #249 (`44888520208`) passed. Source-only deployment run #105 (`44888609517`) succeeded; migration step was skipped because this commit did not change migration files, Worker secrets uploaded successfully and Telegram webhook/command registration succeeded.
- Production Worker version `c8a21659-d0f0-47eb-aa9e-941e4b94a748` receives 100% of traffic (deployment created 2026-11-21T09:14:49Z).
- The bot archive commands are deployed: `/archive [query]` and `/archive_restore ID`. Archive list rows now show filename, size and a SHA-256 prefix.

## Owner E2E still required

CI, D1 schema verification, Worker deployment and Telegram command registration do not prove a real archive interaction. In the private Telegram chat, verify: create a watch; receive and index its initial snapshot; cause a page change and receive/index a second snapshot; search by title/URL with `/archive`; restore both with `/archive_restore ID`; and test a source message deleted from the archive channel. A restore is only possible while the original archive message exists and the bot retains source-channel access.

## Future migration requirement

The production database currently has migration `0005` applied, but the GitHub Actions secret `CLOUDFLARE_D1_API_TOKEN` is still required for any future migration-changing push. Configure it in repository Settings → Secrets and variables → Actions with Account > D1 > Edit permission; never put the token in source control or chat.

## Follow-up release: archive pagination — 2026-11-21

- PR #53 merged: https://github.com/Nolane-x/Nolane-search/pull/53
- Release commit: `69c131775570a2bdb93653d4576c1ef3801ae6ac`.
- New command: `/archive_page PAGE [query]`. Pages contain five snapshots; previous/next commands are printed and preserve the search query.
- Page numbers are restricted to 1–1001 (D1 query offset 0–5000); search text is limited to 120 characters and HTML-escaped.
- CI run #252 passed on the PR, main CI run #253 passed, deployment #106 passed, and Worker export/smoke test #99 passed.
- Cloudflare now routes 100% traffic to Worker version `8c8cbfb8-15dc-4ec8-98ee-adabb0c0133c`. Telegram webhook and command registration completed successfully.
- No schema migration was needed. Existing `archive_snapshots` D1 table is reused.
- The owner-level Telegram E2E check remains outstanding: create initial/change captures, search across pages, restore a document and test behavior after deleting an archive source message.

## Follow-up release: D1 index failure recovery — 2026-11-21

- PR #54 merged: https://github.com/Nolane-x/Nolane-search/pull/54
- Release commit: `5f0744a6714c1a343dc4541b1b648e2f903dae25`.
- A successful `sendDocument` followed by a failed D1 index insert no longer leaves the owner without a direct copy: Worker calls Telegram `copyMessage` to the owner's private chat, then notifies that the snapshot is not indexed/searchable.
- If copying also fails, a safe warning includes filename + original archive message ID for manual lookup. Recovery and notification exceptions are isolated from watch processing.
- PR CI #254 and main CI #255 passed. Deployment #107 and build/smoke #100 passed. No schema changes.
- Cloudflare production version: `508f7849-fefc-4592-b93a-f871ec1ed27a`, 100% traffic.
- Owner-level end-to-end Telegram validation is still outstanding (first capture, change capture, page navigation, restore, deleted source message).

## Follow-up release: reliable watch archive retries — 2026-11-21

- PR #55 merged: https://github.com/Nolane-x/Nolane-search/pull/55
- Release commit: `9e36d4bbb99fab28f7532d97cc8f5e0f9e556639`.
- Root cause fixed: the previous watch implementation committed the new page hash and validators before sending/indexing the Telegram snapshot. If sendDocument failed, the next request could receive 304 and the capture was silently lost.
- The Worker now pre-arms `last_status=-4`, keeps the prior content hash and clears ETag/Last-Modified while the archive operation is pending. On the next Cron check it fetches without conditional headers, then advances hash/validators only after both the Telegram document and D1 index succeed.
- /watches describes -4 as `archive pending · retry scheduled`. The failure warning is sent once per initial failure; a normal changed-site alert follows only after success.
- No schema changes. Reuses `watches.last_status`.
- PR CI #258, main CI #259, deployment #108 and build/smoke #101 passed.
- Cloudflare version `cb1e062b-386e-4ed5-aae8-f8a8d5c1959c` receives 100% production traffic.
- Remaining owner-side E2E still required: create a watch, cause archive upload to fail once (or observe naturally), verify `/watches` pending state, and confirm a later scheduled check archives/indexes it. Also re-run initial capture/change/search/pagination/restore checks.


## Follow-up release: isolate watch alert failures — 2026-11-21

- PR #56 merged: https://github.com/Nolane-x/Nolane-search/pull/56
- Release commit: `f08257952cdebd7435daf59aec08c27254f9f9e0`.
- The private "Website changed" alert no longer shares the archive operation's failure boundary. If the archive document and D1 metadata have succeeded but the owner's chat cannot receive the alert, the Worker logs the delivery error and retains the committed snapshot/hash state. This prevents a false pending marker and duplicate archive upload on the next scheduled check.
- The archive-channel change announcement is still attempted separately and its errors remain contained.
- Added a regression test simulating Telegram private-chat sendMessage failure after successful sendDocument and `saveArchiveSnapshot`; expected behavior is one upload, successful watch-hash commit and no transition back to `last_status = -4`.
- PR CI #260 and main CI #261 passed (24 test files / 206 unit tests, type-check, deployment scripts, 96 Python tool-runner tests and Worker build). Deploy #109 and Worker export/smoke #102 passed.
- Cloudflare Worker version `d0e64bf3-7b72-44bf-98fa-1fb35b520a33` receives 100% production traffic.
- No D1 schema migration was required. Telegram webhook and slash-command registration succeeded.
- Owner-level Telegram E2E remains outstanding: real first/change capture, archive search/page navigation, restore, and behavior after deleting an original archive message.


## Follow-up release: truthful archive-state notifications — 2026-11-21

- PR #57 merged: https://github.com/Nolane-x/Nolane-search/pull/57
- Release commit: `019abadd9a36cf8599e9e0b9bdc6ebab81876fe1`.
- Watch change alerts now distinguish between a saved snapshot and a notification-only change when Telegram archive is not configured. The Worker no longer tells the owner that the snapshot was archived if no archive channel exists.
- Regression test covers archive-disabled behavior: update the local indexed hash, send only the change notification, do not call `sendDocument`, and do not claim that a snapshot exists.
- PR CI #262 and main CI #263 passed (24 test files / 207 unit tests, TypeScript, deployment checks, 96 Python runner tests and Worker build). Deploy #110 and Export/Smoke #103 passed.
- Cloudflare Worker version `09d9e4ab-dc2b-4084-ac29-e81e61f27449` receives 100% production traffic.
- No D1 migration was required. The deployment registered the Telegram webhook and command list successfully.
- Owner-side Telegram E2E remains outstanding: real first/change capture, archive search/page navigation, restore and deleted-source-message behavior.
