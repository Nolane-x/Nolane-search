"""Wave 31 pinned PRONOM/Siegfried identification.

The wrapper runs one local file only, emits a privacy-reduced report and never
returns the submitted filename, runner path, raw stderr or file content.
"""
from __future__ import annotations

import html
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

from wave28 import _report, _size_guard


MAX_SIEGFRIED_OUTPUT = 1024 * 1024
SIEGFRIED_TIMEOUT_SECONDS = 30


def _label(value: object, limit: int = 140) -> str:
    if not isinstance(value, str):
        return ""
    cleaned = "".join(ch for ch in value if ch >= " " and ch not in "\x7f")
    return html.escape(cleaned.strip()[:limit], quote=False)


def parse_siegfried_json(content: str) -> dict:
    """Validate one-file Siegfried JSON output and return privacy-safe aggregates."""
    if not isinstance(content, str) or len(content.encode("utf-8", errors="replace")) > MAX_SIEGFRIED_OUTPUT:
        raise RuntimeError("Siegfried output exceeds the 1 MiB report input limit.")
    try:
        payload = json.loads(content)
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise RuntimeError("Siegfried returned malformed JSON.") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("Siegfried output root is not a JSON object.")
    engine = _label(payload.get("siegfried"), 40) or "unknown"
    created = payload.get("created")
    signature_date = _label(created, 40)
    files = payload.get("files")
    if not isinstance(files, list) or len(files) != 1 or not isinstance(files[0], dict):
        raise RuntimeError("Siegfried did not return exactly one file record.")
    file_record = files[0]
    matches = file_record.get("matches")
    if not isinstance(matches, list) or len(matches) > 128:
        raise RuntimeError("Siegfried match list is invalid or exceeds the 128-match limit.")
    errors = file_record.get("errors")
    error_present = isinstance(errors, str) and bool(errors.strip())
    file_size = file_record.get("filesize")
    if isinstance(file_size, bool) or not isinstance(file_size, int) or file_size < 0:
        file_size = None
    unique = set()
    puids = set()
    formats = set()
    versions = set()
    mimes = set()
    basis_categories = set()
    for item in matches:
        if not isinstance(item, dict):
            continue
        namespace = item.get("ns", item.get("namespace", ""))
        identifier = item.get("id", item.get("puid", ""))
        format_name = item.get("format", item.get("name", ""))
        version = item.get("version", "")
        mime = item.get("mime", item.get("mime_type", ""))
        basis = item.get("basis", "")
        namespace = namespace.strip().lower() if isinstance(namespace, str) else ""
        identifier = identifier.strip() if isinstance(identifier, str) else ""
        format_name = _label(format_name, 140)
        version = _label(version, 80)
        mime = _label(mime, 120)
        basis_text = basis.lower() if isinstance(basis, str) else ""
        if "extension" in basis_text or "filename" in basis_text:
            basis_categories.add("filename-extension hint")
        elif "container" in basis_text:
            basis_categories.add("container signature")
        elif any(token in basis_text for token in ("byte", "text", "xml", "riff", "signature")):
            basis_categories.add("content signature")
        elif basis_text:
            basis_categories.add("other signature basis")
        if identifier and re.fullmatch(r"(?:fmt|x-fmt|xpr)/[A-Za-z0-9._-]+", identifier, re.I):
            puids.add(identifier.lower())
        if format_name:
            formats.add(format_name)
        if version:
            versions.add(version)
        if mime:
            mimes.add(mime)
        if identifier or format_name or mime:
            unique.add((namespace, identifier, format_name, version, mime))
    if len(unique) > 128:
        raise RuntimeError("Siegfried returned too many distinct identification results.")
    selected = sorted(unique, key=lambda item: (item[0], item[1], item[2], item[3], item[4]))
    display = []
    for namespace, identifier, format_name, version, mime in selected[:8]:
        fields = []
        if namespace:
            fields.append(namespace.upper())
        if identifier:
            fields.append(identifier)
        label = format_name or "Format name unavailable"
        if version:
            label += " " + version
        fields.append(label)
        if mime:
            fields.append(mime)
        display.append(" · ".join(fields))
    if not selected:
        verdict = "UNKNOWN — no matching content signature"
    elif len(selected) > 1:
        verdict = "AMBIGUOUS — multiple signature matches"
    elif basis_categories == {"filename-extension hint"}:
        verdict = "PROVISIONAL — identification relies on an extension hint only"
    else:
        verdict = "IDENTIFIED — one content/signature match"
    return {
        "engine": engine,
        "signature_date": signature_date,
        "file_size": file_size,
        "match_count": len(selected),
        "puids": sorted(puids),
        "formats": sorted(formats),
        "versions": sorted(versions),
        "mimes": sorted(mimes),
        "basis_categories": sorted(basis_categories),
        "display": display,
        "truncated_matches": max(0, len(selected) - len(display)),
        "error_present": error_present,
        "verdict": verdict,
    }


def file_format_identify(path: Path) -> dict:
    """Identify one local file against a pinned Siegfried signature database."""
    _size_guard(path)
    binary = os.environ.get("NOLANE_SIEGFRIED_BINARY") or shutil.which("sf") or ""
    signature = os.environ.get("NOLANE_SIEGFRIED_SIG") or ""
    if not binary or not Path(binary).is_file():
        raise RuntimeError("Pinned Siegfried engine is unavailable; the runner install step did not complete.")
    if not signature or not Path(signature).is_file():
        raise RuntimeError("Pinned PRONOM signature database is unavailable; the runner install step did not complete.")
    try:
        with path.open("rb") as source:
            process = subprocess.run(
                [binary, "-json", "-multi", "1", "-sig", signature, "-name", "nolane-upload", "-"],
                stdin=source,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=SIEGFRIED_TIMEOUT_SECONDS,
                check=False,
            )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Siegfried identification exceeded the 30-second time limit.") from exc
    except OSError as exc:
        raise RuntimeError("Could not start the local Siegfried identification engine.") from exc
    if process.returncode != 0:
        raise RuntimeError("Siegfried could not identify this file with the pinned PRONOM database.")
    return _report_from_result(path, parse_siegfried_json(process.stdout))


def _report_from_result(path: Path, result: dict) -> dict:
    lines = [
        result["verdict"],
        f"Siegfried engine: {result['engine']}",
        f"PRONOM signature set created: {result['signature_date'] or 'date unavailable'}",
        f"Input size: {result['file_size'] if result['file_size'] is not None else path.stat().st_size:,} bytes",
        f"Distinct signature matches: {result['match_count']:,}",
        f"PRONOM PUIDs: {', '.join(result['puids'][:8]) if result['puids'] else 'none'}",
        f"Format labels: {', '.join(result['formats'][:8]) if result['formats'] else 'none'}",
        f"MIME types: {', '.join(result['mimes'][:8]) if result['mimes'] else 'none'}",
        f"Identification records shown: {len(result['display']):,}",
    ]
    lines.extend(f"- {item}" for item in result["display"])
    if result["truncated_matches"]:
        lines.append(f"Additional distinct matches not shown: {result['truncated_matches']:,}")
    if result["basis_categories"]:
        lines.append("Match basis: " + ", ".join(result["basis_categories"]))
    if result["error_present"]:
        lines.append("Siegfried reported a scan warning/error; raw diagnostic text is withheld.")
    lines.extend([
        "Identification is based on file signatures and may be unknown or ambiguous; it is not a malware scan or proof that a file is safe.",
        "The submitted filename, directory path, modification time, raw stderr, file contents and arbitrary metadata values are not included in this report.",
        "Only the single uploaded local file is scanned; archives are not recursively extracted.",
    ])
    return _report(path, "file-format-identify", "PRONOM/Siegfried file format identification", lines)
