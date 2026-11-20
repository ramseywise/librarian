---
title: "Bias-Variance Decomposition and Model Complexity"
tags: [data-science, classical-ml, concept]
summary: "Expected squared error splits into bias squared, variance and irreducible noise; complexity trades the first two, and the symptom table says which side to fix."
updated: 2026-11-20
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--01-statistical-foundations.md
  - data/raw/papers/2026-11-08-islp-ch02-statistical-learning.md
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

## Classification: Bayes error and K-nearest neighbours

ISLP's Chapter 2 calls a fit overfit when training MSE is low but test MSE is high and a simpler model would have scored better on test data; training MSE usually sits below test MSE even when nothing is overfit. Expected test MSE at a point x0 is the variance of the fitted function at x0, plus its squared bias, plus Var(eps), so it cannot fall below Var(eps); the book states the decomposition without proof. On three simulated regression sets (moderately non-linear, near-linear and highly non-linear truth) training MSE fell with flexibility while test MSE was U-shaped, and the best flexibility depended on how linear the truth was.

For classification the counterpart of irreducible error is the Bayes error rate (one minus the expected largest class probability given X), the floor on test error for any classifier; the Bayes classifier picks, for each observation, whichever class has the highest conditional probability. K-nearest neighbours estimates that probability as the share of the K nearest training points in each class. On the book's simulated two-class data (Fig 2.13) the Bayes error rate is above zero because the classes overlap. KNN with K=10 had a test error close to it, K=1 overfitted and K=100 underfitted. In Fig 2.17 (200 training observations, 5,000 test observations) training error was 0 at K=1 and test error traced a U against 1/K, bottoming out around K=10, and the noisy curves reflect the small training set.

## Limits

- ISLP states the decomposition and the optimality of the Bayes classifier without proof, and all of its error curves come from simulated data.
- The Fig 2.13 Bayes error rate appears as 0.133 on one page and 0.1304 on the next.
- ISLP notes that with f unknown neither bias nor variance can be calculated, so the trade-off is a guide to choosing flexibility, not a number to read off.

## See Also
- [[Train, Validation and Test Discipline]] — extends
- [[Regularisation as a Prior]] — related
- [[Explain vs Predict Modelling]] — related
- [[Maximum Likelihood and Estimator Bias]] — related (the same split on a single estimator)
- [[Soft Inductive Bias, Benign Overfitting and Double Descent]] — extends
- [[Covariance Penalty Estimates of Prediction Error]] — related
