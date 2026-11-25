import { afterEach, describe, expect, it, vi } from "vitest";
import { resolveMediaEmbed } from "../src/media-embed-resolver";

afterEach(() => vi.unstubAllGlobals());

function json(value: unknown, status = 200): Response {
  return new Response(JSON.stringify(value), {
    status,
    headers: { "content-type": "application/json" },
  });
}

describe("Wave 64 user-provided media URL resolver", () => {
  it("resolves YouTube watch, short and shorts URLs to the privacy-enhanced player", async () => {
    const mock = vi.fn();
    vi.stubGlobal("fetch", mock);

    const watch = await resolveMediaEmbed("https://www.youtube.com/watch?v=M7lc1UVf-VE");
    const short = await resolveMediaEmbed("https://youtu.be/M7lc1UVf-VE");
    const shorts = await resolveMediaEmbed("https://www.youtube.com/shorts/M7lc1UVf-VE");

    expect(watch).toMatchObject({
      status: "resolved",
      item: {
        provider: "YouTube",
        mediaType: "video",
        sourceUrl: "https://www.youtube.com/watch?v=M7lc1UVf-VE",
        embedUrl: "https://www.youtube-nocookie.com/embed/M7lc1UVf-VE?playsinline=1&rel=0",
      },
    });
    expect(shorts).toMatchObject({ status: "resolved", item: { embedUrl: watch.status === "resolved" ? watch.item.embedUrl : null } });
    expect(short).toMatchObject({ status: "resolved", item: { provider: "YouTube" } });
    expect(mock).not.toHaveBeenCalled();
  });

  it("rejects non-HTTPS, credentials, ports, IP literals and untrusted YouTube hosts", async () => {
    const mock = vi.fn();
    vi.stubGlobal("fetch", mock);
    const inputs = [
      "http://youtube.com/watch?v=M7lc1UVf-VE",
      "https://user:pass@youtube.com/watch?v=M7lc1UVf-VE",
      "https://youtube.com:8443/watch?v=M7lc1UVf-VE",
      "https://127.0.0.1/watch?v=M7lc1UVf-VE",
      "https://youtube.com.attacker.example/watch?v=M7lc1UVf-VE",
      "https://evil.example/watch?v=M7lc1UVf-VE",
      "https://www.youtube.com/watch?v=../admin",
    ];
    for (const input of inputs) {
      expect((await resolveMediaEmbed(input)).status).toBe("unsupported");
    }
    expect(mock).not.toHaveBeenCalled();
  });

  it("resolves PeerTube only from a canonical UUID and exact instance origin", async () => {
    const result = await resolveMediaEmbed(
      "https://videos.example.org/videos/watch/a65bc12e-9383-462e-81ae-8207e8b434ee"
    );
    expect(result).toMatchObject({
      status: "resolved",
      item: {
        provider: "PeerTube",
        instanceHost: "videos.example.org",
        embedUrl: "https://videos.example.org/videos/embed/a65bc12e-9383-462e-81ae-8207e8b434ee",
      },
    });
  });

  it("resolves Vimeo through the fixed official oEmbed endpoint and preserves its unlisted hash", async () => {
    const mock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = new URL(String(input));
      expect(url.origin).toBe("https://vimeo.com");
      expect(url.pathname).toBe("/api/oembed.json");
      expect(url.searchParams.get("url")).toBe("https://vimeo.com/123456789/abcdef1234");
      expect(url.searchParams.get("dnt")).toBe("true");
      expect(init?.redirect).toBe("error");
      return json({
        type: "video",
        provider_name: "Vimeo",
        title: "Vimeo test video",
        author_name: "Video author",
        html: '<iframe src="https://player.vimeo.com/video/123456789?h=abcdef1234"></iframe>',
        thumbnail_url: "https://i.vimeocdn.com/video/12345_640.jpg",
      });
    });
    vi.stubGlobal("fetch", mock);

    const result = await resolveMediaEmbed("https://vimeo.com/123456789/abcdef1234");
    expect(result).toMatchObject({
      status: "resolved",
      item: {
        provider: "Vimeo",
        title: "Vimeo test video",
        credit: "Video author",
        embedUrl: "https://player.vimeo.com/video/123456789?h=abcdef1234&dnt=1",
        previewUrl: "https://i.vimeocdn.com/video/12345_640.jpg",
      },
    });
    expect(mock).toHaveBeenCalledTimes(1);
  });

  it("rejects Vimeo oEmbed HTML whose iframe source is not the matching official player", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => json({
      type: "video",
      html: '<iframe src="https://evil.example/video/123456789"></iframe>',
    })));
    await expect(resolveMediaEmbed("https://vimeo.com/123456789"))
      .rejects.toThrow("Vimeo returned an invalid embed URL");
  });

  it("does not invent a Dailymotion player ID when the deployment has none", async () => {
    const result = await resolveMediaEmbed("https://www.dailymotion.com/video/x84sh87");
    expect(result).toMatchObject({
      status: "needs_configuration",
      provider: "Dailymotion",
    });
  });

  it("uses a configured Dailymotion Player ID with the documented player endpoint", async () => {
    const result = await resolveMediaEmbed("https://dai.ly/x84sh87", "x8lr5");
    expect(result).toMatchObject({
      status: "resolved",
      item: {
        provider: "Dailymotion",
        embedUrl: "https://geo.dailymotion.com/player/x8lr5.html?video=x84sh87",
        referrerPolicy: "strict-origin-when-cross-origin",
      },
    });
  });

  it("rejects inputs longer than the URL parsing limit before provider access", async () => {
    const mock = vi.fn();
    vi.stubGlobal("fetch", mock);
    const result = await resolveMediaEmbed("https://www.youtube.com/watch?v=" + "a".repeat(3000));
    expect(result.status).toBe("unsupported");
    expect(mock).not.toHaveBeenCalled();
  });

  it("rejects malformed or unsupported URLs without issuing any provider request", async () => {
    const mock = vi.fn();
    vi.stubGlobal("fetch", mock);
    for (const input of ["", "not a URL", "ftp://vimeo.com/12345", "https://vimeo.com.attacker.example/12345"]) {
      expect((await resolveMediaEmbed(input)).status).toBe("unsupported");
    }
    expect(mock).not.toHaveBeenCalled();
  });
});
