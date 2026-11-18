export type SearchMode = "web" | "tech" | "research" | "news" | "github" | "wiki" | "local";

export interface SearchResult {
  title: string;
  url: string;
  snippet: string;
  domain: string;
  provider: string;
  score: number;
  publishedAt?: string;
}

export interface DeepSearchJob {
  id: string;
  chatId: number;
  userId: number;
  query: string;
  createdAt: number;
}

export interface SiteCrawlJob {
  kind: "site-crawl";
  id: string;
  chatId: number;
  userId: number;
  seedUrl: string;
  maxPages: number;
  createdAt: number;
}

export type SearchQueueJob = DeepSearchJob | SiteCrawlJob;

export interface Env {
  DB: D1Database;
  SEARCH_JOBS: Queue<SearchQueueJob>;
  TELEGRAM_BOT_TOKEN?: string;
  TELEGRAM_WEBHOOK_SECRET?: string;
  ALLOWED_TELEGRAM_USER_IDS?: string;
  TAVILY_API_KEY?: string;
  TELEGRAM_ARCHIVE_CHAT_ID?: string;
  EXA_API_KEY?: string;
  BRAVE_SEARCH_API_KEY?: string;
  TINYFISH_API_KEY?: string;
  OPENROUTER_API_KEY?: string;
  /** Legacy single-model setting. Kept for backward compatibility. */
  OPENROUTER_MODEL?: string;
  /** Comma- or newline-separated model IDs, tried in priority order by OpenRouter. */
  OPENROUTER_MODELS?: string;
  /** JSON secret containing provider/key/model routes for the AI gateway. */
  AI_ROUTER_CONFIG?: string;
  GITHUB_TOKEN?: string;
}

export interface D1Result<T = Record<string, unknown>> {
  results: T[];
  success?: boolean;
  meta?: { changes?: number; duration?: number; rows_read?: number; rows_written?: number };
}

export interface D1Statement {
  bind(...values: unknown[]): D1Statement;
  all<T = Record<string, unknown>>(): Promise<D1Result<T>>;
  first<T = Record<string, unknown>>(): Promise<T | null>;
  run(): Promise<D1Result>;
}

export interface D1Database {
  prepare(sql: string): D1Statement;
  batch<T = unknown>(statements: D1Statement[]): Promise<D1Result<T>[]>;
}

export interface Queue<T> {
  send(message: T): Promise<void>;
}

export interface ExecutionContext {
  waitUntil(promise: Promise<unknown>): void;
}

export interface QueueMessage<T> {
  body: T;
  attempts: number;
  ack(): void;
  retry(options?: { delaySeconds?: number }): void;
}

export interface MessageBatch<T> {
  queue: string;
  messages: QueueMessage<T>[];
}

export interface TelegramUser {
  id: number;
  username?: string;
  first_name?: string;
}

export interface TelegramMessage {
  message_id: number;
  chat: { id: number; type: string };
  from?: TelegramUser;
  text?: string;
}

export interface TelegramCallbackQuery {
  id: string;
  from: TelegramUser;
  data?: string;
  message?: TelegramMessage;
}

export interface TelegramUpdate {
  update_id: number;
  message?: TelegramMessage;
  callback_query?: TelegramCallbackQuery;
}
