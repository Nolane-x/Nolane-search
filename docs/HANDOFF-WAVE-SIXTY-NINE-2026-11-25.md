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
