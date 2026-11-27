# Wave 75 research — cross-URL duplicate coverage hints

Date: 2026-11-27  
Status: implementation candidate in [PR #154](https://github.com/Nolane-x/Nolane-search/pull/154).

## Problem statement

Federated retrieval can return one normalized URL from multiple providers, which Wave 74 now records as `discoveredBy`. A separate issue remains: distinct URLs may contain near-identical copies of the same article. Treating every URL as independent evidence risks overstating how many distinct reports support a claim.

## Selected approach

Use a bounded, deterministic, pairwise similarity hint over the already-ranked result set (maximum 20 results):

1. Require distinct publisher-site keys, not merely different URL paths or subdomains.
2. Require valid publication timestamps no more than seven days apart.
3. Tokenize title and excerpt with the existing NFKC/lowercase tokenizer and a conservative English/Vietnamese stop-word list.
4. Require at least five meaningful title tokens and Jaccard similarity ≥0.90.
5. Require at least 18 meaningful excerpt tokens, containment ≥0.88 and excerpt Jaccard ≥0.72.
6. Form complete-link groups so every member must match every other member, then annotate each member without changing result ordering or deleting any URL.

These thresholds are deliberately strict. They are initial engineering heuristics, not empirically calibrated classifier thresholds.

## Why not collapse results?

A similarity match cannot establish that two pages share a publisher, were syndicated, or independently reported an event. Both result URLs remain visible and citeable. The warning tells users and synthesis models not to count the grouped URLs as independent corroboration, while leaving final source evaluation to the reader.

## Known limitations

- The publisher-site key uses a short common compound-suffix list, not the full Public Suffix List. Some hosting platforms use multi-tenant subdomains, and this can cause false site separation or grouping.
- Rewritten, translated, substantially shortened or differently dated reprints can be missed.
- Separate reporting that quotes the same press release may still look similar; the warning is therefore phrased as "có thể trùng nội dung".
- Invalid/missing timestamps and short excerpts are not matched, reducing false positives at the cost of recall.
- The similarity result is not a copyright determination, authorship claim, source-trust score or factual verification.

## Verification in PR #154

- Positive match retains both distinct URLs and annotates group size/hostnames.
- Similar titles with materially different excerpts are not grouped.
- Publication dates outside the seven-day window are not grouped.
- Subdomains under the same publisher-site key are not grouped.
- Telegram Search and Deep Search show the uncertainty warning.
- Provider AI synthesis test verifies that duplicate-group hints enter its evidence context and the system prompt forbids counting them as independent corroboration.

No new provider, API key, secret, hosted compute, recurring cost or database migration is required.
