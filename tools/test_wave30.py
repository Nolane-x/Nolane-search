import json
import tempfile
import unittest
import zipfile
from pathlib import Path

import wave30


class Wave30Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def write(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def zip_file(self, name, entries):
        path = self.root / name
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for member, data in entries.items():
                archive.writestr(member, data)
        return path

    @staticmethod
    def ome_group(version="0.6", shape=(8, 16, 16), dataset_path="scale0", axes=None):
        axes = axes or [
            {"name": "z", "type": "space", "unit": "micrometer"},
            {"name": "y", "type": "space", "unit": "micrometer"},
            {"name": "x", "type": "space", "unit": "micrometer"},
        ]
        return {
            "zarr_format": 3,
            "node_type": "group",
            "attributes": {
                "ome": {
                    "version": version,
                    "multiscales": [{
                        "name": "PRIVATE_EXPERIMENT_NAME",
                        "type": "mean",
                        "coordinateSystems": [{"name": "physical", "axes": axes}],
                        "datasets": [{
                            "path": dataset_path,
                            "coordinateTransformations": [{
                                "type": "scale",
                                "scale": [1.0] * len(axes),
                                "input": {"path": dataset_path},
                                "output": {"name": "physical"},
                            }],
                        }],
                    }],
                }
            },
        }

    def test_ome_ngff_v06_valid_metadata_checks_array_rank_without_reading_chunks(self):
        root = self.ome_group()
        array = {
            "zarr_format": 3,
            "node_type": "array",
            "shape": [8, 16, 16],
            "data_type": "uint16",
        }
        path = self.zip_file("sample.ome.zarr.zip", {
            "sample.ome.zarr/zarr.json": json.dumps(root).encode(),
            "sample.ome.zarr/scale0/zarr.json": json.dumps(array).encode(),
            "sample.ome.zarr/scale0/c/0/0/0": b"PRIVATE_MICROSCOPY_PIXEL_BYTES",
        })
        result = wave30.ome_ngff_audit(path)
        self.assertIn("OME metadata version labels: 1", result["summary"])
        self.assertIn("OME image/multiscale groups inspected: 1", result["summary"])
        self.assertIn("Resolution-level dataset references: 1", result["summary"])
        self.assertIn("Dataset arrays missing from metadata hierarchy: 0", result["summary"])
        self.assertIn("Invalid scale/identity/sequence transformations: 0", result["summary"])
        self.assertNotIn("PRIVATE_EXPERIMENT_NAME", result["summary"])
        self.assertNotIn("PRIVATE_MICROSCOPY_PIXEL_BYTES", result["summary"])

    def test_ome_ngff_detects_shape_rank_and_transform_mismatch(self):
        axes = [
            {"name": "time", "type": "time", "unit": "second"},
            {"name": "channel", "type": "channel"},
            {"name": "y", "type": "space", "unit": "micrometer"},
            {"name": "x", "type": "space", "unit": "micrometer"},
        ]
        root = self.ome_group(axes=axes, shape=(4, 3, 32, 32))
        array = {"zarr_format": 3, "node_type": "array", "shape": [4, 3, 32], "data_type": "uint16"}
        path = self.zip_file("mismatch.ome.zarr.zip", {
            "store/zarr.json": json.dumps(root).encode(),
            "store/scale0/zarr.json": json.dumps(array).encode(),
        })
        result = wave30.ome_ngff_audit(path)
        self.assertIn("Invalid dataset array metadata: 1", result["summary"])

    def test_ome_ngff_rejects_missing_dataset_array_metadata(self):
        root = self.ome_group()
        root["attributes"]["ome"]["multiscales"][0]["datasets"].append({
            "path": "scale1",
            "coordinateTransformations": [{
                "type": "scale",
                "scale": [2.0, 2.0, 2.0],
                "input": {"path": "scale1"},
                "output": {"name": "physical"},
            }],
        })
        array = {"zarr_format": 3, "node_type": "array", "shape": [8, 16, 16], "data_type": "uint16"}
        path = self.zip_file("missing-level.ome.zarr.zip", {
            "store/zarr.json": json.dumps(root).encode(),
            "store/scale0/zarr.json": json.dumps(array).encode(),
        })
        result = wave30.ome_ngff_audit(path)
        self.assertIn("Dataset arrays missing from metadata hierarchy: 1", result["summary"])
        self.assertNotIn("scale1", result["summary"])

    def test_ome_ngff_flags_non_descending_resolution_levels(self):
        root = self.ome_group()
        root["attributes"]["ome"]["multiscales"][0]["datasets"].append({
            "path": "scale1",
            "coordinateTransformations": [{
                "type": "scale",
                "scale": [2.0, 2.0, 2.0],
                "input": {"path": "scale1"},
                "output": {"name": "physical"},
            }],
        })
        coarse = {"zarr_format": 3, "node_type": "array", "shape": [8, 16, 16], "data_type": "uint16"}
        fine = {"zarr_format": 3, "node_type": "array", "shape": [16, 32, 32], "data_type": "uint16"}
        path = self.zip_file("inverted.ome.zarr.zip", {
            "store/zarr.json": json.dumps(root).encode(),
            "store/scale0/zarr.json": json.dumps(coarse).encode(),
            "store/scale1/zarr.json": json.dumps(fine).encode(),
        })
        result = wave30.ome_ngff_audit(path)
        self.assertIn("Non-descending multiscale resolution steps: 1", result["summary"])

    def test_ome_ngff_rejects_unsafe_zip_paths(self):
        path = self.zip_file("unsafe.ome.zarr.zip", {
            "../escape/zarr.json": b'{"zarr_format":3,"node_type":"group"}',
        })
        with self.assertRaisesRegex(RuntimeError, "unsafe member path"):
            wave30.ome_ngff_audit(path)

    def test_ome_ngff_rejects_invalid_metadata_json(self):
        path = self.zip_file("bad.ome.zarr.zip", {
            "store/zarr.json": b'{"zarr_format":3,',
        })
        with self.assertRaisesRegex(RuntimeError, "malformed or not UTF-8"):
            wave30.ome_ngff_audit(path)

    def test_parquet_metadata_audit_reports_footer_without_column_names_or_stats(self):
        import duckdb

        path = self.root / "private.parquet"
        connection = duckdb.connect(database=":memory:")
        try:
            connection.execute(
                "CREATE TABLE sample AS SELECT 'PRIVATE_ROW_VALUE' AS private_column, 17 AS record_count, 3.5 AS score"
            )
            connection.execute(
                "COPY sample TO '" + str(path).replace("'", "''") + "' (FORMAT PARQUET, COMPRESSION ZSTD)"
            )
        finally:
            connection.close()
        result = wave30.parquet_metadata_audit(path)
        self.assertIn("Parquet format version:", result["summary"])
        self.assertIn("Rows declared in footer: 1", result["summary"])
        self.assertIn("Row groups: 1", result["summary"])
        self.assertIn("Column-chunk metadata records: 3", result["summary"])
        self.assertIn("Distinct compression codecs: 1", result["summary"])
        self.assertIn("GeoParquet 'geo' metadata key present: False", result["summary"])
        self.assertNotIn("PRIVATE_ROW_VALUE", result["summary"])
        self.assertNotIn("private_column", result["summary"])
        self.assertNotIn("record_count", result["summary"])
        self.assertNotIn("score", result["summary"])

    def test_parquet_metadata_audit_does_not_read_row_values(self):
        import duckdb

        path = self.root / "sensitive.parquet"
        connection = duckdb.connect(database=":memory:")
        try:
            connection.execute(
                "CREATE TABLE sample AS SELECT repeat('PRIVATE_MINIMUM_MAXIMUM_VALUE', 20) AS private_text"
            )
            connection.execute(
                "COPY sample TO '" + str(path).replace("'", "''") + "' (FORMAT PARQUET)"
            )
        finally:
            connection.close()
        result = wave30.parquet_metadata_audit(path)
        self.assertIn("Only footer/schema/row-group metadata is inspected", result["summary"])
        self.assertNotIn("PRIVATE_MINIMUM_MAXIMUM_VALUE", result["summary"])

    def test_parquet_metadata_audit_rejects_non_parquet_content(self):
        path = self.write("broken.parquet", b"this is not parquet content")
        with self.assertRaisesRegex(RuntimeError, "footer is malformed"):
            wave30.parquet_metadata_audit(path)

    def test_parquet_metadata_audit_enforces_input_size(self):
        path = self.write("oversized.parquet", b"x" * (20 * 1024 * 1024 + 1))
        with self.assertRaisesRegex(RuntimeError, "20 MiB"):
            wave30.parquet_metadata_audit(path)

    def test_cog_geotiff_audit_reports_layout_without_pixel_or_tag_values(self):
        import numpy as np
        import rasterio
        from rasterio.transform import from_origin

        path = self.root / "sensitive.cog.tif"
        with rasterio.open(
            path,
            "w",
            driver="GTiff",
            width=256,
            height=256,
            count=1,
            dtype="uint8",
            transform=from_origin(0, 256, 1, 1),
        ) as dataset:
            dataset.write(np.zeros((1, 256, 256), dtype="uint8"))
            dataset.update_tags(PRIVATE_TAG="PRIVATE_GEOTIFF_TAG_VALUE")
        result = wave30.cog_geotiff_audit(path)
        self.assertIn("COG layout compliant:", result["summary"])
        self.assertIn("Validation errors:", result["summary"])
        self.assertIn("Internal overview levels on first band:", result["summary"])
        self.assertNotIn("PRIVATE_GEOTIFF_TAG_VALUE", result["summary"])
        self.assertNotIn("PRIVATE", result["summary"])

    def test_cog_geotiff_audit_rejects_oversized_file(self):
        path = self.write("large.cog.tif", b"x" * (20 * 1024 * 1024 + 1))
        with self.assertRaisesRegex(RuntimeError, "20 MiB"):
            wave30.cog_geotiff_audit(path)

    def test_cog_geotiff_audit_rejects_unreadable_raster(self):
        path = self.write("invalid.tif", b"not a TIFF")
        with self.assertRaisesRegex(RuntimeError, "not a readable GeoTIFF"):
            wave30.cog_geotiff_audit(path)


if __name__ == "__main__":
    unittest.main()
