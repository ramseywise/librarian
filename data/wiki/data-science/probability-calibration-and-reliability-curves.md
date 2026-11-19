---
title: "Probability Calibration and Reliability Curves"
tags: [data-science, concept]
summary: "A score is calibrated when a 0.8 happens 80% of the time; check with a reliability diagram and Brier score, and fix on held-out data with isotonic, Platt or temperature scaling."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--04-model-evaluation.md
  - data/raw/papers/2026-11-07-guo-2017-calibration-modern-neural-networks.md
  - data/raw/papers/2026-11-07-minderer-2021-revisiting-calibration-modern-neural-networks.md
  - data/raw/papers/2026-11-08-van-den-goorbergh-2022-harm-class-imbalance-corrections.md
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

Expected calibration error (ECE) is the average over equal-width bins of the gap between accuracy and mean confidence, weighted by bin size; MCE is the largest bin gap (Guo et al., 2017). On CIFAR-100 a 110-layer ResNet was more accurate than a 5-layer LeNet but over-confident. Raising depth, width or Batch Normalization, or lowering weight decay, each increased ECE, and temperature scaling beat the other post-hoc calibrators on the vision tasks ([[Temperature Scaling for Post-Hoc Calibration]]); the authors do not claim these factors are causal. Minderer et al. (2021) released calibration measurements for 180 models from 16 families (top-label ECE, 100 equal-mass bins) and found nothing indicating that newer or more accurate networks are generally worse calibrated; MLP-Mixer, ViT and BiT were both accurate and well calibrated. Three points are easy to miss:

- Temperature scaling leaves accuracy alone and corrects average over- or underconfidence; differences between families remain.
- Calibration under ImageNet-C corruption decayed more slowly for MLP-Mixer and ViT than for other families.
- Choose on accuracy and ECE together: the bin count (15 to 5,000) can flip the sign of the link between ECE and accuracy.

## Calibration after imbalance correction

van den Goorbergh et al. (2022) trained standard and ridge logistic regression after random under-sampling, random over-sampling and SMOTE. Uncorrected models had median calibration intercepts near zero; corrected ones had -4.5 or lower at 1% events, and an intercept-only logistic recalibration restored them to between -0.07 and 0.03 (simulation, 24 scenarios, 2000 runs each). See [[SMOTE: Synthetic Minority Over-sampling]].

## Limits

The image results are 2021 and 2017 image classifiers (ImageNet-scale data); do not carry the ranking to other domains. Guo et al. report a single run per setting with 15-bin equal-width ECE, and the estimators are biased (Minderer et al.), with rankings depending on the ECE variant. The imbalance simulation covers only logistic regression with equal-strength predictors. The Minderer extraction's count of the released dataset (180 models in 16 families) differs from the 7 families in the main text and 8 in its Table 1.

## See Also
- [[Classification Metrics, Confusion Matrix and Thresholds]] — prerequisite-for
- [[Calibrated Score, Deterministic Decision Rule]] — related
- [[Prior Shift Correction for Oversampled Defaults]] — related
- [[Confidence-Gated Escalation]] — extends (calibration measured per task for an LLM gate)
- [[MC Dropout]] — related (an uncertainty estimate whose calibration is a separate check)
- [[Platt Scaling for SVM Probabilistic Outputs]] — instance-of
- [[Temperature Scaling for Post-Hoc Calibration]] — extends
- [[SMOTE: Synthetic Minority Over-sampling]] — related (resampling distorts probabilities)
