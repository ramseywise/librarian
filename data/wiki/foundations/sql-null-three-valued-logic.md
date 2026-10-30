---
title: SQL NULL and Three-Valued Logic
tags: [foundations, concept]
summary: "NULL means unknown, so any comparison with it is unknown and WHERE drops it — which silently breaks `!=` filters, `= NULL`, and `NOT IN` over a nullable subquery; plus the related expression traps: half-open date ranges, integer division, and dialect-specific string/date functions."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/programming--sql--notes--02-nulls-and-expressions.md
  - data/raw/repos/learn-ai-engineering/programming--sql--README.md
---

# SQL NULL and Three-Valued Logic

> `NULL` means "unknown", not "zero" or "empty". Any comparison with an unknown is itself unknown.

## Three-valued logic

`NULL` propagates: arithmetic or comparison involving `NULL` yields `NULL`. `WHERE` keeps only rows where the condition is **true** — unknown counts as not true.

| Expression | Result |
|---|---|
| `NULL = NULL` | `NULL` (not true) |
| `NULL <> 1` | `NULL` |
| `1 + NULL` | `NULL` |
| `NULL AND false` | `false` |
| `NULL OR true` | `true` |

```sql
SELECT * FROM Visited WHERE dated = NULL;      -- always empty: wrong
SELECT * FROM Visited WHERE dated IS NULL;     -- correct
```

## The traps

**Negated filters drop NULLs.** "Everything not measured by Lake" is not `WHERE person != 'lake'` — rows where `person` is `NULL` drop out too. Say what you mean:

```sql
SELECT * FROM Survey WHERE person != 'lake' OR person IS NULL;
```

**`NOT IN` with a NULL returns nothing.** If the subquery returns even one `NULL`, `x NOT IN (…)` is never true and the query returns zero rows. Use `NOT EXISTS` for anti-joins (see [[SQL Subqueries and CTEs]]).

## Replacing NULL

- `COALESCE(a, b, …)` returns the first non-`NULL` argument — standard SQL, works everywhere. `IFNULL` (SQLite/MySQL) and `ISNULL` (SQL Server) are two-argument dialect versions.
- `NULLIF(x, sentinel)` turns a sentinel value (e.g. `0` meaning "none") into `NULL`.
- `COALESCE` only protects a field if the incoming side can actually be `NULL` — see [[Coalesce Against a Never-Null Source]].

## Aggregates ignore NULL

`COUNT(*)` counts rows; `COUNT(col)` counts non-`NULL` values; `AVG(col)` divides by the non-`NULL` count. Usually right, but be deliberate: if a missing reading really means zero, write `AVG(COALESCE(reading, 0))`. `sum` over zero rows is `NULL`, not 0. The same mechanic is why `count(b.id)` (not `count(*)`) is needed after a `LEFT JOIN` ([[SQL Join Patterns]]).

## Dates: half-open ranges

Engines store dates differently, but the ideas carry across:

| Task | SQLite | Postgres / DuckDB |
|---|---|---|
| Truncate to month | `strftime('%Y-%m', ts)` | `date_trunc('month', ts)` |
| Extract a part | `CAST(strftime('%H', ts) AS INTEGER)` | `extract(hour FROM ts)` |
| Add an interval | `datetime(ts, '+30 minutes')` | `ts + interval '30 minutes'` |
| Difference in days | `julianday(b) - julianday(a)` | `b::date - a::date` |
| Now | `datetime('now')` | `now()` |

```sql
-- September 2012: exact and index-friendly
WHERE starttime >= '2012-09-01' AND starttime < '2012-10-01'
```

**Prefer half-open ranges to `BETWEEN` for timestamps.** `BETWEEN '2012-09-01' AND '2012-09-30'` silently drops everything after midnight on the 30th. Wrapping the column in a function (`WHERE strftime('%Y-%m', starttime) = '2012-09'`) is correct but stops the database using an index — see [[SQL Indexes and Query Plans]] on sargable predicates.

## Strings

- `upper`, `length`, `substr`, `replace`, `trim`, `||` for concatenation.
- SQLite `LIKE` is case-insensitive for ASCII; **Postgres `LIKE` is case-sensitive** and uses `ILIKE` for case-insensitive matching.
- Postgres and DuckDB support regular expressions (`~`, `regexp_matches`); plain SQLite does not.

## Types and integer division

```sql
SELECT 7 / 2, 7 / 2.0, CAST(7 AS REAL) / 2;    -- 3, 3.5, 3.5
```

Integer division catches people in every dialect. Make one side decimal (`* 1.0`, `100.0 *`, `CAST`) before computing a ratio.

## See Also
- [[SQL Query Fundamentals]] — prerequisite-for (filters and aggregates the NULL rules act on)
- [[SQL Subqueries and CTEs]] — extends (NOT EXISTS as the NULL-safe anti-join)
- [[SQL Join Patterns]] — extends (outer joins manufacture NULLs)
- [[SQL Indexes and Query Plans]] — related (why half-open ranges stay sargable)
- [[Coalesce Against a Never-Null Source]] — related (a COALESCE merge that never fires)
- [[Programming Curriculum]] — related (course map)
