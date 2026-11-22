# Wave 15 release handoff — Spreadsheet and PDF privacy auditors

Date: 2026-11-22
Repository: https://github.com/Nolane-x/Nolane-search
PR: https://github.com/Nolane-x/Nolane-search/pull/65
Production source commit: f94cc153936de383e629ed92fcd0fab011883b41

## Release state

Wave 15 is merged and deployed. The catalog is now 314 production processors (up from 312). Cloudflare Worker version 72, ID `ec64a6ca-e7a8-402b-88c4-e06f0d50c294`, receives 100% traffic through deployment `23d28228-ab44-41e7-a0ee-a9eeb5fb0641`.

- PR CI final-head run: passed — https://github.com/Nolane-x/Nolane-search/actions/runs/44967612153
- Main CI #288: passed — https://github.com/Nolane-x/Nolane-search/actions/runs/44967710533 (105 Python runner tests plus TS/Vitest/type-check/Worker build)
- Cloudflare export and production smoke #112: passed — https://github.com/Nolane-x/Nolane-search/actions/runs/44967710414
- Production deploy #119: passed — https://github.com/Nolane-x/Nolane-search/actions/runs/44967710386
- Fresh `/health`: `ok: true`, database `reachable`; four AI provider routes and nine model routes reported. This is route/configuration health, not live quota/inference confirmation for every provider.
- Registry parity: 314 unique TypeScript catalog IDs; 314 Python RUNNERS; 314 Python handlers; 756 matching TS/Python pipeline edges.
- No D1 schema migration, new secret or external service was required.

## Added tools

- `xlsx-privacy-audit`: email-like, Luhn-valid card candidates, credential-like token patterns, IPv4, phone-like values in phone-labelled columns and sensitive headers. Reports sheet, column, cell coordinates, type and count, never raw cell values. Reads cached formula results only.
- `pdf-privacy-audit`: email-like, Luhn card candidates, labelled phone values, IPv4, identity-document-like and credential-like patterns in the PDF text layer. Reports page/type/count only; never copies raw values or surrounding text; no OCR.

## Bounds and limitations

- XLSX: at most 100 sheets, 50,000 rows per sheet, 200 columns per sheet and 2,000,000 declared/scanned cells. Formula cells are inspected only through cached values; no formula recalculation.
- PDF: at most 300 pages and 2,000,000 extracted text characters. Image-only/scanned pages may be missed because OCR is deliberately not run.
- All detections are heuristics and cannot prove personal-data identity, valid credentials or active payment cards.
- CI tests assert raw email, card, token and phone examples do not appear in reports.

## Remaining real-world verification

Live Telegram E2E remains to be verified by uploading representative XLSX and PDF files, checking the bot's delivered reports, and exercising retry. CI, webhook registration and `/health` do not prove the complete Telegram user journey.

## Continue from here

- Keep main at 314 production tools unless the next addition provides a genuinely distinct user capability and full catalog/runner/pipeline/test parity.
- For the next wave, prioritize practical file outputs, robust malformed-input handling, bounded resource use and privacy-safe reporting rather than cosmetic count growth.
