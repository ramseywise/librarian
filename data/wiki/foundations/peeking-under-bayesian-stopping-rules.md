---
title: Peeking Under Bayesian Stopping Rules
tags: [foundations, pattern]
summary: "Bayesian tests are not immune to peeking: a daily P(B > A) > 0.95 rule shipped 23.8% of no-effect changes in simulation, and an expected-loss rule ships quickly but needs a minimum sample size to stop harmful launches."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--04-bayesian-analysis--notes--04-bayesian-ab-testing.md
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

## See Also
- [[Bayesian A/B Testing with Expected Loss]] — prerequisite-for
- [[Multiple Comparisons Corrections]] — related
- [[Minimum Detectable Effect and Sample Size]] — related (setting the minimum sample)
