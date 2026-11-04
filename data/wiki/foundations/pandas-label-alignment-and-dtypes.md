---
title: Pandas Label Alignment and Dtypes
tags: [foundations, concept]
summary: pandas matches values by label rather than position and ties behaviour to per-column dtypes, so NaN promotion and text-typed numbers are the first things to check on any frame.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--01-python-for-data-analysis--notes--01-series-and-dataframe.md
---

# Pandas Label Alignment and Dtypes

A Series is one column of a single dtype plus a label for every value (the index). A DataFrame is a set of Series sharing one index, so each column has its own dtype. Arithmetic is vectorised: it runs in compiled NumPy code and states intent without a loop.

## Alignment

Operations between two objects match values by **label, not position**. The result carries the union of the labels, and a label present on only one side becomes `NaN` rather than a guess. The same numbers as bare NumPy arrays add by position and silently pair unrelated items, which is the mistake alignment removes. The residual trap is visible `NaN`s.

- If a missing label really means zero, say so: `a.add(b, fill_value=0)`.
- Whether a gap means zero or unknown is a question about the data, not the code. See [[Pandas Missing Data Decisions]].
- With a partly matching index (for example a dict Series reindexed), unmatched labels get `NaN` too.

## NaN is a float

`NaN` is a floating-point value, so an integer column that needs to hold a gap is promoted to `float64`. A whole-number column printing with `.0` usually hides a missing value: check `isna().sum()`. `NaN == NaN` is false, so test with `isna()`, never `==`.

## Dtypes decide what an operation means

| dtype | Missing marker | Typical trouble |
|---|---|---|
| `int64` | cannot hold one | one gap promotes to `float64` |
| `float64` | `NaN` | rounding error when summing money |
| `str` | `NaN` | numbers and dates read as text |
| `bool` | cannot hold one | a gap makes it `object` |
| `datetime64` | `NaT` | dates left as text |
| `category` | `NaN` | a value outside the declared set becomes `NaN` |

A single stray token such as `"n/a"` makes a numeric column read as text, and then `sum` concatenates strings instead of adding. Convert deliberately: `astype` when the type is known, `pd.to_numeric` or `pd.to_datetime` when the data may be dirty.

Since pandas 3.0 inferred text gets a dedicated `str` dtype instead of `object`; it holds only strings or missing values. Code that finds text columns with `dtype == object` no longer works.

## First look at a new frame

Run the same few calls before believing anything: `shape`, `head`, `dtypes`, `info`, `isna().sum()`, `describe`, and `value_counts` on categorical columns. In `describe`, `count` is non-missing values, so a count below the row total is the first sign of gaps, and a mean well above the median signals skew (see [[Robust Summaries for Skewed Metrics]]). These calls catch an impossible maximum or a category spelled two ways.

## Habits

- Methods return new objects (`drop`, `sort_values`); assign the result or nothing is kept.
- Avoid row-by-row loops and `iterrows`; look for a vectorised column expression first.
- Pre-3.0 advice about views and copies is obsolete: see [[Pandas Copy-on-Write and Chained Assignment]].

## See Also
- [[Pandas Copy-on-Write and Chained Assignment]] — related (the other 3.0 behaviour change)
- [[Pandas loc, iloc and the Integer Index Trap]] — extends
- [[Pandas Missing Data Decisions]] — extends
- [[Robust Summaries for Skewed Metrics]] — related
