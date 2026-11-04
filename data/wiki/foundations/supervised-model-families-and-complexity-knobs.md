---
title: "Supervised Model Families and Complexity Knobs"
tags: [foundations, reference]
summary: "Each classical supervised family has one knob that sets its complexity, a typical strength and a typical failure; sweep the knob first and start with a simple model."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--02-supervised-learning.md
---

# Supervised Model Families and Complexity Knobs

The target picks the task: a class label from a fixed set is classification (default score accuracy, losses log-loss, hinge or Gini/entropy), a continuous number is regression (default score R squared, squared-error loss). The test is whether there is continuity between possible outputs.

Every family has a **complexity knob** that trades bias against variance (see [[Bias-Variance Decomposition and Model Complexity]]). The first move with any new model is to sweep the knob and plot train and test score against it.

## Families

| Model | Knob | Scale features? | Good for | Avoid when |
|---|---|---|---|---|
| kNN | `n_neighbors` | Yes | Small low-dimensional data, baseline, explanation by example | Many features, large n |
| Linear | `alpha` / `C` | Yes | High-dimensional, sparse, large data | Low-dim non-linear structure |
| Naive Bayes | `alpha` | No | Very fast text baselines | Accuracy matters most |
| Decision tree | `max_depth` | No | Explaining a model to people | Accuracy (use an ensemble) |
| Random forest | `max_features` | No | Strong tabular default | Very sparse high-dim data |
| Gradient boosting | learning rate, trees, depth | No | Best tabular accuracy | Tuning is unaffordable |
| Kernel SVM | `C`, `gamma` | Yes | Medium data, similar-scale features | Large n |
| MLP | layers, `alpha` | Yes | Large data, time to tune | Small tabular data |

Advice for a new dataset: start with a simple model (linear, naive Bayes or kNN) to learn what the data is like, then move to forests, boosting, SVMs or networks. See [[Random Forests and Bagging]] and [[Gradient Boosting Mechanics and Library Choice]].

## Notes per family

- **kNN** memorises the training set and votes among the k closest points. On the breast-cancer split used in the source, k=1 scores 1.0 train and 0.902 test (overfit), k=6 gives 0.937 test. It fails when distances stop meaning anything (many features, sparse data) and is dominated by the largest-range feature unless scaled.
- **Naive Bayes** fits per-class statistics of each feature independently and applies Bayes' rule in a single pass: Gaussian for continuous, Bernoulli for binary, multinomial for counts. Smoothing `alpha` pretends each feature was seen that many extra times per class. The independence assumption is wrong but the ranking is often good; usually slightly worse than a linear model, trained much faster.
- **Decision tree** asks if/else questions chosen to make groups pure; leaves predict the majority class or mean. Grown until pure, it memorises (1.0 train, 0.895 test on the split); `max_depth=4` gives 0.988 / 0.902 using 10 of 30 features. Control it by pre-pruning (`max_depth`, `max_leaf_nodes`, `min_samples_leaf`) or cost-complexity post-pruning (`ccp_alpha`). Trees need no scaling (only the order of a feature's values matters) and **cannot extrapolate**: predictions are means of training leaves, so on a trending series they flatline at the last training value. Model the trend with a linear part or difference the target.
- **MLP**: stacked linear models with a non-linearity between; without it the stack collapses to one linear model. Recipe: build a network big enough to overfit, then shrink it or raise `alpha` until test score peaks. Scaling to mean 0, variance 1 is required; different seeds give visibly different boundaries on small data. For tabular data boosted trees usually win.

## Uncertainty estimates

`decision_function` returns a signed margin (scale is model-specific); `predict_proba` returns class probabilities summing to 1. A probability is only as good as the model's calibration: an overfit model reports 1.0 on points it gets wrong, and boosted trees and SVMs distort probabilities in a sigmoid shape while logistic regression does not. See [[Probability Calibration and Reliability Curves]].

## From scratch: gradient descent vs the normal equation

Gradient descent iterates with a learning rate; the normal equation is closed form at about cubic cost in the number of features. Gradient descent diverges if the learning rate is too high (plot cost per iteration), is slowed badly by features on different scales (normalise first), and a regularisation term never penalises the bias weight.

## Pitfalls

- Unscaled features for a distance or margin model: scores near the dummy rate, and scaling jumps them.
- Reading coefficients as causes: correlated features can flip sign between fits.
- A convergence warning ignored: coefficients differ with solver or seed; scale or raise `max_iter`.

## See Also
- [[Penalised Linear Models: Ridge, Lasso and Elastic Net]] — extends
- [[Kernel SVM and the Kernel Trick]] — extends
- [[Random Forests and Bagging]] — extends
- [[Bias-Variance Decomposition and Model Complexity]] — prerequisite-for
