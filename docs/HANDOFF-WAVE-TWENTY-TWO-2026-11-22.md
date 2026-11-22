# Wave 22 candidate handoff — Multidomain engineering, GIS, CAD and productivity

Date: 2026-11-22  
Repository: https://github.com/Nolane-x/Nolane-search  
Branch: \`feat/wave-twenty-two-multidomain-tool-suite\`  
Status: implementation, dependency wiring, documentation and regression tests added; awaiting PR CI and production release gates.

## Goal

Expand beyond the 354 production processors without duplicating existing OCR, subtitle repair, PDF/Office, JSON Schema, PCAP, barcode/QR, Parquet, repository analysis and media functions. Wave 22 introduces 17 additional processors across database engineering, application security, measurement, 3D/CAD, geospatial, localization, computational notebooks, image formats and static web QA.

## New processors

| ID | Capability | Input → output | Key boundary |
|---|---|---|---|
| \`sqlglot-format\` | Format SQL and transpile dialects | SQL/JSON envelope → .sql | 5 MiB, 1,000,000 characters, 200 statements; parsing only, no query execution. |
| \`sqlfluff-lint\` | Dialect-aware SQL lint | .sql → TXT report | 5 MiB/1,000,000 characters; report contains rule and source locations, not SQL text. |
| \`python-security-audit\` | Bandit static security scan | .py → TXT report | One Python file, 10 MiB, 120-second timeout; source is parsed but never executed. |
| \`unit-convert\` | Physical unit conversion | TXT/CSV → CSV | 2 MiB/1,000 lines; restricted quantity grammar and dimensional compatibility checks. |
| \`mesh-inspect\` | 3D triangle mesh inspection | STL/OBJ/PLY/OFF/GLB/GLTF/3MF → TXT | 20 MiB; max 2M vertices/4M faces; watertight/volume work only up to 500K faces. |
| \`dxf-audit\` | CAD drawing structure/auditor | .dxf → TXT | 20 MiB/1M modelspace entities; no rendering or external-reference loading. |
| \`shapefile-audit\` | ESRI Shapefile bundle inspection | ZIP containing .shp/.shx/.dbf → TXT | 20 MiB archive/100 MiB expanded/100 members/20 datasets; no attribute values. |
| \`gettext-catalog-audit\` | Localization catalog QA | .po/.pot → TXT | 10 MiB/100K entries; untranslated/fuzzy/obsolete/plural/placeholder counts; source strings withheld. |
| \`notebook-audit\` | Jupyter Notebook schema and output inventory | .ipynb → TXT | 20 MiB/20K cells; no code execution or cell source/output disclosure. |
| \`notebook-strip-outputs\` | Remove notebook execution artifacts | .ipynb → cleaned .ipynb | 20 MiB/20K cells; removes outputs and execution counts while retaining cell source. |
| \`heic-convert\` | HEIC/HEIF to standard image | .heic/.heif → JPEG/PNG | 20 MiB/80 MP; keeps frame zero; camera/GPS metadata is not retained. |
| \`subtitle-quality-audit\` | Caption timing/readability metrics | .srt/.vtt → CSV | 10 MiB/20K cues; reports CPS, line length, overlaps and short cues without subtitle text. |
| \`kml-to-geojson\` | Convert KML placemarks to GeoJSON | .kml/.xml → .geojson | 20 MiB/20K features/500K coordinates; blocks DTD/entities and does not fetch NetworkLinks. |
| \`coordinate-transform\` | EPSG coordinate transformation | JSON envelope → GeoJSON | 10 MiB/10K coordinates; EPSG identifiers only, PROJ network disabled. |
| \`html-seo-audit\` | Static SEO/accessibility metadata inventory | .html/.htm → TXT | 10 MiB; reports counts/rules without page metadata values or network fetches. |
| \`html-local-link-audit\` | Check internal resources/fragments in a site bundle | ZIP of HTML site → CSV | 20 MiB/100 MiB expanded/500 files/200 HTML pages/5K findings; external links skipped. |
| \`css-quality-audit\` | CSS parser and maintainability metrics | .css → TXT | 10 MiB; duplicate selectors/properties, !important, imports, external URLs and parse errors; no CSS values copied. |

## Upstream projects and licensing

| Project | License verified | Integrated capability |
|---|---|---|
| [SQLGlot](https://github.com/tobymao/sqlglot) | MIT | SQL parsing, formatting and dialect conversion. |
| [SQLFluff](https://github.com/sqlfluff/sqlfluff) | MIT | SQL lint rules and dialect-aware source locations. |
| [Bandit](https://github.com/PyCQA/bandit) | Apache-2.0 | Static Python security findings. |
| [Pint](https://github.com/hgrecco/pint) | BSD-3-Clause | Physical quantity/unit conversion. |
| [trimesh](https://github.com/mikedh/trimesh) | MIT | 3D triangle mesh geometry inspection. |
| [ezdxf](https://github.com/mozman/ezdxf) | MIT | DXF parsing and drawing audit. |
| [PyShp](https://github.com/GeospatialPython/pyshp) | MIT | Shapefile reader. |
| [polib](https://github.com/izimobil/polib) | MIT | gettext PO/POT parser. |
| [nbformat](https://github.com/jupyter/nbformat) | BSD-3-Clause | Jupyter Notebook schema/model. |
| [pillow-heif](https://github.com/bigcat88/pillow_heif) | BSD-3-Clause | HEIF/HEIC codec integration for Pillow. |
| [pyproj](https://github.com/pyproj4/pyproj) | MIT | EPSG coordinate transformations. |
| [tinycss2](https://github.com/Kozea/tinycss2) | BSD-3-Clause | CSS tokenizer/parser. |

KML conversion, subtitle quality analysis, HTML metadata/link checks use bounded Python standard-library parsing. No upstream application source is vendored.

## Integration

All 17 IDs are registered in:
- TypeScript \`TOOL_CATALOG\`;
- Python \`RUNNERS\` and the handler \`TOOLS\` map;
- matching TypeScript/Python pipeline transitions;
- \`TEXT_OUTPUT_TOOLS\` for report-only processors;
- the GitHub Actions runner with per-tool conditional dependency installs;
- CI dependency installation and regression tests.

Current source parity check: 371 TypeScript IDs, 371 Python allowlist IDs and 371 Python handlers; the two pipeline transition maps match. Seventeen Wave 22 Python tests cover the new processors. Final CI remains the source of truth for syntax, test and build verification.

## Safety boundaries

- Python source is never executed by Bandit; the call is a fixed \`python -m bandit\` invocation against a single uploaded path.
- SQL is parsed/linted/formatted only; no database connection or query execution exists.
- KML and Notebook parsing are local; external KML NetworkLinks are ignored.
- Coordinate transformation restricts CRS identifiers to EPSG and disables PROJ network access.
- Shapefile ZIP paths, symlinks, encrypted entries, member count and expanded size are bounded.
- HTML website ZIP entries are inspected in memory; no external URL is fetched.
- HEIC conversion creates a fresh pixel image and does not carry EXIF/GPS metadata forward.
- Subtitle CSV contains timing/readability metrics, never dialogue text.
- Uploaded inputs/outputs remain on the ephemeral GitHub-hosted runner; no D1 persistence is introduced.

## Release gates

1. TypeScript catalog contains 371 unique IDs.
2. Python RUNNERS and TOOLS contain exactly the same 371 IDs.
3. Worker and Python pipeline transition maps are identical.
4. All 17 Python regression tests pass; all TypeScript assertions are updated.
5. SQLGlot/SQLFluff, Bandit, Pint, trimesh, ezdxf, PyShp, polib, nbformat, pillow-heif, pyproj and tinycss2 are installed in CI; runner installs remain conditional per selected processor.
6. PR CI passes TypeScript type-check, unit tests, deployment-script checks, Python tests and Worker build.
7. Main CI, Worker export/health smoke and Cloudflare deployment pass before production is recorded as 371 tools.
8. Owner-level Telegram E2E remains necessary: upload representative SQL, Python, units, 3D, DXF, Shapefile, PO, Notebook, HEIC, subtitle, KML, coordinate, HTML, site ZIP and CSS files; inspect outputs and exercise \`/tool_retry\`.

Production remains Wave 21 / 354 tools until every release gate is met.
