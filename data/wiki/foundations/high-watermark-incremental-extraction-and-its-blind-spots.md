---
title: "High-Watermark Incremental Extraction and Its Blind Spots"
tags: [foundations, pattern]
summary: "Reading rows newer than the last seen updated_at misses late-committed rows and every hard delete; an overlap window patches the first, nothing patches the second, and dlt's incremental cursor is the same mechanism."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--02-ingest-and-modelling--notes--01-ingest.md
---

# High-Watermark Incremental Extraction and Its Blind Spots

Once a table is too large to copy nightly, a loader keeps the largest `updated_at` it has seen (the **high watermark**), asks next time for anything larger, and merges on the key. It looks correct and fails silently in two ways.

## Where it breaks

Setup: 3,000 source rows, first extract sets the mark to 2026-01-03 23:00:00. Overnight, three things happen in the source.

| Source event | Extracted? | Why |
|---|---|---|
| Correction whose transaction began at 22:30, committed later | No (warehouse keeps the old fare, 53.67 instead of 99.0) | `updated_at` was stamped at transaction start, before the mark |
| Hard delete | No (row stays in the warehouse) | A query cannot return a row that no longer exists |
| Ordinary update after the mark | Yes (1 row extracted) | Only this one is visible |

Reading the mark from a lagging replica adds a third way to miss rows. `updated_at` is written by the application, often at transaction start, and bulk fixes or manual SQL may skip it.

## The overlap patch

Re-read a window behind the mark and let the merge dedupe. With a two-hour overlap the late correction is found, at the price of re-reading: 1,002 rows to find two (this synthetic source stamps a whole day's rows at one time). Limits:

- It only covers commits within its width, so it is a guess about the longest transaction. Write the assumption down and monitor it.
- It never finds deletes. Teams use soft-delete columns (only if every writer honours them) or a periodic key comparison against the source.
- Take the mark from the data actually received, not from `now()`, or rows committed between the read and the clock are lost.

## dlt's incremental cursor is a watermark

The `dlt` library keeps the high-water mark as state between runs (`dlt.sources.incremental`), merges on a `primary_key` (`write_disposition` is `append`, `replace` or `merge`), normalises nested JSON into child tables, and adds new columns instead of dropping them. Its `>=` boundary and merge dedupe rows at the boundary value. Against the same source, a second run picked up the changed fare and the count held at 2,999 (trip 43 had been deleted before the first run). A delete after the first run would stay. dlt gives state, schema evolution and merge in a few lines; it cannot see a change the query cannot see. A reasonable default for API sources, with a hand-rolled loader kept for understanding.

## Choosing a method

| Method | Sees updates | Sees hard deletes | Load on source | Operational cost |
|---|---|---|---|---|
| Full copy | Yes | Yes | High, per run | Low |
| Window replace | Only if window immutable | Within the window | Low | Low |
| Watermark + overlap | Within the overlap | No | Medium, needs an index | Low |
| Log-based CDC | Yes | Yes | Low on query path | High: connector, broker, snapshots |

Order of cost: copy the table if small; watermark with overlap if rows are never hard-deleted and a small error is tolerable; CDC when deletes matter, the table is too big to re-read, or consumers need minutes of freshness.

## See Also
- [[Idempotent Window-Replace Loads]] — prerequisite-for
- [[Change Data Capture and the Dual-Write Problem]] — alternative-to
- [[SQL Schema Design and DDL]] — related (upserts)
- [[Data Engineering Foundations]] — related
