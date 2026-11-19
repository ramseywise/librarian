---
title: Covariance Penalty Estimates of Prediction Error
tags: [data-analytics, probability-and-statistics, concept]
summary: "Apparent error understates true prediction error by twice the covariance between each fit and its observation; Cp, AIC, SURE and a bootstrap penalty estimate that term from a model, while cross-validation estimates the average error of the algorithm without one."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch12-cross-validation-cp-estimates-prediction.md
---

# Covariance Penalty Estimates of Prediction Error

Efron and Hastie (Computer Age Statistical Inference, ch. 12) ask how to estimate the accuracy of a chosen prediction rule, either without a model (cross-validation) or with one (covariance penalties). Apparent error is the average training-set discrepancy between each response and its prediction; true error is the expected discrepancy on a new pair drawn independently of the training data.

## The covariance penalty

The expected true error at case i equals the expected apparent error plus 2 cov(fit_i, y_i). Mallows Cp, AIC, SURE (Stein's unbiased risk estimate) and a bootstrap penalty are four ways to estimate that covariance. Under normality SURE replaces the covariance by sigma^2 times the derivative of the fit with respect to y_i, and the general degrees of freedom is given as (1/sigma^2) times the summed covariances, divided by 2, as printed in eq 12.53. The bootstrap version averages (fit deviation)(y deviation) over parametric replications.

Worked numbers (supernova data, N = 39, sigma^2 = 1, 10 predictors, OLS without intercept): apparent error 0.719 plus penalty 0.513 gives a Cp estimate of 1.23. A lasso fit with 7 nonzero coefficients has penalty 2*7/39 = 0.359 and a Cp estimate of 1.08, which ignores that the 7 was chosen from the data. Bootstrap degrees of freedom for that lasso rule were 6.85 with p fixed at 7 and 7.48 with p chosen adaptively (B = 1000 each), so selection cost about 0.6 degrees of freedom. On kidney data (N = 157), lowess with span 1/3 had SURE degrees of freedom 6.67 against 6.81 from a parametric bootstrap (B = 1000, sigma^2 = 3.28); the bootstrap penalty 0.284 raised error by about 9% over the apparent 3.15.

## Cross-validation compared

Setup: lasso with lambda picked by Cp, 39 supernovas, 13 random groups of 3, squared error. Cross-validated error came out 62% above the apparent 0.72, and R^2 dropped from an apparent 0.816 to 0.701. Over 500 bootstrap simulations from those 39 pairs, the average cross-validated error (1.07) sat near the average true error (1.02), and both exceeded the average apparent error (0.57) by about 80%. Per case, cross-validated and true errors were only weakly correlated (0.175 in the table, though the text says negatively and the extraction cannot confirm the sign); the authors read this as cross-validation estimating how the algorithm does on average rather than how the fitted rule does.

Setup: spam data, N = 4061, 57 predictors, logistic regression, 10 groups. Classification error rose under cross-validation from 0.064 to 0.069. A glmnet lasso sequence had its lowest cross-validated error, 0.067, at 47 predictors.

Efron and Hastie advise grouped 10-fold cross-validation (optionally averaged over several splits) over leave-one-out for discontinuous rules, and prefer covariance penalties to cross-validation whenever a believable parametric model exists. The .632 rule, reported in an endnote, blends out-of-bootstrap error with apparent error at weights 0.632 and 0.368, since a bootstrap replicate omits about 0.368 of the cases.

## Ephemeral predictors

Predictors whose power fades over time make a randomly drawn validation set overoptimistic. Setup: simulated microarray study, 360 subjects, 100 genes, Random Forests, transient episodes of about 30 days. Random days gave 15% test error, but days following the training period gave 27%; under a random split both the test error and the cross-validated training error fell toward 15% as the forest grew. The authors advise validating on data well separated in time or location, using blocked folds.

## Limits

- Cross-validated error estimates the algorithm's average error, not the error of the fitted rule.
- Choosing the rule with the lowest cross-validated error is not itself cross-validated, which makes that minimum optimistic.
- The factor 1/2 in the degrees-of-freedom formula (12.53) is reproduced as printed and may not match the usual definition.
- Covariance penalties need a probability model and the chapter assumes sigma^2 known.
- The extraction's text layer lost minus signs, so Table 12.1, the episode means in eq 12.84 and whether the 0.175 correlation is negative cannot be confirmed.

## See Also
- [[Model Selection Criteria]] — prerequisite-for
- [[Cross-Validation Variants and Nested Search]] — alternative-to
- [[Bias-Variance Decomposition and Model Complexity]] — prerequisite-for
- [[Bootstrap Resampling and Its Failures]] — related (the resampling behind the bootstrap penalty)
