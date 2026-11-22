"""Wave 28 scientific, medical, geospatial and preservation format auditors.

Read-only and bounded metadata/header inspection. No pixel, voxel, point-cloud,
array-chunk or scientific payload values are exported. External references are
never fetched and archive members are never extracted to disk.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import math
import re
import struct
import zipfile
from pathlib import Path, PurePosixPath

MAX_INPUT = 20 * 1024 * 1024
MAX_EXPANDED = 180 * 1024 * 1024
MAX_MEMBERS = 10_000
MAX_METADATA = 10 * 1024 * 1024


def _report(path: Path, slug: str, heading: str, lines: list[str]) -> dict:
    output = path.with_name(path.stem + "-" + slug + "-report.txt")
    body = heading + "\n\n" + "\n".join(lines) + "\n"
    output.write_text(body, encoding="utf-8")
    return {"summary": body[:5_500], "output_path": str(output)}


def _size_guard(path: Path) -> None:
    if path.stat().st_size > MAX_INPUT:
        raise RuntimeError("Scientific-format input exceeds the 20 MiB limit.")


def _json_bytes(raw: bytes, label: str) -> dict:
    if len(raw) > 2 * 1024 * 1024:
        raise RuntimeError(f"{label} metadata file exceeds the 2 MiB per-file limit.")
    try:
        value = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"{label} metadata is malformed or not UTF-8.") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} metadata root must be an object.")
    return value


def _safe_member(name: str) -> bool:
    if not name or "\\" in name or "\x00" in name or name.startswith("/"):
        return False
    if re.match(r"^[A-Za-z]:", name):
        return False
    parts = name.rstrip("/").split("/")
    return bool(parts) and all(part not in {"", ".", ".."} for part in parts)


def _zip_index(path: Path, label: str):
    if path.stat().st_size > MAX_INPUT:
        raise RuntimeError(f"{label} ZIP exceeds the 20 MiB compressed-size limit.")
    try:
        archive = zipfile.ZipFile(path, "r")
    except (OSError, zipfile.BadZipFile) as exc:
        raise RuntimeError(f"{label} ZIP archive is malformed.") from exc
    infos = archive.infolist()
    if len(infos) > MAX_MEMBERS:
        archive.close()
        raise RuntimeError(f"{label} ZIP exceeds the 10,000-member limit.")
    members = {}
    expanded = 0
    try:
        for info in infos:
            name = info.filename.rstrip("/") if info.is_dir() else info.filename
            if not _safe_member(name):
                raise RuntimeError(f"{label} archive contains an unsafe member path.")
            mode = (info.external_attr >> 16) & 0xFFFF
            if (mode & 0o170000) == 0o120000 or info.flag_bits & 1:
                raise RuntimeError(f"{label} archive contains a symlink or encrypted member.")
            if name in members:
                raise RuntimeError(f"{label} archive contains duplicate member paths.")
            if not info.is_dir():
                expanded += info.file_size
                if expanded > MAX_EXPANDED:
                    raise RuntimeError(f"{label} archive exceeds the 180 MiB expanded-size limit.")
                members[name] = info
        return archive, members, expanded
    except Exception:
        archive.close()
        raise


def _read_bounded(archive: zipfile.ZipFile, info: zipfile.ZipInfo, limit: int) -> bytes:
    if info.file_size > limit:
        raise RuntimeError("A scientific-format metadata document exceeds its size limit.")
    with archive.open(info, "r") as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise RuntimeError("A scientific-format metadata document exceeds its size limit.")
    return raw


def ocfl_object_audit(path: Path) -> dict:
    """Audit a ZIP-packaged OCFL Object inventory and fixity without extraction."""
    _size_guard(path)
    archive = None
    try:
        archive, members, expanded = _zip_index(path, "OCFL")
        inventories = [name for name in members if PurePosixPath(name).name == "inventory.json"]
        roots = [name[:-len("inventory.json")] for name in inventories if name.endswith("inventory.json")]
        if len(inventories) != 1 or len(roots) != 1:
            raise RuntimeError("OCFL archive must contain exactly one object-root inventory.json.")
        root = roots[0]
        inventory_name = inventories[0]
        declaration_names = [name for name in members if name.startswith(root) and
                             PurePosixPath(name[len(root):]).name in {"0=ocfl_object_1.0", "0=ocfl_object_1.1"}]
        if len(declaration_names) != 1:
            raise RuntimeError("OCFL object must contain one 1.0 or 1.1 NAMASTE declaration.")
        declaration = PurePosixPath(declaration_names[0]).name
        version = declaration.rsplit("_", 1)[-1]
        raw = _read_bounded(archive, members[inventory_name], 8 * 1024 * 1024)
        inventory = _json_bytes(raw, "OCFL inventory")
        algorithm = str(inventory.get("digestAlgorithm", "")).lower()
        if algorithm not in {"sha512", "sha256", "sha1", "md5"}:
            raise RuntimeError("OCFL inventory declares an unsupported digest algorithm.")
        current = inventory.get("head")
        versions = inventory.get("versions")
        manifest = inventory.get("manifest")
        if not isinstance(current, str) or not isinstance(versions, dict) or not versions or not isinstance(manifest, dict):
            raise RuntimeError("OCFL inventory is missing head, versions or manifest structures.")
        sidecar_name = inventory_name + "." + algorithm
        sidecar_checked = 0
        sidecar_mismatch = 0
        if sidecar_name in members:
            sidecar = _read_bounded(archive, members[sidecar_name], 4096).decode("ascii", errors="replace").strip().split()
            expected = sidecar[0].lower() if sidecar else ""
            actual = hashlib.new(algorithm, raw).hexdigest().lower()
            sidecar_checked = 1
            sidecar_mismatch = int(expected != actual)
        else:
            sidecar_mismatch = 1
        manifest_digests = {}
        unsafe_paths = missing_files = digest_mismatches = 0
        files_checked = 0
        for digest, paths in manifest.items():
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-fA-F]+", digest):
                unsafe_paths += 1
                continue
            try:
                hashlib.new(algorithm)
            except ValueError:
                unsafe_paths += 1
                continue
            if not isinstance(paths, list):
                unsafe_paths += 1
                continue
            manifest_digests[digest.lower()] = paths
            for relative in paths:
                if not isinstance(relative, str) or not _safe_member(relative):
                    unsafe_paths += 1
                    continue
                archive_name = root + relative
                info = members.get(archive_name)
                if info is None:
                    missing_files += 1
                    continue
                hasher = hashlib.new(algorithm)
                with archive.open(info, "r") as stream:
                    while True:
                        chunk = stream.read(1024 * 1024)
                        if not chunk:
                            break
                        hasher.update(chunk)
                digest_mismatches += int(hasher.hexdigest().lower() != digest.lower())
                files_checked += 1
        state_refs = missing_state_digests = invalid_states = 0
        for version_id, version_info in versions.items():
            if not isinstance(version_id, str) or not re.fullmatch(r"v[1-9]\d*", version_id) or not isinstance(version_info, dict):
                invalid_states += 1
                continue
            state = version_info.get("state")
            if not isinstance(state, dict):
                invalid_states += 1
                continue
            logical_paths = set()
            for digest, paths in state.items():
                if not isinstance(paths, list):
                    invalid_states += 1
                    continue
                state_refs += len(paths)
                if str(digest).lower() not in manifest_digests:
                    missing_state_digests += 1
                for logical in paths:
                    if not isinstance(logical, str) or not _safe_member(logical):
                        invalid_states += 1
                    elif logical in logical_paths:
                        invalid_states += 1
                    else:
                        logical_paths.add(logical)
        head_missing = int(current not in versions)
        lines = [
            f"OCFL specification declaration: {version}",
            f"Inventory sidecar checked: {sidecar_checked:,}",
            f"Inventory sidecar digest mismatches or missing: {sidecar_mismatch:,}",
            f"Current head resolves to a version: {not bool(head_missing)}",
            f"Object versions: {len(versions):,}",
            f"Manifest digest entries: {len(manifest_digests):,}",
            f"Manifest content paths checked: {files_checked:,}",
            f"Manifest files missing from archive: {missing_files:,}",
            f"Content digest mismatches: {digest_mismatches:,}",
            f"State-to-manifest digest references: {state_refs:,}",
            f"State digests missing from manifest: {missing_state_digests:,}",
            f"Invalid or duplicate state paths/records: {invalid_states:,}",
            f"Unsafe manifest paths/entries: {unsafe_paths:,}",
            f"Archive members: {len(members):,}",
            f"Expanded archive bytes: {expanded:,}",
            "Object identifiers, logical paths, content paths, version messages and payload bytes are withheld.",
        ]
        return _report(path, "ocfl", "OCFL 1.0/1.1 object inventory and fixity audit", lines)
    except (zipfile.BadZipFile, OSError, EOFError) as exc:
        raise RuntimeError("OCFL archive is malformed or damaged.") from exc
    finally:
        if archive is not None:
            archive.close()


def zarr_store_audit(path: Path) -> dict:
    """Inspect Zarr v2/v3 ZIP stores at metadata level; never reads chunk payloads."""
    archive, members, expanded = _zip_index(path, "Zarr")
    try:
        metadata_names = [name for name in members
                          if PurePosixPath(name).name in {".zgroup", ".zarray", ".zattrs", "zarr.json", ".zmetadata"}]
        if not metadata_names:
            raise RuntimeError("ZIP does not contain recognized Zarr v2/v3 metadata files.")
        roots = []
        for name in metadata_names:
            parts = name.split("/")
            for i, part in enumerate(parts[:-1]):
                if part.lower().endswith(".zarr"):
                    roots.append("/".join(parts[:i + 1]) + "/")
        if roots:
            root = min(roots, key=len)
        else:
            metadata_parents = [str(PurePosixPath(name).parent) for name in metadata_names]
            non_root_parents = [value for value in metadata_parents if value not in {"", "."}]
            root = ""
            if non_root_parents and len(non_root_parents) == len(metadata_parents):
                first_parts = non_root_parents[0].split("/")
                common = []
                for index in range(min(map(lambda value: len(value.split("/")), non_root_parents))):
                    component = first_parts[index]
                    if all(value.split("/")[index] == component for value in non_root_parents):
                        common.append(component)
                    else:
                        break
                if common:
                    root = "/".join(common) + "/"
        parsed = {}
        total = 0
        for name in metadata_names:
            if not name.startswith(root):
                continue
            raw = _read_bounded(archive, members[name], 2 * 1024 * 1024)
            total += len(raw)
            if total > MAX_METADATA:
                raise RuntimeError("Zarr metadata exceeds the 10 MiB aggregate limit.")
            parsed[name[len(root):]] = _json_bytes(raw, "Zarr")
        groups = arrays = malformed = 0
        nodes = {}
        for key, value in parsed.items():
            base = PurePosixPath(key).name
            parent = str(PurePosixPath(key).parent)
            if base == ".zgroup":
                groups += 1
                nodes[parent] = "group-v2"
                malformed += int(value.get("zarr_format") != 2)
            elif base == ".zarray":
                arrays += 1
                nodes[parent] = "array-v2"
                shape, chunks = value.get("shape"), value.get("chunks")
                malformed += int(value.get("zarr_format") != 2 or not isinstance(shape, list) or
                                 not isinstance(chunks, list) or len(shape or []) != len(chunks or []) or
                                 any(not isinstance(n, int) or n < 0 for n in (shape or [])) or
                                 any(not isinstance(n, int) or n <= 0 for n in (chunks or [])) or
                                 not isinstance(value.get("dtype"), str))
            elif base == "zarr.json":
                node_type = value.get("node_type")
                if value.get("zarr_format") != 3 or node_type not in {"group", "array"}:
                    malformed += 1
                elif node_type == "group":
                    groups += 1
                    nodes[parent] = "group-v3"
                else:
                    arrays += 1
                    nodes[parent] = "array-v3"
                    shape = value.get("shape")
                    malformed += int(not isinstance(shape, list) or
                                     any(not isinstance(n, int) or n < 0 for n in (shape or [])) or
                                     not isinstance(value.get("data_type"), str))
            elif base == ".zattrs":
                malformed += int(not isinstance(value, dict))
        missing_parent_groups = 0
        for node_path in nodes:
            parts = [] if node_path in {"", "."} else node_path.split("/")
            for i in range(1, len(parts)):
                ancestor = "/".join(parts[:i])
                if ancestor not in nodes or not nodes[ancestor].startswith("group"):
                    missing_parent_groups += 1
        root_nodes = int("" in nodes or "." in nodes)
        versions = set()
        if any(name.endswith("/zarr.json") or name == "zarr.json" for name in parsed):
            versions.add("v3")
        if any(name.endswith(("/.zgroup", "/.zarray")) or name in {".zgroup", ".zarray"} for name in parsed):
            versions.add("v2")
        lines = [
            f"Zarr metadata versions detected: {', '.join(sorted(versions)) or 'unknown'}",
            f"Group metadata nodes: {groups:,}",
            f"Array metadata nodes: {arrays:,}",
            f"Root node metadata present: {bool(root_nodes)}",
            f"Metadata documents inspected: {len(parsed):,}",
            f"Malformed or inconsistent metadata records: {malformed:,}",
            f"Nodes with a missing/non-group ancestor: {missing_parent_groups:,}",
            f"ZIP members: {len(members):,}",
            f"Expanded archive bytes (chunks not read): {expanded:,}",
            "Array shapes and chunk payload values, attributes, paths and metadata contents are withheld.",
        ]
        return _report(path, "zarr", "Zarr v2/v3 store metadata audit", lines)
    finally:
        archive.close()


def nifti_header_audit(path: Path) -> dict:
    """Read only the fixed NIfTI-1/2 header, not voxel data."""
    _size_guard(path)
    try:
        if path.name.lower().endswith(".gz"):
            with gzip.open(path, "rb") as stream:
                header = stream.read(544)
        else:
            with path.open("rb") as stream:
                header = stream.read(544)
    except (OSError, EOFError) as exc:
        raise RuntimeError("NIfTI header could not be read; gzip stream may be damaged.") from exc
    if len(header) < 348:
        raise RuntimeError("NIfTI file is shorter than a NIfTI-1 header.")
    little = struct.unpack("<i", header[:4])[0]
    big = struct.unpack(">i", header[:4])[0]
    if little in {348, 540}:
        endian, header_size = "<", little
    elif big in {348, 540}:
        endian, header_size = ">", big
    else:
        raise RuntimeError("NIfTI sizeof_hdr is not 348 (NIfTI-1) or 540 (NIfTI-2).")
    if header_size == 348:
        if len(header) < 348:
            raise RuntimeError("NIfTI-1 header is truncated.")
        magic = header[344:348]
        if magic not in {b"n+1\x00", b"ni1\x00"}:
            raise RuntimeError("NIfTI-1 magic field is invalid.")
        rank = struct.unpack(endian + "h", header[40:42])[0]
        dims = struct.unpack(endian + "8h", header[40:56])[1:]
        datatype, bitpix = struct.unpack(endian + "2h", header[70:74])
        pixdim = struct.unpack(endian + "8f", header[76:108])[1:]
        format_name = "NIfTI-1"
    else:
        if len(header) < 540:
            raise RuntimeError("NIfTI-2 header is truncated.")
        magic = header[4:12]
        if magic not in {b"n+2\x00\r\n\x1a\n", b"ni2\x00\r\n\x1a\n"}:
            raise RuntimeError("NIfTI-2 magic field is invalid.")
        datatype, bitpix = struct.unpack(endian + "2h", header[12:16])
        rank = struct.unpack(endian + "q", header[16:24])[0]
        dims = struct.unpack(endian + "8q", header[16:80])[1:]
        pixdim = struct.unpack(endian + "8d", header[104:168])[1:]
        format_name = "NIfTI-2"
    if rank < 1 or rank > 7 or any(value <= 0 for value in dims[:rank]):
        raise RuntimeError("NIfTI dimensionality or active dimension sizes are invalid.")
    if bitpix <= 0 or bitpix % 8:
        raise RuntimeError("NIfTI bitpix must be a positive multiple of eight.")
    datatype_bits = {1: 1, 2: 8, 4: 16, 8: 32, 16: 32, 32: 64, 64: 64, 128: 24,
                     256: 8, 512: 16, 768: 32, 1024: 64, 1280: 64, 1536: 128,
                     1792: 128, 2048: 256, 2304: 32}
    expected_bits = datatype_bits.get(datatype)
    bitpix_mismatch = int(expected_bits is not None and expected_bits != bitpix)
    invalid_spacing = sum(1 for value in pixdim[:rank] if not math.isfinite(value) or value == 0)
    lines = [
        f"Header format: {format_name}",
        f"Byte order: {'little-endian' if endian == '<' else 'big-endian'}",
        f"Header size: {header_size:,} bytes",
        f"Dimensional rank valid: {1 <= rank <= 7}",
        f"Active dimension entries: {rank:,}",
        f"Voxel datatype code recognized: {expected_bits is not None}",
        f"Datatype/bitpix mismatch: {bitpix_mismatch:,}",
        f"Invalid or zero active voxel spacing values: {invalid_spacing:,}",
        "Dimensions, spacing values, affine transforms, intent parameters and voxel data are withheld.",
        "Header-only inspection: image voxels and extensions were not decoded.",
    ]
    return _report(path, "nifti", "NIfTI-1/2 header audit", lines)


def dicom_privacy_audit(path: Path) -> dict:
    """Count selected DICOM identifiers and private tags without printing values."""
    _size_guard(path)
    try:
        import pydicom
        from pydicom.tag import Tag
        dataset = pydicom.dcmread(path, stop_before_pixels=True, force=False)
    except ImportError as exc:
        raise RuntimeError("DICOM audit requires the pydicom runtime package.") from exc
    except Exception as exc:
        raise RuntimeError("DICOM file is malformed or not a supported Part 10 dataset.") from exc
    phi_tags = {
        Tag(0x00100010), Tag(0x00100020), Tag(0x00100030), Tag(0x00100032),
        Tag(0x00100040), Tag(0x00101000), Tag(0x00101001), Tag(0x00102154),
        Tag(0x00080050), Tag(0x00080080), Tag(0x00080090), Tag(0x00081010),
    }
    present_phi = sum(1 for tag in phi_tags if tag in dataset)
    private_elements = 0
    element_count = 0
    vr_counts = {}
    try:
        for element in dataset.iterall():
            element_count += 1
            if element_count > 100_000:
                raise RuntimeError("DICOM header exceeds the 100,000-element inspection limit.")
            if element.tag.is_private:
                private_elements += 1
            vr_counts[element.VR] = vr_counts.get(element.VR, 0) + 1
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError("DICOM dataset contains an unsupported nested element structure.") from exc
    lines = [
        "Read mode: header only; pixel data excluded",
        f"Top-level selected direct-identifier fields present: {present_phi:,} of {len(phi_tags):,}",
        f"Private elements detected in parsed dataset: {private_elements:,}",
        f"Header elements inspected: {element_count:,}",
        f"Value-representation categories: {len(vr_counts):,}",
        f"Patient-identifying fields may be present: {bool(present_phi or private_elements)}",
        "No DICOM element values, names, identifiers, dates, institution strings or pixel data are included.",
        "This is a limited metadata risk screen, not a complete DICOM de-identification, confidentiality or clinical validation.",
    ]
    return _report(path, "dicom", "DICOM header privacy risk screen", lines)


def las_pointcloud_audit(path: Path) -> dict:
    """Inspect LAS header metadata only; point records and coordinates are not read."""
    _size_guard(path)
    with path.open("rb") as stream:
        header = stream.read(375)
    if len(header) < 227 or header[:4] != b"LASF":
        raise RuntimeError("LAS file signature or minimum header is invalid.")
    major, minor = header[24], header[25]
    if major != 1 or minor > 4:
        raise RuntimeError("Only LAS 1.0 through 1.4 headers are supported.")
    header_size = struct.unpack_from("<H", header, 94)[0]
    point_offset = struct.unpack_from("<I", header, 96)[0]
    vlr_count = struct.unpack_from("<I", header, 100)[0]
    raw_format = header[104]
    point_format = raw_format & 0x3F
    compressed = bool(raw_format & 0xC0)
    record_length = struct.unpack_from("<H", header, 105)[0]
    legacy_count = struct.unpack_from("<I", header, 107)[0]
    minimum_lengths = {0: 20, 1: 28, 2: 26, 3: 34, 4: 57, 5: 63, 6: 30, 7: 36, 8: 38, 9: 59, 10: 67}
    if header_size < 227 or point_offset < header_size or point_offset > path.stat().st_size:
        raise RuntimeError("LAS header size or point-data offset is inconsistent.")
    extended_count = 0
    evlr_count = 0
    if minor >= 4:
        if header_size < 375 or len(header) < 375:
            raise RuntimeError("LAS 1.4 header is truncated.")
        evlr_count = struct.unpack_from("<I", header, 243)[0]
        extended_count = struct.unpack_from("<Q", header, 247)[0]
    point_count = extended_count if extended_count else legacy_count
    min_record = minimum_lengths.get(point_format)
    if min_record is None or record_length < min_record:
        raise RuntimeError("LAS point format or point record length is unsupported.")
    if compressed:
        raise RuntimeError("Compressed LAZ point data is not supported by this LAS header-only auditor.")
    data_end = point_offset + point_count * record_length
    if data_end > path.stat().st_size:
        raise RuntimeError("LAS point-record byte range extends beyond the file size.")
    lines = [
        f"LAS version: {major}.{minor}",
        f"Header size: {header_size:,} bytes",
        f"Point-data offset: valid",
        f"Variable-length record declarations: {vlr_count:,}",
        f"Extended variable-length record declarations: {evlr_count:,}",
        f"Point record format: {point_format}",
        f"Point record length: {record_length:,} bytes",
        f"Point count: {point_count:,}",
        "Point records, coordinates, offsets, bounds, CRS text and record payload values are not read or emitted.",
        "LAZ-compressed point data is not supported.",
    ]
    return _report(path, "las", "LAS 1.0-1.4 point-cloud header audit", lines)


def jp2_box_audit(path: Path) -> dict:
    """Validate outer JP2 box framing and jp2h/ihdr metadata without decoding pixels."""
    _size_guard(path)
    raw = path.read_bytes()
    if len(raw) < 12 or raw[4:8] != b"jP  " or raw[8:12] != b"\r\n\x87\n":
        raise RuntimeError("JPEG 2000 JP2 signature box is missing or invalid.")
    boxes = 0
    malformed = 0
    types = set()
    image_header = None

    def parse_boxes(data: bytes, nested: bool = False):
        nonlocal boxes, malformed, image_header
        offset = 0
        while offset < len(data):
            if len(data) - offset < 8:
                malformed += 1
                break
            length = struct.unpack_from(">I", data, offset)[0]
            kind = data[offset + 4:offset + 8]
            header_len = 8
            if length == 1:
                if len(data) - offset < 16:
                    malformed += 1
                    break
                length = struct.unpack_from(">Q", data, offset + 8)[0]
                header_len = 16
            elif length == 0:
                length = len(data) - offset
            if length < header_len or offset + length > len(data):
                malformed += 1
                break
            payload = data[offset + header_len:offset + length]
            boxes += 1
            if boxes > 100_000:
                raise RuntimeError("JP2 box count exceeds the 100,000-box limit.")
            label = kind.decode("ascii", errors="replace")
            types.add(label)
            if label == "jp2h":
                parse_boxes(payload, True)
            elif label == "ihdr" and nested:
                if len(payload) < 14:
                    malformed += 1
                else:
                    height, width, components = struct.unpack_from(">IIH", payload, 0)
                    image_header = (height, width, components)
            offset += length
        return offset

    parse_boxes(raw)
    required_missing = sum(1 for value in {"ftyp", "jp2h", "jp2c"} if value not in types)
    if image_header is None:
        malformed += 1
    elif any(value <= 0 for value in image_header):
        malformed += 1
    lines = [
        "JP2 signature box: valid",
        f"Top-level and jp2h box count: {boxes:,}",
        f"Distinct box types: {len(types):,}",
        f"Required ftyp/jp2h/jp2c boxes missing: {required_missing:,}",
        f"Image header present and dimensions positive: {image_header is not None and all(v > 0 for v in image_header)}",
        f"Malformed or out-of-bounds box records: {malformed:,}",
        "Image dimensions, component details, codestream bytes and pixel values are withheld.",
        "This checks JP2 box framing and basic image-header presence, not full JPEG 2000 codestream conformance or image decoding.",
    ]
    return _report(path, "jp2", "JPEG 2000 JP2 box-structure audit", lines)


def netcdf_classic_audit(path: Path) -> dict:
    """Inspect NetCDF classic CDF-1/CDF-2 headers; array payloads are not read."""
    _size_guard(path)
    raw = path.read_bytes()
    if len(raw) < 8 or raw[:3] != b"CDF":
        raise RuntimeError("NetCDF classic magic bytes are missing.")
    version = raw[3]
    if version not in {1, 2}:
        raise RuntimeError("This auditor supports NetCDF classic CDF-1 and CDF-2 only.")
    offset = 4
    def take(fmt: str):
        nonlocal offset
        size = struct.calcsize(">" + fmt)
        if offset + size > len(raw):
            raise RuntimeError("NetCDF header is truncated.")
        value = struct.unpack_from(">" + fmt, raw, offset)[0]
        offset += size
        return value
    def take_bytes(size: int):
        nonlocal offset
        if size < 0 or offset + size > len(raw):
            raise RuntimeError("NetCDF header field extends beyond the file.")
        value = raw[offset:offset + size]
        offset += size
        return value
    def padding(size: int):
        take_bytes((-size) % 4)
    def name():
        length = take("I")
        if length > 1_048_576:
            raise RuntimeError("NetCDF name exceeds the 1 MiB string limit.")
        value = take_bytes(length)
        padding(length)
        if b"\x00" in value:
            raise RuntimeError("NetCDF names must not contain NUL bytes.")
        return value.decode("utf-8", errors="replace")
    num_records = take("I")
    def list_header(expected_tag: int):
        tag, count = take("I"), take("I")
        if tag == 0 and count == 0:
            return 0
        if tag != expected_tag or count > 100_000:
            raise RuntimeError("NetCDF header list tag or entry count is invalid.")
        return count
    dim_count = list_header(10)
    dimension_ids = []
    for _ in range(dim_count):
        name()
        dimension_ids.append(take("I"))
    attr_count = list_header(12)
    type_sizes = {1: 1, 2: 1, 3: 2, 4: 4, 5: 4, 6: 8}
    def read_attributes(count):
        total = 0
        for _ in range(count):
            name()
            kind, elements = take("I"), take("I")
            if kind not in type_sizes or elements > 10_000_000:
                raise RuntimeError("NetCDF attribute type or element count is unsupported.")
            size = type_sizes[kind] * elements
            take_bytes(size)
            padding(size)
            total += 1
        return total
    global_attrs = read_attributes(attr_count)
    var_count = list_header(11)
    record_vars = invalid_var_dims = 0
    for _ in range(var_count):
        name()
        ndims = take("I")
        if ndims > dim_count:
            raise RuntimeError("NetCDF variable dimensionality exceeds the dimension table.")
        dims = [take("I") for _ in range(ndims)]
        invalid_var_dims += sum(1 for index in dims if index >= dim_count)
        attrs = list_header(12)
        read_attributes(attrs)
        kind = take("I")
        vsize = take("I")
        begin = take("I") if version == 1 else take("Q")
        if kind not in type_sizes or begin >= len(raw) or vsize > len(raw):
            raise RuntimeError("NetCDF variable descriptor contains unsupported type or offsets.")
        if dims and dims[0] < len(dimension_ids) and dimension_ids[dims[0]] == 0:
            record_vars += 1
    lines = [
        f"NetCDF classic version: CDF-{version}",
        f"Unlimited record count: {num_records:,}",
        f"Dimension entries: {dim_count:,}",
        f"Global attribute entries: {global_attrs:,}",
        f"Variable descriptors: {var_count:,}",
        f"Record variables: {record_vars:,}",
        f"Variable dimension references outside table: {invalid_var_dims:,}",
        f"Header bytes parsed: {offset:,}",
        "Dimension names, variable names, attribute names/values, offsets and array values are withheld.",
        "NetCDF-4/HDF5 and CDF-5 are not included in this classic-header audit.",
    ]
    return _report(path, "netcdf", "NetCDF classic CDF-1/CDF-2 header audit", lines)


def nwb_structure_audit(path: Path) -> dict:
    """Inspect NWB HDF5 hierarchy and dataset metadata without reading data arrays."""
    _size_guard(path)
    try:
        import h5py
        with h5py.File(path, "r") as root:
            attrs = root.attrs
            nwb_version = "nwb_version" in attrs
            namespaces = "namespaces" in attrs
            top_level = {name: isinstance(root.get(name, getlink=True), h5py.HardLink) and
                         isinstance(root.get(name), h5py.Group)
                         for name in ("acquisition", "analysis", "general", "processing", "stimulus", "intervals")}
            groups = datasets = attrs_total = external_links = 0
            stack = [(root, 0)]
            visited = set()
            while stack:
                group, depth = stack.pop()
                if depth > 64:
                    raise RuntimeError("NWB hierarchy exceeds the 64-level nesting limit.")
                address = h5py.h5o.get_info(group.id).addr
                if address in visited:
                    continue
                visited.add(address)
                for name in group.keys():
                    link = group.get(name, getlink=True)
                    if isinstance(link, (h5py.ExternalLink, h5py.SoftLink)):
                        external_links += 1
                        continue
                    obj = group.get(name)
                    attrs_total += len(obj.attrs)
                    if isinstance(obj, h5py.Group):
                        groups += 1
                        stack.append((obj, depth + 1))
                    elif isinstance(obj, h5py.Dataset):
                        datasets += 1
                    if groups + datasets > 100_000:
                        raise RuntimeError("NWB hierarchy exceeds the 100,000-object inspection limit.")
            lines = [
                f"HDF5 file opens successfully: True",
                f"NWB version attribute present: {nwb_version}",
                f"Namespaces attribute present: {namespaces}",
                f"Standard top-level acquisition/analysis/general groups present: {sum(top_level.values())} of {len(top_level)}",
                f"Groups inspected: {groups:,}",
                f"Datasets inspected (metadata only): {datasets:,}",
                f"Attributes counted (values not read): {attrs_total:,}",
                f"Soft/external links skipped: {external_links:,}",
                "Time-series, image, electrode, unit, acquisition and stimulus data values are never read.",
                "This is an HDF5 hierarchy screen, not full NWB schema validation or scientific-data validation.",
            ]
            return _report(path, "nwb", "NWB neurophysiology HDF5 structure audit", lines)
    except ImportError as exc:
        raise RuntimeError("NWB audit requires the h5py runtime package.") from exc
    except OSError as exc:
        raise RuntimeError("NWB input is not a readable HDF5 file.") from exc
