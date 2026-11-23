from __future__ import annotations

import io
import json
from pathlib import Path
import tempfile
import unittest

import wave34


class Wave34Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def write(self, name: str, content: str | bytes) -> Path:
        path = self.root / name
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")
        return path

    def report(self, result: dict) -> str:
        return Path(result["output_path"]).read_text(encoding="utf-8")

    def test_mcap_reads_summary_counts_without_emitting_topics_or_message_payloads(self):
        from mcap.writer import Writer

        buffer = io.BytesIO()
        writer = Writer(buffer)
        writer.start(profile="ros2", library="private-library-name")
        schema_id = writer.register_schema("PrivateSchema", "ros2msg", b"PRIVATE_SCHEMA_SENTINEL")
        channel_id = writer.register_channel("/robot/private-topic", "cdr", schema_id)
        writer.add_message(channel_id, 1_700_000_000_000_000_000, b"PRIVATE_MESSAGE_SENTINEL", 1_700_000_000_000_000_001)
        writer.finish()
        path = self.write("drive.mcap", buffer.getvalue())

        report = self.report(wave34.mcap_recording_audit(path))
        self.assertIn("Summary section: present", report)
        self.assertIn("Messages declared by summary: 1", report)
        self.assertIn("Distinct channels: 1", report)
        self.assertIn("Distinct schemas: 1", report)
        self.assertNotIn("private-topic", report)
        self.assertNotIn("PRIVATE_MESSAGE_SENTINEL", report)
        self.assertNotIn("PRIVATE_SCHEMA_SENTINEL", report)
        self.assertNotIn("private-library-name", report)

    def test_mcap_accepts_no_summary_but_marks_totals_unavailable(self):
        from mcap.writer import Writer

        buffer = io.BytesIO()
        writer = Writer(buffer, use_statistics=False, use_summary_offsets=False)
        writer.start()
        writer.finish()
        path = self.write("minimal.mcap", buffer.getvalue())
        report = self.report(wave34.mcap_recording_audit(path))
        self.assertIn("Summary section: absent", report)
        self.assertIn("unavailable without scanning", report)

    def test_mcap_rejects_invalid_magic_and_unsupported_extension(self):
        invalid = self.write("broken.mcap", b"not-an-mcap-file-data")
        with self.assertRaisesRegex(RuntimeError, "header/footer"):
            wave34.mcap_recording_audit(invalid)
        other = self.write("broken.bin", b"not-an-mcap-file-data")
        with self.assertRaisesRegex(RuntimeError, "accepts .mcap"):
            wave34.mcap_recording_audit(other)

    def test_iceberg_metadata_v2_validates_schema_and_snapshot_references(self):
        metadata = {
            "format-version": 2,
            "table-uuid": "00000000-0000-0000-0000-000000000001",
            "location": "file:///private/table",
            "last-updated-ms": 1700000000000,
            "last-column-id": 1,
            "schemas": [{"type": "struct", "schema-id": 0, "fields": [
                {"id": 1, "name": "private-id", "required": True, "type": "long"}
            ]}],
            "current-schema-id": 0,
            "partition-specs": [{"spec-id": 0, "fields": []}],
            "default-spec-id": 0,
            "last-partition-id": 999,
            "properties": {"private.secret": "PRIVATE_PROPERTY_SENTINEL"},
            "current-snapshot-id": 101,
            "snapshots": [{
                "snapshot-id": 101,
                "timestamp-ms": 1700000000000,
                "manifest-list": "file:///private/manifest.avro",
                "summary": {"operation": "append"},
                "schema-id": 0
            }],
            "snapshot-log": [],
            "metadata-log": [],
            "sort-orders": [{"order-id": 0, "fields": []}],
            "default-sort-order-id": 0,
            "refs": {"main": {"snapshot-id": 101, "type": "branch"}}
        }
        path = self.write("00001.metadata.json", json.dumps(metadata))
        report = self.report(wave34.iceberg_metadata_audit(path))
        self.assertIn("Table format version: 2", report)
        self.assertIn("Snapshots: 1", report)
        self.assertIn("Snapshot references/branches/tags: 1", report)
        self.assertIn("Metadata consistency warnings: 0", report)
        self.assertNotIn("private/table", report)
        self.assertNotIn("PRIVATE_PROPERTY_SENTINEL", report)
        self.assertNotIn("manifest.avro", report)
        self.assertNotIn("private-id", report)

    def test_iceberg_metadata_rejects_missing_current_snapshot_and_dangling_refs(self):
        metadata = {
            "format-version": 2,
            "table-uuid": "00000000-0000-0000-0000-000000000001",
            "location": "s3://private/table",
            "last-updated-ms": 1700000000000,
            "last-column-id": 1,
            "schemas": [{"type": "struct", "schema-id": 0, "fields": [{"id": 1, "name": "id", "required": True, "type": "long"}]}],
            "current-schema-id": 0,
            "partition-specs": [{"spec-id": 0, "fields": []}],
            "default-spec-id": 0,
            "properties": {},
            "current-snapshot-id": 999,
            "snapshots": [],
            "sort-orders": [{"order-id": 0, "fields": []}],
            "default-sort-order-id": 0,
            "refs": {"main": {"snapshot-id": 999, "type": "branch"}}
        }
        report = self.report(wave34.iceberg_metadata_audit(self.write("bad.metadata.json", json.dumps(metadata))))
        self.assertIn("Current snapshot missing from snapshot list: 1", report)
        self.assertIn("References pointing to missing snapshots: 1", report)
        self.assertNotIn("s3://private", report)

    def test_iceberg_metadata_rejects_unknown_format_version(self):
        path = self.write("unknown.json", '{"format-version":99}')
        with self.assertRaisesRegex(RuntimeError, "fails the selected format-version model"):
            wave34.iceberg_metadata_audit(path)

    def test_onnx_checks_valid_model_without_running_inference(self):
        import onnx
        from onnx import TensorProto, helper

        x = helper.make_tensor_value_info("PRIVATE_INPUT_NAME", TensorProto.FLOAT, [1])
        y = helper.make_tensor_value_info("PRIVATE_OUTPUT_NAME", TensorProto.FLOAT, [1])
        node = helper.make_node("Relu", ["PRIVATE_INPUT_NAME"], ["PRIVATE_OUTPUT_NAME"], name="PRIVATE_NODE_NAME")
        graph = helper.make_graph([node], "PRIVATE_GRAPH", [x], [y])
        model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 18)])
        path = self.write("model.onnx", model.SerializeToString())
        report = self.report(wave34.onnx_model_audit(path))
        self.assertIn("Model validation: passed", report)
        self.assertIn("Graph nodes (including nested subgraphs): 1", report)
        self.assertNotIn("PRIVATE_INPUT_NAME", report)
        self.assertNotIn("PRIVATE_NODE_NAME", report)
        self.assertNotIn("PRIVATE_GRAPH", report)

    def test_onnx_checker_rejects_invalid_graph_without_leaking_names(self):
        import onnx
        from onnx import TensorProto, helper

        x = helper.make_tensor_value_info("PRIVATE_INPUT_NAME", TensorProto.FLOAT, [1])
        node = helper.make_node("Relu", ["NOT_DEFINED"], ["out"], name="PRIVATE_NODE_NAME")
        graph = helper.make_graph([node], "PRIVATE_GRAPH", [x], [])
        model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 18)])
        path = self.write("bad.onnx", model.SerializeToString())
        report = self.report(wave34.onnx_model_audit(path))
        self.assertIn("Model validation: failed", report)
        self.assertNotIn("NOT_DEFINED", report)
        self.assertNotIn("PRIVATE_GRAPH", report)

    def otel_payload(self):
        return {
            "resourceSpans": [{
                "scopeSpans": [{
                    "spans": [{
                        "traceId": "1" * 32,
                        "spanId": "a" * 16,
                        "parentSpanId": "",
                        "name": "PRIVATE_SPAN_NAME",
                        "kind": 2,
                        "startTimeUnixNano": "1700000000000000000",
                        "endTimeUnixNano": "1700000000000000100",
                        "attributes": [{"key": "http.url", "value": {"stringValue": "https://private.invalid"}}],
                        "events": [{"timeUnixNano": "1700000000000000050", "name": "PRIVATE_EVENT"}],
                        "links": [],
                        "status": {"code": "STATUS_CODE_OK"}
                    }, {
                        "traceId": "1" * 32,
                        "spanId": "b" * 16,
                        "parentSpanId": "a" * 16,
                        "name": "PRIVATE_CHILD_NAME",
                        "kind": 3,
                        "startTimeUnixNano": "1700000000000000010",
                        "endTimeUnixNano": "1700000000000000090",
                        "attributes": [],
                        "events": [],
                        "links": [],
                        "status": {"code": "STATUS_CODE_ERROR"}
                    }]
                }]
            }]
        }

    def test_otel_trace_counts_spans_and_withholds_identifiers_and_attributes(self):
        path = self.write("trace.json", json.dumps(self.otel_payload()))
        report = self.report(wave34.otel_trace_audit(path))
        self.assertIn("Spans inspected: 2", report)
        self.assertIn("Distinct trace IDs: 1", report)
        self.assertIn("Events: 1", report)
        self.assertIn("Span kinds (internal/server/client/producer/consumer): 0/1/1/0/0", report)
        self.assertIn("Status counts (unset/ok/error): 0/1/1", report)
        self.assertIn("Structural findings: 0", report)
        self.assertNotIn("PRIVATE_SPAN_NAME", report)
        self.assertNotIn("https://private.invalid", report)
        self.assertNotIn("a" * 16, report)

    def test_otel_trace_detects_duplicate_ids_bad_times_and_duplicate_attribute_keys(self):
        payload = self.otel_payload()
        duplicate = dict(payload["resourceSpans"][0]["scopeSpans"][0]["spans"][0])
        duplicate["endTimeUnixNano"] = "1"
        duplicate["attributes"] = [{"key": "x"}, {"key": "x"}]
        payload["resourceSpans"][0]["scopeSpans"][0]["spans"].append(duplicate)
        report = self.report(wave34.otel_trace_audit(self.write("bad-trace.json", json.dumps(payload))))
        self.assertIn("Duplicate span IDs within a trace: 1", report)
        self.assertIn("Invalid or reversed timestamps: 1", report)
        self.assertIn("Invalid attribute/event/link collections: 1", report)
        self.assertNotIn("bad-trace", report)

    def test_otel_trace_rejects_invalid_root_and_oversized_exports(self):
        path = self.write("wrong.json", '{"resourceSpans":{}}')
        with self.assertRaisesRegex(RuntimeError, "must contain a resourceSpans array"):
            wave34.otel_trace_audit(path)
        large = self.root / "large.json"
        large.write_bytes(b" " * (wave34.MAX_OTLP_BYTES + 1))
        with self.assertRaisesRegex(RuntimeError, "10 MiB"):
            wave34.otel_trace_audit(large)


if __name__ == "__main__":
    unittest.main()
