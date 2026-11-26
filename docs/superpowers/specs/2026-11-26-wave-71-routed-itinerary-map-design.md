# Wave 71 — Routed Itinerary Map Design

Date: 2026-11-26
Status: implementation design for the existing private Nearby Places page

## Intent

Turn the Wave 70 manually ordered saved-place list into a useful map itinerary. A user should be able to see selected stops on a map, request a real road/path route in the order already chosen, and inspect total distance, estimated duration, and each leg between stops.

The feature is for the existing single-owner, low-volume workspace. It must not turn shared public routing or tile services into a high-volume backend.

## Existing behavior and constraints

- /nearby is an owner-session-only HTML page served by nearbyAppResponse() in src/nearby-ui.ts.
- Search coordinates are user-entered or obtained only after an explicit geolocation click. Nearby search calls public Overpass from the Worker and does not store the search center.
- Wave 70 saves only explicitly selected POI data (name, category, address, coordinates) to versioned localStorage. It is browser/device local, capped at 50; there is no favorites API or D1 row.
- Saved places are manually ordered and can be exported as GPX. The order is not currently a computed route.
- src/nearby-ui.ts serves a self-contained HTML template with inline JavaScript and a restrictive CSP. Tests assert the inline script parses.
- This is a Cloudflare Worker + inline UI project; no Leaflet or routing dependency is installed.
- Public OSRM/FOSSGIS routing endpoints and OSM tiles are community services. Routing is best-effort, no SLA, at most one route request per second, and may log requested routes. OSM tile policy requires correct attribution, a valid browser Referer and normal interactive-use caching; no bulk/offline/prefetch use.

## Goals

- Add an interactive Leaflet map to Nearby Places using standard OpenStreetMap raster tiles and visible attribution.
- Plot numbered markers for the first 10 saved places in the user's exact manually chosen order.
- Provide three explicitly named travel profiles: driving, cycling, and walking. Use the matching public OSRM/FOSSGIS route profile endpoints rather than pretending one profile serves all modes.
- On an explicit Tính tuyến đường action, request a real route for the selected profile and selected stops.
- Draw returned GeoJSON route on the map and fit the viewport.
- Show total distance and estimated duration plus a leg-by-leg breakdown between consecutive saved stops.
- Handle fewer than two stops, more than 10 saved places, provider errors, NoRoute/NoSegment, malformed provider payloads, rate-limit cooldown, and Leaflet load failure clearly.
- Keep favorites and route-result state local to the current page/browser. No new D1 schema, favorites API, server route proxy, or account sync.
- Keep the existing list cap at 50; routing consumes only the first 10 positions in the user's saved order and discloses this if more are saved.

## Non-goals

- No automatic stop reordering or shortest-path optimization.
- No turn-by-turn spoken navigation, live traffic or traffic-aware ETA.
- No route recording, continuous/background location tracking, or server-side route history.
- No offline maps, tile prefetch, bulk tile downloads, or route geometry caching.
- No new paid provider, API key, self-hosted routing cluster, or database migration.
- No claim of route availability for every mode or region; community graph data may be missing or stale.

## Approaches considered

1. Browser-side Leaflet + OSRM/FOSSGIS public profiles — chosen. Fits the existing self-contained, owner-only page without credentials, a D1 migration, or a server proxy. It can show route geometry, distance and duration. Trade-offs: shared service rate limits and no SLA; provider sees/logs coordinates; browser must honor provider usage policy.
2. Self-host OSRM/Valhalla. Greater control over availability, profiles, logging and data freshness, but requires a server and ongoing graph-data imports/resources outside this low-volume Cloudflare Worker project.
3. Managed paid routing provider. Could provide contractual limits, support and additional routing features, but introduces account/API-key management, billing and another external dependency without a demonstrated need for this private owner-only use.

The chosen approach is option 1. Revisit options 2 or 3 before public/high-traffic rollout or if provider policy/availability ceases to fit.

## Architecture and behavior

- Keep the feature in src/nearby-ui.ts; route computation is requested directly by the browser. This preserves the browser's normal User-Agent and Referer behavior required by the public services and avoids storing route requests in the Worker.
- Use Leaflet 1.9.4 with pinned CDN Subresource Integrity. On CDN load failure, leave the saved itinerary usable and show a clear map-unavailable message; never crash the entire page.
- Use OSM raster tiles from https://tile.openstreetmap.org/{z}/{x}/{y}.png, only as Leaflet requests tiles for the visible map. Show © OpenStreetMap contributors and an OpenStreetMap copyright link.
- Change the page's referrer policy from no-referrer to strict-origin-when-cross-origin so the tile provider receives a valid origin Referer without exposing the full page path.
- Allow only the exact routing hosts in CSP and use fixed profile-to-endpoint mappings:
  - driving: https://router.project-osrm.org/route/v1/driving
  - cycling: https://routing.openstreetmap.de/routed-bike/route/v1/bike
  - walking: https://routing.openstreetmap.de/routed-foot/route/v1/foot
- Send coordinates in longitude,latitude order as required by OSRM. Ask for GeoJSON geometry, no alternatives and no route steps for the first iteration. Use the returned route's distance and duration, and its legs' distance/duration. Do not estimate traffic.
- Only explicit button activation can start a route request. Disable the button while in flight and enforce a minimum 1,100 ms between route-provider calls in the page instance. Do not automatically retry, recalculate on reorder, or send requests on page load.
- Bound one route to 10 waypoints. If the saved list exceeds 10, route only the first 10 in its current order and show an explicit notice. A route requires at least two selected points.
- Validate response before drawing: HTTP success, code === "Ok", a first route, finite non-negative duration/distance, a valid LineString of bounded finite [longitude, latitude] pairs, and leg count consistent with the requested adjacent stops. Display provider errors safely using textContent.
- Render numeric stop markers and the route polyline. Show total km/minutes plus each adjacent pair's distance and estimated time. Fit the map to the route and invalidate map size after layout changes.
- Route request disclosure must say stop coordinates are sent directly to the selected external routing service and requests may be logged there. Favorites remain localStorage-only and are not sent to Nolane's server.
- The current route is transient page state only. Do not write it to localStorage, D1, telemetry, or any API.
- CSP must permit Leaflet's pinned unpkg CSS/JS, OSM tile host, and the three fixed route endpoints only. Referrer-policy must meet OSM tile requirements.

## Security, privacy and provider limits

- No user-controlled URL or profile URL is ever fetched. The profile selector maps to a static, hard-coded allowlist.
- Saved POI coordinates are restored through Wave 70's existing cleanSavedPlace validation; route building uses only checked numeric coordinates.
- Limit to 10 stops and one route request per 1.1 seconds; no request fan-out or retries.
- OSM tiles are normal interactive map tiles only. Respect response caching; no forced no-cache, proxy cache, prefetch, offline cache or bulk scraping.
- Keep visible attribution and correct referrer behavior.
- Provider route requests may be logged by the provider. UI must disclose that before the route is requested.
- No sensitive/private home addresses should be encouraged as saved POIs; GPX exports and locally saved favorites remain under user control.

## Acceptance criteria

- A user can save, reorder and remove places as in Wave 70 with no regression.
- With 2–10 saved stops and a selected profile, clicking the route button makes exactly one request to the profile's fixed endpoint, in current saved order.
- A successful bounded response draws a route and shows total distance/duration plus per-leg values.
- No route request occurs from page load, selection changes, or reordering.
- A second request inside 1.1 seconds is blocked locally; requests cannot run concurrently.
- Invalid coordinates or provider payloads, HTTP errors, NoRoute/NoSegment and unavailable Leaflet are handled safely.
- More than 10 saved entries clearly disclose that only the first 10 in list order are routed.
- The full existing checks pass: TypeScript, Vitest, deployment script checks, Python runner tests and Worker build.
- Production deploy smoke confirms /nearby remains private and no D1 migration is needed. The smoke does not assert third-party routing providers' uptime.

## Calls made by the implementer

- Default profile is driving.
- Use Leaflet 1.9.4, pinned by SRI.
- Maximum routed stops is 10; favorites cap remains 50.
- Request routes only when the user clicks; no auto-refresh on saved-list edits.
- Show total and per-leg metrics; defer turn instructions and traffic-aware ETA.
- Direct browser requests are chosen over a server proxy to preserve browser request identity and avoid sending saved stops to Nolane's Worker.
