---
title: Maximum Likelihood and Estimator Bias
tags: [foundations, concept]
summary: "An estimator is a recipe judged by bias, variance and MSE; maximum likelihood picks the parameter that makes the data most probable, gives standard errors from the curvature of the log-likelihood, and is a little biased at small n."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--04-estimation.md
---

# Maximum Likelihood and Estimator Bias

An **estimand** is the quantity you want, an **estimator** the recipe applied to data, an **estimate** the number it returns. Estimators are judged by bias (average error), variance (spread across datasets) and MSE (bias squared plus variance).

## Bias is not the whole story

Variance computed by dividing by n is biased low; dividing by n-1 removes the bias. Simulated at small n:

| Estimator | Bias | MSE |
|---|---|---|
| divide by n | -0.81 | 5.76 |
| divide by n-1 | -0.012 | 7.98 |

The biased estimator had the lower MSE. Unbiasedness is a property worth having, not a goal that beats variance every time.

## Maximum likelihood

Write the probability of the observed data as a function of the parameter and pick the value that maximises it (in practice the log-likelihood).

- **Bernoulli:** the MLE of p is k/N, the observed rate.
- **Standard error from curvature:** the sharper the peak of the log-likelihood, the more the data pin the parameter down. For a conversion rate the curvature-based SE (0.00328 in the example) matched sqrt(p(1-p)/N). This is how regression packages produce standard errors.
- **Lognormal:** fit on the log scale; the mean implied by the fitted parameters (64.59 in the example) differs from the raw sample mean (59.59). Fitting a parametric model is a bet that the family is right, and its implied mean leans on the tail the sample may not contain.

MLEs are consistent and efficient with enough data, but not guaranteed unbiased at small n, as the variance case shows.

## See Also
- [[Confidence Interval Coverage and Wilson]] — extends (intervals built on these standard errors)
- [[Delta Method for Ratio Metrics]] — extends (propagating the standard error through a function)
- [[Distribution Selection for Metrics]] — prerequisite-for
- [[Generalised Linear Models and Deviance]] — related (GLMs are fitted by maximum likelihood)
- [[Expectation and Variance Rules]] — prerequisite-for
