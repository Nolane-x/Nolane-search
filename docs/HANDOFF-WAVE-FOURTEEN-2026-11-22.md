# Wave 14 release handoff — Document, privacy and archive auditors

Date: 2026-11-22
Repository: https://github.com/Nolane-x/Nolane-search
PR: https://github.com/Nolane-x/Nolane-search/pull/64
Production source commit: ccd74ad52825c498413622e571cfb2970da4b995

## Release state

Wave 14 is merged and deployed. The catalog is now 312 production processors (up from 308). Cloudflare Worker version 71, ID `8c86c559-30c2-4ba4-a7e4-5365751df737`, receives 100% traffic through deployment `9194f2a0-9974-4961-8433-9109066cf4b1`.

- PR CI #64: passed — https://github.com/Nolane-x/Nolane-search/actions/runs/44966857743
- Main CI #286: passed — https://github.com/Nolane-x/Nolane-search/actions/runs/44966971539
- Worker export and production smoke test #110: passed — https://github.com/Nolane-x/Nolane-search/actions/runs/44966971507
- Production deployment #117: passed — https://github.com/Nolane-x/Nolane-search/actions/runs/44966971557
- Live `/health`: `ok: true`, database `reachable`; four provider-key routes and nine model routes reported. This is not proof every upstream key currently has quota or successful inference.
- Catalog parity: 312 unique TypeScript IDs, 312 Python runner allowlist IDs, 312 Python handlers and 752 matching pipeline edges.
- Python runner test suite: 104 tests passed; TypeScript type-check, Vitest, deployment-script checks and Worker build passed.
- No D1 schema migration or new secret/external dependency was required. Office dependencies are installed for relevant GitHub-hosted runner jobs.

## Added tools

- `docx-audit`: heading hierarchy, empty table first rows, missing image alt text, unsafe external hyperlinks and tracked changes/comments. No paragraph/table content is emitted.
- `pptx-audit`: per-slide text/image counters, missing/duplicate/long titles, blank or dense slides, explicitly set font runs below 12 pt and missing image alt text. No rendering/clipping certification.
- `csv-privacy-audit`: email-like patterns, Luhn card candidates, IPv4, phone-like values in phone-named columns and sensitive header names. Reports column/type/count and sample row numbers, never raw cell values.
- `archive-security-audit`: ZIP/TAR path traversal/absolute paths, duplicates/case collisions, links/special entries, encrypted ZIP entries, extreme ratios, large files, nested archive and executable/script suffixes. Metadata-only, no extraction/exec.

## Limits and interpretation

- Runner upload remains capped by 20 MiB.
- DOCX checks are structural heuristics, not a full accessibility/WCAG certification or rendered Word layout audit.
- PPTX is capped at 300 slides; font-size warnings only cover explicit run size values and do not account for theme/master inheritance, overlap or clipping.
- CSV is capped at 50,000 records and 200 columns. Pattern/header detection can have false positives and false negatives; raw values are withheld from the report.
- ZIP/TAR is capped at 10,000 entries; no member content is read. Executable/script extensions are review signals, not a malware verdict.

## Remaining real-world verification

Live Telegram end-to-end behavior remains to be verified by uploading representative DOCX, PPTX, CSV and ZIP files, checking that the bot delivers the expected report/artifact, and exercising retry. Successful CI, webhook registration and `/health` do not prove that full Telegram user journey.

## Continue from here

- Keep `main` at 312 production tools unless the next addition has a genuinely useful distinct capability and complete TypeScript/Python/docs/pipeline/test parity.
- For next file-tool wave, prioritize real user workflows that output usable artifacts, robust malformed-file handling, bounded resource usage and privacy-safe reports rather than cosmetic count growth.
