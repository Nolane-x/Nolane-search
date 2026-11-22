import { describe, expect, it } from "vitest";
import { TOOL_CATALOG, getTool, inferToolForUpload, isToolCompatible, validateToolDag, validateToolDagDefinition, validateToolPipeline, validateToolPipelineDefinition } from "../src/tools";

describe("Nolane Tools registry", () => {
  it("contains uniquely identified, documented tools", () => {
    const ids = TOOL_CATALOG.map(tool => tool.id);
    expect(new Set(ids).size).toBe(ids.length);
    expect(TOOL_CATALOG).toHaveLength(308);
    expect(TOOL_CATALOG.every(tool => tool.ready && tool.description.length > 12 && tool.accepts.length > 0)).toBe(true);
    for (const id of ["text-extract-todo-comments", "text-extract-markdown-images", "text-strip-markdown-frontmatter", "text-markdown-to-plain", "text-sort-unique-words", "text-word-to-lines", "text-join-lines", "text-extract-domains", "text-extract-uuids", "text-extract-semver", "text-extract-ipv6", "text-redact-secrets", "text-extract-comment-lines", "text-tabs-to-spaces", "text-escape-regex", "text-unescape-regex", "json-merge-objects", "json-array-dedupe", "json-array-to-lines", "csv-trim-cells", "csv-remove-empty-columns", "csv-empty-cell-report"]) expect(getTool(id)?.ready).toBe(true);
    for (const id of ["text-translate","language-detect","text-uppercase","text-lowercase","text-title-case","text-sort-lines","text-reverse-lines","text-number-lines","text-remove-blank-lines","text-wrap","text-trim-lines","text-extract-emails","text-extract-urls","text-extract-hashtags","text-to-base64","base64-to-text","url-encode","url-decode","json-minify","json-sort-keys","text-slugify","text-word-frequency","text-extract-numbers","text-extract-dates","text-reverse-characters","text-snake-case","text-kebab-case","text-camel-case","text-swap-case","text-extract-ipv4","text-mask-emails","text-mask-phones","json-to-jsonl","jsonl-to-json","csv-to-tsv","tsv-to-csv","csv-to-markdown","html-minify","xml-minify","text-remove-emoji","text-collapse-whitespace","text-remove-punctuation","text-to-ascii","text-html-escape","text-html-unescape","text-extract-mentions","text-extract-hex-colors","text-extract-phones","text-dedupe-lines","text-count-report","text-quote-lines","text-unquote-lines","csv-transpose","csv-sort-rows","csv-dedupe-rows","csv-to-xml","csv-to-html","json-sort-array","json-remove-nulls","json-to-html-table","text-pascal-case","text-constant-case","text-dot-case","text-initials","text-normalize-unicode","text-remove-control-chars","text-remove-duplicate-words","text-extract-markdown-links","text-extract-markdown-headings","text-extract-quotes","text-paragraph-report","json-flatten","json-unflatten","json-keys-report","csv-remove-empty-rows","csv-add-row-numbers","csv-column-stats","csv-normalize-headers","csv-to-jsonl","jsonl-to-csv","text-indent-lines","text-unindent-lines","text-dedupe-paragraphs","text-tokenize-words","text-sentence-report","text-line-length-report","text-normalize-newlines","text-remove-zero-width","text-extract-file-paths","text-sort-words","html-extract-links","html-extract-images","html-extract-title","html-sanitize","xml-tree-report","json-to-xml","json-type-report","json-escape-string","json-unescape-string","csv-unique-values","text-sentence-case","text-normalize-quotes","text-normalize-dashes","text-reverse-word-order","text-extract-words","text-extract-sentences","text-dedupe-sentences","text-remove-markdown-formatting","text-markdown-toc","text-markdown-code-blocks","text-markdown-table-extract","text-extract-numbered-lists","text-join-hyphenated-lines","text-strip-bom","text-normalize-paragraph-spacing","csv-schema-infer","csv-duplicates-report","csv-sample-rows","json-array-stats","json-canonicalize"]) expect(getTool(id)?.ready).toBe(true);
    for (const id of ["pdf-rotate-cw","pdf-remove-blank","image-trim-border","image-pixelate","image-diff","audio-stereo-split","audio-metadata-clean","video-scene-frames","video-metadata-clean","json-flatten-csv","csv-to-sqlite","log-insights","json-diff","text-join"]) expect(getTool(id)).not.toBeNull();
  });

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
    expect(TOOL_CATALOG).toHaveLength(308);
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
    expect(TOOL_CATALOG).toHaveLength(308);
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
      expect(validateToolPipeline({mimeType,fileName},[{toolId:id},{toolId:id==="xlsx-to-markdown"?"markdown-outline":"text-clean"}]).ok).toBe(true);
    }
  });

});
