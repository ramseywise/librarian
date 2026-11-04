---
title: "Same-Weekday Median and MAD Volume Monitor"
tags: [foundations, pattern]
summary: "A row-count baseline built from the median and MAD of the last six values for the same weekday catches a 25% loss that a 28-day mean-and-three-sigma band misses almost every time; validate any threshold by injecting losses into real history."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--02-monitors-and-lineage.md
---

# Same-Weekday Median and MAD Volume Monitor

A row-count monitor asks whether today's count is unusual. The obvious version alerts at three standard deviations from the mean of the last 28 days. The sturdier one uses the median and median absolute deviation (MAD, scaled by 1.4826 to match a standard deviation on normal data) of the last six values for the same weekday, with a floor (2% of the median) so a flat history does not fire on noise, and alerts at five times that spread.

## Why

A median barely moves when one value is extreme, so a duplicated day does not ruin the baseline. Comparing like with like shrinks the noise: weekday and weekend counts differed by 30% in the synthetic feed, so a mixed window had a standard deviation large enough to hide a modest loss.

## Sensitivity (synthetic feed, 46 scored days)

Both fired on the two blunt faults (zero rows, double rows). Injecting a loss into each normal day:

| Rows lost | Naive flagged | Robust flagged |
|---|---|---|
| 0% | 0% | 0% |
| 10% | 0% | 29% |
| 25% | 2% | 98% |
| 50% | 36% | 100% |

The naive monitor misses a quarter of the data almost every time. The gain comes from the seasonal comparison and the robust estimate together, not a clever threshold. These percentages describe that feed; run the injection on your own history before trusting a threshold. Using the last six days of any weekday instead pushed false alarms on normal days from 0% to 27%.

## Store metrics as a pipeline

Metrics need one row per day and metric, keyed by the data's **logical date**, not `now()`, so a backfill replaces rather than adds (a full rerun left 364 rows and the same sum). Alert on each metric the same way: null share, duplicate keys, median of a key column. Cautions:

- An empty day has a median of zero, so alert on row count first and suppress downstream noise.
- Recomputing history erases what was visible when; keep the original value and the time recorded if detection delay matters.
- Dropping the metrics table on each run, as a demo loop does, loses history.
- Alert on what consumers act on; chart the rest with no page attached.

## See Also
- [[Freshness Alerts Need a Date Spine]] — related
- [[Distribution Monitors Need an Effect Size and a Fixed Reference]] — related
- [[Robust Summaries for Skewed Metrics]] — related (median over mean)
- [[Idempotent Backfills and Dated Corrections]] — related
