# Wave 16 release handoff — Office and PDF active-content security audits

Date: 2026-11-22
Repository: https://github.com/Nolane-x/Nolane-search
PR: https://github.com/Nolane-x/Nolane-search/pull/66
Production source commit: cae8ddd629f5bccc30199e7d036dd89377cf7b6f

## Release state

Wave 16 is merged and deployed. Nolane Search now has 316 production processors (up from 314). Cloudflare Worker version 73, ID `03210f3c-6bd5-47a9-ab1d-deeac1fca8a1`, receives 100% traffic through deployment `c39bb7f6-fb16-4749-ac9c-a540400483de`.

- PR CI: passed — https://github.com/Nolane-x/Nolane-search/actions/runs/44975448150
- Main CI #294: passed — https://github.com/Nolane-x/Nolane-search/actions/runs/44975539445 (107 Python runner tests, type-check, Vitest, deployment-script checks and Worker build)
- Cloudflare export and production smoke #112: passed — https://github.com/Nolane-x/Nolane-search/actions/runs/44975539435
- Production deploy #119: passed — https://github.com/Nolane-x/Nolane-search/actions/runs/44975539446
- Fresh `/health`: `ok: true`, database `reachable`; four AI provider routes and nine model routes reported. This is configuration/route health, not live quota/inference proof for every provider.
- Registry parity: 316 unique TypeScript catalog IDs, 316 Python RUNNERS entries, 316 Python handlers and 760 matching TS/Python transition edges.
- No new Python package, D1 schema migration, secret or external service was required.

## Added tools

- `office-active-content-audit`: OOXML DOCX/DOCM/DOTX/DOTM/PPTX/PPTM/PPSX/PPSM/POTX/POTM/XLSX/XLSM/XLTX/XLTM package audit for VBA project binaries, macro-enabled content types, ActiveX, OLE/embedded parts, customUI, external relationships/workbook links/connections, unsafe URI schemes, encrypted members and traversal-like paths. Only ZIP metadata and bounded relationship/content-type XML are read; no macro/object is opened or executed.
- `pdf-active-content-audit`: PDF indirect object and link metadata scan for JavaScript/JS, OpenAction, Additional Actions, Launch, EmbeddedFiles/Filespec, RichMedia, AcroForm/XFA, SubmitForm/ImportData, remote GoTo and URI actions. Reports counts only; no action is executed and attachments are not opened/extracted.

## Limits and interpretation

- Office packages: maximum 20,000 ZIP entries, 500 MiB declared expanded size, 2,000 relationship parts and 12 MiB total relationship/content-type XML reads. DTD/entity declarations are rejected for parsed XML.
- PDF: maximum 300 pages, 15,000 indirect objects and 3,000,000 object metadata characters. Oversized object dictionaries are truncated for marker scans; streams are not decoded or rendered.
- URL targets, macro code, attachment names and content are not copied into reports.
- These markers can be legitimate in normal documents. Results are static review signals, not malware scanning or a guarantee that a file is safe.

## Remaining real-world verification

Live Telegram E2E remains to be verified by uploading representative Office macro-enabled/normal files and PDFs, checking delivered reports and exercising retry. CI, webhook registration and `/health` do not prove the entire Telegram user journey.

## Next direction

- Keep `main` at 316 production tools unless new additions provide a genuinely distinct, useful capability and complete TypeScript/Python/handler/pipeline/test parity.
- Prioritize robust malformed-input handling, actual useful output artifacts, bounded parsing and privacy-safe reports rather than count-only additions.
