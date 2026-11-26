# Zero-cost Media Node Implementation Plan

For agentic workers: implement the tasks inline through GitHub repository tools. Each task is a separate test-first commit.

Goal: Replace the paid Wave 73 Container prototype with an owner-only, self-hosted yt-dlp and FFmpeg Media Node connected to Nolane Search through the existing free Worker.

Architecture: A local Python service uses SQLite and bounded yt-dlp subprocesses. Tailscale Funnel exposes the loopback-only API. The Worker authenticates requests and streams media responses. GitHub Actions remains CI/CD only.

Tech Stack: Python 3.12 standard library, yt-dlp with yt-dlp-ejs, FFmpeg, Node.js 22, Windows Defender Firewall, Tailscale Personal/Funnel, Cloudflare Workers Free, TypeScript and Vitest.

Spec: docs/superpowers/specs/2026-11-26-zero-cost-media-node-design.md

## Global constraints

- No paid Workers, cloud runtime, R2, hosted media storage, or paid credits.
- The Media Node binds to 127.0.0.1:8765; only Tailscale Funnel is exposed.
- Worker requests require a valid session, private-chat owner identity and allowlist.
- Node requests require a 256-bit shared secret and owner ID.
- No cookies, browser profiles, login credentials, DRM/paywall bypass, playlists, or arbitrary proxy endpoints.
- One active downloader process; at most three queued or running jobs per owner.
- Source duration max 7,200 seconds; final output max 3 GiB; watchdog 30 minutes.
- Temporary file and share retention is 12 hours; HTTP Range and HEAD are required.
- GitHub Actions is CI/CD only, not an end-user downloader backend.
- Feature remains disabled until operator completes local installation and configures MEDIA_NODE_URL and MEDIA_NODE_TOKEN.

## Review focus

- DNS changes or redirects to loopback, metadata, private, link-local, CGNAT or IPv6 special-use addresses must not become SSRF.
- A stale running row after a crash must not duplicate a download after restart.
- Cancel or revoke concurrent with process completion must not restore a deleted share or file.
- Browser disconnects and Range retries must not buffer full media files or leak the internal token.
- Worker node URL configuration must not become an arbitrary outbound fetch primitive.

---

### Task 1: Media Node policy, persistent job store and worker

Files:
- Create media-node/server.py
- Create media-node/test_server.py
- Create media-node/requirements.txt

Interfaces:
- normalize_source_url(value, resolver=...) returns (normalized_url, host), or raises SourceUrlError.
- MediaNodeStore provides enqueue, claim_next, get_job, update_progress, complete, renew_share, authorize_share, request_cancel, revoke and recover_interrupted.
- build_ytdlp_command returns an argv array.
- parse_range returns a single byte interval or None.
- safe_output_file rejects symlinks and ambiguous output sets.
- create_http_server returns a loopback-bound HTTP server.

Steps:
- [x] Add tests for URL policy, DNS rejection, byte ranges, argument-array-only extraction, persistent jobs, owner boundaries, queue cap, share-token hash/expiry/revocation, symlink rejection and internal endpoint auth.
- [ ] Observe the new tests fail because the production implementation is absent.
- [ ] Implement URL/DNS policy, SQLite state, single-job worker, progress, cancellation/watchdog, output/file-size enforcement, token-protected API and streaming Range handler.
- [ ] Run the complete Python suite on Linux and Windows.

### Task 2: Worker-to-node adapter and route integration

Files:
- Replace src/media-downloader.ts with a minimal Media Node request builder.
- Modify src/index.ts, src/types.ts and cloudflare.config.ts.
- Create tests/media-downloader.test.ts.

Interfaces:
- isMediaNodeConfigured(env) returns boolean.
- createMediaNodeRequest(env, ownerId, path, init, timeoutMs) returns Request or null.
- Only validated HTTPS *.ts.net origins and fixed /internal routes may be called.
- Public watch/file routes pass share-token and Range headers and stream response bodies without buffering.

Steps:
- [x] Add tests for *.ts.net origin validation, strong token, secret and owner headers, path traversal rejection and Range preservation.
- [ ] Observe tests fail because the adapter does not yet exist.
- [ ] Implement adapter and replace DO/Container calls with the node API.
- [ ] Run npm test, npm run typecheck and Worker build.

### Task 3: Windows installation and network hardening

Files:
- Create media-node/install.ps1, start.ps1, uninstall.ps1, .env.example and README.md.
- Modify root .gitignore.

Steps:
- [ ] Check Windows, Python 3.12, Node 22, FFmpeg, Tailscale CLI and firewall readiness.
- [ ] Install pinned Python dependencies in a local virtual environment.
- [ ] Generate a random local token into ignored .env and register a per-user startup task.
- [ ] Install idempotent program-scoped firewall blocks for Python, FFmpeg and Node against non-public IPv4 and IPv6 ranges.
- [ ] Document Funnel setup, URL retrieval, startup, stop, removal and fault recovery.
- [ ] Validate PowerShell syntax in Windows CI; never change host firewall rules from CI.

### Task 4: UI, deployment workflow and documentation

Files:
- Modify src/media-ui.ts, tests/media-ui.test.ts, .github/workflows/deploy.yml and .github/workflows/ci.yml.
- Update the operator handoff and downloader research docs.

Steps:
- [ ] Replace paid-Container/snapshot copy with local Media Node, Tailscale Funnel and 12-hour local retention.
- [ ] Deploy optional MEDIA_NODE_URL and MEDIA_NODE_TOKEN secrets; absent values leave the UI disabled.
- [ ] Delete Container Docker/DO/Egress code and obsolete test shims.
- [ ] Preserve search providers, media discovery, HLS/DASH playback and Telegram features.

### Task 5: Verification and review

- [ ] Run full Python tests on Ubuntu and Windows.
- [ ] Run all TypeScript tests, type-check and default Worker build.
- [ ] Verify no active Container, Durable Object snapshot or R2 dependency remains in downloader code/config/CI.
- [ ] Review cancellation races, Range streaming, token redaction and DNS-rebinding defenses.
- [ ] Keep PR #149 as Draft; do not merge or deploy.
