---
title: SQL Join Patterns
tags: [foundations, pattern]
summary: "Choosing inner, left, self, anti and cross joins by what should happen to unmatched rows — and the two silent-wrong-answer traps: a WHERE filter on a LEFT JOIN's right table turning it back into an inner join, and fan-out when the join key isn't unique."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/programming--sql--notes--04-joins.md
  - data/raw/repos/learn-ai-engineering/programming--sql--README.md
---

# SQL Join Patterns

> A join pairs rows from two tables that satisfy a condition. The kind of join decides what happens to rows that don't find a partner.

## Inner join

```sql
SELECT s.name, v.dated, sv.quant, sv.reading
FROM Site s
JOIN Visited v  ON s.name = v.site
JOIN Survey  sv ON v.id   = sv.taken;
```

Conceptually: build every pair of rows (the cross product), keep pairs where `ON` is true. Unmatched rows on either side disappear.

## Fan-out: watch the row count

If the join key isn't unique on one side, rows multiply. Joining 4,044 `bookings` to `members` on `memid` returns 4,044 rows only because `memid` is unique in `members`; a table with several rows per `memid` would return more. **Duplicated rows after a join usually mean the key isn't the one you assumed.** Predict the output row count before running the join, and aggregate *after* checking it — a `sum` over a fanned-out join double-counts.

## Outer joins

| Join | Keeps |
|---|---|
| `LEFT JOIN` | Every left row; right-hand columns `NULL` where no match |
| `RIGHT JOIN` | The mirror image — rewrite as `LEFT JOIN` for readability |
| `FULL OUTER JOIN` | Unmatched rows from both sides (SQLite 3.39+, Postgres, DuckDB) |

## Self-join

One table, two aliases, with a foreign key pointing back into the same table:

```sql
-- Every member, plus who recommended them (if anyone)
SELECT m.firstname, m.surname, r.firstname AS rec_first, r.surname AS rec_last
FROM members m
LEFT JOIN members r ON r.memid = m.recommendedby;
```

For an unbounded chain (recommender of the recommender…), use a recursive CTE ([[SQL Subqueries and CTEs]]).

## The LEFT JOIN + WHERE trap

A filter on the right-hand table in `WHERE` discards the `NULL` rows the `LEFT JOIN` just kept — it silently becomes an inner join. Conditions on the right table go in `ON`:

```sql
-- Every facility, with its September bookings (0 if none)
SELECT f.name, count(b.bookid) AS n
FROM facilities f
LEFT JOIN bookings b
  ON b.facid = f.facid
 AND b.starttime >= '2012-09-01' AND b.starttime < '2012-10-01'
GROUP BY f.name;
```

Note **`count(b.bookid)`, not `count(*)`**: a facility with no bookings still has one row (of `NULL`s), so `count(*)` would report 1. See [[SQL NULL and Three-Valued Logic]].

## Anti-join: rows with no match

```sql
-- Members who have never booked
SELECT m.memid, m.surname
FROM members m
LEFT JOIN bookings b ON b.memid = m.memid
WHERE b.memid IS NULL;
```

Here the `WHERE … IS NULL` on the right table is intentional — it keeps exactly the unmatched rows. `NOT EXISTS` does the same job; modern planners usually run them identically, so pick whichever reads better. Avoid `NOT IN (subquery)` — it returns nothing if the subquery yields a `NULL`.

## Cross join: generate the grid

`CROSS JOIN` returns every pair. Useful for generating combinations (every facility × every month) that you then `LEFT JOIN` facts onto, so empty cells show up as zeros rather than missing rows. A recursive date series serves the same role for time ([[SQL Subqueries and CTEs]]).

## Set operations

```sql
SELECT surname FROM members
UNION              -- deduplicates; UNION ALL keeps duplicates and is faster
SELECT name FROM facilities;
```

`INTERSECT` and `EXCEPT` work the same way. Both sides need the same number of columns with compatible types.

## Choosing

| Question | Join |
|---|---|
| Only rows that match on both sides | `JOIN` |
| All of A, with B's data where it exists | `LEFT JOIN`, B-filters in `ON` |
| A's rows with no B | anti-join (`LEFT JOIN … IS NULL` or `NOT EXISTS`) |
| A row relating to another row of the same table | self-join |
| Every combination, to fill gaps | `CROSS JOIN` then `LEFT JOIN` |

## See Also
- [[SQL Query Fundamentals]] — prerequisite-for
- [[SQL NULL and Three-Valued Logic]] — prerequisite-for (outer joins produce NULLs; NOT IN breaks on them)
- [[SQL Subqueries and CTEs]] — alternative-to (EXISTS / NOT EXISTS as semi- and anti-joins)
- [[SQL Window Functions]] — alternative-to (lag/lead replace many self-joins)
- [[Programming Interview Study Guide]] — related (predict-the-row-count idiom)
- [[Programming Curriculum]] — related (course map)
