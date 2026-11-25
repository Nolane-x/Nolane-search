# Wave 68 handoff — Nearby Places

Date: 2026-11-25
Branch: `feat/wave-68-nearby-places`

## Goal

Add an ordinary-user local discovery tool and a first-class entry from Telegram Mini App without guessing the user's location or storing it.

## Implementation

- `src/nearby-places-tools.ts`: fixed category allowlist, validated coordinates, bounded radius/result count, bounded Overpass POST, normalized named OSM elements, straight-line distance, source links and attribution.
- `src/nearby-ui.ts`: responsive `/nearby` page, explicit click-to-request geolocation, manual coordinate entry, category/radius controls, result cards and OpenStreetMap links.
- `src/index.ts`: owner-session-protected `GET /nearby` and `POST /api/nearby/search`; cross-origin POSTs use existing rejection rules.
- `src/agent-tools.ts`: `search_nearby_places` function schema and dispatch for explicitly supplied coordinates.
- `src/telegram-mini-app-ui.ts`: Workspace quick link.
- No D1 migration or location persistence.

## Validation

- Validate numeric coordinates, category enum, radius 200–5000 m and limit 1–25.
- Static Overpass query filters; no user-controlled tags or fetch URL.
- HTTPS-only external website links; safe OSM object/map links.
- Community-data caveats: straight-line distance, unverified opening-hours tags, missing/stale data.
- ODbL attribution visible.

## Release boundary

This is a low-volume personal-use integration with the public Overpass endpoint. Public Overpass instances are shared and are not a high-traffic backend guarantee. Before public-scale use, use a self-hosted instance or a provider with matching terms/capacity. No route directions, live availability, address geocoding or background tracking are implemented.
