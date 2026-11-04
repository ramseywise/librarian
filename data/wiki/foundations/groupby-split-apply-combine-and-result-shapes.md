---
title: Groupby Split-Apply-Combine and Result Shapes
tags: [foundations, concept]
summary: groupby splits a table, applies a function per group and recombines; agg, transform, filter and apply differ by the shape they return, and picking one starts from what a row of output should mean.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--01-python-for-data-analysis--notes--05-groupby-and-aggregation.md
---

# Groupby Split-Apply-Combine and Result Shapes

## The pattern

Break a problem into pieces, work on each piece independently, then reassemble. It appears at every stage of analysis: standardising values, marginal summaries, a model per panel. It is `GROUP BY` and the spreadsheet pivot table as one idea. A GroupBy object computes nothing until you aggregate; iterating over it yields (key, piece) pairs.

The limit: pieces must be independent. A running mean, where each step overlaps the last, needs rolling windows instead (see [[Time-Series Leakage: Shift and Rolling Windows]]).

## Keys

A key can be a column, a list of columns (giving a MultiIndex, see [[Pandas Index Design, MultiIndex and Reindex]]), or any array of the right length, so you can group by something computed on the spot (`orders["date"].dt.day_name()`, `orders["revenue"] > 40`). `as_index=False` keeps keys as columns.

## Choose by returned shape

| Method | Function gets | Returns | Result has | Question |
|---|---|---|---|---|
| `agg` | one column of one group | a single value | one row per group | revenue per region |
| `transform` | one column of one group | one value or one per row | same rows as input | share of region, deviation from group mean |
| `filter` | a whole group | True/False | subset of input rows | orders from repeat customers |
| `apply` | a whole group | anything | whatever you stitch | top order per region, weighted average |

- **Named aggregation** gives flat, chosen column names: `agg(units=("qty", "sum"), customers=("customer", "nunique"))`. Built-in names run in compiled code; a Python function is called once per group.
- **`transform`** broadcasts a group figure back to every row, so it can become a column: `x / x.groupby(key).transform("sum")` gives each row's share (shares per group sum to 1, which is worth asserting). Subtracting a group mean asks "is this large for its group?". It is the SQL window function `OVER (PARTITION BY ...)` (see [[SQL Window Functions]]).
- **`filter`** keeps or drops whole groups (`len(d) >= 2`); in SQL, `HAVING`.
- **`apply`** is the general, slowest escape hatch. For top row per group, `sort_values` then `groupby(...).head(n)` is faster and keeps the frame flat.

## Current-pandas behaviour

- `mean` on a frame with text columns raises `TypeError` (old versions silently dropped them). Select numeric columns or pass `numeric_only=True`.
- `groupby(axis=1)` was removed in 3.0; `grouped["a", "b"]` must be `grouped[["a", "b"]]`.
- `size` counts rows; `count` counts non-missing values per column. They differ exactly when a column has gaps.

## Pitfalls

Means without counts, averaging averages, lost keys: see [[Ratio of Sums vs Mean of Rates]] and [[Groupby Silent Group Loss and Pivot Defaults]]. Reaching for `apply` first.

## See Also
- [[Ratio of Sums vs Mean of Rates]] — extends
- [[Groupby Silent Group Loss and Pivot Defaults]] — extends
- [[SQL Window Functions]] — related
- [[Tidy Data and Long-Wide Reshaping]] — related
