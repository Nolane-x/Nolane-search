import { afterEach, describe, expect, it, vi } from "vitest";
import { runConsumerDiscoveryTool } from "../src/consumer-discovery-tools";
import { executeAgentTool, AGENT_TOOL_DEFINITIONS } from "../src/agent-tools";
import type { Env } from "../src/types";

afterEach(() => vi.unstubAllGlobals());
const env = { DB: {} as never, SEARCH_JOBS: {} as never } as Env;
function json(value: unknown, status = 200): Response {
  return new Response(JSON.stringify(value), { status, headers: { "content-type": "application/json" } });
}

describe("Wave 53 consumer discovery", () => {
  it("searches recipes by name and returns bounded user-facing cards", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("www.themealdb.com");
      expect(url.pathname).toBe("/api/json/v1/1/search.php");
      expect(url.searchParams.get("s")).toBe("chicken");
      expect(new Headers(init?.headers).get("user-agent")).toContain("NolaneSearch");
      return json({ meals: [{
        idMeal: "52772", strMeal: "Teriyaki Chicken Casserole", strCategory: "Chicken",
        strArea: "Japanese", strMealThumb: "https://www.themealdb.com/images/media/meals/wvpsxx1468256321.jpg",
        strSource: "https://www.example.org/recipe", strTags: "Dinner,Chicken",
      }, { idMeal: "bad/id", strMeal: "Unsafe" }] });
    }));
    const result = JSON.parse(await runConsumerDiscoveryTool("search_meal_recipes", { query: "chicken", limit: 4 }));
    expect(result.result_count).toBe(1);
    expect(result.meals[0]).toMatchObject({ meal_id: "52772", name: "Teriyaki Chicken Casserole", cuisine_area: "Japanese" });
    expect(result.meals[0].thumbnail_url).toContain("themealdb.com");
  });

  it("returns ingredients and cooking instructions for a verified recipe ID", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      expect(url.pathname).toBe("/api/json/v1/1/lookup.php");
      expect(url.searchParams.get("i")).toBe("52772");
      return json({ meals: [{
        idMeal: "52772", strMeal: "Example Meal", strInstructions: "Cook carefully.",
        strIngredient1: "Chicken", strMeasure1: "500 g",
        strIngredient2: "Soy sauce", strMeasure2: "2 tbsp",
        strIngredient3: "", strMeasure3: "",
        strMealThumb: "https://www.themealdb.com/images/media/meals/test.jpg",
      }] });
    }));
    const result = JSON.parse(await runConsumerDiscoveryTool("get_meal_recipe_details", { meal_id: "52772" }));
    expect(result.recipe.instructions).toBe("Cook carefully.");
    expect(result.recipe.ingredients).toEqual([
      { ingredient: "Chicken", measure: "500 g" },
      { ingredient: "Soy sauce", measure: "2 tbsp" },
    ]);
  });

  it("filters meals by exactly one category, area or main ingredient", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      expect(url.pathname).toBe("/api/json/v1/1/filter.php");
      expect(url.searchParams.get("i")).toBe("chicken_breast");
      return json({ meals: [{ idMeal: "12345", strMeal: "Chicken Dish", strMealThumb: "https://www.themealdb.com/images/media/meals/test.jpg" }] });
    }));
    const result = JSON.parse(await runConsumerDiscoveryTool("filter_meal_recipes", { ingredient: "chicken_breast" }));
    expect(result.filter).toEqual({ type: "ingredient", value: "chicken_breast" });
    expect(result.meals[0].meal_id).toBe("12345");
    await expect(runConsumerDiscoveryTool("filter_meal_recipes", { ingredient: "chicken", area: "Japanese" })).rejects.toThrow("exactly one");
  });

  it("returns a clear not-found result for an unknown recipe and rejects malformed IDs", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => json({ meals: null })));
    const result = JSON.parse(await runConsumerDiscoveryTool("get_meal_recipe_details", { meal_id: "88888" }));
    expect(result.status).toBe("not_found");
    await expect(runConsumerDiscoveryTool("get_meal_recipe_details", { meal_id: "../../etc/passwd" })).rejects.toThrow("digits only");
  });

  it("searches Wikidata in Vietnamese or English and keeps item URLs canonical", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("www.wikidata.org");
      expect(url.searchParams.get("action")).toBe("wbsearchentities");
      expect(url.searchParams.get("language")).toBe("vi");
      expect(url.searchParams.get("maxlag")).toBe("5");
      expect(new Headers(init?.headers).get("user-agent")).toContain("NolaneSearch");
      return json({ search: [{
        id: "Q42", label: "Douglas Adams", description: "English writer and humorist",
        aliases: ["Douglas Noël Adams"],
      }, { id: "not-a-qid", label: "Unsafe" }] });
    }));
    const result = JSON.parse(await runConsumerDiscoveryTool("search_wikidata_entities", { query: "Douglas Adams", language: "vi" }));
    expect(result.entities).toHaveLength(1);
    expect(result.entities[0].entity_id).toBe("Q42");
    expect(result.entities[0].wikidata_url).toBe("https://www.wikidata.org/wiki/Q42");
  });

  it("looks up English and Vietnamese labels, aliases and encyclopedia links", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      expect(url.searchParams.get("action")).toBe("wbgetentities");
      expect(url.searchParams.get("ids")).toBe("Q42");
      expect(url.searchParams.get("sitefilter")).toBe("enwiki|viwiki");
      return json({ entities: { Q42: {
        labels: { en: { language: "en", value: "Douglas Adams" }, vi: { language: "vi", value: "Douglas Adams" } },
        descriptions: { en: { language: "en", value: "English writer" }, vi: { language: "vi", value: "Nhà văn người Anh" } },
        aliases: { en: [{ value: "Douglas Noël Adams" }], vi: [] },
        sitelinks: { enwiki: { title: "Douglas Adams" }, viwiki: { title: "Douglas Adams" } },
      } } });
    }));
    const result = JSON.parse(await runConsumerDiscoveryTool("get_wikidata_entity", { entity_id: "Q42" }));
    expect(result.labels.vi).toBe("Douglas Adams");
    expect(result.descriptions.vi).toBe("Nhà văn người Anh");
    expect(result.encyclopedia_articles).toHaveLength(2);
    expect(result.encyclopedia_articles[1].url).toContain("vi.wikipedia.org");
  });

  it("rejects invalid Wikidata IDs and unknown languages before network access", async () => {
    const mock = vi.fn();
    vi.stubGlobal("fetch", mock);
    await expect(runConsumerDiscoveryTool("get_wikidata_entity", { entity_id: "P31" })).rejects.toThrow("Q42");
    await expect(runConsumerDiscoveryTool("search_wikidata_entities", { query: "test", language: "fr" })).rejects.toThrow("en or vi");
    expect(mock).not.toHaveBeenCalled();
  });

  it("backs off clearly when upstream rate limits the request", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => json({}, 429)));
    await expect(runConsumerDiscoveryTool("search_wikidata_entities", { query: "test" })).rejects.toThrow("rate-limiting");
  });

  it("registers and dispatches all Wave 53 tools through the AI interface", async () => {
    const names = AGENT_TOOL_DEFINITIONS.map(tool => tool.function.name);
    expect(names).toEqual(expect.arrayContaining([
      "search_meal_recipes", "filter_meal_recipes", "get_meal_recipe_details",
      "search_wikidata_entities", "get_wikidata_entity",
    ]));
    vi.stubGlobal("fetch", vi.fn(async () => json({ search: [{ id: "Q42", label: "Douglas Adams", description: "Writer" }] })));
    const result = JSON.parse(await executeAgentTool(env, "search_wikidata_entities", { query: "Douglas Adams" }));
    expect(result.entities[0].entity_id).toBe("Q42");
  });
});
