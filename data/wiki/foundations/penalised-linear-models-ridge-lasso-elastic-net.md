---
title: "Penalised Linear Models: Ridge, Lasso and Elastic Net"
tags: [foundations, concept]
summary: "L2 shrinks all weights, L1 zeros some, Elastic Net mixes them; alpha raises simplicity while classifier C works the opposite way."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--02-supervised-learning.md
---

# Penalised Linear Models: Ridge, Lasso and Elastic Net

A linear model predicts a weighted sum `w.x + b`; classifiers threshold it at zero. scikit-learn fits for prediction and reports no standard errors. Plain least squares has no complexity control and overfits when features are many relative to rows.

| Model | Penalty added to squared error | Effect | Knob |
|---|---|---|---|
| OLS | none | Overfits with many features | none |
| Ridge | alpha times the L2 norm of weights squared | Shrinks all weights toward 0 | `alpha` (higher = simpler) |
| Lasso | alpha times the L1 norm | Sets some weights exactly to 0, so it selects features | `alpha`; raise `max_iter` when small |
| Elastic Net | both | Lasso's sparsity with ridge's stability | `alpha`, `l1_ratio` |

## Worked numbers

Setup: the diabetes data expanded to degree-3 polynomial features, giving 285 features and 331 training rows, so OLS has room to overfit.

| Model | Train R squared | Test R squared | Nonzero weights |
|---|---|---|---|
| OLS | 0.90 | -9.32 | 285 |
| Ridge alpha 0.1 | 0.55 | 0.37 | 285 |
| Lasso alpha 0.1 | 0.55 | 0.36 | 7 |

OLS memorises the training set and is far worse than predicting the mean on test. Both penalties rescue it at the cost of train score; lasso matches ridge with 7 weights. Default to ridge; use lasso when you expect few features to matter or need a model you can read. With enough data regularisation matters less and OLS catches up (learning curves).

## Classifiers: the inverted knob

Logistic regression and linear SVM both draw a hyperplane; they differ in loss (log-loss vs hinge), not boundary shape. Their knob is **`C`, the inverse of regularisation strength**: high `C` fits each training point harder, low `C` keeps weights small. This is the opposite direction from `alpha`. `penalty="l1"` gives sparse coefficients. On the breast-cancer split both score 0.944 test accuracy. Linear classifiers are binary by nature: one-vs-rest trains a classifier per class; `LogisticRegression` defaults to a true multinomial (softmax) loss.

Linear models suit very many features, sparse text, huge data (`SGDClassifier`, `solver="sag"`) and readable coefficients; they fail on low-dimensional non-linear boundaries unless features are added. Coefficients of correlated features can flip sign, so do not over-read them.

The same idea appears as a tree's depth limit and a network's weight decay; ridge and lasso are MAP estimates under Gaussian and Laplace priors ([[Regularisation as a Prior]]). For perfectly separable data see [[Logistic Regression Separation]].

## See Also
- [[Supervised Model Families and Complexity Knobs]] — prerequisite-for
- [[Regularisation as a Prior]] — related
- [[Logistic Regression Separation]] — related
- [[OLS Influence and Collinearity Diagnostics]] — related
