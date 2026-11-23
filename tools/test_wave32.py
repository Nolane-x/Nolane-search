from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest
import zipfile
from types import SimpleNamespace
from unittest.mock import patch

import wave32


class Wave32Tests(unittest.TestCase):
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

    def test_rdf_turtle_audit_counts_without_revealing_terms_or_literals(self):
        path = self.write(
            "sample.ttl",
            """
@prefix ex: <https://example.invalid/> .
ex:alice a ex:Person ; ex:name "PRIVATE_PERSON_SENTINEL" ; ex:active true .
ex:bob a ex:Person .
""",
        )
        result = wave32.rdf_graph_audit(path)
        report = self.report(result)
        self.assertIn("Syntax: turtle", report)
        self.assertIn("Triples/quads inspected: 4", report)
        self.assertIn("Distinct subjects: 2", report)
        self.assertNotIn("PRIVATE_PERSON_SENTINEL", report)
        self.assertNotIn("example.invalid", report)
        self.assertNotIn("ex:alice", report)

    def test_rdf_nquads_counts_named_graphs(self):
        path = self.write(
            "sample.nq",
            '<https://example.invalid/s> <https://example.invalid/p> "secret" <https://example.invalid/g> .\n',
        )
        report = self.report(wave32.rdf_graph_audit(path))
        self.assertIn("Named graphs: 1", report)
        self.assertNotIn("secret", report)
        self.assertNotIn("example.invalid", report)

    def test_rdf_parser_rejects_unsupported_syntax_and_malformed_data(self):
        unsupported = self.write("sample.jsonld", '{"@context":"https://example.invalid/context"}')
        with self.assertRaisesRegex(RuntimeError, "Supported RDF uploads"):
            wave32.rdf_graph_audit(unsupported)
        malformed = self.write("invalid.ttl", "@prefix ex: <urn:example:> . ex:s ex:p")
        with self.assertRaisesRegex(RuntimeError, "could not be parsed"):
            wave32.rdf_graph_audit(malformed)

    def make_shacl_zip(self, data: str, shapes: str, name: str = "package.zip") -> Path:
        path = self.root / name
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("data.ttl", data)
            archive.writestr("shapes.ttl", shapes)
        return path

    def test_shacl_valid_graph_conforms(self):
        data = """
@prefix ex: <https://example.invalid/> .
ex:alice a ex:Person ; ex:name "PRIVATE_PERSON_SENTINEL" .
"""
        shapes = """
@prefix ex: <https://example.invalid/> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
ex:PersonShape a sh:NodeShape ;
  sh:targetClass ex:Person ;
  sh:property [ sh:path ex:name ; sh:minCount 1 ] .
"""
        result = wave32.shacl_validate(self.make_shacl_zip(data, shapes))
        report = self.report(result)
        self.assertIn("Conforms: yes", report)
        self.assertIn("Validation results: 0", report)
        self.assertNotIn("PRIVATE_PERSON_SENTINEL", report)
        self.assertNotIn("example.invalid", report)

    def test_shacl_violation_reports_only_aggregated_severity(self):
        data = """
@prefix ex: <https://example.invalid/> .
ex:alice a ex:Person .
"""
        shapes = """
@prefix ex: <https://example.invalid/> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
ex:PersonShape a sh:NodeShape ;
  sh:targetClass ex:Person ;
  sh:property [ sh:path ex:name ; sh:minCount 1 ; sh:message "PRIVATE_SHAPE_MESSAGE" ] .
"""
        report = self.report(wave32.shacl_validate(self.make_shacl_zip(data, shapes)))
        self.assertIn("Conforms: no", report)
        self.assertIn("Validation results: 1", report)
        self.assertIn("Violation: 1", report)
        self.assertNotIn("PRIVATE_SHAPE_MESSAGE", report)
        self.assertNotIn("example.invalid", report)

    def test_shacl_rejects_remote_and_executable_extensions(self):
        shapes = """
@prefix ex: <urn:example:> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
ex:Shape a sh:NodeShape ; sh:sparql [ sh:select "SELECT * WHERE { ?this ?p ?o }" ] .
"""
        path = self.make_shacl_zip("@prefix ex: <urn:example:> . ex:a ex:b ex:c .", shapes)
        with self.assertRaisesRegex(RuntimeError, "extensions that are disabled"):
            wave32.shacl_validate(path)

    def test_shacl_requires_exact_root_members(self):
        path = self.root / "bad.zip"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("data.ttl", "@prefix ex: <urn:> . ex:a ex:b ex:c .")
            archive.writestr("shapes.ttl", "@prefix sh: <http://www.w3.org/ns/shacl#> .")
            archive.writestr("../escape.ttl", "not extracted")
        with self.assertRaisesRegex(RuntimeError, "exactly data.ttl and shapes.ttl"):
            wave32.shacl_validate(path)

    def test_cron_preview_uses_fixed_utc_base_and_does_not_echo_expression(self):
        path = self.write("schedules.cron", "# batch jobs\n0 9 * * 1\n*/15 * * * *\nnot-a-cron\n")
        base = datetime(2026, 1, 6, 0, 0, tzinfo=timezone.utc)
        report = self.report(wave32.cron_schedule_audit(path, base))
        self.assertIn("Schedules inspected: 3", report)
        self.assertIn("Valid schedules: 2", report)
        self.assertIn("Invalid schedules: 1", report)
        self.assertIn("Line 2: valid; next runs:", report)
        self.assertIn("2026-01-12 09:00 UTC", report)
        self.assertNotIn("*/15 * * * *", report)
        self.assertNotIn("not-a-cron", report)

    def test_cron_rejects_six_field_expressions(self):
        path = self.write("schedules.cron", "0 0 9 * * *\n")
        report = self.report(wave32.cron_schedule_audit(path, datetime(2026, 1, 1, tzinfo=timezone.utc)))
        self.assertIn("Invalid schedules: 1", report)

    def test_pdf_searchable_uses_neutral_paths_and_creates_pdf_output(self):
        source = self.write("private-customer-name.pdf", b"%PDF-1.7\nsynthetic")
        captured = {}

        def fake_run(command, **kwargs):
            captured["command"] = command
            captured["cwd"] = kwargs["cwd"]
            captured["timeout"] = kwargs["timeout"]
            captured["input"] = (Path(kwargs["cwd"]) / "input.pdf").read_bytes()
            (Path(kwargs["cwd"]) / "output.pdf").write_bytes(b"%PDF-1.7\nsearchable")
            return SimpleNamespace(returncode=0, stdout="", stderr="PRIVATE_STDERR_SENTINEL")

        with patch.object(wave32.subprocess, "run", side_effect=fake_run):
            result = wave32.pdf_ocr_searchable(source)

        self.assertTrue(Path(result["output_path"]).is_file())
        self.assertTrue(result["output_path"].endswith("-searchable.pdf"))
        self.assertEqual(captured["input"], b"%PDF-1.7\nsynthetic")
        self.assertEqual(captured["timeout"], wave32.PDF_OCR_TIMEOUT_SECONDS)
        self.assertIn("--skip-text", captured["command"])
        self.assertIn("eng+vie", captured["command"])
        self.assertIn("--deskew", captured["command"])
        self.assertIn("--rotate-pages", captured["command"])
        self.assertNotIn("private-customer-name.pdf", captured["command"])
        self.assertNotIn("PRIVATE_STDERR_SENTINEL", result["summary"])

    def test_pdf_ocr_fails_without_exposing_raw_diagnostics(self):
        source = self.write("sample.pdf", b"%PDF-1.7\nsynthetic")
        with patch.object(
            wave32.subprocess,
            "run",
            return_value=SimpleNamespace(returncode=1, stdout="", stderr="PRIVATE_ERROR_SENTINEL"),
        ):
            with self.assertRaisesRegex(RuntimeError, "diagnostic output is withheld"):
                wave32.pdf_ocr_searchable(source)

    def test_pdf_ocr_timeout_is_bounded(self):
        source = self.write("sample.pdf", b"%PDF-1.7\nsynthetic")
        import subprocess
        with patch.object(
            wave32.subprocess,
            "run",
            side_effect=subprocess.TimeoutExpired("ocrmypdf", 1),
        ):
            with self.assertRaisesRegex(RuntimeError, "20-minute processing limit"):
                wave32.pdf_ocr_searchable(source)


if __name__ == "__main__":
    unittest.main()
