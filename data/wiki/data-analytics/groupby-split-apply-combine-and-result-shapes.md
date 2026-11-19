---
title: Groupby Split-Apply-Combine and Result Shapes
tags: [data-analytics, python-for-data-analysis, concept]
summary: groupby splits a table, applies a function per group and recombines; agg, transform, filter and apply differ by the shape they return, and picking one starts from what a row of output should mean.
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--01-python-for-data-analysis--notes--05-groupby-and-aggregation.md
  - data/raw/papers/2026-11-08-python-for-data-analysis-ch10-data-aggregation-group.md
  - data/raw/papers/2026-11-08-python-for-data-analysis-ch12-advanced-pandas.md
  - data/raw/papers/2026-11-08-python-for-data-analysis-ch14-data-analysis-examples.md
  - data/raw/papers/2026-11-08-python-data-science-handbook-ch03-data-manipulation-pandas.md
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

## What the books add

- Wickham coined the term split-apply-combine; McKinney builds *Python for Data Analysis* ch10 on it and VanderPlas's ch3 gives the same four-way split: aggregate reduces each group, filter removes whole groups, transform preserves shape, and apply covers the rest.
- McKinney: user-written aggregators are usually far slower than the built-ins, owing to call and data-reshuffling overhead (qualitative, no timing). Pass a list of `(name, function)` tuples to `agg`, since lambdas are all named `<lambda>`. `as_index=False` avoids some computation compared with `reset_index`. `group_keys=False` in `apply` drops the group index, and `g.name` inside `apply` gives the group's key.
- ch12: `transform('mean')` broadcasts group means to the original shape, and `(value - transform('mean')) / transform('std')` equals an `apply(normalize)` (first element -1.161895 on a 12-row example); he claims the built-in `transform` path is much faster than `apply`, with no timing. For per-key time bins, group by `[key, TimeGrouper('5min')]` with time as the index. `assign` with callables and `pipe` avoid temporaries in chains, though he says chaining is a matter of taste.
- ch14 normalises inside groups using `transform('sum')` instead of `apply`, and takes top-n with `nlargest` rather than sorting by hand.
- A worked `apply` on 2003-01-02 to 2011-10-14 closes (2,214 rows): the per-year correlation between AAPL and SPX daily returns ran from 0.374283 (2004) up to 0.710105 (2010), and the yearly OLS slope of AAPL on SPX fell from 1.766415 (2005) to 0.806605 (2011).

## Current-pandas behaviour

- `mean` on a frame with text columns raises `TypeError` (old versions silently dropped them). Select numeric columns or pass `numeric_only=True`.
- `groupby(axis=1)` was removed in 3.0; selecting several columns with `grouped["a", "b"]` must pass a list of names instead.
- `size` counts rows; `count` counts non-missing values per column. They differ exactly when a column has gaps.

## Pitfalls

Means without counts, averaging averages, lost keys: see [[Ratio of Sums vs Mean of Rates]] and [[Groupby Silent Group Loss and Pivot Defaults]]. Reaching for `apply` first.

## Limits

- Edition: ch10 relies on `groupby(axis=1)`, tuple-style column selection and NumPy functions passed to `agg`, all later deprecated or removed. `TimeGrouper` was removed; the extraction names `pd.Grouper(freq='5min')` as the replacement (its own knowledge, not the chapter's).
- None of the speed claims above has a timing. The ch10 example data are unseeded random draws, so printed numbers do not reproduce. Resampling is deferred to ch11 and more groupby cases to ch14.
- ch12 typo: one `assign` example averages `col2` where `col1` is intended. Its chained-assignment example would trigger `SettingWithCopy`, which the extraction notes the chapter does not say.

## See Also
- [[Ratio of Sums vs Mean of Rates]] — extends
- [[Groupby Silent Group Loss and Pivot Defaults]] — extends
- [[SQL Window Functions]] — related
- [[Tidy Data and Long-Wide Reshaping]] — related
