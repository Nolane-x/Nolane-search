# Wave 70 handoff — Local Saved Places and GPX Itinerary

Date: 2026-11-26
Branch: feat/wave-70-local-saved-places-itinerary

## User-facing changes

- Nearby results now include **Lưu địa điểm**. Saved places are deduplicated by their OpenStreetMap object ID.
- A separate **Địa điểm đã lưu · Lịch trình** panel displays locally saved items and supports moving a stop up/down or removing it.
- A route can be exported as a GPX 1.1 `<rte>` containing ordered route points. XML text is escaped, coordinates are type/range checked, and the filename is fixed.
- The saved list is capped at 50 places to bound storage and export size.
- Stored favorites are sanitized when restored: only node/way/relation IDs, finite numeric coordinates within geographic ranges and bounded text fields are accepted. Duplicate IDs and entries beyond the cap are dropped.
- OSM map links for saved places are rebuilt from validated coordinates; arbitrary stored URLs are not trusted.
- Save/remove/reorder operations refresh result controls, so removed places can be saved again without repeating the search.

## Privacy and data boundaries

- Search-center coordinates remain transient: sent only after a user-initiated search to the Overpass API; never written to D1 or a server-side search history.
- A place's name, category, address and coordinates are written to this browser's versioned localStorage key only after the user explicitly clicks **Lưu địa điểm**.
- No favorites API, D1 table, account sync, analytics event or background location is added. Local favorites remain on the current browser profile/device and are not available on other devices.
- Clearing browser site data removes these favorites. Users should avoid saving sensitive private addresses.
- GPX export is a local file generated only after clicking the export button. It preserves the user's stop order, but it is **not** a calculated route, does not include road geometry, turn-by-turn directions, distance or travel-time estimates.

## Provider scope

- No new upstream provider or routing service is introduced. OSM map links continue to open the public OpenStreetMap website.
- The public Overpass endpoint remains for bounded low-volume personal queries only.

## Validation plan

- UI tests cover privacy disclosure, versioned browser storage, the 50-place cap, validation of stored records, manual ordering, GPX MIME/type and the explicit no-routing boundary.
- Existing geolocation permission and HTTPS result-link assertions remain.
- Full TypeScript, Vitest, Python runner, Worker build, production smoke and deployment checks must pass before merge/deploy.

## Production rollout — Wave 70 (2026-11-26)

- [PR #144](https://github.com/Nolane-x/Nolane-search/pull/144) merged as `09a65237d0253316dfdf6dfad2128857bc39ff5d`.
- PR CI #45749439137 and main CI #45749647312 passed TypeScript, 41 Vitest files / 419 tests, deployment checks, 449 Python runner tests and Worker build.
- Cloudflare deploy #45749647341 succeeded with Worker version `bcc51f91-edd2-4cec-b4f3-be339d7a4918`; Telegram webhook and commands were verified/registered. Worker export #45749647309 succeeded.
- Production smoke passed for Workspace HTML/CSP/auth/tabs, Nearby link, anonymous `/nearby` redirect and nearby search API anonymous 401. Smoke does not make a live Overpass query.
- No D1 migration, new upstream provider or routing engine was needed.
