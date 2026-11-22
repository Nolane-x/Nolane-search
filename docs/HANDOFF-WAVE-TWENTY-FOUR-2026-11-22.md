# Wave 24 handoff — 2026-11-22

## Branch and scope

- Branch: `feat/wave-twenty-four-interoperability-tools`
- Base production: Wave 23 / 383 tools, Cloudflare Worker Version 80 `f30ef26b-02c1-4d57-922a-acf3e698669d`
- Candidate catalog: **395 unique tools**, +12 processors.
- Candidate remains off production until PR CI, Worker export/smoke and Cloudflare deployment pass.

## Added processors

| ID | Format/domain | Primary checks |
|---|---|---|
| `odf-package-audit` | ODT / ODS / ODP | ZIP mimetype ordering, manifest match, unmanifested/missing members, encrypted entries, script/object paths and basic XML structure counts. |
| `xliff-audit` | XLIFF 1.x / 2.x | Units/segments, source/target presence, empty targets, states and placeholder-count mismatches. |
| `mbox-audit` | Email archive | Message count, MIME parts, attachment count, header presence, parseable/malformed dates and top-level MIME types. |
| `geopackage-audit` | GeoPackage / GIS | SQLite application ID, metadata tables, geometry type categories, CRS count, feature row count and quick_check. |
| `mbtiles-audit` | Map tile database | Metadata/tiles table shape, tile count, zoom levels, duplicate/out-of-range tile coordinates and format category. |
| `openraster-audit` | ORA layered images | mimetype, stack XML, canvas, layers/groups, visibility, composite mode and missing/unsafe layer paths. |
| `krita-project-audit` | KRA native painting projects | maindoc XML, canvas, color model/depth, layer/node counts, hidden/locked state and preview presence. |
| `gltf-audit` | glTF JSON / GLB | GLB header/chunks, scenes, nodes, meshes, accessors, extensions, embedded/external resources and unsafe URI paths. |
| `drawio-audit` | draw.io / mxfile | Page decoding, mxCell, vertices, edges, duplicate IDs and missing parent/source/target relationships. |
| `n8n-workflow-audit` | n8n workflow JSON | Nodes/connections, duplicate/dangling references, credential object references, execution-sensitive node families and hardcoded-secret field presence. |
| `design-token-audit` | DTCG 2025.10 | Token/group shapes, effective type, empty values, aliases, unresolved references and circular alias paths. |
| `warc-archive-audit` | WARC 1.0/1.1 and gzip | Record version/type/content-type counts, Content-Length checks, truncated records and total expanded-byte bound. |

## Implementation map

- New processor module: `tools/wave24.py`.
- New isolated regression suite: `tools/test_wave24.py` (13 tests).
- Python import, allowlist, handler, text-output support and pipeline transitions: `tools/runner.py`.
- TypeScript catalog, pipeline transitions and upload inference: `src/tools.ts`.
- Registry and inference test updates: `tests/tools.test.ts`.
- Telegram Tool Center count assertion: `tests/telegram.test.ts`.
- Research and licensing rationale: `docs/TOOL-RESEARCH-2026-11-22.md`.
- Candidate/production status and limits: `docs/STATUS.md` and `docs/NOLANE-TOOLS.md`.

## Safety, privacy and bounds

- The analyzers never execute workflow code, scripts, commands, SQL, or embedded macros.
- No external URL, texture, buffer, map tile, WARC target or linked resource is fetched.
- Email addresses/names/subjects/body/attachment filenames, GIS coordinates/geometry/feature attributes, diagram labels/URLs, workflow parameter/credential values, design token paths/values and WARC record URLs/headers/payloads are withheld.
- SQLite GeoPackage/MBTiles are opened with `mode=ro&immutable=1` and query_only.
- ZIP package inspectors reject traversal, absolute paths, symlinks, encrypted entries, duplicate paths and oversized archives. XML parsers reject DTD/entity declarations.
- Standard input limit is 20 MiB. ZIP default expanded cap is 120 MiB / 1,000 members; ORA 150 MiB and KRA 180 MiB. WARC expanded stream is capped at 120 MiB / 50,000 records. Formats also have stricter XML/JSON/node/message limits.
- All reports are static diagnostics, not full format conformance certification, a malware verdict, recovery guarantee, rendering engine, or semantic validation of the underlying application project.

## Release gates

1. Verify exactly 395 unique IDs in TypeScript catalog, Python allowlist and Python handler map.
2. Type-check, Vitest, Python compilation and full unittest discovery.
3. Worker build/export and deployed health smoke.
4. Cloudflare deployment, webhook and command registration.
5. Owner-level Telegram E2E: upload representative samples, inspect reports and test `/tool_retry`.

Do not describe Wave 24 as production until all automated release gates pass. Wave 23 remains the 383-tool production baseline.
