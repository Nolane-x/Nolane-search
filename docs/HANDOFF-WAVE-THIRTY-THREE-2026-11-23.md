# Wave 33 handoff — content extraction, policy, schema and provenance

Date: 2026-11-23
Repository: https://github.com/Nolane-x/Nolane-search
Branch: feat/wave-thirty-three-content-policy-provenance
Status: implemented, merged via PR #86 and deployed to production on 2026-11-23.

## Production boundary

Wave 32 production baseline was 442 tools. Wave 33 merged as `18acca8f983ee8e1667939e282f25d59aa41e2f1` and increased the production catalog to **446 tools**. Main CI `45150195124`, Worker export/health smoke `45150195535` and Cloudflare deployment `45150195611` all passed. Worker Version ID: `016b7d5b-629d-400a-bf86-0c0f5b70913a`.

## Added processors

| ID | Description |
|---|---|
| `web-article-extract` | Extract main article body/metadata from a saved HTML file to Markdown; require at least 40 characters of main text and never fetch URLs. |
| `rego-policy-check` | OPA strict parsing/compilation using the Rego v0/v1-compatible language set; never evaluates policies. |
| `k8s-schema-validate` | Kubeconform strict schema checks against Kubernetes 1.34.0 schemas pinned to a repository commit; no cluster access. |
| `cosign-verify-blob` | Verify artifact signature using Sigstore bundle, local PEM public key and user-supplied TrustedRoot. |

## Code and integration

- Python handlers: `tools/wave33.py`.
- Focused regression tests: `tools/test_wave33.py`.
- Conditional binary installer with SHA-256 verification: `scripts/install-wave33-binaries.sh`.
- TypeScript catalog and pipeline edges are mirrored in Python `RUNNERS`, `TOOLS`, `TEXT_OUTPUT_TOOLS` and `PIPELINE_TRANSITIONS`.
- CI installs Trafilatura 2.3.1 for deterministic unit tests and checks installer shell syntax.
- Tool execution installs OPA 1.22.4, Kubeconform 0.8.0 and Cosign 3.1.4 only if a job selects that processor.
- No D1 migration, Cloudflare secret or persistent service is added.

## Security notes

- Trafilatura receives HTML bytes only; it does not call `fetch_url` or any network API.
- OPA invokes only `opa check`; policy logic and built-ins are not executed.
- Kubeconform uses strict OpenAPI schema validation with a fixed schema repository commit and Kubernetes v1.34.0 baseline. CRDs and server-side validations remain outside scope.
- Cosign requires a four-file package and verifies with local trust materials; KMS, keyless OIDC and trust-root auto-download are not enabled.
- All subprocesses have hard timeouts; stdout/stderr and sensitive diagnostics are withheld. Temporary files use fixed neutral names.
- All tools are bounded by per-file, total-input and output limits.

Detailed sources and limitations: `docs/TOOL-RESEARCH-2026-11-23-WAVE33.md`.

## Verification status

Verified: TypeScript/Vitest/Python/Worker CI, post-merge Worker export and health smoke, and Cloudflare deployment all passed. Production is **446 tools**. Owner Telegram E2E remains a separate manual acceptance check.
