CREATE TABLE IF NOT EXISTS archive_snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  watch_id INTEGER NOT NULL,
  user_id TEXT NOT NULL,
  chat_id TEXT NOT NULL,
  archive_chat_id TEXT NOT NULL,
  archive_message_id INTEGER NOT NULL,
  telegram_file_id TEXT NOT NULL,
  telegram_file_unique_id TEXT,
  file_name TEXT NOT NULL,
  file_size INTEGER,
  url TEXT NOT NULL,
  normalized_url TEXT NOT NULL,
  title TEXT NOT NULL,
  content_hash TEXT NOT NULL,
  capture_kind TEXT NOT NULL CHECK (capture_kind IN ('initial', 'change')),
  captured_at TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  UNIQUE (archive_chat_id, archive_message_id)
);

CREATE INDEX IF NOT EXISTS idx_archive_snapshots_user_time
  ON archive_snapshots(user_id, captured_at DESC, id DESC);
CREATE INDEX IF NOT EXISTS idx_archive_snapshots_user_url
  ON archive_snapshots(user_id, normalized_url, captured_at DESC);
CREATE INDEX IF NOT EXISTS idx_archive_snapshots_watch_time
  ON archive_snapshots(watch_id, captured_at DESC);
