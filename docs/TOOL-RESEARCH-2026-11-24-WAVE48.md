# Wave 48 — marine, earthquake, books and postal tools

Date: 2026-11-24
Status: implementation branch; CI, merge and deployment pending.
Branch: feat/wave-48-marine-earthquake-books-postal
Base main commit: bdab89165ccdd068efe14aefe386b5082011c220
Scope: four directly model-callable everyday information functions. The 534 file-processor catalog remains unchanged.

## Provider and repository review

| Project / API | Research and decision |
|---|---|
| https://github.com/open-meteo/open-meteo | Marine OpenAPI and public docs include wave height/direction/period, swell, sea temperature, ocean currents and sea-grid selection. Use the API only for non-commercial personal use and include CC BY 4.0 attribution/model caveats. |
| https://earthquake.usgs.gov/fdsnws/event/1/ | USGS FDSN Event Service supports GeoJSON queries with latitude, longitude, maximum radius in km, time range and minimum magnitude. Use read-only catalog results only; never present as early warning. |
| https://openlibrary.org/developers/api | Open Library Search API documentation allows human-initiated requests but forbids bulk harvesting/high-traffic commercial infrastructure; default is 1 request/second, with app identification via User-Agent. Limit to 10 results, set a descriptive User-Agent and throttle to one request/second per warm Worker isolate. |
| https://github.com/zippopotamus/zippopotamus | Project README and official docs describe a free postal/ZIP lookup based on GeoNames; coverage varies and data is provided as-is. Use read-only postcode lookup, not delivery confirmation. |

Open Food Facts was deliberately excluded: its API docs require prospective integrations to review reuse terms and complete an API usage form, and publish per-IP read/search rate limits. It is not integrated without provider onboarding. REST Countries was excluded because the current docs specify account API keys and monthly quotas.

## Functions

| Function | User outcome | Provider |
|---|---|---|
| get_marine_forecast | Current wave/swell conditions and up to 7 daily forecasts for a coastal/sea place | Open-Meteo Marine |
| get_earthquake_activity | Recent reported USGS events near a named city with bounded days/radius/magnitude | USGS FDSN Event Service |
| search_books | Small book search by title/author/subject with bibliographic metadata | Open Library |
| lookup_postal_code | Resolve a country/postal code to mapped towns, regions and coordinates | Zippopotam.us / GeoNames |

## Safety and operational boundaries

- All provider requests use fixed HTTPS hosts, reject redirects, time out after 12 seconds and cap JSON responses at 500 KB.
- Marine uses the nearest sea grid; returned model coordinates and distance are included. A warning is added when that grid is more than 80 km away. The result is not a navigation, swimming or rescue service.
- Open-Meteo free API use is non-commercial only; values are model output with CC BY 4.0 attribution.
- USGS events are reported catalog records, not an earthquake warning or a declaration that an area is safe. Range is limited to 30 days, radius to 1,000 km, magnitude to 0–9.9 and results to 30.
- Open Library is human-initiated low-volume search only; max 10 records, one request/second per warm isolate, descriptive User-Agent. Records do not establish book availability.
- Zippopotam.us derives from GeoNames and is provided as-is; coverage/accuracy varies, and no result does not prove a postcode is invalid.
- No API key, paid service, D1 migration, new dependency, bulk crawler, copied source code or assets are added.

## Validation plan

Mocked-fetch tests cover all providers, bounds, response shaping, postcode 404 handling, URL allowlisting and API dispatch. CI must pass TypeScript, full Vitest, deployment scripts, Python runner tests and Worker build before merge.
