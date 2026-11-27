---
title: AdaBoost as Stagewise Exponential-Loss Fitting
tags: [data-science, classical-ml, concept]
summary: "AdaBoost reweights misclassified cases so the next tree faces a coin flip; statistically it is forward-stagewise fitting of exponential loss, whose population minimiser is half the logit, and a nonnegative lasso can prune the resulting tree ensemble."
updated: 2026-11-20
sources:
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch17-random-forests-boosting.md
---

# AdaBoost as Stagewise Exponential-Loss Fitting

Efron and Hastie (Computer Age Statistical Inference, ch. 17) present boosting as repeatedly growing shallow trees to the residuals and summing them. Gradient boosting generalises the squared-error recipe to other loss functions, with each added tree scaled by a shrinkage factor epsilon. Depth d gives an interaction model of order d - 1, so stumps give an additive model.

## AdaBoost

In AdaBoost, after each round's reweighting of the cases, the classifier just fitted would have a weighted error of 0.5, no better than a coin flip.

Statistically it is forward-stagewise fitting with exponential loss exp[-y f(x)], whose population minimiser is half the logit, so the output G is half the logit. The binomial loss has a linear left tail where the exponential loss has a severe one. The margin y f(x) is positive when classification is correct.

## Setup-specific results

- ALS data (1197 training and 625 test observations, 369 predictors, response the progression rate of a functional rating score): depth 4 with shrinkage 0.02 is about best; d = 1 is worse, while d = 7 starts overfitting near 200 trees and d = 4 near 300. A 25-fold smaller shrinkage (0.02 against 0.5, boosted depth-3 models on a subset of the data, up to 250 trees) gives lower validation error and a much later onset of overfitting, but needs many more trees. Boosting slightly outperformed a random forest on test MSE (500 trees; the figure's values are not printed as numbers), but needs time-costly cross-validated tuning; adding trees to the forest does not overfit, while adding them to the boosted model does. The boosted model used 267 of 369 variables, and Onset.Delta scored 100 on relative importance, over twice the next two at about 40.
- Spam data, test error: a single pruned tree 9.3%, lasso 7.1% and interaction lasso 5.7% (quoted from ch. 16). Boosting and a random forest were not significantly different by McNemar's test but both beat bagging; the forest's error levelled off after about 500 trees (m = 7 of 57 features).
- A nonnegative lasso applied to the boosted depth-2 trees matched the full ALS model with one-third of the trees, but choosing the count is critical.
- By default gbm fits each tree to a random half of the data, which cuts variance in the way bagging does.

The authors suggest using a random forest as a yardstick for a parametric model; a large gap suggests the model lacks interactions.

## Limits

- Only the spam and ALS datasets are used, runs are not repeated, there are no error bars, and the figure values are not given numerically.
- The authors concede boosting needs careful cross-validated tuning of B, d and shrinkage, whereas random forests are nearly automatic.
- The chapter predates XGBoost- and LightGBM-style implementations; it uses the R packages randomForest and gbm only.

## See Also
- [[Gradient Boosting Mechanics and Library Choice]] — prerequisite-for
- [[Random Forests and Bagging]] — alternative-to
- [[Least-Angle Regression and the Lasso Path]] — related (the lasso used to prune trees)
- [[Bias-Variance Decomposition and Model Complexity]] — prerequisite-for
