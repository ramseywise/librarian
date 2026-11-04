---
title: Robust Summaries for Skewed Metrics
tags: [foundations, concept]
summary: "When mean and median disagree, the tail is running the summary: choose location, spread and correlation measures the shape allows, and report percentiles and the mean-to-median ratio instead of one number."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--01-descriptive-statistics-and-eda.md
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--README.md
---

# Robust Summaries for Skewed Metrics

A summary of location is one number standing in for many, and it is honest only if the data allow it. Money, session length and most product metrics are right-skewed and often zero-inflated, which breaks the default summaries.

## Location

On a worked revenue column (20,000 users, about 5% buyers, lognormal spend) the figures were: among buyers, mean 65.86, 10% trimmed mean 46.81, median 37.38; across all users, mean 3.30 and median 0.00. The top 1% of buyers held 10% of revenue.

- The **mean** scales to totals: total revenue is mean times users, whatever the shape. Use it to forecast.
- The **median** describes the typical buyer. Neither is more true; they answer different questions.
- The **trimmed mean** drops a fixed share from each end, a compromise that removes the leverage of extremes.
- A robust statistic is not automatically better: an experiment that only moves the largest customers can leave the median flat while the business changes.

## Spread

Standard deviation squares deviations, so one large value dominates. The interquartile range and the median absolute deviation (MAD, the median distance from the median) ignore the tail. Leaving two bad rows of 48,000 among 20,000 moved the buyers' mean from 65.86 to 161.25 and the standard deviation from 93.65 to 2,139, while the median moved from 37.38 to 37.45.

That comparison is the most reliable outlier detector: when mean and median, or standard deviation and IQR, disagree by a lot, look at the tail. Report percentiles (141 at p90 and 427 at p99 say more than a mean) and the mean-to-median ratio. For a lognormal with log-scale sigma s the theoretical ratio is exp(s^2/2), about 1.83 for s = 1.1.

## Shape and scale

A histogram of the raw column shows a long right tail; on a log10 scale the same data were near symmetric, which says the spend is roughly lognormal (skewness 5.1 raw, about 0 on the log scale). Compare on the log scale when you care about multiplicative change. The empirical CDF has no bins to choose and reads as sentences ("61% of orders are at most 50").

## Pearson against Spearman

Pearson correlation is linear and as outlier-sensitive as the mean. One bad row among 500 flipped a Pearson correlation from +0.44 to -0.31, while Spearman (on ranks) moved from +0.42 to +0.41. Compute both; if they disagree, plot. A correlation near zero rules out only a straight-line relationship.

## See Also
- [[EDA Audit Loop]] — related (where these summaries are chosen)
- [[Distribution Selection for Metrics]] — related (lognormal and zero-inflated shapes)
- [[Statistical Test Selection]] — related (rank tests for the same skew problem)
- [[CLT on Heavy-Tailed Metrics]] — related (skew also slows the central limit theorem)
- [[Matplotlib Object Model and Seaborn Function Levels]] — related (box plots on a log scale for skewed values)
