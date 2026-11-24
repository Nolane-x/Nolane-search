import { readJsonResponse } from "./http";

type Obj = Record<string, unknown>;
const USER_AGENT = "NolaneSearch/0.1 (+https://github.com/Nolane-x/Nolane-search)";
const COMMONS_API = "https://commons.wikimedia.org/w/api.php";
const NASA_API = "https://images-api.nasa.gov";
const NASA_ASSET_HOST = "images-assets.nasa.gov";

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
function safeExternalHttpsUrl(value: unknown): string | null {
  if (typeof value !== "string" || value.length > 2048) return null;
  try {
    const url = new URL(value);
    if (url.protocol !== "https:" || url.port || url.username || url.password) return null;
    return url.toString();
  } catch { return null; }
}
function metadataText(value: unknown, max = 500): string | null {
  if (typeof value === "string") return htmlText(value, max);
  if (Array.isArray(value)) return value.flatMap(item => typeof item === "string" ? [item] : [])
    .map(item => item.trim()).filter(Boolean).join(", ").slice(0, max) || null;
  return null;
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
  provider: "Wikimedia Commons" | "NASA" | "Openverse" | "Internet Archive";
  mediaType: "image" | "video" | "audio";
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

export async function searchOpenverseImages(queryInput: unknown, limitInput?: unknown): Promise<{status:string;source:string;query:string;items:MediaSearchItem[];note:string}> {
  const query = cleanText(queryInput, "query", 2, 160);
  const limit = boundedInt(limitInput, "limit", 8, 1, 10);
  const url = new URL("https://api.openverse.org/v1/images/");
  url.searchParams.set("q", query);
  url.searchParams.set("page_size", String(limit));
  url.searchParams.set("mature", "false");
  url.searchParams.set("filter_dead", "true");
  const payload = object(await fetchJson<unknown>(url, "Openverse", 400_000), "Openverse image search");
  const rows = Array.isArray(payload.results) ? payload.results : [];
  const items = rows.flatMap((raw): MediaSearchItem[] => {
    if (!raw || typeof raw !== "object" || Array.isArray(raw)) return [];
    const row = raw as Obj;
    if (row.mature === true || row.removed_from_source === true) return [];
    const id = typeof row.id === "string" && /^[a-zA-Z0-9-]{8,80}$/.test(row.id) ? row.id : "";
    const title = metadataText(row.title, 220);
    const mediaUrl = safeExternalHttpsUrl(row.url);
    const previewUrl = safeHttpUrl(row.thumbnail, "api.openverse.org");
    const sourceUrl = safeExternalHttpsUrl(row.foreign_landing_url);
    const licenseCode = typeof row.license === "string" ? row.license.toLowerCase().slice(0, 40) : "";
    const licenseUrl = safeHttpUrl(row.license_url, "creativecommons.org");
    if (!id || !title || !mediaUrl || !previewUrl || !sourceUrl || !licenseCode || !licenseUrl) return [];
    const version = typeof row.license_version === "string" ? row.license_version.slice(0, 20) : "";
    return [{
      id,
      title,
      provider: "Openverse",
      mediaType: "image",
      sourceUrl,
      previewUrl,
      mediaUrl,
      description: metadataText(row.description, 600),
      credit: metadataText(row.creator, 240),
      license: (licenseCode.toUpperCase() + (version ? " " + version : "")).slice(0, 60),
      licenseUrl,
      dateCreated: typeof row.indexed_on === "string" ? row.indexed_on.slice(0, 40) : null,
      width: typeof row.width === "number" && Number.isFinite(row.width) ? row.width : null,
      height: typeof row.height === "number" && Number.isFinite(row.height) ? row.height : null,
    }];
  }).slice(0, limit);
  return {
    status: items.length ? "ok" : "not_found",
    source: "Openverse",
    query,
    items,
    note: "Openverse indexes openly licensed and public-domain images, but the license may include attribution, share-alike, non-commercial or no-derivatives conditions. Preserve creator and source links and review the original license before reuse; open licensing does not automatically permit every use.",
  };
}

async function internetArchiveItem(identifier: string, expectedType: "movies" | "audio"): Promise<MediaSearchItem | null> {
  const url = new URL("https://archive.org/metadata/" + encodeURIComponent(identifier));
  const payload = object(await fetchJson<unknown>(url, "Internet Archive item metadata", 350_000), "Internet Archive item metadata");
  const metadata = payload.metadata && typeof payload.metadata === "object" && !Array.isArray(payload.metadata)
    ? payload.metadata as Obj : {};
  const restricted = [metadata["access-restricted-item"], metadata["access-restricted"], metadata.noindex]
    .some(value => value === true || value === 1 || value === "true" || value === "1");
  if (restricted || metadata.mediatype !== expectedType) return null;
  const files = Array.isArray(payload.files) ? payload.files : [];
  const candidates = files.flatMap(raw => {
    if (!raw || typeof raw !== "object" || Array.isArray(raw)) return [];
    const file = raw as Obj;
    if (file.private === true || file.private === 1 || file.private === "true" || file.private === "1") return [];
    if (file.source !== "original") return [];
    const name = typeof file.name === "string" ? file.name : "";
    const format = typeof file.format === "string" ? file.format.toLowerCase() : "";
    if (!name || name.length > 300 || /[\/\\\u0000-\u001f]/.test(name) || name === "." || name === "..") return [];
    const extension = expectedType === "movies" ? /\.(mp4|m4v|webm|ogv)$/i : /\.(mp3|m4a|ogg|oga|opus|flac|wav|aac|aiff)$/i;
    const formatMatch = expectedType === "movies" ? /(mpeg.?4|video|webm|ogg)/i.test(format) : /(mp3|mpeg.?audio|audio|ogg|vorbis|flac|wave|wav|aac|m4a|opus|aiff)/i.test(format);
    if (!extension.test(name) || !formatMatch) return [];
    const size = typeof file.size === "string" || typeof file.size === "number" ? Number(file.size) : 0;
    if (!Number.isSafeInteger(size) || size <= 0) return [];
    return [{ name, size, format }];
  });
  if (!candidates.length) return null;
  candidates.sort((a, b) => {
    const score = (file: {name:string;format:string}) => expectedType === "movies"
      ? (/\.(mp4|m4v)$/i.test(file.name) ? 0 : /webm/i.test(file.name) ? 1 : 2)
      : (/\.mp3$/i.test(file.name) ? 0 : /\.(ogg|oga|opus)$/i.test(file.name) ? 1 : /\.(m4a|aac)$/i.test(file.name) ? 2 : 3);
    return score(a) - score(b) || a.size - b.size;
  });
  const selected = candidates[0];
  const title = metadataText(metadata.title, 220) ?? identifier;
  const path = selected.name.split("/").map(segment => encodeURIComponent(segment)).join("/");
  const licenseUrl = safeHttpUrl(metadata.licenseurl, "creativecommons.org");
  return {
    id: identifier,
    title,
    provider: "Internet Archive",
    mediaType: expectedType === "movies" ? "video" : "audio",
    sourceUrl: "https://archive.org/details/" + encodeURIComponent(identifier),
    previewUrl: safeHttpUrl("https://archive.org/services/img/" + encodeURIComponent(identifier), "archive.org"),
    mediaUrl: "https://archive.org/download/" + encodeURIComponent(identifier) + "/" + path,
    description: metadataText(metadata.description, 700),
    credit: metadataText(metadata.creator ?? metadata.contributor, 240),
    license: metadataText(metadata.license ?? metadata.rights, 120) ?? (licenseUrl ? "Creative Commons (see item)" : "Rights not specified"),
    licenseUrl,
    dateCreated: metadataText(metadata.year ?? metadata.date, 40),
  };
}

export async function searchInternetArchiveVideos(queryInput: unknown, limitInput?: unknown): Promise<{status:string;source:string;query:string;items:MediaSearchItem[];note:string}> {
  const query = cleanText(queryInput, "query", 2, 140);
  const limit = boundedInt(limitInput, "limit", 4, 1, 5);
  const phrase = query.replace(/["\\]/g, " ").replace(/[^\p{L}\p{N}\s-]/gu, " ").replace(/\s+/g, " ").trim();
  if (phrase.length < 2) throw new Error("query must include searchable letters or numbers.");
  const url = new URL("https://archive.org/advancedsearch.php");
  url.searchParams.set("q", 'title:"' + phrase + '" AND mediatype:movies');
  for (const field of ["identifier", "title", "year", "creator", "mediatype"]) url.searchParams.append("fl[]", field);
  url.searchParams.set("rows", String(limit));
  url.searchParams.set("page", "1");
  url.searchParams.set("output", "json");
  const payload = object(await fetchJson<unknown>(url, "Internet Archive search", 300_000), "Internet Archive search");
  const response = payload.response && typeof payload.response === "object" && !Array.isArray(payload.response)
    ? payload.response as Obj : {};
  const docs = Array.isArray(response.docs) ? response.docs : [];
  const identifiers = docs.flatMap(raw => {
    if (!raw || typeof raw !== "object" || Array.isArray(raw)) return [];
    const identifier = (raw as Obj).identifier;
    return typeof identifier === "string" && /^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$/.test(identifier)
      ? [identifier] : [];
  }).slice(0, limit);
  const settled = await Promise.allSettled(identifiers.map(identifier => internetArchiveItem(identifier, "movies")));
  const items = settled.flatMap(result => result.status === "fulfilled" && result.value ? [result.value] : []);
  return {
    status: items.length ? "ok" : "not_found",
    source: "Internet Archive",
    query,
    items,
    note: "Only publicly indexed Internet Archive movie items with a direct original MP4, M4V, WebM or Ogg video file are returned. Access-restricted/private files are omitted. Rights vary by item and may be missing or incomplete: check the item page and rights statement before reuse. Playback links point to archive.org and are not rehosted by Nolane.",
  };
}

export async function searchInternetArchiveAudio(queryInput: unknown, limitInput?: unknown): Promise<{status:string;source:string;query:string;items:MediaSearchItem[];note:string}> {
  const query = cleanText(queryInput, "query", 2, 140);
  const limit = boundedInt(limitInput, "limit", 4, 1, 5);
  const phrase = query.replace(/["\\]/g, " ").replace(/[^\p{L}\p{N}\s-]/gu, " ").replace(/\s+/g, " ").trim();
  if (phrase.length < 2) throw new Error("query must include searchable letters or numbers.");
  const url = new URL("https://archive.org/advancedsearch.php");
  url.searchParams.set("q", 'title:"' + phrase + '" AND mediatype:audio');
  for (const field of ["identifier", "title", "year", "creator", "mediatype"]) url.searchParams.append("fl[]", field);
  url.searchParams.set("rows", String(limit));
  url.searchParams.set("page", "1");
  url.searchParams.set("output", "json");
  const payload = object(await fetchJson<unknown>(url, "Internet Archive audio search", 300_000), "Internet Archive audio search");
  const response = payload.response && typeof payload.response === "object" && !Array.isArray(payload.response)
    ? payload.response as Obj : {};
  const docs = Array.isArray(response.docs) ? response.docs : [];
  const identifiers = docs.flatMap(raw => {
    if (!raw || typeof raw !== "object" || Array.isArray(raw)) return [];
    const identifier = (raw as Obj).identifier;
    return typeof identifier === "string" && /^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$/.test(identifier)
      ? [identifier] : [];
  }).slice(0, limit);
  const settled = await Promise.allSettled(identifiers.map(identifier => internetArchiveItem(identifier, "audio")));
  const items = settled.flatMap(result => result.status === "fulfilled" && result.value ? [result.value] : []);
  return {
    status: items.length ? "ok" : "not_found",
    source: "Internet Archive",
    query,
    items,
    note: "Only public Internet Archive audio items with a listed non-private original MP3, M4A, Ogg, Opus, FLAC, WAV, AAC or AIFF file are returned. Access-restricted/private files and derivatives are omitted. Rights vary by item and may be missing or incomplete: inspect the original item page and rights statement before reuse. Audio links point to archive.org and are not rehosted by Nolane.",
  };
}

type OffProductType = "all" | "food" | "beauty" | "petfood" | "product";
type OffReadResult = { status: "ok"; host: string; row: Obj } | { status: "not_found"; host: string };
const OFF_HOSTS: Record<Exclude<OffProductType, "all">, string> = {
  food: "world.openfoodfacts.org",
  beauty: "world.openbeautyfacts.org",
  petfood: "world.openpetfoodfacts.org",
  product: "world.openproductsfacts.org",
};
const OFF_DATABASE_NAMES: Record<Exclude<OffProductType, "all">, string> = {
  food: "Open Food Facts",
  beauty: "Open Beauty Facts",
  petfood: "Open Pet Food Facts",
  product: "Open Products Facts",
};
const OFF_FIELDS = [
  "code", "product_type", "product_name", "product_name_en", "generic_name", "brands", "quantity",
  "categories", "categories_tags", "ingredients_text", "ingredients_text_en", "allergens", "allergens_tags",
  "traces", "traces_tags", "labels", "nutriscore_grade", "nutriscore_score", "nova_group",
  "environmental_score_grade", "environmental_score_score", "nutrition", "nutriments", "image_front_url", "image_url", "lang",
].join(",");

function validBarcode(value: unknown): string {
  if (typeof value !== "string" || !/^\d{8,14}$/.test(value.trim())) {
    throw new Error("barcode must contain 8 to 14 digits (EAN/UPC/GTIN).");
  }
  return value.trim();
}
function offProductType(value: unknown, fallback: OffProductType = "all"): OffProductType {
  if (value === undefined || value === null || value === "") return fallback;
  if (typeof value !== "string" || !["all","food","beauty","petfood","product"].includes(value)) {
    throw new Error("product_type must be all, food, beauty, petfood or product.");
  }
  return value as OffProductType;
}
function buildOffProductUrl(host: string, barcode: string, type: OffProductType): URL {
  const url = new URL("https://" + host + "/api/v3/product/" + encodeURIComponent(barcode));
  url.searchParams.set("fields", OFF_FIELDS);
  url.searchParams.set("product_type", type);
  return url;
}
function isOffRedirectTarget(value: string, barcode: string, base: URL): URL | null {
  try {
    const target = new URL(value, base);
    const hosts = Object.values(OFF_HOSTS);
    const pathPattern = new RegExp("^/api/v3/product/" + barcode + "(?:\\.json)?$");
    if (target.protocol !== "https:" || !hosts.includes(target.hostname) || target.username || target.password ||
        target.port || !pathPattern.test(target.pathname)) return null;
    return target;
  } catch { return null; }
}
async function fetchOffProductResponse(url: URL, provider: string, barcode: string, allowRedirect: boolean): Promise<{response:Response;finalUrl:URL}|null> {
  let response: Response;
  try {
    response = await fetch(url, {
      method: "GET",
      headers: { accept: "application/json", "user-agent": USER_AGENT },
      redirect: "manual",
      signal: AbortSignal.timeout(12_000),
    });
  } catch {
    throw new Error(provider + " could not be reached or the request timed out.");
  }
  if (response.status === 404) {
    await response.body?.cancel().catch(() => undefined);
    return null;
  }
  if (response.status >= 300 && response.status < 400) {
    const location = response.headers.get("location");
    await response.body?.cancel().catch(() => undefined);
    if (!allowRedirect || !location) throw new Error(provider + " returned an unexpected redirect.");
    const target = isOffRedirectTarget(location, barcode, url);
    if (!target) throw new Error(provider + " returned a redirect outside the approved Open Facts databases.");
    target.search = url.search;
    return fetchOffProductResponse(target, provider, barcode, false);
  }
  if (!response.ok) {
    await response.body?.cancel().catch(() => undefined);
    if (response.status === 429 || response.status === 503) {
      throw new Error(provider + " is temporarily rate-limiting requests. Reduce query frequency and retry later.");
    }
    throw new Error(provider + " returned HTTP " + response.status + ".");
  }
  return { response, finalUrl: url };
}
async function readOffProduct(barcode: string, type: OffProductType): Promise<OffReadResult> {
  const initialHost = type === "all" ? OFF_HOSTS.food : OFF_HOSTS[type];
  const url = buildOffProductUrl(initialHost, barcode, type);
  const provider = type === "all" ? "Open Facts" : OFF_DATABASE_NAMES[type];
  const fetched = await fetchOffProductResponse(url, provider, barcode, true);
  if (!fetched) return { status: "not_found", host: initialHost };
  const payload = object(await readJsonResponse<unknown>(fetched.response, 400_000), provider);
  const statusValue = payload.status;
  const isSuccessful = statusValue === "success" || statusValue === "success_with_warnings" ||
    statusValue === "success_with_errors" || statusValue === 1;
  if (!isSuccessful || !payload.product || typeof payload.product !== "object" || Array.isArray(payload.product)) {
    if (statusValue === "failure") {
      const errors = Array.isArray(payload.errors) ? payload.errors.length : 0;
      if (errors) throw new Error(provider + " could not read this product (API reported a failure).");
    }
    return { status: "not_found", host: fetched.finalUrl.hostname };
  }
  return { status: "ok", host: fetched.finalUrl.hostname, row: payload.product as Obj };
}
function offNumber(value: unknown): number | null {
  if (typeof value === "number") return Number.isFinite(value) ? value : null;
  if (typeof value === "string" && /^-?\d+(?:\.\d+)?$/.test(value.trim())) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
}
function offImage(value: unknown): string | null {
  if (typeof value !== "string" || value.length > 2048) return null;
  try {
    const url = new URL(value);
    const allowed = [
      "images.openfoodfacts.org", "images.openbeautyfacts.org",
      "images.openpetfoodfacts.org", "images.openproductsfacts.org",
    ];
    return url.protocol === "https:" && allowed.includes(url.hostname) && !url.username && !url.password && !url.port
      ? url.toString() : null;
  } catch { return null; }
}
function offString(value: unknown, max: number): string | null {
  if (typeof value !== "string") return null;
  const clean = value.replace(/\u0000/g, "").trim();
  return clean ? clean.slice(0, max) : null;
}
function offList(value: unknown, maxItems = 20): string[] {
  if (!Array.isArray(value)) return [];
  return value.filter((item): item is string => typeof item === "string")
    .map(item => item.slice(0, 100)).slice(0, maxItems);
}
function nutritionValue(container: Obj, name: string): number | null {
  const field = container[name];
  if (!field || typeof field !== "object" || Array.isArray(field)) return null;
  const value = (field as Obj).value ?? (field as Obj).value_computed;
  return offNumber(value);
}
function normalizeOffProduct(row: Obj, barcode: string, host: string): Obj {
  const v3Nutrition = row.nutrition && typeof row.nutrition === "object" && !Array.isArray(row.nutrition)
    ? row.nutrition as Obj : {};
  const aggregatedSet = v3Nutrition.aggregated_set && typeof v3Nutrition.aggregated_set === "object" &&
      !Array.isArray(v3Nutrition.aggregated_set) ? v3Nutrition.aggregated_set as Obj : {};
  const aggregatedNutrients = aggregatedSet.nutrients && typeof aggregatedSet.nutrients === "object" &&
      !Array.isArray(aggregatedSet.nutrients) ? aggregatedSet.nutrients as Obj : {};
  const legacyNutrition = row.nutriments && typeof row.nutriments === "object" && !Array.isArray(row.nutriments)
    ? row.nutriments as Obj : {};
  const v3Per = aggregatedSet.per;
  const nutritionReference = v3Per === "100g" || v3Per === "100ml" || v3Per === "serving"
    ? v3Per : (Object.keys(aggregatedNutrients).length ? "unknown" : "100g");
  const isPer100g = Object.keys(aggregatedNutrients).length
    ? v3Per === "100g"
    : true;
  const choose = (modern: string, legacy: string) => {
    if (Object.keys(aggregatedNutrients).length) {
      return isPer100g ? nutritionValue(aggregatedNutrients, modern) : null;
    }
    return offNumber(legacyNutrition[legacy]);
  };
  const nutritionPer100g = {
    energy_kcal: choose("energy-kcal", "energy-kcal_100g"),
    fat_g: choose("fat", "fat_100g"),
    saturated_fat_g: choose("saturated-fat", "saturated-fat_100g"),
    carbohydrates_g: choose("carbohydrates", "carbohydrates_100g"),
    sugars_g: choose("sugars", "sugars_100g"),
    fiber_g: choose("fiber", "fiber_100g"),
    proteins_g: choose("proteins", "proteins_100g"),
    salt_g: choose("salt", "salt_100g"),
  };
  const productType = typeof row.product_type === "string" && ["food","beauty","petfood","product"].includes(row.product_type)
    ? row.product_type as Exclude<OffProductType,"all">
    : (Object.entries(OFF_HOSTS).find(([, value]) => value === host)?.[0] as Exclude<OffProductType,"all"> | undefined) ?? "food";
  return {
    barcode: offString(row.code, 24) ?? barcode,
    product_type: productType,
    name: offString(row.product_name, 180) ?? offString(row.product_name_en, 180) ?? offString(row.generic_name, 180),
    generic_name: offString(row.generic_name, 180),
    brands: offString(row.brands, 220),
    quantity: offString(row.quantity, 80),
    categories: typeof row.categories === "string"
      ? row.categories.split(",").slice(0, 15).map(x => x.trim()).filter(Boolean)
      : offList(row.categories_tags, 15),
    ingredients: offString(row.ingredients_text, 1200) ?? offString(row.ingredients_text_en, 1200),
    allergens: offString(row.allergens, 500),
    allergens_tags: offList(row.allergens_tags, 30),
    traces: offString(row.traces, 400),
    labels: offString(row.labels, 500),
    nutriscore_grade: offString(row.nutriscore_grade, 12),
    nutriscore_score: offNumber(row.nutriscore_score),
    nova_group: offNumber(row.nova_group),
    environmental_score_grade: offString(row.environmental_score_grade, 12),
    environmental_score_score: offNumber(row.environmental_score_score),
    nutrition_reference: nutritionReference,
    nutrition_per_100g: nutritionPer100g,
    image_front_url: offImage(row.image_front_url),
    image_url: offImage(row.image_url),
    language: offString(row.lang, 12),
    source_url: "https://" + host + "/product/" + barcode,
  };
}
async function getOffProduct(barcodeInput: unknown, typeInput: unknown): Promise<{status:"ok";provider:string;product:Obj;barcode:string}|{status:"not_found";provider:string;barcode:string}> {
  const barcode = validBarcode(barcodeInput);
  const type = offProductType(typeInput);
  const found = await readOffProduct(barcode, type);
  if (found.status === "not_found") return { status: "not_found", provider: type === "all" ? "Open Facts" : OFF_DATABASE_NAMES[type], barcode };
  const product = normalizeOffProduct(found.row, barcode, found.host);
  const databaseType = product.product_type as Exclude<OffProductType,"all">;
  return {
    status: "ok",
    provider: OFF_DATABASE_NAMES[databaseType],
    product,
    barcode,
  };
}
const OFF_DATA_NOTE = "Open Facts databases are community-contributed; product fields may be incomplete, user-entered or outdated. Nutrition data, when present, is per 100 g and is not medical or dietary advice. Database contents are published under the Open Database License (ODbL); attribute the source and comply with share-alike requirements.";
export async function lookupConsumerProduct(barcodeInput: unknown, typeInput?: unknown): Promise<string> {
  const result = await getOffProduct(barcodeInput, typeInput);
  if (result.status === "not_found") {
    return JSON.stringify({
      status: "not_found",
      source: result.provider,
      barcode: result.barcode,
      note: "No product was found for this barcode in the selected Open Facts catalog. The record may be missing or not yet indexed.",
    });
  }
  return JSON.stringify({
    status: "ok",
    source: result.provider,
    barcode: result.barcode,
    product: result.product,
    note: OFF_DATA_NOTE,
  });
}
export async function lookupFoodProduct(barcodeInput: unknown): Promise<string> {
  const result = await lookupConsumerProduct(barcodeInput, "food");
  const payload = JSON.parse(result) as Obj;
  if (payload.status === "ok") payload.source = "Open Food Facts";
  return JSON.stringify(payload);
}
export async function compareFoodProducts(barcodesInput: unknown): Promise<string> {
  if (!Array.isArray(barcodesInput) || barcodesInput.length < 2 || barcodesInput.length > 4) {
    throw new Error("barcodes must contain between 2 and 4 food product barcodes.");
  }
  const barcodes = barcodesInput.map(value => validBarcode(value));
  if (new Set(barcodes).size !== barcodes.length) throw new Error("barcodes must be unique.");
  const products: Array<{ barcode:string; product:Obj }> = [];
  for (const barcode of barcodes) {
    const found = await getOffProduct(barcode, "food");
    if (found.status === "ok" && found.product.product_type === "food") {
      products.push({ barcode, product: found.product });
    } else {
      products.push({ barcode, product: { barcode, not_found: true, reason: found.status === "ok" ? "not_a_food_product" : "not_found" } });
    }
  }
  const metricSpecs: Array<{key:string;label:string;unit:string}> = [
    { key: "energy_kcal", label: "Energy", unit: "kcal/100 g" },
    { key: "fat_g", label: "Fat", unit: "g/100 g" },
    { key: "saturated_fat_g", label: "Saturated fat", unit: "g/100 g" },
    { key: "sugars_g", label: "Sugars", unit: "g/100 g" },
    { key: "fiber_g", label: "Fiber", unit: "g/100 g" },
    { key: "proteins_g", label: "Protein", unit: "g/100 g" },
    { key: "salt_g", label: "Salt", unit: "g/100 g" },
  ];
  const comparisons = metricSpecs.flatMap(spec => {
    const values = products.flatMap(item => {
      const nutrition = item.product.nutrition_per_100g && typeof item.product.nutrition_per_100g === "object"
        ? item.product.nutrition_per_100g as Obj : {};
      const value = offNumber(nutrition[spec.key]);
      return item.product.not_found !== true && value !== null ? [{ barcode: item.barcode, value }] : [];
    });
    if (values.length < 2) return [];
    const sorted = [...values].sort((a, b) => a.value - b.value);
    return [{ metric: spec.label, unit: spec.unit, values, minimum: sorted[0], maximum: sorted[sorted.length - 1] }];
  });
  return JSON.stringify({
    status: products.filter(item => item.product.not_found !== true).length >= 2 ? "ok" : "insufficient_data",
    source: "Open Food Facts",
    products,
    comparison_basis: "Values are compared per 100 g only. Lower or higher values are descriptive comparisons, not a health ranking or dietary recommendation.",
    comparisons,
    note: OFF_DATA_NOTE,
  });
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
  if (name === "search_openverse_images") {
    return JSON.stringify(await searchOpenverseImages(args.query, args.limit));
  }
  if (name === "search_internet_archive_audio") {
    return JSON.stringify(await searchInternetArchiveAudio(args.query, args.limit));
  }
  if (name === "search_internet_archive_videos") {
    return JSON.stringify(await searchInternetArchiveVideos(args.query, args.limit));
  }
  if (name === "lookup_food_product") return lookupFoodProduct(args.barcode);
  if (name === "lookup_consumer_product") return lookupConsumerProduct(args.barcode, args.product_type);
  if (name === "compare_food_products") return compareFoodProducts(args.barcodes);
  throw new Error("Unknown media discovery tool.");
}
