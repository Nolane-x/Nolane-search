import { afterEach, describe, expect, it, vi } from "vitest";
import { NearbyPlacesInputError, searchNearbyPlaces } from "../src/nearby-places-tools";

afterEach(() => vi.unstubAllGlobals());

const coordinates = {
  latitude: 20.8449,
  longitude: 106.6881,
  category: "pharmacy",
  radius_m: 1500,
};

describe("Nearby Places · OpenStreetMap", () => {
  it("uses a fixed Overpass endpoint, static category filters and bounded radius", async () => {
    const mock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      expect(new URL(String(input)).toString()).toBe("https://overpass-api.de/api/interpreter");
      expect(init?.method).toBe("POST");
      const body = new URLSearchParams(String(init?.body || ""));
      const query = body.get("data") || "";
      expect(query).toContain('[out:json][timeout:15][maxsize:10485760]');
      expect(query).toContain('nwr["amenity"~"^(pharmacy)$"](around:1500,20.84490,106.68810);');
      expect(query).toContain("out center tags 100 qt;");
      expect(query).not.toContain("https://");
      return new Response(JSON.stringify({ elements: [] }), {
        status: 200,
        headers: { "content-type": "application/json" },
      });
    });
    vi.stubGlobal("fetch", mock);

    const result = await searchNearbyPlaces(coordinates);
    expect(result.status).toBe("no_results");
    expect(result.source).toBe("OpenStreetMap Overpass API");
    expect(result.resultCount).toBe(0);
    expect(result.radiusMeters).toBe(1500);
    expect(result.license).toBe("ODbL 1.0");
    expect(mock).toHaveBeenCalledTimes(1);
  });

  it("normalizes named elements, includes way centers, filters unnamed records and sorts by straight-line distance", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify({
      elements: [
        { type: "way", id: 2, center: { lat: 20.8460, lon: 106.6890 }, tags: {
          name: "Nhà thuốc xa", amenity: "pharmacy", website: "http://unsafe.example",
          opening_hours: "Mo-Fr 08:00-20:00", "addr:street": "Đường B", "addr:city": "Hải Phòng",
        } },
        { type: "node", id: 3, lat: 20.8449, lon: 106.6881, tags: { amenity: "pharmacy" } },
        { type: "node", id: 1, lat: 20.8450, lon: 106.6882, tags: {
          name: "Nhà thuốc gần", amenity: "pharmacy", website: "https://pharmacy.example",
        "contact:website": "https://192.168.1.10/admin",
        } },
      ],
      osm3s: { timestamp_osm_base: "2026-11-25T12:00:00Z" },
    }), { status: 200, headers: { "content-type": "application/json" } })));

    const result = await searchNearbyPlaces(coordinates);
    expect(result.status).toBe("ok");
    expect(result.resultCount).toBe(2);
    expect(result.places[0]).toMatchObject({
      id: "node/1", name: "Nhà thuốc gần", category: "pharmacy",
      categoryLabel: "Nhà thuốc", website: "https://pharmacy.example/",
    });
    expect(result.places[0].distanceMeters).toBeLessThan(result.places[1].distanceMeters);
    expect(result.places[0].osmUrl).toBe("https://www.openstreetmap.org/node/1");
    expect(result.places[0].mapUrl).toContain("mlat=20.84500");
    expect(result.places[1]).toMatchObject({
      id: "way/2", name: "Nhà thuốc xa", website: null,
      address: "Đường B, Hải Phòng", openingHours: "Mo-Fr 08:00-20:00",
    });
    expect(result.dataUpdatedAt).toBe("2026-11-25T12:00:00Z");
    expect(result.note).toContain("đường chim bay");
    expect(result.note).toContain("không xác nhận địa điểm đang mở");
  });

  it("searches multiple essential categories in one bounded Overpass query and labels each result", async () => {
    const mock = vi.fn(async (_input: RequestInfo | URL, init?: RequestInit) => {
      const query = new URLSearchParams(String(init?.body || "")).get("data") || "";
      expect(query).toContain('nwr["amenity"~"^(restaurant|cafe|fast_food|pharmacy|hospital|clinic|doctors|dentist|atm|bank|fuel|charging_station)$"]');
      expect(query).toContain('nwr["shop"~"^(supermarket|convenience)$"]');
      return new Response(JSON.stringify({ elements: [
        { type: "node", id: 21, lat: 20.8450, lon: 106.6882, tags: { name: "Cà phê", amenity: "cafe" } },
        { type: "node", id: 22, lat: 20.8451, lon: 106.6883, tags: { name: "Siêu thị", shop: "supermarket" } },
        { type: "node", id: 23, lat: 20.8452, lon: 106.6884, tags: { name: "Nhà thuốc", amenity: "pharmacy" } },
        { type: "node", id: 24, lat: 20.8453, lon: 106.6885, tags: { name: "ATM", amenity: "atm" } },
        { type: "node", id: 25, lat: 20.8454, lon: 106.6886, tags: { name: "Trạm sạc", amenity: "charging_station" } },
      ] }), { status: 200, headers: { "content-type": "application/json" } });
    });
    vi.stubGlobal("fetch", mock);
    const result = await searchNearbyPlaces({ ...coordinates, category: "essentials" });
    expect(mock).toHaveBeenCalledTimes(1);
    expect(result.category).toBe("essentials");
    expect(result.categoryLabel).toBe("Tiện ích thiết yếu");
    expect(result.places.map((place: { category: string }) => place.category)).toEqual([
      "food", "shopping", "pharmacy", "atm", "charging",
    ]);
    expect(result.places.map((place: { categoryLabel: string }) => place.categoryLabel)).toEqual([
      "Ăn uống", "Mua sắm", "Nhà thuốc", "ATM / Ngân hàng", "Trạm sạc",
    ]);
  });

  it("rejects malformed coordinates, categories and out-of-policy limits before fetch", async () => {
    const mock = vi.fn();
    vi.stubGlobal("fetch", mock);
    await expect(searchNearbyPlaces({ ...coordinates, latitude: 91 })).rejects.toBeInstanceOf(NearbyPlacesInputError);
    await expect(searchNearbyPlaces({ ...coordinates, longitude: "106.6" })).rejects.toBeInstanceOf(NearbyPlacesInputError);
    await expect(searchNearbyPlaces({ ...coordinates, category: "all" })).rejects.toThrow("category");
    await expect(searchNearbyPlaces({ ...coordinates, radius_m: 5001 })).rejects.toThrow("radius_m");
    await expect(searchNearbyPlaces({ ...coordinates, limit: 26 })).rejects.toThrow("limit");
    expect(mock).not.toHaveBeenCalled();
  });

  it("rejects non-object payloads", async () => {
    await expect(searchNearbyPlaces(null)).rejects.toThrow("JSON object");
    await expect(searchNearbyPlaces([])).rejects.toThrow("JSON object");
  });

  it("turns Overpass rate limits and service timeouts into safe user-facing errors", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => new Response("busy", { status: 429 })));
    await expect(searchNearbyPlaces(coordinates)).rejects.toThrow("đang giới hạn truy vấn");

    vi.stubGlobal("fetch", vi.fn(async () => new Response("gateway timeout", { status: 504 })));
    await expect(searchNearbyPlaces(coordinates)).rejects.toThrow("đang bận");
  });

  it("does not present partial results when Overpass returns a remark", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify({
      remark: "runtime error: query timed out",
      elements: [{ type: "node", id: 1, lat: 20.845, lon: 106.688, tags: { name: "Maybe", amenity: "pharmacy" } }],
    }), { status: 200, headers: { "content-type": "application/json" } })));
    await expect(searchNearbyPlaces(coordinates)).rejects.toThrow("không hoàn tất truy vấn");
  });
});
