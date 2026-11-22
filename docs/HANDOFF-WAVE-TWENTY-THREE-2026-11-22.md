# Wave 23 handoff — 2026-11-22

## Branch and scope

- Branch: feat/wave-twenty-three-domain-tools
- Base production commit: 35ed71a5905b1d2995ba27ad000b1151a78bac77 (Wave 22 / 371 tools)
- Candidate catalog: **383 tools**, +12 processors.
- Candidate is not production until PR CI, Worker export/smoke and Cloudflare deployment pass.

## Added processors

| ID | Domain | File support | Core function |
|---|---|---|---|
| gcode-audit | CNC / 3D printing | GCODE/GCO/TAP/NC | Count G/M commands, XYZ extents, feed/spindle words and review-worthy commands. No simulation or machine execution. |
| midi-audit | Audio/music | MIDI/SMF | Parse MThd/MTrk chunks, tracks, note events, meta/tempo events and ticks; do not play. |
| musicxml-audit | Music notation | MusicXML/MXL | Count parts/measures/notes/rests/key/time/tempo; reject DTD/entity and archive traversal. |
| bibtex-audit | Research/writing | BIB | Duplicate citation keys, DOI counts and missing bibliographic fields; suppress citation values. |
| nmea-track-audit | GNSS/GPS | NMEA | Check checksums, RMC/GGA coordinate formats and sentence distribution; never output coordinates/timestamps. |
| ansible-playbook-audit | DevOps | YAML | Static counts for shell/command/raw, become, no_log, ignored failures and package version/state omissions. |
| prometheus-rules-audit | Observability | YAML | Group/rule counts, duplicate groups and missing severity/summary/description metadata; no PromQL execution. |
| grafana-dashboard-audit | Observability | JSON | Panel types/IDs, datasource refs, query target counts, template counts and public flags; withhold all values. |
| hdf5-audit | Scientific data | H5/HDF5 | Metadata-only group/dataset/shape/dtype/compression/chunking scan; skip soft/external links and never read dataset values. |
| avro-schema-audit | Data engineering | AVSC | Structural scan of record/enum/fixed/array/map/union, duplicate fields and missing schema parts. Not a complete Avro validator. |
| graphql-schema-audit | API engineering | GraphQL SDL | Local parse, schema construction and validation using graphql-core; no resolver/query/mutation execution. |
| protobuf-schema-audit | API/data engineering | PROTO | Static token/field-number scan for syntax, declarations, services, RPCs and reserved ranges; no protoc compilation. |

## Implementation map

- New reusable processors: tools/wave23.py.
- New isolated regression suite: tools/test_wave23.py (14 tests).
- Registry and dispatch: tools/runner.py.
- User catalog, pipeline transitions and upload inference: src/tools.ts.
- Registry/category/inference tests: tests/tools.test.ts.
- Runner installs h5py and graphql-core only when those tools are selected; YAML packages are reused conditionally for Ansible/Prometheus.
- Research, upstream links and license review: docs/TOOL-RESEARCH-2026-11-22.md.
- Production and candidate status: docs/STATUS.md and docs/NOLANE-TOOLS.md.

## Safety and limits

- No uploaded code, YAML task, CNC instruction, MIDI event, PromQL expression, GraphQL resolver or Protocol Buffers program is executed.
- No network fetch is performed by these analyzers.
- GPS positions, timestamps, bibliography identity values, dashboard UIDs/URLs/queries, data tensor values and schema field names are not copied into reports.
- h5py skips external/soft links and reads metadata only; GraphQL is parse/validate only; MXL blocks DTD/entities and rejects unsafe member paths.
- All input/output stays within the existing 20 MiB input and 45 MiB output runner boundaries; processors add stricter per-format limits.
- Reports are static diagnostics, not CNC safety approvals, full standard validators, runtime tests, or security guarantees.

## Release gates

1. TypeScript catalog uniqueness/count and supported upload inference.
2. Type-check, Vitest, Python compilation and full unittest discovery for tools/test_*.py.
3. Worker build/export and production health smoke.
4. Cloudflare deployment with webhook/command registration verification.
5. Owner-level Telegram E2E for a representative file from each domain and /tool_retry.

Do not mark the 383-tool catalog as production until all automated release gates pass. Wave 22 remains the last verified production baseline at 371 processors.
