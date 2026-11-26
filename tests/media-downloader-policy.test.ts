import { afterEach, describe, expect, it, vi } from "vitest";
import {
  hasOnlyPublicDnsAnswers,
  isPublicDomainName,
  isPublicIpAddress,
  normalizeMediaDownloadUrl,
  parseMediaDownloadInput,
} from "../src/media-downloader-policy";

afterEach(() => vi.unstubAllGlobals());

describe("Wave 73 media downloader URL policy", () => {
  it("normalizes public HTTP and HTTPS page URLs without userinfo or custom ports", () => {
    expect(normalizeMediaDownloadUrl("https://www.youtube.com/watch?v=abc123")).toEqual({
      ok: true,
      url: "https://www.youtube.com/watch?v=abc123",
    });
    expect(normalizeMediaDownloadUrl("  https://vimeo.com/12345678  ")).toMatchObject({
      ok: true,
      url: "https://vimeo.com/12345678",
    });
    expect(normalizeMediaDownloadUrl("http://example.org/video")).toMatchObject({ ok: true });
  });

  it("rejects non-HTTP schemes, credentials, custom ports, fragments and invalid lengths", () => {
    for (const value of [
      "ftp://example.org/video",
      "file:///etc/passwd",
      "javascript:alert(1)",
      "https://user:password@example.org/video",
      "https://example.org:8443/video",
      "https://example.org/video#fragment",
      "https://x",
      "https://example.org/" + "a".repeat(2050),
      "https://example.org/video\nX-Header: bad",
    ]) {
      expect(normalizeMediaDownloadUrl(value).ok).toBe(false);
    }
    expect(normalizeMediaDownloadUrl(null).ok).toBe(false);
  });

  it("rejects direct IP addresses, loopback, private, link-local and internal hostnames", () => {
    for (const host of [
      "127.0.0.1", "10.0.0.1", "172.16.0.1", "192.168.1.5",
      "169.254.169.254", "100.64.0.1", "0.0.0.0",
      "localhost", "media.local", "service.internal", "metadata.google.internal",
      "host.example", "host.invalid", "host.test", "host.onion",
    ]) {
      expect(isPublicDomainName(host), host).toBe(false);
      expect(normalizeMediaDownloadUrl("https://" + host + "/video").ok, host).toBe(false);
    }
  });

  it("handles numeric host obfuscation as IP addresses after URL normalization", () => {
    for (const host of ["2130706433", "0x7f000001", "0177.0.0.1", "127.1"]) {
      expect(normalizeMediaDownloadUrl("http://" + host + "/video").ok, host).toBe(false);
    }
  });

  it("classifies public and non-public IPv4 and IPv6 ranges", () => {
    for (const address of [
      "127.0.0.1", "10.1.2.3", "172.20.1.1", "192.168.1.1",
      "169.254.1.2", "100.64.1.1", "198.18.0.1", "224.0.0.1",
      "0.0.0.0", "192.0.2.1", "203.0.113.9",
    ]) {
      expect(isPublicIpAddress(address), address).toBe(false);
    }
    for (const address of ["1.1.1.1", "8.8.8.8", "93.184.216.34"]) {
      expect(isPublicIpAddress(address), address).toBe(true);
    }
    for (const address of [
      "::", "::1", "fe80::1", "fc00::1", "fd12::1234",
      "ff02::1", "::ffff:192.168.1.1", "2001:db8::1",
      "2001::1", "64:ff9b::808:808",
    ]) {
      expect(isPublicIpAddress(address), address).toBe(false);
    }
    for (const address of ["2001:4860:4860::8888", "2606:4700:4700::1111", "2a00:1450:4001::1"]) {
      expect(isPublicIpAddress(address), address).toBe(true);
    }
  });

  it("accepts only a bounded media format and quality selection", () => {
    expect(parseMediaDownloadInput({
      url: "https://www.youtube.com/watch?v=abc123", format: "video", quality: "1080",
    })).toMatchObject({ ok: true, value: { format: "video", quality: "1080" } });
    expect(parseMediaDownloadInput({
      url: "https://soundcloud.com/artist/track", format: "audio",
    })).toMatchObject({ ok: true, value: { format: "audio", quality: "720" } });
    expect(parseMediaDownloadInput({ url: "https://example.org/a", format: "playlist" }).ok).toBe(false);
    expect(parseMediaDownloadInput({ url: "https://example.org/a", format: "video", quality: "2160" }).ok).toBe(false);
    expect(parseMediaDownloadInput({ url: "https://example.org/a", format: "audio", quality: "best" }).ok).toBe(false);
    expect(parseMediaDownloadInput([]).ok).toBe(false);
  });

  it("fails closed when DNS returns a private address or an empty answer", async () => {
    const fetcher = vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      const type = Number(url.searchParams.get("type"));
      return new Response(JSON.stringify({
        Status: 0,
        Answer: [{ type, data: type === 1 ? "93.184.216.34" : "fd00::1" }],
      }), { status: 200 });
    });
    await expect(hasOnlyPublicDnsAnswers("example.org", fetcher)).resolves.toBe(false);
    expect(fetcher).toHaveBeenCalledTimes(2);

    const emptyFetcher = vi.fn(async () => new Response(JSON.stringify({ Status: 0, Answer: [] }), { status: 200 }));
    await expect(hasOnlyPublicDnsAnswers("example.org", emptyFetcher)).resolves.toBe(false);
  });

  it("fails closed on DNS errors, non-2xx responses and invalid names before network access", async () => {
    const errorFetcher = vi.fn(async () => new Response("unavailable", { status: 503 }));
    await expect(hasOnlyPublicDnsAnswers("example.org", errorFetcher)).rejects.toThrow("HTTP 503");
    expect(errorFetcher).toHaveBeenCalledTimes(2);

    const invalidFetcher = vi.fn();
    await expect(hasOnlyPublicDnsAnswers("metadata.google.internal", invalidFetcher)).resolves.toBe(false);
    expect(invalidFetcher).not.toHaveBeenCalled();
  });
});
