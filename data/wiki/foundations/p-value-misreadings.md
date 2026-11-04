---
title: P-Value Misreadings
tags: [foundations, concept]
summary: "A p-value is the chance of data at least this extreme if the null were true, not the chance the null is true, not an effect size, and not evidence of no effect when large; with millions of users a negligible lift is highly significant."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--05-hypothesis-testing.md
---

# P-Value Misreadings

## The recipe

State H0 (no effect) and H1, fix alpha, choose a test statistic, compute the **p-value** (probability of a statistic at least this extreme if H0 holds), then decide. Under a true null the p-value is uniform on [0, 1], so 5% of true nulls are "significant" by construction.

## Four misreadings

1. **p is not P(H0 is true).** Turning one into the other needs a prior and base rates ([[Bayes Rule and the Base Rate Fallacy]]).
2. **A large p does not mean no effect.** p = 0.2 means the data are compatible with zero, not that zero is established; look at the interval and power ([[Minimum Detectable Effect and Sample Size]]).
3. **A tiny p does not mean a big effect.** With 5 million users per arm a lift of 0.0004 (0.9% relative) gave p = 2.9e-3. Significance measures detectability; size is the estimate.
4. **The difference between significant and not significant is not itself significant.** p < 0.05 in one study and p > 0.05 in another does not show they disagree; test the difference directly.

## Pairing matters

The same data gave p = 0.0004 when analysed as paired and 0.33 unpaired. Using the test that matches the design is not optional ([[Statistical Test Selection]]).

## Defaults for reporting

Report the estimate and its interval, not just the verdict. Significant results from underpowered tests are inflated ([[Winner's Curse]]), and running many tests breaks the nominal alpha ([[Multiple Comparisons Corrections]]). A [[Permutation Test]] shows the null distribution the p-value refers to.

## See Also
- [[Confidence Interval Coverage and Wilson]] — related
- [[Data Defect Correlation]] — related (a tiny p on selected data is still wrong)
- [[Eval Error Bars and Sample Size]] — related
