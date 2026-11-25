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
  "/api/auth/exchange",
];

const missing = requiredMarkers.filter(marker => !html.includes(marker));
if (missing.length) {
  throw new Error("Telegram Mini App HTML is missing required UI markers: " + missing.join(", "));
}

console.log("Telegram Mini App smoke test passed: HTTPS route, private cache policy, CSP, auth bootstrap, five workspace tabs and Media Studio link.");
