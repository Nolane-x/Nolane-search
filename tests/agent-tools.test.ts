import { afterEach, describe, expect, it, vi } from "vitest";
import { executeAgentTool, AGENT_TOOL_DEFINITIONS, runAgentLoop } from "../src/agent-tools";
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
    expect(result.length).toBeGreaterThanOrEqual(45);
    expect(result.some(tool => tool.id === "video-compress")).toBe(true);
  });

  it("exposes Developer and Repository categories to the AI tool-discovery interface", async () => {
    const definition = AGENT_TOOL_DEFINITIONS.find(tool => tool.function.name === "list_nolane_tools");
    const schema = definition?.function.parameters as { properties?: { category?: { enum?: string[] } } };
    expect(schema.properties?.category?.enum).toEqual(expect.arrayContaining(["developer", "repository"]));
    const repository = JSON.parse(await executeAgentTool(env, "list_nolane_tools", { category: "repository" })) as Array<{id:string}>;
    expect(repository.some(tool => tool.id === "repo-security-audit")).toBe(true);
    expect(repository.some(tool => tool.id === "repo-supply-chain")).toBe(true);
    const developer = JSON.parse(await executeAgentTool(env, "list_nolane_tools", { category: "developer" })) as Array<{id:string}>;
    expect(developer.some(tool => tool.id === "code-imports")).toBe(true);
  });

  it("formats JSON and cleans text through bounded processor calls", async () => {
    const formatted = await executeAgentTool(env, "process_text_content", {tool_id:"json-format",content:'{"b":2,"a":1}'});
    expect(formatted).toBe("{\n  \"b\": 2,\n  \"a\": 1\n}");
    const cleaned = await executeAgentTool(env, "process_text_content", {tool_id:"text-clean",content:"Cafe\u0301  \u200b\r\n\n\nline"});
    expect(cleaned).toBe("Café\n\nline");
  });

  it("runs new everyday text, extraction, encoding and JSON utilities", async () => {
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-uppercase",content:"Xin chào"})).toBe("XIN CHÀO");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-reverse-lines",content:"first\nsecond\nthird"})).toBe("third\nsecond\nfirst");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-emails",content:"A@Example.com and a@example.com"})).toBe("A@Example.com");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"url-encode",content:"xin chào"})).toBe("xin%20ch%C3%A0o");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"url-decode",content:"xin%20ch%C3%A0o"})).toBe("xin chào");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"json-sort-keys",content:'{"z":1,"a":{"y":2,"b":3}}'})).toBe('{\n  "a": {\n    "b": 3,\n    "y": 2\n  },\n  "z": 1\n}');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"language-detect",content:"Xin chào, tôi là người Việt Nam"})).toContain("Vietnamese");
    const schema=AGENT_TOOL_DEFINITIONS.find(tool=>tool.function.name==="process_text_content")?.function.parameters as {properties?:Record<string,unknown>};
    expect(schema.properties?.target_language).toBeDefined();
  });

  it("runs the second wave of slug, data extraction, casing, masking and JSONL processors", async () => {
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-slugify",content:"Xin Chào Đặng\nHello World"})).toBe("xin-chao-dang\nhello-world");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-snake-case",content:"Hello World\nXML Parser"})).toBe("hello_world\nxml_parser");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-kebab-case",content:"Hello World"})).toBe("hello-world");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-camel-case",content:"Hello World"})).toBe("helloWorld");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-reverse-characters",content:"abc\nxin"})).toBe("cba\nnix");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-word-frequency",content:"One two one"})).toContain("one\t2");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-numbers",content:"x=-12, 3.14 and 3.14"})).toBe("-12\n3.14");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-dates",content:"2024-02-29 and 31/02/2024"})).toBe("2024-02-29");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-ipv4",content:"192.168.1.1 and 999.1.1.1"})).toBe("192.168.1.1");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-mask-emails",content:"Contact user@example.com"})).not.toContain("user@example.com");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-mask-phones",content:"Call 0912345678"})).not.toContain("0912345678");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-swap-case",content:"HeLLo"})).toBe("hEllO");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-remove-emoji",content:"Hello 😀 world"})).toBe("Hello  world");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"json-to-jsonl",content:'[{"a":1},{"b":2}]'})).toBe('{"a":1}\n{"b":2}');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"jsonl-to-json",content:'{"a":1}\n{"b":2}'})).toBe('[\n  {\n    "a": 1\n  },\n  {\n    "b": 2\n  }\n]');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-to-tsv",content:'name,note\nAn,"hello, world"'})).toBe("name\tnote\nAn\thello, world");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"tsv-to-csv",content:"name\tnote\nAn\tworld"})).toBe("name,note\nAn,world");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-to-markdown",content:"name,score\nAn,7"})).toContain("| An | 7 |");
  });

  it("runs the third wave of text cleanup, extraction, CSV and JSON helpers", async () => {
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-collapse-whitespace",content:" a   b  \n c "})).toBe("a b\nc");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-remove-punctuation",content:"hello,world! nice-day"})).toBe("hello world nice day");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-to-ascii",content:"Đặng café"})).toBe("Dang cafe");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-html-escape",content:'<b a="x">'})).toBe("&lt;b a=&quot;x&quot;&gt;");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-html-unescape",content:"&lt;b&gt;Hi&amp;bye&lt;/b&gt;"})).toBe("<b>Hi&bye</b>");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-mentions",content:"@Nolane @Nolane user@example.com @helper"})).toBe("@Nolane\n@helper");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-hex-colors",content:"color #abc and #AABBCC #abc"})).toBe("#ABC\n#AABBCC");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-phones",content:"Call +84 912 345 678"})).toBe("+84 912 345 678");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-dedupe-lines",content:"One\nTwo\none\n"})).toBe("One\nTwo\n");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-count-report",content:"one two\nthree"})).toContain("Words: 3");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-quote-lines",content:"one\ntwo"})).toBe('"one"\n"two"');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-unquote-lines",content:'"one"\n"two"'})).toBe("one\ntwo");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-transpose",content:"a,b\n1,2\n3,4"})).toBe("a,1,3\nb,2,4");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-sort-rows",content:"name,score\nB,2\nA,1"})).toBe("name,score\nA,1\nB,2");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-dedupe-rows",content:"name,score\nA,1\na,1\nB,2"})).toBe("name,score\nA,1\nB,2");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-to-xml",content:'name,note\nAn,"<script>"'})).toContain("&lt;script&gt;");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-to-html",content:'name,note\nAn,"<script>"'})).toContain("&lt;script&gt;");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"json-sort-array",content:'[{"z":1},{"a":2}]'})).toBe('[\n  {\n    "a": 2\n  },\n  {\n    "z": 1\n  }\n]');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"json-remove-nulls",content:'{"a":null,"b":[1,null,{"x":null,"y":2}] }'})).toBe('{\n  "b": [\n    1,\n    {\n      "y": 2\n    }\n  ]\n}');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"json-to-html-table",content:'[{"name":"<script>","score":7}]'})).toContain("&lt;script&gt;");
  });

  it("runs third-wave AI cleanup, extraction, CSV and JSON processors", async () => {
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-collapse-whitespace",content:" a   b  \n c "})).toBe("a b\nc");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-remove-punctuation",content:"hello,world! nice-day"})).toBe("hello world nice day");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-to-ascii",content:"Đặng café"})).toBe("Dang cafe");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-html-escape",content:'<b a="x">'})).toBe("&lt;b a=&quot;x&quot;&gt;");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-html-unescape",content:"&lt;b&gt;Hi&amp;bye&lt;/b&gt;"})).toBe("<b>Hi&bye</b>");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-mentions",content:"@Nolane @Nolane user@example.com @helper"})).toBe("@Nolane\n@helper");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-hex-colors",content:"color #abc and #AABBCC #abc"})).toBe("#ABC\n#AABBCC");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-phones",content:"Call +84 912 345 678"})).toBe("+84 912 345 678");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-dedupe-lines",content:"One\nTwo\none\n"})).toBe("One\nTwo\n");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-count-report",content:"one two\nthree"})).toContain("Words: 3");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-quote-lines",content:"one\ntwo"})).toBe('"one"\n"two"');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-unquote-lines",content:'"one"\n"two"'})).toBe("one\ntwo");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-transpose",content:"a,b\n1,2\n3,4"})).toBe("a,1,3\nb,2,4");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-sort-rows",content:"name,score\nB,2\nA,1"})).toBe("name,score\nA,1\nB,2");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-dedupe-rows",content:"name,score\nA,1\na,1\nB,2"})).toBe("name,score\nA,1\nB,2");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-to-xml",content:'name,note\nAn,"<script>"'})).toContain("&lt;script&gt;");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-to-html",content:'name,note\nAn,"<script>"'})).toContain("&lt;script&gt;");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"json-sort-array",content:'[{"z":1},{"a":2}]'})).toBe('[\n  {\n    "a": 2\n  },\n  {\n    "z": 1\n  }\n]');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"json-remove-nulls",content:'{"a":null,"b":[1,null,{"x":null,"y":2}] }'})).toBe('{\n  "b": [\n    1,\n    {\n      "y": 2\n    }\n  ]\n}');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"json-to-html-table",content:'[{"name":"<script>","score":7}]'})).toContain("&lt;script&gt;");
  });

  it("runs fourth-wave naming, Markdown, JSON and CSV processors", async () => {
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-pascal-case",content:"hello world\nXML parser"})).toBe("HelloWorld\nXmlParser");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-constant-case",content:"hello world"})).toBe("HELLO_WORLD");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-dot-case",content:"hello world"})).toBe("hello.world");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-initials",content:"Open AI\nNolane Search"})).toBe("OA\nNS");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-normalize-unicode",content:"Cafe\u0301"})).toBe("Café");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-remove-control-chars",content:"A\u0000B\nC"})).toBe("AB\nC");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-remove-duplicate-words",content:"One one two TWO three"})).toBe("One two three");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-markdown-links",content:'[Site](https://example.com "Example")'})).toContain('"url":"https://example.com"');
    const fence=String.fromCharCode(96).repeat(3);
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-markdown-headings",content:"# Title\n"+fence+"\n# Hidden\n"+fence+"\n## Sub"})).toContain('"text":"Sub"');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-quotes",content:'Say "hello" and “world”'})).toBe("hello\nworld");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-paragraph-report",content:"one two\n\nthree"})).toContain("Paragraphs: 2");

    const flat=await executeAgentTool(env,"process_text_content",{tool_id:"json-flatten",content:'{"a":{"b":1,"x/y":2},"items":[1,2]}'}); 
    expect(flat).toContain('"/a/b": 1');
    expect(flat).toContain('"/a/x~1y": 2');
    const restored=await executeAgentTool(env,"process_text_content",{tool_id:"json-unflatten",content:flat});
    expect(JSON.parse(restored)).toEqual({a:{b:1,"x/y":2},items:[1,2]});
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"json-keys-report",content:'{"a":{"b":1},"items":[{"c":2}]}'})).toContain("$.items[0].c");

    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-remove-empty-rows",content:"name,score\nAn,7\n,\nB,8"})).toBe("name,score\nAn,7\nB,8");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-add-row-numbers",content:"name,score\nAn,7"})).toBe("_row_number,name,score\n1,An,7");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-column-stats",content:"name,score\nAn,7\nB,8"})).toContain('"numeric":2');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-normalize-headers",content:"First Name,Score,First Name\nAn,7,B"})).toContain("first_name,score,first_name_2");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-to-jsonl",content:"name,score\nAn,7\nB,8"})).toBe('{"name":"An","score":"7"}\n{"name":"B","score":"8"}');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"jsonl-to-csv",content:'{"name":"An","score":7}\n{"name":"B","extra":true}'})).toBe("name,score,extra\nAn,7,\nB,,true");
  });

  it("runs fifth-wave text, HTML, JSON and CSV processors", async () => {
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-indent-lines",content:"alpha\n\nbeta"})).toBe("    alpha\n\n    beta");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-unindent-lines",content:"    alpha\n        beta\n    gamma"})).toBe("alpha\n    beta\ngamma");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-dedupe-paragraphs",content:"One paragraph.\n\none   paragraph.\n\nSecond."})).toBe("One paragraph.\n\nSecond.");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-tokenize-words",content:"Hello, world! I'm here."})).toBe("Hello\nworld\nI'm\nhere");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-sentence-report",content:"One sentence. Two words here!"})).toContain("Sentences (heuristic): 2");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-line-length-report",content:"a\nlongest line\nbb"})).toContain("Longest line: 12");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-normalize-newlines",content:"a\r\nb\rc"})).toBe("a\nb\nc");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-remove-zero-width",content:"a\u200bb\u200dc\ufeff"})).toBe("abc");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-extract-file-paths",content:"See /var/log/app.log and /home/user/a.txt"})).toContain("/var/log/app.log");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"text-sort-words",content:"pear Apple banana"})).toBe("Apple\nbanana\npear");

    const html='<html><head><title>Example &amp; Demo</title></head><body><a href="https://example.com" title="Home">Example</a><img src="/img/a.png" alt="A"></body></html>';
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"html-extract-links",content:html})).toContain('"url":"https://example.com"');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"html-extract-images",content:html})).toContain("/img/a.png");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"html-extract-title",content:html})).toBe("Example & Demo\n");

    expect(await executeAgentTool(env,"process_text_content",{tool_id:"json-to-xml",content:'{"person":{"@id":"7","name":"An","tags":["a","b"]}}'})).toContain('<person id="7">');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"json-type-report",content:'{"a":[1,true,null]}'})).toContain("Maximum depth: 2");
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"json-escape-string",content:'hello "world"'})).toBe('"hello \\"world\\""');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"json-unescape-string",content:'"hello \\"world\\""'})).toBe('hello "world"');
    expect(await executeAgentTool(env,"process_text_content",{tool_id:"csv-unique-values",content:"Name,Team\nAn,A\nAn,B\nBình,A"})).toContain('"count":2');
  });

  it("routes AI tool-call translation through the configured translation model", async () => {
    const fetchMock=vi.fn(async (_input:RequestInfo|URL,init?:RequestInit)=>{
      const body=JSON.parse(String(init?.body)) as {messages:Array<{role:string;content:string}>};
      expect(body.messages[0]?.content).toContain("professional translator");
      expect(body.messages[1]?.content).toContain("Hello world");
      return new Response(JSON.stringify({
        choices:[{message:{content:"Bonjour le monde"}}],
      }),{status:200});
    });
    vi.stubGlobal("fetch",fetchMock);
    const config={
      strategy:"priority",
      providers:[{
        id:"agent-translation",
        protocol:"openai-compatible",
        baseUrl:"https://api.example.ai/v1",
        apiKey:"agent-translation-secret",
        models:[{id:"translation-model",tasks:["translation"]}],
      }],
    };
    const result=await executeAgentTool({
      ...env,AI_ROUTER_CONFIG:JSON.stringify(config),
    } as Env,"process_text_content",{
      tool_id:"text-translate",target_language:"French",content:"Hello world",
    });
    expect(result).toBe("Bonjour le monde");
    expect(fetchMock).toHaveBeenCalledTimes(1);
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
