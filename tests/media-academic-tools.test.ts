import { afterEach, describe, expect, it, vi } from "vitest";
import { runLiveEverydayTool } from "../src/live-everyday-tools";

afterEach(() => { vi.useRealTimers(); vi.unstubAllGlobals(); });

let providerClock = Date.parse("2035-01-01T00:00:00.000Z");
function startProviderClock(): void {
  providerClock += 5_000;
  vi.useFakeTimers();
  vi.setSystemTime(providerClock);
}

function json(value: unknown, status = 200): Response {
  return new Response(JSON.stringify(value), {
    status,
    headers: { "content-type": "application/json" },
  });
}

describe("Wave 50 media and academic discovery tools", () => {
  it("searches TVmaze shows and returns cleaned metadata with attribution", async () => {
    startProviderClock();
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("api.tvmaze.com");
      expect(url.pathname).toBe("/search/shows");
      expect(url.searchParams.get("q")).toBe("Example Show");
      return json([{
        score: 0.98,
        show: {
          id: 42,
          name: "Example Show",
          type: "Scripted",
          language: "English",
          genres: ["Drama", "Family"],
          status: "Ended",
          premiered: "2020-01-01",
          ended: "2023-01-01",
          averageRuntime: 45,
          rating: { average: 8.2 },
          network: { name: "Example Network", country: { name: "United States" } },
          webChannel: { name: "Example Streamer" },
          schedule: { time: "20:00", days: ["Monday"] },
          summary: "<p>A <b>family</b> story &amp; adventure.</p>",
          officialSite: "https://example.org/show",
          url: "https://www.tvmaze.com/shows/42/example-show",
        },
      }]);
    }));
    const result = JSON.parse(await runLiveEverydayTool("search_tv_shows", { query: "Example Show" }));
    expect(result.status).toBe("ok");
    expect(result.shows).toHaveLength(1);
    expect(result.shows[0].name).toBe("Example Show");
    expect(result.shows[0].summary).toBe("A family story & adventure.");
    expect(result.shows[0].rating_average).toBe(8.2);
    expect(result.shows[0].tvmaze_url).toBe("https://www.tvmaze.com/shows/42/example-show");
    expect(result.attribution).toContain("CC BY-SA");
    expect(result.note).toContain("not a streaming-availability checker");
  });

  it("retrieves a TVmaze episode list and includes specials only when requested", async () => {
    startProviderClock();
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("api.tvmaze.com");
      expect(url.pathname).toBe("/shows/42/episodes");
      expect(url.searchParams.get("specials")).toBe("1");
      return json([
        {
          id: 501, name: "Pilot", season: 1, number: 1, type: "regular",
          airdate: "2020-01-01", airtime: "20:00", runtime: 45,
          summary: "<p>The first episode.</p>", url: "https://www.tvmaze.com/episodes/501/pilot",
        },
        {
          id: 502, name: "Behind the Scenes", season: 0, number: null, type: "insignia",
          airdate: "2020-01-02", airtime: "", runtime: 20,
          summary: "A special feature.", url: "https://www.tvmaze.com/episodes/502/behind-the-scenes",
        },
      ]);
    }));
    const result = JSON.parse(await runLiveEverydayTool("get_tv_show_episodes", {
      tvmaze_show_id: 42, include_specials: true, limit: 10,
    }));
    expect(result.status).toBe("ok");
    expect(result.show_id).toBe(42);
    expect(result.episodes).toHaveLength(2);
    expect(result.episodes[0].name).toBe("Pilot");
    expect(result.episodes[1].season).toBe(0);
    expect(result.note).toContain("not a live streaming schedule");
  });

  it("searches Apple's selected storefront without returning artwork or audio-preview URLs", async () => {
    startProviderClock();
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("itunes.apple.com");
      expect(url.pathname).toBe("/search");
      expect(url.searchParams.get("term")).toBe("science podcast");
      expect(url.searchParams.get("media")).toBe("podcast");
      expect(url.searchParams.get("country")).toBe("vn");
      return json({
        resultCount: 1,
        results: [{
          trackName: "Science for Everyone",
          artistName: "Example Studio",
          collectionName: "Science for Everyone",
          kind: "podcast",
          primaryGenreName: "Science",
          releaseDate: "2026-01-01T00:00:00Z",
          trackCount: 42,
          trackTimeMillis: 1800000,
          trackViewUrl: "https://podcasts.apple.com/vn/podcast/example/id123",
          artworkUrl600: "https://is1-ssl.mzstatic.com/image.jpg",
          previewUrl: "https://audio.example.org/preview.m4a",
        }],
      });
    }));
    const result = JSON.parse(await runLiveEverydayTool("search_apple_media", { query: "science podcast" }));
    expect(result.status).toBe("ok");
    expect(result.storefront_country_code).toBe("VN");
    expect(result.results[0].title).toBe("Science for Everyone");
    expect(result.results[0].store_url).toContain("podcasts.apple.com");
    expect(JSON.stringify(result)).not.toContain("artworkUrl600");
    expect(JSON.stringify(result)).not.toContain("previewUrl");
    expect(JSON.stringify(result)).not.toContain("audio.example.org");
    expect(result.note).toContain("metadata and official store links only");
  });

  it("searches MusicBrainz metadata with a User-Agent and never returns recordings", async () => {
    startProviderClock();
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("musicbrainz.org");
      expect(url.pathname).toBe("/ws/2/artist/");
      expect(url.searchParams.get("fmt")).toBe("json");
      expect(url.searchParams.get("query")).toBe("artist:Example");
      expect(new Headers(init?.headers).get("user-agent")).toContain("NolaneSearch");
      return json({
        artists: [{
          id: "01234567-89ab-cdef-0123-456789abcdef",
          name: "Example Artist",
          disambiguation: "British singer",
          score: 100,
          country: "GB",
          area: { name: "London" },
          "life-span": { begin: "1960", end: null },
          tags: [{ name: "pop", count: 9 }],
        }],
      });
    }));
    const result = JSON.parse(await runLiveEverydayTool("search_music_metadata", {
      query: "artist:Example", entity_type: "artist",
    }));
    expect(result.status).toBe("ok");
    expect(result.records[0].name).toBe("Example Artist");
    expect(result.records[0].musicbrainz_url).toBe("https://musicbrainz.org/artist/01234567-89ab-cdef-0123-456789abcdef");
    expect(result.records[0].area).toBe("London");
    expect(result.note).toContain("does not provide music recordings");
    expect(result.note).toContain("Non-commercial use only");
  });

  it("searches Crossref bibliographic metadata and applies publication-year filters", async () => {
    startProviderClock();
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("api.crossref.org");
      expect(url.pathname).toBe("/works");
      expect(url.searchParams.get("query.bibliographic")).toBe("neural networks in education");
      expect(url.searchParams.get("rows")).toBe("5");
      expect(url.searchParams.get("filter")).toBe("from-pub-date:2022-01-01,until-pub-date:2026-12-31");
      expect(new Headers(init?.headers).get("user-agent")).toContain("NolaneSearch");
      return json({
        message: {
          items: [{
            DOI: "10.1234/example.2026",
            title: ["A Research Paper"],
            author: [{ given: "Ada", family: "Writer" }],
            issued: { "date-parts": [[2026, 3, 1]] },
            publisher: "Example Press",
            "container-title": ["Journal of Example Studies"],
            "references-count": 10,
            "is-referenced-by-count": 3,
            type: "journal-article",
            score: 50,
          }],
        },
      });
    }));
    const result = JSON.parse(await runLiveEverydayTool("search_scholarly_works", {
      query: "neural networks in education", year_from: 2022, year_to: 2026,
    }));
    expect(result.status).toBe("ok");
    expect(result.works[0].title).toBe("A Research Paper");
    expect(result.works[0].authors).toEqual(["Ada Writer"]);
    expect(result.works[0].doi_url).toBe("https://doi.org/10.1234/example.2026");
    expect(result.works[0].published_year).toBe(2026);
    expect(result.note).toContain("citation counts are not a measure of research quality");
    expect(result.note).toContain("does not retrieve article text");
  });

  it("rejects invalid media, MusicBrainz and scholarly search options before networking", async () => {
    startProviderClock();
    const mock = vi.fn();
    vi.stubGlobal("fetch", mock);
    await expect(runLiveEverydayTool("search_apple_media", {
      query: "anything", media_type: "free download",
    })).rejects.toThrow("media_type");
    await expect(runLiveEverydayTool("search_music_metadata", {
      query: "anything", entity_type: "album-track-file",
    })).rejects.toThrow("entity_type");
    await expect(runLiveEverydayTool("search_scholarly_works", {
      query: "anything", year_from: 2025, year_to: 2020,
    })).rejects.toThrow("year_from");
    await expect(runLiveEverydayTool("get_tv_show_episodes", {
      tvmaze_show_id: 0,
    })).rejects.toThrow("tvmaze_show_id");
    expect(mock).not.toHaveBeenCalled();
  });
});
