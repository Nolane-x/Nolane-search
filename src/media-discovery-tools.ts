import { readJsonResponse } from "./http";

type Obj = Record<string, unknown>;
const USER_AGENT = "NolaneSearch/0.1 (+https://github.com/Nolane-x/Nolane-search)";
const COMMONS_API = "https://commons.wikimedia.org/w/api.php";
const NASA_API = "https://images-api.nasa.gov";
const NASA_ASSET_HOST = "images-assets.nasa.gov";
const OFF_API = "https://world.openfoodfacts.org/api/v3/product";

function object(value: unknown, label: string): Obj {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error(label + " returned an unexpected response.");
  return value as Obj;
}
function cleanText(value: unknown, key: string, min = 2, max = 160): string {
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
function safeHttpUrl(value: unknown, host: string): string | null {
  if (typeof value !== "string" || value.length > 2048) return null;
  try {
    const url = new URL(value);
    if (url.protocol !== "https:" || url.hostname !== host || url.port || url.username || url.password) return null;
    return url.toString();
  } catch { return null; }
}
async function fetchJson<T>(url: URL, provider: string, maxBytes = 500_000): Promise<T> {
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
    if (response.status === 429 || response.status === 503) {
      throw new Error(provider + " is temporarily rate-limiting requests. Reduce query frequency and retry later.");
    }
    throw new Error(provider + " returned HTTP " + response.status + ".");
  }
  return readJsonResponse<T>(response, maxBytes);
}
function htmlText(value: unknown, max = 500): string | null {
  if (typeof value !== "string" || !value) return null;
  const decoded = value.replace(/<br\s*\/?\s*>/gi, " ").replace(/<[^>]*>/g, " ")
    .replace(/&nbsp;/gi, " ").replace(/&amp;/gi, "&").replace(/&quot;/gi, '"')
    .replace(/&#39;|&apos;/gi, "'").replace(/&lt;/gi, "<").replace(/&gt;/gi, ">")
    .replace(/&#(\d+);/g, (_m, n: string) => String.fromCodePoint(Math.min(0x10ffff, Number(n))))
    .replace(/&#x([0-9a-f]+);/gi, (_m, n: string) => String.fromCodePoint(Math.min(0x10ffff, parseInt(n, 16))))
    .replace(/\s+/g, " ").trim();
  return decoded ? decoded.slice(0, max) : null;
}
function extValue(metadata: Obj, key: string): string | null {
  const item = metadata[key];
  if (!item || typeof item !== "object" || Array.isArray(item)) return null;
  return htmlText((item as Obj).value, 400);
}

export interface MediaSearchItem {
  id: string;
  title: string;
  provider: "Wikimedia Commons" | "NASA";
  mediaType: "image" | "video";
  sourceUrl: string;
  previewUrl: string | null;
  mediaUrl: string | null;
  description: string | null;
  credit: string | null;
  license: string | null;
  licenseUrl: string | null;
  dateCreated: string | null;
  width?: number | null;
  height?: number | null;
  duration?: number | null;
}

export async function searchWikimediaImages(queryInput: unknown, limitInput?: unknown): Promise<{status:string;source:string;query:string;items:MediaSearchItem[];note:string}> {
  const query = cleanText(queryInput, "query", 2, 160);
  const limit = boundedInt(limitInput, "limit", 8, 1, 12);
  const url = new URL(COMMONS_API);
  url.searchParams.set("action", "query");
  url.searchParams.set("format", "json");
  url.searchParams.set("formatversion", "2");
  url.searchParams.set("generator", "search");
  url.searchParams.set("gsrsearch", query);
  url.searchParams.set("gsrnamespace", "6");
  url.searchParams.set("gsrlimit", String(limit));
  url.searchParams.set("prop", "imageinfo");
  url.searchParams.set("iiprop", "url|size|mime|extmetadata");
  url.searchParams.set("iiurlwidth", "720");
  url.searchParams.set("iiextmetadatalanguage", "en");
  const payload = object(await fetchJson<unknown>(url, "Wikimedia Commons"), "Wikimedia Commons");
  const queryObject = payload.query && typeof payload.query === "object" ? payload.query as Obj : {};
  const pages = Array.isArray(queryObject.pages) ? queryObject.pages : [];
  const items = pages.flatMap((entry): MediaSearchItem[] => {
    if (!entry || typeof entry !== "object" || Array.isArray(entry)) return [];
    const page = entry as Obj;
    const info = Array.isArray(page.imageinfo) ? page.imageinfo[0] : null;
    if (!info || typeof info !== "object" || Array.isArray(info)) return [];
    const image = info as Obj;
    const mime = typeof image.mime === "string" ? image.mime : "";
    if (!mime.startsWith("image/") || mime === "image/svg+xml") return [];
    const metadata = image.extmetadata && typeof image.extmetadata === "object" && !Array.isArray(image.extmetadata)
      ? image.extmetadata as Obj : {};
    const license = extValue(metadata, "LicenseShortName");
    const licenseUrl = extValue(metadata, "LicenseUrl");
    const mediaUrl = safeHttpUrl(image.url, "upload.wikimedia.org");
    const previewUrl = safeHttpUrl(image.thumburl, "upload.wikimedia.org") ?? mediaUrl;
    const sourceUrl = safeHttpUrl(image.descriptionurl, "commons.wikimedia.org");
    if (!license || !licenseUrl || !mediaUrl || !previewUrl || !sourceUrl) return [];
    const title = typeof page.title === "string" ? page.title.replace(/^File:/, "").slice(0, 220) : "Untitled Commons image";
    return [{
      id: String(page.pageid ?? title),
      title,
      provider: "Wikimedia Commons",
      mediaType: "image",
      sourceUrl,
      previewUrl,
      mediaUrl,
      description: extValue(metadata, "ImageDescription") ?? extValue(metadata, "ObjectName"),
      credit: extValue(metadata, "Credit") ?? extValue(metadata, "Artist"),
      license,
      licenseUrl,
      dateCreated: extValue(metadata, "DateTimeOriginal"),
      width: typeof image.width === "number" ? image.width : null,
      height: typeof image.height === "number" ? image.height : null,
    }];
  });
  return {
    status: items.length ? "ok" : "not_found",
    source: "Wikimedia Commons MediaWiki API",
    query,
    items,
    note: "Wikimedia Commons results are subject to file-specific licenses. Reuse only after reviewing the source page, license URL and required attribution; some licenses require attribution or share-alike conditions.",
  };
}

function nasaDescription(item: Obj): string | null {
  const raw = item.description ?? item.description_508;
  return typeof raw === "string" ? raw.replace(/<[^>]*>/g, " ").replace(/\s+/g, " ").trim().slice(0, 700) || null : null;
}
async function nasaVideoUrl(nasaId: string): Promise<string | null> {
  const url = new URL("/asset/" + encodeURIComponent(nasaId), NASA_API);
  const payload = object(await fetchJson<unknown>(url, "NASA asset manifest", 200_000), "NASA asset manifest");
  const collection = payload.collection && typeof payload.collection === "object" ? payload.collection as Obj : {};
  const entries = Array.isArray(collection.items) ? collection.items : [];
  const candidates = entries.flatMap(item => {
    if (!item || typeof item !== "object" || Array.isArray(item)) return [];
    const href = (item as Obj).href;
    const safe = safeHttpUrl(href, NASA_ASSET_HOST);
    if (!safe) return [];
    const path = new URL(safe).pathname.toLowerCase();
    return path.endsWith(".mp4") ? [safe] : [];
  });
  candidates.sort((a,b) => {
    const score = (u:string) => /~orig\.mp4$/i.test(u) ? 0 : /~large\.mp4$/i.test(u) ? 1 : 2;
    return score(a)-score(b) || a.length-b.length;
  });
  return candidates[0] ?? null;
}
export async function searchNasaMedia(queryInput: unknown, mediaTypeInput?: unknown, limitInput?: unknown): Promise<{status:string;source:string;query:string;mediaType:string;items:MediaSearchItem[];note:string}> {
  const query = cleanText(queryInput, "query", 2, 160);
  const mediaType = mediaTypeInput === undefined ? "all" : mediaTypeInput;
  if (mediaType !== "all" && mediaType !== "image" && mediaType !== "video") throw new Error("media_type must be image, video or all.");
  const limit = boundedInt(limitInput, "limit", 6, 1, 8);
  const url = new URL("/search", NASA_API);
  url.searchParams.set("q", query);
  url.searchParams.set("media_type", mediaType === "all" ? "image,video" : mediaType);
  url.searchParams.set("page_size", String(limit));
  const payload = object(await fetchJson<unknown>(url, "NASA Image and Video Library"), "NASA media search");
  const collection = payload.collection && typeof payload.collection === "object" ? payload.collection as Obj : {};
  const entries = Array.isArray(collection.items) ? collection.items : [];
  const items: MediaSearchItem[] = [];
  for (const raw of entries.slice(0, limit)) {
    if (!raw || typeof raw !== "object" || Array.isArray(raw)) continue;
    const entry = raw as Obj;
    const data = Array.isArray(entry.data) ? entry.data[0] : null;
    if (!data || typeof data !== "object" || Array.isArray(data)) continue;
    const row = data as Obj;
    const nasaId = typeof row.nasa_id === "string" ? row.nasa_id : "";
    const kind = row.media_type === "video" ? "video" : row.media_type === "image" ? "image" : null;
    if (!nasaId || !kind) continue;
    const links = Array.isArray(entry.links) ? entry.links : [];
    let preview: string | null = null;
    for (const link of links) {
      if (link && typeof link === "object" && !Array.isArray(link)) {
        const objLink = link as Obj;
        preview = safeHttpUrl(objLink.href, NASA_ASSET_HOST);
        if (preview && objLink.rel === "preview") break;
      }
    }
    const sourceUrl = "https://images.nasa.gov/details/" + encodeURIComponent(nasaId);
    let mediaUrl: string | null = kind === "image" ? preview : null;
    if (kind === "video") {
      try { mediaUrl = await nasaVideoUrl(nasaId); } catch { mediaUrl = null; }
    }
    items.push({
      id: nasaId,
      title: typeof row.title === "string" ? row.title.slice(0, 220) : nasaId,
      provider: "NASA",
      mediaType: kind,
      sourceUrl,
      previewUrl: preview,
      mediaUrl,
      description: nasaDescription(row),
      credit: [row.photographer, row.secondary_creator, row.center].filter(x => typeof x === "string" && x.trim()).join(" · ").slice(0, 300) || null,
      license: "NASA media terms",
      licenseUrl: "https://www.nasa.gov/nasa-brand-center/images-and-media/",
      dateCreated: typeof row.date_created === "string" ? row.date_created.slice(0, 40) : null,
    });
  }
  return {
    status: items.length ? "ok" : "not_found",
    source: "NASA Image and Video Library",
    query,
    mediaType,
    items,
    note: "NASA provides these media assets for public use subject to NASA's media usage guidelines. Do not imply NASA endorsement; some third-party material and identifiable persons may have additional restrictions. Video files are only returned when the public asset manifest lists a direct MP4.",
  };
}

export async function lookupFoodProduct(barcodeInput: unknown): Promise<string> {
  if (typeof barcodeInput !== "string" || !/^\d{8,14}$/.test(barcodeInput.trim())) {
    throw new Error("barcode must contain 8 to 14 digits (EAN/UPC).");
  }
  const barcode = barcodeInput.trim();
  const url = new URL(OFF_API + "/" + barcode + ".json");
  url.searchParams.set("fields", [
    "code", "product_name", "product_name_en", "brands", "quantity", "categories",
    "ingredients_text", "ingredients_text_en", "allergens", "allergens_tags", "labels",
    "nutriscore_grade", "nutrition_grades_tags", "nova_group", "ecoscore_grade",
    "nutriments", "image_front_url", "image_url", "url", "lang",
  ].join(","));
  const payload = object(await fetchJson<unknown>(url, "Open Food Facts", 350_000), "Open Food Facts");
  if (payload.status !== 1 || !payload.product || typeof payload.product !== "object" || Array.isArray(payload.product)) {
    return JSON.stringify({status:"not_found",source:"Open Food Facts",barcode,note:"Barcode not found in the community-maintained database."});
  }
  const row = payload.product as Obj;
  const nutrition = row.nutriments && typeof row.nutriments === "object" && !Array.isArray(row.nutriments)
    ? row.nutriments as Obj : {};
  const safeImage = (v: unknown) => {
    if (typeof v !== "string" || v.length > 2048) return null;
    try { const u = new URL(v); return u.protocol === "https:" && ["images.openfoodfacts.org","world.openfoodfacts.org"].includes(u.hostname) ? u.toString() : null; }
    catch { return null; }
  };
  const result = {
    status: "ok",
    source: "Open Food Facts",
    source_url: "https://world.openfoodfacts.org/product/" + barcode,
    barcode,
    product: {
      name: typeof row.product_name === "string" ? row.product_name.slice(0,180) : typeof row.product_name_en === "string" ? row.product_name_en.slice(0,180) : null,
      brands: typeof row.brands === "string" ? row.brands.slice(0,220) : null,
      quantity: typeof row.quantity === "string" ? row.quantity.slice(0,80) : null,
      categories: typeof row.categories === "string" ? row.categories.split(",").slice(0,15).map(x=>x.trim()).filter(Boolean) : [],
      ingredients: typeof row.ingredients_text === "string" ? row.ingredients_text.slice(0,1200) : typeof row.ingredients_text_en === "string" ? row.ingredients_text_en.slice(0,1200) : null,
      allergens: typeof row.allergens === "string" ? row.allergens.slice(0,500) : null,
      allergens_tags: Array.isArray(row.allergens_tags) ? row.allergens_tags.filter(x=>typeof x==="string").slice(0,30) : [],
      labels: typeof row.labels === "string" ? row.labels.slice(0,500) : null,
      nutriscore_grade: typeof row.nutriscore_grade === "string" ? row.nutriscore_grade : null,
      nova_group: typeof row.nova_group === "number" ? row.nova_group : null,
      ecoscore_grade: typeof row.ecoscore_grade === "string" ? row.ecoscore_grade : null,
      nutrition_per_100g: {
        energy_kcal: typeof nutrition["energy-kcal_100g"] === "number" ? nutrition["energy-kcal_100g"] : null,
        fat_g: typeof nutrition.fat_100g === "number" ? nutrition.fat_100g : null,
        saturated_fat_g: typeof nutrition["saturated-fat_100g"] === "number" ? nutrition["saturated-fat_100g"] : null,
        carbohydrates_g: typeof nutrition.carbohydrates_100g === "number" ? nutrition.carbohydrates_100g : null,
        sugars_g: typeof nutrition.sugars_100g === "number" ? nutrition.sugars_100g : null,
        fiber_g: typeof nutrition.fiber_100g === "number" ? nutrition.fiber_100g : null,
        proteins_g: typeof nutrition.proteins_100g === "number" ? nutrition.proteins_100g : null,
        salt_g: typeof nutrition.salt_100g === "number" ? nutrition.salt_100g : null,
      },
      image_front_url: safeImage(row.image_front_url),
      image_url: safeImage(row.image_url),
      language: typeof row.lang === "string" ? row.lang : null,
    },
    note: "Open Food Facts is community-contributed data; product fields may be incomplete, user-entered or outdated. Nutrition values are per 100 g and do not constitute medical or dietary advice. Database contents are published under the Open Database License (ODbL); attribute Open Food Facts and share-alike database adaptations as required.",
  };
  return JSON.stringify(result);
}

export async function runMediaDiscoveryTool(name: string, rawArgs: unknown): Promise<string> {
  if (!rawArgs || typeof rawArgs !== "object" || Array.isArray(rawArgs)) throw new Error("Tool arguments must be a JSON object.");
  const args = rawArgs as Obj;
  if (name === "search_wikimedia_images") {
    return JSON.stringify(await searchWikimediaImages(args.query, args.limit));
  }
  if (name === "search_nasa_media") {
    return JSON.stringify(await searchNasaMedia(args.query, args.media_type, args.limit));
  }
  if (name === "lookup_food_product") return lookupFoodProduct(args.barcode);
  throw new Error("Unknown media discovery tool.");
}
