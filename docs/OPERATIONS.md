# Operations

## Commands

| Command | Description |
|---|---|
| /start, /menu | Open the interactive inline dashboard |
| /id | Show numeric Telegram user ID |
| /cancel | Cancel the selected one-shot input mode and return to the dashboard |
| /help | Show commands |
| /status | Provider configuration and index counters |
| /search query | General web search |
| /tech query | Technology + GitHub search |
| /github query | GitHub repository search |
| /ai prompt | Direct AI request through the multi-provider router |
| /ask question | Web search followed by AI evidence synthesis |
| /ai_status, /models | AI provider/key-route and model configuration overview |
| /wiki query | Free English/Vietnamese Wikipedia reference search |
| /research query | Research discovery |
| /news query | News search |
| /deep question | Queue multi-query research |
| /site example.com query | Provider site-restricted query |
| /local query | Search indexed page extracts |
| /watch https://example.com | Monitor public HTTPS page |\n| /crawl https://example.com [1-20] | Crawl a bounded public website into the private FTS5 index |\n| /crawls | List recent site indexing jobs |
| /watches | List active watches |
| /unwatch 12 | Disable watch ID 12 |
| /archive [query] | Search the first page of archived website snapshots by title or URL |
| /archive_page 2 [query] | Browse another page; five snapshots are shown per page |
| /archive_restore 12 | Copy an archived snapshot document back into the private chat |
| /jobs | List the latest eight Deep Search jobs |
| /retry JOB_ID | Re-enqueue a failed Deep Search query as a new job |

`/start` and `/menu` open the interactive Telegram dashboard. Tap a mode, then send the question as the next plain-text message; the selected mode is consumed once and expires after 10 minutes. `/cancel` returns to the dashboard. Plain text without a selected mode still defaults to `/search`. The Telegram webhook must subscribe to both `message` and `callback_query`; `scripts/set-webhook.mjs` verifies this after `setWebhook` using `getWebhookInfo`. Callback taps are acknowledged before D1 operations. Search results show five items per page and up to 20 candidates; result messages include inline actions for source-grounded AI and Deep Search. Search sessions are user/chat-bound and expire after 15 minutes. Pagination and menu navigation edit existing messages where possible.

## Search operators

- `site:example.com` limits results to the specified domain and its subdomains.
- `filetype:pdf` filters results whose URL path ends with `.pdf`.
- `intitle:workers` requires all specified tokens to occur in the result title.
- `after:2026-01-10` accepts published timestamps from 2026-01-11 onward; `before:2026-02-01` accepts timestamps before 2026-02-01. Combined, they define a strict date interval.
- Date filters exclude results without a parseable publication timestamp. Only ISO `YYYY-MM-DD` dates are currently accepted.

Examples: `/search cloudflare site:developers.cloudflare.com`, `/search workers filetype:pdf`, `/search cloudflare intitle:workers`, `/search AI after:2026-01-10 before:2026-02-01`.

## Result delivery and archive

- Search results go to the conversation where the query was sent. Up to 12 ranked candidates are displayed five per page; inline Previous/Next buttons edit the same message. Sessions expire after 15 minutes and are bound to the requesting Telegram user and chat.
- If TELEGRAM_ARCHIVE_CHAT_ID is configured, search and Deep Search results are copied to the archive channel.
- Page snapshots are sent as TXT documents on first capture and detected content changes.
- Every successful snapshot upload records its Telegram channel/message and file references plus URL, title, watch ID, capture time and SHA-256 in D1. The original content remains a Telegram document; D1 stores metadata only.
- A watch only advances its `content_hash` and HTTP validators after the configured Telegram archive upload and D1 metadata index succeed. On failure, it keeps the old hash, clears ETag/Last-Modified, sets status `archive pending` and retries with a full fetch on the next scheduled check. This prevents a later HTTP 304 from silently skipping a snapshot that failed to upload.
- `/watches` labels these records as `archive pending · retry scheduled`. The user receives one warning for the initial failure; a normal change alert is sent once the snapshot is successfully indexed.
- `/archive [query]` searches the signed-in owner's snapshots by title or URL, showing five items per page. Use `/archive_page PAGE [query]` to move between pages; the next/previous commands preserve the current search query. The archive query API currently caps its offset at 5,000 rows. `/archive_restore ID` uses Telegram `copyMessage` to resend the original archived document; it does not rebuild content from D1.
- The archive index is owner-scoped. A snapshot can be restored only while the source channel message still exists and the bot retains channel access. Deleting a watch does not delete its historical snapshots.
- Change alerts go to the requesting chat and archive.
- Archive delivery failures are logged; direct search replies still go to the user.

## Scheduled monitoring

- Cron runs every 30 minutes.
- Each invocation checks at most 12 due pages sequentially.
- Minimum watch interval is 30 minutes.
- ETag and Last-Modified are used where available.
- Content hash detects changes when validators are absent or unreliable.
- First successful capture is a baseline and does not send a change alert.
- Non-2xx or unsupported content types are recorded as status, not indexed as page content.
- Before fetching a watched page, the Worker reads the origin's robots.txt and applies the NolaneSearchBot/wildcard rules. Disallowed pages are skipped. 401/403/429, 5xx or robots-fetch failures defer the watch; /watches labels these as robots disallow or robots unavailable. The parser handles core Allow/Disallow, wildcard and end-anchor rules; it does not implement every robots.txt extension such as Crawl-delay. Do not add sources that forbid automated access or require login.

- When Telegram snapshot archiving is configured, the watch's prior content hash remains authoritative and HTTP validators are cleared until both the Telegram document upload and D1 archive index succeed. Failures retain `last_status = -4`; a later scheduled check performs a full fetch and retries.
- A private change-alert delivery failure after the archive/index has succeeded is logged independently. It must not roll back the committed hash or mark the snapshot pending again; this avoids duplicate captures caused only by notification outages.
- The channel announcement is a separate best-effort delivery. Searchable archive metadata is committed independently from that announcement.
- Change detection compares the existing SHA-256 body hash plus the title stored in the previous `indexed_pages` row. A title-only edit is treated as a change without changing the stored hash format or requiring a migration.
- When no archive channel is configured, a detected change still produces a private notification but explicitly says no snapshot was saved; the Worker must not imply that a Telegram archive document exists.

## Search quotas and provider errors

- /search tries Tavily first. If Tavily fails or returns fewer than four results, it queries configured Exa, TinyFish and Brave providers plus the free Wikipedia reference API in parallel and merges available results. A healthy Tavily response with at least four hits avoids this fallback fan-out.
- /wiki directly searches Wikipedia: Vietnamese diacritics select vi.wikipedia.org; other queries use en.wikipedia.org. Treat it as an encyclopedia reference, not primary research or live reporting.
- /research calls configured Tavily and/or Exa providers.
- /tech calls GitHub and Tavily where configured.
- /github uses public GitHub API unless optional token is configured.
- /deep uses configured providers in parallel and may use OpenRouter.
- /jobs reads D1 job records; /retry only accepts a failed job owned by the requesting Telegram user.
- Main Queue delivery retries up to three times with increasing delay. Exhausted jobs arrive at the DLQ and are marked failed; the user can then retry them manually.
- Cron also checks for up to 10 stale queued/running jobs older than 10 minutes. It conditionally claims and re-enqueues them to recover from interrupted Worker executions. Recovery is bounded by the next 30-minute Cron invocation; it is not an exactly-once guarantee.
- Provider failures are returned as an error message; they are not represented as successful zero-result searches.

External search APIs have their own quotas and possible paid overages. Wikipedia uses the public MediaWiki Action API without a secret; requests include an identifying User-Agent and a short timeout. Monitor paid-provider dashboards.


## AI Router

- `AI_ROUTER_CONFIG` is a single encrypted Worker secret containing provider/key/model routes. The deployment workflow supplies an empty safe configuration if the owner has not added this secret yet.
- Each provider entry represents one API key. Multiple keys from one vendor must be separate entries with different `id` labels; they may share the same base URL and model list.
- Supported protocols: OpenAI-compatible Chat Completions, Anthropic Messages and Gemini Interactions. Custom endpoints must be public HTTPS.
- `balanced` rotates the starting candidate per Worker isolate; `priority` tries higher configured priority first; `cheapest` uses supplied per-model token prices. Each candidate is attempted at most once, up to `maxAttempts` (maximum 24).
- 429/5xx/auth/model errors, timeout or empty response moves to the next candidate. Failover does not guarantee that the rejected request is unbilled; check each provider's billing and quota.
- `/ai prompt` routes a direct prompt; task prefixes include `fast`, `reasoning`, `coding`, `creative`, `translation`, `research`, `summary` and `classification`.
- `/ask question` retrieves web evidence, asks the AI Router for an evidence-grounded synthesis and lists source links.\n- Browser search results include optional helpful/not-helpful votes. Votes are stored against a hashed exact query/mode and normalized URL; prior votes nudge that exact query's ranking slightly, with a hard cap of ±0.10. Search feedback events expire after 30 minutes and aggregate feedback entries after 180 days.
- `/ai_status` and `/models` show configured route labels, protocols and model IDs without exposing keys. Configuration status does not prove API-key validity; a real `/ai` request is required to test upstream access.
- Existing `OPENROUTER_API_KEY` and model variables remain a fallback route. Current production health reports one legacy OpenRouter key route and six model candidates until the owner adds their own `AI_ROUTER_CONFIG`.
- Cost fields produce estimates only; a durable cross-provider billing ledger is not implemented. Balanced rotation is not globally synchronized across Worker isolates.

## Cloudflare resources

- Worker: nolane-search
- URL: https://nolane-search.nolane-file.workers.dev
- D1: nolane-search-db
- Queue: nolane-search-jobs
- Dead-letter Queue: nolane-search-dlq
- Cron: every 30 minutes

D1 stores small operational records and a compact index. General search cache expires after two minutes (news is shorter and research longer) and is pruned by scheduled maintenance. Internal `search-event:`, `search-feedback:`, `search-vote:` and `site-crawl:` cache entries have dedicated retention windows and are excluded from the displayed cache count. Telegram update IDs are pruned after seven days. Completed/failed Deep Search job records are pruned after 30 days; queued/running jobs are retained.

## Debugging checklist

1. Check GitHub Actions deployment run.
2. Check GET /health.
3. Send /status in Telegram.
4. Verify provider secret and provider quota.
5. If Telegram does not respond, inspect Bot API getWebhookInfo.
6. Check Cloudflare Worker logs.
7. For stuck Deep Search, inspect /jobs, then Queue and DLQ metrics. Retry failed jobs with /retry JOB_ID.
8. For watch failures, inspect last status, response headers and site's crawling policy.

Never print secrets in logs. Avoid logging raw user content unless necessary for a specific diagnosis.

## Recovery

- Re-running deployment applies only unapplied D1 migrations.
- D1 rows are not deleted by code deployment.
- Telegram archive is a human-readable secondary archive, not an automatic full restore mechanism for watch metadata.
- If D1 operational data is lost, re-create watch definitions manually; archive snapshots survive only when archive was configured and delivery succeeded.


## Personal memory and AI cost controls

- Save only details you explicitly want the assistant to retain: `/remember [profile|preference|project|note] text`.
- Review the saved list with `/memories`; delete an entry with `/forget ID`.
- The store is capped at 50 entries per Telegram user, uses the existing D1 cache table and expires entries after five years. Memory is not automatically extracted from chat.
- Repeated AI Overview/`/ask` queries can reuse a short-lived answer cache. News/current queries expire after two minutes, research after five minutes and other modes after ten minutes.
- AI Router defaults to three failover routes per completion and clamps configured `maxAttempts` to six. Recently failing routes are temporarily skipped per Worker isolate.
- Browser chat passes at most eight valid recent turns / 8,000 aggregate characters to the model. Character limits are an approximation for context control, not an exact token count.
- These controls do not change provider prices or guarantee lower bills; inspect response usage fields when the selected provider reports token usage.


## Upstream response and redirect limits

- JSON responses from search providers and the Telegram Bot API are read with a streaming 1 MB decoded-byte cap. A too-large Content-Length is rejected early; chunked bodies are cancelled when the cap is crossed.
- Invalid or empty upstream JSON is treated as a provider/API failure and follows the existing fallback/error handling.
- Website Watch checks the configured site's robots.txt and refuses redirects to another origin. If a site redirects to a different hostname, the check is marked as a fetch failure; update the watch target to the canonical URL if appropriate.
- The selected-site crawler continues to allow only same-origin redirects, and redirect bodies are cancelled before the next request.
- TinyFish page extraction is matched back to the safe public URL actually requested. Its returned final URL is only used when it is itself a safe public HTTPS URL.


## Personal Web Index management

- In the private browser workspace, the Personal Web Index panel lists the most recently updated indexed pages. Filter by page title, URL or hostname and use the page/domain removal controls to prune the local index.
- Telegram: `/indexed [filter]` lists up to 15 matching indexed pages; `/unindex https://example.com/page` removes one normalized page; `/unindex_domain example.com` removes pages on the exact domain, its `www` host and subdomains.
- Removal deletes the corresponding FTS5 row and `indexed_pages` row in a single D1 batch. It also deactivates watches whose normalized URL is among the removed pages, preventing scheduled watch checks from immediately re-indexing those exact URLs.
- Removing a domain does not delete crawl-job history, Telegram archive snapshots or pages on unrelated domains. A crawl already running may still write pages after a deletion completes; refresh the index after the job finishes and remove again if necessary.
- This feature reuses existing D1 tables and needs no migration, new secret or additional Cloudflare resource.


## Single-owner usage and upstream quotas

Nolane Search is a private, single-owner service. It does not impose application-level per-minute request caps on Telegram commands or authenticated Web Workspace actions. Provider-side quotas, model access, upstream billing, Cloudflare platform limits and Queue capacity still apply.

Crawling remains bounded per job (up to 20 pages), rejects unsafe/private destinations, stays on the original public origin and respects robots.txt. These are safety and execution bounds for an individual crawl, not per-user request throttles.


## Nolane Tools runner

- The private Telegram bot accepts photos, documents, audio, voice messages, videos and animations from the allowlisted owner in the private chat.
- Photos automatically select Vietnamese/English OCR. Other uploads are mapped by MIME type and file extension. Use `/tool TOOL_ID` to arm an explicit tool for the next file, `/tools` to inspect the catalog, and `/tool_jobs` for recent task status.
- The Web Workspace Tools hub is a catalog and job-history view. For the first release, upload the actual file through Telegram; the browser page copies the corresponding `/tool` command.
- The Worker validates the selected registry entry, private-chat ownership, MIME/extension compatibility and the 20 MB Telegram input limit. It writes a D1 job record under `tool-job:` and dispatches only the opaque UUID to GitHub Actions.
- The runner fetches job metadata from a private Worker endpoint, downloads the Telegram file directly with `getFile`, processes it on an ephemeral Ubuntu GitHub-hosted runner and sends any output document back to the same chat. Inputs are not committed, uploaded as GitHub artifacts or stored in D1.
- Internal runner callbacks use the existing `TELEGRAM_WEBHOOK_SECRET` as a bearer secret. The workflow concurrency group is keyed by job ID; terminal job states and notification completion are tracked for 30 days in the existing D1 cache. After completion/failure, the Telegram `file_id` is cleared; the record keeps filename/MIME/size, task status and at most 6,000 characters of result summary.
- The Worker needs the optional GitHub Actions secret `GITHUB_ACTIONS_TOKEN`, a fine-grained PAT scoped only to this repo with repository `Actions: Read and write`. The deploy workflow uploads it as a hidden Worker secret. Without it, Search remains operational but Tools dispatch returns a setup message.
- No extra D1 migration, Cloudflare R2, KV, object storage or new Queue is needed.
- The catalog includes OCR (Vietnamese/English), image inspection/EXIF cleanup/compression/image-to-PDF/QR decoding, PDF text and scan OCR/PDF info, DOCX/PPTX/XLSX extraction, CSV profiling, JSON validation/formatting, ZIP/TAR inspection without extraction, Whisper audio transcription/audio metadata, video metadata/thumbnail, file hashes, TXT/Markdown cleanup, SRT/VTT transcript extraction, HTML text extraction, audio loudness normalization, video audio extraction and short video-to-GIF conversion.
