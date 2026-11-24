import { afterEach, describe, expect, it, vi } from "vitest";
import { runLiveEverydayTool } from "../src/live-everyday-tools";

afterEach(() => vi.unstubAllGlobals());
const city = {
  name: "Da Nang", admin1: "Da Nang", country: "Vietnam", country_code: "VN",
  latitude: 16.0544, longitude: 108.2022, timezone: "Asia/Ho_Chi_Minh",
};
function json(value: unknown, status = 200): Response {
  return new Response(JSON.stringify(value), { status, headers: { "content-type": "application/json" } });
}

describe("Wave 48 live everyday discovery tools", () => {
  it("returns marine wave and swell forecasts with distance to the model sea grid", async () => {
    const mock = vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      if (url.hostname === "geocoding-api.open-meteo.com") return json({ results: [city] });
      expect(url.hostname).toBe("marine-api.open-meteo.com");
      expect(url.searchParams.get("cell_selection")).toBe("sea");
      expect(url.searchParams.get("forecast_days")).toBe("2");
      return json({
        latitude: 16.05, longitude: 108.20, timezone: "Asia/Ho_Chi_Minh",
        current: { time: "2026-11-24T12:00", wave_height: 0.8, wave_direction: 90, wave_period: 5, swell_wave_height: 0.3, swell_wave_direction: 110, swell_wave_period: 7, sea_surface_temperature: 28, ocean_current_velocity: 0.4, ocean_current_direction: 130 },
        current_units: { wave_height: "m", wave_period: "s" },
        daily: { time: ["2026-11-24","2026-11-25"], wave_height_max: [1.2,1.4], wave_direction_dominant: [90,100], wave_period_max: [6,7], swell_wave_height_max: [0.5,0.6], swell_wave_direction_dominant: [110,120], swell_wave_period_max: [8,9] },
      });
    });
    vi.stubGlobal("fetch", mock);
    const result = JSON.parse(await runLiveEverydayTool("get_marine_forecast", { location: "Da Nang", country_code: "VN", forecast_days: 2 }));
    expect(result.current.wave_height_m).toBe(0.8);
    expect(result.daily_forecast).toHaveLength(2);
    expect(result.marine_model_grid.distance_from_requested_location_km).toBeLessThan(1);
    expect(result.note).toContain("navigation");
    expect(mock).toHaveBeenCalledTimes(2);
  });

  it("queries USGS earthquake events around a city and keeps trusted detail links only", async () => {
    const timestamp = Date.parse("2026-11-24T02:00:00Z");
    const mock = vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      if (url.hostname === "geocoding-api.open-meteo.com") return json({ results: [city] });
      expect(url.hostname).toBe("earthquake.usgs.gov");
      expect(url.searchParams.get("format")).toBe("geojson");
      expect(url.searchParams.get("maxradiuskm")).toBe("250");
      return json({
        metadata: { count: 1 },
        features: [{
          id: "us700-test",
          properties: { mag: 4.2, magType: "mb", place: "20 km offshore", time: timestamp, url: "https://earthquake.usgs.gov/earthquakes/eventpage/us700-test", tsunami: 0 },
          geometry: { coordinates: [108.1,16.1,10.5] },
        }],
      });
    });
    vi.stubGlobal("fetch", mock);
    const result = JSON.parse(await runLiveEverydayTool("get_earthquake_activity", { location: "Da Nang", country_code: "VN" }));
    expect(result.event_count).toBe(1);
    expect(result.events[0].magnitude).toBe(4.2);
    expect(result.events[0].time_utc).toBe(new Date(timestamp).toISOString());
    expect(result.events[0].detail_url).toContain("earthquake.usgs.gov");
    expect(result.note).toContain("early-warning");
    expect(mock).toHaveBeenCalledTimes(2);
  });

  it("searches Open Library with an identified User-Agent and bounded result fields", async () => {
    const mock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("openlibrary.org");
      expect(url.pathname).toBe("/search.json");
      expect(url.searchParams.get("q")).toBe("The Little Prince");
      expect(new Headers(init?.headers).get("user-agent")).toContain("NolaneSearch");
      return json({ numFound: 12, docs: [{
        key: "/works/OL123W", title: "The Little Prince", author_name: ["Antoine de Saint-Exupery"],
        first_publish_year: 1943, edition_count: 80, isbn: ["1234567890"], subject: ["Fiction","Children"],
      }] });
    });
    vi.stubGlobal("fetch", mock);
    const result = JSON.parse(await runLiveEverydayTool("search_books", { query: "The Little Prince" }));
    expect(result.total_matching_records).toBe(12);
    expect(result.books[0]).toMatchObject({ title: "The Little Prince", first_publication_year: 1943, edition_count: 80 });
    expect(result.books[0].open_library_url).toBe("https://openlibrary.org/works/OL123W");
  });

  it("looks up postcodes and preserves multi-place mapping", async () => {
    const mock = vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("api.zippopotam.us");
      expect(url.pathname).toBe("/us/90210");
      return json({
        "post code": "90210", country: "United States", "country abbreviation": "US",
        places: [
          { "place name": "Beverly Hills", state: "California", "state abbreviation": "CA", latitude: "34.0901", longitude: "-118.4065" },
          { "place name": "Other place", state: "California", "state abbreviation": "CA", latitude: "34.1", longitude: "-118.5" },
        ],
      });
    });
    vi.stubGlobal("fetch", mock);
    const result = JSON.parse(await runLiveEverydayTool("lookup_postal_code", { country_code: "US", postal_code: "90210" }));
    expect(result.places).toHaveLength(2);
    expect(result.places[0]).toMatchObject({ place_name: "Beverly Hills", latitude: 34.0901 });
  });

  it("returns a friendly not-found result for unknown or unsupported postal codes", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => json({ error: "not found" }, 404)));
    const result = JSON.parse(await runLiveEverydayTool("lookup_postal_code", { country_code: "VN", postal_code: "00000" }));
    expect(result.status).toBe("not_found");
  });

  it("validates bounds before issuing provider requests", async () => {
    await expect(runLiveEverydayTool("lookup_postal_code", { country_code: "USA", postal_code: "123" })).rejects.toThrow("two-letter");
    await expect(runLiveEverydayTool("get_earthquake_activity", { location: "Da Nang", days_back: 31 })).rejects.toThrow("days_back");
  });
});
