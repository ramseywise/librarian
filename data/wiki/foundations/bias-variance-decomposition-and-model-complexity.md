---
title: "Bias-Variance Decomposition and Model Complexity"
tags: [foundations, concept]
summary: "Expected squared error splits into bias squared, variance and irreducible noise; complexity trades the first two, and the symptom table says which side to fix."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--01-statistical-foundations.md
---

# Bias-Variance Decomposition and Model Complexity

A model estimates `f` in `y = f(x) + noise`. Learning picks an estimate from a family of functions; generalisation is how close that estimate stays to `f` on new `x`. Expected squared error at a point decomposes into three parts:

- **Bias squared**: the model family is too simple (a line through a curve).
- **Variance**: the fit depends on which samples were drawn (a high-degree polynomial through few points).
- **Irreducible error**: noise in `y` itself; no model removes it.

Raising complexity trades bias for variance, so test error is U-shaped. The target is the bottom of the U.

## Seeing it in a simulation

Only a simulation with a known truth shows the split. Setup: `f(x) = sin(2*pi*x)`, noise standard deviation 0.3 (irreducible variance 0.09), 30 points per training set, 200 training sets, polynomial degree as the complexity knob.

| Degree | Bias squared | Variance | Test MSE |
|---|---|---|---|
| 1 | 0.157 | 0.021 | 0.268 |
| 3 | 0.003 | 0.013 | 0.106 |
| 5 | 0.000 | 0.025 | 0.115 |
| 7 | 0.001 | 0.196 | 0.287 |
| 9 | 0.010 | 17.864 | 17.963 |

The line is all bias; degrees 3 to 5 are the sweet spot; at degree 9 the average fit is still near the truth but any single fit swings wildly. With 300 points per set instead of 30, variance at degree 9 collapses (17.9 to 0.003) while bias barely moves, so degree 5 becomes best and degrees 7 and 9 nearly as good. The right complexity depends on data size: more varied data supports a more complex model, and collecting data often beats a cleverer model.

## Diagnosing from train and test scores

| Symptom | Train | Test | Diagnosis | Fix |
|---|---|---|---|---|
| Underfitting | Low | Low, near train | High bias | More features, more flexible model, less regularisation |
| Overfitting | High | Much lower | High variance | More data, simpler model, more regularisation, early stopping |
| Good fit | High | Close to train | none | Stop tuning; check the test set once |

A bigger model fixes bias only. If train rises while test falls, it is variance. If the test score stops improving under any model or feature, the floor may be irreducible noise; estimate it (repeat labels, human agreement) before tuning further.

## Regularisation

Regularisation is any constraint pulling the fit toward simplicity: an L2 penalty (ridge), an L1 penalty (lasso, which also zeros features), a depth cap, a minimum neighbour count. Ridge is the MAP estimate under a Gaussian prior on weights and lasso under a Laplace prior; see [[Regularisation as a Prior]].

## Explaining versus predicting

Explanatory modelling focuses on minimising bias; predictive modelling on bias and variance together, so a "wrong" model can sometimes predict better than the correct one. See [[Explain vs Predict Modelling]].

## See Also
- [[Train, Validation and Test Discipline]] — extends
- [[Regularisation as a Prior]] — related
- [[Explain vs Predict Modelling]] — related
- [[Maximum Likelihood and Estimator Bias]] — related (the same split on a single estimator)
