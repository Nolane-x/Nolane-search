import type { D1Database } from "./types";

/**
 * Consume one slot in a per-user, per-action fixed one-minute window.
 * The conditional UPSERT makes the cap atomic across concurrent Worker requests.
 */
export async function consumeRateLimit(
  db: D1Database,
  userId: number,
  action: string,
  limit: number,
  now = Date.now(),
): Promise<boolean> {
  if (!Number.isSafeInteger(userId) || userId < 0) return false;
  if (!/^[a-z0-9:_-]{1,64}$/i.test(action)) return false;
  if (!Number.isSafeInteger(limit) || limit < 1 || limit > 10_000) return false;
  if (!Number.isFinite(now) || now < 0) return false;

  const windowStart = Math.floor(now / 60_000) * 60_000;
  const result = await db.prepare(
    `INSERT INTO web_rate_limits (user_id, action, window_start, request_count)
     VALUES (?, ?, ?, 1)
     ON CONFLICT(user_id, action, window_start)
     DO UPDATE SET request_count = request_count + 1
     WHERE request_count < ?`,
  ).bind(String(userId), action, windowStart, limit).run();

  return (result.meta?.changes ?? 0) > 0;
}
