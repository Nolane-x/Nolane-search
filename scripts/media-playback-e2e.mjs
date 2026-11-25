import { createServer } from "node:http";
import { readFile, mkdir, writeFile, appendFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { transformWithEsbuild } from "vite";
import { chromium } from "playwright";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const outputDir = resolve(root, "artifacts");
const reportPath = resolve(outputDir, "media-playback-report.json");
const summaryPath = process.env.GITHUB_STEP_SUMMARY;
const timeoutMs = Number(process.env.MEDIA_E2E_TIMEOUT_MS || 55_000);

const samples = [
  {
    id: "hls-mux-abr",
    label: "HLS · Mux Big Buck Bunny · ABR ladder",
    url: "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8",
    expected: { quality: 2 },
  },
  {
    id: "hls-shaka-audio",
    label: "HLS · Shaka Angel One · alternate audio",
    url: "https://storage.googleapis.com/shaka-demo-assets/angel-one-hls/hls.m3u8",
    expected: { audio: 2 },
  },
  {
    id: "hls-jw-captions",
    label: "HLS · HLS Test Streams · WebVTT subtitles",
    url: "https://mtoczko.github.io/hls-test-streams/test-vtt-ts-segments/playlist.m3u8",
    expected: { subtitles: 1 },
  },
  {
    id: "dash-shaka-angel-one",
    label: "DASH · Shaka Angel One · multiple languages and subtitles",
    url: "https://storage.googleapis.com/shaka-demo-assets/angel-one/dash.mpd",
    expected: { quality: 2, audio: 2, subtitles: 1 },
  },
  {
    id: "dash-shaka-sintel",
    label: "DASH · Shaka Sintel · subtitle and representation test",
    url: "https://storage.googleapis.com/shaka-demo-assets/sintel/dash.mpd",
    expected: { quality: 2, subtitles: 1 },
  },
];

const results = [];

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
  const path = url.pathname.toLowerCase();
  const streamType = path.endsWith(".m3u8") ? "hls" : path.endsWith(".mpd") ? "dash" : null;
  if (!streamType || url.protocol !== "https:") return null;
  const provider = streamType === "hls" ? "HLS" : "DASH";
  return {
    id: streamType + ":" + url.hostname + url.pathname,
    title: provider + " browser test stream",
    provider,
    mediaType: "video",
    sourceUrl: url.toString(),
    previewUrl: null,
    mediaUrl: url.toString(),
    embedUrl: null,
    streamType,
    description: "Direct public test stream. Media bytes are loaded by the browser.",
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
  if (typeof mediaUi.mediaAppResponse !== "function") {
    throw new Error("mediaAppResponse export was not found in src/media-ui.ts");
  }
  const response = mediaUi.mediaAppResponse(false);
  if (!response.ok) throw new Error("mediaAppResponse did not return a successful response");
  return {
    html: await response.text(),
    headers: Object.fromEntries(response.headers.entries()),
  };
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
        sendJson(response, 422, { status: "unsupported", error: "Unsupported test manifest URL" });
        return;
      }
      sendJson(response, 200, { status: "resolved", item });
      return;
    }
    sendJson(response, 404, { error: "Not found in the browser test harness" });
  });
  await new Promise((resolveListen, rejectListen) => {
    server.once("error", rejectListen);
    server.listen(0, "127.0.0.1", resolveListen);
  });
  const address = server.address();
  if (!address || typeof address === "string") throw new Error("Could not obtain local browser-harness port");
  return { server, origin: "http://127.0.0.1:" + address.port };
}

function safeResourceUrl(value) {
  try {
    const url = new URL(value);
    return url.origin + url.pathname;
  } catch {
    return String(value).slice(0, 200);
  }
}

async function optionSnapshot(page, selector) {
  return page.locator(selector).evaluate((select) => ({
    visible: !select.closest("label")?.hidden,
    selected: select.value,
    options: Array.from(select.options).map((option) => ({
      value: option.value,
      label: option.textContent?.trim() || "",
    })),
  }));
}

async function waitForExpectedOptions(page, selector, count, label, errors) {
  if (!count) return null;
  try {
    await page.waitForFunction(
      ({ selector, count }) => {
        const select = document.querySelector(selector);
        return Boolean(select && !select.closest("label")?.hidden && select.options.length >= count);
      },
      { selector, count },
      { timeout: 20_000 },
    );
  } catch {
    const snapshot = await optionSnapshot(page, selector).catch(() => null);
    errors.push(label + " selector did not expose enough tracks/options: " + JSON.stringify(snapshot));
    return snapshot;
  }
  return optionSnapshot(page, selector);
}

async function runSample(browser, origin, sample) {
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1000 },
    reducedMotion: "reduce",
  });
  const failures = [];
  const consoleErrors = [];
  const mediaResponses = [];
  page.on("requestfailed", (request) => {
    if (request.url().startsWith("https://")) {
      failures.push({
        url: safeResourceUrl(request.url()),
        error: request.failure()?.errorText || "request failed",
      });
    }
  });
  page.on("response", async (response) => {
    if (!response.url().startsWith(origin) && response.url().startsWith("https://")) {
      try {
        const headers = await response.allHeaders();
        mediaResponses.push({
          url: safeResourceUrl(response.url()),
          status: response.status(),
          contentType: headers["content-type"] || null,
          accessControlAllowOrigin: headers["access-control-allow-origin"] || null,
        });
      } catch {
        mediaResponses.push({ url: safeResourceUrl(response.url()), status: response.status() });
      }
    }
  });
  page.on("pageerror", (error) => consoleErrors.push(error.message));
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text().slice(0, 400));
  });

  const result = {
    id: sample.id,
    label: sample.label,
    url: sample.url,
    expected: sample.expected,
    browser: "Playwright Chromium",
    player: sample.url.toLowerCase().endsWith(".m3u8") ? "HLS.js 1.7.4" : "dash.js 5.3.0",
    passed: false,
    quality: null,
    audio: null,
    subtitles: null,
    playbackRate: null,
    playbackSeconds: 0,
    manifestResponse: null,
    corsEvidence: [],
    requestFailures: failures,
    consoleErrors,
    errors: [],
  };

  try {
    await page.goto(origin + "/media", { waitUntil: "domcontentloaded", timeout: timeoutMs });
    await page.waitForFunction(
      () => document.querySelector("#status")?.textContent?.includes("Đã đăng nhập"),
      undefined,
      { timeout: 10_000 },
    );
    await page.locator("#q").fill(sample.url);
    await page.locator("#search").evaluate((form) => form.requestSubmit());
    await page.locator(".stream-card .embed-load").waitFor({ state: "visible", timeout: 15_000 });

    await page.locator(".stream-card .embed-load").click();
    await page.locator("video.stream-video").waitFor({ state: "attached", timeout: 10_000 });

    const manifestHost = new URL(sample.url).host;
    try {
      await page.waitForFunction(
        (host) => performance.getEntriesByType("resource").some((entry) => {
          try { return new URL(entry.name).host === host; } catch { return false; }
        }),
        manifestHost,
        { timeout: 20_000 },
      );
    } catch {
      result.errors.push("The browser did not record a request to the manifest host.");
    }

    const video = page.locator("video.stream-video");
    await page.waitForFunction(
      () => {
        const element = document.querySelector("video.stream-video");
        return Boolean(element && (element.readyState >= 2 || element.error));
      },
      undefined,
      { timeout: 45_000 },
    );
    const playback = await page.evaluate(async () => {
      const element = document.querySelector("video.stream-video");
      if (!element) throw new Error("No stream video element was created");
      element.muted = true;
      try {
        await element.play();
        return { playError: null };
      } catch (error) {
        return { playError: error instanceof Error ? error.message : String(error) };
      }
    });
    if (playback.playError) result.errors.push("video.play() failed: " + playback.playError);

    try {
      await page.waitForFunction(
        () => {
          const element = document.querySelector("video.stream-video");
          return Boolean(element && element.currentTime >= 2);
        },
        undefined,
        { timeout: timeoutMs },
      );
    } catch {
      const details = await page.evaluate(() => {
        const element = document.querySelector("video.stream-video");
        return {
          currentTime: element?.currentTime ?? null,
          readyState: element?.readyState ?? null,
          networkState: element?.networkState ?? null,
          mediaError: element?.error ? {
            code: element.error.code,
            message: element.error.message,
          } : null,
          status: document.querySelector(".stream-status")?.textContent || "",
        };
      });
      result.errors.push("Playback did not advance to 2 seconds: " + JSON.stringify(details));
    }

    const minimumQualityOptions = sample.expected.quality ? sample.expected.quality + 1 : 0;
    const minimumAudioOptions = sample.expected.audio || 0;
    const minimumSubtitleOptions = sample.expected.subtitles ? sample.expected.subtitles + 1 : 0;

    result.quality = await waitForExpectedOptions(page, "select.stream-quality", minimumQualityOptions, "Quality", result.errors);
    result.audio = await waitForExpectedOptions(page, "select.stream-track[aria-label='Ngôn ngữ âm thanh']", minimumAudioOptions, "Audio", result.errors);
    result.subtitles = await waitForExpectedOptions(page, "select.stream-track[aria-label='Ngôn ngữ phụ đề']", minimumSubtitleOptions, "Subtitle", result.errors);

    if (result.quality?.visible && (sample.expected.quality || 0) > 0) {
      const manual = result.quality.options.find((option) => option.value !== "-1");
      if (manual) {
        await page.locator("select.stream-quality").selectOption(manual.value);
        await page.waitForFunction(
          () => document.querySelector(".stream-status")?.textContent?.includes("Đã yêu cầu chất lượng"),
          undefined,
          { timeout: 8_000 },
        ).catch(() => result.errors.push("Manual quality selection did not reach the player handler."));
      }
    }

    if (result.audio?.visible && (sample.expected.audio || 0) >= 2) {
      const alternate = result.audio.options.find((option) => option.value !== result.audio.options[0]?.value);
      if (alternate) {
        await page.locator("select.stream-track[aria-label='Ngôn ngữ âm thanh']").selectOption(alternate.value);
      }
    }

    if (result.subtitles?.visible && (sample.expected.subtitles || 0) >= 1) {
      const subtitle = result.subtitles.options.find((option) => option.value !== "-1");
      if (subtitle) {
        await page.locator("select.stream-track[aria-label='Ngôn ngữ phụ đề']").selectOption(subtitle.value);
      }
    }

    result.uiDiagnostics = await page.evaluate(() => {
      const preview = document.querySelector(".stream-card .preview");
      const element = document.querySelector("video.stream-video");
      return {
        playerStatus: document.querySelector(".stream-status")?.textContent || "",
        previewChildren: Array.from(preview?.children || []).map((child) => ({
          tag: child.tagName,
          className: typeof child.className === "string" ? child.className : "",
          hidden: Boolean(child.hidden),
          display: getComputedStyle(child).display,
          text: (child.textContent || "").trim().slice(0, 100),
        })),
        selects: Array.from(preview?.querySelectorAll("select") || []).map((select) => ({
          className: select.className,
          value: select.value,
          disabled: select.disabled,
          hidden: Boolean(select.closest("label")?.hidden),
          display: getComputedStyle(select).display,
          options: Array.from(select.options).map((option) => ({ value: option.value, label: option.textContent?.trim() || "" })),
        })),
        video: element ? {
          currentTime: element.currentTime,
          readyState: element.readyState,
          networkState: element.networkState,
          paused: element.paused,
          ended: element.ended,
          error: element.error ? { code: element.error.code, message: element.error.message } : null,
          playbackRate: element.playbackRate,
        } : null,
      };
    });

    const rateControl = result.uiDiagnostics.selects.find((select) => select.className.split(/\\s+/).includes("stream-rate"));
    if (!rateControl) {
      result.errors.push("Playback-rate selector is missing from the rendered player DOM.");
    } else if (rateControl.hidden || rateControl.disabled || !rateControl.options.some((option) => option.value === "1.25")) {
      result.errors.push("Playback-rate selector exists but is not usable: " + JSON.stringify(rateControl));
    } else {
      await page.locator("select.stream-rate").selectOption("1.25");
      result.playbackRate = await video.evaluate((element) => element.playbackRate);
      if (result.playbackRate !== 1.25) result.errors.push("Playback-rate control did not set 1.25x.");
    }

    result.videoDiagnostics = await video.evaluate((element) => ({
      currentTime: element.currentTime,
      readyState: element.readyState,
      networkState: element.networkState,
      paused: element.paused,
      ended: element.ended,
      error: element.error ? { code: element.error.code, message: element.error.message } : null,
      playbackRate: element.playbackRate,
    }));
    result.playbackSeconds = result.videoDiagnostics.currentTime;
    result.manifestResponse = mediaResponses.find((entry) => entry.url.startsWith(new URL(sample.url).origin)) || null;
    result.corsEvidence = mediaResponses.slice(0, 12);
    result.requestFailures = failures.slice(0, 20);
    result.consoleErrors = consoleErrors.slice(0, 20);

    if (failures.length > 0) result.errors.push("Browser reported " + failures.length + " failed HTTPS request(s).");
    if (consoleErrors.some((message) => /cors|access-control|media error|manifest.*error/i.test(message))) {
      result.errors.push("Browser console reported a CORS or media/manifest error.");
    }
    result.passed = result.errors.length === 0;
  } catch (error) {
    result.errors.push(error instanceof Error ? error.message : String(error));
    result.requestFailures = failures.slice(0, 20);
    result.consoleErrors = consoleErrors.slice(0, 20);
    result.corsEvidence = mediaResponses.slice(0, 12);
  } finally {
    await page.close().catch(() => {});
  }

  return result;
}

async function main() {
  await mkdir(outputDir, { recursive: true });
  const { server, origin } = await startHarness();
  let browser;
  const startedAt = new Date().toISOString();

  try {
    browser = await chromium.launch({
      headless: true,
      args: ["--autoplay-policy=no-user-gesture-required"],
    });
    for (const sample of samples) {
      const result = await runSample(browser, origin, sample);
      results.push(result);
      const state = result.passed ? "PASS" : "FAIL";
      console.log(
        state + " " + sample.id +
        " · quality=" + (result.quality?.options?.length ?? "n/a") +
        " · audio=" + (result.audio?.options?.length ?? "n/a") +
        " · subtitles=" + (result.subtitles?.options?.length ?? "n/a") +
        " · played=" + result.playbackSeconds.toFixed(1) + "s",
      );
      for (const error of result.errors) console.error("  - " + error);
      if (result.corsEvidence.length) console.log("  CORS evidence:", JSON.stringify(result.corsEvidence.slice(0, 3)));
    }
  } finally {
    if (browser) await browser.close().catch(() => {});
    await new Promise((resolveClose) => server.close(resolveClose));
  }

  const report = {
    title: "Nolane Search · Wave 66 live browser playback",
    startedAt,
    finishedAt: new Date().toISOString(),
    browser: "Playwright Chromium",
    hlsJs: "1.7.4",
    dashJs: "5.3.0",
    sourcePolicy: "Third-party HTTPS sources; direct browser requests; no Worker media proxy",
    passed: results.filter((item) => item.passed).length,
    failed: results.filter((item) => !item.passed).length,
    results,
  };
  await writeFile(reportPath, JSON.stringify(report, null, 2) + "\n", "utf8");

  const lines = [
    "## Wave 66 · live browser playback",
    "",
    "| Sample | Player | Quality options | Audio options | Subtitle options | Playback | Result |",
    "|---|---|---:|---:|---:|---:|---|",
    ...results.map((item) => [
      item.label,
      item.player,
      item.quality?.options?.length ?? "—",
      item.audio?.options?.length ?? "—",
      item.subtitles?.options?.length ?? "—",
      item.playbackSeconds.toFixed(1) + "s",
      item.passed ? "PASS" : "FAIL",
    ].map((value) => String(value).replaceAll("|", "\\|")).join(" | ")).map((row) => "| " + row + " |"),
    "",
    "Passed: **" + report.passed + "/" + results.length + "**. These results describe the sources and browser at test time; external owners can change or retire them.",
    "",
    "Full machine-readable report: media-playback-report.json.",
  ].join("\n");

  if (summaryPath) await appendFile(summaryPath, lines + "\n", "utf8");
  console.log(lines);
  console.log("Report written to " + reportPath);

  if (report.failed > 0) process.exitCode = 1;
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
