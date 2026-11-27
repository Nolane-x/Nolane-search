# Wave 75 handoff — 2026-11-27

**Scope:** conservative cross-URL duplicate-coverage hints  
**PR:** https://github.com/Nolane-x/Nolane-search/pull/154  
**Branch:** `feat/wave-75-syndicated-coverage-detection`  
**Verification:** PR CI #46009196913 passed TypeScript, Vitest, deployment-script checks, Python runner tests, Windows Media Node policy/storage/HTTP tests, PowerShell installer syntax and Worker build.  
**Release state:** PR candidate. Not merged or deployed yet.

## Why this exists

Wave 74 preserves the list of search providers that found the same normalized URL. It does not identify substantially similar article copies returned under different URLs. In research tasks, counting several copies as independent reports could overstate the breadth of evidence.

## Behavior

- The ranker annotates likely duplicate coverage only when results use different publisher-site keys, both have valid publication dates within seven days, title-token Jaccard similarity is at least 0.90, excerpt overlap is high (containment at least 0.88 and Jaccard at least 0.72), and each excerpt has at least 18 meaningful tokens.
- Results are grouped using complete-link matching: each candidate must meet the pairwise threshold against every existing group member.
- The result payload receives optional `possibleDuplicateCoverage` metadata: a local group ID, group size, up to eight hostnames and the algorithm-basis label.
- All original result URLs and ranking positions are retained. No result is removed, merged or rewritten.
- Web Search, Telegram Search and Deep Search show a short similarity hint.
- Browser Ask, Telegram Ask and Deep Search synthesis receive the hint and are instructed not to count grouped URLs as independent corroboration.

## Limits and safety

This is a heuristic, not proof of syndication, copied text, common ownership, factual accuracy or editorial independence. Reprints can have different dates or excerpts and may be missed; unrelated content can occasionally look similar. The feature deliberately favors precision over recall.

The publisher-site key uses a small list of common compound public suffixes. It is not a complete Public Suffix List, so unusual hosting arrangements and multi-tenant domains may be classified imperfectly. Hostnames are surfaced only as context for the warning.

Missing/invalid dates do not match. Results from the same derived publisher-site key do not match. Distinct URLs remain distinct evidence records.

## Operational impact

No new provider, API key, secret, database schema, migration, paid dependency or recurring service is introduced. The optional metadata is compatible with existing cached result objects; older cache records remain valid without it.
