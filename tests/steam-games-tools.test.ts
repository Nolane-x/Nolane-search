import { afterEach, describe, expect, it, vi } from "vitest";
import { getSteamGameDetails, runSteamGamesTool, searchSteamGames } from "../src/steam-games-tools";
import { AGENT_TOOL_DEFINITIONS, executeAgentTool } from "../src/agent-tools";
import type { Env } from "../src/types";

afterEach(() => vi.unstubAllGlobals());

function json(value: unknown, status = 200): Response {
  return new Response(JSON.stringify(value), {
    status,
    headers: { "content-type": "application/json" },
  });
}

describe("Wave 60 Steam game discovery", () => {
  it("searches the Vietnam storefront with bounded results and retains official store links", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = new URL(String(input));
      expect(url.origin).toBe("https://store.steampowered.com");
      expect(url.pathname).toBe("/api/storesearch/");
      expect(url.searchParams.get("term")).toBe("Hades");
      expect(url.searchParams.get("cc")).toBe("vn");
      expect(url.searchParams.get("l")).toBe("vietnamese");
      expect(init?.redirect).toBe("error");
      expect(new Headers(init?.headers).get("user-agent")).toContain("NolaneSearch");
      return json({
        total: 2,
        items: [
          {
            id: 1145360,
            name: "Hades",
            type: "game",
            tiny_image: "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1145360/header.jpg",
            price: { currency: "VND", final_formatted: "165.000₫", discount_percent: 50 },
            metascore: "93",
          },
          {
            id: 999,
            name: "Unsafe image sample",
            type: "dlc",
            tiny_image: "https://evil.example/image.jpg",
            price: null,
          },
        ],
      });
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await searchSteamGames("Hades", 5, "VN", "vietnamese");
    const items = result.items as Array<Record<string, unknown>>;
    expect(result).toMatchObject({ status: "ok", source: "Steam Store", countryCode: "VN", language: "vietnamese" });
    expect(items).toHaveLength(2);
    expect(items[0]).toMatchObject({
      appId: 1145360,
      name: "Hades",
      type: "game",
      metascore: 93,
      storeUrl: "https://store.steampowered.com/app/1145360/",
    });
    expect(items[0]?.price).toMatchObject({ currency: "VND", final: "165.000₫", discountPercent: 50 });
    expect(items[0]?.image).toContain("steamstatic.com");
    expect(items[1]?.image).toBeNull();
    expect(items[1]?.storeUrl).toBe("https://store.steampowered.com/app/999/");
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("returns compact game details, local price, platforms and only trusted screenshot hosts", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      expect(url.origin).toBe("https://store.steampowered.com");
      expect(url.pathname).toBe("/api/appdetails");
      expect(url.searchParams.get("appids")).toBe("620");
      expect(url.searchParams.get("cc")).toBe("vn");
      return json({
        "620": {
          success: true,
          data: {
            type: "game",
            name: "Portal 2",
            short_description: "<b>Think with portals.</b> A puzzle game.",
            developers: ["Valve"],
            publishers: ["Valve"],
            genres: [{ id: "1", description: "Action" }, { id: "2", description: "Adventure" }],
            categories: [{ id: 2, description: "Single-player" }],
            release_date: { coming_soon: false, date: "Apr 19, 2011" },
            is_free: false,
            price_overview: { currency: "VND", initial: 120000, final: 24000, discount_percent: 80, initial_formatted: "120.000₫", final_formatted: "24.000₫" },
            platforms: { windows: true, mac: true, linux: true },
            metacritic: { score: 95, url: "https://www.metacritic.com/game/portal-2/" },
            recommendations: { total: 250000 },
            required_age: 0,
            supported_languages: "English, Vietnamese",
            header_image: "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/620/header.jpg",
            screenshots: [
              { id: 1, path_full: "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/620/1.jpg" },
              { id: 2, path_full: "https://evil.example/2.jpg" },
            ],
          },
        },
      });
    }));

    const result = await getSteamGameDetails(620, "vn", "vietnamese");
    expect(result).toMatchObject({
      status: "ok",
      appId: 620,
      name: "Portal 2",
      type: "game",
      shortDescription: "Think with portals. A puzzle game.",
      developers: ["Valve"],
      publishers: ["Valve"],
      genres: ["Action", "Adventure"],
      categories: ["Single-player"],
      releaseDate: "Apr 19, 2011",
      isFree: false,
      metacriticScore: 95,
      recommendations: 250000,
      platforms: { windows: true, mac: true, linux: true },
      storeUrl: "https://store.steampowered.com/app/620/",
      price: { currency: "VND", final: "24.000₫", discountPercent: 80, initial: "120.000₫" },
    });
    expect(result.screenshots).toHaveLength(1);
    expect(result.headerImage).toContain("steamstatic.com");
  });

  it("rejects malformed inputs before any network request", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    await expect(searchSteamGames("x")).rejects.toThrow("2–100");
    await expect(searchSteamGames("Hades", 11)).rejects.toThrow("limit");
    await expect(searchSteamGames("Hades", 5, "VNM")).rejects.toThrow("country_code");
    await expect(searchSteamGames("Hades", 5, "vn", "not-a-language")).rejects.toThrow("language");
    await expect(getSteamGameDetails(-1)).rejects.toThrow("app ID");
    await expect(getSteamGameDetails("620/..")).rejects.toThrow("app ID");
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("handles unavailable and rate-limited Steam responses without retry storms", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => json({ error: "rate limited" }, 429)));
    await expect(searchSteamGames("Portal")).rejects.toThrow("rate-limiting");
  });

  it("registers both Steam tools and dispatches them through the AI agent", async () => {
    const names = AGENT_TOOL_DEFINITIONS.map((item) => item.function.name);
    expect(names).toContain("search_steam_games");
    expect(names).toContain("get_steam_game_details");

    vi.stubGlobal("fetch", vi.fn(async () => json({ total: 1, items: [{ id: 620, name: "Portal 2", type: "game" }] })));
    const result = await executeAgentTool({ DB: {} as never, SEARCH_JOBS: {} as never } as Env, "search_steam_games", { query: "Portal 2" });
    expect(result).toContain('"appId":620');

    vi.stubGlobal("fetch", vi.fn(async () => json({ "620": { success: true, data: { type: "game", name: "Portal 2" } } })));
    const detail = await runSteamGamesTool("get_steam_game_details", { app_id: 620 });
    expect(detail).toContain('"name":"Portal 2"');
  });
});
