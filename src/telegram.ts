import { htmlEscape } from "./security";
import type { Env, SearchMode, SearchResult } from "./types";

const MAX_FORMATTED_LENGTH = 3600;

export async function telegramApi<T = Record<string, unknown>>(env: Env, method: string, body: Record<string, unknown>): Promise<T> {
  if (!env.TELEGRAM_BOT_TOKEN) throw new Error("TELEGRAM_BOT_TOKEN is not configured");
  const response = await fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/${method}`, {
    method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body),
    signal: AbortSignal.timeout(15_000),
  });
  const data = await response.json() as { ok?: boolean; description?: string; result?: T };
  if (!response.ok || !data.ok) throw new Error(data.description || `Telegram API error (${response.status})`);
  return data.result as T;
}

export async function sendSearchPage(
  env: Env,
  chatId: number | string,
  text: string,
  replyMarkup?: { inline_keyboard: Array<Array<{ text: string; callback_data: string }>> },
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
  const data = await response.json() as { ok?: boolean; description?: string };
  if (!response.ok || !data.ok) throw new Error(data.description || `Telegram sendDocument failed (${response.status})`);
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
): { inline_keyboard: Array<Array<{ text: string; callback_data: string }>> } | undefined {
  const totalPages = Math.ceil(totalResults / SEARCH_PAGE_SIZE);
  if (totalPages <= 1) return undefined;
  const currentPage = Math.max(0, Math.min(totalPages - 1, page));
  const row: Array<{ text: string; callback_data: string }> = [];
  if (currentPage > 0) row.push({ text: "⬅️ Trước", callback_data: `ns:${sessionId}:${currentPage - 1}` });
  row.push({ text: `${currentPage + 1}/${totalPages}`, callback_data: `ns:${sessionId}:${currentPage}` });
  if (currentPage < totalPages - 1) row.push({ text: "Tiếp ➡️", callback_data: `ns:${sessionId}:${currentPage + 1}` });
  return { inline_keyboard: [row] };
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
