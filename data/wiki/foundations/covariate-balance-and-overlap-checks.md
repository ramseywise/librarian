---
title: Covariate Balance and Overlap Checks
tags: [foundations, pattern]
summary: "Before reading any outcome, check that treated and comparison groups are comparable using standardised mean differences, variance ratios and propensity overlap; fix the design on balance alone, and report the effective sample size since 5,710 weighted controls were worth 107."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--05-matching-and-weighting.md
---

# Covariate Balance and Overlap Checks

Separate design from analysis: until the groups look comparable there is no reason to read the outcome, and not having read it, you cannot tune the design towards the answer you want.

## Measures

- Standardised mean difference (SMD): treated mean minus control mean over the treated standard deviation. Unlike a t-test it does not grow with the sample size, so it measures imbalance, not n.
- Variance ratio: treated over control variance; groups can share a mean and differ in shape.
- Guideline: regression adjustment is trusted when absolute SMD is below 0.25 and the variance ratio lies in 0.5 to 2. Stricter designs use 0.1. In a club-membership table, 9 of 10 covariates failed on SMD and 4 on variance ratio before adjustment, so regression would extrapolate (log prior orders SMD 1.00, variance ratio 5.02).
- Plot SMDs before and after adjustment per design (a Love plot).

## Overlap and common support

Fit the propensity score (probability of treatment given covariates, logistic regression) and compare its distribution by group. Matching and weighting can compare only people who could have gone either way. In the example 970 treated units scored above 0.9 against only 40 controls: any method keeping all treated must lean hard on those 40, and any that does not must drop treated units and change the question. When restricting, describe who is left with real variables, not scores.

## Effective sample size

(sum of weights) squared over sum of squared weights is how many equally weighted units the weights are worth. Report it with the largest weight share. Example controls: 5,710 used under propensity weights were worth 107 with one control holding 8.6% of weight; entropy balancing's were worth 267; CEM's 1,106.

## Limits

Balance covers observed covariates only. A perfect Love plot left the estimate about 3.60 pounds high, and imbalance on the unlogged trait rose from 0.29 to 0.48 SD after balancing the logged history ([[Sensitivity Analysis for Unmeasured Confounding]]).

## See Also
- [[Matching and Weighting Estimators]] — prerequisite-for
- [[Potential Outcomes and Selection Bias]] — extends
- [[Entropy Balancing]] — related
