import { constantTimeEqual, htmlEscape } from "./security";
import { performDeepSearch, performSearch } from "./search";
import { fetchOpenRouterSummary } from "./providers";
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
      "<code>/local từ khóa</code> — tìm trong trang đã được index\n" +
      "<code>/watch https://example.com</code> — theo dõi một trang\n" +
      "<code>/watches</code> — danh sách đang theo dõi\n" +
      "<code>/unwatch ID</code> — bỏ theo dõi\n" +
      "<code>/status</code> — trạng thái cấu hình bot\n" +
      "<code>/id</code> — Telegram ID\n\n" +
      "Gửi văn bản không kèm lệnh cũng được hiểu là tìm web.");
    return;
  }

  if (command === "status") {
    const [watchCount, pageCount, cacheCount] = await Promise.all([
      env.DB.prepare("SELECT COUNT(*) AS count FROM watches WHERE active = 1").first<{ count: number }>(),
      env.DB.prepare("SELECT COUNT(*) AS count FROM indexed_pages").first<{ count: number }>(),
      env.DB.prepare("SELECT COUNT(*) AS count FROM search_cache WHERE expires_at > ?").bind(Date.now()).first<{ count: number }>(),
    ]);
    await reply(env, chatId,
      "<b>Nolane Search status</b>\n" +
      `Web search: ${env.TAVILY_API_KEY ? "ready" : "missing"}\n` +
      `Semantic search: ${env.EXA_API_KEY ? "ready" : "not configured"}\n` +
      `Backup search: ${env.BRAVE_SEARCH_API_KEY ? "ready" : "not configured"}\n` +
      `AI synthesis: ${env.OPENROUTER_API_KEY && env.OPENROUTER_MODEL ? "ready" : "not configured"}\n` +
      `Telegram archive: ${env.TELEGRAM_ARCHIVE_CHAT_ID ? "configured" : "not configured"}\n` +
      `Active watches: ${watchCount?.count ?? 0}\n` +
      `Indexed pages: ${pageCount?.count ?? 0}\n` +
      `Cached queries: ${cacheCount?.count ?? 0}\n\n` +
      "<i>Ready means a secret is configured; it does not guarantee the upstream API is healthy.</i>");
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
      await env.SEARCH_JOBS.send(job);
      const message = "<b>Deep Search đã được xếp hàng.</b>\nMình sẽ chạy nhiều truy vấn, khử trùng lặp và gửi báo cáo vào cuộc trò chuyện này khi hoàn tất.";
      await reply(env, chatId, message);
      await sendToArchive(env, `<b>Deep Search queued</b>\n${htmlEscape(args)}\nJob: <code>${job.id}</code>`);
    } catch (error) {
      console.error("Queue send failed:", error instanceof Error ? error.message : "unknown");
      await reply(env, chatId, "Không thể tạo Deep Search job. Hãy kiểm tra cấu hình Cloudflare Queue.");
    }
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
  try {
    const results = await performDeepSearch(env, job.query);
    const summary = await fetchOpenRouterSummary(env, job.query, results);
    const report = formatDeepReport(job.query, results, summary);
    await sendTelegram(env, job.chatId, report);
    await sendToArchive(env, `<b>Deep Search archive</b>\nJob: <code>${job.id}</code>\n${report}`);
  } catch (error) {
    console.error("Deep Search job failed:", error instanceof Error ? error.message : "unknown");
    await sendTelegram(env, job.chatId, "Deep Search gặp lỗi khi truy xuất nguồn. Không có báo cáo hoàn chỉnh được tạo; hãy thử lại sau.");
  }
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
            github: true,
            openrouter: Boolean(env.OPENROUTER_API_KEY && env.OPENROUTER_MODEL),
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
      await processDeepJob(env, message.body);
      message.ack();
    }
  },

  async scheduled(_controller: { cron: string; scheduledTime: number }, env: Env): Promise<void> {
    try {
      const stats = await checkWatchTargets(env);
      await env.DB.prepare("DELETE FROM search_cache WHERE expires_at <= ?").bind(Date.now()).run();
      await env.DB.prepare("DELETE FROM telegram_updates WHERE processed_at < datetime('now', '-7 days')").run();
      if (stats.checked) console.log("Watch run complete", stats);
    } catch (error) {
      console.error("Scheduled maintenance failed:", error instanceof Error ? error.message : "unknown");
    }
  },
};
