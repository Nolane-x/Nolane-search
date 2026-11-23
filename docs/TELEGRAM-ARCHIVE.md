# Telegram snapshot archive

## Storage model

Nolane Search keeps website snapshot files in the private Telegram archive channel configured by TELEGRAM_ARCHIVE_CHAT_ID. Each successful sendDocument response is indexed in Cloudflare D1 with the owner and originating chat, watch ID, URL, title, capture timestamp, capture type, SHA-256 hash, Telegram channel/message/file references, filename and file size.

The page text and document bytes are not copied into D1. D1 is a searchable catalogue and recovery pointer; Telegram holds the archived document. This avoids turning the database into a file store.

## Commands

- /archive lists the five most recent snapshots belonging to the current owner (page 1).
- /archive query searches the owner's snapshot titles and URLs; results are shown five per page.
- /archive_page PAGE [query] opens another page and can carry the same optional search query. The command supports pages 1–1001 (the query layer caps offset at 5,000 rows).
- Each non-final page shows previous/next commands. Query text is HTML-escaped before it is shown in Telegram.
- /archive_restore ID copies the original channel document back into the private bot chat using Telegram copyMessage.
- /archive_export creates a versioned JSON backup of the owner's snapshot index and sends it to the owner's private chat. It includes metadata, SHA-256 hashes and Telegram channel/message/file references only; snapshot page bodies are not copied into the backup.
- /archive_import explains the recovery process. To import, send the JSON backup file as a Telegram document with caption `/archive_import`. Import is restricted to the same owner ID and configured archive channel. Existing channel/message references are skipped, so importing the same backup twice is idempotent.

## Index backup and recovery

The backup envelope records a format identifier, version, export timestamp, owner Telegram ID, archive channel ID, record count and snapshot metadata. It is capped at 2,000 records and 5 MiB. Imports validate owner/channel binding, HTTPS source URLs, record fields, SHA-256 shape and duplicate message IDs before writing. Telegram file downloads are bounded to 5 MiB and the Bot API file path is validated before fetching. D1 rows are restored in small batches with `INSERT OR IGNORE`; old internal D1 IDs are regenerated, while Telegram message references remain unchanged.

Keep the JSON backup private: it contains source URLs, titles, file references and capture timestamps. The file does not contain snapshot text/documents and cannot recreate deleted Telegram channel messages. The archive channel still needs to exist and the bot must retain access. An export is a backup of the index, not a copy of the underlying snapshot files.

The archive index is owner-scoped and commands require the private chat. A snapshot cannot be restored after its source message is deleted from Telegram or the bot loses access to the source channel. The D1 index does not independently reconstruct or download the file.

## Recovery boundaries

- Restoring a snapshot copies the original Telegram document; it does not restore the watch definition, provider credentials, D1 state or site-index rows.
- Deleting or disabling a watch does not delete its archived snapshots.
- If the D1 index is lost, the human-readable Telegram archive channel remains the secondary copy, but the bot cannot automatically enumerate its old messages through the Bot API. Rebuild the index only from new captures unless a separate export/backup is available.
- The SHA-256 records identify the captured text payload; they are integrity metadata, not a signature or proof that the upstream website itself was trustworthy.
