# Wave 17 handoff — Email and JWT security audits

Date: 2026-11-22
Repository: https://github.com/Nolane-x/Nolane-search
Branch: feat/wave-seventeen-email-jwt-auditors

## Scope

Wave 17 is merged and deployed. The two new bounded processors are included in the production catalog (318 tools total).

- email-security-audit: parses EML headers/MIME structure for From/Reply-To/Return-Path domain mismatches, duplicate/missing critical headers, Received hop count, header-asserted SPF/DKIM/DMARC, suspicious URI schemes/known shorteners and high-risk attachment suffixes. Never reports addresses, domains, subject, URLs, attachment names or content. Does not open attachments or perform DNS/network checks.
- jwt-security-audit: finds compact JWT-like strings, decodes header/payload locally and reports algorithm counts, alg=none, missing/expired exp, missing/invalid iat/nbf, lifetime over 90 days, jku/x5u, critical headers and missing issuer/audience. Never reports token, signature or claim values; does not verify signatures or key trust.

## Bounds and interpretation

- EML: at most 10 MiB, 1,000 MIME parts, 500 attachments and 2 MiB body text scanned. Authentication-Results headers can be forged and are not cryptographic proof; no SPF/DKIM/DMARC DNS validation is performed.
- JWT: at most 5 MiB input and 1,000 token-like strings; segments are capped before JSON decoding. The analysis is structural only and must not be interpreted as successful token validation.
- No new dependency, D1 migration, secret or external service is required.

## Acceptance gates

1. 318 unique TypeScript catalog IDs, 318 Python RUNNERS, 318 Python handlers and both tools present in TEXT_OUTPUT_TOOLS.
2. TypeScript/Python pipeline transitions match exactly.
3. Python fixtures assert domain/URL/attachment-name and JWT token/claims are withheld from reports.
4. Type-check, Vitest, deployment-script checks, Python suite and Worker build pass.
5. Worker export/smoke and production deployment pass before counting 318 production.
6. Live Telegram EML/JWT uploads, report delivery and retry remain owner-level E2E.

## Production rollout — 2026-11-22

- PR #67 merged into `main`: https://github.com/Nolane-x/Nolane-search/pull/67
- Main commit: `66aeb33c1319c161b224d8e65df1832e11bce4ac`.
- PR CI [44976302924](https://github.com/Nolane-x/Nolane-search/actions/runs/44976302924), main CI [44977998187](https://github.com/Nolane-x/Nolane-search/actions/runs/44977998187), Worker export/smoke [44977998129](https://github.com/Nolane-x/Nolane-search/actions/runs/44977998129) and production deployment [44977998189](https://github.com/Nolane-x/Nolane-search/actions/runs/44977998189) all passed.
- Deployment verified source, typecheck/Vitest, Worker bundle, runtime-secret upload and Telegram webhook/command registration. D1 migration step was skipped because this release had no schema change.
- Production Worker Version ID: `f3180bcc-896d-4fef-9887-c81146865265`.
- Catalog: 318 production processors. No dependency, migration, secret or external service was added.
