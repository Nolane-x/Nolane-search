# Wave 21 release handoff — Broader file, data and productivity tools

Date: 2026-11-22  
Repository: https://github.com/Nolane-x/Nolane-search  
Branch: \`feat/wave-twenty-one-expanded-tool-suite\`  
Status: merged and deployed to production on 2026-11-22.

## Goal

Expand the catalog beyond another set of static auditors. Wave 21 adds new document extraction, structured-data querying, network planning, visual generation, similarity analysis and columnar data interchange capabilities.

## Nine released processors

| ID | Capability | Input → output | Notes |
|---|---|---|---|
| \`pdf-table-extract\` | Detect and extract text/vector tables from PDFs | PDF → ZIP of CSV tables | Uses pdfplumber; maximum 200 pages, 200 tables, 20,000 total rows and 500,000 cells. Scanned-image tables are not OCR'd. |
| \`json-jmespath-query\` | Filter/project nested JSON using JMESPath | JSON query envelope → JSON | Envelope is \`{"query":"people[*].name","data":{...}}\`; expression maximum 4,096 characters, result maximum 20 MiB. No code evaluation. |
| \`ip-network-report\` | Normalize IPv4/IPv6 addresses and CIDRs | TXT → CSV | Offline Python \`ipaddress\`; maximum 2,000 networks; reports prefix, address count, private/global flags and overlap counts. No DNS or host contact. |
| \`barcode-generate\` | Generate Code 128 barcode images | TXT lines → ZIP of PNGs | 1–50 non-empty ASCII payloads, maximum 120 printable characters each. |
| \`docx-to-markdown\` | Convert common Word structure to Markdown | DOCX → MD | Preserves headings, paragraphs, common list styles, inline bold/italic/underline and tables. Does not render images, headers/footers or page layout. |
| \`pptx-notes-extract\` | Extract presenter notes by slide | PPTX → MD | Maximum 300 slides; extracts notes only, not visible slide body or embedded media. |
| \`fuzzy-match-report\` | Find near-duplicate lines | TXT/MD/CSV/log → CSV | RapidFuzz ratio, 85% threshold, 1,200-line and 5,000-pair bounds. Output intentionally contains compared lines. |
| \`csv-to-parquet\` | Convert CSV into compressed columnar storage | CSV → Parquet | DuckDB with Zstandard compression; cells remain strings to preserve leading zeroes; maximum 1,000,000 rows. |
| \`parquet-to-csv\` | Convert Parquet back to UTF-8 CSV | Parquet → CSV | DuckDB fixed read/export operations; no user SQL; maximum 1,000,000 rows. |

## Upstream research and licensing

| Upstream | License | Reused capability |
|---|---|---|
| [jsvine/pdfplumber](https://github.com/jsvine/pdfplumber) | MIT | PDF table and geometry extraction; no upstream code copied into the repository. |
| [jmespath/jmespath.py](https://github.com/jmespath/jmespath.py) | MIT | Declarative JSON query expression engine. |
| [WhyNotHugo/python-barcode](https://github.com/WhyNotHugo/python-barcode) | MIT | Code 128 barcode generation; Pillow is already present on the runner. |
| [duckdb/duckdb](https://github.com/duckdb/duckdb) | MIT | Embedded CSV/Parquet conversion with fixed SQL statements. |
| [rapidfuzz/RapidFuzz](https://github.com/rapidfuzz/RapidFuzz) | MIT | Efficient fuzzy string similarity. |
| [python-openxml/python-docx](https://github.com/python-openxml/python-docx) | MIT | Existing runner dependency reused for DOCX reading. |
| [scanny/python-pptx](https://github.com/scanny/python-pptx) | MIT | Existing runner dependency reused for slide notes. |
| Python standard library \`ipaddress\` | Python Software Foundation License | Offline IP/CIDR parsing and overlap logic. |

No upstream application source is vendored. Runtime dependencies are installed only in the relevant ephemeral GitHub Actions runner job; CI installs the same packages for tests.

## Integration and safety

All nine IDs are registered in:
- TypeScript \`TOOL_CATALOG\`;
- Python \`RUNNERS\` and \`TOOLS\`;
- TypeScript and Python pipeline-transition allowlists;
- the direct upload/job runner, with conditional dependencies;
- the catalog and runner regression tests.

Controls:
- uploaded files remain on the ephemeral runner;
- no user-provided SQL or source code is executed;
- no IP/DNS/network probes are performed by the IP report;
- PDF/Office parsing is bounded by file size and structure limits;
- generated outputs are constrained to the runner input directory and existing 45 MiB intermediate-output cap;
- fuzzy-match CSV contains user-supplied line text by design, so sensitive source files should not be uploaded to that operation.

## Release verification

1. TypeScript catalog contains 354 unique IDs.
2. Python \`RUNNERS\` and \`TOOLS\` contain exactly the same 354 IDs.
3. Worker and runner pipeline transition maps are identical.
4. Python fixtures cover PDF tables, JMESPath, IP/CIDR, barcode output, DOCX, PPTX notes, fuzzy matching and CSV ↔ Parquet.
5. TypeScript tests, Python runner tests, deployment-script checks and Worker build pass.
6. Only after main CI, Worker export/health smoke and Cloudflare deployment pass should the count be recorded as 354 production tools.
7. Owner-level Telegram checks remain necessary for representative PDF/DOCX/PPTX/CSV/TXT uploads and retries.

## Production release evidence

- PR [#73](https://github.com/Nolane-x/Nolane-search/pull/73) merged into \`main\`.
- Production commit: \`7709aac8173a90a661cea8ea99240ca34526ef8f\`.
- Main CI: [run 44992164320](https://github.com/Nolane-x/Nolane-search/actions/runs/44992164320) — success; 144 Python runner tests, TypeScript tests, type-check, deployment-script validation and Worker build.
- Worker export/smoke: [run 44992164270](https://github.com/Nolane-x/Nolane-search/actions/runs/44992164270) — success.
- Cloudflare deployment: [run 44992164238](https://github.com/Nolane-x/Nolane-search/actions/runs/44992164238) — success; Worker upload, runtime-secret upload and Telegram webhook verification.
- Worker Version ID: \`05af480c-6631-4402-8711-07bcba267bfe\`.
- D1 migration was skipped because no schema changes were introduced.
- Production catalog: 354 processors.

The deployment and webhook checks are complete. Real owner-level Telegram E2E still needs the user to upload representative files and inspect outputs / retry behavior. This is intentionally not represented as having been performed by CI.
