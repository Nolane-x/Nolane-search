export type MediaDownloadFormat = "video" | "audio";
export type MediaDownloadQuality = "best" | "1080" | "720" | "480";

export interface MediaDownloadInput {
  url: string;
  format: MediaDownloadFormat;
  quality: MediaDownloadQuality;
}

export type MediaDownloadParseResult =
  | { ok: true; value: MediaDownloadInput }
  | { ok: false; error: string };

const RESERVED_SUFFIXES = [
  ".localhost", ".local", ".internal", ".test", ".example", ".invalid", ".onion", ".arpa",
];
const IPV4_DENY_CIDRS: Array<[number, number]> = [
  [0x00000000, 8],  // 0.0.0.0/8
  [0x0a000000, 8],  // 10.0.0.0/8
  [0x64400000, 10], // 100.64.0.0/10 (CGNAT)
  [0x7f000000, 8],  // 127.0.0.0/8
  [0xa9fe0000, 16], // 169.254.0.0/16
  [0xac100000, 12], // 172.16.0.0/12
  [0xc0000000, 24], // 192.0.0.0/24
  [0xc0000200, 24], // 192.0.2.0/24
  [0xc0586300, 24], // 192.88.99.0/24
  [0xc0a80000, 16], // 192.168.0.0/16
  [0xc6120000, 15], // 198.18.0.0/15
  [0xc6336400, 24], // 198.51.100.0/24
  [0xcb007100, 24], // 203.0.113.0/24
  [0xe0000000, 4],  // multicast and reserved
];

function parseIpv4(value: string): number[] | null {
  const parts = value.split(".");
  if (parts.length !== 4) return null;
  const octets = parts.map(part => {
    if (!/^(?:0|[1-9][0-9]{0,2})$/.test(part)) return -1;
    const number = Number(part);
    return number >= 0 && number <= 255 ? number : -1;
  });
  return octets.every(part => part >= 0) ? octets : null;
}

function parseIpv6(value: string): bigint | null {
  let address = value.toLowerCase().replace(/^\[|\]$/g, "");
  if (!address || address.includes("%")) return null;

  const v4Tail = address.match(/(\d{1,3}(?:\.\d{1,3}){3})$/);
  if (v4Tail) {
    const octets = parseIpv4(v4Tail[1]);
    if (!octets) return null;
    const high = ((octets[0] << 8) | octets[1]).toString(16);
    const low = ((octets[2] << 8) | octets[3]).toString(16);
    address = address.slice(0, -v4Tail[1].length) + high + ":" + low;
  }

  if ((address.match(/::/g) || []).length > 1) return null;
  const compressed = address.includes("::");
  const halves = address.split("::");
  const left = halves[0] ? halves[0].split(":") : [];
  const right = compressed && halves[1] ? halves[1].split(":") : [];
  const missing = 8 - left.length - right.length;
  if ((!compressed && missing !== 0) || (compressed && missing < 1)) return null;
  const words = compressed ? [...left, ...Array(missing).fill("0"), ...right] : left;
  if (words.length !== 8 || words.some(word => !/^[0-9a-f]{1,4}$/.test(word))) return null;
  return words.reduce((result, word) => (result << 16n) | BigInt("0x" + word), 0n);
}

function inV4Cidr(value: number, network: number, prefix: number): boolean {
  const mask = prefix === 0 ? 0 : (0xffffffff << (32 - prefix)) >>> 0;
  return ((value >>> 0) & mask) === ((network >>> 0) & mask);
}

export function isPublicIpAddress(value: string): boolean {
  const v4 = parseIpv4(value);
  if (v4) {
    const address = (((v4[0] << 24) >>> 0) + (v4[1] << 16) + (v4[2] << 8) + v4[3]) >>> 0;
    if (v4[0] === 0 || v4[0] >= 224) return false;
    return !IPV4_DENY_CIDRS.some(([network, prefix]) => inV4Cidr(address, network, prefix));
  }

  const v6 = parseIpv6(value);
  if (v6 === null) return false;
  // Globally routable IPv6 unicast is inside 2000::/3. This also excludes
  // IPv4-mapped, loopback, link-local, ULA, multicast, NAT64 and unspecified.
  if ((v6 >> 125n) !== 1n) return false;
  // Documentation, benchmarking and special-purpose 2001::/23 ranges.
  if ((v6 >> 96n) === (0x20010db8n)) return false; // 2001:db8::/32
  if ((v6 >> 113n) === (0x2001n << 7n)) return false; // 2001::/23
  return true;
}

export function isPublicDomainName(hostInput: string): boolean {
  const host = hostInput.toLowerCase().replace(/\.$/, "");
  if (!host || host.length > 253 || !host.includes(".") || host.includes(":")) return false;
  if (host === "localhost" || RESERVED_SUFFIXES.some(suffix => host.endsWith(suffix))) return false;
  if (/^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$/.test(host) || parseIpv6(host) !== null) return false;
  return host.split(".").every(label =>
    label.length >= 1 && label.length <= 63 &&
    /^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$/.test(label),
  );
}

export function normalizeMediaDownloadUrl(value: unknown): { ok: true; url: string } | { ok: false; error: string } {
  if (typeof value !== "string") return { ok: false, error: "Hãy nhập URL video hoặc audio công khai." };
  const input = value.normalize("NFKC").trim();
  if (input.length < 12 || input.length > 2048 || /[\u0000-\u001f\u007f]/.test(input)) {
    return { ok: false, error: "URL phải dài 12–2048 ký tự và không chứa ký tự điều khiển." };
  }
  let url: URL;
  try { url = new URL(input); }
  catch { return { ok: false, error: "URL không hợp lệ." }; }
  if (url.protocol !== "http:" && url.protocol !== "https:") {
    return { ok: false, error: "Chỉ hỗ trợ trang công khai qua HTTP hoặc HTTPS." };
  }
  if (url.username || url.password) return { ok: false, error: "URL không được chứa thông tin đăng nhập." };
  if (url.port) return { ok: false, error: "Không hỗ trợ cổng mạng tùy chỉnh." };
  if (url.hash) return { ok: false, error: "Hãy bỏ phần fragment (#) khỏi URL." };
  const host = url.hostname.toLowerCase().replace(/\.$/, "");
  if (!isPublicDomainName(host)) {
    return { ok: false, error: "Không hỗ trợ IP trực tiếp, máy chủ nội bộ hoặc tên miền đặc biệt." };
  }
  url.hostname = host;
  return { ok: true, url: url.toString() };
}

export function parseMediaDownloadInput(value: unknown): MediaDownloadParseResult {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return { ok: false, error: "Dữ liệu tải media không hợp lệ." };
  }
  const input = value as Record<string, unknown>;
  const normalizedUrl = normalizeMediaDownloadUrl(input.url);
  if (!normalizedUrl.ok) return normalizedUrl;
  if (input.format !== "video" && input.format !== "audio") {
    return { ok: false, error: "Định dạng phải là video hoặc audio." };
  }
  const quality = input.quality === undefined ? "720" : input.quality;
  if (!["best", "1080", "720", "480"].includes(String(quality))) {
    return { ok: false, error: "Chất lượng video không hợp lệ." };
  }
  if (input.format === "audio" && quality !== "720") {
    return { ok: false, error: "Chọn chất lượng mặc định khi tải audio." };
  }
  return {
    ok: true,
    value: {
      url: normalizedUrl.url,
      format: input.format,
      quality: quality as MediaDownloadQuality,
    },
  };
}

export interface DnsJsonAnswer {
  type?: number;
  data?: string;
}

interface DnsJsonResponse {
  Status?: number;
  Answer?: DnsJsonAnswer[];
}

/**
 * Resolves through Cloudflare's DNS-over-HTTPS JSON endpoint and fails closed.
 * Each outbound hop is checked again by the container's Worker egress handler.
 */
export async function hasOnlyPublicDnsAnswers(host: string, fetcher: typeof fetch = fetch): Promise<boolean> {
  if (!isPublicDomainName(host)) return false;
  const results = await Promise.all([1, 28].map(async type => {
    const endpoint = new URL("https://cloudflare-dns.com/dns-query");
    endpoint.searchParams.set("name", host);
    endpoint.searchParams.set("type", String(type));
    const response = await fetcher(endpoint, {
      headers: { accept: "application/dns-json" },
      redirect: "error",
      signal: AbortSignal.timeout(4000),
    });
    if (!response.ok) throw new Error("DNS-over-HTTPS returned HTTP " + response.status);
    const payload = await response.json() as DnsJsonResponse;
    if (payload.Status !== 0) throw new Error("DNS-over-HTTPS returned a DNS error.");
    return (payload.Answer || []).filter(answer => answer.type === type && typeof answer.data === "string");
  }));
  const answers = results.flat();
  if (!answers.length) return false;
  return answers.every(answer => isPublicIpAddress(answer.data!));
}
