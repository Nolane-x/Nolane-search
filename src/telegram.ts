import { htmlEscape } from "./security";
import type { Env, SearchMode, SearchResult } from "./types";

export async function telegramApi<T = Record<string, unknown>>(env: Env, method: string, body: Record<string, unknown>): Promise<T> {
  if (!env.TELEGRAM_BOT_TOKEN) throw new Error("TELEGRAM_BOT_TOKEN is not configured");
  const response = await fetch(\`https://api.telegram.org/bot\${env.TELEGRAM_BOT_TOKEN}/\${method}\`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(15_000),
  });
  const data = await response.json() as { ok?: boolean; description?: string; result?: T };
  if (!response.ok || !data.ok) throw new Error(data.description || \`Telegram API error (\${response.status})\`);
  return data.result as T;
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
      chat_id: chatId,
      text: chunk,
      parse_mode: "HTML",
      disable_web_page_preview: true,
    });
  }
}

export async function sendToArchive(env: Env, text: string): Promise<void> {
  if (!env.TELEGRAM_ARCHIVE_CHAT_ID) return;
  try {
    await sendTelegram(env, env.TELEGRAM_ARCHIVE_CHAT_ID, text);
  } catch (error) {
    console.error("Telegram archive delivery failed:", error instanceof Error ? error.message : "unknown error");
  }
}

export async function sendArchiveDocument(env: Env, filename: string, content: string, caption: string): Promise<void> {
  if (!env.TELEGRAM_ARCHIVE_CHAT_ID || !env.TELEGRAM_BOT_TOKEN) return;
  const form = new FormData();
  form.set("chat_id", env.TELEGRAM_ARCHIVE_CHAT_ID);
  form.set("caption", caption.slice(0, 900));
  form.set("document", new Blob([content], { type: "text/plain;charset=utf-8" }), filename);
  const response = await fetch(\`https://api.telegram.org/bot\${env.TELEGRAM_BOT_TOKEN}/sendDocument\`, {
    method: "POST",
    body: form,
    signal: AbortSignal.timeout(20_000),
  });
  const data = await response.json() as { ok?: boolean; description?: string };
  if (!response.ok || !data.ok) throw new Error(data.description || \`Telegram sendDocument failed (\${response.status})\`);
}

const MODE_LABELS: Record<SearchMode, string> = {
  web: "Web Search",
  tech: "Technology Search",
  research: "Research Search",
  news: "News Search",
  github: "GitHub Search",
  local: "My Sites Index",
};

export function formatSearchResults(query: string, mode: SearchMode, results: SearchResult[]): string {
  if (!results.length) return \`<b>Nolane Search</b>\nKhông tìm thấy kết quả phù hợp cho: <code>\${htmlEscape(query)}</code>\`;
  const lines = [
    \`<b>Nolane Search · \${MODE_LABELS[mode]}</b>\`,
    \`<i>\${htmlEscape(query)}</i>\`,
    \`Tìm thấy \${results.length} kết quả\`,
    "",
  ];
  results.slice(0, 7).forEach((item, index) => {
    lines.push(\`<b>\${index + 1}. <a href="\${htmlEscape(item.url)}">\${htmlEscape(item.title)}</a></b>\`);
    if (item.snippet) lines.push(htmlEscape(item.snippet.slice(0, 350)));
    lines.push(\`<code>\${htmlEscape(item.domain)}</code> · \${htmlEscape(item.provider)}\`);
    lines.push("");
  });
  lines.push("<i>Điểm xếp hạng là heuristic nội bộ, không phải xác suất độ đúng.</i>");
  return lines.join("\n").slice(0, 3900);
}

export function formatDeepReport(query: string, results: SearchResult[], summary: string | null): string {
  const lines = [
    "<b>Nolane Search · Deep Search</b>",
    \`<i>\${htmlEscape(query)}</i>\`,
    \`Đã tổng hợp \${results.length} kết quả duy nhất từ nhiều lượt truy vấn.\`,
    "",
  ];
  if (summary) {
    lines.push("<b>Tổng hợp AI</b>");
    lines.push(htmlEscape(summary.slice(0, 2200)));
    lines.push("");
  } else {
    lines.push("<b>Evidence digest</b>");
    lines.push("Chưa bật AI synthesis. Dưới đây là các nguồn thu thập được; hãy mở nguồn để tự kiểm chứng.");
    lines.push("");
  }
  results.slice(0, 8).forEach((item, index) => {
    lines.push(\`<b>\${index + 1}. <a href="\${htmlEscape(item.url)}">\${htmlEscape(item.title)}</a></b>\`);
    if (item.snippet) lines.push(htmlEscape(item.snippet.slice(0, 240)));
    lines.push(\`<code>\${htmlEscape(item.domain)}</code> · \${htmlEscape(item.provider)}\`);
    lines.push("");
  });
  lines.push("<i>Deep Search là tổng hợp các nguồn truy xuất được; không bảo đảm bao quát toàn bộ tài liệu hiện có.</i>");
  return lines.join("\n").slice(0, 3900);
}
