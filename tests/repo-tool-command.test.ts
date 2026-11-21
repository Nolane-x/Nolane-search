import { describe, expect, it } from "vitest";
import { parseRepositoryToolCommand } from "../src/repo-tools";

describe("direct GitHub repository tool command", () => {
  it("accepts an individual repository auditor and a branch URL", () => {
    expect(parseRepositoryToolCommand(
      "repo-runtime-risk https://github.com/acme/project/tree/feature/security"
    )).toEqual({
      toolId: "repo-runtime-risk",
      source: { owner: "acme", repo: "project", ref: "feature/security" },
    });
  });

  it("accepts the existing repository security and inventory tools", () => {
    expect(parseRepositoryToolCommand(
      "repo-security-audit https://github.com/acme/project"
    )?.toolId).toBe("repo-security-audit");
    expect(parseRepositoryToolCommand(
      "repo-inventory https://github.com/acme/project"
    )?.toolId).toBe("repo-inventory");
  });

  it.each([
    "",
    "unknown-tool https://github.com/acme/project",
    "repo https://github.com/acme/project",
    "repo-runtime-risk",
    "text-clean https://github.com/acme/project",
    "repo-runtime-risk https://evil.example/acme/project",
    "repo-runtime-risk https://github.com/acme/project/tree/../private",
    "repo-runtime-risk https://user:pass@github.com/acme/project",
    "repo-runtime-risk https://github.com/acme/project extra",
  ])("rejects unsupported or malformed request: %s", input => {
    expect(parseRepositoryToolCommand(input)).toBeNull();
  });

  it("rejects an oversized command before parsing", () => {
    expect(parseRepositoryToolCommand("repo-test-map " + "x".repeat(800))).toBeNull();
  });
});
