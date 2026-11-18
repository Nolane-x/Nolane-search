const token = process.env.TELEGRAM_BOT_TOKEN;
const secret = process.env.TELEGRAM_WEBHOOK_SECRET;
const url = process.env.WEBHOOK_URL || "https://nolane-search.nolane-file.workers.dev/telegram/webhook";

if (!token) throw new Error("Missing TELEGRAM_BOT_TOKEN.");
if (!secret) throw new Error("Missing TELEGRAM_WEBHOOK_SECRET.");
if (!/^[A-Za-z0-9_-]{1,256}$/.test(secret)) {
  throw new Error("TELEGRAM_WEBHOOK_SECRET must use only A-Z, a-z, 0-9, underscore or hyphen and be 1-256 characters.");
}

const response = await fetch(`https://api.telegram.org/bot${token}/setWebhook`, {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: JSON.stringify({
    url,
    secret_token: secret,
    allowed_updates: ["message", "callback_query"],
    drop_pending_updates: false,
    max_connections: 20,
  }),
});
const data = await response.json();
if (!response.ok || !data.ok) throw new Error(`Telegram setWebhook failed: ${data.description || response.status}`);

const verification = await fetch(`https://api.telegram.org/bot${token}/getWebhookInfo`, {
  method: "GET",
  signal: AbortSignal.timeout(15_000),
});
const verificationData = await verification.json();
if (!verification.ok || !verificationData.ok) {
  throw new Error(`Telegram getWebhookInfo failed: ${verificationData.description || verification.status}`);
}
const webhook = verificationData.result || {};
const configuredUpdates = Array.isArray(webhook.allowed_updates) ? webhook.allowed_updates : [];
if (webhook.url !== url || !configuredUpdates.includes("callback_query")) {
  throw new Error("Telegram webhook verification failed: callback_query is not enabled for the configured URL.");
}
console.log(`Telegram webhook verified: ${url} (message + callback_query)`);
