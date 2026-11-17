# Operations

## Commands

| Command | Description |
|---|---|
| /start | Start bot |
| /id | Show numeric Telegram user ID |
| /help | Show commands |
| /status | Provider configuration and index counters |
| /search query | General web search |
| /tech query | Technology + GitHub search |
| /github query | GitHub repository search |
| /ai prompt | Direct AI request through the multi-provider router |
| /ask question | Web search followed by AI evidence synthesis |
| /ai_status, /models | AI provider/key-route and model configuration overview |
| /wiki query | Free English/Vietnamese Wikipedia reference search |
| /wiki query | Free English/Vietnamese Wikipedia reference search |
| /research query | Research discovery |
| /news query | News search |
| /deep question | Queue multi-query research |
| /site example.com query | Provider site-restricted query |
| /local query | Search indexed page extracts |
| /watch https://example.com | Monitor public HTTPS page |
| /watches | List active watches |
| /unwatch 12 | Disable watch ID 12 |
| /jobs | List the latest eight Deep Search jobs |
| /retry JOB_ID | Re-enqueue a failed Deep Search query as a new job |

Plain text messages are treated as /search. Search results show five items per page and up to 12 candidates; pagination sessions are user/chat-bound and expire after 15 minutes.

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

## Cloudflare resources

- Worker: nolane-search
- URL: https://nolane-search.nolane-file.workers.dev
- D1: nolane-search-db
- Queue: nolane-search-jobs
- Dead-letter Queue: nolane-search-dlq
- Cron: every 30 minutes

D1 stores small operational records and a compact index. Search cache expires after two minutes and is pruned by scheduled maintenance. Telegram update IDs are pruned after seven days. Completed/failed Deep Search job records are pruned after 30 days; queued/running jobs are retained.

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
