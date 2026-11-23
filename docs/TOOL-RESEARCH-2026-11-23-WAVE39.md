# Wave 39 — everyday-user tool research

Date: 2026-11-23  
Scope: useful daily utilities, not another specialist developer-tool wave.

## Why this wave changes direction

The catalog reached 462 processors, but the mix was increasingly weighted toward specialist file formats, infrastructure, ML and repository audits. A large catalog is not automatically useful to a normal person. Wave 39 deliberately adds practical calculators that can be understood from their names and used from an ordinary chat prompt.

## Upstream repositories reviewed

The review used repository metadata, README and LICENSE files. The repositories below are independent reference projects; no source code, assets or bundled dependencies were copied into Nolane Search.

| Repository | License checked | Useful product ideas observed | Decision |
|---|---|---|---|
| [iib0011/omni-tools](https://github.com/iib0011/omni-tools) | MIT | Image/video/audio, PDF, text/list, date/time, timezone and math utilities | Used as a breadth reference for everyday utility coverage |
| [ethereaglehq/privatools](https://github.com/ethereaglehq/privatools) | MIT | Document/media conversions, batch processing and multi-step file workflows | Used as a file-workflow and privacy-boundary reference; existing Nolane runner remains authoritative |
| [PMK765/lifehacktoolbox](https://github.com/PMK765/lifehacktoolbox) | MIT | Money/bill calculations, school helpers, home/project calculators and science explainers | Used to identify categories ordinary users are likely to understand |
| [qarmin/czkawka](https://github.com/qarmin/czkawka) | MIT | Duplicate and similar-file discovery | Reviewed as a possible future media/file utility; not part of this wave |

A source license is not a guarantee that an upstream implementation is suitable for direct transplantation. Nolane's processors are new, narrowly scoped implementations; upstream projects are credited as research inspiration rather than runtime dependencies.

## Wave 39 implementation

Ten small, independent processors are added:

| ID | User-facing name | Purpose |
|---|---|---|
| \`bill-split-calculator\` | Chia hóa đơn | Add tax/tip and split a bill without leaving a rounding remainder |
| \`loan-payment-calculator\` | Tính khoản trả góp | Estimate a fixed-rate payment and produce an amortization CSV, including optional extra monthly payments |
| \`date-calculator\` | Tính ngày và khoảng thời gian | Add/subtract days, compare dates and count weekdays |
| \`timezone-converter\` | Đổi múi giờ quốc tế | Convert local times using IANA timezones and explicitly handle daylight-saving gaps/ambiguities |
| \`recipe-scaler\` | Điều chỉnh định lượng công thức | Scale ingredient quantities to a new serving count |
| \`grade-calculator\` | Tính điểm tổng kết | Calculate weighted grades and the score needed on remaining work |
| \`paint-calculator\` | Ước tính lượng sơn | Estimate wall/ceiling area, openings, coats and paint volume |
| \`fuel-trip-calculator\` | Tính chi phí xăng chuyến đi | Estimate fuel consumption, trip cost and per-passenger share |
| \`discount-calculator\` | Tính giá sau giảm giá | Apply sequential discounts, tax and quantity |
| \`unit-price-comparator\` | So sánh giá theo đơn vị | Normalize compatible mass, volume, length and count units to compare package value |

## Integration and safety

- Every processor exists in the TypeScript catalog, Python runner allowlist and actual Python handler map.
- The AI \`process_text_content\` tool can call these calculators directly with a compact JSON request; file upload is not required for a normal calculation.
- The existing file planner can select them for supported JSON uploads.
- The Python implementations use the standard library only; they add no runtime package, paid API, Cloudflare service, D1 migration, secret or persistent storage.
- Input JSON is bounded to 1 MiB. Duplicate JSON keys are rejected. Lists, numbers, dates, timezones, currencies and units are validated.
- Calculations run offline and do not call banks, lenders, payment providers, maps, fuel-price feeds or external services.
- Loan, paint and fuel outputs are estimates based on user-supplied assumptions. They do not include lender fees, insurance, tolls, actual paint-product coverage or changing market prices.
- The timezone calculator uses IANA timezone data and does not silently guess nonexistent wall-clock times during daylight-saving changes.
- Inputs and outputs remain under the existing ephemeral GitHub Actions runner boundary. The existing upload cap and Telegram result-delivery flow are unchanged.

## Validation

The PR must pass the existing CI workflow: TypeScript type-check, Vitest suite, Python compilation, full Python unittest discovery and Cloudflare Worker build. The new Python suite contains focused fixtures for all ten calculators and input edge cases. The AI tests exercise every new calculator through the same callable tool used by normal chat.

No new catalog item should be counted as production-ready until PR CI and the main-branch deployment have succeeded.
