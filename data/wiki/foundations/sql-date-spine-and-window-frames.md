---
title: SQL Date Spine and Window Frames
tags: [foundations, pattern]
summary: "Grouping drops periods with no rows, which inflates averages and lies on charts; start from a table of every period and left join. Also: explicit window frames, lag-by-rows pitfalls, QUALIFY for top-N and a one-scan funnel with FILTER."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--06-sql-for-analytics.md
---

# SQL Date Spine and Window Frames

## Date spine

Group rare events by week and weeks with none disappear: a chart draws a line across the gap and an average comes out too high. Generate every period (a spine), left join the data, coalesce NULL to 0. Eight weeks of a rare event averaged 1.83 per week without the spine versus the true 1.38. Rule: count output rows against the number of periods meant to be reported.

## Window frames

- Year-to-date: sum over a window partitioned by year, ordered by month (restarts each January).
- Three-month average: ROWS BETWEEN 2 PRECEDING AND CURRENT ROW. With ORDER BY, the default frame is a RANGE that treats ties as peers; write ROWS when rows are meant.
- Year-on-year via lag(revenue, 12) counts rows, not months, so it is correct only with no missing months; on a sparse table build a spine first.

## Top N per group

A window result cannot go in WHERE (WHERE runs before windows). QUALIFY (DuckDB; absent in PostgreSQL, which needs a subquery) filters after windows. rank gives ties the same place and leaves a gap, dense_rank leaves none, row_number picks a winner arbitrarily unless the ORDER BY has a tie-breaker.

## Funnel in one scan

Each funnel step as a conditional count with FILTER in one pass (or sum(CASE WHEN ...) where FILTER is missing); it reproduced the pandas funnel exactly (checkout-to-payment 84.0 and 67.6, conversion 11.65 and 5.37) and is cheaper than a subquery per step. See [[Funnel Step Diagnosis]].

## See Also
- [[SQL Window Functions]] — prerequisite-for
- [[SQL Sessionisation and Gaps-and-Islands]] — related
- [[Funnel Step Diagnosis]] — related
