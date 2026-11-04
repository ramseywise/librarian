---
title: Explain vs Predict Modelling
tags: [foundations, concept]
summary: "Explanation wants low bias on a coefficient and prediction wants low total error, so a wrong simple model can win held-out error at small n while the true form wins at large n; say which goal comes first."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--07-data-generating-process.md
---

# Explain vs Predict Modelling

Explanation wants an unbiased coefficient; prediction wants small total error (bias plus variance). They pull apart.

## Small n favours wrong-but-simple

A wrong short model beat the true form on held-out error in 78% of datasets at n = 30; at n = 3,000 the true form won 81% of the time. Even then the gain was about 2%. Predictive accuracy is a weak guide to the truth.

## Rashomon

Many models fit equally well and tell different stories. A good fit does not identify mechanism ([[Model Selection Criteria]]).

## Selection into the sample

A model fit on an opt-in-on-segment sample had R-squared 0.774 against a population RMSE of 2.461. Selecting on a regressor does little harm to the slope; selecting on the outcome or unmeasured drivers does ([[Data Defect Correlation]], [[External Validity and Transportability]]).

## Rule

State the goal first. Collinearity ([[OLS Influence and Collinearity Diagnostics]]) harms the explanation, not the prediction.

## See Also
- [[Functional Form Misspecification]] — related
- [[Regression Covariate Adjustment]] — related
