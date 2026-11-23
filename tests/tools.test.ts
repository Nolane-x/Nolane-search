import { describe, expect, it } from "vitest";
import { TOOL_CATALOG, getTool, inferToolForUpload, isToolCompatible, validateToolDag, validateToolDagDefinition, validateToolPipeline, validateToolPipelineDefinition } from "../src/tools";

describe("Nolane Tools registry", () => {
  it("contains uniquely identified, documented tools", () => {
    const ids = TOOL_CATALOG.map(tool => tool.id);
    expect(new Set(ids).size).toBe(ids.length);
    expect(TOOL_CATALOG).toHaveLength(462);
    expect(TOOL_CATALOG.every(tool => tool.ready && tool.description.length > 12 && tool.accepts.length > 0)).toBe(true);
    for (const id of ["pdf-table-extract","json-jmespath-query","ip-network-report","barcode-generate","docx-to-markdown","pptx-notes-extract","fuzzy-match-report","csv-to-parquet","parquet-to-csv","sqlglot-format","sqlfluff-lint","python-security-audit","unit-convert","mesh-inspect","dxf-audit","shapefile-audit","gettext-catalog-audit","notebook-audit","notebook-strip-outputs","heic-convert","subtitle-quality-audit","kml-to-geojson","coordinate-transform","html-structured-data-audit","html-local-link-audit","css-quality-audit","text-extract-todo-comments", "text-extract-markdown-images", "text-strip-markdown-frontmatter", "text-markdown-to-plain", "text-sort-unique-words", "text-word-to-lines", "text-join-lines", "text-extract-domains", "text-extract-uuids", "text-extract-semver", "text-extract-ipv6", "text-redact-secrets", "text-extract-comment-lines", "text-tabs-to-spaces", "text-escape-regex", "text-unescape-regex", "json-merge-objects", "json-array-dedupe", "json-array-to-lines", "csv-trim-cells", "csv-remove-empty-columns", "csv-empty-cell-report"]) expect(getTool(id)?.ready).toBe(true);
    for (const id of ["text-translate","language-detect","text-uppercase","text-lowercase","text-title-case","text-sort-lines","text-reverse-lines","text-number-lines","text-remove-blank-lines","text-wrap","text-trim-lines","text-extract-emails","text-extract-urls","text-extract-hashtags","text-to-base64","base64-to-text","url-encode","url-decode","json-minify","json-sort-keys","text-slugify","text-word-frequency","text-extract-numbers","text-extract-dates","text-reverse-characters","text-snake-case","text-kebab-case","text-camel-case","text-swap-case","text-extract-ipv4","text-mask-emails","text-mask-phones","json-to-jsonl","jsonl-to-json","csv-to-tsv","tsv-to-csv","csv-to-markdown","html-minify","xml-minify","text-remove-emoji","text-collapse-whitespace","text-remove-punctuation","text-to-ascii","text-html-escape","text-html-unescape","text-extract-mentions","text-extract-hex-colors","text-extract-phones","text-dedupe-lines","text-count-report","text-quote-lines","text-unquote-lines","csv-transpose","csv-sort-rows","csv-dedupe-rows","csv-to-xml","csv-to-html","json-sort-array","json-remove-nulls","json-to-html-table","text-pascal-case","text-constant-case","text-dot-case","text-initials","text-normalize-unicode","text-remove-control-chars","text-remove-duplicate-words","text-extract-markdown-links","text-extract-markdown-headings","text-extract-quotes","text-paragraph-report","json-flatten","json-unflatten","json-keys-report","csv-remove-empty-rows","csv-add-row-numbers","csv-column-stats","csv-normalize-headers","csv-to-jsonl","jsonl-to-csv","text-indent-lines","text-unindent-lines","text-dedupe-paragraphs","text-tokenize-words","text-sentence-report","text-line-length-report","text-normalize-newlines","text-remove-zero-width","text-extract-file-paths","text-sort-words","html-extract-links","html-extract-images","html-extract-title","html-sanitize","xml-tree-report","json-to-xml","json-type-report","json-escape-string","json-unescape-string","csv-unique-values","text-sentence-case","text-normalize-quotes","text-normalize-dashes","text-reverse-word-order","text-extract-words","text-extract-sentences","text-dedupe-sentences","text-remove-markdown-formatting","text-markdown-toc","text-markdown-code-blocks","text-markdown-table-extract","text-extract-numbered-lists","text-join-hyphenated-lines","text-strip-bom","text-normalize-paragraph-spacing","csv-schema-infer","csv-duplicates-report","csv-sample-rows","json-array-stats","json-canonicalize"]) expect(getTool(id)?.ready).toBe(true);
    for (const id of ["pdf-rotate-cw","pdf-remove-blank","image-trim-border","image-pixelate","image-diff","audio-stereo-split","audio-metadata-clean","video-scene-frames","video-metadata-clean","json-flatten-csv","csv-to-sqlite","log-insights","json-diff","text-join"]) expect(getTool(id)).not.toBeNull();
  });
    for (const id of ["gcode-audit", "midi-audit", "musicxml-audit", "bibtex-audit", "nmea-track-audit", "ansible-playbook-audit", "prometheus-rules-audit", "grafana-dashboard-audit", "hdf5-audit", "avro-schema-audit", "graphql-schema-audit", "protobuf-schema-audit"]) expect(getTool(id)?.ready).toBe(true);
    for (const id of ["odf-package-audit", "xliff-audit", "mbox-audit", "geopackage-audit", "mbtiles-audit", "openraster-audit", "krita-project-audit", "gltf-audit", "drawio-audit", "n8n-workflow-audit", "design-token-audit", "warc-archive-audit"]) expect(getTool(id)?.ready).toBe(true);
    for (const id of ["wasm-module-audit", "sarif-report-audit", "sbom-audit", "junit-xml-audit", "coverage-xml-audit", "fits-audit", "step-cad-audit", "otel-collector-audit", "godot-project-audit", "unity-package-audit", "unreal-project-audit"]) expect(getTool(id)?.ready).toBe(true);
    for (const id of ["fasta-sequence-audit", "fastq-quality-audit", "vcf-variant-audit", "sam-alignment-audit", "gff3-annotation-audit", "bed-interval-audit", "genbank-record-audit", "pdb-structure-audit", "gfa-assembly-audit", "newick-tree-audit", "sequence-alignment-audit"]) expect(getTool(id)?.ready).toBe(true);
    for (const id of ["bagit-archive-audit", "frictionless-package-audit", "ro-crate-audit", "iiif-manifest-audit", "datacite-metadata-audit", "mets-package-audit", "premis-event-audit", "stac-catalog-audit", "tei-document-audit"]) expect(getTool(id)?.ready).toBe(true);
    for (const id of ["ocfl-object-audit", "zarr-store-audit", "nifti-header-audit", "dicom-privacy-audit", "las-pointcloud-audit", "jp2-box-audit", "netcdf-classic-audit", "nwb-structure-audit"]) expect(getTool(id)?.ready).toBe(true);
    for (const id of ["ome-ngff-audit", "parquet-metadata-audit", "cog-geotiff-audit"]) expect(getTool(id)?.ready).toBe(true);
    expect(getTool("file-format-identify")?.ready).toBe(true);

  it("infers a suitable default tool from common uploaded media", () => {
    expect(inferToolForUpload({}, true)).toBe("image-ocr");
    expect(inferToolForUpload({ mimeType: "image/jpeg", fileName: "photo.jpg" })).toBe("image-ocr");
    expect(inferToolForUpload({ mimeType: "application/octet-stream", fileName: "photo.png" })).toBe("image-ocr");
    expect(isToolCompatible(getTool("pdf-text")!, "application/octet-stream", "scan.pdf")).toBe(true);
    expect(inferToolForUpload({ mimeType: "application/pdf", fileName: "scan.pdf" })).toBe("pdf-text");
    expect(inferToolForUpload({ mimeType: "application/epub+zip", fileName: "book.epub" })).toBe("epub-text");
    expect(inferToolForUpload({ mimeType: "application/octet-stream", fileName: "archive.sqlite" })).toBe("sqlite-inspect");
    expect(inferToolForUpload({ mimeType: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", fileName: "sales.xlsx" })).toBe("xlsx-profile");
    expect(inferToolForUpload({ mimeType: "text/yaml", fileName: "config.yml" })).toBe("yaml-format");
    expect(inferToolForUpload({ mimeType: "application/xml", fileName: "feed.xml" })).toBe("xml-format");
    expect(inferToolForUpload({ mimeType: "text/x-python", fileName: "script.py" })).toBe("code-check");
    expect(inferToolForUpload({ mimeType: "text/html", fileName: "page.html" })).toBe("html-text");
    expect(inferToolForUpload({ mimeType: "text/plain", fileName: "notes.txt" })).toBe("text-clean");
    expect(inferToolForUpload({ mimeType: "text/vtt", fileName: "captions.vtt" })).toBe("subtitle-text");
    expect(inferToolForUpload({ mimeType: "audio/mpeg", fileName: "voice.mp3" })).toBe("audio-transcribe");
    expect(inferToolForUpload({ mimeType: "video/mp4", fileName: "clip.mp4" })).toBe("video-info");
    expect(inferToolForUpload({ mimeType: "text/csv", fileName: "data.csv" })).toBe("csv-profile");
    expect(inferToolForUpload({ mimeType: "application/json", fileName: "data.json" })).toBe("json-format");
    expect(inferToolForUpload({ mimeType: "application/octet-stream", fileName: "capture.har" })).toBe("har-privacy-audit");
    expect(inferToolForUpload({ mimeType: "text/calendar", fileName: "calendar.ics" })).toBe("ics-calendar-audit");
    expect(inferToolForUpload({ mimeType: "text/vcard", fileName: "contacts.vcf" })).toBe("vcard-privacy-audit");
    expect(inferToolForUpload({ mimeType: "application/gpx+xml", fileName: "route.gpx" })).toBe("gpx-track-report");
    expect(inferToolForUpload({ mimeType: "application/geo+json", fileName: "map.geojson" })).toBe("geojson-audit");
    expect(inferToolForUpload({ mimeType: "application/vnd.tcpdump.pcap", fileName: "capture.pcap" })).toBe("pcap-network-audit");
    expect(inferToolForUpload({ mimeType: "application/rss+xml", fileName: "news.rss" })).toBe("rss-atom-audit");
    expect(inferToolForUpload({ mimeType: "text/plain", fileName: "robots.txt" })).toBe("robots-txt-audit");
    expect(inferToolForUpload({ mimeType: "image/svg+xml", fileName: "logo.svg" })).toBe("svg-safety-audit");
    expect(inferToolForUpload({ mimeType: "text/plain", fileName: "id_ed25519.pub" })).toBe("ssh-public-key-audit");
    expect(inferToolForUpload({ mimeType: "text/markdown", fileName: "guide.md" })).toBe("markdown-quality-audit");
    expect(inferToolForUpload({ mimeType: "application/octet-stream", fileName: "example.zone" })).toBe("dns-zone-audit");
    expect(inferToolForUpload({ mimeType: "application/pkix-cert", fileName: "certificate.pem" })).toBe("x509-certificate-audit");
    expect(inferToolForUpload({ mimeType: "application/octet-stream", fileName: "brand.otf" })).toBe("font-inspect");
    expect(inferToolForUpload({ mimeType: "application/x-ndjson", fileName: "events.jsonl" })).toBe("jsonl-format");
    expect(inferToolForUpload({ mimeType: "application/vnd.openxmlformats-officedocument.wordprocessingml.document", fileName: "notes.docx" })).toBe("office-text");
  });

  it("validates multi-step pipelines against explicit file types and data-flow edges", () => {
    const video = { mimeType: "video/mp4", fileName: "clip.mp4" };
    const valid = validateToolPipeline(video, [
      { toolId: "video-audio", reason: "extract audio" },
      { toolId: "audio-convert", reason: "normalize for speech recognition" },
      { toolId: "audio-transcribe", reason: "transcribe" },
    ]);
    expect(valid.ok).toBe(true);
    if (valid.ok) expect(valid.steps.map(step => step.toolId)).toEqual(["video-audio","audio-convert","audio-transcribe"]);

    expect(validateToolPipeline(video, [{toolId:"pdf-text"}]).ok).toBe(false);
    expect(validateToolPipeline(video, [{toolId:"video-info"},{toolId:"audio-transcribe"}]).ok).toBe(false);
    expect(validateToolPipeline(video, [{toolId:"video-audio"},{toolId:"video-audio"}]).ok).toBe(false);
    expect(validateToolPipeline(video, [
      {toolId:"video-audio"},{toolId:"audio-convert"},{toolId:"audio-transcribe"},{toolId:"text-clean"},{toolId:"text-clean"},
    ]).ok).toBe(false);
    expect(validateToolPipeline({mimeType:"application/json",fileName:"rows.json"}, [
      {toolId:"json-to-csv"},{toolId:"csv-clean"},{toolId:"csv-to-xlsx"},
    ]).ok).toBe(true);
    expect(validateToolPipeline({mimeType:"text/csv",fileName:"rows.csv"}, [{toolId:"csv-to-json"},{toolId:"json-format"}]).ok).toBe(true);
    expect(validateToolPipeline({mimeType:"application/pdf",fileName:"scan.pdf"}, [{toolId:"pdf-extract-images"},{toolId:"archive-inspect"}]).ok).toBe(true);
  });

  it("validates reusable workflow definitions without assuming an uploaded file", () => {
    const valid = validateToolPipelineDefinition([
      { toolId: "video-audio" },
      { toolId: "audio-convert" },
      { toolId: "audio-transcribe" },
    ]);
    expect(valid.ok).toBe(true);
    expect(validateToolPipelineDefinition([{ toolId: "not-real" }]).ok).toBe(false);
    expect(validateToolPipelineDefinition([{ toolId: "video-info" }, { toolId: "audio-transcribe" }]).ok).toBe(false);
    expect(validateToolPipelineDefinition([{ toolId: "image-ocr" }, { toolId: "text-clean" }, { toolId: "text-clean" }]).ok).toBe(false);
    expect(validateToolPipelineDefinition(Array.from({ length: 5 }, () => ({ toolId: "file-hash" }))).ok).toBe(false);
    const longer = validateToolPipelineDefinition([
      "video-audio", "audio-convert", "audio-transcribe", "text-clean", "text-deduplicate", "text-stats",
    ].map(toolId => ({ toolId })));
    expect(longer.ok).toBe(true);
    expect(longer.ok && longer.steps).toHaveLength(6);
    for (const id of ["pdf-merge","pdf-metadata-clean","pdf-outline","image-contact-sheet","image-duplicates","csv-split","csv-join","json-schema","json-to-yaml","sqlite-integrity","audio-silence-report","video-silence-report","video-frames","subtitle-convert","text-deduplicate","text-diff","code-size-report"]) {
      expect(getTool(id)?.ready).toBe(true);
    }
  });

  it("validates explicit tool selection against MIME types and extensions", () => {
    expect(isToolCompatible(getTool("image-ocr")!, "image/jpeg", "photo.jpg")).toBe(true);
    expect(isToolCompatible(getTool("image-ocr")!, "application/octet-stream", "photo.png")).toBe(true);
    expect(isToolCompatible(getTool("pdf-text")!, "application/pdf", "scan.pdf")).toBe(true);
    expect(isToolCompatible(getTool("pdf-info")!, "application/octet-stream", "scan.PDF")).toBe(true);
    expect(isToolCompatible(getTool("image-info")!, "application/octet-stream", "photo.webp")).toBe(true);
    expect(isToolCompatible(getTool("audio-info")!, "application/octet-stream", "recording.aac")).toBe(true);
    expect(isToolCompatible(getTool("video-thumbnail")!, "application/octet-stream", "movie.avi")).toBe(true);
    expect(isToolCompatible(getTool("audio-normalize")!, "audio/mpeg", "podcast.mp3")).toBe(true);
    expect(isToolCompatible(getTool("video-audio")!, "video/mp4", "clip.mp4")).toBe(true);
    expect(isToolCompatible(getTool("video-gif")!, "video/webm", "clip.webm")).toBe(true);
    expect(isToolCompatible(getTool("image-webp")!, "image/png", "transparent.png")).toBe(true);
    expect(isToolCompatible(getTool("pdf-to-images")!, "application/pdf", "book.pdf")).toBe(true);
    expect(isToolCompatible(getTool("sqlite-inspect")!, "application/octet-stream", "data.sqlite3")).toBe(true);
    expect(isToolCompatible(getTool("archive-safe-extract")!, "application/zip", "bundle.zip")).toBe(true);
    expect(isToolCompatible(getTool("pdf-text")!, "image/jpeg", "photo.jpg")).toBe(false);
    expect(isToolCompatible(getTool("office-text")!, "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "notes.docx")).toBe(true);
    expect(isToolCompatible(getTool("csv-to-json")!, "text/csv", "people.csv")).toBe(true);
    expect(isToolCompatible(getTool("jsonl-format")!, "application/x-ndjson", "events.jsonl")).toBe(true);
    expect(isToolCompatible(getTool("pdf-extract-images")!, "application/pdf", "scan.pdf")).toBe(true);
    expect(isToolCompatible(getTool("sqlite-export")!, "application/octet-stream", "data.sqlite3")).toBe(true);
    expect(isToolCompatible(getTool("image-grayscale")!, "image/png", "photo.png")).toBe(true);
    expect(getTool("not-a-tool")).toBeNull();
  });
  it("allows a bounded text-join fan-in only after compatible parent branches", () => {
    const dag = [
      { id: "source", toolId: "pdf-text", dependsOn: [] },
      { id: "clean", toolId: "text-clean", dependsOn: ["source"] },
      { id: "stats", toolId: "text-stats", dependsOn: ["clean"] },
      { id: "unique", toolId: "text-deduplicate", dependsOn: ["clean"] },
      { id: "merged", toolId: "text-join", dependsOn: ["stats", "unique"] },
    ];
    expect(validateToolDagDefinition(dag)).toMatchObject({
      ok: true, roots: ["source"], leaves: ["merged"],
    });
    expect(validateToolDag({ mimeType: "application/pdf", fileName: "report.pdf" }, dag).ok).toBe(true);

    const ordinaryMultiParent = dag.map(node => ({ ...node }));
    ordinaryMultiParent[4] = { id: "merged", toolId: "text-clean", dependsOn: ["stats", "unique"] };
    expect(validateToolDagDefinition(ordinaryMultiParent).ok).toBe(false);

    const singleParentJoin = dag.map(node => ({ ...node }));
    singleParentJoin[4] = { id: "merged", toolId: "text-join", dependsOn: ["stats"] };
    expect(validateToolDagDefinition(singleParentJoin).ok).toBe(false);

    const repeatedParent = dag.map(node => ({ ...node }));
    repeatedParent[4] = { id: "merged", toolId: "text-join", dependsOn: ["stats", "stats"] };
    expect(validateToolDagDefinition(repeatedParent).ok).toBe(false);

    expect(validateToolPipelineDefinition([
      { toolId: "text-stats" }, { toolId: "text-join" },
    ]).ok).toBe(false);
    expect(validateToolPipelineDefinition([
      { toolId: "repo-security-audit" }, { toolId: "archive-inspect" },
    ]).ok).toBe(true);
    expect(validateToolPipelineDefinition([
      { toolId: "repo-supply-chain" }, { toolId: "archive-manifest" },
    ]).ok).toBe(true);
    expect(validateToolPipelineDefinition([{ toolId: "text-join" }]).ok).toBe(false);
  });

  it("validates branching DAGs, topological dependencies and file-compatible roots", () => {
    const dag = [
      { id: "source", toolId: "video-audio", dependsOn: [] },
      { id: "transcript", toolId: "audio-transcribe", dependsOn: ["source"] },
      { id: "converted", toolId: "audio-convert", dependsOn: ["source"] },
    ];
    expect(validateToolDagDefinition(dag)).toMatchObject({ ok: true, roots: ["source"], leaves: ["transcript", "converted"] });
    expect(validateToolDag({ mimeType: "video/mp4", fileName: "clip.mp4" }, dag).ok).toBe(true);
    expect(validateToolDag({ mimeType: "image/png", fileName: "photo.png" }, dag).ok).toBe(false);
    expect(validateToolDagDefinition([
      { id: "source", toolId: "video-audio", dependsOn: [] },
      { id: "bad", toolId: "pdf-text", dependsOn: ["source"] },
    ]).ok).toBe(false);
    expect(validateToolDagDefinition([
      { id: "source", toolId: "video-audio", dependsOn: [] },
      { id: "child", toolId: "audio-transcribe", dependsOn: ["later"] },
      { id: "later", toolId: "audio-convert", dependsOn: ["source"] },
    ]).ok).toBe(false);
    expect(validateToolDagDefinition([
      { id: "only", toolId: "file-hash", dependsOn: [] },
      { id: "next", toolId: "text-clean", dependsOn: ["only"] },
    ]).ok).toBe(false);
  });

  it("validates the new developer processors and their real data-flow transitions", () => {
    expect(getTool("markdown-outline")?.category).toBe("developer");
    expect(getTool("code-secret-scan")?.ready).toBe(true);
    expect(isToolCompatible(getTool("markdown-outline")!, "text/markdown", "README.md")).toBe(true);
    expect(isToolCompatible(getTool("code-imports")!, "text/x-python", "main.py")).toBe(true);
    expect(isToolCompatible(getTool("log-timeline")!, "text/plain", "service.log")).toBe(true);
    expect(validateToolPipeline({mimeType:"text/markdown",fileName:"README.md"}, [
      {toolId:"markdown-links"},{toolId:"csv-profile"},
    ]).ok).toBe(true);
    expect(validateToolPipeline({mimeType:"text/plain",fileName:"service.log"}, [
      {toolId:"log-timeline"},{toolId:"text-stats"},
    ]).ok).toBe(true);
    expect(validateToolPipeline({mimeType:"text/plain",fileName:"notes.txt"}, [
      {toolId:"text-redact"},{toolId:"text-deduplicate"},
    ]).ok).toBe(true);
    expect(validateToolPipeline({mimeType:"text/plain",fileName:"source.py"}, [
      {toolId:"code-secret-scan"},{toolId:"text-stats"},
    ]).ok).toBe(true);
  });

  it("validates repository ZIP processors and their real report transitions", () => {
    for (const id of ["repo-inventory","repo-dependencies","repo-license-report","repo-secret-scan","repo-todo-scan","repo-code-stats","repo-config-audit","repo-duplicates","repo-intelligence","repo-security-audit","repo-supply-chain"]) {
      expect(getTool(id)?.category).toBe("repository");
      expect(isToolCompatible(getTool(id)!, "application/zip", "source.zip")).toBe(true);
    }
    expect(validateToolPipeline({mimeType:"application/zip",fileName:"source.zip"}, [
      {toolId:"repo-secret-scan"},{toolId:"text-stats"},
    ]).ok).toBe(true);
    expect(validateToolPipeline({mimeType:"application/zip",fileName:"source.zip"}, [
      {toolId:"repo-duplicates"},{toolId:"csv-profile"},
    ]).ok).toBe(true);
    expect(validateToolPipeline({mimeType:"application/zip",fileName:"source.zip"}, [
      {toolId:"repo-todo-scan"},{toolId:"text-deduplicate"},
    ]).ok).toBe(true);
    expect(validateToolPipeline({mimeType:"application/zip",fileName:"source.zip"}, [
      {toolId:"repo-inventory"},{toolId:"pdf-text"},
    ]).ok).toBe(false);
  });


  it("accepts the new translation and everyday text pipelines", () => {
    const textFile={mimeType:"text/plain",fileName:"notes.txt"};
    expect(isToolCompatible(getTool("text-translate")!,textFile.mimeType,textFile.fileName)).toBe(true);
    expect(validateToolPipeline(textFile,[{toolId:"text-translate"},{toolId:"text-clean"},{toolId:"text-stats"}]).ok).toBe(true);
    expect(validateToolPipeline(textFile,[{toolId:"text-extract-emails"},{toolId:"text-deduplicate"}]).ok).toBe(true);
    expect(validateToolPipeline({mimeType:"application/json",fileName:"data.json"},[{toolId:"json-minify"},{toolId:"json-format"}]).ok).toBe(true);
    expect(validateToolPipeline(textFile,[{toolId:"text-slugify"},{toolId:"text-clean"}]).ok).toBe(true);
    expect(validateToolPipeline({mimeType:"application/json",fileName:"records.json"},[{toolId:"json-to-jsonl"},{toolId:"jsonl-format"}]).ok).toBe(true);
    expect(validateToolPipeline({mimeType:"text/csv",fileName:"rows.csv"},[{toolId:"csv-to-tsv"},{toolId:"tsv-to-csv"},{toolId:"csv-profile"}]).ok).toBe(true);
    expect(isToolCompatible(getTool("xml-minify")!,"application/xml","feed.xml")).toBe(true);
    expect(validateToolPipeline(textFile,[{toolId:"text-sentence-case"},{toolId:"text-clean"}]).ok).toBe(true);
    expect(validateToolPipeline(textFile,[{toolId:"text-markdown-toc"},{toolId:"text-stats"}]).ok).toBe(true);
    expect(validateToolPipeline({mimeType:"text/csv",fileName:"table.csv"},[{toolId:"csv-schema-infer"},{toolId:"csv-profile"}]).ok).toBe(true);
    expect(validateToolPipeline({mimeType:"application/json",fileName:"array.json"},[{toolId:"json-canonicalize"},{toolId:"json-format"}]).ok).toBe(true);

    expect(validateToolPipeline(textFile,[{toolId:"text-collapse-whitespace"},{toolId:"text-clean"}]).ok).toBe(true);
    expect(validateToolPipeline({mimeType:"text/csv",fileName:"rows.csv"},[{toolId:"csv-transpose"},{toolId:"csv-profile"}]).ok).toBe(true);
    expect(validateToolPipeline({mimeType:"application/json",fileName:"rows.json"},[{toolId:"json-remove-nulls"},{toolId:"json-format"}]).ok).toBe(true);
    expect(isToolCompatible(getTool("json-to-html-table")!,"application/json","rows.json")).toBe(true);
    expect(validateToolPipeline(textFile,[{toolId:"text-html-escape"},{toolId:"text-html-unescape"}]).ok).toBe(true);
    expect(validateToolPipeline({mimeType:"text/csv",fileName:"rows.csv"},[{toolId:"csv-to-html"},{toolId:"html-minify"}]).ok).toBe(true);
    expect(validateToolPipeline({mimeType:"application/json",fileName:"rows.json"},[{toolId:"json-sort-array"},{toolId:"json-format"}]).ok).toBe(true);
    expect(isToolCompatible(getTool("language-detect")!,"text/plain","notes.log")).toBe(true);
    expect(validateToolPipeline(textFile,[{toolId:"text-pascal-case"},{toolId:"text-clean"}]).ok).toBe(true);
    expect(validateToolPipeline({mimeType:"application/json",fileName:"nested.json"},[{toolId:"json-flatten"},{toolId:"json-unflatten"}]).ok).toBe(true);
    expect(validateToolPipeline({mimeType:"text/csv",fileName:"rows.csv"},[{toolId:"csv-normalize-headers"},{toolId:"csv-to-jsonl"},{toolId:"jsonl-to-csv"}]).ok).toBe(true);
    expect(isToolCompatible(getTool("jsonl-to-csv")!,"application/x-ndjson","records.jsonl")).toBe(true);
    expect(validateToolPipeline({mimeType:"text/markdown",fileName:"README.md"},[{toolId:"text-extract-markdown-images"},{toolId:"html-extract-images"}]).ok).toBe(true);
    expect(validateToolPipeline({mimeType:"text/plain",fileName:"source.log"},[{toolId:"text-redact-secrets"},{toolId:"text-clean"}]).ok).toBe(true);
    expect(validateToolPipeline({mimeType:"application/json",fileName:"array.json"},[{toolId:"json-array-dedupe"},{toolId:"json-canonicalize"}]).ok).toBe(true);
    expect(validateToolPipeline({mimeType:"text/csv",fileName:"missing.csv"},[{toolId:"csv-empty-cell-report"},{toolId:"csv-profile"}]).ok).toBe(true);
    expect(validateToolPipeline({mimeType:"text/csv",fileName:"data.csv"},[{toolId:"csv-trim-cells"},{toolId:"csv-schema-infer"}]).ok).toBe(true);
    expect(validateToolPipeline(textFile,[{toolId:"text-indent-lines"},{toolId:"text-unindent-lines"}]).ok).toBe(true);
    expect(validateToolPipeline({mimeType:"text/html",fileName:"page.html"},[{toolId:"html-extract-title"}]).ok).toBe(true);
    expect(isToolCompatible(getTool("html-extract-links")!,"text/html","page.html")).toBe(true);
    expect(validateToolPipeline({mimeType:"application/xml",fileName:"tree.xml"},[{toolId:"xml-tree-report"}]).ok).toBe(true);
    expect(isToolCompatible(getTool("xml-to-json")!,"application/xml","tree.xml")).toBe(true);
    expect(validateToolPipeline(textFile,[{toolId:"json-escape-string"},{toolId:"json-unescape-string"}]).ok).toBe(true);
    expect(isToolCompatible(getTool("csv-unique-values")!,"text/csv","values.csv")).toBe(true);

  });


  it("validates common fourth-wave text, JSON Pointer and CSV/JSONL pipelines", () => {
    const textFile={mimeType:"text/plain",fileName:"notes.txt"};
    const jsonFile={mimeType:"application/json",fileName:"nested.json"};
    const csvFile={mimeType:"text/csv",fileName:"rows.csv"};
    const jsonlFile={mimeType:"application/x-ndjson",fileName:"records.jsonl"};
    expect(validateToolPipeline(textFile,[{toolId:"text-pascal-case"},{toolId:"text-clean"}]).ok).toBe(true);
    expect(validateToolPipeline(jsonFile,[{toolId:"json-flatten"},{toolId:"json-unflatten"}]).ok).toBe(true);
    expect(validateToolPipeline(csvFile,[{toolId:"csv-normalize-headers"},{toolId:"csv-to-jsonl"},{toolId:"jsonl-to-csv"}]).ok).toBe(true);
    expect(isToolCompatible(getTool("jsonl-to-csv")!,jsonlFile.mimeType,jsonlFile.fileName)).toBe(true);
  });



  it("registers and validates the fourteen Wave 7 processors", () => {
    const ids=[
      "text-extract-mac-addresses","text-extract-port-numbers","text-normalize-path-separators",
      "text-extract-file-extensions","text-escape-shell-argument","text-sort-unique-lines",
      "text-normalize-unicode-nfkc","csv-to-sql-inserts","csv-to-yaml","csv-empty-row-report",
      "csv-row-width-report","json-remove-empty-values","json-to-typescript","json-nesting-report",
    ];
    expect(TOOL_CATALOG).toHaveLength(462);
    for(const id of ids)expect(getTool(id)?.ready).toBe(true);
    expect(validateToolPipeline({mimeType:"text/plain",fileName:"macs.txt"},[{toolId:"text-extract-mac-addresses"},{toolId:"text-deduplicate"}]).ok).toBe(true);
    expect(validateToolPipeline({mimeType:"text/csv",fileName:"rows.csv"},[{toolId:"csv-to-yaml"},{toolId:"yaml-format"},{toolId:"yaml-to-json"}]).ok).toBe(true);
    expect(validateToolPipeline({mimeType:"text/csv",fileName:"rows.csv"},[{toolId:"csv-to-sql-inserts"}]).ok).toBe(true);
    expect(validateToolPipeline({mimeType:"application/json",fileName:"sample.json"},[{toolId:"json-to-typescript"},{toolId:"code-check"}]).ok).toBe(true);
  });



  it("registers all fourteen Wave 8 configuration and DevOps processors", () => {
    const ids=[
      "env-audit","env-redact","env-to-example","ini-to-json","ini-validate","toml-to-json","toml-validate",
      "properties-to-json","dockerfile-audit","docker-compose-audit","requirements-audit","package-json-audit",
      "gitignore-audit","env-reference-report",
    ];
    for(const id of ids)expect(getTool(id)?.ready).toBe(true);
    expect(inferToolForUpload({mimeType:"text/plain",fileName:".env.production"})).toBe("env-audit");
    expect(inferToolForUpload({mimeType:"application/json",fileName:"package.json"})).toBe("package-json-audit");
    expect(inferToolForUpload({mimeType:"text/plain",fileName:"Dockerfile"})).toBe("dockerfile-audit");
    expect(inferToolForUpload({mimeType:"application/yaml",fileName:"compose.yaml"})).toBe("docker-compose-audit");
    expect(validateToolPipeline({mimeType:"text/plain",fileName:".env"},[{toolId:"env-audit"},{toolId:"env-to-example"}]).ok).toBe(true);
    expect(validateToolPipeline({mimeType:"text/plain",fileName:"settings.ini"},[{toolId:"ini-to-json"},{toolId:"json-format"}]).ok).toBe(true);
    expect(validateToolPipeline({mimeType:"application/json",fileName:"package.json"},[{toolId:"package-json-audit"}]).ok).toBe(true);
  });



  it("registers and infers the eight Wave 9 infrastructure and CI/CD auditors", () => {
    const ids=["github-actions-audit","kubernetes-manifest-audit","terraform-audit","nginx-config-audit","apache-config-audit","caddy-config-audit","systemd-unit-audit","shell-script-audit"];
    expect(TOOL_CATALOG).toHaveLength(462);
    for(const id of ids)expect(getTool(id)?.ready).toBe(true);
    expect(inferToolForUpload({mimeType:"text/plain",fileName:"main.tf"})).toBe("terraform-audit");
    expect(inferToolForUpload({mimeType:"text/plain",fileName:"nginx.conf"})).toBe("nginx-config-audit");
    expect(inferToolForUpload({mimeType:"text/plain",fileName:"apache2.conf"})).toBe("apache-config-audit");
    expect(inferToolForUpload({mimeType:"text/plain",fileName:"Caddyfile"})).toBe("caddy-config-audit");
    expect(inferToolForUpload({mimeType:"text/plain",fileName:"service.service"})).toBe("systemd-unit-audit");
    expect(inferToolForUpload({mimeType:"text/plain",fileName:"deploy.sh"})).toBe("shell-script-audit");
    expect(inferToolForUpload({mimeType:"application/yaml",fileName:"ci.yml"})).toBe("github-actions-audit");
    expect(inferToolForUpload({mimeType:"application/yaml",fileName:"deployment.yaml"})).toBe("kubernetes-manifest-audit");
    expect(validateToolPipeline({mimeType:"text/plain",fileName:"main.tf"},[{toolId:"terraform-audit"},{toolId:"text-clean"}]).ok).toBe(true);
    expect(validateToolPipeline({mimeType:"text/plain",fileName:"nginx.conf"},[{toolId:"nginx-config-audit"},{toolId:"text-stats"}]).ok).toBe(true);
  });


  it("registers the eight Wave 10 repository engineering intelligence processors", () => {
    const ids=["repo-test-map","repo-test-quality","repo-complexity-report","repo-api-surface","repo-docs-audit","repo-migration-audit","repo-runtime-risk","repo-i18n-audit"];
    for (const id of ids) {
      expect(getTool(id)?.category).toBe("repository");
      expect(getTool(id)?.ready).toBe(true);
      expect(isToolCompatible(getTool(id)!, "application/zip", id + ".zip")).toBe(true);
    }
    expect(validateToolPipeline({mimeType:"application/zip",fileName:"repo.zip"}, [
      {toolId:"repo-test-map"},{toolId:"text-stats"},
    ]).ok).toBe(true);
    expect(validateToolPipeline({mimeType:"application/zip",fileName:"repo.zip"}, [
      {toolId:"repo-runtime-risk"},{toolId:"text-clean"},
    ]).ok).toBe(true);
  });


  it("registers the six Wave 11 repository engineering analyzers", () => {
    const ids=["repo-env-contract","repo-architecture-cycles","repo-change-impact","repo-api-spec-audit","repo-container-audit","repo-ci-reliability"];
    for (const id of ids) {
      expect(getTool(id)?.category).toBe("repository");
      expect(getTool(id)?.ready).toBe(true);
      expect(isToolCompatible(getTool(id)!, "application/zip", id + ".zip")).toBe(true);
    }
    expect(validateToolPipeline({mimeType:"application/zip",fileName:"repo.zip"}, [
      {toolId:"repo-env-contract"},{toolId:"text-clean"},
    ]).ok).toBe(true);
  });


  it("registers the five Wave 12 static HTML quality auditors", () => {
    const ids=["html-seo-audit","html-accessibility-audit","html-link-audit","html-form-audit","html-image-audit"];
    for (const id of ids) {
      expect(getTool(id)?.category).toBe("developer");
      expect(getTool(id)?.ready).toBe(true);
      expect(isToolCompatible(getTool(id)!, "text/html", "page.html")).toBe(true);
      expect(validateToolPipeline({mimeType:"text/html",fileName:"page.html"}, [
        {toolId:id},{toolId:"text-clean"},
      ]).ok).toBe(true);
    }
  });

  it("registers six Wave 13 productivity tools with compatible outputs", () => {
    const cases=[
      ["xlsx-formula-report","data","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet","book.xlsx"],
      ["xlsx-to-markdown","data","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet","book.xlsx"],
      ["subtitle-audit","audio-video","text/vtt","captions.vtt"],
      ["image-favicon","image","image/png","logo.png"],
      ["pdf-page-audit","document","application/pdf","report.pdf"],
      ["markdown-toc","developer","text/markdown","guide.md"],
    ] as const;
    for (const [id,category,mimeType,fileName] of cases) {
      expect(getTool(id)?.category).toBe(category);
      expect(getTool(id)?.ready).toBe(true);
      expect(isToolCompatible(getTool(id)!,mimeType,fileName)).toBe(true);
      expect(validateToolPipeline({mimeType,fileName},[{toolId:id},{toolId:id==="xlsx-to-markdown"||id==="markdown-toc"?"markdown-outline":id==="image-favicon"?"file-hash":"text-clean"}]).ok).toBe(true);
    }
  });


  it("registers four Wave 14 file-quality and privacy auditors", () => {
    const cases=[
      ["docx-audit","document","application/vnd.openxmlformats-officedocument.wordprocessingml.document","report.docx"],
      ["pptx-audit","document","application/vnd.openxmlformats-officedocument.presentationml.presentation","slides.pptx"],
      ["csv-privacy-audit","data","text/csv","contacts.csv"],
      ["archive-security-audit","utility","application/zip","bundle.zip"],
    ] as const;
    for (const [id,category,mimeType,fileName] of cases) {
      expect(getTool(id)?.category).toBe(category);
      expect(getTool(id)?.ready).toBe(true);
      expect(isToolCompatible(getTool(id)!,mimeType,fileName)).toBe(true);
      expect(validateToolPipeline({mimeType,fileName},[{toolId:id},{toolId:"text-clean"}]).ok).toBe(true);
    }
  });


  it("registers Wave 15 spreadsheet and PDF privacy auditors", () => {
    const cases=[
      ["xlsx-privacy-audit","data","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet","private.xlsx"],
      ["pdf-privacy-audit","document","application/pdf","private.pdf"],
    ] as const;
    for (const [id,category,mimeType,fileName] of cases) {
      expect(getTool(id)?.category).toBe(category);
      expect(getTool(id)?.ready).toBe(true);
      expect(isToolCompatible(getTool(id)!,mimeType,fileName)).toBe(true);
      expect(validateToolPipeline({mimeType,fileName},[{toolId:id},{toolId:"text-clean"}]).ok).toBe(true);
    }
  });


  it("registers Wave 16 Office and PDF active-content auditors", () => {
    const cases=[
      ["office-active-content-audit","document","application/vnd.openxmlformats-officedocument.wordprocessingml.document","report.docx"],
      ["office-active-content-audit","document","application/vnd.ms-excel.sheet.macroEnabled.12","book.xlsm"],
      ["pdf-active-content-audit","document","application/pdf","report.pdf"],
    ] as const;
    for (const [id,category,mimeType,fileName] of cases) {
      expect(getTool(id)?.category).toBe(category);
      expect(getTool(id)?.ready).toBe(true);
      expect(isToolCompatible(getTool(id)!,mimeType,fileName)).toBe(true);
      expect(validateToolPipeline({mimeType,fileName},[{toolId:id},{toolId:"text-clean"}]).ok).toBe(true);
    }
  });


  it("registers nine Wave 20 creator and content utilities", () => {
    const cases=[
      ["rss-atom-audit","data","application/rss+xml","feed.rss"],
      ["sitemap-xml-audit","developer","application/xml","sitemap.xml"],
      ["robots-txt-audit","developer","text/plain","robots.txt"],
      ["jsonl-profile","data","application/x-ndjson","records.jsonl"],
      ["image-privacy-audit","image","image/jpeg","photo.jpg"],
      ["svg-safety-audit","image","image/svg+xml","logo.svg"],
      ["wcag-contrast-audit","utility","text/plain","colors.txt"],
      ["ssh-public-key-audit","developer","text/plain","authorized_keys"],
      ["archive-checksum-manifest","utility","application/zip","bundle.zip","csv-profile"],
    ] as const;
    for (const [id,category,mimeType,fileName,nextToolId] of cases) {
      expect(getTool(id)?.category).toBe(category);
      expect(getTool(id)?.ready).toBe(true);
      expect(isToolCompatible(getTool(id)!,mimeType,fileName)).toBe(true);
      if(nextToolId) expect(validateToolPipeline({mimeType,fileName},[{toolId:id},{toolId:nextToolId}]).ok).toBe(true);
      else expect(validateToolPipeline({mimeType,fileName},[{toolId:id},{toolId:"text-clean"}]).ok).toBe(true);
    }
  });

  it("registers eight Wave 19 network, media, document and data tools", () => {
    const cases=[
      ["pcap-network-audit","developer","application/vnd.tcpdump.pcap","capture.pcap","text-clean"],
      ["audio-tag-audit","audio-video","audio/mpeg","song.mp3","text-clean"],
      ["image-similarity-audit","image","application/zip","images.zip","csv-profile"],
      ["json-schema-validate","data","application/json","validation.json","text-clean"],
      ["epub-structure-audit","document","application/epub+zip","book.epub","text-clean"],
      ["markdown-quality-audit","developer","text/markdown","guide.md","text-clean"],
      ["dns-zone-audit","developer","text/plain","example.zone","text-clean"],
      ["x509-certificate-audit","developer","application/pkix-cert","certificate.pem","text-clean"],
    ] as const;
    for (const [id,category,mimeType,fileName,nextToolId] of cases) {
      expect(getTool(id)?.category).toBe(category);
      expect(getTool(id)?.ready).toBe(true);
      expect(isToolCompatible(getTool(id)!,mimeType,fileName)).toBe(true);
      expect(validateToolPipeline({mimeType,fileName},[{toolId:id},{toolId:nextToolId}]).ok).toBe(true);
    }
  });

  it("registers ten Wave 18 cross-domain tools and validates their pipelines", () => {
    const cases=[
      ["har-privacy-audit","developer","application/json","capture.har"],
      ["ics-calendar-audit","utility","text/calendar","calendar.ics"],
      ["vcard-privacy-audit","utility","text/vcard","contacts.vcf"],
      ["gpx-track-report","data","application/gpx+xml","route.gpx"],
      ["geojson-audit","data","application/geo+json","map.geojson"],
      ["qr-code-generate","image","text/plain","payload.txt","image-info"],
      ["font-inspect","developer","font/ttf","typeface.ttf"],
      ["subtitle-fix","audio-video","text/vtt","captions.vtt","subtitle-audit"],
      ["openapi-contract-audit","developer","application/yaml","openapi.yaml"],
      ["color-convert","utility","text/plain","palette.txt"],
    ] as const;
    for (const [id,category,mimeType,fileName,nextToolId] of cases) {
      expect(getTool(id)?.category).toBe(category);
      expect(getTool(id)?.ready).toBe(true);
      expect(isToolCompatible(getTool(id)!,mimeType,fileName)).toBe(true);
      expect(validateToolPipeline({mimeType,fileName},[{toolId:id},{toolId:nextToolId || "text-clean"}]).ok).toBe(true);
    }
  });

  it("registers Wave 17 email and JWT security auditors", () => {
    const cases=[
      ["email-security-audit","document","message/rfc822","message.eml"],
      ["jwt-security-audit","developer","text/plain","tokens.jwt"],
      ["jwt-security-audit","developer","application/json","tokens.json"],
    ] as const;
    for (const [id,category,mimeType,fileName] of cases) {
      expect(getTool(id)?.category).toBe(category);
      expect(getTool(id)?.ready).toBe(true);
      expect(isToolCompatible(getTool(id)!,mimeType,fileName)).toBe(true);
      expect(validateToolPipeline({mimeType,fileName},[{toolId:id},{toolId:"text-clean"}]).ok).toBe(true);
    }
  });


  it("infers Wave 23 domain-specific file types before generic text handlers", () => {
    expect(inferToolForUpload({ fileName: "part.gcode" })).toBe("gcode-audit");
    expect(inferToolForUpload({ fileName: "song.mid" })).toBe("midi-audit");
    expect(inferToolForUpload({ fileName: "score.musicxml" })).toBe("musicxml-audit");
    expect(inferToolForUpload({ fileName: "references.bib" })).toBe("bibtex-audit");
    expect(inferToolForUpload({ fileName: "track.nmea" })).toBe("nmea-track-audit");
    expect(inferToolForUpload({ fileName: "site.yml" })).toBe("ansible-playbook-audit");
    expect(inferToolForUpload({ fileName: "alerts.rules.yml" })).toBe("prometheus-rules-audit");
    expect(inferToolForUpload({ fileName: "grafana-dashboard.json" })).toBe("grafana-dashboard-audit");
    expect(inferToolForUpload({ fileName: "samples.h5" })).toBe("hdf5-audit");
    expect(inferToolForUpload({ fileName: "events.avsc" })).toBe("avro-schema-audit");
    expect(inferToolForUpload({ fileName: "schema.graphql" })).toBe("graphql-schema-audit");
    expect(inferToolForUpload({ fileName: "events.proto" })).toBe("protobuf-schema-audit");
  });

  it("infers Wave 24 interoperability and creative project formats", () => {
    expect(inferToolForUpload({ fileName: "document.odt" })).toBe("odf-package-audit");
    expect(inferToolForUpload({ fileName: "translation.xliff" })).toBe("xliff-audit");
    expect(inferToolForUpload({ fileName: "archive.mbox" })).toBe("mbox-audit");
    expect(inferToolForUpload({ fileName: "map.gpkg" })).toBe("geopackage-audit");
    expect(inferToolForUpload({ fileName: "tiles.mbtiles" })).toBe("mbtiles-audit");
    expect(inferToolForUpload({ fileName: "art.ora" })).toBe("openraster-audit");
    expect(inferToolForUpload({ fileName: "painting.kra" })).toBe("krita-project-audit");
    expect(inferToolForUpload({ fileName: "scene.glb" })).toBe("gltf-audit");
    expect(inferToolForUpload({ fileName: "architecture.drawio" })).toBe("drawio-audit");
    expect(inferToolForUpload({ fileName: "automation.n8n.json" })).toBe("n8n-workflow-audit");
    expect(inferToolForUpload({ fileName: "workflow.json" })).toBe("n8n-workflow-audit");
    expect(inferToolForUpload({ fileName: "brand.tokens.json" })).toBe("design-token-audit");
    expect(inferToolForUpload({ fileName: "crawl.warc.gz" })).toBe("warc-archive-audit");
  });

  it("infers Wave 25 build, observability, binary and engineering files", () => {
    expect(inferToolForUpload({ fileName: "module.wasm" })).toBe("wasm-module-audit");
    expect(inferToolForUpload({ fileName: "results.sarif" })).toBe("sarif-report-audit");
    expect(inferToolForUpload({ fileName: "bom.cdx.json" })).toBe("sbom-audit");
    expect(inferToolForUpload({ fileName: "junit-report.xml" })).toBe("junit-xml-audit");
    expect(inferToolForUpload({ fileName: "coverage.xml" })).toBe("coverage-xml-audit");
    expect(inferToolForUpload({ fileName: "observation.fits" })).toBe("fits-audit");
    expect(inferToolForUpload({ fileName: "model.step" })).toBe("step-cad-audit");
    expect(inferToolForUpload({ fileName: "otel-collector.yaml" })).toBe("otel-collector-audit");
    expect(inferToolForUpload({ fileName: "project.godot" })).toBe("godot-project-audit");
    expect(inferToolForUpload({ fileName: "sample.unitypackage" })).toBe("unity-package-audit");
    expect(inferToolForUpload({ fileName: "game.uproject" })).toBe("unreal-project-audit");
  });

  it("infers Wave 26 bioinformatics formats without stealing vCard .vcf files", () => {
    expect(inferToolForUpload({ fileName: "assembly.fasta" })).toBe("fasta-sequence-audit");
    expect(inferToolForUpload({ fileName: "reads.fastq.gz" })).toBe("fastq-quality-audit");
    expect(inferToolForUpload({ fileName: "calls.vcf.gz" })).toBe("vcf-variant-audit");
    expect(inferToolForUpload({ fileName: "alignment.sam" })).toBe("sam-alignment-audit");
    expect(inferToolForUpload({ fileName: "genes.gff3" })).toBe("gff3-annotation-audit");
    expect(inferToolForUpload({ fileName: "regions.bed" })).toBe("bed-interval-audit");
    expect(inferToolForUpload({ fileName: "records.gbk" })).toBe("genbank-record-audit");
    expect(inferToolForUpload({ fileName: "protein.pdb" })).toBe("pdb-structure-audit");
    expect(inferToolForUpload({ fileName: "assembly.gfa1" })).toBe("gfa-assembly-audit");
    expect(inferToolForUpload({ fileName: "tree.nwk" })).toBe("newick-tree-audit");
    expect(inferToolForUpload({ fileName: "alignment.sto" })).toBe("sequence-alignment-audit");
    expect(inferToolForUpload({ fileName: "contact.vcf", mimeType: "text/vcard" })).toBe("vcard-privacy-audit");
  });

  it("handles compressed bioinformatics text formats and disambiguates genomic VCF from vCard", () => {
    expect(inferToolForUpload({ fileName: "genome.fna.gz" })).toBe("fasta-sequence-audit");
    expect(inferToolForUpload({ fileName: "records.gbff.gz" })).toBe("genbank-record-audit");
    expect(inferToolForUpload({ fileName: "protein.pdb.gz" })).toBe("pdb-structure-audit");
    expect(inferToolForUpload({ fileName: "tree.nwk.gz" })).toBe("newick-tree-audit");
    expect(inferToolForUpload({ fileName: "alignment.sto.gz" })).toBe("sequence-alignment-audit");
    expect(inferToolForUpload({ fileName: "variants.vcf", mimeType: "text/x-vcf" })).toBe("vcf-variant-audit");
    expect(inferToolForUpload({ fileName: "contact.vcf", mimeType: "text/vcard" })).toBe("vcard-privacy-audit");
  });

  it("uses PRONOM signature identification as the fallback for unknown uploads", () => {
    expect(inferToolForUpload({ mimeType: "application/octet-stream", fileName: "opaque.bin" })).toBe("file-format-identify");
    expect(inferToolForUpload({ mimeType: "application/octet-stream", fileName: "unknown.data" })).toBe("file-format-identify");
    expect(isToolCompatible(getTool("file-format-identify")!, "application/pdf", "document.pdf")).toBe(true);
    expect(isToolCompatible(getTool("file-format-identify")!, "application/octet-stream", "blob.unknown")).toBe(true);
    expect(inferToolForUpload({ mimeType: "application/pdf", fileName: "document.pdf" })).toBe("pdf-text");
  });

  it("infers Wave 30 bioimaging, Parquet metadata and COG GeoTIFF files", () => {
    expect(inferToolForUpload({ fileName: "experiment.ome.zarr.zip" })).toBe("ome-ngff-audit");
    expect(inferToolForUpload({ fileName: "warehouse.parquet" })).toBe("parquet-metadata-audit");
    expect(inferToolForUpload({ fileName: "orthophoto.cog.tif" })).toBe("cog-geotiff-audit");
    expect(inferToolForUpload({ fileName: "generic.tif" })).not.toBe("cog-geotiff-audit");
    expect(inferToolForUpload({ fileName: "manifest.json" })).not.toBe("ome-ngff-audit");
  });

  it("infers Wave 28 scientific, medical, imaging and spatial formats", () => {
    expect(inferToolForUpload({ fileName: "object.ocfl.zip" })).toBe("ocfl-object-audit");
    expect(inferToolForUpload({ fileName: "study.zarr.zip" })).toBe("zarr-store-audit");
    expect(inferToolForUpload({ fileName: "scan.nii" })).toBe("nifti-header-audit");
    expect(inferToolForUpload({ fileName: "scan.nii.gz" })).toBe("nifti-header-audit");
    expect(inferToolForUpload({ fileName: "image.dcm" })).toBe("dicom-privacy-audit");
    expect(inferToolForUpload({ fileName: "cloud.las" })).toBe("las-pointcloud-audit");
    expect(inferToolForUpload({ fileName: "image.jp2" })).toBe("jp2-box-audit");
    expect(inferToolForUpload({ fileName: "model.nc" })).toBe("netcdf-classic-audit");
    expect(inferToolForUpload({ fileName: "experiment.nwb" })).toBe("nwb-structure-audit");
    expect(inferToolForUpload({ fileName: "manifest.json" })).not.toBe("ocfl-object-audit");
  });

  it("infers Wave 27 preservation and research-data descriptor formats", () => {
    expect(inferToolForUpload({ fileName: "archive.bag.zip" })).toBe("bagit-archive-audit");
    expect(inferToolForUpload({ fileName: "datapackage.json" })).toBe("frictionless-package-audit");
    expect(inferToolForUpload({ fileName: "ro-crate-metadata.json" })).toBe("ro-crate-audit");
    expect(inferToolForUpload({ fileName: "iiif-manifest.json" })).toBe("iiif-manifest-audit");
    expect(inferToolForUpload({ fileName: "dataset.datacite.xml" })).toBe("datacite-metadata-audit");
    expect(inferToolForUpload({ fileName: "archive.mets.xml" })).toBe("mets-package-audit");
    expect(inferToolForUpload({ fileName: "archive.premis.xml" })).toBe("premis-event-audit");
    expect(inferToolForUpload({ fileName: "stac-item.json" })).toBe("stac-catalog-audit");
    expect(inferToolForUpload({ fileName: "edition.tei.xml" })).toBe("tei-document-audit");
    expect(inferToolForUpload({ fileName: "package.json" })).toBe("package-json-audit");
    expect(inferToolForUpload({ fileName: "manifest.json" })).not.toBe("iiif-manifest-audit");
  });
  it("registers Wave 35 AI model, fine-tuning and 3MF processors", () => {
    const ids = [
      "safetensors-audit",
      "gguf-model-audit",
      "hf-model-card-audit",
      "chat-dataset-audit",
      "promptfoo-config-audit",
      "three-mf-package-audit",
    ];
    expect(TOOL_CATALOG).toHaveLength(462);
    for (const id of ids) expect(getTool(id)?.ready).toBe(true);
    expect(inferToolForUpload({ fileName: "weights.safetensors" })).toBe("safetensors-audit");
    expect(inferToolForUpload({ fileName: "local-model.gguf" })).toBe("gguf-model-audit");
    expect(inferToolForUpload({ fileName: "training.jsonl" })).toBe("chat-dataset-audit");
    expect(inferToolForUpload({ fileName: "promptfooconfig.yaml" })).toBe("promptfoo-config-audit");
    expect(inferToolForUpload({ fileName: "sample.3mf" })).toBe("three-mf-package-audit");
    expect(inferToolForUpload({ fileName: "model-card.md" })).toBe("hf-model-card-audit");
    expect(validateToolPipeline(
      { mimeType: "application/octet-stream", fileName: "weights.safetensors" },
      [{ toolId: "safetensors-audit" }, { toolId: "text-clean" }]
    ).ok).toBe(true);
  });


  it("registers Wave 36 Ollama, Hugging Face, MLflow, DVC and Helm tools", () => {
    const ids = [
      "ollama-modelfile-audit",
      "hf-tokenizer-audit",
      "hf-dataset-card-audit",
      "mlflow-model-audit",
      "dvc-pipeline-audit",
      "helm-chart-audit",
    ];
    expect(TOOL_CATALOG).toHaveLength(462);
    for (const id of ids) expect(getTool(id)?.ready).toBe(true);
    expect(inferToolForUpload({ fileName: "Modelfile" })).toBe("ollama-modelfile-audit");
    expect(inferToolForUpload({ fileName: "tokenizer.json" })).toBe("hf-tokenizer-audit");
    expect(inferToolForUpload({ fileName: "dataset-card.md" })).toBe("hf-dataset-card-audit");
    expect(inferToolForUpload({ fileName: "MLmodel" })).toBe("mlflow-model-audit");
    expect(inferToolForUpload({ fileName: "dvc.yaml" })).toBe("dvc-pipeline-audit");
    expect(inferToolForUpload({ fileName: "dvc.lock" })).toBe("dvc-pipeline-audit");
    expect(inferToolForUpload({ fileName: "Chart.yaml" })).toBe("helm-chart-audit");
    expect(validateToolPipeline(
      { mimeType: "text/yaml", fileName: "Chart.yaml" },
      [{ toolId: "helm-chart-audit" }, { toolId: "text-clean" }]
    ).ok).toBe(true);
  });

});
