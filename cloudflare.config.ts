import { bindings, defineConfig, defineContainer, exports, triggers } from "cf/config";
import * as entrypoint from "./src/index.ts" with { type: "cf-worker" };
import type { SearchQueueJob } from "./src/types";

declare const process: { env: Record<string, string | undefined> };

const mediaContainersEnabled = process.env.MEDIA_DOWNLOADER_CONTAINER_ENABLED === "true";
const mediaDownloaderContainer = mediaContainersEnabled ? defineContainer({
  name: "nolane-media-downloader",
  schedulingPolicy: "durable-object",
  images: {
    base: { dockerfile: "./media-downloader/Dockerfile" },
  },
}) : undefined;

export default defineConfig({
  containers: mediaDownloaderContainer ? [mediaDownloaderContainer] : [],
  accountId: "1172c01120a2470aa12f81e5b4778556",
  worker: {
    name: "nolane-search",
    exports: mediaDownloaderContainer ? {
      MediaDownloader: exports.durableObject({
        storage: "sqlite",
        container: mediaDownloaderContainer,
      }),
      MediaDownloaderEgress: exports.worker(),
    } : undefined,
    entrypoint,
    compatibilityDate: "2026-11-17",
    compatibilityFlags: ["enable_ctx_exports"],
    workersDev: true,
    observability: {
      enabled: true,
      logs: { enabled: true, headSamplingRate: 0.2, invocationLogs: true, persist: false },
      traces: { enabled: true, headSamplingRate: 0.01, persist: false },
    },
    env: {
      DB: bindings.d1({ name: "nolane-search-db", id: "4f6a8cbd-cc8c-42b9-be6a-ed45c709d3db" }),
      SEARCH_JOBS: bindings.queue<SearchQueueJob>({ name: "nolane-search-jobs" }),
      TELEGRAM_BOT_TOKEN: bindings.secret(),
      TELEGRAM_WEBHOOK_SECRET: bindings.secret(),
      ALLOWED_TELEGRAM_USER_IDS: bindings.secret(),
      TAVILY_API_KEY: bindings.secret(),
      TELEGRAM_ARCHIVE_CHAT_ID: bindings.secret(),
      EXA_API_KEY: bindings.secret(),
      TINYFISH_API_KEY: bindings.secret(),
      OPENROUTER_API_KEY: bindings.secret(),
      OPENROUTER_MODEL: bindings.secret(),
      OPENROUTER_MODELS: bindings.secret(),
      AI_ROUTER_CONFIG: bindings.secret(),
      MEDIA_ALLOW_NSFW: bindings.secret(),
      MEDIA_DOWNLOADER_ENABLED: bindings.secret(),
      MEDIA_DOWNLOADER: mediaDownloaderContainer
        ? bindings.durableObject({ worker: "nolane-search", exportName: "MediaDownloader" })
        : undefined,
    },
    triggers: [
      triggers.queue({ name: "nolane-search-jobs", deadLetterQueue: "nolane-search-dlq", maxBatchSize: 3, maxRetries: 3, retryDelay: 30, maxConcurrency: 1 }),
      triggers.queue({ name: "nolane-search-dlq", maxBatchSize: 3, maxRetries: 1, retryDelay: 60, maxConcurrency: 1 }),
      triggers.scheduled({ schedule: "*/30 * * * *" }),
    ],
  },
});
