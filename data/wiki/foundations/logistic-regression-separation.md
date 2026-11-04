---
title: Logistic Regression Separation
tags: [foundations, pattern]
summary: "When a feature perfectly predicts the outcome, maximum likelihood diverges, giving a huge coefficient and an absurd standard error; a penalty or weakly informative prior stabilises it."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--06-regression-and-glms.md
---

# Logistic Regression Separation

If some value of a regressor always occurs with one outcome, the likelihood keeps improving as the coefficient grows, so the fit has no finite maximum. Symptoms: coefficient 28.52 with SE 171,433 in the example, a warning from the optimiser, and a meaningless p-value.

## Fixes

- A **ridge penalty**: coefficient 4.92 in the example, finite and usable.
- A weakly informative prior does the same job from a Bayesian side.
- Collapse or drop the categories involved (and ask whether the perfect prediction is a leak).

Never read the unpenalised coefficient: the optimiser has stopped, not found an answer. The likelihood basis is in [[Maximum Likelihood and Estimator Bias]]; the odds-ratio reading in [[Logistic Regression Odds Ratios vs Marginal Effects]].

## See Also
- [[Generalised Linear Models and Deviance]] — related
- [[Small-N Trap and Shrinkage]] — related (shrinkage as a stabiliser)
