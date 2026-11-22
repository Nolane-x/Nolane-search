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

## Wave 21 repositories reviewed

| Repository | Scope examined | License observed | Integration decision |
|---|---|---|---|
| [jsvine/pdfplumber](https://github.com/jsvine/pdfplumber) | PDF text geometry and table extraction | MIT (\`LICENSE.txt\`) | Added bounded extraction of detected text/vector tables to CSV; no OCR of scanned tables and no upstream source copied. |
| [jmespath/jmespath.py](https://github.com/jmespath/jmespath.py) | Declarative JSON query language and Python runtime | MIT | Added a query+data envelope processor; expression execution is declarative and bounded, not arbitrary Python evaluation. |
| [WhyNotHugo/python-barcode](https://github.com/WhyNotHugo/python-barcode) | Standards-based 1D barcode generation | MIT (project metadata) | Added Code 128 PNG generation for bounded printable-ASCII payloads; Pillow was already available. |
| [duckdb/duckdb](https://github.com/duckdb/duckdb) | Embedded analytical SQL engine and Parquet/CSV interchange | MIT | Added fixed CSV ↔ Parquet conversion only. No SQL text is accepted from the user; CSV columns remain strings on import to preserve leading zeros. |
| [rapidfuzz/RapidFuzz](https://github.com/rapidfuzz/RapidFuzz) | High-performance string similarity and matching | MIT | Added bounded near-duplicate line pairs with similarity scores; CSV output intentionally contains compared user-provided lines. |
| [python-openxml/python-docx](https://github.com/python-openxml/python-docx) | DOCX document object model | MIT | Reused existing runner dependency for DOCX-to-Markdown conversion; no new package required by the runner. |
| [scanny/python-pptx](https://github.com/scanny/python-pptx) | PowerPoint slide and notes access | MIT | Reused existing runner dependency to extract speaker notes only. |
| Python \`ipaddress\` | IP address, network and subnet primitives | Python Software Foundation License | Uses the standard library for local IPv4/IPv6/CIDR normalization and overlap reporting; no DNS or network activity. |

### Wave 21 selection rationale

The nine candidates were selected to add capabilities that were absent from the 345-tool Wave 20 catalog rather than creating more cosmetic text aliases. They span PDF information extraction, declarative data selection, network planning, barcode generation, Office interoperability, fuzzy matching and columnar data interchange.

The integrations call upstream libraries through their public APIs; they do not copy upstream project source into Nolane Search. Each optional dependency is installed only when a matching processor is requested, while CI installs the complete test dependency set.

### Wave 21 exclusions and limits

- PDF table extraction uses text/vector geometry and does not claim reliable table recognition on scanned images.
- JMESPath is a JSON selection language, not a code execution engine.
- IP/CIDR reports are offline; no DNS, socket or remote reachability checks are performed.
- Barcode generation is limited to Code 128 printable ASCII; 2D barcode formats remain a separate candidate.
- DOCX-to-Markdown is structural conversion, not pixel-faithful page rendering.
- PPTX extraction reads presenter notes and intentionally excludes slide-body text.
- Fuzzy matching is bounded to 1,200 lines and reports source strings in its CSV output.
- Parquet conversions use fixed DuckDB operations, with a one-million-row ceiling and no user SQL.


## Wave 22 repositories reviewed

| Repository | Scope examined | License verified | Integration decision |
|---|---|---|---|
| [tobymao/sqlglot](https://github.com/tobymao/sqlglot) | SQL parsing, formatting and transpilation across dialects | MIT | Added SQLGlot formatter/transpiler; supports a bounded dialect allowlist and never executes SQL. |
| [sqlfluff/sqlfluff](https://github.com/sqlfluff/sqlfluff) | SQL linting and dialect-aware style rules | MIT | Added SQL lint report with rule/line/column metadata; source query is not copied into the report. |
| [PyCQA/bandit](https://github.com/PyCQA/bandit) | Static Python security pattern scanning | Apache-2.0 | Added single-file Bandit scan through a fixed subprocess invocation; Python source is parsed but never executed. |
| [hgrecco/pint](https://github.com/hgrecco/pint) | Physical quantities, unit registry and dimensional conversion | BSD-3-Clause | Added bounded quantity-to-target conversion with dimensionality checking and a restricted input grammar. |
| [mikedh/trimesh](https://github.com/mikedh/trimesh) | Triangle mesh loading, topology and geometry inspection | MIT | Added offline STL/OBJ/PLY/OFF/GLB/GLTF/3MF inspection with vertex/face and expensive-operation limits. |
| [mozman/ezdxf](https://github.com/mozman/ezdxf) | DXF CAD document parsing and auditor | MIT | Added DXF layer/entity/block inventory and local audit; does not render or resolve external references. |
| [GeospatialPython/pyshp](https://github.com/GeospatialPython/pyshp) | ESRI Shapefile reader and writer | MIT | Added ZIP-based .shp/.shx/.dbf structure audit; attribute record values are not emitted. |
| [izimobil/polib](https://github.com/izimobil/polib) | GNU gettext PO/POT catalog parsing | MIT | Added localization completeness, plural and placeholder consistency audit without copying translation strings. |
| [jupyter/nbformat](https://github.com/jupyter/nbformat) | Jupyter Notebook schema and in-memory cell model | BSD-3-Clause | Added schema/cell/output audit and a separate output-stripping conversion; no notebook cells are executed. |
| [bigcat88/pillow_heif](https://github.com/bigcat88/pillow_heif) | HEIF/HEIC decoding and Pillow integration | BSD-3-Clause | Added HEIC/HEIF to JPEG/PNG conversion; only frame zero is kept and camera/GPS metadata is not copied. |
| [pyproj4/pyproj](https://github.com/pyproj4/pyproj) | PROJ coordinate reference systems and transformations | MIT | Added EPSG-to-EPSG transformation for bounded coordinate arrays; PROJ network access is disabled. |
| [Kozea/tinycss2](https://github.com/Kozea/tinycss2) | CSS tokenization and syntax parsing | BSD-3-Clause | Added CSS rule/declaration quality counts, parser errors, duplicate selectors and external reference counts. |

### Standard-library processors

KML-to-GeoJSON, subtitle timing QA, JSON-LD structured-data auditing, HTML local-link checking and CSS-free HTML parsing use Python's standard library (ElementTree, HTMLParser, json, csv, zipfile, urllib.parse and regular expressions). KML rejects DTD/entity declarations; HTML and local-link tools do not fetch external URLs; archive members are inspected in memory under explicit count/expanded-size limits.

### Wave 22 exclusions and selection notes

- [frictionlessdata/frictionless-py](https://github.com/frictionlessdata/frictionless-py) (MIT) was reviewed for Data Package/Table Schema validation. It was deferred because the framework brings a broad dependency graph; a narrower, explicit schema-contract use case should be selected before adding it.
- [Breakthrough/PySceneDetect](https://github.com/Breakthrough/PySceneDetect) (BSD-3-Clause) was reviewed but not added because Nolane already has FFmpeg-based scene/frame extraction; the incremental capability did not justify another video-processing dependency in this wave.
- [nschloe/meshio](https://github.com/nschloe/meshio) (MIT) was reviewed for mesh format conversion. The initial 3D capability uses trimesh for inspection only; a separate mesh conversion workflow can be evaluated later if format conversion proves useful.
- [python-babel/babel](https://github.com/python-babel/babel) (BSD-3-Clause) and [html5lib/html5lib-python](https://github.com/html5lib/html5lib-python) (MIT) were reviewed. Gettext parsing is handled by polib, and current HTML metadata/link metrics are handled by a bounded standard-library parser, so neither package was added.

No upstream project source is vendored. Runtime packages are installed only when a matching tool is selected on the ephemeral GitHub Actions runner; CI installs the set for regression testing. The feature branch adds 17 processors, but they remain candidates until CI, Worker export/health smoke and Cloudflare deployment all pass.
