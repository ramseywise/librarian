---
title: "Autoencoder Bottleneck vs PCA and Anomaly Scores"
tags: [data-science, comparison]
summary: "An autoencoder beats PCA on reconstruction only at tight codes (2 to 8 dims) and loses at 32, a denoising variant trades clean accuracy for repair, and the best reconstruction is not the best anomaly detector: compute PCA first."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--05-sequence-models.md
  - data/raw/papers/2026-11-08-fundamentals-of-deep-learning-ch06-embedding-representation-learning.md
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

## A textbook MNIST run with a 2-D code (Fundamentals of Deep Learning, chapter 6)

The chapter recreates the Hinton and Salakhutdinov MNIST setup: a sigmoid autoencoder with batch norm (Adam, learning rate 0.001) and a 2-neuron code reaches validation L2 reconstruction cost 4.78 after about 200 epochs. To judge that number it gives yardsticks from one arbitrary image of a 1: its mean L2 distance to other 1s is 5.75, to the nearest other class (7s) 8.94 and to the farthest (0s) 11.05. Qualitatively, 2-D autoencoder codes cluster by digit while 2-D PCA codes do not (PCA mixes up 5, 3 and 8, 0 and 8, and 4 and 9, and the autoencoder looks like PCA after just 5 epochs). With 30-dimensional codes the chapter says PCA improves a lot but remains significantly worse than the autoencoder, with no numbers.

Other mechanisms it covers: a denoising autoencoder zeroes a fixed fraction of input pixels (its code corrupts about half) and reconstructs the clean image, which the authors advise as regularisation for robust codes; and a sparsity penalty (beta times a KL-divergence penalty against a zero-mean target) is advised when the code layer is as wide as the input, since otherwise the net can simply learn to copy. It cites k-sparse autoencoders as effective and cheaper, with no experiment of its own. It advises sigmoid, not ReLU, when codes will be visualised.

## Limits

- The PCA comparison is visual; the 30-d claim has no figures, and no downstream classifier accuracy is reported.
- The encoder function, hidden sizes, batch size and epoch count are not printed.
- The sparsity section gives no implementation or results. Code is Python 2 with TensorFlow 0.x.

## See Also
- [[Seq2seq Bottleneck and Attention]] — related
- [[Contrastive Self-Supervised Pretraining]] — related
- [[Dropout and Input Distortion as Ridge Regression]] — related
