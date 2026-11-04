---
title: "Regularisation Under Noisy Labels"
tags: [foundations, comparison]
summary: "With 30% flipped labels a wide net memorises (train 1.000, clean test 0.694); early stopping on a clean validation set beat weight decay and dropout, and dropout should be off at test time and, for underfitting models, only used early."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--02-optimisation-and-regularisation.md
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--README.md
---

# Regularisation Under Noisy Labels

Setup: 300 rows with 30% of labels flipped, a wide MLP trained 100 epochs, scored on a clean test set.

| Method | Clean test |
|---|---|
| none (train accuracy 1.000) | 0.694 |
| weight decay 1 | 0.733 |
| weight decay 3 | 0.790 |
| dropout 0.5 | 0.745 |
| stop at epoch 8 | 0.878 |

The epoch-8 figure peeks at the answer. Honest early stopping uses 60 held-out rows with trustworthy labels: 0.787, 0.728 and 0.835 across three runs, against 0.719, 0.715 and 0.702 at the last epoch. The rule: keep a clean validation set and stop on it.

## Dropout

Inverted dropout zeroes units with probability p during training and divides the survivors by the keep probability so no rescaling is needed at test; it is switched off by `eval()`. Dropout slows fitting, so it hurts an underfitting model: on a small digits MLP, none 0.935, standard dropout 0.2 gave 0.919, and **early dropout** (off after epoch 5) 0.934. In a ViT-T, baseline 73.9, standard dropout 67.9, early dropout 74.3; stochastic depth on ViT-B moved 81.6 to 82.3.

## Order of checks

Regularise only after the signal survives ([[Weight Initialisation and Activation Scale]]) and the optimiser progresses ([[Adam, AdamW and Decoupled Weight Decay]]). For the Bayesian reading of weight decay see [[Regularisation as a Prior]]; for label noise as a data problem see [[Error Analysis, Bias and Variance Gaps]].

## See Also
- [[Regularisation as a Prior]] — related
- [[Adam, AdamW and Decoupled Weight Decay]] — related
- [[Learning Curves and Bias-Variance Diagnosis]] — related
