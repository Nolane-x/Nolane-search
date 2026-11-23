# Wave 33 handoff — content extraction, policy, schema and provenance

Date: 2026-11-23
Repository: https://github.com/Nolane-x/Nolane-search
Branch: feat/wave-thirty-three-content-policy-provenance
Status: implementation branch; not merged or deployed.

## Production boundary

Wave 32 remains the latest production release: **442 tools**. Wave 33 adds four entries on this branch (446 catalog entries) but must not be described as production until PR CI, Worker export/health smoke and Cloudflare deployment pass.

## Added processors

| ID | Description |
|---|---|
| `web-article-extract` | Extract main article body/metadata from a saved HTML file to Markdown; never fetch URLs. |
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

Pending: TypeScript/Vitest/Python/Worker CI, post-merge Worker export and health smoke, Cloudflare deployment, then owner Telegram E2E. Until those gates pass, production count stays **442**.
