---
title: "Classification Metrics, Confusion Matrix and Thresholds"
tags: [foundations, reference]
summary: "Read accuracy against a dummy baseline, derive precision, recall, F1, balanced accuracy and MCC from the confusion matrix, and move the threshold on validation data."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--04-model-evaluation.md
---

# Classification Metrics, Confusion Matrix and Thresholds

Accuracy treats every mistake the same; business consequences rarely do. A false positive (Type I) and a false negative (Type II) cost different amounts: in screening a miss is very bad, in a spam filter a lost real email is bad and spam in the inbox merely annoying. The same cells apply to hypothesis testing (rejecting a true null is the false positive) and to retrieval (a relevant chunk in the top k is a true positive, the cut-off k acts as the threshold, and true negatives are so many that accuracy says nothing).

## Dummy baseline first

Relabel digits as "is it a 9?" (10% positives): always answering "not 9" scores 0.896 accuracy. A depth-2 tree scores 0.918 and logistic regression 0.984. If accuracy barely beats a `DummyClassifier`, accuracy is the wrong metric.

## Metrics from the four cells

| Metric | Formula | Optimise when |
|---|---|---|
| Accuracy | (TP+TN)/n | Balanced classes, symmetric costs |
| Precision | TP/(TP+FP) | False positives are costly |
| Recall (TPR) | TP/(TP+FN) | False negatives are costly |
| Specificity | TN/(TN+FP) | Share of negatives left alone |
| F1 | 2PR/(P+R) | One number for a rare positive class |
| Balanced accuracy | mean of recall over the two classes; 0.5 is chance | Skewed classes, no costs |
| MCC | uses all four cells; 0 is chance, 1 perfect | One number with no costs |

On the same models: always-negative has accuracy 0.896, balanced 0.500, MCC 0.000, F1 0 on the positive class; the tree 0.918 / 0.729 / 0.515; logistic 0.984 / 0.935 / 0.915. The tree's accuracy looks close to the dummy's; the other columns show the gap. Balanced accuracy is argued for because accuracy driven by an imbalanced test set drops to chance there; MCC is argued for over accuracy and F1 when a threshold is used. Neither is a cost.

Multiclass: the confusion matrix is K by K; average F1 by `macro` (classes equally), `weighted` (by support) or `micro` (samples equally, equal to accuracy for single-label). Regression: R squared for comparison; for reporting use MAE (robust), RMSE (penalises big misses) or MAPE (relative, undefined at zero).

## Moving the threshold

`predict` thresholds `decision_function` at 0 or `predict_proba` at 0.5. Moving it trades precision for recall without retraining: an SVC at threshold 0 has precision 0.978, recall 0.936; at -0.8 precision 0.758, recall 1.0. **Never pick the threshold on the test set**; use validation or CV (`TunedThresholdClassifierCV`).

Adult census example (base rate 0.241 positives): dummy accuracy 0.759, model 0.847, AUC 0.901, AP 0.754. Business rule "at least 80% of flagged must be high earners": a threshold of 0.61 picked on validation gave precision 0.783 and recall 0.484 on test, against 0.725 and 0.584 at 0.5. The validation target of 0.80 landed at 0.783 on test because a threshold picked on one sample is itself an estimate.

## See Also
- [[Precision-Recall vs ROC and Average Precision]] — extends
- [[Probability Calibration and Reliability Curves]] — extends
- [[Choosing a Metric From the Cost of Errors]] — extends
- [[Calibrated Score, Deterministic Decision Rule]] — related
