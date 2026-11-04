---
title: "Convolution, Shift Sensitivity and Parameter Sharing"
tags: [foundations, concept]
summary: "A convolution reuses one small filter at every position (sharing plus sparse connections), so it survives shifts that wreck an MLP, but pooling and the final linear layer keep it from true invariance; augmentation buys invariance only for the shifts shown."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--04-convolutional-networks.md
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--03-structuring-ml-projects.md
---

# Convolution, Shift Sensitivity and Parameter Sharing

## Mechanism

A filter slides over the input taking a dot product at each position. Two consequences an MLP lacks: **sharing** (the same weights apply everywhere) and **sparse connections** (each output sees only a patch). Output size is floor((n + 2p - f) / s) + 1 for input n, filter f, padding p, stride s. Pooling has no parameters. LeNet-5 shows the payoff: 345,308 connections but only about 60,000 trainable parameters. PyTorch layout is (batch, channels, height, width).

## Why an MLP fails on shifts

Each MLP input weight is tied to one pixel position. On 8x8 digits (about 4,810 vs 6,090 parameters): MLP test 0.975 but 0.473 on digits shifted one pixel; CNN 0.983 and 0.656. A one-pixel roll alone raised an MLP's error to 59.3%, far more than noise (11.5%); see [[Error Analysis, Bias and Variance Gaps]]. The CNN is not fully invariant: max pooling and the final linear layer still care about position.

## Buying invariance with augmentation

Training the CNN with one-pixel-rolled copies added: 0.988 on the original test set, 0.989 on the test set rolled the same way, 0.890 rolled the other way. The shift shown is handled; unseen directions only roughly.

## LeNet-5 benchmark and the collapse problem

On MNIST (60,000 train, 10,000 test) LeNet-5 reached 0.95% test error, 0.8% with distorted training copies; a linear classifier got 12%, a one-hidden-layer MLP 4.7%, an SVM 1.4%. If a loss only pulls the correct output's target closer, a network can make all targets equal and ignore its input; the fix is a discriminative loss that also pushes wrong answers away, the role negatives play in [[Contrastive Self-Supervised Pretraining]].

## Related ideas in the same chapter

- Neural style transfer freezes the weights and runs gradient descent on the pixels: content matched by activations at one layer, style by the Gram matrix of channel correlations (which features co-occur, not where).
- For depth, see [[Residual Connections and the Degradation Problem]]; for dense 1-D causal variants see [[Dilated Causal Convolutions]].

## See Also
- [[Residual Connections and the Degradation Problem]] — extends
- [[Dilated Causal Convolutions]] — related
- [[Object Detection Anchors, Non-Max Suppression and Focal Loss]] — extends
