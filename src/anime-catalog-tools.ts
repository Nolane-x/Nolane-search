import { readJsonResponse } from "./http";

type Obj = Record<string, unknown>;
type CatalogType = "anime" | "manga";
const BASE = "https://api.jikan.moe/v4";
const USER_AGENT = "NolaneSearch/0.1 (https://github.com/Nolane-x/Nolane-search)";
const NOTES = "Jikan is an unofficial, community-maintained API that parses public MyAnimeList data. Records, scores, titles and publication details may lag or be incomplete; verify important details on the linked MyAnimeList page. SFW filtering is enabled. This catalog does not provide streaming availability or download links.";

function object(value: unknown, label: string): Obj {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error(label + " returned an unexpected response.");
  return value as Obj;
}
function cleanText(value: unknown, key: string, min = 2, max = 120): string {
  if (typeof value !== "string") throw new Error(key + " is required.");
  const clean = value.normalize("NFKC").replace(/[\u0000-\u001f\u007f]/g, " ").replace(/\s+/g, " ").trim();
  if (clean.length < min || clean.length > max) throw new Error(key + " must contain " + min + " to " + max + " characters.");
  return clean;
}
function boundedInt(value: unknown, key: string, fallback: number, min: number, max: number): number {
  if (value === undefined || value === null) return fallback;
  if (typeof value !== "number" || !Number.isSafeInteger(value) || value < min || value > max) {
    throw new Error(key + " must be a whole number from " + min + " to " + max + ".");
  }
  return value;
}
function positiveId(value: unknown, key: string): number {
  const raw = typeof value === "number" ? String(value) : typeof value === "string" ? value.trim() : "";
  if (!/^[1-9]\d{0,9}$/.test(raw)) throw new Error(key + " must be a positive numeric MyAnimeList ID.");
  const id = Number(raw);
  if (!Number.isSafeInteger(id)) throw new Error(key + " is outside the supported ID range.");
  return id;
}
function safeMalUrl(value: unknown, id: number, type: CatalogType): string {
  if (typeof value === "string" && value.length <= 2048) {
    try {
      const url = new URL(value);
      if (url.protocol === "https:" && ["myanimelist.net","www.myanimelist.net"].includes(url.hostname) &&
          !url.username && !url.password && !url.port) return url.toString();
    } catch { /* fall through to the canonical page */ }
  }
  return "https://myanimelist.net/" + type + "/" + id;
}
function safeImageUrl(value: unknown): string | null {
  if (typeof value !== "string" || value.length > 2048) return null;
  try {
    const url = new URL(value);
    if (url.protocol !== "https:" || url.hostname !== "cdn.myanimelist.net" || url.username || url.password || url.port) return null;
    return url.toString();
  } catch { return null; }
}
function nestedObject(value: unknown): Obj {
  return value && typeof value === "object" && !Array.isArray(value) ? value as Obj : {};
}
function imageUrl(row: Obj): string | null {
  const images = nestedObject(row.images);
  const jpg = nestedObject(images.jpg);
  const webp = nestedObject(images.webp);
  return safeImageUrl(jpg.large_image_url) ?? safeImageUrl(webp.large_image_url) ??
    safeImageUrl(jpg.image_url) ?? safeImageUrl(webp.image_url);
}
function boundedString(value: unknown, max = 1000): string | null {
  if (typeof value !== "string") return null;
  const clean = value.replace(/\u0000/g, "").trim();
  return clean ? clean.slice(0, max) : null;
}
function numberField(value: unknown, min = 0, max = Number.MAX_SAFE_INTEGER): number | null {
  return typeof value === "number" && Number.isFinite(value) && value >= min && value <= max ? value : null;
}
function names(value: unknown, max = 8): string[] {
  if (!Array.isArray(value)) return [];
  return value.flatMap(item => {
    if (!item || typeof item !== "object" || Array.isArray(item)) return [];
    const name = boundedString((item as Obj).name, 100);
    return name ? [name] : [];
  }).slice(0, max);
}
function dateRange(value: unknown): { from: string | null; to: string | null } | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) return null;
  const row = value as Obj;
  return { from: boundedString(row.from, 40), to: boundedString(row.to, 40) };
}
function normalizeEntry(raw: unknown, type: CatalogType): Obj | null {
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) return null;
  const row = raw as Obj;
  const id = numberField(row.mal_id, 1, 2_000_000);
  const title = boundedString(row.title, 240);
  if (id === null || !title) return null;
  const genres = names(row.genres, 10);
  const base: Obj = {
    mal_id: id,
    title,
    title_english: boundedString(row.title_english, 240),
    title_japanese: boundedString(row.title_japanese, 240),
    type: boundedString(row.type, 60),
    status: boundedString(row.status, 80),
    score: numberField(row.score, 0, 10),
    scored_by: numberField(row.scored_by, 0, 2_000_000_000),
    rank: numberField(row.rank, 1, 2_000_000),
    popularity: numberField(row.popularity, 1, 2_000_000),
    synopsis: boundedString(row.synopsis, 1200),
    genres,
    image_url: imageUrl(row),
    myanimelist_url: safeMalUrl(row.url, id, type),
  };
  if (type === "anime") {
    base.episodes = numberField(row.episodes, 0, 100_000);
    base.duration = boundedString(row.duration, 100);
    base.rating = boundedString(row.rating, 80);
    base.season = boundedString(row.season, 30);
    base.year = numberField(row.year, 1900, 2200);
    base.studios = names(row.studios, 6);
    base.aired = dateRange(row.aired);
    base.airing = typeof row.airing === "boolean" ? row.airing : null;
  } else {
    base.chapters = numberField(row.chapters, 0, 500_000);
    base.volumes = numberField(row.volumes, 0, 100_000);
    base.publishing = typeof row.publishing === "boolean" ? row.publishing : null;
    base.authors = names(row.authors, 6);
    base.serializations = names(row.serializations, 6);
    base.published = dateRange(row.published);
  }
  return base;
}
async function request<T>(url: URL, label: string, maxBytes = 650_000): Promise<T> {
  let response: Response;
  try {
    response = await fetch(url, {
      method: "GET",
      headers: { accept: "application/json", "user-agent": USER_AGENT },
      redirect: "error",
      signal: AbortSignal.timeout(12_000),
    });
  } catch {
    throw new Error("Jikan could not be reached or the request timed out.");
  }
  if (!response.ok) {
    await response.body?.cancel().catch(() => undefined);
    if (response.status === 429) throw new Error("Jikan is rate-limiting requests. Slow down and retry later.");
    if (response.status === 503 || response.status === 504) throw new Error("Jikan or its MyAnimeList source is temporarily unavailable. Retry later.");
    if (response.status === 404) throw new Error(label + " was not found.");
    throw new Error("Jikan returned HTTP " + response.status + ".");
  }
  const payload = await readJsonResponse<T>(response, maxBytes);
  if (payload && typeof payload === "object" && !Array.isArray(payload)) {
    const error = (payload as Obj).error;
    if (typeof error === "string" && error) throw new Error("Jikan API error: " + error.slice(0, 220));
  }
  return payload;
}
async function searchCatalog(type: CatalogType, argsRaw: unknown): Promise<string> {
  const args = object(argsRaw, "Tool arguments");
  const query = cleanText(args.query, "query", 2, 120);
  const limit = boundedInt(args.limit, "limit", 6, 1, 8);
  const mediaType = args.type;
  if (mediaType !== undefined && mediaType !== null && mediaType !== "") {
    const valid = type === "anime"
      ? ["TV","OVA","Movie","Special","ONA","Music","CM","PV","TV Special"]
      : ["manga","novel","lightnovel","oneshot","doujin","manhwa","manhua"];
    if (typeof mediaType !== "string" || !valid.includes(mediaType)) {
      throw new Error("type must be one of: " + valid.join(", ") + ".");
    }
  }
  const url = new URL(BASE + "/" + type);
  url.searchParams.set("q", query);
  url.searchParams.set("limit", String(limit));
  url.searchParams.set("sfw", "true");
  if (typeof mediaType === "string" && mediaType) url.searchParams.set("type", mediaType);
  const payload = object(await request<unknown>(url, type + " search", 500_000), "Jikan search");
  const rows = Array.isArray(payload.data) ? payload.data : [];
  const results = rows.flatMap(raw => {
    const entry = normalizeEntry(raw, type);
    return entry ? [entry] : [];
  }).slice(0, limit);
  return JSON.stringify({
    status: results.length ? "ok" : "not_found",
    source: "Jikan / MyAnimeList",
    catalog: type,
    query,
    result_count: results.length,
    results,
    note: NOTES,
  });
}
async function getDetails(type: CatalogType, idRaw: unknown): Promise<string> {
  const id = positiveId(idRaw, type === "anime" ? "anime_id" : "manga_id");
  const url = new URL(BASE + "/" + type + "/" + id + "/full");
  const payload = object(await request<unknown>(url, type + " details", 700_000), "Jikan detail");
  const entry = normalizeEntry(payload.data, type);
  if (!entry) return JSON.stringify({
    status: "not_found",
    source: "Jikan / MyAnimeList",
    catalog: type,
    mal_id: id,
    myanimelist_url: "https://myanimelist.net/" + type + "/" + id,
    note: "No public SFW catalog entry was returned for this ID.",
  });
  const row = nestedObject(payload.data);
  const extended: Obj = {
    ...entry,
    background: boundedString(row.background, 1200),
    titles: Array.isArray(row.titles) ? row.titles.flatMap(item => {
      if (!item || typeof item !== "object" || Array.isArray(item)) return [];
      const title = boundedString((item as Obj).title, 240);
      const titleType = boundedString((item as Obj).type, 60);
      return title ? [{ type: titleType, title }] : [];
    }).slice(0, 12) : [],
    themes: names(row.themes, 10),
    demographics: names(row.demographics, 8),
  };
  if (type === "anime") {
    extended.producers = names(row.producers, 8);
    extended.licensors = names(row.licensors, 8);
    extended.broadcast = boundedString(nestedObject(row.broadcast).string, 120);
  }
  return JSON.stringify({
    status: "ok",
    source: "Jikan / MyAnimeList",
    catalog: type,
    item: extended,
    note: NOTES,
  });
}
export async function runAnimeCatalogTool(name: string, args: unknown): Promise<string> {
  if (name === "search_anime_titles") return searchCatalog("anime", args);
  if (name === "get_anime_details") {
    const raw = object(args, "Tool arguments");
    return getDetails("anime", raw.anime_id);
  }
  if (name === "search_manga_titles") return searchCatalog("manga", args);
  if (name === "get_manga_details") {
    const raw = object(args, "Tool arguments");
    return getDetails("manga", raw.manga_id);
  }
  throw new Error("Unknown anime/manga catalog tool: " + name + ".");
}
