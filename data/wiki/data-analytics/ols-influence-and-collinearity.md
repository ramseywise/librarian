---
title: OLS Influence and Collinearity Diagnostics
tags: [data-analytics, probability-and-statistics, concept]
summary: "One high-leverage point can flip a regression slope, flagged by leverage and Cook's distance, while near-duplicate regressors inflate standard errors without hurting prediction, flagged by the variance inflation factor."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--06-regression-and-glms.md
  - data/raw/papers/2026-11-08-practical-statistics-for-data-scientists-ch04-regression-prediction.md
  - data/raw/papers/2026-11-08-islp-ch03-linear-regression.md
  - data/raw/papers/2026-11-08-statistical-rethinking-ch05-multivariate-linear-models.md
---

# OLS Influence and Collinearity Diagnostics

## Influence

A point far out in x has **leverage**; if it also sits off the line it has **influence**, measured by **Cook's distance**. One high-leverage point flipped the fitted slope from 2.02 to -0.18 (leverage 0.55, Cook's D 107). Check leverage before trusting any slope, and look at the point: error, a different population, or a real rare case. Do not delete it silently; report the fit with and without.

## Collinearity

When two regressors move together the model cannot say which one matters. The **variance inflation factor (VIF)** gives how much a coefficient's variance is inflated. With VIF 391 the coefficients were 1.51 and 0.54 with SEs around 0.8, against a solo SE of 0.041. Prediction error was the same (RMSE 0.920).

So collinearity hurts explanation, not prediction: if you need to interpret a coefficient, drop or combine near-duplicates; if you only predict, ignore it.

## Book example: King County house sales

Chapter 4 of *Practical Statistics for Data Scientists* (R, King County sales, zip code 98105 for the influence work) shows the same ideas on housing data. The largest outlier there has a standardized residual of -4.33, an overestimate of $757,753, from a partial-interest sale. Removing influential points moved the Bathrooms coefficient from 2,282 to -16,132. In the five-predictor model, dropping the bedroom, size and bathroom variables flips the Bedrooms coefficient from negative to positive (27,657); the authors treat this as confounding and advise checking for omitted variables before reading coefficients causally. They advise removing variables until multicollinearity is gone, and observe that with large data a stray outlier seldom changes the fit, though standardized residuals remain useful for flagging anomalies.

## More diagnostics from two books

- VIF is 1 divided by 1 minus the R-squared of a regressor on the others; Introduction to Statistical Learning ch03 gives 5 or 10 as the rule of thumb. On Credit data (balance on age, rating and limit) age scores 1.01 and rating and limit about 160.7 and 160.6. Pairing rating with limit instead of age multiplies the limit standard error by 12 and gives it p = 0.7012, while dropping rating leaves R-squared at 0.75 against 0.754.
- On the Advertising data (200 markets) the VIFs are about 1.0 to 1.15, so collinearity is not what widens the newspaper interval. The newspaper coefficient falls from 0.055 alone (p = 0.00115) to -0.001 with TV and radio (p = 0.8599); the authors read newspaper as a surrogate for radio, with which it correlates 0.35. With 12 Boston predictors the largest VIFs are 9.0 and 7.4.
- Average leverage is always (p+1)/n. In a simulation, one low-leverage outlier raised the residual standard error from 0.77 to 1.09 and cut R-squared to 0.805 from 0.892 with the line hardly shifting; its studentised residual exceeded 6 where -3 to 3 is usual. A high-leverage outlier moved the fit much more.
- Interaction: adding TV by radio to the Advertising model raised R-squared from 89.7% to 96.8% (interaction t-statistic 20.73), and each extra $1,000 of TV is then associated with 19 plus 1.1 times the radio budget in extra units sold, all on the training fit.
- Statistical Rethinking ch05 (first edition) simulates the same collinearity, which the page [[Masked Relationships and Collinear Predictors]] covers. A random predictor with a set correlation r to percent fat is added to a primate-milk regression, 100 least-squares fits at each r, with r running 0 to 0.99 by 0.01 under flat priors. The posterior SD of the slope inflates rapidly once r passes about 0.9 and grows without bound as r approaches 1. The authors read correlations above about 0.9 as a warning.

## Limits

- The chapter uses one dataset in R, its formulas (hat-value and Cook's distance thresholds) were lost in extraction, and it states no dataset size beyond degrees of freedom.
- Introduction to Statistical Learning ch03: R-squared, residual standard error and the VIF material all rest on the training fit; the Credit sample size is not given, the outlier example is simulated, and the F test fails when p exceeds n.
- Statistical Rethinking ch05: the authors say the flat priors in their collinearity simulation exaggerate the SD inflation, and the simulation is one design on one dataset.

## See Also
- [[Regression Covariate Adjustment]] — prerequisite-for
- [[Robust Standard Errors]] — related
- [[Explain vs Predict Modelling]] — related
- [[Robust Summaries for Skewed Metrics]] — related (outliers and robustness)
- [[Masked Relationships and Collinear Predictors]] — related
