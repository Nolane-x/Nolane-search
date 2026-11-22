# Wave 15 handoff — Spreadsheet and PDF privacy auditors

Date: 2026-11-22
Repository: https://github.com/Nolane-x/Nolane-search
Branch: feat/wave-fifteen-spreadsheet-pdf-privacy

## Scope

This wave adds two privacy-oriented processors. They are registered in source but must not be counted as production until PR CI, main CI, export/smoke and deployment all pass.

- xlsx-privacy-audit: scans XLSX cached values for email-like, Luhn-valid payment-card candidates, credential-like token patterns, IPv4, phone-like values in phone-named columns and sensitive headers. Reports sheet/column/cell coordinate/type/count only; never copies raw cell values.
- pdf-privacy-audit: scans existing PDF text layer for email-like values, Luhn-valid card candidates, labelled phone numbers, IPv4, identity-document-like markers and credential-like tokens. Reports page/type/count only; no OCR or raw text.

## Bounds and limitations

- XLSX: at most 100 sheets, 50,000 rows per sheet, 200 columns per sheet and 2,000,000 declared/scanned cells. Formula cells are inspected only through cached values; formula recalculation is not performed.
- PDF: at most 300 pages and 2,000,000 extracted text characters. Image-only/scanned pages may be missed because OCR is deliberately not run.
- Detection is heuristic and cannot prove that a value is personal data, a valid credential or a live payment card.
- No D1 schema migration, new secret or new external service is required. XLSX uses the existing openpyxl install gate and PDF uses the existing PyMuPDF base libraries.

## Acceptance gates

1. Catalog has 314 unique IDs and every ID is present in the Python runner allowlist, handler map and text-output allowlist.
2. TypeScript/Python pipeline transition graphs match exactly.
3. Python fixtures verify all expected categories and explicitly assert that raw email/card/token/phone values are absent from reports.
4. Type-check, Vitest, Python compile/unit tests and Worker build pass.
5. Cloudflare export/smoke and production deployment pass before calling 314 production tools.
6. Real Telegram upload/report/retry remains a separate owner-level end-to-end test.
