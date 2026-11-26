# Nolane Media Node (self-hosted, no subscription)

The node runs yt-dlp and FFmpeg on your own Windows computer. Nolane Search's existing Cloudflare Worker authenticates the owner and streams completed files. Media bytes never enter D1, R2, GitHub Artifacts or a cloud bucket.

## Requirements

- Windows 10 or Windows 11.
- Python 3.12 with the py launcher.
- Node.js 22 or newer.
- FFmpeg available as ffmpeg.exe on PATH.
- Tailscale installed and signed in to a Personal tailnet.
- Windows Defender Firewall enabled for all network profiles.
- This is designed for one personal, non-commercial owner. Tailscale Personal's free plan is not for commercial use.

## Install

1. Install Python 3.12, Node.js 22, FFmpeg and Tailscale from their official sources. The script does not download or install third-party software for you.
2. Open PowerShell as Administrator in this folder.
3. Run: Set-ExecutionPolicy -Scope Process Bypass -Force
4. Run: .\install.ps1

The installer creates a Python virtual environment, installs pinned yt-dlp packages, generates a 256-bit random local secret, installs outbound Windows Firewall blocks for Python/FFmpeg/Node to private and special-use address ranges, verifies those rules, and registers a per-user logon task. It does not open an inbound router port.

If firewall profiles are disabled or any protection cannot be installed and verified, setup stops. Do not enable Funnel until the firewall rules are present.

## Enable the public HTTPS tunnel

After the task has started, verify the local service from PowerShell:

    Get-ScheduledTask -TaskName "Nolane Media Node"
    Get-Content .\data\media-node.log -Tail 20

Run the Tailscale CLI command:

    tailscale funnel --bg --https=443 http://127.0.0.1:8765

Tailscale displays or prompts for the Funnel URL. It must be an HTTPS hostname ending in .ts.net. Check the status:

    tailscale funnel status

Funnel is a public internet endpoint, not a private tailnet-only endpoint. Only the token-authenticated API is exposed. The Python service itself binds to 127.0.0.1, not 0.0.0.0. Do not change this binding.

Tailscale Funnel is beta and its bandwidth limits are non-configurable. The official docs do not publish a numeric throughput guarantee. Large file shares may therefore be slow or capped. This is not an unlimited CDN.

## Connect Nolane Search

Read the local secret without sharing the .env file:

    (Get-Content .\.env | Where-Object { $_ -match '^NOLANE_INTERNAL_TOKEN=' }).Split('=',2)[1]

In the GitHub repository Settings, add these Actions secrets:

- MEDIA_NODE_URL: the HTTPS Funnel URL, for example https://computer.tailnet.ts.net
- MEDIA_NODE_TOKEN: the 64-character secret from .env

Keep the token private. Do not put it in source code, an issue, a PR, a screenshot or a chat message. After saving the two secrets, run the existing Cloudflare deploy workflow from the repository Actions tab. The workflow uploads the optional secrets to the existing Worker; when either is absent, Media Studio remains disabled.

No paid Cloudflare plan, R2 bucket or GitHub Actions runtime is used by the downloader. GitHub Actions remains CI/CD only.

## Operation

- Start now: Start-ScheduledTask -TaskName "Nolane Media Node"
- Stop: Stop-ScheduledTask -TaskName "Nolane Media Node"
- Status: Get-ScheduledTask -TaskName "Nolane Media Node"
- Funnel status: tailscale funnel status
- Disable public ingress: tailscale funnel --https=443 off
- Uninstall service/rules: .\uninstall.ps1 (Administrator)
- Also delete local job database and media: .\uninstall.ps1 -RemoveData (Administrator)

The local database and media are stored under media-node\data. Completed media expires after 12 hours; unshared, cancelled and failed job metadata is periodically cleaned. The computer must remain powered on, connected to the Internet and signed in for new downloads and playback. Sleep, shutdown, ISP limits, upload speed and Funnel limits affect availability.

## Security model

- Every Worker-to-node call uses an independent 256-bit secret and owner ID.
- Every internal route, including health, requires that secret.
- Share URLs use random 256-bit tokens; only their SHA-256 hashes are stored locally.
- Source URLs are validated by both Worker and node, and every DNS answer must be globally routable.
- Windows Firewall outbound rules block private, loopback, link-local, CGNAT and special-use ranges for Python, FFmpeg and Node. Redirects to those ranges should therefore fail at the network layer too.
- No browser cookies, credentials, paywall or DRM bypass, playlists or generic proxy.
- Download subprocesses are bounded by duration, output size, wall time and concurrency. Logs do not record source URLs or tokens.
- Temporary share links expire after 12 hours and can be revoked.

If the computer's firewall rules are removed, do not keep Funnel enabled. Run install.ps1 again to recreate and verify the rules.
