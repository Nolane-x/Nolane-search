import { DurableObject, WorkerEntrypoint } from "cloudflare:workers";
import { parseJsonObjectBody } from "./http";
import { normalizeMediaDownloadUrl, parseMediaDownloadInput, hasOnlyPublicDnsAnswers } from "./media-downloader-policy";
import type { Env } from "./types";

const PORT = 8080;
const INSTANCE = "standard-1";
const MAX_OUTPUT_BYTES = 3 * 1024 * 1024 * 1024;
const SHARE_TTL_MS = 12 * 60 * 60 * 1000;
const CONTAINER_IDLE_MS = 6 * 60 * 60 * 1000;
const STATE_KEY = "media-downloader:current:v1";
const SECRET_KEY = "media-downloader:container-secret:v1";
const JOB_ID_RE = /^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i;
const HASH_RE = /^[a-f0-9]{64}$/i;

interface SnapshotHandle {
  id: string;
  size: number;
  name?: string;
}

interface DownloadState {
  jobId: string;
  status: "queued" | "running" | "complete" | "failed" | "cancelled" | "revoked";
  progress: number;
  format: "video" | "audio";
  quality: "best" | "1080" | "720" | "480";
  sourceHost: string;
  createdAt: number;
  updatedAt: number;
  fileName?: string;
  contentType?: string;
  size?: number;
  errorCode?: string;
  snapshot?: SnapshotHandle;
  shareTokenHash?: string;
  shareExpiresAt?: number;
}

interface ContainerJobResponse {
  id?: string;
  status?: string;
  progress?: number;
  fileName?: string;
  extension?: string;
  contentType?: string;
  size?: number;
  error?: string;
}

interface InternalStartBody {
  jobId: string;
  url: string;
  format: "video" | "audio";
  quality: "best" | "1080" | "720" | "480";
  shareTokenHash: string;
}

function isJobId(value: string): boolean {
  return JOB_ID_RE.test(value);
}

function randomHex(bytes = 32): string {
  const data = new Uint8Array(bytes);
  crypto.getRandomValues(data);
  return Array.from(data, byte => byte.toString(16).padStart(2, "0")).join("");
}

async function sha256Hex(value: string): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value));
  return Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2, "0")).join("");
}

function equalHex(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let difference = 0;
  for (let index = 0; index < a.length; index++) {
    difference |= a.charCodeAt(index) ^ b.charCodeAt(index);
  }
  return difference === 0;
}

function json(data: unknown, status = 200): Response {
  return Response.json(data, {
    status,
    headers: { "cache-control": "no-store", "x-content-type-options": "nosniff" },
  });
}

function errorMessage(code: string): string {
  switch (code) {
    case "timeout": return "Tác vụ vượt quá thời hạn xử lý.";
    case "container_stopped": return "Runner đã dừng trước khi hoàn tất. Hãy thử tạo tác vụ mới.";
    case "snapshot_failed": return "Không thể tạo bản lưu tạm để chia sẻ video.";
    case "too_large": return "Tệp vượt giới hạn dung lượng của Media Downloader.";
    default: return "Không thể tải media từ nguồn này. Hãy kiểm tra URL hoặc thử nguồn khác.";
  }
}

export class MediaDownloaderEgress extends WorkerEntrypoint<Env> {
  async fetch(request: Request): Promise<Response> {
    const method = request.method.toUpperCase();
    if (!["GET", "HEAD", "POST"].includes(method)) {
      return new Response("Method not allowed", { status: 405, headers: { allow: "GET, HEAD, POST" } });
    }

    const normalized = normalizeMediaDownloadUrl(request.url);
    if (!normalized.ok) return new Response("Blocked outbound URL", { status: 403 });

    try {
      const url = new URL(normalized.url);
      const publicDns = await hasOnlyPublicDnsAnswers(url.hostname);
      if (!publicDns) return new Response("Destination is not publicly routable", { status: 403 });

      const headers = new Headers(request.headers);
      for (const name of [
        "authorization", "cookie", "cookie2", "proxy-authorization", "proxy-authenticate",
        "x-nolane-internal", "x-nolane-share-token", "x-forwarded-for", "x-real-ip",
        "forwarded", "cf-connecting-ip", "cf-ipcountry", "host", "accept-encoding",
        "connection", "transfer-encoding", "upgrade",
      ]) headers.delete(name);

      let body: ArrayBuffer | undefined;
      if (method === "POST") {
        const declaredLength = Number(request.headers.get("content-length") || 0);
        if (!Number.isSafeInteger(declaredLength) || declaredLength < 0 || declaredLength > 1_000_000) {
          return new Response("Outbound POST body exceeds the allowed size", { status: 413 });
        }
        body = await request.arrayBuffer();
        if (body.byteLength > 1_000_000) return new Response("Outbound POST body exceeds the allowed size", { status: 413 });
      }

      const outbound = new Request(url.toString(), {
        method,
        headers,
        body: method === "POST" ? body : undefined,
        redirect: "manual",
        signal: AbortSignal.timeout(60_000),
      });
      // Redirects are deliberately manual. yt-dlp follows them by issuing a new
      // request, which passes through this policy and DNS validation again.
      return await fetch(outbound);
    } catch {
      return new Response("Outbound request failed or timed out", { status: 502 });
    }
  }
}

export class MediaDownloader extends DurableObject<Env> {
  private starting: Promise<void> | null = null;
  private monitoring: Promise<void> | null = null;

  constructor(ctx: DurableObjectState, env: Env) {
    super(ctx, env);
    // Container state is recoverable from the DO snapshot/state on the next
    // request. Do not hold blockConcurrencyWhile across container I/O.
    if (ctx.container?.running) {
      void ctx.container.setInactivityTimeout(CONTAINER_IDLE_MS)
        .then(() => this.observeExit())
        .catch(() => undefined);
    }
  }

  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);
    const parts = url.pathname.split("/").filter(Boolean);
    if (parts[0] !== "internal" || parts.length < 2) return new Response("Not found", { status: 404 });

    if (parts[1] === "start" && request.method === "POST") {
      const body = await parseJsonObjectBody(request, 8_000);
      if (!body) return json({ error: "Invalid request body." }, 400);
      try {
        const jobId = typeof body.jobId === "string" ? body.jobId : null;
        const sourceUrl = typeof body.url === "string" ? body.url : null;
        const format = body.format === "audio" || body.format === "video" ? body.format : null;
        const quality = body.quality === "best" || body.quality === "1080" || body.quality === "720" || body.quality === "480"
          ? body.quality : null;
        const shareTokenHash = typeof body.shareTokenHash === "string" ? body.shareTokenHash : null;
        if (!jobId || !sourceUrl || !format || !quality || !shareTokenHash) {
          return json({ error: "Invalid media job fields." }, 400);
        }
        const result = await this.startDownload({ jobId, url: sourceUrl, format, quality, shareTokenHash });
        return json(result, 202);
      } catch (error) {
        const message = error instanceof Error ? error.message : "Media download could not start.";
        const status = message.includes("already") ? 409 : message.includes("invalid") ? 400 : 503;
        return json({ error: message }, status);
      }
    }

    if (parts[1] === "status" && parts.length === 3 && request.method === "GET") {
      return this.getStatus(parts[2]);
    }

    if (parts[1] === "cancel" && parts.length === 3 && request.method === "POST") {
      return this.cancel(parts[2]);
    }

    if (parts[1] === "renew-share" && parts.length === 3 && request.method === "POST") {
      const body = await parseJsonObjectBody(request, 2_000);
      const tokenHash = typeof body?.tokenHash === "string" ? body.tokenHash : "";
      if (!HASH_RE.test(tokenHash)) return json({ error: "Invalid share token." }, 400);
      return this.renewShare(parts[2], tokenHash);
    }

    if (parts[1] === "share-info" && parts.length === 3 && request.method === "GET") {
      return this.shareInfo(parts[2], request.headers.get("x-nolane-share-token") || "");
    }

    if (parts[1] === "share-file" && parts.length === 3 && (request.method === "GET" || request.method === "HEAD")) {
      return this.serveSharedFile(parts[2], request);
    }

    if (parts[1] === "revoke" && parts.length === 3 && request.method === "DELETE") {
      return this.revoke(parts[2]);
    }

    return new Response("Not found", { status: 404 });
  }

  private async readState(): Promise<DownloadState | null> {
    return await this.ctx.storage.get<DownloadState>(STATE_KEY) ?? null;
  }

  private async writeState(state: DownloadState): Promise<void> {
    state.updatedAt = Date.now();
    await this.ctx.storage.put(STATE_KEY, state);
  }

  private async containerSecret(): Promise<string> {
    let secret = await this.ctx.storage.get<string>(SECRET_KEY);
    if (!secret) {
      secret = randomHex(32);
      await this.ctx.storage.put(SECRET_KEY, secret);
    }
    return secret;
  }

  private async ensureContainer(snapshot?: SnapshotHandle): Promise<void> {
    const container = this.ctx.container;
    if (!container) throw new Error("Media downloader container is not configured.");
    if (container.running) {
      await container.setInactivityTimeout(CONTAINER_IDLE_MS);
      this.observeExit();
      return;
    }

    this.starting ??= this.startContainer(snapshot).finally(() => {
      this.starting = null;
    });
    await this.starting;
  }

  private async startContainer(snapshot?: SnapshotHandle): Promise<void> {
    const container = this.ctx.container;
    if (!container) throw new Error("Media downloader container is not configured.");

    const egress = this.ctx.exports.MediaDownloaderEgress;

    // Register both interceptors before startup. The container has no direct
    // Internet/DNS route; every outbound HTTP(S) hop goes through this Worker.
    await container.interceptAllOutboundHttp(egress);
    await container.interceptOutboundHttps("*", egress);

    const common = {
      instance: INSTANCE,
      enableInternet: false,
      env: { NOLANE_INTERNAL_TOKEN: await this.containerSecret() },
    };
    if (snapshot) {
      container.start({ ...common, containerSnapshot: snapshot });
    } else {
      container.start({ ...common, image: container.images.base });
    }
    await container.setInactivityTimeout(CONTAINER_IDLE_MS);
    this.observeExit();

    const port = container.getTcpPort(PORT);
    let lastError: unknown;
    for (let attempt = 0; attempt < 100; attempt++) {
      try {
        const response = await port.fetch("http://container/health", {
          headers: { "x-nolane-internal": await this.containerSecret() },
          signal: AbortSignal.timeout(1000),
        });
        await response.body?.cancel();
        if (response.ok) return;
        lastError = new Error("Downloader health check returned HTTP " + response.status);
      } catch (error) {
        lastError = error;
      }
      await new Promise(resolve => setTimeout(resolve, 200));
    }
    throw new Error("Media downloader container did not become ready.", { cause: lastError });
  }

  private observeExit(): void {
    if (this.monitoring || !this.ctx.container?.running) return;
    this.monitoring = this.ctx.container.monitor()
      .catch(() => undefined)
      .finally(() => { this.monitoring = null; });
    this.ctx.waitUntil(this.monitoring);
  }

  private async containerRequest(path: string, init: RequestInit = {}): Promise<Response> {
    const container = this.ctx.container;
    if (!container?.running) throw new Error("container_stopped");
    const headers = new Headers(init.headers);
    headers.set("x-nolane-internal", await this.containerSecret());
    return container.getTcpPort(PORT).fetch("http://container" + path, {
      ...init,
      headers,
    });
  }

  private async startDownload(input: InternalStartBody): Promise<{
    jobId: string; status: string; progress: number;
  }> {
    if (!input || typeof input !== "object" || !isJobId(input.jobId) || !HASH_RE.test(input.shareTokenHash)) {
      throw new Error("invalid media download request.");
    }
    const normalized = normalizeMediaDownloadUrl(input.url);
    if (!normalized.ok) throw new Error("invalid media download URL.");
    const parsed = parseMediaDownloadInput({
      url: normalized.url, format: input.format, quality: input.quality,
    });
    if (!parsed.ok) throw new Error("invalid media download options.");

    const now = Date.now();
    const state: DownloadState = {
      jobId: input.jobId,
      status: "queued",
      progress: 0,
      format: parsed.value.format,
      quality: parsed.value.quality,
      sourceHost: new URL(parsed.value.url).hostname,
      createdAt: now,
      updatedAt: now,
      shareTokenHash: input.shareTokenHash.toLowerCase(),
    };
    const claimed = await this.ctx.storage.transaction(async transaction => {
      const current = await transaction.get<DownloadState>(STATE_KEY);
      if (current && ["queued", "running"].includes(current.status)) return false;
      if (current?.snapshot && current.shareExpiresAt && current.shareExpiresAt > Date.now()) return false;
      await transaction.put(STATE_KEY, state);
      return true;
    });
    if (!claimed) throw new Error("A previous media download or share link is still active.");

    try {
      await this.ensureContainer();
      const response = await this.containerRequest("/jobs", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          id: state.jobId,
          url: parsed.value.url,
          format: parsed.value.format,
          quality: parsed.value.quality,
        }),
      });
      if (!response.ok) {
        const error = response.status === 409 ? "A media download is already running." : "Container rejected the media job.";
        state.status = "failed";
        state.errorCode = "container_rejected";
        await this.writeState(state);
        throw new Error(error);
      }
      return { jobId: state.jobId, status: "queued", progress: 0 };
    } catch (error) {
      if (state.status !== "failed") {
        state.status = "failed";
        state.errorCode = "container_start_failed";
        await this.writeState(state);
      }
      throw error;
    }
  }

  private async getStatus(jobId: string): Promise<Response> {
    if (!isJobId(jobId)) return json({ error: "Not found." }, 404);
    const state = await this.readState();
    if (!state || state.jobId !== jobId) return json({ error: "Not found." }, 404);

    if (state.status === "queued" || state.status === "running") {
      if (!this.ctx.container?.running) {
        state.status = "failed";
        state.errorCode = "container_stopped";
        state.shareTokenHash = undefined;
        await this.writeState(state);
      } else {
        try {
          const response = await this.containerRequest("/jobs/" + jobId);
          if (!response.ok) throw new Error("container_status_unavailable");
          const job = await response.json() as ContainerJobResponse;
          if (job.status === "queued" || job.status === "running") {
            state.status = job.status;
            state.progress = Math.max(0, Math.min(99, Number(job.progress) || 0));
            await this.writeState(state);
          } else if (job.status === "complete") {
            const size = Number(job.size);
            if (!Number.isSafeInteger(size) || size < 1 || size > MAX_OUTPUT_BYTES ||
                typeof job.fileName !== "string" || typeof job.contentType !== "string") {
              state.status = "failed";
              state.errorCode = "too_large";
              state.shareTokenHash = undefined;
              await this.writeState(state);
            } else {
              try {
                const snapshot = await this.ctx.container.snapshotContainer({
                  name: "media-" + jobId.slice(0, 8),
                });
                if (snapshot.size > 20 * 1024 * 1024 * 1024) throw new Error("snapshot_too_large");
                state.status = "complete";
                state.progress = 100;
                state.fileName = job.fileName;
                state.contentType = job.contentType;
                state.size = size;
                state.snapshot = { id: snapshot.id, size: snapshot.size, name: snapshot.name };
                state.shareExpiresAt = Date.now() + SHARE_TTL_MS;
                await this.writeState(state);
                await this.ctx.container.destroy();
              } catch {
                state.status = "failed";
                state.errorCode = "snapshot_failed";
                state.shareTokenHash = undefined;
                await this.writeState(state);
                await this.ctx.container.destroy().catch(() => undefined);
              }
            }
          } else {
            state.status = job.status === "cancelled" ? "cancelled" : "failed";
            state.errorCode = job.error || "extractor_failed";
            state.shareTokenHash = undefined;
            await this.writeState(state);
          }
        } catch {
          state.status = "failed";
          state.errorCode = "container_status_unavailable";
          state.shareTokenHash = undefined;
          await this.writeState(state);
        }
      }
    }

    return json({
      jobId: state.jobId,
      status: state.status,
      progress: state.progress,
      format: state.format,
      quality: state.quality,
      fileName: state.fileName ?? null,
      contentType: state.contentType ?? null,
      size: state.size ?? null,
      error: state.errorCode ? errorMessage(state.errorCode) : null,
      shareExpiresAt: state.shareExpiresAt ?? null,
      sourceHost: state.sourceHost,
      createdAt: state.createdAt,
      updatedAt: state.updatedAt,
    });
  }

  private async cancel(jobId: string): Promise<Response> {
    if (!isJobId(jobId)) return json({ error: "Not found." }, 404);
    const state = await this.readState();
    if (!state || state.jobId !== jobId) return json({ error: "Not found." }, 404);
    if (state.status === "queued" || state.status === "running") {
      if (this.ctx.container?.running) {
        await this.containerRequest("/jobs/" + jobId + "/cancel", { method: "POST" }).catch(() => undefined);
      }
      state.status = "cancelled";
      state.shareTokenHash = undefined;
      await this.writeState(state);
      return json({ ok: true, status: state.status });
    }
    return this.revoke(jobId);
  }

  private async renewShare(jobId: string, tokenHash: string): Promise<Response> {
    if (!isJobId(jobId)) return json({ error: "Not found." }, 404);
    const state = await this.readState();
    if (!state || state.jobId !== jobId || state.status !== "complete" || !state.snapshot) {
      return json({ error: "A completed media file is required before sharing." }, 409);
    }
    state.shareTokenHash = tokenHash.toLowerCase();
    state.shareExpiresAt = Date.now() + SHARE_TTL_MS;
    await this.writeState(state);
    return json({
      ok: true,
      jobId,
      shareExpiresAt: state.shareExpiresAt,
      fileName: state.fileName,
      contentType: state.contentType,
      size: state.size,
    });
  }

  private async validShare(jobId: string, token: string): Promise<DownloadState | null> {
    if (!isJobId(jobId) || !HASH_RE.test(token)) return null;
    const state = await this.readState();
    if (!state || state.jobId !== jobId || state.status !== "complete" ||
        !state.snapshot || !state.shareTokenHash ||
        !state.shareExpiresAt || state.shareExpiresAt <= Date.now()) return null;
    const tokenHash = await sha256Hex(token);
    return equalHex(tokenHash, state.shareTokenHash) ? state : null;
  }

  private async shareInfo(jobId: string, token: string): Promise<Response> {
    const state = await this.validShare(jobId, token);
    if (!state) return json({ error: "Share link is invalid or expired." }, 404);
    return json({
      jobId: state.jobId,
      fileName: state.fileName,
      contentType: state.contentType,
      size: state.size,
      format: state.format,
      shareExpiresAt: state.shareExpiresAt,
    });
  }

  private async serveSharedFile(jobId: string, request: Request): Promise<Response> {
    const token = request.headers.get("x-nolane-share-token") || "";
    const state = await this.validShare(jobId, token);
    if (!state || !state.snapshot) return json({ error: "Share link is invalid or expired." }, 404);
    try {
      await this.ensureContainer(state.snapshot);
      await this.ctx.container?.setInactivityTimeout(10 * 60 * 1000);
      const headers = new Headers();
      const range = request.headers.get("range");
      if (range) headers.set("range", range);
      const upstream = await this.containerRequest("/files/" + jobId, {
        method: request.method,
        headers,
      });
      const responseHeaders = new Headers();
      for (const name of ["content-type", "content-length", "content-range", "content-disposition", "accept-ranges"]) {
        const value = upstream.headers.get(name);
        if (value) responseHeaders.set(name, value);
      }
      responseHeaders.set("cache-control", "private, no-store");
      responseHeaders.set("x-content-type-options", "nosniff");
      responseHeaders.set("referrer-policy", "no-referrer");
      responseHeaders.set("cross-origin-resource-policy", "same-origin");
      return new Response(request.method === "HEAD" ? null : upstream.body, {
        status: upstream.status,
        headers: responseHeaders,
      });
    } catch {
      return json({ error: "The temporary media file is unavailable." }, 410);
    }
  }

  private async revoke(jobId: string): Promise<Response> {
    if (!isJobId(jobId)) return json({ error: "Not found." }, 404);
    const state = await this.readState();
    if (!state || state.jobId !== jobId) return json({ error: "Not found." }, 404);
    if (state.status === "queued" || state.status === "running") {
      if (this.ctx.container?.running) {
        await this.containerRequest("/jobs/" + jobId + "/cancel", { method: "POST" }).catch(() => undefined);
      }
    }
    state.status = "revoked";
    state.shareTokenHash = undefined;
    state.snapshot = undefined;
    state.shareExpiresAt = undefined;
    await this.writeState(state);
    return json({
      ok: true,
      status: "revoked",
      notice: "Share access is revoked. Cloudflare Container snapshots cannot be manually deleted and expire automatically after up to 30 days from the last restore.",
    });
  }
}

