# Wave 69 handoff — Nearby Essentials

Date: 2026-11-25
Branch: `feat/wave-69-nearby-essentials`

## Changes

- Add `essentials` as a combined nearby category.
- One fixed Overpass POST includes two static allowlisted filters (amenity and shop); no parallel calls.
- Infer each result's category label (food, shopping, pharmacy, medical, ATM/bank, fuel, EV charging).
- Limit Essentials to 3 km; individual categories retain 5 km. UI disables 5 km for Essentials and the API enforces the cap independently.
- Validate OSM website fields through shared `isSafePublicUrl`, rejecting non-HTTPS, local/private hosts, IP literals, credentials and non-standard ports.
- Existing owner session protection, user-initiated location permission, no-location-history policy and visible ODbL attribution remain.

## Validation added

- Multi-category query allowlist and result-category mapping.
- One-upstream-request assertion for Essentials.
- Essentials radius cap and UI selector behavior.
- Unsafe OSM website filtering.
- Existing Wave68 owner-only route/API tests and no-location-storage assertions remain.

## Provider boundary

The public Overpass endpoint remains shared infrastructure for low-volume personal use. This change intentionally does not add tiles, routing, geocoding, background location, or provider traffic fan-out.


## Production rollout — Wave 69 (2026-11-25)

- PR #143 merged into `main` as `2c32d99ca66114a07e24288cbb4625c7cd3ba0e2`.
- PR CI #636 (`45647984799`) and main CI #637 (`45648607173`) passed TypeScript, 41 Vitest files / 419 tests, deployment checks, 449 Python runner tests and Worker build.
- Cloudflare deploy #176 (`45648607094`) and Worker export #169 (`45648607096`) succeeded. Telegram webhook/commands were registered; the post-deploy Mini App smoke passed. No D1 migration was required.
- The deployed source commit `194161c96e59705a92539605c4ec32949c0bfefa` and merge commit `2c32d99ca66114a07e24288cbb4625c7cd3ba0e2` share the same Git tree.
- Smoke log confirms /nearby private redirect and nearby API anonymous 401. It does not prove every live Overpass request will succeed; the public endpoint remains shared, low-volume-only infrastructure.
