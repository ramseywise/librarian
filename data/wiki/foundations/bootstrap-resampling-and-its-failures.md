---
title: Bootstrap Resampling and Its Failures
tags: [foundations, pattern]
summary: "The bootstrap resamples the independent unit with replacement to get a standard error or interval without a formula, but it fails for extremes, tails that the sample never saw, and dependent rows resampled one at a time."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--04-estimation.md
---

# Bootstrap Resampling and Its Failures

## Mechanism

Treat the sample as the population, resample it with replacement many times, recompute the statistic each time, and read the standard error or interval off the spread. No formula needed, so it works for medians, ratios and odd statistics. The rule that matters: **resample the independent unit**.

## Interval choice

On skewed revenue the percentile interval was [1.872, 3.610] and the bias-corrected and accelerated (BCa) interval [1.941, 3.802]. BCa corrects for bias and skew and moves toward the heavy tail; prefer it on skewed statistics.

## Where it fails

| Failure | Evidence | Why |
|---|---|---|
| Extremes (maximum) | 64% of resamples tie with the sample maximum | resampling cannot exceed what was observed |
| Rows when the unit is a cluster | row SE 0.027, cluster SE 0.047, true SE 0.049 | rows are dependent; resampling them hides it |
| Tail not in the sample | the interval misses a whale that was never drawn | the bootstrap only knows the sample |
| Time series | needs a block bootstrap | resampling single points breaks autocorrelation |

Resample at the cluster level (user, store, school) when rows share one ([[Pseudoreplication and Intraclass Correlation]], [[Clustered Standard Errors]]).

## Uses

Cross-check for the [[Delta Method for Ratio Metrics]] (user-level bootstrap SE 0.195 against delta 0.193); interval for a median difference when a rank test does not answer the question ([[Statistical Test Selection]]); a way to avoid trusting the CLT on heavy tails ([[CLT on Heavy-Tailed Metrics]]).

## See Also
- [[Permutation Test]] — related (resampling for a null distribution rather than a standard error)
- [[Confidence Interval Coverage and Wilson]] — alternative-to
- [[Independence Pitfalls]] — related
