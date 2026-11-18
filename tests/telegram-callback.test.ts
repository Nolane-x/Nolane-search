import { afterEach, describe, expect, it, vi } from "vitest";
import { processUpdate } from "../src/index";
import type { Env } from "../src/types";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("Telegram callback delivery", () => {
  it("acknowledges a dashboard button before the first D1 operation", async () => {
    const events: string[] = [];
    const env = {
      TELEGRAM_BOT_TOKEN: "test-token",
      ALLOWED_TELEGRAM_USER_IDS: "42",
      DB: {
        prepare() {
          const statement = {
            bind() { return statement; },
            async run() {
              events.push("d1:run");
              return { meta: { changes: 1 } };
            },
            async first() {
              events.push("d1:first");
              return null;
            },
            async all() {
              events.push("d1:all");
              return { results: [] };
            },
          };
          return statement;
        },
      },
    } as unknown as Env;

    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = new URL(String(input));
      const method = url.pathname.split("/").pop();
      events.push("telegram:" + method);
      return Response.json({ ok: true, result: true });
    }));

    await processUpdate(env, {
      update_id: 9001,
      callback_query: {
        id: "callback-test-1",
        from: { id: 42 },
        data: "ui:mode:ask",
        message: {
          message_id: 77,
          chat: { id: 42, type: "private" },
          text: "◈ NOLANE SEARCH",
        },
      },
    });

    expect(events[0]).toBe("telegram:answerCallbackQuery");
    expect(events[1]).toBe("d1:run");
    expect(events).toContain("telegram:editMessageText");
  });
});
