---
title: "Idempotent Window-Replace Loads"
tags: [foundations, pattern]
summary: "A retried append doubles the day's rows with no error; make the unit of work a window and replace it inside one transaction (or merge on a key) so a re-run changes nothing."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--02-ingest-and-modelling--notes--01-ingest.md
---

# Idempotent Window-Replace Loads

Schedulers retry, operators re-run. A load that gives a different answer on the second run turns every timeout into a data bug. An operation is **idempotent** when performing it once or many times has the same effect. Setting a value is idempotent; incrementing a counter is not, and an append is a kind of increment.

## The failure

Setup: a small operational table, three days of 1,000 trips each (3,000 rows), loaded into a warehouse table by day.

- An `append` load for one day times out at the client after it already committed, and the scheduler retries.
- Result: 2,000 rows holding 1,000 distinct trips. Every downstream sum is twice the truth, and nothing failed, so nothing alerts.

## The fix: replace the window, in a transaction

```python
def load_window(day):
    rows = source.execute("SELECT * FROM trips WHERE pickup_date = ?", (day,)).fetchall()
    wh.execute("BEGIN")
    wh.execute("DELETE FROM raw_trips WHERE pickup_date = ?", (day,))
    wh.executemany("INSERT INTO raw_trips VALUES (?,?,?,?,?)", rows)
    wh.execute("COMMIT")
```

Run twice, the table holds 1,000 rows and 1,000 distinct trips. The transaction matters as much as the delete: without it, a crash between the two statements leaves the day empty (count 0). That is worse than duplicates, because the totals look merely low, like a slow day. With the transaction and a rollback in the handler, the count stays at 1,000.

## What a chunked loader leaves to you

A simple batch loader streams a file in 100,000-row chunks (bounded memory), creates the table from the first chunk's schema, and appends the rest. Production adds:

| Property | Naive loader | Production |
|---|---|---|
| Idempotency | `replace` on every run: a full reload | Partition-scoped overwrite, or merge on a key, so a rerun of one day replaces only that day |
| Schema | Inferred from data | Explicit, so one bad file cannot redefine a column |
| Types | Only some columns cast | Cast every column at the boundary or in staging |
| Partial failure | A crash mid-loop leaves a half-loaded table | Load to a temp table, swap on success |

Packaging the loader as a container makes the ingest job a unit an orchestrator can schedule instead of a script on a laptop.

## Pitfalls

- Appending in a retried task is the most common way to double a metric.
- Delete-then-insert outside a transaction leaves a hole.
- Transforming on the way in. Keep the raw layer as received so everything can be re-derived when a transform turns out wrong.

Window replace only works when the source gives whole windows that nobody touches again. For rows that change in place, see [[High-Watermark Incremental Extraction and Its Blind Spots]].

## See Also
- [[High-Watermark Incremental Extraction and Its Blind Spots]] — extends (what to do when rows change in place)
- [[Change Data Capture and the Dual-Write Problem]] — related
- [[SQL Schema Design and DDL]] — related (ON CONFLICT upserts and atomic transactions)
- [[Rerunnable Cleaning Loader with Assertions]] — related
- [[Data Engineering Foundations]] — related
