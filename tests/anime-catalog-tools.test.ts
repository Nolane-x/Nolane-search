import { afterEach, describe, expect, it, vi } from "vitest";
import { runAnimeCatalogTool } from "../src/anime-catalog-tools";
import { executeAgentTool, AGENT_TOOL_DEFINITIONS } from "../src/agent-tools";
import type { Env } from "../src/types";

afterEach(() => vi.unstubAllGlobals());
const env = { DB: {} as never, SEARCH_JOBS: {} as never } as Env;
function json(value: unknown, status = 200): Response {
  return new Response(JSON.stringify(value), { status, headers: { "content-type": "application/json" } });
}

describe("Wave 57 anime and manga discovery", () => {
  it("searches SFW anime titles and normalizes ranking, studio and cover data", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("api.jikan.moe");
      expect(url.pathname).toBe("/v4/anime");
      expect(url.searchParams.get("q")).toBe("Fullmetal Alchemist");
      expect(url.searchParams.get("limit")).toBe("4");
      expect(url.searchParams.get("sfw")).toBe("true");
      expect(url.searchParams.get("type")).toBe("TV");
      expect(new Headers(init?.headers).get("user-agent")).toContain("NolaneSearch");
      return json({ data: [
        { mal_id: 5114, url: "https://myanimelist.net/anime/5114/Fullmetal_Alchemist__Brotherhood",
          title: "Fullmetal Alchemist: Brotherhood", title_english: "Fullmetal Alchemist: Brotherhood",
          type: "TV", episodes: 64, status: "Finished Airing", score: 9.1, scored_by: 2200000,
          synopsis: "Two brothers search for the Philosopher's Stone.",
          images: { jpg: { large_image_url: "https://cdn.myanimelist.net/images/anime/1208/94745l.jpg" } },
          studios: [{ mal_id: 4, name: "Bones", url: "https://myanimelist.net/anime/producer/4/Bones" }],
          genres: [{ mal_id: 1, name: "Action" }, { mal_id: 2, name: "Adventure" }]
        },
        { mal_id: "bad", title: "Malformed Entry" }
      ] });
    }));
    const result = JSON.parse(await runAnimeCatalogTool("search_anime_titles", { query: "Fullmetal Alchemist", limit: 4, type: "TV" }));
    expect(result.result_count).toBe(1);
    expect(result.results[0]).toMatchObject({
      mal_id: 5114, title: "Fullmetal Alchemist: Brotherhood", score: 9.1,
      episodes: 64, studios: ["Bones"], genres: ["Action","Adventure"]
    });
    expect(result.results[0].image_url).toContain("cdn.myanimelist.net");
  });

  it("retrieves full anime details with canonical links and bounded titles", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      expect(url.pathname).toBe("/v4/anime/5114/full");
      return json({ data: {
        mal_id: 5114, title: "Fullmetal Alchemist: Brotherhood",
        url: "https://myanimelist.net/anime/5114/Fullmetal_Alchemist__Brotherhood",
        synopsis: "Two brothers search for the Philosopher's Stone.",
        background: "A popular adaptation.",
        type: "TV", episodes: 64, score: 9.1, airing: false,
        aired: { from: "2009-04-05T00:00:00+00:00", to: "2010-07-04T00:00:00+00:00" },
        studios: [{ name: "Bones" }], producers: [{ name: "Aniplex" }],
        broadcast: { string: "Sundays at 17:00 (JST)" },
        titles: [{ type: "Default", title: "Fullmetal Alchemist: Brotherhood" }, { type: "Japanese", title: "鋼の錬金術師 FULLMETAL ALCHEMIST" }],
        themes: [{ name: "Military" }], demographics: [{ name: "Shounen" }]
      } });
    }));
    const result = JSON.parse(await runAnimeCatalogTool("get_anime_details", { anime_id: "5114" }));
    expect(result.item).toMatchObject({
      mal_id: 5114, episodes: 64, studios: ["Bones"], producers: ["Aniplex"],
      themes: ["Military"], demographics: ["Shounen"]
    });
    expect(result.item.broadcast).toBe("Sundays at 17:00 (JST)");
    expect(result.item.titles).toHaveLength(2);
  });

  it("searches manga SFW and returns chapters, volumes and authors", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      expect(url.pathname).toBe("/v4/manga");
      expect(url.searchParams.get("q")).toBe("One Piece");
      expect(url.searchParams.get("sfw")).toBe("true");
      expect(url.searchParams.get("type")).toBe("manga");
      return json({ data: [{
        mal_id: 13, title: "One Piece", title_english: "One Piece",
        url: "https://myanimelist.net/manga/13/One_Piece",
        type: "Manga", chapters: 1100, volumes: 110,
        score: 9.2, scored_by: 250000,
        synopsis: "A young pirate searches for the legendary treasure.",
        images: { jpg: { image_url: "https://cdn.myanimelist.net/images/manga/2/253146.jpg" } },
        authors: [{ name: "Oda, Eiichiro" }],
        genres: [{ name: "Adventure" }, { name: "Fantasy" }],
        serializations: [{ name: "Weekly Shounen Jump" }]
      }] });
    }));
    const result = JSON.parse(await runAnimeCatalogTool("search_manga_titles", { query: "One Piece", type: "manga" }));
    expect(result.results[0]).toMatchObject({
      mal_id: 13, chapters: 1100, volumes: 110, authors: ["Oda, Eiichiro"],
      serializations: ["Weekly Shounen Jump"]
    });
    expect(result.results[0].myanimelist_url).toContain("/manga/13/");
  });

  it("retrieves manga details and preserves publication dates and demographic labels", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      expect(url.pathname).toBe("/v4/manga/13/full");
      return json({ data: {
        mal_id: 13, title: "One Piece", url: "https://myanimelist.net/manga/13/One_Piece",
        type: "Manga", chapters: 1100, volumes: 110, publishing: true,
        published: { from: "1997-07-22T00:00:00+00:00", to: null },
        authors: [{ name: "Oda, Eiichiro" }],
        genres: [{ name: "Adventure" }], demographics: [{ name: "Shounen" }],
        titles: [{ type: "Default", title: "One Piece" }]
      } });
    }));
    const result = JSON.parse(await runAnimeCatalogTool("get_manga_details", { manga_id: 13 }));
    expect(result.item).toMatchObject({
      mal_id: 13, chapters: 1100, volumes: 110, publishing: true,
      authors: ["Oda, Eiichiro"], demographics: ["Shounen"],
      published: { from: "1997-07-22T00:00:00+00:00", to: null }
    });
  });

  it("rejects invalid queries, types and MyAnimeList IDs before making requests", async () => {
    const mock = vi.fn();
    vi.stubGlobal("fetch", mock);
    await expect(runAnimeCatalogTool("search_anime_titles", { query: "x" })).rejects.toThrow("2 to 120");
    await expect(runAnimeCatalogTool("search_anime_titles", { query: "Test", type: "HENTAI" })).rejects.toThrow("type must be one of");
    await expect(runAnimeCatalogTool("get_anime_details", { anime_id: "../1" })).rejects.toThrow("positive numeric");
    await expect(runAnimeCatalogTool("get_manga_details", { manga_id: 0 })).rejects.toThrow("positive numeric");
    expect(mock).not.toHaveBeenCalled();
  });

  it("uses an explicit SFW filter and reports upstream rate limiting without retrying", async () => {
    const mock = vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      expect(url.searchParams.get("sfw")).toBe("true");
      return json({ message: "Too many requests" }, 429);
    });
    vi.stubGlobal("fetch", mock);
    await expect(runAnimeCatalogTool("search_anime_titles", { query: "Popular anime" })).rejects.toThrow("rate-limiting");
    expect(mock).toHaveBeenCalledTimes(1);
  });

  it("returns a not-found result when a valid item ID has no SFW record", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => json({ data: { mal_id: "bad", title: "" } })));
    const result = JSON.parse(await runAnimeCatalogTool("get_anime_details", { anime_id: 999999 }));
    expect(result.status).toBe("not_found");
  });

  it("registers and dispatches all four anime and manga tools through the AI interface", async () => {
    const names = AGENT_TOOL_DEFINITIONS.map(tool => tool.function.name);
    expect(names).toEqual(expect.arrayContaining([
      "search_anime_titles","get_anime_details","search_manga_titles","get_manga_details"
    ]));
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      expect(url.pathname).toBe("/v4/anime");
      return json({ data: [{ mal_id: 5114, title: "Fullmetal Alchemist" }] });
    }));
    const result = JSON.parse(await executeAgentTool(env, "search_anime_titles", { query: "Fullmetal Alchemist" }));
    expect(result.results[0].mal_id).toBe(5114);
  });
});
