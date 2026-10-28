---
title: Bounded Slice After In-Memory Eligibility
tags: [patterns, infra, pattern]
summary: "When eligibility is decided in memory after the fetch (held-by-batch, hash-already-enriched, skip reasons), a SQL `LIMIT N` can return N rows that all get filtered out. So fetch everything with explicit pagination, order with a pure function, then truncate the candidate list but never the skip accounting. An implicit API row cap (PostgREST's 1000) makes the 'everything' silently partial, and that misclassifies rows rather than just reordering them."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-15-dis271-batch-slice-limit.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-15-dis271-batch-slice-limit.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-15-dis271-batch-slice-limit.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-15-dis271-batch-slice-limit.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-15-dis271-batch-slice-limit.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-15-dis271-batch-slice-limit.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-15-dis271-batch-slice-limit.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-15-dis271-batch-slice-limit.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-15-dis271-batch-slice-limit.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-15-dis271-batch-slice-limit.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-15-dis271-batch-slice-limit.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-15-dis271-batch-slice-limit.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-28-pr413.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-28-pr413.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-28-pr413.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-28-pr413.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-28-pr413.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-15-dis263-accepted-candidate-bridge.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-15-dis263-accepted-candidate-bridge.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-15-dis263-accepted-candidate-bridge.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-15-dis263-accepted-candidate-bridge.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-15-dis263-accepted-candidate-bridge.md
---

# Bounded Slice After In-Memory Eligibility

From akira's batch-enrichment slicing plan (DIS-271). The batch selector returned every
eligible backlog row. The spend ceiling on a batch submit **refused outright** when the
estimate was too large; there was no partial-submit path. So the only choices were "the
whole backlog or nothing". The goal was `--limit N` with a stated, reproducible order, so a
refusal becomes a bounded slice.

## Why not `ORDER BY … LIMIT`

- **Filters live after the fetch.** Rows held by an in-flight batch, rows whose content hash
  matches a current enrichment, and past events are all excluded in memory. A SQL-side
  `LIMIT 50` could return 50 rows that all get filtered, leaving zero candidates from a
  backlog of thousands.
- **The ordering key and the eligibility live on different tables.** The order uses
  `start_at` on the content table, but eligibility needs the enrichment and batch-item
  tables as well. A single-table `ORDER BY … LIMIT` can't express that without a join the
  codebase doesn't otherwise use.

So: fetch fully, decide in memory, order with an exported pure
`orderBacklogCandidates(candidates, vertical)`, and only then truncate. The ordering is
explicit. Events go soonest-upcoming first, which is also the set most urgent to enrich
before it can publish. Standing content, which has no date, goes by id ascending: stable,
with no claim beyond "same slice, same order". Ties break on id.

## The hidden prerequisite: the implicit row cap

Neither of the selector's reads had `.order()`/`.range()`. Both relied on PostgREST's
default `db-max-rows` (1000). Below 1000 rows this is invisible, and the backlog was already
at 418 for one vertical. Past the cap there are two failures:

1. ordering a truncated, arbitrarily-ordered fetch is not deterministic;
2. worse, if the **current-enrichment** read truncates, already-enriched rows past the
   cutoff are classified as unenriched and re-submitted. That is a correctness bug, not an
   ordering one.

The fix reused the repo's existing convention: `PAGE_SIZE = 1000`, `.order('id').range()`
in a loop until a short page comes back. The same gap in a sibling re-enrichment selector
was recorded as a follow-up rather than silently left. The publish-module refactor found
the same truncation in its own reads that week
([[Characterization Pins Before Extraction]]).

## Rules that came out of it

- **Truncate candidates, never the skip list.** The `skipped` accounting stays a full record
  of what the sweep declined and why, whatever the slice size.
- **No default limit.** Omitting the flag keeps "submit everything eligible" exactly as
  before, so existing scripts see no behaviour change.
- **Say when a flag is ignored.** `--limit` with `--missing` (re-enrichment mode) prints a
  one-line notice that the limit is ignored rather than silently doing nothing.
- **Test the page-2 error path.** Review found that the fake client never returned an error,
  so a later edit that swallowed a page-2 error would return a *partial* set as if it were
  complete, and nothing would go red. The fix added a `queueError({atCall})` hook and two
  tests that fail when the `if (error) throw` line is commented out. Pagination loops have
  a failure mode that single reads don't: partial success that looks like success.
- **Don't let the docs sanction a consumer that doesn't exist.** The decision record said
  the ordering function was exported "so the experiment runner can call it". No such caller
  existed, and a reviewer read that sentence as licence for a new dependency arrow. It was
  reworded to give the real reason: a pure function, tested directly.

## The cap in review: three more places it hid (akira reviews, 2026-09-14/15)

- **A recovery pre-query with no limit and no order.** A query collecting event ids with a
  future occurrence was meant to rescue merged events. Past 1000 rows it would return an
  arbitrary subset and log nothing, the very silent truncation the module's own pool-cap log
  existed to prevent. Fix: select only the id, order it deterministically, `.limit()` it, and
  log at `error` when the limit binds.
- **A per-batch join that multiplies.** 100 parent ids times more than 10 child rows each
  exceeds the cap inside a single batch. The map then holds an arbitrary subset, and a parent
  whose returned children are all past reads as expired. Fix: page each chunk with
  `.order('event_id').order('id').range()` until a short page, with a page ceiling and an
  `error` log.
- **`.range()` paging without `.order()`.** Postgres gives no ordering guarantee across separate
  queries, so pages can skip or repeat rows, and a duplicate check can miss the one row it
  exists to find. The review asked for two tests: a full first page with the target row on page
  2, and a page-2 error that must fail closed.

To make the cap testable, the fake client was taught to **emulate PostgREST's 1000-row cap**.
The paging test then went red first ("expected 1000 to have a length of 1001"), and only after
that was the paged query probed against production.

## See Also
- [[Silent Failure Catalogue]] — instance-of (implicit row cap as a silent partial read)
- [[Characterization Pins Before Extraction]] — related
- [[Batch Path Through the Synchronous Chain]] — related (the batch enrichment path this slices)
- [[The Run Record Belongs to the Process]] — related (the scheduled sweep that consumes slices)
- [[Red-Then-Green Proof for Fix-Stage Tests]] — related (error-path tests proven non-vacuous)
- [[Page on a Total Order]] — extends (tiebreakers, capped read then sort, fakes that ignore range)
