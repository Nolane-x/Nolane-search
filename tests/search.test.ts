import { describe, expect, it } from "vitest";
import { normalizeUrl } from "../src/security";

describe("search URL normalization", () => {
  it("treats tracking-parameter variants as the same URL", () => {
    expect(normalizeUrl("https://example.com/a?utm_source=x&id=2"))
      .toBe(normalizeUrl("https://example.com/a?id=2"));
  });

  it("preserves meaningful query parameters", () => {
    expect(normalizeUrl("https://example.com/search?q=workers"))
      .toContain("q=workers");
  });
});
