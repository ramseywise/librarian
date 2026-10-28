---
title: Read-Side Retraction by Observer Vintage
tags: [meta, infra, pattern]
summary: "When a new observer starts writing verified records into an append-only, un-backfillable ledger that already holds self-reported ones, mark each record with a three-valued per-write 'observed' field and an observer version stamp, so old records never launder into verified counts and a defective observer's output can be retracted by a read-side filter instead of editing history."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/docs/plans/2026-08-14-gal-14-observed-transitions.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-14-gal-14-observed-transitions.md
---

# Read-Side Retraction by Observer Vintage

Context: the galactus plan-transition ledger (`plan-transitions.jsonl`) is append-only,
unrotated and never backfilled. A PreToolUse hook was added so transitions are *observed*
rather than self-reported (see [[Observed Transitions, Not Declared]]). The goal was to make
a count like "the `EXECUTED → PLANNED` loop-back was traversed 0 times" admissible
evidence. The hook itself rolls back in one line; **its output does not roll back at all**
— and the first draft reasoned only about the reversible half.

## Four mechanisms

1. **Separate populations, never merge.** Once some records are verified, a count over the
   whole file silently launders the older self-reported ones. The reader reports verified
   and unverified populations separately. Absent field = "written before the observer
   existed" — the honest reading, needing no migration.
2. **Three-valued, not boolean.** `verified` / `skipped` (ran, nothing to check) /
   absent (could not run). A boolean collapses "the observer could not run" into "the
   observer found nothing" — and a crashed hook that exits 0 is otherwise
   indistinguishable from an approving one. The token is written **only on the verified
   path**, so a crash produces *absence*, never `verified`.
3. **Per-write, not per-session.** A session-latched "observer was on" sentinel certifies
   sessions, not transitions, and re-creates the laundering. The token is keyed to
   `(doc, from, to)` and consumed on read.
4. **Version-stamp the observer.** Each record carries an `observer` integer. To retract a
   defective vintage, bump the integer and have the reader report per-vintage counts, so a
   known-bad range is **excluded by selection rather than by editing**. Hand-editing the
   JSONL is explicitly not the rollback path — it destroys the audit trail the build exists
   to create.

## Ordering: write to the permanent file last

The step that writes the new field into the permanent ledger is sequenced **after** the
observer has run in front of real sessions. A defect found in that window costs nothing,
because no field exists yet to be wrong. Do not promote the ledger step early "to get it
done."

Also: append the new field *outside* any existing dedup key — adding it inside a
substring-matched record would have changed dedup behaviour and reintroduced
double-counting.

## See Also
- [[Observed Transitions, Not Declared]] — extends
- [[Append-Only Log Writer Invariants]] — extends (reader-side consequences of append-only)
- [[Void, Don't Close, an Invalid Measurement]] — extends (retract by sidecar/flag, never edit history)
- [[Silence Reads as Clean]] — instance-of (could-not-run must not read as found-nothing)
