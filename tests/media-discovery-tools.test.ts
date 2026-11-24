import { afterEach, describe, expect, it, vi } from "vitest";
import { runMediaDiscoveryTool, searchNasaMedia, searchWikimediaImages, searchOpenverseImages, searchInternetArchiveVideos, searchInternetArchiveAudio, lookupFoodProduct } from "../src/media-discovery-tools";
import { executeAgentTool, AGENT_TOOL_DEFINITIONS } from "../src/agent-tools";
import type { Env } from "../src/types";

afterEach(() => vi.unstubAllGlobals());
const env = { DB: {} as never, SEARCH_JOBS: {} as never } as Env;
function json(value: unknown, status = 200): Response {
  return new Response(JSON.stringify(value), { status, headers: { "content-type": "application/json" } });
}

describe("Wave 52 media and product discovery", () => {
  it("searches Commons files and retains image license, author and original-page links", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("commons.wikimedia.org");
      expect(url.searchParams.get("gsrnamespace")).toBe("6");
      expect(url.searchParams.get("iiprop")).toContain("extmetadata");
      expect(new Headers(init?.headers).get("user-agent")).toContain("NolaneSearch");
      return json({ query: { pages: [{
        pageid: 7, title: "File:Example.jpg",
        imageinfo: [{
          mime: "image/jpeg", width: 1200, height: 800,
          url: "https://upload.wikimedia.org/wikipedia/commons/example.jpg",
          thumburl: "https://upload.wikimedia.org/wikipedia/commons/thumb/example.jpg",
          descriptionurl: "https://commons.wikimedia.org/wiki/File:Example.jpg",
          extmetadata: {
            LicenseShortName: { value: "CC BY-SA 4.0" },
            LicenseUrl: { value: "https://creativecommons.org/licenses/by-sa/4.0/" },
            Artist: { value: "Example Artist" },
            ImageDescription: { value: "<p>Example landscape</p>" },
          },
        }],
      }] } });
    }));
    const result = await searchWikimediaImages("landscape", 5);
    expect(result.items).toHaveLength(1);
    expect(result.items[0].license).toBe("CC BY-SA 4.0");
    expect(result.items[0].credit).toBe("Example Artist");
    expect(result.items[0].description).toBe("Example landscape");
    expect(result.items[0].sourceUrl).toContain("commons.wikimedia.org/wiki/File");
  });

  it("omits Commons files with absent license data or untrusted media URLs", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => json({ query: { pages: [
      { pageid: 8, title: "File:Unknown.jpg", imageinfo: [{ mime: "image/jpeg", url: "https://upload.wikimedia.org/a.jpg", thumburl: "https://upload.wikimedia.org/a.jpg", descriptionurl: "https://commons.wikimedia.org/wiki/File:Unknown.jpg", extmetadata: {} }] },
      { pageid: 9, title: "File:Remote.jpg", imageinfo: [{ mime: "image/jpeg", url: "https://evil.example/a.jpg", thumburl: "https://evil.example/a.jpg", descriptionurl: "https://commons.wikimedia.org/wiki/File:Remote.jpg", extmetadata: { LicenseShortName:{value:"CC0"}, LicenseUrl:{value:"https://creativecommons.org/publicdomain/zero/1.0/"} } }] },
    ] } })));
    const result = await searchWikimediaImages("test");
    expect(result.items).toHaveLength(0);
  });

  it("searches NASA image results and returns preview and source links", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("images-api.nasa.gov");
      expect(url.pathname).toBe("/search");
      expect(url.searchParams.get("media_type")).toBe("image");
      return json({ collection: { items: [{
        data: [{ nasa_id: "PIA123", title: "Mars Example", media_type: "image", description: "A Martian landscape", center: "JPL", date_created: "2026-01-01" }],
        links: [{ rel: "preview", href: "https://images-assets.nasa.gov/image/PIA123/PIA123~thumb.jpg" }],
      }] } });
    }));
    const result = await searchNasaMedia("Mars", "image", 4);
    expect(result.items).toHaveLength(1);
    expect(result.items[0].previewUrl).toContain("images-assets.nasa.gov");
    expect(result.items[0].mediaUrl).toBe(result.items[0].previewUrl);
  });

  it("resolves public NASA video MP4 from a same-host asset manifest", async () => {
    const mock = vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      if (url.pathname === "/search") return json({ collection: { items: [{
        data: [{ nasa_id: "VID123", title: "Space video", media_type: "video", center: "NASA" }],
        links: [{ rel: "preview", href: "https://images-assets.nasa.gov/video/VID123/VID123~thumb.jpg" }],
      }] } });
      if (url.pathname === "/asset/VID123") return json({ collection: { items: [
        { href: "https://images-assets.nasa.gov/video/VID123/VID123~orig.mp4" },
        { href: "https://evil.example/VID123.mp4" },
      ] } });
      throw new Error("Unexpected NASA endpoint");
    });
    vi.stubGlobal("fetch", mock);
    const result = await searchNasaMedia("space video", "video", 3);
    expect(result.items[0].mediaUrl).toBe("https://images-assets.nasa.gov/video/VID123/VID123~orig.mp4");
    expect(mock).toHaveBeenCalledTimes(2);
  });

  it("searches Openverse and preserves license, creator and source metadata", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("api.openverse.org");
      expect(url.pathname).toBe("/v1/images/");
      expect(url.searchParams.get("q")).toBe("red panda");
      expect(url.searchParams.get("mature")).toBe("false");
      expect(url.searchParams.get("filter_dead")).toBe("true");
      expect(new Headers(init?.headers).get("user-agent")).toContain("NolaneSearch");
      return json({ results: [
        {
          id: "123e4567-e89b-12d3-a456-426614174000",
          title: "Red panda in a tree",
          url: "https://cdn.example.org/red-panda.jpg",
          thumbnail: "https://api.openverse.org/v1/thumbs/123e4567-e89b-12d3-a456-426614174000",
          foreign_landing_url: "https://photos.example.org/red-panda",
          creator: "Wildlife photographer",
          license: "by-sa",
          license_version: "4.0",
          license_url: "https://creativecommons.org/licenses/by-sa/4.0/",
          mature: false,
          removed_from_source: false,
          indexed_on: "2026-11-20T00:00:00Z",
          width: 1600,
          height: 900
        },
        {
          id: "223e4567-e89b-12d3-a456-426614174000",
          title: "Mature result",
          url: "https://cdn.example.org/adult.jpg",
          thumbnail: "https://api.openverse.org/v1/thumbs/223e4567-e89b-12d3-a456-426614174000",
          foreign_landing_url: "https://photos.example.org/adult",
          creator: "Unknown",
          license: "by",
          license_url: "https://creativecommons.org/licenses/by/4.0/",
          mature: true
        }
      ] });
    }));
    const result = await searchOpenverseImages("red panda", 5);
    expect(result.items).toHaveLength(1);
    expect(result.items[0]).toMatchObject({
      provider: "Openverse",
      mediaType: "image",
      title: "Red panda in a tree",
      license: "BY-SA 4.0",
      credit: "Wildlife photographer",
      sourceUrl: "https://photos.example.org/red-panda",
      width: 1600,
      height: 900
    });
    expect(result.items[0].previewUrl).toContain("api.openverse.org");
  });

  it("omits Openverse results without verifiable license or safe source links", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => json({ results: [
      {
        id: "123e4567-e89b-12d3-a456-426614174000", title: "No license",
        url: "https://cdn.example.org/a.jpg", thumbnail: "https://api.openverse.org/v1/thumbs/123e4567-e89b-12d3-a456-426614174000",
        foreign_landing_url: "https://photos.example.org/a"
      },
      {
        id: "223e4567-e89b-12d3-a456-426614174000", title: "Unsafe URL",
        url: "javascript:alert(1)", thumbnail: "https://api.openverse.org/v1/thumbs/223e4567-e89b-12d3-a456-426614174000",
        foreign_landing_url: "https://photos.example.org/b", license: "by",
        license_url: "https://creativecommons.org/licenses/by/4.0/"
      }
    ] })));
    const result = await searchOpenverseImages("test");
    expect(result.items).toHaveLength(0);
  });

  it("finds publicly downloadable Internet Archive videos and skips restricted items", async () => {
    const mock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("archive.org");
      expect(new Headers(init?.headers).get("user-agent")).toContain("NolaneSearch");
      if (url.pathname === "/advancedsearch.php") {
        expect(url.searchParams.get("q")).toBe('title:"public documentary" AND mediatype:movies');
        expect(url.searchParams.getAll("fl[]")).toContain("identifier");
        expect(url.searchParams.get("rows")).toBe("2");
        return json({ response: { docs: [{ identifier: "public-film" }, { identifier: "restricted-film" }] } });
      }
      if (url.pathname === "/metadata/public-film") {
        return json({ metadata: {
          mediatype: "movies", title: "A Public Documentary", year: "1984",
          creator: "Archive contributor", licenseurl: "https://creativecommons.org/publicdomain/zero/1.0/",
          description: "An <b>archival</b> documentary"
        }, files: [
          { name: "metadata.xml", format: "Metadata", size: "100", source: "original" },
          { name: "documentary.mp4", format: "MPEG4", size: "1200000", source: "original" },
          { name: "private-copy.mp4", format: "MPEG4", size: "1200000", source: "original", private: "true" }
        ] });
      }
      if (url.pathname === "/metadata/restricted-film") {
        return json({ metadata: {
          mediatype: "movies", title: "Restricted Film", "access-restricted-item": "true"
        }, files: [{ name: "restricted.mp4", format: "MPEG4", size: "1200", source: "original" }] });
      }
      throw new Error("Unexpected Internet Archive endpoint: " + url.pathname);
    });
    vi.stubGlobal("fetch", mock);
    const result = await searchInternetArchiveVideos("public documentary", 2);
    expect(result.items).toHaveLength(1);
    expect(result.items[0]).toMatchObject({
      provider: "Internet Archive",
      mediaType: "video",
      title: "A Public Documentary",
      credit: "Archive contributor",
      license: "Creative Commons (see item)",
      licenseUrl: "https://creativecommons.org/publicdomain/zero/1.0/",
      dateCreated: "1984",
      sourceUrl: "https://archive.org/details/public-film",
      mediaUrl: "https://archive.org/download/public-film/documentary.mp4"
    });
    expect(result.items[0].previewUrl).toContain("/services/img/public-film");
    expect(mock).toHaveBeenCalledTimes(3);
  });

  it("returns no Internet Archive playback URL when an item has no original video file", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      if (url.pathname === "/advancedsearch.php") return json({ response: { docs: [{ identifier: "no-video" }] } });
      return json({ metadata: { mediatype: "movies", title: "No video" }, files: [
        { name: "cover.jpg", format: "JPEG", size: "200", source: "original" },
        { name: "movie.mp4", format: "MPEG4", size: "200", source: "derivative" }
      ] });
    }));
    const result = await searchInternetArchiveVideos("no video");
    expect(result.items).toHaveLength(0);
    expect(result.status).toBe("not_found");
  });

  it("searches public Internet Archive audio and selects an original MP3 file", async () => {
    const mock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("archive.org");
      expect(new Headers(init?.headers).get("user-agent")).toContain("NolaneSearch");
      if (url.pathname === "/advancedsearch.php") {
        expect(url.searchParams.get("q")).toBe('title:"public lecture" AND mediatype:audio');
        expect(url.searchParams.getAll("fl[]")).toContain("identifier");
        expect(url.searchParams.get("rows")).toBe("2");
        return json({ response: { docs: [{ identifier: "audio-public" }, { identifier: "audio-private" }] } });
      }
      if (url.pathname === "/metadata/audio-public") {
        return json({ metadata: {
          mediatype: "audio", title: "A Public Lecture", year: "1998",
          creator: "Public University", licenseurl: "https://creativecommons.org/licenses/by/4.0/",
          description: "An <i>archived</i> public lecture"
        }, files: [
          { name: "lecture_meta.xml", format: "Metadata", size: "120", source: "original" },
          { name: "lecture_64kb.mp3", format: "VBR MP3", size: "450000", source: "derivative" },
          { name: "lecture.mp3", format: "MP3", size: "1800000", source: "original" },
          { name: "private.mp3", format: "MP3", size: "1800000", source: "original", private: "true" },
          { name: "transcript.pdf", format: "PDF", size: "12000", source: "original" }
        ] });
      }
      if (url.pathname === "/metadata/audio-private") {
        return json({ metadata: {
          mediatype: "audio", title: "Restricted Recording", "access-restricted-item": "true"
        }, files: [{ name: "restricted.mp3", format: "MP3", size: "1000", source: "original" }] });
      }
      throw new Error("Unexpected archive audio endpoint: " + url.pathname);
    });
    vi.stubGlobal("fetch", mock);
    const result = await searchInternetArchiveAudio("public lecture", 2);
    expect(result.items).toHaveLength(1);
    expect(result.items[0]).toMatchObject({
      provider: "Internet Archive",
      mediaType: "audio",
      title: "A Public Lecture",
      credit: "Public University",
      license: "Creative Commons (see item)",
      sourceUrl: "https://archive.org/details/audio-public",
      mediaUrl: "https://archive.org/download/audio-public/lecture.mp3"
    });
    expect(result.items[0].previewUrl).toContain("/services/img/audio-public");
    expect(mock).toHaveBeenCalledTimes(3);
  });

  it("does not return audio unless a non-private original audio file with a valid format exists", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      if (url.pathname === "/advancedsearch.php") return json({ response: { docs: [{ identifier: "audio-derivative-only" }] } });
      return json({ metadata: { mediatype: "audio", title: "Derivative Only" }, files: [
        { name: "only.mp3", format: "VBR MP3", size: "1200", source: "derivative" },
        { name: "unsafe.mp3", format: "MP3", size: "1200", source: "original", private: "true" },
        { name: "wrong.wav", format: "JPEG", size: "1200", source: "original" }
      ] });
    }));
    const result = await searchInternetArchiveAudio("derivative only");
    expect(result.items).toHaveLength(0);
    expect(result.status).toBe("not_found");
  });

  it("looks up food by barcode and returns bounded ingredients and nutrition", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("world.openfoodfacts.org");
      expect(url.pathname).toBe("/api/v3/product/3017620422003.json");
      expect(new Headers(init?.headers).get("user-agent")).toContain("NolaneSearch");
      return json({ status: 1, product: {
        product_name: "Example spread", brands: "Example", quantity: "400 g",
        ingredients_text: "Sugar, oil and cocoa.", allergens: "May contain milk.",
        nutriscore_grade: "e", nova_group: 4, ecoscore_grade: "c",
        nutriments: { "energy-kcal_100g": 539, fat_100g: 30, "saturated-fat_100g": 10, sugars_100g: 57, proteins_100g: 6 },
        image_front_url: "https://images.openfoodfacts.org/images/products/301/762/042/2003/front.jpg",
      } });
    }));
    const result = JSON.parse(await lookupFoodProduct("3017620422003"));
    expect(result.product.name).toBe("Example spread");
    expect(result.product.nutrition_per_100g.energy_kcal).toBe(539);
    expect(result.product.image_front_url).toContain("images.openfoodfacts.org");
  });

  it("rejects invalid food barcodes before network access", async () => {
    const mock = vi.fn();
    vi.stubGlobal("fetch", mock);
    await expect(lookupFoodProduct("abc-123")).rejects.toThrow("8 to 14 digits");
    expect(mock).not.toHaveBeenCalled();
  });

  it("rejects invalid media types and handles rate limits", async () => {
    const mock = vi.fn(async () => json({}, 429));
    vi.stubGlobal("fetch", mock);
    await expect(searchNasaMedia("space", "audio")).rejects.toThrow("media_type");
    await expect(searchNasaMedia("space", "video")).rejects.toThrow("rate-limiting");
  });

  it("exposes and dispatches all Wave 52 tools through the agent interface", async () => {
    const names = AGENT_TOOL_DEFINITIONS.map(tool => tool.function.name);
    expect(names).toEqual(expect.arrayContaining([
      "search_wikimedia_images", "search_nasa_media", "lookup_food_product", "search_openverse_images", "search_internet_archive_videos", "search_internet_archive_audio",
    ]));
    vi.stubGlobal("fetch", vi.fn(async () => json({ query: { pages: [{
      pageid: 8, title: "File:Dispatch.jpg",
      imageinfo: [{
        mime: "image/jpeg", url: "https://upload.wikimedia.org/a.jpg", thumburl: "https://upload.wikimedia.org/a.jpg",
        descriptionurl: "https://commons.wikimedia.org/wiki/File:Dispatch.jpg",
        extmetadata: { LicenseShortName: { value: "CC0" }, LicenseUrl: { value: "https://creativecommons.org/publicdomain/zero/1.0/" } },
      }],
    }] } })));
    const result = JSON.parse(await executeAgentTool(env, "search_wikimedia_images", { query: "sample image" }));
    expect(result.items[0].title).toBe("Dispatch.jpg");
  });
});
