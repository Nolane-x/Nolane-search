import { readFileSync } from "node:fs";

const source = readFileSync(new URL("./set-webhook.mjs", import.meta.url), "utf8");
const required = [
  'allowed_updates: ["message", "callback_query"]',
  "getWebhookInfo",
  'configuredUpdates.includes("callback_query")',
];
for (const item of required) {
  if (!source.includes(item)) {
    throw new Error("Telegram webhook regression: missing " + item);
  }
}
console.log("Telegram webhook config check passed (message + callback_query, verified with getWebhookInfo).");
