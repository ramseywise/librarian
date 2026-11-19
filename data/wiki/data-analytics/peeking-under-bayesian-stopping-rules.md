---
title: Peeking Under Bayesian Stopping Rules
tags: [data-analytics, bayesian-analysis, pattern]
summary: "Bayesian tests are not immune to peeking: a daily P(B > A) > 0.95 rule shipped 23.8% of no-effect changes in simulation, and an expected-loss rule ships quickly but needs a minimum sample size to stop harmful launches."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--04-bayesian-analysis--notes--04-bayesian-ab-testing.md
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch03-bayesian-inference.md
---

# Peeking Under Bayesian Stopping Rules

The posterior is a valid summary at any N, and it is often claimed that this makes peeking free. A simulation tests the claim: 30 days at 500 visitors per arm per day, a 5% base rate, 4,000 simulated tests per row, Normal approximations to the posteriors.

| Rule | Ships no-effect | Ships -0.5 points | Ships +1 point (mean day) |
|---|---|---|---|
| P(B > A) > 0.95, last day only | 0.047 | 0.000 | 0.987 (30.0) |
| P(B > A) > 0.95, checked daily | 0.238 | 0.046 | 0.995 (6.2) |
| Expected loss < 0.05 points, daily | 0.589 | 0.143 | 1.000 (3.9) |
| Expected loss < 0.05 points, from day 14 | 0.482 | 0.038 | 1.000 (14.1) |

## Reading the table

- Rows 1 versus 2: with a flat prior the threshold is close to a one-sided p < 0.05, so checking once gives the familiar 4.7%. Checking daily inflates it to 23.8%, in line with repeated-look inflation of about 25% over twenty looks (see [[P-Value Misreadings]]). The posterior is calibrated on average over the prior, not when the effect is fixed at zero; taking the first favourable look still selects on noise.
- Row 3: shipping a no-effect change costs nothing, so the expected-loss rule has no reason to resist it. The column that matters is -0.5 points: 14.3% of harmful changes shipped, because early posteriors are wide and a lucky start can make expected loss look small.
- Row 4: a minimum sample size cuts harmful shipping to 3.8%, about what the daily probability rule manages, while real wins still ship essentially always. Full weeks also absorb day-of-week effects.

Tightening epsilon to 0.01 points (from 0.05) on the daily row cut no-effect shipping from 0.589 to 0.251 and harmful shipping from 0.143 to 0.028, with real wins at 0.997.

## Rule of thumb

An expected-loss threshold, a minimum sample size set in advance, and full weeks. Never describe the test as immune to peeking. The figures depend on effect sizes, traffic and epsilon: rerun the simulation with your own (see [[Multiple Comparisons Corrections]] for the frequentist side).

## The likelihood-principle view

Efron and Hastie (*Computer Age Statistical Inference*, ch. 3) give the frequentist side of the same issue. Setup: one N(theta, 1) observation a month for up to 30 months, testing theta = 0, and declaring significance if either the month-20 or month-30 statistic tops 1.645. The type I error is 0.074 rather than 0.05, yet the Bayesian posterior is unaffected because the likelihood is the same; the data had Z20 = 0.79 and Z30 = 1.66. They make a related claim that selection of the winner among many estimates leaves the likelihood unchanged, with the burden moving to a genuine prior. Their prostate example (6033 genes, 52 patients and 50 controls, largest statistic 5.29): a flat prior gives 5.29, while an empirical Bayes uninformative prior gives 4.11. The authors caution this needs a real prior. The table above shows that a posterior-threshold rule still ships no-effect changes when checked daily.

## Limits

- CASI ch. 3 is expository; the authors concede some subjectivity without real prior information, and that Bayesian immunity to selection bias needs caution with uninformative priors.

## See Also
- [[Bayesian A/B Testing with Expected Loss]] — prerequisite-for
- [[Multiple Comparisons Corrections]] — related
- [[Minimum Detectable Effect and Sample Size]] — related (setting the minimum sample)
