from __future__ import annotations

import json
import struct
import tempfile
import zipfile
from pathlib import Path
import unittest

import wave35


class Wave35Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def write(self, name: str, content: bytes | str) -> Path:
        path = self.root / name
        path.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))
        return path

    def report(self, result: dict) -> str:
        return Path(result["output_path"]).read_text(encoding="utf-8")

    def test_safetensors_valid_header_checks_offsets_without_leaking_names_or_metadata(self):
        header = {
            "PRIVATE_WEIGHT_NAME": {"dtype": "F32", "shape": [2], "data_offsets": [0, 8]},
            "__metadata__": {"private": "PRIVATE_METADATA_VALUE"},
        }
        raw = json.dumps(header, separators=(",", ":")).encode()
        path = self.write("weights.safetensors", struct.pack("<Q", len(raw)) + raw + b"\x00" * 8)
        report = self.report(wave35.safetensors_audit(path))
        self.assertIn("Tensor descriptors: 1", report)
        self.assertIn("Malformed descriptors / byte-size mismatches: 0", report)
        self.assertNotIn("PRIVATE_WEIGHT_NAME", report)
        self.assertNotIn("PRIVATE_METADATA_VALUE", report)

    def test_safetensors_rejects_duplicate_json_keys_and_bad_ranges(self):
        duplicate = b'{"x":{"dtype":"U8","shape":[1],"data_offsets":[0,1]},"x":{"dtype":"U8","shape":[1],"data_offsets":[0,1]}}'
        path = self.write("duplicate.safetensors", struct.pack("<Q", len(duplicate)) + duplicate + b"x")
        with self.assertRaisesRegex(RuntimeError, "unique keys"):
            wave35.safetensors_audit(path)
        bad = json.dumps({"x": {"dtype": "F32", "shape": [2], "data_offsets": [0, 3]}}).encode()
        path = self.write("bad.safetensors", struct.pack("<Q", len(bad)) + bad + b"xxx")
        report = self.report(wave35.safetensors_audit(path))
        self.assertIn("Malformed descriptors / byte-size mismatches: 1", report)

    def test_gguf_header_audit_checks_structure_and_withholds_tensor_names(self):
        payload = bytearray(b"GGUF")
        payload += struct.pack("<IQQ", 3, 1, 1)
        def gguf_string(value: str) -> bytes:
            encoded = value.encode("utf-8")
            return struct.pack("<Q", len(encoded)) + encoded
        payload += gguf_string("general.alignment") + struct.pack("<II", 4, 32)
        payload += gguf_string("PRIVATE_TENSOR_NAME") + struct.pack("<IQQQI", 2, 4, 4, 1, 0) + struct.pack("<Q", 0)
        payload += b"\x00" * ((-len(payload)) % 32)
        payload += b"\x00" * 32
        report = self.report(wave35.gguf_model_audit(self.write("model.gguf", bytes(payload))))
        self.assertIn("GGUF version: 3", report)
        self.assertIn("Tensor descriptors: 1", report)
        self.assertIn("Invalid or out-of-range tensor offsets: 0", report)
        self.assertNotIn("PRIVATE_TENSOR_NAME", report)

    def test_gguf_rejects_bad_magic_and_truncated_metadata(self):
        with self.assertRaisesRegex(RuntimeError, "magic bytes"):
            wave35.gguf_model_audit(self.write("bad.gguf", b"NOPE" + b"\0" * 40))
        with self.assertRaisesRegex(RuntimeError, "truncated or malformed"):
            wave35.gguf_model_audit(self.write("short.gguf", b"GGUF\x03\0"))

    def test_huggingface_model_card_checks_frontmatter_and_sections_without_content_leak(self):
        card = """---
license: mit
tags:
  - text-generation
datasets:
  - private-dataset
language:
  - en
pipeline_tag: text-generation
---
# Model Card
## Model Description
An internal model.
## Intended Uses
Private use.
## Limitations and Risks
Not validated.
## Training Data
Internal set.
## Evaluation
Private results.
"""
        report = self.report(wave35.hf_model_card_audit(self.write("README.md", card)))
        self.assertIn("YAML front matter: present", report)
        self.assertIn("Recognized documentation sections: 5/5", report)
        self.assertNotIn("private-dataset", report)
        self.assertNotIn("Internal model", report)

    def test_huggingface_model_card_warns_when_frontmatter_is_missing(self):
        report = self.report(wave35.hf_model_card_audit(self.write("README.md", "# A model\n\nJust text.")))
        self.assertIn("YAML front matter: missing", report)
        self.assertNotIn("Just text", report)

    def test_chat_dataset_audit_reports_aggregate_structure_and_never_echoes_messages(self):
        rows = [
            {"messages": [
                {"role": "user", "content": "PRIVATE_USER_PROMPT"},
                {"role": "assistant", "content": "PRIVATE_ASSISTANT_REPLY"},
            ]}
            for _ in range(10)
        ]
        data = "\n".join(json.dumps(row) for row in rows) + "\n"
        report = self.report(wave35.chat_dataset_audit(self.write("training.jsonl", data)))
        self.assertIn("Structurally valid chat examples: 10", report)
        self.assertIn("OpenAI supervised fine-tuning minimum of 10 examples: met", report)
        self.assertNotIn("PRIVATE_USER_PROMPT", report)
        self.assertNotIn("PRIVATE_ASSISTANT_REPLY", report)

    def test_chat_dataset_audit_counts_bad_lines_and_duplicate_records(self):
        row = json.dumps({"messages": [{"role": "user", "content": "secret"}, {"role": "assistant", "content": "answer"}]})
        report = self.report(wave35.chat_dataset_audit(self.write("train.jsonl", row + "\n" + row + "\nnot-json")))
        self.assertIn("Exact duplicate lines: 1", report)
        self.assertIn("Invalid examples / malformed lines: 1", report)
        self.assertNotIn("secret", report)

    def test_promptfoo_config_audit_checks_provider_prompt_test_structure(self):
        config = """description: translation test
providers:
  - openai:gpt-6
prompts:
  - 'Translate {{input}}'
tests:
  - vars:
      input: private text
    assert:
      - type: contains
        value: private phrase
scenarios:
  - tests:
      - vars:
          input: another private sample
"""
        report = self.report(wave35.promptfoo_config_audit(self.write("promptfooconfig.yaml", config)))
        self.assertIn("Providers configured: 1", report)
        self.assertIn("Prompts configured: 1", report)
        self.assertIn("Structural findings: 0", report)
        self.assertNotIn("openai:gpt-6", report)
        self.assertNotIn("private text", report)

    def test_promptfoo_config_audit_reports_missing_core_fields_without_echoing_values(self):
        report = self.report(wave35.promptfoo_config_audit(self.write("promptfooconfig.yaml", "description: private\n")))
        self.assertIn("Structural findings: 2", report)
        self.assertNotIn("private", report)

    def test_3mf_package_audit_checks_opc_relationships_and_mesh_indices(self):
        package = self.root / "sample.3mf"
        content_types = b"""<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Override PartName="/3D/3dmodel.model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>"""
        relationships = b"""<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="r0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel" Target="/3D/3dmodel.model"/></Relationships>"""
        model = b"""<model xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources><object id="1" type="model" name="PRIVATE_OBJECT"><mesh><vertices><vertex x="0" y="0" z="0"/><vertex x="1" y="0" z="0"/><vertex x="0" y="1" z="0"/></vertices><triangles><triangle v1="0" v2="1" v3="2"/></triangles></mesh></object></resources><build><item objectid="1"/></build></model>"""
        with zipfile.ZipFile(package, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("[Content_Types].xml", content_types)
            archive.writestr("_rels/.rels", relationships)
            archive.writestr("3D/3dmodel.model", model)
        report = self.report(wave35.three_mf_package_audit(package))
        self.assertIn("Objects / mesh objects / build items / components: 1/1/1/0", report)
        self.assertIn("Vertices / triangles: 3/1", report)
        self.assertIn("Structural findings: 0", report)
        self.assertNotIn("PRIVATE_OBJECT", report)

    def test_3mf_package_audit_rejects_path_traversal_and_bad_relationship(self):
        package = self.root / "bad.3mf"
        with zipfile.ZipFile(package, "w") as archive:
            archive.writestr("../escape.txt", "unsafe")
        with self.assertRaisesRegex(RuntimeError, "unsafe or encrypted"):
            wave35.three_mf_package_audit(package)


if __name__ == "__main__":
    unittest.main()
