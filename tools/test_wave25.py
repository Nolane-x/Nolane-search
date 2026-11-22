from __future__ import annotations

import io
import json
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wave25


class Wave25BuildObservabilityBinaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, name: str, content: str) -> Path:
        path = self.root / name
        path.write_text(content, encoding="utf-8")
        return path

    def write_bytes(self, name: str, content: bytes) -> Path:
        path = self.root / name
        path.write_bytes(content)
        return path

    def assert_report(self, result):
        self.assertTrue(Path(result["output_path"]).is_file())
        self.assertIn("audit", result["summary"].lower())

    def test_wasm_audit_counts_sections_without_executing_module(self):
        # WASM v1 header followed by an empty type section (section id 1, vector length 0).
        data = b"\x00asm\x01\x00\x00\x00" + b"\x01\x01\x00"
        result = wave25.wasm_module_audit(self.write_bytes("module.wasm", data))
        self.assert_report(result)
        self.assertIn("Binary version: 1", result["summary"])
        self.assertIn("Standard sections: 1", result["summary"])
        self.assertIn("type=0", result["summary"])
        self.assertNotIn("instruction", result["summary"].lower().replace("instruction bodies", ""))

    def test_wasm_audit_accepts_data_count_before_code_section(self):
        # In the Core binary order, data-count section 12 precedes code section 10.
        data = b"\x00asm\x01\x00\x00\x00" + b"\x0c\x01\x00" + b"\x0a\x01\x00"
        result = wave25.wasm_module_audit(self.write_bytes("data-count.wasm", data))
        self.assert_report(result)
        self.assertIn("Section-order inversions (coarse static check): 0", result["summary"])
        self.assertIn("Code bodies: 0", result["summary"])

    def test_wasm_audit_rejects_truncated_section(self):
        data = b"\x00asm\x01\x00\x00\x00" + b"\x01\x08\x00"
        with self.assertRaisesRegex(RuntimeError, "boundary"):
            wave25.wasm_module_audit(self.write_bytes("broken.wasm", data))

    def test_sarif_audit_counts_results_and_withholds_messages_and_paths(self):
        document = {
            "$schema": "https://example.invalid/sarif-schema.json",
            "version": "2.1.0",
            "runs": [{
                "tool": {"driver": {"name": "PrivateScanner", "rules": [{"id": "SECRET-RULE"}]}},
                "results": [
                    {"ruleId": "SECRET-RULE", "level": "error", "message": {"text": "Private finding text"}, "locations": [{"physicalLocation": {"artifactLocation": {"uri": "secret.py"}}}]},
                    {"ruleId": "MISSING-RULE", "level": "warning", "message": {"text": "Another private finding"}},
                ],
            }],
        }
        result = wave25.sarif_report_audit(self.write("report.sarif", json.dumps(document)))
        self.assert_report(result)
        self.assertIn("Results: 2", result["summary"])
        self.assertIn("error=1", result["summary"])
        self.assertIn("Results referencing undeclared rule IDs: 1", result["summary"])
        self.assertNotIn("PrivateScanner", result["summary"])
        self.assertNotIn("Private finding text", result["summary"])
        self.assertNotIn("secret.py", result["summary"])

    def test_cyclonedx_sbom_audit_counts_components_and_dangling_edges(self):
        document = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.7",
            "components": [
                {"type": "library", "name": "PrivateLibrary", "bom-ref": "pkg:generic/private@1.0"},
                {"type": "library", "name": "AnotherLibrary", "bom-ref": "pkg:generic/another@2.0", "licenses": [{"license": {"id": "MIT"}}]},
            ],
            "dependencies": [
                {"ref": "pkg:generic/private@1.0", "dependsOn": ["pkg:generic/another@2.0", "pkg:generic/missing@1.0"]}
            ],
            "vulnerabilities": [{"id": "PRIVATE-CVE-ID"}],
        }
        result = wave25.cyclonedx_sbom_audit(self.write("bom.cdx.json", json.dumps(document)))
        self.assert_report(result)
        self.assertIn("SBOM format: CycloneDX JSON", result["summary"])
        self.assertIn("Components/packages: 2", result["summary"])
        self.assertIn("Dependency edges with missing endpoints: 1", result["summary"])
        self.assertIn("Vulnerability records: 1", result["summary"])
        self.assertNotIn("PrivateLibrary", result["summary"])
        self.assertNotIn("PRIVATE-CVE-ID", result["summary"])

    def test_spdx_json_audit_counts_packages_files_and_relationships(self):
        document = {
            "spdxVersion": "SPDX-2.3",
            "SPDXID": "SPDXRef-DOCUMENT",
            "packages": [{"name": "PrivatePackage", "SPDXID": "SPDXRef-Package", "licenseDeclared": "MIT"}],
            "files": [{"fileName": "private.bin", "SPDXID": "SPDXRef-File"}],
            "relationships": [{"spdxElementId": "SPDXRef-Package", "relationshipType": "CONTAINS", "relatedSpdxElement": "SPDXRef-File"}],
        }
        result = wave25.cyclonedx_sbom_audit(self.write("sbom.spdx.json", json.dumps(document)))
        self.assert_report(result)
        self.assertIn("SBOM format: SPDX JSON", result["summary"])
        self.assertIn("Package records: 1", result["summary"])
        self.assertIn("File records: 1", result["summary"])
        self.assertNotIn("PrivatePackage", result["summary"])
        self.assertNotIn("private.bin", result["summary"])

    def test_junit_audit_counts_failures_errors_skips_without_test_messages(self):
        source = """<testsuites><testsuite tests="4" failures="1" errors="1" skipped="1" time="1.25"><testcase name="private-pass"/><testcase name="private-fail"><failure message="Secret assertion">Private trace</failure></testcase><testcase name="private-error"><error message="Sensitive error"/></testcase><testcase name="private-skip"><skipped/></testcase><system-out>private stdout</system-out></testsuite></testsuites>"""
        result = wave25.junit_xml_audit(self.write("junit.xml", source))
        self.assert_report(result)
        self.assertIn("Test cases: 4", result["summary"])
        self.assertIn("Observed failures: 1", result["summary"])
        self.assertIn("Observed errors: 1", result["summary"])
        self.assertIn("Observed skipped tests: 1", result["summary"])
        self.assertNotIn("private-pass", result["summary"])
        self.assertNotIn("Private trace", result["summary"])
        self.assertNotIn("private stdout", result["summary"])

    def test_cobertura_coverage_audit_reports_aggregates_only(self):
        source = """<coverage line-rate="0.75" branch-rate="0.5"><sources><source>private/src</source></sources><packages><package name="secret"><classes><class name="PrivateClass" filename="secret.py"><methods><method name="privateMethod"/></methods><lines><line number="1" hits="3" branch="true"><conditions><condition number="0" type="jump" coverage="50%"/></conditions></line><line number="2" hits="0"/></lines></class></classes></package></packages></coverage>"""
        result = wave25.coverage_xml_audit(self.write("coverage.xml", source))
        self.assert_report(result)
        self.assertIn("Coverage format: Cobertura", result["summary"])
        self.assertIn("line rate: 75.000%", result["summary"])
        self.assertIn("1/2 covered", result["summary"])
        self.assertNotIn("PrivateClass", result["summary"])
        self.assertNotIn("secret.py", result["summary"])

    def test_jacoco_coverage_audit_reports_counter_totals_only(self):
        source = """<report name="private"><package name="secret"><class name="Secret"><method name="hidden"><counter type="LINE" missed="2" covered="8"/><counter type="BRANCH" missed="1" covered="1"/></method></class><sourcefile name="Private.java"><line nr="1" mi="0" ci="1"/></sourcefile></package></report>"""
        result = wave25.coverage_xml_audit(self.write("jacoco.xml", source))
        self.assert_report(result)
        self.assertIn("Coverage format: JaCoCo", result["summary"])
        self.assertIn("line: 8/10 covered", result["summary"])
        self.assertNotIn("Secret", result["summary"])
        self.assertNotIn("Private.java", result["summary"])

    def test_fits_audit_parses_header_and_skips_pixel_data(self):
        def card(key: str, value: str | None = None) -> bytes:
            text = key.ljust(8) if value is None else key.ljust(8) + "= " + value
            return text.ljust(80).encode("ascii")
        header = b"".join([
            card("SIMPLE", "T"),
            card("BITPIX", "8"),
            card("NAXIS", "1"),
            card("NAXIS1", "4"),
            card("OBJECT", "'PrivateTarget'"),
            card("END"),
        ])
        header = header.ljust(2880, b" ")
        data = header + (b"\x01\x02\x03\x04").ljust(2880, b"\x00")
        result = wave25.fits_file_audit(self.write_bytes("observation.fits", data))
        self.assert_report(result)
        self.assertIn("HDUs inspected: 1", result["summary"])
        self.assertIn("Declared data bytes (not pixel-decoded): 4", result["summary"])
        self.assertNotIn("PrivateTarget", result["summary"])

    def test_step_audit_counts_entities_and_dangling_refs_without_text(self):
        source = """ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('Private design'),'2;1');
FILE_NAME('secret.step','2026-11-22',('Author'),('Org'),'App','System','');
FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));
ENDSEC;
DATA;
#1=APPLICATION_CONTEXT('private context');
#2=PRODUCT('SecretProduct','private description','',(#1));
#3=PRODUCT_CONTEXT('',#99,'mechanical');
ENDSEC;
END-ISO-10303-21;
"""
        result = wave25.step_cad_audit(self.write("model.step", source))
        self.assert_report(result)
        self.assertIn("Entity instances: 3", result["summary"])
        self.assertIn("Entity references without a corresponding definition: 1", result["summary"])
        self.assertIn("HEADER sections: 1", result["summary"])
        self.assertNotIn("SecretProduct", result["summary"])
        self.assertNotIn("secret.step", result["summary"])

    def test_otel_collector_audit_detects_missing_and_unused_components_without_addresses(self):
        source = """receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
  unusedreceiver:
    endpoint: 127.0.0.1:9999
processors:
  batch: {}
exporters:
  debug: {}
service:
  pipelines:
    traces:
      receivers: [otlp, missingreceiver]
      processors: [batch]
      exporters: [debug]
  extensions: []
"""
        result = wave25.otel_collector_audit(self.write("otel.yaml", source))
        self.assert_report(result)
        self.assertIn("Configured receivers: 2", result["summary"])
        self.assertIn("Undefined service component references: 1", result["summary"])
        self.assertIn("Configured but unreferenced components/extensions: 1", result["summary"])
        self.assertNotIn("0.0.0.0:4317", result["summary"])
        self.assertNotIn("missingreceiver", result["summary"])

    def test_godot_project_audit_counts_settings_without_project_paths(self):
        source = """config_version=5

[application]
config/name="Private Game"
run/main_scene="res://scenes/main.tscn"

[autoload]
Global="*res://scripts/global.gd"

[editor_plugins]
enabled=PackedStringArray("res://addons/private/plugin.cfg")

[network]
api_token="secret-token-value"
endpoint="https://private.example"
"""
        result = wave25.godot_project_audit(self.write("project.godot", source))
        self.assert_report(result)
        self.assertIn("Autoload/singleton entries: 1", result["summary"])
        self.assertIn("Enabled editor plugin path entries: 1", result["summary"])
        self.assertIn("Potential hardcoded-secret settings (values withheld): 1", result["summary"])
        self.assertNotIn("Private Game", result["summary"])
        self.assertNotIn("secret-token-value", result["summary"])
        self.assertNotIn("private.example", result["summary"])

    def test_unity_package_audit_counts_guid_records_without_paths(self):
        path = self.root / "sample.unitypackage"
        guid = "a" * 32
        members = {
            f"{guid}/asset": b"private asset bytes",
            f"{guid}/asset.meta": b"guid: private-guid",
            f"{guid}/pathname": b"Assets/Secret.prefab",
        }
        with tarfile.open(path, "w:gz") as archive:
            for name, data in members.items():
                info = tarfile.TarInfo(name)
                info.size = len(data)
                archive.addfile(info, io.BytesIO(data))
        result = wave25.unity_package_audit(path)
        self.assert_report(result)
        self.assertIn("GUID directory groups: 1", result["summary"])
        self.assertIn("Groups missing asset or pathname member: 0", result["summary"])
        self.assertIn("Groups missing asset.meta member: 0", result["summary"])
        self.assertNotIn("Assets/Secret.prefab", result["summary"])
        self.assertNotIn(guid, result["summary"])

    def test_unreal_project_audit_counts_modules_and_plugins_without_names(self):
        document = {
            "FileVersion": 3,
            "EngineAssociation": "5.x-private",
            "Modules": [
                {"Name": "PrivateGame", "Type": "Runtime"},
                {"Name": "PrivateEditor", "Type": "Editor"},
            ],
            "Plugins": [
                {"Name": "PrivatePlugin", "Enabled": True},
                {"Name": "DisabledPlugin", "Enabled": False},
            ],
            "apiToken": "sensitive-value",
            "TargetPlatforms": ["Win64"],
        }
        result = wave25.unreal_project_audit(self.write("project.uproject", json.dumps(document)))
        self.assert_report(result)
        self.assertIn("Module declarations: 2", result["summary"])
        self.assertIn("Enabled plugins: 1", result["summary"])
        self.assertIn("Disabled plugins: 1", result["summary"])
        self.assertIn("Potential secret-bearing descriptor fields (values withheld): 1", result["summary"])
        self.assertNotIn("PrivateGame", result["summary"])
        self.assertNotIn("sensitive-value", result["summary"])


if __name__ == "__main__":
    unittest.main()
