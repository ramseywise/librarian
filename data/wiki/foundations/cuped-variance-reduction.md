---
title: CUPED Variance Reduction
tags: [foundations, pattern]
summary: "CUPED subtracts theta times the centred pre-experiment value of the same metric from each outcome, cutting variance by rho squared without bias because the covariate predates assignment; it equals regression adjustment and fails for new users or weak predictors."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--03-experimentation-at-scale.md
---

# CUPED Variance Reduction

Controlled-experiment Using Pre-Experiment Data removes noise unrelated to the treatment: most variation in a user's activity this month is the kind of user they already were, and last month's activity predicts that. Reported variance reductions on real search metrics were about 50%.

## Mechanism

Replace each outcome Y with Y - theta (X - mean X), where theta = cov(X, Y) / var(X) is the slope of Y on X (a linear control variate). Variance falls by rho squared, the squared correlation.

Simulation (40,000 users, true effect 0.12, rho = 0.702): raw effect 0.101, SE 0.0488, z 2.08; CUPED effect 0.123, SE 0.0348, z 3.53; variance ratio 0.508, which equals 1 - rho squared, so about 51% of the users give the same power. Over 1,500 repeated runs the mean estimate stayed near 0.12 (raw 0.116, CUPED 0.123) while the spread fell from 0.216 to 0.153, about 30% (the square root of the halved variance).

## Properties

- The expected effect is unchanged: randomisation balances the pre-period mean across arms in expectation. A single estimate moves because it corrects chance imbalance.
- It needs a good predictor. At rho 0.3 variance falls only 9%; at rho 0.5 it falls 25%, so you need 75% of the users. New-user products have no pre-period; rare outcomes are hard to predict.
- Users with no history keep their raw value or are adjusted within their own group: with 70% having history, SE was 0.0393 against raw 0.0488 and 0.0348 with full history. Validity is kept, some gain is lost.
- It is identical to regression with the centred pre-period value as a control (effect 0.123, SE 0.0348), the old ANCOVA ([[Regression Covariate Adjustment]]).

## Rules

1. The covariate must be measured strictly before exposure; anything the treatment can touch reintroduces bias.
2. Prefer the same metric from the pre-period.
3. Check that arms agree on the pre-period mean: a gap is evidence of an assignment problem and a free A/A test ([[Sample Ratio Mismatch]]).

Variance reduction lets small effects become affordable ([[Minimum Detectable Effect and Sample Size]]).

## See Also
- [[Regression Covariate Adjustment]] — related (same estimator)
- [[A/B Test Lifecycle and Interval Decisions]] — related
- [[OEC, Guardrails and North Star Metrics]] — related (revenue metrics are noisy)
