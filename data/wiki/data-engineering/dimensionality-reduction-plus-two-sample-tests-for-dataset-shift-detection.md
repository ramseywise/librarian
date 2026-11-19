---
title: "Dimensionality Reduction Plus Two-Sample Tests for Dataset-Shift Detection"
tags: [data-engineering, ml-platform, concept]
summary: "Rabanser, Günnemann and Lipton compare ways of shrinking high-dimensional inputs before a two-sample test; testing a classifier's softmax outputs per dimension with a Bonferroni correction came out best in their image experiments."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-rabanser-2018-failing-loudly.md
---

# Dimensionality Reduction Plus Two-Sample Tests for Dataset-Shift Detection

The paper looks for the best pairing of a reduction step and a two-sample test when inputs are high-dimensional and samples are few, then asks whether a detected shift can be described and judged harmful or benign. The pipeline shrinks source and target samples to low-dimensional representations, then compares them with a test: MMD, a per-dimension KS test with a Bonferroni correction, chi-squared for hard labels, or a binomial test on a domain classifier's accuracy. The reductions compared are no reduction, PCA, SRP, UAE, TAE, a label classifier's outputs, and the domain classifier. Black box shift detection (BBSD) uses an off-the-shelf label classifier's outputs as the reduced representation: BBSDs takes the softmax outputs, BBSDh the hard labels.

## Results

All results below are the authors' own (self-reported). Setup: MNIST and CIFAR-10 with simulated shifts applied to the test sets only (splits of 50k/10k/10k and 40k/10k/10k respectively), alpha 0.05, mean over 5 random splits, detection measured at 8 target sample sizes.

- BBSDs (KS with Bonferroni on softmax outputs) was the best reduction for univariate testing and overall, pooled over all shifts (self-reported).
- The best multivariate setup was UAE with MMD; MMD was capped at 1,000 samples (self-reported).
- Several univariate tests with Bonferroni performed comparably to multivariate kernel tests (self-reported).
- The domain classifier with a binomial test was weak at low sample sizes and caught up as samples grew (self-reported).
- With BBSDs, large shifts were caught at better than chance level from 20 samples. A shift touching only 10% of the target was hard to catch (univariate tests, 1,000 samples), and so was the knock-out label shift, even at 1,000 samples (self-reported).
- PCA with K=32 explained about 80% of CIFAR-10 variance (CIFAR-10).

## Detected is not necessarily harmful

On COIL-100 (2,400 images each for train, validation and test, 100 classes; source angles 0 to 175 degrees, target 180 to 355) the rotation split was detected without hurting the classifier, and a shuffled split correctly passed (self-reported). Applying the method to the original MNIST train/test split, a two-sample KS test on the sixes in input space was compared with a Bonferroni threshold of 6.3e-5; the authors read this as a shift that their malignancy detector calls harmless (self-reported).

The malignancy heuristic takes the domain classifier's most anomalous samples and labels them with a labelling function; the authors report it needs far fewer labels than the full sample size (self-reported). A 2019 footnote of the paper says TensorFlow data validation looked only at summary statistics for the two samples.

## Limits

- Experiments are mostly image classification; text and graphs are left for later work.
- Online detection is left open; neighbouring time steps are correlated.
- The reduction step is surjective, so pathological shifts can slip through; the authors guess that is rare outside adversarial settings.
- The paper gives no formal definition of detection accuracy; figures pool datasets and shift strengths over just 5 splits and the tables show no variance.
- Judging harm relies on a labelling function supplied from outside, which the authors describe as a strong assumption; describing shifts and judging harm are preliminary goals.
- Shifts touching 10% of the data are hard to detect; the authors suggest outlier detection.

## See Also
- [[Drift Tests: Significance, Magnitude and False Alarms]] — prerequisite-for
- [[Multiple Comparisons Corrections]] — prerequisite-for (the Bonferroni step)
- [[PCA, NMF and Low-Rank Factorisation]] — prerequisite-for (one of the reductions compared)
- [[Autoencoder Bottleneck vs PCA and Anomaly Scores]] — prerequisite-for (autoencoder reductions)
