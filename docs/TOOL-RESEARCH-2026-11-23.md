# Wave 32 upstream research — 2026-11-23

Repository: https://github.com/Nolane-x/Nolane-search
Branch: feat/wave-thirty-two-semantic-and-pdf-tools
Status: implemented, merged in PR #85 and deployed to production on 2026-11-23. Production catalog: 442 tools; Worker Version ID: ddfedcef-6feb-42da-97a3-e29c4fcfaa3e.

Wave 32 deliberately adds capabilities that are not equivalent to the existing CSV/JSON/Office validators or the existing PDF text extractor.

| Upstream | Version reviewed | License | Capability selected | Integration decision |
|---|---:|---|---|---|
| [OCRmyPDF](https://github.com/ocrmypdf/OCRmyPDF) | 17.14.2 (released 2026-11-16) | MPL-2.0 | Add a searchable text layer to scanned PDFs | Use the CLI as an isolated child process; do not modify or vendor upstream source. Pin the Python package version. |
| [RDFLib](https://github.com/RDFLib/rdflib) | 7.6.0 (released 2026-02-13) | BSD-3-Clause | Parse and profile RDF graphs/datasets | Add a bounded read-only profiler for Turtle, N-Triples, N-Quads and TriG. Do not load JSON-LD remote contexts or RDF/XML. |
| [pySHACL](https://github.com/RDFLib/pySHACL) | 0.40.2 (released 2026-10-26) | Apache-2.0 | Validate RDF data against SHACL shapes | Accept one strict ZIP package with data.ttl and shapes.ttl; enable SHACL Core only, disable JS/advanced behavior and block imports/SPARQL constraints. |
| [croniter](https://github.com/pallets-eco/croniter) | 7.0.0 (released 2026-11-09) | MIT | Validate cron expressions and preview next run times | Accept five-field expressions only; preview in UTC; never execute commands or create scheduler state. |

## New processors

### pdf-ocr-searchable

Creates a new PDF with a searchable text layer using Tesseract English and Vietnamese language data. It skips pages that already contain text, performs automatic page rotation and deskew, and writes a standard PDF (not PDF/A). The existing pdf-text tool remains the default PDF upload path; this new processor is explicit in Tool Center so users choose the output transformation.

Runtime limits: 20 MiB input, 20-minute subprocess timeout and 45 MiB output. OCRmyPDF is installed only for jobs selecting this tool. The temporary input/output filenames are neutral (input.pdf, output.pdf); stdout/stderr are captured and not returned to the user. OCRmyPDF documents that it is not designed to be secure against malicious PDFs, so the file is processed on an ephemeral GitHub-hosted runner, without bot credentials in the OCR processing step. This is not a malware scanner.

### rdf-graph-audit

Profiles local RDF graph/dataset structure from Turtle, N-Triples, N-Quads and TriG. It reports aggregate triple/quad, subject, predicate, literal, blank-node, namespace and named-graph counts. It never returns graph identifiers, subjects, predicates, labels, literal values or source paths. JSON-LD and RDF/XML are intentionally excluded to avoid remote context/DTD processing. Input is capped at 5 MiB and 50,000 triples/quads.

### shacl-validate

Accepts a ZIP containing exactly two root-level members: data.ttl and shapes.ttl. It validates the data graph with pySHACL using no inference and SHACL Core only. Remote ontology imports, SPARQL constraints, JavaScript constraints and rules are rejected. The report contains conformance, aggregate result-severity and constraint-component counts; it does not include focus nodes, RDF values, result paths, messages or source identifiers. ZIP input is capped at 5 MiB, each Turtle member at 2 MiB, data graph at 50,000 triples and shapes graph at 10,000 triples. The ZIP is inspected in memory; members are not extracted.

### cron-schedule-audit

Validates one five-field cron expression per non-comment line and previews the next three occurrences in UTC for up to 100 schedules. Up to 1,000 schedule rows and 2 MiB of input are accepted. The report deliberately avoids echoing raw expressions or possible command text. It never runs commands, writes crontabs or creates schedules; UTC previews do not infer a server timezone or DST policy.

## Architecture and acceptance gates

- The four IDs must exist exactly once in the TypeScript catalog, Python runner allowlist and Python handler map.
- Worker and runner pipeline transition maps must remain identical.
- RDF/SHACL/cron report processors can feed text-clean and text-stats. The OCR PDF output can feed the existing PDF processors.
- Optional runtime dependencies are installed only for the selected tool. CI installs the Python parser dependencies to exercise all unit tests.
- No D1 migration, Cloudflare secret, persistent service or paid resource is introduced.
- Regression coverage is in tools/test_wave32.py (13 focused tests): RDF formats and privacy, SHACL conforming/violating/forbidden packages, cron UTC previews and privacy, and PDF OCR command isolation/error handling.
- Release verification: PR #85 merged as f9359406a25043220e51a90e33cc9a72c6fc7321. Main CI 45145755895, Worker export/health smoke 45145756137 and Cloudflare deployment 45145755910 all passed. Production catalog is now 442 tools.
- Owner-level Telegram acceptance remains separate: exercise one searchable scanned PDF, one small RDF graph, one valid/invalid SHACL package and one cron file through the private bot; inspect returned files/reports and test /tool_retry.

Research links:
- OCRmyPDF releases: https://github.com/ocrmypdf/OCRmyPDF/releases
- OCRmyPDF API: https://ocrmypdf.readthedocs.io/en/latest/api.html
- RDFLib changelog: https://github.com/RDFLib/rdflib/blob/main/CHANGELOG.md
- pySHACL releases: https://github.com/RDFLib/pySHACL/releases
- croniter PyPI: https://pypi.org/project/croniter/
