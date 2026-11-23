# Wave 37 — unified AI access to Nolane tools

Date: 2026-11-23  
Status: merged and deployed production release via [PR #90](https://github.com/Nolane-x/Nolane-search/pull/90).  
Main merge commit: `fb74281e75e72f16e33f2bcefe37d1b5938eabed`.  
Worker Version ID: `e2d45f4e-056d-42a8-afe8-b7447b7cd13a`.  
CI: [45183200600](https://github.com/Nolane-x/Nolane-search/actions/runs/45183200600).  
Export/health smoke: [45183200645](https://github.com/Nolane-x/Nolane-search/actions/runs/45183200645).  
Cloudflare deploy: [45183200619](https://github.com/Nolane-x/Nolane-search/actions/runs/45183200619).

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

## Verification evidence

Production main CI and deploy completed successfully:
- TypeScript type-check passed.
- Vitest: 25 files / 257 tests passed, including complete 462-ID pagination coverage, default consumer-first ordering, developer/repository reachability, context gating and a mocked real agent function-call round trip.
- Python runner: 354 tests passed, including catalog/runner/docs parity.
- Cloudflare Worker build passed.

Deployment succeeded, live health returned `ok: true`, database reachable and archive enabled; Telegram webhook and command menu registration passed. Owner-level acceptance remains necessary: test `/ai` asking for a PDF/image/audio/video operation, verify the agent arms the upload flow, send representative non-sensitive files in the same private Telegram chat, inspect returned artifacts and test job status/retry. CI does not prove real Bot API uploads or provider/model function-calling support.

## Current release baseline

Wave 37 is deployed to production. The catalog remains **462 tools** (no tools added in this integration wave). The latest deployed Worker Version ID is recorded above. Do not claim that actual private Telegram file upload/retry journeys have been owner-verified until representative real files are tested.
