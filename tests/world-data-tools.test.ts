import { afterEach, describe, expect, it, vi } from "vitest";
import { runWorldDataTool } from "../src/world-data-tools";
import { executeAgentTool, AGENT_TOOL_DEFINITIONS } from "../src/agent-tools";
import type { Env } from "../src/types";

afterEach(() => vi.unstubAllGlobals());
const env = { DB: {} as never, SEARCH_JOBS: {} as never } as Env;
function json(value: unknown, status = 200): Response {
  return new Response(JSON.stringify(value), { status, headers: { "content-type": "application/json" } });
}

describe("Wave 51 country and biodiversity discovery tools", () => {
  it("searches World Bank country metadata and excludes aggregate regions", async () => {
    const mock = vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("api.worldbank.org");
      expect(url.pathname).toBe("/v2/country");
      expect(url.searchParams.get("per_page")).toBe("400");
      return json([{ page: 1, pages: 1, total: 2 }, [
        { id: "VNM", iso2Code: "VN", name: "Viet Nam", capitalCity: "Hanoi",
          region: { id: "EAS", value: "East Asia & Pacific" }, incomeLevel: { id: "LMC", value: "Lower middle income" },
          lendingType: { id: "IBD", value: "Blend" }, latitude: "21.0245", longitude: "105.8412" },
        { id: "WLD", iso2Code: "", name: "World", capitalCity: "",
          region: { id: "NA", value: "Aggregates" }, incomeLevel: { id: "NA", value: "Aggregates" },
          lendingType: { id: "NA", value: "Aggregates" }, latitude: "", longitude: "" },
      ]]);
    });
    vi.stubGlobal("fetch", mock);
    const result = JSON.parse(await runWorldDataTool("search_country_profiles", { query: "Vietnam" }));
    expect(result.result_count).toBe(1);
    expect(result.countries[0].iso3_code).toBe("VNM");
    expect(result.countries[0].region).toContain("East Asia");
  });

  it("gets multiple latest non-empty WDI indicators for multiple countries in one request", async () => {
    const mock = vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("api.worldbank.org");
      expect(url.pathname).toContain("/country/VNM;THA/indicator/");
      expect(url.searchParams.get("format")).toBe("json");
      expect(url.searchParams.get("source")).toBe("2");
      expect(url.searchParams.get("mrnev")).toBe("1");
      expect(url.pathname).toContain("SP.POP.TOTL");
      expect(url.pathname).toContain("NY.GDP.PCAP.CD");
      return json([{ page: 1, pages: 1, total: 4 }, [
        { country: { id: "VNM", value: "Viet Nam" }, countryiso3code: "VNM",
          indicator: { id: "SP.POP.TOTL", value: "Population, total" }, date: "2025", value: 101000000, unit: "", obs_status: "" },
        { country: { id: "THA", value: "Thailand" }, countryiso3code: "THA",
          indicator: { id: "SP.POP.TOTL", value: "Population, total" }, date: "2025", value: 71600000, unit: "", obs_status: "" },
        { country: { id: "VNM", value: "Viet Nam" }, countryiso3code: "VNM",
          indicator: { id: "NY.GDP.PCAP.CD", value: "GDP per capita" }, date: "2024", value: 4300, unit: "", obs_status: "" },
        { country: { id: "THA", value: "Thailand" }, countryiso3code: "THA",
          indicator: { id: "NY.GDP.PCAP.CD", value: "GDP per capita" }, date: "2024", value: 7200, unit: "", obs_status: "" },
      ]]);
    });
    vi.stubGlobal("fetch", mock);
    const result = JSON.parse(await runWorldDataTool("get_world_bank_indicators", {
      country_codes: ["VN", "THA"], indicators: ["population_total", "gdp_per_capita_usd"],
    }));
    expect(result.country_count).toBe(2);
    expect(result.countries[0].indicators.population_total.value).toBe(101000000);
    expect(result.countries[1].indicators.gdp_per_capita_usd.year).toBe("2024");
  });

  it("validates ISO codes and supported indicator keys before making a request", async () => {
    const mock = vi.fn();
    vi.stubGlobal("fetch", mock);
    await expect(runWorldDataTool("get_world_bank_indicators", { country_codes: ["Vietnam"] }))
      .rejects.toThrow("two- or three-letter ISO");
    await expect(runWorldDataTool("get_world_bank_indicators", { country_codes: ["VN"], indicators: ["unknown"] }))
      .rejects.toThrow("Unsupported indicator");
    expect(mock).not.toHaveBeenCalled();
  });

  it("matches a GBIF taxon and returns its accepted GBIF usage key", async () => {
    const mock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("api.gbif.org");
      expect(url.pathname).toBe("/v1/species/match");
      expect(url.searchParams.get("name")).toBe("Panthera tigris");
      expect(new Headers(init?.headers).get("user-agent")).toContain("Nolane-search");
      return json({ usageKey: 1, acceptedUsageKey: 2435099, scientificName: "Panthera tigris (Linnaeus, 1758)",
        canonicalName: "Panthera tigris", rank: "SPECIES", status: "ACCEPTED", matchType: "EXACT",
        confidence: 100, kingdom: "Animalia", phylum: "Chordata", class: "Mammalia", order: "Carnivora", family: "Felidae", genus: "Panthera" });
    });
    vi.stubGlobal("fetch", mock);
    const result = JSON.parse(await runWorldDataTool("search_gbif_species", { name: "Panthera tigris" }));
    expect(result.taxon_key).toBe(2435099);
    expect(result.confidence).toBe(100);
    expect(result.gbif_record_url).toBeUndefined();
    expect(result.source_url).toContain("/species/2435099");
  });

  it("returns a safe not-found response for a taxon match with no usage key", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => json({ matchType: "NONE", confidence: 0 })));
    const result = JSON.parse(await runWorldDataTool("search_gbif_species", { name: "not a real taxon" }));
    expect(result.status).toBe("not_found");
  });

  it("filters GBIF occurrences to reusable licenses and hides coordinates and precise locality", async () => {
    const mock = vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("api.gbif.org");
      expect(url.pathname).toBe("/v1/occurrence/search");
      expect(url.searchParams.get("taxonKey")).toBe("2435099");
      expect(url.searchParams.get("basisOfRecord")).toBe("HUMAN_OBSERVATION");
      expect(url.searchParams.get("country")).toBe("VN");
      expect(url.searchParams.get("year")).toBe("2020,2025");
      expect(url.searchParams.get("limit")).toBe("100");
      return json({ count: 900, results: [
        { key: 1001, scientificName: "Panthera tigris", vernacularName: "Tiger", eventDate: "2024-04-02",
          country: "Vietnam", countryCode: "VN", basisOfRecord: "HUMAN_OBSERVATION", license: "http://creativecommons.org/licenses/by/4.0/",
          datasetKey: "11111111-1111-4111-8111-111111111111", datasetName: "Example survey", recordedBy: "A. Observer",
          decimalLatitude: 12.34, decimalLongitude: 56.78, locality: "Protected site" },
        { key: 1002, scientificName: "Panthera tigris", eventDate: "2024-04-03", license: "http://creativecommons.org/licenses/by-nc/4.0/" },
        { key: 1003, scientificName: "Panthera tigris", eventDate: "2024-04-04", license: "UNSPECIFIED" },
        { key: 1004, scientificName: "Panthera tigris", eventDate: "2024-04-05", license: "http://creativecommons.org/publicdomain/zero/1.0/" },
      ] });
    });
    vi.stubGlobal("fetch", mock);
    const result = JSON.parse(await runWorldDataTool("search_gbif_observations", {
      taxon_key: 2435099, country_code: "VN", year_from: 2020, year_to: 2025, limit: 5,
    }));
    expect(result.status).toBe("ok");
    expect(result.records.map((row: { gbif_id: number }) => row.gbif_id)).toEqual([1001, 1004]);
    expect(result.records[0].recorded_by).toBe("A. Observer");
    expect(result.records[0].license).toBe("CC_BY_4_0");
    expect(result.records[0].decimalLatitude).toBeUndefined();
    expect(result.records[0].locality).toBeUndefined();
    expect(result.note).toContain("coordinates and locality descriptions are deliberately omitted");
    expect(result.note).toContain("CC BY");
  });

  it("rejects invalid occurrence filters and surfaces GBIF rate limiting", async () => {
    const mock = vi.fn(async () => json({}, 429));
    vi.stubGlobal("fetch", mock);
    await expect(runWorldDataTool("search_gbif_observations", { taxon_key: -1 })).rejects.toThrow("taxon_key");
    expect(mock).not.toHaveBeenCalled();
    await expect(runWorldDataTool("search_gbif_observations", { taxon_key: 42 })).rejects.toThrow("rate-limiting");
  });

  it("exposes and dispatches all Wave 51 tools through the model-callable interface", async () => {
    const names = AGENT_TOOL_DEFINITIONS.map(tool => tool.function.name);
    expect(names).toEqual(expect.arrayContaining([
      "search_country_profiles", "get_world_bank_indicators", "search_gbif_species", "search_gbif_observations",
    ]));
    const mock = vi.fn(async () => json([{ page: 1, pages: 1, total: 1 }, [
      { id: "VNM", iso2Code: "VN", name: "Viet Nam", capitalCity: "Hanoi",
        region: { id: "EAS", value: "East Asia & Pacific" }, incomeLevel: { id: "LMC", value: "Lower middle income" },
        lendingType: { id: "IBD", value: "Blend" }, latitude: "21.0245", longitude: "105.8412" },
    ]]));
    vi.stubGlobal("fetch", mock);
    const response = JSON.parse(await executeAgentTool(env, "search_country_profiles", { query: "VN" }));
    expect(response.countries[0].iso3_code).toBe("VNM");
  });
});
