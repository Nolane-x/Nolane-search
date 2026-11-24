import { afterEach, describe, expect, it, vi } from "vitest";
import { runLiveEverydayTool } from "../src/live-everyday-tools";

afterEach(() => { vi.useRealTimers(); vi.unstubAllGlobals(); });
function json(value: unknown, status = 200): Response {
  return new Response(JSON.stringify(value), { status, headers: { "content-type": "application/json" } });
}
const city = {
  name: "Hai Phong", admin1: "Hai Phong", country: "Vietnam", country_code: "VN",
  latitude: 20.85, longitude: 106.68, timezone: "Asia/Ho_Chi_Minh",
};

describe("Wave 49 learning and world discovery tools", () => {
  it("returns English definitions, examples, synonyms and only trusted pronunciation audio links", async () => {
    const mock = vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("api.dictionaryapi.dev");
      expect(url.pathname).toBe("/api/v2/entries/en/serendipity");
      return json([{
        word: "serendipity", phonetic: "/ˌser.ənˈdɪp.ə.ti/",
        phonetics: [
          { text: "/ˌser.ənˈdɪp.ə.ti/", audio: "//ssl.gstatic.com/dictionary/static/sounds/20200429/hello--_gb_1.mp3" },
          { text: "unsafe", audio: "https://attacker.example/audio.mp3" },
        ],
        origin: "Coined in the eighteenth century.",
        meanings: [{ partOfSpeech: "noun", definitions: [{
          definition: "The occurrence of events by chance in a happy or beneficial way.",
          example: "Finding the book was pure serendipity.",
          synonyms: ["chance", "fortune"], antonyms: ["design"],
        }] }],
      }]);
    });
    vi.stubGlobal("fetch", mock);
    const result = JSON.parse(await runLiveEverydayTool("define_english_word", { word: "Serendipity" }));
    expect(result.entries[0].phonetic).toContain("ser");
    expect(result.entries[0].meanings[0].definitions[0].synonyms).toContain("chance");
    expect(result.entries[0].pronunciations[0].audio_url).toContain("ssl.gstatic.com");
    expect(result.entries[0].pronunciations[1].audio_url).toBeNull();
  });

  it("returns a friendly not-found response for an unknown English word", async () => {
    const future = Date.now() + 1500;
    vi.useFakeTimers();
    vi.setSystemTime(future);
    vi.stubGlobal("fetch", vi.fn(async () => json({ title: "No Definitions Found" }, 404)));
    const result = JSON.parse(await runLiveEverydayTool("define_english_word", { word: "notarealwordxyz" }));
    expect(result.status).toBe("not_found");
  });

  it("searches only records Gutendex marks public domain in the United States", async () => {
    const mock = vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("gutendex.com");
      expect(url.searchParams.get("copyright")).toBe("false");
      expect(url.searchParams.get("languages")).toBe("en");
      expect(url.searchParams.get("topic")).toBe("adventure");
      return json({ count: 10, results: [
        { id: 11, title: "Alice's Adventures in Wonderland", authors: [{ name: "Lewis Carroll", birth_year: 1832, death_year: 1898 }],
          languages: ["en"], subjects: ["Fantasy"], bookshelves: ["Children's Fiction"], copyright: false, download_count: 25000,
          formats: { "text/html": "https://www.gutenberg.org/ebooks/11.html.images" } },
        { id: 12, title: "Copyrighted book", authors: [], languages: ["en"], subjects: [], bookshelves: [], copyright: true, download_count: 1, formats: {} },
      ] });
    });
    vi.stubGlobal("fetch", mock);
    const result = JSON.parse(await runLiveEverydayTool("search_public_domain_books", { query: "Alice Wonderland", topic: "adventure" }));
    expect(result.result_count).toBe(1);
    expect(result.books[0].catalog_url).toBe("https://www.gutenberg.org/ebooks/11");
    expect(result.note).toContain("Vietnam");
  });

  it("searches public-domain museum artworks and builds a fixed official IIIF image URL", async () => {
    const mock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("api.artic.edu");
      const params = JSON.parse(url.searchParams.get("params") || "{}");
      expect(params.query.term.is_public_domain).toBe(true);
      expect(params.q).toBe("Monet");
      expect(new Headers(init?.headers).get("AIC-User-Agent")).toContain("NolaneSearch");
      return json({ pagination: { total: 1 }, data: [
        { id: 129884, title: "Starry Night and the Astronauts", artist_title: "Alma Thomas",
          date_display: "1972", medium_display: "Acrylic", image_id: "aabbccdd-1122-3344-5566-778899001122",
          is_public_domain: true, web_url: "https://www.artic.edu/artworks/129884" },
        { id: 129885, title: "Protected image", artist_title: "Another artist", image_id: "bbccddaa-1122-3344-5566-778899001122",
          is_public_domain: false, web_url: "https://www.artic.edu/artworks/129885" },
      ] });
    });
    vi.stubGlobal("fetch", mock);
    const result = JSON.parse(await runLiveEverydayTool("search_museum_artworks", { query: "Monet" }));
    expect(result.result_count).toBe(1);
    expect(result.artworks[0].image_url).toBe("https://www.artic.edu/iiif/2/aabbccdd-1122-3344-5566-778899001122/full/843,/0/default.jpg");
    expect(result.artworks[0].is_public_domain).toBe(true);
  });

  it("filters NASA EONET events and extracts only GeoJSON point locations", async () => {
    const mock = vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("eonet.gsfc.nasa.gov");
      expect(url.pathname).toBe("/api/v3/events");
      expect(url.searchParams.get("category")).toBe("wildfires");
      expect(url.searchParams.get("days")).toBe("7");
      return json({ events: [{
        id: "EONET_123", title: "Test wildfire", description: "A curated event.",
        link: "https://eonet.gsfc.nasa.gov/api/v3/events/EONET_123", closed: null,
        categories: [{ id: "wildfires", title: "Wildfires" }],
        sources: [{ id: "EO", title: "Earth Observatory", source: "https://earthobservatory.nasa.gov/", link: "https://eonet.gsfc.nasa.gov/api/v3/sources/EO" }],
        geometry: [
          { date: "2026-11-24T00:00:00Z", type: "Point", coordinates: [106.7,20.8] },
          { date: "2026-11-24T01:00:00Z", type: "Polygon", coordinates: [] },
        ],
      }] });
    });
    vi.stubGlobal("fetch", mock);
    const result = JSON.parse(await runLiveEverydayTool("get_natural_events", { category: "wildfires", days_back: 7 }));
    expect(result.event_count).toBe(1);
    expect(result.events[0].recent_geometry[0].point.latitude).toBe(20.8);
    expect(result.events[0].sources[0].source_url).toBe("https://earthobservatory.nasa.gov/");
    expect(result.events[0].sources[0].api_url).toContain("eonet.gsfc.nasa.gov");
    expect(result.note).toContain("not an emergency alert");
  });

  it("gets current local date and time from the geocoded IANA time zone", async () => {
    const mock = vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("geocoding-api.open-meteo.com");
      return json({ results: [city] });
    });
    vi.stubGlobal("fetch", mock);
    const result = JSON.parse(await runLiveEverydayTool("get_local_time", { location: "Hai Phong", country_code: "VN" }));
    expect(result.time_zone).toBe("Asia/Ho_Chi_Minh");
    expect(result.local_date).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    expect(result.local_time).toMatch(/^\d{2}:\d{2}:\d{2}$/);
    expect(result.utc_offset).toContain("GMT+07:00");
    expect(mock).toHaveBeenCalledTimes(1);
  });

  it("rejects invalid word, language, category and event options before networking", async () => {
    const mock = vi.fn();
    vi.stubGlobal("fetch", mock);
    await expect(runLiveEverydayTool("define_english_word", { word: "two words" })).rejects.toThrow("one English word");
    await expect(runLiveEverydayTool("search_public_domain_books", { query: "classic", language: "english" })).rejects.toThrow("two-letter");
    await expect(runLiveEverydayTool("get_natural_events", { category: "bad category" })).rejects.toThrow("category");
    await expect(runLiveEverydayTool("get_natural_events", { status: "future" })).rejects.toThrow("status");
    expect(mock).not.toHaveBeenCalled();
  });
});
