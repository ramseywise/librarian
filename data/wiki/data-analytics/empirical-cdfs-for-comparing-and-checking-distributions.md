---
title: "Empirical CDFs for Comparing and Checking Distributions"
tags: [data-analytics, probability-and-statistics, pattern]
summary: "A cumulative distribution function compares groups without the noise of a PMF, converts values to percentile ranks, generates random draws by inversion, and turns exponential, Pareto and lognormal fit checks into straight-line tests."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-think-stats-ch03-cumulative-distribution-functions.md
  - data/raw/papers/2026-11-08-think-stats-ch04-continuous-distributions.md
  - data/raw/papers/2026-11-08-think-stats-ch02-descriptive-statistics.md
---

# Empirical CDFs for Comparing and Checking Distributions

Downey's *Think Stats* uses the cumulative distribution function (CDF) as the working tool for describing a sample. CDF(x) is the fraction of sample values at or below x, which makes it a step function: zero until the smallest value, one from the largest on. The sample {1, 2, 2, 3, 5} gives CDF(2) = 0.6 and CDF(4) = 0.8.

## Comparing groups

A histogram or PMF (probability mass function) of a continuous quantity shows noise spikes, and bins large enough to smooth them can also smooth out real information. For groups of unequal size he advises PMFs, not histograms, and for distributions with many distinct values he advises CDFs. In the NSFG birth-weight data (first babies against others, no sample sizes given), the CDFs put first babies a little lighter across the range, with the gap widest above the mean, a pattern that noisy PMFs hid.

## Percentile ranks and sampling

- The percentile rank of a value is 100 times the count of scores at or below it divided by the number of scores. Take the scores 55, 66, 77, 88 and 99: 88 sits at rank 80, and 77 is the 50th percentile.
- To compare across groups, convert each measurement to a percentile rank within a conditioning cohort.
- To draw random values from a distribution, pick p uniform in 0 to 1 and return the value whose CDF is p. For the exponential, x = -log(1 - p) / lambda.
- The median is the 50th percentile and the interquartile range is the 75th minus the 25th percentile. Downey's median does not average the middle two values for even n.
- Bisection on the sorted values makes each CDF lookup O(log n).

## Straight-line checks for continuous models

Downey advises plotting the complementary CDF (one minus the CDF) on transformed axes:

| Model | Plot | A fit looks like |
|---|---|---|
| Exponential | CCDF, log y axis | a line of slope -lambda |
| Pareto | CCDF, log-log axes | a line of slope -alpha |
| Lognormal | normal check on the logged values | the log is normal |
| Normal | normal probability plot: sorted data against sorted standard-normal values or rankits | a straight line |

In Exercise 4.9, rankits for 6 standard normal draws are found as the mean of the sorted values over 1000 repetitions.

Worked cases from the chapters:

- NSFG live-birth weights: a normal with mu = 116.5 and sigma = 19.9 ounces has small error overall but underpredicts babies below the 10th percentile, so it should not be used for preterm studies.
- Forty-four births in one Brisbane day (18 December 1997): interarrival times look roughly exponential, but the CCDF on a log axis is not exactly straight.
- BRFSS 2008 adult weights in kg (414,509 respondents, of whom 398,484 have weights): a normal describes log weight well, which makes weight lognormal, apart from the heaviest values that exceed the model. A lognormal's mean works out to exp(mu + sigma^2/2) rather than mu.
- Take a Pareto with xm = 0.5 and alpha = 1: its median is 1 yet its 95th percentile reaches 10, where an exponential with median 1 gives 1.5.

Downey's rule is that a model is acceptable only where it fits the part of the range that matters to you.

## Limits

- Every fit check is by eye on a line; the chapters supply no formal test or tolerance.
- The birth-weight contrast comes from a plot, without sample sizes or a significance test.
- The extractions note the code is Python 2 era and relies on the author's own library and downloads.
- The Percentile function as printed is O(n^2) and sorts its input in place.
- The normal fails in the lower tail of birth weight and the lognormal in the upper tail of weight.

## See Also
- [[Distribution Selection for Metrics]] — prerequisite-for
- [[Robust Summaries for Skewed Metrics]] — related (the empirical CDF as a bin-free summary)
- [[Inspection Paradox in Metrics]] — related (the same chapter's size-biased sampling)
