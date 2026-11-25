import { afterEach, describe, expect, it, vi } from "vitest";
import { searchPeerTubeVideos } from "../src/media-discovery-tools";
import { executeAgentTool, AGENT_TOOL_DEFINITIONS } from "../src/agent-tools";
import type { Env } from "../src/types";

afterEach(() => vi.unstubAllGlobals());

const env = { DB: {} as never, SEARCH_JOBS: {} as never } as Env;

function json(value: unknown, status = 200): Response {
  return new Response(JSON.stringify(value), {
    status,
    headers: { "content-type": "application/json" },
  });
}

describe("Wave 59 PeerTube federated video discovery", () => {
  it("queries SepiaSearch with bounded SFW and relevance-ranked parameters", async () => {
    const mock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = new URL(String(input));
      expect(url.origin).toBe("https://sepiasearch.org");
      expect(url.pathname).toBe("/api/v1/search/videos");
      expect(url.searchParams.get("search")).toBe("open source science");
      expect(url.searchParams.get("start")).toBe("0");
      expect(url.searchParams.get("count")).toBe("4");
      expect(url.searchParams.get("sort")).toBe("-match");
      expect(url.searchParams.get("nsfw")).toBe("false");
      expect(init?.redirect).toBe("error");
      expect(new Headers(init?.headers).get("user-agent")).toContain("NolaneSearch");
      return json({
        total: 18,
        data: [
          {
            uuid: "a65bc12e-9383-462e-81ae-8207e8b434ee",
            name: "Open <b>Science</b> Video",
            url: "https://videos.example.org/videos/watch/a65bc12e-9383-462e-81ae-8207e8b434ee",
            truncatedDescription: "An <p>open science</p> introduction.",
            publishedAt: "2026-11-20T10:00:00.000Z",
            duration: 245,
            views: 1234,
            nsfw: false,
            isLive: false,
            account: { name: "creator", displayName: "Science Creator", host: "videos.example.org" },
            channel: { name: "science", displayName: "Science Channel", host: "videos.example.org" },
            language: { id: "en", label: "English" },
            licence: { id: 1, label: "Creative Commons Attribution" }
          },
          {
            name: "Cross-host URL",
            url: "https://attacker.example/videos/watch/unsafe",
            account: { name: "creator", host: "videos.example.org" },
            channel: { name: "channel", host: "videos.example.org" },
            nsfw: false
          },
          {
            name: "NSFW result",
            url: "https://videos.example.org/videos/watch/nsfw",
            account: { name: "creator", host: "videos.example.org" },
            channel: { name: "channel", host: "videos.example.org" },
            nsfw: true
          },
          {
            name: "Missing origin",
            url: "https://videos.example.org/videos/watch/no-host",
            nsfw: false
          }
        ]
      });
    });
    vi.stubGlobal("fetch", mock);

    const result = await searchPeerTubeVideos("open source science", 4);

    expect(result.status).toBe("ok");
    expect(result.source).toContain("SepiaSearch");
    expect(result.total).toBe(18);
    expect(result.result_count).toBe(1);
    expect(result.items[0]).toMatchObject({
      provider: "PeerTube",
      mediaType: "video",
      title: "Open Science Video",
      sourceUrl: "https://videos.example.org/videos/watch/a65bc12e-9383-462e-81ae-8207e8b434ee",
      embedUrl: "https://videos.example.org/videos/embed/a65bc12e-9383-462e-81ae-8207e8b434ee",
      instanceHost: "videos.example.org",
      author: "Science Creator",
      channel: "Science Channel",
      durationSeconds: 245,
      views: 1234,
      language: "English",
      license: "Creative Commons Attribution",
      isLive: false,
      dateCreated: "2026-11-20T10:00:00.000Z"
    });
    expect(result.items[0].previewUrl).toBeNull();
    expect(result.items[0].mediaUrl).toBeNull();
    expect(mock).toHaveBeenCalledTimes(1);
  });


  it("includes source-flagged NSFW results only when explicitly requested", async () => {
    const mock = vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      expect(url.searchParams.get("nsfw")).toBe("true");
      return json({
        total: 2,
        data: [
          {
            uuid: "a65bc12e-9383-462e-81ae-8207e8b434ee",
            name: "Public standard result",
            url: "https://videos.example.org/videos/watch/standard",
            account: { name: "author", host: "videos.example.org" },
            channel: { name: "channel", host: "videos.example.org" },
            nsfw: false,
            nsfwFlags: 0
          },
          {
            uuid: "b65bc12e-9383-462e-81ae-8207e8b434ef",
            name: "Age-gated result",
            url: "https://videos.example.org/videos/watch/adult",
            account: { name: "author", host: "videos.example.org" },
            channel: { name: "channel", host: "videos.example.org" },
            nsfw: true,
            nsfwFlags: 2
          }
        ]
      });
    });
    vi.stubGlobal("fetch", mock);

    const result = await searchPeerTubeVideos("adult catalog", 4, true);
    expect(result.result_count).toBe(2);
    expect(result.items[1]).toMatchObject({
      title: "Age-gated result",
      nsfw: true,
      nsfwFlags: 2,
      previewUrl: null,
      mediaUrl: null
    });
    expect(result.note).toContain("18+ mode");
    expect(mock).toHaveBeenCalledTimes(1);
  });

  it("rejects non-boolean NSFW controls before network access", async () => {
    const mock = vi.fn();
    vi.stubGlobal("fetch", mock);
    await expect(searchPeerTubeVideos("video query", 4, "true")).rejects.toThrow("include_nsfw must be a boolean");
    expect(mock).not.toHaveBeenCalled();
  });

  it("rejects unsafe domains, IP hosts and invalid URL schemes before returning links", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => json({
      data: [
        {
          name: "IP address",
          url: "https://127.0.0.1/videos/watch/unsafe",
          account: { host: "127.0.0.1" },
          channel: { host: "127.0.0.1" }
        },
        {
          name: "HTTP origin",
          url: "http://videos.example.org/videos/watch/unsafe",
          account: { host: "videos.example.org" },
          channel: { host: "videos.example.org" }
        },
        {
          name: "Credentials",
          url: "https://user:pass@videos.example.org/videos/watch/unsafe",
          account: { host: "videos.example.org" },
          channel: { host: "videos.example.org" }
        }
      ]
    })));

    const result = await searchPeerTubeVideos("safe video");
    expect(result.status).toBe("not_found");
    expect(result.items).toHaveLength(0);
  });

  it("validates query and result bounds before network access", async () => {
    const mock = vi.fn();
    vi.stubGlobal("fetch", mock);
    await expect(searchPeerTubeVideos("x")).rejects.toThrow("2 to 140 characters");
    await expect(searchPeerTubeVideos("science", 9)).rejects.toThrow("1 to 8");
    expect(mock).not.toHaveBeenCalled();
  });

  it("reports rate limits and temporary upstream failures clearly", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => json({}, 429)));
    await expect(searchPeerTubeVideos("open source")).rejects.toThrow("temporarily rate-limiting");
    vi.stubGlobal("fetch", vi.fn(async () => json({}, 503)));
    await expect(searchPeerTubeVideos("open source")).rejects.toThrow("temporarily rate-limiting");
  });

  it("requires the adult-media feature gate before AI tools can request NSFW records", async () => {
    const definition = AGENT_TOOL_DEFINITIONS.find(tool => tool.function.name === "search_peertube_videos");
    expect(definition?.function.parameters).toMatchObject({
      properties: { include_nsfw: { type: "boolean" } },
      required: ["query"],
      additionalProperties: false
    });
    const mock = vi.fn();
    vi.stubGlobal("fetch", mock);
    await expect(executeAgentTool(env, "search_peertube_videos", {
      query: "adult catalog", include_nsfw: true
    })).rejects.toThrow("NSFW search is disabled");
    expect(mock).not.toHaveBeenCalled();
  });

  it("passes the explicit NSFW choice to SepiaSearch when the deployment gate is enabled", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      expect(url.searchParams.get("nsfw")).toBe("true");
      return json({
        total: 1,
        data: [{
          uuid: "b65bc12e-9383-462e-81ae-8207e8b434ef",
          name: "Age-gated result",
          url: "https://videos.example.org/videos/watch/adult",
          account: { name: "author", host: "videos.example.org" },
          channel: { name: "channel", host: "videos.example.org" },
          nsfw: true,
          nsfwFlags: 2
        }]
      });
    }));
    const enabledEnv = { ...env, MEDIA_ALLOW_NSFW: "true" } as Env;
    const result = JSON.parse(await executeAgentTool(enabledEnv, "search_peertube_videos", {
      query: "adult catalog", include_nsfw: true
    }));
    expect(result.items[0]).toMatchObject({ title: "Age-gated result", nsfw: true, nsfwFlags: 2 });
  });

  it("registers and invokes PeerTube search through the AI tool interface", async () => {
    const definition = AGENT_TOOL_DEFINITIONS.find(tool => tool.function.name === "search_peertube_videos");
    expect(definition).toBeDefined();
    expect(definition?.function.parameters).toMatchObject({
      required: ["query"],
      additionalProperties: false
    });

    vi.stubGlobal("fetch", vi.fn(async () => json({
      total: 1,
      data: [{
        uuid: "a65bc12e-9383-462e-81ae-8207e8b434ee",
        name: "Agent Search Video",
        url: "https://videos.example.org/videos/watch/a65bc12e-9383-462e-81ae-8207e8b434ee",
        account: { name: "author", host: "videos.example.org" },
        channel: { name: "channel", host: "videos.example.org" },
        nsfw: false
      }]
    })));

    const result = JSON.parse(await executeAgentTool(env, "search_peertube_videos", {
      query: "agent search video"
    }));
    expect(result.items[0]).toMatchObject({
      title: "Agent Search Video",
      provider: "PeerTube",
      instanceHost: "videos.example.org"
    });
  });
});
