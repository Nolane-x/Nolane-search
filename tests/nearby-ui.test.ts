import { describe, expect, it } from "vitest";
import { nearbyAppResponse } from "../src/nearby-ui";

describe("Nearby Places UI", () => {
  it("serves a responsive no-store page with same-origin API and OpenStreetMap attribution", async () => {
    const response = nearbyAppResponse();
    const html = await response.text();
    const csp = response.headers.get("content-security-policy") || "";
    expect(response.status).toBe(200);
    expect(response.headers.get("content-type")).toContain("text/html");
    expect(response.headers.get("cache-control")).toContain("no-store");
    expect(response.headers.get("x-content-type-options")).toBe("nosniff");
    expect(csp).toContain("connect-src 'self'");
    expect(csp).toContain("frame-ancestors 'none'");
    expect(csp).toContain("https://unpkg.com");
    expect(csp).toContain("https://tile.openstreetmap.org");
    expect(csp).toContain("https://router.project-osrm.org");
    expect(csp).toContain("https://routing.openstreetmap.de");
    expect(response.headers.get("referrer-policy")).toBe("strict-origin-when-cross-origin");
    expect(html).toContain("leaflet@1.9.4/dist/leaflet.css");
    expect(html).toContain("leaflet@1.9.4/dist/leaflet.js");
    expect(html).toContain("id=\"routeMap\"");
    expect(html).toContain("id=\"routeProfile\"");
    expect(html).toContain("id=\"routeButton\"");
    expect(html).toContain("routeProfileValue()");
    expect(html).toContain("https://router.project-osrm.org/route/v1/driving/");
    expect(html).toContain("https://routing.openstreetmap.de/routed-bike/route/v1/bike/");
    expect(html).toContain("https://routing.openstreetmap.de/routed-foot/route/v1/foot/");
    expect(html).toContain("nhà cung cấp có thể ghi log yêu cầu");
    expect(html).toContain("Bản đồ chỉ tải sau khi bạn chủ động bấm");
    expect(html).toContain("khu vực đang xem qua yêu cầu các ô bản đồ");
    expect(html).toContain("var ROUTE_MAX_STOPS=10;");
    expect(html).toContain("function reserveRouteRequestTime(now)");
    expect(html).toContain("localStorage.setItem(ROUTE_COOLDOWN_KEY,String(now))");
    expect(html).toContain("routeRequestInFlight");
    expect(html).toContain("data.code!=='Ok'");
    expect(html).toContain("route.geometry.type!=='LineString'");
    expect(html).toContain("OpenStreetMap contributors");
    expect(html).toContain("ODbL");
    expect(html).toContain("/api/nearby/search");
    expect(html).toContain("tọa độ tìm kiếm chỉ được gửi");
    expect(html).toContain("Dùng vị trí hiện tại");
    expect(html).toContain('<option value="essentials">Tiện ích thiết yếu (nhiều nhóm)</option>');
    expect(html).toContain("function syncEssentialsRadius()");
    expect(html).toContain("if(five)five.disabled=essentials;");
    expect(html).toContain("if(essentials&&$('radius').value==='5000')$('radius').value='3000';");
    expect(html).toContain("Địa điểm quanh đây");
    expect(html).toContain("Địa điểm yêu thích chỉ được lưu trên trình duyệt này");
    expect(html).toContain("var STORAGE_KEY='nolane.nearby.saved-places.v1';");
    expect(html).toContain("var MAX_SAVED=50;");
    expect(html).toContain("localStorage.setItem(STORAGE_KEY,JSON.stringify(next))");
    expect(html).toContain("function cleanSavedPlace(raw)");
    expect(html).toContain("typeof latitude!=='number'");
    expect(html).toContain("slice(0,MAX_SAVED)");
    expect(html).toContain("function moveSavedPlace(index,delta)");
    expect(html).toContain("function exportSavedPlaces()");
    expect(html).toContain("application/gpx+xml;charset=utf-8");
    expect(html).toContain('<rtept lat="');
    expect(html).toContain("chưa phải tuyến đường được tối ưu");
    expect(html).not.toContain("/api/nearby/saved");
  });

  it("only requests browser geolocation from an explicit user click", async () => {
    const html = await (await nearbyAppResponse()).text();
    expect(html).toContain("$('locate').addEventListener('click',function(){");
    expect(html).toContain("navigator.geolocation.getCurrentPosition");
    expect(html).toContain("Hãy nhập tọa độ thủ công");
    expect(html).toContain("maximumAge:60000");
    expect(html).toContain("timeout:15000");
    const start = html.indexOf("<script>");
    const end = html.indexOf("</script>", start);
    expect(start).toBeGreaterThanOrEqual(0);
    expect(end).toBeGreaterThan(start);
    expect(() => new Function(html.slice(start + "<script>".length, end))).not.toThrow();
  });

  it("keeps result links constrained to HTTPS", async () => {
    const html = await (await nearbyAppResponse()).text();
    expect(html).toContain("url.protocol==='https:'");
    expect(html).toContain("noopener noreferrer");
    expect(html).toContain("Chưa xác nhận đang mở");
  });
});


class NearbyTestElement {
  children: NearbyTestElement[] = [];
  listeners: Record<string, (event?: unknown) => unknown> = {};
  attributes: Record<string, string> = {};
  classList = { toggle: () => undefined, add: () => undefined, remove: () => undefined };
  value = "";
  disabled = false;
  href = "";
  target = "";
  rel = "";
  download = "";
  textContent = "";
  innerHTML = "";
  style: Record<string, string> = {};
  constructor(readonly id = "") {}
  appendChild(child: NearbyTestElement) { this.children.push(child); return child; }
  replaceChildren() { this.children = []; }
  addEventListener(name: string, callback: (event?: unknown) => unknown) { this.listeners[name] = callback; }
  setAttribute(name: string, value: string) { this.attributes[name] = value; }
  getAttribute(name: string) { return this.attributes[name] || null; }
  querySelector() { return new NearbyTestElement(); }
  remove() { /* no-op DOM shim */ }
  click() { return this.listeners.click?.(); }
}

async function mountNearbyBrowser(routeResponse: unknown, savedPlacesInput?: Array<Record<string, unknown>>, sharedStorage?: Map<string, string>) {
  const elements = new Map<string, NearbyTestElement>();
  const documentMock = {
    getElementById(id: string) {
      if (!elements.has(id)) elements.set(id, new NearbyTestElement(id));
      return elements.get(id)!;
    },
    createElement(tag: string) { return new NearbyTestElement(tag); },
    querySelectorAll() { return []; },
    body: new NearbyTestElement("body"),
  };
  ["routeProfile", "routeButton", "routeStatus", "routeSummary", "routeMap", "routeMapPlaceholder", "routeLegs", "exportGpx", "savedPlaces", "savedCount", "status", "results", "resultCount", "category", "radius", "latitude", "longitude", "locate", "search"].forEach(id => documentMock.getElementById(id));
  documentMock.getElementById("routeProfile").value = "driving";
  const seed = savedPlacesInput || [
    { id: "node/501", name: "Điểm A", category: "food", categoryLabel: "Ăn uống", latitude: 20.8449, longitude: 106.6881, address: "Hải Phòng" },
    { id: "way/502", name: "Điểm B", category: "shopping", categoryLabel: "Mua sắm", latitude: 20.8460, longitude: 106.6890, address: "Hải Phòng" },
  ];
  const storage = sharedStorage || new Map([["nolane.nearby.saved-places.v1", JSON.stringify(seed)]]);
  const localStorageMock = {
    getItem(key: string) { return storage.get(key) || null; },
    setItem(key: string, value: string) { storage.set(key, value); },
  };
  const layers: Array<{ data?: unknown; bounds?: unknown }> = [];
  const tileCalls: string[] = [];
  const makeLayer = (data?: unknown) => ({
    data,
    addTo() { layers.push({ data }); return this; },
    bindTooltip() { return this; },
    getBounds() { return { isValid: () => true }; },
    clearLayers() { layers.length = 0; },
    addLayer(layer: unknown) { layers.push({ data: (layer as { data?: unknown } | null)?.data }); return this; },
  });
  const leaflet = {
    map() {
      return {
        setView() { return this; },
        addLayer() { return this; },
        fitBounds() { return this; },
        invalidateSize() { return this; },
      };
    },
    tileLayer(url: string) { tileCalls.push(url); return makeLayer(); },
    layerGroup() { return makeLayer(); },
    circleMarker() { return makeLayer(); },
    marker() { return makeLayer(); },
    geoJSON(data: unknown) { return makeLayer(data); },
    latLngBounds() { return { isValid: () => true }; },
    divIcon(options: unknown) { return options; },
  };
  const calls: Array<{ url: string; init?: RequestInit }> = [];
  const fetchMock = async (input: RequestInfo | URL, init?: RequestInit) => {
    calls.push({ url: String(input), init });
    return new Response(JSON.stringify(routeResponse), {
      status: 200,
      headers: { "content-type": "application/json" },
    });
  };
  const html = await (await nearbyAppResponse()).text();
  const start = html.indexOf("<script>");
  const end = html.indexOf("</script>", start);
  const script = html.slice(start + "<script>".length, end);
  const windowMock = { setTimeout: () => 0 };
  const urlMock = { createObjectURL: () => "blob:test", revokeObjectURL: () => undefined };
  new Function("document", "localStorage", "window", "URL", "Blob", "navigator", "fetch", "L", script)(
    documentMock, localStorageMock, windowMock, urlMock, class TestBlob {}, {}, fetchMock, leaflet,
  );
  return { elements, calls, layers, tileCalls, html, storage };
}

describe("Nearby Places routed itinerary", () => {
  const routeFixture = {
    code: "Ok",
    waypoints: [
      { name: "Start street", location: [106.6881, 20.8449], distance: 1 },
      { name: "End street", location: [106.6890, 20.8460], distance: 2 },
    ],
    routes: [{
      distance: 1250,
      duration: 420,
      geometry: {
        type: "LineString",
        coordinates: [[106.6881, 20.8449], [106.6885, 20.8454], [106.6890, 20.8460]],
      },
      legs: [{ distance: 1250, duration: 420, steps: [] }],
    }],
  };

  it("requests a driving route only after an explicit click and renders real distance and duration", async () => {
    const mounted = await mountNearbyBrowser(routeFixture);
    expect(mounted.calls).toHaveLength(0);
    expect(mounted.tileCalls).toHaveLength(0);
    const routeButton = mounted.elements.get("routeButton");
    expect(routeButton).toBeDefined();
    await routeButton!.click();
    expect(mounted.calls).toHaveLength(1);
    expect(mounted.tileCalls).toEqual(["https://tile.openstreetmap.org/{z}/{x}/{y}.png"]);
    expect(mounted.calls[0].url).toContain("https://router.project-osrm.org/route/v1/driving/106.68810,20.84490;106.68900,20.84600");
    expect(mounted.calls[0].url).toContain("geometries=geojson");
    expect(mounted.elements.get("routeSummary")?.textContent).toContain("1.25 km");
    expect(mounted.elements.get("routeSummary")?.textContent).toContain("7 phút");
    expect(mounted.layers.some(layer => (layer.data as { geometry?: { type?: string } } | undefined)?.geometry?.type === "LineString")).toBe(true);
  });

  it("uses the dedicated foot and bicycle profile endpoints rather than the car profile", async () => {
    const foot = await mountNearbyBrowser(routeFixture);
    foot.elements.get("routeProfile")!.value = "walking";
    await foot.elements.get("routeButton")!.click();
    expect(foot.calls[0].url).toContain("https://routing.openstreetmap.de/routed-foot/route/v1/foot/");
    expect(foot.elements.get("routeSummary")?.textContent).toContain("1.25 km");

    const bike = await mountNearbyBrowser(routeFixture);
    bike.elements.get("routeProfile")!.value = "cycling";
    await bike.elements.get("routeButton")!.click();
    expect(bike.calls[0].url).toContain("https://routing.openstreetmap.de/routed-bike/route/v1/bike/");
    expect(bike.elements.get("routeSummary")?.textContent).toContain("1.25 km");
  });

  it("blocks a rapid repeat route request in the same page instance", async () => {
    const mounted = await mountNearbyBrowser(routeFixture);
    await mounted.elements.get("routeButton")!.click();
    await mounted.elements.get("routeButton")!.click();
    expect(mounted.calls).toHaveLength(1);
    expect(mounted.elements.get("routeStatus")?.textContent).toContain("chờ");
  });

  it("shares the routing cooldown across page loads without storing route coordinates", async () => {
    const first = await mountNearbyBrowser(routeFixture);
    await first.elements.get("routeButton")!.click();
    expect(first.storage.has("nolane.nearby.route-last-request-at.v1")).toBe(true);
    const storedCooldown = first.storage.get("nolane.nearby.route-last-request-at.v1") || "";
    expect(Number.isFinite(Number(storedCooldown))).toBe(true);
    expect(storedCooldown).not.toContain("106.");
    const second = await mountNearbyBrowser(routeFixture, undefined, first.storage);
    await second.elements.get("routeButton")!.click();
    expect(second.calls).toHaveLength(0);
    expect(second.elements.get("routeStatus")?.textContent).toContain("chờ");
  });

  it("shows a safe no-route message instead of drawing an invalid result", async () => {
    const mounted = await mountNearbyBrowser({ code: "NoRoute", routes: [], waypoints: [] });
    await mounted.elements.get("routeButton")!.click();
    expect(mounted.elements.get("routeStatus")?.textContent).toContain("Không tìm được đường");
    expect(mounted.elements.get("routeSummary")?.textContent).toBe("");
    expect(mounted.layers.some(layer => (layer.data as { geometry?: { type?: string } } | undefined)?.geometry?.type === "LineString")).toBe(false);
  });

  it("rejects malformed route geometry without drawing a polyline", async () => {
    const malformed = {
      code: "Ok",
      waypoints: [
        { name: "Start", location: [106.6881, 20.8449], distance: 0 },
        { name: "End", location: [106.6890, 20.8460], distance: 0 },
      ],
      routes: [{
        distance: 1000,
        duration: 300,
        geometry: { type: "MultiLineString", coordinates: [[[106.6881, 20.8449]]] },
        legs: [{ distance: 1000, duration: 300, steps: [] }],
      }],
    };
    const mounted = await mountNearbyBrowser(malformed);
    await mounted.elements.get("routeButton")!.click();
    expect(mounted.elements.get("routeStatus")?.textContent).toContain("Hình dạng tuyến đường không hợp lệ");
    expect(mounted.elements.get("routeSummary")?.textContent).toBe("");
    expect(mounted.layers.some(layer => (layer.data as { geometry?: { type?: string } } | undefined)?.geometry?.type === "MultiLineString")).toBe(false);
  });

  it("routes only the first ten saved places in their original order", async () => {
    const manyStops = Array.from({ length: 12 }, (_, index) => ({
      id: "node/" + (700 + index),
      name: "Điểm " + (index + 1),
      category: "food",
      categoryLabel: "Ăn uống",
      latitude: 20.8000 + index / 1000,
      longitude: 106.6000 + index / 1000,
    }));
    const tenStopResponse = {
      code: "Ok",
      waypoints: Array.from({ length: 10 }, () => ({ name: "", location: [106.6, 20.8], distance: 0 })),
      routes: [{
        distance: 9000, duration: 3600,
        geometry: { type: "LineString", coordinates: [[106.6, 20.8], [106.61, 20.81]] },
        legs: Array.from({ length: 9 }, () => ({ distance: 1000, duration: 400, steps: [] })),
      }],
    };
    const mounted = await mountNearbyBrowser(tenStopResponse, manyStops);
    await mounted.elements.get("routeButton")!.click();
    const requestedUrl = mounted.calls[0].url;
    expect(requestedUrl).toContain("106.60000,20.80000;106.60100,20.80100");
    expect(requestedUrl).toContain("106.60900,20.80900");
    expect(requestedUrl).not.toContain("106.61000,20.81000");
    expect(mounted.elements.get("routeStatus")?.textContent).toContain("Đã dùng 10 điểm đầu");
  });

});
