# Wave 32 handoff — semantic data and searchable PDF tools

Date: 2026-11-23
Repository: https://github.com/Nolane-x/Nolane-search
Branch: feat/wave-thirty-two-semantic-and-pdf-tools
Status: implemented, merged via PR #85 and deployed to production on 2026-11-23.

## Production baseline

Wave 31 production baseline was 438 tools. Wave 32 merged as `f9359406a25043220e51a90e33cc9a72c6fc7321` and increased the production catalog to **442 tools**. Main CI `45145755895`, Worker export/health smoke `45145756137` and Cloudflare deployment `45145755910` all passed. Worker Version ID: `ddfedcef-6feb-42da-97a3-e29c4fcfaa3e`.

## Scope

- **pdf-ocr-searchable**: create a searchable PDF with English/Vietnamese OCR, skip pages with existing text, auto-rotate and deskew.
- **rdf-graph-audit**: aggregate-only RDF profile for Turtle, N-Triples, N-Quads and TriG.
- **shacl-validate**: offline SHACL Core validation for a ZIP with exactly data.ttl and shapes.ttl.
- **cron-schedule-audit**: validate five-field cron and preview three UTC occurrences.

## Implementation

- Python handlers live in tools/wave32.py; focused unit tests live in tools/test_wave32.py.
- TypeScript catalog, upload inference and pipeline transitions are mirrored with Python runner allowlist, handler registry, text-output registry and pipeline transitions.
- The PDF OCR tool uses a neutral temporary working directory and suppresses raw process output. OCRmyPDF is installed only when the selected job requires it.
- RDF parsers are limited to offline text syntaxes; graph terms and literal values are never included in reports.
- SHACL package members are not extracted to disk. Imports, SPARQL/JavaScript constraints and rules are disabled/rejected.
- Cron reports do not echo expressions or command text and never invoke a scheduler.
- No Worker/D1 schema or secret changes are planned.

## Dependencies and upstream licenses

- OCRmyPDF 17.14.2 — MPL-2.0.
- RDFLib 7.6.0 — BSD-3-Clause.
- pySHACL 0.40.2 — Apache-2.0.
- croniter 7.0.0 — MIT.

All runtime packages are pinned. The CI dependency set includes RDFLib, pySHACL and croniter; the runner installs optional dependencies only for the selected processor.

## Verification gates

1. GitHub PR CI must pass type-checking, Vitest, Python unittest discovery, runner/catalog/handler parity and Worker build.
2. Verified after merge: Worker export/health smoke and Cloudflare deployment both passed; production count is 442.
3. Owner-level Telegram E2E remains necessary: upload test fixtures for all four processors, inspect output files/reports and exercise /tool_retry.
4. Telegram Archive backup/restore remains a separate owner-level recovery test. Wave 32 does not change its metadata-only backup semantics.

Detailed upstream evaluation and limits: docs/TOOL-RESEARCH-2026-11-23.md.
