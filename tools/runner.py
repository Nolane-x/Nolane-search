#!/usr/bin/env python3
"""Private GitHub-hosted execution engine for Nolane Tools."""
from __future__ import annotations
import argparse, base64, concurrent.futures, csv, hashlib, json, mimetypes, os, posixpath, re, shutil, stat, subprocess, sys, tarfile, tempfile, textwrap, threading, time, unicodedata, urllib.error, urllib.parse, urllib.request, zipfile
from pathlib import Path
from html import escape, unescape
from html.parser import HTMLParser
from typing import Any

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
}

MULTI_INPUT_TOOLS = {"text-join"}
MAX_DAG_PARENTS = 3
TEXT_OUTPUT_TOOLS = {"image-ocr","qr-read","pdf-text","office-text","html-text","subtitle-text","audio-transcribe","epub-text","pdf-outline","sqlite-integrity","audio-silence-report","video-silence-report","code-size-report","text-stats","log-insights","json-diff","markdown-outline","code-imports","code-todos","code-secret-scan","log-timeline","repo-inventory","repo-dependencies","repo-license-report","repo-secret-scan","repo-todo-scan","repo-code-stats","repo-config-audit","repo-test-map","repo-test-quality","repo-complexity-report","repo-api-surface","repo-docs-audit","repo-migration-audit","repo-runtime-risk","repo-i18n-audit","repo-env-contract","repo-architecture-cycles","repo-change-impact","repo-api-spec-audit","repo-container-audit","repo-ci-reliability","docx-audit","pptx-audit","csv-privacy-audit","archive-security-audit","xlsx-privacy-audit","pdf-privacy-audit","office-active-content-audit","pdf-active-content-audit","email-security-audit","jwt-security-audit","har-privacy-audit","ics-calendar-audit","vcard-privacy-audit","gpx-track-report","geojson-audit","font-inspect","openapi-contract-audit","color-convert","pcap-network-audit","audio-tag-audit","json-schema-validate","epub-structure-audit","markdown-quality-audit","dns-zone-audit","x509-certificate-audit","rss-atom-audit","sitemap-xml-audit","robots-txt-audit","jsonl-profile","image-privacy-audit","svg-safety-audit","wcag-contrast-audit","ssh-public-key-audit","sqlfluff-lint","python-security-audit","mesh-inspect","dxf-audit","shapefile-audit","gettext-catalog-audit","notebook-audit","html-structured-data-audit","css-quality-audit"}
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
 "html-structured-data-audit":html_structured_data_audit,"html-accessibility-audit":html_accessibility_audit,
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
 "html-seo-audit":html_seo_audit,
 "html-local-link-audit":html_local_link_audit,
 "css-quality-audit":css_quality_audit,

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
