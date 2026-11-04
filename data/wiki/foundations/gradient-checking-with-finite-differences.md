---
title: "Gradient Checking with Finite Differences"
tags: [foundations, pattern]
summary: "A centred finite difference gives a slow but independent estimate of every gradient; the relative difference to backprop separates a correct implementation (about 9e-11) from a planted 10% error (about 0.05), and the check is switched off in training."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--01-neural-networks-fundamentals.md
---

# Gradient Checking with Finite Differences

Backpropagation is the chain rule applied from the loss back through each layer, reusing the cached forward values; for a sigmoid output with cross-entropy the output-layer error is simply `A - Y`. Hand-written backprop fails silently: the loss still falls a little, so the bug shows up only as a model that is mysteriously worse. Gradient checking compares the analytic gradient against a numerical one.

## Mechanism

For each parameter, perturb it by +eps and -eps (eps 1e-5), recompute the loss, and take the centred difference `(J(theta+e) - J(theta-e)) / (2 eps)`. Compare the two gradient vectors with

```
rel_diff = ||g_num - g_bp|| / (||g_num|| + ||g_bp||)
```

A relative difference below about 10^{-7} passes.

## What the numbers look like

On a small network trained on the two-moons data: correct backprop gave 9.1108e-11, and the same gradient multiplied by 1.1 (a planted 10% error) gave 0.0476. A constant scaling error c gives `|c-1|/(c+1)` whatever the data, so the size of the relative difference tells you the size of the scaling error (0.995 with m=400 in one run).

## When it misleads or costs too much

- It needs two forward passes per parameter, so run it once on a tiny network and turn it off before training.
- ReLU's kink can raise the difference slightly when a unit sits at zero; that is not necessarily a bug.
- It checks gradients, not the model. A correct gradient of the wrong loss passes.

## Companion check: symmetry

Random initial weights are needed so hidden units differ; zero initialisation leaves every unit in a layer computing the same thing. See [[Weight Initialisation and Activation Scale]] for what scale to use.

Autograd removes the backprop code, not the need to understand it: a PyTorch network given the NumPy weights reproduced the NumPy gradients to 6.9388e-17. See [[PyTorch Training Loop Silent Bugs]] for the failures that remain once autograd does the backward pass.

## See Also
- [[PyTorch Training Loop Silent Bugs]] — related (the next layer of silent failures)
- [[Weight Initialisation and Activation Scale]] — related
