---
title: SQL Subqueries and CTEs
tags: [foundations, concept]
summary: "A query is a table, so it can go anywhere SQL expects a table or value: scalar, correlated and derived-table subqueries, EXISTS vs IN (and why NOT IN breaks on NULL), CTEs for readable multi-step queries, and recursive CTEs for hierarchies and gap-free date series."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/programming--sql--notes--05-subqueries-and-ctes.md
---

# SQL Subqueries and CTEs

> A query is a table. Anywhere SQL expects a table or a value, you can put another query. CTEs give those inner queries names.

## Scalar subqueries

One row, one column — usable anywhere a value is:

```sql
SELECT bookid, slots FROM bookings
WHERE slots > (SELECT avg(slots) FROM bookings);
```

## Correlated subqueries

A correlated subquery refers to the outer row, so in principle it runs once per outer row:

```sql
SELECT m.surname,
       (SELECT min(b.starttime) FROM bookings b WHERE b.memid = m.memid) AS first_booking
FROM members m;
```

Planners often rewrite these as joins. When they can't, a correlated subquery over a large table is slow; a join to a pre-aggregated subquery, or a window function ([[SQL Window Functions]]), usually does better.

## Derived tables (subqueries in FROM)

```sql
SELECT facid, total
FROM (SELECT facid, sum(slots) AS total FROM bookings GROUP BY facid) t
WHERE total > 1000;
```

An alternative to `HAVING`, and the way to filter on anything computed in an inner `SELECT`.

## EXISTS vs IN

```sql
SELECT m.surname FROM members m
WHERE EXISTS (
  SELECT 1 FROM bookings b JOIN facilities f ON f.facid = b.facid
  WHERE b.memid = m.memid AND f.name LIKE 'Tennis%'
);
```

- `EXISTS` stops at the first match and ignores the selected columns (`SELECT 1` is convention).
- `IN (subquery)` is fine for positive matches.
- **`NOT IN (subquery)` is broken if the subquery can return `NULL`** — it returns no rows at all ([[SQL NULL and Three-Valued Logic]]). Use `NOT EXISTS` for anti-joins (or the `LEFT JOIN … IS NULL` form in [[SQL Join Patterns]]).

## Common table expressions

`WITH` names a subquery and puts it before the main query, so a multi-step query reads top to bottom:

```sql
WITH member_slots AS (
  SELECT memid, sum(slots) AS slots FROM bookings GROUP BY memid
),
ranked AS (
  SELECT memid, slots, slots * 1.0 / (SELECT sum(slots) FROM member_slots) AS share
  FROM member_slots
)
SELECT m.surname, r.slots, round(r.share * 100, 1) AS pct
FROM ranked r JOIN members m USING (memid)
ORDER BY r.slots DESC LIMIT 5;
```

Why: each step can be tested alone (`SELECT * FROM member_slots`), intermediate results get names, and one CTE can be reused several times. **Postgres 12+, DuckDB and SQLite inline CTEs** into the main query unless you ask for `MATERIALIZED`, so in general they cost nothing. CTEs are also the standard wrapper for filtering on a window function's output.

## Recursive CTEs

Anchor query, `UNION ALL`, then a step referring to the CTE itself; repeats until the step returns no rows. Use for hierarchies, graphs and number/date series.

```sql
-- The chain of recommenders above member 27
WITH RECURSIVE chain(memid, recommendedby, depth) AS (
  SELECT memid, recommendedby, 0 FROM members WHERE memid = 27
  UNION ALL
  SELECT m.memid, m.recommendedby, c.depth + 1
  FROM members m JOIN chain c ON m.memid = c.recommendedby
)
SELECT c.depth, m.surname FROM chain c JOIN members m USING (memid)
WHERE c.depth > 0 ORDER BY c.depth;
```

### Date series: make empty days visible

```sql
WITH RECURSIVE days(d) AS (
  SELECT '2012-09-01'
  UNION ALL
  SELECT date(d, '+1 day') FROM days WHERE d < '2012-09-30'
)
SELECT d, count(b.bookid) AS bookings
FROM days LEFT JOIN bookings b ON date(b.starttime) = d
GROUP BY d;
```

Grouping the facts alone omits days with no rows; generating the series and `LEFT JOIN`ing onto it reports them as zero. This is also the prerequisite for a correct `ROWS BETWEEN 6 PRECEDING` moving average.

**Always give recursion a stopping condition.** A cycle in the data (A recommends B, B recommends A) loops forever without a depth limit or a visited-path check.

## See Also
- [[SQL Query Fundamentals]] — prerequisite-for
- [[SQL NULL and Three-Valued Logic]] — prerequisite-for (why NOT IN fails)
- [[SQL Join Patterns]] — alternative-to (joins vs EXISTS for semi/anti-joins)
- [[SQL Window Functions]] — extends (CTE wraps the window, filter outside)
- [[Programming Curriculum]] — related (course map)
