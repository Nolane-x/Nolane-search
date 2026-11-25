import { readJsonResponse } from "./http";

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
};

const OVERPASS_ENDPOINT = "https://overpass-api.de/api/interpreter";
const USER_AGENT = "NolaneSearch/0.1 (+https://github.com/Nolane-x/Nolane-search)";
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
  return Math.round(value * 10_000) / 10_000;
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
  try {
    const url = new URL(raw);
    if (url.protocol !== "https:" || url.username || url.password || url.port || url.hash) return null;
    if (!url.hostname.includes(".") || url.hostname.endsWith(".local")) return null;
    return url.toString();
  } catch {
    return null;
  }
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
    return `nwr["${filter.key}"~"^(${values})$"](around:${radiusMeters},${latitude.toFixed(4)},${longitude.toFixed(4)});`;
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
  return {
    id,
    name,
    category,
    categoryLabel: CATEGORIES[category].label,
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

export async function searchNearbyPlaces(rawArgs: unknown): Promise<NearbyPlacesResult> {
  const args = requireObject(rawArgs);
  const latitude = coordinate(args.latitude, "latitude", -90, 90);
  const longitude = coordinate(args.longitude, "longitude", -180, 180);
  if (typeof args.category !== "string" || !Object.hasOwn(CATEGORIES, args.category)) {
    throw new NearbyPlacesInputError("category phải là một trong: " + NEARBY_CATEGORIES.join(", ") + ".");
  }
  const category = args.category as NearbyCategory;
  const radiusMeters = boundedInteger(args.radius_m, "radius_m", 1500, 200, 5000);
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
