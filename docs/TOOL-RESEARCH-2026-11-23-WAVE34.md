# Wave 34 upstream research — 2026-11-23

Repository: https://github.com/Nolane-x/Nolane-search
Branch: feat/wave-thirty-four-robotics-ml-observability
Status: implementation branch; not merged or deployed. Production remains **446 tools** until all post-merge release gates pass.

Wave 34 adds four data/observability ecosystems not represented in the current production catalog.

| Upstream project | Pinned upstream release | License | Selected capability |
|---|---|---|---|
| [Foxglove MCAP](https://github.com/foxglove/mcap) | Python package `mcap==1.6.0`, released 2026-10-19 | MIT | Inspect robotics recording header/footer and indexed summary without decoding message payloads |
| [Apache Iceberg Python](https://github.com/apache/iceberg-python) | `pyiceberg==0.12.0`, released 2026-09-01 | Apache-2.0 | Parse and validate local Iceberg v1/v2/v3 table metadata and snapshot references |
| [ONNX](https://github.com/onnx/onnx) | `onnx==1.23.2`, released 2026-10-06 | Apache-2.0 | Validate a serialized model's protobuf/graph/opset consistency without inference |
| [OpenTelemetry Proto](https://github.com/open-telemetry/opentelemetry-proto) | OTLP schema release `v1.11.1`, released 2026-09-29 | Apache-2.0 | Validate OTLP/JSON trace IDs, spans, timestamps, kinds, status and aggregate structure |

## Processor scope

### `mcap-recording-audit`

Uses the official MCAP Python reader to parse the header, footer and optional indexed summary. When present, it reports declared message totals, channel/schema counts, chunk/attachment/metadata index counts, and consistency between statistics and summary index structures. It does **not** iterate messages, decompress chunks, read message payloads, extract attachments or expose topic/schema names.

The input is capped at 50 MiB and individual MCAP record reads are capped at 2 MiB. An MCAP without an indexed summary is accepted but totals are reported as unavailable rather than forcing a full data scan. This is an index/structure audit, not a full-file fixity check: chunk CRCs and data-section CRCs are not verified.

### `iceberg-metadata-audit`

Uses PyIceberg's version-discriminated metadata models to parse local JSON table metadata for format versions 1, 2 and 3. It counts schema versions, top-level fields, partition specs, sort orders, snapshots, snapshot/metadata logs, refs, properties and encryption-key entries. It checks duplicate schema/partition/snapshot IDs and current-snapshot/ref references against the local snapshot list.

The JSON is limited to 8 MiB. The processor never contacts a REST/Hive/Glue catalog, reads a manifest, opens a data file, or accesses S3/ADLS/GCS. It suppresses table UUID, storage location, schema field names, manifest locations, property values, snapshot summaries and encryption material. A passing metadata model does not prove that the external files referenced by the table exist or are readable.

### `onnx-model-audit`

Uses ONNX 1.23.2 `onnx.load(..., load_external_data=False)` and `onnx.checker.check_model` with built-in-domain checks enabled and shape inference disabled. It reports IR/opset counts, graph input/output counts, node/operator-type counts, initializers and external tensor references. It recursively counts nested graph attributes, but never executes inference or custom operators.

The model is capped at 50 MiB and the graph at 200,000 nodes. External tensor bytes are not loaded or verified. Custom-domain implementations and runtime compatibility are not evaluated. The report does not contain model/graph/node names, operator names, tensor values/shapes or metadata property values. A successful checker result means structural model validation, not correctness or safety of inference.

### `otel-trace-audit`

Validates OTLP/JSON `resourceSpans` exports. It checks trace ID (16-byte/32-hex) and span ID (8-byte/16-hex) formatting, duplicate IDs within a trace, UInt64 timestamp values and start/end ordering, parent ID formatting, span-kind and status enums, and structural types/duplicate keys in span attributes, events and links. It reports aggregate spans/traces/events/links and counts by kind/status.

Input is capped at 10 MiB, 1,000 ResourceSpans groups and 100,000 spans. Trace/span IDs, span names, resource/service attributes, URLs, messages and attribute values are withheld. This is a structural OTLP/JSON audit; it does not contact a collector, reconstruct complete distributed traces, infer missing parent spans or validate every semantic convention.

## Runtime/deployment design

- MCAP, PyIceberg and ONNX dependencies are pinned and installed only for jobs that select their processors. OTLP uses the Python standard library.
- All uploaded files remain on the existing ephemeral GitHub-hosted runner; no new Worker secret, persistent service, D1 migration or paid provider is introduced.
- Inputs are bounded before parsing; raw parser diagnostics and private identifiers/values are withheld from reports.
- Tool output is a text report and may be followed by existing `text-clean` and `text-stats` steps.

## Acceptance gates

1. TypeScript catalog IDs, Python `RUNNERS`, Python handler map, text-output registry, pipeline transitions and `docs/NOLANE-TOOLS.md` must match exactly.
2. CI must pass type-check, all Vitest files, Python unittest discovery and Worker build. The MCAP, Iceberg and ONNX tests use actual upstream libraries and locally generated fixtures.
3. After merge, Worker export/health smoke and Cloudflare deployment must pass before raising production from **446 to 450**.
4. Owner-level Telegram E2E remains separate: send a small MCAP recording, a synthetic Iceberg metadata JSON, a valid/invalid ONNX model and an OTLP trace export; inspect reports and exercise `/tool_retry`.
5. Telegram Archive export/import/restore E2E is a separate owner-level recovery check and is not changed by Wave 34.

## Primary upstream sources

- MCAP Python reader: https://github.com/foxglove/mcap/blob/releases/python/mcap/v1.6.0/python/mcap/mcap/reader.py
- MCAP Python writer: https://github.com/foxglove/mcap/blob/releases/python/mcap/v1.6.0/python/mcap/mcap/writer.py
- MCAP license: https://github.com/foxglove/mcap/blob/main/LICENSE
- PyIceberg table metadata models: https://github.com/apache/iceberg-python/blob/pyiceberg-0.12.0/pyiceberg/table/metadata.py
- PyIceberg release metadata: https://github.com/apache/iceberg-python/blob/pyiceberg-0.12.0/pyproject.toml
- ONNX checker: https://github.com/onnx/onnx/blob/v1.23.2/onnx/checker.py
- ONNX version and dependencies: https://github.com/onnx/onnx/blob/v1.23.2/pyproject.toml
- OTLP Trace protobuf schema: https://github.com/open-telemetry/opentelemetry-proto/blob/v1.11.1/opentelemetry/proto/trace/v1/trace.proto
