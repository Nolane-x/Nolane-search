# Wave 56 research — Internet Archive public audio discovery

Date: 2026-11-24
Repository: https://github.com/Nolane-x/Nolane-search
Branch: feat/wave-56-internet-archive-audio

## Product intent

Extend the authenticated Media Portal and AI discovery catalog from images/video to public audio. Focus on recordings, lectures, speeches, public talks, music archive items and other audio material. This is discovery and playback of existing Internet Archive assets, not a user-file host or a general third-party downloader.

## Official source and metadata model

Internet Archive metadata documentation:
https://internetarchive.readthedocs.io/en/stable/metadata.html

Internet Archive metadata API reference:
https://internetarchive.readthedocs.io/en/stable/api.html

Internet Archive CLI/API documentation:
https://internetarchive.readthedocs.io/en/stable/cli.html

The Archive's metadata model defines `mediatype=audio` for the majority of audio items and `mediatype=movies` for video. Live Music Archive items may use the distinct `etree` mediatype; this first integration does not query `etree` because it has separate upload/metadata conventions.

## New tool

`search_internet_archive_audio`:
- Uses the official Advanced Search endpoint with a bounded query for `mediatype:audio`.
- Caps result discovery to five item IDs per request.
- Calls the official per-item metadata endpoint only for validated identifiers.
- Returns a playable direct link only when the item declares `mediatype=audio` and includes a listed, non-private original audio file with a supported file extension and a matching audio format.
- Supported original formats include MP3, M4A, Ogg/OGA, Opus, FLAC, WAV, AAC and AIFF.
- Prefers MP3, then Ogg/Opus, then M4A/AAC, then other supported lossless formats; smaller files are preferred only within an equal format-priority class.
- Returns the original item URL, archive preview image, creator, description, date and rights/license metadata when present.

## Access and rights protections

- Explicit `access-restricted-item`, `access-restricted` and `noindex` items are omitted.
- Files marked `private` are omitted.
- Files explicitly marked as derivatives are omitted; only an original file or a file with no derivative marker is considered.
- Metadata item IDs are constrained to a safe identifier alphabet before API calls.
- Filenames with slash, backslash, control characters, dot traversal names or excessive length are omitted.
- A matching extension alone is insufficient: the Archive file-format metadata must also identify audio.
- Rights are item-specific and may be absent or incomplete. The feature does not infer public-domain status from playback availability. Users should inspect the item page and rights field before reusing or redistributing material.
- Nolane links directly to archive.org; it does not download or rehost the audio.

## Media Portal changes

- Adds an Audio tab and audio-only filter.
- Adds an HTML audio player with controls and metadata preload; it does not autoplay.
- Adds an audio badge and original-audio link.
- The archive.org media host was already permitted for Internet Archive video and remains the only host used for Archive media.
- When "all media" is selected, the API independently queries Commons/Openverse/NASA images, NASA/Internet Archive videos and Internet Archive audio. Provider failures remain isolated and visible as warnings.

## Explicitly not included

- Does not enable downloading arbitrary third-party video/audio sites through yt-dlp or gallery-dl.
- Does not bypass DRM, paywalls, login requirements or access controls.
- Does not copy audio bytes to Cloudflare R2 or Telegram.
- Does not implement private user upload/share links; the Cloudflare account still returns R2 activation error 10042.
- Does not query `etree` Live Music Archive items in this first version.

## Validation

Mocked tests cover:
- Advanced Search query and bounded result count.
- Metadata lookup and `mediatype=audio`.
- Selection of a listed original MP3.
- Omission of restricted items, private files, derivatives and non-audio formats.
- AI tool registration and dispatch.

CI verifies types, tests, the file processor runner and Worker build. This is not a guarantee that each live Archive item is playable or that its rights statement permits redistribution.
