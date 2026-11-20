import { describe, expect, it } from "vitest";
import {
  isValidGitHubRepositorySource,
  parseGitHubCompareCommand,
  parseGitHubRepositoryUrl,
} from "../src/github-intelligence";

describe("GitHub Repository Intelligence source validation", () => {
  it("accepts public repository URLs and leaves the default ref unresolved", () => {
    expect(parseGitHubRepositoryUrl("https://github.com/octocat/Hello-World")).toEqual({
      owner: "octocat", repo: "Hello-World", ref: "",
    });
    expect(parseGitHubRepositoryUrl("https://github.com/Nolane-x/Nolane-search.git")).toEqual({
      owner: "Nolane-x", repo: "Nolane-search", ref: "",
    });
  });

  it("accepts a branch name with slashes in a tree URL", () => {
    expect(parseGitHubRepositoryUrl("https://github.com/acme/project/tree/feature/new-parser")).toEqual({
      owner: "acme", repo: "project", ref: "feature/new-parser",
    });
  });

  it("accepts immutable commit references", () => {
    expect(parseGitHubRepositoryUrl("https://github.com/acme/project/commit/0123456789abcdef0123456789abcdef01234567")).toMatchObject({
      owner: "acme", repo: "project", ref: "0123456789abcdef0123456789abcdef01234567",
    });
  });

  it.each([
    "http://github.com/acme/project",
    "https://evil.example/acme/project",
    "https://github.com.evil.example/acme/project",
    "https://user:pass@github.com/acme/project",
    "https://github.com:8443/acme/project",
    "https://github.com/acme/project?tab=readme",
    "https://github.com/acme/project#readme",
    "https://github.com/acme/project/pull/12",
    "https://github.com/acme/project/tree/../private",
    "https://github.com/acme/project/tree/feature%5Cescape",
    "https://github.com/-bad/project",
    "https://github.com/acme/project/commit/not-a-commit",
  ])("rejects unsafe or unsupported URL: %s", url => {
    expect(parseGitHubRepositoryUrl(url)).toBeNull();
  });

  it("parses a branch comparison without confusing the repository URL", () => {
    expect(parseGitHubCompareCommand("https://github.com/acme/project main...feature/new-ui")).toEqual({
      owner: "acme", repo: "project", ref: "feature/new-ui",
      compareBase: "main", compareHead: "feature/new-ui",
    });
  });

  it.each([
    "https://github.com/acme/project main...main",
    "https://github.com/acme/project ../main",
    "https://github.com/acme/project main...feature..bad",
    "https://github.com/acme/project main...feature extra",
    "https://example.com/acme/project main...feature",
  ])("rejects invalid comparison request: %s", input => {
    expect(parseGitHubCompareCommand(input)).toBeNull();
  });

  it("validates the exact persisted source schema", () => {
    expect(isValidGitHubRepositorySource({ owner: "acme", repo: "project", ref: "feature/ref" })).toBe(true);
    expect(isValidGitHubRepositorySource({
      owner: "acme", repo: "project", ref: "feature/ref", compareBase: "main", compareHead: "feature/ref",
    })).toBe(true);
    expect(isValidGitHubRepositorySource({ owner: "acme", repo: "project", ref: "", extra: "unexpected" })).toBe(false);
    expect(isValidGitHubRepositorySource({ owner: "acme", repo: "project", ref: "", compareBase: "main" })).toBe(false);
  });
});
