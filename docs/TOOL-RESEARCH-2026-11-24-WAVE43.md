# Wave 43 — product research for home, hobby and learning tools

Date: 2026-11-24  
Status: Research and implementation are on a review branch. The production count remains Wave 42 / 502 until PR, CI and deployment are verified.

## Selection rule

Wave 43 expands beyond calculators into lightweight organizers and planners for everyday activities. A candidate should solve a recognisable task, accept information the person already knows, return something usable, and work without a new paid API or always-on backend.

The implementation is independent Nolane code. These repositories were reviewed for workflows and product design; no source code, icons, visual assets, data files or dependencies were copied.

## Repositories reviewed

| Project | Workflow/features observed | Lesson applied in Nolane | License / scope note |
|---|---|---|---|
| [Loop Habit Tracker](https://github.com/iSoron/uhabits) | Habit history, graphs and streaks, flexible schedules such as several times per week, reminders and export | Summarise check-ins over a time window and report current/longest streaks against a user-set weekly target | README states GPLv3. No code or assets copied |
| [Plant-it](https://github.com/MDeLuise/plant-it) | Plant collection, activity logs, photos and reminders based on time since the user's last plant-care event | Track a user-defined care interval and show due/overdue items without pretending to know a plant's exact biological needs | No clear LICENSE file surfaced in the reviewed paths; no code or dependencies reused |
| [Open Garden Planner](https://github.com/cofade/open-garden-planner) | Metric garden layout, beds and paths, plant spacing, sun/shade and harvest/task planning; offline files | Calculate a conservative planting capacity from bed dimensions and user-entered row/plant spacing | README identifies GPLv3. No code, models or assets copied |
| [Growstuff](https://github.com/Growstuff/growstuff) | Food-gardening community data about what members grow and harvest | Keep garden planning transparent and based on supplied dimensions rather than inventing regional growing advice | The reviewed README describes open source/open data; no application code or dataset reused |
| [HomeBox](https://github.com/sysadminsmedia/homebox) | Household inventory, categorisation, search, photos, purchase and maintenance records, warranty tracking | Summarise home items, historical purchase totals, locations and entered warranty/service-life dates | Repository LICENSE is AGPLv3. No code, schema or dependencies copied |
| [Py-FSRS](https://github.com/open-spaced-repetition/py-fsrs) | A Python implementation of a spaced-repetition scheduler with card review ratings and due dates | Offer a small transparent review planner based on a user's confidence rating and an override interval | Repository states MIT. Nolane does not claim to implement FSRS and does not import this package |
| [Seating.Art / Seating Planner](https://github.com/gabriel1ll7/Seating-Planner) | Guest list, table capacities, seating assignment and event-venue planning | Assign complete guest groups to tables, honor capacity, and support user-specified avoid pairs | Repository states MIT. Nolane's text-based allocator is independently implemented |
| [Pet Care Tracker](https://github.com/DianaFarhat29/PetCare-Tracker) | Pet profiles and reminders for recurring appointments and care events | Produce a repeatable, user-defined daily routine checklist for each pet | No license was verified in the reviewed README; no code or dependency reused |
| [Super Productivity](https://github.com/super-productivity/super-productivity) | Private, offline-first task planning, daily focus and schedules | Keep the new planners bounded, copyable and useful without creating a persistent account or server feature | README states MIT. No code or dependency copied |

## Wave 43 implementation scope

1. habit-history-analyzer — calculate check-ins in a selected window, completion against a weekly target, current streak and longest recorded streak.
2. plant-care-scheduler — create due/overdue reminders from the user's last completed action and interval.
3. garden-bed-capacity-calculator — estimate rows and plants per row from bed dimensions, edge margin and spacing.
4. home-inventory-report — group household inventory by category/currency and report historical purchase amounts, purchase dates, warranty dates and user-entered expected service-life dates.
5. home-maintenance-scheduler — create recurring maintenance due dates and show overdue days, estimated minutes and priority.
6. pet-routine-planner — generate a dated checklist for non-medical routines such as walks, brushing and cleaning, based on the user's days and times.
7. event-seating-planner — keep guest groups together, fit them into user-defined table capacities and avoid user-specified pairs.
8. spaced-review-scheduler — turn a confidence rating into a simple review interval, with a custom-interval override and planning horizon.

## Accuracy and safety boundaries

- No live weather, local growing zone, soil, species-specific plant care, veterinary, vaccination, diagnosis or medication advice is fetched or inferred.
- Plant-care intervals and pet routines are reminders chosen by the user. Medical pet-care instructions must come from the veterinarian.
- Garden capacity is a geometric estimate. It does not know mature plant size, companion planting, access paths or local agricultural guidance.
- Home inventory values are historical purchase amounts, not resale, replacement, tax or insurance valuations.
- Home maintenance intervals and estimated work times are supplied by the user; the report is not a building-safety inspection.
- Event seating is a deterministic greedy assignment. If a group cannot fit under the constraints, it is explicitly reported as unassigned; it does not silently split the group.
- The spaced-review utility is a transparent heuristic (1/2/4/7/14 days by confidence, unless overridden), not FSRS and not a guarantee of learning outcomes.
- No new paid API, secret, database migration, persistent storage service or Python runtime dependency is introduced.
