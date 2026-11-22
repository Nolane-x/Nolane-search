# Wave 14 handoff — Document, privacy and archive auditors

Date: 2026-11-22
Repository: https://github.com/Nolane-x/Nolane-search
Branch: feat/wave-fourteen-file-auditors

## Scope

Wave 14 proposes four bounded processors. Production baseline remains 308 until PR CI, main CI, Worker export/smoke and production deployment all pass.

- docx-audit: structure audit for heading hierarchy, table first rows, image alternative text, unsafe external-link schemes and tracked change markers. Reports counters only; no paragraph/table contents.
- pptx-audit: slide counters, missing titles, empty slides, dense text, repeated/long titles, explicitly small font runs and images lacking alt text. No rendering or actual clipping detection.
- csv-privacy-audit: email-like values, Luhn-valid 13–19 digit card candidates, IPv4, phone-like values in phone-named columns and sensitive-looking headers. Reports column/type/count/row numbers only; never raw cell values.
- archive-security-audit: ZIP/TAR metadata preflight for absolute/traversal paths, duplicate/case-colliding paths, links/special entries, encrypted ZIP members, extreme compression ratios, large members, nested archives and executable/script suffixes. No extraction or member-content reads.

## Limits

- Upload remains bounded by the runner's 20 MiB limit.
- DOCX: at most 20,000 paragraphs, 1,000 tables and 2,000 inline images.
- PPTX: at most 300 slides. Font-size warnings use explicitly set run sizes only; no rendering, clipping or full accessibility validation.
- CSV: at most 50,000 records and 200 columns; reports metadata only. Header and phone checks are heuristic.
- Archive: at most 10,000 entries; no extraction. Executable extensions are review signals, not a malware verdict.
- Office dependencies installed only for DOCX/PPTX/Office jobs; CI adds these libraries for fixture tests.
- No new secret, external service or database migration.

## Acceptance gates

1. TypeScript registry has 312 unique IDs.
2. TypeScript catalog, Python RUNNERS, Python TOOLS handlers, docs and transition graphs match.
3. Python tests cover all four tools, especially the CSV raw-value non-disclosure and archive path/collision/ratio findings.
4. Vitest, type-check, Python compile/unit tests and Worker build pass.
5. Cloudflare export/smoke and production deploy pass before counting 312 as production.
6. Live Telegram upload/response/retry for representative DOCX, PPTX, CSV and ZIP remains owner-level E2E; CI does not prove it.
