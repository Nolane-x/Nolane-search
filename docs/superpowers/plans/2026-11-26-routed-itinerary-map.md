# Wave 71 Routed Itinerary Map Implementation Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Add an interactive driving/cycling/walking route map for up to 10 manually ordered locally saved places, with real route geometry and distance/time summaries.

**Architecture:** Extend the existing private Nearby HTML page with Leaflet and fixed browser-side OSRM/FOSSGIS endpoints. Reuse Wave 70's locally validated saved-place data; route only on explicit user action, render GeoJSON geometry and leg metrics, and keep route state transient.

**Tech Stack:** TypeScript Worker template HTML, inline browser JavaScript, Leaflet 1.9.4, OpenStreetMap tiles, OSRM HTTP Route API, Vitest.

**Spec:** docs/superpowers/specs/2026-11-26-wave-71-routed-itinerary-map-design.md

## Global Constraints

- Public routing endpoint use: no more than 1 request per second; one route request at a time; maximum 10 waypoints; low-volume personal use only; no SLA.
- Do not fetch user-provided route URLs; use only the three fixed profile endpoints in the spec.
- Do not auto-route on load, mode change, place reorder, or save/delete; a human click is required.
- Preserve the saved list's exact order. Do not optimize or reverse stops.
- Tile requests are viewport-driven only. No bulk, offline or prefetch requests; respect provider caching.
- Attribution remains visible: © OpenStreetMap contributors. Keep correct Referer behavior using strict-origin-when-cross-origin.
- Routing provider disclosure: coordinates are sent directly to that provider and route requests may be logged there.
- Never persist route geometry, route requests, search center or favorites to server/D1; Wave 70 favorite localStorage behavior remains unchanged. A timestamp-only local cooldown key may be written to prevent reloads/tabs from violating the shared provider rate limit.
- Do not claim live traffic, real navigation instructions, road-distance guarantee or ETA accuracy beyond the provider's route profile estimate.

## Files

- Modify src/nearby-ui.ts: map markup, CSP/referrer policy, static route profile mapping, route request, response validation, rendering and user-facing disclosures.
- Modify tests/nearby-ui.test.ts: acceptance assertions for map/CSP/providers, click-only behavior, rate guard, bounded stop count, route validation and no-route boundaries.
- Create docs/superpowers/specs/2026-11-26-wave-71-routed-itinerary-map-design.md: durable design decision.
- Create docs/superpowers/plans/2026-11-26-routed-itinerary-map.md: this implementation plan.

## Review Focus

- Restored localStorage contains malformed coordinates or an unsupported OSM ID; route builder must use only Wave70-validated records.
- Provider returns NoRoute, NoSegment, non-Ok code, malformed JSON, wrong geometry type, non-finite coordinates, too many geometry points, or inconsistent legs; UI must show safe errors without drawing a broken line.
- Saved list has 0, 1, 10, 11, or 50 items; the first 10 only must be routed, in exact order.
- Leaflet script or CSS fails to load; saved places and GPX functions must remain usable and the page must remain operable.
- User changes mode or saved-place order while a route request is pending; stale results must not overwrite the newer itinerary.
- Repeated clicks during an active request or within 1.1 seconds must not create parallel or excessive route calls.

---

### Task 1: Test route map contract and provider boundaries

**Files:**
- Modify: tests/nearby-ui.test.ts

**Interfaces:**
- Consumes current nearbyAppResponse(): Response and the rendered HTML template contract.
- Produces test expectations that pin map markup, Leaflet version/SRI, fixed routing profiles, privacy disclosure, route click-only behavior, rate guard, 10-stop cap, response validation and existing Wave70 behavior.

- [x] **Step 1: Add failing UI assertions first**
  - Assert response referrer-policy equals strict-origin-when-cross-origin.
  - Assert CSP allows https://unpkg.com, https://tile.openstreetmap.org, https://router.project-osrm.org and https://routing.openstreetmap.de only in their respective directives, while preserving frame-ancestors 'none'.
  - Assert markup includes a map container, profile selector values driving, cycling, walking, a manual route button and visible OSM attribution.
  - Assert static endpoint strings map driving to router.project-osrm.org/route/v1/driving, cycling to routing.openstreetmap.de/routed-bike/route/v1/bike, and walking to routing.openstreetmap.de/routed-foot/route/v1/foot.
  - Assert UI discloses direct transfer of stop coordinates and provider-side route logging.
  - Execute the inline script in a browser shim and assert no route or tile request occurs at page load; the map tile request starts only after the explicit route click.
  - Assert code includes an explicit click listener, a 1,100 ms cooldown, one in-flight request guard and a 10-stop route cap.
  - Assert response validation covers code === "Ok", LineString, bounded finite coordinates and consistent legs.
  - Keep existing Wave68/69/70 assertions intact.
- [x] **Step 2: Run the focused test and verify RED**
  - Run: npm test -- tests/nearby-ui.test.ts
  - Expected: failure because the map, route controls, endpoint mappings and headers are not implemented yet (not a parse error).
- [x] **Step 3: Commit the failing contract test**
  - Commit message: test(nearby): define Wave 71 routed itinerary contract

### Task 2: Implement map and route workflow

**Files:**
- Modify: src/nearby-ui.ts
- Test: tests/nearby-ui.test.ts

**Interfaces:**
- Consumes: Wave70 savedPlaces entries with id, name, latitude, longitude, categoryLabel, address; existing renderSavedPlaces(), setStatus(), nearbyAppResponse().
- Produces: ensureRouteMap(), refreshRouteStops(), requestSavedPlacesRoute(), validateRoutePayload(), buildRouteUrl(), drawComputedRoute() and renderRouteMetrics() inside the page script; static page-level CSP/referrer behavior.

- [x] **Step 1: Add the Leaflet map surface**
  - Add Leaflet 1.9.4 CSS and JS with pinned SRI/crossorigin. Keep the map panel useful if the script fails to load.
  - Add the OSM tile layer with visible attribution and a link to OSM copyright/fix map. Do not initialize Leaflet or fetch tiles on page load; initialize only after the explicit route click.
- [x] **Step 2: Add fixed route profiles and request controls**
  - Add profile select (driving default, cycling, walking), manual route button and explicit provider-logging/privacy note.
  - Build URL only from the profile allowlist and validated saved POI numeric coordinates in lon,lat order.
  - Request geometries=geojson&overview=full&steps=false&alternatives=false.
  - Route only the first 10 saved entries; show an explicit notice when entries are omitted.
- [x] **Step 3: Add throttling and request-state safeguards**
  - Block concurrent route requests and enforce 1,100 ms minimum spacing between provider calls, with a timestamp-only localStorage key shared across page loads/tabs.
  - Initialize/refresh the map first after the user's click, then capture the final itinerary signature and revision immediately before fetch. Ignore stale responses if profile or itinerary changed while the request was pending.
  - No auto-retry, no background call, and no route call from initialization.
- [x] **Step 4: Validate and display route**
  - Validate response code, route metrics, geometry type/coordinates/point cap, route legs and waypoint count.
  - Draw route and numbered markers; fit bounds without assuming Leaflet succeeded.
  - Show total km and estimated minutes plus per-leg km/minute summaries using safe DOM text.
  - Clearly say this is not live traffic and public providers may log routes.
- [x] **Step 5: Update page CSP and Referer behavior**
  - Add only required external hosts to script/style/img/connect-src.
  - Set referrer-policy: strict-origin-when-cross-origin to provide OSM tiles a valid origin Referer without full page path.
- [x] **Step 6: Run focused test and verify GREEN**
  - Run: npm test -- tests/nearby-ui.test.ts
  - Expected: every route-map and Wave70 UI contract assertion passes; inline script passes new Function parsing.
- [x] **Step 7: Run all tests and typecheck**
  - Run: npm run typecheck && npm test
  - Expected: TypeScript succeeds; every Vitest test file and test passes.
- [x] **Step 8: Commit implementation**
  - Commit message: feat(nearby): add routed itinerary map

### Task 3: Document provider policy and release evidence

**Files:**
- Create: docs/TOOL-RESEARCH-2026-11-26-WAVE71-ROUTED-ITINERARY.md
- Create: docs/HANDOFF-WAVE-SEVENTY-ONE-2026-11-26.md

**Interfaces:**
- Consumes: route endpoints, their profile semantics, rate limits, OSM attribution/tile policy and implementation behavior.
- Produces: a user-facing repo handoff plus a durable provider-policy note; no runtime configuration changes.

- [x] **Step 1: Document provider terms**
  - State the one request/second maximum, no-SLA/best-effort boundary, route request logging, attribution and valid Referer requirements, map lazy-load behavior, and no offline/prefetch/bulk tiles.
  - State that route duration is profile estimate, not live traffic.
- [x] **Step 2: Document actual implementation and limitations**
  - Record 10-waypoint route cap, first-10 ordering rule, profile endpoint map, no server-side route/favorite persistence, and CDN/tile dependencies.
- [x] **Step 3: Commit docs**
  - Commit message: docs: add Wave 71 routing policy and handoff

## Release verification

Before merge:
- npm run typecheck
- npm test
- Full GitHub Actions CI: TypeScript, Vitest, deployment scripts, Python runner tests and Worker build.
- Self-review final branch diff for CSP source scope, static URL allowlist, localStorage data validation, no request fan-out and no routing before click.

After merge:
- Main CI success.
- Worker deploy and Worker export success.
- Production Telegram Workspace/Nearby smoke verifies auth boundaries.
- Report clearly that automated production smoke does not validate public OSRM/FOSSGIS provider uptime or every Leaflet tile request.
