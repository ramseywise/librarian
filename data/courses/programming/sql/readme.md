---
imported_hash: e1f888843b0b4b63
title: SQL
summary: Build these as schema drills (window-functions/, ctes/, analytics/) per ../README.md, each with a small seed schema so the answer can be run in SQLite or DuckDB.
order: 1
kind: reading
source: sisyphus/drills/sql/README.md
---

# SQL

| Folder | What | Count |
|---|---|---|
| [`hackerrank/Basic Select/`](hackerrank/Basic%20Select/) | `SELECT`, `WHERE`, `ORDER BY`, string functions | 20 |
| [`hackerrank/Advanced Select/`](hackerrank/Advanced%20Select/) | `CASE`, pivots, hierarchy queries | 5 |
| [`hackerrank/Aggregation/`](hackerrank/Aggregation/) | `COUNT`/`SUM`/`AVG`, rounding, median | 17 |
| [`hackerrank/Basic Join/`](hackerrank/Basic%20Join/) | Inner/outer joins, join + group by | 8 |
| [`hackerrank/Advanced Join/`](hackerrank/Advanced%20Join/) | Self-joins, date gaps | 2 |
| [`window-functions/`](window-functions/) | Schema drills: [top orders per user + running total](window-functions/top-orders-per-user.md) | 1 |

## Gaps — what interviews ask that isn't here

- **Window functions**: started (ranking, running totals). Still to add: `LAG`/`LEAD` gaps, moving averages, `NTILE`.
- **CTEs and recursion**: multi-step queries, `WITH RECURSIVE` hierarchies.
- **Analytics patterns**: retention/cohorts, funnels, sessionization, deduplication.
- **Query performance**: reading `EXPLAIN`, index choice. Overlaps `../mcq/`.

Build these as schema drills (`window-functions/`, `ctes/`, `analytics/`) per
[`../README.md`](../00-start-here/readme.md), each with a small seed schema so the answer can be run in
SQLite or DuckDB.
