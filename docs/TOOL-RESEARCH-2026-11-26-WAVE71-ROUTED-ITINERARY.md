# Wave 71 — Routing and Map Provider Research

Date: 2026-11-26
Scope: private owner-only Nearby Places route display, not a public mapping service.

## Selected services

| Capability | Endpoint | Protocol/profile |
|---|---|---|
| Driving | https://router.project-osrm.org | OSRM Route API / driving |
| Cycling | https://routing.openstreetmap.de/routed-bike/route/v1/bike | OSRM-compatible Route API / bike |
| Walking | https://routing.openstreetmap.de/routed-foot/route/v1/foot | OSRM-compatible Route API / foot |
| Map tiles | https://tile.openstreetmap.org/{z}/{x}/{y}.png | OSM standard raster tiles |
| Browser map | Leaflet 1.9.4 via unpkg, pinned with Subresource Integrity | rendering only |

The three route endpoints are not interchangeable. OSRM project frontend configuration documents the public driving endpoint and the FOSSGIS routed-bike/routed-foot paths; the application uses the distinct endpoint/profile pair for each user-selected mode.

## Route API behavior

- Route requests use longitude,latitude coordinate order and preserve the user's current saved-stop order.
- Query: overview=full, geometries=geojson, steps=false, alternatives=false.
- Expected output: code Ok, route distance/duration, LineString geometry, one leg for each adjacent pair, and one waypoint for each requested stop.
- NoRoute, NoSegment and TooBig are handled as user-facing failures; malformed/non-finite/out-of-range geometry is discarded.
- Route duration is the selected profile's estimate. It is not live traffic or a guaranteed arrival time.

## Usage / operational restrictions

- Public OSRM/FOSSGIS instances are best-effort community services, not a contracted backend with an uptime or latency SLA.
- Use no more than one route request per second. The UI enforces a 1,100 ms minimum interval per page and prevents concurrent requests. Use remains intentionally low-volume and owner-only.
- The route providers may log incoming route requests. Route coordinates leave the browser and are sent to the selected provider only after an explicit click.
- The app does not retry, fan out, auto-refresh or route when the page opens.
- Browser User-Agent is native and the response policy strict-origin-when-cross-origin sends an origin Referer without the full route page path.

## OSM tile requirements

- Show visible © OpenStreetMap contributors attribution and link to the copyright page.
- Use the official HTTPS tile hostname and normal browser caching behavior.
- Request tiles only for the currently viewed map area; do not prefetch, bulk-download, create offline caches or use tiles as a data extraction source.
- Leaflet and its CSS are CDN-hosted; the script is pinned to version 1.9.4 with SRI.
- To protect locally saved POIs, the map and tile layer are not initialized on page load. They initialize only after the user clicks Tính tuyến đường. That action also discloses that the tile provider can infer the displayed map area from requested tiles.

## Privacy / persistence

- Saved place names, categories, addresses and coordinates remain in Wave70's versioned browser localStorage key after explicit save. No new favorites API, D1 schema, cloud sync or server-side location history.
- Route requests are sent directly from browser to the chosen routing service. No server proxy, D1 storage, telemetry or route-history endpoint is added.
- Tile requests begin only after the user invokes route calculation; OSM receives map tile coordinates for the displayed area.
- Current route response and geometry are transient page state. GPX remains a local download action.
- Do not save sensitive private addresses as favorites. Browser localStorage can be removed by clearing site data.

## Alternatives reviewed

1. Browser-side OSRM/FOSSGIS + Leaflet — selected for a personal low-volume app without secrets, D1 or infrastructure.
2. Self-hosted OSRM/Valhalla — gives control over rate, availability and logs but requires a separate server, OSM extracts and regular graph-data updates.
3. Managed commercial routing — potentially better uptime/traffic data and contractual limits, but requires an API key/account/billing and is not needed for this private first iteration.

## Primary references

- OSRM HTTP Route API: https://project-osrm.org/docs/v5.24.0/api/#route-service
- Project OSRM frontend's public profiles: https://github.com/Project-OSRM/osrm-frontend/blob/gh-pages/src/leaflet_options.js
- OSRM demo server policy: https://github.com/Project-OSRM/osrm-backend/wiki/Demo-server
- FOSSGIS routing service information: https://routing.openstreetmap.de/about.html
- OpenStreetMap tile usage policy: https://operations.osmfoundation.org/policies/tiles/
- Leaflet 1.9.4 download/SRI: https://leafletjs.com/download.html
