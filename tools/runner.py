#!/usr/bin/env python3
"""Private GitHub-hosted execution engine for Nolane Tools."""
from __future__ import annotations
import argparse, base64, concurrent.futures, csv, hashlib, json, mimetypes, os, posixpath, re, shutil, stat, subprocess, sys, tarfile, tempfile, textwrap, threading, time, unicodedata, urllib.error, urllib.parse, urllib.request, zipfile
from pathlib import Path
from html import escape, unescape
from html.parser import HTMLParser
from typing import Any

from wave23 import (
    ansible_playbook_audit, avro_schema_audit, bibtex_audit, gcode_audit,
    grafana_dashboard_audit, graphql_schema_audit, hdf5_audit, midi_audit,
    musicxml_audit, nmea_track_audit, prometheus_rules_audit, protobuf_schema_audit,
)
from wave24 import (
    drawio_audit, design_token_audit, geopackage_audit, gltf_audit,
    krita_project_audit, mbox_audit, mbtiles_audit, n8n_workflow_audit,
    odf_package_audit, openraster_audit, warc_archive_audit, xliff_audit,
)
from wave25 import (
    coverage_xml_audit, cyclonedx_sbom_audit, fits_file_audit, godot_project_audit,
    junit_xml_audit, otel_collector_audit, sarif_report_audit, step_cad_audit,
    unity_package_audit, unreal_project_audit, wasm_module_audit,
)
from wave26 import (
    bed_interval_audit, fasta_sequence_audit, fastq_quality_audit, genbank_record_audit,
    gfa_assembly_audit, gff3_annotation_audit, newick_tree_audit, pdb_structure_audit,
    sam_alignment_audit, sequence_alignment_audit, vcf_variant_audit,
)
from wave27 import (
    bagit_archive_audit, datacite_metadata_audit, frictionless_package_audit,
    iiif_manifest_audit, mets_package_audit, premis_event_audit, ro_crate_audit,
    stac_catalog_audit, tei_document_audit,
)
from wave28 import (
    dicom_privacy_audit, jp2_box_audit, las_pointcloud_audit, netcdf_classic_audit,
    nifti_header_audit, nwb_structure_audit, ocfl_object_audit, zarr_store_audit,
)
from wave30 import cog_geotiff_audit, ome_ngff_audit, parquet_metadata_audit
from wave31 import file_format_identify
from wave32 import cron_schedule_audit, pdf_ocr_searchable, rdf_graph_audit, shacl_validate
from wave33 import cosign_verify_blob, kubernetes_schema_validate, rego_policy_check, web_article_extract
from wave34 import iceberg_metadata_audit, mcap_recording_audit, onnx_model_audit, otel_trace_audit
from wave35 import (
    chat_dataset_audit, gguf_model_audit, hf_model_card_audit,
    promptfoo_config_audit, safetensors_audit, three_mf_package_audit,
)
from wave36 import (
    dvc_pipeline_manifest_audit, hf_dataset_card_audit, hf_tokenizer_audit,
    helm_chart_metadata_audit, mlflow_model_manifest_audit, ollama_modelfile_audit,
)

WORKER_URL = os.environ.get("NOLANE_WORKER_URL", "https://nolane-search.nolane-file.workers.dev").rstrip("/")
MAX_INPUT = 20 * 1024 * 1024
RUNNERS = {
    "image-ocr", "image-info", "image-clean-exif", "image-compress", "image-to-pdf",
    "qr-read", "pdf-text", "pdf-info", "audio-transcribe", "audio-info",
    "video-info", "video-thumbnail", "csv-profile", "json-format",
    "office-text", "archive-inspect", "file-hash", "text-clean", "subtitle-text", "html-text",
    "audio-normalize", "video-audio", "video-gif", "image-resize", "image-webp", "image-palette",
    "pdf-compress", "pdf-to-images", "epub-text", "sqlite-inspect", "yaml-format", "xml-format",
    "code-check", "video-contact-sheet", "video-compress", "audio-subtitles", "archive-safe-extract", "xlsx-profile", "xlsx-formula-report", "xlsx-to-markdown",
    "image-png", "csv-clean", "json-to-csv", "csv-to-xlsx", "xlsx-to-csv", "pdf-split", "audio-convert",
    "csv-to-json", "jsonl-format", "yaml-to-json", "xml-to-json", "sqlite-export", "xlsx-to-json",
    "pdf-extract-images", "archive-manifest", "text-stats", "image-grayscale",
    "pdf-merge", "pdf-metadata-clean", "pdf-outline", "image-contact-sheet", "image-duplicates", "csv-split", "csv-join", "json-schema", "json-to-yaml", "sqlite-integrity", "audio-silence-report", "video-silence-report", "video-frames", "subtitle-convert", "subtitle-audit", "text-deduplicate", "text-diff", "code-size-report",
    "pdf-rotate-cw","pdf-remove-blank","pdf-page-audit","image-favicon","image-trim-border","image-pixelate","image-diff",
    "audio-stereo-split","audio-metadata-clean","video-scene-frames","video-metadata-clean",
    "json-flatten-csv","csv-to-sqlite","log-insights","json-diff","text-join",
    "markdown-outline","markdown-links","markdown-toc","text-redact","text-extract","code-imports","code-todos","code-secret-scan","log-timeline",
    "repo-inventory","repo-dependencies","repo-license-report","repo-secret-scan","repo-todo-scan","repo-code-stats","repo-config-audit","repo-duplicates","repo-intelligence","repo-security-audit","repo-supply-chain",
    "text-translate", "language-detect", "text-uppercase", "text-lowercase", "text-title-case", "text-sort-lines", "text-reverse-lines", "text-number-lines", "text-remove-blank-lines", "text-wrap", "text-trim-lines", "text-extract-emails", "text-extract-urls", "text-extract-hashtags", "text-to-base64", "base64-to-text", "url-encode", "url-decode", "json-minify", "json-sort-keys",
    "text-slugify", "text-word-frequency", "text-extract-numbers", "text-extract-dates", "text-reverse-characters", "text-snake-case", "text-kebab-case", "text-camel-case", "text-swap-case", "text-extract-ipv4", "text-mask-emails", "text-mask-phones", "json-to-jsonl", "jsonl-to-json", "csv-to-tsv", "tsv-to-csv", "csv-to-markdown", "html-minify", "xml-minify", "text-remove-emoji",
    "text-collapse-whitespace", "text-remove-punctuation", "text-to-ascii", "text-html-escape", "text-html-unescape", "text-extract-mentions", "text-extract-hex-colors", "text-extract-phones", "text-dedupe-lines", "text-count-report", "text-quote-lines", "text-unquote-lines", "csv-transpose", "csv-sort-rows", "csv-dedupe-rows", "csv-to-xml", "csv-to-html", "json-sort-array", "json-remove-nulls", "json-to-html-table",
    "text-pascal-case", "text-constant-case", "text-dot-case", "text-initials", "text-normalize-unicode", "text-remove-control-chars", "text-remove-duplicate-words", "text-extract-markdown-links", "text-extract-markdown-headings", "text-extract-quotes", "text-paragraph-report", "json-flatten", "json-unflatten", "json-keys-report", "csv-remove-empty-rows", "csv-add-row-numbers", "csv-column-stats", "csv-normalize-headers", "csv-to-jsonl", "jsonl-to-csv",
    "text-indent-lines", "text-unindent-lines", "text-dedupe-paragraphs", "text-tokenize-words", "text-sentence-report", "text-line-length-report", "text-normalize-newlines", "text-remove-zero-width", "text-extract-file-paths", "text-sort-words", "html-extract-links", "html-extract-images", "html-extract-title", "html-sanitize", "html-seo-audit", "html-accessibility-audit", "html-link-audit", "html-form-audit", "html-image-audit", "xml-tree-report", "json-to-xml", "json-type-report", "json-escape-string", "json-unescape-string", "csv-unique-values",
    "text-sentence-case", "text-normalize-quotes", "text-normalize-dashes", "text-reverse-word-order", "text-extract-words", "text-extract-sentences", "text-dedupe-sentences", "text-remove-markdown-formatting", "text-markdown-toc", "text-markdown-code-blocks", "text-markdown-table-extract", "text-extract-numbered-lists", "text-join-hyphenated-lines", "text-strip-bom", "text-normalize-paragraph-spacing", "csv-schema-infer", "csv-duplicates-report", "csv-sample-rows", "json-array-stats", "json-canonicalize",
    "text-extract-todo-comments", "text-extract-markdown-images", "text-strip-markdown-frontmatter", "text-markdown-to-plain", "text-sort-unique-words", "text-word-to-lines", "text-join-lines", "text-extract-domains", "text-extract-uuids", "text-extract-semver", "text-extract-ipv6", "text-redact-secrets", "text-extract-comment-lines", "text-tabs-to-spaces", "text-escape-regex", "text-unescape-regex", "json-merge-objects", "json-array-dedupe", "json-array-to-lines", "csv-trim-cells", "csv-remove-empty-columns", "csv-empty-cell-report",
    "text-extract-mac-addresses",
    "text-extract-port-numbers",
    "text-normalize-path-separators",
    "text-extract-file-extensions",
    "text-escape-shell-argument",
    "text-sort-unique-lines",
    "text-normalize-unicode-nfkc",
    "csv-to-sql-inserts",
    "csv-to-yaml",
    "csv-empty-row-report",
    "csv-row-width-report",
    "json-remove-empty-values",
    "json-to-typescript",
    "json-nesting-report",
    "env-audit",
    "env-redact",
    "env-to-example",
    "ini-to-json",
    "ini-validate",
    "toml-to-json",
    "toml-validate",
    "properties-to-json",
    "dockerfile-audit",
    "docker-compose-audit",
    "requirements-audit",
    "package-json-audit",
    "gitignore-audit",
    "env-reference-report",
    "github-actions-audit",
    "kubernetes-manifest-audit",
    "terraform-audit",
    "nginx-config-audit",
    "apache-config-audit",
    "caddy-config-audit",
    "systemd-unit-audit",
    "shell-script-audit",
    "repo-test-map",
    "repo-test-quality",
    "repo-complexity-report",
    "repo-api-surface",
    "repo-docs-audit",
    "repo-migration-audit",
    "repo-runtime-risk",
    "repo-i18n-audit",

    "repo-env-contract",
    "repo-architecture-cycles",
    "repo-change-impact",
    "repo-api-spec-audit",
    "repo-container-audit",
    "repo-ci-reliability",
    "docx-audit", "pptx-audit", "csv-privacy-audit", "archive-security-audit",
    "xlsx-privacy-audit", "pdf-privacy-audit",
    "office-active-content-audit", "pdf-active-content-audit",
    "email-security-audit", "jwt-security-audit",
    "har-privacy-audit","ics-calendar-audit","vcard-privacy-audit","gpx-track-report","geojson-audit",
    "qr-code-generate","font-inspect","subtitle-fix","openapi-contract-audit","color-convert",
    "pcap-network-audit", "audio-tag-audit",
    "image-similarity-audit", "json-schema-validate",
    "epub-structure-audit",
    "markdown-quality-audit",
    "dns-zone-audit",
    "x509-certificate-audit",
    "rss-atom-audit",
    "sitemap-xml-audit",
    "robots-txt-audit",
    "jsonl-profile",
    "image-privacy-audit",
    "svg-safety-audit",
    "wcag-contrast-audit",
    "ssh-public-key-audit",
    "archive-checksum-manifest",
    "pdf-table-extract",
    "json-jmespath-query",
    "ip-network-report",
    "barcode-generate",
    "docx-to-markdown",
    "pptx-notes-extract",
    "fuzzy-match-report",
    "csv-to-parquet",
    "parquet-to-csv",
    "sqlglot-format",
    "sqlfluff-lint",
    "python-security-audit",
    "unit-convert",
    "mesh-inspect",
    "dxf-audit",
    "shapefile-audit",
    "gettext-catalog-audit",
    "notebook-audit",
    "notebook-strip-outputs",
    "heic-convert",
    "subtitle-quality-audit",
    "kml-to-geojson",
    "coordinate-transform",
    "html-structured-data-audit",
    "html-local-link-audit",
    "css-quality-audit",
    "gcode-audit", "midi-audit", "musicxml-audit", "bibtex-audit", "nmea-track-audit",
    "ansible-playbook-audit", "prometheus-rules-audit", "grafana-dashboard-audit",
    "hdf5-audit", "avro-schema-audit", "graphql-schema-audit", "protobuf-schema-audit",
    "odf-package-audit", "xliff-audit", "mbox-audit", "geopackage-audit", "mbtiles-audit", "openraster-audit", "krita-project-audit", "gltf-audit", "drawio-audit", "n8n-workflow-audit", "design-token-audit", "warc-archive-audit",
    "wasm-module-audit", "sarif-report-audit", "sbom-audit", "junit-xml-audit", "coverage-xml-audit", "fits-audit", "step-cad-audit", "otel-collector-audit", "godot-project-audit", "unity-package-audit", "unreal-project-audit",
    "fasta-sequence-audit", "fastq-quality-audit", "vcf-variant-audit", "sam-alignment-audit", "gff3-annotation-audit", "bed-interval-audit", "genbank-record-audit", "pdb-structure-audit", "gfa-assembly-audit", "newick-tree-audit", "sequence-alignment-audit",
    "bagit-archive-audit", "frictionless-package-audit", "ro-crate-audit", "iiif-manifest-audit", "datacite-metadata-audit", "mets-package-audit", "premis-event-audit", "stac-catalog-audit", "tei-document-audit",
    "ocfl-object-audit", "zarr-store-audit", "nifti-header-audit", "dicom-privacy-audit",
    "las-pointcloud-audit", "jp2-box-audit", "netcdf-classic-audit", "nwb-structure-audit",
    "ome-ngff-audit", "parquet-metadata-audit", "cog-geotiff-audit", "file-format-identify", "pdf-ocr-searchable", "rdf-graph-audit", "shacl-validate", "cron-schedule-audit", "web-article-extract", "rego-policy-check", "k8s-schema-validate", "cosign-verify-blob", "mcap-recording-audit", "iceberg-metadata-audit", "onnx-model-audit", "otel-trace-audit",
    "safetensors-audit",
    "gguf-model-audit",
    "hf-model-card-audit",
    "chat-dataset-audit",
    "promptfoo-config-audit",
    "three-mf-package-audit",
    "ollama-modelfile-audit",
    "hf-tokenizer-audit",
    "hf-dataset-card-audit",
    "mlflow-model-audit",
    "dvc-pipeline-audit",
    "helm-chart-audit",
}

GITHUB_SOURCE_PROCESSORS = {
    "repo-intelligence", "repo-inventory", "repo-dependencies", "repo-license-report", "repo-secret-scan", "repo-todo-scan", "repo-code-stats", "repo-config-audit", "repo-duplicates", "repo-security-audit", "repo-supply-chain", "repo-test-map", "repo-test-quality", "repo-complexity-report", "repo-api-surface", "repo-docs-audit", "repo-migration-audit", "repo-runtime-risk", "repo-i18n-audit",
    "repo-env-contract",
    "repo-architecture-cycles",
    "repo-change-impact",
    "repo-api-spec-audit",
    "repo-container-audit",
    "repo-ci-reliability",

}

PIPELINE_TRANSITIONS = {
    "image-ocr": {"text-clean"}, "qr-read": {"text-clean"}, "pdf-text": {"text-clean"},
    "office-text": {"text-clean"}, "html-text": {"text-clean"}, "subtitle-text": {"text-clean"},
    "audio-transcribe": {"text-clean"}, "epub-text": {"text-clean"},
    "video-audio": {"audio-normalize","audio-transcribe","audio-subtitles","audio-info","audio-convert"},
    "audio-convert": {"audio-transcribe","audio-subtitles","audio-info"},
    "audio-normalize": {"audio-transcribe","audio-subtitles","audio-info","audio-convert"},
    "csv-clean": {"csv-profile","csv-to-xlsx"},
    "json-to-csv": {"csv-clean","csv-profile","csv-to-xlsx"},
    "csv-to-xlsx": {"xlsx-profile","xlsx-to-csv","office-text"},
    "pdf-compress": {"pdf-text","pdf-info","pdf-to-images","pdf-split"},
    "image-to-pdf": {"pdf-text","pdf-info","pdf-compress","pdf-to-images","pdf-split"},
    "image-clean-exif": {"image-info","image-compress","image-png","image-webp","image-palette","image-ocr","qr-read","image-to-pdf"},
    "image-compress": {"image-info","image-png","image-webp","image-palette","image-ocr","qr-read","image-to-pdf"},
    "image-resize": {"image-info","image-png","image-webp","image-palette","image-ocr","qr-read","image-to-pdf"},
    "image-png": {"image-info","image-compress","image-webp","image-palette","image-ocr","qr-read","image-to-pdf"},
    "image-webp": {"image-info","image-compress","image-png","image-palette","image-ocr","qr-read","image-to-pdf"},
    "video-compress": {"video-info","video-thumbnail","video-audio","video-contact-sheet","video-gif"},
    "csv-to-json": {"json-format"}, "yaml-to-json": {"json-format"}, "xml-to-json": {"json-format"},
    "xlsx-to-json": {"json-format"}, "json-format": {"json-to-csv"},
    "pdf-extract-images": {"archive-inspect","archive-safe-extract"},
    "sqlite-export": {"archive-inspect","archive-safe-extract"},
    "archive-manifest": {"csv-profile","csv-clean","csv-to-xlsx"},
    "image-grayscale": {"image-info","image-ocr","qr-read","image-to-pdf","image-png","image-webp","image-compress","image-palette"},
    "pdf-merge": {"pdf-info","pdf-text","pdf-compress","pdf-to-images","pdf-split","pdf-extract-images","pdf-metadata-clean","pdf-outline"},
    "pdf-metadata-clean": {"pdf-info","pdf-text","pdf-compress","pdf-to-images","pdf-split","pdf-extract-images","pdf-outline"},
    "pdf-outline": {"text-clean"},
    "image-contact-sheet": {"image-info","image-clean-exif","image-compress","image-resize","image-webp","image-palette","image-ocr","qr-read","image-to-pdf","image-grayscale","image-png"},
    "image-duplicates": {"csv-profile","csv-clean","csv-to-xlsx","csv-to-json"},
    "csv-split": {"archive-inspect","archive-safe-extract","archive-manifest"},
    "csv-join": {"csv-clean","csv-profile","csv-to-xlsx","csv-to-json"},
    "json-schema": {"json-format"},
    "json-to-yaml": {"yaml-format"},
    "sqlite-integrity": {"text-clean"},
    "audio-silence-report": {"text-clean"},
    "video-silence-report": {"text-clean"},
    "video-frames": {"archive-inspect","archive-safe-extract","archive-manifest"},
    "subtitle-convert": {"subtitle-text"},
    "text-deduplicate": {"text-clean","text-stats","text-join"},
    "text-diff": {"text-clean","text-stats"},
    "code-size-report": {"text-clean","text-stats"},
    "text-clean": {"text-stats","text-deduplicate"},
    "text-stats": {"text-clean", "text-join"},
    "pdf-rotate-cw": {"pdf-info","pdf-text","pdf-compress","pdf-to-images","pdf-split","pdf-extract-images","pdf-metadata-clean","pdf-outline","pdf-remove-blank"},
    "pdf-remove-blank": {"pdf-info","pdf-text","pdf-compress","pdf-to-images","pdf-split","pdf-extract-images","pdf-metadata-clean","pdf-outline"},
    "image-trim-border": {"image-info","image-compress","image-resize","image-png","image-webp","image-palette","image-ocr","qr-read","image-to-pdf","image-pixelate"},
    "image-pixelate": {"image-info","image-png","image-webp","image-compress","image-to-pdf"},
    "image-diff": {"archive-inspect","archive-safe-extract","archive-manifest"},
    "audio-stereo-split": {"archive-inspect","archive-safe-extract","archive-manifest"},
    "audio-metadata-clean": {"audio-info","audio-normalize","audio-transcribe","audio-subtitles","audio-convert"},
    "video-scene-frames": {"archive-inspect","archive-safe-extract","archive-manifest"},
    "video-metadata-clean": {"video-info","video-thumbnail","video-audio","video-contact-sheet","video-gif","video-silence-report","video-frames","video-scene-frames"},
    "json-flatten-csv": {"csv-profile","csv-clean","csv-to-xlsx","csv-to-sqlite","csv-join"},
    "csv-to-sqlite": {"sqlite-inspect","sqlite-integrity","sqlite-export"},
    "log-insights": {"text-clean","text-stats","text-deduplicate"},
    "json-diff": {"text-clean","text-stats","text-deduplicate"},
        "xlsx-formula-report": {"text-clean","text-stats"},
    "xlsx-to-markdown": {"markdown-outline","markdown-links","markdown-toc","text-clean"},
    "subtitle-audit": {"subtitle-text","text-clean","text-stats"},
    "image-favicon": {"image-info","file-hash"},
    "pdf-page-audit": {"text-clean","text-stats"},
    "markdown-toc": {"markdown-outline","markdown-links","text-clean"},
"markdown-outline": {"text-clean","text-stats"},
    "markdown-links": {"csv-profile","csv-clean","csv-to-xlsx","csv-to-json"},
    "text-redact": {"text-clean","text-stats","text-deduplicate"},
    "text-extract": {"csv-profile","csv-clean","csv-to-xlsx"},
    "code-imports": {"text-clean","text-stats"},
    "code-todos": {"text-clean","text-stats","text-deduplicate"},
    "code-secret-scan": {"text-clean","text-stats"},
    "log-timeline": {"text-clean","text-stats"},
    "repo-inventory": {"text-clean","text-stats"},
    "repo-dependencies": {"text-clean","text-stats"},
    "repo-license-report": {"text-clean","text-stats"},
    "repo-secret-scan": {"text-clean","text-stats"},
    "repo-todo-scan": {"text-clean","text-stats","text-deduplicate"},
    "repo-code-stats": {"text-clean","text-stats"},
    "repo-config-audit": {"text-clean","text-stats"},
    "repo-duplicates": {"csv-profile","csv-clean","csv-to-xlsx","csv-to-json"},
    "repo-security-audit": {"archive-inspect","archive-safe-extract","archive-manifest"},
    "repo-supply-chain": {"archive-inspect","archive-safe-extract","archive-manifest"},
    "text-translate": {"text-clean","text-stats","text-deduplicate"},
    "language-detect": {"text-clean","text-stats"},
    "text-uppercase": {"text-clean","text-stats","text-deduplicate"},
    "text-lowercase": {"text-clean","text-stats","text-deduplicate"},
    "text-title-case": {"text-clean","text-stats","text-deduplicate"},
    "text-sort-lines": {"text-clean","text-stats","text-deduplicate"},
    "text-reverse-lines": {"text-clean","text-stats"},
    "text-number-lines": {"text-clean","text-stats"},
    "text-remove-blank-lines": {"text-clean","text-stats","text-deduplicate"},
    "text-wrap": {"text-clean","text-stats"},
    "text-trim-lines": {"text-clean","text-stats","text-deduplicate"},
    "text-extract-emails": {"text-deduplicate","text-stats"},
    "text-extract-urls": {"text-deduplicate","text-stats"},
    "text-extract-hashtags": {"text-deduplicate","text-stats"},
    "text-to-base64": {"base64-to-text"},
    "base64-to-text": {"text-clean","text-stats"},
    "url-encode": {"url-decode"},
    "url-decode": {"text-clean","text-stats"},
    "json-minify": {"json-format","json-schema","json-to-csv"},
    "json-sort-keys": {"json-format","json-schema","json-to-csv"},
    "text-slugify": {"text-clean","text-stats","text-deduplicate"},
    "text-word-frequency": {"text-clean","text-stats"},
    "text-extract-numbers": {"text-deduplicate","text-stats"},
    "text-extract-dates": {"text-deduplicate","text-stats"},
    "text-reverse-characters": {"text-clean","text-stats"},
    "text-snake-case": {"text-clean","text-stats","text-deduplicate"},
    "text-kebab-case": {"text-clean","text-stats","text-deduplicate"},
    "text-camel-case": {"text-clean","text-stats","text-deduplicate"},
    "text-swap-case": {"text-clean","text-stats"},
    "text-extract-ipv4": {"text-deduplicate","text-stats"},
    "text-mask-emails": {"text-clean","text-stats"},
    "text-mask-phones": {"text-clean","text-stats"},
    "json-to-jsonl": {"jsonl-format"},
    "jsonl-to-json": {"json-format","json-minify","json-sort-keys","json-to-csv"},
    "csv-to-tsv": {"tsv-to-csv"},
    "tsv-to-csv": {"csv-profile","csv-clean","csv-to-json"},
    "csv-to-markdown": {"text-clean","text-stats"},
    "html-minify": {"html-text","text-clean"},
    "xml-minify": {"xml-format","xml-to-json"},
    "text-remove-emoji": {"text-clean","text-stats"},
    "text-collapse-whitespace": {"text-clean","text-stats"},
    "text-remove-punctuation": {"text-clean","text-stats","text-deduplicate"},
    "text-to-ascii": {"text-clean","text-stats","text-deduplicate"},
    "text-html-escape": {"text-html-unescape","text-clean"},
    "text-html-unescape": {"text-clean","text-stats"},
    "text-extract-mentions": {"text-deduplicate","text-stats"},
    "text-extract-hex-colors": {"text-deduplicate","text-stats"},
    "text-extract-phones": {"text-deduplicate","text-stats"},
    "text-dedupe-lines": {"text-stats","text-clean"},
    "text-count-report": {"text-clean","text-stats"},
    "text-quote-lines": {"text-unquote-lines"},
    "text-unquote-lines": {"text-clean","text-stats"},
    "csv-transpose": {"csv-profile","csv-clean","csv-to-xlsx","csv-to-json"},
    "csv-sort-rows": {"csv-profile","csv-clean","csv-to-xlsx","csv-to-json"},
    "csv-dedupe-rows": {"csv-profile","csv-clean","csv-to-xlsx","csv-to-json"},
    "csv-to-xml": {"xml-format","xml-to-json","xml-minify"},
    "csv-to-html": {"html-minify","html-text"},
    "json-sort-array": {"json-format","json-minify","json-to-jsonl","json-to-csv"},
    "json-remove-nulls": {"json-format","json-minify","json-sort-keys","json-to-csv"},
    "json-to-html-table": {"html-minify","html-text"},
    "text-pascal-case": {"text-clean","text-stats","text-deduplicate"},
    "text-constant-case": {"text-clean","text-stats","text-deduplicate"},
    "text-dot-case": {"text-clean","text-stats","text-deduplicate"},
    "text-initials": {"text-clean","text-stats"},
    "text-normalize-unicode": {"text-clean","text-stats","text-deduplicate"},
    "text-remove-control-chars": {"text-clean","text-stats"},
    "text-remove-duplicate-words": {"text-clean","text-stats"},
    "text-extract-markdown-links": {"text-deduplicate","text-stats"},
    "text-extract-markdown-headings": {"text-deduplicate","text-stats"},
    "text-extract-quotes": {"text-deduplicate","text-stats"},
    "text-paragraph-report": {"text-clean","text-stats"},
    "json-flatten": {"json-unflatten","json-format","json-minify"},
    "json-unflatten": {"json-format","json-minify","json-sort-keys"},
    "json-keys-report": {"json-format","json-sort-keys"},
    "csv-remove-empty-rows": {"csv-profile","csv-clean","csv-normalize-headers"},
    "csv-add-row-numbers": {"csv-profile","csv-clean","csv-normalize-headers"},
    "csv-column-stats": {"csv-profile","csv-clean"},
    "csv-normalize-headers": {"csv-profile","csv-clean","csv-to-jsonl","csv-to-tsv"},
    "csv-to-jsonl": {"jsonl-to-csv","jsonl-format"},
    "jsonl-to-csv": {"csv-profile","csv-clean","csv-normalize-headers"},
    "text-indent-lines": {"text-unindent-lines","text-clean","text-stats"},
    "text-unindent-lines": {"text-indent-lines","text-clean","text-stats"},
    "text-dedupe-paragraphs": {"text-clean","text-stats"},
    "text-tokenize-words": {"text-word-frequency","text-sort-words","text-stats"},
    "text-sentence-report": {"text-paragraph-report","text-stats"},
    "text-line-length-report": {"text-clean","text-stats"},
    "text-normalize-newlines": {"text-clean","text-stats"},
    "text-remove-zero-width": {"text-clean","text-stats"},
    "text-extract-file-paths": {"text-deduplicate","text-stats"},
    "text-sort-words": {"text-word-frequency","text-stats"},
    "html-extract-links": {"html-text","text-clean"},
    "html-extract-images": {"html-text","text-clean"},
    "html-extract-title": {"text-clean","text-stats"},
    "html-sanitize": {"html-minify","html-text"},
    "html-seo-audit": {"text-clean","text-stats"},
    "html-accessibility-audit": {"text-clean","text-stats"},
    "html-link-audit": {"text-clean","text-stats"},
    "html-form-audit": {"text-clean","text-stats"},
    "html-image-audit": {"text-clean","text-stats"},
    "xml-tree-report": {"text-clean","text-stats"},
    "json-to-xml": {"xml-minify","xml-format","xml-to-json"},
    "json-type-report": {"json-format","json-sort-keys"},
    "json-escape-string": {"json-unescape-string","json-format"},
    "json-unescape-string": {"text-clean","text-stats"},
    "csv-unique-values": {"csv-profile","csv-clean","text-deduplicate"},
    "text-sentence-case": {"text-clean","text-stats","text-deduplicate"},
    "text-normalize-quotes": {"text-clean","text-stats"},
    "text-normalize-dashes": {"text-clean","text-stats"},
    "text-reverse-word-order": {"text-clean","text-stats"},
    "text-extract-words": {"text-deduplicate","text-stats"},
    "text-extract-sentences": {"text-deduplicate","text-stats"},
    "text-dedupe-sentences": {"text-stats","text-clean"},
    "text-remove-markdown-formatting": {"text-clean","text-stats","html-text"},
    "text-markdown-toc": {"text-clean","text-stats"},
    "text-markdown-code-blocks": {"code-check","code-size-report"},
    "text-markdown-table-extract": {"csv-profile","csv-clean","csv-to-jsonl","csv-to-xlsx"},
    "text-extract-numbered-lists": {"text-deduplicate","text-stats"},
    "text-join-hyphenated-lines": {"text-clean","text-stats"},
    "text-strip-bom": {"text-clean","text-stats"},
    "text-normalize-paragraph-spacing": {"text-clean","text-stats"},
    "csv-schema-infer": {"csv-profile","csv-clean","csv-column-stats"},
    "csv-duplicates-report": {"csv-dedupe-rows","csv-clean","csv-profile"},
    "csv-sample-rows": {"csv-profile","csv-clean","csv-column-stats"},
    "json-array-stats": {"json-format","json-keys-report","json-schema"},
    "json-canonicalize": {"json-format","json-minify","json-sort-keys"},
    "text-extract-todo-comments": {"code-todos","text-clean","text-stats"},
    "text-extract-markdown-images": {"html-extract-images","text-clean","text-stats"},
    "text-strip-markdown-frontmatter": {"text-markdown-to-plain","markdown-outline","text-clean"},
    "text-markdown-to-plain": {"text-clean","text-stats","text-dedupe-lines"},
    "text-sort-unique-words": {"text-word-frequency","text-stats"},
    "text-word-to-lines": {"text-sort-lines","text-dedupe-lines","text-stats"},
    "text-join-lines": {"text-clean","text-stats","text-wrap"},
    "text-extract-domains": {"text-deduplicate","text-stats"},
    "text-extract-uuids": {"text-deduplicate","text-stats"},
    "text-extract-semver": {"text-deduplicate","text-stats"},
    "text-extract-ipv6": {"text-deduplicate","text-stats"},
    "text-redact-secrets": {"text-clean","text-stats"},
    "text-extract-comment-lines": {"code-todos","text-deduplicate","text-stats"},
    "text-tabs-to-spaces": {"text-clean","text-stats"},
    "text-escape-regex": {"text-clean","text-stats"},
    "text-unescape-regex": {"text-clean","text-stats"},
    "json-merge-objects": {"json-canonicalize","json-format","json-schema"},
    "json-array-dedupe": {"json-sort-array","json-canonicalize","json-format"},
    "json-array-to-lines": {"text-clean","text-stats"},
    "csv-trim-cells": {"csv-profile","csv-clean","csv-schema-infer"},
    "csv-remove-empty-columns": {"csv-profile","csv-schema-infer","csv-clean"},
    "csv-empty-cell-report": {"csv-profile","csv-schema-infer"},
    "text-extract-mac-addresses": {"text-deduplicate", "text-stats"},
    "text-extract-port-numbers": {"text-deduplicate", "text-stats"},
    "text-normalize-path-separators": {"text-clean", "text-stats"},
    "text-extract-file-extensions": {"text-deduplicate", "text-stats"},
    "text-escape-shell-argument": {"text-clean", "text-stats"},
    "text-sort-unique-lines": {"text-clean", "text-stats"},
    "text-normalize-unicode-nfkc": {"text-clean", "text-stats"},
    "csv-to-sql-inserts": set(),
    "yaml-format": {"yaml-to-json", "code-check"},
    "csv-to-yaml": {"yaml-format", "yaml-to-json"},
    "csv-empty-row-report": {"text-clean", "text-stats"},
    "csv-row-width-report": {"text-clean", "text-stats"},
    "json-remove-empty-values": {"json-format", "json-canonicalize", "json-schema"},
    "json-to-typescript": {"code-check", "text-clean"},
    "json-nesting-report": {"text-clean", "text-stats"},
    "env-audit": {"env-redact", "env-to-example", "text-stats"},
    "env-redact": {"env-audit", "text-clean", "text-stats"},
    "env-to-example": {"env-audit", "env-redact", "text-clean"},
    "ini-to-json": {"json-format", "json-schema"},
    "ini-validate": {"text-clean", "text-stats"},
    "toml-to-json": {"json-format", "json-schema"},
    "toml-validate": {"text-clean", "text-stats"},
    "properties-to-json": {"json-format", "json-schema"},
    "dockerfile-audit": {"text-clean", "text-stats"},
    "docker-compose-audit": {"text-clean", "text-stats"},
    "requirements-audit": {"text-clean", "text-stats"},
    "package-json-audit": {"json-format", "json-schema"},
    "gitignore-audit": {"text-clean", "text-stats"},
    "env-reference-report": {"text-clean", "text-stats"},

    "github-actions-audit": {"text-clean", "text-stats"},
    "kubernetes-manifest-audit": {"text-clean", "text-stats"},
    "terraform-audit": {"text-clean", "text-stats"},
    "nginx-config-audit": {"text-clean", "text-stats"},
    "apache-config-audit": {"text-clean", "text-stats"},
    "caddy-config-audit": {"text-clean", "text-stats"},
    "systemd-unit-audit": {"text-clean", "text-stats"},
    "shell-script-audit": {"text-clean", "text-stats"},
    "repo-test-map": {"text-clean", "text-stats"},
    "repo-test-quality": {"text-clean", "text-stats"},
    "repo-complexity-report": {"text-clean", "text-stats"},
    "repo-api-surface": {"text-clean", "text-stats"},
    "repo-docs-audit": {"text-clean", "text-stats"},
    "repo-migration-audit": {"text-clean", "text-stats"},
    "repo-runtime-risk": {"text-clean", "text-stats"},
    "repo-i18n-audit": {"text-clean", "text-stats"},

    "repo-env-contract": {"text-clean", "text-stats"},
    "repo-architecture-cycles": {"text-clean", "text-stats"},
    "repo-change-impact": {"text-clean", "text-stats"},
    "repo-api-spec-audit": {"text-clean", "text-stats"},
    "repo-container-audit": {"text-clean", "text-stats"},
    "repo-ci-reliability": {"text-clean", "text-stats"},
    "docx-audit": {"text-clean", "text-stats"},
    "pptx-audit": {"text-clean", "text-stats"},
    "csv-privacy-audit": {"text-clean", "text-stats"},
    "archive-security-audit": {"text-clean", "text-stats"},
    "xlsx-privacy-audit": {"text-clean", "text-stats"},
    "pdf-privacy-audit": {"text-clean", "text-stats"},
    "office-active-content-audit": {"text-clean", "text-stats"},
    "pdf-active-content-audit": {"text-clean", "text-stats"},
    "email-security-audit": {"text-clean", "text-stats"},
    "jwt-security-audit": {"text-clean", "text-stats"},
    "csv-to-sql-inserts": set(),
    "har-privacy-audit":{"text-clean","text-stats"},
    "ics-calendar-audit":{"text-clean","text-stats"},
    "vcard-privacy-audit":{"text-clean","text-stats"},
    "gpx-track-report":{"text-clean","text-stats"},
    "geojson-audit":{"text-clean","text-stats"},
    "qr-code-generate":{"image-info","image-ocr","qr-read","image-palette","image-to-pdf","image-compress"},
    "font-inspect":{"text-clean","text-stats"},
    "subtitle-fix":{"subtitle-audit","subtitle-convert","subtitle-text"},
    "openapi-contract-audit":{"text-clean","text-stats"},
    "color-convert":{"text-clean","text-stats"},
    "pcap-network-audit":{"text-clean","text-stats"},
    "audio-tag-audit":{"text-clean","text-stats"},
    "image-similarity-audit":{"csv-profile","csv-clean","csv-to-xlsx","csv-to-json"},
    "json-schema-validate":{"text-clean","text-stats"},
    "epub-structure-audit":{"text-clean","text-stats"},
    "markdown-quality-audit":{"text-clean","text-stats"},
    "dns-zone-audit":{"text-clean","text-stats"},
    "x509-certificate-audit":{"text-clean","text-stats"},
    "rss-atom-audit":{"text-clean","text-stats"},
    "sitemap-xml-audit":{"text-clean","text-stats"},
    "robots-txt-audit":{"text-clean","text-stats"},
    "jsonl-profile":{"text-clean","text-stats"},
    "image-privacy-audit":{"text-clean","text-stats"},
    "svg-safety-audit":{"text-clean","text-stats"},
    "wcag-contrast-audit":{"text-clean","text-stats"},
    "ssh-public-key-audit":{"text-clean","text-stats"},
    "archive-checksum-manifest":{"csv-profile","csv-clean","csv-to-xlsx","csv-to-json"},
    "pdf-table-extract":{"archive-inspect","archive-manifest"},
    "json-jmespath-query":{"json-format","json-to-csv"},
    "ip-network-report":{"csv-profile","csv-clean","csv-to-xlsx","csv-to-json","csv-to-parquet"},
    "barcode-generate":{"archive-inspect","archive-safe-extract","archive-manifest"},
    "docx-to-markdown":{"markdown-quality-audit","markdown-outline","markdown-links","markdown-toc","text-clean"},
    "pptx-notes-extract":{"text-clean","text-stats","text-translate"},
    "fuzzy-match-report":{"csv-profile","csv-clean","csv-to-xlsx","csv-to-json","csv-to-parquet"},
    "csv-to-parquet":{"parquet-to-csv"},
    "parquet-to-csv":{"csv-profile","csv-clean","csv-to-xlsx","csv-to-json","csv-to-parquet"},
    "sqlglot-format":{"sqlfluff-lint"},
    "heic-convert":{"image-info","image-clean-exif","image-compress","image-resize","image-webp","image-palette"},
    "kml-to-geojson":{"geojson-audit"},
    "coordinate-transform":{"geojson-audit"},
    "html-local-link-audit":{"csv-profile","csv-clean","csv-to-xlsx","csv-to-json","csv-to-parquet"},
    "subtitle-quality-audit":{"csv-profile","csv-clean","csv-to-xlsx","csv-to-json","csv-to-parquet"},
    "unit-convert":{"csv-profile","csv-clean","csv-to-xlsx","csv-to-json","csv-to-parquet"},
    "gcode-audit":{"text-clean","text-stats"},
    "midi-audit":{"text-clean","text-stats"},
    "musicxml-audit":{"text-clean","text-stats"},
    "bibtex-audit":{"text-clean","text-stats"},
    "nmea-track-audit":{"text-clean","text-stats"},
    "ansible-playbook-audit":{"text-clean","text-stats"},
    "prometheus-rules-audit":{"text-clean","text-stats"},
    "grafana-dashboard-audit":{"text-clean","text-stats"},
    "hdf5-audit":{"text-clean","text-stats"},
    "avro-schema-audit":{"text-clean","text-stats"},
    "graphql-schema-audit":{"text-clean","text-stats"},
    "protobuf-schema-audit":{"text-clean","text-stats"},
    "odf-package-audit":{"text-clean","text-stats"},
    "xliff-audit":{"text-clean","text-stats"},
    "mbox-audit":{"text-clean","text-stats"},
    "geopackage-audit":{"text-clean","text-stats"},
    "mbtiles-audit":{"text-clean","text-stats"},
    "openraster-audit":{"text-clean","text-stats"},
    "krita-project-audit":{"text-clean","text-stats"},
    "gltf-audit":{"text-clean","text-stats"},
    "drawio-audit":{"text-clean","text-stats"},
    "n8n-workflow-audit":{"text-clean","text-stats"},
    "design-token-audit":{"text-clean","text-stats"},
    "warc-archive-audit":{"text-clean","text-stats"},
    "wasm-module-audit":{"text-clean","text-stats"},
    "sarif-report-audit":{"text-clean","text-stats"},
    "sbom-audit":{"text-clean","text-stats"},
    "junit-xml-audit":{"text-clean","text-stats"},
    "coverage-xml-audit":{"text-clean","text-stats"},
    "fits-audit":{"text-clean","text-stats"},
    "step-cad-audit":{"text-clean","text-stats"},
    "otel-collector-audit":{"text-clean","text-stats"},
    "godot-project-audit":{"text-clean","text-stats"},
    "unity-package-audit":{"text-clean","text-stats"},
    "unreal-project-audit":{"text-clean","text-stats"},
    "fasta-sequence-audit":{"text-clean","text-stats"},
    "fastq-quality-audit":{"text-clean","text-stats"},
    "vcf-variant-audit":{"text-clean","text-stats"},
    "sam-alignment-audit":{"text-clean","text-stats"},
    "gff3-annotation-audit":{"text-clean","text-stats"},
    "bed-interval-audit":{"text-clean","text-stats"},
    "genbank-record-audit":{"text-clean","text-stats"},
    "pdb-structure-audit":{"text-clean","text-stats"},
    "gfa-assembly-audit":{"text-clean","text-stats"},
    "newick-tree-audit":{"text-clean","text-stats"},
    "sequence-alignment-audit":{"text-clean","text-stats"},
    "bagit-archive-audit":{"text-clean","text-stats"},
    "frictionless-package-audit":{"text-clean","text-stats"},
    "ro-crate-audit":{"text-clean","text-stats"},
    "iiif-manifest-audit":{"text-clean","text-stats"},
    "datacite-metadata-audit":{"text-clean","text-stats"},
    "mets-package-audit":{"text-clean","text-stats"},
    "premis-event-audit":{"text-clean","text-stats"},
    "stac-catalog-audit":{"text-clean","text-stats"},
    "tei-document-audit":{"text-clean","text-stats"},
    "ocfl-object-audit":{"text-clean","text-stats"},
    "zarr-store-audit":{"text-clean","text-stats"},
    "nifti-header-audit":{"text-clean","text-stats"},
    "dicom-privacy-audit":{"text-clean","text-stats"},
    "las-pointcloud-audit":{"text-clean","text-stats"},
    "jp2-box-audit":{"text-clean","text-stats"},
    "netcdf-classic-audit":{"text-clean","text-stats"},
    "nwb-structure-audit":{"text-clean","text-stats"},
    "ome-ngff-audit":{"text-clean","text-stats"},
    "parquet-metadata-audit":{"text-clean","text-stats"},
    "cog-geotiff-audit":{"text-clean","text-stats"},
    "file-format-identify":{"text-clean","text-stats"},
    "pdf-ocr-searchable":{"pdf-text","pdf-info","pdf-compress","pdf-to-images","pdf-split"},
    "rdf-graph-audit":{"text-clean","text-stats"},
    "shacl-validate":{"text-clean","text-stats"},
    "cron-schedule-audit":{"text-clean","text-stats"},
    "web-article-extract":{"text-clean","text-stats"},
    "rego-policy-check":{"text-clean","text-stats"},
    "k8s-schema-validate":{"text-clean","text-stats"},
    "cosign-verify-blob":{"text-clean","text-stats"},
    "mcap-recording-audit":{"text-clean","text-stats"},
    "iceberg-metadata-audit":{"text-clean","text-stats"},
    "onnx-model-audit":{"text-clean","text-stats"},
    "otel-trace-audit":{"text-clean","text-stats"},
    "safetensors-audit":{"text-clean","text-stats"},
    "gguf-model-audit":{"text-clean","text-stats"},
    "hf-model-card-audit":{"text-clean","text-stats"},
    "chat-dataset-audit":{"text-clean","text-stats"},
    "promptfoo-config-audit":{"text-clean","text-stats"},
    "three-mf-package-audit":{"text-clean","text-stats"},
    "ollama-modelfile-audit":{"text-clean","text-stats"},
    "hf-tokenizer-audit":{"text-clean","text-stats"},
    "hf-dataset-card-audit":{"text-clean","text-stats"},
    "mlflow-model-audit":{"text-clean","text-stats"},
    "dvc-pipeline-audit":{"text-clean","text-stats"},
    "helm-chart-audit":{"text-clean","text-stats"},
}

MULTI_INPUT_TOOLS = {"text-join"}
MAX_DAG_PARENTS = 3
TEXT_OUTPUT_TOOLS = {"image-ocr","qr-read","pdf-text","office-text","html-text","subtitle-text","audio-transcribe","epub-text","pdf-outline","sqlite-integrity","audio-silence-report","video-silence-report","code-size-report","text-stats","log-insights","json-diff","markdown-outline","code-imports","code-todos","code-secret-scan","log-timeline","repo-inventory","repo-dependencies","repo-license-report","repo-secret-scan","repo-todo-scan","repo-code-stats","repo-config-audit","repo-test-map","repo-test-quality","repo-complexity-report","repo-api-surface","repo-docs-audit","repo-migration-audit","repo-runtime-risk","repo-i18n-audit","repo-env-contract","repo-architecture-cycles","repo-change-impact","repo-api-spec-audit","repo-container-audit","repo-ci-reliability","docx-audit","pptx-audit","csv-privacy-audit","archive-security-audit","xlsx-privacy-audit","pdf-privacy-audit","office-active-content-audit","pdf-active-content-audit","email-security-audit","jwt-security-audit","har-privacy-audit","ics-calendar-audit","vcard-privacy-audit","gpx-track-report","geojson-audit","font-inspect","openapi-contract-audit","color-convert","pcap-network-audit","audio-tag-audit","json-schema-validate","epub-structure-audit","markdown-quality-audit","dns-zone-audit","x509-certificate-audit","rss-atom-audit","sitemap-xml-audit","robots-txt-audit","jsonl-profile","image-privacy-audit","svg-safety-audit","wcag-contrast-audit","ssh-public-key-audit","sqlfluff-lint","python-security-audit","mesh-inspect","dxf-audit","shapefile-audit","gettext-catalog-audit","notebook-audit","html-structured-data-audit","css-quality-audit","gcode-audit","midi-audit","musicxml-audit","bibtex-audit","nmea-track-audit","ansible-playbook-audit","prometheus-rules-audit","grafana-dashboard-audit","hdf5-audit","avro-schema-audit","graphql-schema-audit","protobuf-schema-audit","odf-package-audit","xliff-audit","mbox-audit","geopackage-audit","mbtiles-audit","openraster-audit","krita-project-audit","gltf-audit","drawio-audit","n8n-workflow-audit","design-token-audit","warc-archive-audit","wasm-module-audit","sarif-report-audit","sbom-audit","junit-xml-audit","coverage-xml-audit","fits-audit","step-cad-audit","otel-collector-audit","godot-project-audit","unity-package-audit","unreal-project-audit","fasta-sequence-audit","fastq-quality-audit","vcf-variant-audit","sam-alignment-audit","gff3-annotation-audit","bed-interval-audit","genbank-record-audit","pdb-structure-audit","gfa-assembly-audit","newick-tree-audit","sequence-alignment-audit","bagit-archive-audit","frictionless-package-audit","ro-crate-audit","iiif-manifest-audit","datacite-metadata-audit","mets-package-audit","premis-event-audit","stac-catalog-audit","tei-document-audit","ocfl-object-audit","zarr-store-audit","nifti-header-audit","dicom-privacy-audit","las-pointcloud-audit","jp2-box-audit","netcdf-classic-audit","nwb-structure-audit","ome-ngff-audit","parquet-metadata-audit","cog-geotiff-audit","file-format-identify","rdf-graph-audit","shacl-validate","cron-schedule-audit","web-article-extract","rego-policy-check","k8s-schema-validate","cosign-verify-blob","mcap-recording-audit","iceberg-metadata-audit","onnx-model-audit","otel-trace-audit","safetensors-audit","gguf-model-audit","hf-model-card-audit","chat-dataset-audit","promptfoo-config-audit","three-mf-package-audit","ollama-modelfile-audit","hf-tokenizer-audit","hf-dataset-card-audit","mlflow-model-audit","dvc-pipeline-audit","helm-chart-audit"}
MAX_PIPELINE_STEPS = len(RUNNERS)
MAX_PIPELINE_OUTPUT = 45 * 1024 * 1024

def api_json(url: str, method="GET", data=None, token=None):
    headers = {"accept":"application/json", "user-agent":"Nolane-Tools-Runner/1.0"}
    body = None
    if token: headers["authorization"] = "Bearer " + token
    if data is not None:
        headers["content-type"] = "application/json"
        body = json.dumps(data, ensure_ascii=False).encode()
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            raw = response.read(2_000_000)
            return json.loads(raw.decode()) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read(1200).decode("utf-8", "replace")
        raise RuntimeError(f"API HTTP {exc.code}: {detail}") from exc

def validate_pipeline(job):
    steps = job.get("pipeline")
    if steps is None:
        steps = [{"toolId": job.get("toolId")}]
    if not isinstance(steps, list) or not 1 <= len(steps) <= MAX_PIPELINE_STEPS:
        raise RuntimeError("Pipeline must contain at least one step and cannot repeat a processor.")
    ids=[]
    for item in steps:
        if not isinstance(item,dict):
            raise RuntimeError("Invalid pipeline step.")
        tool_id=item.get("toolId")
        if tool_id not in RUNNERS or tool_id in ids:
            raise RuntimeError("Unknown or repeated pipeline processor.")
        ids.append(tool_id)
    if not ids or ids[0] != job.get("toolId"):
        raise RuntimeError("The first pipeline step must match the selected tool.")
    if any(tool_id in MULTI_INPUT_TOOLS for tool_id in ids):
        raise RuntimeError("Multi-input processors can only merge parent artifacts inside a DAG workflow.")
    for previous,current in zip(ids,ids[1:]):
        if current not in PIPELINE_TRANSITIONS.get(previous,set()):
            raise RuntimeError(f"Unsupported pipeline transition: {previous} -> {current}.")
    return [{"toolId":tool_id} for tool_id in ids]

def validate_dag(job):
    nodes=job.get("workflowDag")
    if not isinstance(nodes,list) or not 2<=len(nodes)<=12:
        raise RuntimeError("Workflow DAG must contain between 2 and 12 nodes.")
    by_id={}; clean=[]; roots=[]; children={}
    for index,item in enumerate(nodes):
        if not isinstance(item,dict):
            raise RuntimeError("Invalid DAG node.")
        node_id=str(item.get("id") or "").strip().lower()
        tool_id=item.get("toolId")
        if not re.fullmatch(r"[a-z][a-z0-9_-]{0,19}",node_id) or node_id in by_id:
            raise RuntimeError("Invalid or repeated DAG node ID.")
        if tool_id not in RUNNERS:
            raise RuntimeError("Unknown DAG processor: "+str(tool_id))
        dependencies=item.get("dependsOn")
        if not isinstance(dependencies,list):
            raise RuntimeError("DAG dependencies must be a list.")
        multi_input=tool_id in MULTI_INPUT_TOOLS
        if len(dependencies)>(MAX_DAG_PARENTS if multi_input else 1) or (multi_input and len(dependencies)<2):
            if multi_input:
                raise RuntimeError(f"{tool_id} must receive between 2 and {MAX_DAG_PARENTS} parent artifacts.")
            raise RuntimeError(f"{tool_id} accepts only one parent; text-join is the only multi-input DAG processor.")
        if not dependencies:
            roots.append(node_id)
        else:
            seen_parents=set()
            for parent_id in dependencies:
                if not isinstance(parent_id,str) or parent_id not in by_id or parent_id==node_id or parent_id in seen_parents:
                    raise RuntimeError("DAG dependencies must reference distinct earlier nodes.")
                seen_parents.add(parent_id)
                parent=by_id[parent_id]
                if tool_id not in PIPELINE_TRANSITIONS.get(parent["toolId"],set()):
                    raise RuntimeError(f"Unsupported DAG transition: {parent['toolId']} -> {tool_id}.")
                children[parent_id]=children.get(parent_id,0)+1
        node={"id":node_id,"toolId":tool_id,"dependsOn":list(dependencies),"reason":str(item.get("reason") or "")[:240]}
        by_id[node_id]=node; clean.append(node)
    if not roots:
        raise RuntimeError("DAG must contain at least one input root.")
    if len(roots)==1 and max(children.values() or [0])<2:
        raise RuntimeError("DAG must contain at least two independent branches.")
    if clean[0]["toolId"]!=job.get("toolId"):
        raise RuntimeError("The first DAG node must match the selected tool.")
    leaves=[node["id"] for node in clean if children.get(node["id"],0)==0]
    if not leaves:
        raise RuntimeError("DAG must retain at least one terminal output.")
    return clean
def load_job(path):
    job = json.loads(Path(path).read_text(encoding="utf-8")).get("job", {})
    if not re.fullmatch(r"[0-9a-f-]{36}", str(job.get("id","")), re.I) or job.get("toolId") not in RUNNERS:
        raise RuntimeError("Invalid or unsupported tool job.")
    if job.get("workflowDag") is not None:
        job["workflowDag"]=validate_dag(job)
        job["pipeline"]=[{"toolId":node["toolId"]} for node in job["workflowDag"]]
    else:
        job["pipeline"] = validate_pipeline(job)
    return job

def download_telegram(file_id, filename):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token: raise RuntimeError("Missing TELEGRAM_BOT_TOKEN.")
    info = api_json(f"https://api.telegram.org/bot{token}/getFile?{urllib.parse.urlencode({'file_id':file_id})}")
    if not info.get("ok"): raise RuntimeError(info.get("description","Telegram getFile failed"))
    item = info.get("result") or {}
    if int(item.get("file_size") or 0) > MAX_INPUT: raise RuntimeError("Input exceeds Telegram's 20 MB getFile limit.")
    rel = str(item.get("file_path") or "")
    if not rel or rel.startswith("/") or ".." in Path(rel).parts or "\\" in rel: raise RuntimeError("Unsafe Telegram file path.")
    url = f"https://api.telegram.org/file/bot{token}/{urllib.parse.quote(rel, safe='/')}"
    safe = re.sub(r"[^A-Za-z0-9._-]+","_",Path(filename or Path(rel).name or "upload.bin").name)[:100] or "upload.bin"
    input_root = Path(os.environ.get("RUNNER_TEMP","/tmp")) / "nolane-inputs"
    input_root.mkdir(parents=True, exist_ok=True)
    dest = input_root / safe
    size=0
    with urllib.request.urlopen(urllib.request.Request(url,headers={"user-agent":"Nolane-Tools-Runner/1.0"}),timeout=60) as response, dest.open("wb") as out:
        while True:
            chunk=response.read(1024*1024)
            if not chunk: break
            size += len(chunk)
            if size > MAX_INPUT: raise RuntimeError("Downloaded input exceeds 20 MB.")
            out.write(chunk)
    if not size: raise RuntimeError("The uploaded file is empty.")
    return dest

def tool_text(text, title):
    text = text.strip() or "Không phát hiện nội dung."
    if len(text) > 2800:
        out_root=Path(os.environ.get("RUNNER_TEMP","/tmp"))/"nolane-inputs"
        out_root.mkdir(parents=True,exist_ok=True)
        out=out_root/f"nolane-result-{threading.get_ident()}.txt"
        out.write_text(text,encoding="utf-8")
        return {"summary":f"{title}: hoàn tất, {len(text):,} ký tự. Toàn bộ kết quả được gửi kèm dưới dạng TXT.","output_path":str(out)}
    return {"summary":f"{title}\n\n{text}","output_path":""}

def cmd(name,args,timeout=180):
    exe=shutil.which(name)
    if not exe: raise RuntimeError(f"Missing runner dependency: {name}")
    return subprocess.run([exe,*args],check=True,capture_output=True,text=True,timeout=timeout).stdout.strip()

def image_ocr(p):
    from PIL import Image,ImageOps
    import pytesseract
    with Image.open(p) as raw:
        im=ImageOps.exif_transpose(raw).convert("RGB")
        im.thumbnail((9000,9000))
        text=pytesseract.image_to_string(im,lang="vie+eng",config="--psm 6")
    return tool_text(text,"OCR Việt–Anh")

def image_info(p):
    from PIL import Image
    with Image.open(p) as im:
        exif=im.getexif()
        lines=[f"File: {p.name}",f"Format: {im.format}",f"Size: {im.width} × {im.height}",f"Mode: {im.mode}",f"Bytes: {p.stat().st_size:,}",f"EXIF keys: {', '.join(map(str,exif.keys())) if exif else 'none'}"]
        for k,label in ((271,"Camera"),(272,"Model"),(274,"Orientation"),(306,"DateTime")):
            if exif.get(k): lines.append(f"{label}: {str(exif.get(k))[:100]}")
    return tool_text("\n".join(lines),"Image inspector")

def image_clean(p):
    from PIL import Image,ImageOps
    out=p.with_name(p.stem+"-clean.jpg")
    with Image.open(p) as im: ImageOps.exif_transpose(im).convert("RGB").save(out,"JPEG",quality=94,optimize=True)
    return {"summary":"Đã tạo JPEG mới, loại bỏ EXIF/GPS metadata; file gốc được giữ nguyên.","output_path":str(out)}

def image_compress(p):
    from PIL import Image,ImageOps
    out=p.with_name(p.stem+"-compressed.jpg")
    with Image.open(p) as im: ImageOps.exif_transpose(im).convert("RGB").save(out,"JPEG",quality=82,optimize=True,progressive=True)
    reduction=(1-out.stat().st_size/max(1,p.stat().st_size))*100
    return {"summary":f"Đã nén ảnh: {p.stat().st_size:,} → {out.stat().st_size:,} bytes ({reduction:.1f}% thay đổi).","output_path":str(out)}

def image_pdf(p):
    from PIL import Image,ImageOps
    out=p.with_suffix(".pdf")
    with Image.open(p) as im: ImageOps.exif_transpose(im).convert("RGB").save(out,"PDF",resolution=150)
    return {"summary":"Đã chuyển ảnh thành PDF một trang.","output_path":str(out)}

def qr_read(p):
    from PIL import Image
    from pyzbar.pyzbar import decode
    with Image.open(p) as im: found=decode(im)
    if not found: return tool_text("Không tìm thấy QR/barcode có thể giải mã.","QR / Barcode")
    return tool_text("\n".join(f"{i}. {x.type}: {x.data.decode('utf-8','replace')}" for i,x in enumerate(found,1)),"QR / Barcode")

def pdf_text(p):
    import fitz
    from PIL import Image
    import pytesseract
    doc=fitz.open(p)
    if doc.page_count>120: raise RuntimeError("PDF quá 120 trang. Hãy tách tài liệu.")
    pages=[]
    for n,page in enumerate(doc,1):
        txt=page.get_text("text").strip()
        if not txt:
            pix=page.get_pixmap(matrix=fitz.Matrix(1.6,1.6),alpha=False)
            im=Image.frombytes("RGB",[pix.width,pix.height],pix.samples)
            txt=pytesseract.image_to_string(im,lang="vie+eng",config="--psm 3").strip()
        if txt: pages.append(f"--- Trang {n} ---\n{txt}")
    return tool_text("\n\n".join(pages),"PDF text extraction · OCR scan fallback")

def pdf_info(p):
    import fitz
    doc=fitz.open(p); meta=doc.metadata or {}
    lines=[f"File: {p.name}",f"Pages: {doc.page_count}",f"Bytes: {p.stat().st_size:,}"]
    for k in ("title","author","subject","creator","producer","creationDate","modDate"):
        if meta.get(k): lines.append(f"{k}: {str(meta[k])[:200]}")
    if doc.page_count: lines.append(f"First page: {doc[0].rect.width:.1f} × {doc[0].rect.height:.1f} pt")
    return tool_text("\n".join(lines),"PDF inspector")

def ffprobe(p):
    return json.loads(cmd("ffprobe",["-v","error","-show_format","-show_streams","-of","json",str(p)],120))

def audio_info(p):
    data=ffprobe(p); fmt=data.get("format",{})
    lines=[f"File: {p.name}",f"Format: {fmt.get('format_name')}",f"Duration: {float(fmt.get('duration') or 0):.2f}s",f"Bitrate: {fmt.get('bit_rate','?')}",f"Bytes: {p.stat().st_size:,}"]
    for s in data.get("streams",[]):
        if s.get("codec_type")=="audio": lines.append(f"Audio: {s.get('codec_name')} · {s.get('sample_rate','?')} Hz · {s.get('channels','?')} channels")
    return tool_text("\n".join(lines),"Audio inspector")

def video_info(p):
    data=ffprobe(p); fmt=data.get("format",{})
    lines=[f"File: {p.name}",f"Container: {fmt.get('format_name')}",f"Duration: {float(fmt.get('duration') or 0):.2f}s",f"Bitrate: {fmt.get('bit_rate','?')}",f"Bytes: {p.stat().st_size:,}"]
    for s in data.get("streams",[]):
        if s.get("codec_type")=="video": lines.append(f"Video: {s.get('codec_name')} · {s.get('width')}×{s.get('height')} · {s.get('avg_frame_rate') or s.get('r_frame_rate')} FPS")
        if s.get("codec_type")=="audio": lines.append(f"Audio: {s.get('codec_name')} · {s.get('channels','?')} channels")
    return tool_text("\n".join(lines),"Video inspector")

def video_thumbnail(p):
    data=ffprobe(p); duration=float(data.get("format",{}).get("duration") or 0)
    if duration<=0: raise RuntimeError("Không đọc được thời lượng video.")
    at=max(.1,duration*.5); out=p.with_name(p.stem+"-thumbnail.jpg")
    cmd("ffmpeg",["-y","-ss",str(at),"-i",str(p),"-frames:v","1","-vf","scale=1280:-2","-q:v","3",str(out)],180)
    return {"summary":f"Đã trích xuất thumbnail tại {at:.1f} giây.","output_path":str(out)}

def audio_transcribe(p):
    from faster_whisper import WhisperModel
    model=WhisperModel("small",device="cpu",compute_type="int8",cpu_threads=4)
    segments,info=model.transcribe(str(p),beam_size=5,vad_filter=True)
    lines=[f"[{s.start:07.2f}–{s.end:07.2f}] {s.text.strip()}" for s in segments]
    return tool_text(f"Ngôn ngữ: {info.language} · Thời lượng: {float(info.duration or 0):.1f}s\n\n"+"\n".join(lines),"Whisper transcription")

def csv_profile(p):
    with p.open("r",encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f); cols=reader.fieldnames or []; missing={c:0 for c in cols}; nums={c:[] for c in cols}; samples=[]; count=0
        for row in reader:
            count+=1
            if len(samples)<5: samples.append(row)
            for c in cols:
                v=(row.get(c) or "").strip()
                if not v: missing[c]+=1
                else:
                    try: nums[c].append(float(v.replace(",","")))
                    except ValueError: pass
            if count>=100000: break
    lines=[f"File: {p.name}",f"Rows read: {count:,}",f"Columns: {len(cols)}"]
    for c in cols[:100]:
        values=nums[c]; line=f"- {c}: missing {missing[c]} / {count}"
        if values: line+=f" · min {min(values):g}, max {max(values):g}, avg {sum(values)/len(values):g}"
        lines.append(line)
    lines.append("\nFirst rows:\n"+json.dumps(samples,ensure_ascii=False,indent=2)[:1400])
    return tool_text("\n".join(lines),"CSV profiler")

def json_format(p):
    value=json.loads(p.read_text(encoding="utf-8-sig")); pretty=json.dumps(value,ensure_ascii=False,indent=2)
    if len(pretty)>2800:
        out=p.with_name(p.stem+"-formatted.json"); out.write_text(pretty+"\n",encoding="utf-8")
        return {"summary":f"JSON hợp lệ · root={type(value).__name__} · {len(pretty):,} ký tự. Đã gửi file đã định dạng.","output_path":str(out)}
    return tool_text(pretty,"JSON hợp lệ · formatted")

def office_text(p):
    ext=p.suffix.lower(); lines=[]
    if ext==".docx":
        from docx import Document
        doc=Document(p); lines.extend(x.text for x in doc.paragraphs if x.text.strip())
        for table in doc.tables:
            for row in table.rows: lines.append(" | ".join(c.text.replace("\n"," / ") for c in row.cells))
    elif ext==".pptx":
        from pptx import Presentation
        prs=Presentation(p)
        for i,slide in enumerate(prs.slides,1):
            parts=[s.text for s in slide.shapes if getattr(s,"has_text_frame",False) and s.text.strip()]
            lines.append(f"--- Slide {i} ---\n"+"\n".join(parts))
    elif ext==".xlsx":
        from openpyxl import load_workbook
        wb=load_workbook(p,read_only=True,data_only=True)
        for sheet in wb.worksheets:
            lines.append(f"--- Sheet {sheet.title} ({sheet.max_row}x{sheet.max_column}) ---")
            for row in sheet.iter_rows(min_row=1,max_row=min(sheet.max_row,250),values_only=True):
                vals=["" if x is None else str(x)[:180] for x in row]
                if any(vals): lines.append(" | ".join(vals))
    else: raise RuntimeError("Office hỗ trợ DOCX, PPTX và XLSX.")
    return tool_text("\n".join(lines),"Office text extraction")

def archive_inspect(p):
    entries=[]
    if zipfile.is_zipfile(p):
        with zipfile.ZipFile(p) as z:
            for x in z.infolist()[:500]:
                suspicious=x.filename.startswith(("/","\\")) or ".." in Path(x.filename).parts
                entries.append(f"- {x.filename[:180]} · {x.file_size:,} bytes · compressed {x.compress_size:,}"+(" · ⚠ path traversal" if suspicious else ""))
    else:
        try:
            with tarfile.open(p,"r:*") as t:
                for x in t.getmembers()[:500]:
                    suspicious=x.name.startswith(("/","\\")) or ".." in Path(x.name).parts
                    entries.append(f"- {x.name[:180]} · {x.size:,} bytes"+(" · ⚠ path traversal" if suspicious else ""))
        except tarfile.TarError as e: raise RuntimeError("Archive không được hỗ trợ.") from e
    return tool_text(f"Archive: {p.name}\nBytes: {p.stat().st_size:,}\nItems listed: {len(entries)} (max 500)\nNo files extracted.\n"+"\n".join(entries),"Archive inspector")

def file_hash(p):
    sha=hashlib.sha256(); md5=hashlib.md5()
    with p.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): sha.update(chunk); md5.update(chunk)
    mime=mimetypes.guess_type(p.name)[0] or "application/octet-stream"
    return tool_text(f"File: {p.name}\nBytes: {p.stat().st_size:,}\nMIME: {mime}\nSHA-256: {sha.hexdigest()}\nMD5: {md5.hexdigest()}","File fingerprint")

def text_clean(p):
    raw=p.read_text(encoding="utf-8-sig",errors="replace")
    normalized=unicodedata.normalize("NFC",raw).replace("\r\n","\n").replace("\r","\n")
    normalized=re.sub("[\u200b\u200c\u200d\ufeff]","",normalized)
    lines=[line.rstrip(" \t") for line in normalized.split("\n")]
    cleaned=re.sub(r"\n{3,}","\n\n","\n".join(lines)).strip()+"\n"
    out=p.with_name(p.stem+"-cleaned"+(p.suffix.lower() or ".txt"))
    out.write_text(cleaned,encoding="utf-8")
    return {"summary":f"Đã làm sạch văn bản: {len(raw):,} → {len(cleaned):,} ký tự; chuẩn hóa Unicode NFC, newline, khoảng trắng và ký tự zero-width.","output_path":str(out)}

def _read_text_source(p, max_chars=1_000_000):
    raw=p.read_text(encoding="utf-8-sig",errors="replace")
    if len(raw)>max_chars:
        raise RuntimeError(f"Text input exceeds the {max_chars:,}-character limit.")
    return raw


def _write_text_artifact(p, suffix, content, title, details=""):
    extension=p.suffix.lower() or ".txt"
    out=p.with_name(p.stem+"-"+suffix+extension)
    out.write_text(content,encoding="utf-8")
    return {"summary":f"{title}: {len(content):,} characters"+(f"; {details}" if details else "")+".","output_path":str(out)}


def text_uppercase(p):
    raw=_read_text_source(p)
    return _write_text_artifact(p,"uppercase",raw.upper(),"Uppercase conversion")


def text_lowercase(p):
    raw=_read_text_source(p)
    return _write_text_artifact(p,"lowercase",raw.lower(),"Lowercase conversion")


def text_title_case(p):
    raw=_read_text_source(p)
    titled=re.sub(r"(?u)\b\w",lambda match:match.group(0).upper(),raw.lower())
    return _write_text_artifact(p,"title-case",titled,"Title case conversion")


def text_sort_lines(p):
    raw=_read_text_source(p)
    lines=raw.splitlines()
    ordered=sorted(lines,key=lambda value:value.casefold())
    output="\n".join(ordered)+("\n" if raw.endswith(("\n","\r")) else "")
    return _write_text_artifact(p,"sorted",output,"Line sorting",f"{len(lines):,} lines sorted stably")


def text_reverse_lines(p):
    raw=_read_text_source(p)
    lines=raw.splitlines()
    output="\n".join(reversed(lines))+("\n" if raw.endswith(("\n","\r")) else "")
    return _write_text_artifact(p,"reversed-lines",output,"Line reversal",f"{len(lines):,} lines")


def text_number_lines(p):
    raw=_read_text_source(p)
    lines=raw.splitlines()
    width=max(4,len(str(len(lines))))
    output="\n".join(f"{index:0{width}d} | {line}" for index,line in enumerate(lines,1))
    if raw.endswith(("\n","\r")): output+="\n"
    return _write_text_artifact(p,"numbered",output,"Line numbering",f"{len(lines):,} lines numbered")


def text_remove_blank_lines(p):
    raw=_read_text_source(p)
    lines=[line for line in raw.splitlines() if line.strip()]
    output="\n".join(lines)+("\n" if raw.endswith(("\n","\r")) and lines else "")
    removed=len(raw.splitlines())-len(lines)
    return _write_text_artifact(p,"no-blank-lines",output,"Blank-line removal",f"{removed:,} blank lines removed")


def text_wrap(p):
    raw=_read_text_source(p)
    lines=[]
    for line in raw.splitlines():
        if not line.strip():
            lines.append("")
        else:
            lines.extend(textwrap.wrap(line,width=88,break_long_words=False,break_on_hyphens=False) or [""])
    output="\n".join(lines)+("\n" if raw.endswith(("\n","\r")) else "")
    return _write_text_artifact(p,"wrapped",output,"Text wrapping","target width 88 columns; long words preserved")


def text_trim_lines(p):
    raw=_read_text_source(p)
    output="\n".join(line.strip() for line in raw.splitlines())
    if raw.endswith(("\n","\r")): output+="\n"
    return _write_text_artifact(p,"trimmed-lines",output,"Line trimming")


def _extract_unique_matches(raw, pattern, strip_trailing=""):
    found=[]
    seen=set()
    for match in re.findall(pattern,raw,flags=re.I|re.M):
        value=match.rstrip(strip_trailing) if strip_trailing else match
        key=value.casefold()
        if value and key not in seen:
            seen.add(key); found.append(value)
    return found


def text_extract_emails(p):
    raw=_read_text_source(p)
    values=_extract_unique_matches(raw,r"(?<![\w.+-])[A-Z0-9.!#$%&'*+/=?^_{}|~-]+@[A-Z0-9-]+(?:\.[A-Z0-9-]+)+")
    return _write_text_artifact(p,"emails","\n".join(values)+("\n" if values else ""),"Email extraction",f"{len(values):,} unique addresses")


def text_extract_urls(p):
    raw=_read_text_source(p)
    values=_extract_unique_matches(raw, r"""https?://[^\s<>"']+""", ").,;:!?)]}")
    return _write_text_artifact(p,"urls","\n".join(values)+("\n" if values else ""),"URL extraction",f"{len(values):,} unique URLs")


def text_extract_hashtags(p):
    raw=_read_text_source(p)
    values=_extract_unique_matches(raw,r"(?<![\w#])#[\w]+")
    return _write_text_artifact(p,"hashtags","\n".join(values)+("\n" if values else ""),"Hashtag extraction",f"{len(values):,} unique hashtags")


def text_to_base64(p):
    raw=_read_text_source(p)
    encoded=base64.b64encode(raw.encode("utf-8")).decode("ascii")
    return _write_text_artifact(p,"base64",encoded+"\n","Base64 encoding")


def base64_to_text(p):
    raw=_read_text_source(p)
    compact="".join(raw.split())
    try:
        decoded=base64.b64decode(compact,validate=True).decode("utf-8-sig")
    except (ValueError,UnicodeDecodeError) as exc:
        raise RuntimeError("Input must be valid Base64 containing UTF-8 text.") from exc
    return _write_text_artifact(p,"decoded",decoded,"Base64 decoding")


def url_encode_text(p):
    raw=_read_text_source(p)
    encoded=urllib.parse.quote(raw,safe="")
    return _write_text_artifact(p,"url-encoded",encoded,"URL percent-encoding")


def url_decode_text(p):
    raw=_read_text_source(p)
    try:
        decoded=urllib.parse.unquote(raw,errors="strict")
        decoded.encode("utf-8","strict")
    except (UnicodeError,ValueError) as exc:
        raise RuntimeError("Input contains invalid URL-encoded UTF-8.") from exc
    return _write_text_artifact(p,"url-decoded",decoded,"URL decoding")


def _load_json_reject_duplicates(raw):
    def unique_object(pairs):
        result={}
        for key,value in pairs:
            if key in result: raise ValueError("Duplicate JSON object key: "+str(key))
            result[key]=value
        return result
    return json.loads(raw,object_pairs_hook=unique_object)


def json_minify(p):
    raw=_read_text_source(p)
    try:
        value=_load_json_reject_duplicates(raw)
    except (ValueError,json.JSONDecodeError) as exc:
        raise RuntimeError(f"Invalid JSON: {exc}") from exc
    output=json.dumps(value,ensure_ascii=False,separators=(",",":"))
    return _write_text_artifact(p,"minified",output+"\n","JSON minification")


def json_sort_keys(p):
    raw=_read_text_source(p)
    try:
        value=_load_json_reject_duplicates(raw)
    except (ValueError,json.JSONDecodeError) as exc:
        raise RuntimeError(f"Invalid JSON: {exc}") from exc
    def sort_nested(item):
        if isinstance(item,dict): return {key:sort_nested(item[key]) for key in sorted(item)}
        if isinstance(item,list): return [sort_nested(value) for value in item]
        return item
    output=json.dumps(sort_nested(value),ensure_ascii=False,indent=2)
    return _write_text_artifact(p,"sorted-keys",output+"\n","JSON key sorting")


def language_detect(p):
    raw=_read_text_source(p)
    sample=raw[:20_000]
    if not sample.strip(): return _write_text_artifact(p,"language","Undetermined\nMethod: empty input","Language detection")
    scores={}
    def script_count(pattern):
        return len(re.findall(pattern,sample))
    scripts=[
        (r"[\u3040-\u30ff]","Japanese","Hiragana/Katakana script"),
        (r"[\uac00-\ud7af]","Korean","Hangul script"),
        (r"[\u4e00-\u9fff]","Chinese","Han characters; Japanese without kana may be ambiguous"),
        (r"[\u0400-\u04ff]","Russian or another Cyrillic language","Cyrillic script"),
        (r"[\u0600-\u06ff]","Arabic","Arabic script"),
        (r"[\u0590-\u05ff]","Hebrew","Hebrew script"),
        (r"[\u0370-\u03ff]","Greek","Greek script"),
        (r"[\u0e00-\u0e7f]","Thai","Thai script"),
        (r"[\u0900-\u097f]","Hindi or another Devanagari language","Devanagari script"),
    ]
    for pattern,label,evidence in scripts:
        count=script_count(pattern)
        if count: scores[label]=(count,evidence)
    if scores:
        label,(count,evidence)=max(scores.items(),key=lambda item:item[1][0])
    elif any(char in "ăâđêôơưáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ" for char in sample.lower()):
        label="Vietnamese"; evidence="Vietnamese-specific letters and diacritics"
    else:
        words=set(re.findall(r"[a-zA-ZÀ-ỹ']+",sample.lower()))
        vocab={
            "English":{"the","and","that","with","this","you","for","are","was","have","from"},
            "French":{"le","la","les","et","des","une","est","dans","pour","avec","que"},
            "German":{"der","die","das","und","ist","mit","ein","eine","nicht","auf","für"},
            "Spanish":{"el","la","los","las","y","de","que","una","es","por","para","con"},
            "Portuguese":{"o","a","os","as","e","de","que","uma","é","para","com","não"},
            "Italian":{"il","lo","la","gli","e","di","che","una","per","con","non"},
            "Indonesian":{"yang","dan","ini","itu","untuk","dengan","dari","tidak","adalah"},
        }
        ranked=sorted(((len(words & values),language) for language,values in vocab.items()),reverse=True)
        score,label=ranked[0] if ranked else (0,"")
        if score<2: label="Undetermined"; evidence="Latin-script text without enough distinctive words"
        else: evidence=f"{score} common-word matches in a small vocabulary"
    report=f"Most likely: {label}\nEvidence: {evidence}\nMethod: lightweight heuristic; short or mixed-language text may be misclassified."
    return _write_text_artifact(p,"language",report,"Language detection")


def split_translation_chunks(raw, limit=5_000):
    remaining=raw
    chunks=[]
    while len(remaining)>limit:
        boundary=remaining.rfind("\n",0,limit+1)
        if boundary<limit//2: boundary=limit
        else: boundary+=1
        chunks.append(remaining[:boundary])
        remaining=remaining[boundary:]
    if remaining: chunks.append(remaining)
    return chunks


def text_translate(p, translate_callback=None):
    if not callable(translate_callback):
        raise RuntimeError("Translation requires the Worker AI Router; use the dedicated translation runner step.")
    raw=_read_text_source(p, max_chars=60_000)
    if not raw.strip(): raise RuntimeError("Translation input is empty.")
    chunks=split_translation_chunks(raw)
    translated=[]
    target_language=""
    for index,chunk in enumerate(chunks,1):
        response=translate_callback(chunk)
        value=response.get("translation") if isinstance(response,dict) else None
        if not isinstance(value,str) or not value.strip():
            raise RuntimeError(f"AI translation returned an empty chunk at {index}/{len(chunks)}.")
        target_language=str(response.get("targetLanguage") or target_language)
        translated.append(value)
    output="".join(translated)
    if len(output)>MAX_PIPELINE_OUTPUT: raise RuntimeError("Translated output exceeds the 45 MB output limit.")
    details=f"{len(chunks)} chunk(s)"+(f"; target {target_language}" if target_language else "")
    return _write_text_artifact(p,"translated",output,"AI translation",details)


def _write_text_artifact_ext(p, suffix, extension, content, title, details=""):
    out=p.with_name(p.stem+"-"+suffix+extension)
    out.write_text(content,encoding="utf-8")
    return {"summary":f"{title}: {len(content):,} characters"+(f"; {details}" if details else "")+".","output_path":str(out)}


def text_slugify(p):
    raw=_read_text_source(p)
    lines=[]
    for line in raw.splitlines():
        normalized=unicodedata.normalize("NFKD",line.lower().replace("đ","d"))
        ascii_text=normalized.encode("ascii","ignore").decode("ascii")
        lines.append(re.sub(r"[^a-z0-9]+","-",ascii_text).strip("-"))
    output="\n".join(lines)+("\n" if raw.endswith(("\n","\r")) else "")
    return _write_text_artifact(p,"slugified",output,"Slug generation",str(len(lines))+" line(s)")


def text_word_frequency(p):
    from collections import Counter
    raw=_read_text_source(p)
    words=re.findall(r"[^\W_]+(?:['’][^\W_]+)?",raw.casefold(),flags=re.UNICODE)
    counts=Counter(words)
    lines=["Word frequency | "+str(len(words))+" total tokens | "+str(len(counts))+" unique words",""]
    lines.extend(word+"\t"+str(count) for word,count in sorted(counts.items(),key=lambda item:(-item[1],item[0]))[:500])
    return _write_text_artifact(p,"word-frequency","\n".join(lines)+"\n","Word frequency report",str(len(counts))+" unique words")


def _ordered_unique(values):
    result=[]
    seen=set()
    for value in values:
        key=value.casefold()
        if key not in seen:
            seen.add(key)
            result.append(value)
    return result


def text_extract_numbers(p):
    raw=_read_text_source(p)
    filtered=re.sub(r"(?<!\d)(?:(?:19|20)\d{2}[-/.]\d{1,2}[-/.]\d{1,2}|\d{1,2}[-/.]\d{1,2}[-/.](?:19|20)\d{2})(?!\d)"," ",raw)
    filtered=re.sub(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])"," ",filtered)
    filtered=re.sub(r"(?<!\w)\+?\d[\d\s().-]{5,}\d(?!\w)"," ",filtered)
    values=_ordered_unique(re.findall(r"(?<![\w.])[+-]?\d+(?:[.,]\d+)?(?!\w)",filtered))
    return _write_text_artifact(p,"numbers","\n".join(values)+("\n" if values else ""),"Number extraction",str(len(values))+" unique values")


def text_extract_dates(p):
    from datetime import datetime
    raw=_read_text_source(p)
    candidates=re.findall(r"(?<!\d)(?:(?:19|20)\d{2}[-/.]\d{1,2}[-/.]\d{1,2}|\d{1,2}[-/.]\d{1,2}[-/.](?:19|20)\d{2})(?!\d)",raw)
    formats=("%Y-%m-%d","%Y/%m/%d","%Y.%m.%d","%d/%m/%Y","%d-%m-%Y","%d.%m.%Y","%m/%d/%Y")
    valid=[]
    for value in candidates:
        for fmt in formats:
            try:
                datetime.strptime(value,fmt)
                valid.append(value)
                break
            except ValueError:
                continue
    values=_ordered_unique(valid)
    return _write_text_artifact(p,"dates","\n".join(values)+("\n" if values else ""),"Date extraction",str(len(values))+" unique valid calendar dates")


def text_reverse_characters(p):
    raw=_read_text_source(p)
    lines=raw.splitlines()
    output="\n".join(line[::-1] for line in lines)+("\n" if raw.endswith(("\n","\r")) else "")
    return _write_text_artifact(p,"reversed-characters",output,"Character reversal",str(len(lines))+" line(s)")


def _case_words(value):
    return re.findall(r"[A-Za-z0-9À-ỹ]+",value,flags=re.UNICODE)


def text_snake_case(p):
    raw=_read_text_source(p)
    output="\n".join("_".join(word.casefold() for word in _case_words(line)) for line in raw.splitlines())
    if raw.endswith(("\n","\r")): output+="\n"
    return _write_text_artifact(p,"snake-case",output,"Snake case conversion")


def text_kebab_case(p):
    raw=_read_text_source(p)
    output="\n".join("-".join(word.casefold() for word in _case_words(line)) for line in raw.splitlines())
    if raw.endswith(("\n","\r")): output+="\n"
    return _write_text_artifact(p,"kebab-case",output,"Kebab case conversion")


def text_camel_case(p):
    raw=_read_text_source(p)
    converted=[]
    for line in raw.splitlines():
        words=_case_words(line)
        converted.append(words[0].casefold()+"".join(word[:1].upper()+word[1:].casefold() for word in words[1:]) if words else "")
    output="\n".join(converted)+("\n" if raw.endswith(("\n","\r")) else "")
    return _write_text_artifact(p,"camel-case",output,"Camel case conversion")


def text_swap_case(p):
    raw=_read_text_source(p)
    return _write_text_artifact(p,"swap-case",raw.swapcase(),"Swap case conversion")


def text_extract_ipv4(p):
    import ipaddress
    raw=_read_text_source(p)
    candidates=re.findall(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])",raw)
    valid=[]
    for value in candidates:
        try:
            if ipaddress.ip_address(value).version==4: valid.append(value)
        except ValueError:
            continue
    values=_ordered_unique(valid)
    return _write_text_artifact(p,"ipv4","\n".join(values)+("\n" if values else ""),"IPv4 extraction",str(len(values))+" unique valid addresses")


def text_mask_emails(p):
    raw=_read_text_source(p)
    pattern=r"(?<![\w.+-])([A-Z0-9.!#$%&'*+/=?^_{}|~-]+)@([A-Z0-9-]+)((?:\.[A-Z0-9-]+)+)"
    def mask(match):
        local,domain,suffix=match.groups()
        return (local[:1] or "*")+"***@"+(domain[:1] or "*")+"***"+suffix
    output=re.sub(pattern,mask,raw,flags=re.I)
    return _write_text_artifact(p,"masked-emails",output,"Email masking","heuristic partial masking")


def text_mask_phones(p):
    raw=_read_text_source(p)
    pattern=r"(?<!\w)(?:\+?\d[\d\s().-]{5,}\d)(?!\w)"
    def mask(match):
        digits=re.sub(r"\D","",match.group(0))
        if len(digits)<7: return match.group(0)
        return "*"*max(4,len(digits)-2)+digits[-2:]
    output=re.sub(pattern,mask,raw)
    return _write_text_artifact(p,"masked-phones",output,"Phone masking","heuristic; final two digits retained")


def json_to_jsonl(p):
    raw=_read_text_source(p)
    try: value=_load_json_reject_duplicates(raw)
    except (ValueError,json.JSONDecodeError) as exc: raise RuntimeError("Invalid JSON: "+str(exc)) from exc
    if not isinstance(value,list): raise RuntimeError("JSON-to-JSONL expects a top-level array.")
    if len(value)>100_000: raise RuntimeError("JSON array exceeds the 100,000-record limit.")
    output="\n".join(json.dumps(item,ensure_ascii=False,separators=(",",":")) for item in value)
    if value: output+="\n"
    return _write_text_artifact_ext(p,"jsonl",".jsonl",output,"JSON Lines conversion",str(len(value))+" record(s)")


def jsonl_to_json(p):
    raw=_read_text_source(p)
    records=[]
    for line_number,line in enumerate(raw.splitlines(),1):
        if not line.strip(): continue
        try: records.append(_load_json_reject_duplicates(line))
        except (ValueError,json.JSONDecodeError) as exc: raise RuntimeError("Invalid JSONL at line "+str(line_number)+": "+str(exc)) from exc
        if len(records)>100_000: raise RuntimeError("JSONL exceeds the 100,000-record limit.")
    output=json.dumps(records,ensure_ascii=False,indent=2)
    return _write_text_artifact_ext(p,"array",".json",output+"\n","JSON Lines to JSON",str(len(records))+" record(s)")


def _convert_delimited_file(p,source_delimiter,target_delimiter,suffix,title):
    import io
    raw=_read_text_source(p)
    try: rows=list(csv.reader(io.StringIO(raw,newline=""),delimiter=source_delimiter))
    except csv.Error as exc: raise RuntimeError("Invalid delimited text: "+str(exc)) from exc
    if len(rows)>100_001 or any(len(row)>200 for row in rows):
        raise RuntimeError("Delimited input exceeds 100,000 rows or 200 columns.")
    stream=io.StringIO(newline="")
    writer=csv.writer(stream,delimiter=target_delimiter,lineterminator="\n",quoting=csv.QUOTE_MINIMAL)
    writer.writerows(rows)
    return _write_text_artifact_ext(p,suffix,".tsv" if target_delimiter=="\t" else ".csv",stream.getvalue(),title,str(len(rows))+" row(s)")


def csv_to_tsv(p):
    return _convert_delimited_file(p,",","\t","tsv","CSV to TSV conversion")


def tsv_to_csv(p):
    return _convert_delimited_file(p,"\t",",","csv","TSV to CSV conversion")


def csv_to_markdown(p):
    import io
    raw=_read_text_source(p)
    try: rows=list(csv.reader(io.StringIO(raw,newline="")))
    except csv.Error as exc: raise RuntimeError("Invalid CSV: "+str(exc)) from exc
    if not rows: return _write_text_artifact_ext(p,"table",".md","No rows.\n","CSV Markdown preview")
    if len(rows)>51 or max((len(row) for row in rows),default=0)>20:
        raise RuntimeError("CSV-to-Markdown is limited to 50 data rows and 20 columns.")
    columns=max(len(row) for row in rows)
    def cell(value):
        return value.replace("|","\\|").replace("\r"," ").replace("\n","<br>").strip()
    header=[cell(value) for value in rows[0]]+[""]*(columns-len(rows[0]))
    lines=["| "+" | ".join(header)+" |","| "+" | ".join(["---"]*columns)+" |"]
    for row in rows[1:]:
        padded=row+[""]*(columns-len(row))
        lines.append("| "+" | ".join(cell(value) for value in padded)+" |")
    return _write_text_artifact_ext(p,"table",".md","\n".join(lines)+"\n","CSV to Markdown",str(len(rows)-1)+" data row(s)")


def html_minify(p):
    raw=_read_text_source(p)
    class Minifier(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=False)
            self.parts=[]
            self.stack=[]
            self.preserve={"pre","textarea","script","style"}
        def handle_starttag(self,tag,attrs):
            self.parts.append("<"+tag)
            for key,value in attrs:
                self.parts.append(" "+key if value is None else " "+key+'="'+escape(value,quote=True)+'"')
            self.parts.append(">")
            if tag not in {"area","base","br","col","embed","hr","img","input","link","meta","param","source","track","wbr"}:
                self.stack.append(tag)
        def handle_startendtag(self,tag,attrs):
            self.parts.append("<"+tag)
            for key,value in attrs:
                self.parts.append(" "+key if value is None else " "+key+'="'+escape(value,quote=True)+'"')
            self.parts.append("/>")
        def handle_endtag(self,tag):
            self.parts.append("</"+tag+">")
            if tag in self.stack:
                index=len(self.stack)-1-self.stack[::-1].index(tag)
                self.stack=self.stack[:index]
        def handle_data(self,data):
            self.parts.append(data if any(tag in self.preserve for tag in self.stack) else re.sub(r"\s+"," ",data))
        def handle_entityref(self,name): self.parts.append("&"+name+";")
        def handle_charref(self,name): self.parts.append("&#"+name+";")
        def handle_comment(self,data): pass
        def handle_decl(self,decl): self.parts.append("<!"+decl+">")
    parser=Minifier()
    try: parser.feed(raw); parser.close()
    except Exception as exc: raise RuntimeError("Invalid HTML: "+str(exc)) from exc
    return _write_text_artifact_ext(p,"minified",".html","".join(parser.parts).strip(),"HTML minification")


def xml_minify(p):
    import xml.etree.ElementTree as ET
    raw=_read_text_source(p)
    if re.search(r"<!\s*(?:DOCTYPE|ENTITY)\b",raw,re.I):
        raise RuntimeError("XML DTD and ENTITY declarations are not supported.")
    try: output=ET.tostring(ET.fromstring(raw),encoding="unicode",short_empty_elements=True)
    except ET.ParseError as exc: raise RuntimeError("Invalid XML: "+str(exc)) from exc
    return _write_text_artifact_ext(p,"minified",".xml",output,"XML minification")


def text_remove_emoji(p):
    raw=_read_text_source(p)
    pattern=r"[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200D]"
    output=re.sub(pattern,"",raw)
    return _write_text_artifact(p,"no-emoji",output,"Emoji removal")


def text_collapse_whitespace(p):
    raw=_read_text_source(p)
    output="\n".join(re.sub(r"[ \t\f\v]+"," ",line).strip() for line in raw.splitlines())
    if raw.endswith(("\n","\r")): output+="\n"
    return _write_text_artifact(p,"collapsed",output,"Whitespace normalization")


def text_remove_punctuation(p):
    raw=_read_text_source(p)
    output="".join(" " if unicodedata.category(char).startswith("P") else char for char in raw)
    output=re.sub(r"[ \t]+"," ",output)
    return _write_text_artifact(p,"no-punctuation",output,"Punctuation removal")


def text_to_ascii(p):
    raw=_read_text_source(p)
    normalized=raw.replace("đ","d").replace("Đ","D")
    output=unicodedata.normalize("NFKD",normalized).encode("ascii","ignore").decode("ascii")
    return _write_text_artifact(p,"ascii",output,"ASCII transliteration")


def text_html_escape(p):
    raw=_read_text_source(p)
    return _write_text_artifact(p,"html-escaped",escape(raw,quote=True),"HTML escaping")


def text_html_unescape(p):
    raw=_read_text_source(p)
    return _write_text_artifact(p,"html-unescaped",unescape(raw),"HTML entity decoding")


def text_extract_mentions(p):
    raw=_read_text_source(p)
    values=_ordered_unique(re.findall(r"(?<![\w@])@[A-Za-z0-9_](?:[A-Za-z0-9_.]{0,28}[A-Za-z0-9_])?",raw))
    return _write_text_artifact(p,"mentions","\n".join(values)+("\n" if values else ""),"Mention extraction",str(len(values))+" unique mentions")


def text_extract_hex_colors(p):
    raw=_read_text_source(p)
    values=re.findall(r"(?<![\w])#(?:[0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})(?![0-9A-Fa-f])",raw)
    values=_ordered_unique([value.upper() for value in values])
    return _write_text_artifact(p,"hex-colors","\n".join(values)+("\n" if values else ""),"Hex color extraction",str(len(values))+" unique colors")


def text_extract_phones(p):
    raw=_read_text_source(p)
    candidates=re.findall(r"(?<!\w)\+?\d[\d\s().-]{5,}\d(?!\w)",raw)
    values=[]
    for candidate in candidates:
        digits=re.sub(r"\D","",candidate)
        if 7<=len(digits)<=15:
            values.append(candidate.strip())
    values=_ordered_unique(values)
    return _write_text_artifact(p,"phones","\n".join(values)+("\n" if values else ""),"Phone extraction",str(len(values))+" candidates; heuristic")


def text_dedupe_lines(p):
    raw=_read_text_source(p)
    seen=set()
    output=[]
    removed=0
    for line in raw.splitlines():
        key=line.strip().casefold()
        if key in seen:
            removed+=1
            continue
        seen.add(key)
        output.append(line)
    result="\n".join(output)+("\n" if raw.endswith(("\n","\r")) and output else "")
    return _write_text_artifact(p,"unique-lines",result,"Duplicate-line removal",str(removed)+" duplicate line(s) removed")


def text_count_report(p):
    raw=_read_text_source(p)
    lines=raw.splitlines()
    words=re.findall(r"[^\W_]+(?:['’][^\W_]+)?",raw,flags=re.UNICODE)
    nonspace=sum(not char.isspace() for char in raw)
    nonascii=sum(ord(char)>127 for char in raw)
    report=(
        "Text statistics\n"
        "Lines: "+str(len(lines))+"\n"
        "Words: "+str(len(words))+"\n"
        "Characters: "+str(len(raw))+"\n"
        "Non-whitespace characters: "+str(nonspace)+"\n"
        "UTF-8 bytes: "+str(len(raw.encode("utf-8")))+"\n"
        "Non-ASCII characters: "+str(nonascii)+"\n"
    )
    return _write_text_artifact(p,"count-report",report,"Text count report")


def text_quote_lines(p):
    raw=_read_text_source(p)
    output="\n".join(json.dumps(line,ensure_ascii=False) for line in raw.splitlines())
    if raw.endswith(("\n","\r")): output+="\n"
    return _write_text_artifact(p,"quoted-lines",output,"JSON string quoting per line")


def text_unquote_lines(p):
    raw=_read_text_source(p)
    output=[]
    for line_number,line in enumerate(raw.splitlines(),1):
        try:
            value=json.loads(line)
        except ValueError as exc:
            raise RuntimeError("Invalid JSON string on line "+str(line_number)+".") from exc
        if not isinstance(value,str):
            raise RuntimeError("Line "+str(line_number)+" must be a JSON string.")
        output.append(value)
    result="\n".join(output)+("\n" if raw.endswith(("\n","\r")) and output else "")
    return _write_text_artifact(p,"unquoted-lines",result,"JSON string unquoting")


def csv_transpose(p):
    import io
    raw=_read_text_source(p)
    try: rows=list(csv.reader(io.StringIO(raw,newline="")))
    except csv.Error as exc: raise RuntimeError("Invalid CSV: "+str(exc)) from exc
    if not rows: raise RuntimeError("CSV is empty.")
    width=max(len(row) for row in rows)
    if len(rows)>10_000 or width>200: raise RuntimeError("CSV transpose is limited to 10,000 rows and 200 columns.")
    padded=[row+[""]*(width-len(row)) for row in rows]
    transposed=list(map(list,zip(*padded)))
    stream=__import__("io").StringIO(newline="")
    writer=csv.writer(stream,lineterminator="\n")
    writer.writerows(transposed)
    return _write_text_artifact_ext(p,"transposed",".csv",stream.getvalue(),"CSV transpose",str(len(rows))+" x "+str(width))


def csv_sort_rows(p):
    import io
    raw=_read_text_source(p)
    try: rows=list(csv.reader(io.StringIO(raw,newline="")))
    except csv.Error as exc: raise RuntimeError("Invalid CSV: "+str(exc)) from exc
    if not rows: raise RuntimeError("CSV is empty.")
    header,body=rows[0],rows[1:]
    body=sorted(body,key=lambda row:(row[0] if row else "").casefold())
    stream=io.StringIO(newline="")
    writer=csv.writer(stream,lineterminator="\n")
    writer.writerow(header)
    writer.writerows(body)
    return _write_text_artifact_ext(p,"sorted",".csv",stream.getvalue(),"CSV row sorting",str(len(body))+" row(s)")


def csv_dedupe_rows(p):
    import io
    raw=_read_text_source(p)
    try: rows=list(csv.reader(io.StringIO(raw,newline="")))
    except csv.Error as exc: raise RuntimeError("Invalid CSV: "+str(exc)) from exc
    if not rows: raise RuntimeError("CSV is empty.")
    header,body=rows[0],rows[1:]
    seen=set()
    unique=[]
    removed=0
    for row in body:
        key=tuple(value.casefold() for value in row)
        if key in seen:
            removed+=1
            continue
        seen.add(key)
        unique.append(row)
    stream=io.StringIO(newline="")
    writer=csv.writer(stream,lineterminator="\n")
    writer.writerow(header)
    writer.writerows(unique)
    return _write_text_artifact_ext(p,"deduped",".csv",stream.getvalue(),"CSV duplicate-row removal",str(removed)+" duplicate row(s) removed")


def _csv_xml_tag(value,index,used):
    tag=re.sub(r"[^A-Za-z0-9_.-]","_",value.strip()) or "column_"+str(index+1)
    if not re.match(r"[A-Za-z_]",tag): tag="column_"+tag
    candidate=tag
    suffix=2
    while candidate in used:
        candidate=tag+"_"+str(suffix)
        suffix+=1
    used.add(candidate)
    return candidate


def csv_to_xml(p):
    import io
    import xml.etree.ElementTree as ET
    raw=_read_text_source(p)
    try: rows=list(csv.reader(io.StringIO(raw,newline="")))
    except csv.Error as exc: raise RuntimeError("Invalid CSV: "+str(exc)) from exc
    if not rows: raise RuntimeError("CSV is empty.")
    headers=rows[0]
    if len(headers)>200 or len(rows)>100_001: raise RuntimeError("CSV-to-XML is limited to 100,000 rows and 200 columns.")
    used=set()
    tags=[_csv_xml_tag(value,index,used) for index,value in enumerate(headers)]
    root=ET.Element("rows")
    for row in rows[1:]:
        node=ET.SubElement(root,"row")
        for index,tag in enumerate(tags):
            child=ET.SubElement(node,tag)
            child.text=row[index] if index<len(row) else ""
    output=ET.tostring(root,encoding="unicode",short_empty_elements=True)
    return _write_text_artifact_ext(p,"converted",".xml",output,"CSV to XML conversion",str(len(rows)-1)+" row(s)")


def csv_to_html(p):
    import io
    raw=_read_text_source(p)
    try: rows=list(csv.reader(io.StringIO(raw,newline="")))
    except csv.Error as exc: raise RuntimeError("Invalid CSV: "+str(exc)) from exc
    if not rows: raise RuntimeError("CSV is empty.")
    if len(rows)>10_001 or max((len(row) for row in rows),default=0)>200:
        raise RuntimeError("CSV-to-HTML is limited to 10,000 rows and 200 columns.")
    parts=["<!doctype html><html><head><meta charset=\"utf-8\"><title>CSV table</title></head><body><table><thead><tr>"]
    parts.extend("<th>"+escape(value)+"</th>" for value in rows[0])
    parts.append("</tr></thead><tbody>")
    for row in rows[1:]:
        parts.append("<tr>")
        parts.extend("<td>"+escape(value)+"</td>" for value in row)
        parts.append("</tr>")
    parts.append("</tbody></table></body></html>")
    return _write_text_artifact_ext(p,"table",".html","".join(parts),"CSV to HTML table",str(len(rows)-1)+" row(s)")


def json_sort_array(p):
    raw=_read_text_source(p)
    try: value=_load_json_reject_duplicates(raw)
    except (ValueError,json.JSONDecodeError) as exc: raise RuntimeError("Invalid JSON: "+str(exc)) from exc
    if not isinstance(value,list): raise RuntimeError("JSON array sort expects a top-level array.")
    ordered=sorted(value,key=lambda item:json.dumps(item,ensure_ascii=False,sort_keys=True, separators=(",",":")))
    output=json.dumps(ordered,ensure_ascii=False,indent=2)
    return _write_text_artifact(p,"sorted-array",output+"\n","JSON array sorting",str(len(ordered))+" item(s)")


def json_remove_nulls(p):
    raw=_read_text_source(p)
    try: value=_load_json_reject_duplicates(raw)
    except (ValueError,json.JSONDecodeError) as exc: raise RuntimeError("Invalid JSON: "+str(exc)) from exc
    def clean(item):
        if isinstance(item,dict): return {key:clean(child) for key,child in item.items() if child is not None}
        if isinstance(item,list): return [clean(child) for child in item if child is not None]
        return item
    output=json.dumps(clean(value),ensure_ascii=False,indent=2)
    return _write_text_artifact(p,"without-nulls",output+"\n","JSON null removal")


def json_to_html_table(p):
    raw=_read_text_source(p)
    try: value=_load_json_reject_duplicates(raw)
    except (ValueError,json.JSONDecodeError) as exc: raise RuntimeError("Invalid JSON: "+str(exc)) from exc
    if not isinstance(value,list) or any(not isinstance(item,dict) for item in value):
        raise RuntimeError("JSON-to-HTML-table expects an array of objects.")
    if len(value)>10_000: raise RuntimeError("JSON-to-HTML-table exceeds 10,000 records.")
    headers=[]
    seen=set()
    for item in value:
        for key in item:
            if key not in seen:
                seen.add(key)
                headers.append(key)
    if len(headers)>200: raise RuntimeError("JSON-to-HTML-table exceeds 200 columns.")
    parts=["<!doctype html><html><head><meta charset=\"utf-8\"><title>JSON table</title></head><body><table><thead><tr>"]
    parts.extend("<th>"+escape(key)+"</th>" for key in headers)
    parts.append("</tr></thead><tbody>")
    for item in value:
        parts.append("<tr>")
        for key in headers:
            cell=item.get(key)
            content="" if cell is None else (cell if isinstance(cell,str) else json.dumps(cell,ensure_ascii=False))
            parts.append("<td>"+escape(content)+"</td>")
        parts.append("</tr>")
    parts.append("</tbody></table></body></html>")
    return _write_text_artifact_ext(p,"table",".html","".join(parts),"JSON to HTML table",str(len(value))+" row(s)")


def text_pascal_case(p):
    raw=_read_text_source(p)
    output="\n".join("".join(word[:1].upper()+word[1:].lower() for word in _case_words(line)) for line in raw.splitlines())
    if raw.endswith(("\n","\r")): output+="\n"
    return _write_text_artifact(p,"pascal-case",output,"PascalCase conversion")


def text_constant_case(p):
    raw=_read_text_source(p)
    output="\n".join("_".join(word.upper() for word in _case_words(line)) for line in raw.splitlines())
    if raw.endswith(("\n","\r")): output+="\n"
    return _write_text_artifact(p,"constant-case",output,"CONSTANT_CASE conversion")


def text_dot_case(p):
    raw=_read_text_source(p)
    output="\n".join(".".join(word.lower() for word in _case_words(line)) for line in raw.splitlines())
    if raw.endswith(("\n","\r")): output+="\n"
    return _write_text_artifact(p,"dot-case",output,"dot.case conversion")


def text_initials(p):
    raw=_read_text_source(p)
    output="\n".join("".join(word[0].upper() for word in _case_words(line)) for line in raw.splitlines())
    if raw.endswith(("\n","\r")): output+="\n"
    return _write_text_artifact(p,"initials",output,"Initials extraction")


def text_normalize_unicode(p):
    raw=_read_text_source(p)
    output=unicodedata.normalize("NFC",raw)
    return _write_text_artifact(p,"unicode-nfc",output,"Unicode NFC normalization")


def text_remove_control_chars(p):
    raw=_read_text_source(p)
    output="".join(char for char in raw if char in "\n\r\t" or unicodedata.category(char)!="Cc")
    return _write_text_artifact(p,"no-control-chars",output,"Control-character removal")


def text_remove_duplicate_words(p):
    raw=_read_text_source(p)
    seen=set()
    def remove(match):
        word=match.group(0)
        key=word.casefold()
        if key in seen: return ""
        seen.add(key)
        return word
    output=re.sub(r"\b[^\W_]+\b",remove,raw,flags=re.UNICODE)
    output=re.sub(r"[ \t]{2,}"," ",output)
    return _write_text_artifact(p,"unique-words",output,"Duplicate-word removal",str(len(seen))+" unique words retained")


def text_extract_markdown_links(p):
    raw=_read_text_source(p)
    values=[]
    for match in re.finditer(r"(?<!!)\[([^\]\n]+)\]\(([^)\s]+)(?:\s+[\x22\x27]([^\x22\x27]*)[\x22\x27])?\)",raw):
        label,url,title=match.groups()
        values.append(json.dumps({"text":label,"url":url,"title":title or ""},ensure_ascii=False))
    output="\n".join(_ordered_unique(values))
    return _write_text_artifact(p,"markdown-links",output+("\n" if output else ""),"Markdown link extraction",str(len(values))+" link(s)")


def text_extract_markdown_headings(p):
    raw=_read_text_source(p)
    values=[]
    in_fence=False
    fence=chr(96)*3
    for line in raw.splitlines():
        if line.lstrip().startswith((fence,"~~~")):
            in_fence=not in_fence
            continue
        if in_fence: continue
        match=re.match(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$",line)
        if match:
            level=len(match.group(1))
            title=re.sub(r"\s+#+\s*$","",match.group(2)).strip()
            values.append(json.dumps({"level":level,"text":title},ensure_ascii=False))
    output="\n".join(values)
    return _write_text_artifact(p,"markdown-headings",output+("\n" if output else ""),"Markdown heading extraction",str(len(values))+" heading(s)")


def text_extract_quotes(p):
    raw=_read_text_source(p)
    pattern=r"[\x22]([^\x22\n]{1,2000})[\x22]|[\x27]([^\x27\n]{1,2000})[\x27]|“([^”\n]{1,2000})”|‘([^’\n]{1,2000})’|«([^»\n]{1,2000})»"
    values=[]
    for match in re.finditer(pattern,raw):
        value=next((group for group in match.groups() if group is not None),"").strip()
        if value: values.append(value)
    output="\n".join(_ordered_unique(values))
    return _write_text_artifact(p,"quoted-text",output+("\n" if output else ""),"Quoted-text extraction",str(len(values))+" quote(s)")


def text_paragraph_report(p):
    raw=_read_text_source(p)
    paragraphs=[part.strip() for part in re.split(r"\n\s*\n",raw) if part.strip()]
    words=[len(re.findall(r"[^\W_]+(?:['\u2019][^\W_]+)?",part,flags=re.UNICODE)) for part in paragraphs]
    report=[
        "Paragraph statistics",
        "Paragraphs: "+str(len(paragraphs)),
        "Words: "+str(sum(words)),
        "Average words per paragraph: "+(f"{sum(words)/len(words):.2f}" if words else "0"),
        "Longest paragraph characters: "+str(max((len(part) for part in paragraphs),default=0)),
    ]
    return _write_text_artifact(p,"paragraph-report","\n".join(report)+"\n","Paragraph report")


def _json_pointer_escape(value):
    return str(value).replace("~","~0").replace("/","~1")


def _json_pointer_unescape(value):
    return value.replace("~1","/").replace("~0","~")


def json_flatten(p):
    raw=_read_text_source(p)
    try: value=_load_json_reject_duplicates(raw)
    except (ValueError,json.JSONDecodeError) as exc: raise RuntimeError("Invalid JSON: "+str(exc)) from exc
    if not isinstance(value,dict): raise RuntimeError("JSON flatten expects a top-level object.")
    flattened={}
    def visit(item,path):
        if isinstance(item,dict) and item:
            for key,child in item.items():
                visit(child,path+"/"+_json_pointer_escape(key))
        else:
            flattened[path]=item
    visit(value,"")
    output=json.dumps(flattened,ensure_ascii=False,indent=2)
    return _write_text_artifact(p,"flattened",output+"\n","JSON flattening",str(len(flattened))+" leaf value(s)")


def json_unflatten(p):
    raw=_read_text_source(p)
    try: value=_load_json_reject_duplicates(raw)
    except (ValueError,json.JSONDecodeError) as exc: raise RuntimeError("Invalid JSON: "+str(exc)) from exc
    if not isinstance(value,dict) or any(not isinstance(key,str) or (key and not key.startswith("/")) for key in value):
        raise RuntimeError("JSON unflatten expects an object whose keys are JSON Pointer paths.")
    if "" in value:
        if len(value)!=1: raise RuntimeError("Root JSON pointer cannot be combined with child paths.")
        result=value[""]
    else:
        result={}
        for pointer,leaf in value.items():
            segments=[_json_pointer_unescape(part) for part in pointer[1:].split("/")]
            current=result
            for index,segment in enumerate(segments):
                if index==len(segments)-1:
                    if segment in current and isinstance(current[segment],dict):
                        raise RuntimeError("Conflicting JSON Pointer paths.")
                    current[segment]=leaf
                else:
                    if segment not in current:
                        current[segment]={}
                    existing=current[segment]
                    if not isinstance(existing,dict): raise RuntimeError("Conflicting JSON Pointer paths.")
                    current=existing
    output=json.dumps(result,ensure_ascii=False,indent=2)
    return _write_text_artifact(p,"unflattened",output+"\n","JSON unflattening")


def json_keys_report(p):
    raw=_read_text_source(p)
    try: value=_load_json_reject_duplicates(raw)
    except (ValueError,json.JSONDecodeError) as exc: raise RuntimeError("Invalid JSON: "+str(exc)) from exc
    counts={}
    def visit(item,path="$"):
        if isinstance(item,dict):
            for key,child in item.items():
                child_path=path+"."+key
                counts[child_path]=counts.get(child_path,0)+1
                visit(child,child_path)
        elif isinstance(item,list):
            for index,child in enumerate(item[:100_000]):
                child_path=path+"["+str(index)+"]"
                counts[child_path]=counts.get(child_path,0)+1
                visit(child,child_path)
    visit(value)
    lines=["JSON key/path report","Unique paths: "+str(len(counts))]
    lines.extend(path+"\t"+str(count) for path,count in sorted(counts.items()))
    return _write_text_artifact(p,"keys-report","\n".join(lines)+"\n","JSON key report")


def csv_remove_empty_rows(p):
    import io
    raw=_read_text_source(p)
    try: rows=list(csv.reader(io.StringIO(raw,newline="")))
    except csv.Error as exc: raise RuntimeError("Invalid CSV: "+str(exc)) from exc
    if not rows: raise RuntimeError("CSV is empty.")
    kept=[rows[0]]
    removed=0
    for row in rows[1:]:
        if any(value.strip() for value in row): kept.append(row)
        else: removed+=1
    stream=io.StringIO(newline="")
    csv.writer(stream,lineterminator="\n").writerows(kept)
    return _write_text_artifact_ext(p,"no-empty-rows",".csv",stream.getvalue(),"CSV empty-row removal",str(removed)+" row(s) removed")


def csv_add_row_numbers(p):
    import io
    raw=_read_text_source(p)
    try: rows=list(csv.reader(io.StringIO(raw,newline="")))
    except csv.Error as exc: raise RuntimeError("Invalid CSV: "+str(exc)) from exc
    if not rows: raise RuntimeError("CSV is empty.")
    header=rows[0]
    column="_row_number"
    while column in header: column+="_"
    output=[[column]+header]
    output.extend([[str(index)]+row for index,row in enumerate(rows[1:],1)])
    stream=io.StringIO(newline="")
    csv.writer(stream,lineterminator="\n").writerows(output)
    return _write_text_artifact_ext(p,"numbered",".csv",stream.getvalue(),"CSV row numbering",str(len(rows)-1)+" data row(s)")


def csv_column_stats(p):
    import io
    raw=_read_text_source(p)
    try: rows=list(csv.reader(io.StringIO(raw,newline="")))
    except csv.Error as exc: raise RuntimeError("Invalid CSV: "+str(exc)) from exc
    if not rows: raise RuntimeError("CSV is empty.")
    headers=rows[0]
    if len(headers)>200: raise RuntimeError("CSV column statistics supports at most 200 columns.")
    body=rows[1:]
    lines=["CSV column statistics","Rows: "+str(len(body)),"Columns: "+str(len(headers))]
    for index,header in enumerate(headers):
        values=[row[index].strip() for row in body if index<len(row)]
        nonempty=[value for value in values if value]
        numeric=sum(bool(re.fullmatch(r"[+-]?\d+(?:[.,]\d+)?",value)) for value in nonempty)
        lines.append(json.dumps({"column":header,"non_empty":len(nonempty),"empty":len(body)-len(nonempty),"unique":len(set(nonempty)),"numeric":numeric},ensure_ascii=False))
    return _write_text_artifact(p,"column-stats","\n".join(lines)+"\n","CSV column statistics")


def csv_normalize_headers(p):
    import io
    raw=_read_text_source(p)
    try: rows=list(csv.reader(io.StringIO(raw,newline="")))
    except csv.Error as exc: raise RuntimeError("Invalid CSV: "+str(exc)) from exc
    if not rows: raise RuntimeError("CSV is empty.")
    used=set()
    headers=[]
    for index,value in enumerate(rows[0]):
        words=_case_words(value.strip())
        base="_".join(word.casefold() for word in words) or "column_"+str(index+1)
        name=base
        suffix=2
        while name in used:
            name=base+"_"+str(suffix)
            suffix+=1
        used.add(name)
        headers.append(name)
    rows[0]=headers
    stream=io.StringIO(newline="")
    csv.writer(stream,lineterminator="\n").writerows(rows)
    return _write_text_artifact_ext(p,"normalized-headers",".csv",stream.getvalue(),"CSV header normalization",str(len(headers))+" header(s)")


def csv_to_jsonl(p):
    import io
    raw=_read_text_source(p)
    try: rows=list(csv.reader(io.StringIO(raw,newline="")))
    except csv.Error as exc: raise RuntimeError("Invalid CSV: "+str(exc)) from exc
    if not rows: raise RuntimeError("CSV is empty.")
    headers=[]
    used=set()
    for index,value in enumerate(rows[0]):
        base=value.strip() or "column_"+str(index+1)
        name=base
        suffix=2
        while name in used:
            name=base+"_"+str(suffix)
            suffix+=1
        used.add(name)
        headers.append(name)
    if len(headers)>200 or len(rows)>100_001: raise RuntimeError("CSV-to-JSONL is limited to 100,000 rows and 200 columns.")
    if any(len(row)>len(headers) for row in rows[1:]): raise RuntimeError("CSV data row contains more fields than the header.")
    records=[dict(zip(headers,row+[""]*(len(headers)-len(row)))) for row in rows[1:]]
    output="\n".join(json.dumps(record,ensure_ascii=False,separators=(",",":")) for record in records)
    if records: output+="\n"
    return _write_text_artifact_ext(p,"records",".jsonl",output,"CSV to JSONL",str(len(records))+" record(s)")


def jsonl_to_csv(p):
    raw=_read_text_source(p)
    records=[]
    for line_number,line in enumerate(raw.splitlines(),1):
        if not line.strip(): continue
        try: value=_load_json_reject_duplicates(line)
        except (ValueError,json.JSONDecodeError) as exc: raise RuntimeError("Invalid JSONL at line "+str(line_number)+": "+str(exc)) from exc
        if not isinstance(value,dict): raise RuntimeError("JSONL to CSV requires every record to be an object.")
        records.append(value)
        if len(records)>100_000: raise RuntimeError("JSONL-to-CSV exceeds 100,000 records.")
    headers=[]
    seen=set()
    for record in records:
        for key in record:
            if key not in seen: seen.add(key); headers.append(key)
    import io
    stream=io.StringIO(newline="")
    writer=csv.writer(stream,lineterminator="\n")
    def spreadsheet_safe(value):
        if not isinstance(value,str):
            return value
        stripped=value.lstrip()
        if stripped.startswith(("=","+","@")):
            return "'"+value
        if stripped.startswith("-") and not re.fullmatch(r"-\d+(?:[.,]\d+)?",stripped):
            return "'"+value
        return value
    writer.writerow([spreadsheet_safe(key) for key in headers])
    for record in records:
        writer.writerow([spreadsheet_safe(json.dumps(record.get(key),ensure_ascii=False) if isinstance(record.get(key),(dict,list)) else ("" if record.get(key) is None else record.get(key))) for key in headers])
    return _write_text_artifact_ext(p,"records",".csv",stream.getvalue(),"JSONL to CSV",str(len(records))+" record(s)")


def text_indent_lines(p):
    raw=_read_text_source(p)
    output="\n".join(("    "+line) if line.strip() else "" for line in raw.splitlines())
    if raw.endswith(("\n","\r")): output+="\n"
    return _write_text_artifact(p,"indented",output,"Line indentation","4 spaces added to non-empty lines")


def text_unindent_lines(p):
    raw=_read_text_source(p)
    lines=raw.splitlines()
    indents=[len(line)-len(line.lstrip(" \t")) for line in lines if line.strip()]
    amount=min(indents,default=0)
    output="\n".join(line[amount:] if line.strip() else "" for line in lines)
    if raw.endswith(("\n","\r")): output+="\n"
    return _write_text_artifact(p,"unindented",output,"Common indentation removal",str(amount)+" leading character(s) removed")


def text_dedupe_paragraphs(p):
    raw=_read_text_source(p)
    paragraphs=[part.strip() for part in re.split(r"\n\s*\n",raw) if part.strip()]
    result=[]
    seen=set()
    for paragraph in paragraphs:
        key=re.sub(r"\s+"," ",paragraph).casefold()
        if key in seen: continue
        seen.add(key)
        result.append(paragraph)
    output="\n\n".join(result)+("\n" if raw.endswith(("\n","\r")) and result else "")
    return _write_text_artifact(p,"unique-paragraphs",output,"Paragraph deduplication",str(len(paragraphs)-len(result))+" duplicate paragraph(s) removed")


def text_tokenize_words(p):
    raw=_read_text_source(p)
    words=re.findall(r"[^\W_]+(?:['’][^\W_]+)?",raw,flags=re.UNICODE)
    return _write_text_artifact(p,"tokens","\n".join(words)+("\n" if words else ""),"Word tokenization",str(len(words))+" token(s)")


def text_sentence_report(p):
    raw=_read_text_source(p)
    sentences=[part.strip() for part in re.split(r"(?<=[.!?。！？])\s+",raw) if part.strip()]
    words=re.findall(r"[^\W_]+(?:['’][^\W_]+)?",raw,flags=re.UNICODE)
    counts=[len(re.findall(r"[^\W_]+(?:['’][^\W_]+)?",part,flags=re.UNICODE)) for part in sentences]
    report=[
        "Sentence statistics",
        "Sentences (heuristic): "+str(len(sentences)),
        "Words: "+str(len(words)),
        "Average words per sentence: "+(f"{len(words)/len(sentences):.2f}" if sentences else "0"),
        "Longest sentence words: "+str(max(counts,default=0)),
        "Note: punctuation-based estimate; abbreviations and multilingual text may affect accuracy.",
    ]
    return _write_text_artifact(p,"sentence-report","\n".join(report)+"\n","Sentence report")


def text_line_length_report(p):
    raw=_read_text_source(p)
    lines=raw.splitlines()
    ranked=sorted(enumerate(lines,1),key=lambda item:(-len(item[1]),item[0]))[:100]
    report=["Line length report","Total lines: "+str(len(lines)),"Longest line: "+str(max((len(line) for line in lines),default=0)),"","Rank | Line | Characters"]
    report.extend(f"{rank} | {line_number} | {len(line)}" for rank,(line_number,line) in enumerate(ranked,1))
    return _write_text_artifact(p,"line-lengths","\n".join(report)+"\n","Line-length report")


def text_normalize_newlines(p):
    raw=_read_text_source(p)
    output=raw.replace("\r\n","\n").replace("\r","\n")
    return _write_text_artifact(p,"unix-newlines",output,"Newline normalization","LF line endings")


def text_remove_zero_width(p):
    raw=_read_text_source(p)
    output="".join(char for char in raw if char not in "\u200b\u200c\u200d\u2060\ufeff\u00ad")
    return _write_text_artifact(p,"no-zero-width",output,"Invisible-character removal")


def text_extract_file_paths(p):
    raw=_read_text_source(p)
    pattern=r'(?<![A-Za-z0-9])(?:[A-Za-z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]+|/(?:[^/\s<>:"|?*]+/)*[^/\s<>:"|?*]+)'
    values=_ordered_unique(re.findall(pattern,raw))
    return _write_text_artifact(p,"file-paths","\n".join(values)+("\n" if values else ""),"File-path extraction",str(len(values))+" unique candidate(s)")


def text_sort_words(p):
    raw=_read_text_source(p)
    words=re.findall(r"[^\W_]+(?:['’][^\W_]+)?",raw,flags=re.UNICODE)
    ordered=sorted(words,key=lambda value:(value.casefold(),value))
    return _write_text_artifact(p,"sorted-words","\n".join(ordered)+("\n" if ordered else ""),"Word sorting",str(len(words))+" word(s) sorted")


def html_extract_links(p):
    raw=_read_text_source(p,max_chars=5_000_000)
    class LinkParser(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.items=[]
            self.current=None
        def handle_starttag(self,tag,attrs):
            if tag.lower()=="a":
                values=dict(attrs)
                if values.get("href"):
                    self.current={"url":values["href"],"text":"","title":values.get("title","")}
            elif tag.lower()=="img":
                values=dict(attrs)
                if values.get("src"):
                    self.items.append({"url":values["src"],"alt":values.get("alt",""),"title":values.get("title","")})
        def handle_data(self,data):
            if self.current is not None: self.current["text"]+=data
        def handle_endtag(self,tag):
            if tag.lower()=="a" and self.current is not None:
                self.items.append(self.current)
                self.current=None
    parser=LinkParser()
    try: parser.feed(raw); parser.close()
    except Exception as exc: raise RuntimeError("Invalid HTML: "+str(exc)) from exc
    seen=set()
    results=[]
    for item in parser.items:
        key=(item.get("url",""),item.get("text",""),item.get("alt",""))
        if key in seen: continue
        seen.add(key)
        results.append(json.dumps(item,ensure_ascii=False))
    output="\n".join(results)
    return _write_text_artifact_ext(p,"html-links",".jsonl",output+("\n" if output else ""),"HTML link/image extraction",str(len(results))+" item(s)")


def html_extract_images(p):
    raw=_read_text_source(p,max_chars=5_000_000)
    class ImageParser(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.items=[]
        def handle_starttag(self,tag,attrs):
            if tag.lower()=="img":
                values=dict(attrs)
                if values.get("src"): self.items.append({"src":values["src"],"alt":values.get("alt",""),"title":values.get("title","")})
    parser=ImageParser()
    try: parser.feed(raw); parser.close()
    except Exception as exc: raise RuntimeError("Invalid HTML: "+str(exc)) from exc
    unique=[]
    seen=set()
    for item in parser.items:
        if item["src"] in seen: continue
        seen.add(item["src"])
        unique.append(json.dumps(item,ensure_ascii=False))
    output="\n".join(unique)
    return _write_text_artifact_ext(p,"html-images",".jsonl",output+("\n" if output else ""),"HTML image extraction",str(len(unique))+" unique image(s)")


def html_extract_title(p):
    raw=_read_text_source(p,max_chars=5_000_000)
    class TitleParser(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.active=False
            self.parts=[]
        def handle_starttag(self,tag,attrs):
            if tag.lower()=="title": self.active=True
        def handle_endtag(self,tag):
            if tag.lower()=="title": self.active=False
        def handle_data(self,data):
            if self.active: self.parts.append(data)
    parser=TitleParser()
    try: parser.feed(raw); parser.close()
    except Exception as exc: raise RuntimeError("Invalid HTML: "+str(exc)) from exc
    title=re.sub(r"\s+"," "," ".join(parser.parts)).strip()
    return _write_text_artifact_ext(p,"html-title",".txt",title+"\n" if title else "","HTML title extraction")




class _HTMLAuditParser(HTMLParser):
    """Bounded static HTML collector. It never fetches or executes page resources."""
    VOID = {"area","base","br","col","embed","hr","img","input","link","meta","param","source","track","wbr"}
    TRACKED = {
        "html","title","meta","link","h1","h2","h3","h4","h5","h6","img","a",
        "form","input","select","textarea","button","label","main","nav",
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.nodes = {}
        self.stack = []
        self.ids = set()
        self.id_counts = {}
        self.html_attrs = {}
        self.form_sequence = 0

    def _finish(self, node):
        if node["tracked"]:
            self.nodes.setdefault(node["tag"], []).append(node)

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        values = {str(key).lower(): (value or "") for key, value in attrs}
        if tag == "html" and not self.html_attrs:
            self.html_attrs = values
        element_id = values.get("id", "").strip()
        if element_id:
            self.ids.add(element_id)
            self.id_counts[element_id] = self.id_counts.get(element_id, 0) + 1
        line = self.getpos()[0]
        parent_form = next((item for item in reversed(self.stack) if item["tag"] == "form"), None)
        if tag == "form":
            self.form_sequence += 1
            form_id = self.form_sequence
        else:
            form_id = parent_form.get("form_id") if parent_form else None
        wrapped_label = any(item["tag"] == "label" for item in self.stack)
        role = values.get("role", "").lower()
        node = {
            "tag": tag, "attrs": values, "text": "", "line": line,
            "tracked": tag in self.TRACKED or role in {"main","navigation","banner","contentinfo"},
            "form_id": form_id, "wrapped_label": wrapped_label,
        }
        if tag in self.VOID:
            self._finish(node)
        else:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag.lower() not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        tag = tag.lower()
        match = next((index for index in range(len(self.stack)-1, -1, -1) if self.stack[index]["tag"] == tag), None)
        if match is None:
            return
        closed = self.stack[match:]
        del self.stack[match:]
        for node in reversed(closed):
            self._finish(node)

    def handle_data(self, data):
        if not data:
            return
        for node in self.stack:
            if node["tracked"]:
                node["text"] += data

    def close(self):
        super().close()
        for node in reversed(self.stack):
            self._finish(node)
        self.stack.clear()


def _html_audit_data(path):
    raw = _read_text_source(path, max_chars=5_000_000)
    parser = _HTMLAuditParser()
    try:
        parser.feed(raw)
        parser.close()
    except Exception as exc:
        raise RuntimeError("Unable to parse HTML for static audit: " + str(exc)) from exc
    return parser


def _html_audit_report(path, suffix, heading, lines, finding_count):
    content = "\n".join([heading, *lines, "", "Static heuristic only; no remote URLs, scripts, forms or images were requested or executed."])
    return _write_text_artifact_ext(path, suffix, ".txt", content + "\n", heading, str(finding_count) + " finding(s)")


def html_seo_audit(p):
    data = _html_audit_data(p)
    titles = [node["text"].strip() for node in data.nodes.get("title", []) if node["text"].strip()]
    metas = data.nodes.get("meta", [])
    links = data.nodes.get("link", [])
    description = next((node["attrs"].get("content", "").strip() for node in metas if node["attrs"].get("name", "").lower() == "description"), "")
    robots = next((node["attrs"].get("content", "").strip() for node in metas if node["attrs"].get("name", "").lower() == "robots"), "")
    og_title = next((node["attrs"].get("content", "").strip() for node in metas if node["attrs"].get("property", "").lower() == "og:title"), "")
    og_description = next((node["attrs"].get("content", "").strip() for node in metas if node["attrs"].get("property", "").lower() == "og:description"), "")
    canonical = any("canonical" in node["attrs"].get("rel", "").lower().split() and node["attrs"].get("href", "").strip() for node in links)
    title = titles[0] if titles else ""
    h1_count = len(data.nodes.get("h1", []))
    images = data.nodes.get("img", [])
    missing_alt = sum("alt" not in node["attrs"] for node in images)
    findings = []
    if not title: findings.append("HIGH: missing document title")
    elif not 30 <= len(title) <= 60: findings.append("INFO: title length is outside the common 30–60 character guide")
    if not description: findings.append("WARN: missing meta description")
    elif not 70 <= len(description) <= 160: findings.append("INFO: meta description length is outside the common 70–160 character guide")
    if not canonical: findings.append("INFO: no canonical link was found")
    if not data.html_attrs.get("lang", "").strip(): findings.append("WARN: html lang attribute is missing")
    if h1_count == 0: findings.append("WARN: no H1 heading was found")
    elif h1_count > 1: findings.append("INFO: multiple H1 headings were found")
    if not og_title: findings.append("INFO: Open Graph og:title is missing")
    if not og_description: findings.append("INFO: Open Graph og:description is missing")
    if missing_alt: findings.append("WARN: " + str(missing_alt) + " image(s) have no alt attribute")
    lines = [
        "Title characters: " + str(len(title)),
        "Meta description characters: " + str(len(description)),
        "Canonical link: " + ("present" if canonical else "missing"),
        "Robots directive: " + ("present" if robots else "not declared"),
        "HTML language: " + (data.html_attrs.get("lang", "").strip() or "missing"),
        "H1 headings: " + str(h1_count),
        "Open Graph title/description: " + ("present" if og_title else "missing") + " / " + ("present" if og_description else "missing"),
        "Images missing alt: " + str(missing_alt) + " of " + str(len(images)),
        "Findings:",
    ]
    lines.extend(findings or ["No obvious baseline SEO findings."])
    return _html_audit_report(p, "seo-audit", "HTML SEO audit", lines, len(findings))


def html_accessibility_audit(p):
    data = _html_audit_data(p)
    labels_for = {node["attrs"].get("for", "").strip() for node in data.nodes.get("label", []) if node["attrs"].get("for", "").strip()}
    issues = []
    missing_alt = [node for node in data.nodes.get("img", []) if "alt" not in node["attrs"]]
    for node in missing_alt[:20]:
        issues.append("Image missing alt at line " + str(node["line"]))
    for tag in ("a", "button"):
        for node in data.nodes.get(tag, []):
            attrs = node["attrs"]
            accessible = bool(node["text"].strip() or attrs.get("aria-label", "").strip() or attrs.get("aria-labelledby", "").strip() or attrs.get("title", "").strip())
            if not accessible:
                issues.append(tag + " has no static accessible name at line " + str(node["line"]))
    controls = []
    for tag in ("input", "select", "textarea"):
        controls.extend(data.nodes.get(tag, []))
    for node in controls:
        attrs = node["attrs"]
        kind = attrs.get("type", "text").lower()
        if node["tag"] == "input" and kind in {"hidden","submit","reset","button","image"}:
            continue
        labelled = bool(attrs.get("aria-label", "").strip() or attrs.get("aria-labelledby", "").strip() or attrs.get("title", "").strip() or node["wrapped_label"])
        if attrs.get("id", "").strip() in labels_for:
            labelled = True
        if not labelled:
            issues.append(node["tag"] + " control has no associated label at line " + str(node["line"]))
    if not data.html_attrs.get("lang", "").strip():
        issues.append("Document html element has no lang attribute")
    if not any(node["tag"] == "main" or node["attrs"].get("role", "").lower() == "main" for tag_nodes in data.nodes.values() for node in tag_nodes):
        issues.append("No main landmark was found")
    headings = []
    for level in range(1, 7):
        headings.extend((int(node["tag"][1]), node["line"]) for node in data.nodes.get("h" + str(level), []))
    headings.sort(key=lambda item: item[1])
    previous = None
    for level, line in headings:
        if previous is not None and level > previous + 1:
            issues.append("Heading level jumps from H" + str(previous) + " to H" + str(level) + " at line " + str(line))
        previous = level
    lines = [
        "Images without alt: " + str(len(missing_alt)),
        "Links: " + str(len(data.nodes.get("a", []))),
        "Buttons: " + str(len(data.nodes.get("button", []))),
        "Form controls inspected: " + str(len(controls)),
        "Findings:",
    ]
    lines.extend(issues[:60] or ["No obvious baseline accessibility findings."])
    if len(issues) > 60:
        lines.append("Additional findings omitted: " + str(len(issues) - 60))
    return _html_audit_report(p, "accessibility-audit", "HTML accessibility audit", lines, len(issues))


def html_link_audit(p):
    data = _html_audit_data(p)
    issues = []
    links = data.nodes.get("a", [])
    for node in links:
        attrs = node["attrs"]
        href = attrs.get("href")
        if href is None:
            issues.append("Anchor without href at line " + str(node["line"]))
            continue
        compact = re.sub(r"[\x00-\x20]+", "", href).lower()
        if not compact:
            issues.append("Empty href at line " + str(node["line"]))
        elif compact.startswith(("javascript:","vbscript:","data:")):
            issues.append("Potentially unsafe href scheme at line " + str(node["line"]))
        target = attrs.get("target", "").lower()
        rel = set(attrs.get("rel", "").lower().split())
        if target == "_blank" and not {"noopener","noreferrer"}.intersection(rel):
            issues.append("target=_blank without rel=noopener/noreferrer at line " + str(node["line"]))
        if href.startswith("#") and len(href) > 1 and href[1:] not in data.ids:
            issues.append("Unresolved local fragment at line " + str(node["line"]))
    lines = [
        "Anchors: " + str(len(links)),
        "IDs declared: " + str(len(data.ids)),
        "Unique IDs duplicated: " + str(sum(1 for count in data.id_counts.values() if count > 1)),
        "Findings:",
    ]
    lines.extend(issues[:80] or ["No obvious baseline link findings."])
    if len(issues) > 80:
        lines.append("Additional findings omitted: " + str(len(issues) - 80))
    return _html_audit_report(p, "link-audit", "HTML link audit", lines, len(issues))


def html_form_audit(p):
    data = _html_audit_data(p)
    labels_for = {node["attrs"].get("for", "").strip() for node in data.nodes.get("label", []) if node["attrs"].get("for", "").strip()}
    forms = data.nodes.get("form", [])
    controls = []
    for tag in ("input", "select", "textarea"):
        controls.extend(data.nodes.get(tag, []))
    issues = []
    for form in forms:
        attrs = form["attrs"]
        method = attrs.get("method", "get").strip().lower() or "get"
        action = attrs.get("action", "").strip()
        normalized = re.sub(r"[\x00-\x20]+", "", action).lower()
        if normalized.startswith(("javascript:","vbscript:","data:")):
            issues.append("Form has a potentially unsafe action scheme at line " + str(form["line"]))
        if not attrs.get("method", "").strip():
            issues.append("Form uses the browser default GET method at line " + str(form["line"]))
        owned = [node for node in controls if node.get("form_id") == form["form_id"]]
        if method == "get" and any(node["tag"] == "input" and node["attrs"].get("type", "text").lower() == "password" for node in owned):
            issues.append("Password field is inside a GET form at line " + str(form["line"]))
    for node in controls:
        attrs = node["attrs"]
        kind = attrs.get("type", "text").lower()
        if node["tag"] == "input" and kind in {"button","submit","reset","image"}:
            continue
        if not attrs.get("name", "").strip():
            issues.append(node["tag"] + " control has no name at line " + str(node["line"]))
        labelled = bool(attrs.get("aria-label", "").strip() or attrs.get("aria-labelledby", "").strip() or attrs.get("title", "").strip() or node["wrapped_label"])
        if attrs.get("id", "").strip() in labels_for:
            labelled = True
        if not labelled:
            issues.append(node["tag"] + " control has no associated label at line " + str(node["line"]))
        if node["tag"] == "input" and kind == "password" and not attrs.get("autocomplete", "").strip():
            issues.append("Password input has no autocomplete hint at line " + str(node["line"]))
    lines = [
        "Forms: " + str(len(forms)),
        "Controls: " + str(len(controls)),
        "Findings:",
    ]
    lines.extend(issues[:80] or ["No obvious baseline form findings."])
    if len(issues) > 80:
        lines.append("Additional findings omitted: " + str(len(issues) - 80))
    return _html_audit_report(p, "form-audit", "HTML form audit", lines, len(issues))


def html_image_audit(p):
    data = _html_audit_data(p)
    images = data.nodes.get("img", [])
    missing_alt = [node for node in images if "alt" not in node["attrs"]]
    empty_alt = [node for node in images if "alt" in node["attrs"] and not node["attrs"].get("alt", "").strip()]
    missing_dimensions = [node for node in images if not node["attrs"].get("width", "").strip() or not node["attrs"].get("height", "").strip()]
    not_lazy = [node for node in images if node["attrs"].get("loading", "").lower() != "lazy"]
    issues = []
    for node in missing_alt[:30]:
        issues.append("Missing alt at line " + str(node["line"]))
    for node in missing_dimensions[:30]:
        issues.append("Missing width or height at line " + str(node["line"]))
    lines = [
        "Images: " + str(len(images)),
        "Missing alt attribute: " + str(len(missing_alt)),
        "Empty alt (may be decorative): " + str(len(empty_alt)),
        "Missing width or height: " + str(len(missing_dimensions)),
        "Not marked loading=lazy: " + str(len(not_lazy)) + " (informational; eager loading can be intentional)",
        "Findings:",
    ]
    lines.extend(issues or ["No obvious baseline image findings."])
    return _html_audit_report(p, "image-audit", "HTML image audit", lines, len(issues))


def html_sanitize(p):
    raw=_read_text_source(p,max_chars=5_000_000)
    class Sanitizer(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=False)
            self.parts=[]
            self.skip_stack=[]
            self.void={"area","base","br","col","embed","hr","img","input","link","meta","param","source","track","wbr"}
            self.drop={"script","style","iframe","object","embed","applet"}
        def handle_starttag(self,tag,attrs):
            tag=tag.lower()
            if self.skip_stack:
                if tag not in self.void: self.skip_stack.append(tag)
                return
            if tag in self.drop:
                if tag not in self.void: self.skip_stack.append(tag)
                return
            safe=[]
            for key,value in attrs:
                key=key.lower()
                if key.startswith("on") or key in {"style","srcdoc","srcset"}: continue
                if value is not None and key in {"href","src","xlink:href","formaction","action","poster"}:
                    normalized=re.sub(r"[\x00-\x20]+","",value).lower()
                    if normalized.startswith(("javascript:","vbscript:","data:","blob:","file:")): continue
                safe.append((key,value))
            self.parts.append("<"+tag)
            for key,value in safe:
                if value is None: self.parts.append(" "+key)
                else: self.parts.append(" "+key+'="'+escape(value,quote=True)+'"')
            self.parts.append(">")
        def handle_startendtag(self,tag,attrs):
            tag=tag.lower()
            if self.skip_stack or tag in self.drop: return
            safe=[]
            for key,value in attrs:
                key=key.lower()
                if key.startswith("on") or key in {"style","srcdoc","srcset"}: continue
                if value is not None and key in {"href","src","xlink:href","formaction","action","poster"}:
                    normalized=re.sub(r"[\x00-\x20]+","",value).lower()
                    if normalized.startswith(("javascript:","vbscript:","data:","blob:","file:")): continue
                safe.append((key,value))
            self.parts.append("<"+tag)
            for key,value in safe:
                if value is None: self.parts.append(" "+key)
                else: self.parts.append(" "+key+'="'+escape(value,quote=True)+'"')
            self.parts.append("/>")
        def handle_endtag(self,tag):
            tag=tag.lower()
            if self.skip_stack:
                if tag in self.skip_stack:
                    index=len(self.skip_stack)-1-self.skip_stack[::-1].index(tag)
                    self.skip_stack=self.skip_stack[:index]
                return
            if tag not in self.void: self.parts.append("</"+tag+">")
        def handle_data(self,data):
            if not self.skip_stack: self.parts.append(data)
        def handle_entityref(self,name):
            if not self.skip_stack: self.parts.append("&"+name+";")
        def handle_charref(self,name):
            if not self.skip_stack: self.parts.append("&#"+name+";")
        def handle_comment(self,data): pass
        def handle_decl(self,decl):
            if not self.skip_stack and not re.match(r"\s*doctype\s+html",decl,re.I): self.parts.append("<!"+decl+">")
    parser=Sanitizer()
    try: parser.feed(raw); parser.close()
    except Exception as exc: raise RuntimeError("HTML sanitization failed: "+str(exc)) from exc
    output="".join(parser.parts)
    return _write_text_artifact_ext(p,"sanitized",".html",output,"HTML sanitization","removed executable elements, event handlers, inline styles and unsafe URL schemes")


def _xml_safe_tag(value,index=1):
    tag=re.sub(r"[^A-Za-z0-9_.-]","_",str(value)) or "item_"+str(index)
    if not re.match(r"[A-Za-z_]",tag): tag="item_"+tag
    return tag


def json_to_xml(p):
    import xml.etree.ElementTree as ET
    raw=_read_text_source(p)
    try: value=_load_json_reject_duplicates(raw)
    except (ValueError,json.JSONDecodeError) as exc: raise RuntimeError("Invalid JSON: "+str(exc)) from exc
    if not isinstance(value,dict): raise RuntimeError("JSON-to-XML expects a top-level object.")
    def add_value(parent,name,item):
        if isinstance(item,list):
            for child in item: add_value(parent,name,child)
            return
        element=ET.SubElement(parent,_xml_safe_tag(name))
        if isinstance(item,dict):
            for key,child in item.items():
                if key=="#text":
                    element.text="" if child is None else str(child)
                elif key.startswith("@"):
                    element.set(_xml_safe_tag(key[1:]),"" if child is None else str(child))
                else:
                    add_value(element,key,child)
        elif item is not None:
            element.text=str(item).lower() if isinstance(item,bool) else str(item)
    root=ET.Element("root")
    for key,item in value.items():
        if key.startswith("@"):
            root.set(_xml_safe_tag(key[1:]),"" if item is None else str(item))
        elif key=="#text":
            root.text="" if item is None else str(item)
        else:
            add_value(root,key,item)
    output=ET.tostring(root,encoding="unicode",short_empty_elements=True)
    return _write_text_artifact_ext(p,"converted",".xml",output,"JSON to XML conversion")


def json_type_report(p):
    raw=_read_text_source(p)
    try: value=_load_json_reject_duplicates(raw)
    except (ValueError,json.JSONDecodeError) as exc: raise RuntimeError("Invalid JSON: "+str(exc)) from exc
    counts={"object":0,"array":0,"string":0,"number":0,"boolean":0,"null":0}
    max_depth=0
    def visit(item,depth):
        nonlocal max_depth
        max_depth=max(max_depth,depth)
        if item is None: counts["null"]+=1
        elif isinstance(item,bool): counts["boolean"]+=1
        elif isinstance(item,(int,float)): counts["number"]+=1
        elif isinstance(item,str): counts["string"]+=1
        elif isinstance(item,dict):
            counts["object"]+=1
            for child in item.values(): visit(child,depth+1)
        elif isinstance(item,list):
            counts["array"]+=1
            for child in item: visit(child,depth+1)
    visit(value,0)
    lines=["JSON type report","Maximum depth: "+str(max_depth)]
    lines.extend(kind+": "+str(count) for kind,count in counts.items())
    return _write_text_artifact_ext(p,"type-report",".txt","\n".join(lines)+"\n","JSON type report")


def json_escape_string(p):
    raw=_read_text_source(p)
    return _write_text_artifact_ext(p,"json-string",".json",json.dumps(raw,ensure_ascii=False)+"\n","JSON string escaping")


def json_unescape_string(p):
    raw=_read_text_source(p)
    try: value=json.loads(raw)
    except json.JSONDecodeError as exc: raise RuntimeError("Input must be a valid JSON string scalar.") from exc
    if not isinstance(value,str): raise RuntimeError("Input must be a JSON string, not an object, array or number.")
    return _write_text_artifact_ext(p,"unescaped-string",".txt",value,"JSON string decoding")


def csv_unique_values(p):
    import io
    raw=_read_text_source(p)
    try: rows=list(csv.reader(io.StringIO(raw,newline="")))
    except csv.Error as exc: raise RuntimeError("Invalid CSV: "+str(exc)) from exc
    if not rows: raise RuntimeError("CSV is empty.")
    header=rows[0]
    if len(header)>200: raise RuntimeError("CSV unique-value report supports at most 200 columns.")
    columns=[]
    for index,name in enumerate(header):
        counts={}
        order=[]
        for row in rows[1:]:
            value=row[index].strip() if index<len(row) else ""
            if not value: continue
            if value not in counts: order.append(value); counts[value]=0
            counts[value]+=1
        for value in order:
            columns.append(json.dumps({"column":name,"value":value,"count":counts[value]},ensure_ascii=False))
    output="\n".join(columns)
    return _write_text_artifact_ext(p,"unique-values",".txt",output+("\n" if output else ""),"CSV unique-value report",str(len(columns))+" column/value pair(s)")


def xml_tree_report(p):
    import xml.etree.ElementTree as ET
    raw=_read_text_source(p)
    if re.search(r"<!\s*(?:DOCTYPE|ENTITY)\b",raw,re.I):
        raise RuntimeError("XML DTD and ENTITY declarations are not supported.")
    try: root=ET.fromstring(raw)
    except ET.ParseError as exc: raise RuntimeError("Invalid XML: "+str(exc)) from exc
    tags={}
    attributes=0
    text_nodes=0
    max_depth=0
    def visit(element,depth):
        nonlocal attributes,text_nodes,max_depth
        max_depth=max(max_depth,depth)
        tags[element.tag]=tags.get(element.tag,0)+1
        attributes+=len(element.attrib)
        if (element.text or "").strip(): text_nodes+=1
        for child in list(element): visit(child,depth+1)
    visit(root,1)
    lines=["XML tree report","Root: "+root.tag,"Elements: "+str(sum(tags.values())),"Attributes: "+str(attributes),
      "Non-empty text nodes: "+str(text_nodes),"Maximum depth: "+str(max_depth),"","Element counts"]
    lines.extend(tag+"\t"+str(count) for tag,count in sorted(tags.items()))
    return _write_text_artifact_ext(p,"xml-tree-report",".txt","\n".join(lines)+"\n","XML tree report")


def text_sentence_case(p):
    raw=_read_text_source(p)
    value=raw.lower()
    return _write_text_artifact(p,"sentence-case",re.sub(r"(^|[.!?。！？]\s+)([^\W\d_])",lambda match:match.group(1)+match.group(2).upper(),value,flags=re.UNICODE),"Sentence case conversion")


def text_normalize_quotes(p):
    raw=_read_text_source(p)
    table=str.maketrans({
        "\u2018":"'","\u2019":"'","\u201a":"'","\u201b":"'","\u2032":"'","\u2035":"'","\u201c":'"',
        "\u201d":'"',"\u201e":'"',"\u201f":'"',"\u2033":'"',"\u2036":'"',"\u00ab":'"',"\u00bb":'"',
        "\u2039":"'","\u203a":"'",
    })
    return _write_text_artifact(p,"straight-quotes",raw.translate(table),"Quote normalization")


def text_normalize_dashes(p):
    raw=_read_text_source(p)
    return _write_text_artifact(p,"hyphen-dashes",re.sub(r"[\u2010-\u2015\u2212\ufe58\ufe63\uff0d]","-",raw),"Dash normalization")


def text_reverse_word_order(p):
    raw=_read_text_source(p)
    output="\n".join(" ".join(reversed(line.split())) for line in raw.splitlines())
    if raw.endswith(("\n","\r")): output+="\n"
    return _write_text_artifact(p,"reversed-words",output,"Word-order reversal")


def text_extract_words(p):
    raw=_read_text_source(p)
    words=re.findall(r"[^\W_]+(?:['’][^\W_]+)?",raw,flags=re.UNICODE)
    values=_ordered_unique(words)
    return _write_text_artifact(p,"unique-words","\n".join(values)+("\n" if values else ""),"Unique word extraction",str(len(values))+" unique word(s)")


def _sentence_parts(raw):
    return [match.group(0).strip() for match in re.finditer(r".+?(?:[.!?。！？]+(?=\s|$)|$)",raw,re.S) if match.group(0).strip()]


def text_extract_sentences(p):
    raw=_read_text_source(p)
    values=_sentence_parts(re.sub(r"\s+"," ",raw.strip()))
    return _write_text_artifact(p,"sentences","\n".join(values)+("\n" if values else ""),"Sentence extraction",str(len(values))+" sentence(s); punctuation heuristic")


def text_dedupe_sentences(p):
    raw=_read_text_source(p)
    values=_sentence_parts(re.sub(r"\s+"," ",raw.strip()))
    seen=set()
    kept=[]
    for value in values:
        key=re.sub(r"[.!?。！？]+$","",value).strip().casefold()
        if key in seen: continue
        seen.add(key)
        kept.append(value)
    return _write_text_artifact(p,"unique-sentences"," ".join(kept)+("\n" if kept else ""),"Duplicate sentence removal",str(len(values)-len(kept))+" duplicate sentence(s) removed")


def text_remove_markdown_formatting(p):
    raw=_read_text_source(p)
    value=re.sub(r"!\[([^\]]*)\]\([^)]+\)",r"\1",raw)
    value=re.sub(r"\[([^\]]+)\]\([^)]+\)",r"\1",value)
    value=re.sub(r"(?m)^\s{0,3}#{1,6}\s*","",value)
    value=re.sub(r"(?m)^\s{0,3}>\s?","",value)
    value=re.sub(r"(?m)^\s*[-+*]\s+","",value)
    value=re.sub(r"(?m)^\s*\d+[.)]\s+","",value)
    value=re.sub(r"\x60([^\x60]*)\x60",r"\1",value)
    value=re.sub(r"(\*\*|__|~~|(?<!\w)[*_])","",value)
    value=re.sub(r"(?m)^\s*([-*_]){3,}\s*$","",value)
    return _write_text_artifact(p,"plain-markdown",value,"Markdown formatting removal")


def _markdown_slug(value):
    normalized=unicodedata.normalize("NFKD",value.lower().replace("đ","d"))
    ascii_text=normalized.encode("ascii","ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+","-",ascii_text).strip("-")


def _markdown_heading_rows(raw):
    values=[]
    in_fence=False
    fence_char=None
    fence_len=0
    for line in raw.splitlines():
        stripped=line.lstrip()
        marker=stripped[:1]
        length=len(stripped)-len(stripped.lstrip(marker)) if marker in (chr(96),"~") else 0
        if length>=3:
            if not in_fence:
                in_fence=True;fence_char=marker;fence_len=length
            elif marker==fence_char and length>=fence_len:
                in_fence=False;fence_char=None;fence_len=0
            continue
        if in_fence: continue
        match=re.match(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$",line)
        if match:
            title=re.sub(r"\s+#+\s*$","",match.group(2)).strip()
            values.append((len(match.group(1)),title))
    return values


def text_markdown_toc(p):
    raw=_read_text_source(p)
    headings=_markdown_heading_rows(raw)
    used={}
    lines=[]
    for level,title in headings:
        base=_markdown_slug(re.sub(r"[*_\x60\[\]]","",title)) or "section"
        count=used.get(base,0)+1;used[base]=count
        slug=base if count==1 else base+"-"+str(count)
        lines.append("  "*max(0,level-1)+"- ["+title+"](#"+slug+")")
    return _write_text_artifact(p,"table-of-contents","\n".join(lines)+("\n" if lines else ""),"Markdown table of contents",str(len(lines))+" heading(s)")


def text_markdown_code_blocks(p):
    raw=_read_text_source(p)
    lines=raw.splitlines()
    records=[]
    index=0
    while index<len(lines):
        stripped=lines[index].lstrip()
        marker=stripped[:1]
        fence_len=len(stripped)-len(stripped.lstrip(marker)) if marker in (chr(96),"~") else 0
        if fence_len<3:
            index+=1;continue
        info=stripped[fence_len:].strip()
        start=index+1;index+=1;body=[]
        closed=False
        while index<len(lines):
            candidate=lines[index].lstrip()
            count=len(candidate)-len(candidate.lstrip(marker)) if candidate.startswith(marker) else 0
            if count>=fence_len and not candidate[count:].strip():
                closed=True;index+=1;break
            body.append(lines[index]);index+=1
        records.append(json.dumps({"index":len(records)+1,"language":info.split()[0] if info else "","start_line":start,"closed":closed,"code":"\n".join(body)},ensure_ascii=False))
    output="\n".join(records)
    return _write_text_artifact_ext(p,"code-blocks",".jsonl",output+("\n" if output else ""),"Markdown code block extraction",str(len(records))+" block(s)")


def _markdown_table_cells(line):
    value=line.strip()
    if value.startswith("|"): value=value[1:]
    if value.endswith("|"): value=value[:-1]
    cells=[];current=[];escaped=False
    for char in value:
        if escaped:
            current.append(char);escaped=False
        elif char=="\\":
            escaped=True
        elif char=="|":
            cells.append("".join(current).strip());current=[]
        else:
            current.append(char)
    if escaped: current.append("\\")
    cells.append("".join(current).strip())
    return cells


def text_markdown_table_extract(p):
    raw=_read_text_source(p)
    lines=raw.splitlines()
    for index in range(len(lines)-1):
        header=lines[index].strip()
        separator=lines[index+1].strip()
        if "|" not in header or not re.fullmatch(r"\|?[\s:|-]+\|?",separator):
            continue
        headers=_markdown_table_cells(header)
        marks=_markdown_table_cells(separator)
        if len(headers)!=len(marks) or not all(re.fullmatch(r":?-{3,}:?",item.replace(" ","")) for item in marks):
            continue
        rows=[headers]
        cursor=index+2
        while cursor<len(lines) and "|" in lines[cursor]:
            row=_markdown_table_cells(lines[cursor])
            if len(row)<len(headers): row+=[""]*(len(headers)-len(row))
            rows.append(row[:len(headers)])
            cursor+=1
        import io
        stream=io.StringIO(newline="")
        csv.writer(stream,lineterminator="\n").writerows(rows)
        return _write_text_artifact_ext(p,"markdown-table",".csv",stream.getvalue(),"Markdown table extraction",str(len(rows)-1)+" row(s)")
    return _write_text_artifact_ext(p,"markdown-table",".csv","","Markdown table extraction","no Markdown table found")


def text_extract_numbered_lists(p):
    raw=_read_text_source(p)
    values=[]
    for line in raw.splitlines():
        match=re.match(r"^\s{0,3}\d{1,6}[.)]\s+(.+?)\s*$",line)
        if match: values.append(match.group(1))
    return _write_text_artifact(p,"numbered-items","\n".join(values)+("\n" if values else ""),"Numbered-list extraction",str(len(values))+" item(s)")


def text_join_hyphenated_lines(p):
    raw=_read_text_source(p).replace("\r\n","\n").replace("\r","\n")
    output=re.sub(r"(?<=\w)-[ \t]*\n[ \t]*(?=\w)","",raw,flags=re.UNICODE)
    return _write_text_artifact(p,"joined-hyphenated",output,"Hyphenated-line joining")


def text_strip_bom(p):
    raw=_read_text_source(p)
    output=raw[1:] if raw.startswith("\ufeff") else raw
    return _write_text_artifact(p,"no-bom",output,"BOM removal")


def text_normalize_paragraph_spacing(p):
    raw=_read_text_source(p).replace("\r\n","\n").replace("\r","\n")
    output=re.sub(r"\n[ \t]*\n(?:[ \t]*\n)+","\n\n",raw)
    return _write_text_artifact(p,"paragraph-spacing",output,"Paragraph spacing normalization")


def self_valid_date(value,formats,datetime_module):
    for fmt in formats:
        try:
            datetime_module.strptime(value,fmt)
            return True
        except ValueError:
            pass
    return False


def csv_schema_infer(p):
    import io
    from datetime import datetime
    raw=_read_text_source(p)
    try: rows=list(csv.reader(io.StringIO(raw,newline="")))
    except csv.Error as exc: raise RuntimeError("Invalid CSV: "+str(exc)) from exc
    if not rows: raise RuntimeError("CSV is empty.")
    headers=rows[0]
    if len(headers)>200 or len(rows)>100_001: raise RuntimeError("CSV schema inference is limited to 100,000 rows and 200 columns.")
    body=rows[1:]
    date_formats=("%Y-%m-%d","%Y/%m/%d","%d/%m/%Y","%m/%d/%Y")
    lines=["CSV inferred schema","Rows: "+str(len(body)),"Columns: "+str(len(headers))]
    for index,header in enumerate(headers):
        values=[row[index].strip() for row in body if index<len(row) and row[index].strip()]
        kind="empty"
        if values:
            if all(value.lower() in ("true","false","yes","no") for value in values): kind="boolean"
            elif all(re.fullmatch(r"[+-]?\d+",value) for value in values): kind="integer"
            elif all(re.fullmatch(r"[+-]?(?:\d+[.,]\d+|\d+[eE][+-]?\d+)",value) for value in values): kind="decimal"
            elif all(self_valid_date(value,date_formats,datetime) for value in values): kind="date"
            elif all(value.lower() in ("0","1") for value in values): kind="boolean"
            else: kind="text"
        lines.append(json.dumps({"column":header,"type":kind,"non_empty":len(values),"empty":len(body)-len(values),"unique":len(set(values))},ensure_ascii=False))
    return _write_text_artifact(p,"schema-report","\n".join(lines)+"\n","CSV schema inference")


def csv_duplicates_report(p):
    import io
    from collections import Counter
    raw=_read_text_source(p)
    try: rows=list(csv.reader(io.StringIO(raw,newline="")))
    except csv.Error as exc: raise RuntimeError("Invalid CSV: "+str(exc)) from exc
    if not rows: raise RuntimeError("CSV is empty.")
    if len(rows)>100_001 or max((len(row) for row in rows),default=0)>200: raise RuntimeError("CSV duplicate report is limited to 100,000 rows and 200 columns.")
    counts=Counter(tuple(row) for row in rows[1:])
    duplicated=[{"row":list(row),"count":count} for row,count in counts.items() if count>1]
    lines=["CSV duplicate report","Data rows: "+str(len(rows)-1),"Unique rows: "+str(len(counts)),"Duplicated row groups: "+str(len(duplicated)),"Duplicate occurrences: "+str(sum(count-1 for count in counts.values() if count>1))]
    lines.extend(json.dumps(item,ensure_ascii=False) for item in duplicated[:500])
    return _write_text_artifact(p,"duplicates-report","\n".join(lines)+"\n","CSV duplicate report")


def csv_sample_rows(p):
    import io
    raw=_read_text_source(p)
    try: rows=list(csv.reader(io.StringIO(raw,newline="")))
    except csv.Error as exc: raise RuntimeError("Invalid CSV: "+str(exc)) from exc
    if not rows: raise RuntimeError("CSV is empty.")
    stream=io.StringIO(newline="")
    csv.writer(stream,lineterminator="\n").writerows(rows[:21])
    return _write_text_artifact_ext(p,"sample",".csv",stream.getvalue(),"CSV first-row sample",str(min(20,max(0,len(rows)-1)))+" data row(s)")


def json_array_stats(p):
    raw=_read_text_source(p)
    try: value=_load_json_reject_duplicates(raw)
    except (ValueError,json.JSONDecodeError) as exc: raise RuntimeError("Invalid JSON: "+str(exc)) from exc
    if not isinstance(value,list): raise RuntimeError("JSON array statistics expects a top-level array.")
    if len(value)>100_000: raise RuntimeError("JSON array statistics exceeds 100,000 items.")
    counts={"object":0,"array":0,"string":0,"number":0,"boolean":0,"null":0}
    key_counts={}
    for item in value:
        if item is None: counts["null"]+=1
        elif isinstance(item,bool): counts["boolean"]+=1
        elif isinstance(item,(int,float)): counts["number"]+=1
        elif isinstance(item,str): counts["string"]+=1
        elif isinstance(item,list): counts["array"]+=1
        elif isinstance(item,dict):
            counts["object"]+=1
            for key in item: key_counts[key]=key_counts.get(key,0)+1
    lines=["JSON array statistics","Items: "+str(len(value))]+[key+": "+str(count) for key,count in counts.items()]+["Object keys:"]
    lines.extend(key+"\t"+str(count) for key,count in sorted(key_counts.items()))
    return _write_text_artifact(p,"array-stats","\n".join(lines)+"\n","JSON array statistics")


def json_canonicalize(p):
    raw=_read_text_source(p)
    try: value=_load_json_reject_duplicates(raw)
    except (ValueError,json.JSONDecodeError) as exc: raise RuntimeError("Invalid JSON: "+str(exc)) from exc
    output=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False)
    return _write_text_artifact_ext(p,"canonical",".json",output,"Canonical JSON serialization")


def _ordered_unique_casefold(values):
    result=[]
    seen=set()
    for value in values:
        key=value.casefold()
        if key not in seen:
            seen.add(key)
            result.append(value)
    return result


def text_extract_todo_comments(p):
    raw=_read_text_source(p)
    results=[]
    for line_number,line in enumerate(raw.splitlines(),1):
        match=re.search(r"\b(TODO|FIXME|BUG|HACK|XXX|NOTE)\b\s*[:\-]?\s*(.*)",line,re.I)
        if match:
            results.append(f"{line_number}\t{match.group(1).upper()}\t{match.group(2).strip()}")
    output="\n".join(results)
    return _write_text_artifact(p,"todo-comments",output+("\n" if output else ""),"TODO/FIXME extraction",str(len(results))+" item(s)")


def text_extract_markdown_images(p):
    raw=_read_text_source(p)
    values=[]
    pattern=r"!\[([^\]\n]*)\]\(([^)\s]+)(?:\s+[\x22\x27]([^\x22\x27]*)[\x22\x27])?\)"
    for match in re.finditer(pattern,raw):
        alt,url,title=match.groups()
        values.append(json.dumps({"alt":alt,"url":url,"title":title or ""},ensure_ascii=False))
    output="\n".join(_ordered_unique_casefold(values))
    return _write_text_artifact(p,"markdown-images",output+("\n" if output else ""),"Markdown image extraction",str(len(values))+" image(s)")


def text_strip_markdown_frontmatter(p):
    raw=_read_text_source(p)
    lines=raw.splitlines(keepends=True)
    if not lines or lines[0].strip()!="---":
        return _write_text_artifact(p,"no-frontmatter",raw,"Markdown frontmatter removal","no frontmatter detected")
    closing=None
    for index in range(1,len(lines)):
        if lines[index].strip() in {"---","..."}:
            closing=index
            break
    if closing is None:
        raise RuntimeError("Markdown frontmatter starts with --- but has no closing --- or ... delimiter.")
    output="".join(lines[closing+1:])
    return _write_text_artifact(p,"no-frontmatter",output,"Markdown frontmatter removal","frontmatter removed")


def text_markdown_to_plain(p):
    raw=_read_text_source(p)
    lines=[]
    fence=chr(96)*3
    in_fence=False
    for line in raw.splitlines():
        stripped=line.lstrip()
        if stripped.startswith((fence,"~~~")):
            in_fence=not in_fence
            continue
        if in_fence:
            lines.append(line)
            continue
        value=line
        value=re.sub(r"!\[([^\]]*)\]\([^)]+\)",r"\1",value)
        value=re.sub(r"(?<!!)\[([^\]]+)\]\([^)]+\)",r"\1",value)
        value=re.sub(r"<(https?://[^>]+)>",r"\1",value)
        value=re.sub(r"^\s{0,3}#{1,6}\s*","",value)
        value=re.sub(r"^\s{0,3}(?:[-*+]|\d+[.)])\s+","",value)
        value=re.sub(r"^\s{0,3}>\s?","",value)
        value=re.sub(r"^\s{0,3}[-*_]{3,}\s*$","",value)
        value=re.sub(r"(\*\*|__|\*|_|~~|"+re.escape(chr(96))+r"+)","",value)
        value=re.sub(r"<[^>]+>","",value)
        lines.append(value)
    output="\n".join(lines)
    output=re.sub(r"\n{3,}","\n\n",output).strip()
    return _write_text_artifact(p,"markdown-plain",output,"Markdown to plain text")


def text_sort_unique_words(p):
    raw=_read_text_source(p)
    words=re.findall(r"[^\W_]+(?:['’][^\W_]+)?",raw,flags=re.UNICODE)
    unique=_ordered_unique_casefold(words)
    unique.sort(key=lambda value:(value.casefold(),value))
    output="\n".join(unique)
    return _write_text_artifact(p,"sorted-words",output+("\n" if output else ""),"Unique word sorting",str(len(unique))+" word(s)")


def text_word_to_lines(p):
    raw=_read_text_source(p)
    words=re.findall(r"\S+",raw,flags=re.UNICODE)
    output="\n".join(words)
    return _write_text_artifact(p,"one-word-per-line",output+("\n" if output else ""),"Word to lines conversion",str(len(words))+" token(s)")


def text_join_lines(p):
    raw=_read_text_source(p)
    values=[line.strip() for line in raw.splitlines() if line.strip()]
    output=" ".join(values)
    return _write_text_artifact(p,"joined-lines",output,"Line joining",str(len(values))+" non-empty line(s)")


def text_extract_domains(p):
    raw=_read_text_source(p)
    pattern=r"(?<![@\w.-])(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,63}(?![\w-])"
    values=[value.rstrip(".").lower() for value in re.findall(pattern,raw,re.I)]
    values=_ordered_unique_casefold(values)
    return _write_text_artifact(p,"domains","\n".join(values)+("\n" if values else ""),"Domain extraction",str(len(values))+" domain(s)")


def text_extract_uuids(p):
    raw=_read_text_source(p)
    pattern=r"(?<![0-9A-Fa-f])[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[1-5][0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}(?![0-9A-Fa-f])"
    values=_ordered_unique_casefold(re.findall(pattern,raw))
    return _write_text_artifact(p,"uuids","\n".join(values)+("\n" if values else ""),"UUID extraction",str(len(values))+" UUID(s)")


def text_extract_semver(p):
    raw=_read_text_source(p)
    pattern=r"(?<![A-Za-z0-9])v?(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?(?![A-Za-z0-9])"
    values=_ordered_unique_casefold(re.findall(pattern,raw))
    return _write_text_artifact(p,"semver","\n".join(values)+("\n" if values else ""),"Semantic version extraction",str(len(values))+" version(s)")


def text_extract_ipv6(p):
    import ipaddress
    raw=_read_text_source(p)
    candidates=re.findall(r"(?<![A-Za-z0-9:])(?:[0-9A-Fa-f]{0,4}:){2,7}[0-9A-Fa-f]{0,4}(?![A-Za-z0-9:])",raw)
    values=[]
    for value in candidates:
        try:
            parsed=ipaddress.ip_address(value)
            if parsed.version==6:
                canonical=parsed.compressed
                if canonical not in values: values.append(canonical)
        except ValueError:
            continue
    return _write_text_artifact(p,"ipv6","\n".join(values)+("\n" if values else ""),"IPv6 extraction",str(len(values))+" valid address(es)")


def text_redact_secrets(p):
    raw=_read_text_source(p)
    patterns=[
        (r"\bgithub_pat_[A-Za-z0-9_]{20,}\b","GitHub token"),
        (r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b","GitHub token"),
        (r"\bsk-[A-Za-z0-9_-]{20,}\b","API key"),
        (r"\bAIza[0-9A-Za-z_-]{35}\b","Google API key"),
        (r"\bAKIA[0-9A-Z]{16}\b","AWS access key"),
        (r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b","Slack token"),
        (r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b","JWT"),
    ]
    output=raw
    total=0
    for pattern,label in patterns:
        output,count=re.subn(pattern,"[REDACTED:"+label+"]",output)
        total+=count
    assignment=r"(?i)\b(api[_-]?key|access[_-]?token|secret|password|client[_-]?secret)\b(\s*[:=]\s*)([\x22\x27]?)([^\s,;\x22\x27]+)"
    def replace_assignment(match):
        nonlocal total
        total+=1
        return match.group(1)+match.group(2)+match.group(3)+"[REDACTED]"
    output=re.sub(assignment,replace_assignment,output)
    return _write_text_artifact(p,"redacted-secrets",output,"Secret redaction",str(total)+" candidate(s) redacted")


def text_extract_comment_lines(p):
    raw=_read_text_source(p)
    results=[]
    patterns=(r"//",r"/\*",r"\*",r"\*/",r"--",r"#")
    for line_number,line in enumerate(raw.splitlines(),1):
        stripped=line.lstrip()
        if any(re.match(r"^\s*"+pattern,line) for pattern in patterns):
            results.append(f"{line_number}\t{stripped}")
    output="\n".join(results)
    return _write_text_artifact(p,"comment-lines",output+("\n" if output else ""),"Comment-line extraction",str(len(results))+" line(s)")


def text_tabs_to_spaces(p):
    raw=_read_text_source(p)
    output=raw.expandtabs(4)
    return _write_text_artifact(p,"spaces",output,"Tabs to four spaces")


def text_escape_regex(p):
    raw=_read_text_source(p)
    output=re.escape(raw)
    return _write_text_artifact(p,"regex-escaped",output,"Regex escaping")


def text_unescape_regex(p):
    raw=_read_text_source(p)
    output=re.sub(r"\\([.^$*+?{}\[\]|()\\])",r"\1",raw)
    return _write_text_artifact(p,"regex-unescaped",output,"Regex unescaping")


def json_merge_objects(p):
    raw=_read_text_source(p)
    try: values=_load_json_reject_duplicates(raw)
    except (ValueError,json.JSONDecodeError) as exc: raise RuntimeError("Invalid JSON: "+str(exc)) from exc
    if not isinstance(values,list) or any(not isinstance(value,dict) for value in values):
        raise RuntimeError("JSON merge expects an array of objects.")
    if len(values)>10_000: raise RuntimeError("JSON merge is limited to 10,000 objects.")
    merged={}
    for value in values:
        merged.update(value)
    output=json.dumps(merged,ensure_ascii=False,indent=2,allow_nan=False)
    return _write_text_artifact(p,"merged-object",output+"\n","JSON object merge",str(len(values))+" object(s)")


def json_array_dedupe(p):
    raw=_read_text_source(p)
    try: values=_load_json_reject_duplicates(raw)
    except (ValueError,json.JSONDecodeError) as exc: raise RuntimeError("Invalid JSON: "+str(exc)) from exc
    if not isinstance(values,list): raise RuntimeError("JSON array deduplication expects a top-level array.")
    seen=set()
    unique=[]
    for value in values:
        try: key=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False)
        except ValueError as exc: raise RuntimeError("JSON contains a non-finite numeric value.") from exc
        if key not in seen:
            seen.add(key)
            unique.append(value)
        if len(unique)>100_000: raise RuntimeError("JSON array deduplication exceeds 100,000 unique items.")
    output=json.dumps(unique,ensure_ascii=False,indent=2,allow_nan=False)
    return _write_text_artifact(p,"unique-array",output+"\n","JSON array deduplication",str(len(values)-len(unique))+" duplicate item(s) removed")


def json_array_to_lines(p):
    raw=_read_text_source(p)
    try: values=_load_json_reject_duplicates(raw)
    except (ValueError,json.JSONDecodeError) as exc: raise RuntimeError("Invalid JSON: "+str(exc)) from exc
    if not isinstance(values,list): raise RuntimeError("JSON array to lines expects a top-level array.")
    if len(values)>100_000: raise RuntimeError("JSON array to lines is limited to 100,000 items.")
    if any(not isinstance(value,str) for value in values):
        raise RuntimeError("JSON array to lines requires every item to be a string.")
    output="\n".join(values)
    return _write_text_artifact(p,"array-lines",output+("\n" if output else ""),"JSON string array to lines",str(len(values))+" line(s)")


def csv_trim_cells(p):
    import io
    raw=_read_text_source(p)
    try: rows=list(csv.reader(io.StringIO(raw,newline="")))
    except csv.Error as exc: raise RuntimeError("Invalid CSV: "+str(exc)) from exc
    stream=io.StringIO(newline="")
    csv.writer(stream,lineterminator="\n").writerows([[cell.strip() for cell in row] for row in rows])
    return _write_text_artifact_ext(p,"trimmed",".csv",stream.getvalue(),"CSV cell trimming")


def csv_remove_empty_columns(p):
    import io
    raw=_read_text_source(p)
    try: rows=list(csv.reader(io.StringIO(raw,newline="")))
    except csv.Error as exc: raise RuntimeError("Invalid CSV: "+str(exc)) from exc
    if not rows: raise RuntimeError("CSV is empty.")
    width=max((len(row) for row in rows),default=0)
    if width>200 or len(rows)>100_001: raise RuntimeError("CSV empty-column removal is limited to 100,000 rows and 200 columns.")
    padded=[row+[""]*(width-len(row)) for row in rows]
    if len(padded)==1:
        keep=list(range(width))
    else:
        keep=[index for index in range(width) if any(row[index].strip() for row in padded[1:])]
    stream=io.StringIO(newline="")
    csv.writer(stream,lineterminator="\n").writerows([[row[index] for index in keep] for row in padded])
    return _write_text_artifact_ext(p,"no-empty-columns",".csv",stream.getvalue(),"CSV empty-column removal",str(width-len(keep))+" column(s) removed")


def csv_empty_cell_report(p):
    import io
    raw=_read_text_source(p)
    try: rows=list(csv.reader(io.StringIO(raw,newline="")))
    except csv.Error as exc: raise RuntimeError("Invalid CSV: "+str(exc)) from exc
    if not rows: raise RuntimeError("CSV is empty.")
    headers=rows[0]
    if len(headers)>200 or len(rows)>100_001: raise RuntimeError("CSV empty-cell report is limited to 100,000 rows and 200 columns.")
    body=rows[1:]
    width=len(headers)
    total=len(body)*width
    empty_total=0
    lines=["CSV empty-cell report","Rows: "+str(len(body)),"Columns: "+str(width)]
    for index,header in enumerate(headers):
        missing=sum(1 for row in body if index>=len(row) or not row[index].strip())
        empty_total+=missing
        percent=(missing*100/len(body)) if body else 0
        lines.append(json.dumps({"column":header,"empty":missing,"non_empty":len(body)-missing,"empty_percent":round(percent,2)},ensure_ascii=False))
    lines.append("Total empty cells: "+str(empty_total))
    lines.append("Total data cells: "+str(total))
    return _write_text_artifact(p,"empty-cell-report","\n".join(lines)+"\n","CSV empty-cell report")


def subtitle_text(p):
    raw=p.read_text(encoding="utf-8-sig",errors="replace").replace("\r\n","\n").replace("\r","\n")
    lines=[]
    for line in raw.splitlines():
        value=line.strip()
        if not value or value.upper()=="WEBVTT" or value.startswith("NOTE "):
            continue
        if re.fullmatch(r"\d+",value):
            continue
        if "-->" in value and re.search(r"\d{2}:\d{2}",value):
            continue
        value=re.sub(r"<[^>]*>","",value)
        value=unescape(value).strip()
        if value and (not lines or lines[-1]!=value):
            lines.append(value)
    return tool_text("\n".join(lines),"Subtitle transcript")

class VisibleHtmlText(HTMLParser):
    BLOCK_TAGS={"address","article","aside","blockquote","br","dd","div","dl","dt","fieldset","figcaption","figure","footer","form","h1","h2","h3","h4","h5","h6","header","hr","li","main","nav","ol","p","pre","section","table","td","th","tr","ul"}
    SKIP_TAGS={"head","script","style","noscript","svg","canvas","iframe","template"}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip_depth=0
        self.parts=[]
    def handle_starttag(self,tag,attrs):
        if tag in self.SKIP_TAGS:
            self.skip_depth+=1
        elif not self.skip_depth and tag in self.BLOCK_TAGS:
            self.parts.append("\n")
    def handle_endtag(self,tag):
        if tag in self.SKIP_TAGS and self.skip_depth:
            self.skip_depth-=1
        elif not self.skip_depth and tag in self.BLOCK_TAGS:
            self.parts.append("\n")
    def handle_data(self,data):
        if not self.skip_depth:
            value=data.strip()
            if value:
                self.parts.append(value)

def html_text(p):
    parser=VisibleHtmlText()
    parser.feed(p.read_text(encoding="utf-8-sig",errors="replace"))
    parser.close()
    text=" ".join(parser.parts)
    text=re.sub(r"[ \t]+"," ",text)
    text=re.sub(r" *\n *","\n",text)
    text=re.sub(r"\n{3,}","\n\n",text).strip()
    return tool_text(text,"HTML text extraction")

def audio_normalize(p):
    out=p.with_name(p.stem+"-normalized.mp3")
    cmd("ffmpeg",["-y","-i",str(p),"-vn","-af","loudnorm=I=-16:TP=-1.5:LRA=11","-c:a","libmp3lame","-q:a","2",str(out)],600)
    return {"summary":"Đã chuẩn hóa loudness về mục tiêu -16 LUFS, true peak -1.5 dBTP và xuất MP3.","output_path":str(out)}

def video_audio(p):
    out=p.with_name(p.stem+"-audio.mp3")
    cmd("ffmpeg",["-y","-i",str(p),"-map","0:a:0","-vn","-c:a","libmp3lame","-q:a","2",str(out)],600)
    return {"summary":"Đã tách track âm thanh đầu tiên khỏi video và xuất MP3.","output_path":str(out)}

def video_gif(p):
    data=ffprobe(p)
    duration=float(data.get("format",{}).get("duration") or 0)
    if duration<=0:
        raise RuntimeError("Không đọc được thời lượng video.")
    clip=min(6.0,duration)
    start=max(0.0,(duration-clip)/2)
    out=p.with_name(p.stem+"-preview.gif")
    vf="fps=10,scale=640:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse"
    cmd("ffmpeg",["-y","-ss",str(start),"-t",str(clip),"-i",str(p),"-vf",vf,"-loop","0",str(out)],900)
    return {"summary":f"Đã tạo GIF xem trước dài {clip:.1f} giây, 10 FPS, rộng tối đa 640 px.","output_path":str(out)}


def _guard_image_dimensions(image):
    if image.width * image.height > 80_000_000:
        raise RuntimeError("Ảnh vượt giới hạn 80 megapixel để tránh dùng quá nhiều bộ nhớ.")


def image_resize(p):
    from PIL import Image, ImageOps
    out=p.with_name(p.stem+"-resized.jpg")
    with Image.open(p) as raw:
        _guard_image_dimensions(raw)
        im=ImageOps.exif_transpose(raw)
        im.thumbnail((1920,1920),Image.Resampling.LANCZOS)
        if "A" in im.getbands():
            rgba=im.convert("RGBA")
            background=Image.new("RGB",rgba.size,"white")
            background.paste(rgba,mask=rgba.getchannel("A"))
            im=background
        else:
            im=im.convert("RGB")
        im.save(out,"JPEG",quality=86,optimize=True,progressive=True)
    return {"summary":f"Đã resize ảnh về tối đa 1920 px, giữ tỷ lệ; {p.stat().st_size:,} → {out.stat().st_size:,} bytes.","output_path":str(out)}

def image_webp(p):
    from PIL import Image, ImageOps
    out=p.with_name(p.stem+"-converted.webp")
    with Image.open(p) as raw:
        _guard_image_dimensions(raw)
        im=ImageOps.exif_transpose(raw)
        has_alpha=("A" in im.getbands()) or ("transparency" in im.info)
        if im.mode not in ("RGB","RGBA"):
            im=im.convert("RGBA" if has_alpha else "RGB")
        im.save(out,"WEBP",quality=84,method=6)
    return {"summary":f"Đã chuyển ảnh sang WebP; {p.stat().st_size:,} → {out.stat().st_size:,} bytes.","output_path":str(out)}

def image_palette(p):
    from PIL import Image, ImageOps
    with Image.open(p) as raw:
        _guard_image_dimensions(raw)
        im=ImageOps.exif_transpose(raw).convert("RGB")
        im.thumbnail((512,512),Image.Resampling.LANCZOS)
        quantized=im.quantize(colors=8)
        counts=sorted(quantized.getcolors(512*512) or [],reverse=True)
        palette=quantized.getpalette() or []
    total=max(1,sum(count for count,_ in counts))
    rows=[]
    for count,index in counts[:8]:
        base=index*3
        if base+2>=len(palette): continue
        color="#"+"".join(f"{v:02X}" for v in palette[base:base+3])
        rows.append(f"{color} · {count/total*100:.1f}%")
    return tool_text("Bảng màu chủ đạo (tối đa 8 màu):\n"+"\n".join(rows),"Image color palette")

def pdf_compress(p):
    import fitz
    doc=fitz.open(p)
    if doc.is_encrypted and doc.needs_pass:
        raise RuntimeError("PDF được mã hóa bằng mật khẩu; không thể nén khi chưa mở khóa.")
    if doc.page_count>200:
        raise RuntimeError("PDF quá 200 trang. Hãy chia nhỏ tài liệu trước khi nén.")
    out=p.with_name(p.stem+"-compressed.pdf")
    doc.save(str(out),garbage=4,deflate=True,clean=True,deflate_images=True,deflate_fonts=True)
    doc.close()
    before=p.stat().st_size
    after=out.stat().st_size
    change=(1-after/max(1,before))*100
    return {"summary":f"Đã tối ưu PDF không thay đổi nội dung trang: {before:,} → {after:,} bytes ({change:.1f}% thay đổi).","output_path":str(out)}

def pdf_to_images(p):
    import fitz
    from PIL import Image
    import tempfile
    doc=fitz.open(p)
    if doc.is_encrypted and doc.needs_pass:
        raise RuntimeError("PDF được mã hóa bằng mật khẩu.")
    if doc.page_count>20:
        raise RuntimeError("Chuyển PDF sang ảnh hiện giới hạn 20 trang để giữ tệp đầu ra an toàn.")
    out=p.with_name(p.stem+"-pages.zip")
    root=Path(os.environ.get("RUNNER_TEMP","/tmp"))/"nolane-inputs"
    temp=Path(tempfile.mkdtemp(prefix="pdf-pages-",dir=root))
    try:
        with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
            for number,page in enumerate(doc,1):
                scale=min(1.3,1200/max(page.rect.width,page.rect.height))
                pix=page.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False)
                image=temp/f"page-{number:03d}.jpg"
                Image.frombytes("RGB",(pix.width,pix.height),pix.samples).save(image,"JPEG",quality=82,optimize=True)
                archive.write(image,image.name)
        pages=doc.page_count
    finally:
        doc.close()
        shutil.rmtree(temp,ignore_errors=True)
    return {"summary":f"Đã render {pages} trang PDF thành ảnh JPEG và đóng gói ZIP.","output_path":str(out)}

def epub_text(p):
    import xml.etree.ElementTree as ET
    from urllib.parse import unquote
    if not zipfile.is_zipfile(p):
        raise RuntimeError("Tệp EPUB không phải ZIP hợp lệ.")
    with zipfile.ZipFile(p) as archive:
        infos=archive.infolist()
        if len(infos)>2000 or sum(x.file_size for x in infos)>100*1024*1024:
            raise RuntimeError("EPUB vượt giới hạn 2.000 mục hoặc 100 MB giải nén.")
        names={x.filename for x in infos}
        if "META-INF/container.xml" not in names:
            raise RuntimeError("EPUB thiếu META-INF/container.xml.")
        container=ET.fromstring(archive.read("META-INF/container.xml"))
        rootfiles=container.findall(".//{*}rootfile")
        if not rootfiles:
            raise RuntimeError("Không tìm thấy package OPF trong EPUB.")
        opf_path=unquote(rootfiles[0].attrib.get("full-path",""))
        if not opf_path or opf_path.startswith("/") or ".." in Path(opf_path).parts or opf_path not in names:
            raise RuntimeError("Đường dẫn OPF trong EPUB không an toàn hoặc không tồn tại.")
        package=ET.fromstring(archive.read(opf_path))
        ns={"opf":"http://www.idpf.org/2007/opf","dc":"http://purl.org/dc/elements/1.1/"}
        title=package.findtext(".//dc:title",default=p.stem,namespaces=ns)
        author=package.findtext(".//dc:creator",default="",namespaces=ns)
        manifest={}
        base=Path(opf_path).parent
        for item in package.findall(".//opf:manifest/opf:item",ns):
            href=unquote(item.attrib.get("href","")).split("#",1)[0].split("?",1)[0]
            candidate=posixpath.normpath(posixpath.join(base.as_posix(),href))
            if candidate.startswith("../") or candidate.startswith("/") or candidate not in names:
                continue
            manifest[item.attrib.get("id","")]=candidate
        spine=package.findall(".//opf:spine/opf:itemref",ns)
        chapters=[]
        for ref in spine[:60]:
            name=manifest.get(ref.attrib.get("idref",""))
            if not name or not name.lower().endswith((".xhtml",".html",".htm")):
                continue
            data=archive.read(name)
            parser=VisibleHtmlText()
            parser.feed(data.decode("utf-8-sig","replace"))
            parser.close()
            text_value=re.sub(r"\s+"," "," ".join(parser.parts)).strip()
            if text_value:
                chapters.append(f"--- {Path(name).name} ---\n{text_value}")
    output=f"Title: {title}\nAuthor: {author or 'Unknown'}\nChapters: {len(chapters)}\n\n"+"\n\n".join(chapters)
    return tool_text(output,"EPUB reader · spine order")

def sqlite_inspect(p):
    import sqlite3
    from urllib.parse import quote
    uri="file:"+quote(str(p.resolve()),safe="/:")+"?mode=ro&immutable=1"
    connection=sqlite3.connect(uri,uri=True,timeout=5)
    try:
        connection.execute("PRAGMA query_only=ON")
        connection.set_progress_handler(lambda: 1,2_000_000)
        tables=connection.execute(
            "SELECT name,sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name LIMIT 30"
        ).fetchall()
        lines=[f"Database: {p.name}",f"Tables inspected: {len(tables)} (max 30)","Mode: read-only; no SQL from the uploaded file is executed."]
        for name,create_sql in tables:
            if create_sql and "CREATE VIRTUAL TABLE" in create_sql.upper():
                lines.append(f"\n[{name}] Virtual table skipped for safety.")
                continue
            quoted='"'+name.replace('"','""')+'"'
            try:
                count=connection.execute("SELECT COUNT(*) FROM "+quoted).fetchone()[0]
                columns=connection.execute("PRAGMA table_info("+quoted+")").fetchall()
                rows=connection.execute("SELECT * FROM "+quoted+" LIMIT 5").fetchall()
            except sqlite3.Error as exc:
                lines.append(f"\n[{name}] Inspection skipped: {str(exc)[:160]}")
                continue
            lines.append(f"\n[{name}] rows={count:,}")
            lines.append("Columns: "+", ".join(f"{c[1]} ({c[2] or 'unknown'})" for c in columns[:40]))
            lines.append("Sample: "+json.dumps(rows,ensure_ascii=False,default=str)[:1000])
        return tool_text("\n".join(lines),"SQLite database inspector")
    finally:
        connection.close()

def yaml_format(p):
    import yaml
    raw=p.read_text(encoding="utf-8-sig")
    documents=list(yaml.safe_load_all(raw))
    formatted=yaml.safe_dump_all(documents,allow_unicode=True,sort_keys=False,indent=2)
    out=p.with_name(p.stem+"-formatted.yaml")
    out.write_text(formatted,encoding="utf-8")
    return {"summary":f"YAML hợp lệ: {len(documents)} document(s), đã parse bằng SafeLoader và định dạng lại bằng SafeDumper.","output_path":str(out)}

def xml_format(p):
    import xml.etree.ElementTree as ET
    raw=p.read_text(encoding="utf-8-sig")
    if re.search(r"<!\s*(DOCTYPE|ENTITY)\b",raw,re.I):
        raise RuntimeError("XML có DTD/ENTITY bị chặn để tránh external entity và entity expansion.")
    root=ET.fromstring(raw)
    ET.indent(root,space="  ")
    out=p.with_name(p.stem+"-formatted.xml")
    ET.ElementTree(root).write(out,encoding="utf-8",xml_declaration=True)
    return {"summary":f"XML hợp lệ; root element: {root.tag}. Đã định dạng lại.","output_path":str(out)}

def code_check(p):
    ext=p.suffix.lower()
    report=[f"File: {p.name}","Uploaded code is parsed/checked only; it is never executed."]
    if ext in (".py",".pyw"):
        import ast
        ast.parse(p.read_text(encoding="utf-8-sig"),filename=p.name)
        report.append("Python: syntax OK (AST parse)")
    elif ext in (".js",".mjs",".cjs"):
        result=subprocess.run([shutil.which("node") or "node","--check",str(p)],capture_output=True,text=True,timeout=30)
        if result.returncode:
            raise RuntimeError((result.stderr or result.stdout or "JavaScript syntax error.")[-1200:])
        report.append("JavaScript: syntax OK (Node --check)")
    elif ext in (".sh",".bash"):
        result=subprocess.run([shutil.which("bash") or "bash","-n",str(p)],capture_output=True,text=True,timeout=30)
        if result.returncode:
            raise RuntimeError((result.stderr or result.stdout or "Shell syntax error.")[-1200:])
        report.append("Shell: syntax OK (bash -n)")
    elif ext in (".json",):
        value=json.loads(p.read_text(encoding="utf-8-sig"))
        report.append(f"JSON: syntax OK; root type={type(value).__name__}")
    elif ext in (".yaml",".yml"):
        import yaml
        count=sum(1 for _ in yaml.safe_load_all(p.read_text(encoding="utf-8-sig")))
        report.append(f"YAML: syntax OK; {count} document(s), SafeLoader")
    elif ext==".xml":
        import xml.etree.ElementTree as ET
        raw=p.read_text(encoding="utf-8-sig")
        if re.search(r"<!\s*(DOCTYPE|ENTITY)\b",raw,re.I):
            raise RuntimeError("XML DTD/ENTITY is disabled.")
        root=ET.fromstring(raw)
        report.append(f"XML: syntax OK; root={root.tag}")
    else:
        raise RuntimeError("code-check hỗ trợ .py, .js, .mjs, .cjs, .sh, .bash, .json, .yaml, .yml và .xml.")
    return tool_text("\n".join(report),"Code validation")

def video_contact_sheet(p):
    data=ffprobe(p)
    duration=float(data.get("format",{}).get("duration") or 0)
    if duration<=0 or duration>1800:
        raise RuntimeError("Video phải có thời lượng từ 0 đến 30 phút để tạo contact sheet.")
    out=p.with_name(p.stem+"-contact-sheet.jpg")
    rate=12/max(duration,1)
    vf=f"fps={rate:.8f},scale=320:-2,tile=4x3:padding=12:margin=8"
    cmd("ffmpeg",["-y","-i",str(p),"-vf",vf,"-frames:v","1","-q:v","3",str(out)],300)
    return {"summary":f"Đã tạo contact sheet tối đa 12 khung hình đại diện cho video dài {duration:.1f} giây.","output_path":str(out)}

def video_compress(p):
    data=ffprobe(p)
    duration=float(data.get("format",{}).get("duration") or 0)
    if duration<=0 or duration>360:
        raise RuntimeError("Nén video hiện giới hạn 6 phút để bảo đảm thời gian xử lý và dung lượng gửi.")
    out=p.with_name(p.stem+"-compressed.mp4")
    vf="scale='min(1280,iw)':'min(1280,ih)':force_original_aspect_ratio=decrease:force_divisible_by=2"
    cmd("ffmpeg",["-y","-i",str(p),"-map","0:v:0","-map","0:a?","-vf",vf,"-c:v","libx264","-preset","veryfast","-crf","30","-maxrate","850k","-bufsize","1700k","-c:a","aac","-b:a","80k","-movflags","+faststart","-sn","-dn","-threads","2",str(out)],900)
    if out.stat().st_size>44*1024*1024:
        out.unlink(missing_ok=True)
        raise RuntimeError("Video sau nén vẫn vượt giới hạn gửi 44 MB; hãy chọn clip ngắn hơn.")
    change=(1-out.stat().st_size/max(1,p.stat().st_size))*100
    return {"summary":f"Đã nén H.264/AAC ở tối đa 1280 px, CRF 30: {p.stat().st_size:,} → {out.stat().st_size:,} bytes ({change:.1f}% thay đổi).","output_path":str(out)}

def _subtitle_timestamp(seconds,separator):
    millis=max(0,round(float(seconds)*1000))
    hours,remain=divmod(millis,3_600_000)
    minutes,remain=divmod(remain,60_000)
    secs,millis=divmod(remain,1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}{separator}{millis:03d}"

def audio_subtitles(p):
    from faster_whisper import WhisperModel
    model=WhisperModel("small",device="cpu",compute_type="int8",cpu_threads=4)
    segments,info=model.transcribe(str(p),beam_size=5,vad_filter=True)
    srt=[]; vtt=["WEBVTT",""]
    count=0
    for segment in segments:
        text_value=segment.text.strip()
        if not text_value: continue
        count+=1
        start=_subtitle_timestamp(segment.start,",")
        end=_subtitle_timestamp(segment.end,",")
        srt.extend([str(count),f"{start} --> {end}",text_value,""])
        vtt.extend([f"{_subtitle_timestamp(segment.start,'.')} --> {_subtitle_timestamp(segment.end,'.')}",text_value,""])
        if count>=5000: break
    if not count:
        raise RuntimeError("Whisper không nhận diện được lời thoại để tạo phụ đề.")
    root=Path(os.environ.get("RUNNER_TEMP","/tmp"))/"nolane-inputs"
    out=p.with_name(p.stem+"-subtitles.zip")
    srt_path=root/(p.stem+"-transcript.srt")
    vtt_path=root/(p.stem+"-transcript.vtt")
    srt_path.write_text("\n".join(srt),encoding="utf-8")
    vtt_path.write_text("\n".join(vtt),encoding="utf-8")
    with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(srt_path,srt_path.name)
        archive.write(vtt_path,vtt_path.name)
    srt_path.unlink(missing_ok=True); vtt_path.unlink(missing_ok=True)
    return {"summary":f"Đã tạo phụ đề SRT và VTT bằng Whisper small · ngôn ngữ: {info.language} · {count} cue(s).","output_path":str(out)}

def _safe_archive_parts(name):
    normalized=name.replace("\\","/")
    if "\x00" in normalized or normalized.startswith("/") or re.match(r"^[A-Za-z]:",normalized):
        raise RuntimeError("Archive chứa đường dẫn tuyệt đối hoặc ký tự không an toàn.")
    parts=[part for part in normalized.split("/") if part not in ("",".")]
    if not parts or any(part==".." for part in parts):
        raise RuntimeError("Archive chứa đường dẫn traversal (..).")
    return parts


def _copy_archive_stream(source,destination,current_total,max_bytes,expected_size=None):
    written=0
    with destination.open("wb") as output:
        while True:
            chunk=source.read(1024*1024)
            if not chunk: break
            written+=len(chunk)
            if current_total+written>max_bytes:
                raise RuntimeError("Archive vượt giới hạn 150 MB dữ liệu giải nén thực tế.")
            output.write(chunk)
    if expected_size is not None and written!=expected_size:
        raise RuntimeError("Kích thước giải nén không khớp metadata của archive.")
    return written

def archive_safe_extract(p):
    root=Path(os.environ.get("RUNNER_TEMP","/tmp"))/"nolane-inputs"
    temp=Path(tempfile.mkdtemp(prefix="archive-safe-",dir=root))
    out=p.with_name(p.stem+"-safe-extracted.zip")
    total=0; count=0
    max_files=200; max_bytes=150*1024*1024
    try:
        if zipfile.is_zipfile(p):
            with zipfile.ZipFile(p) as archive:
                for item in archive.infolist():
                    if item.is_dir(): continue
                    count+=1
                    if count>max_files or total+item.file_size>max_bytes:
                        raise RuntimeError("Archive vượt giới hạn 200 tệp hoặc 150 MB sau giải nén.")
                    if item.flag_bits & 0x1:
                        raise RuntimeError("Archive có tệp mã hóa; không thể giải nén an toàn.")
                    mode=(item.external_attr>>16)&0xFFFF
                    if stat.S_ISLNK(mode):
                        raise RuntimeError("Archive chứa symbolic link; đã từ chối giải nén.")
                    if item.file_size>2*1024*1024 and item.compress_size and item.file_size/max(1,item.compress_size)>250:
                        raise RuntimeError("Archive có tỷ lệ nén bất thường (zip bomb protection).")
                    parts=_safe_archive_parts(item.filename)
                    target=temp.joinpath(*parts)
                    target.parent.mkdir(parents=True,exist_ok=True)
                    with archive.open(item) as source:
                        total+=_copy_archive_stream(source,target,total,max_bytes,item.file_size)
        else:
            with tarfile.open(p,"r:*") as archive:
                for item in archive.getmembers():
                    if item.isdir(): continue
                    if not item.isfile():
                        raise RuntimeError("Archive TAR chứa link hoặc special file; đã từ chối giải nén.")
                    count+=1
                    if count>max_files or total+item.size>max_bytes:
                        raise RuntimeError("Archive vượt giới hạn 200 tệp hoặc 150 MB sau giải nén.")
                    parts=_safe_archive_parts(item.name)
                    source=archive.extractfile(item)
                    if source is None: continue
                    target=temp.joinpath(*parts)
                    target.parent.mkdir(parents=True,exist_ok=True)
                    with source:
                        total+=_copy_archive_stream(source,target,total,max_bytes,item.size)
        with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as packaged:
            for item in sorted(temp.rglob("*")):
                if item.is_file():
                    packaged.write(item,item.relative_to(temp).as_posix())
    except (zipfile.BadZipFile,tarfile.TarError) as exc:
        raise RuntimeError("Archive không hợp lệ hoặc không được hỗ trợ.") from exc
    finally:
        shutil.rmtree(temp,ignore_errors=True)
    return {"summary":f"Đã giải nén an toàn {count} tệp ({total:,} bytes), loại bỏ metadata/link nguy hiểm và đóng gói ZIP sạch.","output_path":str(out)}



def xlsx_formula_report(p):
    from openpyxl import load_workbook
    formulas=load_workbook(p,read_only=True,data_only=False)
    cached=load_workbook(p,read_only=True,data_only=True)
    reports=[]
    total=external=volatile=errors=missing=0
    try:
        if len(formulas.worksheets)>20:
            raise RuntimeError("Workbook vượt quá 20 sheets.")
        for index,ws in enumerate(formulas.worksheets):
            cache_ws=cached.worksheets[index]
            samples=[]; sheet_total=0; cache_rows=cache_ws.iter_rows(values_only=True)
            scanned=0
            for row in ws.iter_rows():
                cache_row=next(cache_rows,())
                scanned+=1
                if scanned>50000: raise RuntimeError("Formula report vượt quá 50.000 dòng mỗi sheet.")
                for cell in row[:200]:
                    value=cell.value
                    if not isinstance(value,str) or not value.startswith("="): continue
                    total+=1; sheet_total+=1
                    if re.search(r"\[[^\]]+\]",value): external+=1
                    if re.search(r"\b(NOW|TODAY|RAND|RANDBETWEEN|INDIRECT|OFFSET)\s*\(",value.upper()): volatile+=1
                    if len(samples)<80: samples.append(f"{cell.coordinate}: "+re.sub(r"\s+"," ",value)[:180])
                    cached_value=cache_row[cell.column-1] if len(cache_row)>=cell.column else None
                    if isinstance(cached_value,str) and re.match(r"^#(REF!|DIV/0!|VALUE!|NAME\?|N/A|NUM!|NULL!)$",cached_value.strip(),re.I): errors+=1
                    elif cached_value is None: missing+=1
            reports.append(f"[{ws.title}] formulas={sheet_total:,}; scanned rows={min(scanned,50000):,}")
            reports.extend("  "+sample for sample in samples)
        lines=["XLSX formula report",f"Sheets inspected: {len(formulas.worksheets)}",f"Formula cells: {total:,}",
               f"External-workbook reference formulas: {external:,}",f"Volatile-function formulas: {volatile:,}",
               f"Cached formula errors: {errors:,}",f"Formula cells without cached result: {missing:,}","",
               "Per-sheet details:",*reports,"",
               "Formula calculation is not performed. Cached results may be stale or absent; formula cells and values are not modified."]
    finally:
        formulas.close(); cached.close()
    return _write_text_artifact_ext(p,"formula-report",".txt","\n".join(lines)+"\n","Excel formula report",f"{total:,} formula cell(s)")


def xlsx_to_markdown(p):
    from openpyxl import load_workbook
    workbook=load_workbook(p,read_only=True,data_only=True)
    sections=[]; total_rows=0; sheet_count=len(workbook.worksheets)
    try:
        if sheet_count>20: raise RuntimeError("Workbook vượt quá 20 sheets.")
        for ws in workbook.worksheets:
            rows=[]
            for row in ws.iter_rows(values_only=True):
                total_rows+=1
                if total_rows>5000: raise RuntimeError("XLSX-to-Markdown vượt quá 5.000 dòng tổng cộng.")
                if len(row)>20: raise RuntimeError(f"Sheet {ws.title} vượt quá 20 cột.")
                rows.append(list(row))
            if not rows or not any(value is not None for value in rows[0]):
                sections.extend([f"## {ws.title}","","(Sheet rỗng)",""]); continue
            width=max(1,max(len(row) for row in rows))
            headers=[str(rows[0][i]).strip() if i<len(rows[0]) and rows[0][i] is not None else f"Column {i+1}" for i in range(width)]
            def cell(value):
                if value is None: return ""
                return str(value).replace("\r"," ").replace("\n"," ").replace("|","\\|")[:300]
            sections.extend([f"## {ws.title}","","| "+" | ".join(cell(x) for x in headers)+" |","| "+" | ".join("---" for _ in headers)+" |"])
            for row in rows[1:201]:
                padded=list(row)+[None]*(width-len(row))
                sections.append("| "+" | ".join(cell(x) for x in padded[:width])+" |")
            if len(rows)>201: sections.append(f"> Display truncated: {len(rows)-1} data rows available; first 200 shown.")
            sections.append("")
    finally:
        workbook.close()
    content="# Workbook tables\n\n"+"\n".join(sections)
    if len(content.encode("utf-8"))>10*1024*1024: raise RuntimeError("Markdown workbook output exceeds 10 MB.")
    return _write_text_artifact_ext(p,"tables",".md",content,"Excel to Markdown",f"{sheet_count} sheet(s)")


def pdf_page_audit(p):
    import fitz
    doc=fitz.open(p)
    if doc.is_encrypted and doc.needs_pass:
        doc.close(); raise RuntimeError("PDF được mã hóa bằng mật khẩu.")
    count=doc.page_count
    if count<1 or count>200:
        doc.close(); raise RuntimeError(f"PDF page audit hỗ trợ từ 1 đến 200 trang; nhận {count}.")
    lines=["PDF page audit",f"Total pages: {count}",""]; blank=scan=rotated=0; dimensions=set()
    try:
        for index,page in enumerate(doc,1):
            text=page.get_text("text") or ""; words=len(re.findall(r"\S+",text)); chars=len(text.strip())
            images=len(page.get_images(full=True)); drawings=len(page.get_drawings()); rect=page.rect; rotation=int(page.rotation or 0)
            dimensions.add((round(rect.width,1),round(rect.height,1)))
            if rotation: rotated+=1
            is_blank=chars==0 and images==0 and drawings==0; is_scan=chars==0 and images>0
            if is_blank: blank+=1
            if is_scan: scan+=1
            flags=[]
            if is_blank: flags.append("possibly blank")
            if is_scan: flags.append("image-only / OCR may be needed")
            if words<5 and not is_blank: flags.append("very little text")
            if rotation: flags.append(f"rotated {rotation}°")
            lines.append(f"Page {index}: {words} words; {chars} text chars; {images} image XObject(s); {drawings} vector drawing(s); {rect.width:.1f} × {rect.height:.1f} pt; rotation {rotation}°"+("; flags: "+", ".join(flags) if flags else ""))
    finally: doc.close()
    lines.extend(["",f"Possibly blank pages: {blank}",f"Image-only / OCR candidates: {scan}",f"Rotated pages: {rotated}",f"Distinct page dimensions: {len(dimensions)}","Blank/scan labels are heuristics; vector artwork or unusual PDF structures may need visual review."])
    return _write_text_artifact_ext(p,"page-audit",".txt","\n".join(lines)+"\n","PDF page audit",f"{count} page(s)")


def image_favicon(p):
    from PIL import Image,ImageOps
    out=p.with_name(p.stem+"-favicon.ico"); sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)]
    with Image.open(p) as raw:
        _guard_image_dimensions(raw)
        im=ImageOps.exif_transpose(raw).convert("RGBA")
        if max(im.size)<16: raise RuntimeError("Ảnh nguồn quá nhỏ để tạo favicon rõ nét (cần ít nhất 16 px).")
        im.thumbnail((1024,1024),Image.Resampling.LANCZOS)
        im.save(out,format="ICO",sizes=sizes)
    if out.stat().st_size>5*1024*1024:
        out.unlink(missing_ok=True); raise RuntimeError("Favicon ICO vượt quá giới hạn 5 MB.")
    return {"summary":f"Đã tạo favicon ICO đa kích thước 16, 32, 48, 64, 128 và 256 px từ ảnh nguồn {p.name}; alpha được giữ nếu có.","output_path":str(out)}


def subtitle_audit(p):
    raw=_read_small_text(p,limit=5*1024*1024).replace("\r\n","\n").replace("\r","\n")
    blocks=re.split(r"\n[ \t]*\n",raw.strip())
    stamp=re.compile(r"^\s*((?:(\d{1,2}):)?(\d{2}):(\d{2})[,.](\d{3}))\s*-->\s*((?:(\d{1,2}):)?(\d{2}):(\d{2})[,.](\d{3}))(?:\s+.*)?$")
    cues=[]; malformed=0
    for block in blocks:
        block=block.strip()
        if not block or block.startswith(("WEBVTT","NOTE","STYLE","REGION")): continue
        lines=block.splitlines(); ti=next((i for i,line in enumerate(lines) if "-->" in line),None)
        if ti is None: continue
        match=stamp.match(lines[ti])
        if not match: malformed+=1; continue
        g=match.groups()
        def millis(offset):
            return ((int(g[offset] or 0)*60+int(g[offset+1]))*60+int(g[offset+2]))*1000+int(g[offset+3])
        start=millis(1); end=millis(6)
        caption=unescape(re.sub(r"<[^>]*>","", " ".join(lines[ti+1:])))
        caption=re.sub(r"\s+"," ",caption).strip()
        cues.append({"start":start,"end":end,"caption":caption})
    invalid=sum(c["end"]<=c["start"] for c in cues)
    ordered=overlap=duplicates=long_lines=long_cues=0; seen=set(); prev_start=None; prev_end=None
    prior_intervals=[]
    for cue in cues:
        if prev_start is not None and cue["start"]<prev_start: ordered+=1
        if cue["end"]>cue["start"] and any(cue["start"]<end and cue["end"]>start for start,end in prior_intervals): overlap+=1
        if cue["end"]>cue["start"]: prior_intervals.append((cue["start"],cue["end"]))
        if cue["caption"]:
            key=unicodedata.normalize("NFKC",cue["caption"]).casefold()
            if key in seen: duplicates+=1
            else: seen.add(key)
            if len(cue["caption"])>42: long_lines+=1
            if cue["end"]>cue["start"] and cue["end"]-cue["start"]>7000: long_cues+=1
        prev_start=cue["start"]; prev_end=cue["end"] if prev_end is None else max(prev_end,cue["end"])
    findings=[("Malformed timestamp cues",malformed),("Non-positive cue durations",invalid),("Out-of-order cues",ordered),("Overlapping cues",overlap),("Repeated captions",duplicates),("Long caption lines (>42 characters)",long_lines),("Long cue durations (>7 seconds)",long_cues)]
    total=sum(value for _,value in findings)
    lines=["Subtitle quality audit",f"Format: {'WebVTT' if p.suffix.lower()=='.vtt' or raw.lstrip().startswith('WEBVTT') else 'SRT'}",f"Valid timestamp cues: {len(cues)}",*[f"{label}: {value}" for label,value in findings],"","Findings are heuristic. Long lines/durations may be intentional for some languages or accessibility workflows."]
    if not cues: lines.append("No valid timestamp cues were found.")
    return _write_text_artifact_ext(p,"subtitle-audit",".txt","\n".join(lines)+"\n","Subtitle audit",f"{len(cues)} cue(s); {total} finding(s)")


def markdown_toc(p):
    raw=_read_small_text(p); lines=raw.splitlines(); headings=[]; in_fence=False; fence_char=None; index=0
    fence_start=re.escape(chr(96))
    while index<len(lines):
        line=lines[index]
        fence=re.match(r"^\s{0,3}("+fence_start+r"{3,}|~{3,})",line)
        if fence:
            marker=fence.group(1)[0]
            if not in_fence: in_fence=True; fence_char=marker
            elif marker==fence_char: in_fence=False; fence_char=None
            index+=1; continue
        if in_fence: index+=1; continue
        match=re.match(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$",line); level=0; title=""
        if match: level=len(match.group(1)); title=match.group(2).strip()
        elif index+1<len(lines) and line.strip() and re.match(r"^\s{0,3}(=+|-+)\s*$",lines[index+1]):
            level=1 if lines[index+1].strip().startswith("=") else 2; title=line.strip(); index+=1
        if level and title.casefold()!="table of contents":
            plain=re.sub(r"\x60([^\x60]*)\x60",r"\1",title)
            plain=re.sub(r"\[([^\]]+)\]\([^)]+\)",r"\1",plain)
            plain=re.sub(r"<[^>]+>","",plain)
            slug=unicodedata.normalize("NFKD",plain).encode("ascii","ignore").decode().lower()
            slug=re.sub(r"[^a-z0-9\s-]","",slug); slug=re.sub(r"[\s-]+","-",slug).strip("-") or "section"
            headings.append((level,title,slug))
        index+=1
    if not headings: raise RuntimeError("Không tìm thấy heading Markdown ngoài code fence.")
    seen={}; entries=[]
    for level,title,slug in headings:
        count=seen.get(slug,0); seen[slug]=count+1
        entries.append((level,title,slug if count==0 else f"{slug}-{count}"))
    min_level=min(level for level,_,_ in entries); toc=["## Table of Contents",""]
    for level,title,anchor in entries:
        clean_title=re.sub(r"[\[\]]","",title)
        toc.append("  "*max(0,level-min_level)+f"- [{clean_title}](#{anchor})")
    output="\n".join(toc)+"\n\n---\n\n"+raw.lstrip("\ufeff")
    if len(output.encode("utf-8"))>10*1024*1024: raise RuntimeError("Markdown TOC output exceeds 10 MB.")
    return _write_text_artifact_ext(p,"with-toc",".md",output,"Markdown table of contents",f"{len(entries)} heading(s)")


def xlsx_profile(p):
    from openpyxl import load_workbook
    workbook=load_workbook(p,read_only=True,data_only=True)
    reports=[]
    try:
        for sheet in workbook.worksheets[:20]:
            iterator=sheet.iter_rows(values_only=True)
            header=next(iterator,None)
            if header is None:
                reports.append(f"\n[{sheet.title}] Empty sheet")
                continue
            names=[str(value).strip() if value is not None else f"Column {i+1}" for i,value in enumerate(header[:60])]
            missing=[0]*len(names); numeric=[[] for _ in names]; samples=[]; duplicates=set(); duplicate_count=0; rows=0
            for row in iterator:
                rows+=1
                values=list(row[:len(names)])
                if len(samples)<5: samples.append(values)
                key=hashlib.sha256(json.dumps(values,ensure_ascii=False,default=str).encode()).hexdigest()
                if key in duplicates: duplicate_count+=1
                else: duplicates.add(key)
                for i in range(len(names)):
                    value=values[i] if i<len(values) else None
                    if value is None or str(value).strip()=="": missing[i]+=1
                    elif isinstance(value,(int,float)) and not isinstance(value,bool): numeric[i].append(float(value))
                if rows>=10000: break
            lines=[f"\n[{sheet.title}] data rows={rows:,} · duplicate rows={duplicate_count:,}"+(" · scan capped at 10,000" if rows>=10000 else "")]
            for i,name in enumerate(names):
                line=f"- {name}: missing {missing[i]}/{rows}"
                if numeric[i]: line+=f" · numeric min={min(numeric[i]):g}, max={max(numeric[i]):g}, avg={sum(numeric[i])/len(numeric[i]):g}"
                lines.append(line)
            lines.append("Sample: "+json.dumps(samples,ensure_ascii=False,default=str)[:1200])
            reports.extend(lines)
    finally:
        workbook.close()
    return tool_text("\n".join(reports),"Excel workbook profiler")

def _spreadsheet_safe(value):
    text = "" if value is None else str(value)
    # Preserve ordinary negative numeric values while neutralizing spreadsheet formulas.
    if re.fullmatch(r"-\d+(?:\.\d+)?", text.strip()):
        return text
    if text.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + text
    return text

def image_png(p):
    from PIL import Image, ImageOps
    out=p.with_name(p.stem+"-lossless.png")
    with Image.open(p) as raw:
        _guard_image_dimensions(raw)
        im=ImageOps.exif_transpose(raw)
        if "A" in im.getbands() or "transparency" in im.info:
            im=im.convert("RGBA")
        else:
            im=im.convert("RGB")
        im.save(out,"PNG",optimize=True)
    if out.stat().st_size > 45*1024*1024:
        out.unlink(missing_ok=True)
        raise RuntimeError("PNG output exceeds the 45 MB Telegram delivery limit.")
    return {"summary":f"Đã chuyển sang PNG lossless, giữ transparency khi có thể; {p.stat().st_size:,} → {out.stat().st_size:,} bytes.","output_path":str(out)}

def csv_clean(p):
    out=p.with_name(p.stem+"-clean.csv")
    seen=set(); kept=0; removed_blank=0; removed_duplicate=0
    with p.open("r",encoding="utf-8-sig",newline="") as source:
        reader=csv.reader(source)
        headers=next(reader,None)
        if not headers: raise RuntimeError("CSV không có header.")
        if len(headers)>200: raise RuntimeError("CSV vượt quá 200 cột.")
        headers=[_spreadsheet_safe(unicodedata.normalize("NFC",str(value)).strip() or f"column_{i+1}") for i,value in enumerate(headers)]
        with out.open("w",encoding="utf-8",newline="") as target:
            writer=csv.writer(target,lineterminator="\n")
            writer.writerow(headers)
            for row in reader:
                if len(row)>200: raise RuntimeError("CSV vượt quá 200 cột.")
                values=[unicodedata.normalize("NFC",str(value)).strip() for value in row[:len(headers)]]
                values += [""] * (len(headers)-len(values))
                if not any(values): removed_blank+=1; continue
                key=tuple(values)
                if key in seen: removed_duplicate+=1; continue
                seen.add(key)
                writer.writerow([_spreadsheet_safe(value) for value in values])
                kept+=1
                if kept>100000: raise RuntimeError("CSV vượt quá 100.000 dòng dữ liệu.")
    return {"summary":f"CSV đã làm sạch: giữ {kept:,} dòng; bỏ {removed_blank:,} dòng trống và {removed_duplicate:,} dòng trùng. Spreadsheet formula prefix được escape.","output_path":str(out)}

def json_to_csv(p):
    value=json.loads(p.read_text(encoding="utf-8-sig"))
    if isinstance(value,dict) and isinstance(value.get("data"),list):
        value=value["data"]
    if not isinstance(value,list) or not value or any(not isinstance(item,dict) for item in value):
        raise RuntimeError("JSON-to-CSV yêu cầu một mảng không rỗng gồm các object; hoặc object có trường data là mảng object.")
    if len(value)>100000: raise RuntimeError("JSON array vượt quá 100.000 object.")
    headers=list(dict.fromkeys(key for item in value for key in item.keys()))[:200]
    if not headers: raise RuntimeError("Không tìm thấy trường dữ liệu trong JSON.")
    out=p.with_name(p.stem+"-converted.csv")
    with out.open("w",encoding="utf-8-sig",newline="") as target:
        writer=csv.writer(target,lineterminator="\n")
        writer.writerow([_spreadsheet_safe(header) for header in headers])
        for item in value:
            row=[]
            for key in headers:
                cell=item.get(key)
                if isinstance(cell,(dict,list)): cell=json.dumps(cell,ensure_ascii=False,separators=(",",":"))
                row.append(_spreadsheet_safe(cell))
            writer.writerow(row)
    return {"summary":f"Đã chuyển {len(value):,} object và {len(headers)} trường JSON sang CSV UTF-8.","output_path":str(out)}

def csv_to_xlsx(p):
    from openpyxl import Workbook
    out=p.with_name(p.stem+"-converted.xlsx")
    wb=Workbook(write_only=True)
    ws=wb.create_sheet("Data")
    rows=0
    with p.open("r",encoding="utf-8-sig",newline="") as source:
        reader=csv.reader(source)
        for row in reader:
            if len(row)>200: raise RuntimeError("CSV vượt quá 200 cột.")
            ws.append([_spreadsheet_safe(cell) for cell in row])
            rows+=1
            if rows>100001: raise RuntimeError("CSV vượt quá 100.000 dòng dữ liệu.")
    if rows<1: raise RuntimeError("CSV không có dữ liệu.")
    wb.save(out)
    if out.stat().st_size>45*1024*1024:
        out.unlink(missing_ok=True)
        raise RuntimeError("XLSX output exceeds the 45 MB Telegram delivery limit.")
    return {"summary":f"Đã chuyển {rows-1:,} dòng CSV thành workbook XLSX (tối đa 200 cột). Ô dữ liệu được ghi an toàn dưới dạng text.","output_path":str(out)}

def xlsx_to_csv(p):
    from openpyxl import load_workbook
    root=Path(os.environ.get("RUNNER_TEMP","/tmp"))/"nolane-inputs"
    temp=Path(tempfile.mkdtemp(prefix="xlsx-csv-",dir=root))
    out=p.with_name(p.stem+"-sheets-csv.zip")
    workbook=load_workbook(p,read_only=True,data_only=True)
    entries=[]
    try:
        if len(workbook.worksheets)>20: raise RuntimeError("Workbook vượt quá 20 sheets.")
        for index,ws in enumerate(workbook.worksheets,1):
            target=temp/(f"sheet-{index:02d}.csv")
            rows=0
            with target.open("w",encoding="utf-8-sig",newline="") as handle:
                writer=csv.writer(handle,lineterminator="\n")
                for values in ws.iter_rows(values_only=True):
                    if len(values)>200: raise RuntimeError("Sheet vượt quá 200 cột.")
                    writer.writerow([_spreadsheet_safe(value) for value in values])
                    rows+=1
                    if rows>20001: raise RuntimeError("Sheet vượt quá 20.000 dòng.")
            safe_name=re.sub(r"[^A-Za-z0-9._-]+","_",ws.title).strip("._-")[:50] or f"sheet-{index}"
            entries.append((target,f"{index:02d}-{safe_name}.csv",rows))
    finally:
        workbook.close()
    with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for source,name,_rows in entries: archive.write(source,arcname=name)
    if out.stat().st_size>45*1024*1024:
        out.unlink(missing_ok=True)
        raise RuntimeError("CSV archive exceeds the 45 MB Telegram delivery limit.")
    return {"summary":f"Đã xuất {len(entries)} sheet thành CSV riêng trong ZIP: "+", ".join(f"{name} ({rows} rows)" for _,name,rows in entries[:10]),"output_path":str(out)}

def pdf_split(p):
    import fitz
    source=fitz.open(p)
    if source.is_encrypted and source.needs_pass:
        source.close()
        raise RuntimeError("PDF được mã hóa bằng mật khẩu.")
    if source.page_count<1 or source.page_count>30:
        source.close()
        raise RuntimeError("PDF split hỗ trợ từ 1 đến 30 trang.")
    root=Path(os.environ.get("RUNNER_TEMP","/tmp"))/"nolane-inputs"
    temp=Path(tempfile.mkdtemp(prefix="pdf-split-",dir=root))
    out=p.with_name(p.stem+"-pages.zip")
    count=source.page_count
    try:
        names=[]
        for index in range(count):
            page_doc=fitz.open()
            page_doc.insert_pdf(source,from_page=index,to_page=index)
            page_path=temp/f"page-{index+1:03d}.pdf"
            page_doc.save(page_path,garbage=4,deflate=True)
            page_doc.close()
            names.append(page_path)
    finally:
        source.close()
    with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for name in names: archive.write(name,arcname=name.name)
    if out.stat().st_size>45*1024*1024:
        out.unlink(missing_ok=True)
        raise RuntimeError("PDF split archive exceeds the 45 MB Telegram delivery limit.")
    return {"summary":f"Đã tách PDF {count} trang thành {count} tệp PDF một trang và đóng gói ZIP.","output_path":str(out)}

def audio_convert(p):
    data=ffprobe(p)
    duration=float(data.get("format",{}).get("duration") or 0)
    if duration<=0 or duration>600:
        raise RuntimeError("Audio conversion giới hạn tối đa 10 phút.")
    out=p.with_name(p.stem+"-speech-16khz-mono.wav")
    cmd("ffmpeg",["-y","-i",str(p),"-vn","-ac","1","-ar","16000","-c:a","pcm_s16le",str(out)],900)
    if out.stat().st_size>40*1024*1024:
        out.unlink(missing_ok=True)
        raise RuntimeError("WAV output exceeds the 40 MB safety budget.")
    return {"summary":f"Đã chuyển audio {duration:.1f}s sang WAV PCM 16 kHz mono, phù hợp speech-to-text.","output_path":str(out)}



def csv_to_json(p):
    out=p.with_name(p.stem+"-converted.json")
    rows=[]
    with p.open("r",encoding="utf-8-sig",newline="") as source:
        reader=csv.reader(source)
        headers=next(reader,None)
        if not headers:
            raise RuntimeError("CSV không có header.")
        if len(headers)>200:
            raise RuntimeError("CSV vượt quá 200 cột.")
        headers=[str(value).strip() for value in headers]
        if any(not value for value in headers):
            raise RuntimeError("CSV có tên cột rỗng; hãy đặt header cho mọi cột.")
        if len({value.casefold() for value in headers})!=len(headers):
            raise RuntimeError("CSV có header trùng nhau; không thể chuyển đổi mà không làm mất dữ liệu.")
        for line_number,row in enumerate(reader,2):
            if len(row)>len(headers):
                raise RuntimeError(f"Dòng CSV {line_number} có nhiều ô hơn header.")
            row=row+[""]*(len(headers)-len(row))
            rows.append(dict(zip(headers,row)))
            if len(rows)>100000:
                raise RuntimeError("CSV vượt quá 100.000 dòng dữ liệu.")
    out.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("JSON output exceeds the 45 MB delivery limit.")
    return {"summary":f"Đã chuyển {len(rows):,} dòng và {len(headers)} cột CSV thành mảng JSON; giá trị được giữ nguyên dưới dạng chuỗi.","output_path":str(out)}

def jsonl_format(p):
    out=p.with_name(p.stem+"-formatted.jsonl")
    rendered=[]
    def reject_constant(value):
        raise ValueError("Non-standard JSON constant: "+value)
    with p.open("r",encoding="utf-8-sig") as source:
        for line_number,line in enumerate(source,1):
            if not line.strip():
                continue
            try:
                value=json.loads(line,parse_constant=reject_constant)
            except (json.JSONDecodeError,ValueError) as exc:
                raise RuntimeError(f"JSONL lỗi tại dòng {line_number}: {str(exc)[:220]}") from exc
            rendered.append(json.dumps(value,ensure_ascii=False,separators=(",",":")))
            if len(rendered)>100000:
                raise RuntimeError("JSONL vượt quá 100.000 dòng dữ liệu.")
    if not rendered:
        raise RuntimeError("JSONL không có dòng dữ liệu hợp lệ.")
    out.write_text("\n".join(rendered)+"\n",encoding="utf-8")
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("JSONL output exceeds the 45 MB delivery limit.")
    return {"summary":f"JSONL hợp lệ: {len(rendered):,} dòng đã được chuẩn hóa; dòng trống được bỏ qua.","output_path":str(out)}

def _yaml_json_value(value, depth=0, seen=None, counter=None):
    import datetime as _datetime
    if seen is None: seen=set()
    if counter is None: counter=[0]
    counter[0]+=1
    if counter[0]>100000 or depth>80:
        raise RuntimeError("YAML structure exceeds the 100,000-node or 80-level safety limit.")
    if value is None or isinstance(value,(str,bool,int)):
        return value
    if isinstance(value,float):
        if not __import__("math").isfinite(value):
            raise RuntimeError("YAML non-finite numbers cannot be represented as strict JSON.")
        return value
    if isinstance(value,(_datetime.datetime,_datetime.date,_datetime.time)):
        return value.isoformat()
    if isinstance(value,(list,tuple,dict)):
        identity=id(value)
        if identity in seen:
            raise RuntimeError("YAML recursive aliases are not supported.")
        seen.add(identity)
        try:
            if isinstance(value,dict):
                result={}
                for key,item in value.items():
                    if not isinstance(key,str):
                        raise RuntimeError("YAML mapping keys must be strings for JSON conversion.")
                    result[key]=_yaml_json_value(item,depth+1,seen,counter)
                return result
            return [_yaml_json_value(item,depth+1,seen,counter) for item in value]
        finally:
            seen.remove(identity)
    raise RuntimeError("YAML contains a value type that cannot be represented safely as JSON.")

def yaml_to_json(p):
    import yaml
    out=p.with_name(p.stem+"-converted.json")
    try:
        documents=[]
        for document in yaml.safe_load_all(p.read_text(encoding="utf-8-sig")):
            documents.append(_yaml_json_value(document))
            if len(documents)>100:
                raise RuntimeError("YAML vượt quá 100 document.")
    except yaml.YAMLError as exc:
        raise RuntimeError("YAML không hợp lệ: "+str(exc)[:500]) from exc
    value=documents[0] if len(documents)==1 else documents
    out.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("JSON output exceeds the 45 MB delivery limit.")
    return {"summary":f"Đã chuyển {len(documents)} YAML document bằng SafeLoader sang JSON; alias vòng lặp và key không phải chuỗi bị từ chối.","output_path":str(out)}

def xml_to_json(p):
    import xml.etree.ElementTree as ET
    raw=p.read_text(encoding="utf-8-sig")
    if re.search(r"<!\s*(DOCTYPE|ENTITY)\b",raw,re.I):
        raise RuntimeError("XML DTD/ENTITY is disabled.")
    try:
        root=ET.fromstring(raw)
    except ET.ParseError as exc:
        raise RuntimeError("XML không hợp lệ: "+str(exc)[:300]) from exc
    counter=[0]
    def convert(element,depth=0):
        counter[0]+=1
        if depth>80 or counter[0]>50000:
            raise RuntimeError("XML vượt giới hạn 80 cấp hoặc 50.000 node.")
        children=list(element)
        text_value=(element.text or "").strip()
        if not children and not element.attrib:
            return text_value or None
        result={}
        if element.attrib:
            result["@attributes"]={key:value for key,value in element.attrib.items()}
        for child in children:
            value=convert(child,depth+1)
            if child.tag in result:
                if not isinstance(result[child.tag],list):
                    result[child.tag]=[result[child.tag]]
                result[child.tag].append(value)
            else:
                result[child.tag]=value
        if text_value:
            result["#text"]=text_value
        return result
    value={root.tag:convert(root)}
    out=p.with_name(p.stem+"-converted.json")
    out.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("JSON output exceeds the 45 MB delivery limit.")
    return {"summary":f"Đã chuyển XML root '{root.tag}' thành JSON; giữ thuộc tính, text và phần tử lặp. DTD/ENTITY bị chặn.","output_path":str(out)}

def sqlite_export(p):
    import sqlite3
    from urllib.parse import quote
    root=Path(os.environ.get("RUNNER_TEMP","/tmp"))/"nolane-inputs"
    temp=Path(tempfile.mkdtemp(prefix="sqlite-export-",dir=root))
    out=p.with_name(p.stem+"-tables.zip")
    uri="file:"+quote(str(p.resolve()),safe="/:")+"?mode=ro&immutable=1"
    connection=sqlite3.connect(uri,uri=True,timeout=5)
    exported=[]; total_rows=0
    try:
        connection.execute("PRAGMA query_only=ON")
        connection.set_progress_handler(lambda: 1,2_000_000)
        tables=connection.execute(
            "SELECT name,sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name LIMIT 21"
        ).fetchall()
        if len(tables)>20:
            raise RuntimeError("SQLite export hỗ trợ tối đa 20 bảng.")
        for table_index,(name,create_sql) in enumerate(tables,1):
            if create_sql and "CREATE VIRTUAL TABLE" in create_sql.upper():
                continue
            columns=connection.execute('PRAGMA table_info("'+name.replace('"','""')+'")').fetchall()
            if not columns:
                continue
            if len(columns)>200:
                raise RuntimeError(f"Bảng {name} vượt quá 200 cột.")
            safe_name=re.sub(r"[^A-Za-z0-9._-]+","_",name).strip("._-")[:55] or f"table-{table_index}"
            target=temp/(f"{table_index:02d}-{safe_name}.csv")
            quoted='"'+name.replace('"','""')+'"'
            cursor=connection.execute("SELECT * FROM "+quoted)
            count=0
            with target.open("w",encoding="utf-8-sig",newline="") as handle:
                writer=csv.writer(handle,lineterminator="\n")
                writer.writerow([_spreadsheet_safe(str(column[1])) for column in columns])
                while True:
                    batch=cursor.fetchmany(500)
                    if not batch:
                        break
                    for row in batch:
                        count+=1; total_rows+=1
                        if total_rows>100000:
                            raise RuntimeError("SQLite export vượt quá 100.000 dòng tổng cộng.")
                        values=[]
                        for value in row:
                            if isinstance(value,bytes):
                                value="hex:"+value.hex()
                            values.append(_spreadsheet_safe(value))
                        writer.writerow(values)
            exported.append((target,target.name,count))
    finally:
        connection.close()
    if not exported:
        shutil.rmtree(temp,ignore_errors=True)
        raise RuntimeError("SQLite không có bảng dữ liệu thường để xuất.")
    try:
        with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
            for source,arcname,_count in exported:
                archive.write(source,arcname=arcname)
    finally:
        shutil.rmtree(temp,ignore_errors=True)
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("SQLite export ZIP exceeds the 45 MB delivery limit.")
    return {"summary":f"Đã xuất {len(exported)} bảng SQLite và {total_rows:,} dòng thành CSV trong ZIP; database được mở chỉ đọc.","output_path":str(out)}

def xlsx_to_json(p):
    from openpyxl import load_workbook
    import datetime as _datetime
    workbook=load_workbook(p,read_only=True,data_only=True)
    output={"sheets":[]}; total_rows=0
    try:
        if len(workbook.worksheets)>20:
            raise RuntimeError("Workbook vượt quá 20 sheets.")
        for sheet_index,ws in enumerate(workbook.worksheets,1):
            rows=[]
            iterator=ws.iter_rows(values_only=True)
            header_row=next(iterator,None)
            if header_row is None:
                output["sheets"].append({"name":ws.title,"columns":[],"rows":[]})
                continue
            raw_headers=list(header_row[:200])
            headers=[]
            used=set()
            for column_index,value in enumerate(raw_headers,1):
                base=str(value).strip() if value is not None else ""
                base=base or f"Column {column_index}"
                candidate=base; suffix=2
                while candidate.casefold() in used:
                    candidate=f"{base}_{suffix}"; suffix+=1
                used.add(candidate.casefold()); headers.append(candidate)
            for row in iterator:
                total_rows+=1
                if total_rows>50000:
                    raise RuntimeError("XLSX-to-JSON vượt quá 50.000 dòng tổng cộng.")
                if len(row)>200:
                    raise RuntimeError(f"Sheet {ws.title} vượt quá 200 cột.")
                item={}
                for index,header in enumerate(headers):
                    value=row[index] if index<len(row) else None
                    if isinstance(value,(bytes,bytearray)):
                        value="hex:"+bytes(value).hex()
                    elif isinstance(value,(_datetime.datetime,_datetime.date,_datetime.time)):
                        value=value.isoformat()
                    elif value is not None and not isinstance(value,(str,int,float,bool)):
                        value=str(value)
                    item[header]=value
                rows.append(item)
            output["sheets"].append({"name":ws.title,"columns":headers,"rows":rows})
    finally:
        workbook.close()
    out=p.with_name(p.stem+"-converted.json")
    out.write_text(json.dumps(output,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("JSON output exceeds the 45 MB delivery limit.")
    return {"summary":f"Đã xuất {len(output['sheets'])} sheet và {total_rows:,} dòng thành JSON. Giá trị công thức đọc từ cache; workbook không được thực thi.","output_path":str(out)}

def pdf_extract_images(p):
    import fitz
    document=fitz.open(p)
    out=p.with_name(p.stem+"-embedded-images.zip")
    count=0; total_bytes=0; seen=set()
    try:
        if document.is_encrypted and document.needs_pass:
            raise RuntimeError("PDF được mã hóa bằng mật khẩu.")
        if document.page_count>100:
            raise RuntimeError("PDF image extraction giới hạn tối đa 100 trang.")
        with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
            for page_number,page in enumerate(document,1):
                for image_ref in page.get_images(full=True):
                    xref=int(image_ref[0])
                    if xref in seen:
                        continue
                    seen.add(xref)
                    extracted=document.extract_image(xref)
                    payload=extracted.get("image",b"")
                    if not payload:
                        continue
                    count+=1; total_bytes+=len(payload)
                    if count>100 or len(payload)>20*1024*1024 or total_bytes>120*1024*1024:
                        raise RuntimeError("PDF vượt giới hạn 100 ảnh, 20 MB mỗi ảnh hoặc 120 MB tổng ảnh.")
                    extension=re.sub(r"[^a-z0-9]","",str(extracted.get("ext","bin")).lower())[:5] or "bin"
                    archive.writestr(f"page-{page_number:03d}-image-{count:03d}.{extension}",payload)
    except Exception:
        out.unlink(missing_ok=True)
        raise
    finally:
        document.close()
    if count==0:
        out.unlink(missing_ok=True)
        raise RuntimeError("PDF không có ảnh raster nhúng để trích xuất. Tool này không render nguyên trang PDF.")
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("Extracted images ZIP exceeds the 45 MB delivery limit.")
    return {"summary":f"Đã trích {count} ảnh raster nhúng ({total_bytes:,} bytes) từ PDF và đóng gói ZIP; ảnh dùng chung được khử trùng theo xref.","output_path":str(out)}

def archive_manifest(p):
    out=p.with_name(p.stem+"-sha256-manifest.csv")
    rows=[]; total_size=0
    def digest_stream(handle,expected_size):
        digest=hashlib.sha256(); read_size=0
        while True:
            chunk=handle.read(1024*1024)
            if not chunk: break
            read_size+=len(chunk)
            if read_size>expected_size or read_size>150*1024*1024:
                raise RuntimeError("Archive member vượt kích thước khai báo hoặc giới hạn 150 MB.")
            digest.update(chunk)
        if read_size!=expected_size:
            raise RuntimeError("Archive member có kích thước thực tế không khớp metadata.")
        return digest.hexdigest()
    if zipfile.is_zipfile(p):
        with zipfile.ZipFile(p) as archive:
            infos=archive.infolist()
            if len(infos)>200:
                raise RuntimeError("Archive manifest hỗ trợ tối đa 200 mục.")
            for info in infos:
                if info.is_dir():
                    continue
                parts=_safe_archive_parts(info.filename)
                mode=(info.external_attr>>16)&0xFFFF
                file_type=stat.S_IFMT(mode)
                # Some ZIP writers store permission bits without S_IFREG; zero type bits are not special files.
                if stat.S_ISLNK(mode) or (file_type and file_type not in (stat.S_IFREG,stat.S_IFDIR)):
                    raise RuntimeError("Archive chứa symlink hoặc special file bị chặn.")
                if info.flag_bits&0x1:
                    raise RuntimeError("Archive mã hóa không được hỗ trợ.")
                if info.file_size>150*1024*1024 or (info.compress_size and info.file_size/max(1,info.compress_size)>200):
                    raise RuntimeError("Archive member vượt giới hạn kích thước hoặc compression ratio.")
                total_size+=info.file_size
                if total_size>150*1024*1024:
                    raise RuntimeError("Archive vượt 150 MB dữ liệu giải nén.")
                with archive.open(info,"r") as handle:
                    checksum=digest_stream(handle,info.file_size)
                rows.append(("/".join(parts),info.file_size,checksum))
    elif tarfile.is_tarfile(p):
        with tarfile.open(p,"r:*") as archive:
            members=archive.getmembers()
            if len(members)>200:
                raise RuntimeError("Archive manifest hỗ trợ tối đa 200 mục.")
            for member in members:
                if member.isdir():
                    continue
                if not member.isfile():
                    raise RuntimeError("TAR chứa symlink, hardlink hoặc special file bị chặn.")
                parts=_safe_archive_parts(member.name)
                if member.size<0:
                    raise RuntimeError("TAR member có kích thước không hợp lệ.")
                total_size+=member.size
                if total_size>150*1024*1024:
                    raise RuntimeError("Archive vượt 150 MB dữ liệu giải nén.")
                handle=archive.extractfile(member)
                if handle is None:
                    raise RuntimeError("Không thể đọc TAR member.")
                with handle:
                    checksum=digest_stream(handle,member.size)
                rows.append(("/".join(parts),member.size,checksum))
    else:
        raise RuntimeError("Archive manifest chỉ hỗ trợ ZIP, TAR, TGZ và TAR.GZ hợp lệ.")
    if not rows:
        raise RuntimeError("Archive không có tệp thường để tạo manifest.")
    with out.open("w",encoding="utf-8-sig",newline="") as target:
        writer=csv.writer(target,lineterminator="\n")
        writer.writerow(["path","size_bytes","sha256"])
        writer.writerows(rows)
    return {"summary":f"Đã tạo SHA-256 manifest cho {len(rows)} tệp trong archive ({total_size:,} bytes) mà không giải nén ra đĩa.","output_path":str(out)}

def text_stats(p):
    from collections import Counter
    raw=p.read_text(encoding="utf-8-sig")
    words=re.findall(r"[^\W_]+(?:['’][^\W_]+)?",raw,flags=re.UNICODE)
    normalized=[word.casefold() for word in words]
    counts=Counter(normalized)
    sentences=len(re.findall(r"[.!?。！？]+",raw))
    paragraphs=sum(1 for block in re.split(r"\n\s*\n",raw) if block.strip())
    report=[
        f"File: {p.name}",
        f"Characters (including whitespace): {len(raw):,}",
        f"Characters (excluding whitespace): {sum(not char.isspace() for char in raw):,}",
        f"Words: {len(words):,}",
        f"Unique words: {len(counts):,}",
        f"Sentences (punctuation-based estimate): {sentences:,}",
        f"Non-empty paragraphs: {paragraphs:,}",
        f"Estimated reading time at 200 words/min: {max(1,(len(words)+199)//200)} minute(s)",
        "Top terms: "+(", ".join(f"{word} ({count})" for word,count in counts.most_common(20)) if counts else "No words detected"),
        "Note: tokenization is language-neutral and does not perform Vietnamese syllable/word segmentation.",
    ]
    return tool_text("\n".join(report),"Text statistics")


def _safe_zip_members(archive, suffixes, max_files=200, max_bytes=100*1024*1024):
    selected=[]; count=0; total=0
    allowed={suffix.lower() for suffix in suffixes}
    for item in archive.infolist():
        if item.is_dir(): continue
        count+=1
        if count>max_files: raise RuntimeError(f"ZIP vượt giới hạn {max_files} tệp.")
        if item.flag_bits & 0x1: raise RuntimeError("ZIP chứa tệp mã hóa.")
        mode=(item.external_attr>>16)&0xFFFF
        file_type=stat.S_IFMT(mode)
        if file_type==stat.S_IFLNK or (file_type and file_type not in (stat.S_IFREG,stat.S_IFDIR)):
            raise RuntimeError("ZIP chứa symlink hoặc special file.")
        _safe_archive_parts(item.filename)
        total+=item.file_size
        if total>max_bytes: raise RuntimeError("ZIP vượt giới hạn dữ liệu giải nén.")
        if item.file_size>2*1024*1024 and item.compress_size and item.file_size/max(1,item.compress_size)>250:
            raise RuntimeError("ZIP có tỷ lệ nén bất thường.")
        if Path(item.filename).suffix.lower() in allowed: selected.append(item)
    return selected,total


def pdf_merge(p):
    import fitz
    if not zipfile.is_zipfile(p): raise RuntimeError("Gửi ZIP chứa các PDF cần gộp.")
    out=p.with_name(p.stem+"-merged.pdf"); merged=fitz.open(); total_pages=0; members=[]; total_bytes=0
    try:
        with zipfile.ZipFile(p) as archive:
            members,total_bytes=_safe_zip_members(archive,{".pdf"},max_files=50,max_bytes=100*1024*1024)
            if not members: raise RuntimeError("ZIP không chứa PDF.")
            members.sort(key=lambda item:item.filename.casefold())
            for item in members:
                source=fitz.open(stream=archive.read(item),filetype="pdf")
                try:
                    if source.is_encrypted and source.needs_pass: raise RuntimeError("PDF mã hóa mật khẩu: "+Path(item.filename).name)
                    total_pages+=source.page_count
                    if total_pages>300: raise RuntimeError("Tổng tài liệu vượt quá 300 trang.")
                    merged.insert_pdf(source)
                finally: source.close()
        if merged.page_count<1: raise RuntimeError("Không có trang PDF hợp lệ để gộp.")
        merged.save(str(out),garbage=4,deflate=True,clean=True)
    finally: merged.close()
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True); raise RuntimeError("PDF gộp vượt giới hạn đầu ra 45 MB.")
    return {"summary":f"Đã gộp {len(members)} PDF, tổng {total_pages} trang ({total_bytes:,} bytes ZIP), theo thứ tự tên tệp.","output_path":str(out)}


def pdf_metadata_clean(p):
    import fitz
    document=fitz.open(p)
    if document.is_encrypted and document.needs_pass:
        document.close(); raise RuntimeError("PDF được mã hóa bằng mật khẩu.")
    out=p.with_name(p.stem+"-metadata-clean.pdf")
    try:
        document.set_metadata({"title":"","author":"","subject":"","keywords":"","creator":"","producer":"","creationDate":"","modDate":"","trapped":""})
        try: document.del_xml_metadata()
        except Exception: pass
        document.save(str(out),garbage=4,deflate=True,clean=True)
    finally: document.close()
    return {"summary":"Đã xóa các trường metadata chuẩn và XML metadata khỏi PDF; nội dung trang không bị raster hóa.","output_path":str(out)}


def pdf_outline(p):
    import fitz
    document=fitz.open(p)
    try:
        if document.is_encrypted and document.needs_pass: raise RuntimeError("PDF được mã hóa bằng mật khẩu.")
        if document.page_count>500: raise RuntimeError("PDF outline giới hạn 500 trang.")
        toc=document.get_toc()
        if not toc: return tool_text("PDF không có bookmark hoặc mục lục nhúng.","PDF outline")
        rows=[f"Pages: {document.page_count}",f"Bookmarks: {len(toc)}",""]
        rows.extend("  "*(max(0,int(level)-1))+f"- {title} (page {page})" for level,title,page in toc[:5000])
        return tool_text("\n".join(rows),"PDF outline")
    finally: document.close()


def image_contact_sheet(p):
    import io
    from PIL import Image,ImageOps,ImageDraw
    if not zipfile.is_zipfile(p): raise RuntimeError("Gửi ZIP chứa các ảnh cần xem.")
    thumbnails=[]; labels=[]
    with zipfile.ZipFile(p) as archive:
        members,total=_safe_zip_members(archive,{".jpg",".jpeg",".png",".webp",".bmp",".tif",".tiff"},max_files=120,max_bytes=100*1024*1024)
        if not members: raise RuntimeError("ZIP không chứa ảnh được hỗ trợ.")
        for index,item in enumerate(members[:80],1):
            with Image.open(io.BytesIO(archive.read(item))) as raw:
                _guard_image_dimensions(raw)
                image=ImageOps.exif_transpose(raw).convert("RGB")
                image.thumbnail((232,158),Image.Resampling.LANCZOS)
                thumbnails.append(image.copy()); labels.append(f"{index:03d} {Path(item.filename).name[:46]}")
    columns=4; cell_w=260; cell_h=198; rows=(len(thumbnails)+columns-1)//columns
    sheet=Image.new("RGB",(columns*cell_w,rows*cell_h),(248,248,248)); draw=ImageDraw.Draw(sheet)
    for index,(image,label) in enumerate(zip(thumbnails,labels)):
        x=(index%columns)*cell_w; y=(index//columns)*cell_h
        sheet.paste(image,(x+(cell_w-image.width)//2,y+6+(158-image.height)//2))
        draw.text((x+8,y+168),f"Image {index+1:03d}",fill=(30,30,30))
    out=p.with_name(p.stem+"-contact-sheet.jpg")
    sheet.save(out,"JPEG",quality=88,optimize=True); sheet.close()
    for image in thumbnails: image.close()
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True); raise RuntimeError("Contact sheet vượt giới hạn đầu ra.")
    return {"summary":f"Đã tạo contact sheet cho {len(thumbnails)} ảnh ({total:,} bytes giải nén). Tệp: "+"; ".join(labels),"output_path":str(out)}


def image_duplicates(p):
    import io
    from PIL import Image,ImageOps
    if not zipfile.is_zipfile(p): raise RuntimeError("Gửi ZIP chứa bộ ảnh cần so sánh.")
    records=[]
    with zipfile.ZipFile(p) as archive:
        members,total=_safe_zip_members(archive,{".jpg",".jpeg",".png",".webp",".bmp",".tif",".tiff"},max_files=120,max_bytes=100*1024*1024)
        if not members: raise RuntimeError("ZIP không chứa ảnh hợp lệ.")
        for item in members:
            payload=archive.read(item)
            with Image.open(io.BytesIO(payload)) as raw:
                _guard_image_dimensions(raw)
                image=ImageOps.exif_transpose(raw).convert("L").resize((8,8),Image.Resampling.LANCZOS)
                pixels=list(image.getdata()); average=sum(pixels)/len(pixels)
                phash=sum((1<<index) for index,value in enumerate(pixels) if value>=average)
            records.append((item.filename,hashlib.sha256(payload).hexdigest(),phash))
    out=p.with_name(p.stem+"-image-duplicates.csv"); matches=[]
    for left in range(len(records)):
        for right in range(left+1,len(records)):
            a=records[left]; b=records[right]; distance=(a[2]^b[2]).bit_count()
            if a[1]==b[1]: matches.append((a[0],b[0],"exact-sha256",0))
            elif distance<=4: matches.append((a[0],b[0],"near-visual",distance))
    with out.open("w",encoding="utf-8-sig",newline="") as target:
        writer=csv.writer(target,lineterminator="\n"); writer.writerow(["file_a","file_b","match_type","perceptual_distance"])
        writer.writerows([(_spreadsheet_safe(a),_spreadsheet_safe(b),kind,distance) for a,b,kind,distance in matches])
    return {"summary":f"Đã phân tích {len(records)} ảnh ({total:,} bytes). Tìm thấy {len(matches)} cặp giống/gần giống; perceptual hash 8×8, ngưỡng ≤4.","output_path":str(out)}


def csv_split(p):
    import io
    out=p.with_name(p.stem+"-parts.zip"); total_rows=0; parts=0
    with p.open("r",encoding="utf-8-sig",newline="") as source,zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        reader=csv.reader(source,strict=True); header=next(reader,None)
        if not header: raise RuntimeError("CSV không có header.")
        if len(header)>200: raise RuntimeError("CSV vượt 200 cột.")
        rows=[]
        for row in reader:
            total_rows+=1
            if total_rows>100000: raise RuntimeError("CSV split hỗ trợ tối đa 100.000 dòng dữ liệu.")
            if len(row)>200: raise RuntimeError("Một dòng CSV vượt 200 cột.")
            rows.append(row)
            if len(rows)>=10000:
                parts+=1; buffer=io.StringIO(newline=""); writer=csv.writer(buffer,lineterminator="\n")
                writer.writerow(header); writer.writerows(rows); archive.writestr(f"part-{parts:03d}.csv",buffer.getvalue().encode("utf-8-sig")); rows=[]
        if rows or parts==0:
            parts+=1; buffer=io.StringIO(newline=""); writer=csv.writer(buffer,lineterminator="\n")
            writer.writerow(header); writer.writerows(rows); archive.writestr(f"part-{parts:03d}.csv",buffer.getvalue().encode("utf-8-sig"))
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True); raise RuntimeError("CSV parts ZIP vượt giới hạn đầu ra.")
    return {"summary":f"Đã chia {total_rows:,} dòng thành {parts} CSV; mỗi phần giữ header và tối đa 10.000 dòng.","output_path":str(out)}


def csv_join(p):
    import io
    if not zipfile.is_zipfile(p): raise RuntimeError("Gửi ZIP chứa các CSV cần gộp.")
    out=p.with_name(p.stem+"-joined.csv"); total_rows=0; files=0; expected_header=None
    with zipfile.ZipFile(p) as archive:
        members,total=_safe_zip_members(archive,{".csv"},max_files=100,max_bytes=100*1024*1024)
        if not members: raise RuntimeError("ZIP không chứa CSV.")
        members.sort(key=lambda item:item.filename.casefold())
        with out.open("w",encoding="utf-8-sig",newline="") as target:
            writer=csv.writer(target,lineterminator="\n")
            for item in members:
                with archive.open(item) as raw:
                    text=io.TextIOWrapper(raw,encoding="utf-8-sig",newline=""); reader=csv.reader(text,strict=True); header=next(reader,None)
                    if not header: raise RuntimeError("CSV rỗng hoặc không có header: "+Path(item.filename).name)
                    if len(header)>200: raise RuntimeError("CSV vượt 200 cột.")
                    if expected_header is None:
                        expected_header=header; writer.writerow([_spreadsheet_safe(value) for value in header])
                    elif header!=expected_header: raise RuntimeError("Header giữa các CSV không khớp: "+Path(item.filename).name)
                    for row in reader:
                        total_rows+=1
                        if total_rows>100000: raise RuntimeError("CSV join vượt 100.000 dòng tổng cộng.")
                        if len(row)>200: raise RuntimeError("Một dòng CSV vượt 200 cột.")
                        writer.writerow([_spreadsheet_safe(value) for value in row])
                files+=1
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True); raise RuntimeError("CSV joined vượt giới hạn đầu ra.")
    return {"summary":f"Đã gộp {files} CSV, {total_rows:,} dòng ({total:,} bytes giải nén); header phải khớp và ô nguy hiểm được escape.","output_path":str(out)}


def _schema_for_values(values,depth=0):
    if depth>40: raise RuntimeError("JSON schema vượt 40 cấp lồng nhau.")
    non_null=[value for value in values if value is not None]; nullable=len(non_null)!=len(values)
    if not non_null: return {"type":"null"}
    if all(isinstance(value,dict) for value in non_null):
        keys=sorted(set().union(*(value.keys() for value in non_null)))
        properties={key:_schema_for_values([value[key] for value in non_null if key in value],depth+1) for key in keys}
        required=sorted(key for key in keys if all(key in value for value in non_null))
        result={"type":"object","properties":properties,"additionalProperties":True}
        if required: result["required"]=required
    elif all(isinstance(value,list) for value in non_null):
        children=[child for value in non_null for child in value[:500]]
        result={"type":"array","items":_schema_for_values(children,depth+1) if children else {}}
    else:
        kinds=[]
        for value in non_null:
            if isinstance(value,bool): kind="boolean"
            elif isinstance(value,int): kind="integer"
            elif isinstance(value,float): kind="number"
            elif isinstance(value,str): kind="string"
            else: kind="object" if isinstance(value,dict) else "array" if isinstance(value,list) else "null"
            if kind not in kinds: kinds.append(kind)
        result={"type":kinds[0] if len(kinds)==1 else kinds}
    if nullable and result.get("type")!="null":
        value_type=result["type"]; result["type"]=value_type+["null"] if isinstance(value_type,list) else [value_type,"null"]
    return result


def json_schema(p):
    value=json.loads(p.read_text(encoding="utf-8-sig"))
    schema={"$schema":"https://json-schema.org/draft/2020-12/schema",**_schema_for_values([value])}
    out=p.with_name(p.stem+"-schema.json")
    out.write_text(json.dumps(schema,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True); raise RuntimeError("JSON Schema vượt giới hạn đầu ra.")
    return {"summary":"Đã suy luận JSON Schema 2020-12 từ cấu trúc dữ liệu; hỗ trợ nested, required và nullable.","output_path":str(out)}


def json_to_yaml(p):
    import yaml
    value=json.loads(p.read_text(encoding="utf-8-sig")); out=p.with_name(p.stem+"-converted.yaml")
    out.write_text(yaml.safe_dump(value,allow_unicode=True,sort_keys=False,default_flow_style=False),encoding="utf-8")
    return {"summary":"Đã chuyển JSON sang YAML bằng SafeDumper, giữ Unicode và thứ tự key.","output_path":str(out)}


def sqlite_integrity(p):
    from urllib.parse import quote
    import sqlite3
    uri="file:"+quote(str(p.resolve()),safe="/:")+"?mode=ro&immutable=1"
    connection=sqlite3.connect(uri,uri=True,timeout=5)
    try:
        connection.execute("PRAGMA query_only=ON")
        connection.set_progress_handler(lambda:1,2_000_000)
        integrity=[row[0] for row in connection.execute("PRAGMA integrity_check(100)").fetchmany(100)]
        foreign=list(connection.execute("PRAGMA foreign_key_check").fetchmany(100))
        tables=connection.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchone()[0]
        report=["SQLite integrity report",f"Tables: {tables}",f"Integrity result: {', '.join(integrity) if integrity else 'no result'}",f"Foreign-key violations: {len(foreign)}"]
        report.extend("Foreign key: "+", ".join(str(value) for value in row) for row in foreign[:20])
        report.append("Database opened read-only; no schema or data was modified.")
        report.append("STATUS: issues detected." if integrity!=["ok"] or foreign else "STATUS: integrity check passed.")
        return tool_text("\n".join(report),"SQLite integrity")
    finally: connection.close()


def _silence_report(p,media_kind):
    data=ffprobe(p); duration=float(data.get("format",{}).get("duration") or 0)
    if duration<=0 or duration>1800: raise RuntimeError("Silence analysis hỗ trợ media dài tối đa 30 phút.")
    audio=[stream for stream in data.get("streams",[]) if stream.get("codec_type")=="audio"]
    if not audio: raise RuntimeError("Video không có track audio để phân tích." if media_kind=="video" else "Không tìm thấy track audio.")
    process=subprocess.run(["ffmpeg","-hide_banner","-i",str(p),"-map","0:a:0","-af","silencedetect=noise=-35dB:d=0.4","-f","null","-"],capture_output=True,text=True,timeout=900,check=False)
    if process.returncode!=0: raise RuntimeError("FFmpeg silence detection failed: "+(process.stderr or process.stdout)[-900:])
    starts=[]; intervals=[]
    for line in (process.stderr or "").splitlines():
        match=re.search(r"silence_start:\s*([0-9.]+)",line)
        if match: starts.append(float(match.group(1)))
        match=re.search(r"silence_end:\s*([0-9.]+)",line)
        if match and starts:
            start=starts.pop(0); end=float(match.group(1)); intervals.append((start,max(start,end)))
    for start in starts: intervals.append((start,duration))
    total=sum(end-start for start,end in intervals)
    rows=[f"Media: {p.name}",f"Duration: {duration:.3f} seconds",f"Silence intervals: {len(intervals)}",f"Total detected silence: {total:.3f} seconds","Threshold: -35 dB for at least 0.4 seconds",""]
    rows.extend(f"{i}. {start:.3f}s → {end:.3f}s ({end-start:.3f}s)" for i,(start,end) in enumerate(intervals,1))
    if not intervals: rows.append("No silence interval crossed the selected threshold.")
    return tool_text("\n".join(rows),f"{media_kind.title()} silence analysis")


def audio_silence_report(p): return _silence_report(p,"audio")
def video_silence_report(p): return _silence_report(p,"video")


def video_frames(p):
    data=ffprobe(p); duration=float(data.get("format",{}).get("duration") or 0)
    if duration<=0 or duration>1800: raise RuntimeError("Frame extraction hỗ trợ video dài tối đa 30 phút.")
    root=Path(os.environ.get("RUNNER_TEMP","/tmp"))/"nolane-inputs"
    temp=Path(tempfile.mkdtemp(prefix="video-frames-",dir=root)); out=p.with_name(p.stem+"-frames.zip")
    interval=max(1.0,duration/60.0); pattern=temp/"frame-%03d.jpg"
    try:
        cmd("ffmpeg",["-y","-i",str(p),"-vf",f"fps=1/{interval:.5f},scale='min(960,iw)':-2","-frames:v","60","-q:v","4",str(pattern)],900)
        frames=sorted(temp.glob("frame-*.jpg"))
        if not frames: raise RuntimeError("FFmpeg không trích xuất được frame.")
        with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=4) as archive:
            for frame in frames: archive.write(frame,frame.name)
    finally: shutil.rmtree(temp,ignore_errors=True)
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True); raise RuntimeError("Video frames ZIP vượt giới hạn đầu ra.")
    return {"summary":f"Đã trích {len(frames)} frame JPEG, cách đều khoảng {interval:.2f} giây trên video {duration:.1f} giây.","output_path":str(out)}


def subtitle_convert(p):
    source=p.read_text(encoding="utf-8-sig")
    is_vtt=p.suffix.lower()==".vtt" or source.lstrip().startswith("WEBVTT")
    if is_vtt:
        lines=source.replace("\r\n","\n").replace("\r","\n").split("\n")
        while lines and (not lines[0].strip() or lines[0].strip().startswith(("WEBVTT","NOTE","STYLE","REGION"))): lines.pop(0)
        rendered="\n".join(lines)
        rendered=re.sub(r"(?<!\d)(\d{2}:\d{2}:\d{2})\.(\d{3})(?!\d)",r"\1,\2",rendered)
        out=p.with_name(p.stem+"-converted.srt")
    else:
        rendered=re.sub(r"(?<!\d)(\d{2}:\d{2}:\d{2}),(\d{3})(?!\d)",r"\1.\2",source.replace("\r\n","\n").replace("\r","\n"))
        rendered="WEBVTT\n\n"+rendered.lstrip(); out=p.with_name(p.stem+"-converted.vtt")
    if not re.search(r"\d{2}:\d{2}:\d{2}[,.]\d{3}\s+-->",rendered): raise RuntimeError("Không phát hiện cue timestamp SRT/VTT hợp lệ.")
    out.write_text(rendered.rstrip()+"\n",encoding="utf-8")
    return {"summary":"Đã chuyển định dạng phụ đề "+("WebVTT → SRT" if is_vtt else "SRT → WebVTT")+"; nội dung cue được giữ nguyên.","output_path":str(out)}


def text_join(inputs):
    if not isinstance(inputs,list) or not 2<=len(inputs)<=MAX_DAG_PARENTS:
        raise RuntimeError(f"Text join requires 2 to {MAX_DAG_PARENTS} parent artifacts inside a DAG workflow.")
    paths=inputs
    sections=[]
    total=0
    for index,path in enumerate(paths,1):
        path=Path(path)
        if not path.is_file() or path.is_symlink():
            raise RuntimeError("Text join accepts only regular text files.")
        size=path.stat().st_size
        total+=size
        if total>MAX_PIPELINE_OUTPUT:
            raise RuntimeError("Combined text join inputs exceed the 45 MB limit.")
        try:
            content=path.read_text(encoding="utf-8-sig")
        except UnicodeError as exc:
            raise RuntimeError("Text join input is not valid UTF-8: "+path.name) from exc
        if "\x00" in content:
            raise RuntimeError("Text join refuses binary-like input: "+path.name)
        label=path.name.replace("\r"," ").replace("\n"," ").replace("[","(").replace("]",")")[:120]
        sections.append(f"===== SOURCE {index}: {label} =====\n{content.strip()}\n")
    out=Path(paths[0]).parent/(Path(paths[0]).stem+"-joined.txt")
    rendered="\n".join(sections).rstrip()+"\n"
    if len(rendered.encode("utf-8"))>MAX_PIPELINE_OUTPUT:
        raise RuntimeError("Merged text output exceeds the 45 MB limit.")
    out.write_text(rendered,encoding="utf-8")
    return {"summary":f"Đã hợp nhất {len(paths)} nhánh văn bản theo thứ tự phụ thuộc, tổng {total:,} bytes đầu vào.","output_path":str(out)}


def text_deduplicate(p):
    raw=p.read_text(encoding="utf-8-sig"); seen=set(); kept=[]; removed=0
    for line in raw.splitlines():
        key=unicodedata.normalize("NFC",line).strip().casefold()
        if key and key in seen: removed+=1; continue
        if key: seen.add(key)
        kept.append(line)
    out=p.with_name(p.stem+"-deduplicated"+p.suffix)
    out.write_text("\n".join(kept)+("\n" if raw.endswith(("\n","\r")) else ""),encoding="utf-8")
    return {"summary":f"Đã giữ {len(kept):,} dòng và loại {removed:,} dòng trùng (Unicode NFC, không phân biệt hoa/thường).","output_path":str(out)}


def text_diff(p):
    import difflib
    if not zipfile.is_zipfile(p): raise RuntimeError("Gửi ZIP chứa đúng hai tệp văn bản cần so sánh.")
    with zipfile.ZipFile(p) as archive:
        members,total=_safe_zip_members(archive,{".txt",".md",".log",".srt",".vtt",".json",".csv",".yaml",".yml",".xml"},max_files=20,max_bytes=10*1024*1024)
        if len(members)!=2: raise RuntimeError("ZIP phải có đúng hai tệp văn bản được hỗ trợ.")
        members.sort(key=lambda item:item.filename.casefold())
        left=archive.read(members[0]).decode("utf-8-sig").splitlines(keepends=True)
        right=archive.read(members[1]).decode("utf-8-sig").splitlines(keepends=True)
    diff="".join(difflib.unified_diff(left,right,fromfile=members[0].filename,tofile=members[1].filename,n=3))
    same=not diff
    if same: diff="Hai tệp không có khác biệt về nội dung.\n"
    out=p.with_name(p.stem+"-diff.txt"); out.write_text(diff,encoding="utf-8")
    return {"summary":f"Đã so sánh {Path(members[0].filename).name} và {Path(members[1].filename).name}; "+("không có khác biệt." if same else "unified diff được đính kèm."),"output_path":str(out)}


def code_size_report(p):
    supported={".py",".pyw",".js",".mjs",".cjs",".ts",".tsx",".jsx",".css",".html",".htm",".json",".yaml",".yml",".sh",".bash",".go",".rs",".java",".c",".cpp",".h",".hpp",".cs",".sql",".md"}
    if p.suffix.lower() not in supported: raise RuntimeError("Định dạng source file không được hỗ trợ.")
    if p.stat().st_size>5*1024*1024: raise RuntimeError("Code size report giới hạn file 5 MB.")
    lines=p.read_text(encoding="utf-8-sig").splitlines()
    blank=sum(1 for line in lines if not line.strip())
    prefix=("#","//","/*","*","--",";","<!--")
    comment=sum(1 for line in lines if line.strip() and line.lstrip().startswith(prefix))
    trailing=sum(1 for line in lines if line.rstrip()!=line)
    longest=max(((len(line),index+1) for index,line in enumerate(lines)),default=(0,0))
    report=[f"File: {p.name}",f"Bytes: {p.stat().st_size:,}",f"Total lines: {len(lines):,}",f"Blank lines: {blank:,}",f"Comment-like lines: {comment:,}",f"Non-blank non-comment lines (approx): {max(0,len(lines)-blank-comment):,}",f"Trailing whitespace: {trailing:,}",f"Longest line: {longest[0]:,} characters (line {longest[1]})","Note: comment counting uses a lightweight prefix heuristic, not a language-aware parser."]
    return tool_text("\n".join(report),"Source size report")


def image_grayscale(p):
    from PIL import Image, ImageOps
    out=p.with_name(p.stem+"-grayscale.png")
    with Image.open(p) as raw:
        _guard_image_dimensions(raw)
        oriented=ImageOps.exif_transpose(raw)
        has_alpha=("A" in oriented.getbands()) or ("transparency" in oriented.info)
        if has_alpha:
            rgba=oriented.convert("RGBA")
            gray=ImageOps.grayscale(rgba)
            gray.putalpha(rgba.getchannel("A"))
        else:
            gray=ImageOps.grayscale(oriented)
        gray.save(out,"PNG",optimize=True)
        gray.close()
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("Grayscale PNG exceeds the 45 MB delivery limit.")
    return {"summary":f"Đã chuyển ảnh {p.suffix.lower()} thành PNG thang xám; EXIF orientation được áp dụng và alpha được giữ nếu có.","output_path":str(out)}


def pdf_rotate_cw(p):
    import fitz
    document=fitz.open(p)
    if document.is_encrypted and document.needs_pass:
        document.close()
        raise RuntimeError("PDF được mã hóa bằng mật khẩu.")
    if document.page_count>500:
        document.close()
        raise RuntimeError("Xoay PDF hỗ trợ tối đa 500 trang mỗi lượt.")
    page_count=document.page_count
    out=p.with_name(p.stem+"-rotated-cw.pdf")
    try:
        for page in document:
            page.set_rotation((page.rotation+90)%360)
        document.save(str(out),garbage=4,deflate=True,clean=True)
    finally:
        document.close()
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("PDF sau khi xoay vượt giới hạn đầu ra 45 MB.")
    return {"summary":f"Đã xoay theo chiều kim đồng hồ 90° cho {page_count} trang; text/vector được giữ nguyên.","output_path":str(out)}


def pdf_remove_blank(p):
    import fitz
    from PIL import Image
    source=fitz.open(p)
    if source.is_encrypted and source.needs_pass:
        source.close()
        raise RuntimeError("PDF được mã hóa bằng mật khẩu.")
    if source.page_count>500:
        source.close()
        raise RuntimeError("Kiểm tra trang trắng hỗ trợ tối đa 500 trang.")
    kept=[]; removed=0
    out=p.with_name(p.stem+"-no-blank-pages.pdf")
    try:
        for index,page in enumerate(source):
            if page.get_text("text").strip():
                kept.append(index)
                continue
            pix=page.get_pixmap(matrix=fitz.Matrix(0.5,0.5),alpha=False)
            image=Image.frombytes("RGB",(pix.width,pix.height),pix.samples).convert("L")
            histogram=image.histogram()
            ink=sum(histogram[:245])/max(1,pix.width*pix.height)
            image.close()
            if ink>=0.0001:
                kept.append(index)
            else:
                removed+=1
        if not kept:
            raise RuntimeError("Tất cả trang đều có vẻ trắng; từ chối tạo PDF rỗng.")
        if removed==0:
            raise RuntimeError("Không phát hiện trang trắng chắc chắn để loại bỏ.")
        output=fitz.open()
        try:
            for index in kept:
                output.insert_pdf(source,from_page=index,to_page=index)
            metadata=source.metadata or {}
            if metadata:
                output.set_metadata(metadata)
            output.save(str(out),garbage=4,deflate=True,clean=True)
        finally:
            output.close()
    finally:
        source.close()
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("PDF đầu ra vượt giới hạn 45 MB.")
    return {"summary":f"Đã giữ {len(kept)} trang và loại {removed} trang trắng; trang có text layer hoặc dấu raster được giữ lại.","output_path":str(out)}


def image_trim_border(p):
    from PIL import Image, ImageChops, ImageStat, ImageOps
    with Image.open(p) as raw:
        _guard_image_dimensions(raw)
        oriented=ImageOps.exif_transpose(raw)
        rgb=oriented.convert("RGB")
        w,h=rgb.size
        patch=max(1,min(5,w//20,h//20))
        corners=[
            rgb.crop((0,0,patch,patch)),rgb.crop((w-patch,0,w,patch)),
            rgb.crop((0,h-patch,patch,h)),rgb.crop((w-patch,h-patch,w,h)),
        ]
        stats=[ImageStat.Stat(item).mean for item in corners]
        background=tuple(round(sum(row[channel] for row in stats)/len(stats)) for channel in range(3))
        backdrop=Image.new("RGB",rgb.size,background)
        delta=ImageChops.difference(rgb,backdrop).convert("L")
        mask=delta.point(lambda value:255 if value>22 else 0)
        bbox=mask.getbbox()
        for item in corners: item.close()
        backdrop.close(); delta.close(); mask.close(); rgb.close()
        if not bbox:
            raise RuntimeError("Ảnh gần như đồng nhất; không tìm thấy nội dung để crop.")
        left,top,right,bottom=bbox
        pad=2
        bbox=(max(0,left-pad),max(0,top-pad),min(w,right+pad),min(h,bottom+pad))
        if bbox==(0,0,w,h):
            raise RuntimeError("Không phát hiện viền thừa đủ lớn để crop.")
        out=p.with_name(p.stem+"-trimmed.png")
        cropped=oriented.crop(bbox)
        cropped.save(out,"PNG",optimize=True)
        cropped.close()
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("Ảnh sau crop vượt giới hạn đầu ra 45 MB.")
    return {"summary":f"Đã cắt viền ảnh từ {w}×{h} xuống {bbox[2]-bbox[0]}×{bbox[3]-bbox[1]} px; giữ 2 px padding quanh nội dung.","output_path":str(out)}


def image_pixelate(p):
    from PIL import Image, ImageOps
    with Image.open(p) as raw:
        _guard_image_dimensions(raw)
        image=ImageOps.exif_transpose(raw)
        width,height=image.size
        reduced=(max(1,round(width/48)),max(1,round(height/48)))
        small=image.resize(reduced,Image.Resampling.BILINEAR)
        pixelated=small.resize((width,height),Image.Resampling.NEAREST)
        out=p.with_name(p.stem+"-pixelated.png")
        pixelated.save(out,"PNG",optimize=True)
        small.close(); pixelated.close()
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("Ảnh pixelate vượt giới hạn đầu ra 45 MB.")
    return {"summary":f"Đã pixel hóa toàn bộ ảnh {width}×{height} bằng lưới xấp xỉ 48×48 ô; kết quả là ảnh mới, không ghi đè file gốc.","output_path":str(out)}


def image_diff(p):
    import io
    from PIL import Image, ImageChops, ImageEnhance, ImageOps
    if not zipfile.is_zipfile(p):
        raise RuntimeError("Gửi ZIP chứa đúng hai ảnh cần so sánh.")
    with zipfile.ZipFile(p) as archive:
        members,total=_safe_zip_members(archive,{".jpg",".jpeg",".png",".webp",".bmp",".tif",".tiff"},max_files=10,max_bytes=50*1024*1024)
        if len(members)!=2:
            raise RuntimeError("ZIP phải chứa đúng hai ảnh.")
        members.sort(key=lambda item:item.filename.casefold())
        images=[]
        for item in members:
            with Image.open(io.BytesIO(archive.read(item))) as raw:
                _guard_image_dimensions(raw)
                images.append(ImageOps.exif_transpose(raw).convert("RGB"))
    try:
        width=max(item.width for item in images); height=max(item.height for item in images)
        canvas_a=Image.new("RGB",(width,height),"white")
        canvas_b=Image.new("RGB",(width,height),"white")
        canvas_a.paste(images[0],(0,0)); canvas_b.paste(images[1],(0,0))
        raw_difference=ImageChops.difference(canvas_a,canvas_b)
        changed=raw_difference.getbbox()
        difference=ImageEnhance.Contrast(raw_difference).enhance(3.0)
        overlay=Image.blend(canvas_a,canvas_b,0.5)
        out=p.with_name(p.stem+"-image-diff.zip")
        diff_path=p.with_name(p.stem+"-difference.png")
        overlay_path=p.with_name(p.stem+"-overlay.png")
        difference.save(diff_path,"PNG",optimize=True)
        overlay.save(overlay_path,"PNG",optimize=True)
        with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=4) as result:
            result.write(diff_path,"difference.png")
            result.write(overlay_path,"overlay.png")
        diff_path.unlink(missing_ok=True); overlay_path.unlink(missing_ok=True)
    finally:
        for item in images: item.close()
        for item in (locals().get("canvas_a"),locals().get("canvas_b"),locals().get("raw_difference"),locals().get("difference"),locals().get("overlay")):
            if item is not None: item.close()
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("ZIP ảnh so sánh vượt giới hạn 45 MB.")
    note="có vùng khác biệt" if changed else "hai ảnh giống nhau sau khi đặt lên cùng canvas"
    return {"summary":f"Đã so sánh {members[0].filename} và {members[1].filename}; {note}. ZIP gồm ảnh difference và overlay ({width}×{height}).","output_path":str(out)}


def audio_stereo_split(p):
    data=ffprobe(p)
    streams=[item for item in data.get("streams",[]) if item.get("codec_type")=="audio"]
    if not streams:
        raise RuntimeError("Không tìm thấy audio stream.")
    if int(streams[0].get("channels") or 0)<2:
        raise RuntimeError("Tệp nguồn không có ít nhất hai kênh audio.")
    duration=float(data.get("format",{}).get("duration") or 0)
    if duration<=0 or duration>1800:
        raise RuntimeError("Tách stereo hỗ trợ audio dài tối đa 30 phút.")
    root=Path(os.environ.get("RUNNER_TEMP","/tmp"))/"nolane-inputs"
    root.mkdir(parents=True,exist_ok=True)
    temp=Path(tempfile.mkdtemp(prefix="stereo-split-",dir=root))
    left=temp/"left.mp3"; right=temp/"right.mp3"
    out=p.with_name(p.stem+"-stereo-split.zip")
    try:
        cmd("ffmpeg",["-y","-i",str(p),"-map","0:a:0","-af","pan=mono|c0=FL","-ac","1","-c:a","libmp3lame","-q:a","2",str(left)],900)
        cmd("ffmpeg",["-y","-i",str(p),"-map","0:a:0","-af","pan=mono|c0=FR","-ac","1","-c:a","libmp3lame","-q:a","2",str(right)],900)
        if not left.is_file() or not right.is_file():
            raise RuntimeError("FFmpeg không tạo đủ hai kênh stereo.")
        with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=4) as archive:
            archive.write(left,"left.mp3"); archive.write(right,"right.mp3")
    finally:
        shutil.rmtree(temp,ignore_errors=True)
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("ZIP stereo vượt giới hạn đầu ra 45 MB.")
    return {"summary":f"Đã tách audio stereo thành kênh Left và Right riêng ({duration:.1f} giây); hai MP3 được đóng gói trong ZIP.","output_path":str(out)}


def audio_metadata_clean(p):
    data=ffprobe(p)
    if not any(item.get("codec_type")=="audio" for item in data.get("streams",[])):
        raise RuntimeError("Không tìm thấy audio stream.")
    if p.suffix.lower() not in {".mp3",".wav",".m4a",".ogg",".flac",".aac"}:
        raise RuntimeError("Định dạng audio này không được hỗ trợ remux.")
    out=p.with_name(p.stem+"-metadata-clean"+p.suffix.lower())
    cmd("ffmpeg",["-y","-i",str(p),"-map","0:a:0","-map_metadata","-1","-map_chapters","-1","-c:a","copy",str(out)],900)
    if not out.is_file() or out.stat().st_size==0:
        raise RuntimeError("FFmpeg không tạo được audio sau khi xóa metadata.")
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("Audio đầu ra vượt giới hạn 45 MB.")
    return {"summary":"Đã remux audio stream đầu tiên và loại metadata/chapter tags; codec không bị re-encode.","output_path":str(out)}


def video_scene_frames(p):
    data=ffprobe(p)
    streams=[item for item in data.get("streams",[]) if item.get("codec_type")=="video"]
    duration=float(data.get("format",{}).get("duration") or 0)
    if not streams or duration<=0 or duration>1800:
        raise RuntimeError("Phát hiện scene hỗ trợ video hợp lệ dài tối đa 30 phút.")
    root=Path(os.environ.get("RUNNER_TEMP","/tmp"))/"nolane-inputs"
    root.mkdir(parents=True,exist_ok=True)
    temp=Path(tempfile.mkdtemp(prefix="scene-frames-",dir=root))
    pattern=temp/"scene-%03d.jpg"
    out=p.with_name(p.stem+"-scene-frames.zip")
    try:
        cmd("ffmpeg",["-y","-i",str(p),"-vf","select='gt(scene,0.35)',scale='min(1280,iw)':-2","-fps_mode","vfr","-frames:v","80","-an","-q:v","3",str(pattern)],900)
        frames=sorted(temp.glob("scene-*.jpg"))
        if not frames:
            raise RuntimeError("Không phát hiện chuyển cảnh vượt ngưỡng 0,35; thử dùng video-frames để lấy mẫu đều.")
        with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=4) as archive:
            for frame in frames:
                archive.write(frame,frame.name)
    finally:
        shutil.rmtree(temp,ignore_errors=True)
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("Scene frames ZIP vượt giới hạn đầu ra 45 MB.")
    return {"summary":f"Đã phát hiện và trích {len(frames)} keyframe chuyển cảnh (ngưỡng 0,35) từ video {duration:.1f} giây.","output_path":str(out)}


def video_metadata_clean(p):
    data=ffprobe(p)
    if not any(item.get("codec_type")=="video" for item in data.get("streams",[])):
        raise RuntimeError("Không tìm thấy video stream.")
    duration=float(data.get("format",{}).get("duration") or 0)
    if duration<=0 or duration>1800:
        raise RuntimeError("Remux metadata hỗ trợ video dài tối đa 30 phút.")
    out=p.with_name(p.stem+"-metadata-clean.mkv")
    cmd("ffmpeg",["-y","-i",str(p),"-map","0","-map_metadata","-1","-map_chapters","-1","-c","copy",str(out)],900)
    if not out.is_file() or out.stat().st_size==0:
        raise RuntimeError("FFmpeg không tạo được video MKV sau khi xóa metadata.")
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("Video đầu ra vượt giới hạn 45 MB.")
    return {"summary":"Đã remux toàn bộ stream sang MKV và loại metadata/chapter tags; video/audio không bị re-encode.","output_path":str(out)}


def json_flatten_csv(p):
    import json
    import csv
    if p.stat().st_size>20*1024*1024:
        raise RuntimeError("JSON flatten giới hạn đầu vào 20 MB.")
    try:
        data=json.loads(p.read_text(encoding="utf-8-sig"))
    except (UnicodeError,ValueError) as exc:
        raise RuntimeError("Tệp JSON không hợp lệ hoặc không phải UTF-8.") from exc
    if isinstance(data,dict):
        records=[data]
    elif isinstance(data,list) and all(isinstance(item,dict) for item in data):
        records=data
    else:
        raise RuntimeError("JSON root phải là object hoặc mảng các object.")
    if len(records)>200000:
        raise RuntimeError("JSON flatten giới hạn 200.000 records.")
    def flatten(value,prefix="",depth=0,target=None):
        if target is None:
            target={}
        if depth>24:
            raise RuntimeError("JSON nesting vượt quá 24 cấp.")
        if isinstance(value,dict) and value:
            for key,item in value.items():
                column=f"{prefix}.{key}" if prefix else str(key)
                flatten(item,column,depth+1,target)
        elif prefix:
            target[prefix]=json.dumps(value,ensure_ascii=False,separators=(",",":")) if isinstance(value,(dict,list)) else value
        return target
    rows=[flatten(record) for record in records]
    columns=[]; seen=set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key); columns.append(key)
                if len(columns)>500:
                    raise RuntimeError("JSON flatten giới hạn 500 cột.")
    if not columns:
        columns=["value"]
    out=p.with_name(p.stem+"-flattened.csv")
    with out.open("w",encoding="utf-8-sig",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=columns,extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("CSV đầu ra vượt giới hạn 45 MB.")
    return {"summary":f"Đã làm phẳng {len(rows):,} record thành {len(columns):,} cột CSV; object con dùng tên cột dạng path, array được serialize an toàn.","output_path":str(out)}


def csv_to_sqlite(p):
    import csv
    import sqlite3
    if p.stat().st_size>20*1024*1024:
        raise RuntimeError("CSV sang SQLite giới hạn đầu vào 20 MB.")
    out=p.with_name(p.stem+".sqlite")
    names=[]; seen=set(); inserted=0
    connection=sqlite3.connect(out)
    try:
        with p.open("r",encoding="utf-8-sig",newline="") as handle:
            sample=handle.read(8192); handle.seek(0)
            try:
                dialect=csv.Sniffer().sniff(sample,delimiters=",;\t|")
            except csv.Error:
                dialect=csv.excel
            reader=csv.reader(handle,dialect)
            headers=next(reader,None)
            if not headers:
                raise RuntimeError("CSV không có header.")
            if len(headers)>500:
                raise RuntimeError("CSV sang SQLite giới hạn 500 cột.")
            for index,raw in enumerate(headers,1):
                base=(raw or "").strip() or f"column_{index}"
                candidate=base; suffix=2
                while candidate.casefold() in seen:
                    candidate=f"{base}_{suffix}"; suffix+=1
                seen.add(candidate.casefold()); names.append(candidate)
            quoted=['"' + name.replace('"','""') + '"' for name in names]
            connection.execute("CREATE TABLE records ("+",".join(name+" TEXT" for name in quoted)+")")
            placeholders=",".join("?" for _ in names)
            statement="INSERT INTO records ("+",".join(quoted)+") VALUES ("+placeholders+")"
            batch=[]
            for row in reader:
                if not row:
                    continue
                if len(row)>len(names):
                    raise RuntimeError("CSV có dòng chứa nhiều giá trị hơn số cột header.")
                row=row+[""]*(len(names)-len(row))
                batch.append(row); inserted+=1
                if inserted>250000:
                    raise RuntimeError("CSV sang SQLite giới hạn 250.000 dòng.")
                if len(batch)>=2000:
                    connection.executemany(statement,batch); batch.clear()
            if batch:
                connection.executemany(statement,batch)
        connection.commit()
    except Exception:
        connection.rollback()
        connection.close()
        out.unlink(missing_ok=True)
        raise
    else:
        connection.close()
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("SQLite đầu ra vượt giới hạn 45 MB.")
    return {"summary":f"Đã nhập {inserted:,} dòng và {len(names):,} cột vào bảng SQLite records; mọi giá trị được lưu TEXT để tránh mất định dạng hoặc độ chính xác.","output_path":str(out)}


def log_insights(p):
    if p.stat().st_size>20*1024*1024:
        raise RuntimeError("Log insights giới hạn đầu vào 20 MB.")
    raw=p.read_text(encoding="utf-8-sig",errors="replace")
    lines=raw.splitlines()
    levels={name:0 for name in ("FATAL","CRITICAL","ERROR","WARN","INFO","DEBUG","TRACE")}
    patterns={}
    level_re=re.compile(r"\b(FATAL|CRITICAL|ERROR|WARN(?:ING)?|INFO|DEBUG|TRACE)\b",re.I)
    timestamp_re=re.compile(r"^\s*\[?\d{4}-\d{2}-\d{2}[T ][^\]\s]+\]?\s*")
    for line in lines:
        match=level_re.search(line)
        if not match:
            continue
        level=match.group(1).upper()
        if level=="WARNING":
            level="WARN"
        levels[level]=levels.get(level,0)+1
        if level in ("FATAL","CRITICAL","ERROR"):
            message=timestamp_re.sub("",line[match.end():])
            message=re.sub(r"\b[0-9a-f]{8}-[0-9a-f-]{27,}\b","<id>",message,flags=re.I)
            message=re.sub(r"\b\d+\b","#",message)
            message=" ".join(message.split())[:180] or "(empty error message)"
            patterns[message]=patterns.get(message,0)+1
    report=[f"File: {p.name}",f"Total lines: {len(lines):,}",f"Total bytes: {p.stat().st_size:,}","","Level counts:"]
    report.extend(f"{name}: {levels[name]:,}" for name in levels)
    report.extend(["","Most repeated error patterns:"])
    ranked=sorted(patterns.items(),key=lambda item:(-item[1],item[0]))[:20]
    report.extend(f"{count:>6,} x {message}" for message,count in ranked)
    if not ranked:
        report.append("No FATAL/CRITICAL/ERROR lines detected.")
    report.append("")
    report.append("Note: this is heuristic log grouping, not a root-cause diagnosis.")
    return tool_text("\n".join(report),"Log insights")


def json_diff(p):
    import difflib
    if not zipfile.is_zipfile(p):
        raise RuntimeError("Gửi ZIP chứa đúng hai tệp JSON cần so sánh.")
    with zipfile.ZipFile(p) as archive:
        members,total=_safe_zip_members(archive,{".json"},max_files=10,max_bytes=20*1024*1024)
        if len(members)!=2:
            raise RuntimeError("ZIP phải chứa đúng hai tệp JSON.")
        members.sort(key=lambda item:item.filename.casefold())
        documents=[]
        for item in members:
            try:
                parsed=json.loads(archive.read(item).decode("utf-8-sig"))
            except (UnicodeError,ValueError) as exc:
                raise RuntimeError("JSON không hợp lệ: "+Path(item.filename).name) from exc
            documents.append(json.dumps(parsed,ensure_ascii=False,indent=2,sort_keys=True).splitlines(keepends=True))
    diff="".join(difflib.unified_diff(documents[0],documents[1],fromfile=members[0].filename,tofile=members[1].filename,n=3))
    if not diff:
        diff="Hai tài liệu JSON giống nhau sau khi chuẩn hóa key order và indentation.\n"
    return tool_text(diff,"JSON diff")



def _read_small_text(p, limit=5*1024*1024):
    if p.stat().st_size > limit:
        raise RuntimeError(f"Text analysis is limited to {limit // (1024*1024)} MB per file.")
    try:
        return p.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise RuntimeError("Tệp phải là văn bản UTF-8 hợp lệ.") from exc


def markdown_outline(p):
    raw=_read_small_text(p)
    lines=raw.splitlines()
    headings=[]
    in_fence=False
    fence_char=None
    index=0
    while index < len(lines):
        line=lines[index]
        fence=re.match(r"^\s{0,3}(\x60{3,}|~{3,})",line)
        if fence:
            marker=fence.group(1)[0]
            if not in_fence:
                in_fence=True; fence_char=marker
            elif marker==fence_char:
                in_fence=False; fence_char=None
            index+=1; continue
        if in_fence:
            index+=1; continue
        match=re.match(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$",line)
        level=0; title=""
        if match:
            level=len(match.group(1)); title=match.group(2).strip()
        elif index+1<len(lines) and line.strip() and re.match(r"^\s{0,3}(=+|-+)\s*$",lines[index+1]):
            level=1 if lines[index+1].strip().startswith("=") else 2
            title=line.strip()
            index+=1
        if level and title:
            slug=unicodedata.normalize("NFKD",title).encode("ascii","ignore").decode().lower()
            slug=re.sub(r"[^a-z0-9\s-]","",slug)
            slug=re.sub(r"[\s-]+","-",slug).strip("-") or "section"
            headings.append((level,title,slug,index+1))
        index+=1
    report=[f"File: {p.name}",f"Headings: {len(headings):,}",""]
    report.extend(("  "*(level-1)+f"- {title}  (#{slug})" for level,title,slug,_ in headings))
    if not headings: report.append("Không tìm thấy heading Markdown ngoài code fence.")
    report.extend(["","Anchor được chuẩn hóa dạng GitHub-style đơn giản; kiểm tra lại với renderer nếu tài liệu dùng custom slug."])
    out=p.with_name(p.stem+"-outline.txt")
    out.write_text("\n".join(report)+"\n",encoding="utf-8")
    return {"summary":f"Đã trích {len(headings)} heading Markdown từ {p.name}.","output_path":str(out)}


def markdown_links(p):
    raw=_read_small_text(p)
    rows=[]
    in_fence=False
    for line_no,line in enumerate(raw.splitlines(),1):
        if re.match(r"^\s{0,3}(\x60{3,}|~{3,})",line):
            in_fence=not in_fence
            continue
        if in_fence: continue
        for match in re.finditer(r"(!?)\[([^\]]{1,300})\]\((<[^>]+>|[^)\s]+)(?:\s+['\"][^)]*['\"])?\)",line):
            target=unescape(match.group(3).strip("<>"))
            if target:
                rows.append((line_no,"image" if match.group(1) else "link",match.group(2),target))
            if len(rows)>=10000: break
        if len(rows)>=10000: break
    out=p.with_name(p.stem+"-links.csv")
    with out.open("w",encoding="utf-8-sig",newline="") as handle:
        writer=csv.writer(handle,lineterminator="\n")
        writer.writerow(["line","kind","label","url"])
        writer.writerows(rows)
    return {"summary":f"Đã trích {len(rows):,} liên kết Markdown (giới hạn 10.000).","output_path":str(out)}


def text_redact(p):
    raw=_read_small_text(p)
    patterns=[
        ("email",re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",re.I)),
        ("GitHub token",re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
        ("AWS access key",re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
        ("OpenAI-style token",re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
        ("Bearer token",re.compile(r"(?i)(\bBearer\s+)[A-Za-z0-9._~+/-]{16,}")),
        ("credential assignment",re.compile(r"(?i)(\b(?:api[_-]?key|access[_-]?token|client[_-]?secret|password|passwd)\b\s*[:=]\s*['\"]?)([A-Za-z0-9_./+=-]{8,})")),
        ("phone-like number",re.compile(r"(?<!\w)(?:\+?\d{1,3}[-. ]?)?(?:\(?\d{2,4}\)?[-. ]?)\d{3,4}[-. ]?\d{3,4}(?!\w)")),
    ]
    counts={}
    result=raw
    for label,pattern in patterns:
        if label=="credential assignment":
            result,n=pattern.subn(lambda match: match.group(1)+"[REDACTED]",result)
        elif label=="Bearer token":
            result,n=pattern.subn(lambda match: match.group(1)+"[REDACTED]",result)
        else:
            result,n=pattern.subn("[REDACTED]",result)
        counts[label]=n
    out=p.with_name(p.stem+"-redacted"+(p.suffix if p.suffix else ".txt"))
    out.write_text(result,encoding="utf-8")
    total=sum(counts.values())
    detail=", ".join(f"{name}: {count}" for name,count in counts.items() if count) or "Không phát hiện mẫu phù hợp."
    return {"summary":f"Đã tạo bản redacted của {p.name}; tổng {total} vùng được thay thế. {detail} Giá trị gốc không được đưa vào báo cáo.","output_path":str(out)}


def text_extract(p):
    import bisect
    import ipaddress
    raw=_read_small_text(p)
    line_starts=[0]
    line_starts.extend(index+1 for index,char in enumerate(raw) if char=="\n")
    found={}
    patterns=[
        ("URL",re.compile(r"https?://[^\s<>()\[\]{}\"']+",re.I)),
        ("email",re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",re.I)),
        ("IPv4",re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")),
    ]
    for kind,pattern in patterns:
        if len(found)>=20000: break
        for match in pattern.finditer(raw):
            value=match.group(0).rstrip(".,;:!?)]}")
            if kind=="IPv4":
                try: ipaddress.IPv4Address(value)
                except ipaddress.AddressValueError: continue
            if kind=="URL" and value.endswith("."): value=value[:-1]
            if not value: continue
            key=(kind,value)
            item=found.setdefault(key,{"count":0,"line":bisect.bisect_right(line_starts,match.start())})
            item["count"]+=1
            if len(found)>=20000: break
    out=p.with_name(p.stem+"-entities.csv")
    with out.open("w",encoding="utf-8-sig",newline="") as handle:
        writer=csv.writer(handle,lineterminator="\n")
        writer.writerow(["kind","value","occurrences","first_line"])
        for (kind,value),item in sorted(found.items(),key=lambda pair:(pair[0][0],pair[0][1].casefold())):
            writer.writerow([kind,value,item["count"],item["line"]])
    return {"summary":f"Đã tìm thấy {len(found):,} giá trị URL/email/IPv4 duy nhất; kết quả kèm số lần và dòng đầu tiên.","output_path":str(out)}


def code_imports(p):
    raw=_read_small_text(p)
    suffix=p.suffix.lower()
    imports=[]
    if suffix in {".py",".pyw"}:
        import ast
        try: tree=ast.parse(raw,filename=p.name)
        except SyntaxError as exc: raise RuntimeError(f"Python syntax error at line {exc.lineno}: {exc.msg}") from exc
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):
                imports.extend((node.lineno,alias.name,"import") for alias in node.names)
            elif isinstance(node,ast.ImportFrom):
                imports.append((node.lineno,("."*node.level)+(node.module or ""), "from"))
    elif suffix==".go":
        imports.extend((i,m.group(1),"import") for i,line in enumerate(raw.splitlines(),1) for m in re.finditer(r'^\s*(?:import\s+)?["\x60]([^"\x60]+)["\x60]',line))
    else:
        patterns=[
            re.compile(r'(?m)^\s*import\s+(?:[^;\n]*?\s+from\s+)?["\']([^"\']+)["\']'),
            re.compile(r'\b(?:require|import)\s*\(\s*["\']([^"\']+)["\']\s*\)'),
        ]
        for pattern in patterns:
            imports.extend((raw.count("\n",0,m.start())+1,m.group(1),"module") for m in pattern.finditer(raw))
    unique=sorted(set(imports),key=lambda item:(item[0],item[1]))
    report=[f"File: {p.name}",f"Static import declarations: {len(unique):,}",""]
    report.extend(f"L{line}: {kind} {name}" for line,name,kind in unique)
    if not unique: report.append("Không nhận diện được import/require.")
    report.extend(["","Phân tích cú pháp/regex tĩnh; không import, tải package hoặc thực thi mã."])
    out=p.with_name(p.stem+"-imports.txt")
    out.write_text("\n".join(report)+"\n",encoding="utf-8")
    return {"summary":f"Đã tìm thấy {len(unique)} khai báo import tĩnh trong {p.name}.","output_path":str(out)}


def code_todos(p):
    raw=_read_small_text(p)
    pattern=re.compile(r"\b(TODO|FIXME|HACK|BUG|XXX)\b(?:\s*[:\-]?\s*(.*))?",re.I)
    rows=[]
    counts={}
    for line_no,line in enumerate(raw.splitlines(),1):
        match=pattern.search(line)
        if match:
            kind=match.group(1).upper()
            counts[kind]=counts.get(kind,0)+1
            rows.append((line_no,kind,match.group(2) or line.strip()))
    report=[f"File: {p.name}",f"Markers: {len(rows):,}",""]
    report.extend(f"L{line_no} [{kind}] {message[:240]}" for line_no,kind,message in rows[:2000])
    if not rows: report.append("Không phát hiện TODO/FIXME/HACK/BUG/XXX.")
    report.extend(["","Counts: "+(", ".join(f"{key}={value}" for key,value in sorted(counts.items())) if counts else "none")])
    out=p.with_name(p.stem+"-todos.txt")
    out.write_text("\n".join(report)+"\n",encoding="utf-8")
    return {"summary":f"Đã quét {len(raw.splitlines()):,} dòng và tìm {len(rows):,} marker công việc.","output_path":str(out)}


def code_secret_scan(p):
    raw=_read_small_text(p)
    patterns=[
        ("GitHub token",re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
        ("AWS access key",re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
        ("OpenAI-style token",re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
        ("Bearer token",re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]{16,}")),
        ("Credential assignment",re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|client[_-]?secret|password|passwd)\b\s*[:=]\s*['\"]?([A-Za-z0-9_./+=-]{8,})")),
        ("Private key header",re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----")),
    ]
    findings=[]
    placeholders=("changeme","example","your_","replace_me","placeholder","dummy","testtoken")
    for line_no,line in enumerate(raw.splitlines(),1):
        for label,pattern in patterns:
            for match in pattern.finditer(line):
                sample=match.group(1) if label=="Credential assignment" and match.lastindex else match.group(0)
                if sample.casefold().startswith(placeholders): continue
                findings.append((line_no,label))
    findings=list(dict.fromkeys(findings))
    report=[f"File: {p.name}",f"Potential findings: {len(findings):,}",""]
    report.extend(f"L{line_no}: {label} [value withheld]" for line_no,label in findings[:1000])
    if not findings: report.append("Không phát hiện mẫu credential phổ biến.")
    report.extend(["","Static pattern scan only; may include false positives and is not a complete security audit. Secret values are never printed."])
    out=p.with_name(p.stem+"-secret-scan.txt")
    out.write_text("\n".join(report)+"\n",encoding="utf-8")
    return {"summary":f"Quét tĩnh hoàn tất: {len(findings)} kết quả tiềm năng; giá trị secret không được xuất ra.","output_path":str(out)}


def log_timeline(p):
    raw=_read_small_text(p)
    pattern=re.compile(r"\b(20\d{2}-\d{2}-\d{2})[T ](\d{2}):(\d{2}):(\d{2})(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?\b")
    days={}; hours={}; parsed=[]
    for line_no,line in enumerate(raw.splitlines(),1):
        match=pattern.search(line)
        if not match: continue
        date=match.group(1); hour=match.group(2)
        days[date]=days.get(date,0)+1
        hours[(date,hour)]=hours.get((date,hour),0)+1
        parsed.append((date,hour,line_no))
    report=[f"File: {p.name}",f"Timestamp lines: {len(parsed):,}",""]
    if parsed:
        report.extend([f"First: {parsed[0][0]} {parsed[0][1]}:xx (line {parsed[0][2]})",
                       f"Last: {parsed[-1][0]} {parsed[-1][1]}:xx (line {parsed[-1][2]})","",
                       "By day:"])
        report.extend(f"{date}: {count:,}" for date,count in sorted(days.items()))
        report.extend(["","Busiest hours:"])
        report.extend(f"{date} {hour}:xx — {count:,} lines" for (date,hour),count in sorted(hours.items(),key=lambda item:(-item[1],item[0]))[:24])
    else:
        report.append("Không tìm thấy timestamp ISO 8601 dạng YYYY-MM-DD HH:MM:SS.")
    report.extend(["","Parser nhận diện ISO date-time cơ bản; không chuẩn hóa timezone giữa các dòng."])
    out=p.with_name(p.stem+"-timeline.txt")
    out.write_text("\n".join(report)+"\n",encoding="utf-8")
    return {"summary":f"Đã phân tích {len(parsed):,} dòng có timestamp ISO và gom theo ngày/giờ.","output_path":str(out)}




def _repo_members(p, read_text=False, hash_all=False):
    """Yield safe ZIP repository members without extracting paths to disk."""
    if not zipfile.is_zipfile(p):
        raise RuntimeError("Repository Intelligence chỉ nhận ZIP hợp lệ.")
    total=0
    with zipfile.ZipFile(p) as archive:
        infos=archive.infolist()
        if len(infos)>500:
            raise RuntimeError("Repository ZIP vượt giới hạn 500 mục.")
        for info in infos:
            if info.is_dir():
                continue
            parts=_safe_archive_parts(info.filename)
            mode=(info.external_attr>>16)&0xFFFF
            file_type=stat.S_IFMT(mode)
            if stat.S_ISLNK(mode) or (file_type and file_type not in (stat.S_IFREG,stat.S_IFDIR)):
                raise RuntimeError("Repository ZIP chứa symlink hoặc special file bị chặn.")
            if info.flag_bits&0x1:
                raise RuntimeError("Repository ZIP mã hóa không được hỗ trợ.")
            if info.file_size<0 or info.file_size>100*1024*1024:
                raise RuntimeError("Repository ZIP có file vượt giới hạn 100 MB.")
            if info.compress_size and info.file_size/max(1,info.compress_size)>200:
                raise RuntimeError("Repository ZIP có compression ratio bất thường.")
            total+=info.file_size
            if total>100*1024*1024:
                raise RuntimeError("Repository ZIP vượt 100 MB dữ liệu giải nén.")
            path="/".join(parts)
            data=None
            digest=None
            should_read=hash_all or (read_text and info.file_size<=2*1024*1024)
            if should_read:
                hasher=hashlib.sha256() if hash_all else None
                chunks=[]
                actual=0
                with archive.open(info,"r") as handle:
                    while True:
                        chunk=handle.read(1024*1024)
                        if not chunk: break
                        actual+=len(chunk)
                        if actual>info.file_size or actual>100*1024*1024:
                            raise RuntimeError("Repository ZIP member có kích thước thực tế vượt metadata.")
                        if hasher: hasher.update(chunk)
                        if read_text: chunks.append(chunk)
                if actual!=info.file_size:
                    raise RuntimeError("Repository ZIP member có kích thước thực tế không khớp metadata.")
                if hasher: digest=hasher.hexdigest()
                if read_text and info.file_size<=2*1024*1024:
                    raw=b"".join(chunks)
                    if b"\x00" not in raw:
                        try: data=raw.decode("utf-8-sig")
                        except UnicodeDecodeError: data=None
            yield {"path":path,"size":info.file_size,"data":data,"sha256":digest}


_REPO_SOURCE_EXTENSIONS={
    ".py",".pyw",".js",".mjs",".cjs",".ts",".tsx",".jsx",".vue",".svelte",
    ".go",".rs",".java",".kt",".kts",".scala",".c",".cc",".cpp",".h",".hpp",
    ".cs",".php",".rb",".swift",".sh",".bash",".zsh",".sql",".css",".scss",
    ".html",".htm",".xml",".json",".yaml",".yml",".toml",".md",".mdx",
}
_REPO_SKIP_PARTS={"node_modules","vendor","dist","build","target",".git",".venv","venv","__pycache__",".next",".cache"}
_REPO_SECRET_PATTERNS=[
    ("GitHub token",re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("AWS access key",re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("OpenAI-style token",re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("Bearer token",re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]{16,}")),
    ("Credential assignment",re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|client[_-]?secret|password|passwd)\b\s*[:=]\s*['\"]?([A-Za-z0-9_./+=-]{8,})")),
    ("Private key header",re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----")),
]


def _repo_text_candidates(p):
    for item in _repo_members(p,read_text=True):
        if item["data"] is None: continue
        path=item["path"]
        if any(part.casefold() in _REPO_SKIP_PARTS for part in path.split("/")): continue
        yield item


def repo_inventory(p):
    from collections import Counter
    extensions=Counter(); folders=Counter(); largest=[]; total=0; files=0
    for item in _repo_members(p):
        path=item["path"]; size=item["size"]
        files+=1; total+=size
        suffix=Path(path).suffix.lower() or "[no extension]"
        extensions[suffix]+=1
        parent=path.rsplit("/",1)[0] if "/" in path else "[root]"
        folders[parent.split("/",1)[0] if parent!="[root]" else parent]+=1
        largest.append((size,path))
    report=[f"Repository archive: {p.name}",f"Files: {files:,}",f"Uncompressed bytes: {total:,}",
            f"Average file size: {total//max(1,files):,} bytes","","File types:"]
    report.extend(f"{ext}: {count:,}" for ext,count in extensions.most_common(30))
    report.extend(["","Top-level folders:"])
    report.extend(f"{name}: {count:,} files" for name,count in folders.most_common(20))
    report.extend(["","Largest files:"])
    report.extend(f"{size:,} bytes · {path}" for size,path in sorted(largest,reverse=True)[:20])
    out=p.with_name(p.stem+"-repo-inventory.txt")
    out.write_text("\n".join(report)+"\n",encoding="utf-8")
    return {"summary":f"Kiểm kê {files:,} file, {len(extensions)} nhóm phần mở rộng, tổng {total:,} bytes giải nén.","output_path":str(out)}


def repo_dependencies(p):
    import json as json_module
    import tomllib
    dependencies=[]
    manifests=[]
    for item in _repo_text_candidates(p):
        path=item["path"]; name=Path(path).name.casefold(); raw=item["data"]
        if name=="package.json":
            try: obj=json_module.loads(raw)
            except Exception: continue
            manifests.append(path)
            for scope in ("dependencies","devDependencies","peerDependencies","optionalDependencies"):
                value=obj.get(scope,{})
                if isinstance(value,dict):
                    dependencies.extend((path,str(pkg),scope,str(version)) for pkg,version in value.items())
        elif name=="requirements.txt":
            manifests.append(path)
            for line in raw.splitlines():
                line=line.strip()
                if not line or line.startswith(("#","-")): continue
                line=line.split(";",1)[0].strip()
                match=re.match(r"([A-Za-z0-9_.-]+)\s*(.*)",line)
                if match: dependencies.append((path,match.group(1),"requirements",match.group(2).strip() or "unspecified"))
        elif name=="pyproject.toml":
            try: obj=tomllib.loads(raw)
            except Exception: continue
            manifests.append(path)
            project=obj.get("project",{})
            if isinstance(project,dict):
                for value in project.get("dependencies",[]) if isinstance(project.get("dependencies",[]),list) else []:
                    match=re.match(r"\s*([A-Za-z0-9_.-]+)\s*(.*)",str(value))
                    if match: dependencies.append((path,match.group(1),"project",match.group(2).strip() or "unspecified"))
                optional=project.get("optional-dependencies",{})
                if isinstance(optional,dict):
                    for scope,items in optional.items():
                        if isinstance(items,list):
                            for value in items:
                                match=re.match(r"\s*([A-Za-z0-9_.-]+)\s*(.*)",str(value))
                                if match: dependencies.append((path,match.group(1),str(scope),match.group(2).strip() or "unspecified"))
        elif name=="cargo.toml":
            try: obj=tomllib.loads(raw)
            except Exception: continue
            manifests.append(path)
            for scope in ("dependencies","dev-dependencies","build-dependencies"):
                values=obj.get(scope,{})
                if isinstance(values,dict):
                    dependencies.extend((path,str(pkg),scope,str(spec.get("version","workspace/path/git") if isinstance(spec,dict) else spec)) for pkg,spec in values.items())
        elif name=="go.mod":
            manifests.append(path); active=False
            for line in raw.splitlines():
                line=line.strip()
                if line.startswith("require ("): active=True; continue
                if active and line==")": active=False; continue
                if line.startswith("require "):
                    parts=line.split()
                    if len(parts)>=3: dependencies.append((path,parts[1],"go",parts[2]))
                elif active and line and not line.startswith("//"):
                    parts=line.split()
                    if len(parts)>=2: dependencies.append((path,parts[0],"go",parts[1]))
        elif name=="composer.json":
            try: obj=json_module.loads(raw)
            except Exception: continue
            manifests.append(path)
            for scope in ("require","require-dev"):
                value=obj.get(scope,{})
                if isinstance(value,dict):
                    dependencies.extend((path,str(pkg),scope,str(version)) for pkg,version in value.items() if pkg!="php")
    report=[f"Repository: {p.name}",f"Dependency manifests: {len(manifests)}",f"Dependencies found: {len(dependencies):,}",""]
    report.extend("Manifest: "+manifest for manifest in manifests[:40])
    report.append("")
    report.extend(f"{manifest} · {scope} · {package} · {version}" for manifest,package,scope,version in dependencies[:1500])
    if not dependencies: report.append("Không tìm thấy dependency trong các manifest được hỗ trợ.")
    report.extend(["","Static manifest parsing only. No dependency installation, network access or code execution."])
    out=p.with_name(p.stem+"-dependencies.txt")
    out.write_text("\n".join(report)+"\n",encoding="utf-8")
    return {"summary":f"Đã đọc {len(manifests)} dependency manifest và trích {len(dependencies)} khai báo dependency.","output_path":str(out)}


def repo_license_report(p):
    import json as json_module
    import tomllib
    evidence=[]; metadata=[]
    patterns=[
        ("MIT",re.compile(r"\bMIT License\b",re.I)),
        ("Apache-2.0",re.compile(r"Apache License\s*Version 2\.0",re.I)),
        ("GPL-family",re.compile(r"GNU GENERAL PUBLIC LICENSE",re.I)),
        ("BSD-family",re.compile(r"BSD [234]-Clause",re.I)),
        ("MPL-2.0",re.compile(r"Mozilla Public License\s*Version 2\.0",re.I)),
        ("Unlicense",re.compile(r"This is free and unencumbered software",re.I)),
    ]
    for item in _repo_text_candidates(p):
        path=item["path"]; name=Path(path).name.casefold(); raw=item["data"]
        if name.startswith(("license","licence","copying","notice")):
            match=next((label for label,pattern in patterns if pattern.search(raw[:12000])), "Unclassified license-like file")
            evidence.append((path,match))
        if name=="package.json":
            try:
                value=json_module.loads(raw).get("license")
                if value: metadata.append((path,str(value)[:180]))
            except Exception: pass
        elif name=="pyproject.toml":
            try:
                value=tomllib.loads(raw).get("project",{}).get("license")
                if value: metadata.append((path,str(value)[:180]))
            except Exception: pass
        elif name=="cargo.toml":
            try:
                value=tomllib.loads(raw).get("package",{}).get("license")
                if value: metadata.append((path,str(value)[:180]))
            except Exception: pass
    report=[f"Repository: {p.name}","License evidence (not legal advice):"]
    report.extend(f"- {path}: {label}" for path,label in evidence)
    report.append("")
    report.append("Manifest declarations:")
    report.extend(f"- {path}: {value}" for path,value in metadata)
    if not evidence and not metadata: report.append("Không phát hiện license file hoặc metadata license trong các vị trí đã kiểm tra.")
    report.extend(["","Automated text-pattern detection only. This report does not establish licensing compatibility or grant reuse rights. Review the complete license and third-party notices manually."])
    out=p.with_name(p.stem+"-licenses.txt")
    out.write_text("\n".join(report)+"\n",encoding="utf-8")
    return {"summary":f"Đã kiểm tra {len(evidence)} tệp license-like và {len(metadata)} khai báo metadata license.","output_path":str(out)}


def repo_secret_scan(p):
    findings=[]; scanned=0
    for item in _repo_text_candidates(p):
        path=item["path"]
        if Path(path).suffix.lower() not in _REPO_SOURCE_EXTENSIONS and Path(path).name not in {".env","Dockerfile"}: continue
        scanned+=1
        for line_no,line in enumerate(item["data"].splitlines(),1):
            for label,pattern in _REPO_SECRET_PATTERNS:
                for match in pattern.finditer(line):
                    sample=match.group(1) if label=="Credential assignment" and match.lastindex else match.group(0)
                    if sample.casefold().startswith(("changeme","example","your_","replace_me","placeholder","dummy","testtoken")): continue
                    findings.append((path,line_no,label))
                    if len(findings)>=1000: break
                if len(findings)>=1000: break
            if len(findings)>=1000: break
        if len(findings)>=1000: break
    report=[f"Repository: {p.name}",f"Files scanned: {scanned:,}",f"Potential findings: {len(findings):,}",""]
    report.extend(f"{path}:L{line_no} · {label} · [value withheld]" for path,line_no,label in findings)
    if not findings: report.append("Không phát hiện mẫu credential phổ biến trong các file văn bản được quét.")
    report.extend(["","Static pattern scan only; false positives and false negatives are possible. Secret values are never printed."])
    out=p.with_name(p.stem+"-repo-secret-scan.txt")
    out.write_text("\n".join(report)+"\n",encoding="utf-8")
    return {"summary":f"Đã quét {scanned} file văn bản trong repository; {len(findings)} mẫu secret tiềm năng, không xuất giá trị.","output_path":str(out)}


def repo_todo_scan(p):
    pattern=re.compile(r"\b(TODO|FIXME|HACK|BUG|XXX)\b(?:\s*[:\-]?\s*(.*))?",re.I)
    rows=[]; scanned=0
    for item in _repo_text_candidates(p):
        path=item["path"]
        if Path(path).suffix.lower() not in _REPO_SOURCE_EXTENSIONS: continue
        scanned+=1
        for line_no,line in enumerate(item["data"].splitlines(),1):
            match=pattern.search(line)
            if match:
                rows.append((path,line_no,match.group(1).upper(),(match.group(2) or line.strip())[:180]))
                if len(rows)>=2000: break
        if len(rows)>=2000: break
    report=[f"Repository: {p.name}",f"Source files scanned: {scanned:,}",f"Markers: {len(rows):,}",""]
    report.extend(f"{path}:L{line_no} [{kind}] {message}" for path,line_no,kind,message in rows)
    if not rows: report.append("Không tìm thấy TODO/FIXME/HACK/BUG/XXX.")
    out=p.with_name(p.stem+"-repo-todos.txt")
    out.write_text("\n".join(report)+"\n",encoding="utf-8")
    return {"summary":f"Đã quét {scanned} source files và tìm {len(rows)} marker công việc.","output_path":str(out)}


def repo_code_stats(p):
    from collections import Counter
    stats={}
    total_lines=0; total_bytes=0; scanned=0; skipped=0
    for item in _repo_text_candidates(p):
        path=item["path"]; ext=Path(path).suffix.lower()
        if ext not in _REPO_SOURCE_EXTENSIONS: continue
        if item["data"] is None: skipped+=1; continue
        lines=item["data"].splitlines()
        bucket=stats.setdefault(ext,{"files":0,"lines":0,"blank":0,"nonblank":0,"bytes":0})
        bucket["files"]+=1; bucket["lines"]+=len(lines)
        bucket["blank"]+=sum(1 for line in lines if not line.strip())
        bucket["nonblank"]+=sum(1 for line in lines if line.strip())
        bucket["bytes"]+=item["size"]
        total_lines+=len(lines); total_bytes+=item["size"]; scanned+=1
    report=[f"Repository: {p.name}",f"Source files scanned: {scanned:,}",f"Skipped or unsupported text candidates: {skipped:,}",f"Total source bytes: {total_bytes:,}",f"Total lines: {total_lines:,}",""]
    report.extend(f"{ext}: {v['files']} files · {v['lines']:,} lines · {v['blank']:,} blank · {v['bytes']:,} bytes" for ext,v in sorted(stats.items(),key=lambda pair:-pair[1]["lines"]))
    if not stats: report.append("Không tìm thấy source file có phần mở rộng được hỗ trợ.")
    report.extend(["","Line counts are lexical; they do not distinguish comments from executable statements. Vendor/build directories are excluded."])
    out=p.with_name(p.stem+"-repo-code-stats.txt")
    out.write_text("\n".join(report)+"\n",encoding="utf-8")
    return {"summary":f"Thống kê {scanned} source files, {total_lines:,} dòng và {total_bytes:,} bytes mã nguồn.","output_path":str(out)}


def repo_config_audit(p):
    paths={item["path"].casefold() for item in _repo_members(p)}
    names={Path(path).name.casefold() for path in paths}
    checks=[
        ("README / project documentation",any(Path(path).name.casefold().startswith("readme") for path in paths)),
        ("License / copying notice",any(Path(path).name.casefold().startswith(("license","licence","copying")) for path in paths)),
        ("Package manifest",bool(names.intersection({"package.json","pyproject.toml","requirements.txt","cargo.toml","go.mod","composer.json"}))),
        ("Dependency lockfile",bool(names.intersection({"package-lock.json","pnpm-lock.yaml","yarn.lock","poetry.lock","uv.lock","cargo.lock","go.sum","composer.lock"}))),
        ("Automated tests",any("/test" in path or "/tests/" in path or Path(path).name.startswith(("test_","test.")) for path in paths)),
        ("CI workflow",any(path.startswith(".github/workflows/") or "/.github/workflows/" in path for path in paths)),
        ("Container build",any(Path(path).name.casefold() in {"dockerfile","docker-compose.yml","compose.yaml","compose.yml"} for path in paths)),
        ("Lint / static-analysis config",bool(names.intersection({".eslintrc",".eslintrc.json","eslint.config.js","ruff.toml",".pre-commit-config.yaml","mypy.ini","tsconfig.json"}))),
        ("Environment example",any(Path(path).name.casefold() in {".env.example",".env.sample","example.env"} for path in paths)),
    ]
    report=[f"Repository: {p.name}","Configuration inventory (presence only):",""]
    report.extend(f"{'PRESENT' if present else 'NOT FOUND'} · {label}" for label,present in checks)
    report.extend(["",f"Present: {sum(1 for _,present in checks if present)}/{len(checks)}",
                   "This is a presence check, not a security, quality or CI correctness audit."])
    out=p.with_name(p.stem+"-repo-config-audit.txt")
    out.write_text("\n".join(report)+"\n",encoding="utf-8")
    return {"summary":f"Đã kiểm kê {len(checks)} nhóm cấu hình; có {sum(1 for _,present in checks if present)} nhóm hiện diện.","output_path":str(out)}


def repo_duplicates(p):
    from collections import defaultdict
    groups=defaultdict(list); total=0; files=0
    for item in _repo_members(p,hash_all=True):
        files+=1; total+=item["size"]
        groups[(item["sha256"],item["size"])].append(item["path"])
    duplicate_groups=[(digest,size,paths) for (digest,size),paths in groups.items() if len(paths)>1]
    out=p.with_name(p.stem+"-repo-duplicates.csv")
    with out.open("w",encoding="utf-8-sig",newline="") as handle:
        writer=csv.writer(handle,lineterminator="\n")
        writer.writerow(["sha256","size_bytes","duplicate_count","paths"])
        for digest,size,paths in sorted(duplicate_groups,key=lambda item:(-len(item[2]),item[2][0])):
            writer.writerow([digest,size,len(paths)," | ".join(paths)])
    duplicate_files=sum(len(paths) for _,_,paths in duplicate_groups)
    return {"summary":f"Đã hash {files} file ({total:,} bytes); tìm thấy {len(duplicate_groups)} nhóm trùng với {duplicate_files} file.","output_path":str(out)}


def _github_identity(owner, repo):
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})", str(owner or "")):
        raise RuntimeError("GitHub owner is invalid.")
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", str(repo or "")):
        raise RuntimeError("GitHub repository name is invalid.")
    return "https://api.github.com/repos/" + owner + "/" + repo


def _github_ref(value):
    return (isinstance(value, str) and 1 <= len(value) <= 255 and
            not value.startswith(("-", "/")) and not value.endswith("/") and
            ".." not in value and "\\" not in value and
            not re.search(r"[\x00-\x20\x7f~^:?*\[\]]", value) and
            all(part not in ("", ".", "..") for part in value.split("/")))


class _GitHubArchiveRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urllib.parse.urlparse(newurl)
        if parsed.scheme != "https" or parsed.hostname != "codeload.github.com" or parsed.port:
            raise RuntimeError("GitHub archive redirect left the trusted codeload.github.com host.")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def download_github_source(job, output_path_file):
    source = job.get("githubSource")
    if not isinstance(source, dict):
        raise RuntimeError("Missing GitHub repository source.")
    owner = source.get("owner")
    repo = source.get("repo")
    requested_ref = source.get("ref", "")
    api_root = _github_identity(owner, repo)
    if requested_ref and not _github_ref(requested_ref):
        raise RuntimeError("GitHub ref is invalid.")
    has_base = "compareBase" in source
    has_head = "compareHead" in source
    if has_base != has_head or (has_base and (
        not _github_ref(source.get("compareBase")) or
        not _github_ref(source.get("compareHead")) or
        source.get("compareBase") == source.get("compareHead")
    )):
        raise RuntimeError("GitHub compare refs are invalid.")

    repository = api_json(api_root)
    if not isinstance(repository, dict) or repository.get("private") is True:
        raise RuntimeError("Chỉ hỗ trợ repository GitHub công khai.")
    ref = requested_ref or repository.get("default_branch")
    if not _github_ref(ref):
        raise RuntimeError("Không xác định được default branch hoặc ref hợp lệ.")

    archive_url = api_root + "/zipball/" + urllib.parse.quote(ref, safe="")
    request = urllib.request.Request(archive_url, headers={
        "accept": "application/vnd.github+json",
        "user-agent": "Nolane-Repository-Intelligence/1.0",
        "x-github-api-version": "2022-11-28",
    })
    root = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "nolane-inputs"
    root.mkdir(parents=True, exist_ok=True)
    archive_path = root / "github-repository-source.zip"
    opener = urllib.request.build_opener(_GitHubArchiveRedirect())
    try:
        with opener.open(request, timeout=90) as response:
            final = urllib.parse.urlparse(response.geturl())
            if final.scheme != "https" or final.hostname != "codeload.github.com" or final.port:
                raise RuntimeError("GitHub archive download resolved to an untrusted host.")
            declared = response.headers.get("Content-Length")
            if declared and int(declared) > 100 * 1024 * 1024:
                raise RuntimeError("GitHub repository archive exceeds the 100 MB download limit.")
            written = 0
            with archive_path.open("wb") as output:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    written += len(chunk)
                    if written > 100 * 1024 * 1024:
                        raise RuntimeError("GitHub repository archive exceeded the 100 MB download limit.")
                    output.write(chunk)
    except urllib.error.HTTPError as exc:
        detail = exc.read(1000).decode("utf-8", "replace")
        if exc.code == 404:
            raise RuntimeError("Không tìm thấy repository/ref công khai; repository private hoặc ref không tồn tại cũng có thể trả về 404.") from exc
        raise RuntimeError(f"GitHub archive HTTP {exc.code}: {detail}") from exc
    if written <= 0 or not zipfile.is_zipfile(archive_path):
        archive_path.unlink(missing_ok=True)
        raise RuntimeError("GitHub không trả về một ZIP snapshot hợp lệ.")

    try:
        commits = api_json(api_root + "/commits?per_page=20&sha=" + urllib.parse.quote(ref, safe=""))
        if not isinstance(commits, list):
            commits = []
    except Exception as exc:
        commits = []
        commits_error = str(exc)[:180]
    else:
        commits_error = ""

    metadata = {
        "repository": {
            "full_name": repository.get("full_name") or owner + "/" + repo,
            "html_url": repository.get("html_url") or "https://github.com/" + owner + "/" + repo,
            "description": (repository.get("description") or "")[:500],
            "default_branch": repository.get("default_branch") or "",
            "analyzed_ref": ref,
            "created_at": repository.get("created_at"),
            "updated_at": repository.get("updated_at"),
            "pushed_at": repository.get("pushed_at"),
            "stars": repository.get("stargazers_count"),
            "forks": repository.get("forks_count"),
            "open_issues": repository.get("open_issues_count"),
            "language": repository.get("language"),
            "license": (repository.get("license") or {}).get("spdx_id") if isinstance(repository.get("license"), dict) else None,
            "archived": repository.get("archived"),
            "size_kb": repository.get("size"),
        },
        "commits": [],
        "commits_error": commits_error,
        "compare": None,
        "archive_bytes": written,
    }
    for item in commits[:20]:
        if not isinstance(item, dict):
            continue
        details = item.get("commit") or {}
        author = details.get("author") or {}
        metadata["commits"].append({
            "sha": str(item.get("sha") or "")[:40],
            "date": author.get("date"),
            "author": str(author.get("name") or "")[:80],
            "message": str(details.get("message") or "").splitlines()[0][:220],
            "url": str(item.get("html_url") or "")[:300],
        })

    if has_base:
        base = source["compareBase"]
        head = source["compareHead"]
        compare_url = api_root + "/compare/" + urllib.parse.quote(base, safe="") + "..." + urllib.parse.quote(head, safe="")
        try:
            compared = api_json(compare_url)
            files = []
            for item in (compared.get("files") or [])[:100]:
                if not isinstance(item, dict):
                    continue
                files.append({
                    "filename": str(item.get("filename") or "")[:300],
                    "status": str(item.get("status") or "")[:30],
                    "additions": int(item.get("additions") or 0),
                    "deletions": int(item.get("deletions") or 0),
                    "changes": int(item.get("changes") or 0),
                })
            metadata["compare"] = {
                "base": base, "head": head, "status": compared.get("status"),
                "ahead_by": compared.get("ahead_by"), "behind_by": compared.get("behind_by"),
                "total_commits": compared.get("total_commits"), "files": files,
                "files_truncated": len(compared.get("files") or []) > 100, "error": None,
            }
        except Exception as exc:
            metadata["compare"] = {"base": base, "head": head, "error": str(exc)[:250], "files": []}

    (root / "github-source-metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    Path(output_path_file).write_text(str(archive_path), encoding="utf-8")
    print(f"Downloaded public GitHub snapshot: {owner}/{repo}@{ref} ({written:,} bytes)")


def _repo_architecture_graph(p):
    import ast
    paths = set()
    text_files = {}
    for item in _repo_text_candidates(p):
        path = item["path"]
        if item.get("data") is not None and Path(path).suffix.lower() in _REPO_SOURCE_EXTENSIONS:
            paths.add(path)
            text_files[path] = item["data"]
    edges = set()
    parse_failures = 0
    js_pattern = re.compile(r"""(?:\bfrom\s*|\bimport\s*|\brequire\s*\(\s*|\bimport\s*\(\s*)["']([^"']+)["']""")

    def resolve_js(source, specifier):
        if not specifier.startswith(("./", "../")):
            return None
        target = posixpath.normpath(posixpath.join(posixpath.dirname(source), specifier))
        if target.startswith("../") or target in ("..", ".") or target.startswith("/"):
            return None
        candidates = [
            target, target + ".js", target + ".jsx", target + ".ts", target + ".tsx",
            target + ".mjs", target + ".cjs", target + ".vue", target + ".svelte",
            target + ".py", target + "/index.js", target + "/index.ts",
            target + "/index.tsx", target + "/__init__.py",
        ]
        return next((candidate for candidate in candidates if candidate in paths), None)

    def resolve_python_module(module):
        base = module.replace(".", "/")
        candidates = (base + ".py", base + "/__init__.py")
        for candidate in candidates:
            exact = next((path for path in sorted(paths) if path == candidate or path.endswith("/" + candidate)), None)
            if exact:
                return exact
        return None

    for source, raw in text_files.items():
        suffix = Path(source).suffix.lower()
        if suffix in (".py", ".pyw"):
            try:
                tree = ast.parse(raw[:2 * 1024 * 1024], filename=source)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            match = resolve_python_module(alias.name)
                            if match:
                                edges.add((source, match))
                    elif isinstance(node, ast.ImportFrom):
                        if node.level:
                            parent = posixpath.dirname(source)
                            base = posixpath.normpath(posixpath.join(parent, *([".."] * (node.level - 1)), (node.module or "").replace(".", "/")))
                            candidates = (base + ".py", base + "/__init__.py")
                            match = next((candidate for candidate in candidates if candidate in paths), None)
                        else:
                            match = resolve_python_module(node.module or "")
                        if match:
                            edges.add((source, match))
            except (SyntaxError, ValueError, RecursionError):
                parse_failures += 1
        elif suffix in (".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".vue", ".svelte"):
            for match in js_pattern.finditer(raw[:2 * 1024 * 1024]):
                target = resolve_js(source, match.group(1))
                if target:
                    edges.add((source, target))

    indegree = {path: 0 for path in paths}
    outdegree = {path: 0 for path in paths}
    for source, target in edges:
        outdegree[source] = outdegree.get(source, 0) + 1
        indegree[target] = indegree.get(target, 0) + 1
    nodes = [
        {"path": path, "imports": outdegree.get(path, 0), "imported_by": indegree.get(path, 0)}
        for path in sorted(paths, key=lambda value: (-indegree.get(value, 0), -outdegree.get(value, 0), value))[:500]
    ]
    return {
        "schema_version": 1,
        "method": "Static import extraction; local imports only; no code execution.",
        "source_files_considered": len(text_files),
        "python_parse_failures": parse_failures,
        "nodes": nodes,
        "edges": [{"from": source, "to": target} for source, target in sorted(edges)[:5000]],
        "edges_truncated": len(edges) > 5000,
    }



def _repo_report_text(p, suffix, title, lines, summary):
    out=p.with_name(p.stem+suffix)
    out.write_text("\n".join([title, "="*min(len(title),100), ""]+list(lines)).rstrip()+"\n",encoding="utf-8")
    return {"summary":str(summary)[:500],"output_path":str(out)}


def _repo_is_test_path(path):
    name=Path(path).name.casefold()
    parts={part.casefold() for part in path.split("/")}
    return bool(parts & {"test","tests","spec","specs","__tests__"}) or name.startswith(("test_","tests_")) or ".test." in name or ".spec." in name or name.endswith(("_test.go","_spec.rb")) or (name.startswith("test") and Path(name).suffix in {".java",".kt",".cs"})


def repo_test_map(p):
    source=[]; tests=[]
    for item in _repo_text_candidates(p):
        path=item["path"]
        if item["data"] is None or Path(path).suffix.lower() not in _REPO_SOURCE_EXTENSIONS: continue
        (tests if _repo_is_test_path(path) else source).append(path)
    test_basenames={}
    for path in tests:
        stem=Path(path).stem.casefold()
        for prefix in ("test_","tests_"):
            if stem.startswith(prefix): stem=stem[len(prefix):]
        if stem.endswith((".test",".spec")): stem=stem.rsplit(".",1)[0]
        if stem.endswith(("_test","_spec")): stem=stem.rsplit("_",1)[0]
        test_basenames.setdefault(stem,set()).add(path)
    matched=[]; unmatched=[]
    for path in source:
        candidates=set(test_basenames.get(Path(path).stem.casefold(),set()))
        if candidates: matched.append((path,sorted(candidates)))
        else: unmatched.append(path)
    source_stems={Path(path).stem.casefold() for path in source}
    orphan=[path for stem,paths in test_basenames.items() if stem not in source_stems for path in paths]
    lines=[f"Source files: {len(source):,}",f"Test files: {len(tests):,}",f"Source files with filename-based test candidates: {len(matched):,}",f"Source files without a filename-based test candidate: {len(unmatched):,}",f"Potential orphan test files: {len(orphan):,}","","Matched source files (filename/path heuristic):"]
    for path,candidates in matched[:250]:
        lines.append("- "+path)
        lines.extend("    candidate: "+candidate for candidate in candidates[:5])
    lines.extend(["","Source files with no matching test filename:"])
    lines.extend("- "+path for path in unmatched[:250])
    lines.extend(["","Potential orphan test files:"])
    lines.extend("- "+path for path in sorted(set(orphan))[:150])
    lines.append("Filename heuristics only; this is not line coverage, test execution or proof of behavioral coverage.")
    return _repo_report_text(p,"-repo-test-map.txt","Repository test map",lines,f"Mapped {len(source)} source files and {len(tests)} likely test files; candidate tests found for {len(matched)} source files.")


def repo_test_quality(p):
    import collections
    test_items=[item for item in _repo_text_candidates(p) if _repo_is_test_path(item["path"])]
    declaration_patterns=[
        ("Python test",re.compile(r"^\s*(?:async\s+)?def\s+test_[A-Za-z0-9_]+\s*\(",re.M)),
        ("Python test class",re.compile(r"^\s*class\s+Test[A-Za-z0-9_]*\b",re.M)),
        ("JavaScript/TypeScript test",re.compile(r"\b(?:it|test)\s*(?:\.\s*(?:skip|only|todo)\s*)?\(",re.I)),
        ("Suite declaration",re.compile(r"\bdescribe\s*(?:\.\s*(?:skip|only)\s*)?\(",re.I)),
        ("Go test",re.compile(r"^\s*func\s+Test[A-Z]\w*\s*\(",re.M)),
        ("Java/JUnit test",re.compile(r"@\s*(?:Test|ParameterizedTest|RepeatedTest)\b")),
    ]
    assertion_patterns=[re.compile(r"\bassert(?:Equal|True|False|Raises|AlmostEqual|In|NotIn|IsNone|IsNotNone)?\s*\("),re.compile(r"\bexpect\s*\("),re.compile(r"\.to(?:Be|Equal|Contain|Throw|Match|HaveBeenCalled)\s*\("),re.compile(r"\bassert\s+")]
    totals=collections.Counter(); findings=[]; declarations=[]
    for item in test_items:
        path=item["path"]; raw=item["data"] or ""
        counts={label:len(pattern.findall(raw)) for label,pattern in declaration_patterns}
        decl=sum(counts.values()); assertions=sum(len(pattern.findall(raw)) for pattern in assertion_patterns)
        totals["files"]+=1; totals["declarations"]+=decl; totals["assertions"]+=assertions
        for label,count in counts.items(): totals[label]+=count
        if decl==0: findings.append(("WARN",path,"No recognizable test declaration found; framework may be unsupported."))
        if decl>0 and assertions==0: findings.append(("WARN",path,"Test declarations detected but no common assertion pattern was found."))
        if re.search(r"\b(?:it|test)\s*\.\s*only\s*\(",raw): findings.append(("HIGH",path,"Focused-only test marker (.only) may exclude other tests."))
        if re.search(r"\b(?:it|test)\s*\.\s*skip\s*\(",raw) or re.search(r"@Disabled\b|pytest\.mark\.skip|unittest\.skip",raw): findings.append(("INFO",path,"Skipped test marker detected; verify it is intentional."))
        if re.search(r"\b(?:except\s+Exception|catch\s*\(\s*(?:Exception|Throwable|Error)\b)",raw): findings.append(("INFO",path,"Broad exception handling appears in a test file; check whether failures are swallowed."))
        for match in list(re.finditer(r"\b(?:TODO|FIXME|XXX)\b",raw,re.I))[:5]:
            findings.append(("INFO",path+":"+str(raw.count("\n",0,match.start())+1),"Unresolved test TODO marker."))
        declarations.append((decl,assertions,path))
    if not test_items: findings.append(("WARN","[repository]","No likely test files detected by supported naming heuristics."))
    lines=[f"Likely test files: {totals['files']:,}",f"Recognizable test declarations: {totals['declarations']:,}",f"Common assertion-pattern matches: {totals['assertions']:,}","","Declaration counts by pattern:"]
    lines.extend(f"- {label}: {totals[label]:,}" for label,_ in declaration_patterns)
    lines.extend(["","Files with the most recognizable test declarations:"])
    lines.extend(f"- {path}: declarations={decl}, assertion-pattern matches={assertions}" for decl,assertions,path in sorted(declarations,reverse=True)[:40])
    lines.extend(["","Review findings:"])
    lines.extend(f"- {severity} · {path} · {message}" for severity,path,message in findings[:400])
    lines.append("Regex heuristics only: not a test run, mutation score, branch coverage or assertion-quality score; matches may occur in comments or strings.")
    return _repo_report_text(p,"-repo-test-quality.txt","Repository test quality signals",lines,f"Inspected {len(test_items)} likely test files: {totals['declarations']} recognizable declarations and {len(findings)} review signals.")


def repo_complexity_report(p):
    import ast
    branch_nodes=(ast.If,ast.For,ast.AsyncFor,ast.While,ast.ExceptHandler,ast.IfExp,ast.Match)
    def function_metrics(node):
        decisions=1; depth=0
        stack=[(child,1) for child in getattr(node,"body",[])]
        while stack:
            current,level=stack.pop()
            if isinstance(current,(ast.FunctionDef,ast.AsyncFunctionDef,ast.Lambda,ast.ClassDef)): continue
            if isinstance(current,branch_nodes): decisions+=1
            elif isinstance(current,ast.BoolOp): decisions+=max(0,len(current.values)-1)
            if isinstance(current,(ast.If,ast.For,ast.AsyncFor,ast.While,ast.Try,ast.With)): depth=max(depth,level)
            stack.extend((child,level+1) for child in ast.iter_child_nodes(current))
        return decisions,depth
    rows=[]; totals={"files":0,"lines":0,"python_functions":0,"parse_failures":0,"branch_signals":0,"long_lines":0}
    js_patterns=[re.compile(r"\bif\s*\("),re.compile(r"\b(?:for|while)\s*\("),re.compile(r"\bcatch\s*\("),re.compile(r"\?\s*[^?:\n]+\s*:"),re.compile(r"&&|\|\|")]
    for item in _repo_text_candidates(p):
        path=item["path"]; raw=item["data"] or ""; suffix=Path(path).suffix.lower()
        if suffix not in _REPO_SOURCE_EXTENSIONS: continue
        row_lines=raw.splitlines(); totals["files"]+=1; totals["lines"]+=len(row_lines); totals["long_lines"]+=sum(1 for line in row_lines if len(line)>120)
        if suffix in {".py",".pyw"}:
            try:
                tree=ast.parse(raw)
                for node in ast.walk(tree):
                    if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
                        complexity,depth=function_metrics(node); end=getattr(node,"end_lineno",node.lineno)
                        rows.append((complexity,max(1,end-node.lineno+1),path,node.name,node.lineno,depth)); totals["python_functions"]+=1
            except (SyntaxError,ValueError): totals["parse_failures"]+=1
        elif suffix in {".js",".mjs",".cjs",".ts",".tsx",".jsx",".vue",".svelte"}:
            signals=sum(len(pattern.findall(raw)) for pattern in js_patterns); totals["branch_signals"]+=signals
            rows.append((signals,len(row_lines),path,"[file-level JS/TS branch signals]",1,0))
    lines=[f"Source files measured: {totals['files']:,}",f"Source lines: {totals['lines']:,}",f"Python functions/methods inspected: {totals['python_functions']:,}",f"Python parse failures: {totals['parse_failures']:,}",f"JS/TS branch-pattern matches (heuristic): {totals['branch_signals']:,}",f"Lines longer than 120 characters: {totals['long_lines']:,}","","Highest Python decision-count functions (AST approximation):"]
    lines.extend(f"- {path}:{line} · {name} · decisions={complexity} · LOC={loc} · nested depth signal={depth}" for complexity,loc,path,name,line,depth in sorted([row for row in rows if not row[3].startswith("[")],reverse=True)[:100])
    lines.extend(["","Highest JS/TS file-level branch signals (not cyclomatic complexity):"])
    lines.extend(f"- {path} · {complexity} regex signals · {loc} lines" for complexity,loc,path,name,line,depth in sorted([row for row in rows if row[3].startswith("[")],reverse=True)[:60])
    lines.append("Python values are lightweight AST decision counts; JS/TS values are file-level regex matches. Neither is a formal complexity or maintainability score.")
    return _repo_report_text(p,"-repo-complexity.txt","Repository complexity signals",lines,f"Measured {totals['files']} source files, {totals['python_functions']} Python functions and {totals['branch_signals']} JS/TS branch-pattern signals.")


def repo_api_surface(p):
    patterns=[
        re.compile(r"^\s*@(?:\w+\.)?(?:app|router|api|bp)\.(?:route|get|post|put|patch|delete|options|head)\s*\(([^)]*)\)",re.I),
        re.compile(r"\b(?:app|router|server|fastify)\s*\.\s*(get|post|put|patch|delete|options|head)\s*\(\s*['\"\x60]([^'\"\x60]+)",re.I),
        re.compile(r"^\s*export\s+(?:async\s+)?function\s+(GET|POST|PUT|PATCH|DELETE|OPTIONS|HEAD)\s*\(",re.M),
        re.compile(r"^\s*@(GetMapping|PostMapping|PutMapping|PatchMapping|DeleteMapping|RequestMapping)\s*(?:\(([^)]*)\))?",re.I),
        re.compile(r"\b(?:http\.)?HandleFunc\s*\(\s*['\"\x60]([^'\"\x60]+)['\"\x60]"),
    ]
    entries=[]; scanned=0
    for item in _repo_text_candidates(p):
        path=item["path"]; raw=item["data"] or ""; suffix=Path(path).suffix.lower()
        if suffix not in {".py",".pyw",".js",".mjs",".cjs",".ts",".tsx",".jsx",".java",".go"}: continue
        scanned+=1
        for line_no,line in enumerate(raw.splitlines(),1):
            if suffix in {".py",".pyw"}:
                match=patterns[0].search(line)
                if match: entries.append((path,line_no,"Python route decorator",match.group(1).strip()[:150]))
            elif suffix==".java":
                match=patterns[3].search(line)
                if match: entries.append((path,line_no,"Java route annotation",match.group(0).strip()[:150]))
            elif suffix==".go":
                match=patterns[4].search(line)
                if match: entries.append((path,line_no,"Go HTTP handler",match.group(1)[:150]))
            else:
                match=patterns[1].search(line)
                if match: entries.append((path,line_no,"JS/TS route call",match.group(1).upper()+" "+match.group(2)[:120]))
                match=patterns[2].search(line)
                if match: entries.append((path,line_no,"Next.js route export",match.group(1).upper()))
    entries.sort(key=lambda row:(row[0],row[1],row[2]))
    lines=[f"Source files scanned: {scanned:,}",f"Route/handler clues: {len(entries):,}","","Discovered API surface candidates:"]
    lines.extend(f"- {path}:{line} · {kind} · {detail}" for path,line,kind,detail in entries[:600])
    lines.append("Static route candidates only: dynamic prefixes, aliases, router composition, middleware rewrites, RPC/GraphQL and generated routes may be missed. This is not a complete OpenAPI specification.")
    return _repo_report_text(p,"-repo-api-surface.txt","Repository API surface candidates",lines,f"Scanned {scanned} source files and found {len(entries)} API route/handler candidates.")


def repo_docs_audit(p):
    import posixpath
    from urllib.parse import unquote,urlsplit
    members=list(_repo_members(p)); paths={item["path"] for item in members}
    markdown=[item for item in _repo_text_candidates(p) if Path(item["path"]).suffix.lower() in {".md",".mdx"}]
    required=["README.md","CONTRIBUTING.md","SECURITY.md","CODE_OF_CONDUCT.md","CHANGELOG.md","LICENSE"]
    root_names={Path(path).name.casefold() for path in paths if "/" not in path}
    broken=[]; total_links=0; checked=0
    link_pattern=re.compile(r"!?\[[^\]]*\]\((?:<([^>]+)>|([^)]+))\)")
    for item in markdown:
        path=item["path"]; raw=item["data"] or ""
        raw=re.sub(r"(?ms)^\s*(?:~~~+|\x60{3,}).*$.*?^\s*(?:~~~+|\x60{3,})\s*$","",raw)
        for match in link_pattern.finditer(raw):
            target=(match.group(1) or match.group(2) or "").strip()
            if not target or target.startswith("#"): continue
            total_links+=1; parsed=urlsplit(target)
            if parsed.scheme or parsed.netloc or target.startswith(("mailto:","data:")): continue
            relative=unquote(parsed.path).replace("\\","/")
            if not relative: continue
            checked+=1; resolved=posixpath.normpath(posixpath.join(posixpath.dirname(path),relative))
            candidates={resolved,resolved.rstrip("/")+"/README.md",resolved.rstrip("/")+"/index.md",resolved+".md"}
            exists=False if resolved.startswith("../") or resolved==".." else bool(candidates & paths)
            if not exists: broken.append((path,raw.count("\n",0,match.start())+1,target[:180]))
    lines=[f"Markdown/MDX files inspected: {len(markdown):,}",f"Links detected: {total_links:,}",f"Relative links checked: {checked:,}",f"Broken relative link candidates: {len(broken):,}","","Root-level documentation files:"]
    lines.extend("- "+name+": "+("found" if name.casefold() in root_names else "not found at repository root") for name in required)
    lines.extend(["","Broken relative links (heuristic):"])
    lines.extend(f"- {path}:{line} · {target}" for path,line,target in broken[:400])
    lines.append("Only relative Markdown links are resolved against ZIP paths. External links and anchors are not requested or checked.")
    return _repo_report_text(p,"-repo-docs-audit.txt","Repository documentation audit",lines,f"Inspected {len(markdown)} Markdown files and found {len(broken)} unresolved relative link candidates.")


def repo_migration_audit(p):
    rules=[
        ("HIGH",re.compile(r"\bDROP\s+(?:TABLE|COLUMN|INDEX|SCHEMA)\b",re.I),"Destructive DROP operation; review rollback and data-retention requirements."),
        ("HIGH",re.compile(r"\bTRUNCATE\s+(?:TABLE\s+)?",re.I),"TRUNCATE removes rows; verify intended scope and backup."),
        ("HIGH",re.compile(r"\bDELETE\s+FROM\s+([\w\".]+)(?:\s*;|\s*$)",re.I),"DELETE without a visible WHERE clause may remove every row."),
        ("WARN",re.compile(r"\bALTER\s+TABLE\b.*\bALTER\s+(?:COLUMN\s+)?\w+\s+TYPE\b",re.I),"Column type change may rewrite or truncate existing data."),
        ("WARN",re.compile(r"\bALTER\s+TABLE\b.*\bALTER\s+(?:COLUMN\s+)?\w+\s+SET\s+NOT\s+NULL\b",re.I),"Adding NOT NULL can fail on existing NULL values."),
        ("WARN",re.compile(r"\bRENAME\s+(?:TABLE|COLUMN)\b",re.I),"Rename operations may break older application versions during rolling deployments."),
        ("WARN",re.compile(r"\bADD\s+COLUMN\b.*\bNOT\s+NULL\b",re.I),"Adding a non-null column may require a default or staged backfill."),
    ]
    findings=[]; inspected=0
    migration_path=re.compile(r"(?:^|/)(?:migrations?|migrate|schema|prisma)(?:/|$)",re.I)
    for item in _repo_text_candidates(p):
        path=item["path"]; suffix=Path(path).suffix.lower()
        if suffix not in {".sql",".prisma",".py",".ts",".js",".go",".rb"} or (not migration_path.search(path) and suffix!=".sql"): continue
        inspected+=1
        for line_no,line in enumerate((item["data"] or "").splitlines(),1):
            stripped=re.sub(r"--.*$","",line); stripped=re.sub(r"/\*.*?\*/","",stripped)
            for severity,pattern,message in rules:
                if not pattern.search(stripped): continue
                if "DELETE without" in message and re.search(r"\bWHERE\b",stripped,re.I): continue
                findings.append((severity,path,line_no,message))
    lines=[f"Migration/schema files inspected: {inspected:,}",f"Review signals: {len(findings):,}","","Findings:"]
    lines.extend(f"- {severity} · {path}:{line} · {message}" for severity,path,line,message in findings[:500])
    lines.append("Static pattern scan only. No database is connected; dialects, multi-line clauses, migration order and actual data impact are not evaluated.")
    return _repo_report_text(p,"-repo-migration-audit.txt","Repository migration risk audit",lines,f"Inspected {inspected} migration/schema files and found {len(findings)} destructive-change review signals.")


def repo_runtime_risk(p):
    rules=[
        ("HIGH","EXEC-001",re.compile(r"\b(?:eval|exec)\s*\("),"Dynamic code execution primitive."),
        ("HIGH","PICKLE-001",re.compile(r"\bpickle\.(?:loads|load)\s*\("),"Pickle deserialization can execute code for untrusted data."),
        ("HIGH","YAML-001",re.compile(r"\byaml\.load\s*\("),"YAML load should use a safe loader for untrusted documents."),
        ("HIGH","SHELL-001",re.compile(r"\bsubprocess\.(?:run|Popen|call|check_output)\s*\([^)]*shell\s*=\s*True",re.S),"Subprocess shell=True requires strict command/input handling."),
        ("HIGH","OS-001",re.compile(r"\bos\.system\s*\("),"os.system executes a command through a shell."),
        ("HIGH","JS-FUNC-001",re.compile(r"\bnew\s+Function\s*\("),"Dynamic Function constructor."),
        ("HIGH","HTML-001",re.compile(r"\.innerHTML\s*="),"HTML sink may require sanitization."),
        ("HIGH","HTML-002",re.compile(r"dangerouslySetInnerHTML"),"React raw HTML sink; sanitize untrusted input."),
        ("WARN","TLS-001",re.compile(r"\b(?:verify\s*=\s*False|rejectUnauthorized\s*:\s*false|NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*['\"]?0)"),"TLS certificate verification appears disabled."),
        ("WARN","SQL-001",re.compile(r"(?:execute|query)\s*\(\s*f['\"]|(?:execute|query)\s*\([^)]*\+\s*(?:req|request|params)\b",re.I),"Possible dynamic SQL construction; use parameterized queries."),
        ("WARN","CRYPTO-001",re.compile(r"\b(?:md5|sha1)\s*\("),"Legacy hash algorithm detected; assess whether cryptographic integrity is required."),
    ]
    suffixes={".py",".pyw",".js",".mjs",".cjs",".ts",".tsx",".jsx",".java",".go",".rb",".php",".cs",".rs"}
    findings=[]; inspected=0
    for item in _repo_text_candidates(p):
        path=item["path"]; raw=item["data"] or ""
        if Path(path).suffix.lower() not in suffixes: continue
        inspected+=1
        for severity,rule,pattern,message in rules:
            for match in list(pattern.finditer(raw))[:80]:
                findings.append((severity,rule,path,raw.count("\n",0,match.start())+1,message))
    lines=[f"Source files inspected: {inspected:,}",f"Runtime risk signals: {len(findings):,}","","Findings (matched code and values are intentionally omitted):"]
    lines.extend(f"- {severity} · {rule} · {path}:{line} · {message}" for severity,rule,path,line,message in findings[:700])
    lines.append("Static triage signals only: not exploitability, reachability or data-flow proof. Comments/tests may cause false positives; aliases and dynamic construction may cause false negatives. No code is executed.")
    return _repo_report_text(p,"-repo-runtime-risk.txt","Repository runtime risk signals",lines,f"Scanned {inspected} source files and found {len(findings)} static runtime-risk signals.")


def repo_i18n_audit(p):
    import json
    locale_file=re.compile(r"^(?:[a-z]{2,3}(?:[-_][A-Za-z0-9]{2,8})?|messages|translations)(?:\.json)?$",re.I)
    candidates=[]
    for item in _repo_text_candidates(p):
        path=item["path"]; parts={part.casefold() for part in path.split("/")}
        likely=bool(parts & {"i18n","locales","locale","translations","messages"}) or bool(locale_file.match(Path(path).name))
        if not likely or Path(path).suffix.lower()!=".json": continue
        try: obj=json.loads(item["data"] or "")
        except (ValueError,TypeError): continue
        if not isinstance(obj,dict): continue
        flattened=set()
        def walk(value,prefix=""):
            if isinstance(value,dict):
                for key,child in value.items(): walk(child,(prefix+"."+str(key)).strip("."))
            elif isinstance(value,list):
                for index,child in enumerate(value): walk(child,prefix+"["+str(index)+"]")
            else: flattened.add(prefix)
        walk(obj); candidates.append((path,flattened))
    groups={}
    for path,keys in candidates: groups.setdefault(posixpath.dirname(path),[]).append((path,keys))
    comparisons=[]
    for parent,items in sorted(groups.items()):
        if len(items)<2: continue
        base_path,base_keys=max(items,key=lambda pair:len(pair[1]))
        for path,keys in items:
            if path==base_path: continue
            comparisons.append((base_path,path,len(base_keys-keys),len(keys-base_keys),sorted(base_keys-keys),sorted(keys-base_keys)))
    lines=[f"JSON locale candidates: {len(candidates):,}",f"Locale directories compared: {sum(1 for items in groups.values() if len(items)>1):,}",f"Pairwise comparisons: {len(comparisons):,}","","Locale files:"]
    lines.extend(f"- {path}: {len(keys):,} leaf keys" for path,keys in candidates[:200])
    lines.extend(["","Missing/extra key comparisons (largest locale in each directory is the reference):"])
    for base,path,missing,extra,missing_keys,extra_keys in comparisons[:200]:
        lines.append(f"- {path} vs {base}: {missing} missing, {extra} extra")
        lines.extend("    missing: "+key for key in missing_keys[:20])
        lines.extend("    extra: "+key for key in extra_keys[:20])
    if not comparisons: lines.append("- No comparable locale JSON groups found using directory/name heuristics.")
    lines.append("JSON key comparison only; it does not assess translation quality, plural rules, context or locale completeness.")
    return _repo_report_text(p,"-repo-i18n-audit.txt","Repository localization audit",lines,f"Found {len(candidates)} JSON locale candidates and {len(comparisons)} pairwise key comparisons.")



def repo_env_contract(p):
    references={}; declarations={}; secret_refs={}
    suffixes={".py",".pyw",".js",".jsx",".mjs",".cjs",".ts",".tsx",".go",".rb",".php",".java",".cs",".rs"}
    code_patterns=[
        re.compile(r"\bprocess\.env\.([A-Z][A-Z0-9_]*)"),
        re.compile(r"\bimport\.meta\.env\.([A-Z][A-Z0-9_]*)"),
        re.compile(r"\bos\.(?:getenv|environ\.get)\s*\(\s*['\"]([A-Z][A-Z0-9_]*)['\"]"),
        re.compile(r"\bos\.environ\s*\[\s*['\"]([A-Z][A-Z0-9_]*)['\"]\s*\]"),
        re.compile(r"\bDeno\.env\.get\s*\(\s*['\"]([A-Z][A-Z0-9_]*)['\"]"),
        re.compile(r"\bgetenv\s*\(\s*['\"]([A-Z][A-Z0-9_]*)['\"]"),
        re.compile(r"\$_ENV\s*\[\s*['\"]([A-Z][A-Z0-9_]*)['\"]\s*\]"),
    ]
    ignored={"NODE_ENV","CI","PATH","HOME","PWD","SHELL","USER","PORT","HOST","LANG","TZ"}
    inspected=0
    for item in _repo_text_candidates(p):
        path=item["path"]; raw=item.get("data")
        if raw is None: continue
        name=Path(path).name.casefold(); suffix=Path(path).suffix.lower()
        if name.startswith((".env",".dev.vars")) or name in ("env.example","env.sample"):
            for line_no,line in enumerate(raw.splitlines(),1):
                match=re.match(r"^\s*(?:export\s+)?([A-Z][A-Z0-9_]*)\s*=",line)
                if match: declarations.setdefault(match.group(1),[]).append((path,line_no))
        if suffix in suffixes:
            inspected+=1
            for pattern in code_patterns:
                for match in pattern.finditer(raw[:2*1024*1024]):
                    key=match.group(1)
                    if key not in ignored:
                        references.setdefault(key,[]).append((path,raw.count("\n",0,match.start())+1))
        if ".github/workflows/" in path.lower():
            for match in re.finditer(r"\$\{\{\s*(?:secrets|vars)\.([A-Za-z_][A-Za-z0-9_]*)",raw,re.I):
                key=match.group(1)
                secret_refs.setdefault(key,[]).append((path,raw.count("\n",0,match.start())+1))
        if name=="dockerfile" or name.startswith("dockerfile.") or name=="containerfile":
            for line_no,line in enumerate(raw.splitlines(),1):
                match=re.match(r"^\s*(?:ARG|ENV)\s+([A-Z][A-Z0-9_]*)\b",line,re.I)
                if match: declarations.setdefault(match.group(1),[]).append((path,line_no))
    referenced=set(references); declared=set(declarations); secrets=set(secret_refs)
    missing=sorted(referenced-declared-secrets)
    unused=sorted(declared-referenced-secrets)
    lines=[
        f"Source files inspected: {inspected:,}",
        f"Code environment names: {len(referenced):,}",
        f"Tracked examples/container declarations: {len(declared):,}",
        f"GitHub Actions secret/variable names: {len(secrets):,}",
        f"References without tracked example/declaration: {len(missing):,}",
        f"Declared names without detected code use: {len(unused):,}",
        "",
        "Missing example/declaration candidates:",
    ]
    lines.extend("- "+key for key in missing[:400])
    lines.extend(["","Unused example/container declaration candidates:"])
    lines.extend("- "+key for key in unused[:400])
    lines.extend(["","Referenced names and first locations (values are never printed):"])
    for key,locations in sorted(references.items()):
        lines.append(f"- {key}: {len(locations)} reference(s), first at {locations[0][0]}:{locations[0][1]}")
    lines.extend(["","GitHub Actions secret/variable references:"])
    for key,locations in sorted(secret_refs.items()):
        lines.append(f"- {key}: {len(locations)} reference(s), first at {locations[0][0]}:{locations[0][1]}")
    lines.append("Static text scan only. Dynamic names and framework-specific configuration APIs may be missed. Absence from an example is not proof that a production secret is missing. Values are intentionally excluded.")
    return _repo_report_text(p,"-repo-env-contract.txt","Repository environment contract",lines,
        f"Found {len(referenced)} code references, {len(secrets)} Actions references and {len(missing)} names lacking tracked examples.")


def repo_architecture_cycles(p):
    import collections
    graph=_repo_architecture_graph(p)
    nodes=[item.get("path") for item in graph.get("nodes",[]) if isinstance(item,dict) and item.get("path")]
    adjacency={node:[] for node in nodes}; reverse={node:[] for node in nodes}; self_loops=set()
    for edge in graph.get("edges",[]):
        if not isinstance(edge,dict): continue
        source,target=edge.get("from"),edge.get("to")
        if source not in adjacency or target not in reverse: continue
        adjacency[source].append(target); reverse[target].append(source)
        if source==target: self_loops.add(source)
    visited=set(); order=[]
    for start in nodes:
        if start in visited: continue
        visited.add(start); stack=[(start,iter(adjacency[start]))]
        while stack:
            node,children=stack[-1]
            try: child=next(children)
            except StopIteration:
                order.append(node); stack.pop(); continue
            if child not in visited:
                visited.add(child); stack.append((child,iter(adjacency.get(child,[]))))
    assigned=set(); components=[]
    for start in reversed(order):
        if start in assigned: continue
        assigned.add(start); component=[]; stack=[start]
        while stack:
            node=stack.pop(); component.append(node)
            for child in reverse.get(node,[]):
                if child not in assigned:
                    assigned.add(child); stack.append(child)
        if len(component)>1 or (len(component)==1 and component[0] in self_loops):
            components.append(sorted(component))
    components.sort(key=lambda group:(-len(group),group))
    indegree={node:len(reverse[node]) for node in nodes}; outdegree={node:len(adjacency[node]) for node in nodes}
    lines=[
        f"Graph nodes: {len(nodes):,}",f"Local import edges: {len(graph.get('edges',[])):,}",
        f"Cyclic strongly connected components: {len(components):,}",
        f"Files participating in cycles: {sum(len(group) for group in components):,}",
        f"Python parse failures: {graph.get('python_parse_failures',0):,}",
        f"Edges truncated by upstream extractor: {bool(graph.get('edges_truncated'))}","","Cycles:",
    ]
    for index,group in enumerate(components[:150],1):
        lines.append(f"- Component {index}: {len(group)} file(s)")
        lines.extend("    "+path for path in group[:50])
        if len(group)>50: lines.append(f"    ... {len(group)-50} more")
    if not components: lines.append("- No cycle detected in extracted local-import graph.")
    lines.extend(["","Highest import-connectedness files:"])
    hubs=sorted(nodes,key=lambda node:(-(indegree[node]+outdegree[node]),node))[:80]
    lines.extend(f"- {node}: imports={outdegree[node]}, imported_by={indegree[node]}" for node in hubs)
    lines.append("Static local-import graph only. Aliases, dynamic loading, dependency injection, runtime calls and cross-language edges may be missed. Cycles are architectural review signals, not automatically defects.")
    return _repo_report_text(p,"-repo-architecture-cycles.txt","Repository architecture cycles",lines,
        f"Analyzed {len(nodes)} nodes and found {len(components)} cyclic components.")


def repo_change_impact(p):
    import collections
    graph=_repo_architecture_graph(p)
    nodes={item.get("path") for item in graph.get("nodes",[]) if isinstance(item,dict) and item.get("path")}
    reverse=collections.defaultdict(set)
    for edge in graph.get("edges",[]):
        if isinstance(edge,dict) and edge.get("from") in nodes and edge.get("to") in nodes:
            reverse[edge["to"]].add(edge["from"])
    metadata_path=Path(os.environ.get("RUNNER_TEMP","/tmp"))/"nolane-inputs"/"github-source-metadata.json"
    try: metadata=json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.is_file() else {}
    except Exception: metadata={}
    compare=metadata.get("compare") if isinstance(metadata,dict) else None
    changed_files=compare.get("files",[]) if isinstance(compare,dict) else []
    if not isinstance(changed_files,list): changed_files=[]
    if not isinstance(compare,dict) or not compare.get("base") or not compare.get("head"):
        lines=[
            "No GitHub Compare metadata is attached to this snapshot.",
            "Run /repo_compare https://github.com/owner/repository base...head to produce change-impact results.",
            "A normal ZIP upload or single-ref repository analysis has no trusted changed-file list.",
        ]
        return _repo_report_text(p,"-repo-change-impact.txt","Repository change impact",lines,"No compare metadata; use /repo_compare to map changed files to reverse import dependents.")
    known={path.casefold():path for path in nodes}; unresolved=[]; changed=[]; impacted={}
    for item in changed_files[:100]:
        if not isinstance(item,dict): continue
        path=str(item.get("filename") or "").replace("\\","/")[:300]
        if not path: continue
        status=str(item.get("status") or "modified")
        changed.append((path,status,int(item.get("additions") or 0),int(item.get("deletions") or 0)))
        node=known.get(path.casefold())
        if not node:
            matches=[value for key,value in known.items() if key.endswith("/"+path.casefold()) or path.casefold().endswith("/"+key)]
            node=matches[0] if len(matches)==1 else None
        if not node:
            unresolved.append(path); continue
        seen={node}; queue=[node]; depth={node:0}
        while queue:
            current=queue.pop(0)
            for dependent in reverse.get(current,()):
                if dependent not in seen:
                    seen.add(dependent); depth[dependent]=depth[current]+1; queue.append(dependent)
        for dependent in seen:
            if dependent==node: continue
            value=impacted.setdefault(dependent,{"max_depth":0,"sources":set()})
            value["max_depth"]=max(value["max_depth"],depth.get(dependent,0))
            value["sources"].add(path)
    lines=[
        f"Compared refs: {compare.get('base')} -> {compare.get('head')}",
        f"Compare status: {compare.get('status') or 'not supplied'}",
        f"Changed file records: {len(changed):,}",
        f"Changed files matched into local graph: {len(changed)-len(unresolved):,}",
        f"Changed files not represented in graph: {len(unresolved):,}",
        f"Potential transitive dependent modules: {len(impacted):,}","","Changed files:",
    ]
    lines.extend(f"- {path} [{status}] +{adds}/-{deletes}" for path,status,adds,deletes in changed[:100])
    lines.extend(["","Potential reverse-import dependents:"])
    for module,value in sorted(impacted.items(),key=lambda pair:(-len(pair[1]["sources"]),-pair[1]["max_depth"],pair[0]))[:300]:
        lines.append(f"- {module}: {len(value['sources'])} changed source(s), max dependency distance {value['max_depth']}")
        lines.extend("    affected by: "+path for path in sorted(value["sources"])[:10])
    lines.extend(["","Changed files absent from the local graph:"])
    lines.extend("- "+path for path in unresolved[:100])
    lines.append("Static import approximation only. It omits dynamic imports, runtime reflection, external consumers, generated code, tests and semantic changes. Compare metadata is capped at 100 file records.")
    return _repo_report_text(p,"-repo-change-impact.txt","Repository change impact",lines,
        f"Compared {len(changed)} files and found {len(impacted)} potential reverse-import dependents.")


def repo_api_spec_audit(p):
    import json
    try: import yaml
    except ImportError: yaml=None
    candidates=[]; findings=[]; operations=0; attempted=0
    methods={"get","put","post","delete","options","head","patch","trace"}
    def resolve_pointer(document,ref):
        if not ref.startswith("#/"): return False
        current=document
        for part in ref[2:].split("/"):
            key=part.replace("~1","/").replace("~0","~")
            if isinstance(current,dict) and key in current: current=current[key]
            elif isinstance(current,list) and key.isdigit() and int(key)<len(current): current=current[int(key)]
            else: return False
        return True
    for item in _repo_text_candidates(p):
        path=item["path"]; raw=item.get("data")
        if raw is None or Path(path).suffix.casefold() not in (".json",".yaml",".yml"): continue
        basename=Path(path).name.casefold()
        if not (basename.startswith(("openapi","swagger","api-spec")) or re.search(r"(?m)^\s*(?:openapi|swagger)\s*:",raw[:12000]) or re.search(r'"(?:openapi|swagger)"\s*:',raw[:12000])): continue
        attempted+=1
        try:
            document=json.loads(raw) if Path(path).suffix.casefold()==".json" else (yaml.safe_load(raw) if yaml else None)
        except Exception as exc:
            findings.append(("ERROR",path,1,"Cannot parse API description ("+type(exc).__name__+").")); continue
        if document is None:
            findings.append(("WARN",path,1,"YAML parser is unavailable; structural validation skipped.")); continue
        if not isinstance(document,dict):
            findings.append(("ERROR",path,1,"API description root must be an object/map.")); continue
        candidates.append(path)
        version=str(document.get("openapi") or document.get("swagger") or "")
        if not (version.startswith("3.") or version.startswith("2.")):
            findings.append(("WARN",path,1,"Missing or unsupported OpenAPI/Swagger version marker."))
        info=document.get("info")
        if not isinstance(info,dict) or not info.get("title") or not info.get("version"):
            findings.append(("WARN",path,1,"Top-level info.title and info.version should be present."))
        routes=document.get("paths")
        if not isinstance(routes,dict) or not routes:
            findings.append(("WARN",path,1,"No non-empty paths object was found.")); routes={}
        operation_ids={}
        for route,definition in routes.items():
            if not isinstance(definition,dict): continue
            for method,operation in definition.items():
                method=str(method).casefold()
                if method not in methods or not isinstance(operation,dict): continue
                operations+=1
                opid=str(operation.get("operationId") or "").strip()
                if opid:
                    if opid.casefold() in operation_ids:
                        findings.append(("ERROR",path,1,"Duplicate operationId "+opid[:100]+" on "+str(route)[:120]+"."))
                    else: operation_ids[opid.casefold()]=str(route)
                else: findings.append(("INFO",path,1,"Missing operationId for "+method.upper()+" "+str(route)[:120]+"."))
                if not isinstance(operation.get("responses"),dict) or not operation.get("responses"):
                    findings.append(("WARN",path,1,"Missing responses map for "+method.upper()+" "+str(route)[:120]+"."))
                params=operation.get("parameters",[])
                params={(str(v.get("name")),str(v.get("in"))) for v in params if isinstance(v,dict)} if isinstance(params,list) else set()
                for param in re.findall(r"\{([^{}]+)\}",str(route)):
                    if (param,"path") not in params:
                        findings.append(("WARN",path,1,"Path parameter "+param+" is not declared for "+method.upper()+" "+str(route)[:120]+"."))
        def visit(value):
            if isinstance(value,dict):
                for key,child in value.items():
                    if key=="$ref" and isinstance(child,str):
                        if child.startswith("#/") and not resolve_pointer(document,child):
                            findings.append(("ERROR",path,1,"Unresolved local $ref: "+child[:180]))
                        elif child.startswith(("http://","https://")):
                            findings.append(("INFO",path,1,"Remote $ref not dereferenced by offline audit."))
                    visit(child)
            elif isinstance(value,list):
                for child in value: visit(child)
        visit(document)
    lines=[f"API spec candidates structurally inspected: {len(candidates):,}",f"Candidate files attempted: {attempted:,}",f"Operations detected: {operations:,}",f"Review findings: {len(findings):,}","","Findings:"]
    lines.extend(f"- {level} · {path}:{line} · {message}" for level,path,line,message in findings[:600])
    if not candidates: lines.append("- No OpenAPI/Swagger JSON/YAML documents were detected.")
    lines.append("Offline structural heuristic only. Remote refs are not fetched; dialect extensions, callbacks, webhooks, discriminators and semantic constraints are not fully validated.")
    return _repo_report_text(p,"-repo-api-spec-audit.txt","Repository OpenAPI contract audit",lines,
        f"Inspected {len(candidates)} API specs, found {operations} operations and {len(findings)} review findings.")


def repo_container_audit(p):
    findings=[]; inspected=0
    for item in _repo_text_candidates(p):
        path=item["path"]; raw=item.get("data")
        if raw is None: continue
        name=Path(path).name.casefold(); suffix=Path(path).suffix.casefold()
        dockerfile=name=="dockerfile" or name.startswith("dockerfile.") or name=="containerfile" or name.startswith("containerfile.")
        compose=name in ("docker-compose.yml","docker-compose.yaml","compose.yml","compose.yaml") or ("compose" in name and suffix in (".yml",".yaml"))
        if not dockerfile and not compose: continue
        inspected+=1; lines=raw.splitlines()
        if dockerfile:
            base_lines=[(n,line) for n,line in enumerate(lines,1) if re.match(r"^\s*FROM\s+",line,re.I)]
            if not any(re.match(r"^\s*USER\s+",line,re.I) for line in lines):
                findings.append(("WARN",path,1,"No USER instruction detected; final image may run as root."))
            for n,line in base_lines:
                image=re.sub(r"^\s*FROM\s+","",line,flags=re.I).split()[0]
                last=image.rsplit("/",1)[-1]
                if ":" not in last and "@" not in image:
                    findings.append(("WARN",path,n,"Base image has no explicit version tag or immutable digest."))
                if last.endswith(":latest"):
                    findings.append(("WARN",path,n,"Base image uses the floating latest tag."))
            if not any(re.match(r"^\s*HEALTHCHECK\s+",line,re.I) for line in lines):
                findings.append(("INFO",path,1,"No HEALTHCHECK instruction detected."))
            for n,line in enumerate(lines,1):
                if re.match(r"^\s*(?:ARG|ENV)\s+[A-Z0-9_]*(?:PASSWORD|TOKEN|SECRET|CREDENTIAL|PRIVATE_KEY)[A-Z0-9_]*\b",line,re.I):
                    findings.append(("HIGH",path,n,"Credential-like variable declared via Docker ARG/ENV may persist in image metadata or layers."))
                if re.match(r"^\s*(?:COPY|ADD)\s+.*(?:^|[\s/])\.env(?:\s|$)",line,re.I):
                    findings.append(("HIGH",path,n,"Potential .env file copied into the image; verify .dockerignore and secret handling."))
                if re.match(r"^\s*ADD\s+https?://",line,re.I):
                    findings.append(("WARN",path,n,"Remote URL added directly to image; verify immutable source and checksum."))
        if compose:
            for n,line in enumerate(lines,1):
                stripped=line.strip()
                if re.match(r"privileged\s*:\s*true\b",stripped,re.I): findings.append(("HIGH",path,n,"Compose service enables privileged mode."))
                if re.match(r"network_mode\s*:\s*host\b",stripped,re.I): findings.append(("WARN",path,n,"Compose service uses host network mode."))
                if "/var/run/docker.sock" in line: findings.append(("HIGH",path,n,"Compose service mounts Docker socket."))
                image=re.match(r"image\s*:\s*['\"]?([^'\"]+)",stripped,re.I)
                if image:
                    last=image.group(1).rsplit("/",1)[-1]
                    if last.endswith(":latest") or (":" not in last and "@" not in image.group(1)):
                        findings.append(("WARN",path,n,"Compose image uses latest or an implicit floating tag."))
    lines=[f"Container configuration files inspected: {inspected:,}",f"Review signals: {len(findings):,}","","Findings:"]
    lines.extend(f"- {level} · {path}:{line} · {message}" for level,path,line,message in findings[:500])
    if not findings: lines.append("- No supported container configuration signals found.")
    lines.append("Static line-pattern review only. Multi-stage inheritance, interpolation, runtime policy and the final effective USER are not fully evaluated.")
    return _repo_report_text(p,"-repo-container-audit.txt","Repository container audit",lines,
        f"Inspected {inspected} container files and found {len(findings)} review signals.")


def repo_ci_reliability(p):
    findings=[]; inspected=0
    for item in _repo_text_candidates(p):
        path=item["path"]; raw=item.get("data")
        if raw is None or not re.search(r"(^|/)\.github/workflows/[^/]+\.(?:yml|yaml)$",path,re.I): continue
        inspected+=1
        try:
            import yaml
            data=yaml.safe_load(raw)
        except Exception:
            data=None
        if not isinstance(data,dict):
            findings.append(("ERROR",path,1,"Workflow YAML could not be parsed for reliability analysis.")); continue
        jobs=data.get("jobs",{})
        if not isinstance(jobs,dict) or not jobs:
            findings.append(("WARN",path,1,"No recognizable jobs map found.")); continue
        if "concurrency" not in data:
            findings.append(("INFO",path,1,"No workflow-level concurrency group; duplicate runs may consume runner capacity."))
        for job_id,job in jobs.items():
            if not isinstance(job,dict): continue
            timeout=job.get("timeout-minutes")
            if not isinstance(timeout,int) or timeout<=0:
                findings.append(("WARN",path,1,"Job "+str(job_id)[:80]+" has no positive timeout-minutes limit."))
            if job.get("continue-on-error") is True:
                findings.append(("WARN",path,1,"Job "+str(job_id)[:80]+" sets continue-on-error: true."))
            steps=job.get("steps",[])
            if isinstance(steps,list):
                for step in steps:
                    if not isinstance(step,dict): continue
                    run=step.get("run")
                    if isinstance(run,str) and re.search(r"(?:\|\|\s*true\b|;\s*true\s*$)",run):
                        findings.append(("WARN",path,1,"A step in job "+str(job_id)[:80]+" may mask a command failure with || true or trailing true."))
                    if isinstance(run,str) and "set +e" in run:
                        findings.append(("INFO",path,1,"A step in job "+str(job_id)[:80]+" disables shell fail-fast; verify failures are checked explicitly."))
                    uses=step.get("uses")
                    if isinstance(uses,str) and re.search(r"@(?:main|master|v\d+|latest)$",uses,re.I):
                        findings.append(("INFO",path,1,"A step in job "+str(job_id)[:80]+" uses a moving action tag; action pinning is covered by security audit."))
    lines=[f"GitHub Actions workflow files inspected: {inspected:,}",f"Reliability review signals: {len(findings):,}","","Findings:"]
    lines.extend(f"- {level} · {path}:{line} · {message}" for level,path,line,message in findings[:600])
    if not findings: lines.append("- No supported CI reliability signals detected.")
    lines.append("Static workflow review only. Matrix expansion, reusable workflows, composite actions, branch protection, org policy, runner availability and actual test outcomes are not evaluated.")
    return _repo_report_text(p,"-repo-ci-reliability.txt","Repository CI reliability audit",lines,
        f"Inspected {inspected} GitHub Actions workflow files and found {len(findings)} review signals.")



def repo_intelligence(p):
    import collections
    import zipfile
    members = list(_repo_members(p))
    source_items = list(_repo_text_candidates(p))
    source_files = [
        item for item in source_items
        if item.get("data") is not None and Path(item["path"]).suffix.lower() in _REPO_SOURCE_EXTENSIONS
    ]
    graph = _repo_architecture_graph(p)
    output_artifacts = []
    processors = [
        ("inventory", repo_inventory),
        ("dependencies", repo_dependencies),
        ("license", repo_license_report),
        ("secret-scan", repo_secret_scan),
        ("todo-scan", repo_todo_scan),
        ("code-stats", repo_code_stats),
        ("config-audit", repo_config_audit),
        ("duplicates", repo_duplicates),
        ("security-audit", repo_security_audit),
        ("supply-chain", repo_supply_chain),
        ("test-map", repo_test_map),
        ("test-quality", repo_test_quality),
        ("complexity", repo_complexity_report),
        ("api-surface", repo_api_surface),
        ("docs-audit", repo_docs_audit),
        ("migration-audit", repo_migration_audit),
        ("runtime-risk", repo_runtime_risk),
        ("i18n-audit", repo_i18n_audit),
        ("env-contract", repo_env_contract),
        ("architecture-cycles", repo_architecture_cycles),
        ("change-impact", repo_change_impact),
        ("api-spec-audit", repo_api_spec_audit),
        ("container-audit", repo_container_audit),
        ("ci-reliability", repo_ci_reliability),
    ]
    summaries = {}
    for name, processor in processors:
        result = processor(p)
        summaries[name] = str(result.get("summary", ""))[:500]
        raw_output = result.get("output_path")
        if raw_output:
            artifact = Path(raw_output)
            if artifact.is_file() and artifact.stat().st_size <= 8 * 1024 * 1024:
                output_artifacts.append((name, artifact))

    metadata_path = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "nolane-inputs" / "github-source-metadata.json"
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.is_file() else {}
    except Exception:
        metadata = {}
    repository = metadata.get("repository") if isinstance(metadata, dict) else {}
    repository = repository if isinstance(repository, dict) else {}
    commits = metadata.get("commits", []) if isinstance(metadata, dict) else []
    commits = commits if isinstance(commits, list) else []
    bug_terms = re.compile(r"\b(fix(?:es|ed)?|bug|hotfix|regression|crash|patch)\b", re.I)
    bug_marked = [item for item in commits if isinstance(item, dict) and bug_terms.search(str(item.get("message") or ""))]

    manifest_names = {"package.json", "pyproject.toml", "requirements.txt", "cargo.toml", "go.mod", "composer.json", "gemfile", "pom.xml", "build.gradle"}
    lock_names = {"package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lockb", "bun.lock", "poetry.lock", "uv.lock", "cargo.lock", "go.sum", "composer.lock", "gemfile.lock", "gradle.lockfile"}
    names = {Path(item["path"]).name.casefold() for item in members}
    manifests = sorted(name for name in manifest_names if name in names)
    lockfiles = sorted(name for name in lock_names if name in names)
    directories = collections.Counter(item["path"].split("/", 1)[0] if "/" in item["path"] else "[root]" for item in members)
    report = [
        "# GitHub Repository Intelligence", "",
        f"- Repository: {repository.get('full_name') or p.stem}",
        f"- Source snapshot: {repository.get('html_url') or 'Uploaded ZIP archive'}",
        f"- Analyzed ref: {repository.get('analyzed_ref') or 'ZIP snapshot'}",
        f"- Downloaded archive: {p.stat().st_size:,} bytes",
        f"- Safe archive entries: {len(members):,}",
        f"- UTF-8 source/text files analyzed: {len(source_files):,}", "",
        "## Repository profile",
        f"- Description: {repository.get('description') or 'Not available'}",
        f"- Default branch: {repository.get('default_branch') or 'Not available'}",
        f"- Primary language reported by GitHub: {repository.get('language') or 'Not available'}",
        f"- Stars / forks: {repository.get('stars', 'n/a')} / {repository.get('forks', 'n/a')}",
        f"- Open issue count reported by GitHub: {repository.get('open_issues', 'n/a')}",
        f"- Last pushed: {repository.get('pushed_at') or 'Not available'}",
        f"- Declared SPDX license: {repository.get('license') or 'Not declared in repository metadata'}", "",
        "## Architecture and module map",
        f"- Source files considered: {graph['source_files_considered']:,}",
        f"- Local import edges identified: {len(graph['edges']):,}",
        f"- Python files that could not be parsed: {graph['python_parse_failures']:,}",
        "- module-graph.json contains up to 500 source nodes and 5,000 local import edges.",
        "- Static and heuristic extraction: Python AST plus relative JS/TS imports. Aliases, dynamic loading and cross-language calls may be missed.", "",
        "## Dependency and supply-chain signals",
        "- Manifest files detected: " + (", ".join(manifests) if manifests else "none detected"),
        "- Lockfiles detected: " + (", ".join(lockfiles) if lockfiles else "none detected"),
        "- Lockfiles indicate install reproducibility only. This runner does not install dependencies or query CVE/advisory databases.", "",
        "## Static audit results",
    ]
    for name in ("inventory", "dependencies", "license", "secret-scan", "todo-scan", "code-stats", "config-audit", "duplicates", "security-audit", "supply-chain", "test-map", "test-quality", "complexity", "api-surface", "docs-audit", "migration-audit", "runtime-risk", "i18n-audit", "env-contract", "architecture-cycles", "change-impact", "api-spec-audit", "container-audit", "ci-reliability"):
        report.append("- " + name + ": " + summaries.get(name, "not available"))
    report.extend([
        "", "## Git history and change signals",
        f"- Recent commits retrieved: {len(commits):,} (up to 20 on the analyzed ref)",
        f"- Commit messages containing fix/bug/hotfix/regression/crash/patch markers: {len(bug_marked):,}",
        "- Marker counts are search heuristics, not verified bug counts or defect rates.",
    ])
    for item in commits[:20]:
        if not isinstance(item, dict):
            continue
        report.append(
            "- " + str(item.get("sha") or "")[:8] + " · " +
            str(item.get("date") or "unknown date")[:30] + " · " +
            str(item.get("message") or "")[:180]
        )
    if metadata.get("commits_error"):
        report.append("- Commit history unavailable: " + str(metadata["commits_error"])[:180])

    compare = metadata.get("compare") if isinstance(metadata, dict) else None
    if isinstance(compare, dict):
        report.extend([
            "", "## Branch and version comparison",
            f"- Comparison: {compare.get('base', '?')} → {compare.get('head', '?')}",
            f"- Status: {compare.get('status') or 'unavailable'} · ahead {compare.get('ahead_by', '?')} · behind {compare.get('behind_by', '?')}",
            f"- Commits: {compare.get('total_commits', '?')} · changed files returned: {len(compare.get('files') or []):,}",
        ])
        for item in (compare.get("files") or [])[:80]:
            report.append(
                "- " + str(item.get("status", "?")) + " " + str(item.get("filename", "?"))[:240] +
                " · +" + str(item.get("additions", 0)) + " / -" + str(item.get("deletions", 0))
            )
        if compare.get("files_truncated"):
            report.append("- File list truncated to the first 100 entries.")
        if compare.get("error"):
            report.append("- Compare API error: " + str(compare["error"])[:180])

    report.extend([
        "", "## Maintenance signals",
        "- Top-level roots: " + ", ".join(f"{name} ({count})" for name, count in directories.most_common(12)),
        "- Review test coverage, CI behavior, permissions, secret handling and deployment configuration manually.",
        "", "## Safety and interpretation",
        "- Public GitHub archive only. Repository source is inspected as data; scripts, workflows and package installation hooks are never executed.",
        "- Secret scan reports file path, line and finding type only. Secret values are withheld.",
        "- TODO/FIXME and commit-message markers can contain false positives.",
        "- This is static repository intelligence, not a penetration test, legal opinion, complete dependency vulnerability audit or correctness guarantee.",
    ])
    report_path = p.with_name(p.stem + "-intelligence-report.md")
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    graph_path = p.with_name(p.stem + "-module-graph.json")
    graph_path.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
    metadata_output = p.with_name(p.stem + "-github-metadata.json")
    metadata_output.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    package = p.with_name(p.stem + "-intelligence.zip")
    with zipfile.ZipFile(package, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=4) as archive:
        archive.write(report_path, "report/repository-intelligence.md")
        archive.write(graph_path, "architecture/module-graph.json")
        archive.write(metadata_output, "github/github-metadata.json")
        for name, path in output_artifacts:
            archive.write(path, "reports/" + name + path.suffix.lower())
    if package.stat().st_size > 45 * 1024 * 1024:
        package.unlink(missing_ok=True)
        raise RuntimeError("Repository Intelligence report package exceeds the 45 MB output limit.")
    return {
        "summary": (
            f"GitHub Intelligence: {repository.get('full_name') or p.stem} · {len(members):,} files · "
            f"{len(source_files):,} source/text files · {len(graph['edges']):,} local import edges · "
            f"{len(commits):,} recent commits · {len(output_artifacts)} audit artifacts."
        ),
        "output_path": str(package),
    }





def repo_security_audit(p):
    """Static security checks for GitHub Actions, containers, Kubernetes and Terraform."""
    import zipfile
    try:
        import yaml
    except ImportError:
        yaml = None

    rules = {
        "NOLANE-GHA-001": ("Privileged pull_request_target workflow", "warning",
            "pull_request_target runs with the base repository trust context. Keep untrusted pull-request code and expressions out of privileged jobs."),
        "NOLANE-GHA-002": ("Pull-request shell expression injection", "error",
            "Pass untrusted GitHub event values through environment variables and quote them; do not interpolate them directly into run scripts."),
        "NOLANE-GHA-003": ("GitHub Action is not pinned to an immutable reference", "warning",
            "Pin third-party actions to a verified full commit SHA and optionally keep the release tag in a comment."),
        "NOLANE-GHA-004": ("Privileged pull_request_target checks out untrusted code", "error",
            "Do not check out or execute a contributor-controlled head in a privileged pull_request_target workflow."),
        "NOLANE-CTR-001": ("Container base image is not immutable", "warning",
            "Pin production base images to an explicit supported version or digest; avoid latest and implicit tags."),
        "NOLANE-CTR-002": ("Remote script is piped to a shell", "error",
            "Download and verify scripts separately, pin checksums/signatures, then execute only reviewed content."),
        "NOLANE-CTR-003": ("Potential secret is declared as a Docker build ARG or ENV", "warning",
            "Do not bake credentials into image layers. Use the build platform's secret-mount mechanism."),
        "NOLANE-CTR-004": ("Container explicitly runs as root", "warning",
            "Use a dedicated unprivileged runtime user unless root is demonstrably required."),
        "NOLANE-CTR-005": ("Container has no explicit runtime user", "warning",
            "Declare a dedicated unprivileged USER in the image or set a non-root identity in the runtime configuration."),
        "NOLANE-K8S-001": ("Privileged container security context", "error",
            "Remove privileged mode and grant only the minimum Linux capabilities required."),
        "NOLANE-K8S-002": ("Privilege escalation is allowed", "warning",
            "Set allowPrivilegeEscalation to false unless the workload has a documented requirement."),
        "NOLANE-K8S-003": ("Container runs as UID 0", "warning",
            "Set runAsNonRoot: true and use a non-zero runAsUser."),
        "NOLANE-K8S-004": ("Pod uses host namespaces", "error",
            "Avoid hostNetwork, hostPID and hostIPC; isolate workloads unless host access is necessary."),
        "NOLANE-K8S-005": ("Pod mounts a host path", "warning",
            "Avoid hostPath volumes or restrict them to a narrowly scoped, read-only host directory."),
        "NOLANE-K8S-006": ("Dangerous Linux capability requested", "error",
            "Remove broad capabilities such as ALL or SYS_ADMIN; grant only narrowly justified capabilities."),
        "NOLANE-IAC-001": ("Wildcard IAM action and resource", "warning",
            "Replace wildcard IAM actions/resources with the smallest required action and resource set."),
        "NOLANE-IAC-002": ("Sensitive management port exposed to the world", "error",
            "Restrict SSH/RDP ingress to trusted networks or an identity-aware access path."),
        "NOLANE-IAC-003": ("Object storage public access appears enabled", "warning",
            "Block public access by default and grant access through explicit identity policies."),
    }
    findings = []
    scanned = 0

    def add(rule_id, path, line, detail=""):
        if len(findings) >= 1000:
            return
        title, level, help_text = rules[rule_id]
        findings.append({
            "ruleId": rule_id, "level": level, "path": path,
            "line": max(1, int(line or 1)), "title": title,
            "detail": str(detail)[:240], "remediation": help_text,
        })

    def line_for(raw, token):
        index = raw.find(token)
        return raw[:index].count("\n") + 1 if index >= 0 else 1

    def visit_kubernetes(value, path, raw, parent_key=""):
        if isinstance(value, dict):
            for key, child in value.items():
                key_text = str(key)
                low = key_text.casefold()
                if low == "privileged" and child is True:
                    add("NOLANE-K8S-001", path, line_for(raw, key_text + ": true"))
                elif low == "allowprivilegeescalation" and child is True:
                    add("NOLANE-K8S-002", path, line_for(raw, key_text + ": true"))
                elif low == "runasuser" and str(child) == "0":
                    add("NOLANE-K8S-003", path, line_for(raw, key_text + ": 0"))
                elif low in ("hostnetwork", "hostpid", "hostipc") and child is True:
                    add("NOLANE-K8S-004", path, line_for(raw, key_text + ": true"), key_text)
                elif low == "hostpath" and isinstance(child, dict):
                    add("NOLANE-K8S-005", path, line_for(raw, key_text + ":"))
                elif low == "add" and isinstance(child, list):
                    dangerous = [str(item) for item in child if str(item).upper() in ("ALL", "SYS_ADMIN")]
                    if dangerous:
                        add("NOLANE-K8S-006", path, line_for(raw, key_text + ":"), ", ".join(dangerous))
                visit_kubernetes(child, path, raw, key_text)
        elif isinstance(value, list):
            for child in value:
                visit_kubernetes(child, path, raw, parent_key)

    for item in _repo_text_candidates(p):
        path = item["path"]
        raw = item.get("data")
        if raw is None:
            continue
        scanned += 1
        low_path = path.casefold()
        basename = Path(path).name.casefold()

        if ("/.github/workflows/" in "/" + low_path) and basename.endswith((".yml", ".yaml")):
            pull_target = bool(re.search(r"(?m)^\s*pull_request_target\s*:", raw) or
                               re.search(r"(?m)^\s*on\s*:\s*\[[^\]]*\bpull_request_target\b", raw))
            elevated = bool(re.search(
                r"(?im)^\s*(?:write-all|contents|pull-requests|actions|packages|id-token)\s*:\s*write\b", raw
            ) or re.search(r"(?im)^\s*permissions\s*:\s*write-all\b", raw))
            checks_out_head = bool(re.search(
                r"(?im)^\s*ref\s*:\s*.*\$\{\{\s*github\.event\.pull_request\.head\.(?:sha|ref)", raw
            ))
            if pull_target:
                add("NOLANE-GHA-004" if checks_out_head and elevated else "NOLANE-GHA-001",
                    path, line_for(raw, "pull_request_target"),
                    "Workflow also grants write permissions." if elevated else
                    ("Workflow checks out contributor-controlled head code." if checks_out_head else ""))

            for line_no, line in enumerate(raw.splitlines(), 1):
                uses = re.match(r"^\s*(?:-\s*)?uses\s*:\s*([^\s#]+)", line)
                if uses:
                    action_ref = uses.group(1)
                    if action_ref.startswith("./"):
                        continue
                    ref = action_ref.rsplit("@", 1)[-1] if "@" in action_ref else ""
                    immutable = bool(re.fullmatch(r"[a-f0-9]{40}", ref, re.I) or
                                     re.fullmatch(r"sha256:[a-f0-9]{64}", ref, re.I))
                    if not immutable:
                        add("NOLANE-GHA-003", path, line_no, "An action reference is mutable or not pinned to a full commit SHA.")

            if yaml is not None:
                try:
                    document = yaml.safe_load(raw)
                except Exception:
                    document = None

                def inspect_steps(value):
                    if isinstance(value, dict):
                        for key, child in value.items():
                            if str(key) == "run" and isinstance(child, str):
                                for match in re.finditer(
                                    r"\$\{\{\s*github\.event\.(?:pull_request\.(?:title|body|head\.ref)|issue\.(?:title|body)|comment\.body)\s*\}\}",
                                    child,
                                ):
                                    expr = match.group(0)
                                    add("NOLANE-GHA-002", path, line_for(raw, expr), expr[:120])
                            else:
                                inspect_steps(child)
                    elif isinstance(value, list):
                        for child in value:
                            inspect_steps(child)
                inspect_steps(document)

        if basename.startswith(("dockerfile", "containerfile")):
            lines = raw.splitlines()
            has_user = False
            for line_no, line in enumerate(lines, 1):
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                match = re.match(r"(?i)^FROM\s+(?:--platform=\S+\s+)?(\S+)", stripped)
                if match:
                    image = match.group(1)
                    if not image.lower().endswith(":latest") and "@" not in image and ":" not in image.rsplit("/", 1)[-1]:
                        add("NOLANE-CTR-001", path, line_no, "Base image uses an implicit tag.")
                    elif image.lower().endswith(":latest"):
                        add("NOLANE-CTR-001", path, line_no, "Base image uses latest.")
                if re.match(r"(?i)^ADD\s+https?://", stripped):
                    add("NOLANE-CTR-002", path, line_no, "Remote URL used by ADD.")
                if re.match(r"(?i)^RUN\b", stripped) and re.search(
                    r"(?i)(?:curl|wget)\b[^|;&]*\|\s*(?:sudo\s+)?(?:sh|bash)\b", stripped
                ):
                    add("NOLANE-CTR-002", path, line_no)
                if re.match(r"(?i)^(?:ARG|ENV)\s+", stripped) and re.search(
                    r"(?i)\b(?:[A-Z0-9_]*(?:API[_-]?KEY|TOKEN|PASSWORD|PASSWD|SECRET)[A-Z0-9_]*)\b", stripped
                ):
                    add("NOLANE-CTR-003", path, line_no, "Credential-like variable name; value intentionally omitted.")
                user_match = re.match(r"(?i)^USER\s+(.+)$", stripped)
                if user_match:
                    has_user = True
                    if user_match.group(1).strip().lower() in ("root", "0"):
                        add("NOLANE-CTR-004", path, line_no)
            if not has_user:
                add("NOLANE-CTR-005", path, 1, "No USER instruction found; runtime may default to root.")

        if basename.endswith(".tf"):
            if (re.search(r'(?i)\bactions?\s*[:=]\s*(?:\[[^\]]*["\']\*["\'][^\]]*\]|["\']\*["\'])', raw) and
                    re.search(r'(?i)\bresources?\s*[:=]\s*(?:\[[^\]]*["\']\*["\'][^\]]*\]|["\']\*["\'])', raw)):
                add("NOLANE-IAC-001", path, line_for(raw, "*"))
            if re.search(r'(?i)\b(?:cidr_blocks|source_ranges)\s*=\s*\[[^\]]*["\']0\.0\.0\.0/0["\']', raw, re.S) and re.search(
                r"(?is)(?:from_port|to_port|port)\s*=\s*(?:22|3389)", raw
            ):
                add("NOLANE-IAC-002", path, line_for(raw, "0.0.0.0/0"))
            if re.search(r'(?i)\bacl\s*=\s*["\']public-read["\']', raw) or re.search(
                r"(?i)\bblock_public_(?:acls|policy)\s*=\s*false", raw
            ):
                add("NOLANE-IAC-003", path, line_for(raw, "public-read") if "public-read" in raw else line_for(raw, "block_public_"))

        if basename.endswith((".yaml", ".yml")) and yaml is not None:
            # Only inspect YAML documents that look like Kubernetes resources.
            if re.search(r"(?m)^\s*(?:apiVersion|kind)\s*:", raw):
                try:
                    for document in yaml.safe_load_all(raw):
                        if isinstance(document, dict) and ("apiVersion" in document or "kind" in document):
                            visit_kubernetes(document, path, raw)
                except Exception:
                    pass

    findings.sort(key=lambda item: (item["level"] != "error", item["ruleId"], item["path"], item["line"]))
    counts = {level: sum(1 for item in findings if item["level"] == level) for level in ("error", "warning", "note")}
    rules_used = sorted({item["ruleId"] for item in findings})
    sarif_rules = [{
        "id": rule_id,
        "name": rule_id,
        "shortDescription": {"text": rules[rule_id][0]},
        "fullDescription": {"text": rules[rule_id][2]},
        "defaultConfiguration": {"level": rules[rule_id][1]},
        "help": {"text": rules[rule_id][2]},
        "properties": {"tags": ["security", "static-analysis"]},
    } for rule_id in rules_used]
    sarif_results = [{
        "ruleId": item["ruleId"],
        "level": item["level"],
        "message": {"text": item["title"] + (": " + item["detail"] if item["detail"] else "")},
        "locations": [{
            "physicalLocation": {
                "artifactLocation": {"uri": item["path"]},
                "region": {"startLine": item["line"]},
            }
        }],
    } for item in findings]
    sarif = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {"driver": {"name": "Nolane Repository Security Audit", "rules": sarif_rules}},
            "results": sarif_results,
        }],
    }
    report = [
        "# Static repository security audit", "",
        f"- Text/config files scanned: {scanned:,}",
        f"- Findings: {len(findings):,} (errors {counts['error']}, warnings {counts['warning']})",
        "- Output includes SARIF 2.1.0 for compatible code-scanning viewers.",
        "",
        "## Findings",
    ]
    for item in findings:
        report.append(
            f"- [{item['level'].upper()}] {item['ruleId']} · {item['path']}:L{item['line']} · "
            f"{item['title']}" + (f" · {item['detail']}" if item["detail"] else "") +
            f"\n  Remediation: {item['remediation']}"
        )
    if not findings:
        report.append("No matching patterns were detected in the scanned files.")
    report.extend([
        "", "## Scope and limitations",
        "- Static pattern and YAML-structure checks only; no workflow, container, Terraform or application code is executed.",
        "- Heuristics can produce false positives and false negatives. Review each finding in context.",
        "- This is not a complete cloud posture assessment, penetration test or guarantee of security.",
    ])
    json_path = p.with_name(p.stem + "-security-findings.json")
    sarif_path = p.with_name(p.stem + "-security.sarif")
    text_path = p.with_name(p.stem + "-security-audit.md")
    json_path.write_text(json.dumps({"schema_version": 1, "scanned_files": scanned, "counts": counts, "findings": findings}, ensure_ascii=False, indent=2), encoding="utf-8")
    sarif_path.write_text(json.dumps(sarif, ensure_ascii=False, indent=2), encoding="utf-8")
    text_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    package = p.with_name(p.stem + "-security-audit.zip")
    with zipfile.ZipFile(package, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=4) as archive:
        archive.write(text_path, "security-audit.md")
        archive.write(sarif_path, "security.sarif")
        archive.write(json_path, "security-findings.json")
    if package.stat().st_size > 15 * 1024 * 1024:
        package.unlink(missing_ok=True)
        raise RuntimeError("Repository security audit package exceeds the 15 MB output limit.")
    return {
        "summary": f"Static security audit: {scanned:,} files · {len(findings):,} findings · {counts['error']} errors · {counts['warning']} warnings.",
        "output_path": str(package),
    }


def repo_supply_chain(p):
    """Inventory manifest and lockfile evidence without resolving or installing packages."""
    import json as json_module
    import tomllib
    import zipfile

    manifest_kinds = {
        "package.json": "npm", "pyproject.toml": "python", "requirements.txt": "python",
        "cargo.toml": "cargo", "go.mod": "go", "composer.json": "composer",
        "gemfile": "ruby", "pom.xml": "maven", "build.gradle": "gradle",
        "build.gradle.kts": "gradle",
    }
    lock_kinds = {
        "package-lock.json": "npm", "pnpm-lock.yaml": "npm", "yarn.lock": "npm",
        "bun.lock": "npm", "bun.lockb": "npm", "npm-shrinkwrap.json": "npm",
        "poetry.lock": "python", "uv.lock": "python", "pipfile.lock": "python",
        "cargo.lock": "cargo", "go.sum": "go", "composer.lock": "composer",
        "gemfile.lock": "ruby", "gradle.lockfile": "gradle",
    }
    lock_names_by_kind = {}
    for name, kind in lock_kinds.items():
        lock_names_by_kind.setdefault(kind, set()).add(name)

    members = list(_repo_members(p))
    candidates = {item["path"]: item for item in _repo_text_candidates(p)}
    manifests = []
    lockfiles = []
    dependencies = []
    lifecycle_hooks = []
    remote_sources = []
    floating_specs = []

    def classify_requirement(value):
        spec = str(value or "").strip()
        lower = spec.lower()
        if re.search(r"(?:git\+|https?://|github:)", lower):
            return "remote-vcs-or-url"
        if lower.startswith(("file:", "workspace:", "path:")):
            return "local-or-workspace-reference"
        if lower in ("", "*", "latest", "x"):
            return "unspecified-or-floating"
        if re.search(r"(?:\^|~|>=|<=|!=|>|<|\|\|)", spec):
            return "version-range"
        if re.search(r"==|===", spec):
            return "exact-version-pin"
        return "tag-or-version-specifier"

    def add_dependency(manifest, ecosystem, name, scope, requirement):
        if len(dependencies) >= 5000:
            return
        dep_name = str(name).strip()[:180]
        req = str(requirement or "").strip()[:180]
        classification = classify_requirement(req)
        if classification == "remote-vcs-or-url":
            req = "[remote URL/reference omitted]"
        item = {
            "manifest": manifest, "ecosystem": ecosystem, "name": dep_name,
            "scope": str(scope)[:80], "requirement": req,
            "source_class": classification,
        }
        dependencies.append(item)
        if classification == "remote-vcs-or-url":
            remote_sources.append({"manifest": manifest, "name": dep_name, "scope": str(scope)[:80]})
        if classification == "unspecified-or-floating":
            floating_specs.append({"manifest": manifest, "name": dep_name, "scope": str(scope)[:80]})

    for path, item in candidates.items():
        name = Path(path).name.casefold()
        ecosystem = manifest_kinds.get(name)
        if not ecosystem:
            if name in lock_kinds:
                lockfiles.append({"path": path, "ecosystem": lock_kinds[name]})
            continue
        raw = item.get("data") or ""
        dependencies_before = len(dependencies)
        entry = {"path": path, "ecosystem": ecosystem}
        try:
            if name == "package.json":
                obj = json_module.loads(raw)
                for scope in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
                    values = obj.get(scope, {})
                    if isinstance(values, dict):
                        for dep_name, requirement in values.items():
                            add_dependency(path, ecosystem, dep_name, scope, requirement)
                scripts = obj.get("scripts", {})
                if isinstance(scripts, dict):
                    for hook in ("preinstall", "install", "postinstall", "prepare"):
                        if hook in scripts:
                            lifecycle_hooks.append({"manifest": path, "hook": hook})
            elif name == "requirements.txt":
                for line in raw.splitlines():
                    value = line.strip()
                    if not value or value.startswith(("#", "-")):
                        continue
                    value = value.split(";", 1)[0].strip()
                    if value.lower().startswith(("https://", "http://", "git+")):
                        add_dependency(path, ecosystem, "direct-url-dependency", "requirements", value)
                        continue
                    match = re.match(r"([A-Za-z0-9_.-]+)(.*)", value)
                    if match:
                        add_dependency(path, ecosystem, match.group(1), "requirements", match.group(2).strip())
            elif name == "pyproject.toml":
                obj = tomllib.loads(raw)
                project = obj.get("project", {})
                if isinstance(project, dict):
                    for value in project.get("dependencies", []) if isinstance(project.get("dependencies", []), list) else []:
                        match = re.match(r"\s*([A-Za-z0-9_.-]+)\s*(.*)", str(value))
                        if match:
                            add_dependency(path, ecosystem, match.group(1), "project", match.group(2).strip())
                    optional = project.get("optional-dependencies", {})
                    if isinstance(optional, dict):
                        for scope, values in optional.items():
                            if isinstance(values, list):
                                for value in values:
                                    match = re.match(r"\s*([A-Za-z0-9_.-]+)\s*(.*)", str(value))
                                    if match:
                                        add_dependency(path, ecosystem, match.group(1), str(scope), match.group(2).strip())
            elif name == "cargo.toml":
                obj = tomllib.loads(raw)
                for scope in ("dependencies", "dev-dependencies", "build-dependencies"):
                    values = obj.get(scope, {})
                    if isinstance(values, dict):
                        for dep_name, spec in values.items():
                            if isinstance(spec, dict):
                                requirement = spec.get("version", "git/path/workspace")
                                if spec.get("git"):
                                    requirement = "git+" + str(spec.get("git"))[:100]
                                elif spec.get("path"):
                                    requirement = "path:" + str(spec.get("path"))[:100]
                            else:
                                requirement = spec
                            add_dependency(path, ecosystem, dep_name, scope, requirement)
            elif name == "go.mod":
                active = False
                for line in raw.splitlines():
                    value = line.strip()
                    if value.startswith("require ("):
                        active = True
                        continue
                    if active and value == ")":
                        active = False
                        continue
                    if value.startswith("require "):
                        parts = value.split()
                        if len(parts) >= 3:
                            add_dependency(path, ecosystem, parts[1], "require", parts[2])
                    elif active and value and not value.startswith("//"):
                        parts = value.split()
                        if len(parts) >= 2:
                            add_dependency(path, ecosystem, parts[0], "require", parts[1])
            elif name == "composer.json":
                obj = json_module.loads(raw)
                for scope in ("require", "require-dev"):
                    values = obj.get(scope, {})
                    if isinstance(values, dict):
                        for dep_name, requirement in values.items():
                            if dep_name.lower() != "php":
                                add_dependency(path, ecosystem, dep_name, scope, requirement)
        except Exception:
            entry["parse_status"] = "invalid-or-unsupported"
        entry["dependency_count"] = len(dependencies) - dependencies_before
        manifests.append(entry)

    lock_dirs = {}
    for item in lockfiles:
        parent = str(Path(item["path"]).parent)
        lock_dirs.setdefault((item["ecosystem"], parent), []).append(item["path"])

    def nearby_locks(manifest_path, ecosystem):
        parent = Path(manifest_path).parent
        found = []
        parts = parent.parts
        for depth in range(0, min(3, len(parts)) + 1):
            ancestor = str(Path(*parts[:len(parts) - depth])) if depth else str(parent)
            found.extend(lock_dirs.get((ecosystem, ancestor), []))
        return sorted(set(found))

    for manifest in manifests:
        nearby = nearby_locks(manifest["path"], manifest["ecosystem"])
        manifest["nearby_lockfiles"] = nearby
        manifest["lockfile_status"] = "paired" if len(nearby) == 1 else ("ambiguous" if nearby else "not-found")

    multiple_lockfile_dirs = []
    for (ecosystem, parent), values in sorted(lock_dirs.items()):
        if len(values) > 1:
            multiple_lockfile_dirs.append({"ecosystem": ecosystem, "directory": parent, "lockfiles": sorted(values)})

    data = {
        "schema_version": 1,
        "analysis": "Static manifest/lockfile inventory only; no dependency installation, network resolution or CVE lookup.",
        "counts": {
            "manifests": len(manifests), "lockfiles": len(lockfiles),
            "dependencies": len(dependencies), "remote_sources": len(remote_sources),
            "floating_or_unspecified_specs": len(floating_specs),
            "lifecycle_hooks": len(lifecycle_hooks), "manifests_without_nearby_lockfile": sum(1 for item in manifests if item["lockfile_status"] == "not-found"),
            "manifests_with_ambiguous_lockfiles": sum(1 for item in manifests if item["lockfile_status"] == "ambiguous"),
        },
        "manifests": manifests[:500],
        "lockfiles": lockfiles[:500],
        "dependencies": dependencies,
        "remote_sources": remote_sources[:1000],
        "floating_or_unspecified_specs": floating_specs[:1000],
        "package_lifecycle_hooks": lifecycle_hooks[:1000],
        "multiple_lockfile_directories": multiple_lockfile_dirs[:500],
    }
    report = [
        "# Repository dependency and supply-chain inventory", "",
        f"- Manifests: {data['counts']['manifests']:,}",
        f"- Lockfiles: {data['counts']['lockfiles']:,}",
        f"- Manifest dependency declarations: {data['counts']['dependencies']:,}",
        f"- Remote VCS/URL references: {data['counts']['remote_sources']:,}",
        f"- Floating or unspecified requirements: {data['counts']['floating_or_unspecified_specs']:,}",
        f"- Package lifecycle hooks: {data['counts']['lifecycle_hooks']:,}",
        f"- Manifests without a nearby lockfile: {data['counts']['manifests_without_nearby_lockfile']:,}",
        f"- Manifests with ambiguous lockfiles: {data['counts']['manifests_with_ambiguous_lockfiles']:,}",
        "", "## Manifest and lockfile pairing",
    ]
    for manifest in manifests[:300]:
        report.append(
            f"- {manifest['path']} · {manifest['ecosystem']} · {manifest['dependency_count']} declarations · "
            f"lockfile: {manifest['lockfile_status']}" +
            (f" ({', '.join(manifest['nearby_lockfiles'])})" if manifest["nearby_lockfiles"] else "")
        )
    report.extend(["", "## Remote dependency sources"])
    for item in remote_sources[:300]:
        report.append(f"- {item['manifest']} · {item['scope']} · {item['name']} · remote VCS/URL source")
    if not remote_sources:
        report.append("- None detected in supported manifest fields.")
    report.extend(["", "## Install lifecycle hooks"])
    for item in lifecycle_hooks[:300]:
        report.append(f"- {item['manifest']} · {item['hook']} hook is declared (command omitted).")
    if not lifecycle_hooks:
        report.append("- No supported npm lifecycle hooks detected.")
    report.extend([
        "", "## Interpretation",
        "- Lockfile pairing is a path-based heuristic; workspace/package-manager conventions may use a parent lockfile or another mechanism.",
        "- Version ranges are not automatically vulnerabilities. A lockfile is evidence of resolution intent, not proof of safety.",
        "- Only supported manifest fields are parsed. Lockfile contents are inventoried but not resolved into a complete transitive dependency graph.",
        "- No packages are installed, no network requests are made and no CVE/advisory database is queried.",
    ])
    md_path = p.with_name(p.stem + "-supply-chain.md")
    json_path = p.with_name(p.stem + "-supply-chain.json")
    md_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    package = p.with_name(p.stem + "-supply-chain.zip")
    with zipfile.ZipFile(package, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=4) as archive:
        archive.write(md_path, "supply-chain.md")
        archive.write(json_path, "supply-chain.json")
    if package.stat().st_size > 15 * 1024 * 1024:
        package.unlink(missing_ok=True)
        raise RuntimeError("Repository supply-chain package exceeds the 15 MB output limit.")
    return {
        "summary": (
            f"Supply-chain inventory: {len(manifests)} manifests · {len(lockfiles)} lockfiles · "
            f"{len(dependencies)} dependencies · {len(remote_sources)} remote refs · "
            f"{len(lifecycle_hooks)} lifecycle hooks."
        ),
        "output_path": str(package),
    }





def text_extract_mac_addresses(p):
    raw=_read_text_source(p)
    candidates=re.findall(r"(?<![0-9A-Fa-f])(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}(?![0-9A-Fa-f])",raw)
    values=[]
    seen=set()
    for value in candidates:
        canonical=value.replace("-",":").upper()
        if canonical not in seen:
            seen.add(canonical)
            values.append(canonical)
    return _write_text_artifact(p,"mac-addresses","\n".join(values)+("\n" if values else ""),"MAC address extraction",str(len(values))+" address(es)")


def text_extract_port_numbers(p):
    raw=_read_text_source(p)
    patterns=[r"(?i)\bport\s*[:=]\s*(\d{1,5})\b",r"(?i)\blocalhost:(\d{1,5})\b",r"(?i)https?://[^/\s:]+:(\d{1,5})(?:[/\s?#]|$)"]
    values=[]
    seen=set()
    for pattern in patterns:
        for value in re.findall(pattern,raw):
            number=int(value)
            if 1<=number<=65535 and number not in seen:
                seen.add(number)
                values.append(number)
    return _write_text_artifact(p,"port-numbers","\n".join(map(str,values))+("\n" if values else ""),"Port extraction",str(len(values))+" port(s)")


def text_normalize_path_separators(p):
    raw=_read_text_source(p)
    return _write_text_artifact(p,"normalized-paths",raw.replace("\\","/"),"Path separator normalization")


def text_extract_file_extensions(p):
    raw=_read_text_source(p)
    candidates=[]
    pattern=r"(?<![A-Za-z0-9])(?:[A-Za-z0-9_.-]+)\.([A-Za-z0-9]{1,12})(?![A-Za-z0-9])"
    for match in re.finditer(pattern,raw):
        prefix=raw[max(0,match.start()-64):match.start()]
        if re.search(r"https?://[^/\s:]*$",prefix,re.I): continue
        candidates.append(match.group(1))
    values=[]
    seen=set()
    for value in candidates:
        extension=value.lower()
        if extension not in seen:
            seen.add(extension)
            values.append(extension)
    return _write_text_artifact(p,"file-extensions","\n".join(values)+("\n" if values else ""),"File extension extraction",str(len(values))+" extension(s)")


def text_escape_shell_argument(p):
    raw=_read_text_source(p)
    output="'" + raw.replace("'","'\"'\"'") + "'"
    return _write_text_artifact(p,"shell-quoted",output,"POSIX shell argument quoting","one complete argument; POSIX shells")


def text_sort_unique_lines(p):
    raw=_read_text_source(p)
    values=[]
    seen=set()
    for line in raw.splitlines():
        key=line.strip().casefold()
        if key and key not in seen:
            seen.add(key)
            values.append(line)
    values.sort(key=lambda value:(value.casefold(),value))
    output="\n".join(values)
    return _write_text_artifact(p,"sorted-unique-lines",output+("\n" if output else ""),"Unique line sorting",str(len(values))+" unique line(s)")


def text_normalize_unicode_nfkc(p):
    raw=_read_text_source(p)
    return _write_text_artifact(p,"unicode-nfkc",unicodedata.normalize("NFKC",raw),"Unicode NFKC normalization")


def csv_to_sql_inserts(p):
    import io
    raw=_read_text_source(p)
    try: rows=list(csv.reader(io.StringIO(raw,newline="")))
    except csv.Error as exc: raise RuntimeError("Invalid CSV: "+str(exc)) from exc
    if not rows: raise RuntimeError("CSV is empty.")
    headers=rows[0]
    if not headers or len(headers)>200 or len(rows)>100_001:
        raise RuntimeError("CSV-to-SQL is limited to 100,000 rows and 200 columns.")
    def safe_identifier(value,index):
        name=re.sub(r"[^A-Za-z0-9_]","_",value.strip()) or "column_"+str(index+1)
        if name[0].isdigit(): name="_"+name
        return name
    names=[]
    used=set()
    for index,value in enumerate(headers):
        base=safe_identifier(value,index)
        name=base
        suffix=2
        while name.casefold() in used:
            name=base+"_"+str(suffix)
            suffix+=1
        used.add(name.casefold())
        names.append('"'+name+'"')
    statements=["-- Review the target table and column types before executing."]
    for row in rows[1:]:
        values=[]
        for index in range(len(headers)):
            value=row[index] if index<len(row) else ""
            values.append("NULL" if value=="" else "'"+value.replace("'","''")+"'")
        statements.append('INSERT INTO "records" ('+", ".join(names)+") VALUES ("+", ".join(values)+");")
    if len(rows)==1: statements.append("-- No data rows were present.")
    return _write_text_artifact_ext(p,"inserts",".sql","\n".join(statements)+"\n","CSV to SQL INSERT",str(max(0,len(rows)-1))+" row(s)")


def csv_to_yaml(p):
    import io
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("CSV-to-YAML requires PyYAML on the runner.") from exc
    raw=_read_text_source(p)
    try: rows=list(csv.reader(io.StringIO(raw,newline="")))
    except csv.Error as exc: raise RuntimeError("Invalid CSV: "+str(exc)) from exc
    if not rows: raise RuntimeError("CSV is empty.")
    if len(rows)>100_001 or len(rows[0])>200:
        raise RuntimeError("CSV-to-YAML is limited to 100,000 rows and 200 columns.")
    headers=[]
    used=set()
    for index,value in enumerate(rows[0]):
        base=value.strip() or "column_"+str(index+1)
        name=base
        suffix=2
        while name in used:
            name=base+"_"+str(suffix)
            suffix+=1
        used.add(name)
        headers.append(name)
    records=[]
    for row in rows[1:]:
        records.append({key:(row[index] if index<len(row) else "") for index,key in enumerate(headers)})
    output=yaml.safe_dump(records,allow_unicode=True,sort_keys=False,default_flow_style=False)
    return _write_text_artifact_ext(p,"records",".yaml",output,"CSV to YAML",str(len(records))+" record(s)")


def csv_empty_row_report(p):
    import io
    raw=_read_text_source(p)
    try: rows=list(csv.reader(io.StringIO(raw,newline="")))
    except csv.Error as exc: raise RuntimeError("Invalid CSV: "+str(exc)) from exc
    if not rows: raise RuntimeError("CSV is empty.")
    empty=[index for index,row in enumerate(rows[1:],1) if not any(cell.strip() for cell in row)]
    report=["CSV empty-row report","Header columns: "+str(len(rows[0])),"Data rows: "+str(len(rows)-1),"Empty rows: "+str(len(empty)),
            "Empty row numbers (excluding header): "+(", ".join(map(str,empty)) if empty else "none")]
    return _write_text_artifact(p,"empty-row-report","\n".join(report)+"\n","CSV empty-row report")


def csv_row_width_report(p):
    import io
    raw=_read_text_source(p)
    try: rows=list(csv.reader(io.StringIO(raw,newline="")))
    except csv.Error as exc: raise RuntimeError("Invalid CSV: "+str(exc)) from exc
    if not rows: raise RuntimeError("CSV is empty.")
    expected=len(rows[0])
    mismatches=[]
    for line_number,row in enumerate(rows[1:],2):
        if len(row)!=expected:
            mismatches.append({"line":line_number,"actual_columns":len(row),"expected_columns":expected,"difference":len(row)-expected})
    report=["CSV row-width report","Expected columns: "+str(expected),"Data rows: "+str(len(rows)-1),"Mismatched rows: "+str(len(mismatches))]
    report.extend(json.dumps(item,ensure_ascii=False) for item in mismatches[:5000])
    return _write_text_artifact(p,"row-width-report","\n".join(report)+"\n","CSV row-width report")


def json_remove_empty_values(p):
    raw=_read_text_source(p)
    try: value=_load_json_reject_duplicates(raw)
    except (ValueError,json.JSONDecodeError) as exc: raise RuntimeError("Invalid JSON: "+str(exc)) from exc
    def clean(item,depth=0):
        if depth>80: raise RuntimeError("JSON nesting exceeds the 80-level processor limit.")
        if isinstance(item,dict):
            result={}
            for key,child in item.items():
                cleaned=clean(child,depth+1)
                if cleaned is None or cleaned=="" or cleaned==[] or cleaned=={}: continue
                result[key]=cleaned
            return result
        if isinstance(item,list):
            result=[]
            for child in item:
                cleaned=clean(child,depth+1)
                if cleaned is None or cleaned=="" or cleaned==[] or cleaned=={}: continue
                result.append(cleaned)
            return result
        return item
    output=json.dumps(clean(value,0),ensure_ascii=False,indent=2,allow_nan=False)
    return _write_text_artifact(p,"no-empty-values",output+"\n","JSON empty-value removal")


def json_to_typescript(p):
    raw=_read_text_source(p)
    try: value=_load_json_reject_duplicates(raw)
    except (ValueError,json.JSONDecodeError) as exc: raise RuntimeError("Invalid JSON: "+str(exc)) from exc
    declarations=[]
    name_counts={}
    def safe_name(value):
        words=re.findall(r"[A-Za-z0-9]+",str(value))
        name="".join(word[:1].upper()+word[1:] for word in words) or "Field"
        if name[0].isdigit(): name="T"+name
        return name
    def type_of(item,name,depth=0):
        if depth>40: raise RuntimeError("JSON-to-TypeScript is limited to 40 nested levels.")
        if item is None: return "null"
        if isinstance(item,bool): return "boolean"
        if isinstance(item,(int,float)): return "number"
        if isinstance(item,str): return "string"
        if isinstance(item,list):
            if not item: return "unknown[]"
            types=sorted(set(type_of(child,name+"Item",depth+1) for child in item))
            return "("+ " | ".join(types)+")[]"
        if isinstance(item,dict):
            base=safe_name(name)
            count=name_counts.get(base,0)+1
            name_counts[base]=count
            interface=base if count==1 else base+str(count)
            members=[]
            for key,child in item.items():
                members.append("  "+json.dumps(key,ensure_ascii=False)+": "+type_of(child,interface+safe_name(key),depth+1)+";")
            declarations.append("export interface "+interface+" {\n"+"\n".join(members)+"\n}")
            return interface
        return "unknown"
    root_type=type_of(value,"Root")
    output="\n\n".join(declarations)+"\n\nexport type RootType = "+root_type+";\n"
    return _write_text_artifact_ext(p,"types",".ts",output,"JSON to TypeScript type")


def json_nesting_report(p):
    raw=_read_text_source(p)
    try: value=_load_json_reject_duplicates(raw)
    except (ValueError,json.JSONDecodeError) as exc: raise RuntimeError("Invalid JSON: "+str(exc)) from exc
    counts={"objects":0,"arrays":0,"strings":0,"numbers":0,"booleans":0,"nulls":0,"keys":0,"items":0}
    maximum=0
    def visit(item,depth):
        nonlocal maximum
        if depth>80: raise RuntimeError("JSON nesting exceeds the 80-level processor limit.")
        maximum=max(maximum,depth)
        if isinstance(item,dict):
            counts["objects"]+=1
            counts["keys"]+=len(item)
            for child in item.values(): visit(child,depth+1)
        elif isinstance(item,list):
            counts["arrays"]+=1
            counts["items"]+=len(item)
            for child in item: visit(child,depth+1)
        elif isinstance(item,str): counts["strings"]+=1
        elif isinstance(item,bool): counts["booleans"]+=1
        elif item is None: counts["nulls"]+=1
        elif isinstance(item,(int,float)): counts["numbers"]+=1
    visit(value,0)
    lines=["JSON nesting report","Maximum depth: "+str(maximum)]
    lines.extend(key.replace("_"," ").title()+": "+str(count) for key,count in counts.items())
    return _write_text_artifact(p,"nesting-report","\n".join(lines)+"\n","JSON nesting report")




def _env_parse(raw):
    parsed=[]
    invalid=[]
    for line_no,line in enumerate(raw.splitlines(),1):
        stripped=line.strip()
        if not stripped or stripped.startswith("#"): continue
        match=re.match(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$",line)
        if match: parsed.append((line_no,match.group(1),match.group(2)))
        elif "=" in line: invalid.append(line_no)
    return parsed,invalid


def _looks_secret_name(name):
    return bool(re.search(r"(?:PASS(?:WORD)?|TOKEN|SECRET|API[_-]?KEY|PRIVATE|CREDENTIAL|AUTH|ACCESS[_-]?KEY)",name,re.I))


def _redact_env(raw,placeholder="[REDACTED]"):
    output=[]
    pattern=re.compile(r"^(\s*(?:export\s+)?[A-Za-z_][A-Za-z0-9_]*\s*=\s*).*$")
    for line in raw.splitlines(keepends=True):
        ending=""
        body=line
        if body.endswith("\r\n"): body,ending=body[:-2],"\r\n"
        elif body.endswith("\n") or body.endswith("\r"): body,ending=body[:-1],body[-1]
        match=pattern.match(body)
        output.append((match.group(1)+placeholder if match else body)+ending)
    return "".join(output)


def env_audit(p):
    raw=_read_text_source(p)
    parsed,invalid=_env_parse(raw)
    counts={}
    for _,name,_ in parsed: counts[name]=counts.get(name,0)+1
    duplicates=sorted(name for name,count in counts.items() if count>1)
    empty=sorted(name for _,name,value in parsed if not value.strip() or value.strip() in ("''",'""'))
    secret_names=sorted(set(name for _,name,_ in parsed if _looks_secret_name(name)))
    lines=["ENV audit report",f"Assignment lines: {len(parsed)}",f"Unique keys: {len(counts)}",
        f"Duplicate keys: {len(duplicates)}",f"Invalid assignment lines: {len(invalid)}",
        f"Empty values: {len(empty)}",f"Secret-like variable names: {len(secret_names)}"]
    if duplicates: lines.append("Duplicate names: "+", ".join(duplicates[:100]))
    if invalid: lines.append("Invalid assignment line numbers: "+", ".join(map(str,invalid[:100])))
    if empty: lines.append("Empty variable names: "+", ".join(empty[:100]))
    if secret_names: lines.append("Secret-like names (values never shown): "+", ".join(secret_names[:100]))
    return _write_text_artifact(p,"env-audit","\n".join(lines)+"\n","ENV audit")


def env_redact(p):
    raw=_read_text_source(p)
    result=_redact_env(raw,"[REDACTED]")
    return _write_text_artifact_ext(p,"redacted",".env",result,"ENV values redacted","No assignment values are included in the output")


def env_to_example(p):
    raw=_read_text_source(p)
    result=_redact_env(raw,"")
    return _write_text_artifact_ext(p,"example",".env.example",result,"ENV example template","All assignment values are blank")


def _ini_parser(raw):
    import configparser
    parser=configparser.ConfigParser(interpolation=None,strict=True,allow_no_value=True,empty_lines_in_values=False)
    parser.optionxform=str
    parser.read_string(raw)
    return parser


def ini_to_json(p):
    raw=_read_text_source(p)
    try: parser=_ini_parser(raw)
    except Exception as exc: raise RuntimeError("Invalid INI: "+str(exc)[:300]) from exc
    value={"DEFAULT":dict(parser.defaults())}
    for section in parser.sections():
        value[section]=dict(parser.items(section,raw=True))
    output=json.dumps(value,ensure_ascii=False,indent=2)
    return _write_text_artifact_ext(p,"converted",".json",output+"\n","INI to JSON",str(len(parser.sections()))+" section(s)")


def ini_validate(p):
    raw=_read_text_source(p)
    try: parser=_ini_parser(raw)
    except Exception as exc: raise RuntimeError("Invalid INI: "+str(exc)[:300]) from exc
    option_count=sum(len(list(parser.options(section))) for section in parser.sections())
    lines=["INI validation report","Status: valid",f"Sections: {len(parser.sections())}",f"Options (including inherited defaults): {option_count}"]
    return _write_text_artifact(p,"ini-report","\n".join(lines)+"\n","INI validation")


def _toml_value(value):
    import datetime
    if isinstance(value,dict): return {str(k):_toml_value(v) for k,v in value.items()}
    if isinstance(value,list): return [_toml_value(v) for v in value]
    if isinstance(value,(datetime.datetime,datetime.date,datetime.time)): return value.isoformat()
    return value


def _load_toml(raw):
    import tomllib
    try: return tomllib.loads(raw)
    except Exception as exc: raise RuntimeError("Invalid TOML: "+str(exc)[:300]) from exc


def toml_to_json(p):
    raw=_read_text_source(p)
    value=_toml_value(_load_toml(raw))
    output=json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)
    return _write_text_artifact_ext(p,"converted",".json",output+"\n","TOML to JSON")


def toml_validate(p):
    raw=_read_text_source(p)
    value=_load_toml(raw)
    def count_tables(obj):
        total=0
        for item in obj.values():
            if isinstance(item,dict):
                total+=1+count_tables(item)
            elif isinstance(item,list):
                total+=sum(1+count_tables(x) for x in item if isinstance(x,dict))
        return total
    lines=["TOML validation report","Status: valid",f"Top-level keys: {len(value)}",f"Nested table/object count: {count_tables(value)}",
        "Top-level key names: "+(", ".join(sorted(value.keys())[:100]) if value else "none")]
    return _write_text_artifact(p,"toml-report","\n".join(lines)+"\n","TOML validation")


def _properties_unescape(value):
    output=[]
    index=0
    mapping={"t":"\t","n":"\n","r":"\r","f":"\f"}
    while index<len(value):
        char=value[index]
        if char!="\\":
            output.append(char);index+=1;continue
        index+=1
        if index>=len(value): break
        escaped=value[index]
        if escaped=="u" and index+4<len(value):
            code=value[index+1:index+5]
            try: output.append(chr(int(code,16)));index+=5;continue
            except ValueError: pass
        output.append(mapping.get(escaped,escaped))
        index+=1
    return "".join(output)


def _parse_properties(raw):
    logical=[]
    pending=""
    for line in raw.splitlines():
        current=pending+line.lstrip() if pending else line
        slash_count=len(current)-len(current.rstrip("\\"))
        if slash_count%2==1:
            pending=current[:-1]
            continue
        logical.append(current);pending=""
    if pending: logical.append(pending)
    values={};duplicates=[];invalid=[]
    for line_no,line in enumerate(logical,1):
        stripped=line.lstrip()
        if not stripped or stripped.startswith(("#","!")): continue
        escaped=False;separator=None
        for index,char in enumerate(line):
            if escaped: escaped=False;continue
            if char=="\\": escaped=True;continue
            if char in ("=",":") or char.isspace():
                separator=index;break
        if separator is None:
            key=line.strip();value=""
        else:
            key=line[:separator].rstrip()
            index=separator
            if line[index].isspace():
                while index<len(line) and line[index].isspace(): index+=1
                if index<len(line) and line[index] in ("=",":"): index+=1
            else: index+=1
            while index<len(line) and line[index].isspace(): index+=1
            value=line[index:]
        key=_properties_unescape(key)
        value=_properties_unescape(value)
        if not key: invalid.append(line_no);continue
        if key in values: duplicates.append(key)
        values[key]=value
    return values,duplicates,invalid


def properties_to_json(p):
    raw=_read_text_source(p)
    values,duplicates,invalid=_parse_properties(raw)
    output=json.dumps(values,ensure_ascii=False,indent=2)
    return _write_text_artifact_ext(p,"converted",".json",output+"\n","Java Properties to JSON",
        f"{len(values)} key(s); {len(duplicates)} duplicate assignment(s); {len(invalid)} invalid line(s)")


def dockerfile_audit(p):
    raw=_read_text_source(p)
    logical=re.sub(r"\\\r?\n","\n",raw)
    instructions=[]
    for line_no,line in enumerate(logical.splitlines(),1):
        stripped=line.strip()
        if not stripped or stripped.startswith("#"): continue
        match=re.match(r"^([A-Za-z]+)\s+(.*)$",stripped)
        if match: instructions.append((line_no,match.group(1).upper(),match.group(2).strip()))
    counts={}
    for _,command,_ in instructions: counts[command]=counts.get(command,0)+1
    findings=[]
    from_lines=[(n,v) for n,k,v in instructions if k=="FROM"]
    if not from_lines: findings.append("ERROR: no FROM instruction found")
    for line_no,value in from_lines:
        image=value.split()[0]
        if image.lower().endswith(":latest") or ":" not in image and image.lower()!="scratch":
            findings.append(f"WARN line {line_no}: base image {image.split('@')[0]} is not explicitly version-pinned")
    for number,command,arg in instructions:
        if command=="ADD": findings.append(f"WARN line {number}: ADD is broader than COPY; review remote URL/archive behavior")
        if command in ("ENV","ARG"):
            pairs=re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([^\s]+)",arg)
            for key,_secret_value in pairs:
                if _looks_secret_name(key): findings.append(f"WARN line {number}: secret-like {command} key {key}; do not bake credentials into image layers")
    if not counts.get("USER"): findings.append("WARN: USER is not set; container may run as root")
    if not counts.get("HEALTHCHECK"): findings.append("INFO: HEALTHCHECK is not defined")
    lines=["Dockerfile static audit",f"Instructions: {len(instructions)}",f"FROM: {counts.get('FROM',0)}",f"RUN: {counts.get('RUN',0)}",f"USER: {counts.get('USER',0)}",f"HEALTHCHECK: {counts.get('HEALTHCHECK',0)}",f"Findings: {len(findings)}"]
    lines.extend(findings or ["No baseline findings."])
    lines.append("Static inspection only; no image was built and no command was executed.")
    return _write_text_artifact(p,"dockerfile-audit","\n".join(lines)+"\n","Dockerfile audit")


def docker_compose_audit(p):
    import yaml
    raw=_read_text_source(p)
    try: document=yaml.safe_load(raw)
    except Exception as exc: raise RuntimeError("Invalid Compose YAML: "+str(exc)[:300]) from exc
    if not isinstance(document,dict) or not isinstance(document.get("services"),dict):
        raise RuntimeError("Compose file must contain a top-level services mapping.")
    findings=[]
    services=document["services"]
    secret_count=0;published_ports=0
    for service,value in services.items():
        if not isinstance(value,dict): findings.append(f"ERROR: service {service} is not a mapping");continue
        image=value.get("image")
        if isinstance(image,str) and (image.endswith(":latest") or ":" not in image and "@" not in image):
            findings.append(f"WARN {service}: image is not explicitly version-pinned")
        if value.get("privileged") is True: findings.append(f"HIGH {service}: privileged mode is enabled")
        if str(value.get("network_mode","")).lower()=="host": findings.append(f"HIGH {service}: host network mode is enabled")
        ports=value.get("ports",[])
        if isinstance(ports,list):
            for port in ports:
                published_ports+=1
                source=str(port.get("published","") if isinstance(port,dict) else port)
                if source.startswith("0.0.0.0:") or source.startswith(":::"):
                    findings.append(f"WARN {service}: port binding listens on all interfaces")
        volumes=value.get("volumes",[])
        if isinstance(volumes,list):
            for volume in volumes:
                source=str(volume.get("source","") if isinstance(volume,dict) else volume).split(":")[0]
                if source=="/var/run/docker.sock" or source=="/":
                    findings.append(f"HIGH {service}: Docker socket or root host path is mounted ({source})")
        environment=value.get("environment",{})
        env_items=environment.items() if isinstance(environment,dict) else [(str(x).split("=",1)[0],str(x).split("=",1)[1] if "=" in str(x) else "") for x in environment] if isinstance(environment,list) else []
        for key,val in env_items:
            if _looks_secret_name(str(key)) and val not in (None,"") and not (isinstance(val,str) and re.fullmatch(r"\$\{[^}]+\}",val.strip())):
                secret_count+=1
                findings.append(f"HIGH {service}: secret-like environment key {key} appears to have a literal value (value omitted)")
    if document.get("version") is not None: findings.append("INFO: top-level version field is obsolete in modern Compose specification")
    lines=["Docker Compose static audit",f"Services: {len(services)}",f"Published port entries: {published_ports}",f"Literal secret-like values: {secret_count}",f"Findings: {len(findings)}"]
    lines.extend(findings or ["No baseline findings."])
    lines.append("Static YAML inspection only; no containers or commands were started.")
    return _write_text_artifact(p,"compose-audit","\n".join(lines)+"\n","Docker Compose audit")


def requirements_audit(p):
    raw=_read_text_source(p)
    seen={};unpinned=[];direct=[];invalid=[]
    for line_no,line in enumerate(raw.splitlines(),1):
        value=line.strip()
        if not value or value.startswith("#") or value.startswith(("-r ","--requirement ","-c ","--constraint ")): continue
        if value.startswith(("-","--")): continue
        if re.search(r"(?:git[+]|https?://|svn[+]|hg[+])",value,re.I):
            direct.append(line_no);continue
        match=re.match(r"^([A-Za-z0-9][A-Za-z0-9_.-]*)(.*)$",value)
        if not match: invalid.append(line_no);continue
        name=re.sub(r"[-_.]+","-",match.group(1)).lower()
        if name in seen: seen[name].append(line_no)
        else: seen[name]=[line_no]
        spec=match.group(2).split(";",1)[0].strip()
        if not (spec.startswith(("==","===")) and len(spec)>2 and spec[2].isalnum()): unpinned.append((line_no,name))
    duplicates={name:lines for name,lines in seen.items() if len(lines)>1}
    lines=["Python requirements audit",f"Requirement entries: {sum(len(v) for v in seen.values())}",f"Unique package names: {len(seen)}",f"Duplicate packages: {len(duplicates)}",f"Not exactly pinned: {len(unpinned)}",f"Direct URL/VCS references: {len(direct)}",f"Invalid lines: {len(invalid)}"]
    for name,locations in sorted(duplicates.items())[:80]: lines.append(f"DUPLICATE {name}: lines "+", ".join(map(str,locations)))
    for line_no,name in unpinned[:100]: lines.append(f"UNPINNED line {line_no}: {name}")
    if direct: lines.append("Direct URL/VCS line numbers: "+", ".join(map(str,direct[:100])))
    if invalid: lines.append("Invalid line numbers: "+", ".join(map(str,invalid[:100])))
    lines.append("Static review only; no package index, CVE database or dependency resolver was queried.")
    return _write_text_artifact(p,"requirements-audit","\n".join(lines)+"\n","requirements audit")


def package_json_audit(p):
    raw=_read_text_source(p)
    try: package=json.loads(raw)
    except Exception as exc: raise RuntimeError("Invalid package.json: "+str(exc)[:300]) from exc
    if not isinstance(package,dict): raise RuntimeError("package.json root must be an object.")
    findings=[]
    name=package.get("name")
    if not isinstance(name,str) or not name.strip(): findings.append("WARN: package name is missing")
    version=package.get("version")
    if not isinstance(version,str) or not version.strip(): findings.append("INFO: package version is not declared")
    groups=("dependencies","devDependencies","peerDependencies","optionalDependencies")
    total=0;wildcards=[];external=[];unpinned=[]
    for group in groups:
        values=package.get(group,{})
        if not isinstance(values,dict): findings.append(f"ERROR: {group} must be an object");continue
        for dep,spec in values.items():
            total+=1;value=str(spec).strip()
            if value in ("*","latest"): wildcards.append((group,dep))
            elif re.match(r"^(?:git[+]|https?://|github:|file:|link:|workspace:)",value,re.I): external.append((group,dep))
            elif not (value.startswith(("^","~","=",">","<","npm:")) or bool(value[:1].isdigit())): unpinned.append((group,dep))
    for group,dep in wildcards[:100]: findings.append(f"HIGH {group}: {dep} uses {package.get(group,{}).get(dep)}")
    for group,dep in external[:100]: findings.append(f"INFO {group}: {dep} uses a non-registry or workspace spec")
    for group,dep in unpinned[:100]: findings.append(f"WARN {group}: {dep} has an unrecognized version spec")
    scripts=package.get("scripts",{})
    dangerous=[]
    if isinstance(scripts,dict):
        for script,command in scripts.items():
            if isinstance(command,str) and re.search(r"(?:curl|wget)[^|;]*\|\s*(?:sh|bash)|\beval\s*\(",command,re.I):
                dangerous.append(script)
    for script in dangerous: findings.append(f"HIGH script {script}: download-to-shell or eval pattern")
    lines=["package.json static audit",f"Package: {name if isinstance(name,str) else '(missing)'}",f"Dependency entries: {total}",f"Wildcard/latest specs: {len(wildcards)}",f"Non-registry/workspace specs: {len(external)}",f"Unrecognized specs: {len(unpinned)}",f"Script patterns for review: {len(dangerous)}",f"Findings: {len(findings)}"]
    lines.extend(findings or ["No baseline findings."])
    lines.append("Static manifest inspection only; package scripts were not executed and no registry/CVE lookup was made.")
    return _write_text_artifact(p,"package-json-audit","\n".join(lines)+"\n","package.json audit")


def gitignore_audit(p):
    import fnmatch
    raw=_read_text_source(p)
    patterns=[line.strip() for line in raw.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    samples=[".env",".env.production",".dev.vars","id_rsa","server.pem",".npmrc"]
    def ignored(path):
        result=False
        for raw_pattern in patterns:
            negate=raw_pattern.startswith("!")
            pattern=raw_pattern[1:] if negate else raw_pattern
            pattern=pattern.lstrip("/")
            if not pattern: continue
            candidate=path
            matched=fnmatch.fnmatchcase(candidate,pattern)
            if "/" not in pattern:
                matched=matched or any(fnmatch.fnmatchcase(part,pattern) for part in candidate.split("/"))
            if matched: result=not negate
        return result
    missing=[path for path in samples if not ignored(path)]
    lines=["Git ignore baseline audit",f"Active non-comment rules: {len(patterns)}",f"Secret/config examples checked: {len(samples)}",f"Not ignored: {len(missing)}"]
    if missing: lines.extend("MISSING protection: "+name for name in missing)
    else: lines.append("All checked secret/config examples appear to be ignored.")
    lines.append("Approximate static matcher only; this is not Git's complete ignore evaluation or a check of the current index.")
    return _write_text_artifact(p,"gitignore-audit","\n".join(lines)+"\n","gitignore audit")


def env_reference_report(p):
    raw=_read_text_source(p)
    patterns=[
        re.compile(r"\bprocess\.env\.([A-Za-z_][A-Za-z0-9_]*)"),
        re.compile(r"\bimport\.meta\.env\.([A-Za-z_][A-Za-z0-9_]*)"),
        re.compile(r"\bos\.environ(?:\.get)?\s*\[\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]\s*\]"),
        re.compile(r"\bos\.getenv\s*\(\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]"),
        re.compile(r"\benv\.([A-Z][A-Z0-9_]*)\b"),
        re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")
    ]
    counts={}
    for pattern in patterns:
        for match in pattern.finditer(raw):
            name=next((value for value in match.groups() if value),None)
            if name: counts[name]=counts.get(name,0)+1
    lines=["Environment variable reference report",f"Unique names: {len(counts)}",f"Occurrences: {sum(counts.values())}"]
    lines.extend(f"{name}\t{count}" for name,count in sorted(counts.items())[:500])
    lines.append("Names and occurrence counts only; environment values are not read.")
    return _write_text_artifact(p,"env-references","\n".join(lines)+"\n","Environment variable references")





def _audit_write(p, tool_id, title, findings, summary=None):
    lines=[title]
    if summary: lines.extend(summary)
    lines.append("Findings: "+str(len(findings)))
    lines.extend(findings or ["No baseline findings."])
    lines.append("Static inspection only. No workflow, container, service or script was executed.")
    return _write_text_artifact(p,tool_id,"\n".join(lines)+"\n",title)


def github_actions_audit(p):
    import yaml
    raw=_read_text_source(p)
    try: workflow=yaml.load(raw,Loader=yaml.BaseLoader)
    except Exception as exc: raise RuntimeError("Invalid GitHub Actions YAML: "+str(exc)[:300]) from exc
    if not isinstance(workflow,dict): raise RuntimeError("GitHub Actions workflow root must be a mapping.")
    findings=[];jobs=workflow.get("jobs",{})
    if not isinstance(jobs,dict): raise RuntimeError("GitHub Actions workflow jobs must be a mapping.")
    perms=workflow.get("permissions")
    if perms in (None,"write-all"): findings.append("HIGH: workflow permissions are absent or write-all; set least privilege explicitly")
    elif isinstance(perms,dict) and any(str(v).lower()=="write-all" for v in perms.values()): findings.append("HIGH: workflow permissions include write-all")
    triggers=workflow.get("on",workflow.get(True,{}))
    if isinstance(triggers,dict) and "pull_request_target" in triggers: findings.append("HIGH: pull_request_target needs manual review for untrusted PR code")
    action_count=0;secret_runs=0;untrusted_runs=0
    for job_name,job in jobs.items():
        if not isinstance(job,dict): findings.append(f"ERROR: job {job_name} is not a mapping");continue
        if job.get("permissions")=="write-all": findings.append(f"HIGH job {job_name}: permissions are write-all")
        steps=job.get("steps",[])
        if not isinstance(steps,list): findings.append(f"ERROR job {job_name}: steps is not a list");continue
        for index,step in enumerate(steps,1):
            if not isinstance(step,dict): continue
            prefix=f"{job_name} step {index}";uses=step.get("uses")
            if isinstance(uses,str):
                action_count+=1
                if uses.startswith("docker://"):
                    image=uses[9:]
                    if (":" not in image and "@" not in image) or image.endswith(":latest"): findings.append(f"WARN {prefix}: Docker action image is not pinned")
                elif "@" in uses and not re.search(r"@[0-9a-f]{40}$",uses,re.I): findings.append(f"WARN {prefix}: action is not pinned to a full commit SHA")
                elif "@" not in uses: findings.append(f"WARN {prefix}: action reference has no immutable SHA")
            with_values=step.get("with",{})
            persisted=with_values.get("persist-credentials",step.get("persist-credentials","")) if isinstance(with_values,dict) else step.get("persist-credentials","")
            if str(persisted).lower()=="true": findings.append(f"WARN {prefix}: checkout persist-credentials is enabled")
            command=step.get("run")
            if isinstance(command,str):
                if re.search(r"\$\{\{\s*secrets\.[^}]+\}\}",command,re.I):
                    secret_runs+=1;findings.append(f"HIGH {prefix}: secret context is interpolated directly into a shell run block")
                if re.search(r"\$\{\{\s*github\.event\.(?:issue|pull_request)\.(?:title|body|head\.ref)",command,re.I):
                    untrusted_runs+=1;findings.append(f"HIGH {prefix}: untrusted event text is interpolated into a shell run block")
    return _audit_write(p,"gha-audit","GitHub Actions static audit",findings,
        [f"Jobs: {len(jobs)}",f"Action references: {action_count}",f"Run blocks with secret interpolation: {secret_runs}",f"Run blocks with untrusted event interpolation: {untrusted_runs}"])


def kubernetes_manifest_audit(p):
    import yaml
    raw=_read_text_source(p)
    try: docs=list(yaml.safe_load_all(raw))
    except Exception as exc: raise RuntimeError("Invalid Kubernetes YAML: "+str(exc)[:300]) from exc
    findings=[];objects=0;containers=0;secret_keys=0
    workloads={"Deployment","StatefulSet","DaemonSet","Job","ReplicaSet","ReplicationController"}
    for doc_no,doc in enumerate(docs,1):
        if doc is None: continue
        if not isinstance(doc,dict): findings.append(f"ERROR document {doc_no}: root is not a mapping");continue
        objects+=1;kind=str(doc.get("kind","unknown"))
        meta=doc.get("metadata") if isinstance(doc.get("metadata"),dict) else {}
        name=str(meta.get("name",f"document-{doc_no}"));spec=doc.get("spec") if isinstance(doc.get("spec"),dict) else {}
        pod={}
        if kind=="Pod": pod=spec
        elif kind in workloads:
            tmpl=spec.get("template",{})
            if isinstance(tmpl,dict) and isinstance(tmpl.get("spec"),dict): pod=tmpl["spec"]
        elif kind=="CronJob":
            job=spec.get("jobTemplate",{});job_spec=job.get("spec",{}) if isinstance(job,dict) else {}
            tmpl=job_spec.get("template",{}) if isinstance(job_spec,dict) else {}
            if isinstance(tmpl,dict) and isinstance(tmpl.get("spec"),dict): pod=tmpl["spec"]
        if kind=="Secret":
            data=doc.get("data",{});strings=doc.get("stringData",{})
            secret_keys+=len(data) if isinstance(data,dict) else 0
            secret_keys+=len(strings) if isinstance(strings,dict) else 0
            if data or strings: findings.append(f"WARN {name}: Secret contains values; verify encryption at rest/RBAC (values omitted)")
        if not isinstance(pod,dict) or not pod: continue
        pod_sec=pod.get("securityContext",{})
        if not isinstance(pod_sec,dict): pod_sec={}
        for field in ("hostNetwork","hostPID","hostIPC"):
            if pod.get(field) is True: findings.append(f"HIGH {name}: {field} is enabled")
        if pod_sec.get("runAsNonRoot") is not True: findings.append(f"WARN {name}: pod does not require runAsNonRoot")
        if pod_sec.get("seccompProfile") is None: findings.append(f"INFO {name}: seccompProfile is not explicit")
        for volume in pod.get("volumes",[]) if isinstance(pod.get("volumes",[]),list) else []:
            if isinstance(volume,dict) and isinstance(volume.get("hostPath"),dict):
                findings.append(f"HIGH {name}: hostPath volume is mounted ({volume['hostPath'].get('path','')})")
        items=[]
        for key in ("containers","initContainers","ephemeralContainers"):
            value=pod.get(key,[])
            if isinstance(value,list): items.extend(x for x in value if isinstance(x,dict))
        for container in items:
            containers+=1;prefix=f"{name}/{container.get('name','unnamed')}"
            image=str(container.get("image",""));last=image.rsplit("/",1)[-1]
            if image and (image.endswith(":latest") or (":" not in last and "@" not in image)): findings.append(f"WARN {prefix}: image is not pinned to a version or digest")
            sec=container.get("securityContext",{})
            if not isinstance(sec,dict): sec={}
            if sec.get("privileged") is True: findings.append(f"HIGH {prefix}: privileged container")
            if sec.get("allowPrivilegeEscalation") is not False: findings.append(f"WARN {prefix}: allowPrivilegeEscalation is not false")
            if sec.get("runAsNonRoot") is not True and pod_sec.get("runAsNonRoot") is not True: findings.append(f"WARN {prefix}: container does not require non-root execution")
            if sec.get("readOnlyRootFilesystem") is not True: findings.append(f"WARN {prefix}: root filesystem is not read-only")
            caps=sec.get("capabilities",{});added=caps.get("add",[]) if isinstance(caps,dict) else []
            if added: findings.append(f"HIGH {prefix}: Linux capabilities added: "+", ".join(map(str,added[:20])))
            resources=container.get("resources",{});limits=resources.get("limits",{}) if isinstance(resources,dict) else {}
            if not isinstance(limits,dict) or not {"cpu","memory"}.issubset(limits.keys()): findings.append(f"WARN {prefix}: CPU and memory limits are not both defined")
    return _audit_write(p,"k8s-audit","Kubernetes manifest static audit",findings,
        [f"YAML documents: {sum(1 for d in docs if d is not None)}",f"Objects: {objects}",f"Containers: {containers}",f"Secret keys counted (values omitted): {secret_keys}"])


def terraform_audit(p):
    raw=_read_text_source(p);findings=[]
    checks=[
        (r"\b(?:access_key|secret_key|password|client_secret|api_token)\s*=\s*['\"][^'\"]+['\"]","HIGH","credential-looking literal assignment; value omitted"),
        (r"\bcidr_blocks\s*=\s*\[[^\]]*['\"]0\.0\.0\.0/0['\"]","HIGH","public ingress CIDR 0.0.0.0/0"),
        (r"\bacl\s*=\s*['\"]public-(?:read|read-write)['\"]","HIGH","public S3 ACL"),
        (r"\b(?:storage_encrypted|encrypted)\s*=\s*false\b","HIGH","storage encryption explicitly disabled"),
        (r"\bpublicly_accessible\s*=\s*true\b","HIGH","database/service is publicly accessible"),
        (r"\bskip_final_snapshot\s*=\s*true\b","WARN","final database snapshot is skipped"),
        (r"\b(?:Action|actions)\s*=\s*\[[^\]]*['\"]\*['\"]","HIGH","wildcard IAM action"),
        (r"\bPrincipal\s*=\s*\{[^}]*AWS\s*=\s*['\"]\*['\"]","HIGH","wildcard IAM principal")
    ]
    for pattern,severity,label in checks:
        for match in re.finditer(pattern,raw,re.I|re.S if "Principal" in pattern else re.I):
            n=raw.count("\n",0,match.start())+1;findings.append(f"{severity} line {n}: {label}")
    if re.search(r"\bprovider\s+['\"][^'\"]+['\"]\s*\{",raw) and not re.search(r"\bversion\s*=\s*['\"][^'\"]+['\"]",raw):
        findings.append("WARN: provider version constraint was not found in this file; inspect required_providers")
    if not re.search(r"\bterraform\s*\{",raw): findings.append("INFO: terraform settings block is not present in this file")
    return _audit_write(p,"terraform-audit","Terraform static audit",findings,[f"Lines: {len(raw.splitlines())}"])


def nginx_config_audit(p):
    raw=_read_text_source(p);active=[]
    for n,line in enumerate(raw.splitlines(),1):
        value=line.split("#",1)[0].strip()
        if value: active.append((n,value))
    text="\n".join(v for _,v in active);findings=[]
    checks=[
        (r"^\s*server_tokens\s+on\b","WARN","server_tokens is enabled"),
        (r"^\s*autoindex\s+on\b","HIGH","directory autoindex is enabled"),
        (r"^\s*proxy_ssl_verify\s+off\b","HIGH","upstream TLS verification is disabled"),
        (r"^\s*ssl_protocols\b.*\b(?:SSLv3|TLSv1(?:\.0)?|TLSv1\.1)\b","HIGH","weak TLS protocol is enabled")
    ]
    for n,value in active:
        for pattern,severity,label in checks:
            if re.search(pattern,value,re.I): findings.append(f"{severity} line {n}: {label}")
    https=bool(re.search(r"^\s*listen\s+[^;]*(?:443|ssl)",text,re.I|re.M))
    if https and not re.search(r"^\s*ssl_certificate\s+",text,re.I|re.M): findings.append("HIGH: HTTPS listener has no ssl_certificate directive in this file")
    if https and not re.search(r"^\s*ssl_certificate_key\s+",text,re.I|re.M): findings.append("HIGH: HTTPS listener has no ssl_certificate_key directive in this file")
    if https and not re.search(r"^\s*add_header\s+Strict-Transport-Security\b",text,re.I|re.M): findings.append("INFO: HSTS header was not found")
    if not https: findings.append("WARN: no HTTPS listener was detected")
    if not re.search(r"^\s*client_max_body_size\s+",text,re.I|re.M): findings.append("INFO: client_max_body_size is not explicitly configured")
    return _audit_write(p,"nginx-audit","Nginx static audit",findings,[f"Active directives: {len(active)}",f"HTTPS listener: {str(https).lower()}"])


def apache_config_audit(p):
    raw=_read_text_source(p);active=[]
    for n,line in enumerate(raw.splitlines(),1):
        value=line.split("#",1)[0].strip()
        if value: active.append((n,value))
    text="\n".join(v for _,v in active);findings=[]
    checks=[
        (r"^\s*ServerTokens\s+(?:Full|OS)\b","WARN","ServerTokens exposes detailed server information"),
        (r"^\s*ServerSignature\s+On\b","WARN","ServerSignature is enabled"),
        (r"^\s*Options\b.*\bIndexes\b","HIGH","directory listing Indexes is enabled"),
        (r"^\s*AllowOverride\s+All\b","INFO","AllowOverride All increases per-directory configuration surface"),
        (r"^\s*TraceEnable\s+On\b","WARN","TRACE method is enabled"),
        (r"^\s*SSLProtocol\b.*(?<!-)\b(?:SSLv3|TLSv1(?:\.0)?|TLSv1\.1)\b","HIGH","weak TLS protocol is enabled")
    ]
    for n,value in active:
        for pattern,severity,label in checks:
            if re.search(pattern,value,re.I): findings.append(f"{severity} line {n}: {label}")
    tls=bool(re.search(r"^\s*SSLEngine\s+on\b",text,re.I|re.M))
    if tls and not re.search(r"^\s*Header\s+always\s+set\s+Strict-Transport-Security\b",text,re.I|re.M): findings.append("INFO: HSTS header was not found")
    if not re.search(r"^\s*ServerRoot\b",text,re.I|re.M): findings.append("INFO: ServerRoot is not defined in this file")
    return _audit_write(p,"apache-audit","Apache HTTPD static audit",findings,[f"Active directives: {len(active)}",f"TLS enabled: {str(tls).lower()}"])


def caddy_config_audit(p):
    raw=_read_text_source(p);active=[]
    for n,line in enumerate(raw.splitlines(),1):
        value=line.split("#",1)[0].strip()
        if value: active.append((n,value))
    text="\n".join(v for _,v in active);findings=[]
    for n,value in active:
        if re.search(r"^\s*auto_https\s+off\b",value,re.I): findings.append(f"HIGH line {n}: automatic HTTPS is disabled")
        if re.search(r"(?:tls_)?insecure_skip_verify\b",value,re.I): findings.append(f"HIGH line {n}: upstream TLS verification is disabled")
        if re.search(r"^\s*debug\b",value,re.I): findings.append(f"INFO line {n}: debug mode is enabled")
        if re.search(r"^\s*protocols?\s+.*\b(?:tls1\.0|tls1\.1)\b",value,re.I): findings.append(f"HIGH line {n}: weak TLS protocol is enabled")
    if re.search(r"\b:80\b",text) and not re.search(r"\b:443\b",text) and not re.search(r"^\s*auto_https\s+on\b",text,re.I|re.M):
        findings.append("WARN: HTTP listener detected without explicit HTTPS site/automatic HTTPS")
    if not re.search(r"\bStrict-Transport-Security\b",text,re.I): findings.append("INFO: HSTS header was not found")
    return _audit_write(p,"caddy-audit","Caddyfile static audit",findings,[f"Active lines: {len(active)}"])


def systemd_unit_audit(p):
    raw=_read_text_source(p);values={};sections=set();section=""
    for n,line in enumerate(raw.splitlines(),1):
        value=line.strip()
        if not value or value.startswith(("#",";")): continue
        if value.startswith("[") and value.endswith("]"):
            section=value[1:-1].strip();sections.add(section);continue
        if "=" not in value: continue
        key,val=value.split("=",1);values.setdefault((section,key.strip()),[]).append((n,val.strip()))
    service={key:items[-1] for (sec,key),items in values.items() if sec=="Service"};findings=[]
    def current(key): return service.get(key,(0,None))[1]
    def line_no(key): return service.get(key,(0,None))[0]
    user=current("User")
    if not user or user=="root": findings.append(f"WARN line {line_no('User') or 1}: service runs as root or does not specify User")
    if current("NoNewPrivileges")!="yes": findings.append(f"WARN line {line_no('NoNewPrivileges') or 1}: NoNewPrivileges=yes is not set")
    if current("ProtectSystem") not in ("strict","full"): findings.append(f"WARN line {line_no('ProtectSystem') or 1}: ProtectSystem=strict/full is not set")
    if current("ProtectHome") not in ("yes","read-only","tmpfs"): findings.append(f"INFO line {line_no('ProtectHome') or 1}: ProtectHome restriction is not set")
    if current("PrivateTmp")!="yes": findings.append(f"INFO line {line_no('PrivateTmp') or 1}: PrivateTmp=yes is not set")
    caps=current("CapabilityBoundingSet")
    if caps and re.search(r"\b(?:CAP_SYS_ADMIN|CAP_SYS_MODULE|CAP_SYS_RAWIO|ALL)\b",caps): findings.append(f"HIGH line {line_no('CapabilityBoundingSet')}: broad capability is granted")
    if re.search(r"(?:/bin/)?(?:ba)?sh\s+-c\b",current("ExecStart") or ""): findings.append(f"WARN line {line_no('ExecStart')}: ExecStart uses a shell -c wrapper")
    umask=current("UMask")
    if umask in ("000","0000","0002"): findings.append(f"WARN line {line_no('UMask')}: permissive UMask {umask}")
    return _audit_write(p,"systemd-audit","systemd unit static audit",findings,
        [f"Sections: {len(sections)}",f"Service directives: {len(service)}",f"User: {user or '(default root)'}"])


def shell_script_audit(p):
    raw=_read_text_source(p);findings=[]
    checks=[
        (r"\beval\s+","HIGH","eval executes dynamically constructed shell code"),
        (r"(?:curl|wget)[^\n;|]*\|\s*(?:sh|bash)\b","HIGH","download piped directly to a shell"),
        (r"\brm\s+-[^\n]*r[^\n]*f\s+/(?:\s|$)","HIGH","recursive deletion of filesystem root"),
        (r"\bchmod\s+(?:-R\s+)?777\b","HIGH","world-writable permissions granted"),
        (r"\bsource\s+<\(\s*(?:curl|wget)\b","HIGH","remote process substitution is sourced"),
        (r"\bsudo\b","INFO","script invokes sudo; review privilege boundary")
    ]
    for pattern,severity,label in checks:
        for match in re.finditer(pattern,raw,re.I):
            n=raw.count("\n",0,match.start())+1;findings.append(f"{severity} line {n}: {label}")
    secret_pattern=r"^\s*(?:export\s+)?([A-Z][A-Z0-9_]*(?:TOKEN|SECRET|PASSWORD|API_KEY|PRIVATE_KEY)[A-Z0-9_]*)\s*=\s*(['\"])[^'\"]+\2"
    for match in re.finditer(secret_pattern,raw,re.M|re.I):
        n=raw.count("\n",0,match.start())+1;findings.append(f"HIGH line {n}: credential-like variable {match.group(1)} has a literal value (value omitted)")
    if not re.search(r"^\s*set\s+-[^#\n]*[eE][^#\n]*[uU][^#\n]*[oO]",raw,re.M):
        findings.append("WARN: strict flags were not found; for Bash consider set -euo pipefail")
    if not re.search(r"^\s*trap\s+",raw,re.M) and re.search(r"\bmktemp\b",raw):
        findings.append("INFO: mktemp is used but no trap cleanup handler was found")
    return _audit_write(p,"shell-audit","Shell script static audit",findings,[f"Lines: {len(raw.splitlines())}",f"Shebang: {str(raw.startswith('#!')).lower()}"])


def docx_audit(p):
    from docx import Document
    doc=Document(p); paragraphs=doc.paragraphs
    if len(paragraphs)>20000 or len(doc.tables)>1000 or len(doc.inline_shapes)>2000:
        raise RuntimeError("DOCX vượt giới hạn cấu trúc kiểm tra.")
    heading_levels=[]; empty_headings=0; long_paragraphs=0
    for index,paragraph in enumerate(paragraphs,1):
        match=re.search(r"heading\s*([1-9])",str(getattr(paragraph.style,"name","") or ""),re.I)
        if match:
            if paragraph.text.strip(): heading_levels.append((index,int(match.group(1))))
            else: empty_headings+=1
        if len(paragraph.text)>1200: long_paragraphs+=1
    jumps=[]; previous=None
    for index,level in heading_levels:
        if previous is not None and level>previous[1]+1: jumps.append(f"paragraph {index}: Heading {previous[1]} -> Heading {level}")
        previous=(index,level)
    empty_tables=0; empty_headers=0; large_tables=0
    for table in doc.tables:
        if not table.rows: empty_tables+=1; continue
        if not any(cell.text.strip() for cell in table.rows[0].cells): empty_headers+=1
        if len(table.columns)>20 or len(table.rows)>2000: large_tables+=1
    images=len(doc.inline_shapes); missing_alt=0
    for shape in doc.inline_shapes:
        props=getattr(getattr(shape,"_inline",None),"docPr",None)
        if not str(getattr(props,"descr","") or "").strip() and not str(getattr(props,"title","") or "").strip(): missing_alt+=1
    links=[]; unsafe=0
    for relation in doc.part.rels.values():
        if not str(getattr(relation,"reltype","")).endswith("/hyperlink") or not getattr(relation,"is_external",False): continue
        links.append(relation)
        scheme=urllib.parse.urlsplit(str(getattr(relation,"target_ref","") or "")).scheme.lower()
        if scheme in {"javascript","data","file","vbscript"}: unsafe+=1
    try:
        insertions=len(doc.element.xpath(".//w:ins")); deletions=len(doc.element.xpath(".//w:del")); comments=len(doc.element.xpath(".//w:commentRangeStart"))
    except Exception:
        insertions=deletions=comments=0
    warnings=[]
    if not str(getattr(doc.core_properties,"title","") or "").strip(): warnings.append("Document title metadata is missing")
    if heading_levels and heading_levels[0][1]>1: warnings.append("First heading is not Heading 1")
    if not any(level==1 for _,level in heading_levels): warnings.append("No Heading 1 style found")
    if empty_headings: warnings.append(f"Empty heading paragraphs: {empty_headings}")
    if jumps: warnings.append(f"Heading hierarchy jumps: {len(jumps)}")
    if empty_headers: warnings.append(f"Tables with an empty first row: {empty_headers}")
    if empty_tables: warnings.append(f"Empty tables: {empty_tables}")
    if large_tables: warnings.append(f"Unusually large tables: {large_tables}")
    if missing_alt: warnings.append(f"Images missing alternative text: {missing_alt}/{images}")
    if unsafe: warnings.append(f"External hyperlinks with unsafe schemes: {unsafe}")
    if insertions or deletions: warnings.append("Tracked insertions/deletions are present")
    if comments: warnings.append(f"Comment range markers: {comments}")
    lines=[
        "DOCX structure and accessibility audit",
        f"Paragraphs: {len(paragraphs):,}; headings: {len(heading_levels):,}; tables: {len(doc.tables):,}; inline images: {images:,}",
        f"External hyperlinks: {len(links):,}; long paragraphs (>1,200 chars): {long_paragraphs:,}",
        f"Tables with empty first row: {empty_headers:,}; empty tables: {empty_tables:,}; unusually large tables: {large_tables:,}",
        f"Images without alt text: {missing_alt:,}; unsafe hyperlink schemes: {unsafe:,}",
        f"Tracked insertions: {insertions:,}; tracked deletions: {deletions:,}; comment range markers: {comments:,}",
        f"Heading hierarchy jumps: {len(jumps):,}","", "Review findings:"
    ]
    lines.extend("- "+item for item in warnings)
    if not warnings: lines.append("- No configured structural warning was detected.")
    lines.extend(["","Static structure check only; not a Word renderer or full WCAG certification. Paragraph and table contents are omitted."])
    return tool_text("\n".join(lines),"DOCX audit")


def pptx_audit(p):
    from pptx import Presentation
    from pptx.enum.shapes import MSO_SHAPE_TYPE
    presentation=Presentation(p)
    if len(presentation.slides)>300: raise RuntimeError("PPTX vượt giới hạn 300 slide.")
    missing_titles=[]; empty_slides=[]; dense=[]; long_titles=[]; repeated={}
    small_runs=0; images=0; missing_alt=0; total_words=0; slide_rows=[]
    for number,slide in enumerate(presentation.slides,1):
        title_shape=slide.shapes.title
        title=str(title_shape.text or "").strip() if title_shape is not None else ""
        if not title: missing_titles.append(number)
        elif len(title)>100: long_titles.append(number)
        else: repeated[title.casefold()]=repeated.get(title.casefold(),0)+1
        words=0; text_shapes=0; slide_images=0; slide_small=0
        for shape in slide.shapes:
            if getattr(shape,"has_text_frame",False):
                value=str(getattr(shape,"text","") or "").strip()
                if value:
                    text_shapes+=1; words+=len(re.findall(r"\b[\w'-]+\b",value,re.UNICODE))
                for paragraph in shape.text_frame.paragraphs:
                    for run in paragraph.runs:
                        size=getattr(getattr(run,"font",None),"size",None)
                        if size is not None and getattr(size,"pt",99)<12: slide_small+=1
            if getattr(shape,"shape_type",None)==MSO_SHAPE_TYPE.PICTURE:
                images+=1; slide_images+=1
                try:
                    nodes=shape._element.xpath(".//p:cNvPr")
                    if nodes and not any((node.get("descr") or node.get("title") or "").strip() for node in nodes): missing_alt+=1
                except Exception: missing_alt+=1
        total_words+=words; small_runs+=slide_small
        if words==0 and slide_images==0: empty_slides.append(number)
        if words>150: dense.append(number)
        slide_rows.append(f"Slide {number}: title={'present' if title else 'missing'}; words={words}; text-shapes={text_shapes}; images={slide_images}; explicit font runs <12pt={slide_small}")
    repeated_titles=sum(1 for count in repeated.values() if count>1)
    lines=[
        "PPTX slide structure and readability audit",
        f"Slides: {len(presentation.slides):,}; total words: {total_words:,}; images: {images:,}",
        f"Slides without a title placeholder/text: {len(missing_titles):,}",
        f"Slides with no detected text or picture content: {len(empty_slides):,}",
        f"Slides over 150 words (density heuristic): {len(dense):,}",
        f"Repeated non-empty slide titles: {repeated_titles:,}",
        f"Titles over 100 characters: {len(long_titles):,}",
        f"Explicit text runs smaller than 12 pt: {small_runs:,}",
        f"Images without alternative text: {missing_alt:,}/{images:,}","",
        "Per-slide summary:",*slide_rows,"",
        "Flagged slide numbers (1-based):",
        "Missing titles: "+(", ".join(map(str,missing_titles[:100])) if missing_titles else "none"),
        "No detected text/picture: "+(", ".join(map(str,empty_slides[:100])) if empty_slides else "none"),
        "Dense text: "+(", ".join(map(str,dense[:100])) if dense else "none"),
        "Long titles: "+(", ".join(map(str,long_titles[:100])) if long_titles else "none"),"",
        "Static audit only: no rendering, theme/master font inheritance, overlap or text clipping is evaluated. Density and 12 pt thresholds are review heuristics; slide text is omitted."
    ]
    return tool_text("\n".join(lines),"PPTX audit")


def csv_privacy_audit(p):
    import ipaddress
    email_re=re.compile(r"(?i)(?<![\w.+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?![\w.-])")
    card_re=re.compile(r"(?<!\d)(?:\d[ -]?){12,18}\d(?!\d)")
    ipv4_re=re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")
    sensitive_re=re.compile(r"(?:password|passwd|secret|token|api[_-]?key|access[_-]?key|email|e[_-]?mail|phone|mobile|telephone|address|street|postal|date[_-]?of[_-]?birth|dob|birth|passport|national[_-]?id|citizen[_-]?id|ssn|credit[_-]?card|card[_-]?number|iban|bank[_-]?account|tax[_-]?id|full[_-]?name|first[_-]?name|last[_-]?name)",re.I)
    phone_re=re.compile(r"(?:phone|mobile|telephone|tel)",re.I)
    counts={}; row_samples={}; sensitive_columns=[]
    def add(index,kind,row_number):
        key=(index,kind); counts[key]=counts.get(key,0)+1
        rows=row_samples.setdefault(key,[])
        if len(rows)<5 and row_number not in rows: rows.append(row_number)
    with p.open("r",encoding="utf-8-sig",errors="replace",newline="") as source:
        sample=source.read(65536); source.seek(0)
        try: dialect=csv.Sniffer().sniff(sample,delimiters=",;\t|")
        except csv.Error: dialect=csv.excel
        reader=csv.reader(source,dialect)
        headers=next(reader,None)
        if not headers: raise RuntimeError("CSV không có header.")
        if len(headers)>200: raise RuntimeError("CSV vượt giới hạn 200 cột.")
        normalized=[]
        for index,header in enumerate(headers):
            label=str(header or "").strip()[:80] or f"Column {index+1}"
            normalized.append(label)
            if sensitive_re.search(re.sub(r"([a-z])([A-Z])",r"\1_\2",label)): sensitive_columns.append(index)
        seen_rows=0
        for row_number,row in enumerate(reader,2):
            seen_rows+=1
            if seen_rows>50000: raise RuntimeError("CSV privacy audit vượt giới hạn 50.000 dòng.")
            if len(row)>200: raise RuntimeError("CSV có dòng vượt giới hạn 200 cột.")
            for index,value in enumerate(row[:len(headers)]):
                value=str(value or "").strip()
                if not value: continue
                header=normalized[index]; candidate=value[:10000]
                if index in sensitive_columns: add(index,"sensitive-column",row_number)
                if email_re.search(candidate): add(index,"email-like",row_number)
                for match in card_re.finditer(candidate):
                    digits=re.sub(r"\D","",match.group(0))
                    if not 13<=len(digits)<=19: continue
                    total=0; parity=len(digits)%2
                    for position,char in enumerate(digits):
                        number=int(char)
                        if position%2==parity:
                            number*=2
                            if number>9: number-=9
                        total+=number
                    if total%10==0: add(index,"payment-card-like (Luhn)",row_number)
                for match in ipv4_re.finditer(candidate):
                    try: ipaddress.ip_address(match.group(0)); add(index,"IPv4 address",row_number)
                    except ValueError: pass
                if phone_re.search(header):
                    digits=re.sub(r"\D","",candidate)
                    if 9<=len(digits)<=15 and len(set(digits))>1: add(index,"phone-like",row_number)
    lines=["CSV privacy / sensitive-data audit",f"Rows scanned: {seen_rows:,}; columns: {len(headers):,}",
        "Detected values are never copied into this report.","","Findings by column:"]
    findings=0
    for index,label in enumerate(normalized):
        items=[(kind,count) for (column,kind),count in counts.items() if column==index]
        if not items: continue
        findings+=len(items)
        lines.append(f"- Column {index+1} [{label}]: "+", ".join(f"{kind}={count:,} (rows {','.join(map(str,row_samples[(index,kind)]))})" for kind,count in sorted(items)))
    if not findings: lines.append("- No supported pattern or sensitive-header signal detected.")
    lines.extend(["",f"Columns with sensitive-looking headers: {len(sensitive_columns):,}",
        "Detection is heuristic: phone-like matches and sensitive headers are not proof of personal data; unsupported formats may be missed. Raw cell values are never included."])
    return tool_text("\n".join(lines),"CSV privacy audit")


def archive_security_audit(p):
    findings=[]; counters={}; seen_exact={}; seen_folded={}; total_uncompressed=0; scanned=0
    def add(kind,level,name,detail=""):
        counters[kind]=counters.get(kind,0)+1
        if len(findings)<250: findings.append(f"[{level}] {kind}: {str(name)[:180]}"+(f" — {detail}" if detail else ""))
    def inspect_name(raw):
        raw=str(raw or ""); normalized=raw.replace("\\","/")
        parts=[part for part in normalized.split("/") if part not in ("",".")]
        canonical="/".join(parts).rstrip("/")
        if "\x00" in raw: add("NUL byte in path","HIGH",raw)
        if normalized.startswith("/") or re.match(r"^[A-Za-z]:",normalized): add("absolute or drive-qualified path","HIGH",raw)
        if ".." in parts: add("path traversal segment","HIGH",raw)
        folded=canonical.casefold()
        if canonical in seen_exact: add("duplicate archive path","MEDIUM",raw)
        elif folded in seen_folded: add("case-insensitive path collision","MEDIUM",raw,f"collides with {seen_folded[folded][:120]}")
        if canonical: seen_exact[canonical]=True; seen_folded.setdefault(folded,canonical)
        suffixes={suffix.lower() for suffix in Path(normalized).suffixes}
        if suffixes.intersection({".exe",".dll",".sys",".scr",".bat",".cmd",".ps1",".vbs"}): add("executable or script file","MEDIUM",raw)
        if suffixes.intersection({".zip",".tar",".gz",".tgz",".7z",".rar"}): add("nested archive","INFO",raw)
    is_zip=zipfile.is_zipfile(p)
    try:
        if is_zip:
            with zipfile.ZipFile(p) as archive:
                infos=archive.infolist()
                if len(infos)>10000: raise RuntimeError("Archive vượt giới hạn 10.000 entry; từ chối quét.")
                for item in infos:
                    scanned+=1; inspect_name(item.filename)
                    if item.is_dir(): continue
                    total_uncompressed+=max(0,int(item.file_size))
                    mode=(item.external_attr>>16)&0xFFFF
                    if stat.S_ISLNK(mode): add("symbolic link","HIGH",item.filename)
                    elif stat.S_IFMT(mode) and not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)): add("special filesystem entry","HIGH",item.filename)
                    if item.flag_bits&0x1: add("encrypted member","HIGH",item.filename)
                    if item.file_size>100*1024*1024: add("member exceeds 100 MiB","HIGH",item.filename)
                    if item.file_size>=1024*1024 and item.file_size/max(1,item.compress_size)>100:
                        add("extreme compression ratio","HIGH",item.filename,f"{item.file_size/max(1,item.compress_size):.1f}:1")
        else:
            with tarfile.open(p,"r:*") as archive:
                for item in archive:
                    scanned+=1
                    if scanned>10000: raise RuntimeError("Archive vượt giới hạn 10.000 entry; từ chối quét.")
                    inspect_name(item.name)
                    if item.issym() or item.islnk(): add("link entry","HIGH",item.name)
                    elif not (item.isfile() or item.isdir()): add("special filesystem entry","HIGH",item.name)
                    if item.isfile():
                        total_uncompressed+=max(0,int(item.size))
                        if item.size>100*1024*1024: add("member exceeds 100 MiB","HIGH",item.name)
    except RuntimeError: raise
    except (zipfile.BadZipFile,tarfile.TarError,OSError) as exc:
        raise RuntimeError("Tệp không phải ZIP/TAR được hỗ trợ hoặc archive bị lỗi.") from exc
    if total_uncompressed>500*1024*1024: add("declared expanded size exceeds 500 MiB","HIGH",p.name,f"{total_uncompressed:,} bytes")
    lines=["Archive security preflight (no extraction performed)",f"Format: {'ZIP' if is_zip else 'TAR'}; entries inspected: {scanned:,}",
        f"Archive bytes: {p.stat().st_size:,}; declared uncompressed file bytes: {total_uncompressed:,}",
        f"Finding records: {len(findings):,}; finding categories: {len(counters):,}","","Counts by category:"]
    lines.extend(f"- {kind}: {count:,}" for kind,count in sorted(counters.items()))
    lines.extend(["","Findings (paths only; no file content read):"])
    lines.extend(findings or ["- No configured archive-risk signals detected."])
    lines.extend(["","Bounded metadata preflight, not malware scanning. Executable/script extensions are review signals, not proof of malicious content."])
    return tool_text("\n".join(lines),"Archive security audit")


def xlsx_privacy_audit(p):
    from openpyxl import load_workbook
    workbook=load_workbook(p,read_only=True,data_only=True,keep_links=False)
    counts={}; samples={}; sensitive_columns=[]; hidden_sheets=[]; total_cells=0; scanned_cells=0
    email_re=re.compile(r"(?i)(?<![\w.+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?![\w.-])")
    card_re=re.compile(r"(?<!\d)(?:\d[ -]?){12,18}\d(?!\d)")
    ipv4_re=re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")
    phone_re=re.compile(r"(?:phone|mobile|telephone|tel|sdt|so_dien_thoai)",re.I)
    sensitive_re=re.compile(r"(?:password|passwd|secret|token|api[_-]?key|access[_-]?key|email|e[_-]?mail|phone|mobile|telephone|address|street|postal|date[_-]?of[_-]?birth|dob|birth|passport|national[_-]?id|citizen[_-]?id|ssn|credit[_-]?card|card[_-]?number|iban|bank[_-]?account|tax[_-]?id|full[_-]?name|first[_-]?name|last[_-]?name)",re.I)
    credential_re=re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,})")
    def add(sheet,column,kind,coordinate):
        key=(sheet,column,kind); counts[key]=counts.get(key,0)+1
        locations=samples.setdefault(key,[])
        if len(locations)<5 and coordinate not in locations: locations.append(coordinate)
    try:
        if len(workbook.worksheets)>100: raise RuntimeError("Workbook vượt giới hạn 100 sheet.")
        for sheet in workbook.worksheets:
            if sheet.sheet_state!="visible": hidden_sheets.append(sheet.title)
            rows=sheet.max_row or 0; cols=sheet.max_column or 0
            if rows>50000 or cols>200: raise RuntimeError(f"Sheet {sheet.title[:80]} vượt giới hạn 50.000 dòng hoặc 200 cột.")
            declared=rows*cols
            total_cells+=declared
            if total_cells>2_000_000: raise RuntimeError("Workbook vượt giới hạn 2.000.000 ô khai báo.")
            if rows==0 or cols==0: continue
            iterator=sheet.iter_rows(min_row=1,max_row=rows,max_col=cols,values_only=False)
            header_row=next(iterator,None)
            if header_row is None: continue
            headers=[]
            for index,cell in enumerate(header_row,1):
                label=str(cell.value or "").strip()[:80] or f"Column {index}"
                headers.append(label)
                if sensitive_re.search(re.sub(r"([a-z])([A-Z])",r"\1_\2",label)):
                    sensitive_columns.append((sheet.title,index,label))
            for row in iterator:
                for index,cell in enumerate(row,1):
                    scanned_cells+=1
                    if scanned_cells>2_000_000: raise RuntimeError("Workbook vượt giới hạn 2.000.000 ô quét.")
                    value=cell.value
                    if value is None: continue
                    candidate=str(value).strip()[:10000]
                    if not candidate: continue
                    header=headers[index-1] if index-1<len(headers) else f"Column {index}"
                    if sensitive_re.search(re.sub(r"([a-z])([A-Z])",r"\1_\2",header)):
                        add(sheet.title,index,"sensitive-column",cell.coordinate)
                    if email_re.search(candidate): add(sheet.title,index,"email-like",cell.coordinate)
                    if credential_re.search(candidate): add(sheet.title,index,"credential-like",cell.coordinate)
                    for match in card_re.finditer(candidate):
                        digits=re.sub(r"\D","",match.group(0))
                        if not 13<=len(digits)<=19: continue
                        total=0; parity=len(digits)%2
                        for position,char in enumerate(digits):
                            number=int(char)
                            if position%2==parity:
                                number*=2
                                if number>9: number-=9
                            total+=number
                        if total%10==0: add(sheet.title,index,"payment-card-like (Luhn)",cell.coordinate)
                    for match in ipv4_re.finditer(candidate):
                        try:
                            import ipaddress
                            ipaddress.ip_address(match.group(0))
                            add(sheet.title,index,"IPv4 address",cell.coordinate)
                        except ValueError:
                            pass
                    if phone_re.search(header):
                        digits=re.sub(r"\D","",candidate)
                        if 9<=len(digits)<=15 and len(set(digits))>1: add(sheet.title,index,"phone-like",cell.coordinate)
    finally:
        workbook.close()
    lines=[
        "XLSX privacy / sensitive-data audit",
        f"Sheets: {len(workbook.sheetnames):,}; non-empty cells scanned: {scanned_cells:,}; declared cell area: {total_cells:,}",
        f"Hidden or very-hidden sheets: {len(hidden_sheets):,}",
        "Only cached formula values are inspected; formula cells without cached results may be missed.",
        "Raw cell values are never copied into this report.",
        "",
        "Findings by sheet and column:"
    ]
    if counts:
        by_sheet={}
        for (sheet,column,kind),count in counts.items():
            by_sheet.setdefault((sheet,column),[]).append((kind,count))
        for (sheet,column),items in sorted(by_sheet.items()):
            label=next((name for s,index,name in sensitive_columns if s==sheet and index==column),"")
            suffix=f" [{label}]" if label else ""
            lines.append(f"- Sheet {sheet}; column {column}{suffix}: "+", ".join(f"{kind}={count:,} (cells {','.join(samples[(sheet,column,kind)])})" for kind,count in sorted(items)))
    else:
        lines.append("- No supported pattern or sensitive-header signal detected.")
    lines.extend(["","Hidden sheet names: "+(", ".join(hidden_sheets[:50]) if hidden_sheets else "none"),
        "Detection is heuristic: header and phone signals can produce false positives/negatives. Workbook formulas are not recalculated and raw cell content is omitted."])
    return tool_text("\n".join(lines),"XLSX privacy audit")


def pdf_privacy_audit(p):
    import fitz
    email_re=re.compile(r"(?i)(?<![\w.+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?![\w.-])")
    card_re=re.compile(r"(?<!\d)(?:\d[ -]?){12,18}\d(?!\d)")
    ipv4_re=re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")
    phone_re=re.compile(r"(?i)(?:phone|mobile|telephone|tel|sdt|so dien thoai|điện thoại)\D{0,20}(\+?[\d][\d\s().-]{7,20})")
    id_re=re.compile(r"(?i)(?:CCCD|CMND|passport|national\s*ID|tax\s*ID)\D{0,20}([A-Z0-9-]{8,16})")
    credential_re=re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,})")
    counts={}; samples={}; total_chars=0
    def add(page,kind):
        key=(page,kind); counts[key]=counts.get(key,0)+1
        if len(samples.setdefault(key,[]))<5: samples[key].append(page)
    document=fitz.open(p)
    try:
        if document.page_count>300: raise RuntimeError("PDF vượt giới hạn 300 trang.")
        for number,page in enumerate(document,1):
            text_value=page.get_text("text") or ""
            total_chars+=len(text_value)
            if total_chars>2_000_000: raise RuntimeError("PDF vượt giới hạn 2.000.000 ký tự text layer.")
            for _ in email_re.finditer(text_value): add(number,"email-like")
            for _ in credential_re.finditer(text_value): add(number,"credential-like")
            for match in card_re.finditer(text_value):
                digits=re.sub(r"\D","",match.group(0))
                if not 13<=len(digits)<=19: continue
                total=0; parity=len(digits)%2
                for position,char in enumerate(digits):
                    digit=int(char)
                    if position%2==parity:
                        digit*=2
                        if digit>9: digit-=9
                    total+=digit
                if total%10==0: add(number,"payment-card-like (Luhn)")
            for match in ipv4_re.finditer(text_value):
                try:
                    import ipaddress
                    ipaddress.ip_address(match.group(0))
                    add(number,"IPv4 address")
                except ValueError:
                    pass
            for match in phone_re.finditer(text_value):
                digits=re.sub(r"\D","",match.group(1))
                if 9<=len(digits)<=15 and len(set(digits))>1: add(number,"phone-like")
            for _ in id_re.finditer(text_value): add(number,"identity-document-like")
        page_count=document.page_count
    finally:
        document.close()
    lines=[
        "PDF privacy / sensitive-data audit",
        f"Pages scanned: {page_count:,}; extracted text characters: {total_chars:,}",
        "Only the existing PDF text layer is inspected; no OCR is performed.",
        "Raw detected values and surrounding text are never included in this report.",
        "",
        "Findings by page:"
    ]
    if counts:
        by_page={}
        for (page,kind),count in counts.items(): by_page.setdefault(page,[]).append((kind,count))
        for page,items in sorted(by_page.items()):
            lines.append(f"- Page {page}: "+", ".join(f"{kind}={count:,}" for kind,count in sorted(items)))
    else:
        lines.append("- No supported pattern detected in the text layer.")
    total_findings=sum(counts.values())
    lines.extend(["",f"Total finding occurrences: {total_findings:,}",
        "Heuristic findings are not proof of identity or payment data. Scanned/image-only pages and unsupported formats may contain undetected information."])
    return tool_text("\n".join(lines),"PDF privacy audit")


def office_active_content_audit(p):
    import xml.etree.ElementTree as ET
    if not zipfile.is_zipfile(p):
        raise RuntimeError("Tệp không phải gói Office OOXML ZIP hợp lệ.")
    counters={}
    external_by_type={}
    unsafe_schemes={}
    total_uncompressed=0
    xml_bytes_read=0
    parsed_relationships=0
    malformed_relationships=0
    encrypted_members=0
    path_traversal=0
    macro_enabled_content_types=0
    macro_members=0
    embedded_objects=0
    activex_objects=0
    custom_ui_parts=0
    external_workbook_links=0
    external_connections=0
    def add(name,count=1):
        counters[name]=counters.get(name,0)+count
    with zipfile.ZipFile(p) as archive:
        infos=archive.infolist()
        if len(infos)>20000:
            raise RuntimeError("Gói Office vượt giới hạn 20.000 thành phần.")
        for info in infos:
            name=str(info.filename or "")
            normalized=name.replace("\\","/")
            parts=[part for part in normalized.split("/") if part not in ("",".")]
            if normalized.startswith("/") or re.match(r"^[A-Za-z]:",normalized) or ".." in parts:
                path_traversal+=1
            if info.flag_bits&0x1:
                encrypted_members+=1
            total_uncompressed+=max(0,int(info.file_size))
            lower=normalized.lower()
            base=Path(lower).name
            if base=="vbaproject.bin" or "vba/" in lower and base.endswith(".bin"):
                macro_members+=1
            if "/activex/" in "/"+lower or lower.startswith("activex/"):
                activex_objects+=1
            if "/embeddings/" in "/"+lower or lower.startswith("embeddings/") or "oleobject" in base:
                embedded_objects+=1
            if lower.startswith("customui/") or "/customui/" in lower:
                custom_ui_parts+=1
            if lower.startswith("xl/externallinks/") or "/externallinks/" in lower:
                external_workbook_links+=1
            if lower.startswith("xl/externalconnections/") or "/externalconnections/" in lower:
                external_connections+=1
        if total_uncompressed>500*1024*1024:
            raise RuntimeError("Gói Office có kích thước giải nén khai báo vượt 500 MiB.")
        rel_files=[item for item in infos if item.filename.lower().endswith(".rels")]
        if len(rel_files)>2000:
            raise RuntimeError("Gói Office có quá nhiều relationships để kiểm tra an toàn.")
        for item in rel_files:
            if item.file_size>2*1024*1024:
                add("oversized_relationship_xml")
                continue
            if xml_bytes_read+item.file_size>12*1024*1024:
                add("relationship_xml_read_limit_reached")
                break
            raw=archive.read(item)
            xml_bytes_read+=len(raw)
            upper=raw.upper()
            if b"<!DOCTYPE" in upper or b"<!ENTITY" in upper:
                malformed_relationships+=1
                add("relationship_xml_with_doctype_or_entity")
                continue
            try:
                root=ET.fromstring(raw)
            except (ET.ParseError,ValueError):
                malformed_relationships+=1
                add("malformed_relationship_xml")
                continue
            for relation in root.iter():
                if not str(relation.tag).lower().endswith("}relationship") and str(relation.tag).lower()!="relationship":
                    continue
                parsed_relationships+=1
                target_mode=str(relation.attrib.get("TargetMode","")).strip().lower()
                if target_mode!="external":
                    continue
                relation_type=str(relation.attrib.get("Type","") or "")
                relation_kind=relation_type.rsplit("/",1)[-1].lower() or "unknown"
                external_by_type[relation_kind]=external_by_type.get(relation_kind,0)+1
                target=str(relation.attrib.get("Target","") or "")
                scheme=urllib.parse.urlsplit(target).scheme.lower()
                if scheme in {"javascript","data","file","vbscript","ms-msdt","shell","command"}:
                    unsafe_schemes[scheme]=unsafe_schemes.get(scheme,0)+1
        content_types=next((item for item in infos if item.filename.lower()=="[content_types].xml"),None)
        if content_types:
            if content_types.file_size>2*1024*1024:
                add("oversized_content_types_xml")
            elif xml_bytes_read+content_types.file_size<=12*1024*1024:
                raw=archive.read(content_types)
                xml_bytes_read+=len(raw)
                if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
                    add("content_types_xml_with_doctype_or_entity")
                else:
                    try:
                        root=ET.fromstring(raw)
                        for element in root.iter():
                            content_type=str(element.attrib.get("ContentType","")).lower()
                            part_name=str(element.attrib.get("PartName","")).lower()
                            if "macroenabled" in content_type or "vbaproject" in content_type:
                                macro_enabled_content_types+=1
                            if "externallink" in part_name:
                                external_workbook_links=max(external_workbook_links,1)
                    except (ET.ParseError,ValueError):
                        add("malformed_content_types_xml")
    if macro_members: add("vba_project_binary",macro_members)
    if macro_enabled_content_types: add("macro_enabled_content_types",macro_enabled_content_types)
    if activex_objects: add("activex_object_parts",activex_objects)
    if embedded_objects: add("embedded_or_ole_parts",embedded_objects)
    if custom_ui_parts: add("custom_ui_parts",custom_ui_parts)
    if external_workbook_links: add("external_workbook_link_parts",external_workbook_links)
    if external_connections: add("external_connection_parts",external_connections)
    if encrypted_members: add("encrypted_zip_members",encrypted_members)
    if path_traversal: add("unsafe_package_paths",path_traversal)
    if malformed_relationships: add("relationship_xml_parse_findings",malformed_relationships)
    if unsafe_schemes:
        for scheme,count in unsafe_schemes.items(): add("external_relationship_unsafe_scheme_"+scheme,count)
    lines=[
        "Office OOXML active-content security audit",
        f"Archive entries: {len(infos):,}; declared uncompressed size: {total_uncompressed:,} bytes",
        f"Relationship parts parsed: {len(rel_files)-malformed_relationships:,}; relationships inspected: {parsed_relationships:,}",
        f"External relationships: {sum(external_by_type.values()):,}; unsafe external schemes: {sum(unsafe_schemes.values()):,}",
        f"VBA project binaries: {macro_members:,}; macro-enabled content types: {macro_enabled_content_types:,}",
        f"ActiveX parts: {activex_objects:,}; embedded/OLE parts: {embedded_objects:,}; custom UI parts: {custom_ui_parts:,}",
        f"External workbook-link parts: {external_workbook_links:,}; external connection parts: {external_connections:,}",
        f"Encrypted members: {encrypted_members:,}; suspicious package paths: {path_traversal:,}",
        "",
        "External relationship types:"
    ]
    if external_by_type:
        lines.extend(f"- {kind}: {count:,}" for kind,count in sorted(external_by_type.items()))
    else:
        lines.append("- None detected")
    lines.extend(["","Review signals:"])
    findings=[]
    if macro_members or macro_enabled_content_types: findings.append("VBA or macro-enabled package markers are present; do not enable macros unless the source is trusted.")
    if activex_objects: findings.append("ActiveX components are present.")
    if embedded_objects: findings.append("Embedded or OLE objects are present; this audit does not inspect or open them.")
    if external_by_type: findings.append("The document contains external relationships which may cause network access or linked-content loading.")
    if unsafe_schemes: findings.append("External relationships use potentially unsafe URI schemes.")
    if custom_ui_parts: findings.append("Custom Office UI parts are present.")
    if encrypted_members: findings.append("One or more ZIP members are encrypted and could not be inspected.")
    if path_traversal: findings.append("Package contains absolute or traversal-like member paths.")
    if malformed_relationships: findings.append("One or more relationship XML parts were malformed or used forbidden DTD/entity declarations.")
    lines.extend("- "+finding for finding in findings or ["No configured active-content indicator was detected."])
    lines.extend(["","Static metadata/XML inspection only. No macro, ActiveX, OLE object, embedded file, link target or external resource was executed, opened or downloaded. This is not malware scanning or a guarantee that a document is safe."])
    return tool_text("\n".join(lines),"Office active-content audit")


def pdf_active_content_audit(p):
    import fitz
    document=fitz.open(p)
    try:
        if document.is_encrypted and document.needs_pass:
            raise RuntimeError("PDF được mã hóa bằng mật khẩu; không thể kiểm tra object graph.")
        if document.page_count>300:
            raise RuntimeError("PDF active-content audit giới hạn 300 trang.")
        xref_length=document.xref_length()
        if xref_length>15000:
            raise RuntimeError("PDF vượt giới hạn 15.000 indirect objects.")
        total_object_chars=0
        scanned_objects=0
        oversized_objects=0
        token_patterns={
            "JavaScript action":re.compile(r"/JavaScript\b"),
            "JS action payload":re.compile(r"/JS\b"),
            "OpenAction":re.compile(r"/OpenAction\b"),
            "Additional Actions":re.compile(r"/AA\b"),
            "Launch action":re.compile(r"/Launch\b"),
            "EmbeddedFiles name tree":re.compile(r"/EmbeddedFiles\b"),
            "File specification":re.compile(r"/Filespec\b"),
            "RichMedia":re.compile(r"/RichMedia\b"),
            "AcroForm":re.compile(r"/AcroForm\b"),
            "XFA form":re.compile(r"/XFA\b"),
            "SubmitForm action":re.compile(r"/SubmitForm\b"),
            "ImportData action":re.compile(r"/ImportData\b"),
            "Remote GoTo action":re.compile(r"/GoToR\b"),
            "URI action":re.compile(r"/URI\b"),
            "Rendition or media action":re.compile(r"/(?:Rendition|Movie|Sound|3D)\b"),
            "Collection or portfolio":re.compile(r"/Collection\b"),
        }
        token_objects={name:0 for name in token_patterns}
        for xref in range(1,xref_length):
            try:
                obj=document.xref_object(xref,compressed=False) or ""
            except Exception:
                continue
            scanned_objects+=1
            total_object_chars+=len(obj)
            if total_object_chars>3_000_000:
                raise RuntimeError("PDF vượt giới hạn 3.000.000 ký tự object metadata.")
            if len(obj)>65536:
                oversized_objects+=1
                obj=obj[:65536]
            for name,pattern in token_patterns.items():
                if pattern.search(obj):
                    token_objects[name]+=1
        uri_links=0
        launch_links=0
        remote_goto_links=0
        unsafe_uri_links=0
        widgets=0
        for page in document:
            try:
                links=page.get_links() or []
            except Exception:
                links=[]
            for link in links:
                kind=link.get("kind")
                if kind==getattr(fitz,"LINK_URI",-100):
                    uri_links+=1
                    uri=str(link.get("uri","") or "")
                    scheme=urllib.parse.urlsplit(uri).scheme.lower()
                    if scheme in {"javascript","data","file","vbscript","ms-msdt","shell","command"}:
                        unsafe_uri_links+=1
                elif kind==getattr(fitz,"LINK_LAUNCH",-101):
                    launch_links+=1
                elif kind==getattr(fitz,"LINK_GOTOR",-102):
                    remote_goto_links+=1
            try:
                widgets_iter=page.widgets()
                if widgets_iter:
                    widgets+=sum(1 for _ in widgets_iter)
            except Exception:
                pass
        try:
            embedded_files=int(document.embfile_count())
        except Exception:
            embedded_files=0
        catalog=document.pdf_catalog()
        try:
            open_action_type,open_action_value=document.xref_get_key(catalog,"OpenAction")
            catalog_open_action=0 if str(open_action_type).lower() in {"null","none"} else 1
        except Exception:
            catalog_open_action=0
        try:
            aa_type,aa_value=document.xref_get_key(catalog,"AA")
            catalog_additional_actions=0 if str(aa_type).lower() in {"null","none"} else 1
        except Exception:
            catalog_additional_actions=0
        findings=sum(token_objects.values())+uri_links+launch_links+remote_goto_links+unsafe_uri_links+embedded_files+widgets
        lines=[
            "PDF active-content security audit",
            f"Pages: {document.page_count:,}; indirect objects scanned: {scanned_objects:,}; object metadata characters: {total_object_chars:,}",
            f"Catalog OpenAction: {catalog_open_action}; catalog Additional Actions: {catalog_additional_actions}",
            f"URI links: {uri_links:,}; Launch links: {launch_links:,}; remote GoTo links: {remote_goto_links:,}; unsafe URI schemes: {unsafe_uri_links:,}",
            f"Embedded files: {embedded_files:,}; form widgets: {widgets:,}; oversized object dictionaries: {oversized_objects:,}",
            "",
            "Active-content markers (number of objects containing each marker):"
        ]
        lines.extend(f"- {name}: {count:,}" for name,count in token_objects.items())
        lines.extend(["","Review signals:"])
        review=[]
        if token_objects["JavaScript action"] or token_objects["JS action payload"]: review.append("JavaScript action markers are present.")
        if token_objects["OpenAction"] or catalog_open_action: review.append("The document defines an OpenAction; it may run when the PDF is opened.")
        if token_objects["Additional Actions"] or catalog_additional_actions: review.append("Additional action dictionaries are present.")
        if token_objects["Launch action"] or launch_links: review.append("Launch actions or launch links are present.")
        if token_objects["EmbeddedFiles name tree"] or token_objects["File specification"] or embedded_files: review.append("File-attachment markers or embedded files are present.")
        if token_objects["RichMedia"] or token_objects["Rendition or media action"]: review.append("Rich media or multimedia action markers are present.")
        if token_objects["AcroForm"] or token_objects["XFA form"] or widgets: review.append("Interactive form fields or XFA markers are present.")
        if token_objects["SubmitForm action"] or token_objects["ImportData action"]: review.append("Form submit/import action markers are present.")
        if token_objects["Remote GoTo action"] or remote_goto_links: review.append("Remote-document navigation markers are present.")
        if unsafe_uri_links: review.append("One or more URI links use a potentially unsafe scheme.")
        lines.extend("- "+item for item in review or ["No configured active-content indicator was detected."])
        lines.extend(["","Static PDF object-graph inspection only. No JavaScript, launch action, link target or embedded file was executed or opened. A marker can be benign; this is not malware scanning or a guarantee that a PDF is safe."])
        return tool_text("\n".join(lines),"PDF active-content audit")
    finally:
        document.close()


def email_security_audit(p):
    from email import policy
    from email.parser import BytesParser
    from email.utils import getaddresses
    size=p.stat().st_size
    if size>10*1024*1024:
        raise RuntimeError("Email vượt giới hạn 10 MiB.")
    raw=p.read_bytes()
    message=BytesParser(policy=policy.default).parsebytes(raw)
    def domains_for(header):
        result=set()
        for _,address in getaddresses([str(value) for value in message.get_all(header,[])]):
            if "@" not in address: continue
            domain=address.rsplit("@",1)[1].strip().strip("<>[]").lower().rstrip(".")
            if domain and re.fullmatch(r"[a-z0-9.-]{1,253}",domain):
                result.add(domain)
        return result
    from_domains=domains_for("From")
    reply_domains=domains_for("Reply-To")
    return_domains=domains_for("Return-Path")
    reply_mismatch=int(bool(from_domains and reply_domains and from_domains.isdisjoint(reply_domains)))
    return_mismatch=int(bool(from_domains and return_domains and from_domains.isdisjoint(return_domains)))
    duplicate_headers={}
    for header in ("From","Date","Message-ID","Subject","Reply-To","Return-Path"):
        count=len(message.get_all(header,[]))
        if count>1: duplicate_headers[header.lower()]=count-1
    required_missing=[name for name in ("From","Date","Message-ID") if not message.get_all(name,[])]
    received_count=len(message.get_all("Received",[]))
    auth_text="\n".join(
        str(value) for name in ("Authentication-Results","ARC-Authentication-Results","Received-SPF")
        for value in message.get_all(name,[])
    )
    auth_pattern=re.compile(r"\b(spf|dkim|dmarc)\s*=\s*(pass|fail|softfail|neutral|none|temperror|permerror)\b",re.I)
    auth_results={}
    for mechanism,result in auth_pattern.findall(auth_text):
        key=(mechanism.lower(),result.lower())
        auth_results[key]=auth_results.get(key,0)+1
    attachments=0
    risky_attachments=0
    attachment_types={}
    risky_suffixes={".exe",".scr",".bat",".cmd",".com",".ps1",".vbs",".vbe",".js",".jse",".hta",".jar",".msi",".msp",".lnk",".iso",".img",".dll",".sys",".docm",".dotm",".xlsm",".xltm",".pptm",".ppsm",".ppam"}
    total_parts=0
    for part in message.walk():
        total_parts+=1
        if total_parts>1000:
            raise RuntimeError("Email vượt giới hạn 1.000 MIME parts.")
        if part.is_multipart():
            continue
        filename=part.get_filename()
        disposition=str(part.get_content_disposition() or "").lower()
        if filename or disposition=="attachment":
            attachments+=1
            if attachments>500:
                raise RuntimeError("Email vượt giới hạn 500 attachments.")
            suffix=Path(str(filename or "").replace("\\","/")).suffix.lower()
            mime=str(part.get_content_type() or "application/octet-stream").lower()
            attachment_types[mime]=attachment_types.get(mime,0)+1
            if suffix in risky_suffixes:
                risky_attachments+=1
    url_count=0
    unsafe_urls=0
    shortener_urls=0
    body_bytes=0
    url_re=re.compile(r"(?i)\b(?:https?|javascript|data|file|vbscript):[^\s<>\"']{1,2048}")
    shorteners={"bit.ly","tinyurl.com","t.co","goo.gl","is.gd","cutt.ly","ow.ly","rb.gy"}
    for part in message.walk():
        if part.is_multipart() or str(part.get_content_disposition() or "").lower()=="attachment":
            continue
        if part.get_content_type() not in {"text/plain","text/html"}:
            continue
        try:
            payload=part.get_payload(decode=True)
        except Exception:
            payload=None
        if not isinstance(payload,bytes): continue
        if body_bytes+len(payload)>2*1024*1024:
            payload=payload[:max(0,2*1024*1024-body_bytes)]
        body_bytes+=len(payload)
        if not payload: continue
        charset=part.get_content_charset() or "utf-8"
        try: body=payload.decode(charset,errors="replace")
        except LookupError: body=payload.decode("utf-8",errors="replace")
        for url in url_re.findall(body):
            url_count+=1
            try:
                parsed_url=urllib.parse.urlsplit(url)
            except ValueError:
                unsafe_urls+=1
                continue
            scheme=parsed_url.scheme.lower()
            if scheme in {"javascript","data","file","vbscript"}: unsafe_urls+=1
            hostname=(parsed_url.hostname or "").lower().rstrip(".")
            if hostname in shorteners: shortener_urls+=1
    defects=len(getattr(message,"defects",[]) or [])
    lines=[
        "Email header and phishing-signal audit",
        f"Message bytes: {size:,}; MIME parts: {total_parts:,}; Received hops: {received_count:,}",
        f"From domains: {len(from_domains):,}; Reply-To domains: {len(reply_domains):,}; Return-Path domains: {len(return_domains):,}",
        f"From/Reply-To domain mismatch: {reply_mismatch}; From/Return-Path domain mismatch: {return_mismatch}",
        f"Attachments: {attachments:,}; attachments with high-risk filename extensions: {risky_attachments:,}",
        f"URLs in text/html or text/plain bodies: {url_count:,}; unsafe URI schemes: {unsafe_urls:,}; known shortener URLs: {shortener_urls:,}",
        f"Parser defects: {defects:,}; duplicate critical headers: {sum(duplicate_headers.values()):,}",
        "Authentication-Results are parsed as header assertions only; this tool does not verify SPF/DKIM/DMARC or trust the header's origin.",
        "",
        "Authentication results asserted by headers:"
    ]
    if auth_results:
        lines.extend(f"- {mechanism.upper()} {result}: {count:,}" for (mechanism,result),count in sorted(auth_results.items()))
    else:
        lines.append("- No parseable SPF/DKIM/DMARC result was found in authentication headers.")
    lines.extend(["","Header and structure findings:"])
    findings=[]
    if reply_mismatch: findings.append("From and Reply-To use different domains.")
    if return_mismatch: findings.append("From and Return-Path use different domains.")
    if required_missing: findings.append("Missing required headers: "+", ".join(required_missing))
    if duplicate_headers: findings.append("Duplicate critical headers: "+", ".join(f"{name} (+{count})" for name,count in sorted(duplicate_headers.items())))
    if risky_attachments: findings.append("One or more attachments use executable, script, macro-enabled Office or shortcut-like extensions.")
    if unsafe_urls: findings.append("One or more body URLs use unsafe URI schemes.")
    if shortener_urls: findings.append("Known URL-shortening services are present in the message body.")
    if defects: findings.append("The email parser reported structural defects.")
    lines.extend("- "+finding for finding in findings or ["No configured spoofing/structure signal was detected."])
    lines.extend(["","Privacy and scope: no sender/recipient address, domain, URL, subject, attachment filename or attachment content is printed. No network lookup is performed and no attachment is opened. A message header may be forged; this report is not a mail-gateway verdict."])
    return tool_text("\n".join(lines),"Email security audit")


def jwt_security_audit(p):
    import base64
    size=p.stat().st_size
    if size>5*1024*1024:
        raise RuntimeError("JWT input vượt giới hạn 5 MiB.")
    raw=p.read_text(encoding="utf-8-sig",errors="replace")
    token_re=re.compile(r"(?<![A-Za-z0-9_-])([A-Za-z0-9_-]{8,4096})\.([A-Za-z0-9_-]{8,16384})\.([A-Za-z0-9_-]{0,4096})(?![A-Za-z0-9_-])")
    matches=[]
    for match in token_re.finditer(raw):
        matches.append(match)
        if len(matches)>1000:
            raise RuntimeError("JWT input vượt giới hạn 1.000 token-like strings.")
    unique_tokens={}
    for match in matches:
        token=match.group(0)
        digest=hashlib.sha256(token.encode("ascii",errors="ignore")).hexdigest()
        unique_tokens.setdefault(digest,(match.group(1),match.group(2),match.group(3)))
    algorithms={}
    counters={
        "alg_none":0,"missing_exp":0,"expired":0,"exp_invalid":0,
        "missing_iat":0,"iat_invalid":0,"nbf_invalid":0,"not_yet_valid":0,
        "long_lifetime":0,"external_key_locator":0,"critical_header":0,
        "missing_signature_segment":0,"malformed":0,"missing_issuer":0,"missing_audience":0
    }
    now=int(time.time())
    def decode_segment(segment):
        padded=segment+"="*((4-len(segment)%4)%4)
        payload=base64.urlsafe_b64decode(padded.encode("ascii"))
        if len(payload)>65536:
            raise ValueError("JWT JSON segment exceeds limit")
        value=json.loads(payload.decode("utf-8"))
        if not isinstance(value,dict):
            raise ValueError("JWT JSON segment is not an object")
        return value
    for header_segment,payload_segment,signature_segment in unique_tokens.values():
        try:
            header=decode_segment(header_segment)
            claims=decode_segment(payload_segment)
        except Exception:
            counters["malformed"]+=1
            continue
        algorithm=str(header.get("alg","")).strip().lower()
        algorithms[algorithm or "(missing)"]=algorithms.get(algorithm or "(missing)",0)+1
        if algorithm=="none": counters["alg_none"]+=1
        if "exp" not in claims: counters["missing_exp"]+=1
        else:
            exp=claims.get("exp")
            if isinstance(exp,(int,float)) and not isinstance(exp,bool):
                if exp<=now: counters["expired"]+=1
            else: counters["exp_invalid"]+=1
        if "iat" not in claims: counters["missing_iat"]+=1
        iat=claims.get("iat")
        if iat is not None and (not isinstance(iat,(int,float)) or isinstance(iat,bool)):
            counters["iat_invalid"]+=1
        nbf=claims.get("nbf")
        if nbf is not None:
            if isinstance(nbf,(int,float)) and not isinstance(nbf,bool):
                if nbf>now: counters["not_yet_valid"]+=1
            else: counters["nbf_invalid"]+=1
        exp=claims.get("exp")
        if isinstance(iat,(int,float)) and not isinstance(iat,bool) and isinstance(exp,(int,float)) and not isinstance(exp,bool):
            if exp-iat>90*24*60*60: counters["long_lifetime"]+=1
        if "jku" in header or "x5u" in header: counters["external_key_locator"]+=1
        if "crit" in header: counters["critical_header"]+=1
        if not signature_segment: counters["missing_signature_segment"]+=1
        if not claims.get("iss"): counters["missing_issuer"]+=1
        if not claims.get("aud"): counters["missing_audience"]+=1
    lines=[
        "JWT compact-token security audit",
        f"Input bytes: {size:,}; token-like strings found: {len(matches):,}; unique strings analyzed: {len(unique_tokens):,}",
        f"Malformed header/payload pairs: {counters['malformed']:,}",
        "This tool does not verify cryptographic signatures, issuer trust, audience policy or key strength.",
        "Raw token strings, signatures and claim values are never included.",
        "",
        "Algorithms (header-declared, untrusted):"
    ]
    if algorithms:
        lines.extend(f"- {name}: {count:,}" for name,count in sorted(algorithms.items()))
    else:
        lines.append("- No decodable JWT headers found.")
    lines.extend([
        "",
        "Review counters:",
        f"- alg=none: {counters['alg_none']:,}",
        f"- Missing exp: {counters['missing_exp']:,}; expired: {counters['expired']:,}; invalid exp type: {counters['exp_invalid']:,}",
        f"- Missing iat: {counters['missing_iat']:,}; invalid iat type: {counters['iat_invalid']:,}",
        f"- Future nbf: {counters['not_yet_valid']:,}; invalid nbf type: {counters['nbf_invalid']:,}",
        f"- Lifetime over 90 days (iat to exp): {counters['long_lifetime']:,}",
        f"- External key locators (jku/x5u): {counters['external_key_locator']:,}; critical header extensions: {counters['critical_header']:,}",
        f"- Empty signature segment: {counters['missing_signature_segment']:,}; missing issuer: {counters['missing_issuer']:,}; missing audience: {counters['missing_audience']:,}",
        "",
        "Scope: compact JWTs are decoded locally for structural review only. Header/claim contents are attacker-controlled until a relying service verifies the signature and applies issuer/audience/expiry policy."
    ])
    return tool_text("\n".join(lines),"JWT security audit")



def har_privacy_audit(p):
    size=p.stat().st_size
    if size>20*1024*1024:
        raise RuntimeError("HAR file vượt giới hạn 20 MiB.")
    try:
        data=json.loads(p.read_text(encoding="utf-8-sig"))
    except (UnicodeError,json.JSONDecodeError) as exc:
        raise RuntimeError("HAR phải là JSON UTF-8 hợp lệ.") from exc
    if not isinstance(data,dict) or not isinstance(data.get("log"),dict):
        raise RuntimeError("Không tìm thấy đối tượng HAR log.")
    entries=data["log"].get("entries",[])
    if not isinstance(entries,list):
        raise RuntimeError("HAR log.entries phải là một mảng.")
    if len(entries)>100000:
        raise RuntimeError("HAR vượt giới hạn 100.000 entries.")
    sensitive=re.compile(r"(?:authorization|proxy-authorization|cookie|set-cookie|token|secret|password|passwd|api[-_]?key|client[-_]?secret|session|email|phone|credential|auth)",re.I)
    bearer=re.compile(r"(?i)\b(?:bearer|basic)\s+[A-Za-z0-9._~+/=-]{8,}")
    jwt=re.compile(r"(?<![A-Za-z0-9_-])[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}(?![A-Za-z0-9_-])")
    counts={"authorization_headers":0,"cookie_headers":0,"sensitive_headers":0,"sensitive_query_parameters":0,"sensitive_cookies":0,"sensitive_form_fields":0,"body_token_patterns":0}
    methods={}; statuses={}; entries_with_sensitive=0; scanned_body_chars=0
    def inspect_headers(items):
        if not isinstance(items,list): return False
        found=False
        for item in items:
            if not isinstance(item,dict): continue
            name=str(item.get("name",""))
            lower=name.lower()
            if lower in {"authorization","proxy-authorization"}: counts["authorization_headers"]+=1; found=True
            elif lower in {"cookie","set-cookie"}: counts["cookie_headers"]+=1; found=True
            elif sensitive.search(name): counts["sensitive_headers"]+=1; found=True
        return found
    def inspect_keyed(items,counter):
        found=False
        if not isinstance(items,list): return found
        for item in items:
            if isinstance(item,dict) and sensitive.search(str(item.get("name",""))):
                counts[counter]+=1; found=True
        return found
    for entry in entries:
        if not isinstance(entry,dict): continue
        request=entry.get("request") if isinstance(entry.get("request"),dict) else {}
        response=entry.get("response") if isinstance(entry.get("response"),dict) else {}
        found=False
        method=str(request.get("method","UNKNOWN")).upper()[:20]
        methods[method]=methods.get(method,0)+1
        status=response.get("status")
        if isinstance(status,int):
            bucket=f"{status//100}xx"
            statuses[bucket]=statuses.get(bucket,0)+1
        found=inspect_headers(request.get("headers")) or found
        found=inspect_headers(response.get("headers")) or found
        found=inspect_keyed(request.get("cookies"),"sensitive_cookies") or found
        found=inspect_keyed(response.get("cookies"),"sensitive_cookies") or found
        found=inspect_keyed(request.get("queryString"),"sensitive_query_parameters") or found
        post=request.get("postData") if isinstance(request.get("postData"),dict) else {}
        found=inspect_keyed(post.get("params"),"sensitive_form_fields") or found
        url=request.get("url")
        if isinstance(url,str):
            try:
                query=urllib.parse.parse_qsl(urllib.parse.urlsplit(url).query,keep_blank_values=True)
                for key,_ in query:
                    if sensitive.search(key):
                        counts["sensitive_query_parameters"]+=1; found=True
            except ValueError:
                pass
        for body in (post.get("text"),(response.get("content") or {}).get("text") if isinstance(response.get("content"),dict) else None):
            if not isinstance(body,str) or scanned_body_chars>=2*1024*1024: continue
            sample=body[:max(0,2*1024*1024-scanned_body_chars)]
            scanned_body_chars+=len(sample)
            token_hits=len(bearer.findall(sample))+len(jwt.findall(sample))
            counts["body_token_patterns"]+=token_hits
            if token_hits: found=True
        if found: entries_with_sensitive+=1
    lines=[
        "HAR privacy exposure audit",
        f"File size: {size:,} bytes; entries: {len(entries):,}; entries with sensitive indicators: {entries_with_sensitive:,}",
        f"Authorization headers: {counts['authorization_headers']:,}; Cookie/Set-Cookie headers: {counts['cookie_headers']:,}",
        f"Other sensitive headers: {counts['sensitive_headers']:,}; sensitive query parameters: {counts['sensitive_query_parameters']:,}",
        f"Sensitive cookie names: {counts['sensitive_cookies']:,}; sensitive form fields: {counts['sensitive_form_fields']:,}",
        f"Bearer/basic or JWT-like body patterns: {counts['body_token_patterns']:,} (bounded scan: {scanned_body_chars:,} characters)",
        "HTTP methods: "+(", ".join(f"{key}={value}" for key,value in sorted(methods.items())) or "none"),
        "Response status groups: "+(", ".join(f"{key}={value}" for key,value in sorted(statuses.items())) or "none"),
        "The report never prints request URLs, header values, cookie values, query values, or captured body content.",
        "Detection is heuristic; custom secrets and personal data may not match these patterns."
    ]
    return tool_text("\n".join(lines),"HAR privacy audit")



def _read_bounded_vobject_components(raw,max_depth=40):
    import vobject
    depth=0
    for line in raw.splitlines():
        if re.match(r"^\s*BEGIN\s*:",line,re.I):
            depth+=1
            if depth>max_depth:
                raise RuntimeError(f"Calendar/contact component nesting exceeds {max_depth} levels.")
        elif re.match(r"^\s*END\s*:",line,re.I):
            depth=max(0,depth-1)
    return list(vobject.readComponents(raw,validate=False))

def ics_calendar_audit(p):
    import vobject
    size=p.stat().st_size
    if size>10*1024*1024: raise RuntimeError("iCalendar input vượt giới hạn 10 MiB.")
    try:
        components=_read_bounded_vobject_components(p.read_text(encoding="utf-8-sig"),max_depth=40)
    except Exception as exc:
        raise RuntimeError("Không thể phân tích iCalendar; hãy kiểm tra định dạng và cấu trúc BEGIN/END.") from exc
    calendars=[item for item in components if str(getattr(item,"name","")).upper()=="VCALENDAR"]
    if not calendars: raise RuntimeError("Không tìm thấy VCALENDAR.")
    def vals(component,key):
        return [item.value for item in component.contents.get(key,[])]
    events=[]; timezone_count=0; todo_count=0
    for cal in calendars:
        events.extend(cal.contents.get("vevent",[]))
        timezone_count+=len(cal.contents.get("vtimezone",[]))
        todo_count+=len(cal.contents.get("vtodo",[]))
    uids=[]; missing_uid=missing_start=missing_end=bad_range=recurring=alarms=attendees=organizers=0
    for event in events:
        uid=vals(event,"uid")
        if uid: uids.append(str(uid[0]).strip())
        else: missing_uid+=1
        starts=vals(event,"dtstart"); ends=vals(event,"dtend")
        if not starts: missing_start+=1
        if not ends and not vals(event,"duration"): missing_end+=1
        if starts and ends:
            try:
                start=starts[0]; end=ends[0]
                if end<=start: bad_range+=1
            except (TypeError,ValueError):
                bad_range+=1
        if vals(event,"rrule"): recurring+=1
        alarms+=len(event.contents.get("valarm",[]))
        attendees+=len(vals(event,"attendee"))
        organizers+=len(vals(event,"organizer"))
    duplicate_uids=len(uids)-len(set(uids))
    lines=[
        "iCalendar structure and privacy-safe audit",
        f"Calendars: {len(calendars):,}; events: {len(events):,}; VTODO components: {todo_count:,}; time zones: {timezone_count:,}",
        f"Events missing UID: {missing_uid:,}; missing DTSTART: {missing_start:,}; missing DTEND/DURATION: {missing_end:,}",
        f"Non-positive or incomparable event ranges: {bad_range:,}; duplicate UIDs: {duplicate_uids:,}",
        f"Recurring events: {recurring:,}; VALARM components: {alarms:,}; attendee fields: {attendees:,}; organizer fields: {organizers:,}",
        "Event titles, descriptions, attendee addresses, organizers, locations and calendar UIDs are never included.",
        "This checks local structure only; it does not expand recurrence rules or verify remote calendar availability."
    ]
    return tool_text("\n".join(lines),"iCalendar audit")


def vcard_privacy_audit(p):
    import vobject
    size=p.stat().st_size
    if size>10*1024*1024: raise RuntimeError("vCard input vượt giới hạn 10 MiB.")
    try:
        components=_read_bounded_vobject_components(p.read_text(encoding="utf-8-sig"),max_depth=40)
    except Exception as exc:
        raise RuntimeError("Không thể phân tích vCard; hãy kiểm tra cấu trúc BEGIN:VCARD/END:VCARD.") from exc
    cards=[item for item in components if str(getattr(item,"name","")).upper()=="VCARD"]
    if not cards: raise RuntimeError("Không tìm thấy VCARD.")
    email_values=[]; phone_values=[]; missing_fn=missing_n=0; photo_cards=0; address_fields=org_fields=note_fields=0; malformed=0
    for card in cards:
        contents=card.contents
        names=contents.get("fn",[]); structured=contents.get("n",[])
        if not names or not str(getattr(names[0],"value","")).strip(): missing_fn+=1
        if not structured: missing_n+=1
        for item in contents.get("email",[]):
            value=str(getattr(item,"value","")).strip().casefold()
            if value: email_values.append(value)
        for item in contents.get("tel",[]):
            value=re.sub(r"\D","",str(getattr(item,"value","")))
            if value: phone_values.append(value)
        if contents.get("photo"): photo_cards+=1
        address_fields+=len(contents.get("adr",[]))
        org_fields+=len(contents.get("org",[]))
        note_fields+=len(contents.get("note",[]))
        malformed+=len(getattr(card,"errors",[]) or [])
    duplicate_emails=len(email_values)-len(set(email_values))
    duplicate_phones=len(phone_values)-len(set(phone_values))
    lines=[
        "vCard contact and privacy audit",
        f"Contact cards: {len(cards):,}; email fields: {len(email_values):,}; telephone fields: {len(phone_values):,}",
        f"Duplicate email values: {duplicate_emails:,}; duplicate normalized telephone values: {duplicate_phones:,}",
        f"Cards missing FN: {missing_fn:,}; missing structured N: {missing_n:,}; cards containing photos: {photo_cards:,}",
        f"Address fields: {address_fields:,}; organization fields: {org_fields:,}; note fields: {note_fields:,}; parser diagnostics: {malformed:,}",
        "Names, email addresses, phone numbers, postal addresses, organization names, notes and photo data are never included."
    ]
    return tool_text("\n".join(lines),"vCard privacy audit")


def gpx_track_report(p):
    import math
    import xml.etree.ElementTree as ET
    size=p.stat().st_size
    if size>20*1024*1024: raise RuntimeError("GPX input vượt giới hạn 20 MiB.")
    try: root=ET.fromstring(p.read_bytes())
    except ET.ParseError as exc: raise RuntimeError("GPX XML không hợp lệ.") from exc
    def local(tag): return tag.rsplit("}",1)[-1].lower()
    def child_value(node,name):
        for child in list(node):
            if local(child.tag)==name:
                return child.text
        return None
    def distance(a,b):
        lat1,lon1=a; lat2,lon2=b
        radius=6371.0088
        phi1=math.radians(lat1); phi2=math.radians(lat2)
        dphi=math.radians(lat2-lat1); dlambda=math.radians(lon2-lon1)
        h=math.sin(dphi/2)**2+math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        return 2*radius*math.asin(min(1,math.sqrt(h)))
    trackpoints=routepoints=waypoints=segments=invalid_points=0
    total_km=ascent=descent=0.0; elevations=[]; timestamps=[]
    def parse_points(nodes):
        nonlocal trackpoints,routepoints,waypoints,invalid_points,total_km,ascent,descent
        previous=None; previous_ele=None; previous_time=None
        for point in nodes:
            try:
                lat=float(point.attrib.get("lat","nan")); lon=float(point.attrib.get("lon","nan"))
                if not math.isfinite(lat) or not math.isfinite(lon) or not -90<=lat<=90 or not -180<=lon<=180:
                    invalid_points+=1; previous=None; previous_ele=None; continue
            except (TypeError,ValueError):
                invalid_points+=1; previous=None; previous_ele=None; continue
            if local(point.tag)=="trkpt": trackpoints+=1
            elif local(point.tag)=="rtept": routepoints+=1
            elif local(point.tag)=="wpt": waypoints+=1
            current=(lat,lon)
            if previous is not None: total_km+=distance(previous,current)
            previous=current
            raw_ele=child_value(point,"ele")
            current_ele=None
            if raw_ele is not None:
                try:
                    current_ele=float(raw_ele)
                    if math.isfinite(current_ele):
                        elevations.append(current_ele)
                        if previous_ele is not None:
                            delta=current_ele-previous_ele
                            if delta>0: ascent+=delta
                            else: descent-=delta
                except ValueError: pass
            previous_ele=current_ele
            raw_time=child_value(point,"time")
            if raw_time:
                try:
                    from datetime import datetime
                    timestamps.append(datetime.fromisoformat(raw_time.replace("Z","+00:00")))
                except ValueError: pass
    for node in root.iter():
        if local(node.tag)=="trkseg":
            segments+=1
            parse_points([child for child in list(node) if local(child.tag)=="trkpt"])
        elif local(node.tag)=="rte":
            parse_points([child for child in list(node) if local(child.tag)=="rtept"])
        elif local(node.tag)=="wpt":
            parse_points([node])
    duration_hours=None
    if len(timestamps)>=2:
        try:
            duration_hours=(max(timestamps)-min(timestamps)).total_seconds()/3600
        except TypeError: duration_hours=None
    lines=[
        "GPX track report",
        f"Track points: {trackpoints:,}; route points: {routepoints:,}; waypoints: {waypoints:,}; track segments: {segments:,}",
        f"Calculated path length: {total_km:.3f} km; invalid coordinate pairs: {invalid_points:,}",
        f"Elevation samples: {len(elevations):,}; cumulative ascent: {ascent:.1f} m; cumulative descent: {descent:.1f} m",
        (f"Elevation range: {min(elevations):.1f}–{max(elevations):.1f} m" if elevations else "Elevation range: unavailable"),
        (f"Timestamp span: {duration_hours:.2f} hours" if duration_hours is not None else "Timestamp span: unavailable"),
        "Coordinates, place names and exact timestamps are withheld from the report to reduce location privacy exposure."
    ]
    return tool_text("\n".join(lines),"GPX track report")


def geojson_audit(p):
    import math
    size=p.stat().st_size
    if size>20*1024*1024: raise RuntimeError("GeoJSON input vượt giới hạn 20 MiB.")
    try: data=json.loads(p.read_text(encoding="utf-8-sig"))
    except (UnicodeError,json.JSONDecodeError) as exc: raise RuntimeError("GeoJSON phải là JSON UTF-8 hợp lệ.") from exc
    geometry_counts={}; features=0; missing_geometry=0; positions=0; invalid_positions=0; property_keys=0; empty_geometries=0
    def walk_coords(value):
        nonlocal positions,invalid_positions
        if not isinstance(value,list): return
        if len(value)>=2 and all(isinstance(x,(int,float)) and not isinstance(x,bool) for x in value[:2]):
            positions+=1
            lon,lat=value[0],value[1]
            if not math.isfinite(float(lon)) or not math.isfinite(float(lat)) or not -180<=lon<=180 or not -90<=lat<=90:
                invalid_positions+=1
            return
        for child in value: walk_coords(child)
    def visit_geometry(geometry):
        nonlocal empty_geometries
        if not isinstance(geometry,dict):
            empty_geometries+=1; return
        kind=str(geometry.get("type","Unknown"))
        geometry_counts[kind]=geometry_counts.get(kind,0)+1
        if kind=="GeometryCollection":
            geoms=geometry.get("geometries",[])
            if not isinstance(geoms,list) or not geoms: empty_geometries+=1
            else:
                for child in geoms: visit_geometry(child)
        else:
            coords=geometry.get("coordinates")
            if not isinstance(coords,list) or not coords: empty_geometries+=1
            else: walk_coords(coords)
    kind=data.get("type") if isinstance(data,dict) else None
    if kind=="FeatureCollection":
        items=data.get("features",[])
        if not isinstance(items,list): raise RuntimeError("FeatureCollection.features phải là một mảng.")
        features=len(items)
        for item in items:
            if not isinstance(item,dict) or item.get("type")!="Feature": missing_geometry+=1; continue
            props=item.get("properties")
            if isinstance(props,dict): property_keys+=len(props)
            if item.get("geometry") is None: missing_geometry+=1
            else: visit_geometry(item.get("geometry"))
    elif kind=="Feature":
        features=1
        props=data.get("properties")
        if isinstance(props,dict): property_keys=len(props)
        if data.get("geometry") is None: missing_geometry=1
        else: visit_geometry(data.get("geometry"))
    else:
        visit_geometry(data)
    lines=[
        "GeoJSON structure audit",
        f"Top-level type: {kind or 'unknown'}; features: {features:,}; geometry counts: "+(", ".join(f"{name}={count}" for name,count in sorted(geometry_counts.items())) or "none"),
        f"Coordinate positions: {positions:,}; invalid longitude/latitude pairs: {invalid_positions:,}; empty geometries: {empty_geometries:,}; missing feature geometries: {missing_geometry:,}",
        f"Property keys across features: {property_keys:,}",
        "Coordinates, feature properties and feature identifiers are not printed."
    ]
    return tool_text("\n".join(lines),"GeoJSON audit")


def qr_code_generate(p):
    import qrcode
    size=p.stat().st_size
    if size>4096: raise RuntimeError("QR generator giới hạn payload 4 KiB.")
    payload=p.read_text(encoding="utf-8-sig")
    if not payload.strip(): raise RuntimeError("Không thể tạo QR từ nội dung trống.")
    qr=qrcode.QRCode(version=None,error_correction=qrcode.constants.ERROR_CORRECT_M,box_size=10,border=4)
    qr.add_data(payload)
    qr.make(fit=True)
    image=qr.make_image(fill_color="black",back_color="white")
    out=p.with_name(p.stem+"-qr.png")
    image.save(out,format="PNG")
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("QR output exceeds the 45 MB delivery limit.")
    return {"summary":f"Đã tạo QR PNG từ payload {size:,} bytes. Nội dung payload không được ghi vào job summary.","output_path":str(out)}


def font_inspect(p):
    from fontTools.ttLib import TTFont
    size=p.stat().st_size
    if size>20*1024*1024: raise RuntimeError("Font inspection giới hạn file 20 MiB.")
    font=None
    try:
        font=TTFont(str(p),lazy=True,recalcBBoxes=False,recalcTimestamp=False)
        names={}
        table=font.get("name")
        if table:
            for record in table.names:
                if record.nameID in {1,2,4,5,6}:
                    try: value=record.toUnicode().strip()
                    except Exception: continue
                    if value: names.setdefault(record.nameID,value[:160])
        family=names.get(1,"Unknown"); subfamily=names.get(2,"Unknown")
        glyphs=len(font.getGlyphOrder())
        cmap=font.getBestCmap() or {}
        axes=[]
        if font.get("fvar"):
            axes=[f"{axis.axisTag} ({axis.minValue:g}–{axis.maxValue:g})" for axis in font["fvar"].axes[:20]]
        os2=font.get("OS/2")
        fs_type=int(getattr(os2,"fsType",0)) if os2 else 0
        embedding=("restricted" if fs_type&0x0002 else "preview/print" if fs_type&0x0004 else "editable" if fs_type&0x0008 else "installable/unrestricted")
        lines=[
            "Font file inspector",
            f"Format: {p.suffix.lower()}; bytes: {size:,}; glyphs: {glyphs:,}; Unicode cmap entries: {len(cmap):,}",
            f"Family: {family}; subfamily: {subfamily}",
            f"Full name: {names.get(4,'Unknown')}; version: {names.get(5,'Unknown')}",
            f"PostScript name: {names.get(6,'Unknown')}",
            f"Variable font axes: {', '.join(axes) if axes else 'none detected'}",
            f"OS/2 fsType embedding flags: 0x{fs_type:04x} ({embedding})",
            "Metadata is informational; embedding permissions are not a legal license determination."
        ]
    except Exception as exc:
        raise RuntimeError("Không thể đọc font hợp lệ hoặc định dạng font chưa được hỗ trợ.") from exc
    finally:
        if font is not None:
            try: font.close()
            except Exception: pass
    return tool_text("\n".join(lines),"Font inspector")


def subtitle_fix(p):
    if p.stat().st_size>10*1024*1024: raise RuntimeError("Subtitle repair giới hạn file 10 MiB.")
    raw=p.read_text(encoding="utf-8-sig").replace("\r\n","\n").replace("\r","\n")
    is_vtt=p.suffix.lower()==".vtt" or raw.lstrip().startswith("WEBVTT")
    stamp=re.compile(r"(?<!\d)(?:(\d{1,2}):)?(\d{2}):(\d{2})[,.](\d{1,3})\s*-->\s*(?:(\d{1,2}):)?(\d{2}):(\d{2})[,.](\d{1,3})(?:\s+.*)?$")
    cues=[]; removed=0; adjusted=0
    def millis(groups,offset):
        hours=int(groups[offset] or 0); minutes=int(groups[offset+1]); seconds=int(groups[offset+2]); fraction=int(groups[offset+3].ljust(3,"0"))
        if minutes>59 or seconds>59: raise ValueError
        return ((hours*60+minutes)*60+seconds)*1000+fraction
    def render(ms,sep):
        hours,rem=divmod(max(0,ms),3600000); minutes,rem=divmod(rem,60000); seconds,milliseconds=divmod(rem,1000)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}{sep}{milliseconds:03d}"
    for block in re.split(r"\n[ \t]*\n",raw.strip()):
        if not block.strip() or block.strip().startswith(("WEBVTT","NOTE","STYLE","REGION")): continue
        lines=block.strip().splitlines()
        timestamp_index=next((i for i,line in enumerate(lines) if "-->" in line),None)
        if timestamp_index is None: continue
        match=stamp.match(lines[timestamp_index].strip())
        if not match: removed+=1; continue
        try:
            groups=match.groups()
            start=millis(groups,0); end=millis(groups,4)
        except (ValueError,TypeError):
            removed+=1; continue
        payload="\n".join(lines[timestamp_index+1:]).strip()
        if not payload: removed+=1; continue
        if end<=start:
            end=start+1; adjusted+=1
        cues.append((start,end,payload))
    if not cues: raise RuntimeError("Không tìm thấy cue phụ đề hợp lệ để sửa.")
    cues.sort(key=lambda item:item[0])
    sep="." if is_vtt else ","
    out_lines=["WEBVTT",""] if is_vtt else []
    for index,(start,end,payload) in enumerate(cues,1):
        if not is_vtt: out_lines.append(str(index))
        out_lines.extend([render(start,sep)+" --> "+render(end,sep),payload,""])
    extension=".vtt" if is_vtt else ".srt"
    out=p.with_name(p.stem+"-fixed"+extension)
    out.write_text("\n".join(out_lines).rstrip()+"\n",encoding="utf-8")
    return {"summary":f"Đã chuẩn hóa {len(cues):,} cue; sắp xếp theo thời gian; loại {removed:,} cue lỗi/rỗng; điều chỉnh {adjusted:,} thời lượng không dương.","output_path":str(out)}


def openapi_contract_audit(p):
    size=p.stat().st_size
    if size>10*1024*1024: raise RuntimeError("OpenAPI file vượt giới hạn 10 MiB.")
    raw=p.read_text(encoding="utf-8-sig")
    try:
        if p.suffix.lower() in {".yaml",".yml"}:
            import yaml
            spec=yaml.safe_load(raw)
        else:
            spec=json.loads(raw)
    except Exception as exc:
        raise RuntimeError("OpenAPI document không phải JSON/YAML hợp lệ.") from exc
    if not isinstance(spec,dict): raise RuntimeError("OpenAPI document phải là object ở cấp gốc.")
    version=str(spec.get("openapi") or ("Swagger "+str(spec.get("swagger")) if spec.get("swagger") else "unknown"))
    is_v3=str(spec.get("openapi","")).startswith("3.")
    is_swagger=spec.get("swagger")=="2.0"
    paths=spec.get("paths",{})
    if not isinstance(paths,dict): raise RuntimeError("OpenAPI paths phải là object.")
    methods={"get","put","post","delete","options","head","patch","trace"}
    operations=0; duplicate_ids=0; missing_ids=0; missing_responses=0; missing_summaries=0; path_parameter_gaps=0; security_references=0
    operation_ids=set(); refs=[]; external_refs=0; malformed_operations=0
    for path,item in paths.items():
        if not isinstance(item,dict): continue
        path_params=set(re.findall(r"\{([^{}]+)\}",str(path)))
        common=item.get("parameters",[]) if isinstance(item.get("parameters",[]),list) else []
        declared_common={str(x.get("name")) for x in common if isinstance(x,dict) and x.get("in")=="path"}
        for method,operation in item.items():
            if str(method).lower() not in methods: continue
            operations+=1
            if not isinstance(operation,dict): malformed_operations+=1; continue
            op_id=operation.get("operationId")
            if not isinstance(op_id,str) or not op_id.strip(): missing_ids+=1
            elif op_id in operation_ids: duplicate_ids+=1
            else: operation_ids.add(op_id)
            responses=operation.get("responses")
            if not isinstance(responses,dict) or not responses: missing_responses+=1
            if not operation.get("summary") and not operation.get("description"): missing_summaries+=1
            params=operation.get("parameters",[]) if isinstance(operation.get("parameters",[]),list) else []
            declared=declared_common|{str(x.get("name")) for x in params if isinstance(x,dict) and x.get("in")=="path"}
            if not path_params.issubset(declared): path_parameter_gaps+=1
            if operation.get("security") is not None: security_references+=1
    def scan_refs(value):
        nonlocal external_refs
        if isinstance(value,dict):
            ref=value.get("$ref")
            if isinstance(ref,str):
                if ref.startswith("#/"): refs.append(ref)
                elif ref.startswith("#"): refs.append(ref)
                else: external_refs+=1
            for child in value.values(): scan_refs(child)
        elif isinstance(value,list):
            for child in value: scan_refs(child)
    scan_refs(spec)
    def resolve_pointer(root,ref):
        if not ref.startswith("#/"): return ref=="#"
        current=root
        for token in ref[2:].split("/"):
            token=token.replace("~1","/").replace("~0","~")
            if isinstance(current,dict) and token in current: current=current[token]
            elif isinstance(current,list) and token.isdigit() and int(token)<len(current): current=current[int(token)]
            else: return False
        return True
    unresolved=sum(not resolve_pointer(spec,ref) for ref in refs)
    servers=spec.get("servers",[]) if isinstance(spec.get("servers",[]),list) else []
    insecure_servers=sum(1 for server in servers if isinstance(server,dict) and str(server.get("url","")).lower().startswith("http://"))
    lines=[
        "OpenAPI contract audit",
        f"Document version: {version}; path items: {len(paths):,}; Operations: {operations:,}",
        f"Operations missing operationId: {missing_ids:,}; duplicate operationId: {duplicate_ids:,}; malformed operation objects: {malformed_operations:,}",
        f"Operations without responses: {missing_responses:,}; without summary/description: {missing_summaries:,}; path-parameter declaration gaps: {path_parameter_gaps:,}",
        f"Local $ref values: {len(refs):,}; unresolved local references: {unresolved:,}; external references not fetched: {external_refs:,}",
        f"Operations with explicit security fields: {security_references:,}; HTTP (non-TLS) server URLs: {insecure_servers:,}",
        "References are checked locally only; remote references are never fetched. This is a structural lint, not a full OpenAPI specification validator."
    ]
    if not (is_v3 or is_swagger): lines.append("Warning: expected OpenAPI 3.x or Swagger 2.0 version marker was not found.")
    return tool_text("\n".join(lines),"OpenAPI audit")


def color_convert(p):
    import colorsys
    if p.stat().st_size>2*1024*1024: raise RuntimeError("Color converter giới hạn input 2 MiB.")
    raw=p.read_text(encoding="utf-8-sig")
    if not raw.strip(): raise RuntimeError("Không có mã màu để chuyển đổi.")
    hex_re=re.compile(r"^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
    rgb_re=re.compile(r"^rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})(?:\s*,\s*[\d.]+)?\s*\)$",re.I)
    rows=[]; invalid=0
    for number,line in enumerate(raw.splitlines(),1):
        value=line.strip()
        if not value: continue
        match=hex_re.fullmatch(value)
        if match:
            digits=match.group(1)
            if len(digits)==3: digits="".join(char*2 for char in digits)
            red,green,blue=(int(digits[i:i+2],16) for i in (0,2,4))
        else:
            match=rgb_re.fullmatch(value)
            if not match: invalid+=1; continue
            red,green,blue=map(int,match.groups())
            if any(channel>255 for channel in (red,green,blue)): invalid+=1; continue
        r,g,b=(channel/255 for channel in (red,green,blue))
        hue,light,saturation=colorsys.rgb_to_hls(r,g,b)
        k=1-max(r,g,b)
        if k>=1: cyan=magenta=yellow=0
        else:
            cyan=(1-r-k)/(1-k); magenta=(1-g-k)/(1-k); yellow=(1-b-k)/(1-k)
        rows.append((number,f"#{red:02X}{green:02X}{blue:02X}",red,green,blue,round(hue*360),round(saturation*100),round(light*100),round(cyan*100),round(magenta*100),round(yellow*100),round(k*100)))
    if not rows: raise RuntimeError("Không tìm thấy mã màu #RGB, #RRGGBB hoặc rgb(r,g,b) hợp lệ.")
    lines=["Color conversion report","Input lines converted: "+str(len(rows))+"; invalid lines skipped: "+str(invalid),"", "Line | HEX | RGB | HSL | CMYK"]
    lines.extend(f"{n} | {hexv} | rgb({r},{g},{b}) | hsl({h},{s}%,{l}%) | cmyk({c}%,{m}%,{y}%,{k}%)" for n,hexv,r,g,b,h,s,l,c,m,y,k in rows[:2000])
    return tool_text("\n".join(lines),"Color converter")


def pcap_network_audit(p):
    import dpkt
    size=p.stat().st_size
    if size>20*1024*1024:
        raise RuntimeError("PCAP input vượt giới hạn 20 MiB.")
    protocol_counts={}
    port_counts={}
    host_count=set()
    packet_count=0
    packet_bytes=0
    parse_errors=0
    tcp_count=udp_count=icmp_count=dns_count=ip_count=0
    timestamps=[]
    try:
        with p.open("rb") as handle:
            magic=handle.read(4)
            handle.seek(0)
            reader=dpkt.pcapng.Reader(handle) if magic==b"\x0a\x0d\x0d\x0a" else dpkt.pcap.Reader(handle)
            linktype=reader.datalink()
            for timestamp,packet_bytes_raw in reader:
                packet_count+=1
                if packet_count>200000:
                    raise RuntimeError("PCAP vượt giới hạn 200.000 packets.")
                packet_bytes+=len(packet_bytes_raw)
                timestamps.append(float(timestamp))
                try:
                    if linktype==dpkt.pcap.DLT_EN10MB:
                        frame=dpkt.ethernet.Ethernet(packet_bytes_raw)
                        network=frame.data
                    elif linktype in (dpkt.pcap.DLT_RAW,dpkt.pcap.DLT_IPV4,dpkt.pcap.DLT_IPV6):
                        if not packet_bytes_raw:
                            continue
                        version=packet_bytes_raw[0]>>4
                        network=dpkt.ip.IP(packet_bytes_raw) if version==4 else dpkt.ip6.IP6(packet_bytes_raw) if version==6 else None
                    else:
                        name="linktype-"+str(linktype)
                        protocol_counts[name]=protocol_counts.get(name,0)+1
                        continue
                    if isinstance(network,dpkt.ip.IP):
                        ip_count+=1
                        host_count.add(network.src)
                        host_count.add(network.dst)
                        payload=network.data
                        protocol_name="IPv4"
                    elif isinstance(network,dpkt.ip6.IP6):
                        ip_count+=1
                        host_count.add(network.src)
                        host_count.add(network.dst)
                        payload=network.data
                        protocol_name="IPv6"
                    else:
                        protocol_counts["non-IP/other"]=protocol_counts.get("non-IP/other",0)+1
                        continue
                    if isinstance(payload,dpkt.tcp.TCP):
                        tcp_count+=1
                        port_counts[payload.sport]=port_counts.get(payload.sport,0)+1
                        port_counts[payload.dport]=port_counts.get(payload.dport,0)+1
                        if payload.dport in (53,5353) or payload.sport in (53,5353):
                            dns_count+=1
                    elif isinstance(payload,dpkt.udp.UDP):
                        udp_count+=1
                        port_counts[payload.sport]=port_counts.get(payload.sport,0)+1
                        port_counts[payload.dport]=port_counts.get(payload.dport,0)+1
                        if payload.dport in (53,5353) or payload.sport in (53,5353):
                            dns_count+=1
                    elif isinstance(payload,(dpkt.icmp.ICMP,dpkt.icmp6.ICMP6)):
                        icmp_count+=1
                    protocol_counts[protocol_name]=protocol_counts.get(protocol_name,0)+1
                except (dpkt.UnpackError,ValueError,IndexError,AttributeError):
                    parse_errors+=1
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError("Không thể đọc PCAP/PCAPNG hoặc định dạng link-layer chưa hỗ trợ.") from exc
    duration=max(timestamps)-min(timestamps) if len(timestamps)>1 else 0.0
    top_ports=sorted(port_counts.items(),key=lambda item:(-item[1],item[0]))[:12]
    lines=[
        "PCAP network capture audit",
        f"File bytes: {size:,}; packets: {packet_count:,}; captured packet bytes: {packet_bytes:,}",
        f"Capture duration: {duration:.3f}s; IP packets: {ip_count:,}; unique IP endpoints: {len(host_count):,}; parse errors: {parse_errors:,}",
        f"TCP packets: {tcp_count:,}; UDP packets: {udp_count:,}; ICMP packets: {icmp_count:,}; DNS/mDNS-port packets: {dns_count:,}",
        "Network type counts: "+(", ".join(f"{name}={count:,}" for name,count in sorted(protocol_counts.items())) or "none"),
        "Top transport ports: "+(", ".join(f"{port} ({count:,})" for port,count in top_ports) or "none"),
        "IP addresses, packet payloads, DNS names and application data are never included.",
        "Offline metadata only; traffic is not replayed and no host is contacted."
    ]
    return tool_text("\n".join(lines),"PCAP network audit")


def audio_tag_audit(p):
    size=p.stat().st_size
    if size>100*1024*1024:
        raise RuntimeError("Audio tag audit giới hạn file 100 MiB.")
    data=ffprobe(p)
    fmt=data.get("format",{})
    format_tags=fmt.get("tags",{}) if isinstance(fmt.get("tags"),dict) else {}
    streams=[item for item in data.get("streams",[]) if item.get("codec_type")=="audio"]
    all_tags=dict(format_tags)
    attached_pictures=sum(1 for item in data.get("streams",[]) if item.get("codec_type")=="video" and (item.get("disposition") or {}).get("attached_pic"))
    for stream in streams:
        if isinstance(stream.get("tags"),dict):
            all_tags.update(stream["tags"])
    normalized={str(key).strip().casefold().replace(" ","_") for key in all_tags}
    groups={
        "title":{"title","tit2"},
        "artist":{"artist","tpe1"},
        "album":{"album","talb"},
        "date/year":{"date","year","tdrc","tyer","originaldate"},
        "genre":{"genre","tcon"},
        "track number":{"track","tracknumber","trck"},
        "disc number":{"disc","discnumber","tpos"},
        "album artist":{"album_artist","albumartist","tpe2"},
        "composer":{"composer","tcom"}
    }
    present=[name for name,keys in groups.items() if normalized&keys]
    missing=[name for name in groups if name not in present]
    lines=[
        "Audio metadata and tag completeness audit",
        f"Bytes: {size:,}; container: {fmt.get('format_name','unknown')}; duration: {float(fmt.get('duration') or 0):.2f}s; audio streams: {len(streams):,}",
        f"Metadata tag keys: {len(normalized):,}; attached cover-art streams: {attached_pictures:,}",
        "Present tag groups: "+(", ".join(present) if present else "none"),
        "Missing common tag groups: "+(", ".join(missing) if missing else "none"),
        "Tag values, file path and embedded cover images are withheld; this checks completeness, not correctness."
    ]
    for stream in streams[:8]:
        lines.append(f"Audio stream: {stream.get('codec_name','unknown')} · {stream.get('sample_rate','?')} Hz · {stream.get('channels','?')} channel(s)")
    return tool_text("\n".join(lines),"Audio tag audit")


def image_similarity_audit(p):
    import io
    import math
    from PIL import Image,ImageOps
    if not zipfile.is_zipfile(p):
        raise RuntimeError("Gửi ZIP chứa bộ ảnh cần tìm ảnh gần giống.")
    def phash_16(image):
        size=32
        resized=image.convert("L").resize((size,size),Image.Resampling.LANCZOS)
        flattened=getattr(resized,"get_flattened_data",None)
        pixels=list(flattened() if flattened else resized.getdata())
        matrix=[pixels[row*size:(row+1)*size] for row in range(size)]
        cosine=[[math.cos(math.pi*(2*position+1)*frequency/(2*size)) for position in range(size)] for frequency in range(16)]
        horizontal=[[sum(matrix[row][x]*cosine[u][x] for x in range(size)) for u in range(16)] for row in range(size)]
        coefficients=[[sum(horizontal[y][u]*cosine[v][y] for y in range(size)) for u in range(16)] for v in range(16)]
        values=[coefficients[v][u] for v in range(16) for u in range(16) if v or u]
        median=sorted(values)[len(values)//2]
        result=0
        bit=0
        for v in range(16):
            for u in range(16):
                if v==0 and u==0:
                    continue
                if coefficients[v][u]>=median:
                    result|=(1<<bit)
                bit+=1
        return result
    records=[]
    total_bytes=0
    allowed={".jpg",".jpeg",".png",".webp",".bmp",".tif",".tiff"}
    try:
        with zipfile.ZipFile(p) as archive:
            infos=archive.infolist()
            if len(infos)>1000:
                raise RuntimeError("ZIP vượt giới hạn 1.000 entries.")
            seen=set()
            members=[]
            for info in infos:
                if info.is_dir():
                    continue
                _safe_archive_parts(info.filename)
                if info.filename in seen:
                    raise RuntimeError("ZIP chứa tên tệp trùng lặp.")
                seen.add(info.filename)
                if Path(info.filename).suffix.lower() not in allowed:
                    continue
                if info.flag_bits&0x1 or info.file_size>20*1024*1024:
                    continue
                total_bytes+=info.file_size
                if total_bytes>150*1024*1024:
                    raise RuntimeError("ZIP vượt 150 MiB dữ liệu ảnh khai báo.")
                members.append(info)
                if len(members)>200:
                    raise RuntimeError("Tối đa 200 ảnh trong một lần so sánh.")
            for info in members:
                payload=archive.read(info)
                with Image.open(io.BytesIO(payload)) as raw:
                    _guard_image_dimensions(raw)
                    image=ImageOps.exif_transpose(raw).convert("RGB")
                    perceptual=phash_16(image)
                records.append((info.filename,hashlib.sha256(payload).hexdigest(),perceptual))
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError("Không thể đọc ZIP hoặc một tệp ảnh bị hỏng/không an toàn.") from exc
    if not records:
        raise RuntimeError("ZIP không có ảnh được hỗ trợ.")
    matches=[]
    for left in range(len(records)):
        for right in range(left+1,len(records)):
            a,b=records[left],records[right]
            distance=(a[2]^b[2]).bit_count()
            if a[1]==b[1]:
                matches.append((a[0],b[0],"exact-sha256",0))
            elif distance<=20:
                matches.append((a[0],b[0],"near-visual-phash16",distance))
    out=p.with_name(p.stem+"-image-similarity.csv")
    with out.open("w",encoding="utf-8-sig",newline="") as target:
        writer=csv.writer(target,lineterminator="\n")
        writer.writerow(["image_a","image_b","match_type","phash16_hamming_distance"])
        writer.writerows([(_spreadsheet_safe(a),_spreadsheet_safe(b),kind,distance) for a,b,kind,distance in matches])
    return {"summary":f"Đã phân tích {len(records):,} ảnh, {total_bytes:,} byte giải nén; tìm thấy {len(matches):,} cặp giống/gần giống. Perceptual hash DCT 16×16, ngưỡng ≤20/255.","output_path":str(out)}


def json_schema_validate(p):
    import jsonschema
    size=p.stat().st_size
    if size>10*1024*1024:
        raise RuntimeError("JSON Schema validation giới hạn input 10 MiB.")
    try:
        envelope=json.loads(p.read_text(encoding="utf-8-sig"))
    except (UnicodeError,json.JSONDecodeError) as exc:
        raise RuntimeError("Input phải là JSON UTF-8 hợp lệ.") from exc
    if not isinstance(envelope,dict) or not isinstance(envelope.get("schema"),dict) or "data" not in envelope:
        raise RuntimeError("JSON phải có hai trường cấp gốc: schema (object) và data.")
    schema=envelope["schema"]
    instance=envelope["data"]
    def reject_remote_refs(value):
        if isinstance(value,dict):
            reference=value.get("$ref")
            if isinstance(reference,str) and not reference.startswith("#"):
                raise RuntimeError("Remote/external $ref bị chặn; chỉ hỗ trợ tham chiếu cục bộ trong schema.")
            for child in value.values():
                reject_remote_refs(child)
        elif isinstance(value,list):
            for child in value:
                reject_remote_refs(child)
    reject_remote_refs(schema)
    try:
        validator_class=jsonschema.validators.validator_for(schema)
        validator_class.check_schema(schema)
        validator=validator_class(schema)
        errors=[]
        for error in validator.iter_errors(instance):
            errors.append(error)
            if len(errors)>=501:
                break
    except Exception as exc:
        raise RuntimeError("Schema không hợp lệ hoặc JSON Schema draft chưa được hỗ trợ.") from exc
    truncated=len(errors)>500
    errors=errors[:500]
    lines=[
        "JSON Schema validation report",
        f"Draft: {schema.get('$schema','default')}; result: {'VALID' if not errors else 'INVALID'}",
        f"Validation errors: {len(errors):,}"+(" (first 500 shown; additional errors omitted)" if truncated else ""),
        "Instance values are never copied into this report."
    ]
    for error in errors[:100]:
        pointer="/" + "/".join(str(part).replace("~","~0").replace("/","~1") for part in error.absolute_path) if error.absolute_path else "(root)"
        lines.append(f"- {pointer}: rule={error.validator or 'unknown'}")
    if len(errors)>100:
        lines.append(f"- {len(errors)-100:,} additional error locations omitted.")
    return tool_text("\n".join(lines),"JSON Schema validation")


def epub_structure_audit(p):
    import xml.etree.ElementTree as ET
    from urllib.parse import unquote
    size=p.stat().st_size
    if size>20*1024*1024:
        raise RuntimeError("EPUB input vượt giới hạn 20 MiB.")
    def parse_xml(raw):
        if re.search(rb"<!\s*(DOCTYPE|ENTITY)\b",raw,re.I):
            raise RuntimeError("EPUB XML DTD/ENTITY bị chặn.")
        return ET.fromstring(raw)
    try:
        with zipfile.ZipFile(p) as archive:
            infos=archive.infolist()
            if len(infos)>3000 or sum(item.file_size for item in infos)>120*1024*1024:
                raise RuntimeError("EPUB vượt 3.000 entries hoặc 120 MiB dữ liệu giải nén.")
            names=[item.filename for item in infos]
            name_set=set(names)
            duplicate_paths=len(names)-len(name_set)
            mimetype_ok=False
            if infos and infos[0].filename=="mimetype":
                info=infos[0]
                if info.file_size<=100 and info.compress_type==zipfile.ZIP_STORED:
                    mimetype_ok=archive.read(info)==b"application/epub+zip"
            if "META-INF/container.xml" not in name_set:
                raise RuntimeError("EPUB thiếu META-INF/container.xml.")
            container_raw=archive.read("META-INF/container.xml")
            if len(container_raw)>1024*1024:
                raise RuntimeError("container.xml vượt 1 MiB.")
            container=parse_xml(container_raw)
            rootfiles=container.findall(".//{*}rootfile")
            if not rootfiles:
                raise RuntimeError("Không tìm thấy OPF rootfile trong container.xml.")
            opf_path=unquote(rootfiles[0].attrib.get("full-path",""))
            if not opf_path or opf_path.startswith(("/","\\")) or ".." in Path(opf_path.replace("\\","/")).parts or opf_path not in name_set:
                raise RuntimeError("Đường dẫn OPF không an toàn hoặc không tồn tại.")
            opf_raw=archive.read(opf_path)
            if len(opf_raw)>3*1024*1024:
                raise RuntimeError("OPF package vượt 3 MiB.")
            package=parse_xml(opf_raw)
            metadata=package.find(".//{*}metadata")
            title_count=len(metadata.findall(".//{*}title")) if metadata is not None else 0
            creator_count=len(metadata.findall(".//{*}creator")) if metadata is not None else 0
            language_count=len(metadata.findall(".//{*}language")) if metadata is not None else 0
            manifest=package.findall(".//{*}manifest/{*}item")
            spine=package.findall(".//{*}spine/{*}itemref")
            identifiers=set()
            duplicate_ids=0
            missing_hrefs=0
            unsafe_hrefs=0
            for item in manifest:
                item_id=item.attrib.get("id","")
                if item_id in identifiers:
                    duplicate_ids+=1
                identifiers.add(item_id)
                href=item.attrib.get("href","")
                parsed=urllib.parse.urlsplit(href)
                if parsed.scheme or parsed.netloc:
                    unsafe_hrefs+=1
                    continue
                target=unquote(parsed.path)
                normalized=posixpath.normpath(posixpath.join(posixpath.dirname(opf_path),target))
                if target.startswith(("/","\\")) or normalized==".." or normalized.startswith("../") or "\\" in target:
                    unsafe_hrefs+=1
                elif normalized not in name_set:
                    missing_hrefs+=1
            unresolved_spine=sum(1 for ref in spine if ref.attrib.get("idref") not in identifiers)
            navigation_items=sum(1 for item in manifest if "nav" in item.attrib.get("properties","").split())
            image_items=sum(1 for item in manifest if item.attrib.get("media-type","").startswith("image/"))
            scripted_items=sum(1 for item in manifest if "scripted" in item.attrib.get("properties","").split())
            encrypted="META-INF/encryption.xml" in name_set
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError("Không thể đọc cấu trúc EPUB hợp lệ hoặc thành phần ZIP/XML bị hỏng.") from exc
    lines=[
        "EPUB package structure audit",
        f"Archive entries: {len(infos):,}; duplicate paths: {duplicate_paths:,}; mimetype first/stored/content: {'OK' if mimetype_ok else 'problem'}",
        f"OPF manifest items: {len(manifest):,}; spine entries: {len(spine):,}; duplicate manifest IDs: {duplicate_ids:,}",
        f"Manifest href targets missing: {missing_hrefs:,}; unsafe href targets: {unsafe_hrefs:,}; unresolved spine idrefs: {unresolved_spine:,}",
        f"Navigation documents: {navigation_items:,}; image resources: {image_items:,}; scripted resources: {scripted_items:,}; encrypted metadata present: {int(encrypted)}",
        f"Metadata field counts: title={title_count:,}; creator={creator_count:,}; language={language_count:,}",
        "Book title, authors, chapter text and archive paths are withheld. This is a local package-structure audit, not a full EPUB conformance certification."
    ]
    return tool_text("\n".join(lines),"EPUB structure audit")


def markdown_quality_audit(p):
    size=p.stat().st_size
    if size>5*1024*1024:
        raise RuntimeError("Markdown quality audit giới hạn input 5 MiB.")
    try:
        raw=p.read_text(encoding="utf-8-sig")
    except UnicodeError as exc:
        raise RuntimeError("Markdown phải là văn bản UTF-8.") from exc
    source_lines=raw.splitlines()
    if len(source_lines)>100000:
        raise RuntimeError("Markdown vượt 100.000 dòng.")
    trailing=long_lines=heading_jumps=duplicate_headings=heading_spacing=empty_links=0
    fence_open=False
    fence_char=""
    fence_len=0
    fence_start=0
    previous_heading=0
    heading_seen={}
    findings=[]
    def add(line,rule):
        if len(findings)<120:
            findings.append((line,rule))
    fence_re=re.compile(r"^\s{0,3}(" + re.escape(chr(96)) + r"{3,}|~{3,})")
    for number,line in enumerate(source_lines,1):
        if line.rstrip(" \t")!=line:
            trailing+=1
            add(number,"trailing-whitespace")
        if len(line)>120:
            long_lines+=1
            add(number,"line-over-120")
        fence=fence_re.match(line)
        if fence:
            token=fence.group(1)
            if not fence_open:
                fence_open=True
                fence_char=token[0]
                fence_len=len(token)
                fence_start=number
            elif token[0]==fence_char and len(token)>=fence_len:
                fence_open=False
            continue
        if fence_open:
            continue
        heading=re.match(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$",line)
        if heading:
            level=len(heading.group(1))
            heading_text=heading.group(2).strip().casefold()
            if previous_heading and level>previous_heading+1:
                heading_jumps+=1
                add(number,"heading-level-jump")
            if heading_seen.get(heading_text):
                duplicate_headings+=1
                add(number,"duplicate-heading")
            heading_seen[heading_text]=True
            previous_heading=level
            if number>1 and source_lines[number-2].strip():
                heading_spacing+=1
                add(number,"heading-without-blank-line-before")
        if re.search(r"\[[^\]]*\]\(\s*\)",line) or re.search(r"\[[^\]]*\]\[\s*\]",line):
            empty_links+=1
            add(number,"empty-link-target")
    if fence_open:
        add(fence_start,"unclosed-code-fence")
    lines=[
        "Markdown quality audit",
        f"Lines: {len(source_lines):,}; bytes: {size:,}; repeated headings: {duplicate_headings:,}",
        f"Trailing-whitespace lines: {trailing:,}; long lines (>120 chars): {long_lines:,}; heading-level jumps: {heading_jumps:,}",
        f"Heading spacing findings: {heading_spacing:,}; empty link targets: {empty_links:,}; unclosed code fence: {int(fence_open)}",
        f"Findings listed: {len(findings):,} (maximum 120); source line contents are not copied into the report."
    ]
    lines.extend(f"- Line {line}: {rule}" for line,rule in findings)
    return tool_text("\n".join(lines),"Markdown quality audit")


def dns_zone_audit(p):
    import dns.rdatatype
    import dns.zone
    size=p.stat().st_size
    if size>10*1024*1024:
        raise RuntimeError("DNS zone audit giới hạn input 10 MiB.")
    try:
        raw=p.read_text(encoding="utf-8-sig")
    except UnicodeError as exc:
        raise RuntimeError("DNS zone file phải là văn bản UTF-8.") from exc
    if re.search(r"(?im)^\s*\$(?:INCLUDE|GENERATE)\b",raw):
        raise RuntimeError("$INCLUDE và $GENERATE bị chặn để tránh truy cập file ngoài hoặc mở rộng dữ liệu ngoài dự kiến.")
    try:
        zone=dns.zone.from_text(raw,origin=None,relativize=False,allow_include=False,check_origin=False)
    except Exception as exc:
        raise RuntimeError("DNS zone không hợp lệ; kiểm tra cú pháp BIND, $ORIGIN và record data.") from exc
    counts={}
    owner_names=records=soa_count=ns_count=mx_count=txt_count=aaaa_count=a_count=cname_count=0
    for owner,node in zone.nodes.items():
        owner_names+=1
        for rrset in node.rdatasets:
            label=dns.rdatatype.to_text(rrset.rdtype)
            amount=len(rrset)
            counts[label]=counts.get(label,0)+amount
            records+=amount
            if rrset.rdtype==dns.rdatatype.SOA:
                soa_count+=amount
            elif rrset.rdtype==dns.rdatatype.NS:
                ns_count+=amount
            elif rrset.rdtype==dns.rdatatype.MX:
                mx_count+=amount
            elif rrset.rdtype==dns.rdatatype.TXT:
                txt_count+=amount
            elif rrset.rdtype==dns.rdatatype.AAAA:
                aaaa_count+=amount
            elif rrset.rdtype==dns.rdatatype.A:
                a_count+=amount
            elif rrset.rdtype==dns.rdatatype.CNAME:
                cname_count+=amount
    lines=[
        "DNS zone file audit",
        f"Origin defined: {int(zone.origin is not None)}; owner names: {owner_names:,}; records: {records:,}",
        f"SOA records: {soa_count:,}; NS: {ns_count:,}; A: {a_count:,}; AAAA: {aaaa_count:,}; MX: {mx_count:,}; CNAME: {cname_count:,}; TXT: {txt_count:,}",
        "Record-type counts: "+(", ".join(f"{name}={count:,}" for name,count in sorted(counts.items())) or "none"),
        "SOA/NS presence: "+("SOA missing" if not soa_count else "SOA present")+"; "+("NS missing" if not ns_count else "NS present"),
        "Domain names, IP addresses, TXT contents and mailbox values are never included. No DNS queries or zone transfers are performed."
    ]
    return tool_text("\n".join(lines),"DNS zone audit")


def x509_certificate_audit(p):
    import datetime
    from cryptography import x509
    from cryptography.hazmat.primitives.asymmetric import rsa,ec,dsa,ed25519,ed448
    size=p.stat().st_size
    if size>5*1024*1024:
        raise RuntimeError("Certificate audit giới hạn input 5 MiB.")
    raw=p.read_bytes()
    blocks=re.findall(rb"-----BEGIN CERTIFICATE-----[\s\S]*?-----END CERTIFICATE-----",raw)
    try:
        certs=[x509.load_pem_x509_certificate(block) for block in blocks] if blocks else [x509.load_der_x509_certificate(raw)]
    except Exception as exc:
        raise RuntimeError("Không thể phân tích PEM/DER X.509 certificate; private keys không được hỗ trợ.") from exc
    if not 1<=len(certs)<=50:
        raise RuntimeError("Certificate bundle phải có từ 1 đến 50 certificates.")
    now=datetime.datetime.now(datetime.timezone.utc)
    expired=not_yet=expiring=weak_signatures=weak_keys=ca_count=self_issued=0
    algorithms={}
    key_types={}
    san_dns=san_ip=0
    for cert in certs:
        not_before=cert.not_valid_before_utc
        not_after=cert.not_valid_after_utc
        if now<not_before:
            not_yet+=1
        elif now>=not_after:
            expired+=1
        elif not_after-now<=datetime.timedelta(days=30):
            expiring+=1
        algorithm=getattr(cert.signature_hash_algorithm,"name","unknown") if cert.signature_hash_algorithm else "unknown"
        algorithms[algorithm]=algorithms.get(algorithm,0)+1
        if algorithm.lower() in {"md5","sha1"}:
            weak_signatures+=1
        key=cert.public_key()
        if isinstance(key,rsa.RSAPublicKey):
            key_name="RSA"
            key_size=key.key_size
            if key_size<2048:
                weak_keys+=1
        elif isinstance(key,ec.EllipticCurvePublicKey):
            key_name="EC"
            key_size=key.key_size
            if key_size<224:
                weak_keys+=1
        elif isinstance(key,dsa.DSAPublicKey):
            key_name="DSA"
            key_size=key.key_size
            if key_size<2048:
                weak_keys+=1
        elif isinstance(key,ed25519.Ed25519PublicKey):
            key_name="Ed25519"
            key_size=256
        elif isinstance(key,ed448.Ed448PublicKey):
            key_name="Ed448"
            key_size=456
        else:
            key_name=type(key).__name__
            key_size=getattr(key,"key_size",0)
        key_types[f"{key_name}-{key_size}"]=key_types.get(f"{key_name}-{key_size}",0)+1
        try:
            basic=cert.extensions.get_extension_for_class(x509.BasicConstraints).value
            if basic.ca:
                ca_count+=1
        except x509.ExtensionNotFound:
            pass
        if cert.subject==cert.issuer:
            self_issued+=1
        try:
            san=cert.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
            san_dns+=len(san.get_values_for_type(x509.DNSName))
            san_ip+=len(san.get_values_for_type(x509.IPAddress))
        except x509.ExtensionNotFound:
            pass
    lines=[
        "X.509 certificate bundle audit",
        f"Certificates: {len(certs):,}; expired: {expired:,}; not-yet-valid: {not_yet:,}; expiring within 30 days: {expiring:,}",
        f"CA certificates: {ca_count:,}; subject=issuer certificates: {self_issued:,}; weak signature hashes (MD5/SHA-1): {weak_signatures:,}; weak public keys: {weak_keys:,}",
        "Signature hash algorithms: "+(", ".join(f"{name}={count:,}" for name,count in sorted(algorithms.items())) or "none"),
        "Public key types/sizes: "+(", ".join(f"{name}={count:,}" for name,count in sorted(key_types.items())) or "none"),
        f"Subject Alternative Name counts: DNS={san_dns:,}; IP={san_ip:,}",
        "Subjects, issuers, serials, SAN values and public-key bytes are withheld. No chain trust, revocation or hostname validation is performed."
    ]
    return tool_text("\n".join(lines),"X.509 certificate audit")


def rss_atom_audit(p):
    import xml.etree.ElementTree as ET
    size=p.stat().st_size
    if size>10*1024*1024:
        raise RuntimeError("RSS/Atom input vượt giới hạn 10 MiB.")
    raw=p.read_bytes()
    if re.search(rb"<!\s*(DOCTYPE|ENTITY)\b",raw,re.I):
        raise RuntimeError("RSS/Atom DTD/ENTITY bị chặn.")
    try:
        root=ET.fromstring(raw)
    except ET.ParseError as exc:
        raise RuntimeError("RSS/Atom XML không hợp lệ.") from exc
    def local(tag):
        return tag.rsplit("}",1)[-1].lower()
    root_type=local(root.tag)
    if root_type not in {"rss","feed","rdf"}:
        raise RuntimeError("Chỉ hỗ trợ RSS, Atom và RSS 1.0/RDF feed.")
    entries=[node for node in root.iter() if local(node.tag) in {"item","entry"}]
    if len(entries)>50000:
        raise RuntimeError("Feed vượt giới hạn 50.000 entries.")
    missing_title=missing_id=missing_link=missing_date=0
    duplicate_ids=0
    ids=set()
    enclosures=authors=categories=0
    for entry in entries:
        children=list(entry)
        def child_values(names):
            return [child for child in children if local(child.tag) in names]
        titles=child_values({"title"})
        if not any((node.text or "").strip() for node in titles):
            missing_title+=1
        id_nodes=child_values({"id","guid"})
        identifier=next(((node.text or "").strip() for node in id_nodes if (node.text or "").strip()),"")
        if not identifier:
            missing_id+=1
        elif identifier in ids:
            duplicate_ids+=1
        else:
            ids.add(identifier)
        links=child_values({"link"})
        valid_link=False
        for node in links:
            href=(node.attrib.get("href") or node.text or "").strip()
            if href:
                valid_link=True
                break
        if not valid_link:
            missing_link+=1
        if not child_values({"published","pubdate","updated","date","modified"}):
            missing_date+=1
        enclosures+=len(child_values({"enclosure"}))
        authors+=len(child_values({"author","creator"}))
        categories+=len(child_values({"category"}))
    channels=sum(1 for node in root.iter() if local(node.tag)=="channel")
    lines=[
        "RSS/Atom feed structure audit",
        f"Root format: {root_type}; channel elements: {channels:,}; entries: {len(entries):,}",
        f"Entries missing title: {missing_title:,}; missing ID/GUID: {missing_id:,}; duplicate IDs: {duplicate_ids:,}",
        f"Entries missing link: {missing_link:,}; missing date fields: {missing_date:,}",
        f"Enclosure elements: {enclosures:,}; author/creator elements: {authors:,}; category elements: {categories:,}",
        "Feed title, entry titles, URLs, authors, descriptions and content are withheld; this is an offline structural audit."
    ]
    return tool_text("\n".join(lines),"RSS/Atom feed audit")


def sitemap_xml_audit(p):
    import xml.etree.ElementTree as ET
    size=p.stat().st_size
    if size>20*1024*1024:
        raise RuntimeError("Sitemap XML vượt giới hạn 20 MiB.")
    raw=p.read_bytes()
    if re.search(rb"<!\s*(DOCTYPE|ENTITY)\b",raw,re.I):
        raise RuntimeError("Sitemap DTD/ENTITY bị chặn.")
    try:
        root=ET.fromstring(raw)
    except ET.ParseError as exc:
        raise RuntimeError("Sitemap XML không hợp lệ.") from exc
    def local(tag):
        return tag.rsplit("}",1)[-1].lower()
    root_type=local(root.tag)
    if root_type not in {"urlset","sitemapindex"}:
        raise RuntimeError("Root phải là urlset hoặc sitemapindex.")
    entry_name="url" if root_type=="urlset" else "sitemap"
    entries=[child for child in list(root) if local(child.tag)==entry_name]
    if len(entries)>50000:
        raise RuntimeError("Sitemap vượt giới hạn 50.000 entries.")
    missing_loc=duplicate_loc=loc_count=lastmod_count=priority_invalid=changefreq_invalid=0
    locs=set()
    valid_freq={"always","hourly","daily","weekly","monthly","yearly","never"}
    for entry in entries:
        locs_for_entry=[child for child in list(entry) if local(child.tag)=="loc"]
        loc=next(((node.text or "").strip() for node in locs_for_entry if (node.text or "").strip()),"")
        if not loc:
            missing_loc+=1
        else:
            loc_count+=1
            if loc in locs:
                duplicate_loc+=1
            locs.add(loc)
        for node in list(entry):
            tag=local(node.tag)
            value=(node.text or "").strip()
            if tag=="lastmod" and value:
                lastmod_count+=1
            elif tag=="priority" and value:
                try:
                    number=float(value)
                    if not 0<=number<=1:
                        priority_invalid+=1
                except ValueError:
                    priority_invalid+=1
            elif tag=="changefreq" and value.casefold() not in valid_freq:
                changefreq_invalid+=1
    lines=[
        "XML sitemap audit",
        f"Root: {root_type}; entries: {len(entries):,}; non-empty loc fields: {loc_count:,}; missing loc: {missing_loc:,}; duplicate loc values: {duplicate_loc:,}",
        f"lastmod fields: {lastmod_count:,}; invalid priority values: {priority_invalid:,}; invalid changefreq values: {changefreq_invalid:,}",
        "Sitemap URLs, lastmod timestamps and path values are withheld; no URL is fetched or crawled."
    ]
    return tool_text("\n".join(lines),"Sitemap XML audit")


def robots_txt_audit(p):
    size=p.stat().st_size
    if size>2*1024*1024:
        raise RuntimeError("robots.txt audit giới hạn input 2 MiB.")
    try:
        raw=p.read_text(encoding="utf-8-sig")
    except UnicodeError as exc:
        raise RuntimeError("robots.txt phải là văn bản UTF-8.") from exc
    lines=raw.splitlines()
    if len(lines)>20000:
        raise RuntimeError("robots.txt vượt 20.000 dòng.")
    groups=rules=allow=disallow=sitemaps=crawl_delay=host=unknown=malformed=orphan_rules=0
    has_agent=False
    has_rule=False
    known={"user-agent","allow","disallow","sitemap","crawl-delay","host","clean-param","request-rate","visit-time"}
    for line in lines:
        cleaned=line.split("#",1)[0].strip()
        if not cleaned:
            if has_rule:
                has_agent=False
                has_rule=False
            continue
        if ":" not in cleaned:
            malformed+=1
            continue
        directive,value=cleaned.split(":",1)
        directive=directive.strip().casefold()
        value=value.strip()
        if directive=="user-agent":
            if has_rule:
                has_agent=False
                has_rule=False
            groups+=1
            has_agent=True
            if not value:
                malformed+=1
        elif directive in {"allow","disallow"}:
            rules+=1
            has_rule=True
            if not has_agent:
                orphan_rules+=1
            if directive=="allow":
                allow+=1
            else:
                disallow+=1
        elif directive=="sitemap":
            sitemaps+=1
        elif directive=="crawl-delay":
            crawl_delay+=1
            has_rule=True
            if not value:
                malformed+=1
        elif directive=="host":
            host+=1
            has_rule=True
        elif directive in known:
            has_rule=True
        else:
            unknown+=1
    lines_out=[
        "robots.txt offline audit",
        f"Lines: {len(lines):,}; user-agent groups: {groups:,}; allow/disallow rules: {rules:,} ({allow:,} allow / {disallow:,} disallow)",
        f"Sitemap directives: {sitemaps:,}; crawl-delay directives: {crawl_delay:,}; Host directives: {host:,}",
        f"Rules outside a user-agent group: {orphan_rules:,}; malformed lines: {malformed:,}; unknown directives: {unknown:,}",
        "Directive paths, user-agent values and sitemap URLs are withheld. No robots policy is fetched and no crawl is performed."
    ]
    return tool_text("\n".join(lines_out),"robots.txt audit")


def jsonl_profile(p):
    size=p.stat().st_size
    if size>20*1024*1024:
        raise RuntimeError("JSONL profile giới hạn input 20 MiB.")
    records=invalid_lines=non_object=duplicate_keys=long_lines=0
    key_counts={}
    key_types={}
    invalid_line_numbers=[]
    def pairs_hook(pairs):
        nonlocal duplicate_keys
        result={}
        for key,value in pairs:
            if key in result:
                duplicate_keys+=1
            result[key]=value
        return result
    def type_name(value):
        if value is None:
            return "null"
        if isinstance(value,bool):
            return "boolean"
        if isinstance(value,(int,float)):
            return "number"
        if isinstance(value,str):
            return "string"
        if isinstance(value,list):
            return "array"
        if isinstance(value,dict):
            return "object"
        return "other"
    with p.open("r",encoding="utf-8-sig",errors="replace") as handle:
        for line_number,line in enumerate(handle,1):
            if line_number>100000:
                raise RuntimeError("JSONL vượt giới hạn 100.000 dòng.")
            if not line.strip():
                continue
            if len(line)>1024*1024:
                long_lines+=1
                invalid_lines+=1
                if len(invalid_line_numbers)<20:
                    invalid_line_numbers.append(line_number)
                continue
            try:
                value=json.loads(line,object_pairs_hook=pairs_hook)
            except json.JSONDecodeError:
                invalid_lines+=1
                if len(invalid_line_numbers)<20:
                    invalid_line_numbers.append(line_number)
                continue
            records+=1
            if not isinstance(value,dict):
                non_object+=1
                continue
            for key,item in value.items():
                key=str(key)
                key_counts[key]=key_counts.get(key,0)+1
                types=key_types.setdefault(key,{})
                name=type_name(item)
                types[name]=types.get(name,0)+1
    top_keys=sorted(key_counts,key=lambda key:(-key_counts[key],key))[:30]
    lines=[
        "JSON Lines data profile",
        f"Bytes: {size:,}; valid records: {records:,}; invalid/oversized lines: {invalid_lines:,}; non-object records: {non_object:,}",
        f"Top-level field names: {len(key_counts):,}; duplicate object keys encountered: {duplicate_keys:,}; oversized lines: {long_lines:,}",
        "Most common field presence and value types:"
    ]
    for key in top_keys:
        type_summary=",".join(f"{name}:{count}" for name,count in sorted(key_types[key].items()))
        lines.append(f"- {key[:80]} · present {key_counts[key]:,}/{records:,} records · {type_summary}")
    if invalid_line_numbers:
        lines.append("First invalid/oversized line numbers: "+", ".join(map(str,invalid_line_numbers)))
    lines.append("JSON values are never copied into this report; field names and aggregate type counts only.")
    return tool_text("\n".join(lines),"JSONL data profile")



def image_privacy_audit(p):
    from PIL import Image,ExifTags
    size=p.stat().st_size
    if size>20*1024*1024:
        raise RuntimeError("Image privacy audit giới hạn file 20 MiB.")
    try:
        with Image.open(p) as image:
            _guard_image_dimensions(image)
            exif=image.getexif()
            names={str(ExifTags.TAGS.get(key,key)).casefold() for key in exif.keys()}
            date_tags={"datetime","datetimeoriginal","datetimedigitized"}
            identity_tags={"make","model","bodyserialnumber","cameraserialnumber","serialnumber","lensserialnumber","ownername","cameraownername","artist","usercomment"}
            gps_present=34853 in exif
            dates=len(names&date_tags)
            identity=sum(1 for key in names if key.replace(" ","") in {item.replace(" ","") for item in identity_tags})
            thumbnail_present=any(key in image.info for key in ("thumbnail","exif_thumbnail"))
            xmp_present=any("xmp" in str(key).casefold() for key in image.info)
            iptc_present=any("iptc" in str(key).casefold() or "photoshop" in str(key).casefold() for key in image.info)
            profile_present="icc_profile" in image.info
            tag_count=len(names)
    except Exception as exc:
        raise RuntimeError("Không thể đọc metadata ảnh hợp lệ.") from exc
    lines=[
        "Image metadata privacy audit",
        f"Format: {p.suffix.lower()}; file bytes: {size:,}; EXIF tags: {tag_count:,}",
        f"GPS metadata present: {int(gps_present)}; date/time tags: {dates:,}; identity/device-related tags: {identity:,}",
        f"Embedded thumbnail present: {int(thumbnail_present)}; XMP metadata present: {int(xmp_present)}; IPTC/Photoshop metadata present: {int(iptc_present)}; ICC profile present: {int(profile_present)}",
        "No EXIF values, GPS coordinates, timestamps, camera serials, owner names or image pixels are included."
    ]
    return tool_text("\n".join(lines),"Image privacy audit")


def svg_safety_audit(p):
    import xml.etree.ElementTree as ET
    size=p.stat().st_size
    if size>5*1024*1024:
        raise RuntimeError("SVG safety audit giới hạn input 5 MiB.")
    raw=p.read_bytes()
    if re.search(rb"<!\s*(DOCTYPE|ENTITY)\b",raw,re.I):
        raise RuntimeError("SVG có DTD/ENTITY bị chặn.")
    try:
        root=ET.fromstring(raw)
    except ET.ParseError as exc:
        raise RuntimeError("SVG/XML không hợp lệ.") from exc
    def local(value):
        return value.rsplit("}",1)[-1].casefold()
    if local(root.tag)!="svg":
        raise RuntimeError("Root document phải là SVG.")
    elements=attrs=scripts=foreign_objects=event_handlers=external_refs=unsafe_schemes=css_url_refs=css_imports=embedded_data=0
    stack=[root]
    while stack:
        element=stack.pop()
        elements+=1
        if elements>100000:
            raise RuntimeError("SVG vượt giới hạn 100.000 elements.")
        tag=local(element.tag)
        if tag=="script": scripts+=1
        elif tag=="foreignobject": foreign_objects+=1
        for key,value in element.attrib.items():
            attrs+=1
            if attrs>250000:
                raise RuntimeError("SVG vượt giới hạn 250.000 attributes.")
            name=local(key)
            lower=str(value).strip().casefold()
            if name.startswith("on"):
                event_handlers+=1
            if name in {"href","src"}:
                if lower.startswith(("javascript:","vbscript:","file:")):
                    unsafe_schemes+=1
                elif lower.startswith("data:"):
                    embedded_data+=1
                elif lower and not lower.startswith("#"):
                    parsed=urllib.parse.urlsplit(str(value).strip())
                    if parsed.scheme or parsed.netloc or value.strip().startswith("//"):
                        external_refs+=1
            if "url(" in lower:
                css_url_refs+=lower.count("url(")
                matches=re.findall(r"url\(\s*['\"]?([^)'\"]+)",lower)
                for target in matches:
                    target=target.strip()
                    if target.startswith(("javascript:","vbscript:","file:")):
                        unsafe_schemes+=1
                    elif target.startswith("data:"):
                        embedded_data+=1
                    elif target and not target.startswith("#"):
                        external_refs+=1
            if "@import" in lower:
                css_imports+=lower.count("@import")
                external_refs+=lower.count("@import")
        stack.extend(list(element))
        if element.text and len(element.text)>2*1024*1024:
            raise RuntimeError("Một text node SVG vượt giới hạn 2 MiB.")
    lines=[
        "SVG active-content and external-reference audit",
        f"File bytes: {size:,}; elements: {elements:,}; attributes: {attrs:,}",
        f"Script elements: {scripts:,}; foreignObject elements: {foreign_objects:,}; event-handler attributes: {event_handlers:,}",
        f"External references: {external_refs:,}; unsafe URI schemes: {unsafe_schemes:,}; data URI references: {embedded_data:,}",
        f"CSS url() references: {css_url_refs:,}; CSS @import directives: {css_imports:,}",
        "Attribute values, external URLs, text content and embedded data are not printed. This is a static audit, not a sanitizer or malware verdict."
    ]
    return tool_text("\n".join(lines),"SVG safety audit")


def wcag_contrast_audit(p):
    size=p.stat().st_size
    if size>2*1024*1024:
        raise RuntimeError("WCAG contrast input giới hạn 2 MiB.")
    try:
        raw=p.read_text(encoding="utf-8-sig")
    except UnicodeError as exc:
        raise RuntimeError("Color pairs phải là UTF-8 text.") from exc
    def parse_hex(value):
        value=value.strip().lstrip("#")
        if not re.fullmatch(r"(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})",value):
            raise ValueError
        if len(value)==3:
            value="".join(character*2 for character in value)
        return tuple(int(value[index:index+2],16) for index in (0,2,4))
    def luminance(rgb):
        channels=[]
        for value in rgb:
            channel=value/255.0
            channels.append(channel/12.92 if channel<=0.04045 else ((channel+0.055)/1.055)**2.4)
        return 0.2126*channels[0]+0.7152*channels[1]+0.0722*channels[2]
    valid=invalid=0
    ratios=[]
    for line_number,line in enumerate(raw.splitlines(),1):
        if line_number>5000:
            raise RuntimeError("WCAG contrast input vượt 5.000 dòng.")
        stripped=line.strip()
        if not stripped or stripped.startswith("# "):
            continue
        colors=re.findall(r"(?<![0-9A-Za-z])#?(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})(?![0-9A-Za-z])",stripped)
        if len(colors)!=2:
            invalid+=1
            continue
        try:
            foreground=parse_hex(colors[0])
            background=parse_hex(colors[1])
        except ValueError:
            invalid+=1
            continue
        first=luminance(foreground)
        second=luminance(background)
        ratio=(max(first,second)+0.05)/(min(first,second)+0.05)
        valid+=1
        ratios.append((line_number,ratio))
    if not valid:
        raise RuntimeError("Không tìm thấy cặp màu hợp lệ. Mỗi dòng cần đúng hai mã HEX.")
    aa_normal=sum(ratio>=4.5 for _,ratio in ratios)
    aa_large=sum(ratio>=3.0 for _,ratio in ratios)
    aaa_normal=sum(ratio>=7.0 for _,ratio in ratios)
    aaa_large=sum(ratio>=4.5 for _,ratio in ratios)
    lines=[
        "WCAG color contrast audit",
        f"Valid pairs: {valid:,}; invalid lines skipped: {invalid:,}",
        f"WCAG 2.2 AA: normal text (4.5:1) {aa_normal:,}/{valid:,}; large text (3:1) {aa_large:,}/{valid:,}",
        f"WCAG 2.2 AAA: normal text (7:1) {aaa_normal:,}/{valid:,}; large text (4.5:1) {aaa_large:,}/{valid:,}",
        "Contrast ratio range: "+f"{min(ratio for _,ratio in ratios):.2f}:1 to {max(ratio for _,ratio in ratios):.2f}:1",
        "Input color codes are withheld from the summary. Large text means at least 18pt regular or 14pt bold; this check does not assess non-text UI contrast."
    ]
    lines.extend(f"- Line {line}: {ratio:.2f}:1" for line,ratio in ratios[:100])
    if len(ratios)>100:
        lines.append(f"- {len(ratios)-100:,} additional color-pair ratios omitted.")
    return tool_text("\n".join(lines),"WCAG contrast audit")


def ssh_public_key_audit(p):
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa,ec,dsa,ed25519
    size=p.stat().st_size
    if size>2*1024*1024:
        raise RuntimeError("SSH public-key audit giới hạn file 2 MiB.")
    try:
        raw=p.read_text(encoding="utf-8-sig")
    except UnicodeError as exc:
        raise RuntimeError("SSH key file phải là UTF-8.") from exc
    keys=[]
    errors=0
    if "-----BEGIN PUBLIC KEY-----" in raw or "-----BEGIN RSA PUBLIC KEY-----" in raw:
        try:
            keys.append(serialization.load_pem_public_key(raw.encode("utf-8")))
        except Exception:
            errors+=1
    else:
        for line in raw.splitlines():
            stripped=line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            token_start=None
            for marker in ("ssh-rsa ","ssh-ed25519 ","ssh-dss ","ecdsa-sha2-","sk-ssh-ed25519@openssh.com ","sk-ecdsa-sha2-nistp256@openssh.com "):
                found=stripped.find(marker)
                if found>=0 and (token_start is None or found<token_start):
                    token_start=found
            if token_start is None:
                errors+=1
                continue
            try:
                keys.append(serialization.load_ssh_public_key(stripped[token_start:].encode("ascii")))
            except Exception:
                errors+=1
            if len(keys)+errors>1000:
                raise RuntimeError("SSH file vượt giới hạn 1.000 key lines.")
    if len(keys)>1000:
        raise RuntimeError("SSH file vượt giới hạn 1.000 public keys.")
    if not keys and errors:
        raise RuntimeError("Không phân tích được SSH public key; private keys không được hỗ trợ.")
    algorithms={}
    duplicates=0
    fingerprints=set()
    weak_rsa=weak_ec=weak_dsa=0
    for key in keys:
        encoded=key.public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)
        fingerprint=hashlib.sha256(encoded).digest()
        if fingerprint in fingerprints:
            duplicates+=1
        fingerprints.add(fingerprint)
        if isinstance(key,rsa.RSAPublicKey):
            name="RSA"
            if key.key_size<2048:
                weak_rsa+=1
        elif isinstance(key,ec.EllipticCurvePublicKey):
            name="ECDSA"
            if key.key_size<256:
                weak_ec+=1
        elif isinstance(key,dsa.DSAPublicKey):
            name="DSA"
            weak_dsa+=1
        elif isinstance(key,ed25519.Ed25519PublicKey):
            name="Ed25519"
        else:
            name=type(key).__name__
        algorithms[name]=algorithms.get(name,0)+1
    lines=[
        "SSH public-key inventory audit",
        f"Valid public keys: {len(keys):,}; malformed/comment-only lines: {errors:,}; duplicate public keys: {duplicates:,}",
        "Algorithms: "+(", ".join(f"{name}={count:,}" for name,count in sorted(algorithms.items())) or "none"),
        f"Weak RSA keys (<2048 bits): {weak_rsa:,}; weak ECDSA keys (<256 bits): {weak_ec:,}; DSA keys (deprecated): {weak_dsa:,}",
        "Key comments, fingerprints, public-key blobs and user identities are not included. No SSH server is contacted or scanned."
    ]
    return tool_text("\n".join(lines),"SSH public-key audit")


def archive_checksum_manifest(p):
    size=p.stat().st_size
    if size>20*1024*1024:
        raise RuntimeError("Archive checksum manifest giới hạn ZIP input 20 MiB.")
    out=p.with_name(p.stem+"-sha256-manifest.csv")
    total_declared=0
    rows=[]
    try:
        with zipfile.ZipFile(p) as archive:
            infos=archive.infolist()
            if len(infos)>1000:
                raise RuntimeError("ZIP vượt giới hạn 1.000 entries.")
            seen=set()
            for info in infos:
                if info.is_dir():
                    continue
                _safe_archive_parts(info.filename)
                if info.filename in seen:
                    raise RuntimeError("ZIP chứa đường dẫn trùng lặp.")
                seen.add(info.filename)
                mode=(info.external_attr>>16)&0o170000
                if mode==stat.S_IFLNK:
                    raise RuntimeError("ZIP chứa symbolic link; checksum manifest từ chối symlink.")
                if info.flag_bits&0x1:
                    raise RuntimeError("ZIP chứa entry mã hóa; không thể tính checksum tin cậy.")
                if info.file_size>50*1024*1024:
                    raise RuntimeError("Một archive member vượt 50 MiB.")
                total_declared+=info.file_size
                if total_declared>200*1024*1024:
                    raise RuntimeError("ZIP vượt 200 MiB dữ liệu giải nén khai báo.")
                digest=hashlib.sha256()
                actual=0
                with archive.open(info,"r") as stream:
                    while True:
                        block=stream.read(1024*1024)
                        if not block:
                            break
                        actual+=len(block)
                        if actual>50*1024*1024 or actual>info.file_size:
                            raise RuntimeError("Archive member vượt kích thước khai báo hoặc giới hạn 50 MiB.")
                        digest.update(block)
                if actual!=info.file_size:
                    raise RuntimeError("Archive member có kích thước thực không khớp directory metadata.")
                rows.append((info.filename,actual,digest.hexdigest()))
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError("Không thể đọc ZIP để tạo checksum manifest.") from exc
    with out.open("w",encoding="utf-8-sig",newline="") as handle:
        writer=csv.writer(handle,lineterminator="\n")
        writer.writerow(["path","size_bytes","sha256"])
        writer.writerows([(_spreadsheet_safe(name),count,digest) for name,count,digest in rows])
    return {"summary":f"Đã tạo SHA-256 manifest cho {len(rows):,} tệp, {sum(row[1] for row in rows):,} byte nội dung. Archive không được giải nén ra filesystem; kết quả là CSV.","output_path":str(out)}


def pdf_table_extract(p):
    import io
    try:
        import pdfplumber
    except ImportError as exc:
        raise RuntimeError("Thiếu pdfplumber; runner cần cài dependency của pdf-table-extract.") from exc
    if p.stat().st_size > 20 * 1024 * 1024:
        raise RuntimeError("PDF table extraction giới hạn input 20 MiB.")
    out = p.with_name(p.stem + "-tables.zip")
    total_tables = 0
    total_rows = 0
    total_cells = 0
    table_files = []
    try:
        with pdfplumber.open(p) as pdf:
            if len(pdf.pages) > 200:
                raise RuntimeError("PDF vượt giới hạn 200 trang.")
            with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
                for page_number, page in enumerate(pdf.pages, 1):
                    for table_number, table in enumerate(page.extract_tables() or [], 1):
                        rows = []
                        for raw_row in table or []:
                            row = [str(cell).replace("\x00", "").strip() if cell is not None else "" for cell in raw_row]
                            if any(cell for cell in row):
                                rows.append(row)
                        if not rows:
                            continue
                        columns = max(len(row) for row in rows)
                        if columns > 100:
                            raise RuntimeError("PDF table có hơn 100 cột; đã dừng để giới hạn tài nguyên.")
                        total_tables += 1
                        total_rows += len(rows)
                        total_cells += sum(len(row) for row in rows)
                        if total_tables > 200 or total_rows > 20000 or total_cells > 500000:
                            raise RuntimeError("PDF vượt giới hạn 200 bảng, 20.000 hàng hoặc 500.000 ô.")
                        buffer = io.StringIO(newline="")
                        writer = csv.writer(buffer, lineterminator="\n")
                        for row in rows:
                            writer.writerow([_spreadsheet_safe(cell) for cell in row + [""] * (columns - len(row))])
                        name = f"page-{page_number:03d}-table-{table_number:03d}.csv"
                        bundle.writestr(name, buffer.getvalue())
                        table_files.append(name)
                report = [
                    "Nolane PDF table extraction",
                    f"Pages scanned: {len(pdf.pages)}",
                    f"Tables extracted: {total_tables}",
                    f"Rows: {total_rows}",
                    f"Cells: {total_cells}",
                    "Method: pdfplumber text/geometry extraction; scanned image tables require OCR/table recognition.",
                ]
                bundle.writestr("report.txt", "\n".join(report) + "\n")
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError("Không thể đọc cấu trúc PDF hoặc trích bảng.") from exc
    if out.stat().st_size > MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("ZIP bảng PDF vượt giới hạn output 45 MiB.")
    return {
        "summary": f"Đã quét PDF và trích {total_tables} bảng thành CSV trong ZIP; {total_rows:,} hàng, {total_cells:,} ô. PDF scan không có text layer có thể không trích được bảng.",
        "output_path": str(out),
    }


def json_jmespath_query(p):
    import jmespath
    if p.stat().st_size > 20 * 1024 * 1024:
        raise RuntimeError("JSON JMESPath giới hạn input 20 MiB.")
    try:
        envelope = json.loads(p.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        raise RuntimeError("Đầu vào phải là JSON envelope có query và data.") from exc
    if not isinstance(envelope, dict) or not isinstance(envelope.get("query"), str) or "data" not in envelope:
        raise RuntimeError('JSON cần dạng {"query":"foo.bar[*]","data":{...}}.')
    query = envelope["query"].strip()
    if not query or len(query) > 4096:
        raise RuntimeError("JMESPath query phải có 1–4.096 ký tự.")
    try:
        expression = jmespath.compile(query)
        selected = expression.search(envelope["data"])
    except Exception as exc:
        raise RuntimeError("JMESPath expression không hợp lệ hoặc không thể thực thi.") from exc
    out = p.with_name(p.stem + "-query.json")
    serialized = json.dumps(selected, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    if len(serialized.encode("utf-8")) > 20 * 1024 * 1024:
        raise RuntimeError("Kết quả JSON query vượt giới hạn 20 MiB.")
    out.write_text(serialized, encoding="utf-8")
    return {"summary": f"Đã áp dụng JMESPath query; kết quả có kiểu {type(selected).__name__}, {len(serialized):,} ký tự.", "output_path": str(out)}


def ip_network_report(p):
    import ipaddress
    if p.stat().st_size > 5 * 1024 * 1024:
        raise RuntimeError("IP network report giới hạn input 5 MiB.")
    networks = []
    invalid = 0
    for line_number, raw in enumerate(p.read_text(encoding="utf-8-sig", errors="replace").splitlines(), 1):
        value = raw.split("#", 1)[0].strip()
        if not value:
            continue
        value = value.split()[0].strip(",;")
        try:
            network = ipaddress.ip_network(value, strict=False)
        except ValueError:
            invalid += 1
            continue
        networks.append((line_number, value, network))
        if len(networks) > 2000:
            raise RuntimeError("IP network report giới hạn 2.000 địa chỉ/CIDR.")
    out = p.with_name(p.stem + "-ip-networks.csv")
    rows = []
    for index, (line_number, original, network) in enumerate(networks):
        overlaps = sum(
            1 for other_index, (_, _, other) in enumerate(networks)
            if other_index != index and network.version == other.version and network.overlaps(other)
        )
        rows.append((
            line_number, original, str(network), network.version, network.prefixlen,
            network.num_addresses, int(network.is_private), int(network.is_global),
            int(network.is_multicast), overlaps,
        ))
    with out.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["line", "input", "canonical_network", "ip_version", "prefix_length", "address_count", "is_private", "is_global", "is_multicast", "overlap_count"])
        writer.writerows(rows)
    return {
        "summary": f"Đã phân tích {len(networks):,} IP/CIDR, {invalid:,} dòng không hợp lệ; báo cáo có thông tin mạng canonical, số địa chỉ, phạm vi và số mạng chồng lấn.",
        "output_path": str(out),
    }


def barcode_generate(p):
    try:
        import barcode
        from barcode.writer import ImageWriter
    except ImportError as exc:
        raise RuntimeError("Thiếu python-barcode/Pillow để tạo Code 128.") from exc
    if p.stat().st_size > 2 * 1024 * 1024:
        raise RuntimeError("Barcode input giới hạn 2 MiB.")
    payloads = [line.strip() for line in p.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    if not payloads or len(payloads) > 50:
        raise RuntimeError("Cần từ 1 đến 50 dòng payload barcode không rỗng.")
    for payload in payloads:
        if len(payload) > 120 or any(ord(char) < 32 or ord(char) > 126 for char in payload):
            raise RuntimeError("Code 128 chỉ nhận tối đa 120 ký tự ASCII in được trên mỗi dòng.")
    out = p.with_name(p.stem + "-barcodes.zip")
    manifest = []
    try:
        with tempfile.TemporaryDirectory(prefix="nolane-barcode-", dir=str(p.parent)) as temp_dir:
            with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
                for index, payload in enumerate(payloads, 1):
                    name = f"barcode-{index:03d}.png"
                    target = Path(temp_dir) / f"barcode-{index:03d}"
                    code = barcode.get_barcode_class("code128")(payload, writer=ImageWriter())
                    generated = code.save(str(target), options={
                        "write_text": True, "font_size": 10, "text_distance": 4,
                        "module_width": 0.25, "module_height": 14.0, "quiet_zone": 6.5,
                    })
                    generated_path = Path(generated)
                    if not generated_path.is_file() or generated_path.stat().st_size > 5 * 1024 * 1024:
                        raise RuntimeError("Barcode output không hợp lệ hoặc vượt 5 MiB.")
                    bundle.write(generated_path, arcname=name)
                    manifest.append((index, name))
                buffer = __import__("io").StringIO(newline="")
                writer = csv.writer(buffer, lineterminator="\n")
                writer.writerow(["index", "filename"])
                writer.writerows(manifest)
                bundle.writestr("manifest.csv", buffer.getvalue())
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError("Không thể tạo Code 128 barcode; kiểm tra payload và dependency.") from exc
    if out.stat().st_size > MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("Barcode ZIP vượt giới hạn output 45 MiB.")
    return {"summary": f"Đã tạo {len(payloads)} barcode Code 128 dạng PNG và đóng gói ZIP; payload chỉ được dùng để mã hóa.", "output_path": str(out)}


def docx_to_markdown(p):
    try:
        from docx import Document
        from docx.oxml.table import CT_Tbl
        from docx.oxml.text.paragraph import CT_P
        from docx.table import Table
        from docx.text.paragraph import Paragraph
    except ImportError as exc:
        raise RuntimeError("Thiếu python-docx để chuyển DOCX sang Markdown.") from exc
    if p.stat().st_size > 20 * 1024 * 1024:
        raise RuntimeError("DOCX to Markdown giới hạn input 20 MiB.")
    try:
        document = Document(str(p))
        chunks = []
        block_count = 0
        for child in document.element.body.iterchildren():
            block_count += 1
            if block_count > 50000:
                raise RuntimeError("DOCX vượt giới hạn 50.000 block.")
            if isinstance(child, CT_P):
                paragraph = Paragraph(child, document)
                content_parts = []
                for run in paragraph.runs:
                    value = run.text.replace("\r", "").replace("\n", "  \n")
                    if not value:
                        continue
                    if run.bold:
                        value = "**" + value + "**"
                    if run.italic:
                        value = "*" + value + "*"
                    if run.underline:
                        value = "<u>" + value + "</u>"
                    content_parts.append(value)
                content = "".join(content_parts).strip() or paragraph.text.strip()
                if not content:
                    continue
                style = (paragraph.style.name if paragraph.style else "").strip().lower()
                if style.startswith("heading"):
                    match = re.search(r"([1-9])$", style)
                    level = min(6, int(match.group(1))) if match else 2
                    content = "#" * level + " " + content
                elif style == "title":
                    content = "# " + content
                elif style.startswith("list bullet"):
                    content = "- " + content
                elif style.startswith("list number"):
                    content = "1. " + content
                elif "quote" in style:
                    content = "> " + content
                chunks.append(content)
            elif isinstance(child, CT_Tbl):
                table = Table(child, document)
                rows = []
                for row in table.rows:
                    rows.append([cell.text.replace("\r", "").replace("\n", "<br>").replace("|", r"\|").strip() for cell in row.cells])
                    if len(rows) > 10000:
                        raise RuntimeError("Một DOCX table vượt 10.000 hàng.")
                if rows:
                    width = max(len(row) for row in rows)
                    normalized = [row + [""] * (width - len(row)) for row in rows]
                    chunks.append("| " + " | ".join(normalized[0]) + " |")
                    chunks.append("| " + " | ".join(["---"] * width) + " |")
                    for row in normalized[1:]:
                        chunks.append("| " + " | ".join(row) + " |")
        markdown = "\n\n".join(chunks).strip() + "\n"
        if len(markdown.encode("utf-8")) > 40 * 1024 * 1024:
            raise RuntimeError("Markdown đầu ra vượt 40 MiB.")
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError("Không thể đọc DOCX; tệp có thể hỏng hoặc chứa cấu trúc không hỗ trợ.") from exc
    out = p.with_name(p.stem + ".md")
    out.write_text(markdown, encoding="utf-8")
    return {"summary": f"Đã chuyển DOCX thành Markdown với {block_count:,} block cấu trúc; giữ heading, đoạn, danh sách phổ biến và bảng. Ảnh, header/footer và bố cục trang không được render.", "output_path": str(out)}


def pptx_notes_extract(p):
    try:
        from pptx import Presentation
    except ImportError as exc:
        raise RuntimeError("Thiếu python-pptx để trích speaker notes.") from exc
    if p.stat().st_size > 20 * 1024 * 1024:
        raise RuntimeError("PPTX speaker notes giới hạn input 20 MiB.")
    try:
        presentation = Presentation(str(p))
        if len(presentation.slides) > 300:
            raise RuntimeError("PPTX vượt giới hạn 300 slide.")
        sections = []
        total_chars = 0
        for index, slide in enumerate(presentation.slides, 1):
            try:
                notes = slide.notes_slide.notes_text_frame.text.strip()
            except (AttributeError, KeyError, ValueError):
                notes = ""
            if not notes:
                continue
            total_chars += len(notes)
            if total_chars > 20 * 1024 * 1024:
                raise RuntimeError("Tổng speaker notes vượt 20 MiB text.")
            sections.append(f"## Slide {index}\n\n{notes}")
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError("Không thể đọc speaker notes từ PPTX.") from exc
    out = p.with_name(p.stem + "-speaker-notes.md")
    out.write_text(("\n\n".join(sections) if sections else "Không tìm thấy speaker notes.\n"), encoding="utf-8")
    return {"summary": f"Đã quét {len(presentation.slides)} slide và trích ghi chú từ {len(sections)} slide; không trích nội dung hiển thị trên slide.", "output_path": str(out)}


def fuzzy_match_report(p):
    try:
        from rapidfuzz import fuzz, process
    except ImportError as exc:
        raise RuntimeError("Thiếu rapidfuzz để chạy fuzzy matching.") from exc
    if p.stat().st_size > 5 * 1024 * 1024:
        raise RuntimeError("Fuzzy match report giới hạn input 5 MiB.")
    lines = [line.strip() for line in p.read_text(encoding="utf-8-sig", errors="replace").splitlines() if line.strip()]
    if len(lines) < 2:
        raise RuntimeError("Cần ít nhất hai dòng văn bản không rỗng để so khớp.")
    if len(lines) > 1200:
        raise RuntimeError("Fuzzy matching giới hạn 1.200 dòng để kiểm soát số phép so sánh.")
    if any(len(line) > 2000 for line in lines):
        raise RuntimeError("Mỗi dòng fuzzy matching không được vượt 2.000 ký tự.")
    pairs = {}
    for index, line in enumerate(lines):
        for match, score, other_index in process.extract(line, lines, scorer=fuzz.ratio, limit=8, score_cutoff=85):
            if other_index <= index or match == line:
                continue
            pairs[(index, other_index)] = round(float(score), 2)
            if len(pairs) >= 5000:
                break
        if len(pairs) >= 5000:
            break
    out = p.with_name(p.stem + "-fuzzy-matches.csv")
    ranked = sorted(pairs.items(), key=lambda item: (-item[1], item[0][0], item[0][1]))
    with out.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["left_line", "right_line", "similarity_percent", "left_text", "right_text"])
        for (left, right), score in ranked:
            writer.writerow([left + 1, right + 1, score, _spreadsheet_safe(lines[left]), _spreadsheet_safe(lines[right])])
    return {"summary": f"Đã so khớp {len(lines):,} dòng bằng RapidFuzz; tìm thấy {len(ranked):,} cặp có độ tương đồng từ 85% trở lên (tối đa 5.000 cặp).", "output_path": str(out)}


def csv_to_parquet(p):
    try:
        import duckdb
    except ImportError as exc:
        raise RuntimeError("Thiếu duckdb để chuyển CSV sang Parquet.") from exc
    if p.stat().st_size > 20 * 1024 * 1024:
        raise RuntimeError("CSV to Parquet giới hạn input 20 MiB.")
    out = p.with_name(p.stem + ".parquet")
    source = str(p.resolve()).replace("'", "''")
    target = str(out.resolve()).replace("'", "''")
    connection = duckdb.connect(database=":memory:")
    try:
        connection.execute("SET threads=2")
        connection.execute("SET memory_limit='256MB'")
        connection.execute("SET enable_progress_bar=false")
        relation = f"read_csv_auto('{source}', header=true, all_varchar=true, sample_size=-1)"
        row_count = connection.execute(f"SELECT count(*) FROM {relation}").fetchone()[0]
        if row_count > 1000000:
            raise RuntimeError("CSV vượt giới hạn 1.000.000 hàng.")
        connection.execute(f"COPY (SELECT * FROM {relation}) TO '{target}' (FORMAT PARQUET, COMPRESSION ZSTD)")
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError("Không thể parse CSV để chuyển sang Parquet.") from exc
    finally:
        connection.close()
    if out.stat().st_size > MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("Parquet output vượt giới hạn 45 MiB.")
    return {"summary": f"Đã chuyển {row_count:,} hàng CSV sang Parquet Zstandard; cột được giữ dạng chuỗi để tránh mất số 0 ở đầu.", "output_path": str(out)}


def parquet_to_csv(p):
    try:
        import duckdb
    except ImportError as exc:
        raise RuntimeError("Thiếu duckdb để chuyển Parquet sang CSV.") from exc
    if p.stat().st_size > 20 * 1024 * 1024:
        raise RuntimeError("Parquet to CSV giới hạn input 20 MiB.")
    out = p.with_name(p.stem + ".csv")
    raw_out = p.with_name(p.stem + "-export-raw.csv")
    source = str(p.resolve()).replace("'", "''")
    target = str(raw_out.resolve()).replace("'", "''")
    connection = duckdb.connect(database=":memory:")
    try:
        try:
            connection.execute("SET threads=2")
            connection.execute("SET memory_limit='256MB'")
            connection.execute("SET enable_progress_bar=false")
            relation = f"read_parquet('{source}')"
            row_count = connection.execute(f"SELECT count(*) FROM {relation}").fetchone()[0]
            if row_count > 1000000:
                raise RuntimeError("Parquet vượt giới hạn 1.000.000 hàng.")
            connection.execute(f"COPY (SELECT * FROM {relation}) TO '{target}' (FORMAT CSV, HEADER, DELIMITER ',', QUOTE '\"', ESCAPE '\"')")
            if raw_out.stat().st_size > MAX_PIPELINE_OUTPUT:
                raise RuntimeError("CSV export từ Parquet vượt giới hạn 45 MiB.")
        finally:
            connection.close()
        with raw_out.open("r", encoding="utf-8", newline="") as source_handle:
            reader = csv.reader(source_handle)
            with out.open("w", encoding="utf-8-sig", newline="") as target_handle:
                writer = csv.writer(target_handle, lineterminator="\n")
                for row in reader:
                    writer.writerow([_spreadsheet_safe(cell) for cell in row])
    finally:
        raw_out.unlink(missing_ok=True)
    if out.stat().st_size > MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("CSV output vượt giới hạn 45 MiB.")
    return {"summary": f"Đã chuyển {row_count:,} hàng Parquet sang CSV UTF-8; ô có thể bị hiểu là công thức bảng tính đã được trung hòa.", "output_path": str(out)}



def sqlglot_format(p):
    try:
        import sqlglot
    except ImportError as exc:
        raise RuntimeError("Thiếu sqlglot để parse/format SQL.") from exc
    if p.stat().st_size > 5 * 1024 * 1024:
        raise RuntimeError("SQL formatter giới hạn input 5 MiB.")
    raw=p.read_text(encoding="utf-8-sig")
    read_dialect="auto"; write_dialect="auto"; sql=raw
    if p.suffix.lower()==".json":
        try:
            envelope=json.loads(raw)
        except (UnicodeError,json.JSONDecodeError) as exc:
            raise RuntimeError("JSON SQL envelope không hợp lệ.") from exc
        if not isinstance(envelope,dict) or not isinstance(envelope.get("sql"),str):
            raise RuntimeError('JSON cần trường "sql" dạng chuỗi.')
        sql=envelope["sql"]
        read_dialect=str(envelope.get("read_dialect","auto")).lower()
        write_dialect=str(envelope.get("write_dialect",read_dialect)).lower()
    allowed={"auto","bigquery","clickhouse","databricks","duckdb","mysql","postgres","presto","redshift","snowflake","spark","sqlite","trino","tsql"}
    if read_dialect not in allowed or write_dialect not in allowed:
        raise RuntimeError("Dialect chưa được hỗ trợ; dùng một dialect được công bố trong tool description.")
    if not sql.strip() or len(sql)>1_000_000:
        raise RuntimeError("SQL phải có nội dung và tối đa 1.000.000 ký tự.")
    try:
        read_arg=None if read_dialect=="auto" else read_dialect
        write_arg=None if write_dialect=="auto" else write_dialect
        statements=sqlglot.parse(sql,read=read_arg)
        if not statements or len(statements)>200:
            raise RuntimeError("SQL cần từ 1 đến 200 statement.")
        converted=sqlglot.transpile(sql,read=read_arg,write=write_arg,pretty=True)
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError("SQL không parse được với dialect đã chọn.") from exc
    if not converted:
        raise RuntimeError("SQL không tạo ra câu lệnh sau khi parse.")
    content=";\n\n".join(item.rstrip().rstrip(";") for item in converted)+";\n"
    if len(content.encode("utf-8"))>10*1024*1024:
        raise RuntimeError("SQL formatter output vượt 10 MiB.")
    out=p.with_name(p.stem+"-formatted.sql")
    out.write_text(content,encoding="utf-8")
    return {"summary":f"Đã parse và format {len(converted)} SQL statement từ {read_dialect} sang {write_dialect}; không thực thi truy vấn.","output_path":str(out)}


def sqlfluff_lint(p):
    try:
        from sqlfluff.core import Linter
    except ImportError as exc:
        raise RuntimeError("Thiếu sqlfluff để kiểm tra chất lượng SQL.") from exc
    if p.stat().st_size>5*1024*1024:
        raise RuntimeError("SQL lint giới hạn input 5 MiB.")
    raw=p.read_text(encoding="utf-8-sig")
    if len(raw)>1_000_000:
        raise RuntimeError("SQL lint giới hạn 1.000.000 ký tự.")
    dialect="ansi"
    first_line=raw.splitlines()[0] if raw.splitlines() else ""
    match=re.match(r"\s*--\s*nolane-dialect:\s*([a-z0-9_]+)\s*$",first_line,re.I)
    if match: dialect=match.group(1).lower()
    allowed={"ansi","bigquery","clickhouse","databricks","duckdb","mysql","postgres","redshift","snowflake","sparksql","sqlite","trino","tsql"}
    if dialect not in allowed:
        raise RuntimeError("SQL dialect không nằm trong danh sách hỗ trợ.")
    try:
        lint=Linter(dialect=dialect).lint_string(raw)
        violations=lint.get_violations()
    except Exception as exc:
        raise RuntimeError("SQLFluff không thể phân tích SQL; kiểm tra dialect hoặc cú pháp.") from exc
    lines=[f"Dialect: {dialect}",f"Violations: {len(violations):,}"]
    counts={}
    for issue in violations[:1000]:
        code=issue.rule_code() or "UNKNOWN"
        counts[code]=counts.get(code,0)+1
    for code,count in sorted(counts.items()):
        lines.append(f"- {code}: {count:,}")
    lines.append("First findings (line/column/rule only; SQL source text is not copied):")
    for issue in violations[:200]:
        lines.append(f"- L{issue.line_no or 0}:C{issue.line_pos or 0} · {issue.rule_code() or 'UNKNOWN'} · {issue.description[:180]}")
    if len(violations)>200: lines.append(f"- {len(violations)-200:,} additional findings omitted.")
    return tool_text("\n".join(lines),"SQLFluff lint report")


def python_security_audit(p):
    if p.suffix.lower()!=".py":
        raise RuntimeError("Python security audit chỉ nhận một tệp .py; mã nguồn được phân tích tĩnh và không chạy.")
    if p.stat().st_size>10*1024*1024:
        raise RuntimeError("Python security audit giới hạn input 10 MiB.")
    command=[sys.executable,"-m","bandit","-f","json","-q","--exit-zero",str(p)]
    try:
        process=subprocess.run(command,capture_output=True,text=True,timeout=120,stdin=subprocess.DEVNULL,check=False)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Bandit vượt giới hạn thời gian 120 giây.") from exc
    if process.returncode not in (0,1) or not process.stdout.strip():
        raise RuntimeError("Bandit không tạo được báo cáo JSON hợp lệ.")
    try:
        report=json.loads(process.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Bandit trả về báo cáo không hợp lệ.") from exc
    issues=report.get("results",[])
    if len(issues)>10000:
        raise RuntimeError("Python source có hơn 10.000 finding; đã dừng để giới hạn output.")
    counts={}
    for issue in issues:
        key=(str(issue.get("issue_severity","UNKNOWN")).upper(),str(issue.get("issue_confidence","UNKNOWN")).upper())
        counts[key]=counts.get(key,0)+1
    lines=[f"Static findings: {len(issues):,}","Source code was not executed."]
    for (severity,confidence),count in sorted(counts.items()):
        lines.append(f"- {severity} severity / {confidence} confidence: {count:,}")
    for issue in issues[:200]:
        lines.append(
            f"- L{int(issue.get('line_number') or 0)} · {issue.get('test_id','UNKNOWN')} · "
            f"{str(issue.get('issue_severity','UNKNOWN')).upper()} / {str(issue.get('issue_confidence','UNKNOWN')).upper()}"
        )
    if len(issues)>200: lines.append(f"- {len(issues)-200:,} additional findings omitted.")
    return tool_text("\n".join(lines),"Bandit Python security report")


def unit_convert(p):
    import math
    try:
        import pint
    except ImportError as exc:
        raise RuntimeError("Thiếu Pint để quy đổi đơn vị đo.") from exc
    if p.stat().st_size>2*1024*1024:
        raise RuntimeError("Unit conversion giới hạn input 2 MiB.")
    registry=pint.UnitRegistry(autoconvert_offset_to_baseunit=True)
    rows=[]; invalid=0
    for line_number,raw in enumerate(p.read_text(encoding="utf-8-sig",errors="replace").splitlines(),1):
        line=raw.strip()
        if not line or line.startswith("#"): continue
        if "->" not in line: invalid+=1; continue
        left,right=(part.strip() for part in line.split("->",1))
        if not left or not right or len(left)>160 or len(right)>100:
            invalid+=1; continue
        if not re.fullmatch(r"[0-9eE+\-*/^. \tA-Za-zµμ°_]+",left) or not re.fullmatch(r"[A-Za-zµμ°_*/^. \t0-9]+",right):
            invalid+=1; continue
        try:
            quantity=registry.Quantity(left)
            converted=quantity.to(right)
            magnitude=float(converted.magnitude)
            if not math.isfinite(magnitude): raise ValueError("non-finite")
            result=f"{magnitude:.12g} {converted.units:~}"
            rows.append((line_number,left,right,result))
        except Exception:
            invalid+=1
        if len(rows)+invalid>1000:
            raise RuntimeError("Unit conversion giới hạn 1.000 dòng.")
    if not rows:
        raise RuntimeError("Không có dòng quy đổi hợp lệ. Định dạng: 1 kilometer -> meter")
    out=p.with_name(p.stem+"-converted.csv")
    with out.open("w",encoding="utf-8-sig",newline="") as handle:
        writer=csv.writer(handle,lineterminator="\n")
        writer.writerow(["line","quantity","target_unit","result"])
        for row in rows: writer.writerow([row[0],_spreadsheet_safe(row[1]),_spreadsheet_safe(row[2]),_spreadsheet_safe(row[3])])
    return {"summary":f"Đã quy đổi {len(rows):,} dòng đơn vị bằng Pint; {invalid:,} dòng không hợp lệ hoặc không tương thích đơn vị.","output_path":str(out)}


def mesh_inspect(p):
    import math
    try:
        import trimesh
    except ImportError as exc:
        raise RuntimeError("Thiếu trimesh để đọc mô hình 3D.") from exc
    allowed={".stl",".obj",".ply",".off",".glb",".gltf",".3mf"}
    if p.suffix.lower() not in allowed:
        raise RuntimeError("Mesh inspector hỗ trợ STL, OBJ, PLY, OFF, GLB, GLTF và 3MF.")
    if p.stat().st_size>20*1024*1024:
        raise RuntimeError("3D mesh inspector giới hạn input 20 MiB.")
    try:
        mesh=trimesh.load(str(p),force="mesh",process=False,maintain_order=True)
    except Exception as exc:
        raise RuntimeError("Không thể parse mô hình 3D; tệp có thể hỏng hoặc không được hỗ trợ.") from exc
    if not hasattr(mesh,"vertices") or not hasattr(mesh,"faces"):
        raise RuntimeError("Tệp không chứa triangle mesh được hỗ trợ.")
    vertices=len(mesh.vertices); faces=len(mesh.faces)
    if vertices>2_000_000 or faces>4_000_000:
        raise RuntimeError("Mesh vượt giới hạn 2 triệu vertices hoặc 4 triệu faces.")
    try:
        extents=[float(value) for value in mesh.extents]
        bounds=[[float(value) for value in row] for row in mesh.bounds]
    except Exception:
        extents=[]; bounds=[]
    watertight=None; volume=None
    if faces<=500_000:
        try:
            topology=mesh.copy()
            # STL commonly repeats every triangle vertex; weld exact duplicates
            # only in this analysis copy so topology statistics reflect the surface.
            topology.merge_vertices()
            watertight=bool(topology.is_watertight)
            if watertight:
                value=float(topology.volume)
                if math.isfinite(value): volume=value
        except Exception: pass
    lines=[
        f"Geometry: {mesh.__class__.__name__}",
        f"Vertices: {vertices:,}",f"Faces: {faces:,}",
        f"Watertight: {watertight if watertight is not None else 'not computed (mesh too large or unsupported)'}",
        f"Extents (model units): {extents if extents else 'unavailable'}",
        f"Bounds (model units): {bounds if bounds else 'unavailable'}",
        f"Volume (model units cubed): {volume if volume is not None else 'not available'}",
        "Watertight/volume use an in-memory analysis copy with duplicate vertices merged; the input file is never modified or repaired."
    ]
    return tool_text("\n".join(lines),"3D mesh inspection")


def dxf_audit(p):
    try:
        import ezdxf
        from collections import Counter
    except ImportError as exc:
        raise RuntimeError("Thiếu ezdxf để đọc bản vẽ DXF.") from exc
    if p.suffix.lower()!=".dxf" or p.stat().st_size>20*1024*1024:
        raise RuntimeError("DXF audit chỉ nhận .dxf tối đa 20 MiB.")
    try:
        document=ezdxf.readfile(str(p))
        auditor=document.audit()
        modelspace=document.modelspace()
        counts=Counter(entity.dxftype() for entity in modelspace)
        if len(modelspace)>1_000_000:
            raise RuntimeError("DXF có hơn một triệu entity trong modelspace.")
        error_count=len(auditor.errors); fix_count=len(auditor.fixes)
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError("Không thể parse hoặc audit DXF; bản vẽ có thể không hợp lệ.") from exc
    lines=[
        f"DXF version: {document.dxfversion}",
        f"Modelspace entities: {len(modelspace):,}",
        f"Layers: {len(document.layers):,}",
        f"Blocks: {len(document.blocks):,}",
        f"INSUNITS code: {document.header.get('$INSUNITS',0)} (0 means unitless)",
        f"Audit errors: {error_count:,}",
        f"Auto-fixes reported by ezdxf auditor: {fix_count:,}",
        "Entity types:"
    ]
    lines.extend(f"- {kind}: {count:,}" for kind,count in counts.most_common(40))
    if len(counts)>40: lines.append(f"- {len(counts)-40:,} less common entity types omitted.")
    return tool_text("\n".join(lines),"DXF CAD audit")


def shapefile_audit(p):
    import struct
    try:
        import shapefile
        from io import BytesIO
    except ImportError as exc:
        raise RuntimeError("Thiếu pyshp để đọc ESRI Shapefile.") from exc
    if p.suffix.lower()!=".zip" or p.stat().st_size>20*1024*1024:
        raise RuntimeError("Shapefile audit yêu cầu ZIP chứa .shp/.shx/.dbf; input tối đa 20 MiB.")
    try:
        with zipfile.ZipFile(p) as archive:
            infos=[item for item in archive.infolist() if not item.is_dir()]
            if len(infos)>100: raise RuntimeError("Shapefile ZIP giới hạn 100 file.")
            total=sum(item.file_size for item in infos)
            if total>100*1024*1024: raise RuntimeError("Shapefile ZIP vượt 100 MiB dữ liệu giải nén.")
            groups={}
            for item in infos:
                parts=_safe_archive_parts(item.filename)
                mode=(item.external_attr>>16)&0xFFFF
                if stat.S_ISLNK(mode) or item.flag_bits&1:
                    raise RuntimeError("Shapefile ZIP chứa symlink hoặc entry mã hóa.")
                path="/".join(parts)
                suffix=Path(path).suffix.lower()
                if suffix in (".shp",".shx",".dbf",".prj"):
                    key=str(Path(path).with_suffix("")).casefold()
                    groups.setdefault(key,{})[suffix]=item
            candidates=[group for group in groups.values() if all(ext in group for ext in (".shp",".shx",".dbf"))]
            if not candidates: raise RuntimeError("Không tìm thấy bộ .shp + .shx + .dbf đầy đủ trong ZIP.")
            if len(candidates)>20: raise RuntimeError("Shapefile ZIP chứa hơn 20 bộ dữ liệu.")
            reports=[]
            for group in candidates:
                shp_data=archive.read(group[".shp"]); shx_data=archive.read(group[".shx"]); dbf_data=archive.read(group[".dbf"])
                reader=shapefile.Reader(shp=BytesIO(shp_data),shx=BytesIO(shx_data),dbf=BytesIO(dbf_data))
                try:
                    fields=[field for field in reader.fields[1:]]
                    bbox=[float(value) for value in reader.bbox] if reader.bbox else []
                    name=Path(group[".shp"].filename).name if hasattr(group[".shp"],"filename") else "dataset"
                    reports.append((name,reader.shapeTypeName,len(reader),len(fields),bbox,[field[0] for field in fields[:40]],".prj" in group))
                finally:
                    reader.close()
    except RuntimeError:
        raise
    except (zipfile.BadZipFile,shapefile.ShapefileException,ValueError,struct.error) as exc:
        raise RuntimeError("Shapefile archive hỏng hoặc thiếu thành phần bắt buộc.") from exc
    lines=[f"Shapefile datasets: {len(reports)}","Attribute values are not included in this report."]
    for name,shape_type,records,field_count,bbox,field_names,has_prj in reports:
        lines.extend([
            f"\n{name}",
            f"- Geometry: {shape_type}; records: {records:,}; fields: {field_count}",
            f"- Bounding box: {bbox if bbox else 'not available'}",
            f"- PRJ present: {has_prj}",
            f"- Field names (first 40): {', '.join(field_names)}"
        ])
    return tool_text("\n".join(lines),"Shapefile inventory")


def gettext_catalog_audit(p):
    try:
        import polib
    except ImportError as exc:
        raise RuntimeError("Thiếu polib để kiểm tra gettext PO/POT.") from exc
    if p.suffix.lower() not in (".po",".pot") or p.stat().st_size>10*1024*1024:
        raise RuntimeError("Gettext audit nhận .po/.pot tối đa 10 MiB.")
    try:
        catalog=polib.pofile(str(p),check_for_duplicates=True)
    except Exception as exc:
        raise RuntimeError("Gettext catalog không parse được hoặc có duplicate msgid.") from exc
    entries=list(catalog)
    if len(entries)>100_000:
        raise RuntimeError("Gettext catalog vượt giới hạn 100.000 entry.")
    untranslated=0; fuzzy=0; obsolete=0; placeholder_mismatch=0; plural_missing=0
    pattern=re.compile(r"%(?:\([^)]+\))?[#0 +\-]?(?:\d+|\*)?(?:\.\d+)?[diouxXeEfFgGcrsa]|\{[A-Za-z_][A-Za-z0-9_.]*\}")
    findings=[]
    for entry in entries:
        if entry.obsolete: obsolete+=1; continue
        if "fuzzy" in entry.flags: fuzzy+=1
        values=list(entry.msgstr_plural.values()) if entry.msgid_plural else [entry.msgstr]
        if not any(values): untranslated+=1
        if entry.msgid_plural and len(values)<2: plural_missing+=1
        source_tokens=sorted(pattern.findall(entry.msgid)+(pattern.findall(entry.msgid_plural or "")))
        target_tokens=sorted(token for value in values for token in pattern.findall(value or ""))
        if source_tokens and source_tokens!=target_tokens:
            placeholder_mismatch+=1
            if len(findings)<100: findings.append(f"- line {entry.linenum}: placeholder set differs")
    lines=[
        f"Active entries: {len(entries)-obsolete:,}",
        f"Untranslated: {untranslated:,}",
        f"Fuzzy: {fuzzy:,}",
        f"Obsolete: {obsolete:,}",
        f"Plural entries missing forms: {plural_missing:,}",
        f"Placeholder mismatches: {placeholder_mismatch:,}",
        "Source/translation strings are not copied into this report."
    ]+findings
    return tool_text("\n".join(lines),"Gettext localization audit")


def notebook_audit(p):
    try:
        import nbformat
    except ImportError as exc:
        raise RuntimeError("Thiếu nbformat để kiểm tra Jupyter Notebook.") from exc
    if p.suffix.lower()!=".ipynb" or p.stat().st_size>20*1024*1024:
        raise RuntimeError("Notebook audit nhận .ipynb tối đa 20 MiB.")
    try:
        notebook=nbformat.read(str(p),as_version=4)
        nbformat.validate(notebook)
    except Exception as exc:
        raise RuntimeError("Notebook JSON/schema không hợp lệ.") from exc
    cells=list(notebook.cells)
    if len(cells)>20_000: raise RuntimeError("Notebook vượt giới hạn 20.000 cell.")
    code=sum(cell.cell_type=="code" for cell in cells)
    markdown=sum(cell.cell_type=="markdown" for cell in cells)
    raw=sum(cell.cell_type=="raw" for cell in cells)
    outputs=sum(len(cell.get("outputs",[])) for cell in cells if cell.cell_type=="code")
    executed=sum(cell.get("execution_count") is not None for cell in cells if cell.cell_type=="code")
    missing_ids=sum(not bool(cell.get("id")) for cell in cells)
    attachments=sum(len(cell.get("attachments",{})) for cell in cells)
    lines=[
        f"Notebook format: nbformat {notebook.nbformat}.{notebook.nbformat_minor}",
        f"Cells: {len(cells):,} (code {code:,}; markdown {markdown:,}; raw {raw:,})",
        f"Executed code cells: {executed:,}/{code:,}",
        f"Stored outputs: {outputs:,}",
        f"Cells missing IDs: {missing_ids:,}",
        f"Markdown attachments: {attachments:,}",
        f"Kernel language: {notebook.metadata.get('kernelspec',{}).get('language','unknown')}",
        "Cell source and execution output contents are not included."
    ]
    return tool_text("\n".join(lines),"Jupyter Notebook audit")


def notebook_strip_outputs(p):
    try:
        import nbformat
    except ImportError as exc:
        raise RuntimeError("Thiếu nbformat để làm sạch Jupyter Notebook.") from exc
    if p.suffix.lower()!=".ipynb" or p.stat().st_size>20*1024*1024:
        raise RuntimeError("Notebook cleaner nhận .ipynb tối đa 20 MiB.")
    try:
        notebook=nbformat.read(str(p),as_version=4)
        nbformat.validate(notebook)
    except Exception as exc:
        raise RuntimeError("Notebook JSON/schema không hợp lệ.") from exc
    if len(notebook.cells)>20_000: raise RuntimeError("Notebook vượt giới hạn 20.000 cell.")
    removed_outputs=0; removed_execution=0
    for cell in notebook.cells:
        if cell.cell_type!="code": continue
        removed_outputs+=len(cell.get("outputs",[]))
        removed_execution+=cell.get("execution_count") is not None
        cell["outputs"]=[]
        cell["execution_count"]=None
    out=p.with_name(p.stem+"-clean.ipynb")
    content=nbformat.writes(notebook,version=4)
    if len(content.encode("utf-8"))>45*1024*1024:
        raise RuntimeError("Clean Notebook output vượt 45 MiB.")
    out.write_text(content,encoding="utf-8")
    return {"summary":f"Đã xóa {removed_outputs:,} execution output và reset {removed_execution:,} execution count; giữ nguyên cell source và cấu trúc notebook.","output_path":str(out)}



def subtitle_quality_audit(p):
    if p.suffix.lower() not in (".srt",".vtt") or p.stat().st_size>10*1024*1024:
        raise RuntimeError("Subtitle quality audit nhận SRT/VTT tối đa 10 MiB.")
    raw=p.read_text(encoding="utf-8-sig",errors="replace").replace("\r\n","\n").replace("\r","\n")
    stamp=re.compile(r"^\s*(?:(\d{1,3}):)?(\d{2}):(\d{2})[,.](\d{1,3})\s*-->\s*(?:(\d{1,3}):)?(\d{2}):(\d{2})[,.](\d{1,3})(?:\s+.*)?$")
    def parse(groups,offset):
        hours=int(groups[offset] or 0); minutes=int(groups[offset+1]); seconds=int(groups[offset+2])
        fraction=int(groups[offset+3].ljust(3,"0"))
        if minutes>59 or seconds>59: raise ValueError()
        return ((hours*60+minutes)*60+seconds)*1000+fraction
    cues=[]
    for block in re.split(r"\n[ \t]*\n",raw.strip()):
        lines=block.splitlines()
        index=next((i for i,line in enumerate(lines) if "-->" in line),None)
        if index is None: continue
        match=stamp.match(lines[index])
        if not match: continue
        try:
            groups=match.groups(); start=parse(groups,0); end=parse(groups,4)
        except (ValueError,TypeError): continue
        text_content="\n".join(lines[index+1:])
        text_content=re.sub(r"<[^>]{0,200}>","",text_content)
        text_content=unescape(text_content)
        visible=re.sub(r"\s+"," ",text_content).strip()
        if end<=start or not visible: continue
        longest=max((len(line.strip()) for line in text_content.splitlines()),default=0)
        chars=len(re.sub(r"\s","",visible))
        cps=chars/max((end-start)/1000,0.001)
        cues.append({"line":index+1,"start":start,"end":end,"duration":end-start,"chars":chars,"cps":cps,"longest":longest,"overlap":False})
        if len(cues)>20000: raise RuntimeError("Subtitle audit giới hạn 20.000 cue.")
    if not cues: raise RuntimeError("Không tìm thấy cue SRT/VTT hợp lệ.")
    chronological=sorted(cues,key=lambda cue:(cue["start"],cue["end"]))
    max_end=-1
    for cue in chronological:
        cue["overlap"]=cue["start"]<max_end
        max_end=max(max_end,cue["end"])
    long_cues=sum(cue["longest"]>42 for cue in cues)
    fast_cues=sum(cue["cps"]>20 for cue in cues)
    overlap_cues=sum(cue["overlap"] for cue in cues)
    short_cues=sum(cue["duration"]<500 for cue in cues)
    out=p.with_name(p.stem+"-subtitle-quality.csv")
    with out.open("w",encoding="utf-8-sig",newline="") as handle:
        writer=csv.writer(handle,lineterminator="\n")
        writer.writerow(["timestamp_line","start_ms","end_ms","duration_ms","visible_chars","chars_per_second","longest_line_chars","overlaps_previous"])
        for cue in sorted(cues,key=lambda item:item["line"]):
            writer.writerow([cue["line"],cue["start"],cue["end"],cue["duration"],cue["chars"],round(cue["cps"],2),cue["longest"],int(cue["overlap"])])
    return {"summary":f"Đã phân tích {len(cues):,} cue; >20 CPS: {fast_cues:,}; dòng dài hơn 42 ký tự: {long_cues:,}; cue overlap: {overlap_cues:,}; cue ngắn hơn 0,5 giây: {short_cues:,}. CSV chỉ chứa timing và số liệu, không chứa lời thoại.","output_path":str(out)}


def kml_to_geojson(p):
    import math
    import xml.etree.ElementTree as ET
    if p.suffix.lower() not in (".kml",".xml") or p.stat().st_size>20*1024*1024:
        raise RuntimeError("KML converter nhận .kml/.xml tối đa 20 MiB.")
    raw=p.read_bytes()
    if re.search(rb"<!\s*(DOCTYPE|ENTITY)\b",raw,re.I):
        raise RuntimeError("KML DTD/ENTITY bị chặn.")
    try:
        root=ET.fromstring(raw)
    except ET.ParseError as exc:
        raise RuntimeError("KML XML không hợp lệ.") from exc
    def local(tag): return tag.rsplit("}",1)[-1]
    coordinate_count=0
    def coordinates(text_value):
        nonlocal coordinate_count
        result=[]
        for token in (text_value or "").split():
            parts=token.split(",")
            if len(parts)<2: continue
            try: values=[float(value) for value in parts[:3] if value!=""]
            except ValueError: continue
            if len(values)<2 or not all(math.isfinite(value) for value in values): continue
            if not -180<=values[0]<=180 or not -90<=values[1]<=90: continue
            result.append(values)
            coordinate_count+=1
            if coordinate_count>500000: raise RuntimeError("KML vượt giới hạn 500.000 tọa độ.")
        return result
    def find_child(node,name):
        return next((child for child in node.iter() if child is not node and local(child.tag)==name),None)
    def geometry(node):
        kind=local(node.tag)
        if kind=="Point":
            item=find_child(node,"coordinates")
            points=coordinates(item.text if item is not None else "")
            return {"type":"Point","coordinates":points[0]} if points else None
        if kind=="LineString":
            item=find_child(node,"coordinates")
            points=coordinates(item.text if item is not None else "")
            return {"type":"LineString","coordinates":points} if len(points)>=2 else None
        if kind=="LinearRing":
            item=find_child(node,"coordinates")
            points=coordinates(item.text if item is not None else "")
            return {"type":"LinearRing","coordinates":points} if len(points)>=4 else None
        if kind=="Polygon":
            rings=[]
            for boundary in node.iter():
                if local(boundary.tag)!="LinearRing": continue
                ring=geometry(boundary)
                if ring: rings.append(ring["coordinates"])
            if not rings: return None
            if rings[0][0]!=rings[0][-1]: rings[0].append(rings[0][0])
            return {"type":"Polygon","coordinates":rings}
        if kind=="MultiGeometry":
            members=[]
            for child in list(node):
                result=geometry(child)
                if result: members.append(result)
            return {"type":"GeometryCollection","geometries":members} if members else None
        return None
    features=[]
    for placemark in (node for node in root.iter() if local(node.tag)=="Placemark"):
        geometry_node=next((child for child in placemark.iter() if local(child.tag) in ("Point","LineString","Polygon","MultiGeometry")),None)
        if geometry_node is None: continue
        result=geometry(geometry_node)
        if not result: continue
        props={}
        for child in list(placemark):
            name=local(child.tag)
            if name in ("name","description") and child.text:
                props[name]=child.text[:2000]
        features.append({"type":"Feature","geometry":result,"properties":props})
        if len(features)>20000: raise RuntimeError("KML vượt giới hạn 20.000 Placemark feature.")
    if not features: raise RuntimeError("Không tìm thấy Point/LineString/Polygon/MultiGeometry hợp lệ trong KML.")
    output={"type":"FeatureCollection","features":features}
    serialized=json.dumps(output,ensure_ascii=False,separators=(",",":"))
    if len(serialized.encode("utf-8"))>MAX_PIPELINE_OUTPUT:
        raise RuntimeError("GeoJSON output vượt 45 MiB.")
    out=p.with_name(p.stem+".geojson")
    out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return {"summary":f"Đã chuyển {len(features):,} Placemark và {coordinate_count:,} tọa độ KML sang GeoJSON; external NetworkLink không được tải.","output_path":str(out)}


def coordinate_transform(p):
    import math
    try:
        import pyproj
    except ImportError as exc:
        raise RuntimeError("Thiếu pyproj để chuyển hệ tọa độ.") from exc
    if p.stat().st_size>10*1024*1024:
        raise RuntimeError("Coordinate transform giới hạn input 10 MiB.")
    try: data=json.loads(p.read_text(encoding="utf-8-sig"))
    except (UnicodeError,json.JSONDecodeError) as exc: raise RuntimeError("Input phải là JSON coordinate envelope hợp lệ.") from exc
    if not isinstance(data,dict) or not isinstance(data.get("coordinates"),list):
        raise RuntimeError('JSON cần source_crs, target_crs và coordinates: [[x,y], ...].')
    source=str(data.get("source_crs","")).upper()
    target=str(data.get("target_crs","")).upper()
    if not re.fullmatch(r"EPSG:[0-9]{3,6}",source) or not re.fullmatch(r"EPSG:[0-9]{3,6}",target):
        raise RuntimeError("Chỉ hỗ trợ CRS dạng EPSG:xxxx; CRS tùy chỉnh và URL bị chặn.")
    coords=data["coordinates"]
    if not 1<=len(coords)<=10000: raise RuntimeError("Cần từ 1 đến 10.000 coordinate.")
    try:
        pyproj.network.set_network_enabled(active=False)
        transformer=pyproj.Transformer.from_crs(source,target,always_xy=True)
        output=[]
        for point in coords:
            if not isinstance(point,list) or len(point) not in (2,3): raise ValueError("coordinate")
            values=[float(item) for item in point]
            if not all(math.isfinite(value) for value in values): raise ValueError("non-finite")
            if len(values)==3:
                x,y,z=transformer.transform(values[0],values[1],values[2],errcheck=True)
                converted=[x,y,z]
            else:
                x,y=transformer.transform(values[0],values[1],errcheck=True)
                converted=[x,y]
            if not all(math.isfinite(value) for value in converted): raise ValueError("non-finite output")
            output.append(converted)
    except Exception as exc:
        raise RuntimeError("Không thể chuyển tọa độ; CRS không tương thích hoặc coordinate nằm ngoài miền hợp lệ.") from exc
    result={"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"Point","coordinates":point},"properties":{"index":index+1}} for index,point in enumerate(output)],"source_crs":source,"target_crs":target}
    out=p.with_name(p.stem+"-transformed.geojson")
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return {"summary":f"Đã chuyển {len(output):,} coordinate từ {source} sang {target} bằng pyproj; truy cập mạng PROJ bị tắt.","output_path":str(out)}


def html_structured_data_audit(p):
    if p.suffix.lower() not in (".html",".htm") or p.stat().st_size>10*1024*1024:
        raise RuntimeError("JSON-LD audit nhận .html/.htm tối đa 10 MiB.")
    class Parser(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.in_jsonld=False
            self.buffer=[]
            self.blocks=[]
        def handle_starttag(self,tag,attrs):
            if tag.lower()=="script":
                attrs_map={key.lower():value for key,value in attrs if key}
                if (attrs_map.get("type") or "").lower()=="application/ld+json":
                    self.in_jsonld=True
                    self.buffer=[]
        def handle_endtag(self,tag):
            if tag.lower()=="script" and self.in_jsonld:
                self.blocks.append("".join(self.buffer))
                self.in_jsonld=False
                self.buffer=[]
        def handle_data(self,data):
            if self.in_jsonld: self.buffer.append(data)
    parser=Parser()
    try:
        parser.feed(p.read_text(encoding="utf-8-sig",errors="replace"))
        parser.close()
    except Exception as exc:
        raise RuntimeError("Không thể parse HTML để trích JSON-LD blocks.") from exc
    malformed=0; missing_context=0; missing_type=0; array_roots=0; graph_roots=0; schema_org=0
    seen_ids=set(); duplicate_ids=0; objects=0
    for raw in parser.blocks:
        try:
            data=json.loads(raw)
        except (ValueError,TypeError):
            malformed+=1
            continue
        objects_to_check=data if isinstance(data,list) else [data]
        if isinstance(data,list): array_roots+=1
        for obj in objects_to_check:
            if not isinstance(obj,dict):
                malformed+=1
                continue
            objects+=1
            context=obj.get("@context")
            if not context: missing_context+=1
            contexts=context if isinstance(context,list) else [context]
            if any(isinstance(value,str) and "schema.org" in value.lower() for value in contexts):
                schema_org+=1
            if obj.get("@graph") is not None: graph_roots+=1
            if not obj.get("@type"): missing_type+=1
            identifier=obj.get("@id")
            if isinstance(identifier,str) and identifier:
                if identifier in seen_ids: duplicate_ids+=1
                seen_ids.add(identifier)
    lines=[
        f"JSON-LD script blocks: {len(parser.blocks):,}",
        f"Parsed JSON objects: {objects:,}",
        f"Malformed JSON/non-object entries: {malformed:,}",
        f"Objects missing @context: {missing_context:,}",
        f"Objects missing @type: {missing_type:,}",
        f"Objects referencing schema.org context: {schema_org:,}",
        f"Blocks with root arrays: {array_roots:,}",
        f"Objects containing @graph: {graph_roots:,}",
        f"Duplicate @id values: {duplicate_ids:,}",
        "JSON-LD contents, names, URLs and identifiers are not copied into this report."
    ]
    return tool_text("\n".join(lines),"JSON-LD structured data audit")


def html_local_link_audit(p):
    from urllib.parse import unquote,urlsplit
    if p.suffix.lower()!=".zip" or p.stat().st_size>20*1024*1024:
        raise RuntimeError("HTML local link audit yêu cầu ZIP site bundle tối đa 20 MiB.")
    class PageParser(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True); self.fragments=set(); self.links=[]
        def handle_starttag(self,tag,attrs):
            values={key.lower():value for key,value in attrs if key}
            if values.get("id"): self.fragments.add(values["id"])
            if tag.lower()=="a" and values.get("name"): self.fragments.add(values["name"])
            for key in ("href","src","poster"):
                value=values.get(key)
                if value: self.links.append((self.getpos()[0],key,value))
    pages={}; members={}; total=0
    try:
        with zipfile.ZipFile(p) as archive:
            infos=[item for item in archive.infolist() if not item.is_dir()]
            if len(infos)>500: raise RuntimeError("HTML site ZIP giới hạn 500 file.")
            for item in infos:
                parts=_safe_archive_parts(item.filename)
                mode=(item.external_attr>>16)&0xFFFF
                if stat.S_ISLNK(mode) or item.flag_bits&1: raise RuntimeError("HTML ZIP chứa symlink hoặc entry mã hóa.")
                total+=item.file_size
                if total>100*1024*1024: raise RuntimeError("HTML ZIP vượt 100 MiB dữ liệu giải nén.")
                path="/".join(parts); members[path]=item
            html_paths=[path for path in members if Path(path).suffix.lower() in (".html",".htm")]
            if len(html_paths)>200: raise RuntimeError("HTML site ZIP giới hạn 200 trang HTML.")
            for path in html_paths:
                parser=PageParser()
                try: parser.feed(archive.read(members[path]).decode("utf-8-sig","replace")); parser.close()
                except Exception: pass
                pages[path]=parser
            findings=[]; skipped_external=0
            for source_path,parser in pages.items():
                for line,key,value in parser.links:
                    if len(findings)>=5000: break
                    raw_value=unescape(value.strip())
                    try: parts=urlsplit(raw_value)
                    except ValueError:
                        findings.append((source_path,line,"malformed-url")); continue
                    if parts.scheme or parts.netloc or raw_value.startswith("//"):
                        skipped_external+=1; continue
                    decoded=unquote(parts.path)
                    if decoded.startswith("/"):
                        target=posixpath.normpath(decoded.lstrip("/"))
                        if target==".": target="index.html"
                    elif decoded: target=posixpath.normpath(posixpath.join(posixpath.dirname(source_path),decoded))
                    else: target=source_path
                    if target=="." : target=source_path
                    if target==".." or target.startswith("../") or target.startswith("/"):
                        findings.append((source_path,line,"path-escapes-site")); continue
                    if target.endswith("/"): target=target+"index.html"
                    if target not in members:
                        if target in ("","./"): target=source_path
                        if target not in members:
                            findings.append((source_path,line,"missing-local-resource")); continue
                    fragment=unquote(parts.fragment)
                    if fragment and target in pages and fragment not in pages[target].fragments:
                        findings.append((source_path,line,"missing-fragment"))
        out=p.with_name(p.stem+"-local-link-audit.csv")
        with out.open("w",encoding="utf-8-sig",newline="") as handle:
            writer=csv.writer(handle,lineterminator="\n")
            writer.writerow(["source_file","line","issue"])
            for row in findings: writer.writerow([_spreadsheet_safe(row[0]),row[1],row[2]])
    except RuntimeError:
        raise
    except (zipfile.BadZipFile,OSError) as exc: raise RuntimeError("HTML site ZIP hỏng hoặc không đọc được.") from exc
    return {"summary":f"Đã kiểm tra {len(pages):,} HTML page; {sum(len(item.links) for item in pages.values()):,} local/external references; external refs skipped: {skipped_external:,}; internal issues: {len(findings):,}. CSV chỉ chứa source path, line và loại lỗi; không fetch URL.","output_path":str(out)}


def css_quality_audit(p):
    try:
        import tinycss2
    except ImportError as exc:
        raise RuntimeError("Thiếu tinycss2 để parse CSS.") from exc
    if p.suffix.lower()!=".css" or p.stat().st_size>10*1024*1024:
        raise RuntimeError("CSS audit nhận .css tối đa 10 MiB.")
    raw=p.read_text(encoding="utf-8-sig",errors="replace")
    try:
        rules=tinycss2.parse_stylesheet(raw,skip_comments=True,skip_whitespace=True)
        errors=sum(rule.type=="error" for rule in rules)
        selectors={}; duplicate_properties=0; important=0; declarations=0; imports=0
        for rule in rules:
            if rule.type=="at-rule":
                if rule.lower_at_keyword=="import": imports+=1
                continue
            if rule.type!="qualified-rule": continue
            selector=tinycss2.serialize(rule.prelude).strip()
            selectors[selector]=selectors.get(selector,0)+1
            parsed=tinycss2.parse_declaration_list(rule.content,skip_comments=True,skip_whitespace=True)
            seen=set()
            for item in parsed:
                if item.type=="error": errors+=1
                elif item.type=="declaration":
                    declarations+=1
                    if item.name.lower() in seen: duplicate_properties+=1
                    seen.add(item.name.lower())
                    if item.important: important+=1
        duplicate_selectors=sum(count-1 for count in selectors.values() if count>1)
        remote_refs=len(re.findall(r"url\(\s*['\"]?(?:https?:)?//",raw,re.I))
        lines=[
            f"Qualified rules: {sum(selectors.values()):,}",
            f"Unique selectors: {len(selectors):,}",
            f"Duplicate selector blocks: {duplicate_selectors:,}",
            f"Declarations: {declarations:,}",
            f"Repeated properties within a rule: {duplicate_properties:,}",
            f"!important declarations: {important:,}",
            f"@import rules: {imports:,}",
            f"External URL references: {remote_refs:,}",
            f"Parser errors: {errors:,}",
            "Selector and declaration values are not copied into this report."
        ]
    except Exception as exc:
        raise RuntimeError("CSS parser không thể hoàn thành audit.") from exc
    return tool_text("\n".join(lines),"CSS quality audit")


def heic_convert(p):
    try:
        import pillow_heif
        from PIL import Image,ImageOps
    except ImportError as exc:
        raise RuntimeError("Thiếu pillow-heif/Pillow để chuyển HEIC/HEIF.") from exc
    if p.suffix.lower() not in (".heic",".heif") or p.stat().st_size>20*1024*1024:
        raise RuntimeError("HEIC converter nhận .heic/.heif tối đa 20 MiB.")
    try:
        pillow_heif.register_heif_opener()
        with Image.open(p) as raw:
            _guard_image_dimensions(raw)
            frames=getattr(raw,"n_frames",1)
            raw.seek(0)
            oriented=ImageOps.exif_transpose(raw)
            has_alpha=("A" in oriented.getbands()) or ("transparency" in oriented.info)
            if has_alpha:
                pixels=oriented.convert("RGBA")
                clean=Image.new("RGBA",pixels.size); clean.paste(pixels)
                out=p.with_name(p.stem+"-converted.png")
                clean.save(out,"PNG",optimize=True)
            else:
                pixels=oriented.convert("RGB")
                clean=Image.new("RGB",pixels.size); clean.paste(pixels)
                out=p.with_name(p.stem+"-converted.jpg")
                clean.save(out,"JPEG",quality=90,optimize=True,progressive=True)
    except Exception as exc:
        raise RuntimeError("Không thể giải mã HEIC/HEIF; tệp có thể hỏng hoặc codec không hỗ trợ.") from exc
    if out.stat().st_size>MAX_PIPELINE_OUTPUT:
        out.unlink(missing_ok=True)
        raise RuntimeError("Converted image vượt 45 MiB.")
    return {"summary":f"Đã chuyển HEIC/HEIF thành {out.suffix.upper()[1:]}; {pixels.width}×{pixels.height}; chọn frame đầu tiên trong {frames} frame; metadata camera/GPS không được giữ.","output_path":str(out)}


TOOLS={
 "image-ocr":image_ocr,"image-info":image_info,"image-clean-exif":image_clean,"image-compress":image_compress,
 "image-to-pdf":image_pdf,"qr-read":qr_read,"pdf-text":pdf_text,"pdf-info":pdf_info,
 "audio-transcribe":audio_transcribe,"audio-info":audio_info,"video-info":video_info,"video-thumbnail":video_thumbnail,
 "csv-profile":csv_profile,"json-format":json_format,"office-text":office_text,"archive-inspect":archive_inspect,"file-hash":file_hash,"text-clean":text_clean,"subtitle-text":subtitle_text,"html-text":html_text,
 "audio-normalize":audio_normalize,"video-audio":video_audio,"video-gif":video_gif,
 "image-resize":image_resize,"image-webp":image_webp,"image-palette":image_palette,
 "pdf-compress":pdf_compress,"pdf-to-images":pdf_to_images,"epub-text":epub_text,"sqlite-inspect":sqlite_inspect,
 "yaml-format":yaml_format,"xml-format":xml_format,"code-check":code_check,
 "video-contact-sheet":video_contact_sheet,"video-compress":video_compress,"audio-subtitles":audio_subtitles,
 "archive-safe-extract":archive_safe_extract,"xlsx-profile":xlsx_profile,"xlsx-formula-report":xlsx_formula_report,"xlsx-to-markdown":xlsx_to_markdown,
 "image-png":image_png,"image-favicon":image_favicon,"csv-clean":csv_clean,"json-to-csv":json_to_csv,"csv-to-xlsx":csv_to_xlsx,
 "xlsx-to-csv":xlsx_to_csv,"pdf-split":pdf_split,"audio-convert":audio_convert,
 "csv-to-json":csv_to_json,"jsonl-format":jsonl_format,"yaml-to-json":yaml_to_json,"xml-to-json":xml_to_json,
 "sqlite-export":sqlite_export,"xlsx-to-json":xlsx_to_json,"pdf-extract-images":pdf_extract_images,
 "archive-manifest":archive_manifest,"text-stats":text_stats,"image-grayscale":image_grayscale,
 "pdf-merge":pdf_merge, "pdf-metadata-clean":pdf_metadata_clean, "pdf-outline":pdf_outline, "image-contact-sheet":image_contact_sheet, "image-duplicates":image_duplicates, "csv-split":csv_split, "csv-join":csv_join, "json-schema":json_schema, "json-to-yaml":json_to_yaml, "sqlite-integrity":sqlite_integrity, "audio-silence-report":audio_silence_report, "video-silence-report":video_silence_report, "video-frames":video_frames, "subtitle-convert":subtitle_convert,"subtitle-audit":subtitle_audit, "text-deduplicate":text_deduplicate, "text-diff":text_diff, "code-size-report":code_size_report,
 "pdf-rotate-cw":pdf_rotate_cw,"pdf-remove-blank":pdf_remove_blank,"pdf-page-audit":pdf_page_audit,
 "image-trim-border":image_trim_border,"image-pixelate":image_pixelate,"image-diff":image_diff,
 "audio-stereo-split":audio_stereo_split,"audio-metadata-clean":audio_metadata_clean,
 "video-scene-frames":video_scene_frames,"video-metadata-clean":video_metadata_clean,
 "json-flatten-csv":json_flatten_csv,"csv-to-sqlite":csv_to_sqlite,"log-insights":log_insights,"json-diff":json_diff,"text-join":text_join,
 "markdown-outline":markdown_outline,"markdown-links":markdown_links,"markdown-toc":markdown_toc,"text-redact":text_redact,"text-extract":text_extract,
 "code-imports":code_imports,"code-todos":code_todos,"code-secret-scan":code_secret_scan,"log-timeline":log_timeline,
 "repo-inventory":repo_inventory,"repo-dependencies":repo_dependencies,"repo-license-report":repo_license_report,"repo-secret-scan":repo_secret_scan,
 "repo-todo-scan":repo_todo_scan,"repo-code-stats":repo_code_stats,"repo-config-audit":repo_config_audit,"repo-duplicates":repo_duplicates,"repo-intelligence":repo_intelligence,
 "repo-security-audit":repo_security_audit,"repo-supply-chain":repo_supply_chain,

 "text-translate":text_translate,"language-detect":language_detect,
 "text-uppercase":text_uppercase,"text-lowercase":text_lowercase,"text-title-case":text_title_case,
 "text-sort-lines":text_sort_lines,"text-reverse-lines":text_reverse_lines,"text-number-lines":text_number_lines,
 "text-remove-blank-lines":text_remove_blank_lines,"text-wrap":text_wrap,"text-trim-lines":text_trim_lines,
 "text-extract-emails":text_extract_emails,"text-extract-urls":text_extract_urls,"text-extract-hashtags":text_extract_hashtags,
 "text-to-base64":text_to_base64,"base64-to-text":base64_to_text,"url-encode":url_encode_text,"url-decode":url_decode_text,
 "json-minify":json_minify,"json-sort-keys":json_sort_keys,
 "text-slugify":text_slugify,"text-word-frequency":text_word_frequency,
 "text-extract-numbers":text_extract_numbers,"text-extract-dates":text_extract_dates,"text-reverse-characters":text_reverse_characters,
 "text-snake-case":text_snake_case,"text-kebab-case":text_kebab_case,"text-camel-case":text_camel_case,"text-swap-case":text_swap_case,
 "text-extract-ipv4":text_extract_ipv4,"text-mask-emails":text_mask_emails,"text-mask-phones":text_mask_phones,
 "json-to-jsonl":json_to_jsonl,"jsonl-to-json":jsonl_to_json,"csv-to-tsv":csv_to_tsv,"tsv-to-csv":tsv_to_csv,
 "csv-to-markdown":csv_to_markdown,"html-minify":html_minify,"xml-minify":xml_minify,"text-remove-emoji":text_remove_emoji,
 "text-collapse-whitespace":text_collapse_whitespace,"text-remove-punctuation":text_remove_punctuation,"text-to-ascii":text_to_ascii,
 "text-html-escape":text_html_escape,"text-html-unescape":text_html_unescape,"text-extract-mentions":text_extract_mentions,
 "text-extract-hex-colors":text_extract_hex_colors,"text-extract-phones":text_extract_phones,"text-dedupe-lines":text_dedupe_lines,
 "text-count-report":text_count_report,"text-quote-lines":text_quote_lines,"text-unquote-lines":text_unquote_lines,
 "csv-transpose":csv_transpose,"csv-sort-rows":csv_sort_rows,"csv-dedupe-rows":csv_dedupe_rows,
 "csv-to-xml":csv_to_xml,"csv-to-html":csv_to_html,"json-sort-array":json_sort_array,"json-remove-nulls":json_remove_nulls,
 "json-to-html-table":json_to_html_table,
 "text-pascal-case":text_pascal_case,"text-constant-case":text_constant_case,"text-dot-case":text_dot_case,
 "text-initials":text_initials,"text-normalize-unicode":text_normalize_unicode,
 "text-remove-control-chars":text_remove_control_chars,"text-remove-duplicate-words":text_remove_duplicate_words,
 "text-extract-markdown-links":text_extract_markdown_links,"text-extract-markdown-headings":text_extract_markdown_headings,
 "text-extract-quotes":text_extract_quotes,"text-paragraph-report":text_paragraph_report,
 "json-flatten":json_flatten,"json-unflatten":json_unflatten,"json-keys-report":json_keys_report,
 "csv-remove-empty-rows":csv_remove_empty_rows,"csv-add-row-numbers":csv_add_row_numbers,
 "csv-column-stats":csv_column_stats,"csv-normalize-headers":csv_normalize_headers,
 "csv-to-jsonl":csv_to_jsonl,"jsonl-to-csv":jsonl_to_csv,
 "text-indent-lines":text_indent_lines,"text-unindent-lines":text_unindent_lines,"text-dedupe-paragraphs":text_dedupe_paragraphs,
 "text-tokenize-words":text_tokenize_words,"text-sentence-report":text_sentence_report,"text-line-length-report":text_line_length_report,
 "text-normalize-newlines":text_normalize_newlines,"text-remove-zero-width":text_remove_zero_width,"text-extract-file-paths":text_extract_file_paths,
 "text-sort-words":text_sort_words,"html-extract-links":html_extract_links,"html-extract-images":html_extract_images,
 "html-extract-title":html_extract_title,"html-sanitize":html_sanitize,
 "html-seo-audit":html_seo_audit,"html-accessibility-audit":html_accessibility_audit,
 "html-link-audit":html_link_audit,"html-form-audit":html_form_audit,"html-image-audit":html_image_audit,"xml-tree-report":xml_tree_report,"json-to-xml":json_to_xml,
 "json-type-report":json_type_report,"json-escape-string":json_escape_string,"json-unescape-string":json_unescape_string,
 "csv-unique-values":csv_unique_values,
 "text-sentence-case":text_sentence_case,"text-normalize-quotes":text_normalize_quotes,"text-normalize-dashes":text_normalize_dashes,
 "text-reverse-word-order":text_reverse_word_order,"text-extract-words":text_extract_words,"text-extract-sentences":text_extract_sentences,
 "text-dedupe-sentences":text_dedupe_sentences,"text-remove-markdown-formatting":text_remove_markdown_formatting,
 "text-markdown-toc":text_markdown_toc,"text-markdown-code-blocks":text_markdown_code_blocks,
 "text-markdown-table-extract":text_markdown_table_extract,"text-extract-numbered-lists":text_extract_numbered_lists,
 "text-join-hyphenated-lines":text_join_hyphenated_lines,"text-strip-bom":text_strip_bom,"text-normalize-paragraph-spacing":text_normalize_paragraph_spacing,
 "csv-schema-infer":csv_schema_infer,"csv-duplicates-report":csv_duplicates_report,"csv-sample-rows":csv_sample_rows,
 "json-array-stats":json_array_stats,"json-canonicalize":json_canonicalize,
 "text-extract-todo-comments":text_extract_todo_comments,"text-extract-markdown-images":text_extract_markdown_images,
 "text-strip-markdown-frontmatter":text_strip_markdown_frontmatter,"text-markdown-to-plain":text_markdown_to_plain,
 "text-sort-unique-words":text_sort_unique_words,"text-word-to-lines":text_word_to_lines,"text-join-lines":text_join_lines,
 "text-extract-domains":text_extract_domains,"text-extract-uuids":text_extract_uuids,"text-extract-semver":text_extract_semver,
 "text-extract-ipv6":text_extract_ipv6,"text-redact-secrets":text_redact_secrets,"text-extract-comment-lines":text_extract_comment_lines,
 "text-tabs-to-spaces":text_tabs_to_spaces,"text-escape-regex":text_escape_regex,"text-unescape-regex":text_unescape_regex,
 "json-merge-objects":json_merge_objects,"json-array-dedupe":json_array_dedupe,"json-array-to-lines":json_array_to_lines,
 "csv-trim-cells":csv_trim_cells,"csv-remove-empty-columns":csv_remove_empty_columns,"csv-empty-cell-report":csv_empty_cell_report,
  "text-extract-mac-addresses":text_extract_mac_addresses,"text-extract-port-numbers":text_extract_port_numbers,
  "text-normalize-path-separators":text_normalize_path_separators,"text-extract-file-extensions":text_extract_file_extensions,
  "text-escape-shell-argument":text_escape_shell_argument,"text-sort-unique-lines":text_sort_unique_lines,"text-normalize-unicode-nfkc":text_normalize_unicode_nfkc,
  "csv-to-sql-inserts":csv_to_sql_inserts,"csv-to-yaml":csv_to_yaml,"csv-empty-row-report":csv_empty_row_report,"csv-row-width-report":csv_row_width_report,
  "json-remove-empty-values":json_remove_empty_values,"json-to-typescript":json_to_typescript,"json-nesting-report":json_nesting_report,
 "env-audit":env_audit,"env-redact":env_redact,"env-to-example":env_to_example,
 "ini-to-json":ini_to_json,"ini-validate":ini_validate,"toml-to-json":toml_to_json,"toml-validate":toml_validate,"properties-to-json":properties_to_json,
 "dockerfile-audit":dockerfile_audit,"docker-compose-audit":docker_compose_audit,"requirements-audit":requirements_audit,
 "package-json-audit":package_json_audit,"gitignore-audit":gitignore_audit,"env-reference-report":env_reference_report,

 "github-actions-audit":github_actions_audit,"kubernetes-manifest-audit":kubernetes_manifest_audit,
 "terraform-audit":terraform_audit,"nginx-config-audit":nginx_config_audit,"apache-config-audit":apache_config_audit,
 "caddy-config-audit":caddy_config_audit,"systemd-unit-audit":systemd_unit_audit,"shell-script-audit":shell_script_audit,

 "repo-test-map":repo_test_map,
 "repo-test-quality":repo_test_quality,
 "repo-complexity-report":repo_complexity_report,
 "repo-api-surface":repo_api_surface,
 "repo-docs-audit":repo_docs_audit,
 "repo-migration-audit":repo_migration_audit,
 "repo-runtime-risk":repo_runtime_risk,
 "repo-i18n-audit":repo_i18n_audit,

 "repo-env-contract":repo_env_contract,
 "repo-architecture-cycles":repo_architecture_cycles,
 "repo-change-impact":repo_change_impact,
 "repo-api-spec-audit":repo_api_spec_audit,
 "repo-container-audit":repo_container_audit,
 "repo-ci-reliability":repo_ci_reliability,
 "docx-audit":docx_audit,
 "pptx-audit":pptx_audit,
 "csv-privacy-audit":csv_privacy_audit,
 "archive-security-audit":archive_security_audit,
 "xlsx-privacy-audit":xlsx_privacy_audit,
 "pdf-privacy-audit":pdf_privacy_audit,
 "office-active-content-audit":office_active_content_audit,
 "pdf-active-content-audit":pdf_active_content_audit,
 "email-security-audit":email_security_audit,
 "jwt-security-audit":jwt_security_audit,
 "har-privacy-audit":har_privacy_audit,
 "ics-calendar-audit":ics_calendar_audit,
 "vcard-privacy-audit":vcard_privacy_audit,
 "gpx-track-report":gpx_track_report,
 "geojson-audit":geojson_audit,
 "qr-code-generate":qr_code_generate,
 "font-inspect":font_inspect,
 "subtitle-fix":subtitle_fix,
 "openapi-contract-audit":openapi_contract_audit,
 "color-convert":color_convert,
 "pcap-network-audit":pcap_network_audit,
 "audio-tag-audit":audio_tag_audit,
 "image-similarity-audit":image_similarity_audit,
 "json-schema-validate":json_schema_validate,
 "epub-structure-audit":epub_structure_audit,
 "markdown-quality-audit":markdown_quality_audit,
 "dns-zone-audit":dns_zone_audit,
 "x509-certificate-audit":x509_certificate_audit,
 "rss-atom-audit":rss_atom_audit,
 "sitemap-xml-audit":sitemap_xml_audit,
 "robots-txt-audit":robots_txt_audit,
 "jsonl-profile":jsonl_profile,
 "image-privacy-audit":image_privacy_audit,
 "svg-safety-audit":svg_safety_audit,
 "wcag-contrast-audit":wcag_contrast_audit,
 "ssh-public-key-audit":ssh_public_key_audit,
 "archive-checksum-manifest":archive_checksum_manifest,
 "pdf-table-extract":pdf_table_extract,
 "json-jmespath-query":json_jmespath_query,
 "ip-network-report":ip_network_report,
 "barcode-generate":barcode_generate,
 "docx-to-markdown":docx_to_markdown,
 "pptx-notes-extract":pptx_notes_extract,
 "fuzzy-match-report":fuzzy_match_report,
 "csv-to-parquet":csv_to_parquet,
 "parquet-to-csv":parquet_to_csv,
 "sqlglot-format":sqlglot_format,
 "sqlfluff-lint":sqlfluff_lint,
 "python-security-audit":python_security_audit,
 "unit-convert":unit_convert,
 "mesh-inspect":mesh_inspect,
 "dxf-audit":dxf_audit,
 "shapefile-audit":shapefile_audit,
 "gettext-catalog-audit":gettext_catalog_audit,
 "notebook-audit":notebook_audit,
 "notebook-strip-outputs":notebook_strip_outputs,
 "heic-convert":heic_convert,
 "subtitle-quality-audit":subtitle_quality_audit,
 "kml-to-geojson":kml_to_geojson,
 "coordinate-transform":coordinate_transform,
 "html-structured-data-audit":html_structured_data_audit,
 "html-local-link-audit":html_local_link_audit,
 "css-quality-audit":css_quality_audit,
 "gcode-audit":gcode_audit,
 "midi-audit":midi_audit,
 "musicxml-audit":musicxml_audit,
 "bibtex-audit":bibtex_audit,
 "nmea-track-audit":nmea_track_audit,
 "ansible-playbook-audit":ansible_playbook_audit,
 "prometheus-rules-audit":prometheus_rules_audit,
 "grafana-dashboard-audit":grafana_dashboard_audit,
 "hdf5-audit":hdf5_audit,
 "avro-schema-audit":avro_schema_audit,
 "graphql-schema-audit":graphql_schema_audit,
 "protobuf-schema-audit":protobuf_schema_audit,
 "odf-package-audit":odf_package_audit,
 "xliff-audit":xliff_audit,
 "mbox-audit":mbox_audit,
 "geopackage-audit":geopackage_audit,
 "mbtiles-audit":mbtiles_audit,
 "openraster-audit":openraster_audit,
 "krita-project-audit":krita_project_audit,
 "gltf-audit":gltf_audit,
 "drawio-audit":drawio_audit,
 "n8n-workflow-audit":n8n_workflow_audit,
 "design-token-audit":design_token_audit,
 "warc-archive-audit":warc_archive_audit,
 "wasm-module-audit":wasm_module_audit,
 "sarif-report-audit":sarif_report_audit,
 "sbom-audit":cyclonedx_sbom_audit,
 "junit-xml-audit":junit_xml_audit,
 "coverage-xml-audit":coverage_xml_audit,
 "fits-audit":fits_file_audit,
 "step-cad-audit":step_cad_audit,
 "otel-collector-audit":otel_collector_audit,
 "godot-project-audit":godot_project_audit,
 "unity-package-audit":unity_package_audit,
 "unreal-project-audit":unreal_project_audit,
 "fasta-sequence-audit":fasta_sequence_audit,
 "fastq-quality-audit":fastq_quality_audit,
 "vcf-variant-audit":vcf_variant_audit,
 "sam-alignment-audit":sam_alignment_audit,
 "gff3-annotation-audit":gff3_annotation_audit,
 "bed-interval-audit":bed_interval_audit,
 "genbank-record-audit":genbank_record_audit,
 "pdb-structure-audit":pdb_structure_audit,
 "gfa-assembly-audit":gfa_assembly_audit,
 "newick-tree-audit":newick_tree_audit,
 "sequence-alignment-audit":sequence_alignment_audit,
 "bagit-archive-audit":bagit_archive_audit,
 "frictionless-package-audit":frictionless_package_audit,
 "ro-crate-audit":ro_crate_audit,
 "iiif-manifest-audit":iiif_manifest_audit,
 "datacite-metadata-audit":datacite_metadata_audit,
 "mets-package-audit":mets_package_audit,
 "premis-event-audit":premis_event_audit,
 "stac-catalog-audit":stac_catalog_audit,
 "tei-document-audit":tei_document_audit,
 "ocfl-object-audit":ocfl_object_audit,
 "zarr-store-audit":zarr_store_audit,
 "nifti-header-audit":nifti_header_audit,
 "dicom-privacy-audit":dicom_privacy_audit,
 "las-pointcloud-audit":las_pointcloud_audit,
 "jp2-box-audit":jp2_box_audit,
 "netcdf-classic-audit":netcdf_classic_audit,
 "nwb-structure-audit":nwb_structure_audit,
 "ome-ngff-audit":ome_ngff_audit,
 "parquet-metadata-audit":parquet_metadata_audit,
 "cog-geotiff-audit":cog_geotiff_audit,
 "file-format-identify":file_format_identify,
 "pdf-ocr-searchable":pdf_ocr_searchable,
 "rdf-graph-audit":rdf_graph_audit,
 "shacl-validate":shacl_validate,
 "cron-schedule-audit":cron_schedule_audit,
 "web-article-extract":web_article_extract,
 "rego-policy-check":rego_policy_check,
 "k8s-schema-validate":kubernetes_schema_validate,
 "cosign-verify-blob":cosign_verify_blob,
 "mcap-recording-audit":mcap_recording_audit,
 "iceberg-metadata-audit":iceberg_metadata_audit,
 "onnx-model-audit":onnx_model_audit,
 "otel-trace-audit":otel_trace_audit,
 "safetensors-audit":safetensors_audit,
 "gguf-model-audit":gguf_model_audit,
 "hf-model-card-audit":hf_model_card_audit,
 "chat-dataset-audit":chat_dataset_audit,
 "promptfoo-config-audit":promptfoo_config_audit,
 "three-mf-package-audit":three_mf_package_audit,
 "ollama-modelfile-audit":ollama_modelfile_audit,
 "hf-tokenizer-audit":hf_tokenizer_audit,
 "hf-dataset-card-audit":hf_dataset_card_audit,
 "mlflow-model-audit":mlflow_model_manifest_audit,
 "dvc-pipeline-audit":dvc_pipeline_manifest_audit,
 "helm-chart-audit":helm_chart_metadata_audit,

}


def _runner_output_path(raw_path, root):
    if not raw_path:
        return None
    candidate=Path(raw_path)
    if candidate.is_symlink():
        raise RuntimeError("Pipeline output symlinks are not allowed.")
    resolved=candidate.resolve(strict=True)
    if resolved.parent != root or not resolved.is_file():
        raise RuntimeError("Pipeline output must be a regular file inside the private runner input directory.")
    if resolved.stat().st_size > MAX_PIPELINE_OUTPUT:
        raise RuntimeError("Pipeline intermediate output exceeds 45 MB.")
    return resolved


def _safe_trace_text(value,root):
    text=str(value).strip()
    roots=[str(root.resolve())]
    for path in roots:
        text=text.replace(path,"[runner-path]").replace(path.replace("/","\\"),"[runner-path]")
    text=re.sub(r"(?:(?:/home/runner|/tmp|/private/var/folders)/[^\s\"']+)", "[runner-path]", text)
    text=re.sub(r"[A-Za-z]:\\[^\s\"']+", "[runner-path]", text)
    return text


class PipelineExecutionError(RuntimeError):
    def __init__(self,message,trace):
        super().__init__(message)
        self.trace=trace


def report_job_progress(job,completed,total,current_tool_ids=None):
    job_id=job.get("id") if isinstance(job,dict) else None
    if not isinstance(job_id,str) or not re.fullmatch(r"[a-f0-9-]{36}",job_id,re.I):
        return
    try:
        callback(job_id,{"status":"progress","progress":{"completed":int(completed),"total":int(total),"currentToolIds":list(current_tool_ids or [])}})
    except Exception as exc:
        print(f"Unable to report progress: {exc}",file=sys.stderr)


def run_tool_dag(job,source,root):
    nodes=validate_dag(job)
    by_id={node["id"]:node for node in nodes}
    order={node["id"]:index for index,node in enumerate(nodes)}
    outputs={}; summaries={}; traces={}
    children={node["id"]:0 for node in nodes}
    for node in nodes:
        for parent_id in node["dependsOn"]: children[parent_id]+=1
    pending=list(nodes)
    while pending:
        ready=[node for node in pending if all(parent_id in outputs for parent_id in node["dependsOn"])]
        if not ready: raise RuntimeError("DAG scheduler found a cycle or unresolved dependency.")
        report_job_progress(job,len(traces),len(nodes),[node["toolId"] for node in ready[:3]])
        def execute_node(node):
            node_id=node["id"]; tool_id=node["toolId"]; started=time.perf_counter()
            parent_ids=node["dependsOn"]
            incoming_files=[outputs[parent_id] for parent_id in parent_ids] if parent_ids else [source]
            isolated_files=[]
            try:
                for input_index,incoming in enumerate(incoming_files,1):
                    isolated=root/f"dag-input-{node_id}-{input_index}-{incoming.name}"
                    shutil.copy2(incoming,isolated)
                    isolated_files.append(isolated)
                input_bytes=sum(path.stat().st_size for path in isolated_files)
                if input_bytes>MAX_PIPELINE_OUTPUT:
                    raise RuntimeError("Combined DAG inputs exceed the 45 MB per-node input limit.")
                if len(isolated_files)>1 and tool_id not in MULTI_INPUT_TOOLS:
                    raise RuntimeError(f"Processor {tool_id} does not support multiple input artifacts.")
                processor_input=isolated_files if len(isolated_files)>1 else isolated_files[0]
                result=TOOLS[tool_id](processor_input)
                if not isinstance(result,dict):
                    raise RuntimeError(f"Processor {tool_id} returned an invalid result.")
                summary=str(result.get("summary","")).strip()
                output=_runner_output_path(result.get("output_path",""),root)
                if output is None:
                    output=root/f"dag-{node_id}-result.txt"
                    output.write_text(summary or "Không phát hiện nội dung.",encoding="utf-8")
                output_bytes=output.stat().st_size
                trace={"nodeId":node_id,"step":order[node_id]+1,"total":len(nodes),"toolId":tool_id,
                    "status":"completed","durationMs":max(0,int((time.perf_counter()-started)*1000)),
                    "inputBytes":input_bytes,"outputBytes":output_bytes,"summary":_safe_trace_text(summary,root)[:180]}
                return node_id,output,summary,trace,None
            except Exception as exc:
                try: input_bytes=sum(path.stat().st_size for path in isolated_files if path.is_file())
                except OSError: input_bytes=0
                message=str(exc).strip() or type(exc).__name__
                trace={"nodeId":node_id,"step":order[node_id]+1,"total":len(nodes),"toolId":tool_id,
                    "status":"failed","durationMs":max(0,int((time.perf_counter()-started)*1000)),
                    "inputBytes":input_bytes,"outputBytes":None,"summary":_safe_trace_text(message,root)[:180],
                    "error":_safe_trace_text(message,root)[:250]}
                return node_id,None,message,trace,message
        with concurrent.futures.ThreadPoolExecutor(max_workers=3,thread_name_prefix="nolane-dag") as executor:
            futures=[executor.submit(execute_node,node) for node in ready]
            batch=[future.result() for future in futures]
        failures=[]
        for node_id,output,summary,trace,error in batch:
            traces[node_id]=trace
            if error:
                failures.append((node_id,error))
            else:
                outputs[node_id]=output
                summaries[node_id]=summary
            pending=[node for node in pending if node["id"]!=node_id]
        report_job_progress(job,len([item for item in traces.values() if item["status"]=="completed"]),len(nodes),[])
        if failures:
            ordered=[traces[node["id"]] for node in nodes if node["id"] in traces]
            message="; ".join(node_id+": "+error for node_id,error in failures)
            raise PipelineExecutionError(message,ordered)
    leaves=[node["id"] for node in nodes if children[node["id"]]==0]
    total_bytes=sum(outputs[node_id].stat().st_size for node_id in leaves)
    if total_bytes>MAX_PIPELINE_OUTPUT:
        raise RuntimeError("Combined DAG branch outputs exceed the 45 MB package limit.")
    package=root/"workflow-results.zip"
    manifest={"workflow":"Nolane DAG","maxConcurrency":3,"nodes":[],"terminalOutputs":leaves}
    with zipfile.ZipFile(package,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=4) as archive:
        for node in nodes:
            manifest["nodes"].append({"id":node["id"],"toolId":node["toolId"],"dependsOn":node["dependsOn"],
                "summary":summaries.get(node["id"],""),"outputBytes":outputs[node["id"]].stat().st_size if node["id"] in outputs else None})
        for node_id in leaves:
            output=outputs[node_id]
            if output.is_symlink() or output.resolve(strict=True).parent!=root.resolve():
                raise RuntimeError("A DAG branch output escaped the private runner directory.")
            archive.write(output,f"branches/{node_id}/{output.name}")
        archive.writestr("manifest.json",json.dumps(manifest,ensure_ascii=False,indent=2))
    if package.stat().st_size>MAX_PIPELINE_OUTPUT:
        package.unlink(missing_ok=True)
        raise RuntimeError("DAG result package exceeds the 45 MB output limit.")
    trace=[traces[node["id"]] for node in nodes]
    summary_lines=[f"Branch {node['id']} · {node['toolId']}: {summaries[node['id']]}" for node in nodes]
    summary="DAG hoàn tất: "+str(len(nodes))+" node, tối đa 3 node chạy đồng thời; "+str(len(leaves))+" nhánh đầu ra được đóng gói.\n\n"+"\n\n".join(summary_lines)
    return {"summary":summary[:6000],"output_path":str(package),"trace":trace}
def run_tool_pipeline(job, source, root, translation_callback=None):
    if job.get("workflowDag") is not None:
        return run_tool_dag(job,source,root)
    steps=validate_pipeline(job)
    current=source
    summaries=[]
    trace=[]
    result={}
    for index,step in enumerate(steps):
        tool_id=step["toolId"]
        report_job_progress(job,index,len(steps),[tool_id])
        started=time.perf_counter()
        try:
            input_bytes=current.stat().st_size if current.is_file() else 0
            if tool_id=="text-translate":
                result=TOOLS[tool_id](current,translation_callback)
            else:
                result=TOOLS[tool_id](current)
            if not isinstance(result,dict):
                raise RuntimeError(f"Processor {tool_id} returned an invalid result.")
            summary=str(result.get("summary","")).strip()
            output=_runner_output_path(result.get("output_path",""),root)
            is_last=index==len(steps)-1
            if output:
                current=output
                output_bytes=output.stat().st_size
            elif not is_last:
                next_id=steps[index+1]["toolId"]
                if next_id != "text-clean" or tool_id not in TEXT_OUTPUT_TOOLS:
                    raise RuntimeError(f"Processor {tool_id} did not produce a file for the next pipeline step.")
                current=root/f"pipeline-step-{index+1}.txt"
                current.write_text(summary or "Không phát hiện nội dung.",encoding="utf-8")
                output_bytes=current.stat().st_size
            else:
                output_bytes=None
            duration_ms=max(0,int((time.perf_counter()-started)*1000))
            trace.append({
                "step":index+1,"total":len(steps),"toolId":tool_id,"status":"completed",
                "durationMs":duration_ms,"inputBytes":input_bytes,"outputBytes":output_bytes,
                "summary":_safe_trace_text(summary,root)[:180],
            })
            summaries.append(f"Step {index+1}/{len(steps)} · {tool_id}: {summary or 'completed'}")
            report_job_progress(job,index+1,len(steps),[])
        except Exception as exc:
            duration_ms=max(0,int((time.perf_counter()-started)*1000))
            try: input_bytes=current.stat().st_size if current.is_file() else 0
            except OSError: input_bytes=0
            message=str(exc).strip() or type(exc).__name__
            trace.append({
                "step":index+1,"total":len(steps),"toolId":tool_id,"status":"failed",
                "durationMs":duration_ms,"inputBytes":input_bytes,"outputBytes":None,
                "summary":_safe_trace_text(message,root)[:180],"error":_safe_trace_text(message,root)[:250],
            })
            raise PipelineExecutionError(message,trace) from exc
    final_output=str(_runner_output_path(result.get("output_path",""),root) or "")
    total_summary="\n\n".join(summaries)
    return {"summary":total_summary[:6000],"output_path":final_output,"trace":trace}

def cmd_fetch(args):
    secret=os.environ.get("TELEGRAM_WEBHOOK_SECRET")
    if not secret: raise RuntimeError("Missing TELEGRAM_WEBHOOK_SECRET.")
    data=api_json(WORKER_URL+"/internal/tools/runner?job_id="+urllib.parse.quote(args.job_id),token=secret)
    Path(args.output).write_text(json.dumps(data,ensure_ascii=False),encoding="utf-8")

def cmd_download(args):
    job=load_job(Path(args.job_file))
    if job.get("githubSource"):
        if job.get("toolId") not in GITHUB_SOURCE_PROCESSORS:
            raise RuntimeError("GitHub source is only allowed for reviewed repository-inspection processors.")
        download_github_source(job,args.output)
        return
    source=download_telegram(job["fileId"],job.get("fileName") or "upload.bin")
    Path(args.output).write_text(str(source),encoding="utf-8")

def _cmd_run(args, translation_callback=None):
    job=load_job(Path(args.job_file))
    source=Path(Path(args.input_path_file).read_text(encoding="utf-8").strip())
    root=(Path(os.environ.get("RUNNER_TEMP","/tmp"))/"nolane-inputs").resolve()
    if source.is_symlink():
        raise RuntimeError("Input file symlinks are not allowed.")
    resolved=source.resolve(strict=True)
    if resolved.parent != root or not resolved.is_file():
        raise RuntimeError("Input file is outside the private runner input directory.")
    try:
        result=run_tool_pipeline(job,resolved,root,translation_callback=translation_callback)
    except PipelineExecutionError as exc:
        Path(args.output).write_text(json.dumps({"error":_safe_trace_text(exc,root)[:1000],"trace":exc.trace},ensure_ascii=False),encoding="utf-8")
        raise
    summary=str(result.get("summary",""))
    output=result.get("output_path","")
    if output:
        candidate=Path(output)
        try:
            root_resolved=root.resolve()
            if not candidate.is_symlink():
                resolved_output=candidate.resolve(strict=True)
                if resolved_output.parent==root_resolved and resolved_output.is_file() and resolved_output.suffix.lower() in {".txt",".md",".csv",".json",".xml",".yaml",".yml",".srt",".vtt",".html"}:
                    preview=resolved_output.read_text(encoding="utf-8-sig",errors="replace")[:3800].strip()
                    if preview:
                        summary += "\n\nNội dung trích xuất (trích đoạn tối đa 3.800 ký tự; tệp đầy đủ được gửi kèm):\n" + preview
        except (OSError,UnicodeError):
            pass
    Path(args.output).write_text(json.dumps({"summary":summary[:6000],"output_path":output,"trace":result.get("trace",[])},ensure_ascii=False),encoding="utf-8")


def cmd_run(args):
    _cmd_run(args)


def cmd_translate(args):
    secret=os.environ.get("TELEGRAM_WEBHOOK_SECRET")
    if not secret: raise RuntimeError("Missing TELEGRAM_WEBHOOK_SECRET for Worker-based translation.")
    job=load_job(Path(args.job_file))
    if not any(step.get("toolId")=="text-translate" for step in job.get("pipeline",[])):
        raise RuntimeError("The selected job does not contain the text-translate processor.")
    def translate_chunk(chunk):
        response=api_json(
            WORKER_URL+"/internal/tools/translate",
            method="POST",
            data={"job_id":job["id"],"text":chunk},
            token=secret,
        )
        if not isinstance(response.get("translation"),str):
            raise RuntimeError("Worker returned an invalid translation result.")
        return response
    _cmd_run(args,translation_callback=translate_chunk)

def send_document(chat_id,path,caption):
    token=os.environ["TELEGRAM_BOT_TOKEN"]; boundary="----NolaneToolBoundary-31d9"
    fields=[]
    def text_field(name,value):
        fields.append((f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n").encode())
    text_field("chat_id",str(chat_id)); text_field("caption",caption[:850])
    filename=Path(path).name.replace('"',"_")[:120]
    head=(f"--{boundary}\r\nContent-Disposition: form-data; name=\"document\"; filename=\"{filename}\"\r\nContent-Type: application/octet-stream\r\n\r\n").encode()
    body=b"".join(fields)+head+Path(path).read_bytes()+f"\r\n--{boundary}--\r\n".encode()
    req=urllib.request.Request(f"https://api.telegram.org/bot{token}/sendDocument",data=body,headers={"content-type":f"multipart/form-data; boundary={boundary}"},method="POST")
    with urllib.request.urlopen(req,timeout=90) as r:
        result=json.loads(r.read(1_000_000).decode())
    if not result.get("ok"): raise RuntimeError(result.get("description","Telegram sendDocument failed."))

def callback(job_id,payload):
    secret=os.environ.get("TELEGRAM_WEBHOOK_SECRET")
    if not secret: raise RuntimeError("Missing TELEGRAM_WEBHOOK_SECRET.")
    return api_json(WORKER_URL+"/internal/tools/runner",method="POST",data={"job_id":job_id,**payload},token=secret)

def cmd_complete(args):
    # Re-fetch authoritative metadata after untrusted file processing has finished.
    token=os.environ.get("TELEGRAM_WEBHOOK_SECRET")
    if not token: raise RuntimeError("Missing TELEGRAM_WEBHOOK_SECRET.")
    job_data=api_json(
        WORKER_URL+"/internal/tools/runner?job_id="+urllib.parse.quote(args.job_id),
        token=token,
    )
    job=job_data.get("job")
    if not isinstance(job,dict) or job.get("id")!=args.job_id:
        raise RuntimeError("Worker returned an invalid or mismatched tool job.")
    result=json.loads(Path(args.result_file).read_text(encoding="utf-8"))
    output=result.get("output_path")
    if output:
        root=(Path(os.environ.get("RUNNER_TEMP","/tmp"))/"nolane-inputs").resolve()
        candidate=Path(output)
        if candidate.is_symlink():
            raise RuntimeError("Tool output symlinks are not allowed.")
        p=candidate.resolve(strict=True)
        if p.parent!=root or not p.is_file() or p.stat().st_size>45*1024*1024:
            raise RuntimeError("Tool output must be a regular file inside the private runner input directory and stay under 45 MB.")
        send_document(int(job["chatId"]),p,"Nolane Tools · "+job["toolId"])
    callback(args.job_id,{"status":"completed","summary":result.get("summary","Đã hoàn thành."),"trace":result.get("trace",[])})

def cmd_fail(args):
    try:
        payload={"status":"failed","error":args.message[:1000]}
        result_path=Path(args.result_file) if args.result_file else None
        if result_path and result_path.is_file():
            try:
                result=json.loads(result_path.read_text(encoding="utf-8"))
                if isinstance(result,dict):
                    if isinstance(result.get("trace"),list): payload["trace"]=result["trace"]
                    if isinstance(result.get("error"),str) and result["error"].strip(): payload["error"]=result["error"][:1000]
            except (OSError,ValueError):
                pass
        callback(args.job_id,payload)
    except Exception as exc: print(f"Unable to report failure: {exc}",file=sys.stderr)


def main():
    parser=argparse.ArgumentParser(); sub=parser.add_subparsers(dest="cmd",required=True)
    p=sub.add_parser("fetch"); p.add_argument("job_id"); p.add_argument("output"); p.set_defaults(func=cmd_fetch)
    p=sub.add_parser("download"); p.add_argument("job_file"); p.add_argument("output"); p.set_defaults(func=cmd_download)
    p=sub.add_parser("run"); p.add_argument("job_file"); p.add_argument("input_path_file"); p.add_argument("output"); p.set_defaults(func=cmd_run)
    p=sub.add_parser("translate"); p.add_argument("job_file"); p.add_argument("input_path_file"); p.add_argument("output"); p.set_defaults(func=cmd_translate)
    p=sub.add_parser("complete"); p.add_argument("job_id"); p.add_argument("result_file"); p.set_defaults(func=cmd_complete)
    p=sub.add_parser("fail"); p.add_argument("job_id"); p.add_argument("--message",default="Tool runner failed; see Actions logs."); p.add_argument("--result-file",default=""); p.set_defaults(func=cmd_fail)
    args=parser.parse_args()
    try: args.func(args)
    except Exception as exc:
        print(f"Nolane Tools error: {exc}",file=sys.stderr)
        sys.exit(1)

if __name__=="__main__": main()
