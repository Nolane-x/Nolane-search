# Wave 42 — product research for everyday personal planning tools

Date: 2026-11-24  
Status: Research completed; implementation is on a review branch. Nothing in this document changes the production count until PR, CI and deployment are verified.

## Selection rule

This wave deliberately avoids another cluster of specialist developer/repository auditors. Candidate tools were selected using four practical questions:

1. Can a person understand the benefit without knowing a technical format or command-line concept?
2. Can the calculation or plan work deterministically from information the person already knows?
3. Can it return a useful result that can be copied, saved or acted on?
4. Can it run without a paid API, new secret, external account, live quote or permanent service?

The implementations are independent Nolane code. The projects below were reviewed for product workflows and user needs; their source code, assets and dependencies were not copied.

## Repositories reviewed

| Project | User workflow observed in its README | What Nolane can learn | Scope / caveat |
|---|---|---|---|
| [Mealie](https://github.com/mealie-recipes/mealie) | Recipe collection/import, weekly meal planning, shopping lists grouped for a supermarket, localisation | Turn several meals into one consolidated grocery list; preserve recipe-serving multipliers and unit awareness | The project states AGPL licensing. No code or dependency was taken |
| [Grocy](https://github.com/grocy/grocy) | Self-hosted grocery and household management; the README describes a home-management goal and an integrated API | Household tasks should be concrete and repeatable, not a pile of generic text transformations | A full inventory/stock-control system is much broader than a stateless tool |
| [Cuicuit](https://github.com/MadeInPierre/cuicuit) | Recipe imports, meal planning, derived shopping lists, shared household spaces and a mobile-friendly PWA | Shopping lists should be derived from planned meals; avoid forcing people to enter the same ingredient twice | README labels the app early alpha and self-hosting as not yet ready at review time |
| [Wallos](https://github.com/ellite/Wallos) | Subscription/payment tracking, categories, statistics, multi-currency support and upcoming-payment notifications | People need to see recurring costs as a yearly and monthly total, not only the sticker price on one billing cycle | Nolane's first pass is a calculator, not a persistent renewal reminder or bank integration |
| [Actual Budget](https://github.com/actualbudget/actual) | Local-first personal finance, privacy-focused budgeting and synchronisation between devices | Prefer explicit budgets and visible totals; keep financial estimates local and transparent | A full account/envelope budgeting product and multi-device sync are outside this wave |
| [Duelet](https://github.com/Rodrigo568/Duelet) | Break assignments into smaller tasks, schedule around deadlines and available study time, reschedule unfinished tasks | Prioritise near deadlines and fit work inside a declared daily capacity; report overload honestly | The README says the project is early development and its license is TBD; no code or dependency was adopted |
| [Travel Planner](https://github.com/LMD1-bot/travel-planner) | Trip itinerary, packing list, budget hints, sharing and offline/PWA use | Generate a packing checklist from trip duration and user-selected activities; retain a personal custom-item section | Its MIT badge applies to that repository; Nolane did not copy its implementation or templates |

## Wave 42 implementation scope

Eight independent utilities were chosen from those workflows:

1. meal-shopping-list-planner — scale ingredients by target servings and merge matching ingredient/unit pairs into one list.
2. travel-packing-checklist — suggest a checklist from number of days, travellers, user-provided climate and activities; allow custom additions.
3. study-plan-scheduler — schedule estimated study minutes around weekdays and deadlines; report any unscheduled work instead of silently overbooking.
4. weekly-chore-planner — spread household chores across selected days and balance estimated minutes among household members.
5. subscription-cost-calculator — annualise weekly/monthly/quarterly/semiannual/yearly subscriptions and group totals by currency without exchange-rate assumptions.
6. commute-cost-calculator — estimate car fuel/parking/toll costs or compare transit pay-as-you-go with a user-entered monthly pass.
7. reading-plan-calculator — turn remaining pages and a deadline into a pages-per-session target, with an optional reading-speed estimate.
8. grocery-budget-planner — add quantities and user-entered prices, group spending by category and show remaining/over-budget amount.

## Safety, accuracy and cost boundaries

- Prices, fuel rates, fares, weather/climate assumptions, dates, quantities and reading speed are supplied by the user; tools do not present these as live market quotes.
- Currency groups remain separate. The tools do not silently convert exchange rates.
- The travel checklist is a generic packing aid, not a source of current visa, border, airline-baggage or safety rules.
- Study scheduling is a deterministic capacity estimate, not a promise that a task can be completed or a substitute for a student's own judgement.
- Meal quantities combine only when ingredient names and units match; they are not a complete kitchen unit-conversion database.
- No new paid API, secret, Cloudflare product, database table, persistent file store or Python runtime dependency is introduced.
- Python runner requests retain the 1 MiB JSON limit and maximum item limits. AI direct processing remains bounded by the existing 40,000-character input limit.

## Future research queue

Further high-value everyday categories to evaluate separately (not part of the eight-tool count): pet-care routines, plant-watering schedules, household maintenance calendars, packing by airline baggage limits (only with current official sources), childcare rota planning, simple meal nutrition estimates (with trusted food datasets), gift/occasion budgets, and appointment preparation checklists. Live prices, public transport, weather and official travel restrictions should be sourced and freshness-labelled before being offered as live facts.
