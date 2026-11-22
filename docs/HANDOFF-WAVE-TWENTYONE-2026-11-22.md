# Wave 21 handoff — Data science, spatial and schema utilities

Date: 2026-11-22
Repository: https://github.com/Nolane-x/Nolane-search
Branch: feat/wave-twentyone-data-science-spatial-sql-tools

## Scope

Adds seven distinct processors beyond the 345-tool Wave 20 production catalog:

- sql-static-audit: parse generic/PostgreSQL/MySQL/BigQuery/SQLite SQL, count SELECT/JOIN/table AST nodes and flag syntactically unscoped UPDATE/DELETE plus DROP/TRUNCATE/ALTER; never executes SQL.
- sql-format: format SQL statements into a separate `.sql` file; parser/formatter only, no execution.
- graphql-schema-audit: parse GraphQL SDL, build and validate schema, count types/fields/deprecations; no GraphQL endpoint is contacted.
- notebook-privacy-audit: inspect notebook format/cell IDs/execution counts/outputs/attachments and bounded secret patterns; never executes notebook code.
- kml-kmz-audit: read KML or a single KML document inside KMZ, count geometries and validate coordinate ranges; never writes extracted files or emits place names/coordinates.
- design-token-audit: inspect nested DTCG-style groups/types/alias references and duplicate keys; this is a limited structural audit, not full normative conformance testing.
- cron-schedule-audit: validate 5-field cron rows and preview three next UTC run times; no commands are run and no scheduler state is changed.

## Limits

- SQL audit/format: 5 MiB; 2,000 statements.
- GraphQL SDL: 5 MiB; 20,000 definitions.
- Jupyter notebook: 20 MiB; 50,000 cells; secret scan capped at 2 MiB of text.
- KML: 20 MiB; KMZ max 1,000 entries/120 MiB declared uncompressed and 10 MiB per KML document; at most 1,000,000 coordinate tuples.
- Design Tokens: 10 MiB JSON input; parser reports aggregate counts only.
- Cron: 2 MiB; 10,000 lines; preview limited to the next three UTC times per schedule, first 100 schedules.

## Upstream and licenses

- SQLGlot (MIT), GraphQL-core (MIT), croniter (MIT), Jupyter nbformat (BSD-3-Clause), Design Tokens Community Group (W3C document license/BSD-3-Clause test software), FastKML (LGPL-2.1 reviewed but not integrated).
- SQLGlot, GraphQL-core and croniter are installed conditionally on selected GitHub Actions jobs and as CI test dependencies; KML, notebook and design-token checks use Python stdlib.

## Acceptance gates

1. 352 unique TypeScript catalog IDs, 352 Python RUNNERS entries and 352 handler mappings.
2. Seven new processors have matching TypeScript/Python pipeline transitions; SQL formatter output feeds SQL static audit.
3. Python fixtures cover all seven tools, including privacy and no-execution behavior.
4. Type-check, Vitest, deployment-script checks, Python runner suite and Worker build pass.
5. Worker export/health smoke and Cloudflare deploy pass before counting 352 production processors.
6. Live Telegram upload/report/retry remains owner-level E2E after deployment.

Research notes: docs/TOOL-RESEARCH-2026-11-22.md