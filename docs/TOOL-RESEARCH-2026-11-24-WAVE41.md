# Wave 41 — daily-life planning and household helpers

Date: 2026-11-24  
Status: implementation branch; PR/CI/deployment pending.  
Branch: \`feat/wave-forty-one-daily-life-planning-tools\`  
Production baseline: **483 processors** (Wave 40).  
Branch target: **494 processors** (+11).

## Product direction

Wave 41 continues the shift from specialist-only processing toward everyday tasks: bills, household planning, mobile data, solar output, home decoration, event portions, transport and storage. Prices, rates, dimensions, and average consumption are inputs supplied by the user. These are not live quotes from utilities, carriers, installers or retailers.

## Reference projects reviewed across the daily-life waves

- [Actual Budget](https://github.com/actualbudget/actual) — an open-source personal-finance and household-budgeting project; product-category inspiration for practical money and household utilities.
- [Grocy](https://github.com/grocy/grocy) — an open-source household and grocery-management project; reference for everyday home workflows.
- [Mealie](https://github.com/mealie-recipes/mealie) — an open-source family recipe and meal-planning project; reference for event food and meal-related consumer workflows, not a code source.
- [OpenSpeedTest](https://github.com/openspeedtest/Speed-Test) — an open-source browser speed-test project; reference for showing network and download quantities in familiar units.
- [Stirling-PDF](https://github.com/Stirling-Tools/Stirling-PDF) — an open-source document utility project; reference for practical file-oriented tools in the wider catalog.

These repositories are used as product-discovery references. No source code, UI, media assets or third-party runtime dependency is copied into Wave 41. See the Wave 40 research note for the previous license review and subdirectory caveats.

## Processors added

| ID | User-facing tool | Function |
|---|---|---|
| \`water-bill-calculator\` | Ước tính hóa đơn nước | Calculate meter consumption and a bill from a user-entered single m³ price, fixed charge and optional sewage percentage |
| \`mobile-data-duration-calculator\` | Ước tính dung lượng 4G/5G | Calculate remaining data duration and a daily limit to last until renewal |
| \`solar-panel-output-calculator\` | Ước tính điện mặt trời | Estimate daily/monthly generation from panel wattage/count, peak-sun hours and losses |
| \`wallpaper-roll-calculator\` | Tính cuộn giấy dán tường | Estimate vertical drops and rolls, including pattern repeat and spare rolls |
| \`curtain-fabric-calculator\` | Tính vải may rèm | Estimate panel count and linear fabric length from window size, fullness, hems and pattern repeat |
| \`moving-box-calculator\` | Ước tính thùng chuyển nhà | Convert an estimated packed volume into boxes with fill and spare allowances |
| \`event-food-calculator\` | Tính đồ ăn cho buổi tiệc | Estimate main-food, snack and drink amounts per guest and event buffer |
| \`fuel-economy-calculator\` | Tính mức tiêu hao nhiên liệu | Calculate L/100 km, km/L, fuel cost and cost per kilometre |
| \`gas-cylinder-runtime-calculator\` | Ước tính thời gian dùng bình gas | Estimate burner hours/days from usable cylinder mass and user-entered consumption |
| \`shipping-volumetric-weight-calculator\` | Tính cân nặng quy đổi vận chuyển | Compare actual and dimensional weight using the carrier's user-entered divisor |
| \`storage-capacity-calculator\` | Ước tính sức chứa bộ nhớ | Estimate photos, video minutes and documents from capacity and average file sizes |

## Integration and safety

- All 11 IDs are registered in \`src/tools.ts\`, Python \`RUNNERS\` and the Python handler map.
- Direct AI chat execution uses the existing \`process_text_content\` tool with compact JSON inputs. Each JSON shape is listed in the model-facing tool description.
- File-based jobs continue through the existing ephemeral GitHub Actions runner.
- Python processors use only the standard library. No package install, paid API, new secret, Cloudflare resource or D1 migration is introduced.
- Inputs are finite and bounded. The existing 1 MiB calculator JSON request limit and 20 MiB file runner limit remain in force.
- Water, mobile data and shipping estimates use user-entered tariffs, package allowance and volumetric divisor. Solar estimates use user-entered peak-sun hours and loss allowance. No current local tariff or carrier quote is implied.
- Wallpaper, curtains and moving-box counts are material planning estimates; installers and suppliers may apply different layout, pattern, measurement and packing rules.
- Gas and fuel values use user-entered consumption and are not promises of real-world runtime or economy. Storage numbers are illustrative because actual file sizes vary.

## Validation plan

The PR must pass TypeScript type-check, Vitest, Python unittest discovery, runner/catalog/documentation parity and Cloudflare Worker build. Focused Python fixtures cover all eleven tools plus invalid meter readings, usage over plan allowance, wallpaper rolls too short for one drop, invalid shipping divisors and duplicate JSON keys. No tool is production-ready until PR CI, merge, Worker export and Cloudflare deployment succeed.
