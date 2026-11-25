import { createServer } from "node:http";
import { spawn, execFileSync } from "node:child_process";
import { readFile, mkdir, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { transformWithEsbuild } from "vite";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const outputDir = resolve(root, "artifacts");
const reportPath = resolve(outputDir, "safari-native-hls-report.json");
const screenshotPath = resolve(outputDir, "safari-native-hls.png");
const sampleUrl = "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8";
const driverOrigin = "http://127.0.0.1:4444";
const timeoutMs = Number(process.env.SAFARI_HLS_TIMEOUT_MS || 45_000);

function sendJson(response, status, value) {
  response.writeHead(status, {
    "content-type": "application/json; charset=utf-8",
    "cache-control": "no-store",
  });
  response.end(JSON.stringify(value));
}

function createResolvedItem(input) {
  let url;
  try { url = new URL(input); } catch { return null; }
  if (url.protocol !== "https:" || !url.pathname.toLowerCase().endsWith(".m3u8")) return null;
  return {
    id: "hls:" + url.hostname + url.pathname,
    title: "HLS Safari native playback test",
    provider: "HLS",
    mediaType: "video",
    sourceUrl: url.toString(),
    previewUrl: null,
    mediaUrl: url.toString(),
    embedUrl: null,
    streamType: "hls",
    description: "Public HLS sample. Safari fetches manifests and media directly.",
    credit: null,
    license: null,
    licenseUrl: null,
    dateCreated: null,
    referrerPolicy: "no-referrer",
  };
}

async function buildMediaPortalHtml() {
  const source = await readFile(resolve(root, "src/media-ui.ts"), "utf8");
  const transformed = await transformWithEsbuild(source, "src/media-ui.ts", {
    loader: "ts",
    format: "esm",
    target: "es2022",
  });
  const moduleUrl = "data:text/javascript;base64," + Buffer.from(transformed.code).toString("base64");
  const mediaUi = await import(moduleUrl);
  if (typeof mediaUi.mediaAppResponse !== "function") throw new Error("mediaAppResponse export was not found");
  const response = mediaUi.mediaAppResponse(false);
  if (!response.ok) throw new Error("Media Portal did not return HTTP 200");
  return { html: await response.text(), headers: Object.fromEntries(response.headers.entries()) };
}

async function startHarness() {
  const page = await buildMediaPortalHtml();
  const server = createServer(async (request, response) => {
    const requestUrl = new URL(request.url || "/", "http://127.0.0.1");
    if (requestUrl.pathname === "/" || requestUrl.pathname === "/media") {
      response.writeHead(200, page.headers);
      response.end(page.html);
      return;
    }
    if (requestUrl.pathname === "/api/auth/me" && request.method === "GET") {
      sendJson(response, 200, { ok: true, userId: 42 });
      return;
    }
    if (requestUrl.pathname === "/api/auth/logout" && request.method === "POST") {
      sendJson(response, 200, { ok: true });
      return;
    }
    if (requestUrl.pathname === "/api/media/resolve" && request.method === "GET") {
      const item = createResolvedItem(requestUrl.searchParams.get("url") || "");
      if (!item) {
        sendJson(response, 422, { status: "unsupported", error: "Unsupported Safari test manifest URL" });
        return;
      }
      sendJson(response, 200, { status: "resolved", item });
      return;
    }
    sendJson(response, 404, { error: "Not found in Safari test harness" });
  });
  await new Promise((resolveListen, rejectListen) => {
    server.once("error", rejectListen);
    server.listen(0, "127.0.0.1", resolveListen);
  });
  const address = server.address();
  if (!address || typeof address === "string") throw new Error("Could not bind local media harness");
  return { server, origin: "http://127.0.0.1:" + address.port };
}

async function webdriver(method, path, body) {
  const response = await fetch(driverOrigin + path, {
    method,
    headers: body === undefined ? undefined : { "content-type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
    signal: AbortSignal.timeout(15_000),
  });
  const text = await response.text();
  let value;
  try { value = text ? JSON.parse(text) : {}; }
  catch { throw new Error("Safari WebDriver returned non-JSON HTTP " + response.status + ": " + text.slice(0, 300)); }
  if (!response.ok || value.value?.error) {
    const detail = value.value?.message || value.message || text.slice(0, 500);
    throw new Error("Safari WebDriver " + method + " " + path + " returned HTTP " + response.status + ": " + detail);
  }
  return value.value ?? value;
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function waitFor(read, predicate, label, maxMs = timeoutMs) {
  const started = Date.now();
  let last;
  while (Date.now() - started < maxMs) {
    last = await read();
    if (predicate(last)) return last;
    await sleep(500);
  }
  throw new Error("Timed out waiting for " + label + "; last state: " + JSON.stringify(last));
}

async function execute(sessionId, script, args = [], asyncScript = false) {
  const endpoint = asyncScript ? "execute/async" : "execute/sync";
  return webdriver("POST", "/session/" + sessionId + "/" + endpoint, {
    script,
    args,
  });
}

async function main() {
  await mkdir(outputDir, { recursive: true });
  const report = {
    title: "Nolane Search · Safari native HLS verification",
    startedAt: new Date().toISOString(),
    browser: "Apple Safari via safaridriver / W3C WebDriver",
    runner: process.env.RUNNER_OS || process.platform,
    source: sampleUrl,
    passed: false,
    nativeHlsCapability: null,
    playerStatus: null,
    video: null,
    playbackSeconds: 0,
    screenshot: null,
    errors: [],
  };
  const harness = await startHarness();
  let driverProcess;
  let sessionId;

  try {
    execFileSync("/usr/bin/safaridriver", ["--enable"], { stdio: "inherit", timeout: 15_000 });
    driverProcess = spawn("/usr/bin/safaridriver", ["-p", "4444"], {
      stdio: "ignore",
      env: process.env,
    });
    driverProcess.once("error", (error) => report.errors.push("Could not start safaridriver: " + error.message));

    await waitFor(
      async () => {
        try { return await webdriver("GET", "/status"); }
        catch { return null; }
      },
      (state) => Boolean(state && state.ready !== false),
      "Safari WebDriver status",
      20_000,
    );

    const created = await webdriver("POST", "/session", {
      capabilities: {
        alwaysMatch: {
          browserName: "safari",
          pageLoadStrategy: "eager",
        },
      },
    });
    sessionId = created.sessionId || created.value?.sessionId;
    report.safariCapabilities = created.capabilities || null;
    if (!sessionId) throw new Error("Safari WebDriver created no session ID");
    await webdriver("POST", "/session/" + sessionId + "/timeouts", {
      script: 15_000,
      pageLoad: 25_000,
      implicit: 0,
    });

    await webdriver("POST", "/session/" + sessionId + "/url", { url: harness.origin + "/media" });
    await waitFor(
      () => execute(sessionId, "return document.querySelector('#status')?.textContent || ''"),
      (status) => typeof status === "string" && status.includes("Đã đăng nhập"),
      "Media Portal owner-session boot",
      15_000,
    );

    const capability = await execute(sessionId, `return {
      userAgent: navigator.userAgent,
      vendor: navigator.vendor,
      canPlayType: document.createElement('video').canPlayType('application/vnd.apple.mpegurl'),
      hlsJsPresent: Boolean(window.Hls)
    }`);
    report.nativeHlsCapability = capability;
    if (!/Apple Computer, Inc\./.test(capability.vendor || "") ||
        !/AppleWebKit/.test(capability.userAgent || "") ||
        !capability.canPlayType ||
        capability.canPlayType === "") {
      throw new Error("Safari did not report Apple WebKit native-HLS support: " + JSON.stringify(capability));
    }

    await execute(sessionId, `document.querySelector('#q').value = arguments[0];
      document.querySelector('#search').requestSubmit();
      return true;`, [sampleUrl]);
    await waitFor(
      () => execute(sessionId, "return Boolean(document.querySelector('.stream-card .embed-load'))"),
      Boolean,
      "resolved HLS player card",
      15_000,
    );

    const button = await webdriver("POST", "/session/" + sessionId + "/element", {
      using: "css selector",
      value: ".stream-card .embed-load",
    });
    const element = button["element-6066-11e4-a52e-4f735466cecf"] || button.ELEMENT;
    if (!element) throw new Error("Could not find the HLS Play button in Safari");
    await webdriver("POST", "/session/" + sessionId + "/element/" + element + "/click", {});

    const nativeState = await waitFor(
      () => execute(sessionId, `const v = document.querySelector('video.stream-video');
        return {
          src: v?.src || '',
          status: document.querySelector('.stream-status')?.textContent || '',
          hlsJsLoaded: performance.getEntriesByType('resource').some((entry) => entry.name.includes('/hls.js@')),
          readyState: v?.readyState ?? -1,
          networkState: v?.networkState ?? -1,
          errorCode: v?.error?.code ?? null,
          errorMessage: v?.error?.message ?? null
        };`),
      (state) => Boolean(state?.status?.includes("HLS native") && state.src.endsWith(".m3u8")),
      "Safari native-HLS player selection",
      10_000,
    );
    if (nativeState.hlsJsLoaded) throw new Error("Safari native-HLS unexpectedly downloaded HLS.js");

    const playResult = await execute(sessionId, `const done = arguments[arguments.length - 1];
      const v = document.querySelector('video.stream-video');
      if (!v) return done({ ok: false, error: 'video element missing' });
      v.muted = true;
      const p = v.play();
      if (p && typeof p.then === 'function') p.then(() => done({ ok: true })).catch((e) => done({ ok: false, error: String(e) }));
      else done({ ok: true });`, [], true);
    if (!playResult?.ok) throw new Error("Safari video.play() failed: " + (playResult?.error || JSON.stringify(playResult)));

    const playback = await waitFor(
      () => execute(sessionId, `const v = document.querySelector('video.stream-video');
        return {
          currentTime: v?.currentTime ?? 0,
          readyState: v?.readyState ?? -1,
          networkState: v?.networkState ?? -1,
          paused: v?.paused ?? true,
          ended: v?.ended ?? false,
          errorCode: v?.error?.code ?? null,
          errorMessage: v?.error?.message ?? null,
          playerStatus: document.querySelector('.stream-status')?.textContent || ''
        };`),
      (state) => state?.currentTime >= 1 && state.readyState >= 2 && !state.paused && !state.errorCode,
      "real Safari native-HLS decode and playback advancement",
      35_000,
    );

    const screenshot = await webdriver("GET", "/session/" + sessionId + "/screenshot");
    if (typeof screenshot === "string" && screenshot.length > 100) {
      await writeFile(screenshotPath, Buffer.from(screenshot, "base64"));
      report.screenshot = "artifacts/safari-native-hls.png";
    }
    report.playerStatus = nativeState.status;
    report.video = playback;
    report.playbackSeconds = playback.currentTime;
    report.passed = true;
    console.log("PASS Safari native HLS · played=" + playback.currentTime.toFixed(1) + "s · readyState=" + playback.readyState);
  } catch (error) {
    report.errors.push(error instanceof Error ? error.message : String(error));
    if (sessionId) {
      try {
        const screenshot = await webdriver("GET", "/session/" + sessionId + "/screenshot");
        if (typeof screenshot === "string" && screenshot.length > 100) {
          await writeFile(screenshotPath, Buffer.from(screenshot, "base64"));
          report.screenshot = "artifacts/safari-native-hls.png";
        }
      } catch {}
      try {
        report.video = await execute(sessionId, `const v = document.querySelector('video.stream-video'); return {
          currentTime: v?.currentTime ?? 0, readyState: v?.readyState ?? -1, networkState: v?.networkState ?? -1,
          paused: v?.paused ?? true, errorCode: v?.error?.code ?? null, errorMessage: v?.error?.message ?? null,
          playerStatus: document.querySelector('.stream-status')?.textContent || ''
        };`);
      } catch {}
    }
    console.error("FAIL Safari native HLS:", report.errors[0]);
  } finally {
    report.finishedAt = new Date().toISOString();
    await writeFile(reportPath, JSON.stringify(report, null, 2) + "\n", "utf8");
    if (sessionId) await webdriver("DELETE", "/session/" + sessionId).catch(() => {});
    if (driverProcess && driverProcess.exitCode === null) driverProcess.kill("SIGTERM");
    await new Promise((resolveClose) => harness.server.close(resolveClose));
  }

  console.log("Safari native-HLS report: " + reportPath);
  if (!report.passed) process.exitCode = 1;
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
