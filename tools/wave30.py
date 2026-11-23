"""Wave 30 bounded metadata auditors for OME-NGFF, Parquet and COG GeoTIFF.

These processors inspect metadata only. They never decode microscopy chunks,
Parquet row values/statistics, raster pixels or externally referenced assets.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path, PurePosixPath

from wave28 import (
    MAX_EXPANDED,
    MAX_INPUT,
    MAX_METADATA,
    _json_bytes,
    _read_bounded,
    _report,
    _safe_member,
    _size_guard,
    _zip_index,
)


def _vector_is_valid(value, rank: int, positive: bool = False) -> bool:
    if not isinstance(value, list) or len(value) != rank:
        return False
    for item in value:
        if isinstance(item, bool) or not isinstance(item, (int, float)) or not math.isfinite(float(item)):
            return False
        if positive and item <= 0:
            return False
    return True


def _ome_axis_layout(axes) -> tuple[bool, int]:
    if not isinstance(axes, list) or not 2 <= len(axes) <= 5:
        return False, 0
    names = []
    kinds = []
    for axis in axes:
        if not isinstance(axis, dict):
            return False, len(axes)
        name = axis.get("name")
        kind = axis.get("type", "custom")
        if not isinstance(name, str) or not name.strip() or not isinstance(kind, str):
            return False, len(axes)
        names.append(name)
        kinds.append(kind.lower())
    if len(set(names)) != len(names):
        return False, len(axes)
    space_count = kinds.count("space")
    time_count = kinds.count("time")
    channel_count = kinds.count("channel")
    if space_count not in {2, 3} or time_count > 1 or channel_count > 1:
        return False, len(axes)
    phases = [0 if kind == "time" else 2 if kind == "space" else 1 for kind in kinds]
    if phases != sorted(phases):
        return False, len(axes)
    if sum(1 for phase in phases if phase == 1) > 1:
        return False, len(axes)
    return True, len(axes)


def _ome_dataset_transform(dataset: dict, path: str, rank: int, coordinate_names: set[str]) -> bool:
    transforms = dataset.get("coordinateTransformations")
    if not isinstance(transforms, list) or len(transforms) != 1 or not isinstance(transforms[0], dict):
        return False
    transform = transforms[0]
    kind = transform.get("type")
    input_ref = transform.get("input")
    output_ref = transform.get("output")
    if not isinstance(input_ref, dict) or input_ref.get("path") != path:
        return False
    if not isinstance(output_ref, dict) or output_ref.get("name") not in coordinate_names:
        return False
    if kind == "scale":
        return _vector_is_valid(transform.get("scale"), rank, positive=True)
    if kind == "identity":
        return True
    if kind == "sequence":
        items = transform.get("transformations")
        if not isinstance(items, list) or len(items) != 2:
            return False
        first, second = items
        return (
            isinstance(first, dict) and first.get("type") == "scale" and
            _vector_is_valid(first.get("scale"), rank, positive=True) and
            isinstance(second, dict) and second.get("type") == "translation" and
            _vector_is_valid(second.get("translation"), rank)
        )
    return False


def ome_ngff_audit(path: Path) -> dict:
    """Audit OME-NGFF v0.5/v0.6 metadata inside a bounded local Zarr ZIP store."""
    _size_guard(path)
    archive = None
    try:
        archive, members, expanded = _zip_index(path, "OME-NGFF")
        metadata_names = [
            name for name in members
            if PurePosixPath(name).name == "zarr.json"
        ]
        if not metadata_names:
            raise RuntimeError("ZIP archive contains no Zarr v3 zarr.json metadata documents.")
        if len(metadata_names) > 10_000:
            raise RuntimeError("OME-NGFF metadata document count exceeds the safety limit.")
        documents = {}
        aggregate = 0
        for name in metadata_names:
            raw = _read_bounded(archive, members[name], 2 * 1024 * 1024)
            aggregate += len(raw)
            if aggregate > MAX_METADATA:
                raise RuntimeError("OME-NGFF metadata exceeds the 10 MiB aggregate limit.")
            documents[name] = _json_bytes(raw, "OME-NGFF Zarr")

        versions = set()
        version_errors = 0
        image_groups = 0
        resolution_levels = 0
        axes_checked = 0
        invalid_axes = 0
        missing_arrays = 0
        invalid_arrays = 0
        invalid_transforms = 0
        inconsistent_shapes = 0
        inconsistent_dtypes = 0
        descents_checked = 0
        zarr_v2_documents = 0

        for name, document in documents.items():
            if document.get("zarr_format") != 3:
                zarr_v2_documents += 1
            attributes = document.get("attributes")
            ome = attributes.get("ome") if isinstance(attributes, dict) else None
            if not isinstance(ome, dict):
                continue
            version = ome.get("version")
            if isinstance(version, str) and re.fullmatch(r"\d+\.\d+(?:\.\d+)?", version):
                versions.add(version)
            else:
                version_errors += 1
            multiscales = ome.get("multiscales")
            if not isinstance(multiscales, list):
                continue
            root_parent = str(PurePosixPath(name).parent)
            store_root = "" if root_parent == "." else root_parent + "/"
            for multiscale in multiscales:
                image_groups += 1
                if not isinstance(multiscale, dict):
                    invalid_axes += 1
                    continue
                systems = multiscale.get("coordinateSystems")
                datasets = multiscale.get("datasets")
                if not isinstance(systems, list) or not systems or not isinstance(datasets, list) or not datasets:
                    invalid_axes += 1
                    continue
                coordinate_names = set()
                rank_candidates = []
                for system in systems:
                    if not isinstance(system, dict):
                        invalid_axes += 1
                        continue
                    system_name = system.get("name")
                    if not isinstance(system_name, str) or not system_name.strip() or system_name in coordinate_names:
                        invalid_axes += 1
                        continue
                    coordinate_names.add(system_name)
                    valid, rank = _ome_axis_layout(system.get("axes"))
                    axes_checked += rank
                    if not valid:
                        invalid_axes += 1
                    else:
                        rank_candidates.append(rank)
                if not rank_candidates or len(set(rank_candidates)) > 1:
                    invalid_axes += 1
                    continue
                rank = rank_candidates[0]
                previous_shape = None
                dtype_set = set()
                seen_paths = set()
                for dataset in datasets:
                    resolution_levels += 1
                    if not isinstance(dataset, dict):
                        invalid_arrays += 1
                        continue
                    dataset_path = dataset.get("path")
                    if not isinstance(dataset_path, str) or not _safe_member(dataset_path) or dataset_path in seen_paths:
                        missing_arrays += 1
                        continue
                    seen_paths.add(dataset_path)
                    array_name = store_root + dataset_path.rstrip("/") + "/zarr.json"
                    array_doc = documents.get(array_name)
                    if array_doc is None:
                        missing_arrays += 1
                        continue
                    if array_doc.get("zarr_format") != 3 or array_doc.get("node_type") != "array":
                        invalid_arrays += 1
                        continue
                    shape = array_doc.get("shape")
                    dtype = array_doc.get("data_type")
                    if not isinstance(shape, list) or len(shape) != rank or any(
                        isinstance(n, bool) or not isinstance(n, int) or n <= 0 for n in shape
                    ) or not isinstance(dtype, str) or not dtype:
                        invalid_arrays += 1
                        continue
                    dtype_set.add(dtype)
                    if previous_shape is not None:
                        descents_checked += 1
                        if any(current > previous for current, previous in zip(shape, previous_shape)):
                            inconsistent_shapes += 1
                    previous_shape = shape
                    if not _ome_dataset_transform(dataset, dataset_path, rank, coordinate_names):
                        invalid_transforms += 1
                if len(dtype_set) > 1:
                    inconsistent_dtypes += 1

        inconsistent_versions = int(len(versions) > 1)
        lines = [
            f"Zarr v3 metadata documents inspected: {len(metadata_names):,}",
            f"OME metadata version labels: {len(versions):,}",
            f"Invalid or missing OME version fields: {version_errors:,}",
            f"OME image/multiscale groups inspected: {image_groups:,}",
            f"Resolution-level dataset references: {resolution_levels:,}",
            f"Coordinate axes inspected: {axes_checked:,}",
            f"Invalid axis definitions/order/rank: {invalid_axes:,}",
            f"Dataset arrays missing from metadata hierarchy: {missing_arrays:,}",
            f"Invalid dataset array metadata: {invalid_arrays:,}",
            f"Invalid scale/identity/sequence transformations: {invalid_transforms:,}",
            f"Non-descending multiscale resolution steps: {inconsistent_shapes:,}",
            f"Images with inconsistent level data types: {inconsistent_dtypes:,}",
            f"Mixed OME metadata versions in one store: {inconsistent_versions:,}",
            f"Non-v3 Zarr metadata documents: {zarr_v2_documents:,}",
            f"Expanded archive bytes (image chunks not read): {expanded:,}",
            "Axis names, group names, labels, coordinates, channel annotations and image values are withheld.",
            "Image chunks, voxel/pixel payloads and externally referenced assets are never read or downloaded.",
            "This is a bounded metadata-structure audit, not full JSON-Schema or image-data conformance certification.",
        ]
        return _report(path, "ome-ngff", "OME-NGFF 0.6 metadata and multiscale audit", lines)
    except (OSError, EOFError) as exc:
        raise RuntimeError("OME-NGFF archive is malformed or unreadable.") from exc
    finally:
        if archive is not None:
            archive.close()


def parquet_metadata_audit(path: Path) -> dict:
    """Inspect Parquet footer/schema/row-group metadata without reading row values."""
    _size_guard(path)
    if path.stat().st_size < 12:
        raise RuntimeError("Parquet file is shorter than the minimum header/footer size.")
    connection = None
    try:
        import duckdb
        connection = duckdb.connect(database=":memory:")
        connection.execute("SET threads=1")
        connection.execute("SET memory_limit='256MB'")
        source = str(path.resolve())
        file_cursor = connection.execute(
            "SELECT num_rows, num_row_groups, format_version, file_size_bytes, footer_size, encryption_algorithm "
            "FROM parquet_file_metadata(?)",
            [source],
        )
        file_row = file_cursor.fetchone()
        if file_row is None:
            raise RuntimeError("Parquet file has no readable file-level metadata.")
        file_meta = dict(zip([item[0] for item in file_cursor.description], file_row))
        row_cursor = connection.execute(
            "SELECT row_group_id, row_group_num_rows, row_group_num_columns, row_group_bytes, "
            "column_id, compression, encodings, total_compressed_size, total_uncompressed_size "
            "FROM parquet_metadata(?)",
            [source],
        )
        row_groups = row_cursor.fetchall()
        if len(row_groups) > 100_000:
            raise RuntimeError("Parquet footer exposes too many column-chunk metadata records.")
        schema_cursor = connection.execute(
            "SELECT type, repetition_type, num_children, converted_type, logical_type "
            "FROM parquet_schema(?)",
            [source],
        )
        schema_rows = schema_cursor.fetchall()
        if len(schema_rows) > 100_000:
            raise RuntimeError("Parquet schema exposes too many metadata nodes.")
        kv_count = 0
        geoparquet = False
        try:
            kv_cursor = connection.execute("SELECT key FROM parquet_kv_metadata(?)", [source])
            kv_rows = kv_cursor.fetchall()
            if len(kv_rows) > 10_000:
                raise RuntimeError("Parquet custom metadata key count exceeds the safety limit.")
            kv_count = len(kv_rows)
            for row in kv_rows:
                key = row[0]
                if isinstance(key, bytes):
                    label = key.decode("utf-8", errors="ignore")
                else:
                    label = str(key)
                if label.strip().lower() == "geo":
                    geoparquet = True
        except RuntimeError:
            raise
        except Exception:
            kv_count = 0
            geoparquet = False

        compression = Counter()
        encodings = Counter()
        for row in row_groups:
            compression[str(row[5] or "unknown").upper()] += 1
            for encoding in re.split(r"[,; ]+", str(row[6] or "")):
                if encoding:
                    encodings[encoding.upper()] += 1
        physical_types = Counter()
        logical_types = Counter()
        group_nodes = 0
        leaf_nodes = 0
        for physical, repetition, children, converted, logical in schema_rows:
            if physical is None:
                if children and int(children) > 0:
                    group_nodes += 1
                continue
            leaf_nodes += 1
            label = str(physical).upper()
            if "INT" in label:
                physical_types["integer"] += 1
            elif "FLOAT" in label or "DOUBLE" in label:
                physical_types["floating-point"] += 1
            elif "BOOLEAN" in label:
                physical_types["boolean"] += 1
            elif "BYTE_ARRAY" in label:
                physical_types["byte-array"] += 1
            elif "FIXED_LEN" in label:
                physical_types["fixed-length"] += 1
            else:
                physical_types["other"] += 1
            logical_label = str(logical or converted or "").upper()
            if logical_label:
                if any(token in logical_label for token in ("STRING", "UTF8", "ENUM")):
                    logical_types["string-like"] += 1
                elif any(token in logical_label for token in ("DECIMAL",)):
                    logical_types["decimal"] += 1
                elif any(token in logical_label for token in ("DATE", "TIME", "TIMESTAMP")):
                    logical_types["date/time"] += 1
                elif any(token in logical_label for token in ("LIST", "MAP", "STRUCT")):
                    logical_types["nested"] += 1
                elif any(token in logical_label for token in ("INT", "UINT")):
                    logical_types["integer"] += 1
                elif any(token in logical_label for token in ("JSON", "UUID", "BSON")):
                    logical_types["structured"] += 1
                else:
                    logical_types["other"] += 1

        lines = [
            f"Parquet format version: {int(file_meta.get('format_version') or 0)}",
            f"Rows declared in footer: {int(file_meta.get('num_rows') or 0):,}",
            f"Row groups: {int(file_meta.get('num_row_groups') or 0):,}",
            f"Column-chunk metadata records: {len(row_groups):,}",
            f"Schema metadata nodes: {len(schema_rows):,}",
            f"Nested/group schema nodes: {group_nodes:,}",
            f"Leaf schema fields: {leaf_nodes:,}",
            f"Distinct physical type categories: {len(physical_types):,}",
            f"Distinct logical type categories: {len(logical_types):,}",
            f"Distinct compression codecs: {len(compression):,}",
            f"Distinct page encodings: {len(encodings):,}",
            f"Custom key/value metadata entries: {kv_count:,}",
            f"GeoParquet 'geo' metadata key present: {geoparquet}",
            f"File bytes: {int(file_meta.get('file_size_bytes') or path.stat().st_size):,}",
            f"Footer bytes: {int(file_meta.get('footer_size') or 0):,}",
            f"Encryption metadata present: {bool(file_meta.get('encryption_algorithm'))}",
            "Column names, row values, min/max statistics, Bloom filter values, custom metadata values and source paths are withheld.",
            "Only footer/schema/row-group metadata is inspected; Parquet row/page values are not queried.",
        ]
        return _report(path, "parquet-metadata", "Apache Parquet footer and schema audit", lines)
    except RuntimeError:
        raise
    except ImportError as exc:
        raise RuntimeError("Parquet metadata audit requires the DuckDB runtime package.") from exc
    except Exception as exc:
        raise RuntimeError("Parquet footer is malformed or could not be inspected safely.") from exc
    finally:
        if connection is not None:
            connection.close()


def cog_geotiff_audit(path: Path) -> dict:
    """Validate local Cloud Optimized GeoTIFF layout without reading raster pixels."""
    _size_guard(path)
    try:
        import rasterio
        from rio_cogeo.cogeo import cog_validate
        valid, errors, warnings = cog_validate(str(path), strict=False, quiet=True)
        with rasterio.open(path, "r") as dataset:
            driver = str(dataset.driver or "unknown")
            band_count = int(dataset.count)
            block_shapes = list(dataset.block_shapes or [])
            overview_count = len(dataset.overviews(1)) if band_count else 0
            compression = str(dataset.compression or "unknown").upper()
            tiled = bool(dataset.profile.get("tiled", False))
    except ImportError as exc:
        raise RuntimeError("COG GeoTIFF audit requires the rio-cogeo/rasterio runtime package.") from exc
    except Exception as exc:
        raise RuntimeError("Local raster is not a readable GeoTIFF or its COG layout could not be inspected.") from exc

    def reason_category(message: str) -> str:
        value = message.lower()
        if "not a geotiff" in value:
            return "not-geotiff"
        if ".ovr" in value or "external overview" in value:
            return "external-overview"
        if "not tiled" in value or "tiled" in value:
            return "tiling-layout"
        if "ifd" in value:
            return "ifd-layout"
        if "offset" in value or "block" in value:
            return "data-offset-layout"
        if "overview" in value:
            return "overview-layout"
        if "gdal" in value or "edition" in value:
            return "structural-metadata"
        return "other-layout"

    error_categories = Counter(reason_category(str(message)) for message in errors)
    warning_categories = Counter(reason_category(str(message)) for message in warnings)
    block_count = len(block_shapes)
    lines = [
        f"Raster driver is GeoTIFF: {driver.upper() == 'GTIFF'}",
        f"COG layout compliant: {bool(valid)}",
        f"Validation errors: {len(errors):,}",
        f"Validation warnings: {len(warnings):,}",
        f"Validation error categories: {len(error_categories):,}",
        f"Validation warning categories: {len(warning_categories):,}",
        f"Raster band count: {band_count:,}",
        f"Band block-layout entries: {block_count:,}",
        f"Internal overview levels on first band: {overview_count:,}",
        f"Block tiling declared: {tiled}",
        f"Compression codec: {compression}",
        "Raster dimensions, CRS, geospatial bounds, tags, band names and pixel values are withheld.",
        "Only local TIFF structural metadata and COG layout offsets are examined; no URL, range endpoint or remote asset is fetched.",
        "This validates COG layout, not scientific image correctness or the semantic accuracy of geospatial coordinates.",
    ]
    return _report(path, "cog", "Cloud Optimized GeoTIFF layout audit", lines)
