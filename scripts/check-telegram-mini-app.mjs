const target = process.env.TELEGRAM_MINI_APP_URL || "https://nolane-search.nolane-file.workers.dev/telegram";
const expectedHost = "nolane-search.nolane-file.workers.dev";

let url;
try {
  url = new URL(target);
} catch {
  throw new Error("TELEGRAM_MINI_APP_URL must be a valid absolute URL.");
}

if (
  url.protocol !== "https:" ||
  url.hostname !== expectedHost ||
  url.username ||
  url.password ||
  url.port ||
  url.pathname !== "/telegram" ||
  url.search ||
  url.hash
) {
  throw new Error("Refusing to smoke-test an unexpected Telegram Mini App origin or path.");
}

const response = await fetch(url, {
  method: "GET",
  headers: { accept: "text/html" },
  redirect: "error",
  signal: AbortSignal.timeout(15_000),
});

if (!response.ok) {
  await response.body?.cancel().catch(() => undefined);
  throw new Error(`Telegram Mini App returned HTTP ${response.status}.`);
}

const contentType = response.headers.get("content-type") || "";
const cacheControl = response.headers.get("cache-control") || "";
const nosniff = response.headers.get("x-content-type-options") || "";
const csp = response.headers.get("content-security-policy") || "";

if (!/^text\/html(?:;|$)/i.test(contentType)) throw new Error("Telegram Mini App did not return HTML.");
if (!/no-store/i.test(cacheControl)) throw new Error("Telegram Mini App response must not be stored in shared caches.");
if (nosniff.toLowerCase() !== "nosniff") throw new Error("Telegram Mini App is missing X-Content-Type-Options: nosniff.");
for (const directive of ["connect-src 'self'", "frame-ancestors 'none'", "https://telegram.org"]) {
  if (!csp.includes(directive)) throw new Error("Telegram Mini App CSP is missing: " + directive);
}

const html = await response.text();
const requiredMarkers = [
  "<title>Nolane · Telegram Workspace</title>",
  "Telegram.WebApp",
  'data-tab="home"',
  'data-tab="search"',
  'data-tab="ai"',
  'data-tab="tools"',
  'data-tab="library"',
  'href="/media"',
  "Media Studio",
  'href="/nearby"',
  "Địa điểm quanh đây",
  "/api/auth/exchange",
];

const missing = requiredMarkers.filter(marker => !html.includes(marker));
if (missing.length) {
  throw new Error("Telegram Mini App HTML is missing required UI markers: " + missing.join(", "));
}

const nearbyUrl = new URL("/nearby", url.origin);
const nearbyPage = await fetch(nearbyUrl, {
  method: "GET",
  headers: { accept: "text/html" },
  redirect: "manual",
  signal: AbortSignal.timeout(15_000),
});
if (nearbyPage.status !== 302) {
  await nearbyPage.body?.cancel().catch(() => undefined);
  throw new Error("Private Nearby Places page must redirect anonymous visitors; got HTTP " + nearbyPage.status + ".");
}
if (nearbyPage.headers.get("location") !== url.origin + "/") {
  await nearbyPage.body?.cancel().catch(() => undefined);
  throw new Error("Nearby Places anonymous redirect did not point to the private workspace sign-in page.");
}
await nearbyPage.body?.cancel().catch(() => undefined);

const nearbyApi = await fetch(new URL("/api/nearby/search", url.origin), {
  method: "POST",
  headers: {
    origin: url.origin,
    "content-type": "application/json",
  },
  body: JSON.stringify({ latitude: 20.8449, longitude: 106.6881, category: "pharmacy" }),
  redirect: "error",
  signal: AbortSignal.timeout(15_000),
});
if (nearbyApi.status !== 401) {
  await nearbyApi.body?.cancel().catch(() => undefined);
  throw new Error("Nearby Places API must reject anonymous POSTs with HTTP 401; got " + nearbyApi.status + ".");
}
await nearbyApi.body?.cancel().catch(() => undefined);

console.log("Telegram Workspace production smoke passed: /telegram HTML/CSP/auth/tabs, Media Studio and Nearby links; /nearby private redirect; nearby search API anonymous 401.");
