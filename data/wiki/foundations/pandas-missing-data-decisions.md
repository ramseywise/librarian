---
title: Pandas Missing Data Decisions
tags: [foundations, decision]
summary: Pandas can count, fill and drop gaps but cannot say what a gap means; the treatment follows from why the value is missing.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--01-python-for-data-analysis--notes--02-loading-and-cleaning.md
  - data/raw/repos/learn-ai-engineering/data-analytics--01-python-for-data-analysis--notes--05-groupby-and-aggregation.md
  - data/raw/repos/learn-ai-engineering/data-analytics--01-python-for-data-analysis--notes--06-time-series.md
---

# Pandas Missing Data Decisions

## What counts as missing on load

`read_csv` treats `n/a`, `NA`, `NaN`, `null` and the empty string as missing by default. A column that gains a gap becomes `float64` (see [[Pandas Label Alignment and Dtypes]]). A file's own marker, such as `-` for "no region", is invisible to pandas: declare it per column with `na_values={"region": ["-"]}`. `pd.to_numeric(..., errors="coerce")` and `pd.to_datetime(..., errors="coerce")` turn failures into `NaN` / `NaT`; always count what they produce, or a format change upstream can wipe out a column unnoticed.

## Decide by asking why it is empty

- **Structural** gap: the value could not exist or be measured, so it can be removed safely.
- **Missing observation**: the value should have been recorded; keep the row or state the exclusion.
- **Related to the value itself**: if high earners skip an income question, dropping those rows biases every later average.

## Treatments and when they fail

| Move | Fits | Fails when |
|---|---|---|
| Fill with a label (`fillna("unknown")`) | a categorical gap that does not block the metric; keeps the row and the ignorance visible | the column feeds arithmetic |
| Find out the true value and write it with one `.loc`, with a comment recording the decision | a gap the metric depends on | no one can confirm it |
| Exclude from the metric and say so | the honest alternative when it cannot be found | the exclusion is silent |
| Fill with the mean | rarely | it shrinks variance and can invent impossible values (a fractional count of items) |
| `ffill` | slowly changing readings, such as a price list | independent events, such as separate orders |
| `dropna(subset=[...])` | gaps in columns you actually need | the gaps are informative |
| Group-wise fill: `fillna(groupby(k).transform("mean"))` | groups differ in level | the reason for missingness is still unexamined |

The old `fillna(method="ffill")` form was removed in pandas 3.0; use `.ffill()`.

## Reading summaries

`sum` and `mean` skip missing values, so a mean can look fine when half the column is empty. Print the count beside the mean. In a group example, a mean of 5.0 rested on one value out of two and a mean of 4.0 on one out of three.

## Gaps in time series

On time data an absent row is a hidden gap. `asfreq` makes it visible as `NaN`; then decide: an outage is true zero revenue, so leaving `NaN` is the honest record; a sensor might be interpolated; a price carried forward. See [[Time-Series Resampling, Bins and Gaps]].

## Impossible values

A value can parse and still be wrong, such as a negative quantity. Set such rows aside in a separate frame rather than deleting them, so the removed amount can be reported and undone. See [[Rerunnable Cleaning Loader with Assertions]].

## See Also
- [[Rerunnable Cleaning Loader with Assertions]] — extends
- [[Groupby Silent Group Loss and Pivot Defaults]] — related
- [[SQL NULL and Three-Valued Logic]] — related
