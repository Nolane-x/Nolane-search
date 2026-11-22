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


## Wave 23 — Scientific data, observability, music, manufacturing and schema tooling

| Repository / specification | Scope reviewed | License / provenance | Design decision |
|---|---|---|---|
| [h5py/h5py](https://github.com/h5py/h5py) | Python interface to HDF5 scientific containers | BSD-3-Clause | Use h5py as a read-only metadata adapter; inspect shapes/dtypes/compression only, skip external/soft links, never load tensor values. |
| [graphql-python/graphql-core](https://github.com/graphql-python/graphql-core) | GraphQL language parser and schema validator | MIT | Use graphql-core for local SDL parse/schema validation only; do not run resolvers or remote introspection. |
| [mido/mido](https://github.com/mido/mido) | Standard MIDI File and MIDI message parsing | MIT | Implement a bounded read-only SMF chunk/event scanner; no hardware backend, synth or playback. |
| [Prometheus alerting/recording rule docs](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/) | YAML groups, alert/record rules, expressions, labels and annotations | Official format documentation | Audit rule structure and common alert metadata; do not evaluate PromQL or expose labels/query text. |
| [prometheus/prometheus](https://github.com/prometheus/prometheus) | Prometheus server, rule format and promtool validation workflows | Apache-2.0 | Use the documented rules model as a reference; no Prometheus binary or daemon is installed. |
| [grafana/grafana](https://github.com/grafana/grafana) | Dashboard JSON model, panel nesting and datasource references | Upstream project reference; no source copied | Count dashboard structures and duplicate IDs only; withhold dashboard UID, datasource URLs, queries and text-panel values. |
| [apache/avro](https://github.com/apache/avro) | Avro schema definitions and named types | Apache-2.0 | Add a bounded JSON structural audit for records, fields, enums, fixed, arrays, maps and union branches; label it as non-complete validation. |
| [protocolbuffers/protobuf](https://github.com/protocolbuffers/protobuf) | Protocol Buffers language and field-number constraints | BSD-3-Clause | Add an independent lexical scan for declarations and invalid/reserved field-number ranges; do not compile with protoc. |
| [Knio/pynmea2](https://github.com/Knio/pynmea2) | NMEA 0183 sentence parsing and checksum patterns | MIT | Implement checksum and RMC/GGA coordinate-format checks without persisting or printing positions/timestamps. |
| [ansible/ansible-lint](https://github.com/ansible/ansible-lint) | Ansible playbook static review conventions | GPL-3.0; consulted only | Implement a small independent, value-redacting policy audit using the existing SafeLoader; no upstream code vendored and no playbook run. |
| [MusicXML documentation](https://www.musicxml.com/) | MusicXML score-partwise and compressed MXL structure | Format specification | Parse XML metadata and count musical elements, reject DTD/entity declarations, and suppress score names/lyrics. |
| [MarlinFirmware/Marlin](https://github.com/MarlinFirmware/Marlin) | Common G-code command families used by 3D printers | GPL-3.0; command conventions only | Add a static command/axis/feed/spindle counter; this is not a machine safety simulation or certification. |

### Wave 23 architecture and safety

All twelve processors live in the separate tools/wave23.py module to keep the mature runner's processor implementations organized. They return bounded text reports into the existing ephemeral runner input directory. The Python allowlist, handler map, pipeline transitions and TypeScript catalog are mirrored. h5py and graphql-core are conditional runner dependencies; PyYAML is installed for the two new YAML auditors by the existing YAML dependency step. No upstream implementation source is vendored.

The report design intentionally avoids user payload disclosure: G-code axis values are aggregated to ranges; MIDI reports counts/ticks; MusicXML omits titles/lyrics/instrument names; BibTeX omits citations and DOI values; NMEA omits all positions and timestamps; Ansible omits task/module values; Prometheus omits alert names/PromQL/labels; Grafana omits UID/URL/query text; HDF5 omits object paths/attributes/data; Avro/GraphQL/Protobuf omit schema identifiers and field names. These controls do not replace user-side review of original files.

Wave 23 merged as PR #75 (commit `32f2fbb4e6936a5caea0bf552e337c852797a1e7`) and is deployed to Cloudflare Worker Version 80 (`f30ef26b-02c1-4d57-922a-acf3e698669d`), with 100% production traffic. Main CI [45013947086](https://github.com/Nolane-x/Nolane-search/actions/runs/45013947086) passed 25 Vitest files and 175 Python runner tests; Worker export [45013946991](https://github.com/Nolane-x/Nolane-search/actions/runs/45013946991) and Cloudflare deployment [45013946981](https://github.com/Nolane-x/Nolane-search/actions/runs/45013946981) passed. Live Telegram upload/report/retry remains an owner-level end-to-end check.


## Wave 24 — Document interoperability, geospatial storage, creative projects and automation exports

| Specification / upstream | Scope reviewed | License / provenance | Design decision |
|---|---|---|---|
| [OASIS OpenDocument 1.3 Package Specification](https://docs.oasis-open.org/office/OpenDocument/v1.3/os/part3-packages/OpenDocument-v1.3-os-part3-packages.html) and [eea/odfpy](https://github.com/eea/odfpy) | ODT/ODS/ODP ZIP package ordering, MIME declaration, manifest and XML structure | ODF is an OASIS standard; odfpy offers GPL-2.0-or-later or Apache-2.0 | Inspect package/manifest and selected XML with stdlib ZIP/XML; no odfpy code or schema is vendored. |
| [OASIS XLIFF 2.1](https://docs.oasis-open.org/xliff/xliff-core/v2.1/os/xliff-core-v2.1-os.html) | Translation units/segments, source/target, state and inline placeholder elements | OASIS standard | Count empty targets, unit states and placeholder-count drift without emitting source or translation text. |
| [RFC 4155](https://www.rfc-editor.org/rfc/rfc4155) | mbox mailbox interchange format | IETF RFC | Use Python mailbox/email parsers to report counts and header presence only; never print message or attachment content. |
| [OGC GeoPackage standard](https://www.ogc.org/standard/geopackage/) and [GeoPackage specification](https://www.geopackage.org/spec/) | SQLite application ID, metadata tables, feature/geometry columns and CRS catalog | OGC standard | Open SQLite immutable/read-only; count table records and geometry-type categories but never read geometry, bounds or attributes. |
| [Mapbox MBTiles specification](https://github.com/mapbox/mbtiles-spec) | SQLite metadata/tiles layout, zoom levels, tile coordinates and formats | Specification repository is CC-BY-3.0 | Validate table shape, counts and coordinate ranges only; do not decode raster/vector tile payloads or disclose attribution/bounds. |
| [OpenRaster specification](https://www.openraster.org/) | ZIP mimetype and stack.xml layer/group relationships | Format specification; no implementation source used | Audit structure and missing source references without decoding PNG layers or merged preview. |
| [KDE Krita](https://invent.kde.org/graphics/krita) | Native KRA layered-painting archive and maindoc.xml | Krita is GPL-3.0; consulted as a format reference only | Inspect project metadata/layer visibility/locks using stdlib ZIP/XML; no Krita code, icons or assets are copied. |
| [Khronos glTF 2.0](https://github.com/KhronosGroup/glTF) | JSON glTF and GLB chunk container, scene graph and resource URIs | Specification material in Khronos repo is CC-BY-4.0 | Validate structural counts and URI safety offline; never fetch external buffers/textures or decode mesh pixels. |
| [draw.io file format and source](https://www.drawio.com/doc/faq/compression) / [jgraph/drawio](https://github.com/jgraph/drawio) | mxfile pages, compressed base64/DEFLATE XML and mxCell relations | draw.io source Apache-2.0, with separate restrictions on bundled icon/stencil assets | Implement only the public file-format decoder with stdlib zlib/XML; no icons, stencils or application source are copied. |
| [n8n workflow export docs](https://docs.n8n.io/workflows/export-import/) / [n8n-io/n8n](https://github.com/n8n-io/n8n) | JSON nodes, connections, credential references and parameter structure | n8n uses a fair-code licensing model; consulted only | Inspect exported JSON statically, flag execution-sensitive node categories and literal secret fields, never execute workflow code or connect to services. |
| [Design Tokens Community Group Format Module 2025.10](https://www.designtokens.org/tr/2025.10/format/) | Groups, tokens, $type/$value, aliases and reference paths | W3C Community Group report, not vendored code | Add a bounded JSON structure/alias audit; suppress token paths, descriptions and values. |
| [ISO 28500 WARC / IIPC WARC specifications](https://iipc.github.io/warc-specifications/) | WARC/1.0 and WARC/1.1 record framing, Content-Length and optional gzip container | International standard / community technical specification | Stream bounded records without retaining response payloads; report aggregate type counts and malformed/truncated framing only. |

### Wave 24 architecture and safety

All twelve processors live in `tools/wave24.py` and use Python standard library components (zipfile, XML ElementTree, mailbox/email, sqlite3, zlib/gzip and JSON). No new runtime or CI dependency is needed; no upstream implementation source, icon set, stencil library or project asset is vendored.

The Python allowlist, handler dispatch, pipeline transitions and TypeScript catalog are mirrored at **395 production IDs**. File-type inference selects these processors for supported extensions. Fourteen focused Python regression tests create synthetic fixtures and verify package integrity, privacy boundaries, unsafe inputs, external references and long design-token alias chains. Wave 24 merged as PR #76 (commit `dc13766a6afdef744e165c231803130db5e2a3a0`) and is deployed on Cloudflare Worker Version 81 (`af2311df-8bac-4597-aaec-e0115fb3106f`), with 100% traffic. Main CI [45015606847](https://github.com/Nolane-x/Nolane-search/actions/runs/45015606847), Worker export/health smoke [45015606799](https://github.com/Nolane-x/Nolane-search/actions/runs/45015606799) and Cloudflare deployment [45015606838](https://github.com/Nolane-x/Nolane-search/actions/runs/45015606838) all passed. Live Telegram upload/report/retry remains an owner-level end-to-end check.



Wave 24 implementation now includes fourteen focused Python regression tests covering package integrity, privacy-preserving output, malformed/unsafe inputs, external references and long alias chains. The candidate remains on its feature branch pending full GitHub Actions CI and production release gates.


## Wave 25 — Build observability, binary analysis, astronomy and game-engine metadata

| Specification / upstream | Scope reviewed | License / provenance | Design decision |
|---|---|---|---|
| [WebAssembly Core specification](https://github.com/WebAssembly/spec) and [Core 2.0 release](https://github.com/WebAssembly/spec/releases/tag/w3c-2025-09-16) | v1 module header, section IDs/order, custom sections and length-delimited binary structure | W3C community specification; repository source not vendored | Implement a read-only section scanner with strict LEB128/length boundaries and semantic ordering for tag/data-count sections; never decode instruction bodies or execute a module. Not a complete validator. |
| [SARIF 2.1.0 specification](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html) | Runs, tool drivers/rules, results, levels, suppressions, locations and fixes | OASIS standard | Count report structure and dangling rule references while withholding messages, paths, snippets and fingerprints. |
| [CycloneDX specification](https://github.com/CycloneDX/specification) and [CycloneDX overview](https://cyclonedx.org/specification/overview/) | Components, package identifiers, services, vulnerabilities, dependency edges and licenses | Official specification repository; no implementation source vendored | Add a JSON/XML structural report with values withheld; no package vulnerability matching or legal license review. |
| [SPDX 2.3 specification](https://spdx.github.io/spdx-spec/v2.3/) | JSON/XML packages, files, snippets, SPDX IDs and relationships | SPDX specification / Linux Foundation documentation | Add a bounded SPDX 2.x inventory/relationship audit; no source download or license compliance conclusion. |
| [JUnit 5 XML report documentation](https://junit.org/junit5/docs/current/user-guide/#running-tests-build-maven) and [Jenkins JUnit plugin](https://plugins.jenkins.io/junit/) | testsuite/testcase, failure/error/skipped, system-out/system-err and duration | Common test-runner report convention; no implementation vendored | Aggregate counts and suite duration; do not expose testcase names or failure/stdout content. |
| [Cobertura](https://cobertura.github.io/cobertura/) and [JaCoCo coverage reports](https://www.jacoco.org/jacoco/trunk/coverage/) | Line/branch rates, source/class/method and counter totals | JaCoCo EPL-2.0; upstream licenses treated separately | Report global percentages/counters only; no per-line source mapping or coverage quality certification. |
| [NASA FITS Standard 4.0](https://fits.gsfc.nasa.gov/fits_standard.html) | 2880-byte records, 80-byte header cards, HDUs, BITPIX/NAXIS, END and padded data units | NASA/IAU standard documentation | Parse header/data-unit boundaries and declared byte counts; never decode image pixels or print observation metadata. |
| [ISO 10303-21 / STEP Part 21](https://www.iso.org/standard/63141.html) | Physical file structure, HEADER, DATA, ENDSEC, entity instances and references | ISO standard; no proprietary CAD code copied | Perform lexical entity/reference and delimiter checks after stripping strings/comments; no geometry/kernel validation. |
| [OpenTelemetry Collector configuration](https://opentelemetry.io/docs/collector/configuration/) | Receivers, processors, exporters, connectors, extensions and service pipelines | OpenTelemetry project Apache-2.0 | Reuse PyYAML conditionally to check component references/public binds/secret field presence; do not start a collector or contact exporters. |
| [Godot project settings](https://docs.godotengine.org/en/stable/tutorials/editor/project_settings.html) and [godotengine/godot](https://github.com/godotengine/godot) | project.godot INI-like settings, autoloads, enabled editor plugins and resource paths | Godot engine MIT; documentation/project format reference only | Parse config text only; do not load scenes/scripts/plugins or fetch remote resources. |
| [Unity .unitypackage format research](https://github.com/Unity-Technologies/UnityCsReference) | gzip/tar archive with GUID folders and asset/asset.meta/pathname members | Unity proprietary package format; community-documented, not a formal public standard | Inspect tar member naming/completeness and archive bounds without extracting files or executing editor code. |
| [Unreal project descriptor documentation](https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-uproject-file-reference) | .uproject JSON fields, module/plugin declarations and target metadata | Epic official documentation; no Unreal Engine source or assets copied | Count declarations and secret-bearing fields only; no project load, module build or plugin execution. |

### Wave 25 architecture, tests and release evidence

All eleven processors live in `tools/wave25.py`. They use Python standard library modules for JSON/XML, archive handling, tar, binary parsing and FITS/STEP inspection. The OpenTelemetry auditor reuses the existing PyYAML dependency, installed only when that tool is selected. No new runtime package or database migration was required.

The TypeScript catalog, Python runner allowlist and handler map have **406 unique IDs**; all eleven new processors have upload inference and pipeline transitions. Seventeen dedicated Python tests use synthetic fixtures to verify parsing, semantic ordering, privacy and report output, including CycloneDX/SPDX JSON/XML variants.

Wave 25 merged as [PR #77](https://github.com/Nolane-x/Nolane-search/pull/77), production commit `bd5b51cd119d049dd14a654147d03a4303fa7e2c`. Main CI [45017239242](https://github.com/Nolane-x/Nolane-search/actions/runs/45017239242) passed 25 Vitest files and 206 Python runner tests. Worker export/health smoke [45017239294](https://github.com/Nolane-x/Nolane-search/actions/runs/45017239294) and Cloudflare deployment [45017239222](https://github.com/Nolane-x/Nolane-search/actions/runs/45017239222) passed. Cloudflare Worker Version 82 (`22378573-aa24-444d-96b0-59e8df345b75`) receives 100% traffic under deployment `1479f8fc-5c7c-4615-a3af-abe1fbb895f5`.

The analyzers remain structural/static diagnostics, not full WebAssembly validation, a vulnerability verdict, legal license advice, test execution, full coverage validation, astronomy rendering, CAD geometry certification or game-engine project verification. Owner-level Telegram uploads, delivered reports and `/tool_retry` still need live end-to-end checks with representative files.

## Wave 26 — Bioinformatics, genomics and sequence-analysis formats

| Specification / upstream | Scope reviewed | Provenance | Implementation decision |
|---|---|---|---|
| [NCBI FASTA format guidance](https://www.ncbi.nlm.nih.gov/genbank/fastaformat/) | Definition line, sequence IDs, line-wrapped nucleotide data and IUPAC alphabet | NCBI submission-format documentation | Count records/lengths/alphabet classes and duplicate IDs; suppress definition lines and raw sequences. |
| [GA4GH/SAMtools HTS format specifications](https://samtools.github.io/hts-specs/) and [SAM v1.6 specification](https://samtools.github.io/hts-specs/SAMv1.pdf) | SAM v1.6, VCF v4.x, BED intervals and alignment columns | Community-maintained genomics format specifications | Parse SAM flags/CIGAR fields, VCF header/variant structure and BED coordinate/block columns. |
| [Sequence Ontology GFF3 specification](https://github.com/The-Sequence-Ontology/Specifications/blob/master/gff3.md) and [Ensembl GFF3 reference](https://www.ensembl.org/info/website/upload/gff3.html) | Nine tab-separated columns, 1-based coordinates, strand/phase, directives and ID/Parent relationships | Sequence Ontology specification | Validate structure/parent references and count features; never emit sequence IDs, coordinates, gene symbols or attributes. |
| [NCBI GenBank release documentation](https://www.ncbi.nlm.nih.gov/genbank/release/current/) | LOCUS, FEATURES, ORIGIN and `//` terminator conventions | NCBI flat-file documentation | Count feature/qualifier rows and compare declared LOCUS length against ORIGIN symbols; suppress accession, taxonomy and sequence. |
| [wwPDB Atomic Coordinate Entry Format 3.3](https://www.wwpdb.org/documentation/file-format-content/format33/v3.3.html) | MODEL, ATOM/HETATM, coordinates, occupancy, B-factor and element columns | Worldwide Protein Data Bank format reference | Count model/atom/residue structures and check coordinate/occupancy parseability; do not expose coordinate tuples, residue names or structure titles. |
| [Graphical Fragment Assembly specification](https://github.com/GFA-spec/GFA-spec) | GFA 1.0/1.1 and GFA 2 segment/link/path/walk record types | Open community format specification | Count graph components and check segment references offline; no graph IDs, read strings, paths or sample/haplotype values in output. |
| [PHYLIP Newick format guide](https://phylipweb.github.io/phylip/newicktree.html) and [Newick grammar interpretation](https://phylipweb.github.io/phylip/newick_doc.html) | Nested parentheses, labels, comments, branch lengths and semicolon tree terminators | Historical community convention; no formal publication of the format standard is cited in the guide | Use a bounded syntax scanner to count leaves/internal nodes/trees and branch-length syntax; not a taxonomy or phylogenetic inference engine. |
| [Stockholm alignment guide](https://docs.r2dt.bio/en/latest/stockholm-alignments.html) and [Clustal format reference](https://www.phylo.org/index.php/help/clustal) | Block-based alignments, sequence rows, annotation lines and consensus symbols | Widely used alignment file conventions | Aggregate row lengths and block/comment counts only; no identifiers, sequence columns or consensus strings. |

### Wave 26 architecture, privacy and limits

All eleven implementations live in `tools/wave26.py` and use Python standard library only. Plain text and gzip inputs are streamed with a 20 MiB input limit, a 120 MiB expanded-stream ceiling and a 1 MiB per-line maximum; record-heavy formats have a one-million-record cap. Newick and multiple-alignment text is capped at 10 MiB. The VCF plain-extension ambiguity with vCard is handled explicitly: `.vcf.gz` and genomic VCF MIME types infer the variant processor, while MIME `text/vcard` retains the existing vCard processor.

Human genomic data can be highly identifying. The summary outputs suppress raw sequences, reads, genotype calls, accession/sample IDs, gene labels, coordinates, protein structure coordinates, graph identifiers and taxon labels. This does not make the upload itself de-identified: source files are still processed by the configured ephemeral GitHub-hosted runner. The tool is not clinical software, medical interpretation, genetic privacy certification or regulatory compliance advice.

The production catalog contains **417 unique IDs** across the TypeScript catalog, Python runner allowlist and handler map. All eleven Wave 26 tools have upload inference and pipeline transitions. The 23 synthetic-fixture Python tests passed with the full runner suite. Wave 26 merged as [PR #78](https://github.com/Nolane-x/Nolane-search/pull/78), commit fd60df0480a82775e6ba6974e386096fa58f6a0c. Main CI [45030758881](https://github.com/Nolane-x/Nolane-search/actions/runs/45030758881), Worker export/health smoke [45030758769](https://github.com/Nolane-x/Nolane-search/actions/runs/45030758769) and Cloudflare deployment [45030758729](https://github.com/Nolane-x/Nolane-search/actions/runs/45030758729) all passed. Worker Version 83 (a0d66d94-083a-46fa-af0b-1237e435a478) receives 100% traffic under deployment 95d12888-5427-4ac6-bb98-3bf4cb40fe89.

## Wave 27 — Digital preservation, research-data packaging and scholarly metadata

| Specification / upstream | Current version / scope reviewed | Provenance | Implementation decision |
|---|---|---|---|
| [RFC 8493 BagIt](https://www.rfc-editor.org/rfc/rfc8493.html) | Bag declaration, payload manifest, tagmanifest, completeness and digest algorithms | IETF Informational RFC | Inspect ZIP/TAR bags safely and compute listed payload/tag checksums without extracting payloads; checksum validity is measured, not inferred from filenames. |
| [Frictionless Data Package specification](https://specs.frictionlessdata.io/data-package/) and [v2 profiles](https://datapackage.org/profiles/2.0/datapackage.json) | Descriptor resources, paths, schema fields, primary/foreign keys and profiles | Frictionless specification | Audit metadata descriptors locally; do not open or fetch resource files referenced by the descriptor. |
| [RO-Crate 1.2 specification](https://www.researchobject.org/ro-crate/specification/1.2/) | JSON-LD @graph, root Data Entity, metadata descriptor, file entities and contextual references | Research Object community specification | Check graph structure, duplicate IDs and unresolved local references without exposing IDs/contextual metadata or dereferencing URLs. |
| [IIIF Presentation API 3.0](https://iiif.io/api/presentation/3.0/) | Manifest, Canvas, Annotation Page/Annotation, Image body, services and ranges | IIIF Consortium specification; API 3.0 is the latest stable version | Check object types, required structure and dimensions; never fetch Canvas images or remote services. |
| [DataCite Metadata Schema 4.7](https://schema.datacite.org/versions.html) | DOI identifier, creators, titles, publisher, publication year, resource type, subjects, related identifiers and dates | DataCite schema; version 4.7 released 3 March 2026 | Check core metadata categories, DOI shape and year format; suppress identifiers, titles and contributor values. |
| [Library of Congress METS schema documentation](https://www.loc.gov/standards/mets/mets-schemadocs.html) | METS 1.12.1 header, descriptive/administrative metadata, fileSec, structMap and ID references | Library of Congress schema documentation; METS 1.12.1 is listed as current | Count sections and cross-check IDREFs/FILEID references; no file extraction or metadata value display. |
| [PREMIS Data Dictionary](https://www.loc.gov/standards/premis/) | PREMIS object, event, agent, rights entities and linking identifiers | PREMIS preservation metadata standard | Count entities and match linking identifiers by target entity kind, identifier type and value; do not print object, agent, rights or event detail. |
| [OGC STAC Community Standard](https://www.ogc.org/standards/stac/) | STAC 1.1.0 Catalog/Collection/Item, links, assets, extensions, bbox and spatiotemporal extent | OGC community standard; 1.1.0 listed as current | Audit link/asset shape and extent structure; suppress geometry, coordinates, asset HREFs and provider metadata. |
| [TEI P5 Guidelines](https://www.tei-c.org/guidelines/p5/) | P5 4.12.0 TEI document/header/text/body structure, xml:id and fragment links | Text Encoding Initiative; 4.12.0 released 28 July 2026 | Count scholarly-text structures and detect duplicate IDs and broken same-document fragments; external/sibling-document fragments are excluded, and no source text or author/title values are exposed. |

### Wave 27 architecture, limits and safety

Nine implementations live in `tools/wave27.py`; all use Python standard library modules. BagIt ZIP/TAR inspection enforces a 20 MiB compressed input cap, 10,000-member cap and 180 MiB expanded limit, rejects unsafe paths/symlinks and streams each manifest-listed file through its selected digest. JSON descriptors are capped at 10 MiB; XML files at 12 MiB; DTD/entity declarations are rejected. Remote links, images, IIIF services and STAC assets are never fetched.

Research metadata can contain personal names, depositor details, rights information and unpublished research context. Reports suppress values, but this is not full data de-identification; the original file is still processed on the configured ephemeral GitHub-hosted runner. The tools are structural checks, not legal deposit certification, complete XSD/JSON Schema validation or a guarantee of long-term preservation.

The candidate has nine unique IDs and twenty-one synthetic-fixture tests. Review hardening makes PREMIS identifier links entity/type-aware and TEI fragment checks same-document-only. PR CI [45037254705](https://github.com/Nolane-x/Nolane-search/actions/runs/45037254705) passes after these changes. Production remains at 417 until merge-triggered Worker export/health smoke and Cloudflare deployment pass.
