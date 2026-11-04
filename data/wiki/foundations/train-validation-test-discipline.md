---
title: "Train, Validation and Test Discipline"
tags: [foundations, pattern]
summary: "The test set is touched once; tuning happens on validation or CV folds, and every score is read against the majority-class base rate."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--01-statistical-foundations.md
---

# Train, Validation and Test Discipline

> The test set is touched once, at the end. Everything tuned is tuned on data the test set never saw.

| Split | Used for | Typical share |
|---|---|---|
| Training | Fitting parameters | 60-80% |
| Validation (or CV folds) | Choosing hyperparameters, features, model family | 10-20%, or k-fold over the training part |
| Test | One final estimate of generalisation | 10-20% |

Three splits rather than two because parameters are fit on train, choices are made on validation, and only then does the test set give an honest estimate. scikit-learn's `train_test_split` shuffles and holds out 25% by default; fix `random_state` for reproducibility and pass `stratify=y` for classification so class balance matches.

## Ways to break it

- **Tuning on the test set.** Picking an SVM's `C` by test score turns the test set into a validation set; the reported score is optimistic.
- **Leakage.** Fitting a scaler or feature selector on all data before splitting lets the model see statistics of test rows. See [[Tabular ML Leakage Taxonomy]] and [[Pipelines Prevent Preprocessing Leakage]].
- **Shuffling ordered data.** Time-stamped or grouped rows need a split by time or group, the way production meets data; otherwise offline score is great and live score poor. See [[Time-Series Leakage: Shift and Rolling Windows]].
- **Reading the test set during development.** The score drops the day the model meets real data.

## Read every score against the base rate

On the adult census income table (32,561 rows, target is income over 50k), 0.759 of rows are "<=50K". Always guessing that class is right about three times in four, so accuracy must be read against that number, not against zero. A sensible-looking rule, "predict >50K if `education-num` >= 13", scores 0.752 accuracy, below the baseline. Print the class proportions before fitting anything.

## The estimator API that makes this routine

Every scikit-learn estimator follows `fit`, then `predict` / `transform` / `score`; learned state ends in an underscore, and `fit` returns `self`. Because the shape is uniform, estimators chain in pipelines and plug into hyperparameter search. A custom estimator subclasses `BaseEstimator`, takes every hyperparameter in `__init__` without logic, and returns `self` from `fit`. Look at the data before fitting (a scatter matrix shows whether classes separate and catches unit errors).

## See Also
- [[Bias-Variance Decomposition and Model Complexity]] — prerequisite-for
- [[Cross-Validation Variants and Nested Search]] — extends
- [[Tabular ML Leakage Taxonomy]] — related
