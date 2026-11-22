"""Wave 25 build, observability, binary and engineering inspectors.

Read-only bounded analyzers. They never execute uploaded programs, workflows,
WebAssembly modules, shell commands, build systems, or CAD instructions. User
identifiers, paths, messages, endpoints, coordinates and payload values are
intentionally excluded from reports.
"""
from __future__ import annotations

import collections
import gzip
import json
import math
import re
import struct
import tarfile
import xml.etree.ElementTree as ET
from pathlib import Path

MAX_INPUT = 20 * 1024 * 1024
MAX_TEXT = 10 * 1024 * 1024
MAX_XML = 12 * 1024 * 1024


def _report(path: Path, slug: str, heading: str, lines: list[str]) -> dict:
    output = path.with_name(path.stem + "-" + slug + "-report.txt")
    body = heading + "\n\n" + "\n".join(lines) + "\n"
    output.write_text(body, encoding="utf-8")
    return {"summary": body[:5_500], "output_path": str(output)}


def _read(path: Path, limit: int = MAX_INPUT) -> bytes:
    if path.stat().st_size > limit:
        raise RuntimeError("Wave 25 input exceeds its format size limit.")
    return path.read_bytes()


def _xml(data: bytes, label: str):
    if len(data) > MAX_XML:
        raise RuntimeError(f"{label} XML exceeds the 12 MiB limit.")
    upper = data.upper()
    if b"<!DOCTYPE" in upper or b"<!ENTITY" in upper:
        raise RuntimeError(f"{label} XML DTD/entity declarations are not allowed.")
    try:
        return ET.fromstring(data)
    except ET.ParseError as exc:
        raise RuntimeError(f"{label} XML is malformed.") from exc


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].split(":", 1)[-1].lower()


def _safe_int(value, default=None):
    try:
        return int(value)
    except (TypeError, ValueError, OverflowError):
        return default


def wasm_module_audit(path: Path) -> dict:
    data = _read(path)
    if len(data) < 8 or data[:4] != b"\x00asm":
        raise RuntimeError("WASM magic header is missing.")
    version = int.from_bytes(data[4:8], "little")
    if version != 1:
        raise RuntimeError("Only WebAssembly binary version 1 modules are supported.")

    def read_u32(offset: int, end: int) -> tuple[int, int]:
        value = 0
        shift = 0
        for index in range(5):
            if offset >= end:
                raise RuntimeError("WASM section contains a truncated LEB128 integer.")
            byte = data[offset]
            offset += 1
            if index == 4 and (byte & 0xF0):
                raise RuntimeError("WASM u32 LEB128 integer overflows 32 bits.")
            value |= (byte & 0x7F) << shift
            if not byte & 0x80:
                return value, offset
            shift += 7
        raise RuntimeError("WASM u32 LEB128 integer exceeds five bytes.")

    vector_sections = {1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13}
    labels = {
        1: "type", 2: "import", 3: "function", 4: "table", 5: "memory",
        6: "global", 7: "export", 8: "start", 9: "element",
        10: "code", 11: "data", 12: "data-count", 13: "tag",
    }
    offset = 8
    counts = collections.Counter()
    seen = set()
    standard_order = []
    custom_sections = section_bytes = 0
    vector_counts = {}
    unknown_sections = 0
    while offset < len(data):
        section_id = data[offset]
        offset += 1
        if section_id > 13:
            unknown_sections += 1
            raise RuntimeError("WASM contains an unrecognized section identifier.")
        size, offset = read_u32(offset, len(data))
        end = offset + size
        if end > len(data):
            raise RuntimeError("WASM section length exceeds the file boundary.")
        section_bytes += size
        counts[section_id] += 1
        if section_id == 0:
            custom_sections += 1
            name_length, cursor = read_u32(offset, end)
            if cursor + name_length > end:
                raise RuntimeError("WASM custom-section name exceeds its section.")
            try:
                data[cursor:cursor + name_length].decode("utf-8")
            except UnicodeError as exc:
                raise RuntimeError("WASM custom-section name is not UTF-8.") from exc
        else:
            if section_id in seen:
                raise RuntimeError("WASM contains a repeated standard section.")
            seen.add(section_id)
            standard_order.append(section_id)
            if section_id in vector_sections:
                count, _ = read_u32(offset, end)
                vector_counts[section_id] = count
            elif section_id == 8:
                # A start section contains a single function index, not a vector.
                _, cursor = read_u32(offset, end)
                if cursor != end:
                    raise RuntimeError("WASM start section has trailing bytes.")
                vector_counts[section_id] = 1
        offset = end
    if offset != len(data):
        raise RuntimeError("WASM parser did not end at the file boundary.")
    # Core section IDs are not a direct ordering relation: tag (13) has a
    # dedicated position after memory, while data-count (12) precedes code (10).
    standard_rank = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 13: 6, 6: 7, 7: 8, 8: 9, 9: 10, 12: 11, 10: 12, 11: 13}
    order_issues = sum(
        1 for left, right in zip(standard_order, standard_order[1:])
        if standard_rank[left] > standard_rank[right]
    )
    function_count = vector_counts.get(3)
    code_count = vector_counts.get(10)
    function_code_mismatch = int(function_count is not None and code_count is not None and function_count != code_count)
    lines = [
        "Binary version: 1",
        f"File bytes: {len(data):,}",
        f"Standard sections: {len(seen):,}",
        f"Custom sections: {custom_sections:,}",
        f"Standard-section duplicate count: 0",
        f"Section-order inversions (coarse static check): {order_issues:,}",
        f"Function declarations: {function_count if function_count is not None else 'not present'}",
        f"Code bodies: {code_count if code_count is not None else 'not present'}",
        f"Function/code vector mismatch: {function_code_mismatch}",
        f"Imported declarations: {vector_counts.get(2, 0):,}",
        f"Exported declarations: {vector_counts.get(7, 0):,}",
        f"Memory declarations: {vector_counts.get(5, 0):,}",
        "Section vector counts: " + (", ".join(f"{labels.get(key, 'custom')}={value}" for key, value in sorted(vector_counts.items())) or "none"),
        "No instruction bodies were decoded or executed; imports, exports, custom-section names and memory limits are withheld.",
        "This structural scan is not a complete WebAssembly validator.",
    ]
    return _report(path, "wasm", "WebAssembly binary structure audit", lines)


def sarif_report_audit(path: Path) -> dict:
    raw = _read(path, MAX_TEXT)
    try:
        document = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("SARIF JSON is malformed.") from exc
    if not isinstance(document, dict) or not isinstance(document.get("runs"), list):
        raise RuntimeError("SARIF document must contain a runs array.")
    if len(document["runs"]) > 100:
        raise RuntimeError("SARIF document contains too many runs.")
    results = rules_total = suppressions = locations = fixes = repeated_rules = missing_rules = 0
    levels = collections.Counter()
    kinds = collections.Counter()
    tool_drivers = 0
    for run in document["runs"]:
        if not isinstance(run, dict):
            continue
        tool = run.get("tool") if isinstance(run.get("tool"), dict) else {}
        driver = tool.get("driver") if isinstance(tool.get("driver"), dict) else {}
        tool_drivers += bool(driver)
        rules = driver.get("rules") if isinstance(driver.get("rules"), list) else []
        rule_ids = []
        for rule in rules:
            if isinstance(rule, dict) and isinstance(rule.get("id"), str):
                rule_ids.append(rule["id"])
        rules_total += len(rule_ids)
        repeated_rules += len(rule_ids) - len(set(rule_ids))
        rule_set = set(rule_ids)
        entries = run.get("results") if isinstance(run.get("results"), list) else []
        if results + len(entries) > 500_000:
            raise RuntimeError("SARIF exceeds the 500,000 result limit.")
        for result in entries:
            if not isinstance(result, dict):
                continue
            results += 1
            level = str(result.get("level", "unspecified")).lower()
            levels[level if level in {"none", "note", "warning", "error"} else "other"] += 1
            kinds[str(result.get("kind", "unspecified")).lower()] += 1
            rule_id = result.get("ruleId")
            if rule_set and isinstance(rule_id, str) and rule_id not in rule_set:
                missing_rules += 1
            suppressions += len(result.get("suppressions", [])) if isinstance(result.get("suppressions"), list) else 0
            locations += len(result.get("locations", [])) if isinstance(result.get("locations"), list) else 0
            fixes += len(result.get("fixes", [])) if isinstance(result.get("fixes"), list) else 0
    version = str(document.get("version", "unspecified"))
    schema_present = isinstance(document.get("$schema"), str)
    lines = [
        f"SARIF version field: {version if version in {'2.1.0'} else 'unrecognized/unspecified'}",
        f"Schema URI field present: {schema_present}",
        f"Runs: {len(document['runs']):,}",
        f"Runs with tool driver: {tool_drivers:,}",
        f"Rule definitions: {rules_total:,}",
        f"Duplicate rule identifiers: {repeated_rules:,}",
        f"Results: {results:,}",
        f"Results referencing undeclared rule IDs (when rule list is present): {missing_rules:,}",
        f"Location entries: {locations:,}",
        f"Suppressions: {suppressions:,}",
        f"Fix objects: {fixes:,}",
        "Result levels: " + (", ".join(f"{key}={value}" for key, value in sorted(levels.items())) or "none"),
        "Result kinds: " + (", ".join(f"{key}={value}" for key, value in sorted(kinds.items())) or "none"),
        "Rule IDs, tool names, message text, file paths, snippets, fingerprints and fix contents are withheld.",
    ]
    return _report(path, "sarif", "SARIF 2.1 static report audit", lines)


def cyclonedx_sbom_audit(path: Path) -> dict:
    raw = _read(path, MAX_TEXT)
    suffix = path.suffix.lower()
    packages = files = components = services = vulnerabilities = relationships = licenses = 0
    duplicate_ids = missing_refs = repeated_edges = 0
    refs = set()
    edges = set()
    version_label = "unspecified"
    format_label = "unknown"
    if suffix == ".xml":
        root = _xml(raw, "SBOM")
        root_type = _local(root.tag)
        if root_type == "bom":
            format_label = "CycloneDX XML"
            version_label = root.attrib.get("version", "unspecified")
            for element in root.iter():
                tag = _local(element.tag)
                bom_ref = element.attrib.get("bom-ref")
                if bom_ref:
                    if bom_ref in refs:
                        duplicate_ids += 1
                    refs.add(bom_ref)
                if tag == "component":
                    components += 1
                    licenses += sum(1 for child in element if _local(child.tag) == "licenses")
                elif tag == "service":
                    services += 1
                elif tag == "vulnerability":
                    vulnerabilities += 1
                elif tag == "dependency":
                    relationships += 1
                    source = element.attrib.get("ref")
                    if source:
                        for child in element:
                            if _local(child.tag) == "dependency":
                                target = child.attrib.get("ref")
                                if target:
                                    if (source, target) in edges:
                                        repeated_edges += 1
                                    edges.add((source, target))
            missing_refs = sum(1 for source, target in edges if source not in refs or target not in refs)
        elif root_type in {"spdxdocument", "spdx"}:
            format_label = "SPDX XML"
            version_label = "SPDX 2.x XML"
            for element in root.iter():
                tag = _local(element.tag)
                if tag in {"package", "file", "snippet"}:
                    packages += tag == "package"
                    files += tag == "file"
                    components += tag == "snippet"
                    for child in element:
                        if _local(child.tag) == "spdxid" and child.text:
                            if child.text in refs:
                                duplicate_ids += 1
                            refs.add(child.text)
                elif tag == "relationship":
                    relationships += 1
                    fields = {_local(child.tag): (child.text or "").strip() for child in element}
                    source = fields.get("spdxelementid")
                    target = fields.get("relatedspdxelement")
                    if source and target:
                        edges.add((source, target))
                elif tag in {"licenseconcluded", "licensedeclared"}:
                    licenses += 1
            missing_refs = sum(1 for source, target in edges if source not in refs or target not in refs)
        else:
            raise RuntimeError("SBOM XML root must be CycloneDX bom or SPDX document.")
    else:
        try:
            document = json.loads(raw.decode("utf-8-sig"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise RuntimeError("SBOM JSON is malformed.") from exc
        if not isinstance(document, dict):
            raise RuntimeError("SBOM JSON root must be an object.")
        if document.get("bomFormat") == "CycloneDX":
            format_label = "CycloneDX JSON"
            version_label = str(document.get("specVersion", "unspecified"))
            stack = list(document.get("components", [])) if isinstance(document.get("components"), list) else []
            metadata = document.get("metadata") if isinstance(document.get("metadata"), dict) else {}
            primary = metadata.get("component")
            if isinstance(primary, dict):
                stack.append(primary)
            visited_nodes = 0
            while stack:
                component = stack.pop()
                visited_nodes += 1
                if visited_nodes > 100_000:
                    raise RuntimeError("CycloneDX component graph exceeds the scan limit.")
                if not isinstance(component, dict):
                    continue
                components += 1
                bom_ref = component.get("bom-ref")
                if isinstance(bom_ref, str) and bom_ref:
                    if bom_ref in refs:
                        duplicate_ids += 1
                    refs.add(bom_ref)
                licenses += len(component.get("licenses", [])) if isinstance(component.get("licenses"), list) else 0
                nested = component.get("components")
                if isinstance(nested, list):
                    stack.extend(nested)
            services_list = document.get("services", [])
            services = len(services_list) if isinstance(services_list, list) else 0
            vulnerabilities_list = document.get("vulnerabilities", [])
            vulnerabilities = len(vulnerabilities_list) if isinstance(vulnerabilities_list, list) else 0
            for dep in document.get("dependencies", []) if isinstance(document.get("dependencies"), list) else []:
                if isinstance(dep, dict):
                    relationships += len(dep.get("dependsOn", [])) if isinstance(dep.get("dependsOn"), list) else 0
                    source = dep.get("ref")
                    if isinstance(source, str):
                        for target in dep.get("dependsOn", []) if isinstance(dep.get("dependsOn"), list) else []:
                            if isinstance(target, str):
                                if (source, target) in edges:
                                    repeated_edges += 1
                                edges.add((source, target))
            missing_refs = sum(1 for source, target in edges if source not in refs or target not in refs)
        elif isinstance(document.get("spdxVersion"), str):
            format_label = "SPDX JSON"
            version_label = document["spdxVersion"]
            for key in ("packages", "files", "snippets"):
                rows = document.get(key, [])
                if not isinstance(rows, list):
                    continue
                if key == "packages":
                    packages += len(rows)
                elif key == "files":
                    files += len(rows)
                else:
                    components += len(rows)
                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    spdx_id = row.get("SPDXID")
                    if isinstance(spdx_id, str) and spdx_id:
                        if spdx_id in refs:
                            duplicate_ids += 1
                        refs.add(spdx_id)
                    licenses += int(bool(row.get("licenseConcluded") or row.get("licenseDeclared")))
            document_id = document.get("SPDXID")
            if isinstance(document_id, str):
                refs.add(document_id)
            for rel in document.get("relationships", []) if isinstance(document.get("relationships"), list) else []:
                if isinstance(rel, dict):
                    relationships += 1
                    source = rel.get("spdxElementId")
                    target = rel.get("relatedSpdxElement")
                    if isinstance(source, str) and isinstance(target, str):
                        edges.add((source, target))
            missing_refs = sum(1 for source, target in edges if source not in refs or target not in refs)
        else:
            raise RuntimeError("SBOM JSON is neither CycloneDX nor SPDX.")
    total_components = components + packages + files + services
    lines = [
        f"SBOM format: {format_label}",
        f"Format version: {version_label if version_label[:10].lower() in {'1.7', '1.6', '1.5', '1.4', 'spdx-2.3', 'spdx-2.2', 'spdx-2.1'} or format_label.endswith('XML') else 'unrecognized/unspecified'}",
        f"Components/packages: {total_components:,}",
        f"Services: {services:,}",
        f"Package records: {packages:,}",
        f"File records: {files:,}",
        f"Vulnerability records: {vulnerabilities:,}",
        f"Relationship/dependency edges: {relationships:,}",
        f"License declarations/entries: {licenses:,}",
        f"Duplicate component/package identifiers: {duplicate_ids:,}",
        f"Repeated dependency edges: {repeated_edges:,}",
        f"Dependency edges with missing endpoints: {missing_refs:,}",
        "Component names, package URLs, license expressions, serial numbers, vulnerability IDs and supplier data are withheld.",
    ]
    return _report(path, "sbom", "CycloneDX/SPDX software bill of materials audit", lines)


def junit_xml_audit(path: Path) -> dict:
    root = _xml(_read(path, MAX_TEXT), "JUnit")
    if _local(root.tag) not in {"testsuite", "testsuites"}:
        raise RuntimeError("JUnit XML root must be testsuite or testsuites.")
    suites = [node for node in root.iter() if _local(node.tag) == "testsuite"]
    cases = [node for node in root.iter() if _local(node.tag) == "testcase"]
    if len(suites) > 50_000 or len(cases) > 500_000:
        raise RuntimeError("JUnit report exceeds suite or testcase limits.")
    failed = errors = skipped = flaky = system_output = missing_names = 0
    for case in cases:
        children = {_local(child.tag) for child in list(case)}
        failed += "failure" in children
        errors += "error" in children
        skipped += "skipped" in children
        flaky += bool(children & {"flakyfailure", "flakyerror", "rerunfailure", "rerunerror"})
        missing_names += not bool(case.attrib.get("name"))
        system_output += sum(1 for child in list(case) if _local(child.tag) in {"system-out", "system-err"})
    declared_tests = declared_failures = declared_errors = declared_skipped = 0
    declared_mismatches = 0
    duration = 0.0
    for suite in suites:
        declared_tests += _safe_int(suite.attrib.get("tests"), 0) or 0
        declared_failures += _safe_int(suite.attrib.get("failures"), 0) or 0
        declared_errors += _safe_int(suite.attrib.get("errors"), 0) or 0
        declared_skipped += _safe_int(suite.attrib.get("skipped"), 0) or 0
        try:
            duration += float(suite.attrib.get("time", "0") or 0)
        except ValueError:
            pass
    declared_mismatches = int(bool(suites) and declared_tests != len(cases))
    lines = [
        f"Test suites: {len(suites):,}",
        f"Test cases: {len(cases):,}",
        f"Declared test count across suites: {declared_tests:,}",
        f"Declared/observed testcase count mismatch: {declared_mismatches}",
        f"Observed failures: {failed:,}",
        f"Observed errors: {errors:,}",
        f"Observed skipped tests: {skipped:,}",
        f"Flaky/rerun result markers: {flaky:,}",
        f"Suites with missing testcase names: {missing_names:,}",
        f"System output/error elements (content withheld): {system_output:,}",
        f"Declared failures/errors/skips: {declared_failures:,}/{declared_errors:,}/{declared_skipped:,}",
        f"Summed suite duration (seconds): {duration:.3f}",
        "Suite names, testcase names, class names, file paths, assertion messages and stdout/stderr are withheld.",
    ]
    return _report(path, "junit", "JUnit XML test-result audit", lines)


def coverage_xml_audit(path: Path) -> dict:
    root = _xml(_read(path, MAX_TEXT), "Coverage")
    root_name = _local(root.tag)
    if root_name == "coverage":
        format_name = "Cobertura"
        classes = sum(1 for node in root.iter() if _local(node.tag) == "class")
        methods = sum(1 for node in root.iter() if _local(node.tag) == "method")
        files = sum(1 for node in root.iter() if _local(node.tag) == "source")
        lines = [node for node in root.iter() if _local(node.tag) == "line"]
        line_hits = sum(1 for node in lines if (_safe_int(node.attrib.get("hits"), 0) or 0) > 0)
        branch_lines = sum(1 for node in lines if node.attrib.get("branch", "").lower() == "true")
        conditions = sum(1 for node in root.iter() if _local(node.tag) == "condition")
        try:
            line_rate = float(root.attrib.get("line-rate", "0"))
        except ValueError:
            line_rate = 0.0
        try:
            branch_rate = float(root.attrib.get("branch-rate", "0"))
        except ValueError:
            branch_rate = 0.0
        metrics = {
            "line rate": f"{line_rate:.3%}",
            "branch rate": f"{branch_rate:.3%}",
            "observed lines": f"{line_hits:,}/{len(lines):,} covered",
            "branch-bearing lines": f"{branch_lines:,}",
            "branch conditions": f"{conditions:,}",
        }
    elif root_name == "report":
        format_name = "JaCoCo"
        classes = sum(1 for node in root.iter() if _local(node.tag) == "class")
        methods = sum(1 for node in root.iter() if _local(node.tag) == "method")
        files = sum(1 for node in root.iter() if _local(node.tag) == "sourcefile")
        lines = sum(1 for node in root.iter() if _local(node.tag) == "line")
        counters = collections.defaultdict(lambda: [0, 0])
        for node in root.iter():
            if _local(node.tag) == "counter":
                key = node.attrib.get("type", "unknown").upper()
                missed = _safe_int(node.attrib.get("missed"), 0) or 0
                covered = _safe_int(node.attrib.get("covered"), 0) or 0
                counters[key][0] += covered
                counters[key][1] += missed
        metrics = {}
        for key, (covered, missed) in sorted(counters.items()):
            total = covered + missed
            metrics[key.lower()] = f"{covered:,}/{total:,} covered" if total else "no items"
    else:
        raise RuntimeError("Coverage XML root must be Cobertura coverage or JaCoCo report.")
    lines_out = [
        f"Coverage format: {format_name}",
        f"Class entries: {classes:,}",
        f"Method entries: {methods:,}",
        f"Source/file entries: {files:,}",
        f"Line entries: {len(lines) if isinstance(lines, list) else lines:,}",
        "Coverage aggregates:",
    ]
    lines_out.extend(f"  {key}: {value}" for key, value in metrics.items())
    lines_out.append("Package/class/method/source names, paths and per-line hit counts are not exposed.")
    return _report(path, "coverage", "Coverage XML audit", lines_out)


def fits_file_audit(path: Path) -> dict:
    data = _read(path)
    block = 2880
    card_size = 80
    if len(data) < block or len(data) % block:
        raise RuntimeError("FITS file size must contain complete 2880-byte blocks.")
    offset = 0
    hdus = []
    bitpix_counts = collections.Counter()
    xtension_counts = collections.Counter()
    total_cards = blank_cards = duplicate_cards = 0
    hdu_limit = 1_000
    while offset < len(data):
        if len(hdus) >= hdu_limit:
            raise RuntimeError("FITS contains too many HDUs.")
        header_start = offset
        keywords = {}
        end_found = False
        hdu_cards = collections.Counter()
        while not end_found:
            if offset + block > len(data):
                raise RuntimeError("FITS header is truncated before END.")
            chunk = data[offset:offset + block]
            if any(byte < 0x20 or byte > 0x7E for byte in chunk):
                raise RuntimeError("FITS header block contains non-printable ASCII bytes.")
            for index in range(0, block, card_size):
                card = chunk[index:index + card_size]
                key = card[:8].decode("ascii").strip().upper()
                total_cards += 1
                hdu_cards[key] += 1
                if not key:
                    blank_cards += 1
                    continue
                if key == "END":
                    end_found = True
                    break
                if card[8:10] == b"= ":
                    value = card[10:].decode("ascii").split("/", 1)[0].strip()
                    keywords[key] = value
            offset += block
        duplicate_cards += sum(value - 1 for key, value in hdu_cards.items() if key and key not in {"COMMENT", "HISTORY"})
        is_primary = not hdus
        if is_primary and keywords.get("SIMPLE", "").upper() not in {"T", "TRUE"}:
            raise RuntimeError("FITS primary HDU does not declare SIMPLE = T.")
        bitpix = _safe_int(keywords.get("BITPIX"))
        naxis = _safe_int(keywords.get("NAXIS"))
        if bitpix not in {8, 16, 32, 64, -32, -64} or naxis is None or not 0 <= naxis <= 999:
            raise RuntimeError("FITS BITPIX or NAXIS values are invalid.")
        axes = []
        for axis in range(1, naxis + 1):
            value = _safe_int(keywords.get(f"NAXIS{axis}"))
            if value is None or value < 0:
                raise RuntimeError("FITS axis length is missing or invalid.")
            axes.append(value)
        pcount = _safe_int(keywords.get("PCOUNT"), 0)
        gcount = _safe_int(keywords.get("GCOUNT"), 1)
        if pcount is None or gcount is None or pcount < 0 or gcount < 1:
            raise RuntimeError("FITS PCOUNT or GCOUNT value is invalid.")
        elements = math.prod(axes) if naxis else 0
        payload_bytes = (elements + pcount) * gcount * (abs(bitpix) // 8)
        padded_bytes = ((payload_bytes + block - 1) // block) * block if payload_bytes else 0
        data_start = offset
        data_end = data_start + padded_bytes
        if data_end > len(data):
            raise RuntimeError("FITS data unit is truncated.")
        extension = keywords.get("XTENSION", "").strip().strip("'").strip().upper() if not is_primary else "PRIMARY"
        xtension_counts[extension or "UNSPECIFIED"] += 1
        bitpix_counts[str(bitpix)] += 1
        hdus.append({
            "header_bytes": offset - header_start,
            "data_bytes": payload_bytes,
            "axis_count": naxis,
            "bitpix": bitpix,
            "extension": extension,
        })
        offset = data_end
        if offset == len(data):
            break
    if offset != len(data):
        raise RuntimeError("FITS file ends between HDUs or contains an incomplete block.")
    lines = [
        f"HDUs inspected: {len(hdus):,}",
        f"Header cards: {total_cards:,}",
        f"Blank/padding cards: {blank_cards:,}",
        f"Duplicate non-comment/history keywords: {duplicate_cards:,}",
        f"Primary HDUs: {sum(hdu['extension'] == 'PRIMARY' for hdu in hdus):,}",
        f"Image/table/extension HDUs: {len(hdus) - 1:,}",
        "XTENSION types: " + (", ".join(f"{key}={value}" for key, value in sorted(xtension_counts.items())) or "none"),
        "BITPIX distribution: " + (", ".join(f"{key}={value}" for key, value in sorted(bitpix_counts.items())) or "none"),
        f"Declared data bytes (not pixel-decoded): {sum(hdu['data_bytes'] for hdu in hdus):,}",
        f"Total FITS bytes: {len(data):,}",
        "Observation names, telescope/instrument metadata, coordinates, dates and pixel values are withheld.",
    ]
    return _report(path, "fits", "FITS astronomical data structure audit", lines)


def step_cad_audit(path: Path) -> dict:
    raw = _read(path, MAX_TEXT)
    try:
        text = raw.decode("ascii")
    except UnicodeError:
        text = raw.decode("latin-1")
    output = []
    in_comment = False
    in_string = False
    malformed_string = 0
    index = 0
    while index < len(text):
        if in_comment:
            if text.startswith("*/", index):
                in_comment = False
                output.extend("  ")
                index += 2
            else:
                output.append("\n" if text[index] == "\n" else " ")
                index += 1
        elif in_string:
            if text[index] == "'":
                if index + 1 < len(text) and text[index + 1] == "'":
                    output.extend("  ")
                    index += 2
                else:
                    output.append(" ")
                    in_string = False
                    index += 1
            else:
                output.append("\n" if text[index] == "\n" else " ")
                index += 1
        elif text.startswith("/*", index):
            in_comment = True
            output.extend("  ")
            index += 2
        elif text[index] == "'":
            in_string = True
            output.append(" ")
            index += 1
        else:
            output.append(text[index])
            index += 1
    malformed_string = int(in_string or in_comment)
    clean = "".join(output)
    upper = clean.upper()
    entity_matches = re.findall(r"#\s*(\d+)\s*=\s*([A-Z][A-Z0-9_]*)\s*\(", upper)
    ids = [item[0] for item in entity_matches]
    types = collections.Counter(item[1] for item in entity_matches)
    all_refs = re.findall(r"#\s*(\d+)", upper)
    defined = set(ids)
    dangling = sum(1 for ref in all_refs if ref not in defined)
    parentheses = 0
    negative = 0
    for char in clean:
        if char == "(":
            parentheses += 1
        elif char == ")":
            parentheses -= 1
            negative += parentheses < 0
    section_count = len(re.findall(r"\bENDSEC\s*;", upper))
    header_count = len(re.findall(r"\bHEADER\s*;", upper))
    data_count = len(re.findall(r"\bDATA\s*;", upper))
    required_header = sum(1 for marker in ("FILE_DESCRIPTION", "FILE_NAME", "FILE_SCHEMA") if marker in upper)
    duplicate_ids = len(ids) - len(set(ids))
    terminator = bool(re.search(r"\bEND-ISO-10303-21\s*;", upper))
    starts_correctly = bool(re.match(r"\s*ISO-10303-21\s*;", upper))
    lines = [
        f"ISO-10303-21 opening marker present: {starts_correctly}",
        f"END-ISO-10303-21 terminator present: {terminator}",
        f"HEADER sections: {header_count:,}",
        f"DATA sections: {data_count:,}",
        f"ENDSEC markers: {section_count:,}",
        f"Required HEADER entities present: {required_header}/3",
        f"Entity instances: {len(entity_matches):,}",
        f"Distinct entity identifiers: {len(defined):,}",
        f"Duplicate entity identifiers: {duplicate_ids:,}",
        f"Entity references without a corresponding definition: {dangling:,}",
        f"STEP entity types: " + (", ".join(f"{key}={value}" for key, value in types.most_common(15)) or "none"),
        f"Balanced parentheses: {parentheses == 0 and negative == 0}",
        f"Unterminated comment/string marker: {malformed_string}",
        "Header names, author/application strings, geometry parameters and entity identifiers are withheld; no CAD geometry is evaluated.",
    ]
    return _report(path, "step", "STEP Part 21 CAD exchange audit", lines)


def otel_collector_audit(path: Path) -> dict:
    raw = _read(path, MAX_TEXT)
    text = raw.decode("utf-8-sig", errors="replace")
    if text.count("&") + text.count("*") > 2_000:
        raise RuntimeError("OpenTelemetry YAML alias/reference count exceeds the safe limit.")
    try:
        import yaml
        document = yaml.safe_load(text)
    except Exception as exc:
        raise RuntimeError("OpenTelemetry Collector YAML could not be parsed safely.") from exc
    if not isinstance(document, dict):
        raise RuntimeError("OpenTelemetry Collector config root must be a mapping.")
    sections = {}
    for key in ("receivers", "processors", "exporters", "connectors", "extensions"):
        value = document.get(key, {})
        if value is not None and not isinstance(value, dict):
            raise RuntimeError(f"OpenTelemetry {key} section must be a mapping.")
        sections[key] = set(value.keys()) if isinstance(value, dict) else set()
    service = document.get("service", {}) if isinstance(document.get("service"), dict) else {}
    pipelines = service.get("pipelines", {}) if isinstance(service.get("pipelines"), dict) else {}
    enabled_extensions = service.get("extensions", []) if isinstance(service.get("extensions"), list) else []
    missing = used_edges = unused = pipeline_count = 0
    used = {key: set() for key in sections}
    for extension in enabled_extensions:
        if isinstance(extension, str):
            used_edges += 1
            used["extensions"].add(extension)
            missing += extension not in sections["extensions"]
    for pipeline in pipelines.values():
        if not isinstance(pipeline, dict):
            continue
        pipeline_count += 1
        for kind in ("receivers", "processors", "exporters"):
            refs = pipeline.get(kind, [])
            if not isinstance(refs, list):
                missing += 1
                continue
            for component in refs:
                if not isinstance(component, str):
                    missing += 1
                    continue
                used_edges += 1
                used[kind].add(component)
                missing += component not in sections[kind]
    for kind, refs in sections.items():
        unused += len(refs - used[kind])
    public_endpoints = remote_endpoints = secret_fields = 0
    stack = [document]
    nodes = 0
    while stack:
        current = stack.pop()
        nodes += 1
        if nodes > 100_000:
            raise RuntimeError("OpenTelemetry Collector config exceeds the node-count limit.")
        if isinstance(current, dict):
            for key, value in current.items():
                key_text = str(key).lower()
                if isinstance(value, str):
                    if "endpoint" in key_text:
                        public_endpoints += value.startswith(("0.0.0.0:", "[::]:", ":::", "0.0.0.0/"))
                        remote_endpoints += value.startswith(("http://", "https://", "grpc://"))
                    if any(token in key_text for token in ("password", "secret", "token", "api_key", "apikey", "private_key")) and value.strip():
                        secret_fields += 1
                    stack.append(value) if isinstance(value, (dict, list)) else None
                elif isinstance(value, (dict, list)):
                    stack.append(value)
        elif isinstance(current, list):
            stack.extend(value for value in current if isinstance(value, (dict, list)))
    lines = [
        f"Configured receivers: {len(sections['receivers']):,}",
        f"Configured processors: {len(sections['processors']):,}",
        f"Configured exporters: {len(sections['exporters']):,}",
        f"Configured connectors: {len(sections['connectors']):,}",
        f"Configured extensions: {len(sections['extensions']):,}",
        f"Service pipelines: {pipeline_count:,}",
        f"Pipeline component references: {used_edges:,}",
        f"Undefined service component references: {missing:,}",
        f"Configured but unreferenced components/extensions: {unused:,}",
        f"Endpoints explicitly bound to all interfaces: {public_endpoints:,}",
        f"HTTP/HTTPS/gRPC endpoint fields: {remote_endpoints:,}",
        f"Potential literal secret fields (values withheld): {secret_fields:,}",
        f"Analyzed YAML nodes: {nodes:,}",
        "Component identifiers, endpoint addresses, authentication tokens, credentials and pipeline names are withheld; no collector is started.",
    ]
    return _report(path, "otel", "OpenTelemetry Collector config audit", lines)


def godot_project_audit(path: Path) -> dict:
    raw = _read(path, MAX_TEXT)
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeError as exc:
        raise RuntimeError("Godot project settings must be UTF-8 text.") from exc
    if len(text.splitlines()) > 200_000:
        raise RuntimeError("Godot project settings contain too many lines.")
    section = ""
    sections = collections.Counter()
    keys = collections.Counter()
    autoloads = plugins = resource_refs = remote_uris = secret_fields = 0
    main_scene = False
    malformed = 0
    for line in text.splitlines():
        current = line.strip()
        if not current or current.startswith((";", "#")):
            continue
        match = re.fullmatch(r"\[([^\]]+)\]", current)
        if match:
            section = match.group(1).strip().lower()
            sections[section] += 1
            continue
        if "=" not in current:
            malformed += 1
            continue
        key, value = current.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            malformed += 1
            continue
        keys[section] += 1
        if section == "autoload":
            autoloads += 1
        if section == "editor_plugins" and key.lower() == "enabled":
            plugins += len(re.findall(r'"[^"]+"', value))
        if key.lower() in {"run/main_scene", "application/run/main_scene"}:
            main_scene = bool(value)
        resource_refs += len(re.findall(r"\bres://", value, flags=re.I))
        remote_uris += len(re.findall(r"(?i)https?://|wss?://", value))
        secret_fields += bool(re.search(r"(?i)(?:password|secret|token|api[_-]?key|private[_-]?key)", key)) and bool(value)
    lines = [
        f"Godot project settings file: project.godot-style INI",
        f"Sections: {len(sections):,}",
        f"Key/value settings: {sum(keys.values()):,}",
        f"Autoload/singleton entries: {autoloads:,}",
        f"Enabled editor plugin path entries: {plugins:,}",
        f"Resource-path references (res://): {resource_refs:,}",
        f"Remote URI references: {remote_uris:,}",
        f"Potential hardcoded-secret settings (values withheld): {secret_fields:,}",
        f"Main scene setting present: {main_scene}",
        f"Unrecognized non-empty lines: {malformed:,}",
        "Section names, setting keys, project paths, plugin names, URI values and secret values are withheld; GDScript and scenes are not executed.",
    ]
    return _report(path, "godot", "Godot project configuration audit", lines)


def unity_package_audit(path: Path) -> dict:
    if path.stat().st_size > MAX_INPUT:
        raise RuntimeError("Unity package exceeds the 20 MiB compressed input limit.")
    try:
        archive = tarfile.open(path, "r:gz")
    except (tarfile.TarError, OSError) as exc:
        raise RuntimeError("Unity .unitypackage is not a readable gzip-compressed tar archive.") from exc
    groups = {}
    members = []
    expanded = 0
    unsafe = duplicate_names = 0
    try:
        for index, member in enumerate(archive):
            if index >= 10_000:
                raise RuntimeError("Unity package exceeds 10,000 members.")
            name = member.name.replace("\\", "/")
            if name.startswith("/") or re.match(r"^[A-Za-z]:", name) or ".." in name.split("/"):
                unsafe += 1
                raise RuntimeError("Unity package contains an unsafe archive path.")
            if member.issym() or member.islnk() or not (member.isfile() or member.isdir()):
                unsafe += 1
                raise RuntimeError("Unity package contains links or unsupported special members.")
            expanded += member.size
            if expanded > 180 * 1024 * 1024:
                raise RuntimeError("Unity package exceeds the 180 MiB expanded-size limit.")
            if name in members:
                duplicate_names += 1
            members.append(name)
            parts = name.split("/")
            if len(parts) < 2 or not re.fullmatch(r"[0-9a-fA-F]{32}", parts[0]):
                continue
            guid = parts[0].lower()
            record = groups.setdefault(guid, {"asset": 0, "meta": 0, "pathname": 0})
            role = parts[-1].lower()
            if role == "asset":
                record["asset"] += 1
            elif role == "asset.meta":
                record["meta"] += 1
            elif role == "pathname":
                record["pathname"] += 1
                if member.isfile() and member.size <= 4_096:
                    source = archive.extractfile(member)
                    if source:
                        source.read(4_096)
                        source.close()
        incomplete = sum(1 for item in groups.values() if not item["asset"] or not item["pathname"])
        missing_meta = sum(1 for item in groups.values() if not item["meta"])
        duplicate_guids = sum(1 for item in groups.values() if any(value > 1 for value in item.values()))
        lines = [
            f"Archive members: {len(members):,}",
            f"Expanded bytes: {expanded:,}",
            f"GUID directory groups: {len(groups):,}",
            f"Groups missing asset or pathname member: {incomplete:,}",
            f"Groups missing asset.meta member: {missing_meta:,}",
            f"GUID groups with repeated role members: {duplicate_guids:,}",
            f"Repeated archive member paths: {duplicate_names:,}",
            f"Unsafe archive paths/special members: {unsafe:,}",
            "Unity GUIDs, project-relative asset paths, asset bytes and metadata contents are withheld; nothing is extracted to disk.",
        ]
    finally:
        archive.close()
    return _report(path, "unitypackage", "Unity .unitypackage archive audit", lines)


def unreal_project_audit(path: Path) -> dict:
    raw = _read(path, MAX_TEXT)
    try:
        document = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Unreal Engine .uproject JSON is malformed.") from exc
    if not isinstance(document, dict):
        raise RuntimeError("Unreal project descriptor must be a JSON object.")
    modules = document.get("Modules", []) if isinstance(document.get("Modules"), list) else []
    plugins = document.get("Plugins", []) if isinstance(document.get("Plugins"), list) else []
    module_names = []
    plugin_names = []
    module_types = collections.Counter()
    enabled = disabled = invalid_plugins = 0
    for item in modules:
        if isinstance(item, dict):
            name = item.get("Name")
            if isinstance(name, str):
                module_names.append(name)
            module_types[str(item.get("Type", "unspecified")).lower()] += 1
    for item in plugins:
        if not isinstance(item, dict):
            invalid_plugins += 1
            continue
        name = item.get("Name")
        if isinstance(name, str):
            plugin_names.append(name)
        if item.get("Enabled") is True:
            enabled += 1
        elif item.get("Enabled") is False:
            disabled += 1
        else:
            invalid_plugins += 1
    targets = document.get("TargetPlatforms", []) if isinstance(document.get("TargetPlatforms"), list) else []
    credential_fields = 0
    stack = [document]
    nodes = 0
    while stack:
        node = stack.pop()
        nodes += 1
        if nodes > 100_000:
            raise RuntimeError("Unreal project descriptor exceeds the JSON node limit.")
        if isinstance(node, dict):
            for key, value in node.items():
                if any(term in str(key).lower() for term in ("password", "secret", "token", "apikey", "api_key")) and isinstance(value, str) and value:
                    credential_fields += 1
                if isinstance(value, (dict, list)):
                    stack.append(value)
        elif isinstance(node, list):
            stack.extend(value for value in node if isinstance(value, (dict, list)))
    lines = [
        f"Project descriptor FileVersion: {_safe_int(document.get('FileVersion'), 'unspecified')}",
        f"Engine association field present: {bool(document.get('EngineAssociation'))}",
        f"Module declarations: {len(modules):,}",
        f"Duplicate module names: {len(module_names) - len(set(module_names)):,}",
        f"Module type counts: " + (", ".join(f"{key}={value}" for key, value in sorted(module_types.items())) or "none"),
        f"Plugin references: {len(plugins):,}",
        f"Enabled plugins: {enabled:,}",
        f"Disabled plugins: {disabled:,}",
        f"Plugin entries with missing/invalid enabled state: {invalid_plugins:,}",
        f"Duplicate plugin names: {len(plugin_names) - len(set(plugin_names)):,}",
        f"Target platform entries: {len(targets):,}",
        f"Potential secret-bearing descriptor fields (values withheld): {credential_fields:,}",
        "Project names, module/plugin identifiers, engine version, target platform values and credential values are withheld; no Unreal module or plugin is loaded.",
    ]
    return _report(path, "unreal", "Unreal Engine project descriptor audit", lines)
