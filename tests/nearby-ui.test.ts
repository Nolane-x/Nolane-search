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
    expect(html).toContain("typeof raw.latitude!=='number'");
    expect(html).toContain("slice(0,MAX_SAVED)");
    expect(html).toContain("function moveSavedPlace(index,delta)");
    expect(html).toContain("function exportSavedPlaces()");
    expect(html).toContain("application/gpx+xml;charset=utf-8");
    expect(html).toContain("<rtept lat=\\\"");
    expect(html).toContain("không chứa tuyến đường được tối ưu");
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
