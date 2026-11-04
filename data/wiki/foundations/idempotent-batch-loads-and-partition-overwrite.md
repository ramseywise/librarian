---
title: "Idempotent Batch Loads and Partition Overwrite"
tags: [foundations, pattern]
summary: "A task is idempotent when rerunning it for the same period leaves the same state as running it once; overwrite the period in one transaction by default, merge only where no period owns the row, and keep tasks pure and side effects keyed."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--03-transform-and-orchestrate--notes--04-idempotency-and-backfills.md
  - data/raw/repos/learn-ai-engineering/data-engineering--02-ingest-and-modelling--notes--01-ingest.md
---

# Idempotent Batch Loads and Partition Overwrite

Every pipeline gets run twice eventually: a timeout after a successful write triggers a retry, a bug needs a month redone, a source sends a correction. A load that gives a different answer on the second run turns every timeout into a data bug. Idempotency makes retries safe and backfills a loop. Batch jobs that replace their output are forgiving in a way online databases are not: roll back the code and rerun, and the output is right (human fault tolerance). The functional framing: a task behaves like a pure function of its inputs and its period, overwrites a partition rather than mutating rows, and reads immutable raw inputs so any output can be recomputed. For stream-style writes, setting a value is naturally idempotent while incrementing is not (an append is a kind of increment), unless the offset that produced each write is stored.

## Three write modes
Appending the same day twice doubled the table (1,100 trips, then 2,200) with no error.
| Write mode | Rerun | Rows deleted upstream | Use |
|---|---|---|---|
| Append | duplicates | stay | almost nothing |
| Overwrite a partition | same result | disappear | almost every batch table; the default |
| Merge on a key | same result | stay | slowly changing entities and CDC, where no period owns the row |

Overwrite means delete the logical date's rows and insert, both in one transaction so readers see old or new and never a gap. Merge never hears about a row the source removed: after a 10 percent correction removing rows, overwrite showed 1,044 where merge still held 1,160.

## Replacing a window in a transaction

An `append` load for one day timed out at the client after it had already committed, and the scheduler retried: 2,000 rows holding 1,000 distinct trips. Every downstream sum is twice the truth, and nothing failed, so nothing alerts.

```python
def load_window(day):
    rows = source.execute("SELECT * FROM trips WHERE pickup_date = ?", (day,)).fetchall()
    wh.execute("BEGIN")
    wh.execute("DELETE FROM raw_trips WHERE pickup_date = ?", (day,))
    wh.executemany("INSERT INTO raw_trips VALUES (?,?,?,?,?)", rows)
    wh.execute("COMMIT")
```

Run twice, the table holds 1,000 rows and 1,000 distinct trips. The transaction matters as much as the delete: without it, a crash between the two statements leaves the day empty (count 0). That is worse than duplicates, because the totals look merely low, like a slow day. With the transaction and a rollback in the handler, the count stays at 1,000.

Window replace only works when the source gives whole windows that nobody touches again. For rows that change in place, see [[High-Watermark Incremental Extraction and Its Blind Spots]].

## What a chunked loader leaves to you

A simple batch loader streams a file in 100,000-row chunks (bounded memory), creates the table from the first chunk's schema, and appends the rest. Production adds:

| Property | Naive loader | Production |
|---|---|---|
| Idempotency | `replace` on every run: a full reload | Partition-scoped overwrite, or merge on a key, so a rerun of one day replaces only that day |
| Schema | Inferred from data | Explicit, so one bad file cannot redefine a column |
| Types | Only some columns cast | Cast every column at the boundary or in staging |
| Partial failure | A crash mid-loop leaves a half-loaded table | Load to a temp table, swap on success |

Packaging the loader as a container makes the ingest job a unit an orchestrator can schedule instead of a script on a laptop.

## Purity checklist
Fingerprint a sorted result and compare across runs; a load timestamp from the clock gave 3 distinct results over 3 runs, a pure build 1. Keep load times in a run log.
| Impurity | Fix |
|---|---|
| `now()`, `current_date` | take the logical date as a parameter |
| latest-state dimension | join as of the logical date |
| `row_number()` without a total order | order by something unique |
| unseeded randomness | seed from the logical date |
| live API read during transform | land the response, transform the landed file |
| "whatever is in the folder" | read only the logical date's partition |

Keep raw immutable; if landing changes in place, no output reproduces.

## Side effects
An email or payment cannot be overwritten. Record an idempotency key derived from the logical date, not generated per attempt, and check it first. There is a gap: a crash between recording and sending loses the send, and the reverse order sends twice. Exactly-once toward an outside system needs its cooperation, usually by it accepting the key (the end-to-end argument: only the endpoints can complete the guarantee). Otherwise choose at-least-once or at-most-once and say which. Keep side effects out of backfills by default as a separate final task.

## Pitfalls
- Appending in a retried task; merging where overwrite is right.
- Delete and insert in separate transactions: a crash leaves the day empty.
- Transforming on the way in. Keep the raw layer as received so everything can be re-derived when a transform turns out wrong.

## See Also
- [[Write-Audit-Publish and Atomic Visibility]] — extends
- [[Backfills, As-Of Dimensions and Past-Dependent Tables]] — extends
- [[Orchestrator Core Loop, Logical Dates and Retries]] — prerequisite-for
- [[dbt Incremental Models: Watermarks, Lookback and Strategies]] — related
- [[Rerunnable Cleaning Loader with Assertions]] — related
- [[Idempotent Backfills and Dated Corrections]] — related (incident repair: corrections and late data)
- [[High-Watermark Incremental Extraction and Its Blind Spots]] — extends (what to do when rows change in place)
- [[Change Data Capture and the Dual-Write Problem]] — related
- [[SQL Schema Design and DDL]] — related (ON CONFLICT upserts and atomic transactions)
- [[Data Engineering Foundations]] — related
