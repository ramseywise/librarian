---
title: "Idempotent Batch Loads and Partition Overwrite"
tags: [foundations, pattern]
summary: "A task is idempotent when rerunning it for the same period leaves the same state as running it once; overwrite the period in one transaction by default, merge only where no period owns the row, and keep tasks pure and side effects keyed."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--03-transform-and-orchestrate--notes--04-idempotency-and-backfills.md
---

# Idempotent Batch Loads and Partition Overwrite

Every pipeline gets run twice eventually: a timeout after a successful write triggers a retry, a bug needs a month redone, a source sends a correction. Idempotency makes retries safe and backfills a loop. Batch jobs that replace their output are forgiving in a way online databases are not: roll back the code and rerun, and the output is right (human fault tolerance). The functional framing: a task behaves like a pure function of its inputs and its period, overwrites a partition rather than mutating rows, and reads immutable raw inputs so any output can be recomputed. For stream-style writes, setting a value is naturally idempotent while incrementing is not, unless the offset that produced each write is stored.

## Three write modes
Appending the same day twice doubled the table (1,100 trips, then 2,200) with no error.
| Write mode | Rerun | Rows deleted upstream | Use |
|---|---|---|---|
| Append | duplicates | stay | almost nothing |
| Overwrite a partition | same result | disappear | almost every batch table; the default |
| Merge on a key | same result | stay | slowly changing entities and CDC, where no period owns the row |

Overwrite means delete the logical date's rows and insert, both in one transaction so readers see old or new and never a gap. Merge never hears about a row the source removed: after a 10 percent correction removing rows, overwrite showed 1,044 where merge still held 1,160.

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

## See Also
- [[Write-Audit-Publish and Atomic Visibility]] — extends
- [[Backfills, As-Of Dimensions and Past-Dependent Tables]] — extends
- [[Orchestrator Core Loop, Logical Dates and Retries]] — prerequisite-for
- [[dbt Incremental Models: Watermarks, Lookback and Strategies]] — related
- [[Rerunnable Cleaning Loader with Assertions]] — related
