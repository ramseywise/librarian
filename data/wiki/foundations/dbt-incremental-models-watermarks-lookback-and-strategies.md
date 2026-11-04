---
title: "dbt Incremental Models: Watermarks, Lookback and Strategies"
tags: [foundations, pattern]
summary: "An incremental model carries two code paths, and a watermark with no key duplicates the boundary row while a bare greater-than watermark loses late rows silently; use a unique key, a lookback sized from measured lateness, and a periodic full refresh."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--03-transform-and-orchestrate--notes--03-dbt-tests-snapshots-incremental.md
---

# dbt Incremental Models: Watermarks, Lookback and Strategies

An incremental model processes only new rows and adds them to the existing table. The cost is two code paths, first build and every later build, and bugs where they disagree. The incremental branch is active only when the target exists, the model is incremental, and no full refresh is requested. Start from `table`; go incremental when the rebuild is a measured problem, and add a reconciliation test the same day.

## Failure modes
- **No key, overlapping filter.** A watermark with `>=` and no `unique_key` appends: with nothing new the table still grew from 1,000 to 1,001 rows (1,000 distinct). A `unique_key` replaces rows with the same key.
- **Bare `>` ties.** A row whose timestamp equals the current maximum is never picked up. Use `>=` with a key, or a lookback with a key.
- **Late rows.** A late row arriving below the watermark is lost for good while a fresh row goes up it; the fact is short of its source and every table test passes. A reconciliation test catches it ([[dbt Singular, Generic and Unit Tests with Reconciliation]]).
- **Lookback.** Reprocess the last few days every run and let the key absorb overlap. It is a bet on lateness: with a 3-day window a row 2 days behind the newest was present, one 4 days behind was not. Measure real lateness, size the window from it, keep a full refresh available and run one periodically; refresh repairs everything because raw was kept. Lookback without a key duplicates every row in the window on every run.
- **Schema change.** `on_schema_change` is ignore (default), fail, append_new_columns or sync_all_columns. Ignore silently drops a new column; append adds it but backfills no existing rows. For a production fact, fail is often kindest because it makes the change somebody's decision.

## Strategies
| Strategy | What it does | Watch out for |
|---|---|---|
| append | inserts, no matching | any overlap duplicates |
| merge | matches on key, updates or inserts | scans the target unless predicates limit it |
| delete+insert | deletes matching keys, inserts | two statements unless in a transaction |
| insert_overwrite | replaces whole partitions | a partial batch deletes the rest of the partition |
| microbatch | one bounded query per time period | needs `event_time` set on upstream too |

Availability differs by adapter.

## Microbatch
Since dbt 1.9, declare `event_time` and `batch_size`; dbt filters each upstream that has an event time to one period and replaces that period in the target. Each batch is independent, so a failed one reruns alone and reprocessing a range is a start and end flag. Restating one day moved it from 5,179 to 25,879 and left its neighbours untouched. An upstream without `event_time` is scanned in full on every batch, so a dimension costs a full read per day. It is the same replace-one-period idea as [[Idempotent Batch Loads and Partition Overwrite]].

## Choosing
Full rebuild fast enough: table. Immutable rows: append with an exact filter. Rows change or arrive late with a reliable event time: microbatch or insert_overwrite. No reliable event time: merge or delete+insert with key and lookback.

## See Also
- [[Idempotent Batch Loads and Partition Overwrite]] — extends
- [[dbt Snapshots: History as Samples]] — related
- [[dbt Layers, Materialisations and the ref Graph]] — prerequisite-for
