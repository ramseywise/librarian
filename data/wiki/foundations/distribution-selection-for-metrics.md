---
title: Distribution Selection for Metrics
tags: [foundations, reference]
summary: "Name the distribution behind a metric and you can usually name the test: Normal for measurements, Binomial for conversions, Poisson for counts, Exponential for gaps, lognormal for money, Beta for an uncertain rate."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--03-distributions-and-sampling.md
---

# Distribution Selection for Metrics

Every test and model is a statement about a distribution: a t-test assumes the sampling distribution of a mean is roughly Normal, a conversion rate is a Binomial proportion, error counts per hour are Poisson, and a prior is a distribution over a parameter.

| Data | Distribution | Parameters | Mean |
|---|---|---|---|
| Continuous measurement (latency, log-revenue) | Normal | mu, sigma | mu |
| Successes in n yes/no trials (conversions) | Binomial | n, p | np |
| Events in a fixed window (errors/hour) | Poisson | lambda | lambda |
| Waiting time between Poisson events | Exponential | lambda | 1/lambda |
| Positive, multiplicative (order value) | Lognormal | mu, sigma on log scale | exp(mu + sigma^2/2) |
| A probability itself | Beta | alpha, beta | alpha/(alpha+beta) |

## Non-obvious mechanisms

- **Poisson and Exponential are one process.** If events arrive at rate lambda, the count per unit time is Poisson(lambda) and the gap is Exponential(lambda). Simulating gaps at 3 per hour gave mean gap 0.333, mean count 3.004, variance 3.037 and P(count > 5) = 0.085 against Poisson 0.084.
- **A lognormal's mean grows with sigma** even when the median exp(mu) stays fixed: the tail moves the mean.
- **Binomial against Poisson:** Binomial for a count out of n trials, Poisson for a count in a window with no fixed ceiling.

## The `scipy.stats` interface

All distribution objects share `.pdf/.pmf`, `.cdf`, `.sf` (survival, P(X > x)), `.ppf` (inverse CDF, for critical values) and `.rvs`. Trap: `sf(k)` is P(X > k), so "10 or more" on a discrete variable is `sf(9)`. This off-by-one is the commonest bug in hand-rolled tests and fails silently.

## Checking a fit

Draw samples and compare with the theoretical distribution, plotting or using a Kolmogorov-Smirnov test. Exponentiated Normal draws were decisively non-Normal (p = 1.5e-56) even with mean and spread fitted. With enough rows a goodness-of-fit test rejects any model, and with few it passes most; read the plot and ask whether the misfit matters for the decision.

The data's distribution is not the statistic's: revenue is not Normal and never will be, the question is whether the mean of revenue is (see [[CLT on Heavy-Tailed Metrics]]).

## See Also
- [[CLT on Heavy-Tailed Metrics]] — extends (when the mean of a skewed metric becomes Normal)
- [[Statistical Test Selection]] — related (the distribution picks the test)
- [[Generalised Linear Models and Deviance]] — related (the distribution is the GLM family)
- [[Robust Summaries for Skewed Metrics]] — related
