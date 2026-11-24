# Wave 44 — implementation handoff

Date: 2026-11-24  
Branch: feat/wave-forty-four-everyday-life-planners  
Base: Wave 43 / 510 production catalog  
Status: Review branch; first PR CI exposed three issues, now corrected on the branch; CI rerun pending.

## Included tools

| ID | User-facing task |
|---|---|
| pantry-use-first-planner | Sort pantry items by the date on the package |
| pantry-recipe-matcher | See which saved recipes fit ingredients on hand |
| meal-prep-timeline-planner | Coordinate a meal with multiple preparation steps |
| laundry-load-organizer | Group laundry into practical machine loads |
| trip-itinerary-planner | Schedule stops within a day-trip time window |
| vehicle-maintenance-planner | Track service intervals by date and odometer |
| document-renewal-planner | Prepare renewal reminders before expiration |
| warranty-claim-assistant | Draft a product-inspection/warranty enquiry |

## Implementation

- tools/wave44.py: eight offline Python processors using the standard library.
- tools/test_wave44.py: 10 focused Python tests including constraints and malformed input.
- src/everyday-life-planners.ts: direct AI-callable implementations for all eight IDs.
- src/tools.ts: eight utility catalog entries.
- src/agent-tools.ts: AI allowlist, input schema guidance and routing.
- tools/runner.py: GitHub Actions runner imports, allowlist and dispatch.
- tests/agent-tools.test.ts: invokes every Wave44 function through the AI tool surface.
- tests/tools.test.ts: asserts all 518 catalog entries are unique/ready and new IDs are registered.
- tests/telegram.test.ts: Tool Center expected count updated to 518.
- docs/TOOL-RESEARCH-2026-11-24-WAVE44.md: upstream workflow research and safety boundaries.
- docs/NOLANE-TOOLS.md: marks eight Wave44 tools as proposed while PR #97 is pending.

## Verification gates

1. TypeScript type-check and full Vitest suite.
2. Python compile and full python -m unittest discover -s tools -p 'test_*.py' suite, including Wave44 tests.
3. Cloudflare Worker build.
4. Verify all eight IDs agree between catalog, AI allowlist/direct implementation, runner allowlist and handler map.
5. Merge only after required PR checks succeed.
6. Confirm main CI, Worker export/health smoke and Cloudflare deploy after merge.
7. Confirm Telegram webhook and commands if the deployment workflow reports that step.
8. Owner-level acceptance remains separate: try safe sample JSON through the private Telegram bot and a JSON upload. Automated tests/webhook registration do not prove every client-side flow.

## Production accounting

Wave 43 / 510 tools remains the latest production release until merge and deployment checks have passed. Wave44's proposed catalog total is 518.