---
title: Jackknife Standard Error
tags: [data-analytics, probability-and-statistics, concept]
summary: The jackknife estimates a statistic's standard error from its n leave-one-out values; it matches classic formulas for smooth statistics but runs high and fails for non-smooth ones such as the median or a lowess curve.
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch10-jackknife-bootstrap.md
---

# Jackknife Standard Error

Chapter 10 of *Computer Age Statistical Inference* (Efron and Hastie) presents the jackknife and the bootstrap as two computational ways to get the standard error of an arbitrary statistic without a Taylor-series formula.

## Mechanism

Leave out observation i and recompute the statistic to get theta_(i). The jackknife standard error is [(n-1)/n x sum of (theta_(i) - theta_(.))^2]^(1/2), where theta_(.) is the mean of the leave-one-out values. Both methods can be viewed as resampling plans on the simplex of weight vectors: jackknife weight vectors sit 1/sqrt(n(n-1)) away from the equal-weight centre, and bootstrap vectors are roughly sqrt(n) times more distant. The infinitesimal jackknife uses the directional derivative with a very small step, and the influence function is the rate at which the statistic changes as a small mass eps is moved onto the point x.

## Worked results

- For the sample mean the jackknife standard error reproduces the classic formula, while the ideal bootstrap variance is off from it by the factor (n-1)/n.
- Setup: kidney data, 157 (age, tot) pairs, sample correlation -0.572. The jackknife and nonparametric bootstrap standard errors are both 0.058; the Taylor-series formula gives 0.057.
- Setup: scores of 22 students on five tests; the statistic is the top eigenvalue as a share of the eigenvalue total (0.693). The bootstrap standard error is 0.075 with B = 2000, and the jackknife value is larger. Reusing the same replications, jackknife-after-bootstrap puts the standard error of that 0.075 at 0.022, so with n = 22 it is not very accurate. Any given observation is absent from about 37% of bootstrap samples. The histogram has a long left tail, so a plus-or-minus 1.96 se interval is unsafe.
- Setup: the kidney lowess curve read off every five years from 20 to 85, bootstrap with B = 500. The jackknife overstates variability at age 25 while the bootstrap standard errors remain dependable.

## When it fails

The jackknife depends on local derivatives. It is upwardly biased for the true standard error (Efron and Stein, 1981) and cannot be trusted for statistics that are not smooth, the median being the example. The influence-function standard error also fails for the median, where Efron and Hastie advise the bootstrap instead.

## Limits

- Fails for non-smooth statistics (the lowess curve at age 25, the median).
- The jackknife standard error is upwardly biased.
- The bootstrap standard error on n = 22 is itself noisy.
- Bootstrap confidence intervals are not covered until chapter 11.

## See Also
- [[Bootstrap Resampling and Its Failures]] — alternative-to
- [[Delta Method for Ratio Metrics]] — alternative-to (the Taylor-series route it replaces)
- [[Confidence Interval Coverage and Wilson]] — related
- [[BCa Bootstrap Confidence Intervals]] — extends (uses the jackknife to get its acceleration constant)
