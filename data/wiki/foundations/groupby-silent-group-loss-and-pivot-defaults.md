---
title: Groupby Silent Group Loss and Pivot Defaults
tags: [foundations, pattern]
summary: Groupby drops NaN keys, hides empty categories or averages by default without a warning, so compare the sum of groups with the overall total and state every default.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--01-python-for-data-analysis--notes--05-groupby-and-aggregation.md
  - data/raw/repos/learn-ai-engineering/data-analytics--01-python-for-data-analysis--notes--02-loading-and-cleaning.md
---

# Groupby Silent Group Loss and Pivot Defaults

## Missing keys vanish

A row whose group key is `NaN` is excluded from the result. In a four-row example (keys `n`, missing, `s`, missing; values 10, 20, 30, 40) the groups summed to 40.0 against an overall 100.0. `dropna=False` keeps the missing keys as their own group (60.0). If a third of orders lack a region, regional totals will not add to the grand total and nothing says so. **Cheap check: the sum of the groups equals the total.** The same silent-loss habit applies to joins (see [[Pandas Merge Validation and Many-to-Many Blow-up]]).

## Bucketed keys

`pd.cut` splits by values you choose (bins closed on the right: `(0, 20]` includes 20, not 0) and fits thresholds that mean something; `pd.qcut` splits by quantiles into equal-sized groups. Their output is a ready groupby key. For categorical keys, `observed` defaults to `True` since pandas 3.0, so empty categories are omitted; `observed=False` lists them all (a `100+` band with count 0), which a report with a fixed row list wants.

## Counts beside means

`size` counts rows, `count` counts non-missing values. A mean of a mostly empty column looks as solid as one from a full column; always show the count. See [[Pandas Missing Data Decisions]].

## Pivot tables and crosstabs

`pivot_table` is a groupby by two keys laid out as a grid, and it aggregates duplicate combinations where `pivot` fails. Its default `aggfunc` is the **mean**, rarely what you want for revenue, so state it. `margins=True` adds totals (check they equal the grand total, 523.5 in the worked example); `fill_value=0` fills empty cells.

`pd.crosstab` counts by default; `normalize="index"` (or columns, or all) turns counts into shares, which is how to compare groups of different sizes.

## Pitfalls

- Averaging averages: see [[Ratio of Sums vs Mean of Rates]].
- Defaults left unstated (`aggfunc`, `dropna`, `observed`).

## See Also
- [[Groupby Split-Apply-Combine and Result Shapes]] — prerequisite-for
- [[Ratio of Sums vs Mean of Rates]] — related
- [[Pandas Missing Data Decisions]] — related
- [[Tidy Data and Long-Wide Reshaping]] — related
