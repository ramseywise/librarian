---
title: "Random Forests and Bagging"
tags: [foundations, concept]
summary: "Averaging deep trees cuts variance only as far as their errors are decorrelated, which is why forests subsample features at each split; the out-of-bag score is a free validation estimate."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--06-ensembles.md
---

# Random Forests and Bagging

## Why averaging works, and its limit

A deep decision tree has low bias and high variance. Averaging B models of variance sigma^2 and pairwise correlation rho gives variance rho x sigma^2 + (1 - rho)/B x sigma^2. More trees shrink only the second term; the first needs the trees to be less alike. That is the whole design: bagging trains each tree on a bootstrap sample (n draws with replacement, about 63% unique rows, the other ~37% "out-of-bag"), and a random forest adds a random feature subset at every split (`max_features`).

Contrast with boosting ([[Gradient Boosting Mechanics and Library Choice]]): bagging builds deep trees independently and cuts variance; boosting builds shallow trees sequentially and cuts bias. More forest trees never hurt, only cost time; more boosting rounds eventually overfit.

## Out-of-bag score

Each row is scored only by trees that did not see it, giving a validation estimate with no held-out set. On a small breast-cancer split: single tree train 1.000, test 0.881; forest of 100 train 1.000, test 0.972, out-of-bag 0.962. Forest training accuracy is always about 1.000, so quote test or OOB. OOB accuracy against forest size: 0.883 at 5 trees (with a warning: some rows are never out of bag), 0.960 at 25, 0.962 at 100, 0.960 at 500, so it plateaued between 25 and 100.

## Knobs

| Parameter | Effect |
|---|---|
| `n_estimators` | More is smoother with diminishing returns; 100 to 500 |
| `max_features` | Low: more random, weaker but less correlated trees; defaults `sqrt` (classification), all features (regression) |
| `max_depth`, `min_samples_leaf` | Rarely needed; used to cut memory and time |
| `random_state` | Seeds matter with few trees; fix it |

Setting `max_features` to all features gives plain bagging. On that split bagging scored 0.986 against 0.972 for the `sqrt` forest, two rows of 143, so the correlation term was not visible on a small easy dataset: compare over many splits before naming a winner. Extra-trees adds random split thresholds: faster, sometimes as good.

## Weaknesses

Poor on very high-dimensional sparse data such as text (linear models first); slow to predict with many deep trees; less interpretable than one tree; cannot extrapolate, because a leaf predicts a constant from training targets, so predictions go flat past the training range (fit a linear trend and trees on the residual, or use features that do not need extrapolating).

## Feature importance caveats

`feature_importances_` totals impurity decrease per feature. On 30 correlated features, a single tree gave non-zero importance to 9 and its top three held 0.89; the forest used all 30 (top three 0.39) because feature subsets force it to try the others; boosting used 30 (top three 0.75). Impurity importance favours high-cardinality features, is computed on training data (rewarding overfit), lets correlated features share or steal credit, and gives magnitude without direction. A random column can get non-trivial credit. Use permutation importance on held-out data (see [[Tree Ensemble Interpretation Beyond Impurity Importance]]).

## Stacking and voting

Combining different families with a meta-model trained on out-of-fold predictions (`cv=`; without it the meta-model trusts overfit base models): forest 0.972, SVC 0.965, stack 0.972. Gains are usually small and maintenance costs high, so it earns its place in competitions more than in production.

## See Also
- [[Bias-Variance Decomposition and Model Complexity]] — prerequisite-for
- [[Supervised Model Families and Complexity Knobs]] — prerequisite-for
- [[Gradient Boosting Mechanics and Library Choice]] — alternative-to
- [[Tree Ensemble Interpretation Beyond Impurity Importance]] — extends
- [[Train, Validation and Test Discipline]] — related
