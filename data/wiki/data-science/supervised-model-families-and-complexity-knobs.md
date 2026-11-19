---
title: "Supervised Model Families and Complexity Knobs"
tags: [data-science, reference]
summary: "Each classical supervised family has one knob that sets its complexity, a typical strength and a typical failure; sweep the knob first and start with a simple model."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--02-supervised-learning.md
  - data/raw/papers/2026-11-08-intro-to-ml-with-python-ch02-supervised-learning.md
  - data/raw/papers/2026-11-08-python-data-science-handbook-ch05-machine-learning.md
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

## One textbook's numbers on the breast-cancer data

Müller and Guido (2016) run each family on the Wisconsin Breast Cancer data (569 rows, 30 features) with 2016-era scikit-learn defaults. The split changes between experiments, so the rows below are not a leaderboard.

| Model and setting | Train | Test | Split |
|---|---|---|---|
| Decision tree, grown until pure | 1.000 | 0.937 | stratified, random_state=42 |
| Same tree, `max_depth=4` | 0.988 | 0.951 | same |
| Random forest, 100 trees, no tuning | 1.000 | 0.972 | `random_state=0` |
| Gradient boosting, defaults (100 trees, depth 3, rate 0.1) | 1.000 | 0.958 | `random_state=0` |
| Gradient boosting, `max_depth=1` | 0.991 | 0.972 | same |
| Gradient boosting, `learning_rate=0.01` | 0.988 | 0.965 | same |
| MLP on unscaled features | 0.92 | 0.90 | `random_state=0` |
| MLP after standardising | 0.991 | 0.965 | same |
| MLP standardised, `alpha=1`, `max_iter=1000` | 0.988 | 0.972 | same |

For k-NN, test accuracy over `n_neighbors` 1 to 10 (stratified split, `random_state=66`) peaks near six, with one neighbour too complex and ten too simple; the worst setting is about 88%. On small synthetic sets, 3-NN scores 0.86 test accuracy on the 26-point forge classification data and R squared 0.83 on 40 samples of the wave regression data. In a depth-4 tree on the cancer data, "worst radius" carries feature importance 0.727, and importances sum to 1.

A tree regressor fitted to RAM price history before the year 2000 and tested from 2000 on keeps predicting the last training value (a qualitative figure, with the target log-transformed). A weight count shows why networks grow quickly: a binary classifier with 100 inputs and two hidden layers of 100 units has 20,100 weights, and two layers of 1,000 units has 1,101,000, about 50 times more (biases not counted).

The authors advise a few things beyond the table: try 3 or 5 neighbours for k-NN and use it as a baseline; use naive Bayes as a baseline on very large high-dimensional sparse count data, where the multinomial variant usually beats the Bernoulli one on long documents; for boosting, fix the number of trees from the time and memory budget, then search the learning rate, and keep depth at five or less; try a random forest before boosting.

## Baselines first (Python Data Science Handbook)

VanderPlas advises starting with naive Bayes as a fast baseline with few tunable parameters, and turning to SVMs only once simpler methods have fallen short. It is practical advice with no experiment behind it in the chapter.

## Limits

- The chapter reports one train/test split per experiment, with no cross-validation or intervals. A 0.01 accuracy gap on 143 test points is a few samples, and several models make the same four mistakes (its footnote 12).
- Parameters such as `alpha` and `C` are picked by looking at test scores, and proper tuning is postponed to a later chapter on model evaluation.
- The kNN and tree figures in the notes above come from a different split than the chapter's (for example an unpruned tree at 0.895 test above, 0.937 in the chapter), so the two sets of numbers are not comparable.
- The data are small and synthetic to moderate (26 to 569 points); the authors concede that intuition from low dimensions may not transfer.
- The chapter's API is dated (`load_boston` is gone from scikit-learn 1.2, the MLP `algorithm` argument is now `solver`, the RBF `gamma` default changed), and so is some advice (xgboost "faster at the time of writing", deep-learning library recommendations). Boston Housing is ethically problematic and was removed from scikit-learn.
- The chapter's text has slips: the Gaussian kernel is written without the minus sign, and the hidden-unit formula reuses the same weights for three units.

## See Also
- [[Penalised Linear Models: Ridge, Lasso and Elastic Net]] — extends
- [[Kernel SVM and the Kernel Trick]] — extends
- [[Random Forests and Bagging]] — extends
- [[Bias-Variance Decomposition and Model Complexity]] — prerequisite-for
- [[Kolmogorov-Arnold Networks]] — related
- [[XGBoost System Design: Sparsity-Aware Splits, Quantile Sketch and Cache-Aware Blocks]] — related
- [[LDA, QDA and Naive Bayes Generative Classifiers]] — extends
- [[Cost-Complexity Pruning of Decision Trees]] — extends
- [[Density Estimators: KDE Bandwidth, GMM Components and the Generative Classifier]] — related
