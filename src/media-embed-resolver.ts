export interface ResolvedMediaEmbedItem {
  id: string;
  title: string;
  provider: "YouTube" | "Vimeo" | "PeerTube" | "Dailymotion";
  mediaType: "video";
  sourceUrl: string;
  previewUrl: string | null;
  mediaUrl: null;
  embedUrl: string;
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

export async function resolveMediaEmbed(
  _input: unknown,
  _dailymotionPlayerId?: unknown,
): Promise<MediaEmbedResolution> {
  return { status: "unsupported", message: "This media URL is not supported." };
}
