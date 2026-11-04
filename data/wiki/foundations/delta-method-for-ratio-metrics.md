---
title: Delta Method for Ratio Metrics
tags: [foundations, pattern]
summary: "A ratio of two per-user totals, such as revenue per session, needs a standard error that accounts for numerator and denominator co-varying; computing it as if sessions were the independent units understates it by about 40 percent."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--04-estimation.md
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

## See Also
- [[Maximum Likelihood and Estimator Bias]] — prerequisite-for
- [[Independence Pitfalls]] — related
- [[Minimum Detectable Effect and Sample Size]] — related
