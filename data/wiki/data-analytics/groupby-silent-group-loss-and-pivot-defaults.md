---
title: Groupby Silent Group Loss and Pivot Defaults
tags: [data-analytics, python-for-data-analysis, pattern]
summary: Groupby drops NaN keys, hides empty categories or averages by default without a warning, so compare the sum of groups with the overall total and state every default.
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--01-python-for-data-analysis--notes--05-groupby-and-aggregation.md
  - data/raw/repos/learn-ai-engineering/data-analytics--01-python-for-data-analysis--notes--02-loading-and-cleaning.md
  - data/raw/papers/2026-11-08-python-for-data-analysis-ch10-data-aggregation-group.md
  - data/raw/papers/2026-11-08-python-for-data-analysis-ch14-data-analysis-examples.md
  - data/raw/papers/2026-11-08-python-for-data-analysis-ch07-data-cleaning-preparation.md
---

# Groupby Silent Group Loss and Pivot Defaults

## Missing keys vanish

A row whose group key is `NaN` is excluded from the result. In a four-row example (keys `n`, missing, `s`, missing; values 10, 20, 30, 40) the groups summed to 40.0 against an overall 100.0. `dropna=False` keeps the missing keys as their own group (60.0). If a third of orders lack a region, regional totals will not add to the grand total and nothing says so. **Cheap check: the sum of the groups equals the total.** The same silent-loss habit applies to joins (see [[Pandas Merge Validation and Many-to-Many Blow-up]]).

## Bucketed keys

`pd.cut` splits by values you choose (bins closed on the right: `(0, 20]` includes 20, not 0) and fits thresholds that mean something; `pd.qcut` splits by quantiles into equal-sized groups. Their output is a ready groupby key. For categorical keys, `observed` defaults to `True` since pandas 3.0, so empty categories are omitted; `observed=False` lists them all (a `100+` band with count 0), which a report with a fixed row list wants.

## Counts beside means

`size` counts rows, `count` counts non-missing values. A mean of a mostly empty column looks as solid as one from a full column; always show the count. See [[Pandas Missing Data Decisions]].

## What the books add

- McKinney confirms that rows whose group key is missing drop out of the output.
- `qcut` gives equal-size groups and `cut` equal-width ones: on 1000 random draws, ten `qcut` buckets held exactly 100 each, while `cut` into four gave 95, 598, 297 and 10. In ch7, `pd.cut` with four age bins on 12 ages gave counts 5, 3, 3, 1.
- On the 244-row tips data, `pd.crosstab(..., margins=True)` counts 151 non-smoker and 93 smoker parties, and `tip_pct` averages 0.159328 for non-smokers against 0.163196 for smokers but standard deviation 0.039910 against 0.085119, driven by a maximum of 0.710345.
- Before ranking group means, drop groups with too few rows: in MovieLens 1M, a threshold of 250 ratings (stated as arbitrary) left 1,216 titles. Restrict to positive amounts before analysing contributions: in the 2012 FEC file, 10,256 non-positive rows (refunds) were dropped, leaving 991,475. Compare bucketed groups after normalising within buckets: Obama had 372,280 contributions in the (10, 100] dollar bin against Romney's 31,853, while Romney led the (1000, 10000] bin.
- `pivot_table` accepts `fill_value` for empty cells and `margins=True` for subtotals.

## Pivot tables and crosstabs

`pivot_table` is a groupby by two keys laid out as a grid, and it aggregates duplicate combinations where `pivot` fails. Its default `aggfunc` is the **mean**, rarely what you want for revenue, so state it. `margins=True` adds totals (check they equal the grand total, 523.5 in the worked example); `fill_value=0` fills empty cells.

`pd.crosstab` counts by default; `normalize="index"` (or columns, or all) turns counts into shares, which is how to compare groups of different sizes.

## Pitfalls

- Averaging averages: see [[Ratio of Sums vs Mean of Rates]].
- Defaults left unstated (`aggfunc`, `dropna`, `observed`).

## Limits

- The ch10 examples use unseeded random data; ch10 and ch14 target 2017-era pandas (`axis=1` in `groupby`, `pd.value_counts`, positional `sum(1)`).
- ch14 is descriptive only: no inference, tests or uncertainty. The chapter admits simplifications: one third-party candidate counted as Republican, an arbitrary 250-rating cut-off, the two largest bins treated as non-individual donors, and no de-duplication of donors. Its printed output is not fully self-consistent (`C.E.O.` still listed after the mapping to `CEO`).

## See Also
- [[Groupby Split-Apply-Combine and Result Shapes]] — prerequisite-for
- [[Ratio of Sums vs Mean of Rates]] — related
- [[Pandas Missing Data Decisions]] — related
- [[Tidy Data and Long-Wide Reshaping]] — related
