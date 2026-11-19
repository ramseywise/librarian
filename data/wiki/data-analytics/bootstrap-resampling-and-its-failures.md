---
title: Bootstrap Resampling and Its Failures
tags: [data-analytics, probability-and-statistics, pattern]
summary: "The bootstrap resamples the independent unit with replacement to get a standard error or interval without a formula, but it fails for extremes, tails that the sample never saw, and dependent rows resampled one at a time."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--04-estimation.md
  - data/raw/papers/2026-11-08-practical-statistics-for-data-scientists-ch02-data-sampling-distributions.md
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch10-jackknife-bootstrap.md
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch01-algorithms-inference.md
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch02-frequentist-inference.md
  - data/raw/papers/2026-11-08-islp-ch05-resampling-methods.md
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch14-statistical-inference-methodology-postwa.md
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

## Book example and advice

In chapter 2 of *Practical Statistics for Data Scientists* (R, `boot` package), a bootstrap of the median loan-applicant income (Lending Club, R = 1000) gave an original median of 62,000, a bias of about -$70 and a standard error of $209. The authors prefer the bootstrap to formula-based standard errors and intervals, advise exploring sample size by varying n, and note that it does not compensate for a small sample.

## More from Computer Age Statistical Inference

- Replications: B = 200 is usually enough for a standard error; confidence intervals need 1,000 to 2,000, and far fewer (25 or even less) can help when resampling is costly. The text says its eigenratio example used ten times more replications than the standard error needed.
- Distinct samples: there are C(2n-1, n) distinct bootstrap samples, 92,378 for n = 10.
- Two groups: the multisample bootstrap resamples each group separately. For AML (n = 25) against ALL (n = 47) with B = 500, the median difference of 0.235 has a bootstrap SE of 0.074, which is 3.18 SE above zero, next to a two-sample t of 3.01.
- Choice of statistic: for 47 ALL scores (B = 1,000 per trim value) a 0.2-trimmed mean has bootstrap SD 0.035 against 0.040 for the mean.
- Non-smooth statistics: for the gfr data (211 kidney patients, B = 1,000) the bootstrap SE of the 25% Winsorized mean is .78 and of the median (52.24) is .87.
- Flexible fits: resampling the 157 kidney (age, tot) pairs 250 times and refitting lowess gave SEs roughly double a straight line's.
- Variants named: a moving-blocks bootstrap for time series, a parametric bootstrap when a model is credible, and Bayesian bootstrap weights.
- Parametric versus nonparametric: on the 22-student score data (eigenratio 0.693, B = 2,000) the nonparametric SE is 0.075; the parametric normal-model version gave a smaller SE, though the data contain a notable outlier that makes normality doubtful.

## Standard-error comparisons from Introduction to Statistical Learning

- Simulated portfolio problem (100 pairs, true alpha 0.6, 1,000 resamples): the bootstrap standard error of the estimate is close to the one from 1,000 fresh simulated data sets, whose estimates average 0.5996. The extraction does not record the two SE values.
- Auto data (392 cars, 1,000 resamples), mpg on horsepower: for the straight-line fit the formula SE of the slope is 0.006 against a bootstrap SE of 0.0074, and the intercept 0.717 against 0.85. The authors attribute the gap to a misspecified linear model; for the quadratic fit the two agree closely.

## Where the bootstrap sits in the postwar scorecard (Efron and Hastie, chapter 14)

Efron and Hastie arrange fifteen postwar methods on a Bayesian, frequentist and Fisherian triangle, colouring each by its reliance on computing; machine speed grew a thousandfold twice over in the period. They name the bootstrap the model computer-intensive method, a frequentist technique carrying Fisherian devices (plug-in accuracy estimates and arguments for why its confidence intervals are correct). The jackknife, which produces frequentist standard errors and biases, needs little electronic computing. Cross-validation is a thoroughly frequentist tool that only became popular once computers were fast.

## Limits

- Practical Statistics ch02: its formulas were lost in extraction, its text prints no author names (the Bruce attribution comes from the book's known authorship), and a small sample is not rescued by bootstrapping it.
- Computer Age chapter 10: with n = 22 the bootstrap SE of 0.075 is imprecise, since resampling the replications puts its own SE at 0.022; the moving-blocks block length is only said to be large enough; the parametric SE (0.070) is doubtful because of the outlier.
- Introduction to Statistical Learning ch05: the bootstrap appears only as a standard-error tool, with no .632 or out-of-bag error, and the full author list is not printed in the extraction.
- Efron and Hastie's chapter 14 placements are an informal scorecard that the authors call not very precise; where each method sits and how it is coloured is the authors' judgment, not a measurement.

## See Also
- [[Permutation Test]] — related (resampling for a null distribution rather than a standard error)
- [[Confidence Interval Coverage and Wilson]] — alternative-to
- [[Independence Pitfalls]] — related
- [[BCa Bootstrap Confidence Intervals]] — extends
- [[Jackknife Standard Error]] — alternative-to
