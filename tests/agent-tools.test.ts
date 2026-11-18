import { afterEach, describe, expect, it, vi } from "vitest";
import { executeAgentTool, AGENT_TOOL_DEFINITIONS } from "../src/agent-tools";
import type { Env } from "../src/types";

afterEach(() => vi.unstubAllGlobals());
const env = { DB: {} as never, SEARCH_JOBS: {} as never } as Env;

describe("Nolane AI callable tools", () => {
  it("exposes the catalog as a real model-callable function", () => {
    expect(AGENT_TOOL_DEFINITIONS.map(tool => tool.function.name)).toEqual([
      "list_nolane_tools", "search_web", "read_web_page", "process_text_content", "hash_text",
    ]);
  });

  it("returns all registered file processors from the catalog tool", async () => {
    const result = JSON.parse(await executeAgentTool(env, "list_nolane_tools", {})) as Array<{id:string}>;
    expect(result.length).toBeGreaterThanOrEqual(38);
    expect(result.some(tool => tool.id === "video-compress")).toBe(true);
  });

  it("formats JSON and cleans text through bounded processor calls", async () => {
    const formatted = await executeAgentTool(env, "process_text_content", {tool_id:"json-format",content:'{"b":2,"a":1}'});
    expect(formatted).toBe('{
  "b": 2,
  "a": 1
}');
    const cleaned = await executeAgentTool(env, "process_text_content", {tool_id:"text-clean",content:"Cafe\u0301  \u200b\r\n\n\nline"});
    expect(cleaned).toBe("Café\n\nline");
  });

  it("cleans CSV safely and profiles columns", async () => {
    const source = "name,score\n A , 4 \nA,4\nB,";
    const cleaned = await executeAgentTool(env, "process_text_content", {tool_id:"csv-clean",content:source});
    expect(cleaned).toBe("name,score\nA,4\nB,");
    const profile = await executeAgentTool(env, "process_text_content", {tool_id:"csv-profile",content:source});
    expect(profile).toContain("Rows: 3");
    expect(profile).toContain("score: missing 1/3");
  });

  it("converts JSON arrays to CSV and extracts only visible HTML text", async () => {
    const csv = await executeAgentTool(env, "process_text_content", {tool_id:"json-to-csv",content:'[{"name":"An","score":7},{"name":"Bình","score":8}]'});
    expect(csv).toBe("name,score\nAn,7\nBình,8");
    const html = await executeAgentTool(env, "process_text_content", {tool_id:"html-text",content:"<script>secret()</script><h1>Hello &amp; hi</h1><p>World</p>"});
    expect(html).toBe("Hello & hi\nWorld");
  });

  it("normalizes subtitle text and computes a SHA-256 fingerprint", async () => {
    const subtitle = await executeAgentTool(env, "process_text_content", {tool_id:"subtitle-text",content:"WEBVTT\n\n00:00:01.000 --> 00:00:02.000\n<v Speaker>Hello</v>"});
    expect(subtitle).toBe("Hello");
    const hash = await executeAgentTool(env, "hash_text", {content:"hello"});
    expect(hash).toMatch(/^SHA-256: [a-f0-9]{64}$/);
  });

  it("runs native agent function calls and returns the final answer with tool provenance", async () => {
    const requests: Array<Record<string, unknown>> = [];
    const fetchMock = vi.fn(async (_input: RequestInfo | URL, init?: RequestInit) => {
      const body = JSON.parse(String(init?.body)) as Record<string, unknown>;
      requests.push(body);
      if (requests.length === 1) {
        return new Response(JSON.stringify({
          choices: [{ message: { content: null, tool_calls: [
            { id: "call_catalog", type: "function", function: { name: "list_nolane_tools", arguments: "{}" } },
          ] } }],
        }), { status: 200 });
      }
      const messages = body.messages as Array<{role:string;content:string}>;
      const toolResult = messages.find(message => message.role === "tool")?.content || "";
      expect(toolResult).toContain("pdf-split");
      expect(toolResult).toContain("audio-convert");
      return new Response(JSON.stringify({
        choices: [{ message: { content: "Nolane có catalog công cụ nâng cao." } }],
      }), { status: 200 });
    });
    vi.stubGlobal("fetch", fetchMock);
    const config = {
      strategy: "priority",
      providers: [{ id: "agent-test", protocol: "openai-compatible", baseUrl: "https://api.example.ai/v1",
        apiKey: "agent-test-secret", models: ["agent-model"] }],
    };
    const result = await runAgentLoop({
      ...env, AI_ROUTER_CONFIG: JSON.stringify(config),
    } as Env, {
      task: "chat", messages: [{role:"user",content:"Hãy liệt kê các công cụ dữ liệu."}],
    });
    expect(result.completion.text).toContain("Nolane có catalog");
    expect(result.toolsUsed).toEqual(["list_nolane_tools"]);
    expect(requests).toHaveLength(2);
    expect(requests[0]?.tool_choice).toBe("auto");
  });

  it("rejects arbitrary tools, invalid arguments and oversized content", async () => {
    await expect(executeAgentTool(env,"shell_exec",{command:"echo unsafe"})).rejects.toThrow("Unknown");
    await expect(executeAgentTool(env,"process_text_content",{tool_id:"code-check",content:"print(1)"})).rejects.toThrow("not enabled");
    await expect(executeAgentTool(env,"process_text_content",{tool_id:"json-format",content:"x".repeat(40_001)})).rejects.toThrow();
  });
});
