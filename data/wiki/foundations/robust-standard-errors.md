---
title: Robust Standard Errors
tags: [foundations, pattern]
summary: "When residual spread changes with the fitted value, classical OLS standard errors are wrong while the coefficients stay fine; HC3 heteroskedasticity-robust errors fix the standard error, not the estimate."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--06-regression-and-glms.md
---

# Robust Standard Errors

Classical OLS standard errors assume constant residual variance. Money and counts rarely oblige.

## Spotting it

Residual spread by fitted-value quintile ran from 11.0 to 31.8 in the example: a funnel on the residual plot.

## The fix

Heteroskedasticity-consistent errors (HC3 is a conservative default for modest n) re-estimate the variance without assuming constancy. The coefficient is unchanged. For the pre-period covariate the SE was 0.0067 classical and 0.0112 HC3, while the randomised treatment term's SE barely moved: randomisation protects the treatment estimate, but covariate inference can be off.

Robust errors repair uncertainty, not a wrong model: if the variance pattern signals a missing term or the wrong form, see [[Functional Form Misspecification]]. They do not handle correlated rows, which need [[Clustered Standard Errors]]. A count with large dispersion has the same cure in [[Poisson Offsets and Overdispersion]].

## See Also
- [[Regression Covariate Adjustment]] — prerequisite-for
- [[OLS Influence and Collinearity Diagnostics]] — related
