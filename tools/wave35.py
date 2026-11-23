from __future__ import annotations

import hashlib
import json
import math
import posixpath
import re
import struct
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any

MAX_FILE_BYTES = 20 * 1024 * 1024
MAX_SAFETENSORS_HEADER = 4 * 1024 * 1024
MAX_TEXT_CONFIG_BYTES = 2 * 1024 * 1024
MAX_GGUF_ENTRIES = 200_000
MAX_GGUF_ARRAY_ITEMS = 1_000_000
MAX_3MF_EXPANDED_BYTES = 100 * 1024 * 1024
MAX_3MF_PART_BYTES = 20 * 1024 * 1024
MAX_CHAT_EXAMPLES = 10_000


def _report(path: Path, prefix: str, title: str, lines: list[str]) -> dict:
    from wave28 import _report as shared_report

    return shared_report(path, prefix, title, lines)


def _check_file(path: Path, label: str, limit: int = MAX_FILE_BYTES) -> int:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"{label} input must be a regular local file.")
    size = path.stat().st_size
    if size <= 0:
        raise RuntimeError(f"{label} input is empty.")
    if size > limit:
        raise RuntimeError(f"{label} input exceeds the {limit // (1024 * 1024)} MiB processing limit.")
    return size


def _unique_json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def safetensors_audit(path: Path) -> dict:
    """Inspect a SafeTensors header and offsets without reading tensor payloads."""
    size = _check_file(path, "SafeTensors")
    if path.suffix.lower() != ".safetensors":
        raise RuntimeError("SafeTensors audit accepts .safetensors files.")

    with path.open("rb") as stream:
        prefix = stream.read(8)
        if len(prefix) != 8:
            raise RuntimeError("SafeTensors header length prefix is truncated.")
        header_size = struct.unpack("<Q", prefix)[0]
        if header_size < 2 or header_size > MAX_SAFETENSORS_HEADER or header_size > size - 8:
            raise RuntimeError("SafeTensors header length is outside the supported bounds.")
        raw_header = stream.read(header_size)

    if not raw_header.startswith(b"{"):
        raise RuntimeError("SafeTensors header must begin with a JSON object.")
    try:
        header_text = raw_header.decode("utf-8").rstrip(" ")
        header = json.loads(header_text, object_pairs_hook=_unique_json_object)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        raise RuntimeError("SafeTensors header is not valid UTF-8 JSON with unique keys.") from None
    if not isinstance(header, dict):
        raise RuntimeError("SafeTensors header root must be an object.")

    data_size = size - 8 - header_size
    tensor_count = 0
    malformed = 0
    unknown_dtypes = 0
    dtype_counts = Counter()
    ranges = []
    expected_bytes = {
        "BOOL": 1, "U8": 1, "I8": 1, "F8_E4M3": 1, "F8_E5M2": 1, "F8_E8M0": 1,
        "U16": 2, "I16": 2, "F16": 2, "BF16": 2,
        "U32": 4, "I32": 4, "F32": 4,
        "U64": 8, "I64": 8, "F64": 8,
    }
    for name, descriptor in header.items():
        if name == "__metadata__":
            if not isinstance(descriptor, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in descriptor.items()):
                malformed += 1
            continue
        tensor_count += 1
        if not isinstance(descriptor, dict):
            malformed += 1
            continue
        dtype = descriptor.get("dtype")
        shape = descriptor.get("shape")
        offsets = descriptor.get("data_offsets")
        if not isinstance(dtype, str) or not isinstance(shape, list) or not isinstance(offsets, list) or len(offsets) != 2:
            malformed += 1
            continue
        if len(shape) > 32 or any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in shape):
            malformed += 1
            continue
        if any(isinstance(value, bool) or not isinstance(value, int) for value in offsets):
            malformed += 1
            continue
        start, end = offsets
        if start < 0 or end < start or end > data_size:
            malformed += 1
            continue
        ranges.append((start, end))
        dtype_counts[dtype] += 1
        item_bytes = expected_bytes.get(dtype)
        if item_bytes is None:
            unknown_dtypes += 1
        else:
            elements = math.prod(shape)
            if elements * item_bytes != end - start:
                malformed += 1

    ranges.sort()
    overlaps = sum(1 for previous, current in zip(ranges, ranges[1:]) if current[0] < previous[1])
    uncovered = 0
    cursor = 0
    for start, end in ranges:
        if start > cursor:
            uncovered += 1
        cursor = max(cursor, end)
    if tensor_count == 0:
        malformed += 1
    return _report(path, "safetensors", "SafeTensors header and tensor-offset audit", [
        f"Tensor descriptors: {tensor_count:,}",
        f"Tensor dtypes: {len(dtype_counts):,} distinct",
        f"Header bytes: {header_size:,}",
        f"Tensor data bytes declared: {data_size:,}",
        f"Malformed descriptors / byte-size mismatches: {malformed:,}",
        f"Overlapping tensor ranges: {overlaps:,}",
        f"Uncovered gaps between tensor ranges: {uncovered:,}",
        f"Unrecognized dtype descriptors (offsets still checked): {unknown_dtypes:,}",
        "Privacy: tensor names, metadata keys/values and tensor weights are withheld",
        "Scope: parses the SafeTensors header only; it does not load tensors, execute model code or prove numerical correctness",
    ])


class _GGUFReader:
    def __init__(self, stream, file_size: int):
        self.stream = stream
        self.file_size = file_size
        self.offset = 0

    def read(self, amount: int) -> bytes:
        if amount < 0 or amount > self.file_size - self.offset:
            raise RuntimeError("GGUF structure extends beyond the uploaded file.")
        data = self.stream.read(amount)
        if len(data) != amount:
            raise RuntimeError("GGUF structure is truncated.")
        self.offset += amount
        return data

    def unpack(self, fmt: str):
        size = struct.calcsize(fmt)
        return struct.unpack(fmt, self.read(size))[0]

    def string(self) -> str:
        length = self.unpack("<Q")
        if length > 1_000_000:
            raise RuntimeError("GGUF string exceeds the 1 MiB metadata-string limit.")
        try:
            return self.read(length).decode("utf-8")
        except UnicodeDecodeError:
            raise RuntimeError("GGUF metadata contains an invalid UTF-8 string.") from None


_GGUF_SCALARS = {
    0: "<B", 1: "<b", 2: "<H", 3: "<h", 4: "<I", 5: "<i",
    6: "<f", 7: "<b", 10: "<Q", 11: "<q", 12: "<d",
}
_GGUF_SCALAR_BYTES = {key: struct.calcsize(value) for key, value in _GGUF_SCALARS.items()}


def _gguf_value(reader: _GGUFReader, value_type: int):
    if value_type == 8:
        return reader.string()
    if value_type == 9:
        element_type = reader.unpack("<I")
        count = reader.unpack("<Q")
        if count > MAX_GGUF_ARRAY_ITEMS:
            raise RuntimeError("GGUF metadata array exceeds the 1,000,000-item limit.")
        if element_type in _GGUF_SCALAR_BYTES:
            reader.read(_GGUF_SCALAR_BYTES[element_type] * count)
            return None
        if element_type == 8:
            for _ in range(count):
                reader.string()
            return None
        raise RuntimeError("GGUF metadata array uses an unsupported nested or unknown element type.")
    fmt = _GGUF_SCALARS.get(value_type)
    if fmt is None:
        raise RuntimeError("GGUF metadata uses an unknown value type.")
    return reader.unpack(fmt)


def gguf_model_audit(path: Path) -> dict:
    """Validate GGUF metadata tables and tensor offsets; never reads tensor weights."""
    size = _check_file(path, "GGUF")
    if path.suffix.lower() != ".gguf":
        raise RuntimeError("GGUF model audit accepts .gguf files.")
    try:
        with path.open("rb") as stream:
            reader = _GGUFReader(stream, size)
            if reader.read(4) != b"GGUF":
                raise RuntimeError("GGUF magic bytes are missing.")
            version = reader.unpack("<I")
            tensor_count = reader.unpack("<Q")
            metadata_count = reader.unpack("<Q")
            if version not in (2, 3):
                raise RuntimeError("Only GGUF versions 2 and 3 are supported.")
            if tensor_count > MAX_GGUF_ENTRIES or metadata_count > MAX_GGUF_ENTRIES:
                raise RuntimeError("GGUF header exceeds the bounded tensor/metadata-entry limits.")

            metadata_keys = set()
            alignment = 32
            for _ in range(metadata_count):
                key = reader.string()
                if key in metadata_keys:
                    raise RuntimeError("GGUF metadata contains duplicate keys.")
                metadata_keys.add(key)
                value_type = reader.unpack("<I")
                value = _gguf_value(reader, value_type)
                if key == "general.alignment":
                    if value_type != 4 or isinstance(value, bool) or not isinstance(value, int):
                        raise RuntimeError("GGUF general.alignment must be a uint32 value.")
                    alignment = value
            if alignment < 8 or alignment > 4096 or alignment & (alignment - 1):
                raise RuntimeError("GGUF tensor alignment must be a power of two between 8 and 4096.")

            tensor_names = set()
            tensor_type_counts = Counter()
            offsets = []
            invalid_descriptors = 0
            total_dimensions = 0
            for _ in range(tensor_count):
                tensor_name = reader.string()
                if tensor_name in tensor_names:
                    invalid_descriptors += 1
                tensor_names.add(tensor_name)
                dimensions = reader.unpack("<I")
                if dimensions < 1 or dimensions > 4:
                    raise RuntimeError("GGUF tensor dimension count is outside the supported 1–4 range.")
                shape = [reader.unpack("<Q") for _ in range(dimensions)]
                if any(dimension == 0 for dimension in shape):
                    invalid_descriptors += 1
                total_dimensions += dimensions
                tensor_type = reader.unpack("<I")
                tensor_type_counts[tensor_type] += 1
                tensor_offset = reader.unpack("<Q")
                offsets.append(tensor_offset)

            data_start = ((reader.offset + alignment - 1) // alignment) * alignment if tensor_count else reader.offset
            data_bytes = size - data_start
            invalid_offsets = 0
            if data_start > size:
                invalid_offsets += tensor_count or 1
            for tensor_offset in offsets:
                if tensor_offset % alignment != 0 or tensor_offset >= data_bytes:
                    invalid_offsets += 1
    except (OSError, struct.error, OverflowError):
        raise RuntimeError("GGUF metadata or tensor index is truncated or malformed.") from None

    return _report(path, "gguf", "GGUF model header and tensor-index audit", [
        f"GGUF version: {version}",
        f"Metadata entries: {metadata_count:,}",
        f"Tensor descriptors: {tensor_count:,}",
        f"Distinct tensor-type IDs: {len(tensor_type_counts):,}",
        f"Tensor dimensions inspected: {total_dimensions:,}",
        f"Tensor-data alignment: {alignment:,} bytes",
        f"Tensor-data section bytes: {max(0, data_bytes):,}",
        f"Duplicate tensor names / zero-sized dimensions: {invalid_descriptors:,}",
        f"Invalid or out-of-range tensor offsets: {invalid_offsets:,}",
        "Privacy: tensor names, metadata values, vocabulary entries and weight bytes are withheld",
        "Scope: checks header/index structure and offset bounds only; it does not decode quantized weights, run inference or validate model quality",
    ])


def hf_model_card_audit(path: Path) -> dict:
    """Review Hugging Face README model-card YAML and section coverage without exposing values."""
    _check_file(path, "Hugging Face model card", MAX_TEXT_CONFIG_BYTES)
    if path.suffix.lower() not in (".md", ".markdown"):
        raise RuntimeError("Hugging Face model-card audit accepts Markdown files.")
    try:
        text = path.read_text(encoding="utf-8-sig", errors="strict")
    except UnicodeDecodeError:
        raise RuntimeError("Model card must be valid UTF-8 Markdown.") from None
    lines = text.splitlines()
    frontmatter = None
    body = text
    if lines and lines[0].strip() == "---":
        closing = next((index for index in range(1, min(len(lines), 500)) if lines[index].strip() in ("---", "...")), None)
        if closing is not None:
            frontmatter = "\n".join(lines[1:closing])
            body = "\n".join(lines[closing + 1:])
    metadata = {}
    warnings = 0
    if frontmatter is None:
        warnings += 1
    else:
        try:
            import yaml
            parsed = yaml.safe_load(frontmatter)
        except Exception:
            raise RuntimeError("Model-card YAML front matter is invalid.") from None
        if not isinstance(parsed, dict):
            warnings += 1
        else:
            metadata = parsed
    expected_types = {
        "license": (str,), "pipeline_tag": (str,), "library_name": (str,),
        "tags": (list, str), "datasets": (list, str), "language": (list, str),
        "base_model": (list, str), "model-index": (list,),
    }
    malformed_fields = 0
    for key, allowed in expected_types.items():
        if key in metadata and not isinstance(metadata[key], allowed):
            malformed_fields += 1
    if "license" not in metadata:
        warnings += 1
    if "tags" not in metadata:
        warnings += 1

    headings = [match.group(1).strip().lower() for match in re.finditer(r"^#{1,6}\s+(.+?)\s*#*\s*$", body, re.M)]
    requirements = {
        "model description": ("model description", "model overview", "about the model"),
        "intended use": ("intended use", "intended uses", "use cases"),
        "limitations / risks": ("limitations", "risks", "bias"),
        "training data": ("training data", "datasets", "data sources"),
        "evaluation": ("evaluation", "results", "metrics", "benchmark"),
    }
    section_presence = {
        label: any(any(token in heading for token in tokens) for heading in headings)
        for label, tokens in requirements.items()
    }
    missing_sections = sum(1 for value in section_presence.values() if not value)
    return _report(path, "hf-model-card", "Hugging Face model-card metadata and completeness audit", [
        f"YAML front matter: {'present' if frontmatter is not None else 'missing'}",
        f"Metadata fields: {len(metadata):,}",
        f"License metadata: {'present' if 'license' in metadata else 'missing'}",
        f"Tags metadata: {'present' if 'tags' in metadata else 'missing'}",
        f"Malformed common metadata fields: {malformed_fields:,}",
        f"Recognized documentation sections: {sum(section_presence.values())}/{len(requirements)}",
        "Section coverage: " + ", ".join(f"{key}={'yes' if value else 'no'}" for key, value in section_presence.items()),
        f"Completeness warnings: {warnings + missing_sections:,}",
        "Privacy: model identifiers, dataset values, tags, metadata values and README body text are withheld",
        "Scope: checks local Markdown/YAML conventions and common model-card sections; it does not verify Hub identifiers, licenses or claims against an external registry",
    ])


def chat_dataset_audit(path: Path) -> dict:
    """Validate bounded JSONL chat fine-tuning examples without printing any message content."""
    size = _check_file(path, "Chat fine-tuning JSONL")
    if path.suffix.lower() not in (".jsonl", ".ndjson"):
        raise RuntimeError("Chat dataset audit accepts .jsonl or .ndjson files.")
    if size > 20 * 1024 * 1024:
        raise RuntimeError("Chat dataset exceeds the 20 MiB limit.")
    valid = invalid = user_examples = assistant_examples = duplicates = 0
    role_counts = Counter()
    seen = set()
    try:
        with path.open("r", encoding="utf-8-sig") as stream:
            for line_number, raw_line in enumerate(stream, 1):
                if line_number > MAX_CHAT_EXAMPLES:
                    raise RuntimeError("Chat dataset exceeds the 10,000-example processing limit.")
                line = raw_line.strip()
                if not line:
                    continue
                digest = hashlib.sha256(line.encode("utf-8")).digest()
                if digest in seen:
                    duplicates += 1
                seen.add(digest)
                try:
                    row = json.loads(line, object_pairs_hook=_unique_json_object)
                except (json.JSONDecodeError, ValueError):
                    invalid += 1
                    continue
                messages = row.get("messages") if isinstance(row, dict) else None
                if not isinstance(messages, list) or not messages:
                    invalid += 1
                    continue
                row_roles = []
                malformed = False
                for message in messages:
                    if not isinstance(message, dict):
                        malformed = True
                        continue
                    role = message.get("role")
                    if role not in ("system", "developer", "user", "assistant", "tool"):
                        malformed = True
                    else:
                        row_roles.append(role)
                        role_counts[role] += 1
                    content = message.get("content")
                    has_tool_calls = isinstance(message.get("tool_calls"), list) and bool(message["tool_calls"])
                    valid_content = isinstance(content, (str, list)) or (content is None and role == "assistant" and has_tool_calls)
                    if not valid_content:
                        malformed = True
                    if role == "assistant" and "tool_calls" in message:
                        calls = message.get("tool_calls")
                        if not isinstance(calls, list) or any(
                            not isinstance(call, dict) or not isinstance(call.get("function"), dict)
                            or not isinstance(call["function"].get("name"), str)
                            or not isinstance(call["function"].get("arguments"), str)
                            for call in (calls if isinstance(calls, list) else [])
                        ):
                            malformed = True
                if malformed or "user" not in row_roles or "assistant" not in row_roles:
                    invalid += 1
                else:
                    valid += 1
                    user_examples += 1
                    assistant_examples += 1
    except UnicodeDecodeError:
        raise RuntimeError("Chat dataset must be UTF-8 JSONL.") from None

    return _report(path, "chat-dataset", "Chat fine-tuning JSONL structure audit", [
        f"Examples parsed: {valid + invalid:,}",
        f"Structurally valid chat examples: {valid:,}",
        f"Invalid examples / malformed lines: {invalid:,}",
        f"Exact duplicate lines: {duplicates:,}",
        f"Message-role counts: system={role_counts['system']:,}, developer={role_counts['developer']:,}, user={role_counts['user']:,}, assistant={role_counts['assistant']:,}, tool={role_counts['tool']:,}",
        f"Examples containing user and assistant messages: {min(user_examples, assistant_examples):,}",
        f"OpenAI supervised fine-tuning minimum of 10 examples: {'met' if valid >= 10 else 'not met'}",
        "Privacy: all prompts, completions, tool arguments, identifiers and sample rows are withheld",
        "Scope: validates local chat-completions JSONL shape only; it does not upload data, call an API, assess data rights or score answer quality",
    ])


def promptfoo_config_audit(path: Path) -> dict:
    """Check a local Promptfoo YAML/JSON config's core evaluation structure without running it."""
    _check_file(path, "Promptfoo config", MAX_TEXT_CONFIG_BYTES)
    if path.suffix.lower() not in (".yaml", ".yml", ".json"):
        raise RuntimeError("Promptfoo config audit accepts YAML or JSON files.")
    text = path.read_text(encoding="utf-8-sig", errors="strict")
    try:
        if path.suffix.lower() == ".json":
            config = json.loads(text, object_pairs_hook=_unique_json_object)
        else:
            import yaml
            config = yaml.safe_load(text)
    except Exception:
        raise RuntimeError("Promptfoo config is not valid YAML/JSON.") from None
    if not isinstance(config, dict):
        raise RuntimeError("Promptfoo config root must be a mapping/object.")

    errors = []
    providers = config.get("providers", config.get("targets"))
    prompts = config.get("prompts")
    tests = config.get("tests")
    if providers is None:
        errors.append("missing providers/targets")
    elif not isinstance(providers, (str, list)) or (isinstance(providers, list) and not providers):
        errors.append("providers/targets must be a non-empty string or list")
    if prompts is None:
        errors.append("missing prompts")
    elif not isinstance(prompts, (str, list, dict)) or (isinstance(prompts, (list, dict)) and not prompts):
        errors.append("prompts must be a non-empty string, list or mapping")

    provider_count = len(providers) if isinstance(providers, list) else int(isinstance(providers, str) and bool(providers.strip()))
    prompt_count = len(prompts) if isinstance(prompts, (list, dict)) else int(isinstance(prompts, str) and bool(prompts.strip()))
    tests_count = len(tests) if isinstance(tests, list) else int(isinstance(tests, (str, dict)))
    if isinstance(tests, list) and any(not isinstance(test, (str, dict)) for test in tests):
        errors.append("tests contains an item that is not a test case or file reference")
    for test in tests if isinstance(tests, list) else []:
        if isinstance(test, dict):
            if "vars" in test and not isinstance(test["vars"], dict):
                errors.append("test vars must be a mapping")
            assertions = test.get("assert", test.get("assertions"))
            if assertions is not None and not isinstance(assertions, (list, dict)):
                errors.append("test assertions must be a list or mapping")
    scenarios = config.get("scenarios")
    if scenarios is not None and not isinstance(scenarios, (list, str)):
        errors.append("scenarios must be a list or file reference")
    if isinstance(scenarios, list) and any(not isinstance(item, (str, dict)) for item in scenarios):
        errors.append("scenarios contains an invalid item")

    return _report(path, "promptfoo-config", "Promptfoo evaluation-config structure audit", [
        f"Providers configured: {provider_count:,}",
        f"Prompts configured: {prompt_count:,}",
        f"Inline/file test entries: {tests_count:,}",
        f"Scenario entries: {len(scenarios) if isinstance(scenarios, list) else int(isinstance(scenarios, str)):,}",
        f"Assertion templates: {int(isinstance(config.get('assertionTemplates'), dict)):,}",
        f"Structural findings: {len(errors):,}",
        *[f"Finding: {item}" for item in errors[:12]],
        "Privacy: provider IDs, model names, prompts, variables, assertions and config values are withheld",
        "Scope: validates common Promptfoo config structure locally; does not resolve file/HTTP references, execute providers, run evaluations or replace the full upstream JSON Schema",
    ])


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].split(":")[-1]


def _safe_3mf_member(name: str) -> bool:
    normalized = name.rstrip("/")
    return bool(normalized) and "\\" not in name and not normalized.startswith("/") and "\\x00" not in normalized and all(part not in ("", ".", "..") for part in normalized.split("/"))


def _read_3mf_xml(archive: zipfile.ZipFile, members: dict[str, zipfile.ZipInfo], name: str) -> ET.Element:
    info = members.get(name)
    if info is None:
        raise RuntimeError("3MF package is missing a required XML part.")
    if info.file_size > MAX_3MF_PART_BYTES:
        raise RuntimeError("3MF XML part exceeds the 20 MiB per-part limit.")
    try:
        data = archive.read(info)
        return ET.fromstring(data)
    except (KeyError, OSError, ET.ParseError, RuntimeError):
        raise RuntimeError("3MF package contains an unreadable or malformed XML part.") from None


def three_mf_package_audit(path: Path) -> dict:
    """Inspect a 3MF OPC ZIP package and mesh indices without extracting payload files."""
    _check_file(path, "3MF package")
    if path.suffix.lower() != ".3mf":
        raise RuntimeError("3MF package audit accepts .3mf files.")
    try:
        with zipfile.ZipFile(path, "r") as archive:
            infos = archive.infolist()
            if not infos or len(infos) > 10_000:
                raise RuntimeError("3MF package entry count is empty or exceeds 10,000.")
            members: dict[str, zipfile.ZipInfo] = {}
            expanded = 0
            duplicate_members = 0
            unsafe_members = 0
            suspicious_ratios = 0
            for info in infos:
                name = info.filename
                if name in members:
                    duplicate_members += 1
                members[name] = info
                if not _safe_3mf_member(name) or (info.external_attr >> 16) & 0o170000 == 0o120000:
                    unsafe_members += 1
                if info.flag_bits & 0x1:
                    unsafe_members += 1
                expanded += info.file_size
                if info.file_size > 0 and info.file_size / max(info.compress_size, 1) > 200:
                    suspicious_ratios += 1
            if expanded > MAX_3MF_EXPANDED_BYTES:
                raise RuntimeError("3MF package exceeds the 100 MiB expanded-size limit.")
            if duplicate_members or unsafe_members:
                raise RuntimeError("3MF package contains duplicate, unsafe or encrypted entries.")
            if suspicious_ratios:
                raise RuntimeError("3MF package contains an excessive compression ratio.")

            content_types = _read_3mf_xml(archive, members, "[Content_Types].xml")
            relationships = _read_3mf_xml(archive, members, "_rels/.rels")
            model_targets = []
            for relationship in relationships.iter():
                if _local_name(relationship.tag) != "Relationship":
                    continue
                rel_type = relationship.attrib.get("Type", "")
                if rel_type.endswith("/3dmodel"):
                    if relationship.attrib.get("TargetMode", "Internal").lower() == "external":
                        raise RuntimeError("3MF primary model relationship must be an internal package part.")
                    target = relationship.attrib.get("Target", "")
                    normalized = posixpath.normpath(target.lstrip("/"))
                    if normalized in ("", ".", "..") or normalized.startswith("../") or "\\" in normalized:
                        raise RuntimeError("3MF model relationship target escapes the package.")
                    model_targets.append(normalized)
            if len(model_targets) != 1:
                raise RuntimeError("3MF root relationships must identify exactly one primary 3D model part.")
            model_name = model_targets[0]
            model_root = _read_3mf_xml(archive, members, model_name)
            if _local_name(model_root.tag) != "model":
                raise RuntimeError("3MF primary model part root must be a model element.")

            overrides = [
                node.attrib.get("ContentType", "")
                for node in content_types.iter()
                if _local_name(node.tag) == "Override" and node.attrib.get("PartName", "").lstrip("/") == model_name
            ]
            content_type_valid = not overrides or any(value == "application/vnd.ms-package.3dmanufacturing-3dmodel+xml" for value in overrides)

            objects = [node for node in model_root.iter() if _local_name(node.tag) == "object"]
            build_items = [node for node in model_root.iter() if _local_name(node.tag) == "item"]
            components = [node for node in model_root.iter() if _local_name(node.tag) == "component"]
            seen_object_ids = set()
            duplicate_object_ids = 0
            invalid_vertices = invalid_triangles = 0
            vertex_count = triangle_count = mesh_count = 0
            for obj in objects:
                object_id = obj.attrib.get("id")
                if object_id is not None:
                    if object_id in seen_object_ids:
                        duplicate_object_ids += 1
                    seen_object_ids.add(object_id)
                mesh = next((child for child in obj if _local_name(child.tag) == "mesh"), None)
                if mesh is None:
                    continue
                mesh_count += 1
                vertices = next((child for child in mesh if _local_name(child.tag) == "vertices"), None)
                triangles = next((child for child in mesh if _local_name(child.tag) == "triangles"), None)
                vertex_nodes = list(vertices) if vertices is not None else []
                triangle_nodes = list(triangles) if triangles is not None else []
                vertex_count += len(vertex_nodes)
                triangle_count += len(triangle_nodes)
                for vertex in vertex_nodes:
                    try:
                        xyz = [float(vertex.attrib[key]) for key in ("x", "y", "z")]
                        if not all(math.isfinite(value) for value in xyz):
                            invalid_vertices += 1
                    except (KeyError, ValueError):
                        invalid_vertices += 1
                for triangle in triangle_nodes:
                    try:
                        indices = [int(triangle.attrib[key]) for key in ("v1", "v2", "v3")]
                        if any(index < 0 or index >= len(vertex_nodes) for index in indices):
                            invalid_triangles += 1
                    except (KeyError, ValueError):
                        invalid_triangles += 1
    except zipfile.BadZipFile:
        raise RuntimeError("3MF upload is not a valid ZIP/OPC package.") from None

    findings = duplicate_object_ids + invalid_vertices + invalid_triangles + (0 if content_type_valid else 1)
    return _report(path, "3mf", "3MF package and mesh-structure audit", [
        f"Package entries: {len(infos):,}",
        f"Expanded package bytes: {expanded:,}",
        f"Primary model part: present",
        f"Model content type: {'recognized' if content_type_valid else 'missing or unexpected'}",
        f"Objects / mesh objects / build items / components: {len(objects):,}/{mesh_count:,}/{len(build_items):,}/{len(components):,}",
        f"Vertices / triangles: {vertex_count:,}/{triangle_count:,}",
        f"Duplicate object IDs: {duplicate_object_ids:,}",
        f"Invalid vertex coordinates: {invalid_vertices:,}",
        f"Invalid triangle indices: {invalid_triangles:,}",
        f"Structural findings: {findings:,}",
        "Privacy: model metadata, object names, material names, paths and vertex coordinates are withheld",
        "Scope: checks the primary 3MF OPC package and local mesh indices; it does not render geometry, validate every extension or certify printability",
    ])
