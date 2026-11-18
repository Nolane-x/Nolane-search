import { describe, expect, it } from "vitest";
import { TOOL_CATALOG, getTool, inferToolForUpload, isToolCompatible } from "../src/tools";

describe("Nolane Tools registry", () => {
  it("contains uniquely identified, documented tools", () => {
    const ids = TOOL_CATALOG.map(tool => tool.id);
    expect(new Set(ids).size).toBe(ids.length);
    expect(TOOL_CATALOG.length).toBeGreaterThanOrEqual(15);
    expect(TOOL_CATALOG.every(tool => tool.ready && tool.description.length > 12 && tool.accepts.length > 0)).toBe(true);
  });

  it("infers a suitable default tool from common uploaded media", () => {
    expect(inferToolForUpload({}, true)).toBe("image-ocr");
    expect(inferToolForUpload({ mimeType: "image/jpeg", fileName: "photo.jpg" })).toBe("image-ocr");
    expect(inferToolForUpload({ mimeType: "application/octet-stream", fileName: "photo.png" })).toBe("image-ocr");
    expect(isToolCompatible(getTool("pdf-text")!, "application/octet-stream", "scan.pdf")).toBe(true);
    expect(inferToolForUpload({ mimeType: "application/pdf", fileName: "scan.pdf" })).toBe("pdf-text");
    expect(inferToolForUpload({ mimeType: "audio/mpeg", fileName: "voice.mp3" })).toBe("audio-transcribe");
    expect(inferToolForUpload({ mimeType: "video/mp4", fileName: "clip.mp4" })).toBe("video-info");
    expect(inferToolForUpload({ mimeType: "text/csv", fileName: "data.csv" })).toBe("csv-profile");
    expect(inferToolForUpload({ mimeType: "application/json", fileName: "data.json" })).toBe("json-format");
    expect(inferToolForUpload({ mimeType: "application/vnd.openxmlformats-officedocument.wordprocessingml.document", fileName: "notes.docx" })).toBe("office-text");
  });

  it("validates explicit tool selection against MIME types and extensions", () => {
    expect(isToolCompatible(getTool("image-ocr")!, "image/jpeg", "photo.jpg")).toBe(true);
    expect(isToolCompatible(getTool("image-ocr")!, "application/octet-stream", "photo.png")).toBe(true);
    expect(isToolCompatible(getTool("pdf-text")!, "application/pdf", "scan.pdf")).toBe(true);
    expect(isToolCompatible(getTool("pdf-info")!, "application/octet-stream", "scan.PDF")).toBe(true);
    expect(isToolCompatible(getTool("image-info")!, "application/octet-stream", "photo.webp")).toBe(true);
    expect(isToolCompatible(getTool("audio-info")!, "application/octet-stream", "recording.aac")).toBe(true);
    expect(isToolCompatible(getTool("video-thumbnail")!, "application/octet-stream", "movie.avi")).toBe(true);
    expect(isToolCompatible(getTool("pdf-text")!, "image/jpeg", "photo.jpg")).toBe(false);
    expect(isToolCompatible(getTool("office-text")!, "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "notes.docx")).toBe(true);
    expect(getTool("not-a-tool")).toBeNull();
  });
});
