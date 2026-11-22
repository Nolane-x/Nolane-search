# Wave 16 handoff — Office and PDF active-content auditors

Date: 2026-11-22
Repository: https://github.com/Nolane-x/Nolane-search
Branch: feat/wave-sixteen-office-pdf-active-content

## Scope

Two bounded static auditors are registered in source; do not count them as production until all PR/main CI, Worker export/smoke and deployment gates pass.

- office-active-content-audit: OOXML DOCX/DOCM/DOTX/DOTM/PPTX/PPTM/PPSX/PPSM/POTX/POTM/XLSX/XLSM/XLTX/XLTM package audit for VBA project binaries, macro-enabled content types, ActiveX, OLE/embedded parts, customUI, external relationships/workbook links/connections, unsafe URI schemes, encrypted members and traversal-like paths. Reads only ZIP metadata and bounded relationships/content-type XML; does not open/execute embedded objects.
- pdf-active-content-audit: scans PDF indirect object dictionaries and link metadata for JavaScript/JS, OpenAction, Additional Actions, Launch, EmbeddedFiles/Filespec, RichMedia, AcroForm/XFA, SubmitForm/ImportData, remote GoTo and URI actions; reports marker counts and embedded file/widget counts only. Does not execute actions or open/extract attachments.

## Safety bounds and interpretation

- Office: maximum 20,000 ZIP entries, 500 MiB declared expanded size, 2,000 relationship parts and 12 MiB total relationship/content-type XML read. DTD/entity declarations are rejected for parsed XML. No archive extraction.
- PDF: maximum 300 pages, 15,000 indirect objects and 3,000,000 total object-dictionary characters. Very large individual dictionaries are truncated for marker scanning; streams are not decoded or rendered.
- URI targets, macro code and attachment names/content are not included in the report.
- Markers may be legitimate in normal enterprise documents. These are static review signals, not malware scanning or a safety guarantee.
- No new Python packages, D1 migration, secret or external service should be required; existing PyMuPDF is installed in the base runner job.

## Acceptance gates

1. 316 unique TypeScript catalog IDs, 316 Python RUNNERS entries, 316 Python handlers and 316 TEXT_OUTPUT_TOOLS entries.
2. TypeScript and Python transition edges match exactly.
3. Python fixtures cover VBA/ActiveX/OLE/external relationship findings without leaking URLs/macro contents, plus PDF JavaScript/OpenAction/embedded-file findings without leaking action source or attachment names/content.
4. Type-check, Vitest, deployment-script checks, Python suite and Worker build pass.
5. Cloudflare Worker build/export/smoke and production deployment pass before increasing production count above 314.
6. Real Telegram upload/report/retry with representative Office/PDF files remains owner-level E2E and is not proved by CI.
