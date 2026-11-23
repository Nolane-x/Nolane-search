from __future__ import annotations

import json
import tempfile
from pathlib import Path
import unittest

import wave36


class Wave36Tests(unittest.TestCase):
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

    def test_ollama_modelfile_recognizes_documented_directives_and_withholds_prompt_values(self):
        source = '''# Local model definition
FROM private-model:latest
PARAMETER temperature 0.2
PARAMETER num_ctx 8192
SYSTEM """PRIVATE_SYSTEM_PROMPT
multi-line instruction
"""
TEMPLATE """{{ .System }} PRIVATE_TEMPLATE {{ .Prompt }}"""
MESSAGE user PRIVATE_EXAMPLE
MESSAGE assistant PRIVATE_REPLY
REQUIRES 0.14.0
CAPABILITY tools
CAPABILITY vision
LICENSE """PRIVATE_LICENSE_TEXT"""
'''
        report = self.report(wave36.ollama_modelfile_audit(self.write("Modelfile", source)))
        self.assertIn("FROM directives: 1", report)
        self.assertIn("PARAMETER directives: 2", report)
        self.assertIn("MESSAGE examples: 2", report)
        self.assertIn("Declared capabilities: 2", report)
        self.assertIn("Malformed or incomplete directives: 0", report)
        for secret in ("private-model", "PRIVATE_SYSTEM_PROMPT", "PRIVATE_TEMPLATE", "PRIVATE_EXAMPLE", "PRIVATE_REPLY", "PRIVATE_LICENSE_TEXT"):
            self.assertNotIn(secret, report)

    def test_ollama_modelfile_requires_from_and_reports_unknown_or_invalid_directives(self):
        source = """PARAMETER temperature
UNKNOWN secret-value
CAPABILITY imaginary
REQUIRES newest
"""
        report = self.report(wave36.ollama_modelfile_audit(self.write("Modelfile", source)))
        self.assertIn("FROM directives: 0", report)
        self.assertIn("Unknown directives: 1", report)
        self.assertGreaterEqual(int(report.split("Malformed or incomplete directives: ")[1].splitlines()[0]), 3)
        self.assertNotIn("secret-value", report)

    def test_hf_tokenizer_audit_checks_vocabulary_ids_components_and_privacy(self):
        tokenizer = {
            "version": "1.0",
            "truncation": {"direction": "Right", "max_length": 512},
            "padding": {"strategy": "BatchLongest", "pad_id": 0},
            "added_tokens": [{"id": 4, "content": "PRIVATE_SPECIAL_TOKEN", "special": True}],
            "normalizer": {"type": "NFC"},
            "pre_tokenizer": {"type": "Whitespace"},
            "post_processor": {"type": "TemplateProcessing"},
            "decoder": {"type": "WordPiece"},
            "model": {
                "type": "WordPiece",
                "vocab": {"[UNK]": 0, "hello": 1, "world": 2},
                "unk_token": "[UNK]",
            },
        }
        report = self.report(wave36.hf_tokenizer_audit(self.write("tokenizer.json", json.dumps(tokenizer))))
        self.assertIn("Vocabulary entries: 3", report)
        self.assertIn("Added-token entries: 1", report)
        self.assertIn("Invalid vocabulary IDs: 0", report)
        self.assertNotIn("PRIVATE_SPECIAL_TOKEN", report)
        self.assertNotIn("hello", report)

    def test_hf_tokenizer_audit_detects_duplicate_and_colliding_ids(self):
        tokenizer = {
            "version": "1.0",
            "added_tokens": [{"id": 1, "content": "secret"}],
            "model": {"type": "BPE", "vocab": {"a": 1, "b": 1}, "merges": [["a", "b"], 4]},
        }
        report = self.report(wave36.hf_tokenizer_audit(self.write("tokenizer.json", json.dumps(tokenizer))))
        self.assertIn("Duplicate vocabulary IDs: 1", report)
        self.assertIn("Added/base vocabulary ID collisions: 1", report)
        self.assertIn("Malformed merge entries: 1", report)
        self.assertNotIn("secret", report)


    def test_hf_tokenizer_audit_accepts_unigram_array_vocabulary(self):
        tokenizer = {
            "version": "1.0",
            "added_tokens": [],
            "model": {
                "type": "Unigram",
                "vocab": [["<unk>", 0.0], ["hello", -1.2], ["world", -2.0]],
                "unk_id": 0,
            },
            "normalizer": None,
            "pre_tokenizer": {"type": "Metaspace"},
        }
        report = self.report(wave36.hf_tokenizer_audit(self.write("tokenizer.json", json.dumps(tokenizer))))
        self.assertIn("Vocabulary entries: 3 (Unigram array)", report)
        self.assertIn("Invalid vocabulary IDs: 0", report)
        self.assertIn("Duplicate vocabulary IDs: 0", report)

    def test_hf_dataset_card_audit_checks_metadata_and_safety_sections(self):
        card = """---
license: mit
language:
  - en
tags:
  - text-classification
task_categories:
  - text-classification
size_categories:
  - 10K<n<100K
configs:
  - config_name: default
---
# Dataset Card
## Dataset Description
Private dataset overview.
## Dataset Structure
Internal structure.
## Data Fields
Private fields.
## Data Splits
Internal split details.
## Dataset Creation
Private source collection.
## Personal and Sensitive Information
Review required.
## Bias and Limitations
Not evaluated.
## Licensing
See internal contract.
"""
        report = self.report(wave36.hf_dataset_card_audit(self.write("dataset-card.md", card)))
        self.assertIn("YAML front matter: present", report)
        self.assertIn("Common metadata fields missing: 0", report)
        self.assertIn("Documentation sections present: 8/8", report)
        self.assertNotIn("Private dataset overview", report)
        self.assertNotIn("internal contract", report.lower())

    def test_hf_dataset_card_audit_warns_for_missing_frontmatter_and_sections(self):
        report = self.report(wave36.hf_dataset_card_audit(self.write("dataset-card.md", "# Dataset\n\nPrivate text.")))
        self.assertIn("YAML front matter: missing or empty", report)
        self.assertIn("Common metadata fields missing: 5", report)
        self.assertNotIn("Private text", report)

    def test_mlflow_manifest_audit_reviews_flavors_signature_without_loading_artifacts(self):
        manifest = """artifact_path: model
flavors:
  python_function:
    loader_module: private.custom_loader
    data: data/model.pkl
    env: conda.yaml
  sklearn:
    pickled_model: model.pkl
signature:
  inputs: '[{"type":"long","name":"private_input"}]'
  outputs: '[{"type":"double","name":"private_output"}]'
  params: '{"temperature":{"type":"double"}}'
metadata:
  internal_owner: private-team
"""
        report = self.report(wave36.mlflow_model_manifest_audit(self.write("MLmodel", manifest)))
        self.assertIn("Declared model flavors: 2", report)
        self.assertIn("Python-function flavor: present", report)
        self.assertIn("Loader/custom-code references: 1", report)
        self.assertIn("Signature input/output/parameter declarations: 1/1/1", report)
        for secret in ("private.custom_loader", "model.pkl", "private_input", "private_output", "private-team"):
            self.assertNotIn(secret, report)

    def test_mlflow_manifest_audit_flags_invalid_flavor_and_signature_shape(self):
        manifest = """flavors:
  python_function: invalid
signature:
  inputs: not-json
  outputs: 42
"""
        report = self.report(wave36.mlflow_model_manifest_audit(self.write("MLmodel", manifest)))
        self.assertIn("Malformed flavor descriptors: 1", report)
        self.assertIn("Structural findings: 3", report)

    def test_dvc_pipeline_audit_checks_stage_graph_inputs_outputs_and_privacy(self):
        manifest = """schema: '2.0'
stages:
  prepare:
    cmd: python prepare.py --token SECRET_VALUE
    deps:
      - raw/private.csv
    params:
      - train.seed
    outs:
      - prepared/private.parquet
  train:
    cmd: python train.py
    deps:
      - prepared/private.parquet
    outs:
      - models/private.bin
    metrics:
      - metrics/private.json
"""
        report = self.report(wave36.dvc_pipeline_manifest_audit(self.write("dvc.yaml", manifest)))
        self.assertIn("Manifest kind: pipeline definition", report)
        self.assertIn("Stage entries: 2", report)
        self.assertIn("Dependency entries: 2", report)
        self.assertIn("Output/metric/plot entries: 3", report)
        self.assertIn("Stages missing a command: 0", report)
        for secret in ("SECRET_VALUE", "private.csv", "private.parquet", "private.bin"):
            self.assertNotIn(secret, report)

    def test_dvc_lock_audit_checks_locked_outputs_without_exposing_hashes(self):
        lock = """schema: '2.0'
stages:
  prepare:
    cmd: python prepare.py
    deps:
      - path: raw.csv
        md5: SECRET_HASH
    outs:
      - path: prepared.csv
        md5: ANOTHER_SECRET_HASH
        size: 42
"""
        report = self.report(wave36.dvc_pipeline_manifest_audit(self.write("dvc.lock", lock)))
        self.assertIn("Manifest kind: lock file", report)
        self.assertIn("Stage entries: 1", report)
        self.assertIn("Dependency entries: 1", report)
        self.assertNotIn("SECRET_HASH", report)
        self.assertNotIn("raw.csv", report)

    def test_helm_chart_audit_validates_metadata_and_dependencies(self):
        chart = """apiVersion: v2
name: private-chart
description: Internal chart
type: application
version: 1.2.3
appVersion: '2026.11'
dependencies:
  - name: redis
    version: 19.0.1
    repository: https://charts.example.invalid
    alias: private-cache
maintainers:
  - name: Private Maintainer
    email: private@example.invalid
annotations:
  example.invalid/owner: private-team
"""
        report = self.report(wave36.helm_chart_metadata_audit(self.write("Chart.yaml", chart)))
        self.assertIn("Chart API version: v2", report)
        self.assertIn("Chart version: valid semver", report)
        self.assertIn("Dependency declarations: 1", report)
        self.assertIn("Structural findings: 0", report)
        for secret in ("private-chart", "charts.example.invalid", "Private Maintainer", "private-team"):
            self.assertNotIn(secret, report)

    def test_helm_chart_audit_detects_invalid_version_type_and_duplicate_dependencies(self):
        chart = """apiVersion: v2
name: bad-chart
version: not-semver
type: service
dependencies:
  - name: redis
    version: 1.0.0
    repository: stable
  - name: redis
    version: 2.0.0
    repository: stable
"""
        report = self.report(wave36.helm_chart_metadata_audit(self.write("Chart.yaml", chart)))
        self.assertIn("Chart version: missing or invalid", report)
        self.assertIn("Chart type: invalid", report)
        self.assertIn("Duplicate dependency names/aliases: 1", report)
        self.assertGreaterEqual(int(report.split("Structural findings: ")[1].splitlines()[0]), 3)


if __name__ == "__main__":
    unittest.main()
