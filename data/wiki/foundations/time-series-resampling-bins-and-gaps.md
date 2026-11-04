---
title: Time-Series Resampling, Bins and Gaps
tags: [foundations, concept]
summary: Absent rows hide gaps in time data, and resample is a time-bin groupby whose closed and label edges, unequal period lengths and fill rules change the numbers.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--01-python-for-data-analysis--notes--06-time-series.md
---

# Time-Series Resampling, Bins and Gaps

Time carries rules that labels do not: rows have order, months have different lengths, a label like "January" stands for an interval, and a missing value is often just an absent row.

## Make gaps visible

With a `DatetimeIndex`, partial strings are slices (`daily.loc["2024-02"]`), and label slices include both ends. A year of daily revenue with three days removed had 363 rows against 366 calendar days and a four-day range returned two rows with no warning. `asfreq("D")` conforms the series to a regular frequency and shows the gaps as `NaN` (3 here). What a gap means then decides the treatment: an outage is true zero, so leave `NaN`; a sensor might be interpolated; a price carried forward. See [[Pandas Missing Data Decisions]]. Sort the index before slicing (`is_monotonic_increasing`).

## resample is a groupby on time bins

`regular.resample("ME").sum()` or `.agg(["sum", "mean", "count"])`. Read the `count`: January had 31 observations, February 29, and March 29 once two outage days dropped out. A monthly sum compares unequal lengths, so mean per day is often the fairer comparison. Month-over-month change on mean daily revenue made December the largest rise (0.444), which matched the built-in December bump.

### closed and label

A bin is an interval; **`closed`** says which edge is inside, **`label`** which edge names it. Month-end bins default to closed right, labelled right (January is `2024-01-31`); 5-minute bins default to left and left. On minutes 0 to 11 the sums were 10, 35, 21 with defaults and 0, 15, 40, 11 with `closed="right", label="right"`. Both are right and answer slightly different questions; in logging and finance whether the value stamped 09:05 belongs to the 09:05 bar is a real decision. `W-SUN` weeks end on Sunday, matching a Monday-to-Sunday report.

### Upsampling

Going to a finer frequency creates empty rows. `asfreq()` leaves `NaN`; `ffill()` carries a value forward, which suits a price list and misrepresents a sales total.

## Periods versus timestamps

A timestamp is a moment; a period is a span (all of March 2024). `to_period("M")` labels monthly rows without arguing about the 1st or the 31st, and works as a groupby key. Grouping by weekday checks for a weekly pattern before trusting cross-day comparisons.

## See Also
- [[Time-Series Leakage: Shift and Rolling Windows]] — extends
- [[Datetime Parsing, Frequency Aliases and Time Zones]] — prerequisite-for
- [[Groupby Split-Apply-Combine and Result Shapes]] — related (resample is the time-keyed form)
- [[Pandas Missing Data Decisions]] — related
