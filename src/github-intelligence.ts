export interface GitHubRepositorySource {
  owner: string;
  repo: string;
  /** Empty means use the repository's default branch at execution time. */
  ref: string;
  compareBase?: string;
  compareHead?: string;
}

const OWNER_PATTERN = /^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$/;
const REPO_PATTERN = /^[A-Za-z0-9_.-]{1,100}$/;

function validGitRef(value: string): boolean {
  return value.length >= 1 && value.length <= 255 &&
    !value.startsWith("-") && !value.startsWith("/") && !value.endsWith("/") &&
    !value.includes("..") && !value.includes("\\") &&
    !/[\u0000-\u0020\u007f~^:?*[\]]/.test(value) &&
    value.split("/").every(part => part.length > 0 && part !== "." && part !== "..");
}

function decodePath(value: string): string | null {
  try { return decodeURIComponent(value); } catch { return null; }
}

/** Accepts only canonical public GitHub repository, branch and commit URLs. */
export function parseGitHubRepositoryUrl(raw: string): GitHubRepositorySource | null {
  if (typeof raw !== "string" || raw.length > 600) return null;
  let url: URL;
  try { url = new URL(raw.trim()); } catch { return null; }
  if (url.protocol !== "https:" || url.hostname !== "github.com" ||
      url.port || url.username || url.password || url.search || url.hash) return null;
  const rawParts = url.pathname.split("/").filter(Boolean);
  const parts = rawParts.map(decodePath);
  if (parts.some(part => part === null || part === "." || part === ".." || part!.includes("\\"))) return null;
  if (parts.length < 2) return null;
  const owner = parts[0]!;
  let repo = parts[1]!;
  if (repo.endsWith(".git")) repo = repo.slice(0, -4);
  if (!OWNER_PATTERN.test(owner) || !REPO_PATTERN.test(repo)) return null;

  let ref = "";
  if (parts.length > 2) {
    const kind = parts[2];
    if (kind !== "tree" && kind !== "commit") return null;
    if (parts.length < 4) return null;
    ref = parts.slice(3).join("/");
    if (!validGitRef(ref)) return null;
    if (kind === "commit" && !/^[a-f0-9]{7,64}$/i.test(ref)) return null;
  }
  return { owner, repo, ref };
}

export function parseGitHubCompareCommand(raw: string): (GitHubRepositorySource & { compareBase: string; compareHead: string }) | null {
  const input = raw.trim();
  const match = input.match(/^(https:\/\/github\.com\/\S+)\s+([^\s]+)\.\.\.([^\s]+)$/i);
  if (!match) return null;
  const source = parseGitHubRepositoryUrl(match[1]!);
  const compareBase = match[2]!;
  const compareHead = match[3]!;
  if (!source || !validGitRef(compareBase) || !validGitRef(compareHead) || compareBase === compareHead) return null;
  return { ...source, ref: compareHead, compareBase, compareHead };
}

export function isValidGitHubRepositorySource(value: unknown): value is GitHubRepositorySource {
  if (!value || typeof value !== "object" || Array.isArray(value)) return false;
  const item = value as Record<string, unknown>;
  if (typeof item.owner !== "string" || !OWNER_PATTERN.test(item.owner) ||
      typeof item.repo !== "string" || !REPO_PATTERN.test(item.repo) ||
      typeof item.ref !== "string" || (item.ref !== "" && !validGitRef(item.ref))) return false;
  const hasBase = item.compareBase !== undefined;
  const hasHead = item.compareHead !== undefined;
  if (hasBase !== hasHead) return false;
  if (hasBase && (typeof item.compareBase !== "string" || typeof item.compareHead !== "string" ||
      !validGitRef(item.compareBase) || !validGitRef(item.compareHead) || item.compareBase === item.compareHead)) return false;
  return Object.keys(item).every(key => ["owner", "repo", "ref", "compareBase", "compareHead"].includes(key));
}
