---
title: SQL Window Functions
tags: [foundations, pattern]
summary: "A window function computes over a group but keeps every row — the tool for top-N per group, dedup-latest, running totals, moving averages, lag/lead comparisons and share-of-total; it runs after GROUP BY so it must be filtered from an outer CTE, and its default RANGE frame silently groups ties."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/programming--sql--notes--06-window-functions.md
  - data/raw/repos/learn-ai-engineering/programming--sql--README.md
---

# SQL Window Functions

> An aggregate collapses a group into one row. A window function computes over a group but keeps every row.

## Anatomy

```sql
func(args) OVER (
  PARTITION BY …     -- restart per group (optional)
  ORDER BY …         -- order within partition (needed for ranking, running totals, lag/lead)
  ROWS BETWEEN …     -- the frame: which neighbouring rows to include (optional)
)
```

```sql
SELECT bookid, memid, slots, sum(slots) OVER (PARTITION BY memid) AS member_total
FROM bookings;
```

**Evaluation order:** windows run *after* `WHERE`, `GROUP BY` and `HAVING` (see [[SQL Query Fundamentals]]), so you cannot filter on them in the same query. Wrap the query in a CTE and filter outside ([[SQL Subqueries and CTEs]]).

## Ranking

| Function | Ties | Scores 10, 10, 8 |
|---|---|---|
| `row_number()` | Arbitrary tie-break, always unique | 1, 2, 3 |
| `rank()` | Ties share, then gaps | 1, 1, 3 |
| `dense_rank()` | Ties share, no gaps | 1, 1, 2 |
| `ntile(n)` | *n* roughly equal buckets | — |

## Pattern: top-N per group

The most common window question in interviews:

```sql
WITH ranked AS (
  SELECT memid, bookid, slots,
         row_number() OVER (PARTITION BY memid ORDER BY slots DESC, bookid) AS rn
  FROM bookings
)
SELECT * FROM ranked WHERE rn <= 3;
```

Add a **unique column (`bookid`) to the `ORDER BY`** so the result is deterministic — otherwise `row_number()` breaks ties arbitrarily and reruns can differ.

## Pattern: running totals and moving averages

```sql
SELECT date(starttime) AS day, sum(slots) AS slots,
       sum(sum(slots)) OVER (ORDER BY date(starttime)) AS running_total,
       avg(sum(slots)) OVER (ORDER BY date(starttime)
                             ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS moving_avg_7d
FROM bookings
GROUP BY date(starttime);
```

- `sum(sum(slots)) OVER …` aggregates per day first, then windows over the daily totals — legal because windows run after `GROUP BY`.
- **The default frame trap.** With `ORDER BY` and no frame clause, the frame is `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`, so *peers* (equal sort keys) are included together. Correct for running totals over unique days; with duplicate sort keys, say `ROWS` explicitly.
- `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` is "this row and six before it" — seven *days* only if every day has a row. Fill gaps first with a date series ([[SQL Subqueries and CTEs]]).

## Pattern: lag / lead

```sql
-- Days between a member's consecutive bookings
SELECT memid, starttime,
       julianday(starttime)
         - julianday(lag(starttime) OVER (PARTITION BY memid ORDER BY starttime))
         AS days_since_previous
FROM bookings;
```

`lag(x, n, default)` looks *n* rows back, `lead` forward — replacing a self-join to the "previous row". `first_value` / `last_value` read the frame edges; for `last_value`, set the frame to `UNBOUNDED FOLLOWING` (the default frame ends at the current row).

## Pattern: share of total

```sql
SELECT facid, sum(slots) AS slots,
       round(100.0 * sum(slots) / sum(sum(slots)) OVER (), 1) AS pct_of_all
FROM bookings GROUP BY facid;
```

`OVER ()` is a window over the whole result. Note `100.0` to avoid integer division ([[SQL NULL and Three-Valued Logic]]).

## Analytics recipes

| Pattern | Recipe |
|---|---|
| Deduplicate (keep latest per key) | `row_number() OVER (PARTITION BY key ORDER BY updated_at DESC) = 1` |
| Sessionise | `lag` to find gaps over a threshold → running `sum` of "new session" flags = session ID |
| Gaps and islands | Consecutive runs share the same `date - row_number()` value; group by it |
| Retention cohorts | `min(date) OVER (PARTITION BY user)` = cohort; group by cohort × period |

## See Also
- [[SQL Query Fundamentals]] — prerequisite-for (evaluation order explains the CTE wrapper)
- [[SQL Subqueries and CTEs]] — prerequisite-for (CTE wrapper and date series)
- [[SQL Join Patterns]] — alternative-to (lag/lead vs self-join)
- [[Programming Interview Study Guide]] — related (ranking functions and dedup-latest as interview staples)
- [[Programming Curriculum]] — related (course map)
