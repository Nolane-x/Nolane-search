import { constantTimeEqual, htmlEscape } from "./security";
import { performDeepSearch, performSearch } from "./search";
import { fetchOpenRouterSummary, fetchTinyFishPage, parseOpenRouterModels } from "./providers";
import { formatDeepReport, formatSearchResults, sendTelegram, sendToArchive } from "./telegram";
import { validateWatchUrl, checkWatchTargets } from "./watch";
import type { DeepSearchJob, Env, ExecutionContext, MessageBatch, SearchMode, TelegramUpdate } from "./types";

function allowedUser(env: Env, userId: number): boolean {
  const allowed = (env.ALLOWED_TELEGRAM_USER_IDS || "")
    .split(",").map((value) => value.trim()).filter(Boolean);
  return allowed.includes(String(userId));
}

function parseCommand(text: string): { command: string; args: string } {
  const trimmed = text.trim();
  if (!trimmed.startsWith("/")) return { command: "search", args: trimmed };
  const [raw, ...rest] = trimmed.split(/\s+/);
  const command = (raw || "").split("@")[0].slice(1).toLowerCase();
  return { command, args: rest.join(" ").trim() };
}

async function reply(env: Env, chatId: number, message: string): Promise<void> {
  await sendTelegram(env, chatId, message);
}

async function recordUpdate(env: Env, updateId: number): Promise<boolean> {
  const result = await env.DB.prepare("INSERT OR IGNORE INTO telegram_updates (update_id) VALUES (?)")
    .bind(String(updateId)).run();
  return (result.meta?.changes ?? 0) > 0;
}

function isDeepSearchJob(value: unknown): value is DeepSearchJob {
  if (!value || typeof value !== "object") return false;
  const job = value as Partial<DeepSearchJob>;
  return typeof job.id === "string" && job.id.length >= 8 && job.id.length <= 80 &&
    typeof job.query === "string" && job.query.length >= 2 && job.query.length <= 400 &&
    Number.isSafeInteger(job.chatId) && Number.isSafeInteger(job.userId) &&
    Number.isFinite(job.createdAt);
}
function jobStatusLabel(status: string): string {
  return ({ queued: "Đang chờ", running: "Đang chạy", completed: "Hoàn tất", failed: "Thất bại" } as Record<string, string>)[status] || "Không rõ";
}
async function handleSearch(env: Env, chatId: number, query: string, mode: SearchMode): Promise<void> {
  if (!query || query.length < 2) {
    await reply(env, chatId, "Hãy nhập truy vấn cần tìm sau lệnh, ví dụ: <code>/search small language models</code>.");
    return;
  }
  if (query.length > 500) {
    await reply(env, chatId, "Truy vấn tối đa 500 ký tự.");
    return;
  }
  try {
    const results = await performSearch(env, query, mode);
    const message = formatSearchResults(query, mode, results);
    await reply(env, chatId, message);
    await sendToArchive(env, message);
  } catch (error) {
    console.error("Search failed:", error instanceof Error ? error.message : "unknown");
    await reply(env, chatId, "Không thể hoàn tất tìm kiếm. Provider có thể đang lỗi hoặc hết quota. Kiểm tra cấu hình API key hoặc thử lại sau.");
  }
}

async function handleCommand(env: Env, chatId: number, userId: number, text: string): Promise<void> {
  const { command, args } = parseCommand(text);

  if (command === "id" || command === "start") {
    if (!allowedUser(env, userId)) {
      await reply(env, chatId,
        `Telegram ID của bạn: <code>${userId}</code>\n\nBot đang ở chế độ private. Chủ bot cần thêm ID này vào GitHub Actions Secret <code>ALLOWED_TELEGRAM_USER_IDS</code> rồi triển khai lại. Không gửi bot token cho bất kỳ ai.`);
      return;
    }
    await reply(env, chatId,
      "<b>Chào mừng đến Nolane Search.</b>\n\nTìm kiếm web, GitHub, tin tức, nghiên cứu và các website bạn theo dõi. Gõ /help để xem lệnh.");
    return;
  }

  if (!allowedUser(env, userId)) {
    await reply(env, chatId, "Bot này hiện chỉ dành cho tài khoản được chủ bot cho phép. Dùng /id để xem Telegram ID của bạn.");
    return;
  }

  if (command === "help") {
    await reply(env, chatId,
      "<b>Nolane Search commands</b>\n" +
      "<code>/search từ khóa</code> — tìm web nhanh\n" +
      "<code>/tech từ khóa</code> — tìm công nghệ + GitHub\n" +
      "<code>/github từ khóa</code> — tìm repository\n" +
      "<code>/research chủ đề</code> — tìm nghiên cứu và nguồn liên quan\n" +
      "<code>/news chủ đề</code> — tìm tin tức\n" +
      "<code>/deep câu hỏi</code> — tìm nhiều lượt, tổng hợp nguồn bất đồng bộ\n" +
      "<code>/site domain.com từ khóa</code> — giới hạn tìm kiếm vào website\n" +
      "<code>/read https://example.com</code> — đọc nội dung trang bằng TinyFish\n" +
      "<code>/local từ khóa</code> — tìm trong trang đã được index\n" +
      "<code>/watch https://example.com</code> — theo dõi một trang\n" +
      "<code>/watches</code> — danh sách đang theo dõi\n" +
      "<code>/unwatch ID</code> — bỏ theo dõi\n" +
      "<code>/status</code> — trạng thái cấu hình bot\n" +
      "<code>/jobs</code> — lịch sử Deep Search gần đây\n" +
      "<code>/retry ID</code> — chạy lại job thất bại\n" +
      "<code>/id</code> — Telegram ID\n\n" +
      "Gửi văn bản không kèm lệnh cũng được hiểu là tìm web.");
    return;
  }

  if (command === "status") {
    const [watchCount, pageCount, cacheCount, deepJobRows] = await Promise.all([
      env.DB.prepare("SELECT COUNT(*) AS count FROM watches WHERE active = 1").first<{ count: number }>(),
      env.DB.prepare("SELECT COUNT(*) AS count FROM indexed_pages").first<{ count: number }>(),
      env.DB.prepare("SELECT COUNT(*) AS count FROM search_cache WHERE expires_at > ?").bind(Date.now()).first<{ count: number }>(),
      env.DB.prepare("SELECT status, COUNT(*) AS count FROM deep_search_jobs WHERE created_at >= ? GROUP BY status")
        .bind(Date.now() - 7 * 24 * 60 * 60 * 1000).all<{ status: string; count: number }>(),
    ]);
    const jobCounts = new Map(deepJobRows.results.map(row => [row.status, row.count]));
    const jobSummary = ["queued", "running", "completed", "failed"]
      .map(status => jobStatusLabel(status) + ": " + (jobCounts.get(status) ?? 0)).join(" · ");
    await reply(env, chatId,
      "<b>Nolane Search status</b>\n" +
      `Web search: ${env.TAVILY_API_KEY ? "ready" : "missing"}\n` +
      `Semantic search: ${env.EXA_API_KEY ? "ready" : "not configured"}\n` +
      `Backup search: ${env.BRAVE_SEARCH_API_KEY ? "ready" : "not configured"}\n` +
      `TinyFish Search/Fetch: ${env.TINYFISH_API_KEY ? "ready" : "not configured"}\n` +
      `AI synthesis: ${env.OPENROUTER_API_KEY && parseOpenRouterModels(env).length ? `ready (${parseOpenRouterModels(env).length} model(s))` : "not configured"}\n` +
      `Telegram archive: ${env.TELEGRAM_ARCHIVE_CHAT_ID ? "configured" : "not configured"}\n` +
      `Active watches: ${watchCount?.count ?? 0}\n` +
      `Indexed pages: ${pageCount?.count ?? 0}\n` +
      `Cached queries: ${cacheCount?.count ?? 0}\n` +
      `Deep Search (7 days): ${jobSummary}\n\n` +
      "<i>Ready means a secret is configured; it does not guarantee the upstream API is healthy.</i>");
    return;
  }

  if (command === "jobs") {
    const rows = await env.DB.prepare(
      `SELECT id, query, status, attempts, last_error FROM deep_search_jobs WHERE user_id = ? ORDER BY created_at DESC LIMIT 8`,
    ).bind(String(userId)).all<{ id: string; query: string; status: string; attempts: number; last_error: string | null }>();
    if (!rows.results.length) {
      await reply(env, chatId, "Chưa có Deep Search job nào. Dùng <code>/deep câu hỏi</code> để bắt đầu.");
      return;
    }
    const lines = ["<b>Deep Search jobs gần đây</b>"];
    for (const row of rows.results) {
      lines.push(`<code>${htmlEscape(row.id)}</code> · <b>${jobStatusLabel(row.status)}</b> · ${row.attempts} lần thử`);
      lines.push(htmlEscape(row.query.slice(0, 180)));
      if (row.last_error && row.status === "failed") {
        lines.push(`<i>Lỗi: ${htmlEscape(row.last_error.slice(0, 180))}</i>`);
      }
      lines.push("");
    }
    lines.push("Dùng <code>/retry JOB_ID</code> để chạy lại job thất bại.");
    await reply(env, chatId, lines.join("\n"));
    return;
  }
  if (command === "retry") {
    if (!/^[a-f0-9-]{8,80}$/i.test(args)) {
      await reply(env, chatId, "Cú pháp: <code>/retry JOB_ID</code>. Xem ID bằng /jobs.");
      return;
    }
    const previous = await env.DB.prepare(
      "SELECT query, chat_id FROM deep_search_jobs WHERE id = ? AND user_id = ? AND status = 'failed'",
    ).bind(args, String(userId)).first<{ query: string; chat_id: string }>();
    if (!previous) {
      await reply(env, chatId, "Không tìm thấy job thất bại thuộc tài khoản của bạn.");
      return;
    }
    const job: DeepSearchJob = { id: crypto.randomUUID(), chatId: Number(previous.chat_id), userId, query: previous.query, createdAt: Date.now() };
    await env.DB.prepare(
      `INSERT INTO deep_search_jobs (id, chat_id, user_id, query, status, attempts, created_at, updated_at)
       VALUES (?, ?, ?, ?, 'queued', 0, ?, ?)`,
    ).bind(job.id, String(job.chatId), String(userId), job.query, job.createdAt, job.createdAt).run();
    try {
      await env.SEARCH_JOBS.send(job);
    } catch (error) {
      await env.DB.prepare("UPDATE deep_search_jobs SET status = 'failed', last_error = ?, updated_at = ? WHERE id = ?")
        .bind(error instanceof Error ? error.message.slice(0, 300) : "Queue send failed", Date.now(), job.id).run();
      await reply(env, chatId, "Không thể đưa job chạy lại vào Queue. Hãy kiểm tra Cloudflare Queue.");
      return;
    }
    try {
      await reply(env, chatId, `Đã tạo job mới từ truy vấn cũ. Job ID: <code>${job.id}</code>`);
    } catch (error) {
      console.error("Job queued but acknowledgement reply failed:", error instanceof Error ? error.message : "unknown");
    }
    return;
  }
  if (command === "read") {
    const validated = validateWatchUrl(args);
    if (!validated) {
      await reply(env, chatId, "Cú pháp: <code>/read https://example.com</code>. Chỉ hỗ trợ URL HTTPS public hợp lệ.");
      return;
    }
    if (!env.TINYFISH_API_KEY) {
      await reply(env, chatId, "Lệnh /read cần cấu hình GitHub Secret <code>TINYFISH_API_KEY</code> rồi triển khai lại.");
      return;
    }
    try {
      const page = await fetchTinyFishPage(env, validated.url.toString());
      const body = htmlEscape(page.text.slice(0, 5_500));
      await reply(env, chatId, `<b>${htmlEscape(page.title)}</b>\n<a href="${htmlEscape(page.finalUrl)}">Mở trang gốc</a>\n\n<pre>${body}</pre>`);
    } catch (error) {
      console.error("TinyFish read failed:", error instanceof Error ? error.message : "unknown");
      await reply(env, chatId, "TinyFish không thể đọc trang này. Trang có thể chặn truy cập, hết quota hoặc API key chưa hợp lệ.");
    }
    return;
  }

  if (command === "search") return handleSearch(env, chatId, args, "web");
  if (command === "tech") return handleSearch(env, chatId, args, "tech");
  if (command === "github") return handleSearch(env, chatId, args, "github");
  if (command === "research") return handleSearch(env, chatId, args, "research");
  if (command === "news") return handleSearch(env, chatId, args, "news");
  if (command === "local") return handleSearch(env, chatId, args, "local");

  if (command === "site") {
    const [domain, ...queryParts] = args.split(/\s+/);
    const query = queryParts.join(" ").trim();
    if (!domain || !query || !/^[a-z0-9.-]+\.[a-z]{2,}$/i.test(domain)) {
      await reply(env, chatId, "Cú pháp: <code>/site example.com từ khóa</code>");
      return;
    }
    return handleSearch(env, chatId, `site:${domain} ${query}`, "web");
  }

  if (command === "deep") {
    if (!args || args.length > 400) {
      await reply(env, chatId, "Cú pháp: <code>/deep câu hỏi cần nghiên cứu</code> (tối đa 400 ký tự).");
      return;
    }
    const job: DeepSearchJob = {
      id: crypto.randomUUID(), chatId, userId, query: args, createdAt: Date.now(),
    };
    try {
      await env.DB.prepare(
        `INSERT INTO deep_search_jobs (id, chat_id, user_id, query, status, attempts, created_at, updated_at)
         VALUES (?, ?, ?, ?, 'queued', 0, ?, ?)`,
      ).bind(job.id, String(chatId), String(userId), args, job.createdAt, job.createdAt).run();
      await env.SEARCH_JOBS.send(job);
    } catch (error) {
      console.error("Deep Search enqueue failed:", error instanceof Error ? error.message : "unknown");
      await env.DB.prepare("UPDATE deep_search_jobs SET status = 'failed', last_error = ?, updated_at = ? WHERE id = ?")
        .bind(error instanceof Error ? error.message.slice(0, 300) : "Queue send failed", Date.now(), job.id)
        .run().catch(() => undefined);
      await reply(env, chatId, "Không thể tạo Deep Search job. Hãy kiểm tra cấu hình Cloudflare Queue.");
      return;
    }

    const message = `<b>Deep Search đã được xếp hàng.</b>\nJob ID: <code>${job.id}</code>\nMình sẽ chạy nhiều truy vấn, khử trùng lặp và gửi báo cáo vào cuộc trò chuyện này khi hoàn tất.`;
    try {
      await reply(env, chatId, message);
    } catch (error) {
      console.error("Deep Search queued but acknowledgement reply failed:", error instanceof Error ? error.message : "unknown");
    }
    await sendToArchive(env, `<b>Deep Search queued</b>\n${htmlEscape(args)}\nJob: <code>${htmlEscape(job.id)}</code>`);
    return;
  }

  if (command === "watch") {
    const validated = validateWatchUrl(args);
    if (!validated) {
      await reply(env, chatId, "Chỉ nhận URL HTTPS public hợp lệ. Không hỗ trợ IP literal, localhost, cổng tùy chỉnh hoặc URL có thông tin đăng nhập.");
      return;
    }
    try {
      await env.DB.prepare(
        `INSERT INTO watches (chat_id, user_id, url, normalized_url)
         VALUES (?, ?, ?, ?)
         ON CONFLICT(user_id, normalized_url) DO UPDATE SET active = 1`,
      ).bind(String(chatId), String(userId), validated.url.toString(), validated.normalized).run();
      const row = await env.DB.prepare("SELECT id FROM watches WHERE user_id = ? AND normalized_url = ?")
        .bind(String(userId), validated.normalized).first<{ id: number }>();
      const message = `<b>Website đã được thêm vào danh sách theo dõi.</b>\nID: <code>${row?.id ?? "unknown"}</code>\nURL: ${htmlEscape(validated.url.toString())}\nKiểm tra định kỳ khoảng mỗi 30 phút trở lên; đây không phải giám sát thời gian thực.`;
      await reply(env, chatId, message);
      await sendToArchive(env, message);
    } catch (error) {
      console.error("Watch insert failed:", error instanceof Error ? error.message : "unknown");
      await reply(env, chatId, "Không thể lưu watch target. Database migration có thể chưa được áp dụng.");
    }
    return;
  }

  if (command === "watches") {
    const rows = await env.DB.prepare(
      "SELECT id, url, interval_minutes, last_checked_at FROM watches WHERE user_id = ? AND active = 1 ORDER BY id DESC LIMIT 30",
    ).bind(String(userId)).all<{ id: number; url: string; interval_minutes: number; last_checked_at: string | null }>();
    if (!rows.results.length) {
      await reply(env, chatId, "Bạn chưa theo dõi website nào. Dùng <code>/watch https://example.com</code>.");
      return;
    }
    const lines = ["<b>Website đang theo dõi</b>"];
    for (const row of rows.results) {
      lines.push(`<code>${row.id}</code> · <a href="${htmlEscape(row.url)}">${htmlEscape(new URL(row.url).hostname)}</a> · mỗi ${row.interval_minutes} phút`);
    }
    await reply(env, chatId, lines.join("\n"));
    return;
  }

  if (command === "unwatch") {
    const id = Number(args);
    if (!Number.isInteger(id) || id <= 0) {
      await reply(env, chatId, "Cú pháp: <code>/unwatch ID</code>. Xem ID bằng /watches.");
      return;
    }
    const result = await env.DB.prepare("UPDATE watches SET active = 0 WHERE id = ? AND user_id = ?")
      .bind(id, String(userId)).run();
    await reply(env, chatId, (result.meta?.changes ?? 0) > 0 ? "Đã ngừng theo dõi website." : "Không tìm thấy watch ID này.");
    return;
  }

  await reply(env, chatId, "Không nhận diện được lệnh. Gõ /help để xem các chức năng.");
}

async function processUpdate(env: Env, update: TelegramUpdate): Promise<void> {
  if (!(await recordUpdate(env, update.update_id))) return;
  const message = update.message;
  if (!message?.text || !message.from) return;
  await handleCommand(env, message.chat.id, message.from.id, message.text);
}

async function processDeepJob(env: Env, job: DeepSearchJob): Promise<void> {
  const now = Date.now();
  await env.DB.prepare(
    `INSERT OR IGNORE INTO deep_search_jobs
      (id, chat_id, user_id, query, status, attempts, created_at, updated_at)
     VALUES (?, ?, ?, ?, 'queued', 0, ?, ?)`,
  ).bind(job.id, String(job.chatId), String(job.userId), job.query, job.createdAt, now).run();
  const claimed = await env.DB.prepare(
    `UPDATE deep_search_jobs SET status = 'running', attempts = attempts + 1, updated_at = ?, last_error = NULL
      WHERE id = ? AND (status = 'queued' OR (status = 'running' AND updated_at <= ?))`,
  ).bind(now, job.id, now - 15 * 60 * 1000).run();
  if ((claimed.meta?.changes ?? 0) === 0) return;
  try {
    const results = await performDeepSearch(env, job.query);
    const summary = await fetchOpenRouterSummary(env, job.query, results);
    const report = formatDeepReport(job.query, results, summary);
    await sendTelegram(env, job.chatId, report);
    await sendToArchive(env, `<b>Deep Search archive</b>\nJob: <code>${htmlEscape(job.id)}</code>\n${report}`);
    const completedAt = Date.now();
    await env.DB.prepare(
      "UPDATE deep_search_jobs SET status = 'completed', updated_at = ?, completed_at = ?, last_error = NULL WHERE id = ?",
    ).bind(completedAt, completedAt, job.id).run();
  } catch (error) {
    const reason = error instanceof Error ? error.message.slice(0, 300) : "Unknown Deep Search error";
    await env.DB.prepare(
      "UPDATE deep_search_jobs SET status = 'queued', updated_at = ?, last_error = ? WHERE id = ? AND status = 'running'",
    ).bind(Date.now(), reason, job.id).run();
    throw error;
  }
}
async function notifyDeadLetter(env: Env, job: DeepSearchJob): Promise<void> {
  const row = await env.DB.prepare("SELECT status FROM deep_search_jobs WHERE id = ?")
    .bind(job.id).first<{ status: string }>();
  if (row?.status === "completed" || row?.status === "failed") return;
  await env.DB.prepare(
    "UPDATE deep_search_jobs SET status = 'failed', updated_at = ?, last_error = 'Delivery retries exhausted' WHERE id = ?",
  ).bind(Date.now(), job.id).run();
  const notice = `Deep Search job <code>${htmlEscape(job.id)}</code> đã thất bại sau nhiều lần thử.\nBạn có thể xem trong /jobs và chạy lại bằng /retry JOB_ID.`;
  try { await sendTelegram(env, job.chatId, notice); }
  catch (error) { console.error("Dead-letter user notification failed:", error instanceof Error ? error.message : "unknown"); }
  await sendToArchive(env, `<b>Deep Search dead-letter</b>\n${notice}`);
}

async function recoverStaleDeepJobs(env: Env): Promise<number> {
  const cutoff = Date.now() - 10 * 60 * 1000;
  const stale = await env.DB.prepare(
    `SELECT id, chat_id, user_id, query, created_at, status, updated_at
       FROM deep_search_jobs
      WHERE status IN ('queued', 'running') AND updated_at <= ?
      ORDER BY updated_at ASC
      LIMIT 10`,
  ).bind(cutoff).all<{
    id: string;
    chat_id: string;
    user_id: string;
    query: string;
    created_at: number;
    status: "queued" | "running";
    updated_at: number;
  }>();

  let recovered = 0;
  for (const row of stale.results) {
    const now = Date.now();
    const claim = await env.DB.prepare(
      `UPDATE deep_search_jobs
          SET status = 'queued', updated_at = ?,
              last_error = CASE
                WHEN status = 'running' THEN 'Recovered after an interrupted or stale Queue delivery'
                ELSE last_error
              END
        WHERE id = ? AND status = ? AND updated_at = ?`,
    ).bind(now, row.id, row.status, row.updated_at).run();

    if ((claim.meta?.changes ?? 0) === 0) continue;

    const job: DeepSearchJob = {
      id: row.id,
      chatId: Number(row.chat_id),
      userId: Number(row.user_id),
      query: row.query,
      createdAt: row.created_at,
    };
    try {
      await env.SEARCH_JOBS.send(job);
      recovered += 1;
    } catch (error) {
      const reason = error instanceof Error ? error.message.slice(0, 300) : "Queue recovery send failed";
      await env.DB.prepare(
        "UPDATE deep_search_jobs SET status = 'failed', last_error = ?, updated_at = ? WHERE id = ? AND status = 'queued'",
      ).bind(reason, Date.now(), row.id).run();
      console.error("Stale Deep Search recovery failed", row.id, reason);
    }
  }
  return recovered;
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/health") {
      try {
        await env.DB.prepare("SELECT 1 AS ok").first();
        return Response.json({
          ok: true,
          service: "nolane-search",
          version: "0.1.0",
          database: "reachable",
          providers: {
            tavily: Boolean(env.TAVILY_API_KEY),
            exa: Boolean(env.EXA_API_KEY),
            brave: Boolean(env.BRAVE_SEARCH_API_KEY),
            tinyfish: Boolean(env.TINYFISH_API_KEY),
            github: true,
            openrouter: Boolean(env.OPENROUTER_API_KEY && parseOpenRouterModels(env).length),
            openrouterModels: parseOpenRouterModels(env).length,
          },
          archiveEnabled: Boolean(env.TELEGRAM_ARCHIVE_CHAT_ID),
        });
      } catch {
        return Response.json({ ok: false, service: "nolane-search", database: "unavailable" }, { status: 503 });
      }
    }
    if (request.method === "GET" && url.pathname === "/") {
      return new Response("Nolane Search API · Telegram-first hybrid search. See /health.", {
        headers: { "content-type": "text/plain; charset=utf-8" },
      });
    }
    if (request.method === "POST" && url.pathname === "/telegram/webhook") {
      const supplied = request.headers.get("x-telegram-bot-api-secret-token") || "";
      if (!env.TELEGRAM_WEBHOOK_SECRET || !constantTimeEqual(supplied, env.TELEGRAM_WEBHOOK_SECRET)) {
        return new Response("Unauthorized", { status: 401 });
      }
      let update: TelegramUpdate;
      try { update = await request.json() as TelegramUpdate; }
      catch { return new Response("Invalid JSON", { status: 400 }); }
      ctx.waitUntil(processUpdate(env, update).catch((error) => {
        console.error("Telegram update processing failed:", error instanceof Error ? error.message : "unknown");
      }));
      return new Response("OK");
    }
    return new Response("Not found", { status: 404 });
  },

  async queue(batch: MessageBatch<DeepSearchJob>, env: Env): Promise<void> {
    for (const message of batch.messages) {
      const job = message.body;
      if (!isDeepSearchJob(job)) {
        console.error("Discarding malformed Deep Search queue message.");
        message.ack();
        continue;
      }
      if (batch.queue === "nolane-search-dlq") {
        try { await notifyDeadLetter(env, job); message.ack(); }
        catch (error) {
          console.error("Dead-letter handling failed:", error instanceof Error ? error.message : "unknown");
          message.retry({ delaySeconds: 60 });
        }
        continue;
      }
      try { await processDeepJob(env, job); message.ack(); }
      catch (error) {
        console.error("Deep Search queue attempt failed:", error instanceof Error ? error.message : "unknown");
        message.retry({ delaySeconds: Math.min(300, 15 * (2 ** Math.max(0, message.attempts - 1))) });
      }
    }
  },

  async scheduled(_controller: { cron: string; scheduledTime: number }, env: Env): Promise<void> {
    try {
      const recovered = await recoverStaleDeepJobs(env);
      const stats = await checkWatchTargets(env);
      await env.DB.prepare("DELETE FROM search_cache WHERE expires_at <= ?").bind(Date.now()).run();
      await env.DB.prepare("DELETE FROM telegram_updates WHERE processed_at < datetime('now', '-7 days')").run();
      await env.DB.prepare(
        "DELETE FROM deep_search_jobs WHERE status IN ('completed', 'failed') AND created_at < ?",
      ).bind(Date.now() - 30 * 24 * 60 * 60 * 1000).run();
      if (recovered) console.log("Recovered stale Deep Search jobs", recovered);
      if (stats.checked) console.log("Watch run complete", stats);
    } catch (error) {
      console.error("Scheduled maintenance failed:", error instanceof Error ? error.message : "unknown");
    }
  },
};
