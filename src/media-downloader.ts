type MediaNodeConfig = {
  MEDIA_NODE_URL?: string;
  MEDIA_NODE_TOKEN?: string;
};

const NODE_TOKEN_RE = /^[a-f0-9]{64}$/i;
const FUNNEL_HOST_RE = /^(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+ts\.net$/;
const INTERNAL_PATH_RE = /^\/internal\/(?:[a-z0-9-]+\/)*[a-z0-9-]+$/;

export function isMediaNodeConfigured(env: MediaNodeConfig): boolean {
  if (typeof env.MEDIA_NODE_URL !== "string" ||
      typeof env.MEDIA_NODE_TOKEN !== "string" ||
      !NODE_TOKEN_RE.test(env.MEDIA_NODE_TOKEN)) return false;
  try {
    const url = new URL(env.MEDIA_NODE_URL);
    return url.protocol === "https:" &&
      url.username === "" && url.password === "" &&
      url.port === "" &&
      url.pathname === "/" && url.search === "" && url.hash === "" &&
      FUNNEL_HOST_RE.test(url.hostname.toLowerCase());
  } catch {
    return false;
  }
}

/**
 * Builds a request to one validated Tailscale Funnel origin. Routes are fixed
 * internal API paths; the browser can never select an arbitrary host or path.
 */
export function createMediaNodeRequest(
  env: MediaNodeConfig,
  ownerId: number,
  path: string,
  init: RequestInit = {},
  timeoutMs = 12_000,
): Request | null {
  if (!isMediaNodeConfigured(env) ||
      !Number.isSafeInteger(ownerId) || ownerId <= 0 ||
      !INTERNAL_PATH_RE.test(path) || path.includes("..") ||
      path.includes("//")) return null;

  const base = new URL(env.MEDIA_NODE_URL!);
  const target = new URL(path, base);
  if (target.origin !== base.origin || target.pathname !== path ||
      target.search !== "" || target.hash !== "") return null;

  const headers = new Headers(init.headers);
  headers.set("x-nolane-internal", env.MEDIA_NODE_TOKEN!);
  headers.set("x-nolane-owner-id", String(ownerId));
  headers.delete("cookie");
  headers.delete("authorization");
  headers.delete("proxy-authorization");

  const requestInit: RequestInit = {
    ...init,
    headers,
    redirect: "error",
  };
  if (timeoutMs > 0) requestInit.signal = AbortSignal.timeout(timeoutMs);
  else delete requestInit.signal;

  return new Request(target, requestInit);
}
