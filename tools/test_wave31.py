from __future__ import annotations

import json
import os
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import wave31


class Wave31Tests(unittest.TestCase):
    def sample_payload(self, matches=None, filename="/runner/private/user-uploaded-secret.pdf"):
        return {
            "siegfried": "1.11.9",
            "scandate": "2026-11-23T06:00:00Z",
            "signature": "/runner/private/signatures/default.sig",
            "created": "2026-09-27T02:12:50Z",
            "identifiers": [{"name": "pronom", "details": "DROID signature file V125"}],
            "files": [{
                "filename": filename,
                "filesize": 512,
                "modified": "2026-11-23T05:00:00Z",
                "errors": "PRIVATE_PATH_ERROR_SENTINEL",
                "matches": matches if matches is not None else [{
                    "ns": "pronom",
                    "id": "fmt/18",
                    "format": "Portable Document Format",
                    "version": "1.7",
                    "mime": "application/pdf",
                    "basis": "byte match at 0, signature 1",
                    "warning": "PRIVATE_MATCH_WARNING_SENTINEL",
                }],
            }],
        }

    def test_parses_pronom_result_and_removes_filename_path_and_raw_errors(self):
        payload = self.sample_payload()
        parsed = wave31.parse_siegfried_json(json.dumps(payload))
        self.assertEqual(parsed["engine"], "1.11.9")
        self.assertEqual(parsed["signature_date"], "2026-09-27T02:12:50Z")
        self.assertEqual(parsed["match_count"], 1)
        self.assertEqual(parsed["puids"], ["fmt/18"])
        self.assertIn("Portable Document Format", parsed["formats"])
        self.assertIn("application/pdf", parsed["mimes"])
        self.assertTrue(parsed["error_present"])
        report = wave31._report_from_result(Path("private-user-file.pdf"), parsed)["summary"]
        self.assertIn("fmt/18", report)
        self.assertIn("Portable Document Format", report)
        self.assertNotIn("private-user-file.pdf", report)
        self.assertNotIn("/runner/private", report)
        self.assertNotIn("PRIVATE_PATH_ERROR_SENTINEL", report)
        self.assertNotIn("PRIVATE_MATCH_WARNING_SENTINEL", report)
        self.assertNotIn("byte match at 0", report)

    def test_unknown_file_is_reported_without_inventing_a_format(self):
        parsed = wave31.parse_siegfried_json(json.dumps(self.sample_payload(matches=[])))
        self.assertEqual(parsed["match_count"], 0)
        self.assertEqual(parsed["verdict"], "UNKNOWN — no matching signature")
        self.assertEqual(parsed["puids"], [])
        report = wave31._report_from_result(Path("opaque.bin"), parsed)["summary"]
        self.assertIn("no matching signature", report)
        self.assertNotIn("Portable Document Format", report)

    def test_ambiguous_identification_keeps_distinct_matches_separate(self):
        matches = [
            {"ns": "pronom", "id": "fmt/18", "format": "Portable Document Format", "version": "1.7", "mime": "application/pdf"},
            {"ns": "pronom", "id": "fmt/19", "format": "Portable Document Format", "version": "1.4", "mime": "application/pdf"},
        ]
        parsed = wave31.parse_siegfried_json(json.dumps(self.sample_payload(matches=matches)))
        self.assertEqual(parsed["match_count"], 2)
        self.assertEqual(parsed["verdict"], "AMBIGUOUS — multiple signature matches")
        self.assertEqual(parsed["puids"], ["fmt/18", "fmt/19"])
        self.assertEqual(len(parsed["display"]), 2)

    def test_deduplicates_repeated_identification_records(self):
        match = {"ns": "pronom", "id": "fmt/18", "format": "Portable Document Format", "version": "1.7", "mime": "application/pdf"}
        parsed = wave31.parse_siegfried_json(json.dumps(self.sample_payload(matches=[match, match])))
        self.assertEqual(parsed["match_count"], 1)
        self.assertEqual(parsed["puids"], ["fmt/18"])

    def test_rejects_malformed_json_and_unexpected_file_count(self):
        with self.assertRaisesRegex(RuntimeError, "malformed JSON"):
            wave31.parse_siegfried_json("{not-json")
        payload = self.sample_payload()
        payload["files"].append(payload["files"][0])
        with self.assertRaisesRegex(RuntimeError, "exactly one file"):
            wave31.parse_siegfried_json(json.dumps(payload))

    def test_bounds_json_output_size_and_match_count(self):
        with self.assertRaisesRegex(RuntimeError, "1 MiB"):
            wave31.parse_siegfried_json(" " * (wave31.MAX_SIEGFRIED_OUTPUT + 1))
        payload = self.sample_payload(matches=[{"id": f"fmt/{n}", "format": "Test"} for n in range(129)])
        with self.assertRaisesRegex(RuntimeError, "128-match limit"):
            wave31.parse_siegfried_json(json.dumps(payload))

    def test_binary_and_signature_paths_are_required_before_execution(self):
        with tempfile.TemporaryDirectory() as temp:
            sample = Path(temp) / "sample.bin"
            sample.write_bytes(b"opaque")
            old_binary = os.environ.pop("NOLANE_SIEGFRIED_BINARY", None)
            old_sig = os.environ.pop("NOLANE_SIEGFRIED_SIG", None)
            try:
                with self.assertRaisesRegex(RuntimeError, "engine is unavailable"):
                    wave31.file_format_identify(sample)
            finally:
                if old_binary is not None:
                    os.environ["NOLANE_SIEGFRIED_BINARY"] = old_binary
                if old_sig is not None:
                    os.environ["NOLANE_SIEGFRIED_SIG"] = old_sig

    def test_runner_uses_neutral_stdin_name_and_never_passes_the_real_path_to_sf(self):
        payload = json.dumps(self.sample_payload())
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "private-name-and-path.pdf"
            binary = root / "sf"
            signature = root / "default.sig"
            source.write_bytes(b"synthetic-private-payload")
            binary.write_bytes(b"test-binary-placeholder")
            signature.write_bytes(b"test-signature-placeholder")
            env = {
                "NOLANE_SIEGFRIED_BINARY": str(binary),
                "NOLANE_SIEGFRIED_SIG": str(signature),
            }
            with patch.dict(os.environ, env):
                with patch.object(
                    wave31.subprocess,
                    "run",
                    return_value=SimpleNamespace(returncode=0, stdout=payload, stderr="PRIVATE_STDERR_SENTINEL"),
                ) as run:
                    result = wave31.file_format_identify(source)
            command = run.call_args.args[0]
            self.assertEqual(command[-3:], ["-name", "nolane-upload", "-"])
            self.assertNotIn(str(source), command)
            self.assertNotIn(source.name, command)
            self.assertEqual(run.call_args.kwargs["stdin"].name, str(source))
            self.assertEqual(run.call_args.kwargs["timeout"], wave31.SIEGFRIED_TIMEOUT_SECONDS)
            self.assertNotIn(source.name, result["summary"])
            self.assertNotIn(temp, result["summary"])
            self.assertNotIn("PRIVATE_STDERR_SENTINEL", result["summary"])

    def test_timeout_is_reported_without_leaking_the_filename(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "sensitive-file-name.dat"
            binary = Path(temp) / "sf"
            signature = Path(temp) / "default.sig"
            source.write_bytes(b"synthetic")
            binary.write_bytes(b"binary")
            signature.write_bytes(b"signature")
            with patch.dict(os.environ, {
                "NOLANE_SIEGFRIED_BINARY": str(binary),
                "NOLANE_SIEGFRIED_SIG": str(signature),
            }):
                with patch.object(
                    wave31.subprocess,
                    "run",
                    side_effect=wave31.subprocess.TimeoutExpired("sf", 30),
                ):
                    with self.assertRaisesRegex(RuntimeError, "30-second time limit"):
                        wave31.file_format_identify(source)

    def test_real_pinned_engine_identifies_a_zip_container_without_returning_path(self):
        binary = os.environ.get("NOLANE_SIEGFRIED_BINARY")
        signature = os.environ.get("NOLANE_SIEGFRIED_SIG")
        if not binary or not signature or not Path(binary).is_file() or not Path(signature).is_file():
            self.skipTest("Pinned Siegfried runtime is installed in CI and selected runner jobs only.")
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "private-archive-name.zip"
            with zipfile.ZipFile(source, "w", compression=zipfile.ZIP_STORED) as archive:
                archive.writestr("example.txt", "Synthetic format identification fixture.")
            result = wave31.file_format_identify(source)
            report = result["summary"]
            self.assertIn("Siegfried engine: 1.11.9", report)
            self.assertIn("Distinct signature matches:", report)
            self.assertNotIn("private-archive-name.zip", report)
            self.assertNotIn(temp, report)


if __name__ == "__main__":
    unittest.main()
