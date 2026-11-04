---
title: "Autoencoder Bottleneck vs PCA and Anomaly Scores"
tags: [foundations, comparison]
summary: "An autoencoder beats PCA on reconstruction only at tight codes (2 to 8 dims) and loses at 32, a denoising variant trades clean accuracy for repair, and the best reconstruction is not the best anomaly detector: compute PCA first."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--05-sequence-models.md
---

# Autoencoder Bottleneck vs PCA and Anomaly Scores

An encoder maps input to a small code, a decoder rebuilds the input, and the loss is input versus output, so no labels are needed. A narrow code prevents copying, so the model learns what is regular. It is a non-linear generalisation of PCA; the original result on MNIST at code 30 was squared error 3.00 against 13.87 for PCA.

## Versus PCA (8x8 digits, 1,797 images, held-out squared error, five splits)

| Code | Autoencoder | PCA |
|---|---|---|
| 2 | 2.807 | 3.399 |
| 4 | 1.739 | 2.432 |
| 8 | 1.233 | 1.569 |
| 16 | 0.764 | 0.738 |
| 32 | 0.315 | 0.171 |

The non-linear model wins only where the code is tight; at 32 PCA wins with far less run-to-run variation and no training. PCA is the baseline and may be enough.

## Denoising

Zero a random share of the input during training and ask for the clean version: copying fails even with a code wider than the input, so corruption replaces the bottleneck. Wide net (256 units), 30% of pixels zeroed: doing nothing scores 4.495; the plain network gets 0.077 clean but 3.771 corrupted (it copies the holes); the denoising one 0.545 clean and 0.927 corrupted. It pays with worse clean reconstruction because it learned a different job.

## Reconstruction error as an anomaly score

Train on normal data; the error becomes a score. Hide one digit from training and measure AUC for spotting it, mean over ten digits: autoencoder 0.902, 0.954, 0.956, 0.954, 0.910 at codes 2, 4, 8, 16, 32; PCA 0.785, 0.798, 0.885, 0.839, 0.743. Digit 1 was hardest (0.848 at code 16). Widening the code keeps improving reconstruction but hurts detection, since a code that can rebuild everything rebuilds anomalies too. Choose code size on labelled anomalies, not reconstruction error. For tabular anomalies try an isolation forest or a Gaussian first.

## See Also
- [[Seq2seq Bottleneck and Attention]] — related
- [[Contrastive Self-Supervised Pretraining]] — related
