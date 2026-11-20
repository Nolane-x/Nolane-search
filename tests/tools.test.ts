import { describe, expect, it } from "vitest";
import { TOOL_CATALOG, getTool, inferToolForUpload, isToolCompatible, validateToolDag, validateToolDagDefinition, validateToolPipeline, validateToolPipelineDefinition } from "../src/tools";

describe("Nolane Tools registry", () => {
  it("contains uniquely identified, documented tools", () => {
    const ids = TOOL_CATALOG.map(tool => tool.id);
    expect(new Set(ids).size).toBe(ids.length);
    expect(TOOL_CATALOG.length).toBeGreaterThanOrEqual(102);
    expect(TOOL_CATALOG.every(tool => tool.ready && tool.description.length > 12 && tool.accepts.length > 0)).toBe(true);
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

});
