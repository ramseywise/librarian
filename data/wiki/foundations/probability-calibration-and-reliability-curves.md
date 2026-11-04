---
title: "Probability Calibration and Reliability Curves"
tags: [foundations, concept]
summary: "A score is calibrated when a 0.8 happens 80% of the time; check with a reliability diagram and Brier score, and fix on held-out data with isotonic, Platt or temperature scaling."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--04-model-evaluation.md
---

# Probability Calibration and Reliability Curves

Thresholds and expected-cost decisions assume `predict_proba` means what it says. Check with a **reliability diagram** (bin predictions, compare mean predicted to observed frequency) and the Brier score; fix with recalibration on held-out data (`CalibratedClassifierCV`: isotonic, or sigmoid/Platt for less data).

Worked case: Gaussian naive Bayes on the one-hot adult census table, a deliberately bad case. Scores pile up at 0 and 1, and only a third of the 1.0 bin is positive; Brier 0.45. Isotonic recalibration gives Brier 0.143 and predicted probabilities much nearer observed frequencies, without changing the ranking much.

## Typical miscalibration by model

| Model | Typical miscalibration |
|---|---|
| Logistic regression | Usually well calibrated |
| Naive Bayes | Pushed towards 0 and 1 |
| SVM decision function, boosted trees | Sigmoid-shaped distortion |
| Random forest | Pulled away from 0 and 1 |
| Deep networks | Often overconfident; temperature scaling (one scalar on the logits) removes the average bias, not the rest |

An overfit model reports 1.0 on points it gets wrong.

## Deep networks

On one image benchmark a 5-layer network's confidence matched its accuracy while a 110-layer network was more accurate but much more confident than right; depth, width, weight decay and batch norm all moved calibration, and temperature scaling worked best among post-hoc fixes. A later study of 180 models from 16 families (top-label expected calibration error, 100 equal-mass bins) found no general trend for recent or accurate networks to be worse calibrated, with recent non-convolutional families among the best. Three points are easy to miss:

- Temperature scaling leaves accuracy alone and corrects average over- or underconfidence; differences between families remain.
- Fitted on clean data, calibration error still grew under corruption for every family.
- Choose on accuracy and ECE together: the bin count (15 to 5,000) can flip the sign of the link between ECE and accuracy.

These are 2021 image classifiers; do not carry the ranking to other domains.

## See Also
- [[Classification Metrics, Confusion Matrix and Thresholds]] — prerequisite-for
- [[Calibrated Score, Deterministic Decision Rule]] — related
- [[Prior Shift Correction for Oversampled Defaults]] — related
