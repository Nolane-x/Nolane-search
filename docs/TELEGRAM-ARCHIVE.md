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

The archive index is owner-scoped and commands require the private chat. A snapshot cannot be restored after its source message is deleted from Telegram or the bot loses access to the source channel. The D1 index does not independently reconstruct or download the file.

## Recovery boundaries

- Restoring a snapshot copies the original Telegram document; it does not restore the watch definition, provider credentials, D1 state or site-index rows.
- Deleting or disabling a watch does not delete its archived snapshots.
- If the D1 index is lost, the human-readable Telegram archive channel remains the secondary copy, but the bot cannot automatically enumerate its old messages through the Bot API. Rebuild the index only from new captures unless a separate export/backup is available.
- The SHA-256 records identify the captured text payload; they are integrity metadata, not a signature or proof that the upstream website itself was trustworthy.
