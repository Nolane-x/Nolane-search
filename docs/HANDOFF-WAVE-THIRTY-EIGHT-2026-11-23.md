# Wave 38 — direct file attachments in Nolane Web Chat

Date: 2026-11-23  
Status: merged and deployed production release via [PR #91](https://github.com/Nolane-x/Nolane-search/pull/91).  
Main merge commit: `5bfe1160c84c0da2be9df4df37ae7ef52725b14b`.  
Worker Version ID: `a6e8b852-cad9-4f87-961b-35de6ac67cf6`.  
Main CI: [45195995372](https://github.com/Nolane-x/Nolane-search/actions/runs/45195995372).  
Worker export/build: [45195995222](https://github.com/Nolane-x/Nolane-search/actions/runs/45195995222).  
Cloudflare deploy: [45195995178](https://github.com/Nolane-x/Nolane-search/actions/runs/45195995178).  
Production base: Wave 37, catalog remains 462 processors.

## Goal

Wave 37 let AI prepare a private Telegram upload from normal chat, but the actual binary file still had to be sent manually in Telegram. Wave 38 adds an attachment control directly to the authenticated Web Workspace chat so the user can describe the task, choose a file and submit both together.

## User flow

1. Open the authenticated Nolane Web Workspace and select the file attachment control in Nolane Chat.
2. Enter a natural-language request, such as extracting text and tables from a PDF, cleaning a spreadsheet or converting a media file.
3. Submit once. The Worker checks the owner session, the matching private Telegram chat, prompt, file name, MIME hint and byte limit.
4. The Worker forwards the file to the owner's private Telegram chat using `sendDocument`, then uses the returned Telegram `file_id` with the existing AI file planner and job runner.
5. Web Chat receives the file name, actual job ID, planned pipeline and AI/fallback status. The completed job/result and AI synthesis are delivered to the paired private Telegram chat; the job also appears in Tool Center history.

## Implementation

- Added `uploadTelegramDocument` and a shared `TELEGRAM_PROCESSING_FILE_MAX_BYTES` constant (20 MiB). It uses Telegram multipart `sendDocument` and returns the validated file reference.
- Added same-origin, authenticated `POST /api/ai/upload` using `multipart/form-data`.
- The endpoint is restricted to a session whose Telegram `chatId` equals the allowed owner `userId`. Cross-origin requests and anonymous sessions are rejected before upload parsing.
- File names are reduced to a safe basename. Prompt control characters and empty/oversized input are rejected.
- The existing `handleAiFileUpload` is now shared by Telegram and Web upload routes and returns structured job metadata while preserving the Telegram progress message.
- The existing ready catalog, MIME checks, explicit pipeline transition graph, GitHub Actions runner and completion synthesis remain authoritative.
- No D1 schema change, new secret, permanent storage service or new processor is added.

## Limits

- Max upload: 20 MiB. The existing runner downloads Telegram-hosted input with a 20 MiB cap, so this remains the effective end-to-end limit even though Telegram's `sendDocument` endpoint can accept larger uploads.
- The Web upload is handed to Telegram, so the raw file is not stored in D1 or committed to GitHub. The runner downloads it for the job and processes it on an ephemeral GitHub Actions runner.
- Result completion is delivered through the paired private Telegram chat and Tool Center job history. Web Chat's immediate response is a job receipt, not a claim that processing has already completed.
- Browser-provided MIME metadata is only a hint; the Worker still validates catalog compatibility and pipeline edges. The uploaded file is untrusted input and no uploaded code is executed.

## Verification

PR CI run [45195143144](https://github.com/Nolane-x/Nolane-search/actions/runs/45195143144) passed TypeScript type-check, all 25 Vitest files / 260 tests, deployment-script checks, 354 Python runner tests and Cloudflare Worker build.

Deployment and actual owner-session upload acceptance are still pending. After merge, check Cloudflare deployment and `/health`. Owner should test representative non-sensitive PDF, image and media files via the browser attachment, then confirm returned artifact, job history and failure/retry handling in private Telegram. CI does not prove the real Telegram Bot API upload or owner-specific session flow.

## Catalog direction

This is an integration/usability wave only. The production catalog remains at 462 processors. Future catalog growth should favor accessible tools for images, documents, audio/video, daily utilities and learning instead of more specialist developer audits.
