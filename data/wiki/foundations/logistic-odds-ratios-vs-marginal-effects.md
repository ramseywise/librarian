---
title: Logistic Regression Odds Ratios vs Marginal Effects
tags: [foundations, concept]
summary: "A logistic coefficient is a change in log-odds; exponentiating gives an odds ratio, but the change in probability depends on the starting rate, so report average marginal effects for business impact."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--06-regression-and-glms.md
---

# Logistic Regression Odds Ratios vs Marginal Effects

Logistic regression is linear on the log-odds scale: coefficient beta means log-odds shifts by beta per unit.

- **Odds ratio:** exp(beta). In the example exp(coef) gave 1.132, odds 13% higher.
- **Marginal effect:** change in probability. The **average marginal effect** was 0.0086 against a base conversion of 7.6%, a tiny absolute move that an odds ratio of 1.13 does not convey.

The same coefficient gives different probability changes by baseline: beta = 0.4 is about +0.010 at a 2% base and +0.099 at 50%. Quick rule: at mid-range probabilities the slope is about beta/4 (the divide-by-4 rule).

Use the odds ratio when comparing across studies, the marginal effect when sizing what changes. The model family and link belong to [[Generalised Linear Models and Deviance]]. Perfect predictors break it ([[Logistic Regression Separation]]).

## See Also
- [[Regression Covariate Adjustment]] — related
- [[Maximum Likelihood and Estimator Bias]] — prerequisite-for
