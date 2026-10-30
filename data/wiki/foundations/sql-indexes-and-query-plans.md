---
title: SQL Indexes and Query Plans
tags: [foundations, concept]
summary: "A B-tree index turns a full scan into a log-n lookup but every write pays for it; read EXPLAIN QUERY PLAN for SCAN vs SEARCH, order composite indexes equality-first/range-last, keep predicates sargable (no function on the indexed column), and know when indexes don't help — including columnar engines that use zone maps instead."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/programming--sql--notes--08-indexes-and-query-plans.md
---

# SQL Indexes and Query Plans

> An index is a sorted copy of some columns that points back to the rows. It turns "read everything" into "jump to the right place", and every write pays to keep it up to date.

Background reading: Markus Winand, *Use The Index, Luke*.

## What an index is

Most databases use a **B-tree**: a balanced, sorted tree of keys. A lookup costs O(log n) instead of a full scan's O(n); a range (`BETWEEN`, `>=`/`<`, `LIKE 'abc%'`) is a lookup followed by a walk along the leaves.

```sql
CREATE INDEX bookings_memid_starttime ON bookings (memid, starttime);
```

## Reading a plan

```sql
EXPLAIN QUERY PLAN
SELECT * FROM bookings WHERE memid = 5 AND starttime >= '2012-09-01';
-- SEARCH bookings USING INDEX ... (memid=? AND starttime>?)
```

| SQLite says | Meaning |
|---|---|
| `SCAN table` | Full table scan — every row read |
| `SEARCH table USING INDEX idx (col=?)` | Index lookup |
| `USING COVERING INDEX` | Index holds every needed column; the table is never read |
| `USE TEMP B-TREE FOR ORDER BY` | Extra sort step no index could provide |

Postgres and DuckDB use `EXPLAIN ANALYZE`, which *runs* the query and reports real row counts and timings per node. **Compare estimated vs actual rows**: a big gap means stale statistics (run `ANALYZE`) or a predicate the planner can't estimate.

## Composite indexes: column order matters

An index on `(memid, starttime)` is sorted by `memid`, then `starttime` within each `memid` — like a phone book by surname then first name.

| Query | Uses `(memid, starttime)`? |
|---|---|
| `WHERE memid = 5` | Yes — leftmost prefix |
| `WHERE memid = 5 AND starttime >= …` | Yes — equality then range |
| `WHERE starttime >= …` | Not efficiently — leading column missing |
| `WHERE memid > 5 AND starttime = …` | Only for `memid`; after a range column, later columns can't narrow the search |

**Rule of thumb: equality columns first, range or sort column last.**

## Sargable predicates

A predicate is *sargable* (Search ARGument ABLE) if the index can satisfy it. Wrapping the indexed column in a function or expression usually disables the index:

| Not sargable | Sargable rewrite |
|---|---|
| `WHERE date(starttime) = '2012-09-14'` | `WHERE starttime >= '2012-09-14' AND starttime < '2012-09-15'` |
| `WHERE slots * 2 > 6` | `WHERE slots > 3` |
| `WHERE lower(surname) = 'smith'` | Expression index `ON members (lower(surname))`, or store it normalised |
| `WHERE surname LIKE '%mith'` | No B-tree helps a leading wildcard — use full-text search or a trigram index |

This is why the half-open date range in [[SQL NULL and Three-Valued Logic]] is preferred over `strftime(...) = ...`, and why keyset paging (`WHERE ts < :last_seen ORDER BY ts DESC LIMIT n`) beats a large `OFFSET` ([[SQL Query Fundamentals]]).

## When indexes don't help

- **Low selectivity.** If the predicate matches a large share of the table, a scan beats thousands of random lookups; the planner rightly ignores the index.
- **Small tables.** A 9-row table always gets scanned.
- **Write cost.** Every `INSERT`, `UPDATE`, `DELETE` updates every index. Index for the queries you actually run, not every column.

## Columnar engines

DuckDB, BigQuery, Snowflake and ClickHouse store data by column and scan compressed column chunks, relying on **per-block min/max statistics (zone maps)** instead of B-trees. Performance there comes from reading fewer columns (avoid `SELECT *`), partitioning or clustering by the common filter column, and pre-aggregation — not from adding indexes.

## See Also
- [[SQL Query Fundamentals]] — prerequisite-for
- [[SQL Schema Design and DDL]] — prerequisite-for (indexes sit on top of the logical schema)
- [[SQL NULL and Three-Valued Logic]] — related (half-open ranges are the sargable form)
- [[Pure Derivation Is a Generated Column]] — related (a stored generated column as the home for a trigram/full-text index)
- [[Data Engineering Foundations]] — related (columnar warehouses and DuckDB)
- [[Programming Curriculum]] — related (course map)
