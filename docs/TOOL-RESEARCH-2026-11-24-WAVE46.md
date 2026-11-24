# Wave 46 — home, vehicle and rental management tools

Date: 2026-11-24
Status: Proposed on review branch; production remains Wave 45 / 526 tools until all CI and deployment checks pass.

## Why these workflows

Wave 46 extends household tools from one-off calculators and schedules into ongoing records and side-by-side comparisons: complete-tank fuel consumption, recorded ownership costs per kilometre, repair-versus-replace arithmetic, repair quote scope coverage, move-in/move-out evidence records, rental total-cost comparison and appliance service histories.

Implementations are independent Nolane code. Upstream repositories were reviewed for product workflows and design needs only; no code, assets, schemas, dependencies, APIs or data were copied.

## GitHub projects reviewed

| Project | User workflow observed | Design lesson | License / reuse boundary |
|---|---|---|---|
| [LubeLogger](https://github.com/hargata/lubelog) | Self-hosted vehicle maintenance and fuel mileage logbook; stores fuel/service entries and vehicle costs | Do not treat one tank fill as a complete consumption measurement; calculate consumption between consecutive full-tank records and keep an auditable running expense log | README and LICENSE inspected; MIT. No code or assets reused |
| [HomeBox](https://github.com/sysadminsmedia/homebox) | Home inventory, categories/locations/tags, photos, documents, warranty, purchase and maintenance tracking | Keep appliance history connected to purchase and warranty dates and make home records searchable by plain-language labels | LICENSE file inspected; AGPL-3.0. No source or assets reused |

Searches for small, maintained open-source tenant inspection and neutral quote-comparison projects did not return a sufficiently strong candidate in this review. The rental reports and repair-quote comparison therefore use explicit user-entered scope and observations instead of adopting a property-management product.

## Wave 46 tools

1. vehicle-fuel-log-analyzer — analyse multiple fill-ups, monthly litres/spend and L/100 km only between consecutive full-tank entries.
2. vehicle-ownership-cost-report — group user-recorded fuel, maintenance, insurance, parking and other costs; calculate recorded cost per kilometre without inventing depreciation.
3. appliance-repair-replace-comparator — compare annualised repair and replacement cost proxies from user-entered prices, lifespan and energy estimates.
4. home-repair-quote-comparator — compare quote totals, required scope coverage, exclusions, warranties and schedule; never rank workmanship from price alone.
5. rental-move-in-inspection-report — create a room-by-room initial condition and meter-reading record with evidence labels.
6. rental-move-out-condition-report — compare initial and final condition labels, show proposed deposit deduction arithmetic and organise notes.
7. rental-offer-cost-comparator — compare rent, recurring fees, utilities, up-front cash and refundable deposit separately over the same lease term.
8. appliance-service-history-report — group service events, repair costs, downtime, next service date and user-entered warranty period by appliance.

## Safety and correctness boundaries

- Fuel consumption uses consecutive full-tank entries; incomplete partial-fill sequences are not presented as reliable standalone consumption figures.
- Vehicle ownership totals only include the user's entered costs and distance. Depreciation, loan interest, resale value and missing expenses are not inferred.
- Repair-versus-replace results are annualised arithmetic, not safety diagnoses. Ask a qualified technician about unsafe, electrical, gas or structural faults.
- Quote comparison checks entered scope coverage and numbers; it cannot verify credentials, workmanship, permits, code compliance or hidden damage.
- Rental move-in/move-out reports record observations and evidence labels. They do not decide cause, fair wear and tear, deposit entitlement or local tenancy law.
- Rental offer totals separate refundable deposit cash from lease expenditure; actual contract fees and utility costs must be checked with the provider.
- Appliance warranty end dates are estimates using the duration entered by the user, not a coverage determination.
- No new paid API, secret, external service, D1 schema, persistent property/vehicle profile or Python dependency is introduced.