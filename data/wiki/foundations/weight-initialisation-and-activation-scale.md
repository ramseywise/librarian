---
title: "Weight Initialisation and Activation Scale"
tags: [foundations, concept]
summary: "Initial weight scale decides whether the signal survives the layers: too small or too large and a deep net never trains, while He (ReLU) and Glorot (tanh) scales keep activation spread stable; measure first-layer and last-layer activation std before blaming the optimiser."
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--02-optimisation-and-regularisation.md
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--README.md
---

# Weight Initialisation and Activation Scale

The first of three checks when training stalls, in order: does the signal survive (initialisation), does the optimiser progress ([[Adam, AdamW and Decoupled Weight Decay]]), does it generalise ([[Regularisation Under Noisy Labels]]).

## Mechanism

Each layer multiplies its input by a weight matrix. If the weights are too small the activations shrink layer by layer toward zero; too large and they and the loss explode. Variance-preserving scales keep the spread roughly constant:

- **He** for ReLU: std = sqrt(2 / n_prev).
- **Glorot** for tanh: std = sqrt(1 / n_prev).
- Zero initialisation also fails by symmetry (every unit in a layer stays identical); see [[Gradient Checking with Finite Differences]].

## Numbers (6-layer MLP on 8x8 digits, 20 epochs)

| ReLU init | Result |
|---|---|
| zeros, or std 0.01 | test 0.102 (chance) |
| std 10 | starting loss 1.09e+12, test 0.446 |
| He | test 0.970; activation std 0.406 at the first layer, 0.317 at the last |

With tanh at six layers: a small std gave 0.330, He 0.975, Glorot 0.970, the last two within noise.

## Practice

- Print per-layer activation std at initialisation; a collapse toward zero or blow-up tells you the cause before any training.
- A loss stuck at chance that does not move points at initialisation or learning rate, not at regularisation.
- Normalisation layers reduce sensitivity to initial scale ([[Batch Normalization]]) but do not replace the check.

## See Also
- [[Batch Normalization]] — related
- [[Gradient Checking with Finite Differences]] — related
- [[Adam, AdamW and Decoupled Weight Decay]] — related (the next check)
- [[BitNet b1.58 Ternary Weights]] — related (weights restricted to three values from the start of training)
