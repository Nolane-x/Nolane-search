# Wave 40 — everyday household, travel and device utilities

Date: 2026-11-24  
Status: implementation branch; PR/CI/deployment pending.  
Branch: \`feat/wave-forty-everyday-household-tools\`  
Production baseline: **472 processors** (Wave 39).  
Branch target: **483 processors** (+11).

## Why these categories

Wave 39 added practical personal calculators. Wave 40 broadens usefulness into ordinary household tasks, trip planning, device runtime and internet transfers. All calculations use measurements, tariffs and costs entered by the user. There is no live electricity tariff, building-material price, currency rate or network-speed lookup, so results do not silently assume a country-specific rate.

## Upstream projects reviewed

| Repository | Public project purpose | License signal checked | What informed Wave 40 |
|---|---|---|---|
| [actualbudget/actual](https://github.com/actualbudget/actual) | Local-first personal finance and envelope budgeting | MIT | A simple monthly cash-flow summary and savings-goal estimator fit the same consumer need without copying Actual's budgeting application or data model |
| [grocy/grocy](https://github.com/grocy/grocy) | Household groceries and home management | MIT | Reinforced the value of everyday home and household workflows rather than specialist developer utilities |
| [mealie-recipes/mealie](https://github.com/mealie-recipes/mealie) | Family recipe manager, meal planner and shopping lists | AGPL-3.0 | Reviewed only as a consumer use-case reference; no code or assets are copied, and Wave 40 avoids reimplementing its recipe/meal-planning application |
| [Stirling-Tools/Stirling-PDF](https://github.com/Stirling-Tools/Stirling-PDF) | Browser/self-hosted PDF editing and conversion toolkit | MIT for the main repository, with separately licensed proprietary, SaaS, engine and desktop subdirectories | Confirms demand for approachable document and file utilities; no PDF code is imported in this wave |
| [OpenSpeedTest/Speed-Test](https://github.com/openspeedtest/Speed-Test) | Browser-based internet performance estimation | MIT | Inspired a deterministic download-time estimator using user-supplied speed and file size |

The license signals above were checked against the repositories' GitHub pages and license information. A repository's headline license does not automatically cover all bundled subdirectories or dependencies. No upstream source code, UI, assets or runtime dependency is copied into Nolane Search. Wave 40 implementations are new, small, standard-library calculations.

## Processors added

| ID | User-facing tool | Function |
|---|---|---|
| \`appliance-energy-calculator\` | Tính điện tiêu thụ thiết bị | Estimate monthly kWh and cost from watts, hours, days and a user-entered kWh tariff |
| \`floor-tile-calculator\` | Tính gạch lát sàn | Estimate tile count, boxes and material cost with a waste allowance |
| \`concrete-volume-calculator\` | Tính khối lượng bê tông | Estimate concrete volume, litres and optional bag count/cost |
| \`soil-mulch-calculator\` | Tính đất và mùn phủ vườn | Estimate soil or mulch volume, bag count and optional cost |
| \`household-budget-calculator\` | Lập ngân sách gia đình | Group monthly expense entries and calculate remaining income |
| \`savings-goal-calculator\` | Tính mục tiêu tiết kiệm | Estimate months to target using current savings, monthly deposits and a constant assumed interest rate |
| \`travel-budget-calculator\` | Lập ngân sách chuyến đi | Add trip expenses, include a buffer and calculate per-person/per-day amounts |
| \`download-time-calculator\` | Tính thời gian tải xuống | Convert file sizes and network speeds correctly between bits and bytes |
| \`work-hours-calculator\` | Tính giờ làm và tiền công | Sum shifts, unpaid breaks and overnight shifts, then estimate gross pay |
| \`battery-runtime-calculator\` | Ước tính thời lượng pin | Estimate runtime from Wh or mAh × voltage, device watts and efficiency |
| \`water-tank-volume-calculator\` | Tính dung tích bồn nước | Estimate rectangular or cylindrical tank capacity and current fill volume |

## Integration and safety

- All 11 IDs are registered in \`src/tools.ts\`, Python \`RUNNERS\` and the Python handler map.
- Direct AI chat execution uses the existing \`process_text_content\` tool with compact JSON requests. The JSON input shape for each calculator is included in the model-facing tool description.
- File-based requests continue through the existing ephemeral GitHub Actions runner.
- Python processors use only the standard library. No package install, paid API, secret, Cloudflare resource or D1 migration is needed.
- User-supplied values are validated and bounded. JSON calculator requests retain the existing 1 MiB request limit and the runner's existing 20 MiB file limit.
- No local or external tariffs are embedded. Electricity cost uses the user's price per kWh. Building-material prices and bag yields are optional inputs. Download time uses the user's stated sustained speed.
- Savings and travel results are arithmetic scenarios, not financial recommendations. Work-hours results do not apply local overtime, tax or employment rules. Device and materials estimates state their main assumptions and omissions.

## Validation plan

The PR must pass TypeScript type-check, the full Vitest suite, Python unittest discovery, the runner catalog/handler/docs parity test and Cloudflare Worker build. The Wave 40 test suite exercises each processor and boundary cases such as overnight shifts, unit conversions and invalid input. No tool is production-ready until PR CI, merge, Worker export and Cloudflare deployment have succeeded.
