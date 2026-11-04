---
title: Model Selection Criteria
tags: [foundations, reference]
summary: "R-squared never rejects extra terms, adjusted R-squared, AIC, BIC, likelihood-ratio tests and cross-validation each trade fit against complexity differently: BIC found a true quadratic 98 percent of the time at n=800, AIC 77 percent."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--07-data-generating-process.md
---

# Model Selection Criteria

| Criterion | Penalises complexity | Note |
|---|---|---|
| R-squared | no | always rises with terms |
| Adjusted R-squared | lightly | weakest selector |
| AIC | 2 per parameter | aims at prediction |
| BIC | log(n) per parameter | favours simpler models as n grows |
| Likelihood-ratio test | by df | for nested models |
| Cross-validation | by held-out error | model-agnostic |

## Choosing between a line and a quadratic

Selection of the true quadratic at n = 800: BIC 0.98, AIC 0.77, CV 0.70, adjusted R-squared 0.39, R-squared never (it always picks the larger model, so it cannot discriminate). AIC and CV keep a fixed surplus-complexity rate, while BIC's log(n) penalty grows, so BIC is pickier with data.

## Perspective

The coefficient of interest hardly moved across flexible forms (0.179 to 0.200); the harm came from leaving the bad form ([[Functional Form Misspecification]]). Selection criteria serve the goal: prediction favours AIC or CV, a sparse explanation BIC ([[Explain vs Predict Modelling]]). Deviance underlies AIC ([[Generalised Linear Models and Deviance]]).

## See Also
- [[Data Generating Process Simulation Check]] — related
- [[Regression Covariate Adjustment]] — related
