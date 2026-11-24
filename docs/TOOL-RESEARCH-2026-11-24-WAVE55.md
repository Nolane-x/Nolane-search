# Wave 55 research — Wikipedia, Wikivoyage and Wiktionary

Date: 2026-11-24
Repository: https://github.com/Nolane-x/Nolane-search
Branch: feat/wave-55-wikipedia-travel-wiktionary

## Product intent

Add everyday reference, travel and language-learning discovery without adding another developer-oriented tool set. The integration reads the official MediaWiki Action API from fixed, allowlisted Wikimedia project hosts. It does not scrape HTML pages, edit wiki pages or crawl entire projects.

## Wikipedia — general knowledge

Project API: https://www.mediawiki.org/wiki/API:Action_API
Action API entry point pattern: https://www.example.org/w/api.php
Search and page properties: https://www.mediawiki.org/wiki/API:Lists and https://www.mediawiki.org/wiki/API:Properties
Page thumbnails: https://www.mediawiki.org/wiki/Extension:PageImages

Tools:
- search_wikipedia_articles — search English, Vietnamese, Japanese, French, Spanish or German Wikipedia.
- get_wikipedia_article — bounded plain-text article extract with original page link, available categories and a validated thumbnail URL where one exists.

Limits:
- One request returns at most 10 search results.
- Article extract is capped at 8,000 characters.
- Page image is accepted only from upload.wikimedia.org.
- Search and article titles are passed as query parameters; no user-controlled host or API path.
- Page metadata and snippets are bounded before returning to the model.

## Wikivoyage — travel planning

Project API: https://en.wikivoyage.org/w/api.php and https://vi.wikivoyage.org/w/api.php

Tools:
- search_wikivoyage_guides — discover destination guides in English or Vietnamese.
- get_wikivoyage_guide — retrieve a bounded article extract and link to the guide's original page.

Travel safety:
- Wikivoyage is community-written and can be incomplete or stale.
- Transport availability, fares, opening hours, safety conditions, visa/entry requirements and business status may change. The guide is for discovery and planning, not a live booking or authoritative government notice.
- Always link to the original guide and instruct the model to verify time-sensitive information with official local providers.

## Wiktionary — language learning

Project API: https://en.wiktionary.org/w/api.php and https://vi.wiktionary.org/w/api.php

Tool:
- lookup_wiktionary_entry — retrieve an English or Vietnamese dictionary entry as bounded plain text with its original page link and available categories.

It does not claim to perform machine translation or to normalize dialect, register, pronunciation or regional variants. The source entry should be checked in context.

## Wikimedia API etiquette and resilience

- Every call sets a descriptive User-Agent and Api-User-Agent header.
- Requests use JSON, maxlag=5 and a 12-second timeout.
- The adapter performs one bounded call per tool invocation; it does not crawl, paginate large datasets or fan out requests in parallel.
- HTTP 429/503 and MediaWiki maxlag/API error payloads are surfaced explicitly; there is no aggressive retry loop.
- A short result window and request-level limits keep the tools interactive and reduce load.
- MediaWiki documentation recommends an informative User-Agent, considerate request cadence and maxlag to yield to busy replicas. In 2026, MediaWiki also documents per-user read rate limits; Nolane must remain a low-volume interactive client.

## Validation and boundaries

- Mocked tests cover all five operations, Vietnamese/English language routing, search snippets, article extracts, categories, canonical links, thumbnail host validation, missing pages, invalid language, 429 and maxlag.
- The API can be available while article content remains incomplete or disputed; provider health is not factual verification.
- No new secret, package, D1 migration, Worker binding or file-processor catalog change is required.
- Live upstream provider query and content checks remain separate from mocked CI.

## Sources
- MediaWiki Action API: https://www.mediawiki.org/wiki/API:Action_API
- API Etiquette: https://www.mediawiki.org/wiki/API:Etiquette/en
- API FAQ / query limits: https://www.mediawiki.org/wiki/API:FAQ/en
- PageImages API: https://www.mediawiki.org/wiki/Extension:PageImages
- MediaWiki lists and properties: https://www.mediawiki.org/wiki/API:Lists and https://www.mediawiki.org/wiki/API:Properties
