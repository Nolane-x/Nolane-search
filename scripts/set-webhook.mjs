const token = process.env.TELEGRAM_BOT_TOKEN;
const secret = process.env.TELEGRAM_WEBHOOK_SECRET;
const url = process.env.WEBHOOK_URL || "https://nolane-search.nolane-file.workers.dev/telegram/webhook";

if (!token) throw new Error("Missing TELEGRAM_BOT_TOKEN.");
if (!secret) throw new Error("Missing TELEGRAM_WEBHOOK_SECRET.");
if (!/^[A-Za-z0-9_-]{1,256}$/.test(secret)) {
  throw new Error("TELEGRAM_WEBHOOK_SECRET must use only A-Z, a-z, 0-9, underscore or hyphen and be 1-256 characters.");
}

const response = await fetch(\`https://api.telegram.org/bot\${token}/setWebhook\`, {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: JSON.stringify({
    url,
    secret_token: secret,
    allowed_updates: ["message"],
    drop_pending_updates: false,
    max_connections: 20,
  }),
});
const data = await response.json();
if (!response.ok || !data.ok) throw new Error(\`Telegram setWebhook failed: \${data.description || response.status}\`);
console.log(\`Telegram webhook configured: \${url}\`);
