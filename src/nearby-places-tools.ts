import { readJsonResponse } from "./http";
import { isSafePublicUrl } from "./security";

export const NEARBY_CATEGORIES = [
  "food",
  "shopping",
  "pharmacy",
  "medical",
  "atm",
  "fuel",
  "charging",
  "parks",
  "sightseeing",
  "stay",
  "essentials",
] as const;

export type NearbyCategory = typeof NEARBY_CATEGORIES[number];

type TagFilter = { key: "amenity" | "shop" | "leisure" | "tourism"; values: readonly string[] };
type CategoryDefinition = { label: string; filters: readonly TagFilter[] };

const CATEGORIES: Record<NearbyCategory, CategoryDefinition> = {
  food: {
    label: "Ăn uống",
    filters: [{ key: "amenity", values: ["restaurant", "cafe", "fast_food", "food_court"] }],
  },
  shopping: {
    label: "Mua sắm",
    filters: [{ key: "shop", values: ["supermarket", "convenience", "mall", "department_store"] }],
  },
  pharmacy: {
    label: "Nhà thuốc",
    filters: [{ key: "amenity", values: ["pharmacy"] }],
  },
  medical: {
    label: "Y tế",
    filters: [{ key: "amenity", values: ["hospital", "clinic", "doctors", "dentist"] }],
  },
  atm: {
    label: "ATM / Ngân hàng",
    filters: [{ key: "amenity", values: ["atm", "bank"] }],
  },
  fuel: {
    label: "Trạm xăng",
    filters: [{ key: "amenity", values: ["fuel"] }],
  },
  charging: {
    label: "Trạm sạc",
    filters: [{ key: "amenity", values: ["charging_station"] }],
  },
  parks: {
    label: "Công viên",
    filters: [{ key: "leisure", values: ["park", "playground", "garden"] }],
  },
  sightseeing: {
    label: "Điểm tham quan",
    filters: [{ key: "tourism", values: ["attraction", "museum", "viewpoint", "gallery"] }],
  },
  stay: {
    label: "Lưu trú",
    filters: [{ key: "tourism", values: ["hotel", "hostel", "guest_house"] }],
  },
  essentials: {
    label: "Tiện ích thiết yếu",
    filters: [
      { key: "amenity", values: ["restaurant", "cafe", "fast_food", "pharmacy", "hospital", "clinic", "doctors", "dentist", "atm", "bank", "fuel", "charging_station"] },
      { key: "shop", values: ["supermarket", "convenience"] },
    ],
  },
};

const OVERPASS_ENDPOINT = "https://overpass-api.de/api/interpreter";
const USER_AGENT = "NolaneSearch/0.1 (+https://github.com/Nolane-x/Nolane-search)";
// Essentials keeps its combined public Overpass scan bounded to one request and a 3 km radius.
const MAX_RESPONSE_BYTES = 2_000_000;

export class NearbyPlacesInputError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "NearbyPlacesInputError";
  }
}

type OverpassElement = {
  type?: unknown;
  id?: unknown;
  lat?: unknown;
  lon?: unknown;
  center?: { lat?: unknown; lon?: unknown } | null;
  tags?: Record<string, unknown> | null;
};

type OverpassPayload = {
  elements?: unknown;
  remark?: unknown;
  osm3s?: { timestamp_osm_base?: unknown } | null;
};

export interface NearbyPlace {
  id: string;
  name: string;
  category: NearbyCategory;
  categoryLabel: string;
  detailType: string;
  latitude: number;
  longitude: number;
  distanceMeters: number;
  osmUrl: string;
  mapUrl: string;
  address: string | null;
  openingHours: string | null;
  website: string | null;
}

export interface NearbyPlacesResult {
  status: "ok" | "no_results";
  source: "OpenStreetMap Overpass API";
  category: NearbyCategory;
  categoryLabel: string;
  center: { latitude: number; longitude: number };
  radiusMeters: number;
  resultCount: number;
  places: NearbyPlace[];
  dataUpdatedAt: string | null;
  attribution: string;
  license: string;
  note: string;
}

function requireObject(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new NearbyPlacesInputError("Dữ liệu tìm địa điểm phải là một JSON object.");
  }
  return value as Record<string, unknown>;
}

function coordinate(value: unknown, key: string, min: number, max: number): number {
  if (typeof value !== "number" || !Number.isFinite(value) || value < min || value > max) {
    throw new NearbyPlacesInputError(key + " phải là số từ " + min + " đến " + max + ".");
  }
  return Math.round(value * 100_000) / 100_000;
}

function boundedInteger(value: unknown, key: string, fallback: number, min: number, max: number): number {
  if (value === undefined || value === null) return fallback;
  if (typeof value !== "number" || !Number.isSafeInteger(value) || value < min || value > max) {
    throw new NearbyPlacesInputError(key + " phải là số nguyên từ " + min + " đến " + max + ".");
  }
  return value;
}

function cleanTag(value: unknown, max = 180): string | null {
  if (typeof value !== "string") return null;
  const clean = value.normalize("NFKC").replace(/[\u0000-\u001f\u007f]/g, " ").replace(/\s+/g, " ").trim();
  return clean ? clean.slice(0, max) : null;
}

function safeWebsite(value: unknown): string | null {
  const raw = cleanTag(value, 2048);
  if (!raw) return null;
  const url = isSafePublicUrl(raw);
  if (!url) return null;
  return url.toString();
}

function haversineMeters(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const rad = (degrees: number) => degrees * Math.PI / 180;
  const dLat = rad(lat2 - lat1);
  const dLon = rad(lon2 - lon1);
  const a = Math.sin(dLat / 2) ** 2 +
    Math.cos(rad(lat1)) * Math.cos(rad(lat2)) * Math.sin(dLon / 2) ** 2;
  return 6_371_000 * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function detailType(tags: Record<string, unknown>): string {
  const raw = cleanTag(tags.amenity) || cleanTag(tags.shop) || cleanTag(tags.leisure) ||
    cleanTag(tags.tourism) || cleanTag(tags.office) || "place";
  const labels: Record<string, string> = {
    restaurant: "Nhà hàng", cafe: "Quán cà phê", fast_food: "Đồ ăn nhanh", food_court: "Khu ẩm thực",
    supermarket: "Siêu thị", convenience: "Cửa hàng tiện lợi", mall: "Trung tâm thương mại",
    department_store: "Cửa hàng bách hóa", pharmacy: "Nhà thuốc", hospital: "Bệnh viện",
    clinic: "Phòng khám", doctors: "Bác sĩ", dentist: "Nha sĩ", atm: "ATM", bank: "Ngân hàng",
    fuel: "Trạm xăng", charging_station: "Trạm sạc xe điện", park: "Công viên",
    playground: "Sân chơi", garden: "Vườn", attraction: "Điểm tham quan", museum: "Bảo tàng",
    viewpoint: "Điểm ngắm cảnh", gallery: "Phòng trưng bày", hotel: "Khách sạn",
    hostel: "Nhà nghỉ / Hostel", guest_house: "Nhà khách",
  };
  return labels[raw] || raw.replace(/_/g, " ");
}

function resultCategory(
  tags: Record<string, unknown>,
  requested: NearbyCategory,
): NearbyCategory {
  if (requested !== "essentials") return requested;
  const amenity = cleanTag(tags.amenity);
  const shop = cleanTag(tags.shop);
  if (["restaurant", "cafe", "fast_food", "food_court"].includes(amenity || "")) return "food";
  if (["supermarket", "convenience", "mall", "department_store"].includes(shop || "")) return "shopping";
  if (amenity === "pharmacy") return "pharmacy";
  if (["hospital", "clinic", "doctors", "dentist"].includes(amenity || "")) return "medical";
  if (["atm", "bank"].includes(amenity || "")) return "atm";
  if (amenity === "fuel") return "fuel";
  if (amenity === "charging_station") return "charging";
  return "essentials";
}

function addressFromTags(tags: Record<string, unknown>): string | null {
  const street = [cleanTag(tags["addr:housenumber"], 32), cleanTag(tags["addr:street"], 100)]
    .filter(Boolean).join(" ");
  const parts = [
    street || null,
    cleanTag(tags["addr:suburb"], 80),
    cleanTag(tags["addr:city"], 80),
    cleanTag(tags["addr:state"], 80),
  ].filter((value): value is string => Boolean(value));
  return parts.length ? parts.join(", ") : null;
}

function buildQuery(category: NearbyCategory, latitude: number, longitude: number, radiusMeters: number): string {
  const definition = CATEGORIES[category];
  const filters = definition.filters.map(filter => {
    const values = filter.values.join("|");
    return `nwr["${filter.key}"~"^(${values})$"](around:${radiusMeters},${latitude.toFixed(5)},${longitude.toFixed(5)});`;
  });
  return [
    "[out:json][timeout:15][maxsize:10485760];",
    "(",
    ...filters,
    ");",
    "out center tags 100 qt;",
  ].join("\n");
}

function normalizeElement(
  raw: unknown,
  category: NearbyCategory,
  center: { latitude: number; longitude: number },
): NearbyPlace | null {
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) return null;
  const element = raw as OverpassElement;
  if (!["node", "way", "relation"].includes(String(element.type)) ||
      typeof element.id !== "number" || !Number.isSafeInteger(element.id) || element.id <= 0) return null;
  const tags = element.tags && typeof element.tags === "object" && !Array.isArray(element.tags)
    ? element.tags as Record<string, unknown> : {};
  const name = cleanTag(tags.name) || cleanTag(tags.brand) || cleanTag(tags.operator);
  if (!name) return null;
  const latitude = typeof element.lat === "number" ? element.lat : element.center?.lat;
  const longitude = typeof element.lon === "number" ? element.lon : element.center?.lon;
  if (typeof latitude !== "number" || !Number.isFinite(latitude) || latitude < -90 || latitude > 90 ||
      typeof longitude !== "number" || !Number.isFinite(longitude) || longitude < -180 || longitude > 180) return null;
  const type = String(element.type);
  const id = type + "/" + element.id;
  const latText = latitude.toFixed(5);
  const lonText = longitude.toFixed(5);
  const osmUrl = "https://www.openstreetmap.org/" + id;
  const itemCategory = resultCategory(tags, category);
  return {
    id,
    name,
    category: itemCategory,
    categoryLabel: CATEGORIES[itemCategory].label,
    detailType: detailType(tags),
    latitude,
    longitude,
    distanceMeters: Math.round(haversineMeters(center.latitude, center.longitude, latitude, longitude)),
    osmUrl,
    mapUrl: "https://www.openstreetmap.org/?mlat=" + latText + "&mlon=" + lonText + "#map=18/" + latText + "/" + lonText,
    address: addressFromTags(tags),
    openingHours: cleanTag(tags.opening_hours, 160),
    website: safeWebsite(tags.website) || safeWebsite(tags["contact:website"]),
  };
}


export interface CityPlaceChoice {
  name: string;
  admin1: string | null;
  country: string;
  country_code: string;
}

export type CityPlacesResult =
  | {
      status: "needs_clarification";
      query: string;
      source: "Open-Meteo geocoding";
      message: string;
      choices: CityPlaceChoice[];
    }
  | (NearbyPlacesResult & {
      requestedCity: string;
      resolvedPlace: CityPlaceChoice;
    });

/**
 * Search a user-named city or town, then query public OpenStreetMap records.
 * This does not inspect, infer or use the browser/device location.
 */
export async function searchPlacesInCity(rawArgs: unknown): Promise<CityPlacesResult> {
  const args = requireObject(rawArgs);
  if (typeof args.city !== "string") throw new NearbyPlacesInputError("city phải là tên thành phố hoặc thị trấn.");
  const city = args.city.normalize("NFKC").replace(/[\u0000-\u001f\u007f]/g, " ").replace(/\s+/g, " ").trim();
  if (city.length < 2 || city.length > 100) {
    throw new NearbyPlacesInputError("city phải có từ 2 đến 100 ký tự.");
  }

  let countryCode: string | undefined;
  if (args.country_code !== undefined && args.country_code !== null && args.country_code !== "") {
    if (typeof args.country_code !== "string" || !/^[A-Za-z]{2}$/.test(args.country_code)) {
      throw new NearbyPlacesInputError("country_code phải là mã quốc gia ISO gồm đúng hai chữ cái.");
    }
    countryCode = args.country_code.toUpperCase();
  }

  if (typeof args.category !== "string" || !Object.hasOwn(CATEGORIES, args.category)) {
    throw new NearbyPlacesInputError("category phải là một trong: " + NEARBY_CATEGORIES.join(", ") + ".");
  }
  const radiusMeters = boundedInteger(args.radius_m, "radius_m", 1500, 200, 5000);
  const limit = boundedInteger(args.limit, "limit", 12, 1, 25);

  const geocodingUrl = new URL("https://geocoding-api.open-meteo.com/v1/search");
  geocodingUrl.searchParams.set("name", city);
  geocodingUrl.searchParams.set("count", "5");
  geocodingUrl.searchParams.set("language", "en");
  geocodingUrl.searchParams.set("format", "json");
  if (countryCode) geocodingUrl.searchParams.set("countryCode", countryCode);

  let geocodingResponse: Response;
  try {
    geocodingResponse = await fetch(geocodingUrl, {
      method: "GET",
      headers: { accept: "application/json", "user-agent": USER_AGENT },
      redirect: "error",
      signal: AbortSignal.timeout(12_000),
    });
  } catch {
    throw new Error("Dịch vụ định vị tên thành phố không phản hồi hoặc đã hết thời gian chờ.");
  }
  if (!geocodingResponse.ok) {
    await geocodingResponse.body?.cancel().catch(() => undefined);
    if (geocodingResponse.status === 429) {
      throw new Error("Dịch vụ định vị thành phố đang giới hạn truy vấn. Hãy thử lại sau.");
    }
    throw new Error("Dịch vụ định vị thành phố trả về HTTP " + geocodingResponse.status + ".");
  }

  const geocodingData = await readJsonResponse<{ results?: unknown }>(geocodingResponse, 500_000);
  const rawResults = Array.isArray(geocodingData.results) ? geocodingData.results : [];
  const candidates = rawResults.flatMap((raw): Array<CityPlaceChoice & { latitude: number; longitude: number }> => {
    if (!raw || typeof raw !== "object" || Array.isArray(raw)) return [];
    const row = raw as Record<string, unknown>;
    if (typeof row.name !== "string" || typeof row.country !== "string" ||
        typeof row.country_code !== "string" || !/^[A-Za-z]{2}$/.test(row.country_code) ||
        typeof row.latitude !== "number" || !Number.isFinite(row.latitude) ||
        row.latitude < -90 || row.latitude > 90 ||
        typeof row.longitude !== "number" || !Number.isFinite(row.longitude) ||
        row.longitude < -180 || row.longitude > 180) return [];
    return [{
      name: row.name.slice(0, 100),
      admin1: typeof row.admin1 === "string" ? row.admin1.slice(0, 100) : null,
      country: row.country.slice(0, 100),
      country_code: row.country_code.toUpperCase(),
      latitude: row.latitude,
      longitude: row.longitude,
    }];
  });
  if (!candidates.length) throw new NearbyPlacesInputError("Không tìm thấy thành phố phù hợp. Hãy thử thêm tên quốc gia hoặc dùng tên địa danh cụ thể hơn.");

  const exact = candidates.filter(place => place.name.toLocaleLowerCase() === city.toLocaleLowerCase());
  const pool = exact.length ? exact : candidates;
  const unique = new Map<string, typeof pool[number]>();
  for (const place of pool) {
    const key = [place.country_code, place.admin1 || "", place.name.toLocaleLowerCase()].join("|");
    if (!unique.has(key)) unique.set(key, place);
  }
  if (unique.size > 1) {
    return {
      status: "needs_clarification",
      query: city,
      source: "Open-Meteo geocoding",
      message: "Có nhiều địa danh trùng hoặc gần trùng tên. Hãy hỏi người dùng chọn quốc gia/khu vực trước khi tra địa điểm; không được tự đoán.",
      choices: [...unique.values()].slice(0, 5).map(({ name, admin1, country, country_code }) => ({
        name, admin1, country, country_code,
      })),
    };
  }

  const place = pool[0]!;
  const result = await searchNearbyPlaces({
    latitude: place.latitude,
    longitude: place.longitude,
    category: args.category,
    radius_m: radiusMeters,
    limit,
  });
  return {
    ...result,
    requestedCity: city,
    resolvedPlace: {
      name: place.name,
      admin1: place.admin1,
      country: place.country,
      country_code: place.country_code,
    },
  };
}

export async function searchNearbyPlaces(rawArgs: unknown): Promise<NearbyPlacesResult> {
  const args = requireObject(rawArgs);
  const latitude = coordinate(args.latitude, "latitude", -90, 90);
  const longitude = coordinate(args.longitude, "longitude", -180, 180);
  if (typeof args.category !== "string" || !Object.hasOwn(CATEGORIES, args.category)) {
    throw new NearbyPlacesInputError("category phải là một trong: " + NEARBY_CATEGORIES.join(", ") + ".");
  }
  const category = args.category as NearbyCategory;
  const radiusMeters = boundedInteger(args.radius_m, "radius_m", 1500, 200, 5000);
  if (category === "essentials" && radiusMeters > 3000) {
    throw new NearbyPlacesInputError("Danh mục tiện ích thiết yếu giới hạn bán kính tối đa 3000 m để giảm tải nguồn dữ liệu công cộng.");
  }
  const limit = boundedInteger(args.limit, "limit", 12, 1, 25);
  const query = buildQuery(category, latitude, longitude, radiusMeters);

  let response: Response;
  try {
    response = await fetch(OVERPASS_ENDPOINT, {
      method: "POST",
      headers: {
        accept: "application/json",
        "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
        "user-agent": USER_AGENT,
      },
      body: new URLSearchParams({ data: query }).toString(),
      redirect: "error",
      signal: AbortSignal.timeout(18_000),
    });
  } catch {
    throw new Error("Dịch vụ OpenStreetMap Overpass không phản hồi hoặc đã hết thời gian chờ.");
  }

  if (!response.ok) {
    await response.body?.cancel().catch(() => undefined);
    if (response.status === 429) {
      throw new Error("OpenStreetMap Overpass đang giới hạn truy vấn. Hãy chờ một lúc rồi thử lại.");
    }
    if (response.status === 504 || response.status === 503) {
      throw new Error("OpenStreetMap Overpass đang bận. Hãy thử giảm bán kính hoặc thử lại sau.");
    }
    throw new Error("OpenStreetMap Overpass trả về HTTP " + response.status + ".");
  }

  const payload = await readJsonResponse<OverpassPayload>(response, MAX_RESPONSE_BYTES);
  if (typeof payload.remark === "string" && payload.remark.trim()) {
    throw new Error("OpenStreetMap Overpass không hoàn tất truy vấn: " + payload.remark.slice(0, 180));
  }
  const elements = Array.isArray(payload.elements) ? payload.elements : [];
  const seen = new Set<string>();
  const places = elements.flatMap(raw => {
    const place = normalizeElement(raw, category, { latitude, longitude });
    if (!place || seen.has(place.id)) return [];
    seen.add(place.id);
    return [place];
  }).sort((a, b) => a.distanceMeters - b.distanceMeters).slice(0, limit);

  return {
    status: places.length ? "ok" : "no_results",
    source: "OpenStreetMap Overpass API",
    category,
    categoryLabel: CATEGORIES[category].label,
    center: { latitude, longitude },
    radiusMeters,
    resultCount: places.length,
    places,
    dataUpdatedAt: cleanTag(payload.osm3s?.timestamp_osm_base, 40),
    attribution: "© OpenStreetMap contributors",
    license: "ODbL 1.0",
    note: "Dữ liệu do cộng đồng OpenStreetMap đóng góp và có thể thiếu hoặc chưa cập nhật. Khoảng cách là đường chim bay, không phải quãng đường đi thực tế. Giờ mở cửa chỉ là thông tin nguồn ghi nhận, không xác nhận địa điểm đang mở.",
  };
}
