import { getTool } from "./tools";
import { parseGitHubRepositoryUrl } from "./github-intelligence";

export interface RepositoryToolCommand {
  toolId: string;
  source: NonNullable<ReturnType<typeof parseGitHubRepositoryUrl>>;
}

/** Parse a repository-only tool ID followed by a public GitHub repository URL. */
export function parseRepositoryToolCommand(input: string): RepositoryToolCommand | null {
  if (typeof input !== "string" || input.length > 700) return null;
  const parts = input.trim().split(/\s+/);
  const toolId = parts.shift() || "";
  const tool = getTool(toolId);
  if (!tool || !tool.ready || tool.category !== "repository" || parts.length !== 1) return null;
  const source = parseGitHubRepositoryUrl(parts[0] || "");
  return source ? { toolId: tool.id, source } : null;
}
