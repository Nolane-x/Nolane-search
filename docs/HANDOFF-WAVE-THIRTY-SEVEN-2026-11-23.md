# Wave 37 — unified AI access to Nolane tools

Date: 2026-11-23  
Status: implementation candidate in [PR #90](https://github.com/Nolane-x/Nolane-search/pull/90); not yet a production release.  
Base: `main` at `9b79de7f79bbb1c36f43fa380db03f3c51f0d6cc`.  
Branch: `feat/ai-unified-tool-access-wave37-20261123`.

## Goal

The production catalog already contains 462 registered processors, but direct AI chat could call only a small set of web/text functions. Binary and rich-file tools were reachable through the separate `/ai_file` flow. This wave connects the normal agent conversation to that workflow and makes the entire catalogue discoverable without returning one oversized JSON response.

## Changes

- `list_nolane_tools` now returns `total`, `offset`, `limit`, `nextOffset` and a bounded `tools` page. The default is 20 entries; callers can request up to 20 and continue using `nextOffset`. Every ready catalog entry is reachable via pagination, query or category.
- Discovery order prioritizes image, document, audio/video, utility and data tools. Developer and repository categories remain available, but the AI system instruction directs it to use them only for explicit technical work.
- `prepare_file_processing` is exposed only when the calling agent has an authorized private-chat callback. It validates the goal and arms the existing five-minute pending-upload record. It does not download a file or execute a processor.
- Both Telegram `/ai` and authenticated Web Workspace chat can arm the same private Telegram upload session. A browser-chat request still requires the user to upload the actual file through the paired private Telegram conversation.
- The upload planner's `process_uploaded_file` schema includes every ready tool ID from the catalog. It prioritizes everyday-user tasks and retains deterministic fallback when AI function calling is unavailable or a proposed pipeline fails validation.
- Existing owner/private-chat checks, MIME validation, transition graph, ephemeral GitHub Actions runner and result synthesis remain the execution boundary.

## Tool access boundaries

“Full access” means the AI can discover and select registered Nolane processors and call the explicitly exposed agent functions. It does not mean arbitrary shell or SQL execution, root privileges, direct access to the user's computer, private-network URL fetching, or execution of uploaded code. File processing begins only after an authorized user sends a file. The file and its embedded text remain untrusted data.

## Validation plan

PR CI must pass:
- TypeScript type-check
- Vitest, including complete 462-ID pagination coverage, default consumer-first ordering, developer/repository reachability, context gating and a mocked real agent function-call round trip
- Python runner tests and catalog/runner/docs parity
- Cloudflare Worker build

After merge, deployment workflow and production health must be checked separately. Owner-level acceptance remains necessary: test `/ai` asking for a PDF/image/audio/video operation, verify the agent arms the upload flow, send representative non-sensitive files in the same private Telegram chat, inspect returned artifacts and test job status/retry. CI does not prove real Bot API uploads or provider/model function-calling support.

## Current release baseline

The latest verified production catalog remains **462 tools (Wave 36)**. Wave 37 changes AI access/integration only; it does not increase the processor count. Do not describe Wave 37 as deployed until PR merge, Worker deployment and health smoke all pass.
