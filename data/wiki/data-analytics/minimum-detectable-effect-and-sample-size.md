---
title: Minimum Detectable Effect and Sample Size
tags: [data-analytics, experimentation-and-causality, reference]
summary: "Sample size per arm is about 16 sigma squared over delta squared at 5 percent significance and 80 percent power, so halving the detectable effect quadruples the users and small relative lifts on rare outcomes need millions."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--04-estimation.md
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--05-hypothesis-testing.md
  - data/raw/papers/2026-11-08-statistics-done-wrong-ch02-statistical-power-underpowered-statistics.md
  - data/raw/papers/2026-11-08-2017-08-kddmetricinterpretationpitfalls.md
  - data/raw/papers/2026-11-08-practical-statistics-for-data-scientists-ch03-statistical-experiments-significan.md
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

## Reinhart's examples (chapter 2)

- Fair coin, 100 flips: 40 to 60 heads occur 95% of the time, so a coin with true heads probability 0.6 is detected with power 0.5 at p < 0.05. At 1,000 flips the fair-coin range is 469 to 531 and power against 60% is near 1.
- For a heart attack trial whose treatment would halve death risk from 20% to 10%, 80% power takes 400 patients (reported). Power of 0.8 or more is what he says scientists usually accept.
- Cited: under 3% of Science and Nature articles work out power beforehand; Cohen's 1960 review of a psychology journal put average power for medium effects (0.5 SD) at 0.48.
- If no formula gives power, simulate many datasets containing the expected effect; power is the share that come out significant. For measuring an effect to a chosen precision he suggests assurance (AIPE) instead, available for only some tests by his account.
- Right-turn-on-red: a Virginia before-and-after study at 20 intersections (308 accidents, then 337) was insignificant, though later studies found about 20% more collisions.

## Other cited cases

- A Microsoft pitfalls paper reports an MSN.com experiment on total page views per user: a +0.5% change was not significant, only a change of 7.8% or more was detectable at 80% power, and the interval was about +-5%. It advises an a priori power analysis for key and guardrail metrics aiming for at least 80% power, and not reading an underpowered non-significant metric as no change.
- Practical Statistics for Data Scientists illustrates with simulated click boxes at a 1.1% baseline click rate: a 10% lift (to 1.21%) cannot be seen from 300 draws per group, and even a 50% lift calls for several thousand impressions (a single draw; power not computed). For rates under 1% it recommends judging sample size by how many rare events (conversions) occur, not by total rows.

## Practical points

- Power is the chance of detecting a real effect of size delta; underpowered tests miss real effects and the "significant" ones they find are exaggerated ([[Winner's Curse]]).
- Fix n in advance; peeking and stopping early inflates false positives ([[Multiple Comparisons Corrections]]).
- Covariate adjustment lowers sigma and so n ([[Regression Covariate Adjustment]]); clustered assignment raises it ([[Clustered Standard Errors]]).
- The 1/sqrt(n) scaling is the same one behind [[CLT on Heavy-Tailed Metrics]] and [[Eval Error Bars and Sample Size]].

## Limits

- Reinhart's chapter 2 is a popular exposition, and its figures come from endnotes not in the extract.
- He notes accuracy-in-parameter-estimation (AIPE) exists for only some tests and is not widely adopted.
- The KDD pitfalls paper's examples are single Microsoft experiments, and experiment sizes and durations are mostly not given.
- Practical Statistics ch. 3 uses hypothetical single-run examples with no power curves, and it gives no general sample-size rule.

## See Also
- [[P-Value Misreadings]] — related (a huge n makes tiny lifts significant)
- [[Delta Method for Ratio Metrics]] — related
- [[Confidence Interval Coverage and Wilson]] — related
- [[A/B Test Lifecycle and Interval Decisions]] — related (the full test pipeline this sizing sits in)
