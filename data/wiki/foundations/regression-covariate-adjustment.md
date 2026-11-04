---
title: Regression Covariate Adjustment
tags: [foundations, pattern]
summary: "OLS on a treatment dummy reproduces the t-test, and adding pre-assignment covariates shrinks the standard error without biasing a randomised estimate, while adding post-treatment or omitting confounders in observational data changes the answer entirely."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--06-regression-and-glms.md
---

# Regression Covariate Adjustment

## A t-test is a regression

OLS of the outcome on a 0/1 treatment dummy returns the difference in means as its coefficient with the same t-statistic (difference 1.350, t = 3.942 in the example). Regression is the general form; the covariates are the extension.

## Randomised data: adjust for precision

Adding a pre-period measure of the outcome cut the treatment SE from 0.343 to 0.287 (R-squared 0.299, about 30% of residual variance removed) and did not move the estimate beyond noise. Randomisation makes treatment independent of covariates, so adjustment only reduces variance. Rules: use covariates fixed **before** assignment; never adjust for anything affected by treatment.

## Observational data: adjust to remove bias

An omitted confounder biases the coefficient. In a simulation with a true effect of 0, the coefficient was 5.69 without the confounder and 0.08 with it. Adjustment here is not an optional precision gain, and it only works for confounders you measured.

## Interactions and subgroups

Testing whether the effect differs by segment uses interaction terms. In the example the interactions were jointly not significant (p = 0.396), and the device variable explained only about 0.5% of variance (SE about 0.342). Slicing into subgroups multiplies tests ([[Multiple Comparisons Corrections]]) and shrinks N ([[Small-N Trap and Shrinkage]]).

## Next checks

After fitting: heteroskedasticity ([[Robust Standard Errors]]), grouped rows ([[Clustered Standard Errors]]), influential points and collinearity ([[OLS Influence and Collinearity Diagnostics]]), and whether the functional form is right ([[Functional Form Misspecification]]).

## See Also
- [[Statistical Test Selection]] — related (ANOVA and t-tests are regressions)
- [[Minimum Detectable Effect and Sample Size]] — related (adjustment lowers required n)
- [[Explain vs Predict Modelling]] — related
- [[CUPED Variance Reduction]] — related (the pre-period covariate case)
