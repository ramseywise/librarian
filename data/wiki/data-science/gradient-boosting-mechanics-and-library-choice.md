---
title: "Gradient Boosting Mechanics and Library Choice"
tags: [data-science, comparison]
summary: "Boosting fits shallow trees to loss gradients; the main libraries tie on accuracy within seed noise, so choose by speed, categorical and missing-value handling, and tune rounds by early stopping."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--06-ensembles.md
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--07-boosting-in-practice.md
  - data/raw/papers/2026-11-07-chen-2016-xgboost.md
  - data/raw/papers/2026-11-07-prokhorenkova-2017-catboost.md
  - data/raw/papers/2026-11-08-karbasi-2023-impossibility-parallelizing-boosting.md
  - data/raw/papers/2026-11-08-practical-statistics-for-data-scientists-ch06-statistical-machine-learning.md
  - data/raw/papers/2026-11-08-islp-ch08-tree-based-methods.md
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch17-random-forests-boosting.md
---

# Gradient Boosting Mechanics and Library Choice

## Mechanism

Fit a shallow tree, take the negative gradient of the loss at the current prediction (residuals for squared error, y - p for log-loss), fit the next tree to it, add it scaled by a learning rate eta, repeat: gradient descent in function space. Shallow trees (depth 1 to 5) mean high bias, low variance; depth d captures interactions of up to d features. Unlike a forest ([[Random Forests and Bagging]]), too many rounds overfit.

Modern libraries use second-order statistics. With first and second derivatives g and h of the loss, and penalties on leaf count and leaf weight (lambda), a leaf's best weight is minus the sum of g over the sum of h plus lambda: a Newton step. For squared error g is the residual and h is 1, so the weight is a shrunken mean of residuals. A hand computation matched a real one-tree model exactly (-1.1513 and 1.1729 on 472 and 528 rows). Boosting is sequential by nature. Karbasi and Larsen (2023) prove a worst-case lower bound: a weak-to-strong learner that uses few rounds of weak-learner calls must make exponentially many queries per round to match AdaBoost's error, and their single-round algorithm needs exp(O(d gamma^-2 ln m)) queries, so it is not practical. The result is purely theoretical and leaves out parallelism within a single weak learner, such as parallel split finding in a tree, which is the kind libraries use ([[XGBoost System Design: Sparsity-Aware Splits, Quantile Sketch and Cache-Aware Blocks]] — extends).

## Benchmark: libraries tie

Adult census (32,561 rows, two columns dropped), learning rate 0.05, up to 2,000 rounds, patience 50, 20% test, five seeds, defaults otherwise:

| Model | AUC | Log-loss | Seconds | Rounds |
|---|---|---|---|---|
| Majority class | 0.5000 | 0.5519 | 0.0 | 0 |
| Random forest (300, one-hot) | 0.8969 | 0.4018 | 0.8 | 300 |
| sklearn GradientBoosting | 0.9294 | 0.2769 | 15.7 | 975 |
| sklearn HistGradientBoosting | 0.9291 | 0.2765 | 3.3 | 285 |
| XGBoost `hist` | 0.9292 | 0.2766 | 0.5 | 255 |
| LightGBM | 0.9295 | 0.2758 | 0.6 | 230 |
| CatBoost | 0.9297 | 0.2761 | 5.9 | 666 |

The best-to-worst AUC gap is 0.0006 while one model moves about 0.003 between seeds; no library wins every seed, so a single-split claim of a winner reads noise. Boosting beats the untuned forest by about 0.03 AUC, and the forest's log-loss gap is larger because log-loss punishes confident mistakes (check [[Probability Calibration and Reliability Curves]]). Speed varies about 30x: histogram libraries bin once while the classic booster sorts every feature at every node. Published benchmarks find tree models still lead neural nets on medium-sized (about 10K) tabular data. A library's own benchmark showing a lead for itself was not reproduced here (untuned, the gap is inside noise).

## Choosing

| | sklearn HGB | XGBoost | LightGBM | CatBoost |
|---|---|---|---|---|
| Growth | Leaf-wise | Depth-wise | Leaf-wise | Symmetric (same split per level) |
| Size knob (default) | `max_leaf_nodes` 31 | `max_depth` 6 | `num_leaves` 31 | `depth` 6 |
| Categoricals | Native, up to 255 levels | `enable_categorical` | Native | Ordered target statistics |
| Missing values | Native | Learned default direction | Native | Numeric yes |

HistGradientBoosting (features binned into at most 255 values, early stopping on by default above 10k rows) is the no-extra-dependency choice; on one split it reached AUC 0.9269 in 193 rounds against 0.8958 for a forest. XGBoost or LightGBM for GPU, monotonic constraints, custom objectives, very large data; CatBoost for small data with many categoricals. Leaf-wise growth can make one side of a tree about 30 levels deep, so cap `num_leaves` or `min_child_samples` on small data.

## Target leakage in categorical encoding

Replacing a level with its target mean leaks each row's own label; for a per-row unique ID the encoding is the label. With a meaningless ~3,000-level ID: no ID test AUC 0.927; greedy mean encoding train 0.967, test 0.811; ordered encoding (each row encoded from earlier rows in a random order) test 0.925. An encoding built from the target has to be fitted out of fold; see [[Categorical Encoding Choices]] and [[Pipelines Prevent Preprocessing Leakage]]. Ordered boosting extends the idea to residuals ("prediction shift"), helping most on small data but not free (plain mode had lower log-loss on four of nine datasets, ordered costs about 1.7x time on one); see [[Ordered Boosting and Ordered Target Statistics]] for the mechanism and the paper's setup.

## Tuning order

Fix the learning rate, let early stopping pick rounds, then tune tree size, leaf size, sampling, penalties. On this table lr 0.3, 0.1, 0.05, 0.02 gave 21, 100, 215, 509 rounds with AUC 0.9252 to 0.9270; leaves 4 to 128 gave 1417 down to 84 rounds, AUC 0.9243 to 0.9270. The whole search moved AUC under 0.003 (seed-noise size) while rounds changed 17-fold, so spend time on features and leakage first. Never grid `n_estimators` with learning rate. Column subsampling effects are data dependent (0.5 lowered AUC on one set, raised NDCG on another). Report search scores only with a reserved test set or [[Cross-Validation Variants and Nested Search]].

Pitfalls: early stopping on the test set; `class_weight` raises log-loss (0.280 to 0.328) and lowers accuracy (0.874 to 0.838) while AUC barely moves (0.9270 to 0.9256); train and serving category dtypes differing; fixing one lucky seed.

## Book example: regularising XGBoost

In chapter 6 of *Practical Statistics for Data Scientists* (R, Lending Club loan data, 250 rounds, 10,000 random test records, the rest for training), a default XGBoost fit overfits, with training error well under test error. Setting lambda = 1000 (eta 0.1, subsample 0.63) lifts the training error to 33.2% and brings the test error down to 34.8%. A 5-fold cross-validation over eta in {0.1, 0.5, 0.9} and max_depth in {3, 6, 12} (100 rounds) selects eta 0.1 with depth 3 (or 6); the worst cell is eta 0.9 at depth 12. The authors advise a small eta with more rounds, shallow trees, subsampling and lambda or alpha regularisation, tuned by cross-validation.

## Depth, shrinkage and BART in two more books

- Introduction to Statistical Learning ch08 advises a shrinkage of 0.01 or 0.001, small trees (depth 1 stumps give an additive model and often work well) and the number of trees chosen by cross-validation. Its Boston lab (70/30 split, 5,000 trees, depth 3) gives test MSE 14.48 at rate 0.001 and 14.50 at 0.2, so shrinkage barely mattered there. On Heart data boosting overfits, its test error climbing past a few hundred iterations.
- Same book, gene data collapsed to cancer versus normal (rate 0.01, up to 5,000 trees): depth 1 slightly beat depth 2 and both beat a forest, but the standard error is about 0.02, so the authors treat the differences as not significant.
- Computer Age Statistical Inference ch17, ALS data (1,197 training rows, 369 predictors, 625 test rows, shrinkage 0.02): depth 4 is about best, depth 1 is worse, and depth 7 overfits from roughly 200 trees against roughly 300 for depth 4. That contrasts with the stump advice above, so depth is data dependent. On a subset with depth 3, a shrinkage of 0.02 reached lower validation error than 0.5 and overfitted much later, at the price of many more trees. Trees of depth d give an interaction model of order d minus 1, and the R gbm package fits each tree on a random half of the rows by default.
- Boosting beat the forest by a small margin on ALS but needed time-costly tuning. AdaBoost as stagewise exponential-loss fitting is covered in [[AdaBoost as Stagewise Exponential-Loss Fitting]].
- BART: the ISLP authors recommend 200 trees, 1,000 iterations and a 100-iteration burn-in; on Heart its error stabilises once burn-in is discarded, with train and test close. Its Boston run used a burn-in of 5 and 15 draws and scored test MSE 20.92, similar to the forest.

## Limits

- The chapter's runs are single and unseeded on one dataset, its code uses older xgboost syntax, and as a 2017 text it predates LightGBM and CatBoost.
- Introduction to Statistical Learning ch08: results are single random splits that shift with the seed; boosting for classification is omitted and BART is shown for regression only; the lab text gives the scikit-learn default learning rate as 0.001, which the extraction could not verify (the current default is commonly cited as 0.1).
- Computer Age ch17: ALS and spam data only, no repeats or error bars, and the ALS errors are read off plots; it uses R gbm, so it predates XGBoost-style libraries.

## See Also
- [[Random Forests and Bagging]] — alternative-to
- [[Ordered Boosting and Ordered Target Statistics]] — extends
- [[XGBoost System Design: Sparsity-Aware Splits, Quantile Sketch and Cache-Aware Blocks]] — extends
- [[Regularisation Knobs and Early Stopping]] — related
- [[Hyperparameter Search Budgets and Selection Optimism]] — related
- [[Tree Ensemble Interpretation Beyond Impurity Importance]] — extends
- [[Bias-Variance Decomposition and Model Complexity]] — prerequisite-for
- [[Supervised Model Families and Complexity Knobs]] — related
- [[AdaBoost as Stagewise Exponential-Loss Fitting]] — instance-of
