---
title: "Penalised Linear Models: Ridge, Lasso and Elastic Net"
tags: [data-science, concept]
summary: "L2 shrinks all weights, L1 zeros some, Elastic Net mixes them; alpha raises simplicity while classifier C works the opposite way."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--02-supervised-learning.md
  - data/raw/papers/2026-11-08-intro-to-ml-with-python-ch02-supervised-learning.md
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch16-sparse-modeling-lasso.md
  - data/raw/papers/2026-11-08-islp-ch06-linear-model-selection-regularization.md
---

# Penalised Linear Models: Ridge, Lasso and Elastic Net

A linear model predicts a weighted sum `w.x + b`; classifiers threshold it at zero. scikit-learn fits for prediction and reports no standard errors. Plain least squares has no complexity control and overfits when features are many relative to rows.

| Model | Penalty added to squared error | Effect | Knob |
|---|---|---|---|
| OLS | none | Overfits with many features | none |
| Ridge | alpha times the L2 norm of weights squared | Shrinks all weights toward 0 | `alpha` (higher = simpler) |
| Lasso | alpha times the L1 norm | Sets some weights exactly to 0, so it selects features | `alpha`; raise `max_iter` when small |
| Elastic Net | both | Lasso's sparsity with ridge's stability | `alpha`, `l1_ratio` |

## Worked numbers

Setup: the diabetes data expanded to degree-3 polynomial features, giving 285 features and 331 training rows, so OLS has room to overfit.

| Model | Train R squared | Test R squared | Nonzero weights |
|---|---|---|---|
| OLS | 0.90 | -9.32 | 285 |
| Ridge alpha 0.1 | 0.55 | 0.37 | 285 |
| Lasso alpha 0.1 | 0.55 | 0.36 | 7 |

OLS memorises the training set and is far worse than predicting the mean on test. Both penalties rescue it at the cost of train score; lasso matches ridge with 7 weights. Default to ridge; use lasso when you expect few features to matter or need a model you can read. With enough data regularisation matters less and OLS catches up (learning curves).

## Classifiers: the inverted knob

Logistic regression and linear SVM both draw a hyperplane; they differ in loss (log-loss vs hinge), not boundary shape. Their knob is **`C`, the inverse of regularisation strength**: high `C` fits each training point harder, low `C` keeps weights small. This is the opposite direction from `alpha`. `penalty="l1"` gives sparse coefficients. On the breast-cancer split both score 0.944 test accuracy. Linear classifiers are binary by nature: one-vs-rest trains a classifier per class; `LogisticRegression` defaults to a true multinomial (softmax) loss.

Linear models suit very many features, sparse text, huge data (`SGDClassifier`, `solver="sag"`) and readable coefficients; they fail on low-dimensional non-linear boundaries unless features are added. Coefficients of correlated features can flip sign, so do not over-read them.

The same idea appears as a tree's depth limit and a network's weight decay; ridge and lasso are MAP estimates under Gaussian and Laplace priors ([[Regularisation as a Prior]]). For perfectly separable data see [[Logistic Regression Separation]].

## Textbook numbers on Boston and breast cancer

Müller and Guido (2016) use the extended Boston data (506 rows, 104 features) with the `train_test_split(random_state=0)` split for regression:

| Model | Train R squared | Test R squared | Notes |
|---|---|---|---|
| OLS | 0.95 | 0.61 | overfits |
| Ridge, alpha 1 | 0.89 | 0.75 | |
| Ridge, alpha 0.1 | 0.93 | 0.77 | |
| Ridge, alpha 10 | 0.79 | 0.64 | |
| Lasso, alpha 1 | 0.29 | 0.21 | 4 features used |
| Lasso, alpha 0.01 (`max_iter=100000`) | 0.90 | 0.77 | 33 features used |
| Lasso, alpha 0.0001 | 0.95 | 0.64 | 94 features used |

On 60 samples of a one-feature wave, OLS scores 0.67 train and 0.66 test, which is underfitting rather than overfitting. In learning curves on subsampled Boston data (ridge with alpha 1 against plain linear regression), linear regression learns nothing below about 400 training points while ridge does better, and the two converge with enough data.

For classification on the breast-cancer data (stratified split, `random_state=42`, L2 penalty), logistic regression scores train 0.953 and test 0.958 at the default `C=1`, 0.972 and 0.965 at `C=100`, and 0.934 and 0.930 at `C=0.01`. With the L1 penalty, `C=100` reaches 0.98 on test (0.99 on train), while `C=0.001` drops to 0.92.

The authors advise defaulting to ridge, using the L1 penalty when few features matter or a readable model is needed, and Elastic Net to combine both. They also sweep `alpha` and `C` on a logarithmic scale, warn against reading coefficient signs as class association when features are correlated, and suggest `solver="sag"`, `SGDClassifier` or `SGDRegressor` for very large data.

## The lasso path and the Hitters and Credit results

Efron and Hastie's chapter 16 says the lasso's coefficient path can be traced by least-angle regression (LAR) only with a modification that drops a variable; dropping tends to happen among highly correlated variables, and the lasso has trouble choosing between such predictors (see [[Least-Angle Regression and the Lasso Path]]). They also report that, under technical conditions, the lasso spends exactly one degree of freedom per LAR step, while forward stepwise selection spends more; the stepwise figure comes from 5,000 simulated data sets on the spam training data (a parametric bootstrap from the full least-squares fit with Gaussian errors). For the path itself, the smallest lambda that zeroes every coefficient is the largest absolute inner product of a predictor with the response divided by n, and the logistic lasso is fitted over a grid of 100 log-spaced lambdas running down from that value to a small fraction of it (for example 0.001 times it). glmnet fits the whole logistic path on the 3,061-variable spam data in 6 seconds (self-reported, on 2015 hardware the chapter does not describe).

ISLP's chapter 6 uses the Hitters baseball data (263 players after dropping 59 with missing Salary, 19 predictors, 5-fold CV for the penalised fits, predictors standardised because ridge needs a common scale). Ridge, run through an elastic-net routine, picks lambda 1.19e-02 with CV MSE 115,527, against 231,788 for the null model. The lasso reaches CV MSE 114,691 with 13 variables kept (6 of 19 coefficients zero). Ridge is the posterior mode under a Gaussian prior on the coefficients and the lasso under a double-exponential prior. In a simulation with 45 predictors and 50 observations, ridge slightly beat the lasso when every predictor was related to the response and the lasso won when only 2 of the 45 were.

On the 10-predictor Credit data the subset-size rules disagree: Cp selects six variables, BIC four, adjusted R squared seven, validation-set and 10-fold CV six, and the one-standard-error rule three. On Hitters, forward selection by Cp picks 10 variables while the default scoring in the lab picks all 19.

## Limits

- The chapter reads each result from one split and chooses `alpha` and `C` by looking at test scores.
- Its code is dated: `load_boston` was removed in scikit-learn 1.2, and an L1 logistic regression now needs the `liblinear` or `saga` solver. Boston Housing is ethically problematic.
- Its text gives `alpha=0.00001` for a lasso figure where the code uses 0.0001.
- The logistic-regression scores above come from the chapter's split and differ from the 0.944 quoted earlier on this page from the course note, which uses another split.
- The Hitters and Credit figures are single runs; the chapter's simulations give no seeds or repeats, its CV standard error is crude, and the lab prints a convergence warning.
- The 5,000-simulation degrees-of-freedom result is a claim from one data set under stated conditions, and the glmnet timing is self-reported with no hardware given.

## See Also
- [[Supervised Model Families and Complexity Knobs]] — prerequisite-for
- [[Regularisation as a Prior]] — related
- [[Logistic Regression Separation]] — related
- [[OLS Influence and Collinearity Diagnostics]] — related
- [[Least-Angle Regression and the Lasso Path]] — extends
- [[Margin Classifiers, Hinge Loss and Kernel Smoothing]] — related
- [[Support Vector Classifier, Slack Budget and Hinge Loss]] — related
