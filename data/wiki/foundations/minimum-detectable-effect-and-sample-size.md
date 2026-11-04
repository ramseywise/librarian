---
title: Minimum Detectable Effect and Sample Size
tags: [foundations, reference]
summary: "Sample size per arm is about 16 sigma squared over delta squared at 5 percent significance and 80 percent power, so halving the detectable effect quadruples the users and small relative lifts on rare outcomes need millions."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--04-estimation.md
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--05-hypothesis-testing.md
---

# Minimum Detectable Effect and Sample Size

## Formula

For a two-arm comparison of means, n per arm = 2 (z_alpha + z_beta)^2 sigma^2 / delta^2. At alpha = 0.05 (two-sided) and 80% power this is about 16 sigma^2/delta^2 (exact multiplier 15.7). Decide the **minimum detectable effect** delta (the smallest change worth acting on) before the test, then solve for n; or fix n and read off the MDE.

## Worked numbers

| Metric | Setup | n per arm |
|---|---|---|
| Revenue per user | sd 30, mean 3.75, 5% relative lift | 401,863 |
| Conversion | p = 0.05, 5% relative lift | 119,303 |
| Conversion | p = 0.05, 1% relative lift | about 3 million |

Halving the effect needs four times the users, so relative lifts of a percent on rare outcomes are out of reach for most products. Noisy metrics (revenue, sd many times the mean) need far more than proportions.

## Practical points

- Power is the chance of detecting a real effect of size delta; underpowered tests miss real effects and the "significant" ones they find are exaggerated ([[Winner's Curse]]).
- Fix n in advance; peeking and stopping early inflates false positives ([[Multiple Comparisons Corrections]]).
- Covariate adjustment lowers sigma and so n ([[Regression Covariate Adjustment]]); clustered assignment raises it ([[Clustered Standard Errors]]).
- The 1/sqrt(n) scaling is the same one behind [[CLT on Heavy-Tailed Metrics]] and [[Eval Error Bars and Sample Size]].

## See Also
- [[P-Value Misreadings]] — related (a huge n makes tiny lifts significant)
- [[Delta Method for Ratio Metrics]] — related
- [[Confidence Interval Coverage and Wilson]] — related
