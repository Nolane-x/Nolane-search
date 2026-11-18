export async function parseJsonObjectBody(
  request: Request,
  maxBytes = 30_000,
): Promise<Record<string, unknown> | null> {
  if (!request.body || !Number.isSafeInteger(maxBytes) || maxBytes < 1) return null;
  const reader = request.body.getReader();
  const chunks: Uint8Array[] = [];
  let total = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      total += value.byteLength;
      if (total > maxBytes) {
        await reader.cancel("Request body exceeded the configured limit").catch(() => undefined);
        return null;
      }
      chunks.push(value);
    }
  } catch {
    return null;
  } finally {
    reader.releaseLock();
  }

  const bytes = new Uint8Array(total);
  let offset = 0;
  for (const chunk of chunks) {
    bytes.set(chunk, offset);
    offset += chunk.byteLength;
  }
  try {
    const value = JSON.parse(new TextDecoder("utf-8", { fatal: false }).decode(bytes)) as unknown;
    return value && typeof value === "object" && !Array.isArray(value)
      ? value as Record<string, unknown>
      : null;
  } catch {
    return null;
  }
}

/**
 * Parse a JSON response without allowing an upstream provider to make the Worker
 * buffer an unbounded body. The limit applies to decoded response bytes.
 */
export async function readJsonResponse<T>(response: Response, maxBytes = 1_000_000): Promise<T> {
  if (!Number.isSafeInteger(maxBytes) || maxBytes < 1) throw new Error("Invalid JSON response size limit.");
  const declaredLength = Number(response.headers.get("content-length"));
  if (Number.isFinite(declaredLength) && declaredLength > maxBytes) {
    await response.body?.cancel("Upstream JSON response exceeded the configured limit").catch(() => undefined);
    throw new Error("Upstream JSON response exceeded the configured size limit.");
  }
  if (!response.body) throw new Error("Upstream returned an empty JSON response.");

  const reader = response.body.getReader();
  const chunks: Uint8Array[] = [];
  let total = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      total += value.byteLength;
      if (total > maxBytes) {
        await reader.cancel("Upstream JSON response exceeded the configured limit").catch(() => undefined);
        throw new Error("Upstream JSON response exceeded the configured size limit.");
      }
      chunks.push(value);
    }
  } finally {
    reader.releaseLock();
  }

  const bytes = new Uint8Array(total);
  let offset = 0;
  for (const chunk of chunks) {
    bytes.set(chunk, offset);
    offset += chunk.byteLength;
  }
  try {
    return JSON.parse(new TextDecoder("utf-8", { fatal: false }).decode(bytes)) as T;
  } catch {
    throw new Error("Upstream returned invalid JSON.");
  }
}
