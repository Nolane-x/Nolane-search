import { describe, expect, it } from "vitest";
import { constantTimeEqual, isSafePublicUrl, normalizeUrl } from "../src/security";
import { isAllowedByRobots, parseRobotsRules } from "../src/watch";

describe("isSafePublicUrl", () => {
  it("accepts HTTPS public websites", () => {
    expect(isSafePublicUrl("https://example.com/docs")?.hostname).toBe("example.com");
  });
  it("rejects non-HTTPS URLs", () => {
    expect(isSafePublicUrl("http://example.com")).toBeNull();
  });
  it("rejects localhost and local suffixes", () => {
    expect(isSafePublicUrl("https://localhost")).toBeNull();
    expect(isSafePublicUrl("https://printer.local")).toBeNull();
    expect(isSafePublicUrl("https://service.internal")).toBeNull();
    expect(isSafePublicUrl("https://nas.home.arpa")).toBeNull();
    expect(isSafePublicUrl("https://printer.lan")).toBeNull();
    expect(isSafePublicUrl("https://corp.intranet")).toBeNull();
    expect(isSafePublicUrl("https://example.onion")).toBeNull();
  });
  it("rejects IP literals and private targets", () => {
    expect(isSafePublicUrl("https://127.0.0.1")).toBeNull();
    expect(isSafePublicUrl("https://192.168.1.20")).toBeNull();
    expect(isSafePublicUrl("https://10.0.0.5")).toBeNull();
  });
  it("rejects credentials and non-standard ports", () => {
    expect(isSafePublicUrl("https://user:pass@example.com")).toBeNull();
    expect(isSafePublicUrl("https://example.com:8443")).toBeNull();
  });
});

describe("normalizeUrl", () => {
  it("removes tracking parameters and fragments", () => {
    expect(normalizeUrl("https://Example.com/page?utm_source=x&id=4#section"))
      .toBe("https://example.com/page?id=4");
  });
  it("sorts query parameters", () => {
    expect(normalizeUrl("https://example.com/?z=2&a=1"))
      .toBe("https://example.com/?a=1&z=2");
  });
});

describe("constantTimeEqual", () => {
  it("matches equal strings and rejects differences", () => {
    expect(constantTimeEqual("secret", "secret")).toBe(true);
    expect(constantTimeEqual("secret", "Secret")).toBe(false);
    expect(constantTimeEqual("short", "longer")).toBe(false);
  });
});

describe("robots.txt policy", () => {
  it("uses the specific NolaneSearchBot group instead of the wildcard group", () => {
    const rules = parseRobotsRules([
      "User-agent: *", "Disallow: /private", "",
      "User-agent: NolaneSearchBot", "Disallow: /internal",
    ].join(String.fromCharCode(10)));
    expect(isAllowedByRobots("https://example.com/public", rules)).toBe(true);
    expect(isAllowedByRobots("https://example.com/private", rules)).toBe(true);
    expect(isAllowedByRobots("https://example.com/internal", rules)).toBe(false);
  });

  it("combines matching groups and picks the longest rule", () => {
    const rules = parseRobotsRules([
      "User-agent: NolaneSearchBot", "Disallow: /docs", "Allow: /docs/public", "",
      "User-agent: nolanesearchbot", "Disallow: /account",
    ].join(String.fromCharCode(10)));
    expect(isAllowedByRobots("https://example.com/docs/private", rules)).toBe(false);
    expect(isAllowedByRobots("https://example.com/docs/public/start", rules)).toBe(true);
    expect(isAllowedByRobots("https://example.com/account", rules)).toBe(false);
  });

  it("supports wildcard and end-anchored rules", () => {
    const rules = parseRobotsRules([
      "User-agent: *", "Disallow: /*.pdf$", "Allow: /open/report.pdf",
    ].join(String.fromCharCode(10)));
    expect(isAllowedByRobots("https://example.com/private/report.pdf", rules)).toBe(false);
    expect(isAllowedByRobots("https://example.com/open/report.pdf", rules)).toBe(true);
    expect(isAllowedByRobots("https://example.com/private/report.pdf?download=1", rules)).toBe(true);
  });

  it("allows URLs when no applicable rules exist", () => {
    const rules = parseRobotsRules(["User-agent: OtherBot", "Disallow: /"].join(String.fromCharCode(10)));
    expect(isAllowedByRobots("https://example.com/page", rules)).toBe(true);
  });

  it("prefers Allow when matching rules have equal specificity", () => {
    const rules = parseRobotsRules([
      "User-agent: *", "Disallow: /same", "Allow: /same",
    ].join(String.fromCharCode(10)));
    expect(isAllowedByRobots("https://example.com/same", rules)).toBe(true);
  });
});
