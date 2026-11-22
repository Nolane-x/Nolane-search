from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import zipfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wave27


class Wave27DigitalPreservationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, name: str, content: str) -> Path:
        path = self.root / name
        path.write_text(content, encoding="utf-8")
        return path

    def archive_bagit(self, name: str, payload: bytes, expected_digest: str | None = None) -> Path:
        path = self.root / name
        digest = hashlib.sha256(payload).hexdigest()
        expected = expected_digest if expected_digest is not None else digest
        bagit = b"BagIt-Version: 1.0\nTag-File-Character-Encoding: UTF-8\n"
        payload_manifest = f"{expected}  data/sample.txt\n".encode()
        tag_manifest = (
            hashlib.sha256(bagit).hexdigest() + "  bagit.txt\n" +
            hashlib.sha256(payload_manifest).hexdigest() + "  manifest-sha256.txt\n"
        ).encode()
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("bagit.txt", bagit)
            archive.writestr("manifest-sha256.txt", payload_manifest)
            archive.writestr("tagmanifest-sha256.txt", tag_manifest)
            archive.writestr("data/sample.txt", payload)
        return path

    def assert_report(self, result):
        self.assertTrue(Path(result["output_path"]).is_file())
        self.assertIn("audit", result["summary"].lower())

    def test_bagit_archive_validates_payload_and_tag_checksums_without_content(self):
        result = wave27.bagit_archive_audit(self.archive_bagit("valid-bag.zip", b"private research payload"))
        self.assert_report(result)
        self.assertIn("Payload files under data/: 1", result["summary"])
        self.assertIn("Payload manifest entries checked: 1", result["summary"])
        self.assertIn("Tag manifest entries checked: 2", result["summary"])
        self.assertIn("Checksum mismatches: 0", result["summary"])
        self.assertIn("Payload files not listed by a manifest: 0", result["summary"])
        self.assertNotIn("private research payload", result["summary"])
        self.assertNotIn("sample.txt", result["summary"])

    def test_bagit_archive_detects_checksum_mismatch(self):
        result = wave27.bagit_archive_audit(self.archive_bagit("bad-bag.zip", b"private payload", "0" * 64))
        self.assert_report(result)
        self.assertIn("Checksum mismatches: 1", result["summary"])

    def test_bagit_archive_rejects_missing_declaration(self):
        path = self.root / "not-bag.zip"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("data/x.txt", "x")
        with self.assertRaisesRegex(RuntimeError, "bagit.txt"):
            wave27.bagit_archive_audit(path)

    def test_frictionless_audit_counts_resource_schema_and_bad_key_references(self):
        document = {
            "profile": "data-package",
            "resources": [{
                "name": "private-resource",
                "path": "data/private.csv",
                "schema": {
                    "fields": [{"name": "id"}, {"name": "label"}],
                    "primaryKey": "absent",
                    "foreignKeys": [{"fields": ["missing"], "reference": {"resource": "other", "fields": ["id"]}}],
                },
            }, {
                "name": "remote-resource",
                "path": "https://private.example/data.csv",
            }],
        }
        result = wave27.frictionless_package_audit(self.write("datapackage.json", json.dumps(document)))
        self.assert_report(result)
        self.assertIn("Resource entries: 2", result["summary"])
        self.assertIn("Schema field entries: 2", result["summary"])
        self.assertIn("Primary-key field references missing from schema: 1", result["summary"])
        self.assertIn("Foreign-key local field reference issues: 1", result["summary"])
        self.assertIn("Remote resource URIs (not fetched): 1", result["summary"])
        self.assertNotIn("private-resource", result["summary"])
        self.assertNotIn("private.example", result["summary"])

    def test_frictionless_audit_detects_duplicate_names_and_unsafe_paths(self):
        document = {
            "resources": [
                {"name": "same", "path": "../outside.csv"},
                {"name": "same", "data": []},
            ]
        }
        result = wave27.frictionless_package_audit(self.write("bad-package.json", json.dumps(document)))
        self.assert_report(result)
        self.assertIn("Duplicate resource names: 1", result["summary"])
        self.assertIn("Unsafe relative resource paths: 1", result["summary"])

    def test_ro_crate_audit_validates_root_descriptor_and_internal_refs_without_ids(self):
        document = {
            "@context": "https://w3id.org/ro/crate/1.2/context",
            "@graph": [
                {"@id": "./", "@type": "Dataset", "hasPart": [{"@id": "data/file.txt"}, {"@id": "missing.txt"}]},
                {"@id": "ro-crate-metadata.json", "@type": "CreativeWork", "about": {"@id": "./"}},
                {"@id": "data/file.txt", "@type": "File"},
            ],
        }
        result = wave27.ro_crate_audit(self.write("ro-crate-metadata.json", json.dumps(document)))
        self.assert_report(result)
        self.assertIn("JSON-LD graph entities: 3", result["summary"])
        self.assertIn("Root Dataset entity count: 1", result["summary"])
        self.assertIn("RO-Crate metadata descriptor node count: 1", result["summary"])
        self.assertIn("Internal references without a matching graph entity: 1", result["summary"])
        self.assertNotIn("missing.txt", result["summary"])
        self.assertNotIn("data/file.txt", result["summary"])

    def test_ro_crate_audit_detects_duplicate_entity_ids(self):
        document = {"@graph": [{"@id": "./", "@type": "Dataset"}, {"@id": "./", "@type": "Dataset"}]}
        result = wave27.ro_crate_audit(self.write("duplicate-ro.json", json.dumps(document)))
        self.assert_report(result)
        self.assertIn("Duplicate @id values: 1", result["summary"])

    def test_iiif_manifest_audit_counts_canvas_pages_and_image_services(self):
        document = {
            "@context": "http://iiif.io/api/presentation/3/context.json",
            "id": "https://private.example/manifest/1",
            "type": "Manifest",
            "items": [{
                "id": "https://private.example/canvas/1",
                "type": "Canvas",
                "width": 1000,
                "height": 800,
                "items": [{
                    "type": "AnnotationPage",
                    "items": [{
                        "type": "Annotation",
                        "motivation": "painting",
                        "target": "https://private.example/canvas/1",
                        "body": {
                            "type": "Image",
                            "id": "https://private.example/image/full.jpg",
                            "service": [{"id": "https://private.example/iiif/image"}],
                        },
                    }],
                }],
            }],
        }
        result = wave27.iiif_manifest_audit(self.write("manifest.json", json.dumps(document)))
        self.assert_report(result)
        self.assertIn("Manifest type valid: True", result["summary"])
        self.assertIn("Canvas items: 1", result["summary"])
        self.assertIn("Annotations: 1", result["summary"])
        self.assertIn("Image body resources: 1", result["summary"])
        self.assertIn("Image service references: 1", result["summary"])
        self.assertNotIn("private.example", result["summary"])

    def test_iiif_manifest_audit_detects_missing_dimensions_and_target(self):
        document = {
            "@context": "http://iiif.io/api/presentation/3/context.json",
            "id": "https://example.invalid/manifest",
            "type": "Manifest",
            "items": [{"id": "https://example.invalid/canvas", "type": "Canvas", "items": [{"items": [{"type": "Annotation", "body": {"type": "TextualBody"}}]}]}],
        }
        result = wave27.iiif_manifest_audit(self.write("bad-manifest.json", json.dumps(document)))
        self.assert_report(result)
        self.assertIn("Canvas records with invalid dimensions: 1", result["summary"])
        self.assertIn("Annotations missing target: 1", result["summary"])

    def test_datacite_audit_counts_core_and_related_metadata_without_values(self):
        source = """<resource xmlns="http://datacite.org/schema/kernel-4" schemaVersion="4.7">
<identifier identifierType="DOI">10.1234/private.doi</identifier>
<creators><creator><creatorName>Private Creator</creatorName></creator></creators>
<titles><title>Secret Dataset Title</title></titles>
<publisher>Private Publisher</publisher><publicationYear>2025</publicationYear>
<resourceType resourceTypeGeneral="Dataset">Research Data</resourceType>
<relatedIdentifiers><relatedIdentifier relatedIdentifierType="URL" relationType="IsSupplementTo">https://private.example</relatedIdentifier></relatedIdentifiers>
</resource>"""
        result = wave27.datacite_metadata_audit(self.write("datacite.xml", source))
        self.assert_report(result)
        self.assertIn("Identifier records: 1", result["summary"])
        self.assertIn("DOI-shaped identifiers: 1", result["summary"])
        self.assertIn("Creator entries: 1", result["summary"])
        self.assertIn("Title entries: 1", result["summary"])
        self.assertIn("Related identifiers: 1", result["summary"])
        self.assertIn("Missing core metadata categories: 0", result["summary"])
        self.assertNotIn("Private Creator", result["summary"])
        self.assertNotIn("Secret Dataset Title", result["summary"])
        self.assertNotIn("private.doi", result["summary"])

    def test_datacite_audit_detects_missing_core_metadata_and_bad_year(self):
        source = """<resource xmlns="http://datacite.org/schema/kernel-4"><identifier identifierType="DOI">bad</identifier><publicationYear>20X5</publicationYear></resource>"""
        result = wave27.datacite_metadata_audit(self.write("incomplete-datacite.xml", source))
        self.assert_report(result)
        self.assertIn("DOI-shaped identifiers: 0", result["summary"])
        self.assertIn("Publication-year format issues: 1", result["summary"])
        self.assertGreater(int(result["summary"].split("Missing core metadata categories: ")[1].splitlines()[0]), 0)

    def test_mets_audit_cross_checks_file_and_metadata_references_without_paths(self):
        source = """<mets xmlns="http://www.loc.gov/METS/" xmlns:xlink="http://www.w3.org/1999/xlink">
<metsHdr ID="HDR1"/><dmdSec ID="DMD1"/><amdSec ID="AMD1"/>
<fileSec><file ID="FILE1"><FLocat xlink:href="secret/data.bin"/></file></fileSec>
<structMap><div DMDID="DMD1" ADMID="AMD1"><fptr FILEID="FILE1"/></div><div><fptr FILEID="MISSING"/></div></structMap>
</mets>"""
        result = wave27.mets_package_audit(self.write("mets.xml", source))
        self.assert_report(result)
        self.assertIn("File entries: 1", result["summary"])
        self.assertIn("Structural maps: 1", result["summary"])
        self.assertIn("FILEID references without matching ID: 1", result["summary"])
        self.assertIn("DMDID/ADMID/CONTENTIDS references without matching ID: 0", result["summary"])
        self.assertNotIn("secret/data.bin", result["summary"])

    def test_mets_audit_detects_duplicate_ids_and_missing_sections(self):
        source = """<mets xmlns="http://www.loc.gov/METS/"><fileSec/><fileSec/><structMap><div/></structMap><fileSec><file ID="X"/></fileSec><structMap><div ID="X"/></structMap></mets>"""
        result = wave27.mets_package_audit(self.write("bad-mets.xml", source))
        self.assert_report(result)
        self.assertGreater(int(result["summary"].split("Duplicate METS IDs: ")[1].splitlines()[0]), 0)

    def test_premis_audit_counts_entities_and_linking_ids_without_values(self):
        source = """<premis xmlns="http://www.loc.gov/premis/v3">
<object><objectIdentifier><objectIdentifierType>local</objectIdentifierType><objectIdentifierValue>secret-object</objectIdentifierValue></objectIdentifier></object>
<event><eventIdentifier><eventIdentifierType>local</eventIdentifierType><eventIdentifierValue>secret-event</eventIdentifierValue></eventIdentifier><eventDateTime>2025-01-01T00:00:00Z</eventDateTime><linkingObjectIdentifier><linkingObjectIdentifierType>local</linkingObjectIdentifierType><linkingObjectIdentifierValue>secret-object</linkingObjectIdentifierValue></linkingObjectIdentifier></event>
<agent><agentIdentifier><agentIdentifierType>local</agentIdentifierType><agentIdentifierValue>secret-agent</agentIdentifierValue></agentIdentifier></agent>
</premis>"""
        result = wave27.premis_event_audit(self.write("premis.xml", source))
        self.assert_report(result)
        self.assertIn("PREMIS object entities: 1", result["summary"])
        self.assertIn("PREMIS event entities: 1", result["summary"])
        self.assertIn("PREMIS agent entities: 1", result["summary"])
        self.assertIn("Linking references without a matching identifier: 0", result["summary"])
        self.assertNotIn("secret-object", result["summary"])
        self.assertNotIn("secret-agent", result["summary"])

    def test_premis_audit_flags_missing_linked_identifiers(self):
        source = """<premis><object/><event><linkingObjectIdentifier><linkingObjectIdentifierValue>orphan</linkingObjectIdentifierValue></linkingObjectIdentifier></event></premis>"""
        result = wave27.premis_event_audit(self.write("orphan-premis.xml", source))
        self.assert_report(result)
        self.assertIn("Linking references without a matching identifier: 1", result["summary"])

    def test_stac_audit_counts_item_assets_and_links_without_geometry(self):
        document = {
            "stac_version": "1.1.0",
            "type": "Feature",
            "id": "private-item",
            "bbox": [1, 2, 3, 4],
            "geometry": {"type": "Point", "coordinates": [1, 2]},
            "properties": {"datetime": "2025-01-01T00:00:00Z"},
            "links": [{"rel": "collection", "href": "https://private.example/collection"}],
            "assets": {"image": {"href": "https://private.example/image.tif", "roles": ["data", "thumbnail"]}},
        }
        result = wave27.stac_catalog_audit(self.write("item.json", json.dumps(document)))
        self.assert_report(result)
        self.assertIn("STAC object type: Feature", result["summary"])
        self.assertIn("STAC version: 1.1.0", result["summary"])
        self.assertIn("Asset entries: 1", result["summary"])
        self.assertIn("Link entries: 1", result["summary"])
        self.assertIn("Item temporal datetime property present: True", result["summary"])
        self.assertNotIn("private-item", result["summary"])
        self.assertNotIn("private.example", result["summary"])
        self.assertNotIn("1, 2", result["summary"])

    def test_stac_audit_detects_invalid_links_and_assets(self):
        document = {"stac_version": "bad", "type": "Catalog", "links": [{"rel": "child"}], "assets": {"bad": "not-an-object"}}
        result = wave27.stac_catalog_audit(self.write("bad-stac.json", json.dumps(document)))
        self.assert_report(result)
        self.assertIn("Invalid link records/refs: 1", result["summary"])
        self.assertIn("Invalid asset entries: 1", result["summary"])
        self.assertIn("STAC version: unspecified/invalid", result["summary"])

    def test_tei_audit_counts_structure_and_xml_ids_without_text(self):
        source = """<TEI xmlns="http://www.tei-c.org/ns/1.0">
<teiHeader><fileDesc><titleStmt><title>Private scholarly title</title><author>Private Author</author></titleStmt><publicationStmt><publisher>Private Press</publisher></publicationStmt><sourceDesc><p>Private source note</p></sourceDesc></fileDesc></teiHeader>
<text><body><div xml:id="section-1"><p xml:id="paragraph-1">Private text content</p><ref target="#missing">Private link text</ref></div><back/></body></text>
</TEI>"""
        result = wave27.tei_document_audit(self.write("document.tei.xml", source))
        self.assert_report(result)
        self.assertIn("TEI header occurrences: 1", result["summary"])
        self.assertIn("text/body/front/back structures: 1/1/0/1", result["summary"])
        self.assertIn("div/p/line/speech/note elements: 1/2/0/0/0", result["summary"])
        self.assertIn("Internal fragment targets without matching xml:id: 1", result["summary"])
        self.assertNotIn("Private scholarly title", result["summary"])
        self.assertNotIn("Private Author", result["summary"])
        self.assertNotIn("Private text content", result["summary"])

    def test_tei_audit_detects_duplicate_xml_ids(self):
        source = """<TEI xmlns="http://www.tei-c.org/ns/1.0"><teiHeader/><text><body><p xml:id="x"/><p xml:id="x"/></body></text></TEI>"""
        result = wave27.tei_document_audit(self.write("duplicate.tei.xml", source))
        self.assert_report(result)
        self.assertIn("Duplicate xml:id values: 1", result["summary"])


if __name__ == "__main__":
    unittest.main()
