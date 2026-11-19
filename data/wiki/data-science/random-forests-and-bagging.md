---
title: "Random Forests and Bagging"
tags: [data-science, concept]
summary: "Averaging deep trees cuts variance only as far as their errors are decorrelated, which is why forests subsample features at each split; the out-of-bag score is a free validation estimate."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--06-ensembles.md
  - data/raw/papers/2026-11-08-practical-statistics-for-data-scientists-ch06-statistical-machine-learning.md
  - data/raw/papers/2026-11-08-intro-to-ml-with-python-ch02-supervised-learning.md
  - data/raw/papers/2026-11-08-islp-ch08-tree-based-methods.md
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch17-random-forests-boosting.md
  - data/raw/papers/2026-11-08-python-data-science-handbook-ch05-machine-learning.md
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
| `max_features` | Low: more random, weaker but less correlated trees; scikit-learn defaults per the course notes: `sqrt` (classification), all features (regression); other books differ, see Limits |
| `max_depth`, `min_samples_leaf` | Rarely needed; used to cut memory and time |
| `random_state` | Seeds matter with few trees; fix it |

Setting `max_features` to all features gives plain bagging. On that split bagging scored 0.986 against 0.972 for the `sqrt` forest, two rows of 143, so the correlation term was not visible on a small easy dataset: compare over many splits before naming a winner. Extra-trees adds random split thresholds: faster, sometimes as good.

## Weaknesses

Poor on very high-dimensional sparse data such as text (linear models first); slow to predict with many deep trees; less interpretable than one tree; cannot extrapolate, because a leaf predicts a constant from training targets, so predictions go flat past the training range (fit a linear trend and trees on the residual, or use features that do not need extrapolating).

## Feature importance caveats

`feature_importances_` totals impurity decrease per feature. On 30 correlated features, a single tree gave non-zero importance to 9 and its top three held 0.89; the forest used all 30 (top three 0.39) because feature subsets force it to try the others; boosting used 30 (top three 0.75). Impurity importance favours high-cardinality features, is computed on training data (rewarding overfit), lets correlated features share or steal credit, and gives magnitude without direction. A random column can get non-trivial credit. Use permutation importance on held-out data (see [[Tree Ensemble Interpretation Beyond Impurity Importance]]).

## Stacking and voting

Combining different families with a meta-model trained on out-of-fold predictions (`cv=`; without it the meta-model trusts overfit base models): forest 0.972, SVC 0.965, stack 0.972. Gains are usually small and maintenance costs high, so it earns its place in competitions more than in production.

## Book example

In chapter 6 of *Practical Statistics for Data Scientists* (R, Lending Club loan3000 sample, 500 trees, default settings) a forest on borrower score and payment-to-income ratio has an out-of-bag error of 38.53%; using all columns (3 variables per split) gives 34.38%. The authors give square root of the predictor count as the rule of thumb for variables per split, prefer permutation (out-of-bag accuracy decrease) importance to the training-based Gini decrease, and advise tuning nodesize and maxnodes by cross-validation on noisy data. The scikit-learn book's chapter 2 says a bootstrap sample leaves out roughly a third of the data points, advises trying the defaults first, and gives the `max_features` default as the square root of the feature count for classification and its base-2 logarithm for regression (in that book's 2016-era scikit-learn; see Limits).

## Settings and results from three more books

- Introduction to Statistical Learning ch08, Heart data (303 patients, 13 predictors): 100 bagged trees are enough and adding more does not overfit; the forest tries 4 of the 13 predictors at each split, close to the square-root rule. Each bagged tree sees about two thirds of the rows, and the left-out third gives an out-of-bag error that the authors say approximates leave-one-out CV when there are many trees (their claim, not tested there).
- Same book, gene-expression data (349 patients, 15 classes, the 500 most variable of 4,718 genes, one random split): one tree errs 45.7% of the time, always predicting the normal class has a null rate of 75.4%, 400 trees suffice, and trying the square root of p predictors slightly beat trying all of them.
- Same book, Boston housing (70/30 split): a pruned tree has test MSE 28.07, bagging 14.63 with 100 trees and 14.61 with 500, and a forest with max_features=6 scored 20.04, worse than bagging (6 is half of the 12 predictors; bagging used all 12). The gene data ordered the two the other way.
- Computer Age Statistical Inference ch17, spam data (57 features, forest trying 7 per split): test error levels off after roughly 500 trees, against 9.3% for one pruned tree. The R randomForest defaults try sqrt(p) variables for classification and a third of p for regression. The authors repeat that out-of-bag error matches leave-one-out CV when the tree count is about three times what the forest needs to stabilise.
- Python Data Science Handbook ch05, scikit-learn digits (1,797 images; default 75/25 split with random_state=0 leaves 450 held out, a count inferred rather than printed): an untuned forest of 1,000 trees scores 0.98 precision, recall and F1, where Gaussian naive Bayes on the same split scores 0.833.
- Boosting against a forest: on the ALS data of Computer Age ch17, boosting beat the forest only slightly and needed cross-validated tuning, which the forest did not. Chapter 17 also derives AdaBoost as stagewise fitting of exponential loss, covered in [[AdaBoost as Stagewise Exponential-Loss Fitting]].

## Limits

- The chapter's numbers are single illustrative runs with no seeds or intervals.
- Introduction to Statistical Learning ch08: the lab results are single random splits and the authors note they change with the seed; they admit lone trees lose on accuracy and that ensembles cost interpretability.
- Computer Age ch17: only the spam and ALS data, with no repeated runs or error bars, and the R randomForest package only.
- Python Data Science Handbook ch05: the digits score is one run on one split of a small, easy dataset, with no interval, and its code uses a 2016-era scikit-learn API.
- `max_features` defaults for regression differ by source and library: the course notes give scikit-learn's as all features, Introduction to Machine Learning with Python ch02 gives the base-2 logarithm of the feature count (that book's 2016-era scikit-learn), and Computer Age ch17 gives p/3 for the R randomForest package. The extractions do not say which is current for scikit-learn.

## See Also
- [[Bias-Variance Decomposition and Model Complexity]] — prerequisite-for
- [[Supervised Model Families and Complexity Knobs]] — prerequisite-for
- [[Gradient Boosting Mechanics and Library Choice]] — alternative-to
- [[Tree Ensemble Interpretation Beyond Impurity Importance]] — extends
- [[Train, Validation and Test Discipline]] — related
- [[AdaBoost as Stagewise Exponential-Loss Fitting]] — alternative-to
- [[Cost-Complexity Pruning of Decision Trees]] — related
