---
title: "Ordered Boosting and Ordered Target Statistics"
tags: [data-science, classical-ml, pattern]
summary: "CatBoost's two permutation-based fixes for target leakage in boosting: categorical encodings and residuals are computed for each example only from examples earlier in a random order."
updated: 2026-11-20
sources:
  - data/raw/papers/2026-11-07-prokhorenkova-2017-catboost.md
---

# Ordered Boosting and Ordered Target Statistics

Prokhorenkova, Gusev, Vorobev et al. (2017) argue that gradient boosting libraries suffer a **prediction shift**: the distribution of the model's output for a training example, given its features, differs from that for a test example, because gradients are computed from the same targets the model was fitted on. They propose one ordering principle and apply it twice, once to categorical features and once to the boosting residuals. The result is the CatBoost library. It sits beside the usual comparison in [[Gradient Boosting Mechanics and Library Choice]].

## Ordered target statistics

A categorical level is replaced by a smoothed mean of the target over rows sharing that level. The paper's formula adds a prior p with weight a: numerator is the sum of targets in the same level plus a*p, denominator is the count in that level plus a.

- Greedy TS, the baseline, computes the statistic without any ordering.
- Ordered TS draws a random permutation and, for each training row, uses only rows that come earlier in it. Test rows use all of the training data.
- Compared in CatBoost Ordered mode with only the TS type varied, greedy TS was up to 57% worse in logloss on Upselling and 40% worse on Amazon; leave-one-out was 5.5% worse than ordered TS on Adult; holdout was the strongest baseline on most datasets, yet ordered TS still beat it (holdout +8.3% on Amazon) (self-reported).

## Ordered boosting

In classic boosting the residual for an example comes from a model that has already seen that example. In ordered boosting, each example's residual is taken from a supporting model that was fitted to only the examples preceding it in a random permutation. CatBoost builds oblivious trees (one split criterion shared across a level) on top of this.

- Theorem 1 shows the bias in a toy case: quadratic loss, two independent coin-flip features, a target linear in both, two stumps fitted on the same data. The resulting bias grows with c2 and shrinks as n grows (self-reported).
- Using more permutations lowered logloss a little, by 0.19% with 3 and 0.38% with 9, against a single permutation (8 datasets, self-reported).
- Allowing feature combinations of up to two features improved logloss by 1.86% on average and up to 11.3% (self-reported).

## Where it helps and what it costs

Setup for the headline: 9 binary classification datasets, one random 80/20 split each, baselines (XGBoost, LightGBM) tuned with 5-fold CV and 50 Hyperopt TPE steps minimising logloss, Epsilon on defaults with only tree count tuned. CatBoost in its strong setting beat both on all nine datasets, with the largest gap on Amazon (self-reported). Adult: baselines 2.4% (LightGBM) and 2.2% (XGBoost) worse in logloss; Internet: 6.8% and 7.9% worse; Upselling, Appetency and Churn: gaps tiny and not significant.

- Ordered mode helps most on small data: Plain mode lost 3.9% logloss on Internet and 1.1% on Adult, yet gained slightly on four of nine datasets (by 0.6% on Amazon, 0.2% on Kick, 0.06% on Churn and 0.05% on Click) (self-reported).
- Per-tree time on Epsilon, run with 16 threads at depth 6 for 8000 trees, was 1.9 s in Ordered mode, 1.1 s in Plain mode (ratio about 1.7) and 3.9 s in XGBoost (self-reported).
- In the raw setting, which is close to classic GBDT, CatBoost matched the baselines on average over 8 datasets, slightly ahead on zero-one loss and slightly behind on logloss (0.2% each) (self-reported).

## Limits

- The proof of prediction shift covers a toy regression only; the general case is argued.
- Each dataset gets a single random 80/20 split with no repeated seeds; a paired t-test is used and how it pairs is unstated.
- Binary classification only; logloss and zero-one loss, no AUC.
- Epsilon used default parameters for all libraries, while the other datasets used tuned baselines.
- Feature combinations are given to CatBoost alone, so the headline gap blends three things: ordered boosting, combinations and oblivious trees. In the raw setting the plain GBDT base comes out roughly level.
- The libraries compared are 2017-2018 releases (versions 0.3, 0.6 and 0.1 for catboost, xgboost and lightgbm). The paper leaves GPU timings to a GitHub page. The arXiv v5 PDF is marked as a preprint, work in progress, with no venue.

## See Also
- [[Gradient Boosting Mechanics and Library Choice]] — prerequisite-for
- [[Categorical Encoding Choices]] — prerequisite-for
- [[Hyperparameter Search Budgets and Selection Optimism]] — related
