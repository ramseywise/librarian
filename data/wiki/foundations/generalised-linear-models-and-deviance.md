---
title: Generalised Linear Models and Deviance
tags: [foundations, concept]
summary: "A GLM pairs a distribution with a link function and is fitted by maximum likelihood; deviance replaces the sum of squares for comparing models, while Pearson dispersion is the better check of the variance assumption."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--06-regression-and-glms.md
---

# Generalised Linear Models and Deviance

| Model | Outcome | Link | Coefficient reads as |
|---|---|---|---|
| Linear | continuous | identity | change in mean |
| Logistic | binary | logit | log odds ratio |
| Poisson | count | log | log rate ratio |
| Negative binomial | overdispersed count | log | log rate ratio |

The choice follows the outcome's distribution ([[Distribution Selection for Metrics]]).

## Deviance

Twice the log-likelihood gap between the fitted model and a **saturated** model (one parameter per row). Maximum likelihood is least total deviance as OLS is least squares. **Null deviance** is for an intercept-only model; **residual deviance** is for yours; the drop plays the explained sum of squares' role and for nested models is the likelihood-ratio statistic (chi-square, one df per added term).

Example: 5482.5 null against 5450.1 residual, a drop of 32.4 for one df, agreeing with the coefficient's z-test (p = 1.2e-8). Only about 0.6% of deviance went, as a small R-squared can accompany a clear effect.

## Check variance with Pearson, compare with deviance

Residual deviance per df was 1.09 where Pearson dispersion was 1.00 on truly Poisson data: with small counts deviance misleads about variance. Use Pearson dispersion for that check ([[Poisson Offsets and Overdispersion]]), deviance for comparing models.

## See Also
- [[Logistic Regression Odds Ratios vs Marginal Effects]] — instance-of
- [[Logistic Regression Separation]] — related
- [[Maximum Likelihood and Estimator Bias]] — prerequisite-for
- [[Model Selection Criteria]] — related
