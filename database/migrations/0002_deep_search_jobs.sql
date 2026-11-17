CREATE TABLE IF NOT EXISTS deep_search_jobs (
  id TEXT PRIMARY KEY,
  chat_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  query TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'queued'
    CHECK (status IN ('queued', 'running', 'completed', 'failed')),
  attempts INTEGER NOT NULL DEFAULT 0 CHECK (attempts >= 0),
  last_error TEXT,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  completed_at INTEGER
);

CREATE INDEX IF NOT EXISTS idx_deep_search_jobs_user_created
  ON deep_search_jobs(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_deep_search_jobs_status_updated
  ON deep_search_jobs(status, updated_at);
