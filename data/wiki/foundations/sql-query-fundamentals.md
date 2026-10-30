---
title: SQL Query Fundamentals
tags: [foundations, reference]
summary: "Core SELECT/WHERE/ORDER BY/CASE/LIMIT and GROUP BY/HAVING mechanics, organised around the logical evaluation order (FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT) that explains most alias and filtering errors, plus the rules of thumb that prevent silent wrong answers."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/programming--sql--README.md
  - data/raw/repos/learn-ai-engineering/programming--sql--notes--01-select-and-filter.md
  - data/raw/repos/learn-ai-engineering/programming--sql--notes--03-aggregation.md
  - data/raw/repos/learn-ai-engineering/programming--sql--notes--10-capstone-murder-mystery.md
---

# SQL Query Fundamentals

> A query describes the rows you want; the database decides how to fetch them.

## Rules of thumb

- Write the query in **evaluation order** (`FROM` → `WHERE` → `GROUP BY` → `HAVING` → `SELECT` → `ORDER BY`), not reading order.
- `NULL` is "unknown", not a value: `= NULL` is never true, and `NOT IN` with a `NULL` in the list returns nothing (see [[SQL NULL and Three-Valued Logic]]).
- Date ranges are half-open: `>= start AND < next_start`.
- A filter on the right table of a `LEFT JOIN` belongs in `ON`, not `WHERE` (see [[SQL Join Patterns]]).
- Top-N per group is `row_number() OVER (PARTITION BY … ORDER BY …, unique_col)` in a CTE, filtered outside (see [[SQL Window Functions]]).
- Run `SELECT count(*)` with the same `WHERE` before any `UPDATE` or `DELETE` (see [[SQL Schema Design and DDL]]).
- Values reach SQL as parameters, never through f-strings (see [[SQL from Python]]).

## Logical order of evaluation

You write a query in one order; the database evaluates it in another. Most "why can't I use that alias here" errors come from this.

| Written | Evaluated |
|---|---|
| `SELECT` | 1. `FROM` / `JOIN` |
| `FROM` | 2. `WHERE` |
| `WHERE` | 3. `GROUP BY` |
| `GROUP BY` | 4. `HAVING` |
| `HAVING` | 5. `SELECT` (aliases and window functions created here) |
| `ORDER BY` | 6. `DISTINCT` |
| `LIMIT` | 7. `ORDER BY` (can use aliases) → 8. `LIMIT` |

Consequences: `WHERE` cannot see `SELECT` aliases or aggregates; `ORDER BY` can use aliases; window functions cannot be filtered in the same query.

## Selecting, sorting, filtering

- **Rows have no order.** Without `ORDER BY`, the order you see is an accident of storage and can change between runs.
- `SELECT *` is fine at the prompt; in code, name the columns so adding a table column doesn't break consumers.
- `DISTINCT` applies to the whole selected tuple: `SELECT DISTINCT taken, quant` is distinct over the *pair*.
- `ORDER BY` may name a column not in the `SELECT` list, an alias, or an expression.
- **`AND` binds tighter than `OR` — always parenthesise mixed `AND`/`OR`.** `quant = 'sal' AND person = 'lake' OR person = 'roe'` returns every `roe` reading, salinity or not.
- `IN (...)` is shorthand for chained `OR`; `LIKE` uses `%` (any run) and `_` (one char); `BETWEEN` is inclusive at both ends.
- ISO-8601 date text (`YYYY-MM-DD`) compares correctly as strings — why SQLite gets away with `TEXT` dates.
- Identifiers are case-insensitive in SQLite and folded to lowercase in Postgres unless quoted.

## CASE

`CASE WHEN … THEN … ELSE … END` is SQL's `if` and can appear anywhere an expression can — `SELECT`, `WHERE`, `ORDER BY`, or inside an aggregate (which is how pivots work, below).

## Limiting and paging

```sql
SELECT * FROM bookings ORDER BY starttime DESC LIMIT 10 OFFSET 20;   -- page 3
```

- `LIMIT` without `ORDER BY` returns *some* ten rows, not the first ten.
- Large `OFFSET`s get slow: the database still reads and discards the skipped rows. Production APIs **page by key** instead: `WHERE starttime < :last_seen ORDER BY starttime DESC LIMIT 10`.
- An `ORDER BY … LIMIT n` cap is only safe while the filter that precedes it stays in SQL — see [[Dropped Filter Flips the Truncation Direction]].

## Aggregation

`GROUP BY` collapses many rows into one per group. Every output column must be in the group key or summarised by an aggregate.

| Function | Notes |
|---|---|
| `count(*)` | Counts rows, `NULL`s included |
| `count(col)` / `count(DISTINCT col)` | Non-`NULL` values / distinct non-`NULL` values |
| `sum`, `avg`, `min`, `max` | Ignore `NULL`. `sum` of zero rows is `NULL`, not 0 — wrap in `COALESCE(…, 0)` |
| `group_concat` (SQLite) / `string_agg` (Postgres, DuckDB) | Joins a group's values into one string |

- **The bare-column rule.** `SELECT person, reading FROM Survey GROUP BY person` is an error in Postgres and DuckDB; SQLite accepts it and returns an arbitrary `reading` per group — a silent bug.
- **`WHERE` filters rows, `HAVING` filters groups.** `WHERE` runs before grouping and can't see aggregates. Push every filter you can into `WHERE` so fewer rows reach grouping.

### Conditional aggregation (portable pivot)

```sql
SELECT facid,
       sum(CASE WHEN strftime('%m', starttime) = '07' THEN slots ELSE 0 END) AS jul,
       sum(CASE WHEN strftime('%m', starttime) = '08' THEN slots ELSE 0 END) AS aug
FROM bookings
WHERE starttime >= '2012-07-01' AND starttime < '2012-09-01'
GROUP BY facid;
```

Postgres and DuckDB also offer `count(*) FILTER (WHERE …)`; DuckDB has a `PIVOT` statement.

### Rollups

`GROUP BY ROLLUP (facid, month)` (Postgres, DuckDB) adds subtotals and a grand total. SQLite lacks `ROLLUP`: emulate with `UNION ALL` of the detailed query and a coarser-grouped one.

## Capstone: SQL as an investigation workflow

The course capstone (Knight Lab's *SQL Murder Mystery*) frames querying as open-ended investigation. Start only from what you know (a crime type, a date, a city) and follow leads:

1. Inspect the schema first (`.tables`; `SELECT sql FROM sqlite_master WHERE name = …`).
2. Find the anchor record by filtering on several columns.
3. Locate witnesses with `LIKE` and `ORDER BY … DESC LIMIT 1`.
4. Cross-reference independent sources (check-ins, licence plates, event attendance) with multi-table joins.
5. Narrow suspects with subqueries and `GROUP BY … HAVING count(*) = 3` — "matched every criterion".
6. Check the answer, then keep going: the first answer is not the whole story.

The skill being exercised is chaining small verifiable queries, each narrowing the candidate set, rather than writing one big query.

## See Also
- [[SQL NULL and Three-Valued Logic]] — extends (NULL semantics behind filters and aggregates)
- [[SQL Join Patterns]] — extends
- [[SQL Subqueries and CTEs]] — extends
- [[SQL Window Functions]] — extends
- [[SQL Indexes and Query Plans]] — extends (why half-open ranges and keyset paging are fast)
- [[Programming Interview Study Guide]] — related (interview-shaped SQL idioms)
- [[Data Engineering Foundations]] — related (SQL is assumed by the transform stage)
- [[Programming Curriculum]] — related (course map)
