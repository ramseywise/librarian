---
title: "Precision-Recall vs ROC and Average Precision"
tags: [data-science, comparison]
summary: "ROC AUC is a ranking probability unaffected by class balance, while PR curves and average precision track the flagged set on rare positives; the two can disagree and PR points must not be linearly interpolated."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--04-model-evaluation.md
  - data/raw/papers/2026-11-08-intro-to-ml-with-python-ch05-model-evaluation-improvement.md
---

# Precision-Recall vs ROC and Average Precision

| Curve | Axes | Use when |
|---|---|---|
| Precision-recall | P vs R | Positive class rare; you care about the flagged set |
| ROC | TPR vs FPR | Ranking quality overall; balanced-ish data |

**ROC AUC** is the probability that a random positive scores above a random negative: 0.5 is chance, 1.0 perfect ranking. A random predictor scores 0.5 regardless of class balance, so AUC beats accuracy for model selection on imbalanced data. On a "is it a 9?" task, SVMs with gamma 1, 0.1 and 0.01 all have accuracy 0.90 (the dummy rate) but AUC 0.50, 0.90 and 1.00: the best ranks perfectly and only its default threshold is wrong.

**Average precision (AP)** summarises the PR curve and ignores the large pool of true negatives, so under heavy imbalance it is more informative than ROC AUC. A random ranker's AP equals the base rate (0.241 on the adult census, where the model has AUC 0.901 and AP 0.754). Always read PR as well when AUC looks high but the flagged set may be mostly false positives.

Rule of thumb: use AUC or average precision for model selection on imbalanced data, and tune the threshold separately, because ranking quality and operating point are separate decisions.

## When the two disagree

For fixed positives and negatives, one curve dominates another in ROC exactly when it dominates in PR. Once curves cross that link gives no ranking, and optimising AUC-ROC does not guarantee the area under PR. In a constructed example with 20 positives and 2,000 negatives, AUC-ROC prefers one curve (0.875 against 0.813) and AUC-PR the other (0.514 against 0.038), because PR area comes mostly from high precision at low recall. The example shows it can happen, not how often.

**Do not linearly interpolate PR points.** Precision need not change linearly with recall: from a single point at recall 0.02 with 433 positives and 56,164 negatives, a straight line gives an area of 0.50 where the correct interpolation gives 0.031. Never draw a PR curve by joining a handful of points.

## The book chapter's examples

On imbalanced blobs (4000 vs 500, SVC gamma=.05 and a 100-tree random forest), the chapter reports F1 preferring the SVC (0.656 against 0.610) and average precision slightly preferring the forest (0.666 against 0.663), with AUC 0.937 for the forest and 0.916 for the SVC. On 9-vs-rest digits, three SVMs with 90% accuracy had AUCs of 0.50, 0.90 and 1.00 for gamma 1, 0.05 and 0.01 respectively; 3-fold CV AUC for a default SVC was 0.994, 0.99 and 0.996 against accuracy 0.9 in every fold. Selecting gamma with AUC gave 0.01 and with accuracy gave 0.0001, and the AUC choice scored higher on test AUC and test accuracy. Its authors advise preferring AUC or average precision to accuracy when classes are imbalanced, feeding them scores (decision_function or predict_proba) instead of hard predictions.

## Limits

The chapter's examples are small and single-split with no significance on the comparisons. Its prose says the gamma=0.05 SVM has AUC 0.5 while its output shows 0.90; the page follows the output. The course note gives gamma 0.1 for the middle SVM where the chapter gives 0.05, for the same AUCs; the page cannot tell which is right. Its code uses an older scikit-learn API.

## See Also
- [[Classification Metrics, Confusion Matrix and Thresholds]] — prerequisite-for
- [[Choosing a Metric From the Cost of Errors]] — related
