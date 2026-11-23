# Wave 32 handoff — semantic data and searchable PDF tools

Date: 2026-11-23
Repository: https://github.com/Nolane-x/Nolane-search
Branch: feat/wave-thirty-two-semantic-and-pdf-tools
Status: implementation branch; not merged or deployed.

## Production baseline

Production remains **438 tools** on Wave 31 (bfc107d1f299b9ae4b7c557fbe4fea0e3eee6599). This branch has four additional catalog entries (442 registered on the branch) and must not be described as production until main CI, Worker export/health smoke and Cloudflare deployment pass after merge.

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
2. Worker export/health smoke and Cloudflare deploy must pass after merge before updating the production count from 438.
3. Owner-level Telegram E2E remains necessary: upload test fixtures for all four processors, inspect output files/reports and exercise /tool_retry.
4. Telegram Archive backup/restore remains a separate owner-level recovery test. Wave 32 does not change its metadata-only backup semantics.

Detailed upstream evaluation and limits: docs/TOOL-RESEARCH-2026-11-23.md.
