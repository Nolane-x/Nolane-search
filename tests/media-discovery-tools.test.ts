import { afterEach, describe, expect, it, vi } from "vitest";
import { runMediaDiscoveryTool, searchNasaMedia, searchWikimediaImages, searchOpenverseImages, searchInternetArchiveVideos, searchInternetArchiveAudio, lookupFoodProduct, lookupConsumerProduct, compareFoodProducts } from "../src/media-discovery-tools";
import { executeAgentTool, AGENT_TOOL_DEFINITIONS } from "../src/agent-tools";
import type { Env } from "../src/types";

afterEach(() => vi.unstubAllGlobals());
const env = { DB: {} as never, SEARCH_JOBS: {} as never } as Env;
type Obj = Record<string, unknown>;
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
        { name: "wrong.wav", format: "JPEG", size: "1200", source: "original" },
        { name: "missing-source.mp3", format: "MP3", size: "1200" }
      ] });
    }));
    const result = await searchInternetArchiveAudio("derivative only");
    expect(result.items).toHaveLength(0);
    expect(result.status).toBe("not_found");
  });

  it("looks up food by barcode using the documented v3 string status and per-100-g data", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = new URL(String(input));
      expect(url.hostname).toBe("world.openfoodfacts.org");
      expect(url.pathname).toBe("/api/v3/product/3017620422003");
      expect(url.searchParams.get("product_type")).toBe("food");
      expect(url.searchParams.get("fields")).toContain("environmental_score_grade");
      expect(new Headers(init?.headers).get("user-agent")).toContain("NolaneSearch");
      expect(init?.redirect).toBe("manual");
      return json({ status: "success_with_warnings", product: {
        code: "3017620422003", product_type: "food",
        product_name: "Example spread", brands: "Example", quantity: "400 g",
        ingredients_text: "Sugar, oil and cocoa.", allergens: "May contain milk.",
        nutriscore_grade: "e", nova_group: 4, environmental_score_grade: "c",
        nutrition: { aggregated_set: {
          per: "100g",
          nutrients: {
            "energy-kcal": { value: 539, unit: "kcal" },
            fat: { value: 30, unit: "g" },
            "saturated-fat": { value: 10, unit: "g" },
            sugars: { value: 57, unit: "g" },
            proteins: { value: 6, unit: "g" }
          }
        } },
        image_front_url: "https://images.openfoodfacts.org/images/products/301/762/042/2003/front.jpg",
      } });
    }));
    const result = JSON.parse(await lookupFoodProduct("3017620422003"));
    expect(result.status).toBe("ok");
    expect(result.product.name).toBe("Example spread");
    expect(result.product.nutrition_per_100g.energy_kcal).toBe(539);
    expect(result.product.environmental_score_grade).toBe("c");
    expect(result.product.image_front_url).toContain("images.openfoodfacts.org");
  });

  it("automatically follows one validated redirect to Open Beauty Facts", async () => {
    const barcode = "8710447445990";
    const calls: string[] = [];
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      calls.push(url.hostname + url.pathname);
      if (url.hostname === "world.openfoodfacts.org") {
        expect(url.searchParams.get("product_type")).toBe("all");
        return new Response(null, { status: 302, headers: {
          location: "https://world.openbeautyfacts.org/api/v3/product/" + barcode
        }});
      }
      expect(url.hostname).toBe("world.openbeautyfacts.org");
      expect(url.searchParams.get("product_type")).toBe("all");
      return json({ status: "success", product: {
        code: barcode, product_type: "beauty", product_name: "Example shampoo",
        brands: "Example Beauty", categories: "Hair care",
        image_front_url: "https://images.openbeautyfacts.org/images/products/871/044/744/5990/front.jpg"
      } });
    }));
    const result = JSON.parse(await lookupConsumerProduct(barcode));
    expect(result.status).toBe("ok");
    expect(result.source).toBe("Open Beauty Facts");
    expect(result.product.product_type).toBe("beauty");
    expect(result.product.nutrition_per_100g.energy_kcal).toBeNull();
    expect(result.product.source_url).toBe("https://world.openbeautyfacts.org/product/" + barcode);
    expect(calls).toEqual([
      "world.openfoodfacts.org/api/v3/product/" + barcode,
      "world.openbeautyfacts.org/api/v3/product/" + barcode
    ]);
  });

  it("supports direct lookup in pet-food and general consumer-product catalogs", async () => {
    const results = [
      { type: "petfood", host: "world.openpetfoodfacts.org", name: "Example dog food" },
      { type: "product", host: "world.openproductsfacts.org", name: "Example household item" }
    ];
    let call = 0;
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const expected = results[call++];
      const url = new URL(String(input));
      expect(url.hostname).toBe(expected.host);
      expect(url.searchParams.get("product_type")).toBe(expected.type);
      return json({ status: "success", product: {
        product_type: expected.type, product_name: expected.name
      } });
    }));
    const pet = JSON.parse(await lookupConsumerProduct("12345678", "petfood"));
    const item = JSON.parse(await lookupConsumerProduct("12345679", "product"));
    expect(pet.product.product_type).toBe("petfood");
    expect(pet.product.name).toBe("Example dog food");
    expect(item.product.product_type).toBe("product");
    expect(item.product.name).toBe("Example household item");
    expect(call).toBe(2);
  });

  it("rejects redirects outside the approved Open Facts hosts", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => new Response(null, {
      status: 302,
      headers: { location: "https://evil.example/api/v3/product/3017620422003" }
    })));
    await expect(lookupConsumerProduct("3017620422003")).rejects.toThrow("outside the approved Open Facts databases");
  });

  it("returns not_found for HTTP 404 and accepts legacy numeric v3 status during migration", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      if (url.pathname.endsWith("/3017620422003")) return json({}, 404);
      return json({ status: 1, product: {
        code: "3017620422004", product_name: "Legacy-shaped product", product_type: "food"
      } });
    }));
    const missing = JSON.parse(await lookupConsumerProduct("3017620422003", "food"));
    const legacy = JSON.parse(await lookupFoodProduct("3017620422004"));
    expect(missing.status).toBe("not_found");
    expect(legacy.status).toBe("ok");
    expect(legacy.product.name).toBe("Legacy-shaped product");
  });

  it("does not label per-100-ml data as per-100-g nutrition", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => json({ status: "success", product: {
      code: "3017620422003", product_type: "food",
      product_name: "Beverage", nutrition: { aggregated_set: {
        per: "100ml", nutrients: { "energy-kcal": { value: 42, unit: "kcal" } }
      } }
    } })));
    const result = JSON.parse(await lookupFoodProduct("3017620422003"));
    expect(result.product.nutrition_reference).toBe("100ml");
    expect(result.product.nutrition_per_100g.energy_kcal).toBeNull();
  });

  it("compares two to four food barcodes using per-100-g values without inventing missing data", async () => {
    const records: Record<string, Obj> = {
      "3017620422003": {
        code: "3017620422003", product_type: "food", product_name: "Spread A",
        nutrition: { aggregated_set: { per: "100g", nutrients: {
          "energy-kcal": { value: 500 }, sugars: { value: 45 }, proteins: { value: 7 }
        } } }
      },
      "5000159484695": {
        code: "5000159484695", product_type: "food", product_name: "Spread B",
        nutrition: { aggregated_set: { per: "100g", nutrients: {
          "energy-kcal": { value: 400 }, sugars: { value: 20 }, proteins: { value: 8 }
        } } }
      },
      "5449000000996": {
        code: "5449000000996", product_type: "food", product_name: "Drink C",
        nutrition: { aggregated_set: { per: "100g", nutrients: {
          "energy-kcal": { value: 5 }, sugars: { value: 0 }
        } } }
      }
    };
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      const barcode = url.pathname.split("/").pop() || "";
      expect(url.hostname).toBe("world.openfoodfacts.org");
      expect(url.searchParams.get("product_type")).toBe("food");
      return records[barcode] ? json({ status: "success", product: records[barcode] }) : json({}, 404);
    }));
    const result = JSON.parse(await compareFoodProducts(["3017620422003","5000159484695","5449000000996"]));
    expect(result.status).toBe("ok");
    expect(result.products).toHaveLength(3);
    expect(result.comparisons.find((entry: Obj) => entry.metric === "Energy")).toMatchObject({
      minimum: { barcode: "5449000000996", value: 5 },
      maximum: { barcode: "3017620422003", value: 500 }
    });
    expect(result.comparisons.find((entry: Obj) => entry.metric === "Protein").values).toHaveLength(2);
    expect(result.comparison_basis).toContain("not a health ranking");
  });

  it("does not compare a product redirected to a non-food database", async () => {
    const beautyBarcode = "8710447445990";
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      const barcode = url.pathname.split("/").pop() || "";
      if (barcode === beautyBarcode && url.hostname === "world.openfoodfacts.org") {
        return new Response(null, { status: 302, headers: {
          location: "https://world.openbeautyfacts.org/api/v3/product/" + beautyBarcode
        }});
      }
      if (url.hostname === "world.openbeautyfacts.org") {
        return json({ status: "success", product: {
          code: beautyBarcode, product_type: "beauty", product_name: "Beauty item",
          nutrition: { aggregated_set: { per: "100g", nutrients: { sugars: { value: 10 } } } }
        } });
      }
      return json({ status: "success", product: {
        code: barcode, product_type: "food", product_name: "Food item",
        nutrition: { aggregated_set: { per: "100g", nutrients: { sugars: { value: 5 } } } }
      } });
    }));
    const result = JSON.parse(await compareFoodProducts(["3017620422003",beautyBarcode]));
    expect(result.status).toBe("insufficient_data");
    expect(result.products[1].product).toMatchObject({
      not_found: true, reason: "not_a_food_product"
    });
    expect(result.comparisons).toHaveLength(0);
  });

  it("validates food-comparison input bounds and uniqueness before network access", async () => {
    const mock = vi.fn();
    vi.stubGlobal("fetch", mock);
    await expect(compareFoodProducts(["3017620422003"])).rejects.toThrow("between 2 and 4");
    await expect(compareFoodProducts(["3017620422003","3017620422003"])).rejects.toThrow("unique");
    await expect(compareFoodProducts(["3017620422003","12345678","123456789012345"])).rejects.toThrow("8 to 14 digits");
    await expect(lookupConsumerProduct("../../etc/passwd")).rejects.toThrow("8 to 14 digits");
    await expect(lookupConsumerProduct("3017620422003","unknown")).rejects.toThrow("product_type");
    expect(mock).not.toHaveBeenCalled();
  });

  it("dispatches Internet Archive audio search through the model tool interface", async () => {
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      if (url.pathname === "/advancedsearch.php") {
        expect(url.searchParams.get("q")).toBe('title:"field recording" AND mediatype:audio');
        return json({ response: { docs: [{ identifier: "field-recording" }] } });
      }
      expect(url.pathname).toBe("/metadata/field-recording");
      return json({ metadata: { mediatype: "audio", title: "Field Recording" }, files: [
        { name: "field.mp3", format: "MP3", size: "1000", source: "original" }
      ] });
    }));
    const result = JSON.parse(await executeAgentTool(env, "search_internet_archive_audio", { query: "field recording" }));
    expect(result.items[0]).toMatchObject({ title: "Field Recording", mediaType: "audio" });
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
