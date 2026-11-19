---
title: Delta Method for Ratio Metrics
tags: [data-analytics, experimentation-and-causality, pattern]
summary: "A ratio of two per-user totals, such as revenue per session, needs a standard error that accounts for numerator and denominator co-varying; computing it as if sessions were the independent units understates it by about 40 percent."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--04-estimation.md
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch01-algorithms-inference.md
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch02-frequentist-inference.md
---

# Delta Method for Ratio Metrics

Metrics like revenue per session or clicks per impression are a ratio of totals, R = mean(Y)/mean(X), where the randomisation unit is the user, not the session. Treating each session as an independent row gives a standard error that is too small.

## Formula

A first-order Taylor expansion gives

```text
Var(R) ~ [ Var(Y) - 2 R Cov(Y, X) + R^2 Var(X) ] / ( n * mean(X)^2 )
```

with variances and covariance taken across the independent units (users) and n their count. The covariance term matters: users with more sessions also have more revenue.

## Check

Revenue per session 1.832:

| Method | SE |
|---|---|
| naive, sessions as independent rows | 0.116 |
| delta method (users as units) | 0.193 |
| user-level bootstrap | 0.195 |

The naive SE was about 40% too small. The delta method and bootstrap agree, so the delta method is the cheap closed form and [[Bootstrap Resampling and Its Failures]] the check.

## When to use

Any ratio of sums where the units differ from the denominator's grain: per-session, per-impression, per-order metrics in an experiment. It is the same fix as cluster-robust errors in spirit: identify the independent unit ([[Clustered Standard Errors]], [[Pseudoreplication and Intraclass Correlation]]) and compute variability there. The rules used are in [[Expectation and Variance Rules]].

## The delta method in the general plug-in toolkit

Efron and Hastie (*Computer Age Statistical Inference*, ch. 2) list five practical devices for the accuracy of an estimate: plug-in, the delta method, parametric maximum likelihood theory, simulation (the bootstrap) and pivotal statistics. Plug-in means estimating the unknown, distribution-dependent accuracy formula from the observed data: the mean's standard error uses the unbiased variance estimate sum (x_i - xbar)^2/(n-1) in [var/n]^(1/2). Setup: gfr values of 211 kidney patients, with mean 54.25 and a plug-in standard error of 0.95. The delta method is a first-order Taylor expansion, var{s(theta-hat)} about |s'(mu)|^2 sigma^2; for xbar squared the standard error is about 2|xbar| times that of xbar. For statistics with no such formula (the 25% Winsorized mean, the median 52.24) they turn to the bootstrap with B = 1000: standard errors .78 and .87. They state that frequentist correctness does not say which statistic to use.

Chapter 1 frames the same split: the average is the algorithm, and its standard error, taken from the same data, is the inference about how accurate it is. Setup: kidney data, 157 volunteers, tot against age. The linear fit's standard errors at ages 20 to 80 run from .21 at age 20 (smallest, .15, at ages 30 to 40) to .42 at age 80, and their plus-or-minus 2 bars give about 95% coverage only if the linear model is valid. Bootstrap standard errors for a lowess curve on the same data (resampling the 157 pairs, 250 replications) come out roughly double, which the chapter calls the price of flexibility.

## Limits

- CASI ch. 1 checks the 95% coverage claim on one dataset only, and the claim holds only if the linear model is valid.
- CASI ch. 2: frequentist correctness does not say which statistic to use, and the authors say their list of devices is not exhaustive.

## See Also
- [[Maximum Likelihood and Estimator Bias]] — prerequisite-for
- [[Independence Pitfalls]] — related
- [[Minimum Detectable Effect and Sample Size]] — related
- [[Ratio Metrics and the Denominator Trap]] — related
- [[Jackknife Standard Error]] — alternative-to
- [[BCa Bootstrap Confidence Intervals]] — alternative-to
