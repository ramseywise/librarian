---
title: "Cross-Validation Variants and Nested Search"
tags: [foundations, pattern]
summary: "Pick the splitter that mirrors how the model meets new data, search hyperparameters on a log scale, and use nested CV because the best CV score is optimistic."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--04-model-evaluation.md
---

# Cross-Validation Variants and Nested Search

A single split gives a score that depends on which points landed in test. **k-fold CV** trains k models, each holding out one fold. Every point is tested once, the **spread** of fold scores shows sensitivity to the training data, and more data trains each model (80% at k=5 against 75% for the default split). CV evaluates a *procedure*; it does not return a model, so refit on all data for the final one.

## Splitters

| Splitter | When | Note |
|---|---|---|
| `KFold(shuffle=True)` | Regression; random order | Without shuffle, class-sorted data (iris) gives folds with unseen classes and 0 scores |
| `StratifiedKFold` | Classification (default) | Keeps class proportions |
| `LeaveOneOut` | Very small data | n fits; high-variance estimate |
| `ShuffleSplit` | Control sizes and repeats; subsample large data | |
| `GroupKFold` | Several rows per subject | A group is never in train and test; otherwise you measure memorisation of the person |
| `TimeSeriesSplit` | Temporal data | Train on the past, test on the future |
| `RepeatedStratifiedKFold` | Small data, tighter estimate | |

The groups rule generalises: the split must mirror production. New users, split by user; next month, split by time. See [[Cross-Validation Fold Spread and Choosing the Splitter]] and [[Time-Series Leakage: Shift and Rolling Windows]].

## Grid search

Hyperparameters are not learned by `fit`. The three-way split applies: pick on validation or CV, report on test once. `GridSearchCV` runs CV on the training part, then refits the best on all of it. On iris with SVC, best CV 0.973 and held-out test 0.974.

- Search on a log scale. A list of dicts handles conditional spaces (gamma only for the RBF kernel).
- Read the result as a heatmap of mean score: best in the interior means the range is right; best on an edge means the optimum may lie outside, so extend the range; flat means the parameter does not matter or the scale is wrong.
- `RandomizedSearchCV` samples from distributions and finds good regions in far fewer fits with many parameters; `HalvingGridSearchCV` drops poor candidates early.
- The scorer decides the winner: on a rare-positive split, accuracy and ROC AUC scorers pick different gamma (0.0001 vs 0.01, test AUC 0.992 vs 1.0). Choose the scorer before searching. Error metrics are negated because scikit-learn always maximises.

## Nested cross-validation

The best CV score is optimistic because it was used for selection. With no separate test set, wrap the grid search in an outer CV (5 x 5 x 36 = 900 fits in the iris example, estimate 0.98). It evaluates the *selection procedure*, not one model. Evidence for why: on null datasets of 40 samples with no signal (true error 50%), tuning two classifiers by minimising CV error gave an average minimum CV error of 37.8% (shrunken centroids) and 41.7% (SVM), with optimism over 20 points on more than a fifth of datasets; nested CV was nearly unbiased with slight pessimism from training on 39 samples. Keeping the best of many tries is the [[Multiple Comparisons Corrections]] problem.

## See Also
- [[Train, Validation and Test Discipline]] — prerequisite-for
- [[Pipelines Prevent Preprocessing Leakage]] — related
- [[Cross-Validation Fold Spread and Choosing the Splitter]] — extends
- [[Multiple Comparisons Corrections]] — related
