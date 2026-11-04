---
title: "Batch Norm Eval Mode and Small-Batch Failure"
tags: [foundations, pattern]
summary: "Batch norm uses batch statistics in train mode and running statistics in eval mode, so forgetting model.eval() costs about 9 accuracy points at batch 32, tiny batches break it, and layer norm removes the batch dependence."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--02-optimisation-and-regularisation.md
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--README.md
---

# Batch Norm Eval Mode and Small-Batch Failure

[[Batch Normalization]] standardises each feature over the batch, then applies a learned scale (gamma) and shift (beta). At test time it must use running statistics accumulated in training. The dependence on the batch is the price of the method.

## The silent bug

Scoring in train mode normalises by the statistics of the scoring batch. On 8x8 digits: at batch 32, eval mode 0.983, train mode 0.892, and statistics recomputed precisely after training 0.981; at batch 2: 0.809, 0.717, 0.820. A final batch of one raises an error in train mode, hence `drop_last`. Call `model.eval()` before scoring; see [[PyTorch Training Loop Silent Bugs]].

## Small batches

Running (exponential-average) statistics lag the current weights. A ResNet-50 at batch 2 had 35.5 error with the running average against 32.0 with precisely computed statistics. The original batch-norm result reached the baseline's 72.2% accuracy in 13.3M steps against 31.0M; the 14x speedup (2.1M steps) also changed other things, so it is not attributable to normalisation alone.

## Alternatives

- **Layer norm** normalises within a sample, so there is no batch dependence; transformers use it ([[Pre-Norm vs Post-Norm and Warm-Up]]).
- **Adaptive gradient clipping** (normalizer-free networks) with lambda 0.01 at batch sizes of 1,024 to 4,096.
- **Derf**, an erf-based point-wise replacement, matched or beat layer norm on a ViT (82.8 vs 82.3) but lost on a small MLP (0.957 vs 0.979, 5 seeds): a replacement validated on one architecture does not transfer by default.

## See Also
- [[Batch Normalization]] — extends
- [[PyTorch Training Loop Silent Bugs]] — related
- [[Weight Initialisation and Activation Scale]] — related
