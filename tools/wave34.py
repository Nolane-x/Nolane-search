"""Wave 34: MCAP robotics recordings, Apache Iceberg metadata, ONNX models and OTLP traces."""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re

MAX_MCAP_BYTES = 50 * 1024 * 1024
MAX_MCAP_RECORD_BYTES = 2 * 1024 * 1024
MAX_ICEBERG_BYTES = 8 * 1024 * 1024
MAX_ONNX_BYTES = 50 * 1024 * 1024
MAX_OTLP_BYTES = 10 * 1024 * 1024
MAX_OTLP_RESOURCE_SPANS = 1_000
MAX_OTLP_SPANS = 100_000


def mcap_recording_audit(path: Path) -> dict:
    """Inspect MCAP header/footer and indexed summary without decoding message payloads."""
    if path.stat().st_size < 16 or path.stat().st_size > MAX_MCAP_BYTES:
        raise RuntimeError("MCAP input must be between 16 bytes and 50 MiB.")
    if path.suffix.lower() != ".mcap":
        raise RuntimeError("Robotics recording audit accepts .mcap files only.")

    try:
        from mcap.reader import SeekingReader

        with path.open("rb") as stream:
            reader = SeekingReader(
                stream,
                validate_crcs=False,
                record_size_limit=MAX_MCAP_RECORD_BYTES,
            )
            header = reader.get_header()
            summary = reader.get_summary()
    except Exception as exc:
        raise RuntimeError("MCAP header/footer or indexed summary is malformed or exceeds a record limit.") from exc

    if summary is None:
        return _mcap_report(path, [
            "Summary section: absent",
            "Message/channel/schema totals: unavailable without scanning the complete data section",
            "Payload handling: message bytes, attachments and embedded schema data were not read",
            "Integrity scope: header and footer structure were parsed; chunk CRCs and message payloads were not scanned",
        ])

    stats = summary.statistics
    if stats is not None:
        message_count = max(0, int(stats.message_count))
        start_time = max(0, int(stats.message_start_time))
        end_time = max(0, int(stats.message_end_time))
        declared_channels = max(0, int(stats.channel_count))
        declared_schemas = max(0, int(stats.schema_count))
        declared_chunks = max(0, int(stats.chunk_count))
    else:
        message_count = start_time = end_time = 0
        declared_channels = declared_schemas = declared_chunks = 0

    channel_ids = set(summary.channels)
    schema_ids = set(summary.schemas)
    channel_schema_dangling = sum(
        1 for channel in summary.channels.values()
        if channel.schema_id != 0 and channel.schema_id not in schema_ids
    )
    statistics_mismatch = 0
    if stats is not None:
        statistics_mismatch += int(declared_channels != len(channel_ids))
        statistics_mismatch += int(declared_schemas != len(schema_ids))
        statistics_mismatch += int(declared_chunks != len(summary.chunk_indexes))

    return _mcap_report(path, [
        "Summary section: present",
        f"Messages declared by summary: {message_count:,}",
        f"Distinct channels: {len(channel_ids):,}",
        f"Distinct schemas: {len(schema_ids):,}",
        f"Chunk indexes: {len(summary.chunk_indexes):,}",
        f"Attachment indexes: {len(summary.attachment_indexes):,}",
        f"Metadata indexes: {len(summary.metadata_indexes):,}",
        f"Declared channel/schema/chunk-count mismatches: {statistics_mismatch:,}",
        f"Channels referencing missing schemas: {channel_schema_dangling:,}",
        f"Message start timestamp (Unix ns): {start_time:,}" if stats is not None and message_count else "Message start timestamp: unavailable",
        f"Message end timestamp (Unix ns): {end_time:,}" if stats is not None and message_count else "Message end timestamp: unavailable",
        f"Header profile present: {'yes' if bool(header.profile) else 'no'}",
        "Payload handling: message bytes, embedded schema data, topic names and metadata values were not read or reported",
        "Integrity scope: header, footer and summary index structure were parsed; data chunks and per-chunk CRCs were not scanned",
    ])


def _mcap_report(path: Path, lines: list[str]) -> dict:
    from wave28 import _report

    return _report(path, "mcap-recording", "MCAP robotics recording structure report", lines)


def iceberg_metadata_audit(path: Path) -> dict:
    """Validate Apache Iceberg metadata JSON locally using the pinned PyIceberg models."""
    if path.stat().st_size <= 0 or path.stat().st_size > MAX_ICEBERG_BYTES:
        raise RuntimeError("Iceberg metadata input must be between 1 byte and 8 MiB.")
    if path.suffix.lower() != ".json":
        raise RuntimeError("Iceberg metadata audit accepts metadata JSON files only.")

    try:
        raw = path.read_text(encoding="utf-8-sig")
        if len(raw.encode("utf-8")) > MAX_ICEBERG_BYTES:
            raise RuntimeError("Iceberg metadata exceeds the 8 MiB size limit.")
        from pyiceberg.table.metadata import TableMetadataUtil

        metadata = TableMetadataUtil.parse_raw(raw)
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError("Iceberg metadata JSON is malformed or fails the selected format-version model.") from exc

    schemas = list(metadata.schemas)
    schema_ids = [int(schema.schema_id) for schema in schemas]
    partition_specs = list(metadata.partition_specs)
    partition_ids = [int(spec.spec_id) for spec in partition_specs]
    snapshots = list(metadata.snapshots)
    snapshot_ids = [int(snapshot.snapshot_id) for snapshot in snapshots]
    refs = dict(metadata.refs)
    ref_snapshot_ids = [int(ref.snapshot_id) for ref in refs.values()]

    duplicate_schema_ids = len(schema_ids) - len(set(schema_ids))
    duplicate_partition_ids = len(partition_ids) - len(set(partition_ids))
    duplicate_snapshot_ids = len(snapshot_ids) - len(set(snapshot_ids))
    current_snapshot_missing = int(
        metadata.current_snapshot_id is not None
        and int(metadata.current_snapshot_id) not in set(snapshot_ids)
    )
    dangling_refs = sum(1 for snapshot_id in ref_snapshot_ids if snapshot_id not in set(snapshot_ids))
    top_level_fields = sum(len(schema.fields) for schema in schemas)
    encrypted_keys = len(getattr(metadata, "encryption_keys", []))

    warnings = (
        duplicate_schema_ids + duplicate_partition_ids + duplicate_snapshot_ids
        + current_snapshot_missing + dangling_refs
    )
    return _iceberg_report(path, [
        f"Table format version: {int(metadata.format_version)}",
        f"Schema versions: {len(schemas):,}",
        f"Top-level schema fields across versions: {top_level_fields:,}",
        f"Partition specs: {len(partition_specs):,}",
        f"Sort orders: {len(metadata.sort_orders):,}",
        f"Snapshots: {len(snapshots):,}",
        f"Snapshot-log entries: {len(metadata.snapshot_log):,}",
        f"Metadata-log entries: {len(metadata.metadata_log):,}",
        f"Snapshot references/branches/tags: {len(refs):,}",
        f"Table properties (values withheld): {len(metadata.properties):,}",
        f"Encryption-key entries (contents withheld): {encrypted_keys:,}",
        f"Duplicate schema IDs: {duplicate_schema_ids:,}",
        f"Duplicate partition-spec IDs: {duplicate_partition_ids:,}",
        f"Duplicate snapshot IDs: {duplicate_snapshot_ids:,}",
        f"Current snapshot missing from snapshot list: {current_snapshot_missing:,}",
        f"References pointing to missing snapshots: {dangling_refs:,}",
        f"Metadata consistency warnings: {warnings:,}",
        "Privacy: table UUID, location, namespace/table names, property values, manifest paths and snapshot summaries are withheld",
        "Scope: validates the metadata JSON model and internal ID relationships; does not open manifests, data files, catalogs or cloud storage",
    ])


def _iceberg_report(path: Path, lines: list[str]) -> dict:
    from wave28 import _report

    return _report(path, "iceberg-metadata", "Apache Iceberg table metadata report", lines)


def onnx_model_audit(path: Path) -> dict:
    """Check ONNX model protobuf/graph consistency without running model inference."""
    if path.stat().st_size <= 0 or path.stat().st_size > MAX_ONNX_BYTES:
        raise RuntimeError("ONNX model input must be between 1 byte and 50 MiB.")
    if path.suffix.lower() != ".onnx":
        raise RuntimeError("ONNX model audit accepts .onnx files only.")

    try:
        import onnx

        model = onnx.load(str(path), load_external_data=False)
        onnx.checker.check_model(
            model,
            full_check=False,
            skip_opset_compatibility_check=False,
            check_custom_domain=False,
        )
    except Exception as exc:
        return _onnx_report(path, [
            "Model validation: failed",
            "The ONNX parser/checker rejected the model; raw diagnostics, graph names and model metadata are withheld",
            "Execution boundary: no inference, custom operator execution, external weight loading or network access occurred",
        ])

    node_count = 0
    nested_graphs = 0
    initializer_count = 0
    external_initializers = 0
    custom_domain_nodes = 0
    operation_counts: Counter[str] = Counter()

    def inspect_graph(graph) -> None:
        nonlocal node_count, nested_graphs, initializer_count, external_initializers, custom_domain_nodes
        initializer_count += len(graph.initializer)
        external_initializers += sum(1 for tensor in graph.initializer if tensor.external_data)
        for node in graph.node:
            node_count += 1
            operation_counts[node.op_type] += 1
            if node.domain:
                custom_domain_nodes += 1
            for attribute in node.attribute:
                if attribute.type == onnx.AttributeProto.GRAPH:
                    nested_graphs += 1
                    inspect_graph(attribute.g)
                elif attribute.type == onnx.AttributeProto.GRAPHS:
                    nested_graphs += len(attribute.graphs)
                    for child in attribute.graphs:
                        inspect_graph(child)

    inspect_graph(model.graph)
    if node_count > 200_000:
        raise RuntimeError("ONNX graph exceeds the 200,000-node processing limit.")

    return _onnx_report(path, [
        "Model validation: passed" if not external_initializers else "Model graph validation: passed (external weights not verified)",
        f"ONNX IR version: {int(model.ir_version):,}",
        f"Opset imports: {len(model.opset_import):,}",
        f"Graph nodes (including nested subgraphs): {node_count:,}",
        f"Distinct operator types: {len(operation_counts):,}",
        f"Custom-domain nodes (not executed): {custom_domain_nodes:,}",
        f"Graph inputs: {len(model.graph.input):,}",
        f"Graph outputs: {len(model.graph.output):,}",
        f"Initializers: {initializer_count:,}",
        f"Initializers with external tensor data: {external_initializers:,}",
        f"Nested graph attributes: {nested_graphs:,}",
        f"Functions: {len(model.functions):,}",
        "Execution boundary: no inference, model optimization, custom operator execution or external weight loading",
        "Privacy: model/graph/node names, operator names, tensor values, shapes, metadata properties and file paths are withheld",
        "Scope: validates ONNX structure and built-in-domain consistency; custom-domain implementations and external tensor payloads are not evaluated",
    ])


def _onnx_report(path: Path, lines: list[str]) -> dict:
    from wave28 import _report

    return _report(path, "onnx-model", "ONNX model structure report", lines)


def otel_trace_audit(path: Path) -> dict:
    """Validate OTLP/JSON trace structure and timing without exposing trace or attribute values."""
    if path.stat().st_size <= 0 or path.stat().st_size > MAX_OTLP_BYTES:
        raise RuntimeError("OTLP trace JSON must be between 1 byte and 10 MiB.")
    if path.suffix.lower() not in {".json", ".otlp.json"}:
        raise RuntimeError("OTLP trace audit accepts JSON exports only.")

    try:
        root = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("OTLP trace input is not valid UTF-8 JSON.") from exc
    if not isinstance(root, dict) or not isinstance(root.get("resourceSpans"), list):
        raise RuntimeError("OTLP trace JSON must contain a resourceSpans array.")
    resource_spans = root["resourceSpans"]
    if len(resource_spans) > MAX_OTLP_RESOURCE_SPANS:
        raise RuntimeError("OTLP trace exceeds the 1,000-resourceSpans limit.")

    span_count = trace_count = event_count = link_count = attribute_count = 0
    invalid_spans = duplicate_span_ids = invalid_timestamps = invalid_attributes = 0
    kind_counts = Counter()
    status_counts = Counter()
    seen_span_ids = set()
    seen_trace_ids = set()

    def parse_uint64(value) -> int | None:
        if isinstance(value, bool):
            return None
        if isinstance(value, int):
            number = value
        elif isinstance(value, str) and value.isdigit():
            number = int(value)
        else:
            return None
        if number < 0 or number > 18_446_744_073_709_551_615:
            return None
        return number

    def valid_hex_id(value, chars: int) -> bool:
        return isinstance(value, str) and len(value) == chars and value != "0" * chars and re.fullmatch(r"[0-9a-fA-F]+", value) is not None

    status_map = {
        "STATUS_CODE_UNSET": "unset",
        "STATUS_CODE_OK": "ok",
        "STATUS_CODE_ERROR": "error",
        0: "unset",
        1: "ok",
        2: "error",
    }
    for resource_item in resource_spans:
        if not isinstance(resource_item, dict):
            invalid_spans += 1
            continue
        scopes = resource_item.get("scopeSpans", [])
        if not isinstance(scopes, list):
            invalid_spans += 1
            continue
        for scope in scopes:
            if not isinstance(scope, dict) or not isinstance(scope.get("spans", []), list):
                invalid_spans += 1
                continue
            for span in scope.get("spans", []):
                span_count += 1
                if span_count > MAX_OTLP_SPANS:
                    raise RuntimeError("OTLP trace exceeds the 100,000-span processing limit.")
                if not isinstance(span, dict):
                    invalid_spans += 1
                    continue

                trace_id = span.get("traceId")
                span_id = span.get("spanId")
                parent_id = span.get("parentSpanId", "")
                valid_ids = valid_hex_id(trace_id, 32) and valid_hex_id(span_id, 16)
                if parent_id not in ("", None) and not valid_hex_id(parent_id, 16):
                    valid_ids = False
                if not valid_ids:
                    invalid_spans += 1
                else:
                    seen_trace_ids.add(trace_id.lower())
                    key = (trace_id.lower(), span_id.lower())
                    if key in seen_span_ids:
                        duplicate_span_ids += 1
                    seen_span_ids.add(key)

                start = parse_uint64(span.get("startTimeUnixNano"))
                end = parse_uint64(span.get("endTimeUnixNano"))
                if start is None or end is None or end < start:
                    invalid_timestamps += 1

                kind = span.get("kind", 0)
                if isinstance(kind, str) and kind.isdigit():
                    kind = int(kind)
                if kind not in (0, 1, 2, 3, 4, 5):
                    invalid_spans += 1
                else:
                    kind_counts[kind] += 1

                status = span.get("status", {})
                status_code = status.get("code", 0) if isinstance(status, dict) else 0
                status_label = status_map.get(status_code)
                if status_label is None:
                    invalid_spans += 1
                else:
                    status_counts[status_label] += 1

                attributes = span.get("attributes", [])
                events = span.get("events", [])
                links = span.get("links", [])
                for collection in (attributes, events, links):
                    if not isinstance(collection, list):
                        invalid_attributes += 1
                if isinstance(attributes, list):
                    attribute_count += len(attributes)
                    keys = [item.get("key") for item in attributes if isinstance(item, dict)]
                    if len(keys) != len(attributes) or len([k for k in keys if isinstance(k, str)]) != len(keys):
                        invalid_attributes += 1
                    if len(keys) != len(set(keys)):
                        invalid_attributes += 1
                if isinstance(events, list):
                    event_count += len(events)
                if isinstance(links, list):
                    link_count += len(links)

    errors = invalid_spans + duplicate_span_ids + invalid_timestamps + invalid_attributes
    return _otel_report(path, [
        f"ResourceSpans groups: {len(resource_spans):,}",
        f"Spans inspected: {span_count:,}",
        f"Distinct trace IDs: {len(seen_trace_ids):,}",
        f"Events: {event_count:,}",
        f"Links: {link_count:,}",
        f"Span attributes: {attribute_count:,}",
        f"Invalid spans/IDs/kinds/status fields: {invalid_spans:,}",
        f"Duplicate span IDs within a trace: {duplicate_span_ids:,}",
        f"Invalid or reversed timestamps: {invalid_timestamps:,}",
        f"Invalid attribute/event/link collections: {invalid_attributes:,}",
        "Span kinds (internal/server/client/producer/consumer): "
        + "/".join(str(kind_counts.get(k, 0)) for k in (1, 2, 3, 4, 5)),
        f"Status counts (unset/ok/error): {status_counts.get('unset', 0):,}/{status_counts.get('ok', 0):,}/{status_counts.get('error', 0):,}",
        f"Structural findings: {errors:,}",
        "Privacy: trace/span IDs, span names, service/resource attributes, URLs and attribute values are withheld",
        "Scope: validates OTLP/JSON trace shape, identifiers, status/kind enums and timestamp ordering; does not infer missing parents or contact a collector",
    ])


def _otel_report(path: Path, lines: list[str]) -> dict:
    from wave28 import _report

    return _report(path, "otel-trace", "OpenTelemetry OTLP trace JSON report", lines)
