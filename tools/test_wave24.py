from __future__ import annotations

import base64
import email.message
import json
import mailbox
import sqlite3
import sys
import tempfile
import urllib.parse
import zipfile
import zlib
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wave24


class Wave24InteroperabilityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, name: str, content: str) -> Path:
        path = self.root / name
        path.write_text(content, encoding="utf-8")
        return path

    def archive(self, name: str, members: list[tuple[str, bytes, int | None]]) -> Path:
        path = self.root / name
        with zipfile.ZipFile(path, "w") as archive:
            for filename, content, compression in members:
                info = zipfile.ZipInfo(filename)
                if compression is not None:
                    info.compress_type = compression
                archive.writestr(info, content)
        return path

    def assert_report(self, result):
        self.assertTrue(Path(result["output_path"]).is_file())
        self.assertIn("audit", result["summary"].lower())

    def test_odf_audit_checks_mimetype_manifest_and_structure_without_text(self):
        manifest = b"""<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"><manifest:file-entry manifest:full-path="/" manifest:media-type="application/vnd.oasis.opendocument.text"/><manifest:file-entry manifest:full-path="content.xml" manifest:media-type="text/xml"/></manifest:manifest>"""
        content = b"""<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"><text:h>Private title</text:h><text:p>Secret body content</text:p><table:table><table:table-row><table:table-cell/></table:table-row></table:table></office:document-content>"""
        path = self.archive("document.odt", [
            ("mimetype", b"application/vnd.oasis.opendocument.text", zipfile.ZIP_STORED),
            ("META-INF/manifest.xml", manifest, zipfile.ZIP_DEFLATED),
            ("content.xml", content, zipfile.ZIP_DEFLATED),
        ])
        result = wave24.odf_package_audit(path)
        self.assert_report(result)
        self.assertIn("Document kind: text", result["summary"])
        self.assertIn("Package MIME matches root manifest entry: True", result["summary"])
        self.assertIn("p: 1", result["summary"])
        self.assertNotIn("Private title", result["summary"])
        self.assertNotIn("Secret body content", result["summary"])

    def test_xliff_audit_detects_empty_target_and_placeholder_mismatch(self):
        source = """<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.1"><file id="f"><unit id="u1"><segment state="initial"><source>Hello {name}</source><target>Xin chào</target></segment></unit><unit id="u2"><segment><source>Save %s</source><target/></segment></unit></file></xliff>"""
        result = wave24.xliff_audit(self.write("vi.xlf", source))
        self.assert_report(result)
        self.assertIn("Translation units: 2", result["summary"])
        self.assertIn("Missing or empty targets: 1", result["summary"])
        self.assertIn("Placeholder-count mismatches: 1", result["summary"])
        self.assertNotIn("Xin chào", result["summary"])
        self.assertNotIn("Hello", result["summary"])

    def test_xliff_audit_rejects_dtd(self):
        with self.assertRaisesRegex(RuntimeError, "DTD"):
            wave24.xliff_audit(self.write("bad.xlf", '<!DOCTYPE xliff [<!ENTITY x "a">]><xliff>&x;</xliff>'))

    def test_mbox_audit_counts_parts_and_withholds_headers_and_body(self):
        path = self.root / "mailbox.mbox"
        box = mailbox.mbox(str(path))
        message = email.message.EmailMessage()
        message["From"] = "private.sender@example.com"
        message["To"] = "private.recipient@example.com"
        message["Subject"] = "Sensitive subject"
        message["Date"] = "Fri, 21 Nov 2025 10:00:00 +0000"
        message.set_content("Private email body")
        message.add_attachment(b"private attachment bytes", maintype="application", subtype="octet-stream", filename="secret.pdf")
        box.add(message)
        box.close()
        result = wave24.mbox_audit(path)
        self.assert_report(result)
        self.assertIn("Messages: 1", result["summary"])
        self.assertIn("Attachment parts: 1", result["summary"])
        self.assertNotIn("private.sender", result["summary"])
        self.assertNotIn("Sensitive subject", result["summary"])
        self.assertNotIn("Private email body", result["summary"])
        self.assertNotIn("secret.pdf", result["summary"])

    def test_geopackage_audit_counts_feature_rows_without_coordinates(self):
        path = self.root / "map.gpkg"
        connection = sqlite3.connect(path)
        connection.executescript("""
        PRAGMA application_id = 1196444487;
        CREATE TABLE gpkg_spatial_ref_sys (srs_name TEXT, srs_id INTEGER PRIMARY KEY, organization TEXT, organization_coordsys_id INTEGER, definition TEXT, description TEXT);
        INSERT INTO gpkg_spatial_ref_sys VALUES ('Private CRS', 4326, 'EPSG', 4326, 'private-definition', '');
        CREATE TABLE gpkg_contents (table_name TEXT PRIMARY KEY, data_type TEXT NOT NULL, identifier TEXT, description TEXT, last_change TEXT NOT NULL, min_x DOUBLE, min_y DOUBLE, max_x DOUBLE, max_y DOUBLE, srs_id INTEGER);
        INSERT INTO gpkg_contents VALUES ('private_features','features','private-name','', '2025-01-01T00:00:00Z',1,2,3,4,4326);
        CREATE TABLE gpkg_geometry_columns (table_name TEXT, column_name TEXT, geometry_type_name TEXT, srs_id INTEGER, z INTEGER, m INTEGER);
        INSERT INTO gpkg_geometry_columns VALUES ('private_features','geom','POINT',4326,0,0);
        CREATE TABLE private_features (id INTEGER PRIMARY KEY, geom BLOB, label TEXT);
        INSERT INTO private_features VALUES (1, X'00', 'private attribute');
        INSERT INTO private_features VALUES (2, X'00', 'another private attribute');
        """)
        connection.commit()
        connection.close()
        result = wave24.geopackage_audit(path)
        self.assert_report(result)
        self.assertIn("Feature rows (count only): 2", result["summary"])
        self.assertIn("POINT=1", result["summary"])
        self.assertNotIn("private attribute", result["summary"])
        self.assertNotIn("Private CRS", result["summary"])

    def test_mbtiles_audit_counts_tiles_and_duplicate_coords(self):
        path = self.root / "tiles.mbtiles"
        connection = sqlite3.connect(path)
        connection.executescript("""
        CREATE TABLE metadata (name TEXT, value TEXT);
        INSERT INTO metadata VALUES ('name','Private map'), ('format','png'), ('minzoom','1'), ('maxzoom','2'), ('bounds','1,2,3,4');
        CREATE TABLE tiles (zoom_level INTEGER, tile_column INTEGER, tile_row INTEGER, tile_data BLOB);
        INSERT INTO tiles VALUES (1,0,0,X'00'), (1,0,0,X'01'), (2,1,1,X'02');
        """)
        connection.commit()
        connection.close()
        result = wave24.mbtiles_audit(path)
        self.assert_report(result)
        self.assertIn("Tile rows: 3", result["summary"])
        self.assertIn("Duplicate tile-coordinate groups: 1", result["summary"])
        self.assertNotIn("Private map", result["summary"])
        self.assertNotIn("1,2,3,4", result["summary"])

    def test_openraster_audit_counts_layers_and_missing_sources(self):
        stack = b"""<image w="512" h="256" name="Private artwork"><stack><layer name="Secret layer" src="data/layer0.png" visibility="visible" opacity="1.0" composite-op="svg:src-over"/><layer name="Missing layer" src="data/missing.png" visibility="hidden"/></stack></image>"""
        path = self.archive("art.ora", [
            ("mimetype", b"image/openraster", zipfile.ZIP_STORED),
            ("stack.xml", stack, zipfile.ZIP_DEFLATED),
            ("data/layer0.png", b"not-decoded-pixels", zipfile.ZIP_STORED),
            ("mergedimage.png", b"preview", zipfile.ZIP_STORED),
        ])
        result = wave24.openraster_audit(path)
        self.assert_report(result)
        self.assertIn("Layer entries: 2", result["summary"])
        self.assertIn("Missing layer source members: 1", result["summary"])
        self.assertIn("Canvas dimensions: 512 × 256", result["summary"])
        self.assertNotIn("Secret layer", result["summary"])

    def test_krita_audit_counts_nodes_without_layer_names(self):
        main = b"""<DOC><IMAGE width="800" height="600" colorspacename="RGBA" colordepth="U8"><layers><layer nodetype="paintlayer" name="Private layer" visible="1"/><layer nodetype="grouplayer" name="Group" visible="0" locked="1"/></layers></IMAGE></DOC>"""
        path = self.archive("painting.kra", [("maindoc.xml", main, zipfile.ZIP_DEFLATED), ("mergedimage.png", b"pixels", zipfile.ZIP_STORED)])
        result = wave24.krita_project_audit(path)
        self.assert_report(result)
        self.assertIn("Layer/node entries: 2", result["summary"])
        self.assertIn("Hidden nodes: 1", result["summary"])
        self.assertIn("Locked nodes: 1", result["summary"])
        self.assertNotIn("Private layer", result["summary"])

    def test_gltf_audit_reports_assets_and_path_traversal_without_uri(self):
        document = {
            "asset": {"version": "2.0", "generator": "Private generator"},
            "scenes": [{"nodes": [0]}],
            "nodes": [{"mesh": 0}],
            "meshes": [{"primitives": []}],
            "buffers": [{"byteLength": 16, "uri": "../secret.bin"}],
            "images": [{"uri": "https://private.example/image.png"}],
            "materials": [{"name": "Secret material"}],
        }
        result = wave24.gltf_audit(self.write("scene.gltf", json.dumps(document)))
        self.assert_report(result)
        self.assertIn("nodes: 1", result["summary"])
        self.assertIn("External resource URIs (not fetched): 2", result["summary"])
        self.assertIn("Unsafe resource URI paths: 1", result["summary"])
        self.assertNotIn("secret.bin", result["summary"])
        self.assertNotIn("Secret material", result["summary"])

    def test_drawio_audit_decodes_compressed_page(self):
        model = '<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/><mxCell id="v1" vertex="1" parent="1"/><mxCell id="e1" edge="1" source="v1" target="missing" parent="1"/></root></mxGraphModel>'
        encoded = urllib.parse.quote(model, safe="!'()*~").encode("ascii")
        compressor = zlib.compressobj(9, zlib.DEFLATED, -15)
        compressed = compressor.compress(encoded) + compressor.flush()
        payload = base64.b64encode(compressed).decode("ascii")
        source = '<mxfile compressed="true"><diagram id="p1">' + payload + '</diagram></mxfile>'
        result = wave24.drawio_audit(self.write("diagram.drawio", source))
        self.assert_report(result)
        self.assertIn("Diagram pages decoded: 1", result["summary"])
        self.assertIn("Vertex cells: 1", result["summary"])
        self.assertIn("Edge cells: 1", result["summary"])
        self.assertIn("Missing parent/source/target references: 1", result["summary"])
        self.assertNotIn("missing", result["summary"])

    def test_n8n_workflow_audit_detects_sensitive_fields_without_values(self):
        workflow = {
            "nodes": [
                {"id": "a", "name": "Private webhook", "type": "n8n-nodes-base.webhook", "parameters": {"path": "private", "token": "sensitive-token"}},
                {"id": "b", "name": "Shell", "type": "n8n-nodes-base.executeCommand", "disabled": True, "parameters": {"command": "private command"}},
            ],
            "connections": {"Private webhook": {"main": [[{"node": "Shell", "type": "main", "index": 0}]]}},
        }
        result = wave24.n8n_workflow_audit(self.write("flow.json", json.dumps(workflow)))
        self.assert_report(result)
        self.assertIn("Workflow node count: 2", result["summary"])
        self.assertIn("Disabled nodes: 1", result["summary"])
        self.assertIn("Potential hardcoded-secret fields (values withheld): 1", result["summary"])
        self.assertNotIn("sensitive-token", result["summary"])
        self.assertNotIn("private command", result["summary"])

    def test_design_token_audit_finds_unresolved_and_circular_aliases(self):
        tokens = {
            "color": {
                "base": {"$type": "color", "$value": "#336699"},
                "primary": {"$type": "color", "$value": "{color.base}"},
                "broken": {"$type": "color", "$value": "{color.absent}"},
            },
            "cycle": {
                "a": {"$type": "dimension", "$value": "{cycle.b}"},
                "b": {"$type": "dimension", "$value": "{cycle.a}"},
            },
            "untype": {"$value": 4}
        }
        result = wave24.design_token_audit(self.write("tokens.json", json.dumps(tokens)))
        self.assert_report(result)
        self.assertIn("Tokens: 6", result["summary"])
        self.assertIn("Unresolved alias/reference targets: 1", result["summary"])
        self.assertGreaterEqual(int(result["summary"].split("Circular alias paths detected: ")[1].splitlines()[0]), 1)
        self.assertIn("Tokens missing an effective $type: 1", result["summary"])
        self.assertNotIn("#336699", result["summary"])
        self.assertNotIn("color.primary", result["summary"])

    def test_warc_audit_counts_records_without_urls_or_headers(self):
        body = b"WARC/1.1\r\nWARC-Type: response\r\nWARC-Record-ID: <urn:uuid:secret-id>\r\nWARC-Target-URI: https://private.example/path\r\nContent-Type: application/http; msgtype=response\r\nContent-Length: 19\r\n\r\nHTTP/1.1 200 OK\r\n\r\n"
        path = self.root / "archive.warc"
        path.write_bytes(body)
        result = wave24.warc_archive_audit(path)
        self.assert_report(result)
        self.assertIn("Records: 1", result["summary"])
        self.assertIn("response=1", result["summary"])
        self.assertNotIn("private.example", result["summary"])
        self.assertNotIn("secret-id", result["summary"])


if __name__ == "__main__":
    unittest.main()
