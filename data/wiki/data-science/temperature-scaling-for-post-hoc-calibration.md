---
title: "Temperature Scaling for Post-Hoc Calibration"
tags: [data-science, pattern]
summary: "Temperature scaling divides a trained classifier's logits by one scalar T, fitted by negative log-likelihood on held-out data; it leaves predictions unchanged and cut ECE sharply on 2017 image benchmarks (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-guo-2017-calibration-modern-neural-networks.md
  - data/raw/papers/2026-11-07-minderer-2021-revisiting-calibration-modern-neural-networks.md
---

# Temperature Scaling for Post-Hoc Calibration

Guo and colleagues (2017) ask which post-processing method best fixes the miscalibration of modern neural networks. Their answer is temperature scaling, a single-parameter version of Platt scaling ([[Platt Scaling for SVM Probabilistic Outputs]]). It was introduced as a calibrator for classifiers, with the network frozen.

## Mechanism

1. Train the network as usual and keep its logits z_i.
2. On a held-out validation set, fit one scalar T > 0 by minimising negative log-likelihood. The extraction describes a convex search over one variable that converged in roughly ten iterations of the conjugate-gradient routine, in well under a second.
3. At prediction time the confidence is the largest entry of softmax(z_i / T).

Because dividing every logit by the same T does not change which logit is largest, the predicted class never changes and accuracy is untouched. The paper contrasts this with histogram binning, isotonic regression and BBQ, which can change class predictions and hurt accuracy. Vector and matrix scaling are strictly more general extensions.

## Results (self-reported)

Setup: top-label ECE with 15 bins on test sets, T fitted on a held-out validation set, single run per setting.

- CIFAR-100, ResNet 110: ECE from 16.53% to 1.26% (validation set of 5,000 images).
- CIFAR-10, ResNet 110: 4.6% to 0.83%.
- ImageNet, ResNet 152: 5.48% to 1.86% (25,000 validation images).
- Temperature scaling beat the other calibrators on the vision tasks and was comparable on the text datasets. It beat vector and matrix scaling although they are more general: vector scaling learned nearly constant entries, and matrix scaling did poorly with hundreds of classes and did not converge on 1000-class ImageNet.
- On CIFAR-100 (conjugate gradient, K = 100), vector scaling took at least two orders of magnitude longer than temperature scaling, and BBQ about three orders.

## What later work adds

Minderer and colleagues (2021) evaluate public pretrained image classifiers on ImageNet and shifted sets, fitting T on 20% of the ImageNet validation set. They report that temperature scaling reveals trends hidden by over- or underconfidence: ranks depend on the ECE variant, but the Pareto-optimal families do not. Under shift (ImageNet-C, five severities, T fitted on a clean 20% ImageNet hold-out), larger models' calibration was more robust, and once temperature-scaled, most families show that trend by size reversed. They found label smoothing makes models artificially underconfident, and without it plus temperature scaling gave the lowest ECE across ImageNet-C severities (EfficientNet-B4, five smoothing levels). They found no general trend for recent or more accurate networks to be poorly calibrated, against the 2017 finding that larger, more accurate networks are worse calibrated; the extraction's lineage marks Minderer as contradicting Guo.

## Limits

- Guo et al.: single run per setting with no seeds or confidence intervals; optimiser and training hyperparameters are not restated. Only top-label, equal-width 15-bin ECE; 2015-2016 architectures.
- Every calibrator needs held-out data drawn from the test distribution; the 2017 paper studies no distribution shift. Temperature scaling did not improve Reuters, and the authors suggest the split or binning may affect that measurement.
- MCE is very sensitive to binning and unsuitable for small test sets. Minderer et al. also report the sign of the ECE-versus-error link flipping with bin count.
- Minderer et al.: image classification at ImageNet scale only; the extraction notes the ECE estimates are biased and that model rankings change with the variant; training hyperparameters of the evaluated models are not given. The extraction's counts of the released dataset (180 models in 16 families) differ from the 7 families in the main text and 8 in its Table 1.
- Causality of depth, width, weight decay and Batch Normalization effects is not claimed; the 2017 paper leaves the reason to future work.

## See Also
- [[Platt Scaling for SVM Probabilistic Outputs]] — prerequisite-for
- [[Probability Calibration and Reliability Curves]] — prerequisite-for
