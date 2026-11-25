import { readJsonResponse } from "./http";

export interface ResolvedMediaEmbedItem {
  id: string;
  title: string;
  provider: "YouTube" | "Vimeo" | "PeerTube" | "Dailymotion" | "Twitch" | "HLS" | "DASH";
  mediaType: "video";
  sourceUrl: string;
  previewUrl: string | null;
  mediaUrl: string | null;
  embedUrl: string | null;
  streamType?: "hls" | "dash";
  instanceHost?: string;
  description: string | null;
  credit: string | null;
  license: null;
  licenseUrl: null;
  dateCreated: null;
  referrerPolicy: "no-referrer" | "strict-origin-when-cross-origin";
}

export type MediaEmbedResolution =
  | { status: "resolved"; item: ResolvedMediaEmbedItem }
  | { status: "needs_configuration"; provider: "Dailymotion"; message: string }
  | { status: "unsupported"; message: string };

type SafeUrl = { url: URL; sourceUrl: string };

const UNSUPPORTED: MediaEmbedResolution = {
  status: "unsupported",
  message: "URL video chưa được hỗ trợ. Media Portal hỗ trợ YouTube, Vimeo, PeerTube, Dailymotion, Twitch và manifest HLS/DASH.",
};

function safePublicHttpsUrl(value: unknown): SafeUrl | null {
  if (typeof value !== "string" || value.length < 12 || value.length > 2048) return null;
  try {
    const url = new URL(value);
    const host = url.hostname.toLowerCase().replace(/\.$/, "");
    if (url.protocol !== "https:" || url.username || url.password || url.port || url.hash) return null;
    if (!host || !host.includes(".") || host === "localhost" || host.endsWith(".localhost") ||
        host.endsWith(".local") || host.endsWith(".internal") || host.endsWith(".test") ||
        host.endsWith(".example") || host.endsWith(".invalid")) return null;
    if (host === "metadata.google.internal" || host === "instance-data") return null;
    if (/^(?:\d{1,3}\.){3}\d{1,3}$/.test(host) || host.includes(":")) return null;
    const labels = host.split(".");
    if (labels.some(label => !/^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$/.test(label))) return null;
    return { url, sourceUrl: url.toString() };
  } catch {
    return null;
  }
}

function baseItem(
  values: Pick<ResolvedMediaEmbedItem, "id" | "title" | "provider" | "sourceUrl" | "embedUrl"> &
    Partial<Pick<ResolvedMediaEmbedItem, "previewUrl" | "instanceHost" | "credit" | "referrerPolicy">>,
): ResolvedMediaEmbedItem {
  return {
    id: values.id,
    title: values.title,
    provider: values.provider,
    mediaType: "video",
    sourceUrl: values.sourceUrl,
    previewUrl: values.previewUrl ?? null,
    mediaUrl: null,
    embedUrl: values.embedUrl,
    ...(values.instanceHost ? { instanceHost: values.instanceHost } : {}),
    description: null,
    credit: values.credit ?? null,
    license: null,
    licenseUrl: null,
    dateCreated: null,
    referrerPolicy: values.referrerPolicy ?? "no-referrer",
  };
}

function resolveAdaptiveStream(url: URL, sourceUrl: string): MediaEmbedResolution | null {
  const path = url.pathname.toLowerCase();
  const streamType = path.endsWith(".m3u8") ? "hls" : path.endsWith(".mpd") ? "dash" : null;
  if (!streamType) return null;

  return {
    status: "resolved",
    item: {
      id: streamType + ":" + url.hostname + url.pathname,
      title: streamType === "hls" ? "HLS adaptive stream" : "MPEG-DASH adaptive stream",
      provider: streamType === "hls" ? "HLS" : "DASH",
      mediaType: "video",
      sourceUrl,
      previewUrl: null,
      mediaUrl: sourceUrl,
      embedUrl: null,
      streamType,
      description: "Phát manifest trực tiếp từ máy chủ nguồn. Máy chủ phải cho phép CORS; Nolane không tải hoặc lưu video.",
      credit: null,
      license: null,
      licenseUrl: null,
      dateCreated: null,
      referrerPolicy: "no-referrer",
    },
  };
}

function resolveYouTube(url: URL, sourceUrl: string): MediaEmbedResolution | null {
  const host = url.hostname.toLowerCase();
  const allowedHosts = ["youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"];
  if (!allowedHosts.includes(host)) return null;
  let id = "";
  if (host === "youtu.be") {
    const parts = url.pathname.split("/").filter(Boolean);
    if (parts.length !== 1) return UNSUPPORTED;
    id = parts[0];
  } else if (url.pathname === "/watch") {
    id = url.searchParams.get("v") ?? "";
  } else {
    const parts = url.pathname.split("/").filter(Boolean);
    if (parts.length === 2 && ["shorts", "live", "embed"].includes(parts[0])) id = parts[1];
    else return UNSUPPORTED;
  }
  if (!/^[A-Za-z0-9_-]{11}$/.test(id)) return UNSUPPORTED;
  const embed = new URL("https://www.youtube-nocookie.com/embed/" + id);
  embed.searchParams.set("playsinline", "1");
  embed.searchParams.set("rel", "0");
  return {
    status: "resolved",
    item: baseItem({
      id,
      title: "YouTube video " + id,
      provider: "YouTube",
      sourceUrl,
      embedUrl: embed.toString(),
    }),
  };
}

function safePeerTubeHost(host: string): boolean {
  const normalized = host.toLowerCase().replace(/\.$/, "");
  if (!normalized || !normalized.includes(".") || normalized.endsWith(".localhost") ||
      normalized.endsWith(".local") || normalized.endsWith(".internal") || normalized.endsWith(".test")) return false;
  if (/^(?:\d{1,3}\.){3}\d{1,3}$/.test(normalized) || normalized.includes(":")) return false;
  return normalized.split(".").every(label => /^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$/.test(label));
}

function resolvePeerTube(url: URL, sourceUrl: string): MediaEmbedResolution | null {
  const host = url.hostname.toLowerCase().replace(/\.$/, "");
  if (!safePeerTubeHost(host)) return null;
  const parts = url.pathname.split("/").filter(Boolean);
  if (parts.length !== 3 || !["videos"].includes(parts[0]) ||
      !["watch", "embed"].includes(parts[1])) return null;
  const uuid = parts[2].toLowerCase();
  if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(uuid)) {
    return UNSUPPORTED;
  }
  const embedUrl = "https://" + host + "/videos/embed/" + uuid;
  return {
    status: "resolved",
    item: baseItem({
      id: uuid,
      title: "PeerTube video " + uuid,
      provider: "PeerTube",
      sourceUrl,
      embedUrl,
      instanceHost: host,
    }),
  };
}

function vimeoVideoId(url: URL): string | null {
  const host = url.hostname.toLowerCase();
  if (!["vimeo.com", "www.vimeo.com"].includes(host)) return null;
  const parts = url.pathname.split("/").filter(Boolean);
  let id: string | undefined;
  if (parts.length === 1) id = parts[0];
  else if (parts.length === 2 && /^[0-9]+$/.test(parts[0])) id = parts[0];
  else if (parts.length === 3 && parts[0] === "channels" && /^[0-9]+$/.test(parts[2])) id = parts[2];
  else if (parts.length === 4 && parts[0] === "groups" && parts[2] === "videos" && /^[0-9]+$/.test(parts[3])) id = parts[3];
  else if (parts.length === 4 && parts[0] === "album" && parts[2] === "video" && /^[0-9]+$/.test(parts[3])) id = parts[3];
  else if (parts.length === 2 && parts[0] === "video") id = parts[1];
  return id && /^[0-9]{5,15}$/.test(id) ? id : null;
}

function decodeHtmlAttribute(value: string): string {
  return value.replace(/&amp;/gi, "&").replace(/&#0*38;/gi, "&")
    .replace(/&quot;/gi, '"').replace(/&#0*39;|&apos;/gi, "'");
}

function parseVimeoEmbed(html: unknown, expectedId: string): string {
  if (typeof html !== "string" || html.length > 20_000) {
    throw new Error("Vimeo returned an invalid embed response.");
  }
  const iframe = html.match(/<iframe\b[^>]*\bsrc\s*=\s*(["'])(.*?)\1/i);
  if (!iframe?.[2]) throw new Error("Vimeo returned an invalid embed URL.");
  let player: URL;
  try { player = new URL(decodeHtmlAttribute(iframe[2])); }
  catch { throw new Error("Vimeo returned an invalid embed URL."); }
  if (player.protocol !== "https:" || player.hostname !== "player.vimeo.com" ||
      player.port || player.username || player.password || player.pathname !== "/video/" + expectedId ||
      player.hash) {
    throw new Error("Vimeo returned an invalid embed URL.");
  }
  for (const key of player.searchParams.keys()) {
    if (key !== "h" && key !== "dnt") throw new Error("Vimeo returned an invalid embed URL.");
  }
  const hash = player.searchParams.get("h");
  if (hash && !/^[A-Za-z0-9_-]{4,80}$/.test(hash)) throw new Error("Vimeo returned an invalid embed URL.");
  player.searchParams.set("dnt", "1");
  return player.toString();
}

async function resolveVimeo(url: URL, sourceUrl: string): Promise<MediaEmbedResolution | null> {
  const id = vimeoVideoId(url);
  if (!id) return null;
  const endpoint = new URL("https://vimeo.com/api/oembed.json");
  endpoint.searchParams.set("url", sourceUrl);
  endpoint.searchParams.set("dnt", "true");
  let response: Response;
  try {
    response = await fetch(endpoint, {
      method: "GET",
      headers: { accept: "application/json" },
      redirect: "error",
      signal: AbortSignal.timeout(8_000),
    });
  } catch {
    throw new Error("Không thể kết nối Vimeo oEmbed hoặc yêu cầu đã hết thời gian.");
  }
  if (!response.ok) {
    await response.body?.cancel().catch(() => undefined);
    if (response.status === 429 || response.status === 503) {
      throw new Error("Vimeo oEmbed đang giới hạn truy cập. Hãy thử lại sau.");
    }
    throw new Error("Vimeo oEmbed trả về HTTP " + response.status + ".");
  }
  const payload = await readJsonResponse<Record<string, unknown>>(response, 100_000);
  if (payload.type !== "video") throw new Error("Vimeo oEmbed không trả về video hợp lệ.");
  const embedUrl = parseVimeoEmbed(payload.html, id);
  const title = typeof payload.title === "string" && payload.title.trim()
    ? payload.title.replace(/[\u0000-\u001f\u007f]/g, " ").trim().slice(0, 220)
    : "Vimeo video " + id;
  const credit = typeof payload.author_name === "string"
    ? payload.author_name.replace(/[\u0000-\u001f\u007f]/g, " ").trim().slice(0, 160) || null
    : null;
  let previewUrl: string | null = null;
  if (typeof payload.thumbnail_url === "string" && payload.thumbnail_url.length <= 2048) {
    try {
      const thumbnail = new URL(payload.thumbnail_url);
      if (thumbnail.protocol === "https:" && thumbnail.hostname === "i.vimeocdn.com" &&
          !thumbnail.port && !thumbnail.username && !thumbnail.password) previewUrl = thumbnail.toString();
    } catch { /* optional thumbnail is omitted */ }
  }
  return {
    status: "resolved",
    item: baseItem({
      id,
      title,
      provider: "Vimeo",
      sourceUrl,
      embedUrl,
      previewUrl,
      credit,
    }),
  };
}

function resolveTwitch(url: URL, sourceUrl: string): MediaEmbedResolution | null {
  const host = url.hostname.toLowerCase();
  const allowedHosts = ["twitch.tv", "www.twitch.tv", "m.twitch.tv", "clips.twitch.tv"];
  if (!allowedHosts.includes(host)) return null;

  const parts = url.pathname.split("/").filter(Boolean);
  let embedUrl: string;
  let id: string;
  let title: string;
  if (host === "clips.twitch.tv" && parts.length === 1 && parts[0] !== "embed") {
    id = parts[0];
    if (!/^[A-Za-z0-9_-]{4,80}$/.test(id)) return UNSUPPORTED;
    const embed = new URL("https://clips.twitch.tv/embed");
    embed.searchParams.set("clip", id);
    embed.searchParams.set("autoplay", "false");
    embedUrl = embed.toString();
    title = "Twitch clip " + id;
  } else if (
    parts.length === 3 &&
    parts[1] === "clip" &&
    ["twitch.tv", "www.twitch.tv", "m.twitch.tv"].includes(host)
  ) {
    id = parts[2];
    if (!/^[A-Za-z0-9_-]{4,80}$/.test(id)) return UNSUPPORTED;
    const embed = new URL("https://clips.twitch.tv/embed");
    embed.searchParams.set("clip", id);
    embed.searchParams.set("autoplay", "false");
    embedUrl = embed.toString();
    title = "Twitch clip " + id;
  } else if (
    parts.length === 2 &&
    parts[0] === "videos" &&
    ["twitch.tv", "www.twitch.tv", "m.twitch.tv"].includes(host)
  ) {
    id = parts[1];
    if (!/^[0-9]{5,15}$/.test(id)) return UNSUPPORTED;
    const embed = new URL("https://player.twitch.tv/");
    embed.searchParams.set("video", "v" + id);
    embed.searchParams.set("autoplay", "false");
    embedUrl = embed.toString();
    title = "Twitch VOD " + id;
  } else {
    return null;
  }

  return {
    status: "resolved",
    item: baseItem({
      id,
      title,
      provider: "Twitch",
      sourceUrl,
      embedUrl,
      referrerPolicy: "strict-origin-when-cross-origin",
    }),
  };
}

function resolveDailymotion(url: URL, sourceUrl: string, playerIdInput?: unknown): MediaEmbedResolution | null {
  const host = url.hostname.toLowerCase();
  if (!["dailymotion.com", "www.dailymotion.com", "dai.ly"].includes(host)) return null;
  const parts = url.pathname.split("/").filter(Boolean);
  let id = "";
  if (host === "dai.ly" && parts.length === 1) id = parts[0];
  else if (parts.length === 2 && parts[0] === "video") id = parts[1].split("_")[0];
  if (!/^[A-Za-z0-9]{4,20}$/.test(id)) return UNSUPPORTED;
  if (typeof playerIdInput !== "string" || !/^[A-Za-z0-9_-]{3,32}$/.test(playerIdInput.trim())) {
    return {
      status: "needs_configuration",
      provider: "Dailymotion",
      message: "Dailymotion yêu cầu Player ID do chủ tài khoản cấu hình. Nolane đã nhận diện link, nhưng chưa thể mở player cho đến khi bổ sung Player ID.",
    };
  }
  const embed = new URL("https://geo.dailymotion.com/player/" + playerIdInput.trim() + ".html");
  embed.searchParams.set("video", id);
  return {
    status: "resolved",
    item: baseItem({
      id,
      title: "Dailymotion video " + id,
      provider: "Dailymotion",
      sourceUrl,
      embedUrl: embed.toString(),
      referrerPolicy: "strict-origin-when-cross-origin",
    }),
  };
}

export async function resolveMediaEmbed(
  input: unknown,
  dailymotionPlayerId?: unknown,
): Promise<MediaEmbedResolution> {
  const safe = safePublicHttpsUrl(input);
  if (!safe) return UNSUPPORTED;
  const { url, sourceUrl } = safe;

  const adaptiveStream = resolveAdaptiveStream(url, sourceUrl);
  if (adaptiveStream) return adaptiveStream;

  const youtube = resolveYouTube(url, sourceUrl);
  if (youtube) return youtube;

  const peerTube = resolvePeerTube(url, sourceUrl);
  if (peerTube) return peerTube;

  const twitch = resolveTwitch(url, sourceUrl);
  if (twitch) return twitch;

  const dailymotion = resolveDailymotion(url, sourceUrl, dailymotionPlayerId);
  if (dailymotion) return dailymotion;

  const vimeo = await resolveVimeo(url, sourceUrl);
  if (vimeo) return vimeo;

  return UNSUPPORTED;
}
