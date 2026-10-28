---
title: Page on a Total Order
tags: [patterns, infra, pattern]
summary: "Offset/range pagination over a capped API (PostgREST's silent 1000-row default) is only correct when the ORDER BY is a total order — page on a non-unique key like `created_at` or `name` and tied rows are dropped or repeated at page boundaries — and a test fake that ignores `.range()` or keeps only the last `.order()` passes whether or not the paging loop exists, so pin the query shape and test against a range-honouring fake."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/reviews/2026-09-18-dis249-dis288-quality-signals.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-18-dis249-dis288-quality-signals.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-18-dis249-dis288-quality-signals.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-18-dis249-dis288-quality-signals.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-18-dis249-dis288-quality-signals.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-27-pr408-facets-v1-hardening.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-27-pr408-facets-v1-hardening.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-27-pr408-facets-v1-hardening.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-27-pr408-facets-v1-hardening.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-27-pr408-facets-v1-hardening.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-28-pr413.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-28-pr413.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-28-pr413.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-28-pr413.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-28-pr413.md
---

# Page on a Total Order

A recurring defect class across a run of akira code reviews: reads against Supabase/PostgREST
that are either not paged at all, or paged on an order that is not a total order.

## Three layers of the same bug

1. **No paging.** PostgREST silently caps an unpaged select at its `db-max-rows` default (1000).
   Below the cap this is invisible. One PR paged correctly in one new file (`PAGE_SIZE = 1000`,
   `.range()` loops) and left two other reads in the same diff unpaged — an inconsistency inside
   one change, not an unknown pattern. See [[Bounded Slice After In-Memory Eligibility]] for why
   a partial read misclassifies rows rather than merely reordering them.
2. **Paging on a non-unique key.** `.order('created_at').range(...)` has no tiebreaker. Rows
   inserted in one statement share `now()`, and Postgres does not guarantee tie order across
   separate range requests, so a row can fall on both sides of a page boundary (read twice) or
   neither (skipped). The same happened with `.order('name')`. In one case the skipped row was a
   natural-key match, so the lookup returned null and the caller inserted a duplicate — exactly
   the failure the lookup existed to prevent. **Fix:** append the primary key,
   `.order('created_at').order('id')`. Where results are keyed into a Map, a repeat is harmless
   and only skips matter; where they feed a lookup or count, both matter.
3. **A capped read, then an in-memory sort.** A list read `.order('id').range(0, PAGE-1)` with
   `PAGE = 2000`, then sorted by priority in memory. The comment said PAGE was "well above the
   scope". Once a filter widened (a null district meant the whole city, about 5,300 rows), the
   priority sort ranked an arbitrary id-ordered slice. **Fix:** page the whole scope, or order
   and filter server-side on the priority; at minimum log when a read fills the page.

## Why tests miss it

- A shared fake recorded `.range()` calls **without slicing** on them, so a paging test written
  against it passed whether or not the loop existed. The fix used a local fake that honours
  `range`, `in` and `eq`, and proved the tests RED against the pre-fix code.
- A row-store fake sorted only by the **last** `.order()` call. After adding the `id`
  tiebreaker it sorted by `id` alone, hiding the primary sort key. It was changed to append sort
  keys as PostgREST does — but a stable-sort fake still cannot reproduce Postgres tie
  instability, so the test also **pins the query shape** (`['created_at', 'id']`).

This is [[A Fake That Conforms to a Broken Seam]] at the query-builder level: the fake implements
the method names but not the semantics that make the defect observable.

## Checklist

- Every multi-row read either has a hard upper bound by construction or loops `.range()` until
  a short page.
- The ORDER BY ends in a unique column.
- Chunk `.in(...)` id lists (e.g. 100 per request) so neither URL length nor the response hits
  the cap.
- A read that fills its page logs it; a fixed PAGE constant is a claim about data size that will
  go stale.
- Tests run against a fake that slices on `range`, plus an assertion on the order keys.

## See Also
- [[Bounded Slice After In-Memory Eligibility]] — extends (implicit cap and in-memory filtering)
- [[A Fake That Conforms to a Broken Seam]] — instance-of
- [[Silent Failure Catalogue]] — instance-of
- [[Natural Key Without a Discriminator Collapses Rows]] — related (a skipped page row defeats natural-key dedup)
