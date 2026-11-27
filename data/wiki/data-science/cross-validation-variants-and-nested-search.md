---
title: "Cross-Validation Variants and Nested Search"
tags: [data-science, classical-ml, pattern]
summary: "Pick the splitter that mirrors how the model meets new data, search hyperparameters on a log scale, and use nested CV because the best CV score is optimistic."
updated: 2026-11-20
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--04-model-evaluation.md
  - data/raw/papers/2026-11-06-varma-2006-bias-error-estimation-when-using.md
  - data/raw/papers/2026-11-08-cawley-2010-over-fitting-model-selection.md
  - data/raw/papers/2026-11-08-intro-to-ml-with-python-ch05-model-evaluation-improvement.md
  - data/raw/papers/2026-11-08-islp-ch05-resampling-methods.md
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch12-cross-validation-cp-estimates-prediction.md
  - data/raw/papers/2026-11-08-python-data-science-handbook-ch05-machine-learning.md
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

## Validation set, LOOCV and k-fold in ISLP

ISLP's Chapter 5 lab compares the three on the Auto data (392 observations, mpg on polynomials of horsepower). A 196/196 validation split gave MSE 23.62, 18.76 and 18.80 for degrees 1 to 3 at random_state=0, and 20.76, 16.95 and 16.97 at random_state=3: the level moved by about 3 MSE units with the split while the ranking stayed. LOOCV MSE over degrees 1 to 5 dropped sharply at degree 2 with no clear gain beyond; 10-fold CV (shuffled, random_state=0, the same splits for each degree) agreed with LOOCV and ran much faster. For least squares the LOOCV error needs a single fit, the average of squared residuals each divided by (1 - leverage h_i), squared, though the generic `cross_validate` call does not use this shortcut. The authors recommend k = 5 or 10 as a balance of bias and variance, and say the location of the CV minimum matters more than the estimated level, since CV can under- or over-estimate the true test MSE.

On the simulated two-class data of Fig 2.13, 10-fold CV picked a 4th-order polynomial logistic regression while the true test-error minimum was at 3rd order; true error was about equal for orders 3 to 6. In the lab, ten repeated 196-observation validation splits gave a mean of 23.8022 with spread 1.4218 for the linear fit; the authors caution that this spread cannot serve as a sampling-variability estimate, since the training sets share observations.

## Training-set scoring, ephemeral predictors and what CV estimates

In the Python Data Science Handbook's Iris example, a 1-nearest-neighbour model scores a perfect 1.0 when judged on the rows it was fitted on, so it does not show how the model does on unseen data. On a 50/50 holdout it reaches about 0.907. Swapping the two halves (two-fold CV) gives 0.960 and 0.907; leave-one-out over the 150 rows averages 0.96; five-fold per-fold accuracies range from 0.933 to 1.0.

Efron and Hastie (CASI ch12) warn about **ephemeral predictors**, features whose predictive power fades over time. In their simulated microarray study (360 subjects, 100 genes, transient episodes of about 30 days), a random forest had 15% test error on a randomly drawn validation set but 27% when validation days followed the training days. Their advice is to validate on blocked folds, separated in time or place, instead of random ones. They also argue that a CV figure describes how the fitting procedure does on average, not the one rule it produced on your data; in their 500 bootstrap simulations the CV estimate correlated only weakly with the true error of each fitted rule. The covariance-penalty route to the same quantity is on [[Covariance Penalty Estimates of Prediction Error]].

## Limits

- Varma and Simon use synthetic Gaussian data with 40 samples and 6,000 features, only two classifiers, and a simplified SVM (top 3 features by t-statistic, fixed kernel, grid search), which the authors say may reduce the bias. Nested CV was shown for shrunken centroids only on null data and for the SVM only on non-null data. Their abstract gives 38% of null datasets under 30% error for the SVM, while their Table 1 gives 22.2%; the paper does not explain this, so only the 18.5% figure for shrunken centroids is safe to cite. The paper gives no cost analysis for nested CV.
- Cawley and Talbot use small datasets (140 to 1,300 training patterns) and mainly kernel machines; their remedies are discussed but not tested, and they state no theory. They ran no nested CV experiment of their own; the internal protocol is its analogue.
- The chapter's examples are iris-sized toy data on single splits, written for an older scikit-learn API.
- The Iris numbers are one dataset and one random split, with no repeated-split spread. CASI Table 12.3 gives a correlation of 0.175 between the CV estimate and true error, while the Fig 12.3 text calls it negative; minus signs are lost in the extract's text layer, so the sign is unconfirmed. CASI also points out that picking the winning rule by its CV score sits outside the CV loop, which makes the winning score optimistic.
- ISLP Chapter 5 leaves out stratified, grouped and time-series CV, nested CV, and preprocessing leakage across folds, and uses the bootstrap only as a standard-error tool.

## See Also
- [[Train, Validation and Test Discipline]] — prerequisite-for
- [[Pipelines Prevent Preprocessing Leakage]] — related
- [[Cross-Validation Fold Spread and Choosing the Splitter]] — extends
- [[Multiple Comparisons Corrections]] — related
- [[Covariance Penalty Estimates of Prediction Error]] — alternative-to
- [[Cost-Complexity Pruning of Decision Trees]] — related
