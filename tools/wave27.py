"""Wave 27 digital preservation and research-data package auditors.

Read-only, bounded structural validators for preservation archives, linked-data
crates, scholarly/heritage metadata, geospatial catalogs and research datasets.
Payloads and metadata values are not emitted. Remote URLs are never fetched.
"""
from __future__ import annotations

import collections
import hashlib
import json
import math
import re
import tarfile
import urllib.parse
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

MAX_INPUT = 20 * 1024 * 1024
MAX_EXPANDED = 180 * 1024 * 1024
MAX_MEMBERS = 10_000
MAX_JSON = 10 * 1024 * 1024
MAX_XML = 12 * 1024 * 1024


def _report(path: Path, slug: str, heading: str, lines: list[str]) -> dict:
    output = path.with_name(path.stem + "-" + slug + "-report.txt")
    body = heading + "\n\n" + "\n".join(lines) + "\n"
    output.write_text(body, encoding="utf-8")
    return {"summary": body[:5_500], "output_path": str(output)}


def _json(path: Path):
    if path.stat().st_size > MAX_JSON:
        raise RuntimeError("Wave 27 JSON descriptor exceeds the 10 MiB limit.")
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Wave 27 JSON descriptor is malformed or not UTF-8.") from exc
    if not isinstance(value, dict):
        raise RuntimeError("Wave 27 JSON descriptor root must be an object.")
    return value


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


def _safe_relative(value: str) -> bool:
    normalized = value.replace("\\", "/")
    return bool(normalized) and not normalized.startswith("/") and not re.match(r"^[A-Za-z]:", normalized) and "\x00" not in normalized and all(part not in {"", ".", ".."} for part in normalized.split("/"))


def _walk_json(value, limit=100_000):
    stack = [value]
    seen = 0
    while stack:
        item = stack.pop()
        seen += 1
        if seen > limit:
            raise RuntimeError("JSON metadata graph exceeds the 100,000-node limit.")
        yield item
        if isinstance(item, dict):
            stack.extend(item.values())
        elif isinstance(item, list):
            stack.extend(item)


def bagit_archive_audit(path: Path) -> dict:
    if path.stat().st_size > MAX_INPUT:
        raise RuntimeError("BagIt archive exceeds the 20 MiB compressed input limit.")
    archive = None
    archive_kind = ""
    member_map = {}
    duplicate_names = 0
    expanded = 0
    unsafe = 0
    try:
        if zipfile.is_zipfile(path):
            archive = zipfile.ZipFile(path, "r")
            archive_kind = "ZIP"
            infos = archive.infolist()
            if len(infos) > MAX_MEMBERS:
                raise RuntimeError("BagIt ZIP exceeds the 10,000-member limit.")
            for info in infos:
                name = info.filename.replace("\\", "/").rstrip("/") if info.is_dir() else info.filename.replace("\\", "/")
                if not name:
                    continue
                if not _safe_relative(name):
                    unsafe += 1
                    raise RuntimeError("BagIt archive contains an unsafe member path.")
                mode = (info.external_attr >> 16) & 0xFFFF
                if (mode & 0o170000) == 0o120000 or info.flag_bits & 1:
                    unsafe += 1
                    raise RuntimeError("BagIt archive contains a symlink or encrypted member.")
                if name in member_map:
                    duplicate_names += 1
                    raise RuntimeError("BagIt archive contains duplicate member paths.")
                if not info.is_dir():
                    expanded += info.file_size
                    if expanded > MAX_EXPANDED:
                        raise RuntimeError("BagIt archive exceeds the 180 MiB expanded-size limit.")
                    member_map[name] = info
            def open_member(name):
                return archive.open(member_map[name], "r")
        else:
            archive = tarfile.open(path, "r:*")
            archive_kind = "TAR"
            for index, member in enumerate(archive):
                if index >= MAX_MEMBERS:
                    raise RuntimeError("BagIt TAR exceeds the 10,000-member limit.")
                name = member.name.replace("\\", "/").rstrip("/") if member.isdir() else member.name.replace("\\", "/")
                if not name:
                    continue
                if not _safe_relative(name):
                    unsafe += 1
                    raise RuntimeError("BagIt archive contains an unsafe member path.")
                if member.issym() or member.islnk() or not (member.isfile() or member.isdir()):
                    unsafe += 1
                    raise RuntimeError("BagIt archive contains links or unsupported special members.")
                if name in member_map:
                    duplicate_names += 1
                    raise RuntimeError("BagIt archive contains duplicate member paths.")
                if member.isfile():
                    expanded += member.size
                    if expanded > MAX_EXPANDED:
                        raise RuntimeError("BagIt archive exceeds the 180 MiB expanded-size limit.")
                    member_map[name] = member
            def open_member(name):
                stream = archive.extractfile(member_map[name])
                if stream is None:
                    raise RuntimeError("BagIt TAR member could not be opened.")
                return stream
        bag_declarations = [name for name in member_map if name == "bagit.txt" or name.endswith("/bagit.txt")]
        if len(bag_declarations) != 1:
            raise RuntimeError("BagIt archive must contain exactly one bagit.txt declaration.")
        bagit_name = bag_declarations[0]
        root_prefix = bagit_name[:-len("bagit.txt")]
        relative = {name[len(root_prefix):]: name for name in member_map if name.startswith(root_prefix)}
        if any(not key or not _safe_relative(key) for key in relative):
            raise RuntimeError("BagIt archive contains an invalid path relative to its bag root.")
        with open_member(bagit_name) as stream:
            declaration = stream.read(64 * 1024).decode("utf-8-sig", errors="replace")
        version_match = re.search(r"(?im)^BagIt-Version:\s*(\d+\.\d+)\s*$", declaration)
        encoding_match = re.search(r"(?im)^Tag-File-Character-Encoding:\s*([A-Za-z0-9._-]+)\s*$", declaration)
        version = version_match.group(1) if version_match else "missing/invalid"
        encoding = encoding_match.group(1) if encoding_match else "missing/invalid"
        bagit_issues = int(not version_match or not encoding_match)
        payload_paths = {key for key in relative if key.startswith("data/") and not key.endswith("/")}
        manifests = [(key, re.fullmatch(r"manifest-([A-Za-z0-9_-]+)\.txt", key)) for key in relative]
        manifests = [(key, match.group(1).lower()) for key, match in manifests if match]
        tag_manifests = [(key, re.fullmatch(r"tagmanifest-([A-Za-z0-9_-]+)\.txt", key)) for key in relative]
        tag_manifests = [(key, match.group(1).lower()) for key, match in tag_manifests if match]
        if not manifests:
            raise RuntimeError("BagIt archive is missing a payload manifest.")
        algorithms = set()
        listed_payloads = set()
        listed_tags = set()
        missing_files = checksum_mismatches = malformed_lines = duplicate_entries = unsupported_algorithms = 0
        payload_checks = tag_checks = 0

        def verify_manifest(key, algorithm, payload):
            nonlocal missing_files, checksum_mismatches, malformed_lines, duplicate_entries, unsupported_algorithms
            nonlocal payload_checks, tag_checks
            try:
                digest = hashlib.new(algorithm)
            except ValueError:
                unsupported_algorithms += 1
                return
            algorithms.add(algorithm)
            seen_paths = set()
            with open_member(relative[key]) as stream:
                raw_manifest = stream.read(8 * 1024 * 1024 + 1)
            if len(raw_manifest) > 8 * 1024 * 1024:
                raise RuntimeError("BagIt manifest exceeds the 8 MiB tag-file limit.")
            try:
                manifest_text = raw_manifest.decode(encoding if encoding != "missing/invalid" else "utf-8")
            except (UnicodeError, LookupError):
                malformed_lines += 1
                return
            for line in manifest_text.splitlines():
                if not line.strip():
                    continue
                match = re.match(r"^([0-9A-Fa-f]+)\s+(.+)$", line)
                if not match:
                    malformed_lines += 1
                    continue
                expected, raw_name = match.groups()
                member_path = urllib.parse.unquote(raw_name.strip())
                if not _safe_relative(member_path):
                    malformed_lines += 1
                    continue
                if member_path in seen_paths:
                    duplicate_entries += 1
                    continue
                seen_paths.add(member_path)
                if payload:
                    listed_payloads.add(member_path)
                    if not member_path.startswith("data/"):
                        malformed_lines += 1
                        continue
                else:
                    listed_tags.add(member_path)
                    if member_path.startswith("data/") or member_path.startswith("tagmanifest-"):
                        malformed_lines += 1
                        continue
                archive_path = root_prefix + member_path
                if archive_path not in member_map:
                    missing_files += 1
                    continue
                actual = hashlib.new(algorithm)
                with open_member(archive_path) as stream:
                    while True:
                        chunk = stream.read(1024 * 1024)
                        if not chunk:
                            break
                        actual.update(chunk)
                if actual.hexdigest().lower() != expected.lower():
                    checksum_mismatches += 1
                if payload:
                    payload_checks += 1
                else:
                    tag_checks += 1

        for key, algorithm in manifests:
            verify_manifest(key, algorithm, True)
        for key, algorithm in tag_manifests:
            verify_manifest(key, algorithm, False)
        unmanifested_payloads = len(payload_paths - listed_payloads)
        tag_files = {key for key in relative if key and not key.startswith("data/") and key not in { "bagit.txt" } and not key.startswith("tagmanifest-")}
        unmanifested_tags = len(tag_files - listed_tags) if tag_manifests else 0
        lines = [
            f"Archive container: {archive_kind}",
            f"BagIt version: {version}",
            f"Tag-file encoding declaration present: {encoding != 'missing/invalid'}",
            f"Bag declaration issues: {bagit_issues:,}",
            f"Archive members: {len(member_map):,}",
            f"Expanded bytes: {expanded:,}",
            f"Payload manifest files: {len(manifests):,}",
            f"Tag manifest files: {len(tag_manifests):,}",
            f"Payload files under data/: {len(payload_paths):,}",
            f"Payload manifest entries checked: {payload_checks:,}",
            f"Tag manifest entries checked: {tag_checks:,}",
            f"Missing referenced files: {missing_files:,}",
            f"Checksum mismatches: {checksum_mismatches:,}",
            f"Payload files not listed by a manifest: {unmanifested_payloads:,}",
            f"Tag files not listed by a tagmanifest: {unmanifested_tags:,}",
            f"Malformed manifest lines: {malformed_lines:,}",
            f"Duplicate manifest entries: {duplicate_entries:,}",
            f"Unsupported checksum algorithms: {unsupported_algorithms:,}",
            f"Duplicate archive member paths: {duplicate_names:,}",
            f"Unsafe archive members rejected: {unsafe:,}",
            "Member paths, checksums, bag metadata, payload contents and tag values are withheld.",
        ]
        return _report(path, "bagit", "BagIt preservation archive audit", lines)
    except (zipfile.BadZipFile, tarfile.TarError, OSError, EOFError) as exc:
        raise RuntimeError("BagIt archive is malformed or damaged.") from exc
    finally:
        if archive is not None:
            archive.close()


def frictionless_package_audit(path: Path) -> dict:
    document = _json(path)
    resources = document.get("resources")
    if not isinstance(resources, list):
        raise RuntimeError("Frictionless Data Package must contain a resources array.")
    resource_names = []
    duplicate_names = unsafe_paths = remote_resources = missing_paths = 0
    fields_total = schema_errors = primary_key_errors = foreign_key_errors = 0
    resource_profiles = collections.Counter()
    for resource in resources:
        if not isinstance(resource, dict):
            schema_errors += 1
            continue
        name = resource.get("name")
        if isinstance(name, str):
            duplicate_names += name in resource_names
            resource_names.append(name)
        path_value = resource.get("path")
        paths_value = resource.get("path")
        if paths_value is None and isinstance(resource.get("data"), list):
            pass
        elif isinstance(paths_value, str):
            parsed = urllib.parse.urlsplit(paths_value)
            if parsed.scheme or parsed.netloc:
                remote_resources += 1
            elif not _safe_relative(paths_value):
                unsafe_paths += 1
        elif isinstance(paths_value, list):
            for item in paths_value:
                if not isinstance(item, str):
                    schema_errors += 1
                    continue
                parsed = urllib.parse.urlsplit(item)
                remote_resources += bool(parsed.scheme or parsed.netloc)
                unsafe_paths += not bool(parsed.scheme or parsed.netloc) and not _safe_relative(item)
        elif not isinstance(resource.get("data"), list):
            missing_paths += 1
        schema = resource.get("schema")
        if schema is not None:
            if not isinstance(schema, dict):
                schema_errors += 1
            else:
                fields = schema.get("fields")
                if not isinstance(fields, list):
                    schema_errors += 1
                    fields = []
                field_names = []
                for field in fields:
                    if not isinstance(field, dict) or not isinstance(field.get("name"), str):
                        schema_errors += 1
                        continue
                    field_names.append(field["name"])
                    fields_total += 1
                if len(field_names) != len(set(field_names)):
                    schema_errors += len(field_names) - len(set(field_names))
                primary = schema.get("primaryKey")
                if primary is not None:
                    keys = primary if isinstance(primary, list) else [primary]
                    primary_key_errors += sum(1 for key in keys if key not in field_names)
                foreign = schema.get("foreignKeys", [])
                if foreign is not None and not isinstance(foreign, list):
                    schema_errors += 1
                elif isinstance(foreign, list):
                    for key in foreign:
                        if not isinstance(key, dict):
                            foreign_key_errors += 1
                            continue
                        local = key.get("fields", [])
                        local = local if isinstance(local, list) else [local]
                        foreign_key_errors += any(item not in field_names for item in local)
        profile = resource.get("profile")
        if isinstance(profile, str):
            resource_profiles["custom/default" if profile in {"dataresource", "https://datapackage.org/profiles/2.0/dataresource.json", "https://specs.frictionlessdata.io/schemas/table-schema.json"} else "custom/other"] += 1
    package_profile = document.get("profile")
    schema_url = document.get("$schema")
    version = "2.0" if isinstance(schema_url, str) and "/2.0/" in schema_url else "1.x/unspecified"
    lines = [
        f"Descriptor format: Frictionless Data Package",
        f"Descriptor version profile: {version}",
        f"Resource entries: {len(resources):,}",
        f"Duplicate resource names: {duplicate_names:,}",
        f"Resources without path or inline data: {missing_paths:,}",
        f"Remote resource URIs (not fetched): {remote_resources:,}",
        f"Unsafe relative resource paths: {unsafe_paths:,}",
        f"Schema field entries: {fields_total:,}",
        f"Schema structure issues: {schema_errors:,}",
        f"Primary-key field references missing from schema: {primary_key_errors:,}",
        f"Foreign-key local field reference issues: {foreign_key_errors:,}",
        f"Resource profile declarations: {sum(resource_profiles.values()):,}",
        f"Package profile field present: {bool(package_profile)}",
        "Package/resource names, paths, URLs, field names, license values and metadata contents are withheld.",
    ]
    return _report(path, "frictionless", "Frictionless Data Package descriptor audit", lines)


def ro_crate_audit(path: Path) -> dict:
    document = _json(path)
    graph = document.get("@graph")
    if not isinstance(graph, list):
        raise RuntimeError("RO-Crate metadata must contain an @graph array.")
    if len(graph) > 100_000:
        raise RuntimeError("RO-Crate @graph exceeds the 100,000-entity limit.")
    ids = set()
    duplicate_ids = invalid_entities = 0
    type_counts = collections.Counter()
    refs = set()
    root_dataset = metadata_descriptor = 0
    for entity in graph:
        if not isinstance(entity, dict):
            invalid_entities += 1
            continue
        identifier = entity.get("@id")
        if not isinstance(identifier, str) or not identifier:
            invalid_entities += 1
            continue
        if identifier in ids:
            duplicate_ids += 1
        ids.add(identifier)
        types = entity.get("@type", [])
        types = types if isinstance(types, list) else [types]
        for value in types:
            if isinstance(value, str):
                type_counts[value.lower()] += 1
        if identifier in {"./", ""} and any(str(value).lower() == "dataset" for value in types):
            root_dataset += 1
        if identifier.endswith("ro-crate-metadata.json") and any(str(value).lower() == "creativework" for value in types):
            metadata_descriptor += 1
        for item in _walk_json(entity, limit=100_000):
            if isinstance(item, dict):
                target = item.get("@id")
                if isinstance(target, str) and target and target not in {identifier, "./"}:
                    if not urllib.parse.urlsplit(target).scheme and not target.startswith("#"):
                        refs.add(target)
    missing_refs = sum(1 for target in refs if target not in ids and not target.endswith("/"))
    lines = [
        f"RO-Crate format version: {document.get('version', 'unspecified') if str(document.get('version', '')).startswith('1.') else '1.x/unspecified'}",
        f"JSON-LD graph entities: {len(graph):,}",
        f"Entities with invalid/missing @id: {invalid_entities:,}",
        f"Duplicate @id values: {duplicate_ids:,}",
        f"Root Dataset entity count: {root_dataset:,}",
        f"RO-Crate metadata descriptor node count: {metadata_descriptor:,}",
        f"Distinct internal @id references: {len(refs):,}",
        f"Internal references without a matching graph entity: {missing_refs:,}",
        "Common entity type counts: " + (", ".join(f"{key}={value}" for key, value in type_counts.most_common(12)) or "none"),
        "Entity IDs, people/organization names, paths, descriptions, license values and contextual metadata are withheld.",
    ]
    return _report(path, "rocrate", "RO-Crate JSON-LD metadata audit", lines)


def iiif_manifest_audit(path: Path) -> dict:
    document = _json(path)
    context = document.get("@context")
    context_values = context if isinstance(context, list) else [context]
    has_iiif_context = any(isinstance(value, str) and "iiif.io/api/presentation" in value for value in context_values)
    manifest_type = str(document.get("type", "")).lower()
    identifier = document.get("id")
    canvases = document.get("items", [])
    if not isinstance(canvases, list):
        raise RuntimeError("IIIF Manifest items must be an array of Canvas resources.")
    if len(canvases) > 100_000:
        raise RuntimeError("IIIF Manifest exceeds the 100,000 Canvas limit.")
    canvas_ids = set()
    duplicate_canvas_ids = missing_canvas_fields = invalid_dimensions = 0
    annotations = annotation_pages = image_bodies = services = ranges = 0
    missing_targets = invalid_ids = 0
    for canvas in canvases:
        if not isinstance(canvas, dict):
            missing_canvas_fields += 1
            continue
        canvas_id = canvas.get("id")
        if not isinstance(canvas_id, str) or not urllib.parse.urlsplit(canvas_id).scheme:
            invalid_ids += 1
        if isinstance(canvas_id, str):
            if canvas_id in canvas_ids:
                duplicate_canvas_ids += 1
            canvas_ids.add(canvas_id)
        if str(canvas.get("type", "")).lower() != "canvas":
            missing_canvas_fields += 1
        try:
            width, height = int(canvas.get("width", 0)), int(canvas.get("height", 0))
            if width <= 0 or height <= 0:
                invalid_dimensions += 1
        except (ValueError, TypeError):
            invalid_dimensions += 1
        pages = canvas.get("items", [])
        if not isinstance(pages, list):
            missing_canvas_fields += 1
            continue
        annotation_pages += len(pages)
        for page in pages:
            if not isinstance(page, dict):
                missing_canvas_fields += 1
                continue
            items = page.get("items", [])
            if not isinstance(items, list):
                missing_canvas_fields += 1
                continue
            annotations += len(items)
            for annotation in items:
                if not isinstance(annotation, dict):
                    missing_canvas_fields += 1
                    continue
                target = annotation.get("target")
                if target is None:
                    missing_targets += 1
                body = annotation.get("body", [])
                body = body if isinstance(body, list) else [body]
                for item in body:
                    if not isinstance(item, dict):
                        continue
                    if str(item.get("type", "")).lower() == "image":
                        image_bodies += 1
                    svc = item.get("service", [])
                    services += len(svc) if isinstance(svc, list) else int(bool(svc))
    structures = document.get("structures", [])
    ranges = len(structures) if isinstance(structures, list) else 0
    lines = [
        f"IIIF Presentation context present: {has_iiif_context}",
        f"Manifest type valid: {manifest_type == 'manifest'}",
        f"Manifest ID present: {bool(identifier)}",
        f"Canvas items: {len(canvases):,}",
        f"Duplicate Canvas IDs: {duplicate_canvas_ids:,}",
        f"Canvas records with missing/wrong type: {missing_canvas_fields:,}",
        f"Canvas records with invalid dimensions: {invalid_dimensions:,}",
        f"Canvas identifiers with invalid/missing URI: {invalid_ids:,}",
        f"Annotation Pages: {annotation_pages:,}",
        f"Annotations: {annotations:,}",
        f"Annotations missing target: {missing_targets:,}",
        f"Image body resources: {image_bodies:,}",
        f"Image service references: {services:,}",
        f"Range/structure entries: {ranges:,}",
        "Manifest labels, canvas IDs, annotation bodies, URLs, image service URLs and rights text are withheld; remote canvases/images are never fetched.",
    ]
    return _report(path, "iiif", "IIIF Presentation API 3 Manifest audit", lines)


def datacite_metadata_audit(path: Path) -> dict:
    root = _xml(path.read_bytes(), "DataCite")
    if _local(root.tag) != "resource":
        raise RuntimeError("DataCite XML root must be resource.")
    def count(name):
        return sum(1 for node in root.iter() if _local(node.tag) == name.lower())
    identifier_nodes = [node for node in root.iter() if _local(node.tag) == "identifier"]
    identifier_valid = sum(1 for node in identifier_nodes if node.attrib.get("identifierType", "").lower() == "doi" and re.fullmatch(r"10\.\d{4,9}/\S+", (node.text or "").strip(), re.I))
    creators = count("creator")
    titles = count("title")
    publisher = count("publisher")
    publication_year = count("publicationyear")
    resource_type = count("resourcetype")
    related = count("relatedidentifier")
    subjects = count("subject")
    dates = count("date")
    descriptions = count("description")
    contributors = count("contributor")
    duplicates = 0
    seen_dois = set()
    for node in identifier_nodes:
        if node.attrib.get("identifierType", "").lower() == "doi":
            value = (node.text or "").strip().lower()
            if value in seen_dois:
                duplicates += 1
            if value:
                seen_dois.add(value)
    required_missing = sum(1 for value in (identifier_nodes, creators, titles, publisher, publication_year, resource_type) if not value)
    invalid_year = 0
    for node in root.iter():
        if _local(node.tag) == "publicationyear":
            value = (node.text or "").strip()
            if not re.fullmatch(r"\d{4}", value):
                invalid_year += 1
    version = root.attrib.get("schemaVersion", "unspecified")
    lines = [
        f"DataCite XML schema version field: {version if version in {'4.7', '4.6', '4.5', '4.4', '4.3', '4.2', '4.1', '4.0'} else 'unspecified/other'}",
        f"Identifier records: {len(identifier_nodes):,}",
        f"DOI-shaped identifiers: {identifier_valid:,}",
        f"Repeated DOI identifier values: {duplicates:,}",
        f"Creator entries: {creators:,}",
        f"Contributor entries: {contributors:,}",
        f"Title entries: {titles:,}",
        f"Publisher entries: {publisher:,}",
        f"Publication-year entries: {publication_year:,}",
        f"Publication-year format issues: {invalid_year:,}",
        f"Resource-type entries: {resource_type:,}",
        f"Related identifiers: {related:,}",
        f"Subject entries: {subjects:,}",
        f"Date entries: {dates:,}",
        f"Description entries: {descriptions:,}",
        f"Missing core metadata categories: {required_missing:,}",
        "DOIs, titles, contributor names, publisher values, subject terms, rights and description text are withheld.",
    ]
    return _report(path, "datacite", "DataCite metadata XML audit", lines)


def mets_package_audit(path: Path) -> dict:
    root = _xml(path.read_bytes(), "METS")
    if _local(root.tag) != "mets":
        raise RuntimeError("METS XML root must be mets.")
    ids = set()
    duplicate_ids = invalid_fptr = missing_section_refs = 0
    file_entries = divs = fptrs = dmd_secs = amd_secs = 0
    struct_maps = file_secs = mets_hdrs = 0
    for node in root.iter():
        tag = _local(node.tag)
        if tag == "mets":
            pass
        if tag == "metshdr":
            mets_hdrs += 1
        elif tag == "dmdsec":
            dmd_secs += 1
        elif tag == "amdsec":
            amd_secs += 1
        elif tag == "filesec":
            file_secs += 1
        elif tag == "structmap":
            struct_maps += 1
        elif tag == "file":
            file_entries += 1
        elif tag == "div":
            divs += 1
        elif tag == "fptr":
            fptrs += 1
        identifier = node.attrib.get("ID") or node.attrib.get("id")
        if identifier:
            if identifier in ids:
                duplicate_ids += 1
            ids.add(identifier)
    for node in root.iter():
        tag = _local(node.tag)
        if tag == "fptr":
            target = node.attrib.get("FILEID") or node.attrib.get("fileId")
            if target and target not in ids:
                invalid_fptr += 1
        for key in ("DMDID", "ADMID", "CONTENTIDS"):
            raw = node.attrib.get(key)
            if raw:
                for target in raw.split():
                    if target not in ids:
                        missing_section_refs += 1
    missing_required = sum(1 for count_value in (mets_hdrs, file_secs, struct_maps) if count_value == 0)
    lines = [
        f"METS root element valid: True",
        f"METS header sections: {mets_hdrs:,}",
        f"Descriptive metadata sections: {dmd_secs:,}",
        f"Administrative metadata sections: {amd_secs:,}",
        f"File sections: {file_secs:,}",
        f"File entries: {file_entries:,}",
        f"Structural maps: {struct_maps:,}",
        f"Structural divisions: {divs:,}",
        f"File pointers: {fptrs:,}",
        f"Duplicate METS IDs: {duplicate_ids:,}",
        f"FILEID references without matching ID: {invalid_fptr:,}",
        f"DMDID/ADMID/CONTENTIDS references without matching ID: {missing_section_refs:,}",
        f"Missing common section categories: {missing_required:,}",
        "File paths, identifiers, checksums, metadata values, labels and descriptive text are withheld.",
    ]
    return _report(path, "mets", "METS preservation package XML audit", lines)


def premis_event_audit(path: Path) -> dict:
    root = _xml(path.read_bytes(), "PREMIS")
    if _local(root.tag) not in {"premis", "premisobject", "premiscontainer"}:
        raise RuntimeError("PREMIS XML root element is not recognized.")
    counts = collections.Counter()
    identifiers = set()
    duplicate_identifiers = missing_links = invalid_dates = 0
    identifier_entity = {
        "objectidentifier": "object",
        "eventidentifier": "event",
        "agentidentifier": "agent",
        "rightsstatementidentifier": "rights",
    }
    linking_entity = {
        "linkingobjectidentifier": "object",
        "linkingeventidentifier": "event",
        "linkingagentidentifier": "agent",
        "linkingrightsstatementidentifier": "rights",
    }
    link_refs = []
    for node in root.iter():
        tag = _local(node.tag)
        if tag in {"object", "event", "agent", "rights"}:
            counts[tag] += 1
        if tag in identifier_entity:
            identifier_type = ""
            identifier_value = ""
            for child in node:
                child_tag = _local(child.tag)
                if child_tag.endswith("identifiertype"):
                    identifier_type = (child.text or "").strip()
                elif child_tag.endswith("identifiervalue"):
                    identifier_value = (child.text or "").strip()
            if identifier_value:
                key = (identifier_entity[tag], identifier_type, identifier_value)
                if key in identifiers:
                    duplicate_identifiers += 1
                identifiers.add(key)
        if tag in linking_entity:
            link_type = ""
            link_value = ""
            for child in node:
                child_tag = _local(child.tag)
                if child_tag.endswith("identifiertype"):
                    link_type = (child.text or "").strip()
                elif child_tag.endswith("identifiervalue"):
                    link_value = (child.text or "").strip()
            if link_value:
                link_refs.append((linking_entity[tag], link_type, link_value))
        if tag == "eventdatetime" and node.text:
            value = node.text.strip()
            if not re.match(r"^\d{4}-\d\d-\d\dT", value):
                invalid_dates += 1
    missing_links = sum(
        1 for entity_type, identifier_type, value in link_refs
        if (entity_type, identifier_type, value) not in identifiers
    )
    lines = [
        f"PREMIS object entities: {counts['object']:,}",
        f"PREMIS event entities: {counts['event']:,}",
        f"PREMIS agent entities: {counts['agent']:,}",
        f"PREMIS rights entities: {counts['rights']:,}",
        f"Object/event/agent/rights identifier elements: {len(identifiers):,}",
        f"Repeated identifier values within entity type: {duplicate_identifiers:,}",
        f"Linking identifier references: {len(link_refs):,}",
        f"Linking references without a matching identifier: {missing_links:,}",
        f"Event-date values with invalid timestamp shape: {invalid_dates:,}",
        "Object identifiers, agents, event detail, software values, rights statements and preservation metadata values are withheld.",
    ]
    return _report(path, "premis", "PREMIS digital preservation event audit", lines)


def stac_catalog_audit(path: Path) -> dict:
    document = _json(path)
    stac_type = str(document.get("type", ""))
    if stac_type not in {"Catalog", "Collection", "Feature"}:
        raise RuntimeError("STAC JSON type must be Catalog, Collection or Feature/Item.")
    version = str(document.get("stac_version", ""))
    version_valid = bool(re.fullmatch(r"\d+\.\d+\.\d+", version))
    version_display = version if version_valid else "unspecified/invalid"
    extensions = document.get("stac_extensions", [])
    links = document.get("links", [])
    assets = document.get("assets", {})
    properties = document.get("properties", {})
    invalid_links = 0
    if not isinstance(links, list):
        invalid_links += 1
        links = []
    if not isinstance(assets, dict):
        invalid_links += 1
        assets = {}
    if not isinstance(properties, dict):
        invalid_links += 1
        properties = {}
    relation_counts = collections.Counter()
    for link in links:
        if not isinstance(link, dict):
            invalid_links += 1
            continue
        rel = link.get("rel")
        if isinstance(rel, str):
            relation_counts[rel] += 1
        href = link.get("href")
        if not isinstance(href, str) or not href:
            invalid_links += 1
    asset_role_counts = collections.Counter()
    invalid_assets = 0
    for asset in assets.values():
        if not isinstance(asset, dict) or not isinstance(asset.get("href"), str):
            invalid_assets += 1
            continue
        roles = asset.get("roles", [])
        if isinstance(roles, list):
            for role in roles:
                if isinstance(role, str):
                    asset_role_counts[role] += 1
        elif roles is not None:
            invalid_assets += 1
    item_bbox = document.get("bbox")
    invalid_bbox = int(item_bbox is not None and (not isinstance(item_bbox, list) or len(item_bbox) not in {4, 6}))
    datetime_present = bool(properties.get("datetime") or properties.get("start_datetime") or properties.get("end_datetime"))
    extent = document.get("extent") if isinstance(document.get("extent"), dict) else {}
    extent_spatial = extent.get("spatial") if isinstance(extent.get("spatial"), dict) else {}
    extent_temporal = extent.get("temporal") if isinstance(extent.get("temporal"), dict) else {}
    spatial_ranges = extent_spatial.get("bbox", []) if isinstance(extent_spatial.get("bbox"), list) else []
    temporal_ranges = extent_temporal.get("interval", []) if isinstance(extent_temporal.get("interval"), list) else []
    lines = [
        f"STAC object type: {stac_type}",
        f"STAC version: {version_display}",
        f"STAC extension references: {len(extensions) if isinstance(extensions, list) else 0}",
        f"Link entries: {len(links):,}",
        f"Invalid link records/refs: {invalid_links:,}",
        f"Link relation categories: " + (", ".join(f"{key}={value}" for key, value in sorted(relation_counts.items())) or "none"),
        f"Asset entries: {len(assets):,}",
        f"Invalid asset entries: {invalid_assets:,}",
        f"Asset role categories: " + (", ".join(f"{key}={value}" for key, value in sorted(asset_role_counts.items())) or "none"),
        f"Item geometry object present: {isinstance(document.get('geometry'), (dict, type(None)))}",
        f"Item bbox shape issue: {invalid_bbox}",
        f"Item temporal datetime property present: {datetime_present}",
        f"Collection spatial extent ranges: {len(spatial_ranges):,}",
        f"Collection temporal extent ranges: {len(temporal_ranges):,}",
        "Item IDs, collection IDs, geometry, coordinates, asset HREFs, metadata and provider information are withheld; external assets are never fetched.",
    ]
    return _report(path, "stac", "STAC catalog/item/collection audit", lines)


def tei_document_audit(path: Path) -> dict:
    root = _xml(path.read_bytes(), "TEI")
    if _local(root.tag) not in {"tei", "teicorpus"}:
        raise RuntimeError("TEI XML root must be TEI or teiCorpus.")
    counts = collections.Counter()
    xml_ids = set()
    duplicate_ids = missing_targets = 0
    targets = set()
    for node in root.iter():
        tag = _local(node.tag)
        if tag in {"teiheader", "filedesc", "titlestmt", "publicationstmt", "sourcedesc", "text", "front", "body", "back", "div", "p", "lg", "l", "sp", "stage", "pb", "lb", "note", "ref", "ptr", "list", "item", "graphic", "persname", "orgname", "placename", "bibl", "biblstruct"}:
            counts[tag] += 1
        xml_id = node.attrib.get("{http://www.w3.org/XML/1998/namespace}id")
        if xml_id:
            if xml_id in xml_ids:
                duplicate_ids += 1
            xml_ids.add(xml_id)
        for key in ("target", "corresp", "sameAs", "copyOf", "next", "prev"):
            value = node.attrib.get(key)
            if value:
                for token in value.split():
                    parsed = urllib.parse.urlsplit(token)
                    # Only a bare same-document fragment is checked against this
                    # TEI file. External and sibling-document fragments are not
                    # false positives for this document's xml:id inventory.
                    if not parsed.scheme and not parsed.netloc and not parsed.path and parsed.fragment:
                        targets.add(urllib.parse.unquote(parsed.fragment))
    missing_targets = sum(1 for target in targets if target not in xml_ids)
    lines = [
        f"TEI root valid: True",
        f"TEI header occurrences: {counts['teiheader']:,}",
        f"fileDesc/titleStmt/publicationStmt/sourceDesc entries: {counts['filedesc']:,}/{counts['titlestmt']:,}/{counts['publicationstmt']:,}/{counts['sourcedesc']:,}",
        f"text/body/front/back structures: {counts['text']:,}/{counts['body']:,}/{counts['front']:,}/{counts['back']:,}",
        f"div/p/line/speech/note elements: {counts['div']:,}/{counts['p']:,}/{counts['l']:,}/{counts['sp']:,}/{counts['note']:,}",
        f"page/line-break and reference elements: {counts['pb']:,}/{counts['lb']:,}/{counts['ref'] + counts['ptr']:,}",
        f"xml:id values: {len(xml_ids):,}",
        f"Duplicate xml:id values: {duplicate_ids:,}",
        f"Distinct internal fragment targets: {len(targets):,}",
        f"Internal fragment targets without matching xml:id: {missing_targets:,}",
        "Document text, titles, author/editor names, place names, IDs, references and scholarly content are withheld.",
    ]
    return _report(path, "tei", "TEI P5 scholarly text structure audit", lines)
