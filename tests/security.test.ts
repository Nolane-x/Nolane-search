import { describe, expect, it } from "vitest";
import { constantTimeEqual, isSafePublicUrl, normalizeUrl } from "../src/security";

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
