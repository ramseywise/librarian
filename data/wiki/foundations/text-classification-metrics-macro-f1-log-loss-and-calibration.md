---
title: "Text Classification Metrics: Macro-F1, Log-Loss and Calibration"
tags: [foundations, concept]
summary: "Which metric fits which text task: macro-F1 exposes ignored small classes, log-loss punishes overconfident Naive Bayes, and multi-label needs micro versus macro averages and per-label thresholds."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--03-nlp--notes--02-text-classification.md
---

# Text Classification Metrics: Macro-F1, Log-Loss and Calibration

Class distributions in text are skewed, so the headline metric decides which model looks best. The baseline models are in [[Linear Text Classifiers and the TF-IDF Baseline]].

| Situation | Metric |
|---|---|
| Balanced topics | Accuracy, macro-F1 |
| Rare positive (spam, toxicity, fraud) | Precision and recall at an operating point, PR-AUC |
| Calibrated probabilities matter | Multiclass log-loss |
| Multi-label | Per-label ROC-AUC averaged, micro and macro F1 |

## Macro-F1 versus accuracy

On a six-genre task (960 test documents, majority share 0.315), accuracy 0.532 hides the confusion table: only 2 of 49 Crime films are found, and Adventure leaks into Action. Large classes carry accuracy while two small classes are barely predicted, which macro-F1 flags. Read the confusion table to see which class pairs the model cannot separate, then read the missed rows before changing anything. Errors between neighbouring classes (Drama and Comedy on mixed-genre items) are often label ambiguity, not model failure.

## Log-loss and overconfidence

Multiclass log-loss punishes confident mistakes without limit, so clip probabilities (about 1e-15) and renormalise. It can rank models differently from accuracy. In a grid search on the genre task, an SVD-plus-logistic-regression pipeline reached CV log-loss 1.325, while Naive Bayes ranged from 9.303 (alpha 0.01) through 6.025 (0.1) and 5.010 (0.3) to 5.485 (1.0), despite respectable accuracy: Naive Bayes is badly overconfident. In a separate competition ladder, tuning the smoothing alpha gave an 8% log-loss improvement. Tune on the metric you will be judged by. See [[Probability Calibration and Reliability Curves]] if probabilities feed a later decision.

## Multi-label

Films have several genres, so one-vs-rest logistic regression with one sigmoid per label is the honest framing. On 17 genres with at least 100 films: micro-F1 0.484 (carried by Drama at 0.68, Comedy 0.62, Action 0.54), macro-F1 0.274, with Documentary and Music at 0.0 at the default 0.5 threshold. Fix first with per-label thresholds or `class_weight="balanced"`.

## See Also
- [[Linear Text Classifiers and the TF-IDF Baseline]] — prerequisite-for
- [[Tabular ML Leakage Taxonomy]] — related
