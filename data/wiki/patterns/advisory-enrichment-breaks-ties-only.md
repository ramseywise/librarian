---
title: Advisory Enrichment Breaks Ties Only
tags: [patterns, infra, pattern]
summary: "Server-side lookups against an external registry should be advisory: never fail or delay the request, keep a tri-state (undefined = not attempted, null = no match) plus a stored lookup status, act on the decision only as a tiebreak when user-stated facts are silent, and surface everything else as reviewer flags."
updated: 2026-10-17
sources:
  - data/raw/repos/nonprofit-success-ai/.claude--docs--plans--2026-10-14-r19-scout-propublica-enrichment.md
  - data/raw/repos/nonprofit-success-ai/.claude--docs--archive--propublica-lookup--spec--nonprofit-lookup.md
---

# Advisory Enrichment Breaks Ties Only

An intake router decides from what an applicant wrote. An external public registry (here,
IRS nonprofit filings) can add revenue, tax status and filing recency. The risk is that the
enrichment quietly becomes the decision: a flaky upstream blocks intake, a stale filing
overrides what the applicant said, or a missing record is read as a negative signal.
nonprofit-success-ai bounded the enrichment like this.

## Mechanism

- **Never fails, never delays.** The lookup runs server-side before routing, behind a
  timeout. Any upstream failure (502, timeout, unexpected shape) becomes status
  `unavailable`, the helper never throws, and the intake still files.
- **Tri-state input.** `registry?: Record | null`. `undefined` means no lookup was
  attempted (evals, demo, tests). `null` means a lookup ran and nothing matched. Every
  consumer treats `undefined` as "no lookup", which makes rollback a no-op.
- **Stored status with an invariant.** A `registry_lookup` enum column
  (`matched/not_found/ambiguous/unavailable/skipped`) sits next to the jsonb record, with
  a check constraint that `matched` ⇔ record present. The route writes both. They are
  facts the server fetched, not claims the applicant can submit.
- **Explicit match rule.** An EIN uses the direct endpoint. A name search counts as a match
  only on a single hit or an exact normalised-name hit. Several hits with no name match is
  `ambiguous`, not "take the first".
- **Acts only in the tiebreak.** Readiness scores do not change. Registry revenue stands
  in for org size **only when the free-text size answer matches neither signal**. When the
  applicant's text matches, the text wins.
- **Everything else becomes a reviewer flag.** No record found, a non-standard tax
  subsection, and a newest filing older than three years are each shown to the human, and
  none of them changes the routing.
- **The model gets the same rule.** Registry facts never change the bucket outside the
  tiebreak, and a missing record is a flag, not a bucket change. The registry line goes
  inside the partner-data delimiter (see [[Keyless Injection Regression Suite]]).

## Status codes, caching, logging (the lookup endpoint)

- An unknown identifier is `404 not_found`. A known org with no extracted filings is
  `200` with `latestFiling: null`. A search with no hits is `200` with an empty list.
  "We know nothing" is kept separate from "they have no filings".
- `Cache-Control: private` (an hour on a hit, minutes on a miss, `no-store` on errors).
  This is **browser-only by design**, because a shared CDN cache would serve one user's
  authenticated response to another.
- Log the route, step, code, upstream status and duration only. The search text may be an
  organisation name, and it is never logged.

## See Also
- [[Input-Starved Enrichment]] — extends
- [[Hide-Unknown Display Contract]] — extends
- [[Four-Source Provenance Contract]] — extends
- [[Keyless Injection Regression Suite]] — extends
