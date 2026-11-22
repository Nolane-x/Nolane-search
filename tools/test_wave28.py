import gzip
import hashlib
import json
import struct
import tempfile
import unittest
import zipfile
from pathlib import Path

import wave28


class Wave28Tests(unittest.TestCase):
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

    def assert_report(self, result):
        self.assertIn("summary", result)
        self.assertTrue(Path(result["output_path"]).is_file())
        self.assertLessEqual(len(result["summary"]), 5500)

    def test_ocfl_valid_inventory_and_payload_fixity(self):
        payload = b"preservation payload"
        digest = hashlib.sha512(payload).hexdigest()
        inventory = {
            "id": "urn:secret-object-id",
            "type": "https://ocfl.io/1.1/spec/#inventory",
            "digestAlgorithm": "sha512",
            "head": "v1",
            "manifest": {digest: ["v1/content/object.bin"]},
            "versions": {
                "v1": {
                    "created": "2026-01-01T00:00:00Z",
                    "state": {digest: ["object.bin"]},
                }
            },
        }
        raw = json.dumps(inventory, separators=(",", ":")).encode()
        sidecar = hashlib.sha512(raw).hexdigest() + " inventory.json\n"
        path = self.zip_file("object.ocfl.zip", {
            "object/0=ocfl_object_1.1": b"",
            "object/inventory.json": raw,
            "object/inventory.json.sha512": sidecar.encode(),
            "object/v1/content/object.bin": payload,
        })
        result = wave28.ocfl_object_audit(path)
        self.assert_report(result)
        self.assertIn("Content digest mismatches: 0", result["summary"])
        self.assertIn("Manifest files missing from archive: 0", result["summary"])
        self.assertNotIn("urn:secret-object-id", result["summary"])

    def test_ocfl_reports_bad_fixity_and_missing_physical_file(self):
        digest = hashlib.sha512(b"expected").hexdigest()
        inventory = {
            "digestAlgorithm": "sha512",
            "head": "v1",
            "manifest": {digest: ["v1/content/missing.bin"]},
            "versions": {"v1": {"state": {digest: ["logical.bin"]}}},
        }
        raw = json.dumps(inventory).encode()
        path = self.zip_file("bad-ocfl.zip", {
            "obj/0=ocfl_object_1.0": b"",
            "obj/inventory.json": raw,
            "obj/inventory.json.sha512": b"deadbeef inventory.json\n",
        })
        result = wave28.ocfl_object_audit(path)
        self.assertIn("Inventory sidecar digest mismatches or missing: 1", result["summary"])
        self.assertIn("Manifest files missing from archive: 1", result["summary"])

    def test_ocfl_rejects_unsafe_archive_paths(self):
        path = self.zip_file("unsafe-ocfl.zip", {"../escape.txt": b"x"})
        with self.assertRaisesRegex(RuntimeError, "unsafe member path"):
            wave28.ocfl_object_audit(path)

    def test_zarr_v3_inspects_groups_and_arrays_without_chunk_values(self):
        path = self.zip_file("study.zarr.zip", {
            "study.zarr/zarr.json": json.dumps({"zarr_format": 3, "node_type": "group"}).encode(),
            "study.zarr/brain/zarr.json": json.dumps({"zarr_format": 3, "node_type": "group"}).encode(),
            "study.zarr/brain/volume/zarr.json": json.dumps({
                "zarr_format": 3, "node_type": "array", "shape": [4, 8, 8], "data_type": "float32"
            }).encode(),
            "study.zarr/brain/volume/c/0/0/0": b"PRIVATE_CHUNK_BYTES",
        })
        result = wave28.zarr_store_audit(path)
        self.assertIn("Zarr metadata versions detected: v3", result["summary"])
        self.assertIn("Group metadata nodes: 2", result["summary"])
        self.assertIn("Array metadata nodes: 1", result["summary"])
        self.assertNotIn("PRIVATE_CHUNK_BYTES", result["summary"])

    def test_zarr_v2_rejects_bad_chunk_shape(self):
        path = self.zip_file("broken.zarr.zip", {
            "broken.zarr/.zgroup": b'{"zarr_format":2}',
            "broken.zarr/array/.zarray": json.dumps({
                "zarr_format": 2, "shape": [10, 20], "chunks": [10], "dtype": "<f4"
            }).encode(),
        })
        result = wave28.zarr_store_audit(path)
        self.assertIn("Malformed or inconsistent metadata records: 1", result["summary"])

    def test_nifti1_header_audit_does_not_read_voxel_payload(self):
        header = bytearray(352)
        struct.pack_into("<i", header, 0, 348)
        struct.pack_into("<8h", header, 40, 3, 2, 3, 4, 1, 1, 1, 1)
        struct.pack_into("<2h", header, 70, 16, 32)
        struct.pack_into("<8f", header, 76, 1, 1, 1, 1, 1, 1, 1, 1)
        header[344:348] = b"n+1\x00"
        path = self.write("volume.nii", bytes(header) + b"SECRET_VOXEL_DATA")
        result = wave28.nifti_header_audit(path)
        self.assertIn("Header format: NIfTI-1", result["summary"])
        self.assertIn("Datatype/bitpix mismatch: 0", result["summary"])
        self.assertNotIn("SECRET_VOXEL_DATA", result["summary"])

    def test_nifti_gzip_header_is_read_without_expanding_voxels(self):
        header = bytearray(352)
        struct.pack_into("<i", header, 0, 348)
        struct.pack_into("<8h", header, 40, 1, 12, 1, 1, 1, 1, 1, 1)
        struct.pack_into("<2h", header, 70, 2, 8)
        struct.pack_into("<8f", header, 76, 1, 1, 1, 1, 1, 1, 1, 1)
        header[344:348] = b"n+1\x00"
        path = self.write("volume.nii.gz", gzip.compress(bytes(header) + b"x" * (1024 * 1024)))
        result = wave28.nifti_header_audit(path)
        self.assertIn("Header format: NIfTI-1", result["summary"])
        self.assertIn("voxel data were not decoded", result["summary"])

    def test_nifti_rejects_invalid_dimensions(self):
        header = bytearray(352)
        struct.pack_into("<i", header, 0, 348)
        struct.pack_into("<8h", header, 40, 2, 0, 3, 1, 1, 1, 1, 1)
        header[344:348] = b"n+1\x00"
        with self.assertRaisesRegex(RuntimeError, "dimensionality"):
            wave28.nifti_header_audit(self.write("bad.nii", bytes(header)))

    def test_dicom_privacy_screen_never_emits_patient_values(self):
        import pydicom
        from pydicom.dataset import FileDataset, FileMetaDataset
        from pydicom.uid import ExplicitVRLittleEndian, SecondaryCaptureImageStorage, generate_uid

        meta = FileMetaDataset()
        meta.MediaStorageSOPClassUID = SecondaryCaptureImageStorage
        meta.MediaStorageSOPInstanceUID = generate_uid()
        meta.TransferSyntaxUID = ExplicitVRLittleEndian
        path = self.root / "patient.dcm"
        ds = FileDataset(str(path), {}, file_meta=meta, preamble=b"\0" * 128)
        ds.SOPClassUID = SecondaryCaptureImageStorage
        ds.SOPInstanceUID = meta.MediaStorageSOPInstanceUID
        ds.PatientName = "PRIVATE_PATIENT_NAME"
        ds.PatientID = "PRIVATE_PATIENT_ID"
        ds.Rows = 1
        ds.Columns = 1
        ds.SamplesPerPixel = 1
        ds.PhotometricInterpretation = "MONOCHROME2"
        ds.BitsAllocated = 8
        ds.BitsStored = 8
        ds.HighBit = 7
        ds.PixelRepresentation = 0
        ds.PixelData = b"\x00"
        ds.save_as(path)
        result = wave28.dicom_privacy_audit(path)
        self.assertIn("header only; pixel data excluded", result["summary"])
        self.assertIn("direct-identifier fields present: 2", result["summary"])
        self.assertNotIn("PRIVATE_PATIENT_NAME", result["summary"])
        self.assertNotIn("PRIVATE_PATIENT_ID", result["summary"])

    def test_las_header_reads_point_count_without_emitting_coordinates(self):
        header = bytearray(227)
        header[:4] = b"LASF"
        header[24] = 1
        header[25] = 2
        struct.pack_into("<H", header, 94, 227)
        struct.pack_into("<I", header, 96, 227)
        struct.pack_into("<I", header, 100, 0)
        header[104] = 0
        struct.pack_into("<H", header, 105, 20)
        struct.pack_into("<I", header, 107, 1)
        point = b"\x00" * 20
        result = wave28.las_pointcloud_audit(self.write("points.las", bytes(header) + point))
        self.assertIn("Point record format: 0", result["summary"])
        self.assertIn("Point count: 1", result["summary"])

    def test_las_rejects_truncated_point_records(self):
        header = bytearray(227)
        header[:4] = b"LASF"
        header[24] = 1
        header[25] = 2
        struct.pack_into("<H", header, 94, 227)
        struct.pack_into("<I", header, 96, 227)
        header[104] = 0
        struct.pack_into("<H", header, 105, 20)
        struct.pack_into("<I", header, 107, 1)
        with self.assertRaisesRegex(RuntimeError, "extends beyond"):
            wave28.las_pointcloud_audit(self.write("truncated.las", bytes(header)))

    def test_jp2_box_audit_checks_framing_and_signature(self):
        def box(kind, payload):
            return struct.pack(">I4s", 8 + len(payload), kind) + payload
        signature = box(b"jP  ", b"\r\n\x87\n")
        ftyp = box(b"ftyp", b"jp2 \x00\x00\x00\x00jp2 ")
        ihdr = box(b"ihdr", struct.pack(">IIHBBBB", 32, 64, 3, 7, 7, 0, 0))
        jp2h = box(b"jp2h", ihdr)
        codestream = box(b"jp2c", b"\xff\x4f\xff\xd9")
        result = wave28.jp2_box_audit(self.write("image.jp2", signature + ftyp + jp2h + codestream))
        self.assertIn("JP2 signature box: valid", result["summary"])
        self.assertIn("Required ftyp/jp2h/jp2c boxes missing: 0", result["summary"])
        self.assertIn("Malformed or out-of-bounds box records: 0", result["summary"])

    def test_netcdf_classic_empty_header(self):
        header = b"CDF\x01" + struct.pack(">7I", 0, 0, 0, 0, 0, 0, 0)
        result = wave28.netcdf_classic_audit(self.write("empty.nc", header))
        self.assertIn("NetCDF classic version: CDF-1", result["summary"])
        self.assertIn("Variable descriptors: 0", result["summary"])

    def test_netcdf_rejects_netcdf4_and_cdf5_magic(self):
        with self.assertRaisesRegex(RuntimeError, "CDF-1 and CDF-2 only"):
            wave28.netcdf_classic_audit(self.write("new.nc", b"CDF\x05" + b"\x00" * 28))

    def test_nwb_structure_audit_never_reads_dataset_values(self):
        import h5py
        path = self.root / "experiment.nwb"
        with h5py.File(path, "w") as root:
            root.attrs["nwb_version"] = "2.7.0"
            root.attrs["namespaces"] = "core"
            root.create_group("general")
            root.create_group("acquisition").create_dataset("private_timeseries", data=[1.0, 2.0])
            root["general"].attrs["subject_id"] = "PRIVATE_SUBJECT_ID"
        result = wave28.nwb_structure_audit(path)
        self.assertIn("NWB version attribute present: True", result["summary"])
        self.assertIn("Datasets inspected (metadata only): 1", result["summary"])
        self.assertNotIn("PRIVATE_SUBJECT_ID", result["summary"])
        self.assertNotIn("private_timeseries", result["summary"])


if __name__ == "__main__":
    unittest.main()
