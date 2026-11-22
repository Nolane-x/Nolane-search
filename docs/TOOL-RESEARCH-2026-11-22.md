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
## Additional Wave 19 repositories reviewed

| Repository | Scope examined | License observed | Integration decision |
|---|---|---|---|
| [kbandla/dpkt](https://github.com/kbandla/dpkt) | PCAP and PCAPNG parsing, packet objects, Ethernet/IP/TCP/UDP protocol layers | BSD-style | Added offline packet counters only; no traffic replay or endpoint contact |
| [python-jsonschema/jsonschema](https://github.com/python-jsonschema/jsonschema) | JSON Schema draft selection, schema self-check, instance validation and error locations | MIT | Added local schema+data envelope validation; remote references are blocked |
| [rthalley/dnspython](https://github.com/rthalley/dnspython) | BIND zone file parser and record-set API | ISC | Added read-only zone parsing; $INCLUDE/$GENERATE and network DNS actions are blocked |
| [pyca/cryptography](https://github.com/pyca/cryptography) | X.509 PEM/DER certificate parsing, public-key and extension access | Apache-2.0 OR BSD-3-Clause | Added local certificate metadata/expiry/key strength summary; no trust-chain or revocation calls |
| [JohannesBuchner/ImageHash](https://github.com/JohannesBuchner/imagehash) | DCT/aHash/pHash/dHash/wHash and crop-resistant hashing | 2-Clause BSD | Reviewed as prior art; implemented a bounded 16×16 DCT pHash using the existing Pillow dependency to avoid NumPy/SciPy/PyWavelets runtime overhead |
| [quodlibet/mutagen](https://github.com/quodlibet/mutagen) | Rich audio tag parsing and editing | GPL-2.0-or-later | Not integrated; audio-tag completeness uses existing FFprobe metadata and never exports values |
| [W3C/epubcheck](https://github.com/w3c/epubcheck) | Official EPUB conformance validation and CLI | Repository LICENSE.md contains BSD-3-Clause-style terms | Reviewed for validation coverage; implemented a limited ZIP/XML structural audit without bundling its Java application |

## Wave 19 implementation

Eight focused processors were selected: PCAP/PCAPNG network audit, audio tag completeness, DCT perceptual image similarity, JSON Schema validation, EPUB package structure audit, Markdown quality audit, BIND DNS zone audit and X.509 certificate inspection.

The implementations are local-only and bounded. Dependencies are installed on CI for tests and conditionally on ephemeral GitHub Actions runner jobs: dpkt (BSD-style), jsonschema (MIT), dnspython (ISC) and cryptography (Apache-2.0 OR BSD-3-Clause). Image similarity uses original DCT code and existing Pillow; EPUB/Markdown use the Python standard library.
## Wave 20 repositories reviewed

| Repository | Scope examined | License observed | Integration decision |
|---|---|---|---|
| [kurtmckee/feedparser](https://github.com/kurtmckee/feedparser) | Mature RSS/Atom/JSON feed parsing and normalization | BSD-2-Clause | Reviewed as a reference; implementation uses stdlib ElementTree for a bounded offline structural audit |
| [KurtWeston/color-contrast-checker](https://github.com/KurtWeston/color-contrast-checker) | WCAG contrast ratio computation | MIT | Added WCAG 2.2 AA/AAA ratio checker using the relative-luminance formula |
| [zshnarz/image-metadata-toolkit](https://github.com/zshnarz/image-metadata-toolkit) | EXIF/GPS/IPTC/ICC metadata, privacy review, duplicate and similar-image workflows | MIT; Pillow dependency | Added metadata privacy presence/count audit using the existing Pillow dependency; no values or GPS coordinates are emitted |
| [jtesta/ssh-audit](https://github.com/jtesta/ssh-audit) | SSH client/server algorithm and policy auditing | MIT | Added offline public-key file inventory only; did not adopt remote server scanning or algorithm recommendation database |
| [darylldoyle/svg-sanitizer](https://github.com/darylldoyle/svg-sanitizer) | SVG sanitization and active-content handling | GPLv2 | Reviewed only; not integrated due license and security-scope considerations. Wave20 provides a read-only static SVG audit instead |
| [dhvcc/rss-parser](https://github.com/dhvcc/rss-parser) | RSS parser | GPL-3.0 | Not integrated; Wave20 uses an independent structural XML counter |

## Wave 20 implementation

Nine tools were selected: RSS/Atom feed audit, XML sitemap audit, robots.txt audit, JSONL profiler, image metadata privacy audit, SVG active-content audit, WCAG contrast checker, SSH public-key audit and ZIP checksum manifest.

No new third-party runtime package is required. RSS/Atom, sitemap, robots, JSONL, SVG and checksum use Python standard-library modules; image metadata reuses Pillow; SSH public keys reuse the cryptography package already installed for X.509.

The SVG sanitizer project and GPL-3.0 RSS parser were deliberately not integrated. The new SVG processor reports risky structures only; it is not a sanitizer.