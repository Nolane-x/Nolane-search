# Wave 44 — everyday life-administration planners

Date: 2026-11-24  
Status: merged and deployed to production as 518 tools on 2026-11-24.

## Product selection

Wave 44 deliberately adds ordinary household and personal workflows, not another set of developer audits. Each tool should take information the user already knows, produce an immediately usable checklist or report, and avoid needing a paid API or persistent profile.

The implementations are independent Nolane code. Upstream repositories were reviewed for product workflows and user needs; no upstream code, assets, schemas, dependencies or datasets were copied.

## GitHub projects reviewed

| Project | Everyday workflow observed | Design lesson used in Nolane | License / boundary |
|---|---|---|---|
| [Grocy](https://github.com/grocy/grocy) | Household inventory, stock/expiry tracking and meal planning around what is already available | Prioritise pantry items by dates supplied by the user and compare saved recipes with ingredients on hand | Project materials reviewed; no code or data imported |
| [Mealie](https://github.com/mealie-recipes/mealie) | Recipe library, weekly meal planning, shopping lists grouped into shopping sections, and URL-based recipe import | Keep pantry matching transparent and make a multi-step meal-preparation schedule from explicit dependencies and equipment | README identifies AGPL-3.0; no source code/schema/dependency reused |
| [LubeLogger](https://github.com/hargata/lubelog) | Vehicle maintenance history and fuel/mileage tracking, with reminders based on service records | Estimate next service trigger from odometer, service history and owner-manual intervals entered by the user | README identifies MIT; no source or assets copied |

## Wave 44 tools

1. pantry-use-first-planner — sort pantry items by user-entered use-by, best-before or expiry dates, with location and optional quantity.
2. pantry-recipe-matcher — rank saved recipes against available ingredients and list missing items. Matching is exact after whitespace/case normalisation; substitutions or aliases are not invented.
3. meal-prep-timeline-planner — schedule cooking tasks from duration, dependencies, equipment/resource and attention requirements; supports parallel steps when they do not conflict.
4. laundry-load-organizer — group garments by user-entered colour/fabric/drying groups, weight capacity and maximum wash temperature.
5. trip-itinerary-planner — build a day itinerary from supplied travel and visit durations; report stops that do not fit the available time.
6. vehicle-maintenance-planner — estimate calendar and odometer service triggers from owner-manual/service-record intervals entered by the user.
7. document-renewal-planner — produce reminder dates for documents with user-selected lead times.
8. warranty-claim-assistant — draft a Vietnamese or English product-inspection request, listing evidence and an estimated warranty end date from user-entered terms.

## Safety and correctness boundaries

- Pantry dates are not a food-safety assessment. Follow package instructions and local food-safety guidance.
- Recipe matching is exact; it does not infer substitutions or assess suitability for a particular person.
- Meal preparation uses declared task dependencies and resource assumptions; it cannot inspect a real kitchen or guarantee cooking quality/temperature.
- Laundry grouping is a sorting aid, not a substitute for garment care labels or machine instructions.
- Trip durations are user-supplied. There is no live routing, traffic, border, opening-hours or travel-requirements lookup.
- Vehicle intervals should come from the actual owner's manual or mechanic/service records. The report is not a mechanical diagnosis or safety clearance.
- Renewal dates and notice windows are user-entered. Check current rules and processing times with the issuing authority/provider.
- Warranty end dates are simple calendar calculations based on the input. They do not decide legal coverage; read the actual terms and exclusions.
- No new paid API, credential, persistent storage, D1 migration or Python runtime dependency is added.

## Release verification

- PR [#97](https://github.com/Nolane-x/Nolane-search/pull/97) merged as `4e7489aeca23de36c1cbf20db5ddf692f276d723`.
- PR CI [45327140857](https://github.com/Nolane-x/Nolane-search/actions/runs/45327140857) and main CI [45327334511](https://github.com/Nolane-x/Nolane-search/actions/runs/45327334511) passed TypeScript type-check, 25 Vitest files / 269 tests, deployment-script checks, 424 Python runner tests and Worker build.
- Worker export/health smoke [45327334519](https://github.com/Nolane-x/Nolane-search/actions/runs/45327334519) returned `ok: true` and database `reachable`.
- Cloudflare deployment [45327334621](https://github.com/Nolane-x/Nolane-search/actions/runs/45327334621) succeeded. Worker Version ID: `adc960a0-89a4-4287-9431-9204636de49e`.
- Telegram webhook was verified for message + callback_query and bot commands were registered.
- No D1 migration or new runtime dependency was needed.
