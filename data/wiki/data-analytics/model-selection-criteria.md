---
title: Model Selection Criteria
tags: [data-analytics, probability-and-statistics, reference]
summary: "R-squared never rejects extra terms, adjusted R-squared, AIC, BIC, likelihood-ratio tests and cross-validation each trade fit against complexity differently: BIC found a true quadratic 98 percent of the time at n=800, AIC 77 percent."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--07-data-generating-process.md
  - data/raw/papers/2026-11-08-islp-ch06-linear-model-selection-regularization.md
  - data/raw/papers/2026-11-08-islp-ch03-linear-regression.md
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

## Subset selection in ISLP

ISLP's Chapter 6 uses the Credit data (10 predictors, 11 with dummies) to compare criteria for the best model of each size, with Cp = (RSS + 2 d sigma2-hat)/n and BIC replaces the 2 in Cp's penalty with log(n), both scaled by 1/n and up to constants. Cp picked six variables (income, limit, rating, cards, age, student), BIC the four-variable one (income, limit, cards, student), and adjusted R-squared a seven-variable model (the Cp model plus own). The BIC penalty is heavier than Cp's when n is above 7. A three-quarters-train validation split and 10-fold CV each settled on six variables, while the one-standard-error rule (the smallest model whose estimated test error is within one standard error of the lowest point) chose three. On Credit, best-subset and forward stepwise selection agree for one to three variables and differ at four (cards against limit).

Best subset needs 2^20 = 1,048,576 fits for p = 20 where forward stepwise needs 1 + p(p+1)/2 = 211, and the authors call best subset infeasible above about p = 40. In ISLP's Hitters lab, forward selection by Cp chose 10 variables, while the default MSE scoring chose all 19. Chapter 3 outlines forward, backward and mixed selection (forward steps that also drop a variable once its p-value climbs past a cutoff); backward selection cannot be used when p > n.

The authors advise CV over Cp, AIC, BIC and adjusted R-squared now that compute is cheap, because it needs no estimate of sigma2 or of degrees of freedom. When selection is combined with CV, the whole selection is redone inside each training fold. Cp, AIC, BIC and adjusted R-squared break down when p >= n, since the variance estimate comes out as 0 there, and in high dimensions training SSE, p-values and R-squared should not be reported as evidence of fit.

## Limits

- ISLP concedes that the justifications for Cp, AIC and BIC are asymptotic and beyond the book's scope, and that adjusted R-squared is less well motivated in theory.
- The Hitters lab's 5-fold CV standard error is only a rough guide, as the folds' training sets share data.

## See Also
- [[Data Generating Process Simulation Check]] — related
- [[Regression Covariate Adjustment]] — related
- [[Stepwise Selection and Overfitting on Noise]] — extends
- [[Covariance Penalty Estimates of Prediction Error]] — extends
- [[Regression Splines, Smoothing Splines and GAMs]] — related
- [[WAIC, KL Divergence and Akaike Weights]] — extends
