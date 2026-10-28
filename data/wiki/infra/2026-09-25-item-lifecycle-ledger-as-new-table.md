---
title: Item Lifecycle Ledger as a New Table
tags: [infra, observability, decision]
summary: "To answer 'where did item X stop, and how many stopped there' across ingestion, identity, enrichment, QC, publish and serve, build a new per-item ledger rather than widening an existing ingestion-outcomes table whose best-effort writes and 60-day retention are load-bearing for its own 7-day alarm — keep writes best-effort but logged at error, collapse high-volume serve stages to the served items, bridge early stages from one existing flush site, and document that a zero at a stage with no writer means 'no writer', not 'no items'."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-25-lifecycle-operating-contract.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-25-lifecycle-operating-contract.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-25-lifecycle-operating-contract.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-25-lifecycle-operating-contract.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-25-lifecycle-operating-contract.md
---

# Item Lifecycle Ledger as a New Table

An operating-contract decision in an events-discovery product (repo akira, 2026-09-25).
The goal was that one query answers "where did item X stop, and how many items stopped
at the same place" across nine lifecycle stages, and that six scale gates each have a
real query behind them, with thresholds deliberately left unset ("define now, pick
numbers later").

## Extend or new table?

The closest existing ledger was an ingestion candidate-outcomes table. It had a closed,
ingestion-only six-value stage list, and two postures that are correct for its own job:

- **Best-effort flush.** A failed insert logs and returns. A measurement write must never
  fail the ingestion it measures.
- **60-day ageing.** It feeds a 7-day operational alarm window.

Both are wrong for an audit ledger that has to cover an item's whole life. Widening the
table would quietly change the contract for every existing reader, including the health
check's alarm window. **Decision: a new table (`item_lifecycle_events`), so each table's
retention and durability fit what actually reads it.**

## Decisions inside the new table

- **Still best-effort, but loud.** A measurement write never fails the stage it
  measures, same as every other measurement writer in the codebase. The difference is
  that every failed insert logs at `error`, so a missing row becomes a countable event a
  later watchdog can alarm on. "Auditable" here means "failures are visible", not
  "cannot fail" (compare [[A Trace Is Not a Number of Record]]).
- **No ageing job yet.** It is left off the outcome-log retention list. Indefinite
  retention is a placeholder to revisit once growth is measured, and it is labelled as a
  placeholder.
- **Collapse the volume stages.** "Eligible/servable" and "served" are written together,
  non-blocking after the response, **only for items in the served result set** (5–8 rows,
  the volume the result-set logs already carry). Logging every candidate the hard filter
  evaluates was deferred until a cheaper aggregate exists.
- **One stage, not two, for "enrichment completed and gated".** The "gated" half is
  already answered by the publish-decision table's join to the enrichment ID. A second
  row would duplicate the join.
- **Bridge, don't rewire.** The three earliest stages are mapped from the single
  existing outcomes-flush call site instead of instrumenting six internal ingestion call
  sites. A vocabulary cross-reference test pins the mapping, so a later vocabulary change
  fails a test instead of the bridge going stale silently.
- **Closed reasons in the application, open at the DB.** `item_kind`, `stage` and
  `outcome` are CHECK-constrained. `reason` is mapped to a per-stage closed vocabulary in
  code. An unmapped value becomes `other`, with the raw string kept in `detail`.
- The writer module lives in the one shared tree that every caller tier may import
  without breaking the dependency arrows.

## Zero means "no writer" until the writer lands

Two stage writers (enrichment and QC) were deliberately held for a separate session to
avoid branch collisions. Until they land, **a funnel query returning zero at those
stages means no writer exists, not that no item reached them.** Every doc updated in
that change says so. A stage count is only evidence once its writer is confirmed live
(see [[Silence Reads as Clean]]).

## Smaller findings

- **The missing identity link was itself the evidence.** Accepting a venue candidate
  wrote the candidate→venue link, but every enrichment row was keyed on the candidate
  ID, so enrichment output never followed the resolved identity. The ledger's venue
  identity stage makes that gap queryable. The repair was left to another issue.
- **Privilege was decided early.** The planned operator route keeps the reviewer gate
  unchanged, and the separate admin Basic-auth stays separate: "a reviewer does not
  become an administrator." This was recorded before any route work so the later
  migration phase could not reopen it.
- The migration was validated with `begin; \i file; rollback;` against the local stack
  before the push (see [[Migration Done Means Pushed and Probed]]).

## See Also
- [[A Trace Is Not a Number of Record]] — extends (an append-only ledger per seam, written best-effort)
- [[Silence Reads as Clean]] — related (zero at a writer-less stage)
- [[Every Column Names Its Reader]] — related (retention and durability follow the reader)
- [[Indistinguishable Rejection on Best-Effort Sinks]] — related (best-effort writes need a visible failure)
- [[Kiez Project]] — instance-of
