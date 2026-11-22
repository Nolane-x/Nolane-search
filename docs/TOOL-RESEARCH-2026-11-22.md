# Open-source tool research — 2026-11-22

## Research objective

Expand Nolane Tools beyond developer/security auditors. Research covered general CLI catalogues, file conversion suites, subtitle utilities, calendar/contact parsers, data transformation, HTTP inspection, font tooling, QR generation and file-management applications.

## Repositories reviewed

| Repository | Upstream project scope | License observed | Nolane Search direction |
|---|---|---|---|
| [k6w/polytool](https://github.com/k6w/polytool) | Broad everyday CLI toolbox: data, text, color, units, QR, files, image, video and PDF | MIT | QR generation and color conversion; one processor per focused task |
| [smolkapps/srt-tools](https://github.com/smolkapps/srt-tools) | SRT/VTT shift, conversion, merge, repair, scale and timing statistics | MIT | Safe SRT/VTT repair with integer millisecond timestamps |
| [py-vobject/vobject](https://github.com/py-vobject/vobject) | iCalendar and vCard parsing/generation | Apache-2.0 | Calendar structure and contact privacy reports through the library API |
| [qarmin/czkawka](https://github.com/qarmin/czkawka) | Duplicate/empty/large/broken files, similar media, invalid links and metadata cleanup | MIT | Broader later roadmap for archive/media inspection; directory-scanning model not copied into single-upload jobs |
| [johnkerl/miller](https://github.com/johnkerl/miller) | Streaming transforms and statistics for CSV, TSV, JSON and JSON Lines | BSD-2-Clause | Data operations should focus on larger/heterogeneous datasets rather than trivial format aliases |
| [lincolnloop/python-qrcode](https://github.com/lincolnloop/python-qrcode) | Pure-Python QR generation, PNG/SVG output and error correction | BSD-3-Clause | PNG QR generation from a bounded text payload |
| [fonttools/fonttools](https://github.com/fonttools/fonttools) | Font metadata and font-table inspection/editing | MIT | Read-only TTF/OTF/WOFF metadata and embedding flags |
| [Redocly/redocly-cli](https://github.com/Redocly/redocly-cli) | OpenAPI/Swagger/AsyncAPI lint, validation, bundling and documentation | MIT | Bounded, local-only OpenAPI contract audit; no remote reference fetching |
| [mitmproxy/mitmproxy](https://github.com/mitmproxy/mitmproxy) | HTTP(S), HTTP/2 and WebSocket inspection and HAR capture workflows | MIT | HAR privacy exposure audit that never echoes captured values |
| [imie/filee](https://github.com/imie/filee) | Offline conversion across documents, media, archives, fonts, CAD and geospatial formats | MIT | Inspiration for category breadth; not adopted as a monolithic desktop runtime |
| [hjelev/cli](https://github.com/hjelev/cli) | Curated Terminal Index: 333 CLI/TUI tools across 23 categories at time of review | MIT | Discovery index for future file, networking, productivity and media tools |

## Wave 18 implementation

Ten focused processors were selected for this batch: HAR privacy audit, iCalendar calendar audit, vCard privacy audit, GPX track report, GeoJSON structure audit, QR code generation, font metadata inspection, SRT/VTT repair, OpenAPI contract audit and HEX/RGB color conversion.

The implementations are original integrations in the Nolane runner. The project does not copy upstream source files or vendor upstream applications. Third-party Python packages are installed only for the processors that need them, on ephemeral GitHub-hosted runners.

## Engineering and privacy rules

- Keep uploaded files on the ephemeral runner; do not commit them or write their contents to D1.
- Keep credentials, HAR values, contact details, calendar details and geospatial coordinates out of summaries and logs.
- Use bounded input sizes, entry counts, body scans and parser nesting.
- Avoid live network lookups, remote refs resolution and arbitrary code execution.
- Keep TypeScript catalog IDs, Python allowlist/handlers, text-output registry and pipeline transitions in parity.
- Do not count a processor as production before CI, Worker export/smoke and production deployment pass.
- Do not equate structural heuristics with legal, security or standards certification.