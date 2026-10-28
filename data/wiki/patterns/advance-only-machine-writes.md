---
title: Advance-Only Machine Writes on a Shared Lifecycle
tags: [patterns, infra, pattern]
summary: "When a pipeline and a human share one lifecycle column, the machine writer moves rows forward only out of states it owns, never into the visible end state, and never over a human decision. The guard is a WHERE filter on the UPDATE itself, so row atomicity closes the race."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-08-26-b21-review-status-writeback.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-26-b21-review-status-writeback.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-26-b21-review-status-writeback.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-26-b21-review-status-writeback.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-26-b21-review-status-writeback.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-26-b21-review-status-writeback.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-26-b21-review-status-writeback.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-25-publishing-workflow.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-25-publishing-workflow.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-25-publishing-workflow.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-25-publishing-workflow.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-25-publishing-workflow.md
---

# Advance-Only Machine Writes on a Shared Lifecycle

This comes from a writeback plan in the akira event pipeline. Enrichment was writing its result to
a legacy `status` column. Visibility, meanwhile, depended on a newer `review_status` column. So
enrichment's output never reached what users saw. A callback route that should have bridged the
two columns turned out to be dead code that still had a live URL.

## The rule

One column was shared by a machine writer (enrichment) and humans (reviewers). The plan fixed
three rules for the machine writer:

1. **It never lands on the visible end state.** Enrichment writes only `draft` or
   `needs_review`, never `published`. Publishing is a separate decision with its own owner.
2. **It only moves rows out of states the machine owns.** If the current value is `draft` or
   `needs_review`, the machine may move the row.
3. **It never overwrites a human decision.** `approved`, `rejected`, `duplicate` and `archived`
   are terminal from the machine's point of view. A re-run of enrichment must not undo an
   operator's reject.

## Put the guard on the write, not before it

The plan did not read the row, check its state and then write. It put the guard in the statement
itself:

```
UPDATE ... SET review_status = $new
WHERE id = $id AND review_status IN ('draft', 'needs_review')
```

A read-then-write sequence has a gap. A reviewer can approve the row after the read and before
the write. With the filter in the UPDATE, the database's row-level atomicity resolves that race,
and a zero-row result simply means a human got there first.

## Review verdicts stay measurement-only (2026-09-25)

A month later, the publishing-workflow spec made the human side of this boundary explicit.
Every review surface writes only to verdict tables, and to a few content fields
(`needs_review`, `start_at`, `image_url`). None of them writes `review_status = 'published'`.
The only path to `published` is a guarded CLI publish pass, capped at 200 rows per run and
gated behind repository variables. The plan recorded this as intentional. Having N agreeing
verdicts auto-publish a row would be a product decision with no spec behind it yet, so it was
named as a future option, not a gap. Undated draft rows got a read-only report, not a new
status. The reason: `archived` already means "was live and is over", and stretching it to
cover "never had a date" would break that single meaning.

## Options rejected

- **Teach the publisher to read the legacy column as well.** This brings back a second
  visibility workflow, so two columns would decide what is shown.
- **Do nothing.** Enrichment would keep running and paying for results that never change
  visibility.

## See Also
- [[State Writer Never Owns Side Effects]] — related (the same split: one writer per concern)
- [[Principal Write Surface Matrix]] — instance-of (each principal gets a bounded set of transitions on a shared column)
- [[Every Column Names Its Reader]] — related (the legacy column had a writer and no reader)
- [[Silence Reads as Clean]] — related (enrichment "succeeded" while visibility never moved)
- [[Re-Crawl Adds, Never Overwrites]] — related (the same principle applied to content columns)
- [[Arm Unattended Writers by Risk Type]] — related (the switches that gate the publish pass)
- [[Idempotency Lives on the Link Column, Not the Synthetic Key]] — related (synthesized rows land in a terminal state)
