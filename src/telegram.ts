import { htmlEscape } from "./security";
import { readJsonResponse } from "./http";
import type { Env, SearchMode, SearchResult } from "./types";
import { getTool, toolCategoryLabel } from "./tools";
import type { ToolCategory, ToolDefinition } from "./tools";
import type { ToolJob } from "./tool-jobs";

const MAX_FORMATTED_LENGTH = 3600;

export async function telegramApi<T = Record<string, unknown>>(env: Env, method: string, body: Record<string, unknown>): Promise<T> {
  if (!env.TELEGRAM_BOT_TOKEN) throw new Error("TELEGRAM_BOT_TOKEN is not configured");
  const response = await fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/${method}`, {
    method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body),
    signal: AbortSignal.timeout(15_000),
  });
  const data = await readJsonResponse<{ ok?: boolean; description?: string; result?: T }>(response, 1_000_000);
  if (!response.ok || !data.ok) throw new Error(data.description || `Telegram API error (${response.status})`);
  return data.result as T;
}

export interface TelegramInlineButton { text: string; callback_data?: string; url?: string; }
export interface TelegramInlineKeyboardMarkup { inline_keyboard: Array<Array<TelegramInlineButton>>; }

export async function sendSearchPage(
  env: Env,
  chatId: number | string,
  text: string,
  replyMarkup?: TelegramInlineKeyboardMarkup,
): Promise<void> {
  await telegramApi(env, "sendMessage", {
    chat_id: chatId, text, parse_mode: "HTML", disable_web_page_preview: true,
    ...(replyMarkup ? { reply_markup: replyMarkup } : {}),
  });
}

export async function sendTelegram(env: Env, chatId: number | string, text: string): Promise<void> {
  const max = 3800;
  const chunks: string[] = [];
  let remaining = text;
  while (remaining.length > max) {
    let splitAt = remaining.lastIndexOf("\n", max);
    if (splitAt < max * 0.6) splitAt = max;
    chunks.push(remaining.slice(0, splitAt));
    remaining = remaining.slice(splitAt).trimStart();
  }
  if (remaining) chunks.push(remaining);
  for (const chunk of chunks) {
    await telegramApi(env, "sendMessage", {
      chat_id: chatId, text: chunk, parse_mode: "HTML", disable_web_page_preview: true,
    });
  }
}

export async function sendToArchive(env: Env, text: string): Promise<void> {
  if (!env.TELEGRAM_ARCHIVE_CHAT_ID) return;
  try { await sendTelegram(env, env.TELEGRAM_ARCHIVE_CHAT_ID, text); }
  catch (error) { console.error("Telegram archive delivery failed:", error instanceof Error ? error.message : "unknown error"); }
}

export async function sendArchiveDocument(env: Env, filename: string, content: string, caption: string): Promise<void> {
  if (!env.TELEGRAM_ARCHIVE_CHAT_ID || !env.TELEGRAM_BOT_TOKEN) return;
  const form = new FormData();
  form.set("chat_id", env.TELEGRAM_ARCHIVE_CHAT_ID);
  form.set("caption", caption.slice(0, 900));
  form.set("document", new Blob([content], { type: "text/plain;charset=utf-8" }), filename);
  const response = await fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendDocument`, {
    method: "POST", body: form, signal: AbortSignal.timeout(20_000),
  });
  const data = await readJsonResponse<{ ok?: boolean; description?: string }>(response, 1_000_000);
  if (!response.ok || !data.ok) throw new Error(data.description || `Telegram sendDocument failed (${response.status})`);
}

export type TelegramInputMode = SearchMode | "ai" | "ask" | "deep";

const INPUT_MODE_LABELS: Record<TelegramInputMode, string> = {
  web: "Web Search", tech: "Technology Search", research: "Research",
  news: "News", github: "GitHub", wiki: "Wikipedia", local: "Website riêng",
  ai: "AI Chat", ask: "AI trả lời có nguồn", deep: "Deep Research",
};

export function formatHomeMenu(firstName = ""): string {
  const greeting = firstName.trim() ? "Chào " + safeHtmlText(firstName.trim(), 70) + "!" : "Xin chào!";
  return [
    "<b>◈ NOLANE SEARCH</b>",
    "<i>Personal Search & AI Workspace</i>",
    "",
    "<b>" + greeting + "</b>",
    "Tìm kiếm web, nghiên cứu nhiều nguồn, hỏi AI và tra cứu website riêng ngay trong cuộc trò chuyện này.",
    "",
    "<b>Chọn một công cụ bên dưới</b>",
    "<i>Chạm vào chế độ → gửi câu hỏi. Không cần nhớ cú pháp lệnh.</i>",
  ].join("\n");
}

export function buildHomeKeyboard(webAppUrl = "https://nolane-search.nolane-file.workers.dev/"): TelegramInlineKeyboardMarkup {
  return { inline_keyboard: [
    [{ text: "🔎 Web Search", callback_data: "ui:mode:web" }, { text: "🧠 AI có nguồn", callback_data: "ui:mode:ask" }],
    [{ text: "⚡ AI Chat", callback_data: "ui:mode:ai" }, { text: "📚 Deep Research", callback_data: "ui:mode:deep" }],
    [{ text: "💻 Công nghệ", callback_data: "ui:mode:tech" }, { text: "📰 Tin tức", callback_data: "ui:mode:news" }],
    [{ text: "🐙 GitHub", callback_data: "ui:mode:github" }, { text: "📖 Wikipedia", callback_data: "ui:mode:wiki" }],
    [{ text: "🔬 Nghiên cứu", callback_data: "ui:mode:research" }, { text: "🗂 Website riêng", callback_data: "ui:mode:local" }],
    [{ text: "🌐 Mở Web Workspace", url: webAppUrl }],
    [{ text: "🧰 Tool Center", callback_data: "tc:home" }],
    [{ text: "📊 Trạng thái", callback_data: "ui:status" }, { text: "❔ Hướng dẫn", callback_data: "ui:help" }],
  ] };
}

export function formatModePrompt(mode: TelegramInputMode): string {
  return [
    "<b>◈ NOLANE SEARCH · " + INPUT_MODE_LABELS[mode] + "</b>",
    "",
    "Gửi câu hỏi hoặc từ khóa của bạn trong tin nhắn tiếp theo.",
    "Mình sẽ xử lý bằng chế độ <b>" + INPUT_MODE_LABELS[mode] + "</b>.",
    "",
    "<i>Lựa chọn này tự hết hạn sau 10 phút. Bạn có thể đổi chế độ bất cứ lúc nào.</i>",
  ].join("\n");
}

export function buildModePromptKeyboard(): TelegramInlineKeyboardMarkup {
  return { inline_keyboard: [[
    { text: "✕ Huỷ lựa chọn", callback_data: "ui:cancel" },
    { text: "⌂ Menu chính", callback_data: "ui:home" },
  ]] };
}

export function buildBackHomeKeyboard(): TelegramInlineKeyboardMarkup {
  return { inline_keyboard: [[{ text: "⌂ Menu chính", callback_data: "ui:home" }]] };
}
const MODE_LABELS: Record<SearchMode, string> = {
  web: "Web Search", tech: "Technology Search", research: "Research Search",
  news: "News Search", github: "GitHub Search", wiki: "Wikipedia Reference", local: "My Sites Index",
};

// Limit escaped output, not raw input: HTML entities can expand substantially.
function safeHtmlText(value: string, maxEscapedLength: number): string {
  let output = "";
  let truncated = false;
  for (const character of value) {
    const escaped = htmlEscape(character);
    if (output.length + escaped.length > maxEscapedLength) { truncated = true; break; }
    output += escaped;
  }
  return truncated ? output + "…" : output;
}

function appendBlock(output: string, block: string, footer: string): string {
  const next = output + "\n\n" + block;
  return next.length + footer.length + 2 <= MAX_FORMATTED_LENGTH ? next : output;
}

export const SEARCH_PAGE_SIZE = 5;

export function buildSearchKeyboard(
  sessionId: string,
  page: number,
  totalResults: number,
): TelegramInlineKeyboardMarkup {
  const totalPages = Math.max(1, Math.ceil(totalResults / SEARCH_PAGE_SIZE));
  const currentPage = Math.max(0, Math.min(totalPages - 1, page));
  const rows: TelegramInlineButton[][] = [];
  if (totalPages > 1) {
    const row: TelegramInlineButton[] = [];
    if (currentPage > 0) row.push({ text: "⬅️ Trước", callback_data: "ns:" + sessionId + ":" + (currentPage - 1) });
    row.push({ text: (currentPage + 1) + "/" + totalPages, callback_data: "ns:" + sessionId + ":" + currentPage });
    if (currentPage < totalPages - 1) row.push({ text: "Tiếp ➡️", callback_data: "ns:" + sessionId + ":" + (currentPage + 1) });
    rows.push(row);
  }
  rows.push([
    { text: "🤖 Hỏi AI có nguồn", callback_data: "na:ask:" + sessionId },
    { text: "📚 Deep Search", callback_data: "na:deep:" + sessionId },
  ]);
  rows.push([{ text: "⌂ Menu chính", callback_data: "ui:home" }]);
  return { inline_keyboard: rows };
}

export function formatSearchResults(
  query: string,
  mode: SearchMode,
  results: SearchResult[],
  page = 0,
  pageSize = SEARCH_PAGE_SIZE,
): string {
  if (!results.length) {
    return `<b>Nolane Search</b>\nKhông tìm thấy kết quả phù hợp cho: <code>${safeHtmlText(query, 260)}</code>`;
  }
  const size = Math.max(1, Math.min(20, Math.floor(pageSize)));
  const totalPages = Math.max(1, Math.ceil(results.length / size));
  const currentPage = Math.max(0, Math.min(totalPages - 1, Math.floor(page)));
  const start = currentPage * size;
  const pageResults = results.slice(start, start + size);
  let output = [
    `<b>Nolane Search · ${MODE_LABELS[mode]}</b>`,
    `<i>${safeHtmlText(query, 260)}</i>`,
    `Kết quả ${start + 1}–${start + pageResults.length} / ${results.length} · Trang ${currentPage + 1}/${totalPages}`,
  ].join("\n");
  const footer = "<i>Điểm xếp hạng là heuristic nội bộ, không phải xác suất độ đúng.</i>";
  for (const [index, item] of pageResults.entries()) {
    const resultNumber = start + index + 1;
    const block = [
      `<b>${resultNumber}. <a href="${htmlEscape(item.url)}">${safeHtmlText(item.title, 150)}</a></b>`,
      safeHtmlText(item.snippet, 230),
      `<code>${safeHtmlText(item.domain, 90)}</code> · ${safeHtmlText(item.provider, 50)}`,
    ].join("\n");
    const next = appendBlock(output, block, footer);
    if (next === output) break;
    output = next;
  }
  return output + "\n\n" + footer;
}

export function formatDeepReport(query: string, results: SearchResult[], summary: string | null): string {
  let output = [
    "<b>Nolane Search · Deep Search</b>",
    `<i>${safeHtmlText(query, 240)}</i>`,
    `Đã tổng hợp ${results.length} kết quả duy nhất từ nhiều lượt truy vấn.`,
  ].join("\n");
  const footer = "<i>Deep Search là tổng hợp các nguồn truy xuất được; không bảo đảm bao quát toàn bộ tài liệu hiện có.</i>";
  if (summary) {
    output = appendBlock(output, `<b>Tổng hợp AI</b>\n${safeHtmlText(summary, 1050)}`, footer);
  } else {
    output = appendBlock(output, "<b>Evidence digest</b>\nChưa bật AI synthesis. Dưới đây là các nguồn thu thập được; hãy mở nguồn để tự kiểm chứng.", footer);
  }
  for (const [index, item] of results.slice(0, 7).entries()) {
    const block = [
      `<b>${index + 1}. <a href="${htmlEscape(item.url)}">${safeHtmlText(item.title, 145)}</a></b>`,
      safeHtmlText(item.snippet, 190),
      `<code>${safeHtmlText(item.domain, 90)}</code> · ${safeHtmlText(item.provider, 45)}`,
    ].join("\n");
    const next = appendBlock(output, block, footer);
    if (next === output) break;
    output = next;
  }
  return output + "\n\n" + footer;
}


export const TOOL_CENTER_PAGE_SIZE = 8;

const TOOL_CENTER_CATEGORIES: ToolCategory[] = [
  "image", "document", "audio-video", "data", "developer", "repository", "utility",
];

function toolCategoryItems(tools: ToolDefinition[], category: ToolCategory): ToolDefinition[] {
  return tools.filter(tool => tool.category === category && tool.ready);
}

export function formatToolCenterHome(tools: ToolDefinition[], configured: boolean): string {
  const ready = tools.filter(tool => tool.ready);
  const categories = TOOL_CENTER_CATEGORIES
    .map(category => ({ category, count: toolCategoryItems(ready, category).length }))
    .filter(item => item.count > 0);
  return [
    "<b>◈ NOLANE TOOL CENTER</b>",
    "<i>" + ready.length + " processor đang có trong catalog · " + categories.length + " danh mục</i>",
    "",
    ...categories.map(item => "<b>" + htmlEscape(toolCategoryLabel(item.category)) + "</b> · " + item.count + " tool"),
    "",
    configured
      ? "Runner đã được cấu hình. Chọn danh mục để duyệt, mở chi tiết rồi bấm <b>Dùng tool</b> và gửi tệp."
      : "⚠️ Runner chưa sẵn sàng: cần cấu hình GitHub Actions token trước khi chạy tệp.",
    "",
    "<code>/tool_search từ khóa</code> · tìm theo tên, mô tả, định dạng",
    "<code>/tool_jobs</code> · lịch sử và trạng thái",
    "<code>/workflows</code> · workflow đã lưu · <code>/workflow_plan</code> · AI lập quy trình",
  ].join("\n");
}

export function buildToolCenterKeyboard(tools: ToolDefinition[]): TelegramInlineKeyboardMarkup {
  const rows: TelegramInlineButton[][] = [];
  const populated = TOOL_CENTER_CATEGORIES.filter(category => toolCategoryItems(tools, category).length > 0);
  for (let index = 0; index < populated.length; index += 2) {
    rows.push(populated.slice(index, index + 2).map(category => ({
      text: toolCategoryLabel(category) + " · " + toolCategoryItems(tools, category).length,
      callback_data: "tc:" + category,
    })));
  }
  rows.push([
    { text: "🧾 Tác vụ gần đây", callback_data: "tc:jobs" },
    { text: "🧩 Workflow", callback_data: "tc:workflows" },
  ]);
  rows.push([{ text: "⌂ Menu chính", callback_data: "ui:home" }]);
  return { inline_keyboard: rows };
}

export function formatToolCategoryPage(tools: ToolDefinition[], category: ToolCategory, page = 0): string {
  const items = toolCategoryItems(tools, category);
  const totalPages = Math.max(1, Math.ceil(items.length / TOOL_CENTER_PAGE_SIZE));
  const currentPage = Math.max(0, Math.min(totalPages - 1, Math.floor(page)));
  const start = currentPage * TOOL_CENTER_PAGE_SIZE;
  const visible = items.slice(start, start + TOOL_CENTER_PAGE_SIZE);
  return [
    "<b>◈ " + htmlEscape(toolCategoryLabel(category)) + "</b>",
    "Danh mục có " + items.length + " tool · Trang " + (currentPage + 1) + "/" + totalPages,
    "",
    ...visible.map((tool, index) =>
      (start + index + 1) + ". <b>" + htmlEscape(tool.name) + "</b>\n<code>" + htmlEscape(tool.id) + "</code> · " +
      htmlEscape(tool.output) + "\n" + htmlEscape(tool.description.slice(0, 115))),
    "",
    "<i>Chạm vào tool để xem định dạng đầu vào, đầu ra và xác nhận chạy.</i>",
  ].join("\n");
}

export function buildToolCategoryKeyboard(tools: ToolDefinition[], category: ToolCategory, page = 0): TelegramInlineKeyboardMarkup {
  const items = toolCategoryItems(tools, category);
  const totalPages = Math.max(1, Math.ceil(items.length / TOOL_CENTER_PAGE_SIZE));
  const currentPage = Math.max(0, Math.min(totalPages - 1, Math.floor(page)));
  const start = currentPage * TOOL_CENTER_PAGE_SIZE;
  const visible = items.slice(start, start + TOOL_CENTER_PAGE_SIZE);
  const rows: TelegramInlineButton[][] = [];
  for (let index = 0; index < visible.length; index += 2) {
    rows.push(visible.slice(index, index + 2).map(tool => ({
      text: tool.name.length > 25 ? tool.name.slice(0, 24) + "…" : tool.name,
      callback_data: "td:" + tool.id,
    })));
  }
  if (totalPages > 1) {
    const navigation: TelegramInlineButton[] = [];
    if (currentPage > 0) navigation.push({ text: "⬅️ Trước", callback_data: "tp:" + category + ":" + (currentPage - 1) });
    navigation.push({ text: (currentPage + 1) + "/" + totalPages, callback_data: "tp:" + category + ":" + currentPage });
    if (currentPage < totalPages - 1) navigation.push({ text: "Tiếp ➡️", callback_data: "tp:" + category + ":" + (currentPage + 1) });
    rows.push(navigation);
  }
  rows.push([{ text: "↩️ Tất cả danh mục", callback_data: "tc:home" }]);
  return { inline_keyboard: rows };
}

export function formatToolDetail(tool: ToolDefinition): string {
  return [
    "<b>◈ " + htmlEscape(tool.name) + "</b>",
    "<code>" + htmlEscape(tool.id) + "</code> · " + htmlEscape(toolCategoryLabel(tool.category)),
    "",
    htmlEscape(tool.description),
    "",
    "<b>Đầu vào</b>",
    htmlEscape(tool.accepts.join(", ")),
    "",
    "<b>Đầu ra</b>",
    htmlEscape(tool.output),
    "",
    "<i>Chọn Dùng tool để chờ tệp tiếp theo trong 15 phút. Tệp sẽ được xử lý trên GitHub-hosted runner dùng một lần.</i>",
  ].join("\n");
}

export function buildToolDetailKeyboard(tool: ToolDefinition): TelegramInlineKeyboardMarkup {
  return { inline_keyboard: [
    [{ text: "▶️ Dùng tool này", callback_data: "tu:" + tool.id }],
    [{ text: "↩️ " + toolCategoryLabel(tool.category), callback_data: "tc:" + tool.category }, { text: "⌂ Tool Center", callback_data: "tc:home" }],
  ] };
}

export function formatToolSearchResults(tools: ToolDefinition[], query: string): string {
  return [
    "<b>◈ Tìm tool · " + tools.length + " kết quả</b>",
    "<i>" + htmlEscape(query.slice(0, 100)) + "</i>",
    "",
    ...tools.slice(0, 12).map((tool, index) =>
      (index + 1) + ". <b>" + htmlEscape(tool.name) + "</b> · <code>" + htmlEscape(tool.id) + "</code>\n" +
      htmlEscape(toolCategoryLabel(tool.category)) + " · " + htmlEscape(tool.output)),
    "",
    "<i>Chạm vào kết quả để xem chi tiết.</i>",
  ].join("\n");
}

export function buildToolSearchKeyboard(tools: ToolDefinition[]): TelegramInlineKeyboardMarkup {
  const rows: TelegramInlineButton[][] = [];
  const visible = tools.slice(0, 12);
  for (let index = 0; index < visible.length; index += 2) {
    rows.push(visible.slice(index, index + 2).map(tool => ({
      text: tool.name.length > 25 ? tool.name.slice(0, 24) + "…" : tool.name,
      callback_data: "td:" + tool.id,
    })));
  }
  rows.push([{ text: "↩️ Tool Center", callback_data: "tc:home" }]);
  return { inline_keyboard: rows };
}


export const TOOL_JOBS_PAGE_SIZE = 5;

function toolJobStatus(job: ToolJob): string {
  return job.status === "completed" ? "✅ Hoàn thành" :
    job.status === "failed" ? "❌ Thất bại" :
    job.status === "running" ? "⚙️ Đang chạy" : "⏳ Đang chờ";
}

function toolJobProgressLabel(job: ToolJob): string {
  const progress = job.progress;
  if (progress) {
    const current = progress.currentToolIds.map(id => getToolLabel(id)).filter(Boolean);
    return "Tiến trình: " + progress.completed + "/" + progress.total +
      (current.length ? " · Đang chạy: " + current.join(", ") : " bước đã xong");
  }
  if (job.trace?.length) return "Trace: " + job.trace.length + "/" + (job.workflowDag?.length || job.pipeline?.length || 1) + " bước";
  return job.status === "running" ? "Runner đang khởi tạo hoặc chưa gửi checkpoint." : "Chưa có checkpoint.";
}

function getToolLabel(id: string): string {
  return getTool(id)?.name || id;
}

export function formatToolJobsPage(jobs: ToolJob[], page = 0): string {
  const totalPages = Math.max(1, Math.ceil(jobs.length / TOOL_JOBS_PAGE_SIZE));
  const currentPage = Math.max(0, Math.min(totalPages - 1, Math.floor(page)));
  const start = currentPage * TOOL_JOBS_PAGE_SIZE;
  const visible = jobs.slice(start, start + TOOL_JOBS_PAGE_SIZE);
  return [
    "<b>◈ NOLANE · JOB CENTER</b>",
    "Tổng " + jobs.length + " tác vụ gần đây · Trang " + (currentPage + 1) + "/" + totalPages,
    "",
    ...(visible.length ? visible.map((job, index) => {
      const title = getToolLabel(job.toolId);
      const attempt = job.attempt && job.attempt > 1 ? " · Retry " + job.attempt : "";
      return (start + index + 1) + ". " + toolJobStatus(job) + " · <b>" + htmlEscape(title) + "</b>" + attempt +
        "\n<code>" + htmlEscape(job.id) + "</code> · " + htmlEscape(job.fileName.slice(0, 90)) +
        "\n<i>" + htmlEscape(toolJobProgressLabel(job)) + "</i>";
    }) : ["Chưa có job nào. Dùng /tools để chọn một công cụ và gửi tệp."]),
    "",
    "<i>Chạm vào một tác vụ để xem tiến trình, trace, kết quả và thao tác retry.</i>",
  ].flat().join("\n");
}

export function buildToolJobsKeyboard(jobs: ToolJob[], page = 0): TelegramInlineKeyboardMarkup {
  const totalPages = Math.max(1, Math.ceil(jobs.length / TOOL_JOBS_PAGE_SIZE));
  const currentPage = Math.max(0, Math.min(totalPages - 1, Math.floor(page)));
  const start = currentPage * TOOL_JOBS_PAGE_SIZE;
  const visible = jobs.slice(start, start + TOOL_JOBS_PAGE_SIZE);
  const rows: TelegramInlineButton[][] = visible.map(job => [{
    text: (job.status === "completed" ? "✅ " : job.status === "failed" ? "❌ " : job.status === "running" ? "⚙️ " : "⏳ ") +
      (job.toolId.length > 24 ? job.toolId.slice(0, 23) + "…" : job.toolId),
    callback_data: "tjv:" + job.id + ":" + currentPage,
  }]);
  if (totalPages > 1) {
    const nav: TelegramInlineButton[] = [];
    if (currentPage > 0) nav.push({ text: "⬅️ Trước", callback_data: "tjp:" + (currentPage - 1) });
    nav.push({ text: (currentPage + 1) + "/" + totalPages, callback_data: "tjp:" + currentPage });
    if (currentPage < totalPages - 1) nav.push({ text: "Tiếp ➡️", callback_data: "tjp:" + (currentPage + 1) });
    rows.push(nav);
  }
  rows.push([
    { text: "↻ Làm mới", callback_data: "tjrlist:" + currentPage },
    { text: "🧰 Tool Center", callback_data: "tc:home" },
  ]);
  return { inline_keyboard: rows };
}

export function formatToolJobDetail(job: ToolJob): string {
  const state = toolJobStatus(job);
  const total = job.workflowDag?.length || job.pipeline?.length || 1;
  const lines = [
    "<b>◈ TOOL JOB · " + state + "</b>",
    "ID: <code>" + htmlEscape(job.id) + "</code>",
    "Tệp: " + htmlEscape(job.fileName),
    "Dung lượng: " + job.fileSize.toLocaleString("en-US") + " bytes · Lần chạy: " + (job.attempt || 1),
    "Tiến trình: <b>" + (job.progress?.completed ?? job.trace?.filter(item => item.status === "completed").length ?? 0) + "/" + total + "</b>",
  ];
  if (job.progress?.currentToolIds.length) {
    lines.push("Đang thực thi: " + htmlEscape(job.progress.currentToolIds.join(", ")));
  }
  if (job.workflowName) lines.push("Workflow: " + htmlEscape(job.workflowName));
  if (job.retryOf) lines.push("Retry từ: <code>" + htmlEscape(job.retryOf) + "</code>");
  if (job.workflowDag) {
    lines.push("", "<b>DAG</b>");
    lines.push(...job.workflowDag.map(node =>
      htmlEscape(node.id + " = " + node.toolId + " ← " + (node.dependsOn.join(",") || "input"))));
  } else {
    lines.push("", "<b>Pipeline</b>", htmlEscape((job.pipeline || [{ toolId: job.toolId }]).map(step => step.toolId).join(" → ")));
  }
  if (job.trace?.length) {
    lines.push("", "<b>Execution trace</b>");
    lines.push(...job.trace.map(step =>
      (step.status === "completed" ? "✅ " : "❌ ") +
      htmlEscape((step.nodeId ? "Node " + step.nodeId : "Step " + step.step) + "/" + step.total + " · " + step.toolId) +
      " · " + step.durationMs + " ms · " + step.inputBytes.toLocaleString("en-US") +
      " → " + (step.outputBytes === null ? "text" : step.outputBytes.toLocaleString("en-US") + " bytes") +
      "\n" + htmlEscape((step.error || step.summary).slice(0, 260))));
  } else {
    lines.push("", "<i>Runner chưa gửi trace bước nào.</i>");
  }
  if (job.resultSummary) lines.push("", "<b>Kết quả</b>", htmlEscape(job.resultSummary.slice(0, 900)));
  if (job.error) lines.push("", "<b>Lỗi</b>", htmlEscape(job.error.slice(0, 500)));
  if (job.status === "failed" && !job.fileId) lines.push("", "Tệp gốc không còn khả dụng để retry; hãy gửi lại tệp.");
  return lines.join("\n");
}

export function buildToolJobDetailKeyboard(job: ToolJob, page = 0): TelegramInlineKeyboardMarkup {
  const rows: TelegramInlineButton[][] = [
    [{ text: "↻ Làm mới tiến trình", callback_data: "tjview:" + job.id + ":" + page }],
  ];
  if (job.status === "failed" && job.fileId) {
    rows.push([{ text: "↻ Retry toàn pipeline", callback_data: "tjr:" + job.id }]);
  }
  rows.push([
    { text: "⬅️ Danh sách job", callback_data: "tjp:" + page },
    { text: "🧰 Tool Center", callback_data: "tc:home" },
  ]);
  return { inline_keyboard: rows };
}
