import { readJsonResponse } from "./http";

type Obj = Record<string, unknown>;
type WikiProject = "wikipedia" | "wikivoyage" | "wiktionary";
const USER_AGENT = "NolaneSearch/0.1 (https://github.com/Nolane-x/Nolane-search)";
const LANGUAGES: Record<WikiProject, readonly string[]> = {
  wikipedia: ["en", "vi", "ja", "fr", "es", "de"],
  wikivoyage: ["en", "vi"],
  wiktionary: ["en", "vi"],
};
const PROJECT_NOTES: Record<WikiProject, string> = {
  wikipedia: "Wikipedia is a collaboratively edited encyclopedia. Articles can be incomplete, disputed or out of date; verify important or high-stakes facts using the cited sources within the article.",
  wikivoyage: "Wikivoyage is a community-written travel guide. Transport, opening hours, prices, safety conditions and visa rules can change quickly; verify current details with official providers before travelling.",
  wiktionary: "Wiktionary is a community-maintained dictionary. Definitions, pronunciation, usage labels and translations can vary by dialect and may be incomplete; check the original entry and context.",
};

function obj(value: unknown, label: string): Obj {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error(label + " returned an unexpected response.");
  return value as Obj;
}
function str(value: unknown, key: string, min = 1, max = 300): string {
  if (typeof value !== "string") throw new Error(key + " is required.");
  const clean = value.normalize("NFKC").replace(/[\u0000-\u001f\u007f]/g, " ").replace(/\s+/g, " ").trim();
  if (clean.length < min || clean.length > max) throw new Error(key + " must contain " + min + " to " + max + " characters.");
  return clean;
}
function integer(value: unknown, key: string, fallback: number, min: number, max: number): number {
  if (value === undefined || value === null) return fallback;
  if (typeof value !== "number" || !Number.isSafeInteger(value) || value < min || value > max) {
    throw new Error(key + " must be a whole number from " + min + " to " + max + ".");
  }
  return value;
}
function language(value: unknown, project: WikiProject): string {
  const code = value === undefined || value === null || value === "" ? (project === "wiktionary" ? "en" : "en") : value;
  if (typeof code !== "string" || !LANGUAGES[project].includes(code)) {
    throw new Error("language must be one of: " + LANGUAGES[project].join(", ") + ".");
  }
  return code;
}
function wikiOrigin(project: WikiProject, lang: string): string {
  return "https://" + lang + "." + project + ".org";
}
async function wikiRequest<T>(project: WikiProject, lang: string, params: Record<string, string>, maxBytes = 750_000): Promise<T> {
  const url = new URL(wikiOrigin(project, lang) + "/w/api.php");
  url.searchParams.set("action", "query");
  url.searchParams.set("format", "json");
  url.searchParams.set("formatversion", "2");
  url.searchParams.set("utf8", "1");
  url.searchParams.set("maxlag", "5");
  for (const [key, value] of Object.entries(params)) url.searchParams.set(key, value);
  let response: Response;
  try {
    response = await fetch(url, {
      method: "GET",
      headers: { accept: "application/json", "user-agent": USER_AGENT, "api-user-agent": USER_AGENT },
      redirect: "error",
      signal: AbortSignal.timeout(12_000),
    });
  } catch {
    throw new Error(project + " could not be reached or the request timed out.");
  }
  if (!response.ok) {
    await response.body?.cancel().catch(() => undefined);
    if (response.status === 429) throw new Error(project + " is rate-limiting requests. Reduce query frequency and retry later.");
    if (response.status === 503) throw new Error(project + " is temporarily unavailable. Retry later.");
    throw new Error(project + " returned HTTP " + response.status + ".");
  }
  const payload = await readJsonResponse<T>(response, maxBytes);
  if (payload && typeof payload === "object" && !Array.isArray(payload)) {
    const error = (payload as Obj).error;
    if (error && typeof error === "object" && !Array.isArray(error)) {
      const details = error as Obj;
      const code = typeof details.code === "string" ? details.code : "api_error";
      const info = typeof details.info === "string" ? details.info.slice(0, 220) : "Wikimedia API rejected the request.";
      if (code === "maxlag") throw new Error(project + " is busy; Wikimedia maxlag is active. Retry later.");
      throw new Error(project + " API error (" + code + "): " + info);
    }
  }
  return payload;
}
function safeWikiThumbnail(value: unknown): string | null {
  if (typeof value !== "string" || value.length > 2048) return null;
  try {
    const url = new URL(value);
    if (url.protocol !== "https:" || url.hostname !== "upload.wikimedia.org" || url.username || url.password || url.port) return null;
    return url.toString();
  } catch { return null; }
}
function normalizedSnippet(value: unknown): string | null {
  if (typeof value !== "string") return null;
  const text = value.replace(/<[^>]*>/g, " ")
    .replace(/&amp;/g, "&").replace(/&quot;/g, '"').replace(/&#39;/g, "'")
    .replace(/&lt;/g, "<").replace(/&gt;/g, ">")
    .replace(/\s+/g, " ").trim();
  return text ? text.slice(0, 650) : null;
}
function canonicalUrl(project: WikiProject, lang: string, value: unknown, title: string): string {
  const origin = wikiOrigin(project, lang);
  if (typeof value === "string" && value.length <= 2048) {
    try {
      const url = new URL(value);
      if (url.protocol === "https:" && url.hostname === lang + "." + project + ".org" && !url.username && !url.password) return url.toString();
    } catch { /* construct canonical project URL below */ }
  }
  return origin + "/wiki/" + encodeURIComponent(title.replace(/ /g, "_"));
}
function searchRows(payload: unknown): Obj[] {
  const root = obj(payload, "Wikimedia API");
  const query = root.query && typeof root.query === "object" && !Array.isArray(root.query) ? root.query as Obj : {};
  return Array.isArray(query.search) ? query.search.filter((x): x is Obj => !!x && typeof x === "object" && !Array.isArray(x)) : [];
}
async function searchProject(project: WikiProject, rawArgs: unknown): Promise<string> {
  const args = obj(rawArgs, "Tool arguments");
  const query = str(args.query, "query", 2, 120);
  const lang = language(args.language, project);
  const limit = integer(args.limit, "limit", project === "wikivoyage" ? 5 : 6, 1, project === "wikivoyage" ? 7 : 10);
  const payload = await wikiRequest<unknown>(project, lang, {
    list: "search", srsearch: query, srnamespace: "0", srlimit: String(limit), srwhat: "text",
  }, 400_000);
  const rows = searchRows(payload);
  const results = rows.flatMap(row => {
    const title = typeof row.title === "string" ? row.title.slice(0, 240) : "";
    const pageId = typeof row.pageid === "number" && Number.isSafeInteger(row.pageid) ? row.pageid : null;
    if (!title || pageId === null) return [];
    return [{
      page_id: pageId,
      title,
      snippet: normalizedSnippet(row.snippet),
      word_count: typeof row.wordcount === "number" && Number.isSafeInteger(row.wordcount) ? row.wordcount : null,
      last_touched: typeof row.timestamp === "string" ? row.timestamp.slice(0, 40) : null,
      url: canonicalUrl(project, lang, null, title),
    }];
  }).slice(0, limit);
  return JSON.stringify({
    status: results.length ? "ok" : "not_found",
    source: project === "wikipedia" ? "Wikipedia" : project === "wikivoyage" ? "Wikivoyage" : "Wiktionary",
    language: lang,
    query,
    result_count: results.length,
    results,
    note: PROJECT_NOTES[project],
  });
}
async function getProjectArticle(project: WikiProject, rawArgs: unknown): Promise<string> {
  const args = obj(rawArgs, "Tool arguments");
  const title = str(args.title, "title", 1, 220);
  const lang = language(args.language, project);
  const payload = obj(await wikiRequest<unknown>(project, lang, {
    prop: "extracts|info|pageimages|categories",
    titles: title,
    redirects: "1",
    explaintext: "1",
    exsectionformat: "plain",
    exchars: "1200",
    exsentences: "10",
    inprop: "url",
    piprop: "thumbnail",
    pithumbsize: "640",
    cllimit: "8",
  }, 850_000), "Wikimedia article");
  const query = payload.query && typeof payload.query === "object" && !Array.isArray(payload.query)
    ? payload.query as Obj : {};
  const pages = Array.isArray(query.pages) ? query.pages : [];
  const page = pages.find(item => item && typeof item === "object" && !Array.isArray(item) &&
    typeof (item as Obj).pageid === "number") as Obj | undefined;
  if (!page) {
    return JSON.stringify({ status: "not_found", title, language: lang, source: project, note: "No matching page was found in this language edition." });
  }
  const normalizedTitle = typeof page.title === "string" ? page.title.slice(0, 240) : title;
  const extract = typeof page.extract === "string" ? page.extract.slice(0, 1_200).trim() : "";
  if (!extract) {
    return JSON.stringify({ status: "not_found", title: normalizedTitle, language: lang, source: project, note: "The page exists but does not expose a readable text extract." });
  }
  const thumb = page.thumbnail && typeof page.thumbnail === "object" && !Array.isArray(page.thumbnail)
    ? page.thumbnail as Obj : {};
  const categories = Array.isArray(page.categories) ? page.categories.flatMap(item => {
    if (!item || typeof item !== "object" || Array.isArray(item)) return [];
    const name = (item as Obj).title;
    return typeof name === "string" ? [name.replace(/^Category:/, "").slice(0, 120)] : [];
  }).slice(0, 8) : [];
  const pageId = typeof page.pageid === "number" && Number.isSafeInteger(page.pageid) ? page.pageid : null;
  return JSON.stringify({
    status: "ok",
    source: project === "wikipedia" ? "Wikipedia" : project === "wikivoyage" ? "Wikivoyage" : "Wiktionary",
    language: lang,
    page_id: pageId,
    title: normalizedTitle,
    url: canonicalUrl(project, lang, page.fullurl, normalizedTitle),
    thumbnail_url: safeWikiThumbnail(thumb.source),
    text: extract,
    categories,
    note: PROJECT_NOTES[project],
  });
}

export async function runOpenKnowledgeTool(name: string, rawArgs: unknown): Promise<string> {
  if (name === "search_wikipedia_articles") return searchProject("wikipedia", rawArgs);
  if (name === "get_wikipedia_article") return getProjectArticle("wikipedia", rawArgs);
  if (name === "search_wikivoyage_guides") return searchProject("wikivoyage", rawArgs);
  if (name === "get_wikivoyage_guide") return getProjectArticle("wikivoyage", rawArgs);
  if (name === "lookup_wiktionary_entry") return getProjectArticle("wiktionary", rawArgs);
  throw new Error("Unknown open knowledge tool: " + name + ".");
}
