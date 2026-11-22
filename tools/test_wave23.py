from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wave23


class Wave23DomainToolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, name: str, content: str) -> Path:
        path = self.root / name
        path.write_text(content, encoding="utf-8")
        return path

    def assert_report(self, result):
        self.assertTrue(Path(result["output_path"]).is_file())
        self.assertIn("audit", result["summary"].lower())

    def test_gcode_audit_reports_commands_and_axis_ranges_without_source(self):
        path = self.write("part.gcode", "G90\nG1 X10 Y-2 Z0.3 F1000\nM3 S900\nM5\n")
        result = wave23.gcode_audit(path)
        self.assert_report(result)
        self.assertIn("M3=1", result["summary"])
        self.assertIn("X: 10 to 10", result["summary"])
        self.assertNotIn("G1 X10", result["summary"])

    def test_midi_audit_parses_note_events(self):
        header = b"MThd" + (6).to_bytes(4, "big") + bytes([0, 1, 0, 1, 1, 0xE0])
        track = bytes([0, 0x90, 60, 100, 0x83, 0x60, 0x80, 60, 64, 0, 0xFF, 0x2F, 0])
        path = self.root / "song.mid"
        path.write_bytes(header + b"MTrk" + len(track).to_bytes(4, "big") + track)
        result = wave23.midi_audit(path)
        self.assert_report(result)
        self.assertIn("Note-on events: 1", result["summary"])
        self.assertIn("Note-off events: 1", result["summary"])

    def test_midi_audit_rejects_truncated_track(self):
        path = self.root / "broken.mid"
        path.write_bytes(b"MThd" + (6).to_bytes(4, "big") + bytes([0, 0, 0, 1, 1, 0xE0]) + b"MTrk" + (20).to_bytes(4, "big") + b"\x00")
        with self.assertRaisesRegex(RuntimeError, "track chunk"):
            wave23.midi_audit(path)

    def test_musicxml_audit_counts_score_structure_without_lyrics(self):
        source = """<score-partwise version="4.0"><part-list><score-part id="P1"><part-name>Private Instrument</part-name></score-part></part-list><part id="P1"><measure number="1"><attributes><time><beats>4</beats><beat-type>4</beat-type></time><key><fifths>0</fifths></key></attributes><note><pitch><step>C</step><octave>4</octave></pitch><duration>1</duration></note><note><rest/><duration>1</duration></note></measure></part></score-partwise>"""
        result = wave23.musicxml_audit(self.write("score.musicxml", source))
        self.assert_report(result)
        self.assertIn("Measures: 1", result["summary"])
        self.assertIn("Notes: 2", result["summary"])
        self.assertNotIn("Private Instrument", result["summary"])

    def test_musicxml_audit_blocks_dtd(self):
        source = """<!DOCTYPE score-partwise [<!ENTITY x "bad">]><score-partwise>&x;</score-partwise>"""
        with self.assertRaisesRegex(RuntimeError, "DTD"):
            wave23.musicxml_audit(self.write("unsafe.musicxml", source))

    def test_bibtex_audit_finds_duplicate_keys_and_missing_fields_privately(self):
        source = """@article{dup, author={Secret Author}, title={Private Research}, year={2024}, journal={Secret Journal}}
@book{dup, title={Another Private Title}}
"""
        result = wave23.bibtex_audit(self.write("refs.bib", source))
        self.assert_report(result)
        self.assertIn("Duplicate citation keys: 1", result["summary"])
        self.assertIn("missing author/editor: 1", result["summary"])
        self.assertNotIn("Secret Author", result["summary"])
        self.assertNotIn("Private Research", result["summary"])

    def test_nmea_audit_checks_checksum_without_disclosing_coordinates(self):
        payload = "GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,"
        checksum = 0
        for char in payload:
            checksum ^= ord(char)
        source = "$" + payload + "*" + format(checksum, "02X") + "\n" + "$GPRMC,123520,A,4807.038,N,01131.000,E,0.0,0.0,230394,,,A*00\n"
        result = wave23.nmea_track_audit(self.write("track.nmea", source))
        self.assert_report(result)
        self.assertIn("Checksum valid: 1", result["summary"])
        self.assertNotIn("4807.038", result["summary"])
        self.assertNotIn("01131.000", result["summary"])

    def test_ansible_audit_reports_shell_and_privilege_counts_without_commands(self):
        source = """- hosts: all
  become: true
  tasks:
    - name: Private task
      shell: echo private-command
      no_log: false
    - name: Package install
      apt:
        name: example
"""
        result = wave23.ansible_playbook_audit(self.write("site.yml", source))
        self.assert_report(result)
        self.assertIn("shell: 1", result["summary"])
        self.assertIn("become: 1", result["summary"])
        self.assertNotIn("private-command", result["summary"])

    def test_prometheus_audit_finds_missing_alert_annotations_without_expressions(self):
        source = """groups:
  - name: service
    rules:
      - alert: PrivateAlertName
        expr: up == 0
        labels: {}
        annotations: {}
"""
        result = wave23.prometheus_rules_audit(self.write("alerts.yml", source))
        self.assert_report(result)
        self.assertIn("Alert rules missing severity label: 1", result["summary"])
        self.assertNotIn("PrivateAlertName", result["summary"])
        self.assertNotIn("up == 0", result["summary"])

    def test_grafana_audit_counts_panels_and_duplicate_ids_without_dashboard_values(self):
        source = {"dashboard": {"uid": "private-uid", "schemaVersion": 39, "panels": [
            {"id": 1, "type": "timeseries", "datasource": {"uid": "secret-ds"}, "targets": [{"expr": "private_metric"}]},
            {"id": 1, "type": "stat"},
        ], "templating": {"list": [{"name": "secret-variable"}]}}}
        result = wave23.grafana_dashboard_audit(self.write("dashboard.json", json.dumps(source)))
        self.assert_report(result)
        self.assertIn("Duplicate panel IDs: 1", result["summary"])
        self.assertNotIn("private-uid", result["summary"])
        self.assertNotIn("private_metric", result["summary"])

    def test_hdf5_audit_reads_metadata_only_and_hides_dataset_names(self):
        import h5py
        path = self.root / "samples.h5"
        with h5py.File(path, "w") as handle:
            handle.create_dataset("private_measurements", data=[1, 2, 3], compression="gzip")
        result = wave23.hdf5_audit(path)
        self.assert_report(result)
        self.assertIn("Datasets: 1", result["summary"])
        self.assertIn("Compressed datasets: 1", result["summary"])
        self.assertNotIn("private_measurements", result["summary"])

    def test_avro_audit_finds_duplicate_field_names(self):
        schema = {"type": "record", "name": "PrivateEvent", "fields": [
            {"name": "id", "type": "string"},
            {"name": "id", "type": ["null", "string"], "default": None},
        ]}
        result = wave23.avro_schema_audit(self.write("event.avsc", json.dumps(schema)))
        self.assert_report(result)
        self.assertIn("duplicate_field_names: 1", result["summary"])
        self.assertNotIn("PrivateEvent", result["summary"])

    def test_graphql_audit_validates_schema_without_field_names(self):
        source = """type Query { hello: String! user(id: ID!): User }
type User { id: ID! old: String @deprecated(reason: "legacy") }
"""
        result = wave23.graphql_schema_audit(self.write("schema.graphql", source))
        self.assert_report(result)
        self.assertIn("Deprecated field definitions: 1", result["summary"])
        self.assertNotIn("hello", result["summary"])
        self.assertIn("Schema validation errors: 0", result["summary"])

    def test_protobuf_audit_counts_schema_constructs(self):
        source = """syntax = "proto3";
package demo.v1;
message Event {
  string id = 1;
  int64 timestamp = 2;
}
service EventService {
  rpc Get(Event) returns (Event);
}
"""
        result = wave23.protobuf_schema_audit(self.write("events.proto", source))
        self.assert_report(result)
        self.assertIn("Message declarations: 1", result["summary"])
        self.assertIn("RPC declarations: 1", result["summary"])
        self.assertIn("Field declarations recognized: 2", result["summary"])
        self.assertNotIn("timestamp", result["summary"])


if __name__ == "__main__":
    unittest.main()
