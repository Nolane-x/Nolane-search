from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
import zipfile
from unittest.mock import patch

import wave33


class Wave33Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def report(self, result: dict) -> str:
        return Path(result["output_path"]).read_text(encoding="utf-8")

    def write(self, name: str, content: str | bytes) -> Path:
        path = self.root / name
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")
        return path

    def test_article_extracts_main_content_and_metadata_without_boilerplate(self):
        path = self.write("article.html", """
<!doctype html>
<html lang="en">
<head>
<title>Open source research report</title>
<meta name="author" content="Test Author">
<meta name="description" content="A test article description.">
</head>
<body>
<header>PRIVATE_HEADER_NAV_SENTINEL</header>
<nav><a href="/">Home</a><a href="/topics">Topics</a></nav>
<main><article>
<h1>Open source research report</h1>
<p>This is a distinctive paragraph about semantic data and document processing.</p>
<p>The second paragraph contains enough context for article extraction.</p>
</article></main>
<footer>PRIVATE_FOOTER_SENTINEL</footer>
</body></html>
""")
        result = wave33.web_article_extract(path)
        output = self.report(result)
        self.assertIn("Open source research report", output)
        self.assertIn("distinctive paragraph about semantic data", output)
        self.assertNotIn("PRIVATE_HEADER_NAV_SENTINEL", output)
        self.assertNotIn("PRIVATE_FOOTER_SENTINEL", output)
        self.assertTrue(result["output_path"].endswith("-article.md"))

    def test_article_rejects_empty_or_nonarticle_html(self):
        path = self.write("empty.html", "<html><head><title>Empty</title></head><body><nav>Only navigation</nav></body></html>")
        with self.assertRaisesRegex(RuntimeError, "No reliable main article"):
            wave33.web_article_extract(path)

    def test_article_rejects_output_collision(self):
        path = self.write("story.html", "<html><body><main><article><p>Some long enough article content to extract reliably.</p></article></main></body></html>")
        self.write("story-article.md", "existing")
        with self.assertRaisesRegex(RuntimeError, "already exists"):
            wave33.web_article_extract(path)

    def test_rego_single_module_uses_opa_check_only_and_suppresses_source(self):
        path = self.write("private-policy.rego", 'package authz\nallow if input.user == "secret-user"\n')
        with patch.object(
            wave33.subprocess,
            "run",
            return_value=SimpleNamespace(returncode=0, stdout="", stderr=""),
        ) as run:
            result = wave33.rego_policy_check(path)
        output = self.report(result)
        command = run.call_args.args[0]
        self.assertEqual(command[1], "check")
        self.assertIn("--strict", command)
        self.assertIn("--rego-v1", command)
        self.assertIn("Rego v1 strict compilation: passed", output)
        self.assertNotIn("secret-user", output)
        self.assertNotIn("private-policy.rego", command)

    def test_rego_compile_failure_hides_raw_diagnostics(self):
        path = self.write("bad.rego", "package authz\n")
        with patch.object(
            wave33.subprocess,
            "run",
            return_value=SimpleNamespace(returncode=1, stdout="PRIVATE_REGO_SOURCE", stderr="PRIVATE_REGO_DIAGNOSTIC"),
        ):
            output = self.report(wave33.rego_policy_check(path))
        self.assertIn("Rego v1 strict compilation: failed", output)
        self.assertNotIn("PRIVATE_REGO_SOURCE", output)
        self.assertNotIn("PRIVATE_REGO_DIAGNOSTIC", output)

    def test_rego_zip_rejects_path_traversal(self):
        path = self.root / "unsafe.zip"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("../escape.rego", "package authz")
        with self.assertRaisesRegex(RuntimeError, "unsafe member path"):
            wave33.rego_policy_check(path)

    def test_kubernetes_validation_uses_pinned_schema_and_reports_counts_only(self):
        path = self.write("deployment.yaml", "apiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: private-app\n")
        payload = {
            "resources": [
                {"filename": "manifest.yaml", "kind": "Deployment", "status": "VALID", "msg": ""},
            ],
            "summary": {"valid": 1, "invalid": 0, "errors": 0, "skipped": 0},
        }
        with patch.object(
            wave33.subprocess,
            "run",
            return_value=SimpleNamespace(returncode=0, stdout=__import__("json").dumps(payload), stderr=""),
        ) as run:
            output = self.report(wave33.kubernetes_schema_validate(path))
        command = run.call_args.args[0]
        self.assertIn("-strict", command)
        self.assertIn("1.34.0", command)
        self.assertTrue(any(".KindSuffix" in item for item in command))
        self.assertTrue(any(wave33.KUBERNETES_SCHEMA_COMMIT in item for item in command))
        self.assertIn("Valid: 1", output)
        self.assertNotIn("private-app", output)

    def test_kubernetes_invalid_resource_does_not_echo_schema_errors(self):
        path = self.write("invalid.yaml", "apiVersion: apps/v1\nkind: Deployment\n")
        payload = {
            "resources": [
                {"filename": "manifest.yaml", "kind": "Deployment", "status": "INVALID", "msg": "PRIVATE_SCHEMA_DIAGNOSTIC"},
            ],
            "summary": {"valid": 0, "invalid": 1, "errors": 0, "skipped": 0},
        }
        with patch.object(
            wave33.subprocess,
            "run",
            return_value=SimpleNamespace(returncode=1, stdout=__import__("json").dumps(payload), stderr="PRIVATE_SCHEMA_DIAGNOSTIC"),
        ):
            output = self.report(wave33.kubernetes_schema_validate(path))
        self.assertIn("Result: failed", output)
        self.assertIn("Invalid: 1", output)
        self.assertNotIn("PRIVATE_SCHEMA_DIAGNOSTIC", output)

    def _cosign_zip(self, path: Path, artifact: bytes = b"private artifact bytes"):
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("artifact.bin", artifact)
            archive.writestr("artifact.sigstore.json", '{"mediaType":"application/vnd.dev.sigstore.bundle.v0.3+json"}')
            archive.writestr("cosign.pub", "-----BEGIN PUBLIC KEY-----\nTEST\n-----END PUBLIC KEY-----\n")
            archive.writestr("trusted_root.json", '{"mediaType":"application/vnd.dev.sigstore.trustedroot+json","tlogs":[],"certificateAuthorities":[]}')
        return path

    def test_cosign_uses_local_public_key_bundle_and_trusted_root(self):
        path = self._cosign_zip(self.root / "verify.zip")
        with patch.object(
            wave33.subprocess,
            "run",
            return_value=SimpleNamespace(returncode=0, stdout="Verified OK", stderr=""),
        ) as run:
            output = self.report(wave33.cosign_verify_blob(path))
        command = run.call_args.args[0]
        self.assertEqual(command[0:2], ["cosign", "verify-blob"])
        self.assertIn("--key", command)
        self.assertIn("--bundle", command)
        self.assertIn("--trusted-root", command)
        self.assertIn("Signature verification: verified", output)
        self.assertNotIn("private artifact bytes", output)
        self.assertNotIn("PUBLIC KEY", output)

    def test_cosign_failure_suppresses_signature_diagnostics(self):
        path = self._cosign_zip(self.root / "verify.zip")
        with patch.object(
            wave33.subprocess,
            "run",
            return_value=SimpleNamespace(returncode=1, stdout="PRIVATE_CERTIFICATE_IDENTITY", stderr="PRIVATE_COSIGN_DIAGNOSTIC"),
        ):
            output = self.report(wave33.cosign_verify_blob(path))
        self.assertIn("Signature verification: not verified", output)
        self.assertNotIn("PRIVATE_CERTIFICATE_IDENTITY", output)
        self.assertNotIn("PRIVATE_COSIGN_DIAGNOSTIC", output)

    def test_cosign_requires_exact_root_files(self):
        path = self.root / "missing.zip"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("artifact.bin", b"artifact")
            archive.writestr("artifact.sigstore.json", "{}")
        with self.assertRaisesRegex(RuntimeError, "must contain exactly"):
            wave33.cosign_verify_blob(path)


if __name__ == "__main__":
    unittest.main()
