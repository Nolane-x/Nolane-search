import { describe, expect, it } from "vitest";
import { TOOL_CATALOG, getTool, inferToolForUpload, isToolCompatible, validateToolPipeline, validateToolPipelineDefinition } from "../src/tools";

describe("Nolane Tools registry", () => {
  it("contains uniquely identified, documented tools", () => {
    const ids = TOOL_CATALOG.map(tool => tool.id);
    expect(new Set(ids).size).toBe(ids.length);
    expect(TOOL_CATALOG.length).toBeGreaterThanOrEqual(72);
    expect(TOOL_CATALOG.every(tool => tool.ready && tool.description.length > 12 && tool.accepts.length > 0)).toBe(true);
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
});
