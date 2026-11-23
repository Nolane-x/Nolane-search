"""Wave 33: offline HTML article extraction, Rego compilation, Kubernetes schema validation and Sigstore blob verification."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tempfile
import zipfile

from wave28 import _read_bounded, _report, _safe_member, _size_guard, _zip_index


MAX_HTML_BYTES = 10 * 1024 * 1024
MAX_ARTICLE_BYTES = 8 * 1024 * 1024
MAX_REGO_FILES = 60
MAX_REGO_FILE_BYTES = 1024 * 1024
MAX_REGO_TOTAL_BYTES = 4 * 1024 * 1024
MAX_REGO_TIMEOUT = 45
MAX_K8S_TIMEOUT = 60
MAX_COSIGN_TIMEOUT = 45
MAX_COSIGN_ARTIFACT_BYTES = 10 * 1024 * 1024
MAX_COSIGN_BUNDLE_BYTES = 2 * 1024 * 1024
MAX_COSIGN_ROOT_BYTES = 4 * 1024 * 1024
MAX_COSIGN_KEY_BYTES = 32 * 1024

KUBERNETES_VERSION = "1.34.0"
KUBERNETES_SCHEMA_COMMIT = "0c4dd99d9873f7b4c2da24c008476f5841adbe2d"
KUBERNETES_SCHEMA_TEMPLATE = (
    "https://raw.githubusercontent.com/yannh/kubernetes-json-schema/"
    + KUBERNETES_SCHEMA_COMMIT
    + "/{{.NormalizedKubernetesVersion}}-standalone{{.StrictSuffix}}/{{.ResourceKind}}.json"
)


def web_article_extract(path: Path) -> dict:
    """Extract a readable article from already-downloaded HTML; never fetch a URL."""
    if path.stat().st_size > MAX_HTML_BYTES:
        raise RuntimeError("HTML input exceeds the 10 MiB extraction limit.")
    if path.suffix.lower() not in {".html", ".htm", ".xhtml"}:
        raise RuntimeError("Article extraction accepts HTML and XHTML files only.")

    try:
        raw = path.read_bytes()
        html = raw.decode("utf-8-sig", errors="replace")
        from trafilatura import extract, extract_metadata

        metadata = extract_metadata(html)
        article = extract(
            html,
            output_format="markdown",
            include_comments=False,
            include_links=False,
            include_tables=True,
            include_formatting=True,
            favor_precision=True,
            deduplicate=True,
        )
    except Exception as exc:
        raise RuntimeError("HTML article extraction failed safely.") from exc

    if not isinstance(article, str) or not article.strip():
        raise RuntimeError("No reliable main article content was found in this HTML document.")

    title = str(getattr(metadata, "title", "") or "").strip()[:500]
    author = str(getattr(metadata, "author", "") or "").strip()[:300]
    date = str(getattr(metadata, "date", "") or "").strip()[:80]
    site = str(getattr(metadata, "sitename", "") or "").strip()[:300]
    description = str(getattr(metadata, "description", "") or "").strip()[:500]

    header = ["# " + (title or "Extracted article"), ""]
    if site:
        header.append(f"**Site:** {site}")
    if author:
        header.append(f"**Author:** {author}")
    if date:
        header.append(f"**Date:** {date}")
    if description:
        header.extend(["", description])
    header.extend(["", "---", ""])
    output_text = "\n".join(header) + article.strip() + "\n"
    encoded = output_text.encode("utf-8")
    if len(encoded) > MAX_ARTICLE_BYTES:
        raise RuntimeError("Extracted article exceeds the 8 MiB output limit.")

    output = path.with_name(path.stem + "-article.md")
    if output.exists() or output.is_symlink():
        raise RuntimeError("An article output with this name already exists.")
    output.write_bytes(encoded)
    summary = f"Extracted article Markdown ({len(encoded):,} bytes)."
    if title:
        summary += f" Title: {title[:160]}"
    return {"summary": summary, "output_path": str(output)}


def _rego_inputs(path: Path) -> tuple[dict[str, bytes], zipfile.ZipFile | None]:
    """Read one Rego module or a safe ZIP tree without extracting untrusted paths."""
    if path.suffix.lower() != ".zip":
        if path.suffix.lower() != ".rego":
            raise RuntimeError("Rego policy check accepts a .rego file or a ZIP of .rego modules.")
        if path.stat().st_size <= 0 or path.stat().st_size > MAX_REGO_FILE_BYTES:
            raise RuntimeError("A Rego module must be between 1 byte and 1 MiB.")
        try:
            raw = path.read_bytes()
            raw.decode("utf-8")
            return {"policy.rego": raw}, None
        except (OSError, UnicodeError) as exc:
            raise RuntimeError("Rego source file is not readable UTF-8.") from exc

    archive = None
    try:
        archive, members, expanded = _zip_index(path, "Rego policy")
        rego_names = sorted(name for name in members if name.lower().endswith(".rego"))
        if not rego_names:
            raise RuntimeError("Rego ZIP must contain at least one .rego module.")
        if len(rego_names) > MAX_REGO_FILES:
            raise RuntimeError("Rego ZIP exceeds the 60-module limit.")
        if len(rego_names) != len(members):
            raise RuntimeError("Rego ZIP may contain only .rego files.")
        total = 0
        contents = {}
        for name in rego_names:
            info = members[name]
            if info.file_size <= 0 or info.file_size > MAX_REGO_FILE_BYTES:
                raise RuntimeError("Each Rego module must be between 1 byte and 1 MiB.")
            if info.compress_size == 0 or info.file_size / info.compress_size > 100:
                raise RuntimeError("Rego ZIP compression ratio exceeds the safety limit.")
            total += info.file_size
            if total > MAX_REGO_TOTAL_BYTES:
                raise RuntimeError("Rego ZIP exceeds the 4 MiB combined source limit.")
            raw = _read_bounded(archive, info, MAX_REGO_FILE_BYTES)
            raw.decode("utf-8")
            contents[name] = raw
        return contents, archive
    except RuntimeError:
        if archive:
            archive.close()
        raise
    except (OSError, UnicodeError, zipfile.BadZipFile) as exc:
        if archive:
            archive.close()
        raise RuntimeError("Rego ZIP is malformed or contains non-UTF-8 source.") from exc


def rego_policy_check(path: Path) -> dict:
    """Parse and compile Rego modules only; policy rules and built-ins are never evaluated."""
    _size_guard(path)
    source_files, archive = _rego_inputs(path)
    try:
        with tempfile.TemporaryDirectory(prefix="nolane-opa-") as temp:
            root = Path(temp)
            files = []
            for name, raw in source_files.items():
                relative = PurePosixPath(name)
                if not _safe_member(name) or any(part in {"", ".", ".."} for part in relative.parts):
                    raise RuntimeError("Rego package contains an unsafe source path.")
                destination = root.joinpath(*relative.parts)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(raw)
                files.append(str(destination))
            try:
                result = subprocess.run(
                    ["opa", "check", "--strict", "--format=json", "--rego-v1", *files],
                    cwd=root,
                    env={"PATH": os.environ.get("PATH", ""), "HOME": str(root), "TMPDIR": str(root)},
                    capture_output=True,
                    text=True,
                    timeout=MAX_REGO_TIMEOUT,
                    check=False,
                )
            except subprocess.TimeoutExpired as exc:
                raise RuntimeError("Rego compilation exceeded the 45-second processing limit.") from exc
            except OSError as exc:
                raise RuntimeError("The pinned OPA compiler is unavailable on this runner.") from exc
    finally:
        if archive:
            archive.close()

    passed = result.returncode == 0
    return _report(path, "rego-policy-check", "OPA Rego static compilation", [
        f"Modules inspected: {len(source_files):,}",
        f"Rego v1 strict compilation: {'passed' if passed else 'failed'}",
        "Execution boundary: rules, queries and built-ins are never evaluated; no input document or network source is loaded.",
        "Privacy: source text, package identifiers and raw compiler diagnostics are withheld.",
        "Scope: parse/compile validation is not a proof of policy correctness, authorization safety or runtime behavior.",
    ])


def kubernetes_schema_validate(path: Path) -> dict:
    """Validate YAML against a pinned Kubernetes OpenAPI JSON-schema snapshot."""
    if path.stat().st_size <= 0 or path.stat().st_size > 10 * 1024 * 1024:
        raise RuntimeError("Kubernetes YAML input must be between 1 byte and 10 MiB.")
    if path.suffix.lower() not in {".yaml", ".yml"}:
        raise RuntimeError("Kubernetes schema validation accepts .yaml and .yml files only.")

    try:
        with tempfile.TemporaryDirectory(prefix="nolane-kubeconform-") as temp:
            root = Path(temp)
            manifest = root / "manifest.yaml"
            cache = root / "schema-cache"
            cache.mkdir()
            shutil.copyfile(path, manifest)
            command = [
                "kubeconform",
                "-strict",
                "-summary",
                "-output", "json",
                "-n", "2",
                "-cache", str(cache),
                "-kubernetes-version", KUBERNETES_VERSION,
                "-schema-location", KUBERNETES_SCHEMA_TEMPLATE,
                str(manifest),
            ]
            try:
                result = subprocess.run(
                    command,
                    cwd=root,
                    env={"PATH": os.environ.get("PATH", ""), "HOME": str(root), "TMPDIR": str(root)},
                    capture_output=True,
                    text=True,
                    timeout=MAX_K8S_TIMEOUT,
                    check=False,
                )
            except subprocess.TimeoutExpired as exc:
                raise RuntimeError("Kubernetes schema validation exceeded the 60-second processing limit.") from exc
            except OSError as exc:
                raise RuntimeError("The pinned Kubeconform validator is unavailable on this runner.") from exc
    except RuntimeError:
        raise

    try:
        payload = json.loads(result.stdout or "{}")
        summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
        if not isinstance(summary, dict):
            raise ValueError("summary")
        valid = int(summary.get("valid", 0))
        invalid = int(summary.get("invalid", 0))
        errors = int(summary.get("errors", 0))
        skipped = int(summary.get("skipped", 0))
        total = valid + invalid + errors + skipped
        if total <= 0:
            raise ValueError("no resources")
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Kubeconform did not return a valid structured validation summary.") from exc

    passed = result.returncode == 0 and invalid == 0 and errors == 0
    return _report(path, "kubernetes-schema-validation", "Kubernetes OpenAPI schema validation", [
        f"Schema baseline: Kubernetes {KUBERNETES_VERSION}",
        f"Schema source commit: {KUBERNETES_SCHEMA_COMMIT}",
        f"Resources inspected: {total:,}",
        f"Valid: {valid:,}",
        f"Invalid: {invalid:,}",
        f"Schema/parser errors: {errors:,}",
        f"Skipped: {skipped:,}",
        f"Result: {'passed' if passed else 'failed'}",
        "Scope: strict OpenAPI/JSON-Schema validation only; CRDs, admission controllers, policy engines and server-side API validation are not included.",
        "Privacy: resource names, namespaces, manifest paths, raw validation messages and YAML values are withheld.",
    ])


def cosign_verify_blob(path: Path) -> dict:
    """Verify a Sigstore bundle with a user-supplied public key and local trusted root."""
    _size_guard(path)
    if path.suffix.lower() != ".zip":
        raise RuntimeError("Cosign verification requires a ZIP with artifact.bin, artifact.sigstore.json, cosign.pub and trusted_root.json.")

    archive = None
    try:
        archive, members, expanded = _zip_index(path, "Cosign verification")
        expected = {"artifact.bin", "artifact.sigstore.json", "cosign.pub", "trusted_root.json"}
        if set(members) != expected:
            raise RuntimeError("Cosign ZIP must contain exactly artifact.bin, artifact.sigstore.json, cosign.pub and trusted_root.json at its root.")
        limits = {
            "artifact.bin": MAX_COSIGN_ARTIFACT_BYTES,
            "artifact.sigstore.json": MAX_COSIGN_BUNDLE_BYTES,
            "cosign.pub": MAX_COSIGN_KEY_BYTES,
            "trusted_root.json": MAX_COSIGN_ROOT_BYTES,
        }
        contents = {}
        for name, info in members.items():
            limit = limits[name]
            if info.file_size <= 0 or info.file_size > limit:
                raise RuntimeError(f"Cosign package member {name} exceeds its size limit.")
            if info.compress_size == 0 or info.file_size / info.compress_size > 100:
                raise RuntimeError("Cosign ZIP compression ratio exceeds the safety limit.")
            contents[name] = _read_bounded(archive, info, limit)
        if b"-----BEGIN PUBLIC KEY-----" not in contents["cosign.pub"]:
            raise RuntimeError("cosign.pub must be a PEM public key.")
        bundle = json.loads(contents["artifact.sigstore.json"].decode("utf-8"))
        trusted_root = json.loads(contents["trusted_root.json"].decode("utf-8"))
        if not isinstance(bundle, dict) or not isinstance(trusted_root, dict):
            raise RuntimeError("Cosign bundle and trusted root must be JSON objects.")
        artifact_digest = hashlib.sha256(contents["artifact.bin"]).hexdigest()
    except RuntimeError:
        if archive:
            archive.close()
        raise
    except (OSError, UnicodeError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        if archive:
            archive.close()
        raise RuntimeError("Cosign package contains malformed JSON, key material or ZIP data.") from exc

    try:
        with tempfile.TemporaryDirectory(prefix="nolane-cosign-") as temp:
            root = Path(temp)
            names = {
                "artifact.bin": root / "artifact.bin",
                "artifact.sigstore.json": root / "bundle.json",
                "cosign.pub": root / "cosign.pub",
                "trusted_root.json": root / "trusted-root.json",
            }
            for name, destination in names.items():
                destination.write_bytes(contents[name])
            command = [
                "cosign", "verify-blob",
                "--key", str(names["cosign.pub"]),
                "--bundle", str(names["artifact.sigstore.json"]),
                "--trusted-root", str(names["trusted_root.json"]),
                str(names["artifact.bin"]),
            ]
            try:
                result = subprocess.run(
                    command,
                    cwd=root,
                    env={"PATH": os.environ.get("PATH", ""), "HOME": str(root), "TMPDIR": str(root)},
                    capture_output=True,
                    text=True,
                    timeout=MAX_COSIGN_TIMEOUT,
                    check=False,
                )
            except subprocess.TimeoutExpired as exc:
                raise RuntimeError("Cosign verification exceeded the 45-second processing limit.") from exc
            except OSError as exc:
                raise RuntimeError("The pinned Cosign verifier is unavailable on this runner.") from exc
    finally:
        if archive:
            archive.close()

    passed = result.returncode == 0
    return _report(path, "cosign-verification", "Sigstore blob signature verification", [
        f"Signature verification: {'verified' if passed else 'not verified'}",
        f"Artifact SHA-256: {artifact_digest}",
        "Verification mode: local PEM public key + Sigstore bundle + user-supplied TrustedRoot; no KMS or keyless identity lookup.",
        "Privacy: artifact bytes, public-key contents, certificate identities and raw verifier diagnostics are withheld.",
        "Scope: this verifies the supplied signature against the supplied trust material; it does not establish that the signer is trusted by your organization.",
    ])
