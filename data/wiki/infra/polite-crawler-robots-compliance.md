---
title: Polite Crawler Robots Compliance
tags: [infra, pattern]
summary: "Making an ingestion crawler honour robots.txt: hand-roll a deliberately minimal parser with its unimplemented boundary written in the docstring, fail open when robots.txt can't be fetched, raise a distinct error that the run log classifies as 'blocked' (we chose not to fetch), not 'failed', and only let Crawl-delay lengthen a source's configured rate limit, never shorten it."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-06-dis197a-beta-blockers.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-06-dis197a-beta-blockers.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-06-dis197a-beta-blockers.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-06-dis197a-beta-blockers.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-06-dis197a-beta-blockers.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-06-dis197a-beta-blockers.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-06-dis197a-beta-blockers.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-06-dis197d-corpus-legal.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-06-dis197d-corpus-legal.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-06-dis197d-corpus-legal.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-06-dis197d-corpus-legal.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-06-dis197d-corpus-legal.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-06-dis197d-corpus-legal.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-06-dis197d-corpus-legal.md
---

# Polite Crawler Robots Compliance

A pre-beta compliance lane for a city-events crawler (repo akira) found that the fetcher had
a per-domain rate limiter and retry/backoff, but it never fetched robots.txt, never parsed
it, and ignored `Crawl-delay`. Its User-Agent was also a placeholder (`…Bot/1.0
(+https://example.com)`). The fix looked like "change one string". It turned out to be the
largest of three lanes: about 90 lines of new logic, plus a rewrite of 5 of the 6 tests in a
well-covered fetcher test file. These are the decisions worth reusing.

## Decisions

- **Hand-roll a minimal parser and name what it leaves out.** A `robots-parser` package was
  in `node_modules`, but only as a transitive dependency of a Lighthouse CI tool. Code that
  relies on an undeclared transitive package breaks silently the day the other tool's
  dependency tree changes. The team picked a roughly 3-directive parser over declaring the
  dependency: `User-agent` group selection, `Disallow` as a plain prefix match, and
  `Crawl-delay`. **Deliberately not implemented:** `*`/`$` wildcards, the RFC 9309
  most-specific-match rule where `Allow` overrides `Disallow`, and `Sitemap:`. That list
  goes into the module docstring, so a later reader knows the boundary was a choice, not an
  oversight. Small venue sites overwhelmingly use plain path prefixes, so wildcard rules are
  the accepted long tail.
- **Fail open when robots.txt can't be fetched.** If the fetch errors, treat it as allow-all.
  A parser bug then behaves at worst like the status quo. It can't silently stop ingestion.
- **A refusal gets its own name.** A disallowed path throws a distinct
  `RobotsDisallowedError`. The run-log classifier used to map only `HTTP 403|429` to
  `'blocked'` and everything else to `'failed'`, which would have filed "we chose not to
  fetch this" under "the fetch broke". It now classifies the robots refusal as `'blocked'`.
  A false positive then shows up in run logs with the exact URL, not as a silent empty
  result.
- **Crawl-delay can only lengthen.** A per-source `rate_limit_ms` column already existed.
  The robots `Crawl-delay` extends it and never shrinks it. Slower runs for sources with
  long delays are the intended effect. If that hurts, the fix is to parallelise across
  domains, not to ignore the directive.
- **Use a real identity, and don't guess public facts.** The User-Agent carries a working
  contact address, following the forward-geocoder UA already in the repo (Nominatim's usage
  policy requires one), and points to a `/bot` identity page. The production domain was not
  confirmed anywhere in the tree, so the UA ships a greppable `[[NEEDS: …]]` token instead of
  a guessed domain. A wrong domain would have reached every one of the ~92 site operators the
  crawler visits.

## Parser vs. posture

The parser answers "may I fetch this path?". It doesn't answer what to do when a *source*
keeps hitting disallows. The companion legal lane treated that as an operational call, not
a legal one, with three options: record-and-surface (the proposed default), silently skip,
or pause the source. It proposed storing the posture on the source row, next to the
existing human-reviewed `redistribution_posture` column, rather than adding a second
mechanism.

## See Also
- [[Change the Channel, Not the Count]] — extends (robots is not the constraint; terms are; this is the fetcher-side mechanics)
- [[Layered Ingestion Failure Posture]] — related (another fail-open choice at a specific grain)
- [[Unfinished Work Must Fail Closed]] — related (the greppable `[[NEEDS:` token for facts nobody in the repo can supply)
- [[A Check Must Say Why It Could Not Check]] — related (blocked vs failed is the same "name the reason" move)
