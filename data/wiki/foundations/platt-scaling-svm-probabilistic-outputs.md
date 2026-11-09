---
title: Platt Scaling for SVM Probabilistic Outputs
tags: [foundations, pattern]
summary: "Platt scaling fits a two-parameter sigmoid P(y=1|f)=1/(1+exp(Af+B)) by maximum likelihood on held-out SVM outputs, with smoothed targets, so a sparse SVM yields calibrated posteriors; in 1999 tests it made fewer errors than a raw SVM on some tasks and was neither better nor worse than a regularized-likelihood machine overall (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-platt-1999-probabilistic-outputs-support-vector-machines.md
---

# Platt Scaling for SVM Probabilistic Outputs

Platt (1999 preprint) asks how to turn an SVM's uncalibrated output f into a posterior P(y=1|x) without losing the sparse solution. The hypothesis is that a sigmoid with two parameters, fitted discriminatively to the outputs, follows the empirical posterior and yields probabilities about as good as those of a kernel machine trained by regularized likelihood.

## Mechanism

1. Train the SVM unchanged.
2. Get unbiased outputs f_i from three-fold cross-validation or a held-out set. Outputs on the SVM's own training data are biased, most of all for non-linear SVMs.
3. Fit the two sigmoid parameters A and B, in P(y=1|f) = s(-(A*f + B)) where s is the logistic function, by minimising cross-entropy with a Levenberg-Marquardt style model-trust optimiser. The assumption is that the SVM output grows in proportion to the log odds of the positive class.
4. Replace hard 0 and 1 targets with the Bayes-motivated t+ = (N+ + 1)/(N+ + 2) and t- = 1/(N- + 2) to guard against overfitting.

The paper's qualitative check bins a linear SVM's outputs on the UCI Adult data into 0.1-wide bins, applies Bayes rule, and finds that a sigmoid fits that non-parametric posterior well even beyond the margins. Class-conditional densities were not Gaussian and showed discontinuities at f = +1 and f = -1.

## Results (self-reported)

Setup: Table 2, five task configurations from three datasets (Reuters, Adult, Web), 5% significance, error counts and test negative log likelihood, comparing a raw SVM with a regularized-likelihood kernel machine.

- Reuters linear: raw SVM 1043 errors, SVM plus sigmoid 963 (significantly better), regularized likelihood 1060.
- Adult quadratic: 2626, 2554 (significantly better), 2610. Adult linear: 2441, 2442, 2434.
- Web linear: 260, 265, 248; Web quadratic: 444, 452, 507.
- Neither method dominates: the sigmoid made fewer errors on 3 of 5 tasks while regularized likelihood gave significantly better probabilities on 3 of 5.
- On Adult quadratic the P = 0.5 point corresponds to f = -0.1722, so f = 0 need not be the Bayes-optimal threshold for a raw SVM, particularly if the two classes are very unevenly represented.

## Limits

- Binary SVMs only; no reliability diagram or expected calibration error, just error counts and test log likelihood.
- The sigmoid shape and smoothed targets are justified empirically and by a MAP argument, with no theory for the class-conditional densities. The sigmoid averages over other feature-space directions.
- A hold-out set or cross-validation costs 1.5x to 2.2x extra. The paper is from 1999; any mapping to neural nets or language-model confidence is the reader's, not the paper's.

## See Also
- [[Probability Calibration and Reliability Curves]] — prerequisite-for
- [[Kernel SVM and the Kernel Trick]] — prerequisite-for
- [[LLM Grader Calibration Insights]] — related
