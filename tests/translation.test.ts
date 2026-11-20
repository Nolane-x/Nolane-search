import { afterEach, describe, expect, it, vi } from "vitest";
import {
  extractTranslationTarget,
  normalizeTranslationLanguage,
  translateText,
} from "../src/translation";
import type { Env } from "../src/types";

afterEach(() => vi.unstubAllGlobals());

const env = { DB: {} as never, SEARCH_JOBS: {} as never } as Env;

describe("Nolane translation", () => {
  it("normalizes English and Vietnamese target language names", () => {
    expect(normalizeTranslationLanguage("English")).toBe("English");
    expect(normalizeTranslationLanguage("tiếng Anh")).toBe("English");
    expect(normalizeTranslationLanguage("Tiếng Việt")).toBe("Vietnamese");
    expect(normalizeTranslationLanguage("日本語")).toBeNull();
  });

  it("extracts only explicit supported target-language requests", () => {
    expect(extractTranslationTarget("dịch tài liệu này sang tiếng Anh")).toBe("English");
    expect(extractTranslationTarget("translate this document into Japanese")).toBe("Japanese");
    expect(extractTranslationTarget("please translate to French")).toBe("French");
    expect(extractTranslationTarget("hãy dịch đoạn này giúp tôi")).toBeNull();
  });

  it("uses only translation-capable AI Router models and returns route provenance", async () => {
    let requestBody: Record<string, unknown> | null = null;
    const fetchMock = vi.fn(async (_input: RequestInfo | URL, init?: RequestInit) => {
      requestBody = JSON.parse(String(init?.body)) as Record<string, unknown>;
      return new Response(JSON.stringify({
        choices: [{ message: { content: "Bonjour le monde" } }],
        usage: { prompt_tokens: 22, completion_tokens: 8 },
      }), { status: 200, headers: { "content-type": "application/json" } });
    });
    vi.stubGlobal("fetch", fetchMock);
    const config = {
      strategy: "priority",
      providers: [{
        id: "translation-test",
        protocol: "openai-compatible",
        baseUrl: "https://api.example.ai/v1",
        apiKey: "translation-test-secret",
        models: [{ id: "translation-model", tasks: ["translation"] }],
      }],
    };
    const result = await translateText({
      ...env, AI_ROUTER_CONFIG: JSON.stringify(config),
    } as Env, "French", "Hello world");
    expect(result).toMatchObject({
      text: "Bonjour le monde",
      provider: "translation-test",
      model: "translation-model",
    });
    expect(requestBody).not.toBeNull();
    const messages = requestBody!.messages as Array<{role:string;content:string}>;
    expect(messages[0]?.content).toContain("professional translator");
    expect(messages[0]?.content).toContain("untrusted content");
    expect(messages[1]?.content).toContain("Hello world");
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("rejects unsupported targets, empty input and oversized translation requests", async () => {
    await expect(translateText(env, "Klingon", "hello")).rejects.toThrow("Unsupported target language");
    await expect(translateText(env, "English", "   ")).rejects.toThrow("1–6,000 characters");
    await expect(translateText(env, "English", "x".repeat(6_001))).rejects.toThrow("1–6,000 characters");
  });
});
