---
title: Cost-Complexity Pruning of Decision Trees
tags: [data-science, classical-ml, concept]
summary: "ISLP grows a large tree and prunes it along a one-parameter family of subtrees indexed by alpha, picking alpha by k-fold CV; on its Boston example the pruned single tree has about twice the test MSE of a bagged forest."
updated: 2026-11-20
sources:
  - data/raw/papers/2026-11-08-islp-ch08-tree-based-methods.md
---

# Cost-Complexity Pruning of Decision Trees

A decision tree splits the predictor space into regions. ISLP's Chapter 8 grows a large tree and then prunes it.

## The pruning step

**Cost-complexity pruning** considers a sequence of subtrees indexed by a non-negative tuning parameter alpha instead of every possible subtree: for each alpha it picks the subtree T that minimises RSS plus alpha times the number of leaves |T|. The book's Algorithm 8.1 grows the large tree, finds the best subtree for each alpha and chooses alpha by K-fold cross-validation. For growing a classification tree the authors use the **Gini index** G, which sums p_mk times (1 - p_mk) over classes and measures node purity, or entropy; they use the classification error rate for pruning when accuracy is the goal. Trees are compared with linear models by CV or validation error, and the linear model wins if the truth is linear.

## Worked results

- Hitters (log Salary, nine features, a random 132/131 train/test split, 6-fold CV): CV error was lowest at 3 leaves while the test error was lowest at 10 leaves. The three-leaf tree gives players with Years under 4.5 a mean log salary of 5.107, about $165,174.
- Heart (303 patients, 13 predictors, binary HD): CV chose a tree with six terminal nodes.
- Carseats (Sales above 8 labelled High, 50/50 split): an unpruned tree scored 73.5% test accuracy and the CV-pruned 30-leaf tree 72.0%, with CV accuracy 68.5% (10-fold over the ccp_alpha path). A depth-3 entropy tree fit on the full data had training accuracy 0.7275 and got 68.5% right on 200 test points.
- Boston (medv, 30% test, 5-fold CV over ccp_alpha): the pruned depth-3 regression tree had test MSE 28.07. On a 70/30 split, bagging gave 14.63 with 100 trees and 14.61 with 500, a random forest with max_features = 6 gave 20.04, boosting (5,000 trees, learning rate 0.001, depth 3) gave 14.48 and BART gave 20.92.

The authors judge single trees weak on accuracy and fragile, and say ensembles trade interpretability for accuracy. In the lab, the dominant Boston random-forest importances were lstat (0.3687) and rm (0.3338).

## Limits

- The lab results are single random splits, and the authors note they change with the seed; they are not benchmarks.
- sklearn trees see each one-hot level as its own variable and cannot split natively on a categorical.
- The Boston ensemble figures use one 70/30 split, so the gap between the forest at max_features = 6 and bagging may not hold on another split.

## See Also
- [[Supervised Model Families and Complexity Knobs]] — prerequisite-for
- [[Random Forests and Bagging]] — extends
- [[Cross-Validation Variants and Nested Search]] — related
