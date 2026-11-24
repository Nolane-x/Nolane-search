import { readJsonResponse } from "./http";

type Obj = Record<string, unknown>;

const MEAL_BASE = "https://www.themealdb.com/api/json/v1/1";
const WIKIDATA_API = "https://www.wikidata.org/w/api.php";
const USER_AGENT = "NolaneSearch/0.1 (https://github.com/Nolane-x/Nolane-search)";
const MEAL_NOTE = "Recipe catalog provided by TheMealDB. Ingredients and quantities are community-submitted and may be incomplete; check the linked source and use your own judgment for allergies, food safety and dietary needs.";
const WIKIDATA_NOTE = "Wikidata is a community-maintained knowledge base. Labels, descriptions and aliases can be incomplete, disputed or out of date; use the linked Wikidata item and encyclopedia articles to verify important facts.";

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
function httpsUrl(value: unknown, hosts?: string[]): string | null {
  if (typeof value !== "string" || value.length > 2048) return null;
  try {
    const url = new URL(value);
    if (url.protocol !== "https:" || url.username || url.password || url.port) return null;
    if (hosts && !hosts.includes(url.hostname.toLowerCase())) return null;
    return url.toString();
  } catch { return null; }
}
async function getJson<T>(url: URL, provider: string, maxBytes = 450_000): Promise<T> {
  let response: Response;
  try {
    response = await fetch(url, {
      method: "GET",
      headers: { accept: "application/json", "user-agent": USER_AGENT },
      redirect: "error",
      signal: AbortSignal.timeout(12_000),
    });
  } catch {
    throw new Error(provider + " could not be reached or the request timed out.");
  }
  if (!response.ok) {
    await response.body?.cancel().catch(() => undefined);
    if (response.status === 429) throw new Error(provider + " is rate-limiting requests. Reduce query frequency and retry later.");
    if (response.status === 503) throw new Error(provider + " is temporarily unavailable. Retry later.");
    throw new Error(provider + " returned HTTP " + response.status + ".");
  }
  return readJsonResponse<T>(response, maxBytes);
}
function stringField(row: Obj, key: string, max = 5000): string | null {
  const value = row[key];
  if (typeof value !== "string") return null;
  const clean = value.replace(/\u0000/g, "").trim();
  return clean ? clean.slice(0, max) : null;
}
function mealIngredients(row: Obj): Array<{ ingredient: string; measure: string | null }> {
  const ingredients: Array<{ ingredient: string; measure: string | null }> = [];
  for (let index = 1; index <= 20; index += 1) {
    const ingredient = stringField(row, "strIngredient" + index, 120);
    if (!ingredient) continue;
    const measure = stringField(row, "strMeasure" + index, 100);
    ingredients.push({ ingredient, measure });
  }
  return ingredients;
}
function mealCard(row: Obj, details: boolean): Obj | null {
  const id = stringField(row, "idMeal", 24);
  const name = stringField(row, "strMeal", 180);
  if (!id || !/^\d{1,16}$/.test(id) || !name) return null;
  const thumbnail = httpsUrl(row.strMealThumb, ["www.themealdb.com", "themealdb.com"]);
  const youtube = httpsUrl(row.strYoutube, ["www.youtube.com", "youtube.com", "youtu.be", "m.youtube.com"]);
  const source = httpsUrl(row.strSource);
  const result: Obj = {
    meal_id: id,
    name,
    category: stringField(row, "strCategory", 100),
    cuisine_area: stringField(row, "strArea", 100),
    tags: (stringField(row, "strTags", 500) ?? "").split(",").map(value => value.trim()).filter(Boolean).slice(0, 12),
    thumbnail_url: thumbnail,
    source_url: source,
    video_url: youtube,
  };
  if (details) {
    result.instructions = stringField(row, "strInstructions", 7000);
    result.ingredients = mealIngredients(row);
  }
  return result;
}
async function searchMeals(args: Obj): Promise<string> {
  const query = cleanText(args.query, "query", 2, 100);
  const limit = boundedInt(args.limit, "limit", 6, 1, 8);
  const url = new URL(MEAL_BASE + "/search.php");
  url.searchParams.set("s", query);
  const payload = object(await getJson<unknown>(url, "TheMealDB"), "TheMealDB");
  const rows = Array.isArray(payload.meals) ? payload.meals : [];
  const meals = rows.flatMap(row => {
    if (!row || typeof row !== "object" || Array.isArray(row)) return [];
    const normalized = mealCard(row as Obj, false);
    return normalized ? [normalized] : [];
  }).slice(0, limit);
  return JSON.stringify({
    status: meals.length ? "ok" : "not_found",
    source: "TheMealDB",
    source_url: "https://www.themealdb.com/",
    query,
    result_count: meals.length,
    meals,
    note: MEAL_NOTE,
  });
}
async function filterMeals(args: Obj): Promise<string> {
  const keys = ["ingredient", "category", "area"] as const;
  const supplied = keys.filter(key => args[key] !== undefined && args[key] !== null && args[key] !== "");
  if (supplied.length !== 1) throw new Error("Provide exactly one of ingredient, category or area.");
  const key = supplied[0];
  const query = cleanText(args[key], key, 2, 80);
  const limit = boundedInt(args.limit, "limit", 8, 1, 10);
  const param = key === "ingredient" ? "i" : key === "category" ? "c" : "a";
  const url = new URL(MEAL_BASE + "/filter.php");
  url.searchParams.set(param, query);
  const payload = object(await getJson<unknown>(url, "TheMealDB"), "TheMealDB");
  const rows = Array.isArray(payload.meals) ? payload.meals : [];
  const meals = rows.flatMap(row => {
    if (!row || typeof row !== "object" || Array.isArray(row)) return [];
    const meal = row as Obj;
    const id = stringField(meal, "idMeal", 24);
    const name = stringField(meal, "strMeal", 180);
    if (!id || !/^\d{1,16}$/.test(id) || !name) return [];
    return [{
      meal_id: id,
      name,
      thumbnail_url: httpsUrl(meal.strMealThumb, ["www.themealdb.com", "themealdb.com"]),
    }];
  }).slice(0, limit);
  return JSON.stringify({
    status: meals.length ? "ok" : "not_found",
    source: "TheMealDB",
    source_url: "https://www.themealdb.com/",
    filter: { type: key, value: query },
    result_count: meals.length,
    meals,
    limitation: key === "ingredient"
      ? "The free filter endpoint matches one ingredient at a time; it does not prove that a recipe contains every item in a pantry."
      : "This is a catalog filter, not a guarantee that ingredients, local availability or dietary requirements are satisfied.",
    note: MEAL_NOTE,
  });
}
async function lookupMeal(args: Obj): Promise<string> {
  const mealId = cleanText(args.meal_id, "meal_id", 1, 16);
  if (!/^\d{1,16}$/.test(mealId)) throw new Error("meal_id must contain digits only.");
  const url = new URL(MEAL_BASE + "/lookup.php");
  url.searchParams.set("i", mealId);
  const payload = object(await getJson<unknown>(url, "TheMealDB"), "TheMealDB");
  const rows = Array.isArray(payload.meals) ? payload.meals : [];
  const row = rows.find(item => item && typeof item === "object" && !Array.isArray(item) &&
    (item as Obj).idMeal === mealId);
  if (!row || typeof row !== "object" || Array.isArray(row)) {
    return JSON.stringify({ status: "not_found", source: "TheMealDB", meal_id: mealId, note: "No recipe was found for this catalog ID." });
  }
  return JSON.stringify({
    status: "ok",
    source: "TheMealDB",
    source_url: "https://www.themealdb.com/",
    recipe: mealCard(row as Obj, true),
    note: MEAL_NOTE,
  });
}

function languageCode(value: unknown): "en" | "vi" {
  if (value === undefined || value === null || value === "") return "en";
  if (value !== "en" && value !== "vi") throw new Error("language must be en or vi.");
  return value;
}
async function searchWikidata(args: Obj): Promise<string> {
  const query = cleanText(args.query, "query", 2, 120);
  const language = languageCode(args.language);
  const limit = boundedInt(args.limit, "limit", 6, 1, 10);
  const url = new URL(WIKIDATA_API);
  url.searchParams.set("action", "wbsearchentities");
  url.searchParams.set("search", query);
  url.searchParams.set("language", language);
  url.searchParams.set("uselang", language);
  url.searchParams.set("type", "item");
  url.searchParams.set("limit", String(limit));
  url.searchParams.set("format", "json");
  url.searchParams.set("maxlag", "5");
  const payload = object(await getJson<unknown>(url, "Wikidata"), "Wikidata");
  const rows = Array.isArray(payload.search) ? payload.search : [];
  const entities = rows.flatMap(raw => {
    if (!raw || typeof raw !== "object" || Array.isArray(raw)) return [];
    const row = raw as Obj;
    const id = stringField(row, "id", 24);
    const label = stringField(row, "label", 240);
    if (!id || !/^Q[1-9]\d{0,11}$/.test(id) || !label) return [];
    const aliases = Array.isArray(row.aliases)
      ? row.aliases.filter((value): value is string => typeof value === "string").slice(0, 6).map(value => value.slice(0, 180))
      : [];
    return [{
      entity_id: id,
      label,
      description: stringField(row, "description", 500),
      aliases,
      wikidata_url: "https://www.wikidata.org/wiki/" + id,
    }];
  });
  return JSON.stringify({
    status: entities.length ? "ok" : "not_found",
    source: "Wikidata search API",
    source_url: "https://www.wikidata.org/",
    query,
    language,
    result_count: entities.length,
    entities,
    note: WIKIDATA_NOTE,
  });
}
function languageValue(collection: unknown, language: "en" | "vi", key: string): string | null {
  if (!collection || typeof collection !== "object" || Array.isArray(collection)) return null;
  const value = (collection as Obj)[language];
  if (!value || typeof value !== "object" || Array.isArray(value)) return null;
  return stringField(value as Obj, key, 1000);
}
function aliasesValue(collection: unknown, language: "en" | "vi"): string[] {
  if (!collection || typeof collection !== "object" || Array.isArray(collection)) return [];
  const values = (collection as Obj)[language];
  if (!Array.isArray(values)) return [];
  return values.flatMap(value => {
    if (!value || typeof value !== "object" || Array.isArray(value)) return [];
    const alias = stringField(value as Obj, "value", 180);
    return alias ? [alias] : [];
  }).slice(0, 8);
}
async function lookupWikidata(args: Obj): Promise<string> {
  const entityId = cleanText(args.entity_id, "entity_id", 2, 16).toUpperCase();
  if (!/^Q[1-9]\d{0,11}$/.test(entityId)) throw new Error("entity_id must be a Wikidata item ID such as Q42.");
  const url = new URL(WIKIDATA_API);
  url.searchParams.set("action", "wbgetentities");
  url.searchParams.set("ids", entityId);
  url.searchParams.set("props", "labels|descriptions|aliases|sitelinks");
  url.searchParams.set("languages", "en|vi");
  url.searchParams.set("sitefilter", "enwiki|viwiki");
  url.searchParams.set("format", "json");
  url.searchParams.set("maxlag", "5");
  const payload = object(await getJson<unknown>(url, "Wikidata", 250_000), "Wikidata");
  const entities = payload.entities && typeof payload.entities === "object" && !Array.isArray(payload.entities)
    ? payload.entities as Obj : {};
  const row = entities[entityId];
  if (!row || typeof row !== "object" || Array.isArray(row) || (row as Obj).missing !== undefined) {
    return JSON.stringify({ status: "not_found", source: "Wikidata", entity_id: entityId, note: "This Wikidata item does not exist or is unavailable." });
  }
  const entity = row as Obj;
  const sitelinks = entity.sitelinks && typeof entity.sitelinks === "object" && !Array.isArray(entity.sitelinks)
    ? entity.sitelinks as Obj : {};
  const articles = (["enwiki", "viwiki"] as const).flatMap(site => {
    const link = sitelinks[site];
    if (!link || typeof link !== "object" || Array.isArray(link)) return [];
    const title = stringField(link as Obj, "title", 300);
    if (!title) return [];
    const host = site === "enwiki" ? "https://en.wikipedia.org/wiki/" : "https://vi.wikipedia.org/wiki/";
    return [{ language: site === "enwiki" ? "en" : "vi", title, url: host + encodeURIComponent(title.replace(/ /g, "_")) }];
  });
  return JSON.stringify({
    status: "ok",
    source: "Wikidata",
    source_url: "https://www.wikidata.org/wiki/" + entityId,
    entity_id: entityId,
    labels: {
      en: languageValue(entity.labels, "en", "value"),
      vi: languageValue(entity.labels, "vi", "value"),
    },
    descriptions: {
      en: languageValue(entity.descriptions, "en", "value"),
      vi: languageValue(entity.descriptions, "vi", "value"),
    },
    aliases: { en: aliasesValue(entity.aliases, "en"), vi: aliasesValue(entity.aliases, "vi") },
    encyclopedia_articles: articles,
    note: WIKIDATA_NOTE,
  });
}

export async function runConsumerDiscoveryTool(name: string, rawArgs: unknown): Promise<string> {
  if (!rawArgs || typeof rawArgs !== "object" || Array.isArray(rawArgs)) throw new Error("Tool arguments must be a JSON object.");
  const args = rawArgs as Obj;
  if (name === "search_meal_recipes") return searchMeals(args);
  if (name === "filter_meal_recipes") return filterMeals(args);
  if (name === "get_meal_recipe_details") return lookupMeal(args);
  if (name === "search_wikidata_entities") return searchWikidata(args);
  if (name === "get_wikidata_entity") return lookupWikidata(args);
  throw new Error("Unknown consumer discovery tool: " + name + ".");
}
