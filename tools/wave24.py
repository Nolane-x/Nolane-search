"""Wave 24 offline interoperability and creative-project inspectors.

All processors are bounded, read-only analyzers. They never execute embedded
workflows, open remote references, load image/audio payloads, or print user
content, coordinates, credentials, labels, or design-token values.
"""
from __future__ import annotations

import base64
import collections
import email
import gzip
import json
import mailbox
import re
import sqlite3
import struct
import urllib.parse
import zipfile
import zlib
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path


MAX_INPUT = 20 * 1024 * 1024
MAX_EXPANDED = 120 * 1024 * 1024
MAX_MEMBERS = 1_000
MAX_XML = 12 * 1024 * 1024


def _report(path: Path, slug: str, heading: str, lines: list[str]) -> dict:
    output = path.with_name(path.stem + "-" + slug + "-report.txt")
    body = heading + "\n\n" + "\n".join(lines) + "\n"
    output.write_text(body, encoding="utf-8")
    return {"summary": body[:5_500], "output_path": str(output)}


def _read(path: Path, limit: int = MAX_INPUT) -> bytes:
    if path.stat().st_size > limit:
        raise RuntimeError("Wave 24 input exceeds its format size limit.")
    return path.read_bytes()


def _safe_zip(path: Path, max_expanded: int = MAX_EXPANDED):
    if path.stat().st_size > MAX_INPUT:
        raise RuntimeError("Archive exceeds the 20 MiB compressed input limit.")
    archive = zipfile.ZipFile(path)
    members = archive.infolist()
    if len(members) > MAX_MEMBERS:
        archive.close()
        raise RuntimeError("Archive contains too many members.")
    expanded = 0
    names = set()
    for item in members:
        name = item.filename.replace("\\", "/")
        mode = (item.external_attr >> 16) & 0xFFFF
        if name.startswith("/") or re.match(r"^[A-Za-z]:", name) or ".." in name.split("/"):
            archive.close()
            raise RuntimeError("Archive contains an unsafe path.")
        if (mode & 0o170000) == 0o120000 or item.flag_bits & 1:
            archive.close()
            raise RuntimeError("Archive contains a symlink or encrypted member.")
        if name in names:
            archive.close()
            raise RuntimeError("Archive contains duplicate member paths.")
        names.add(name)
        expanded += item.file_size
        if expanded > max_expanded:
            archive.close()
            raise RuntimeError("Archive exceeds the expanded-size limit.")
    return archive, members, names, expanded


def _xml(data: bytes, label: str):
    if len(data) > MAX_XML:
        raise RuntimeError(f"{label} XML exceeds its size limit.")
    upper = data.upper()
    if b"<!DOCTYPE" in upper or b"<!ENTITY" in upper:
        raise RuntimeError(f"{label} XML DTD/entity declarations are not allowed.")
    try:
        return ET.fromstring(data)
    except ET.ParseError as exc:
        raise RuntimeError(f"{label} XML is malformed.") from exc


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].split(":", 1)[-1].lower()


def _sqlite_readonly(path: Path):
    if path.stat().st_size > MAX_INPUT:
        raise RuntimeError("SQLite database exceeds the 20 MiB input limit.")
    uri = path.resolve().as_uri() + "?mode=ro&immutable=1"
    try:
        connection = sqlite3.connect(uri, uri=True, timeout=5)
        connection.execute("PRAGMA query_only=ON")
        return connection
    except sqlite3.Error as exc:
        raise RuntimeError("SQLite file could not be opened read-only.") from exc


def _quoted_identifier(value: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 256:
        raise RuntimeError("Database contains an invalid table identifier.")
    return '"' + value.replace('"', '""') + '"'


def odf_package_audit(path: Path) -> dict:
    archive, members, names, expanded = _safe_zip(path)
    try:
        if not members or members[0].filename != "mimetype":
            raise RuntimeError("OpenDocument package must put mimetype first.")
        mime_info = members[0]
        if mime_info.compress_type != zipfile.ZIP_STORED:
            raise RuntimeError("OpenDocument mimetype member must be stored without compression.")
        mime = archive.read("mimetype").decode("ascii", "strict").strip()
        mime_map = {
            "application/vnd.oasis.opendocument.text": "text",
            "application/vnd.oasis.opendocument.spreadsheet": "spreadsheet",
            "application/vnd.oasis.opendocument.presentation": "presentation",
            "application/vnd.oasis.opendocument.graphics": "drawing",
            "application/vnd.oasis.opendocument.formula": "formula",
            "application/vnd.oasis.opendocument.chart": "chart",
        }
        document_kind = mime_map.get(mime, "unknown/other")
        manifest_name = "META-INF/manifest.xml"
        if manifest_name not in names:
            raise RuntimeError("OpenDocument package is missing META-INF/manifest.xml.")
        manifest = _xml(archive.read(manifest_name), "ODF manifest")
        manifest_mimes = []
        encrypted_entries = 0
        manifest_paths = set()
        for element in manifest.iter():
            if _local(element.tag) == "file-entry":
                attrs = {key.rsplit("}", 1)[-1].lower(): value for key, value in element.attrib.items()}
                full_path = attrs.get("full-path")
                media_type = attrs.get("media-type")
                if full_path:
                    manifest_paths.add(full_path)
                if full_path == "/" and media_type:
                    manifest_mimes.append(media_type)
            if _local(element.tag) == "encryption-data":
                encrypted_entries += 1
        root_mime_matches = int(bool(manifest_mimes and manifest_mimes[0] == mime))
        xml_metrics = collections.Counter()
        external_refs = script_parts = embedded_objects = 0
        for xml_name in ("content.xml", "styles.xml", "meta.xml", "settings.xml"):
            if xml_name not in names:
                continue
            data = archive.read(xml_name)
            root = _xml(data, f"ODF {xml_name}")
            for element in root.iter():
                tag = _local(element.tag)
                if tag in {"p", "h", "table", "table-row", "table-cell", "page", "draw-page"}:
                    xml_metrics[tag] += 1
                for key, value in element.attrib.items():
                    local_key = key.rsplit("}", 1)[-1].lower()
                    if local_key in {"href", "link"} and re.match(r"(?i)^(?:https?:|ftp:|file:|data:|javascript:)", value):
                        external_refs += 1
        for name in names:
            normalized = name.lower()
            if normalized.startswith(("scripts/", "basic/")) or "/scripts/" in normalized:
                script_parts += 1
            if normalized.startswith(("objects/", "embeddings/")) or "/embeddings/" in normalized:
                embedded_objects += 1
        unmanifested = sum(
            1 for name in names
            if name not in {"mimetype", manifest_name}
            and not name.startswith("META-INF/")
            and not name.endswith("/")
            and name not in manifest_paths
        )
        lines = [
            f"Container: ZIP / OpenDocument package",
            f"Document kind: {document_kind}",
            f"Package MIME matches root manifest entry: {bool(root_mime_matches)}",
            f"ZIP members: {len(members):,}",
            f"Expanded bytes: {expanded:,}",
            f"Manifest file entries: {len(manifest_paths):,}",
            f"Encrypted manifest entries: {encrypted_entries:,}",
            f"Unmanifested package members: {unmanifested:,}",
            f"External link references: {external_refs:,}",
            f"Script/macro-related package paths: {script_parts:,}",
            f"Embedded object package paths: {embedded_objects:,}",
            "Content structure counts (text and names withheld):",
        ]
        lines.extend(f"  {key}: {value:,}" for key, value in sorted(xml_metrics.items()))
        lines.append("Document text, metadata values, URLs, object names and author fields are not included.")
        return _report(path, "odf", "OpenDocument package audit", lines)
    except (UnicodeError, zipfile.BadZipFile) as exc:
        raise RuntimeError("OpenDocument package is invalid or has unsupported encoding.") from exc
    finally:
        archive.close()


def xliff_audit(path: Path) -> dict:
    data = _read(path, 10 * 1024 * 1024)
    root = _xml(data, "XLIFF")
    if _local(root.tag) != "xliff":
        raise RuntimeError("Root element is not XLIFF.")
    units = segments = sources = targets = empty_targets = same_source_target = 0
    placeholder_mismatches = missing_sources = approved = initial = 0
    states = collections.Counter()
    def text_of(element):
        return "".join(element.itertext()) if element is not None else ""
    def placeholders(element):
        value = text_of(element)
        regex_count = len(re.findall(r"%(?:\d+\$)?[sdif]|\{[A-Za-z_][\w.-]*\}|\{\{[A-Za-z_][\w.-]*\}\}", value))
        structural = sum(1 for node in element.iter() if _local(node.tag) in {"ph", "pc", "bpt", "ept", "it", "sc", "ec"})
        return regex_count + structural
    for element in root.iter():
        tag = _local(element.tag)
        if tag in {"trans-unit", "unit"}:
            units += 1
        if tag in {"trans-unit", "segment", "ignorable"}:
            segments += int(tag != "ignorable")
            children = {_local(child.tag): child for child in list(element)}
            source = children.get("source")
            target = children.get("target")
            if source is None:
                missing_sources += 1
            else:
                sources += 1
            if target is not None:
                targets += 1
                if not text_of(target).strip() and not list(target):
                    empty_targets += 1
            elif source is not None:
                empty_targets += 1
            if source is not None and target is not None:
                if text_of(source).strip() == text_of(target).strip():
                    same_source_target += 1
                if text_of(target).strip() and placeholders(source) != placeholders(target):
                    placeholder_mismatches += 1
            attrs = {key.rsplit("}", 1)[-1].lower(): value.lower() for key, value in element.attrib.items()}
            state = attrs.get("state") or attrs.get("approved") or "unspecified"
            states[state] += 1
            approved += state in {"final", "translated", "reviewed", "yes", "approved"}
            initial += state in {"initial", "needs-translation", "new", "unspecified"}
    if not units and not segments:
        raise RuntimeError("XLIFF contains no translation units or segments.")
    lines = [
        f"XLIFF version: {root.attrib.get('version', 'unspecified')}",
        f"Translation units: {units:,}",
        f"Segments/translation units reviewed: {segments:,}",
        f"Units with source element: {sources:,}",
        f"Units with target element: {targets:,}",
        f"Missing or empty targets: {empty_targets:,}",
        f"Source/target text-identical candidates: {same_source_target:,}",
        f"Missing source elements: {missing_sources:,}",
        f"Placeholder-count mismatches: {placeholder_mismatches:,}",
        f"Approved/advanced-state units: {approved:,}",
        f"Initial/unspecified-state units: {initial:,}",
        "Translation state counts: " + (", ".join(f"{key}={value}" for key, value in states.most_common(12)) or "none"),
        "Source text, translations, file names, language codes and unit identifiers are withheld.",
    ]
    return _report(path, "xliff", "XLIFF translation package audit", lines)


def mbox_audit(path: Path) -> dict:
    if path.stat().st_size > MAX_INPUT:
        raise RuntimeError("MBOX file exceeds 20 MiB.")
    box = mailbox.mbox(str(path), create=False)
    total = multipart = attachments = inline_parts = empty_messages = 0
    header_presence = collections.Counter()
    top_types = collections.Counter()
    parts_total = malformed_dates = invalid_messages = 0
    date_count = 0
    try:
        for index, message in enumerate(box):
            if index >= 20_000:
                raise RuntimeError("MBOX exceeds the 20,000-message limit.")
            if not isinstance(message, email.message.Message):
                invalid_messages += 1
                continue
            total += 1
            for header in ("from", "to", "cc", "bcc", "reply-to", "subject", "date", "message-id"):
                header_presence[header] += int(message.get(header) is not None)
            top_types[message.get_content_type().lower()] += 1
            payload = message.get_payload()
            if not payload:
                empty_messages += 1
            is_multi = message.is_multipart()
            multipart += is_multi
            try:
                if message.get("Date"):
                    parsedate_to_datetime(message.get("Date"))
                    date_count += 1
            except Exception:
                malformed_dates += 1
            for part in message.walk():
                parts_total += 1
                if parts_total > 100_000:
                    raise RuntimeError("MBOX MIME part count exceeds 100,000.")
                disposition = (part.get("Content-Disposition") or "").lower()
                filename = part.get_filename()
                if "attachment" in disposition or filename:
                    attachments += 1
                elif "inline" in disposition:
                    inline_parts += 1
    finally:
        box.close()
    lines = [
        f"Messages: {total:,}",
        f"Multipart messages: {multipart:,}",
        f"Messages without payload: {empty_messages:,}",
        f"MIME parts inspected: {parts_total:,}",
        f"Attachment parts: {attachments:,}",
        f"Inline MIME parts: {inline_parts:,}",
        f"Messages with parseable Date header: {date_count:,}",
        f"Malformed Date headers: {malformed_dates:,}",
        f"Invalid message objects skipped: {invalid_messages:,}",
        "Header presence counts:",
    ]
    lines.extend(f"  {key}: {value:,}" for key, value in sorted(header_presence.items()))
    lines.append("Top-level MIME types: " + (", ".join(f"{key}={value}" for key, value in top_types.most_common(10)) or "none"))
    lines.append("Email addresses, names, subjects, dates, body text, attachment names and attachment bytes are never reported.")
    return _report(path, "mbox", "MBOX privacy and structure audit", lines)


def geopackage_audit(path: Path) -> dict:
    conn = _sqlite_readonly(path)
    try:
        app_id = conn.execute("PRAGMA application_id").fetchone()[0]
        user_version = conn.execute("PRAGMA user_version").fetchone()[0]
        if app_id not in (0, 0x47504B47):
            raise RuntimeError("SQLite application_id is not a GeoPackage magic number.")
        tables = {row[0].lower() for row in conn.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view')")}
        required = {"gpkg_contents", "gpkg_spatial_ref_sys"}
        missing = required - tables
        if missing:
            raise RuntimeError("GeoPackage required metadata tables are missing.")
        content_rows = conn.execute("SELECT data_type, COUNT(*) FROM gpkg_contents GROUP BY data_type").fetchall()
        geometry_rows = conn.execute("SELECT geometry_type_name, COUNT(*) FROM gpkg_geometry_columns GROUP BY geometry_type_name").fetchall() if "gpkg_geometry_columns" in tables else []
        feature_tables = conn.execute("SELECT table_name FROM gpkg_contents WHERE data_type='features' LIMIT 500").fetchall()
        actual_tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        row_count = missing_tables = 0
        for row in feature_tables:
            name = row[0]
            if name not in actual_tables:
                missing_tables += 1
                continue
            row_count += conn.execute(f"SELECT COUNT(*) FROM {_quoted_identifier(name)}").fetchone()[0]
        crs_count = conn.execute("SELECT COUNT(*) FROM gpkg_spatial_ref_sys").fetchone()[0]
        quick = conn.execute("PRAGMA quick_check(1)").fetchone()[0]
        lines = [
            "SQLite application_id matches GeoPackage magic: " + str(app_id == 0x47504B47),
            f"SQLite user_version: {user_version}",
            f"Database tables/views: {len(tables):,}",
            f"Spatial reference systems: {crs_count:,}",
            f"Feature table entries: {len(feature_tables):,}",
            f"Feature rows (count only): {row_count:,}",
            f"Feature metadata entries referencing missing tables: {missing_tables:,}",
            f"Content categories: " + (", ".join(f"{key}={value}" for key, value in content_rows) or "none"),
            f"Geometry type categories: " + (", ".join(f"{key}={value}" for key, value in geometry_rows) or "none"),
            f"SQLite quick_check: {quick}",
            "Table names, CRS identifiers/names, feature attributes, geometry, bounds and metadata values are withheld.",
        ]
    except sqlite3.Error as exc:
        raise RuntimeError("GeoPackage SQLite metadata could not be inspected.") from exc
    finally:
        conn.close()
    return _report(path, "gpkg", "GeoPackage metadata audit", lines)


def mbtiles_audit(path: Path) -> dict:
    conn = _sqlite_readonly(path)
    try:
        tables = {row[0].lower() for row in conn.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view')")}
        if "metadata" not in tables or "tiles" not in tables:
            raise RuntimeError("MBTiles must expose metadata and tiles tables/views.")
        metadata_cols = {row[1].lower() for row in conn.execute("PRAGMA table_info(metadata)")}
        tile_cols = {row[1].lower() for row in conn.execute("PRAGMA table_info(tiles)")}
        missing_meta_cols = {"name", "value"} - metadata_cols
        missing_tile_cols = {"zoom_level", "tile_column", "tile_row", "tile_data"} - tile_cols
        if missing_meta_cols or missing_tile_cols:
            raise RuntimeError("MBTiles metadata/tiles table schema is incomplete.")
        metadata = dict(conn.execute("SELECT name,value FROM metadata WHERE name IN ('format','minzoom','maxzoom','type','version')"))
        format_value = str(metadata.get("format", "unspecified")).lower()
        tile_count = conn.execute("SELECT COUNT(*) FROM tiles").fetchone()[0]
        zooms = conn.execute("SELECT COUNT(DISTINCT zoom_level), MIN(zoom_level), MAX(zoom_level) FROM tiles").fetchone()
        duplicate_coords = conn.execute(
            "SELECT COUNT(*) FROM (SELECT 1 FROM tiles GROUP BY zoom_level,tile_column,tile_row HAVING COUNT(*)>1)"
        ).fetchone()[0]
        invalid_coords = conn.execute(
            "SELECT COUNT(*) FROM tiles WHERE zoom_level<0 OR zoom_level>30 OR tile_column<0 OR tile_row<0 OR tile_column >= (1 << zoom_level) OR tile_row >= (1 << zoom_level)"
        ).fetchone()[0]
        invalid_zoom_order = 0
        try:
            minzoom = int(metadata.get("minzoom"))
            maxzoom = int(metadata.get("maxzoom"))
            invalid_zoom_order = int(minzoom > maxzoom)
        except (TypeError, ValueError):
            pass
        lines = [
            f"SQLite tables/views: {len(tables):,}",
            f"Tile rows: {tile_count:,}",
            f"Distinct zoom levels: {zooms[0] or 0:,}",
            f"Tile zoom range: {zooms[1] if zooms[1] is not None else 'none'} to {zooms[2] if zooms[2] is not None else 'none'}",
            f"Declared format: {format_value if format_value in {'pbf','png','jpg','jpeg','webp'} else 'other/unspecified'}",
            f"Duplicate tile-coordinate groups: {duplicate_coords:,}",
            f"Tile coordinates outside zoom-level range: {invalid_coords:,}",
            f"Declared minzoom/maxzoom order issue: {invalid_zoom_order:,}",
            f"Metadata key/value rows: {conn.execute('SELECT COUNT(*) FROM metadata').fetchone()[0]:,}",
            "Tile imagery/vector payloads, names, bounds, attribution, metadata values and feature attributes are never read or reported.",
        ]
    except sqlite3.Error as exc:
        raise RuntimeError("MBTiles SQLite metadata could not be inspected.") from exc
    finally:
        conn.close()
    return _report(path, "mbtiles", "MBTiles tileset audit", lines)


def openraster_audit(path: Path) -> dict:
    archive, members, names, expanded = _safe_zip(path, max_expanded=150 * 1024 * 1024)
    try:
        if not members or members[0].filename != "mimetype":
            raise RuntimeError("OpenRaster requires the mimetype member first.")
        if members[0].compress_type != zipfile.ZIP_STORED:
            raise RuntimeError("OpenRaster mimetype member must be uncompressed.")
        mime = archive.read("mimetype").decode("ascii", "strict")
        if mime != "image/openraster":
            raise RuntimeError("OpenRaster mimetype value is invalid.")
        if "stack.xml" not in names:
            raise RuntimeError("OpenRaster stack.xml is missing.")
        root = _xml(archive.read("stack.xml"), "OpenRaster stack")
        if _local(root.tag) != "image":
            raise RuntimeError("OpenRaster stack root must be image.")
        layers = groups = hidden = locked = external = missing_sources = 0
        compositing = collections.Counter()
        for element in root.iter():
            tag = _local(element.tag)
            if tag == "layer":
                layers += 1
                visibility = element.attrib.get("visibility", "visible").lower()
                hidden += visibility == "hidden"
                locked += element.attrib.get("edit-locked", "false").lower() in {"true", "1"}
                composite = element.attrib.get("composite-op", "svg:src-over")
                compositing[composite] += 1
                src = element.attrib.get("src", "")
                if src:
                    parsed_src = urllib.parse.urlsplit(src)
                    normalized_src = src.replace("\\", "/")
                    if parsed_src.scheme or parsed_src.netloc or src.startswith(("/", "\\")) or ".." in normalized_src.split("/"):
                        external += 1
                    elif src not in names:
                        missing_sources += 1
            elif tag == "stack":
                groups += 1
        thumbnail = int("Thumbnails/thumbnail.png" in names)
        merged = int("mergedimage.png" in names)
        width = root.attrib.get("w", "unspecified")
        height = root.attrib.get("h", "unspecified")
        lines = [
            f"Canvas dimensions: {width} × {height}",
            f"ZIP members: {len(members):,}",
            f"Expanded bytes: {expanded:,}",
            f"Layer entries: {layers:,}",
            f"Layer stack/group entries: {groups:,}",
            f"Hidden layers: {hidden:,}",
            f"Edit-locked layers: {locked:,}",
            f"Missing layer source members: {missing_sources:,}",
            f"Unsafe layer source paths: {external:,}",
            f"Thumbnail present: {bool(thumbnail)}",
            f"Merged preview present: {bool(merged)}",
            "Compositing modes: " + (", ".join(f"{key}={value}" for key, value in compositing.most_common(12)) or "none"),
            "Layer names, file paths, image pixels, metadata and artwork content are withheld.",
        ]
        return _report(path, "ora", "OpenRaster layered-image audit", lines)
    except (UnicodeError, zipfile.BadZipFile) as exc:
        raise RuntimeError("OpenRaster archive is invalid.") from exc
    finally:
        archive.close()


def krita_project_audit(path: Path) -> dict:
    archive, members, names, expanded = _safe_zip(path, max_expanded=180 * 1024 * 1024)
    try:
        if "maindoc.xml" not in names:
            raise RuntimeError("Krita project is missing maindoc.xml.")
        root = _xml(archive.read("maindoc.xml"), "Krita project")
        images = [node for node in root.iter() if _local(node.tag) == "image"]
        image = images[0] if images else root
        nodes = [node for node in root.iter() if _local(node.tag) in {"node", "layer"}]
        node_types = collections.Counter()
        hidden = locked = selected = 0
        for node in nodes:
            attrs = {key.rsplit("}", 1)[-1].lower(): value for key, value in node.attrib.items()}
            node_types[attrs.get("nodetype", attrs.get("type", "unspecified")).lower()] += 1
            hidden += attrs.get("visible", "1").lower() in {"0", "false", "no"}
            locked += attrs.get("locked", "0").lower() in {"1", "true", "yes"}
            selected += attrs.get("selected", "0").lower() in {"1", "true", "yes"}
        root_attrs = {key.rsplit("}", 1)[-1].lower(): value for key, value in image.attrib.items()}
        preview = int(any(name.lower().endswith("mergedimage.png") or name.lower().endswith("preview.png") for name in names))
        lines = [
            f"Container: Krita KRA ZIP",
            f"Canvas width: {root_attrs.get('width', 'unspecified')}",
            f"Canvas height: {root_attrs.get('height', 'unspecified')}",
            f"Color model: {root_attrs.get('colorspacename', root_attrs.get('colormodel', 'unspecified'))}",
            f"Color depth: {root_attrs.get('colordepth', 'unspecified')}",
            f"Layer/node entries: {len(nodes):,}",
            f"Hidden nodes: {hidden:,}",
            f"Locked nodes: {locked:,}",
            f"Selected nodes: {selected:,}",
            f"Preview/merged image present: {bool(preview)}",
            "Node types: " + (", ".join(f"{key}={value}" for key, value in node_types.most_common(16)) or "none"),
            f"ZIP members: {len(members):,}",
            f"Expanded bytes: {expanded:,}",
            "Layer names, resource paths, pixel data and artwork content are withheld.",
        ]
        return _report(path, "kra", "Krita project structure audit", lines)
    except zipfile.BadZipFile as exc:
        raise RuntimeError("Krita project ZIP is invalid.") from exc
    finally:
        archive.close()


def gltf_audit(path: Path) -> dict:
    raw = _read(path)
    binary_chunks = 0
    if path.suffix.lower() == ".glb":
        if len(raw) < 20:
            raise RuntimeError("GLB file is truncated.")
        magic, version, declared_length = struct.unpack_from("<4sII", raw, 0)
        if magic != b"glTF" or version != 2 or declared_length != len(raw):
            raise RuntimeError("GLB header magic, version or total length is invalid.")
        offset = 12
        json_chunk = None
        seen_bin = False
        while offset < len(raw):
            if offset + 8 > len(raw):
                raise RuntimeError("GLB chunk header is truncated.")
            size, chunk_type = struct.unpack_from("<II", raw, offset)
            offset += 8
            if size % 4 or offset + size > len(raw):
                raise RuntimeError("GLB chunk length/alignment is invalid.")
            chunk = raw[offset:offset + size]
            offset += size
            if chunk_type == 0x4E4F534A and json_chunk is None:
                json_chunk = chunk
            elif chunk_type == 0x004E4942:
                binary_chunks += 1
                if binary_chunks > 1 or json_chunk is None:
                    raise RuntimeError("GLB contains duplicate or out-of-order BIN chunks.")
                seen_bin = True
            else:
                raise RuntimeError("GLB contains an unexpected or out-of-order chunk.")
        if json_chunk is None:
            raise RuntimeError("GLB requires a JSON chunk.")
        try:
            document = json.loads(json_chunk.decode("utf-8").rstrip(" \t\r\n\0"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise RuntimeError("GLB JSON chunk is malformed.") from exc
    else:
        try:
            document = json.loads(raw.decode("utf-8-sig"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise RuntimeError("glTF JSON is malformed.") from exc
    if not isinstance(document, dict):
        raise RuntimeError("glTF root must be a JSON object.")
    asset = document.get("asset", {}) if isinstance(document.get("asset"), dict) else {}
    arrays = ("scenes", "nodes", "meshes", "materials", "textures", "images", "buffers", "bufferViews", "accessors", "animations", "skins", "cameras")
    counts = {key: len(document.get(key, [])) if isinstance(document.get(key), list) else 0 for key in arrays}
    external = data_uris = unsafe = missing_uri = 0
    def inspect_uri(item):
        nonlocal external, data_uris, unsafe
        uri = item.get("uri")
        if not isinstance(uri, str):
            return
        parsed = urllib.parse.urlsplit(uri)
        if parsed.scheme.lower() == "data":
            data_uris += 1
        elif uri and not uri.startswith("#"):
            external += 1
        if ".." in uri.replace("\\", "/").split("/") or "\0" in uri:
            unsafe += 1
    buffers = document.get("buffers", []) if isinstance(document.get("buffers"), list) else []
    for item in buffers:
        if not isinstance(item, dict):
            missing_uri += 1
        elif "uri" in item:
            inspect_uri(item)
        elif binary_chunks == 0:
            missing_uri += 1
    images = document.get("images", []) if isinstance(document.get("images"), list) else []
    for item in images:
        if not isinstance(item, dict):
            continue
        if "uri" in item:
            inspect_uri(item)
        elif "bufferView" not in item:
            missing_uri += 1
    ext_used = document.get("extensionsUsed", []) if isinstance(document.get("extensionsUsed"), list) else []
    ext_required = document.get("extensionsRequired", []) if isinstance(document.get("extensionsRequired"), list) else []
    lines = [
        f"Asset version: {asset.get('version', 'unspecified')}",
        f"Generator field present: {bool(asset.get('generator'))}",
        f"GLB binary chunks: {binary_chunks:,}",
    ]
    lines.extend(f"{key}: {value:,}" for key, value in counts.items())
    lines.extend([
        f"Used extension identifiers: {len(ext_used):,}",
        f"Required extension identifiers: {len(ext_required):,}",
        f"Embedded data URIs: {data_uris:,}",
        f"External resource URIs (not fetched): {external:,}",
        f"Missing resource URI/bufferView references: {missing_uri:,}",
        f"Unsafe resource URI paths: {unsafe:,}",
        "Scene/node/material names, resource paths, metadata values and geometry contents are withheld; external assets are never fetched.",
    ])
    return _report(path, "gltf", "glTF asset structure audit", lines)


def drawio_audit(path: Path) -> dict:
    raw = _read(path)
    if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
        raise RuntimeError("draw.io XML DTD/entity declarations are not allowed.")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise RuntimeError("draw.io XML is malformed.") from exc
    if _local(root.tag) not in {"mxfile", "mxgraphmodel"}:
        raise RuntimeError("Root element is not mxfile or mxGraphModel.")
    models = []
    compressed_errors = 0
    if _local(root.tag) == "mxgraphmodel":
        models = [root]
    else:
        for diagram in [node for node in root.iter() if _local(node.tag) == "diagram"]:
            model = next((child for child in list(diagram) if _local(child.tag) == "mxgraphmodel"), None)
            if model is None:
                payload = (diagram.text or "").strip()
                if not payload:
                    compressed_errors += 1
                    continue
                try:
                    packed = base64.b64decode(payload, validate=True)
                    inflater = zlib.decompressobj(-15)
                    decoded = inflater.decompress(packed, MAX_XML + 1)
                    if len(decoded) > MAX_XML or inflater.unconsumed_tail:
                        raise ValueError("compressed diagram exceeds limit")
                    decoded += inflater.flush()
                    if len(decoded) > MAX_XML:
                        raise ValueError("compressed diagram exceeds limit")
                    xml_text = urllib.parse.unquote(decoded.decode("utf-8"))
                    model = _xml(xml_text.encode("utf-8"), "draw.io compressed diagram")
                except Exception:
                    compressed_errors += 1
                    continue
            models.append(model)
    if not models:
        raise RuntimeError("draw.io file contains no readable diagram page.")
    cells = vertices = edges = dangling = duplicate_ids = 0
    ids = set()
    for model in models:
        page_ids = set()
        for element in model.iter():
            if _local(element.tag) != "mxcell":
                continue
            cells += 1
            attrs = {key.lower(): value for key, value in element.attrib.items()}
            cell_id = attrs.get("id")
            if cell_id:
                if cell_id in page_ids:
                    duplicate_ids += 1
                page_ids.add(cell_id)
                ids.add(cell_id)
            vertices += attrs.get("vertex", "0") == "1"
            edges += attrs.get("edge", "0") == "1"
        for element in model.iter():
            if _local(element.tag) != "mxcell":
                continue
            attrs = {key.lower(): value for key, value in element.attrib.items()}
            for ref in ("parent", "source", "target"):
                if attrs.get(ref) and attrs[ref] not in page_ids and attrs[ref] not in {"0", "1"}:
                    dangling += 1
    lines = [
        f"Diagram pages decoded: {len(models):,}",
        f"mxCell entries: {cells:,}",
        f"Vertex cells: {vertices:,}",
        f"Edge cells: {edges:,}",
        f"Repeated cell IDs within a page: {duplicate_ids:,}",
        f"Missing parent/source/target references: {dangling:,}",
        f"Unreadable compressed pages: {compressed_errors:,}",
        "Diagram labels, page names, URLs, styles and business content are withheld.",
    ]
    return _report(path, "drawio", "draw.io diagram structure audit", lines)


def n8n_workflow_audit(path: Path) -> dict:
    raw = _read(path, 10 * 1024 * 1024)
    try:
        document = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("n8n workflow JSON is malformed.") from exc
    if not isinstance(document, dict) or not isinstance(document.get("nodes"), list):
        raise RuntimeError("n8n export must contain a nodes array.")
    nodes = document["nodes"]
    if len(nodes) > 20_000:
        raise RuntimeError("n8n workflow contains too many nodes.")
    names = set()
    ids = set()
    missing_identity = duplicate_names = duplicate_ids = disabled = credential_nodes = 0
    risky = collections.Counter()
    hardcoded_secret_fields = 0
    type_counts = collections.Counter()
    for node in nodes:
        if not isinstance(node, dict):
            missing_identity += 1
            continue
        name = node.get("name")
        node_id = node.get("id")
        node_type = str(node.get("type", "")).strip()
        if not name or not node_type:
            missing_identity += 1
        if name:
            duplicate_names += int(name in names)
            names.add(name)
        if node_id:
            duplicate_ids += int(node_id in ids)
            ids.add(node_id)
        type_counts[node_type.rsplit(".", 1)[-1] or "unspecified"] += 1
        disabled += node.get("disabled") is True
        credentials = node.get("credentials")
        credential_nodes += isinstance(credentials, dict) and bool(credentials)
        short_type = node_type.lower()
        for marker in ("webhook", "httprequest", "code", "executecommand", "ssh", "readwritefile", "database"):
            if marker in short_type:
                risky[marker] += 1
        params = node.get("parameters")
        stack = [params] if isinstance(params, (dict, list)) else []
        visited = 0
        while stack:
            value = stack.pop()
            visited += 1
            if visited > 50_000:
                raise RuntimeError("n8n node parameters exceed the safety scan limit.")
            if isinstance(value, dict):
                for key, item in value.items():
                    if str(key).lower() in {"password", "apikey", "api_key", "authorization", "accesstoken", "access_token", "clientsecret", "client_secret", "token"} and isinstance(item, str) and item.strip():
                        hardcoded_secret_fields += 1
                    if isinstance(item, (dict, list)):
                        stack.append(item)
            elif isinstance(value, list):
                stack.extend(item for item in value if isinstance(item, (dict, list)))
    connection_count = dangling = 0
    connections = document.get("connections", {})
    if isinstance(connections, dict):
        for source, groups in connections.items():
            if source not in names:
                dangling += 1
            if not isinstance(groups, dict):
                continue
            for outputs in groups.values():
                if not isinstance(outputs, list):
                    continue
                for branch in outputs:
                    if not isinstance(branch, list):
                        continue
                    for edge in branch:
                        if isinstance(edge, dict):
                            connection_count += 1
                            if edge.get("node") not in names:
                                dangling += 1
    lines = [
        f"Workflow node count: {len(nodes):,}",
        f"Connection edges: {connection_count:,}",
        f"Nodes with missing name/type: {missing_identity:,}",
        f"Duplicate node names: {duplicate_names:,}",
        f"Duplicate node IDs: {duplicate_ids:,}",
        f"Disabled nodes: {disabled:,}",
        f"Nodes referencing credentials objects: {credential_nodes:,}",
        f"Potential hardcoded-secret fields (values withheld): {hardcoded_secret_fields:,}",
        f"Dangling connection references: {dangling:,}",
        "Execution-sensitive node category counts: " + (", ".join(f"{key}={value}" for key, value in sorted(risky.items())) or "none"),
        "Common node-type categories: " + (", ".join(f"{key}={value}" for key, value in type_counts.most_common(15)) or "none"),
        "Workflow, credential, expression and parameter values are never executed or included in this report.",
    ]
    return _report(path, "n8n", "n8n workflow static audit", lines)


def design_token_audit(path: Path) -> dict:
    raw = _read(path, 10 * 1024 * 1024)
    try:
        document = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Design Tokens JSON is malformed.") from exc
    if not isinstance(document, dict):
        raise RuntimeError("Design Tokens document root must be a JSON object.")
    tokens = {}
    groups = 0
    invalid_structures = name_issues = untyped = empty_values = 0
    alias_edges = collections.defaultdict(set)
    direct_refs = 0
    def inspect_value(value, source_path):
        nonlocal direct_refs
        found = set()
        stack = [value]
        visited_values = 0
        while stack:
            current = stack.pop()
            visited_values += 1
            if visited_values > 100_000:
                raise RuntimeError("Design Token value structure exceeds the scan limit.")
            if isinstance(current, str):
                for ref in re.findall(r"(?<!\\)\{([^{}]+)\}", current):
                    found.add(ref)
                    direct_refs += 1
            elif isinstance(current, dict):
                if isinstance(current.get("$ref"), str):
                    found.add("#" + current["$ref"].lstrip("#"))
                    direct_refs += 1
                stack.extend(current.values())
            elif isinstance(current, list):
                stack.extend(current)
        return found
    def walk(node, parts=(), inherited_type=None, depth=0):
        nonlocal groups, invalid_structures, name_issues, untyped, empty_values
        if depth > 100 or len(tokens) + groups > 100_000:
            raise RuntimeError("Design Tokens nesting or token count exceeds the safety limit.")
        if not isinstance(node, dict):
            invalid_structures += 1
            return
        group_type = node.get("$type", inherited_type)
        if "$value" in node:
            token_path = ".".join(parts)
            tokens[token_path] = node
            if any(key in node and not key.startswith("$") for key in node):
                invalid_structures += 1
            if not isinstance(node.get("$type", inherited_type), str):
                untyped += 1
            value = node.get("$value")
            if value is None or value == "":
                empty_values += 1
            if any(char in (parts[-1] if parts else "") for char in "{}."):
                name_issues += 1
            alias_edges[token_path].update(inspect_value(value, token_path))
            if isinstance(node.get("$ref"), str):
                alias_edges[token_path].add("#" + node["$ref"].lstrip("#"))
                direct_refs += 1
        else:
            groups += 1
            for key, child in node.items():
                if key.startswith("$"):
                    continue
                if not isinstance(child, dict):
                    invalid_structures += 1
                    continue
                next_parts = parts + (key,)
                walk(child, next_parts, group_type, depth + 1)
    walk(document)
    unresolved = circular = 0
    resolved_graph = {}
    for source, refs in alias_edges.items():
        resolved = set()
        for ref in refs:
            if ref.startswith("#/"):
                pointer = [part.replace("~1", "/").replace("~0", "~") for part in ref[2:].split("/")]
                resolved.add(".".join(pointer))
            else:
                resolved.add(ref)
        resolved_graph[source] = resolved
    for source, refs in resolved_graph.items():
        for ref in refs:
            if ref not in tokens:
                unresolved += 1
    # Iterative graph walk avoids Python recursion limits on large token systems.
    state = {}
    for start in resolved_graph:
        if state.get(start, 0) != 0:
            continue
        state[start] = 1
        stack = [(start, iter(resolved_graph.get(start, ())))]
        while stack:
            node, edges = stack[-1]
            try:
                target = next(edges)
            except StopIteration:
                state[node] = 2
                stack.pop()
                continue
            if target not in tokens:
                continue
            target_state = state.get(target, 0)
            if target_state == 1:
                circular += 1
            elif target_state == 0:
                state[target] = 1
                stack.append((target, iter(resolved_graph.get(target, ()))))
    type_counts = collections.Counter()
    for node in tokens.values():
        token_type = node.get("$type", "inherited/unspecified")
        type_counts[str(token_type)] += 1
    lines = [
        f"Group objects: {groups:,}",
        f"Tokens: {len(tokens):,}",
        f"Tokens missing an effective $type: {untyped:,}",
        f"Tokens with empty $value: {empty_values:,}",
        f"Invalid token/group structures: {invalid_structures:,}",
        f"Token/group names containing reserved punctuation: {name_issues:,}",
        f"Alias/reference occurrences: {direct_refs:,}",
        f"Unresolved alias/reference targets: {unresolved:,}",
        f"Circular alias paths detected: {circular:,}",
        "Token type counts: " + (", ".join(f"{key}={value}" for key, value in type_counts.most_common(18)) or "none"),
        "Token names, token values, descriptions and reference targets are withheld.",
    ]
    return _report(path, "tokens", "Design Tokens 2025.10 static audit", lines)


def warc_archive_audit(path: Path) -> dict:
    if path.stat().st_size > MAX_INPUT:
        raise RuntimeError("WARC compressed input exceeds 20 MiB.")
    use_gzip = path.name.lower().endswith((".gz", ".warc.gz"))
    try:
        stream = gzip.open(path, "rb") if use_gzip else path.open("rb")
    except OSError as exc:
        raise RuntimeError("WARC stream could not be opened.") from exc
    total_bytes = records = bad_headers = missing_lengths = over_limit = 0
    versions = collections.Counter()
    record_types = collections.Counter()
    content_types = collections.Counter()
    warc_ids = 0
    try:
        with stream:
            while True:
                line = stream.readline(8_192)
                total_bytes += len(line)
                while line in (b"\r\n", b"\n"):
                    line = stream.readline(8_192)
                    total_bytes += len(line)
                if not line:
                    break
                if total_bytes > MAX_EXPANDED:
                    raise RuntimeError("Expanded WARC stream exceeds 120 MiB.")
                if not re.fullmatch(rb"WARC/1\.[01]\r?\n", line):
                    bad_headers += 1
                    raise RuntimeError("WARC record version line is malformed.")
                versions[line.decode("ascii", "replace").strip()] += 1
                headers = {}
                while True:
                    header = stream.readline(16_384)
                    total_bytes += len(header)
                    if total_bytes > MAX_EXPANDED:
                        raise RuntimeError("Expanded WARC stream exceeds 120 MiB.")
                    if header in (b"\r\n", b"\n", b""):
                        break
                    if b":" not in header:
                        bad_headers += 1
                        continue
                    key, value = header.split(b":", 1)
                    headers[key.decode("ascii", "ignore").strip().lower()] = value.decode("latin-1", "replace").strip()
                records += 1
                if records > 50_000:
                    raise RuntimeError("WARC exceeds the 50,000-record limit.")
                record_types[headers.get("warc-type", "unspecified").lower()] += 1
                content_types[headers.get("content-type", "unspecified").split(";", 1)[0].lower()] += 1
                warc_ids += bool(headers.get("warc-record-id"))
                raw_length = headers.get("content-length")
                if raw_length is None:
                    missing_lengths += 1
                    raise RuntimeError("WARC record is missing Content-Length.")
                try:
                    length = int(raw_length)
                except ValueError as exc:
                    raise RuntimeError("WARC Content-Length is invalid.") from exc
                if length < 0 or length > MAX_EXPANDED or total_bytes + length > MAX_EXPANDED:
                    over_limit += 1
                    raise RuntimeError("WARC record payload exceeds the expanded-size limit.")
                remaining = length
                while remaining:
                    chunk = stream.read(min(remaining, 65_536))
                    total_bytes += len(chunk)
                    if not chunk:
                        raise RuntimeError("WARC payload is truncated.")
                    remaining -= len(chunk)
                separator = stream.readline(4)
                total_bytes += len(separator)
                if separator not in (b"\r\n", b"\n", b""):
                    bad_headers += 1
                if total_bytes > MAX_EXPANDED:
                    raise RuntimeError("Expanded WARC stream exceeds 120 MiB.")
    except (OSError, EOFError) as exc:
        raise RuntimeError("WARC stream is damaged or has invalid gzip compression.") from exc
    lines = [
        f"Records: {records:,}",
        f"WARC versions: " + (", ".join(f"{key}={value}" for key, value in versions.items()) or "none"),
        f"Record ID fields present: {warc_ids:,}",
        f"Record headers with malformed lines: {bad_headers:,}",
        f"Records missing content length: {missing_lengths:,}",
        f"Records rejected for excessive payload size: {over_limit:,}",
        "WARC record type counts: " + (", ".join(f"{key}={value}" for key, value in record_types.most_common(12)) or "none"),
        "WARC content types: " + (", ".join(f"{key}={value}" for key, value in content_types.most_common(12)) or "none"),
        f"Expanded bytes inspected: {total_bytes:,}",
        "Record IDs, URLs, dates, IPs, headers and archived payload contents are withheld.",
    ]
    return _report(path, "warc", "WARC web-archive structure audit", lines)
