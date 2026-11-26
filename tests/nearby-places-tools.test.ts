import { afterEach, describe, expect, it, vi } from "vitest";
import { NearbyPlacesInputError, searchNearbyPlaces, searchPlacesInCity } from "../src/nearby-places-tools";
import { executeAgentTool, AGENT_TOOL_DEFINITIONS } from "../src/agent-tools";
import type { Env } from "../src/types";

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

  it("only exposes public HTTPS business websites, never local or private targets", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify({
      elements: [
        { type: "node", id: 31, lat: 20.8450, lon: 106.6882, tags: { name: "Public site", amenity: "pharmacy", website: "https://example.com/info" } },
        { type: "node", id: 32, lat: 20.8451, lon: 106.6883, tags: { name: "Loopback", amenity: "pharmacy", website: "https://127.0.0.1/admin" } },
        { type: "node", id: 33, lat: 20.8452, lon: 106.6884, tags: { name: "Private IP", amenity: "pharmacy", website: "https://192.168.1.20" } },
        { type: "node", id: 34, lat: 20.8453, lon: 106.6885, tags: { name: "Credentials", amenity: "pharmacy", website: "https://user:secret@example.org" } },
        { type: "node", id: 35, lat: 20.8454, lon: 106.6886, tags: { name: "Custom port", amenity: "pharmacy", website: "https://example.org:8443" } },
      ],
    }), { status: 200, headers: { "content-type": "application/json" } })));
    const result = await searchNearbyPlaces(coordinates);
    expect(result.places.map((place) => place.website)).toEqual([
      "https://example.com/info", null, null, null, null,
    ]);
  });

  it("searches places from a city explicitly named by the user", async () => {
    const mock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = new URL(String(input));
      if (url.hostname === "geocoding-api.open-meteo.com") {
        expect(url.pathname).toBe("/v1/search");
        expect(url.searchParams.get("name")).toBe("Hai Phong");
        expect(url.searchParams.get("countryCode")).toBe("VN");
        expect(init?.redirect).toBe("error");
        return new Response(JSON.stringify({ results: [{
          name: "Hai Phong", admin1: "Hai Phong", country: "Vietnam", country_code: "VN",
          latitude: 20.8449, longitude: 106.6881,
        }] }), { status: 200, headers: { "content-type": "application/json" } });
      }
      expect(url.hostname).toBe("overpass-api.de");
      const body = new URLSearchParams(String(init?.body || ""));
      expect(body.get("data")).toContain("around:2500,20.84490,106.68810");
      return new Response(JSON.stringify({ elements: [
        { type: "node", id: 101, lat: 20.8450, lon: 106.6882, tags: { name: "Nhà thuốc trung tâm", amenity: "pharmacy" } }
      ] }), { status: 200, headers: { "content-type": "application/json" } });
    });
    vi.stubGlobal("fetch", mock);

    const result = await searchPlacesInCity({
      city: "Hai Phong", country_code: "vn", category: "pharmacy", radius_m: 2500,
    });
    expect(result.status).toBe("ok");
    if (result.status !== "ok") throw new Error("Expected city resolution");
    expect(result.requestedCity).toBe("Hai Phong");
    expect(result.resolvedPlace).toMatchObject({
      name: "Hai Phong", admin1: "Hai Phong", country: "Vietnam", country_code: "VN",
    });
    expect(result.places[0]).toMatchObject({ name: "Nhà thuốc trung tâm", category: "pharmacy" });
    expect(mock).toHaveBeenCalledTimes(2);
  });

  it("asks the user to disambiguate city names instead of guessing", async () => {
    const mock = vi.fn(async () => new Response(JSON.stringify({ results: [
      { name: "Springfield", admin1: "Illinois", country: "United States", country_code: "US", latitude: 39.78, longitude: -89.64 },
      { name: "Springfield", admin1: "Massachusetts", country: "United States", country_code: "US", latitude: 42.10, longitude: -72.59 },
      { name: "Springfield", admin1: "Queensland", country: "Australia", country_code: "AU", latitude: -27.65, longitude: 152.91 },
    ] }), { status: 200, headers: { "content-type": "application/json" } }));
    vi.stubGlobal("fetch", mock);
    const result = await searchPlacesInCity({ city: "Springfield", category: "food" });
    expect(result.status).toBe("needs_clarification");
    if (result.status !== "needs_clarification") throw new Error("Expected clarification");
    expect(result.choices).toHaveLength(3);
    expect(result.choices.map(choice => choice.country_code)).toEqual(["US", "US", "AU"]);
    expect(mock).toHaveBeenCalledTimes(1);
  });

  it("registers and dispatches city discovery as an ordinary-user AI tool", async () => {
    expect(AGENT_TOOL_DEFINITIONS.map(tool => tool.function.name)).toContain("search_places_in_city");
    const mock = vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      if (url.hostname === "geocoding-api.open-meteo.com") {
        return new Response(JSON.stringify({ results: [{
          name: "Hanoi", admin1: "Ha Noi", country: "Vietnam", country_code: "VN",
          latitude: 21.0278, longitude: 105.8342,
        }] }), { status: 200, headers: { "content-type": "application/json" } });
      }
      return new Response(JSON.stringify({ elements: [
        { type: "node", id: 7, lat: 21.0280, lon: 105.8343, tags: { name: "Công viên", leisure: "park" } }
      ] }), { status: 200, headers: { "content-type": "application/json" } });
    });
    vi.stubGlobal("fetch", mock);
    const env = { DB: {} as never, SEARCH_JOBS: {} as never } as Env;
    const result = JSON.parse(await executeAgentTool(env, "search_places_in_city", {
      city: "Hanoi", country_code: "VN", category: "parks",
    }));
    expect(result).toMatchObject({
      status: "ok",
      requestedCity: "Hanoi",
      resolvedPlace: { name: "Hanoi", country_code: "VN" },
      places: [{ name: "Công viên" }],
    });
  });

  it("rejects invalid city options before calling external services", async () => {
    const mock = vi.fn();
    vi.stubGlobal("fetch", mock);
    await expect(searchPlacesInCity({ city: "H", category: "food" })).rejects.toBeInstanceOf(NearbyPlacesInputError);
    await expect(searchPlacesInCity({ city: "Hanoi", category: "food", country_code: "VNM" })).rejects.toThrow("two letters");
    await expect(searchPlacesInCity({ city: "Hanoi", category: "unknown" })).rejects.toThrow("category");
    await expect(searchPlacesInCity({ city: "Hanoi", category: "essentials", radius_m: 4000 })).rejects.toThrow("3000 m");
    expect(mock).not.toHaveBeenCalled();
  });

  it("rejects malformed coordinates, categories and out-of-policy limits before fetch", async () => {
    const mock = vi.fn();
    vi.stubGlobal("fetch", mock);
    await expect(searchNearbyPlaces({ ...coordinates, latitude: 91 })).rejects.toBeInstanceOf(NearbyPlacesInputError);
    await expect(searchNearbyPlaces({ ...coordinates, longitude: "106.6" })).rejects.toBeInstanceOf(NearbyPlacesInputError);
    await expect(searchNearbyPlaces({ ...coordinates, category: "all" })).rejects.toThrow("category");
    await expect(searchNearbyPlaces({ ...coordinates, radius_m: 5001 })).rejects.toThrow("radius_m");
    await expect(searchNearbyPlaces({ ...coordinates, limit: 26 })).rejects.toThrow("limit");
    await expect(searchNearbyPlaces({ ...coordinates, category: "essentials", radius_m: 5000 })).rejects.toThrow("3000 m");
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
