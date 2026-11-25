# Wave 68 research — Nearby Places discovery

Date: 2026-11-25

## User-facing feature

The Telegram Mini App Workspace links to a separate responsive `/nearby` page. It is intended for ordinary local tasks: find food/cafes, supermarkets/convenience stores, pharmacies, clinics/hospitals, ATMs/banks, fuel, EV charging, parks/playgrounds, attractions/museums and accommodation.

The page requires one of two deliberate inputs:
- The user clicks **Dùng vị trí hiện tại** and grants the browser geolocation permission.
- The user enters latitude and longitude manually.

It never runs browser geolocation automatically, does not infer an address/city from IP, and does not geocode a place name.

## Data source and implementation

- Source: OpenStreetMap data through the public Overpass API endpoint `https://overpass-api.de/api/interpreter`.
- Request: one fixed HTTPS endpoint, POST form field `data`, static category filters, `nwr`, bounded radius, `[timeout:15]`, `[maxsize:10485760]`, and `out center tags 100 qt`.
- Limits in application: one category per query, radius 200–5000 m (default 1500 m), at most 25 returned items, 18-second upstream timeout and 2 MB JSON response.
- User input is limited to validated finite coordinates/category/radius/limit. Arbitrary Overpass QL, arbitrary URLs, geocoding and free-form tags are not accepted.
- Result records are normalized and unnamed features omitted. Ways/relations use their returned center. Duplicate OSM object IDs are removed. The result includes the OSM object URL, a map URL, address fields when present, opening-hours tag and an HTTPS-only website field.
- Distance is Haversine straight-line distance; it is not a route distance or travel time.
- Opening-hours is a community-maintained tag, not a live open/closed status.
- The UI does not use external tile imagery. It links to OpenStreetMap map/object pages and displays attribution.

## Privacy and security

- `GET /nearby` and `POST /api/nearby/search` require the existing owner web session.
- The API rejects cross-origin POSTs using the existing same-origin request policy.
- Coordinates are sent only for the explicit user-initiated search. This wave does not create a D1 migration, save coordinates to D1, or add them to search history.
- The location is transmitted to the Overpass service as part of the query; do not enter coordinates you do not wish to share with that third-party endpoint.
- No location is guessed from IP or device metadata.
- The Overpass query is built exclusively from a fixed category allowlist and validated numeric coordinates. The app never fetches user-supplied URLs, so this feature does not add a user-controlled SSRF path.
- Names, websites, addresses, opening hours and OSM objects are community-contributed, may be missing or stale, and must not be presented as verified real-time facts.

## Provider policy / scale boundary

OpenStreetMap's own documentation distinguishes read-only Overpass from its editing API and notes that Overpass instances have their own capacity and fair-use limits. Public instances are shared; the Overpass documentation warns that applications relying on public instances as a backend for broad user audiences should operate their own instance or use a provider intended for that workload. The public Overpass API documentation gives a broad small-user guideline around 10,000 requests/day and under 1 GB/day, but this is not a service-level guarantee.

This is therefore a bounded, low-volume feature for the current personal Nolane Search deployment, not a commitment that the public endpoint can support high traffic. Before broad public rollout or repeated/automated use, replace the public endpoint with a self-hosted Overpass instance or a provider whose plan and terms match the expected usage. Do not parallelize queries or poll the endpoint. Handle HTTP 429/503/504 as temporary service limits/unavailability.

## Licensing / attribution

OpenStreetMap data is made available under the Open Database License (ODbL). The UI displays a visible link: **© OpenStreetMap contributors** to `https://www.openstreetmap.org/copyright`. Do not remove attribution. If future versions publish a substantial derivative database, review ODbL share-alike obligations before release.

## Sources reviewed

- OpenStreetMap Overpass API usage and shared-instance capacity guidance: https://dev.overpass-api.de/overpass-doc/en/preface/commons.html
- OpenStreetMap Wiki Overpass API overview and public instances: https://wiki.openstreetmap.org/wiki/Overpass_API
- OpenStreetMap Foundation API usage policy and service distinction: https://operations.osmfoundation.org/policies/api/
- OpenStreetMap/Overpass API documentation output syntax and supported query model: https://wiki.openstreetmap.org/wiki/Overpass_API
- ODbL attribution and terms reference: https://www.openstreetmap.org/copyright

## Not included

- Turn-by-turn routing or driving/walking times.
- Live opening status, reservation availability, phone verification or place reviews.
- Address/city geocoding or autocomplete.
- Publicly indexed location history, persistent favorites, tracking or background location.
- Paid POI enrichment or a guarantee that every local business is mapped.
