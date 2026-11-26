# Wave 71 handoff — Routed Itinerary Map

Date: 2026-11-26
Branch: feat/wave-71-routed-itinerary-map

## Implemented behavior

- Nearby's Wave70 saved list now feeds an interactive Leaflet 1.9.4 map and route display.
- Three fixed route profiles: driving via OSRM project demo, cycling via FOSSGIS routed-bike and walking via FOSSGIS routed-foot.
- The route request occurs only after the user clicks Tính tuyến đường. It uses the first 10 saved places in their current order; up to 50 favorites can still be retained locally.
- Successful responses draw the route geometry, numbered stop markers, total distance/duration and a breakdown for each leg between consecutive saved places.
- Route output validation includes HTTP status, OSRM code, LineString geometry, finite/range-checked coordinate pairs, a 20,000-point geometry cap, finite non-negative metrics, expected waypoint count and expected legs.
- The UI blocks concurrent requests and enforces a 1,100 ms cooldown using a local numeric timestamp shared across page loads/tabs. This key contains no POI or route information. No retries or route request fan-out are added.
- The map/tile layer is lazy-loaded only after route calculation is explicitly requested, so opening Nearby does not send saved-place positions to OSM tile servers.
- Tile attribution and direct route-provider logging disclosure are visible; page Referrer-Policy is strict-origin-when-cross-origin.

## Privacy and provider limits

- Favorites remain in versioned localStorage only after explicit user action. No D1 migration, server-side favorites, route proxy, account sync or route history.
- Clicking route calculation sends selected coordinates directly to the route provider; that provider may log the request. Loading the map also sends viewport tile requests to OSM, which reveal the visible area.
- Public routing services are best-effort, no SLA and restricted to low-volume personal use; the code caps route requests to one per 1.1 seconds. Do not make high-volume/public promises.
- OSM tiles are normal viewport-driven requests only: no prefetch, bulk download or offline cache.
- Durations are routing-profile estimates, not live traffic or turn-by-turn navigation. No auto-optimization of stops.

## Validation results

- Browser-level tests execute the actual inline JavaScript with controlled DOM, localStorage, Leaflet and OSRM responses. Coverage includes no route/tile call on page load, explicit click, all three profile endpoints, route geometry/metrics, first-10 order, NoRoute/malformed geometry, same-page throttling and timestamp-only cooldown across page loads.
- PR CI #45761827446 and main CI #45762026423 passed TypeScript, 41 Vitest files / 426 tests, deployment scripts, 449 Python runner tests and Worker build.
- Cloudflare deploy #45762026380 and Worker export #45762026504 passed; the production smoke validates the Nearby authentication boundary, not third-party OSRM/FOSSGIS availability or tile rendering.
- No D1 migration, route proxy, external API key or server-side route persistence was needed.

## Production rollout — Wave 71 (2026-11-26)

- [PR #146](https://github.com/Nolane-x/Nolane-search/pull/146) merged into `main` as `77854cfc7e2b2589743a066c855882ca96402962`.
- PR CI #45761827446 and main CI #45762026423 passed TypeScript, 41 Vitest files / 426 tests, deployment checks, 449 Python runner tests and Worker build.
- Cloudflare deploy #45762026380 succeeded with Worker version `2fcd46ac-9573-4a44-88ea-433cef22d196`. Telegram webhook verification, command registration and Workspace/Nearby smoke passed. Worker export #45762026504 succeeded.
- Production smoke checks the protected Nearby route and anonymous API boundary; it does not make live OSRM/FOSSGIS calls or validate Leaflet tile rendering.
- No D1 migration, server route proxy, new secret or server-side route history was needed.
