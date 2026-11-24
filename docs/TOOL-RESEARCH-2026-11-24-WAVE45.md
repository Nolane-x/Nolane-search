# Wave 45 — personal finance and moving-life workflows

Date: 2026-11-24
Status: merged and deployed to production as 526 tools on 2026-11-24.

## Why these workflows

Wave 45 extends practical day-to-day utility coverage beyond calculators: read a bank-export CSV without editing it, forecast recurring income and bills, settle several shared expenses, coordinate a move, label boxes, track retailer return windows, keep gift spending within budget, and size a user-defined emergency supply list.

All implementations are newly written Nolane code. The projects below were examined for user workflows only; no code, assets, data, APIs, schemas or dependencies have been copied.

## GitHub projects reviewed

| Project | Observed user workflow | Relevance | License boundary |
|---|---|---|---|
| [Spliit](https://github.com/spliit-app/spliit) | Group expenses, uneven splits, reimbursements, balances and receipt attachments | Shared expense settlement must support different participants per expense and non-equal shares | README and LICENSE checked; MIT. No code or schema reused |
| [BillBlend](https://github.com/DebanjanSarkar/billblend) | Local-first group trip costs, equal/unequal splits, minimum-transfer settlement, settled history and CSV export | Keep group calculations local/offline and reduce redundant repayment transfers | README checked; no LICENSE file found at repository root, so no code or assets reused |
| [Expense Budget Tracker](https://github.com/kirill-markin/expense-budget-tracker) | Transaction ledger, multi-currency reporting, bank-file import and category views | Analyse bank-export rows by period, category and currency without writing to a bank account | README and LICENSE checked; MIT. No code, data or integrations reused |
| [Actual Budget](https://github.com/actualbudget/actual) | Local-first personal finance and envelope-budget workflows | Keep financial summaries user-controlled and avoid transmitting imported account data | README checked; license not independently verified in this review. No code or assets reused |
| [Firefly III](https://github.com/firefly-iii/firefly-iii) | Self-hosted personal-finance project | Additional reference for why privacy, transaction records and currency handling matter | AGPL-3.0 license file checked; no code or dependencies reused |

Searches for dedicated open-source moving-day, retail-return and household emergency-kit projects did not return a sufficiently strong, maintainable candidate in this review. Those small workflows are based on the user needs themselves, with narrow scope and explicit assumptions rather than pretending to replicate a larger product.

## Wave 45 tools

1. bank-csv-expense-analyzer — import a standard bank-export CSV or provide transaction JSON; totals by month/category/currency, marks exact duplicate rows without deleting them. Negative amounts mean outflow; positive amounts mean inflow.
2. bill-cashflow-calendar-planner — expand once/weekly/monthly/quarterly/yearly bill and income events into a forecast with separate balances per currency.
3. shared-expense-settler — calculate multiple group expenses, equal or exact custom shares, expenses paid by different people and payments already made; suggest a compact transfer plan.
4. moving-day-checklist-planner — calculate due dates relative to moving day, overdue tasks and estimated workload per assignee.
5. moving-box-label-maker — make printable room/contents/fragile/heavy/open-first labels and room box counts.
6. return-deadline-tracker — calculate an estimated return date from a user-entered purchase date and seller window, and show which deadlines need attention.
7. gift-budget-planner — plan gift costs and purchased items per recipient against individual and overall budgets.
8. household-emergency-kit-planner — calculate household supply quantities only from user-entered per-person/per-day and per-household amounts, then compare against on-hand stock.

## Privacy, correctness and safety limits

- Bank analysis reads CSV/JSON locally in the ephemeral runner, produces a text summary and does not update, transmit or connect to any bank account. Users should not upload statements they do not wish to process. Currency totals are never combined or converted.
- For CSV, negative amount means money out and positive means money in. ISO dates are required; the tool flags exact duplicate rows for review instead of automatically deleting them.
- Cash-flow dates and recurrence are supplied by the user. A forecast is not a live bank balance, and it does not know about pending payments or unlisted transactions.
- Group settlement uses one currency per group and cent-accurate totals. It suggests transfers only; users confirm the group agreement and actual payments.
- Move dates, assignees, task durations and return windows are user inputs. The return tracker does not interpret consumer law or determine legal rights; confirm the seller's terms and applicable local rules.
- Gift budgeting is arithmetic, not a recommendation to spend.
- Emergency-kit quantities are multiplied strictly from user-defined rates and stock. They are not an official safety standard, medical advice or a guarantee of readiness; review local authority guidance and household needs.
- No new paid API, external service, database schema, persistent financial storage, credential or Python dependency is added.

## Release verification

- PR [#98](https://github.com/Nolane-x/Nolane-search/pull/98) merged as `e98b456dfbf320a57f9469673e3022f323d15b0f`.
- PR CI [45331231407](https://github.com/Nolane-x/Nolane-search/actions/runs/45331231407) and main CI [45331424637](https://github.com/Nolane-x/Nolane-search/actions/runs/45331424637) passed TypeScript type-check, 25 Vitest files / 271 tests, deployment-script checks, 438 Python runner tests and Worker build.
- Worker export/health smoke [45331424996](https://github.com/Nolane-x/Nolane-search/actions/runs/45331424996) returned `ok: true` and database `reachable`.
- Cloudflare deployment [45331424755](https://github.com/Nolane-x/Nolane-search/actions/runs/45331424755) succeeded. Worker Version ID: `b9168d76-3e11-4cf8-bf84-9276b61d7f04`.
- Telegram webhook was verified for message + callback_query and bot commands were registered. No D1 migration was needed.
