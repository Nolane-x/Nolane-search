# Wave 62 handoff — media download and storage

Date: 2026-11-25
Branch: `docs/wave-62-media-downloaders-and-storage-plan`
Base: `main`
Status: research/handoff only; no download engine is claimed as shipped.

## Main findings

- Existing Media Portal supports licensed images, public NASA MP4s, Internet Archive video/audio records and PeerTube origin links.
- OmniGet is a local desktop UI/MCP service; its useful engines are yt-dlp, gallery-dl, FFmpeg and aria2.
- The current yt-dlp release checked was `2026.11.23`; gallery-dl was `1.32.21` on PyPI/Codeberg.
- Downloader work needs a secure URL inspection phase, pinned toolchain and network egress/SSRF controls.
- Telegram getFile remains a 20 MB limit for the current bot runner.
- Private R2 multipart storage, signed owner-authorized sharing and HTTP Range playback are the intended design.
- R2 is not enabled in the connected Cloudflare account (error 10042). No bucket or credentials exist.
- Dailymotion currently needs a private API key for API v2. Odysee's public search endpoint works, but the tested output lacked reliable mature-content flags even with `nsfw=false`; it is not added to the default portal.

## Required owner action before full downloads

1. Open Cloudflare Dashboard → Storage & databases → R2 → Overview.
2. Complete R2 activation and create a private bucket named `nolane-search-media`.
3. Do not paste access keys or tokens into chat. Configure any required bucket credentials as repository/Worker secrets only after the bucket exists.

After R2 is active, add a Worker binding and implement the multipart endpoint, runner upload client, share-token validation and Range playback. Do not use GitHub Actions artifacts or public buckets as a substitute for private persistent media storage.

## Next coding phases

1. Implement protected URL inspection (yt-dlp + gallery-dl metadata only) after a reviewed runner egress strategy is ready.
2. Add bounded download jobs.
3. Implement R2 multipart upload, failure recovery and cleanup.
4. Add private share/player URLs and Range support.
5. Add live end-to-end tests with a small public/licensed test media asset and larger test-object fixture.
