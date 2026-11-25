const USER_AGENT = "NolaneSearch/0.1 (+https://github.com/Nolane-x/Nolane-search)";
const STEAM_STORE = "https://store.steampowered.com";
const MAX_QUERY_LENGTH = 100;
const MAX_SEARCH_RESULTS = 10;
const MAX_RESPONSE_BYTES = 900_000;

type Obj = Record<string, unknown>;

function asObject(value: unknown, label: string): Obj {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("Steam returned an invalid " + label + " response.");
  }
  return value as Obj;
}

function cleanText(value: unknown, max = 500): string | null {
  if (typeof value !== "string") return null;
  const cleaned = value
    .replace(/<br\\s*\\/?\\s*>/gi, " ")
    .replace(/<[^>]*>/g, " ")
    .replace(/&nbsp;/gi, " ")
    .replace(/&amp;/gi, "&")
    .replace(/&quot;/gi, '"')
    .replace(/&#39;/g, "'")
    .replace(/\\s+/g, " ")
    .trim()
    .slice(0, max);
  return cleaned || null;
}

function requiredQuery(value: unknown): string {
  if (typeof value !== "string") throw new Error("query must be a string.");
  const query = value.normalize("NFKC").trim().replace(/\\s+/g, " ");
  if (query.length < 2 || query.length > MAX_QUERY_LENGTH || /[\\u0000-\\u001f\\u007f]/.test(query)) {
    throw new Error("query must contain 2–100 printable characters.");
  }
  return query;
}

function boundedLimit(value: unknown, fallback: number): number {
  if (value === undefined) return fallback;
  if (!Number.isSafeInteger(value) || Number(value) < 1 || Number(value) > MAX_SEARCH_RESULTS) {
    throw new Error("limit must be an integer from 1 to 10.");
  }
  return Number(value);
}

function countryCode(value: unknown): string {
  if (value === undefined) return "vn";
  if (typeof value !== "string" || !/^[a-z]{2}$/i.test(value)) {
    throw new Error("country_code must be a two-letter country code.");
  }
  return value.toLowerCase();
}

function languageCode(value: unknown): string {
  if (value === undefined) return "vietnamese";
  const supported = new Set([
    "arabic", "brazilian", "bulgarian", "czech", "danish", "dutch", "english",
    "finnish", "french", "german", "greek", "hungarian", "indonesian", "italian",
    "japanese", "koreana", "latam", "norwegian", "polish", "portuguese", "romanian",
    "russian", "schinese", "spanish", "swedish", "tchinese", "thai", "turkish",
    "ukrainian", "vietnamese",
  ]);
  if (typeof value !== "string" || !supported.has(value.toLowerCase())) {
    throw new Error("language is not in the supported Steam storefront language list.");
  }
  return value.toLowerCase();
}

function positiveAppId(value: unknown): number {
  const appId = typeof value === "string" && /^\\d{1,10}$/.test(value) ? Number(value) : value;
  if (!Number.isSafeInteger(appId) || Number(appId) < 1 || Number(appId) > 2_147_483_647) {
    throw new Error("app_id must be a valid positive Steam application ID.");
  }
  return Number(appId);
}

async function fetchSteamJson(url: URL, label: string, maxBytes = MAX_RESPONSE_BYTES): Promise<Obj> {
  let response: Response;
  try {
    response = await fetch(url, {
      method: "GET",
      headers: { accept: "application/json", "user-agent": USER_AGENT },
      redirect: "error",
      cache: "no-store",
      signal: AbortSignal.timeout(12_000),
    });
  } catch {
    throw new Error("Steam " + label + " request failed or timed out. Retry later.");
  }
  if (response.status === 429) throw new Error("Steam is rate-limiting requests. Wait before trying again.");
  if (response.status === 503 || response.status === 502 || response.status === 504) {
    throw new Error("Steam is temporarily unavailable (" + response.status + ").");
  }
  if (!response.ok) throw new Error("Steam " + label + " returned HTTP " + response.status + ".");
  const contentLength = Number(response.headers.get("content-length") || 0);
  if (Number.isFinite(contentLength) && contentLength > maxBytes) {
    await response.body?.cancel().catch(() => undefined);
    throw new Error("Steam " + label + " response exceeded the size limit.");
  }
  if (!response.body) throw new Error("Steam " + label + " returned an empty response.");
  const reader = response.body.getReader();
  const chunks: Uint8Array[] = [];
  let total = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      total += value.byteLength;
      if (total > maxBytes) {
        await reader.cancel();
        throw new Error("Steam " + label + " response exceeded the size limit.");
      }
      chunks.push(value);
    }
  } finally {
    reader.releaseLock();
  }
  const bytes = new Uint8Array(total);
  let offset = 0;
  for (const chunk of chunks) {
    bytes.set(chunk, offset);
    offset += chunk.byteLength;
  }
  let parsed: unknown;
  try {
    parsed = JSON.parse(new TextDecoder().decode(bytes));
  } catch {
    throw new Error("Steam " + label + " returned invalid JSON.");
  }
  return asObject(parsed, label);
}

function objectList(value: unknown, max = 12): string[] {
  if (!Array.isArray(value)) return [];
  return value.slice(0, max).flatMap((entry) => {
    if (!entry || typeof entry !== "object" || Array.isArray(entry)) return [];
    const label = cleanText((entry as Obj).description ?? (entry as Obj).name, 100);
    return label ? [label] : [];
  });
}

function stringList(value: unknown, max = 8): string[] {
  if (!Array.isArray(value)) return [];
  return value.slice(0, max).flatMap((entry) => {
    const label = cleanText(entry, 100);
    return label ? [label] : [];
  });
}

function safeSteamImage(value: unknown): string | null {
  if (typeof value !== "string" || value.length > 2048) return null;
  try {
    const url = new URL(value);
    const hosts = new Set([
      "shared.akamai.steamstatic.com",
      "cdn.akamai.steamstatic.com",
      "shared.fastly.steamstatic.com",
      "cdn.fastly.steamstatic.com",
      "shared.cloudflare.steamstatic.com",
      "cdn.cloudflare.steamstatic.com",
    ]);
    if (url.protocol !== "https:" || !hosts.has(url.hostname) || url.port || url.username || url.password) return null;
    return url.toString();
  } catch {
    return null;
  }
}

function searchPrice(value: unknown): { currency: string | null; final: string | null; discountPercent: number | null } | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) return null;
  const price = value as Obj;
  const discount = price.discount_percent;
  return {
    currency: cleanText(price.currency, 12),
    final: cleanText(price.final_formatted, 80),
    discountPercent: Number.isSafeInteger(discount) && Number(discount) >= 0 && Number(discount) <= 100 ? Number(discount) : null,
  };
}

export async function searchSteamGames(
  queryInput: unknown,
  limitInput?: unknown,
  countryInput?: unknown,
  languageInput?: unknown,
): Promise<Obj> {
  const query = requiredQuery(queryInput);
  const limit = boundedLimit(limitInput, 8);
  const country = countryCode(countryInput);
  const language = languageCode(languageInput);
  const url = new URL("/api/storesearch/", STEAM_STORE);
  url.searchParams.set("term", query);
  url.searchParams.set("cc", country);
  url.searchParams.set("l", language);
  const payload = await fetchSteamJson(url, "game search", 350_000);
  const rows = Array.isArray(payload.items) ? payload.items : [];
  const items = rows.slice(0, limit).flatMap((raw) => {
    if (!raw || typeof raw !== "object" || Array.isArray(raw)) return [];
    const row = raw as Obj;
    const id = positiveSearchId(row.id);
    const name = cleanText(row.name, 180);
    if (!id || !name) return [];
    const price = searchPrice(row.price);
    const metascoreNumber = Number(row.metascore);
    return [{
      appId: id,
      name,
      type: cleanText(row.type, 40),
      price,
      metascore: Number.isSafeInteger(metascoreNumber) && metascoreNumber >= 0 && metascoreNumber <= 100 ? metascoreNumber : null,
      image: safeSteamImage(row.tiny_image),
      storeUrl: STEAM_STORE + "/app/" + id + "/",
    }];
  });
  return {
    status: "ok",
    source: "Steam Store",
    query,
    countryCode: country.toUpperCase(),
    language,
    totalReported: Number.isSafeInteger(payload.total) && Number(payload.total) >= 0 ? Number(payload.total) : null,
    items,
    note: "Prices are localized to the selected Steam storefront and may change by region or over time. Search may also return DLC, soundtracks or other store items; check each result's type and store page. This is game discovery, not a game download or streaming service.",
  };
}

function positiveSearchId(value: unknown): number | null {
  const number = typeof value === "string" && /^\\d{1,10}$/.test(value) ? Number(value) : value;
  return Number.isSafeInteger(number) && Number(number) > 0 && Number(number) <= 2_147_483_647 ? Number(number) : null;
}

export async function getSteamGameDetails(
  appIdInput: unknown,
  countryInput?: unknown,
  languageInput?: unknown,
): Promise<Obj> {
  const appId = positiveAppId(appIdInput);
  const country = countryCode(countryInput);
  const language = languageCode(languageInput);
  const url = new URL("/api/appdetails", STEAM_STORE);
  url.searchParams.set("appids", String(appId));
  url.searchParams.set("cc", country);
  url.searchParams.set("l", language);
  const payload = await fetchSteamJson(url, "game details", 800_000);
  const entry = payload[String(appId)];
  if (!entry || typeof entry !== "object" || Array.isArray(entry)) {
    throw new Error("Steam did not return details for app ID " + appId + ".");
  }
  const wrapper = entry as Obj;
  if (wrapper.success !== true) throw new Error("Steam has no public details for app ID " + appId + ". It may be unavailable or age-restricted.");
  const data = asObject(wrapper.data, "game details");
  const name = cleanText(data.name, 180);
  if (!name) throw new Error("Steam returned a game record without a valid title.");
  const price = searchPrice(data.price_overview);
  const platformsValue = data.platforms && typeof data.platforms === "object" && !Array.isArray(data.platforms) ? data.platforms as Obj : {};
  const metacriticValue = data.metacritic && typeof data.metacritic === "object" && !Array.isArray(data.metacritic) ? data.metacritic as Obj : {};
  const recommendationValue = data.recommendations && typeof data.recommendations === "object" && !Array.isArray(data.recommendations) ? data.recommendations as Obj : {};
  const releaseValue = data.release_date && typeof data.release_date === "object" && !Array.isArray(data.release_date) ? data.release_date as Obj : {};
  const screenshotRows = Array.isArray(data.screenshots) ? data.screenshots.slice(0, 6) : [];
  const screenshots = screenshotRows.flatMap((raw) => {
    if (!raw || typeof raw !== "object" || Array.isArray(raw)) return [];
    const row = raw as Obj;
    const image = safeSteamImage(row.path_full);
    return image ? [image] : [];
  });
  return {
    status: "ok",
    source: "Steam Store",
    appId,
    name,
    type: cleanText(data.type, 40),
    shortDescription: cleanText(data.short_description, 900),
    developers: stringList(data.developers, 8),
    publishers: stringList(data.publishers, 8),
    genres: objectList(data.genres),
    categories: objectList(data.categories, 16),
    releaseDate: cleanText(releaseValue.date, 80),
    comingSoon: typeof releaseValue.coming_soon === "boolean" ? releaseValue.coming_soon : null,
    isFree: typeof data.is_free === "boolean" ? data.is_free : null,
    price: price ? {
      currency: price.currency,
      final: price.final,
      discountPercent: price.discountPercent,
      initial: cleanText((data.price_overview as Obj | undefined)?.initial_formatted, 80),
    } : null,
    platforms: {
      windows: platformsValue.windows === true,
      mac: platformsValue.mac === true,
      linux: platformsValue.linux === true,
    },
    metacriticScore: Number.isSafeInteger(metacriticValue.score) && Number(metacriticValue.score) >= 0 && Number(metacriticValue.score) <= 100
      ? Number(metacriticValue.score) : null,
    recommendations: Number.isSafeInteger(recommendationValue.total) && Number(recommendationValue.total) >= 0
      ? Number(recommendationValue.total) : null,
    requiredAge: Number.isSafeInteger(data.required_age) && Number(data.required_age) >= 0 && Number(data.required_age) <= 100
      ? Number(data.required_age) : null,
    supportedLanguages: cleanText(data.supported_languages, 500),
    headerImage: safeSteamImage(data.header_image),
    screenshots,
    storeUrl: STEAM_STORE + "/app/" + appId + "/",
    countryCode: country.toUpperCase(),
    language,
    note: "Details and regional prices are supplied by Steam and can change. A missing price does not always mean the game is free. Metacritic is a separate critic-score source. Availability and age-gated details may vary by region; confirm on the linked Steam store page. This tool does not download, unlock or stream games.",
  };
}

export async function runSteamGamesTool(name: string, rawArgs: unknown): Promise<string> {
  const args = asObject(rawArgs, "tool arguments");
  if (name === "search_steam_games") {
    return JSON.stringify(await searchSteamGames(args.query, args.limit, args.country_code, args.language));
  }
  if (name === "get_steam_game_details") {
    return JSON.stringify(await getSteamGameDetails(args.app_id, args.country_code, args.language));
  }
  throw new Error("Unknown Steam game discovery tool: " + name);
}
