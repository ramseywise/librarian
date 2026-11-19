---
title: "Cross-Validation Variants and Nested Search"
tags: [data-science, pattern]
summary: "Pick the splitter that mirrors how the model meets new data, search hyperparameters on a log scale, and use nested CV because the best CV score is optimistic."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--04-model-evaluation.md
  - data/raw/papers/2026-11-06-varma-2006-bias-error-estimation-when-using.md
  - data/raw/papers/2026-11-08-cawley-2010-over-fitting-model-selection.md
  - data/raw/papers/2026-11-08-intro-to-ml-with-python-ch05-model-evaluation-improvement.md
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

The best CV score is optimistic because it was used for selection. Without a separate test set, put the grid search inside an outer CV loop (5 x 5 x 36 = 900 fits in the iris example, estimate 0.98). It evaluates the *selection procedure*, not one model. The authors of the book chapter behind the 900-fit example advise using nested CV for assessing a model class on one dataset; its output is a list of scores, so it yields no model to deploy.

Varma and Simon's simulation (self-reported): on null datasets (at least 1000, each 40 samples with 6,000 noise features and no class difference, true error 50%), the cross-validated error of a classifier tuned on that same CV averaged 37.8% for shrunken centroids (10-fold CV tuning delta) and 41.7% for an SVM (leave-one-out tuning of C and gamma), a bias of -12.2 and -8.3 points. On 22.2% of datasets (shrunken centroids) and 25.3% (SVM) the bias was above 20 points. Nested leave-one-out CV gave 54.2% on null data for shrunken centroids (true 50.0%), slightly pessimistic because each inner model trained on 39 samples rather than 40; for the SVM on data with 10 informative features out of 6,000 it gave 35.3% against a true 32.0%. Their rule is to rerun each stage of the pipeline, from feature selection to parameter tuning, within every CV iteration. Taking the best of many candidates is the [[Multiple Comparisons Corrections]] problem.

## Protocols that leak selection

Cawley and Talbot compared evaluation protocols with kernel ridge regression on 13 benchmark datasets (self-reported). Choosing hyper-parameters one time on the full design set and then running 10-fold CV (the external protocol) was optimistically biased on all 13. Selecting on the first five realisations and applying the median to every realisation (the median protocol) was also optimistically biased; on breast cancer, german, heart and thyroid the bias was larger than the usual difference separating classifiers. Under the internal protocol (selection repeated inside each fold) no classifier among kernel ridge, kernel logistic regression and EP-GPC was significantly better; under the median protocol kernel ridge looked significantly superior at the 95% level. They recommend nested CV as the unbiased protocol, at higher compute cost. More hyper-parameters give more to over-fit: an ARD kernel, a superset of RBF, beat RBF significantly on only one of thirteen datasets. See [[Hyperparameter Search Budgets and Selection Optimism]].

## Limits

- Varma and Simon use synthetic Gaussian data with 40 samples and 6,000 features, only two classifiers, and a simplified SVM (top 3 features by t-statistic, fixed kernel, grid search), which the authors say may reduce the bias. Nested CV was shown for shrunken centroids only on null data and for the SVM only on non-null data. Their abstract gives 38% of null datasets under 30% error for the SVM, while their Table 1 gives 22.2%; the paper does not explain this, so only the 18.5% figure for shrunken centroids is safe to cite. The paper gives no cost analysis for nested CV.
- Cawley and Talbot use small datasets (140 to 1,300 training patterns) and mainly kernel machines; their remedies are discussed but not tested, and they state no theory. They ran no nested CV experiment of their own; the internal protocol is its analogue.
- The chapter's examples are iris-sized toy data on single splits, written for an older scikit-learn API.

## See Also
- [[Train, Validation and Test Discipline]] — prerequisite-for
- [[Pipelines Prevent Preprocessing Leakage]] — related
- [[Cross-Validation Fold Spread and Choosing the Splitter]] — extends
- [[Multiple Comparisons Corrections]] — related
