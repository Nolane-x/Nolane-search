# Wave 33 upstream research — 2026-11-23

Repository: https://github.com/Nolane-x/Nolane-search
Branch: feat/wave-thirty-three-content-policy-provenance
Status: implementation branch; not merged and not deployed. Production remains 442 tools until the release workflows pass.

Wave 33 targets capabilities that are materially different from current HTML text extraction, heuristic Kubernetes security audits and static repository pattern checks.

| Upstream | Pinned release/source | License | Capability selected |
|---|---|---|---|
| [Trafilatura](https://github.com/adbar/trafilatura) | 2.3.1, released 2026-10-06 | Apache-2.0 | Main-content/article extraction from HTML that has already been downloaded |
| [Open Policy Agent](https://github.com/open-policy-agent/opa) | 1.22.4, released 2026-11-12 | Apache-2.0 | Parse and strictly compile Rego v1 policy modules |
| [Kubeconform](https://github.com/yannh/kubeconform) | 0.8.0, released 2026-06-04 | Apache-2.0 | Validate Kubernetes YAML against pinned OpenAPI-derived JSON schemas |
| [Sigstore Cosign](https://github.com/sigstore/cosign) | 3.1.4, released 2026-10-20 | Apache-2.0 | Verify a signed artifact against a supplied Sigstore bundle, PEM public key and local trusted root |

## New processors

### web-article-extract

Uses Trafilatura to extract the article body, title, author/date/site metadata and tables from an HTML/XHTML file. Input must already be downloaded: no URL fetch, crawler, sitemap traversal or external-resource loading is performed. Output is UTF-8 Markdown. HTML input is capped at 10 MiB and generated Markdown at 8 MiB. The tool complements, rather than replaces, the generic html-text converter: its job is to identify the main article and discard page boilerplate. Metadata is bounded; no source URL is included.

### rego-policy-check

Uses the pinned OPA binary with `opa check --strict --format=json --rego-v1` to parse and compile against OPA's Rego v0/v1-compatible language set one Rego file or a ZIP of modules. It does not run `opa eval`, instantiate a policy decision, call policy built-ins or load remote bundles/data. ZIP packages must contain only UTF-8 .rego modules, at most 60 files, 1 MiB each and 4 MiB combined. Processing is limited to 45 seconds. Source text and raw compiler diagnostics are withheld from the report.

OPA 1.22.4 Linux static binary SHA-256: `35e3b352e715e80624ead6c89930d8585f6f7d94cdc409eb2a9fe36620dcccba`.

### k8s-schema-validate

Uses Kubeconform 0.8.0 with strict validation and JSON summary output. Kubernetes baseline is explicitly fixed to **1.34.0**. The schema source is pinned to repository commit `0c4dd99d9873f7b4c2da24c008476f5841adbe2d`, not the moving `master` branch. The template only contacts `raw.githubusercontent.com/yannh/kubernetes-json-schema`; resource kind values from the YAML influence the requested schema filename but cannot choose another host or repository. A small local cache is used within the ephemeral runner. Input is capped at 10 MiB, timeout at 60 seconds, and concurrency at two schema lookups. Output includes aggregate valid/invalid/error/skipped counts only.

Kubeconform 0.8.0 Linux AMD64 release archive SHA-256: `9bc2bffbf71f261128533edaf912153948b7ff238f9a531ae6d34466ec287883`.

**Important limitation:** Kubeconform checks manifests against OpenAPI-derived schemas. It does not run Kubernetes admission controllers or server-side validation, and custom CRDs are not included in the default schema set. It is not equivalent to `kubectl apply --dry-run=server`.

### cosign-verify-blob

Accepts one ZIP with exactly four root files: `artifact.bin`, `artifact.sigstore.json`, `cosign.pub` and `trusted_root.json`. It runs Cosign 3.1.4 `verify-blob` with the local PEM public key, Sigstore bundle and supplied TrustedRoot. The workflow deliberately does not enable KMS, keyless/OIDC identity discovery or automatic trust-root downloads. The report returns signature status and the artifact SHA-256, but not the artifact contents, key, certificate identity or raw diagnostics.

Limits: artifact 10 MiB, Sigstore bundle 2 MiB, PEM key 32 KiB, TrustedRoot 4 MiB; combined ZIP and expansion remain below the existing archive guard (20 MiB compressed / 180 MiB expanded), with each member additionally restricted by its limit and compression ratio. Verification timeout is 45 seconds.

Cosign 3.1.4 Linux AMD64 binary SHA-256: `424e2c97d0b45fd7a6b608a87f090f35633f4c23ece5f092d48bba11aaf4bbfa`.

## Operational and security boundaries

- The three downloaded CLIs are installed only when the selected tool requires them; their release binaries are checksum-pinned before execution.
- The Trafilatura package is version-pinned and installed only for the article extraction job.
- All uploaded inputs run in ephemeral GitHub-hosted runners. Temporary working paths use neutral names, raw stdout/stderr are captured and withheld, and every subprocess has a hard timeout.
- OPA is compile-only. Kubernetes validation is schema-only. Cosign relies on user-supplied local verification material.
- No D1 migration, new Cloudflare secret, third-party persistent service or paid resource is added.
- Existing html-text, kubernetes-manifest-audit, repo-security-audit and repo-runtime-risk remain unchanged; Wave 33 adds new semantics rather than replacing their current behavior.

## Acceptance gates

1. Catalog, Python allowlist, handler map, text-output registry and Worker/runner pipeline edges must match exactly.
2. CI must pass type-check, all Vitest tests, Python unittest discovery and Worker build.
3. The runner execution workflow must download only requested pinned CLI binaries, verify SHA-256 and pass tool-specific fixtures.
4. After merge, Worker export/health smoke and Cloudflare deployment must pass before changing the production count from 442 to 446.
5. Owner-level Telegram E2E remains separate: upload a saved HTML page, valid/invalid Rego, Kubernetes YAML with one valid and one invalid resource, and a signed artifact ZIP. Confirm returned outputs and `/tool_retry`.

## Primary sources

- Trafilatura release: https://github.com/adbar/trafilatura/releases/tag/v2.3.1
- Trafilatura project metadata: https://github.com/adbar/trafilatura/blob/master/pyproject.toml
- OPA release and documentation: https://github.com/open-policy-agent/opa/releases/tag/v1.22.4
- OPA `check` implementation: https://github.com/open-policy-agent/opa/blob/main/cmd/check.go
- Kubeconform release: https://github.com/yannh/kubeconform/releases/tag/v0.8.0
- Kubernetes JSON schema snapshot: https://github.com/yannh/kubernetes-json-schema/commit/0c4dd99d9873f7b4c2da24c008476f5841adbe2d
- Cosign release: https://github.com/sigstore/cosign/releases/tag/v3.1.4
- Cosign blob verification options: https://github.com/sigstore/cosign/blob/main/doc/cosign_verify-blob.md
