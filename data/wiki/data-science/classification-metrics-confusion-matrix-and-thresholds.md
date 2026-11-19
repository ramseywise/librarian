---
title: "Classification Metrics, Confusion Matrix and Thresholds"
tags: [data-science, reference]
summary: "Read accuracy against a dummy baseline, derive precision, recall, F1, balanced accuracy and MCC from the confusion matrix, and move the threshold on validation data."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--04-model-evaluation.md
  - data/raw/papers/2026-11-08-intro-to-ml-with-python-ch05-model-evaluation-improvement.md
  - data/raw/papers/2026-11-08-practical-statistics-for-data-scientists-ch05-classification.md
  - data/raw/papers/2026-11-08-islp-ch04-classification.md
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

## The book chapter's version

On the same 9-vs-rest digits task (test n=450: 403 negative, 47 positive), the chapter reports a confusion matrix for logistic regression (C=0.1) with 401 true negatives, 2 false positives, 8 false negatives and 39 true positives, and precision 0.95, recall 0.83 and F1 0.89 for the 'nine' class. F1 for the majority-class model was 0.00, for a dummy 0.10, for the depth-2 tree 0.55, and for logistic regression 0.89; the chapter says F1 separates models that accuracy barely distinguishes. On 10-class digits, logistic regression had accuracy 0.953, micro F1 0.953 and macro F1 0.954. Lowering an SVC threshold from 0 to -0.8 on blobs (400 vs 50, test n=113) moved class-1 recall from 0.67 up to 1.00 while precision slipped from 0.35 to 0.32. The authors advise choosing the metric closest to the business goal, comparing against a dummy baseline, tuning the threshold on validation data and fixing an operating point such as 90% recall, and passing scoring= to GridSearchCV so selection uses that metric.

## Default-data confusion matrices from Introduction to Statistical Learning

Chapter 4 of *An Introduction to Statistical Learning* uses a simulated Default set (10,000 people, 333 defaulters, about 3%). Always predicting no default errs 3.33% of the time. LDA at a 0.5 threshold errs 2.75% but misses 252 of the 333 defaulters (true negatives 9,644, false negatives 252, false positives 23, true positives 81; sensitivity 24.3%, specificity 99.8%). Dropping the threshold to 0.2 shrinks the share of defaulters missed from 75.7% to 41.4% (matrix 9,432, 138, 235, 195) but raises overall error to 3.73%. The ROC AUC is 0.95 and logistic regression's curve is almost the same. On the Caravan data (1,000 test rows) a logistic model at 0.5 predicts no buyers, while at a threshold of 0.25 it flags 29 and 31% of them buy. The authors' point is that overall error hides what a rare-class model does.

## Rare classes in the other book

Chapter 5 of *Practical Statistics for Data Scientists* (R, loan data) warns that a model predicting no purchase for a 0.1% purchaser rate is 99.9% accurate and useless (hypothetical web store), and recommends adding precision, recall, specificity, the ROC curve with its AUC, and lift once a class is rare. Lift is how well the model finds rare positives at different cutoffs; a top decile with 0.3% response against 0.1% at random has a lift of 3. Reading the ROC curve of its loan model, recall is about 75% at a specificity of at least 50%. The authors advise lowering the cutoff to find a rare class, and picking the cutoff from cost-based expected return rather than accuracy or AUC.

## Limits

- Introduction to Machine Learning with Python ch05: the examples are small and single-split, with neither variance nor significance tests on the metric comparisons; calibration and costs get only a mention, and regression metrics get one paragraph.
- Same chapter: its prose and output disagree: the dummy F-score is 0.13 in prose and 0.10 in the output.
- Same chapter: its code uses an older scikit-learn API (for example 'mean_squared_error' scorer names, where current names are neg_mean_squared_error).
- Practical Statistics ch05: numbers quoted in its text for the confusion matrix disagree with the matrix it prints, and its ROC curve was computed on training predictions, so the roughly 75% recall at a specificity of at least 50% comes from a training-set ROC. The chapter's code is R only.
- Introduction to Statistical Learning ch04: the Default data is simulated with an exaggerated balance-to-default link, as the authors say, and its matrices are computed on the 10,000 training rows, so the error rates are optimistic. The Caravan precision rests on a small flagged count (29).

## See Also
- [[Precision-Recall vs ROC and Average Precision]] — extends
- [[Probability Calibration and Reliability Curves]] — extends
- [[Choosing a Metric From the Cost of Errors]] — extends
- [[Calibrated Score, Deterministic Decision Rule]] — related
- [[LDA, QDA and Naive Bayes Generative Classifiers]] — related
