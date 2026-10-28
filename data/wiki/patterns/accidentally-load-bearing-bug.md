---
title: Fixing an Accidentally Load-Bearing Bug
tags: [infra, pattern]
summary: "Before closing a gap, ask what the gap was silently doing: a batch selector that re-swept content held by dead jobs was double-charging, but that same missing check was the only thing rescuing content stranded by crashed jobs — adding the exclusion alone would have traded recoverable spend for a permanently invisible catalogue slice, so the fix had to ship with an explicit release-valve state."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-07-dis202-batch-enrichment.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-07-dis202-batch-enrichment.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-07-dis202-batch-enrichment.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-07-dis202-batch-enrichment.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-07-dis202-batch-enrichment.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-07-dis202-batch-enrichment.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-07-dis202-batch-enrichment.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-08-dis202-batch-enrichment.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-08-dis202-batch-enrichment.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-08-dis202-batch-enrichment.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-08-dis202-batch-enrichment.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-08-dis202-batch-enrichment.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-08-dis202-batch-enrichment.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-08-dis202-batch-enrichment.md
---

# Fixing an Accidentally Load-Bearing Bug

From the review-fix round of the akira batch-enrichment plan.

## The finding

The blocker: the backlog-selection query did not exclude content already held by an
outstanding batch job, so the same item could be submitted (and billed) twice. The obvious
fix is one predicate — exclude anything with a pending batch item.

A second reviewer noticed the missing exclusion had been **accidentally load-bearing**.
Content held by a *dead* job (expired past the provider window, crashed mid-flow) was
re-swept on the next run *precisely because nothing checked*. Adding the exclusion alone
would have converted a double-charge bug into permanent invisibility: those items would be
"held" forever by a job that would never complete, and never enriched again.

That is strictly worse. Overspend is visible on an invoice and recoverable; a
silently-never-enriched slice of the catalogue produces no error, no alert and no row.

## The fix is one mechanism, not two

- Add a terminal **`stranded`** item status. The poller transitions a dead job's pending
  items to `stranded`.
- `stranded` is **deliberately absent** from the "held" set the selector excludes, so
  stranded content becomes selectable again — the behaviour the bug used to provide by
  accident, now provided on purpose and observable.
- Retry is idempotent by reusing the same ownership query: a retry creates a new job whose
  items are `pending`, which *is* the "already retried" signal.

The blocker fix and the release valve were landed together, with tests verified red
against a neutralised exclusion and green with it.

## The general rule

When a fix narrows what a selector, filter or gate admits, enumerate **which rows only
reached the happy path through the gap** before merging. For each class, decide explicitly:
give it a named state that re-admits it, or accept its exclusion in writing. A bug that has
been live long enough has dependents, and they are usually failure-recovery paths nobody
designed.

## See Also
- [[Batch Path Through the Synchronous Chain]] — related (the orchestrator this was found in)
- [[A Wrong Finding Can Manufacture Its Failure]] — related (a "fix" that causes a worse failure than the defect)
- [[Silence Reads as Clean]] — related (permanent invisibility emits no signal)
- [[Map Every State to Its Writer]] — extends (the release-valve state needs a named writer — here the poller)
- [[Paired Bugs That Cancel]] — related (two defects that mask each other; fix both together)
