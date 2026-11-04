---
title: "Learning Curves and Bias-Variance Diagnosis"
tags: [foundations, pattern]
summary: "Plot train and validation error against training size to tell high bias (more data will not help) from high variance (it will)."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--04-model-evaluation.md
---

# Learning Curves and Bias-Variance Diagnosis

Fit a model on increasing numbers of training examples and plot training error and cross-validation error against the count. The shape operationalises [[Bias-Variance Decomposition and Model Complexity]].

| Curve shape | Diagnosis | More data helps? | Fix |
|---|---|---|---|
| Train and validation error both high, converge quickly | High bias (underfit) | No | More features (for example a degree-8 polynomial), less regularisation, bigger model |
| Train error low, large gap to validation | High variance (overfit) | Yes | More data, more regularisation, fewer features |
| Both low, small gap | Good fit | Marginal | Ship it |

Worked case: regularised linear regression on a water-level / outflow dataset fit with a straight line. Training error 0, 2.8, 19.4, 18.2, 23.3, 22.4 and validation error 110.3, 48.4, 33.8, 30.9, 28.9, 29.4 at m = 2, 4, 6, 8, 10, 12. Both level off together and high: the line is too simple and more data will not fix it. Report errors *without* the penalty term when plotting.

Choosing the regularisation strength `lambda` follows the same recipe: sweep it on a grid, pick the lowest validation error (about 3 in that exercise), and report test error once. That is grid search written by hand. scikit-learn's `learning_curve` varies training size; `validation_curve` sweeps one hyperparameter instead. For ridge on the diabetes data, train score rises 0.19 to 0.43 and validation 0.14 to 0.41 from 70 to 353 rows, a small gap with both still climbing.

Plot a learning curve before collecting more data: it says whether more data can help.

## See Also
- [[Bias-Variance Decomposition and Model Complexity]] — prerequisite-for
- [[Cross-Validation Variants and Nested Search]] — related
- [[Penalised Linear Models: Ridge, Lasso and Elastic Net]] — related
- [[Error Analysis, Bias and Variance Gaps]] — related
