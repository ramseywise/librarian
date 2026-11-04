---
title: OLS Influence and Collinearity Diagnostics
tags: [foundations, concept]
summary: "One high-leverage point can flip a regression slope, flagged by leverage and Cook's distance, while near-duplicate regressors inflate standard errors without hurting prediction, flagged by the variance inflation factor."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--06-regression-and-glms.md
---

# OLS Influence and Collinearity Diagnostics

## Influence

A point far out in x has **leverage**; if it also sits off the line it has **influence**, measured by **Cook's distance**. One high-leverage point flipped the fitted slope from 2.02 to -0.18 (leverage 0.55, Cook's D 107). Check leverage before trusting any slope, and look at the point: error, a different population, or a real rare case. Do not delete it silently; report the fit with and without.

## Collinearity

When two regressors move together the model cannot say which one matters. The **variance inflation factor (VIF)** gives how much a coefficient's variance is inflated. With VIF 391 the coefficients were 1.51 and 0.54 with SEs around 0.8, against a solo SE of 0.041. Prediction error was the same (RMSE 0.920).

So collinearity hurts explanation, not prediction: if you need to interpret a coefficient, drop or combine near-duplicates; if you only predict, ignore it.

## See Also
- [[Regression Covariate Adjustment]] — prerequisite-for
- [[Robust Standard Errors]] — related
- [[Explain vs Predict Modelling]] — related
- [[Robust Summaries for Skewed Metrics]] — related (outliers and robustness)
