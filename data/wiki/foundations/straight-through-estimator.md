---
title: Straight-Through Estimator
tags: [foundations, concept]
summary: "The straight-through estimator trains hard-threshold or stochastic binary gates by backpropagating through the threshold as if it were the identity; Bengio and colleagues (2013) tested it against three other estimators on a small gated-layer experiment."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-bengio-2013-estimating-or-propagating-gradients-through.md
---

# Straight-Through Estimator

The 2013 paper by Bengio, Leonard and Courville compares ways to get a usable training signal through such stochastic or non-smooth neurons, motivated by conditional computation: a small gater network switches parts of a large layer on or off so that only a fraction of the compute runs.

## The four estimators

1. Noisy rectifier: inject noise into a rectifier unit.
2. STS (stochastic times smooth) unit: a probability p from a sigmoid, a binary draw with parameter sqrt(p), and an output of the draw divided by sqrt(p).
3. Unbiased estimator for a stochastic binary neuron: the gradient estimate is (h minus sigmoid of the pre-activation) times the loss, with a centred minimum-variance baseline. The paper proves this as a theorem and notes that REINFORCE is a special case. The extraction records that no gradient is backpropagated into the gater with this estimator.
4. Straight-through: treat the hard threshold as the identity when computing the backward pass. The paper reports the estimator is biased yet has the correct sign for one layer, and does better when the sigmoid derivative is left out.

## Experiment

Setup (small, one architecture): MNIST, a gater with 400 hidden units and 2,000 outputs that multiplies a 2,000-unit linear expert layer, 10% target sparsity, compared with rectifier and sigmoid baselines. The paper reports that the straight-through gater had the best validation and test error of all gaters (self-reported). The extraction carries no numeric error values for the other gaters, so no comparison table is given here.

The paper's cost argument is that a gater with sparsity alpha shrinks the cost of the main path from O(N^2) down to O(alpha N^2) while the gater itself costs O(MN) when its bottleneck size M is much smaller than N (a claim, not measured).

## Limits

- One MNIST architecture and one conditional layer; stacking gated layers was not attempted.
- Runtime savings were never timed; they are only expected from the sparsity.
- Each number comes from a single run, with no variance; the MNIST split and epoch count are missing.
- The straight-through estimator is a heuristic and biased; the sign guarantee fails across multiple layers.
- Internal inconsistency noted by the extraction: the noisy rectifier gater scores 1.87 test error while the plain rectifier baseline scores 1.60, which runs against the paper's conclusion.

## See Also
- [[Sequence-Level Knowledge Distillation]] — related
- [[BitNet b1.58 Ternary Weights]] — related (low-bit training also needs a gradient through a rounding step)
- [[MoE Expert Offloading]] — related (conditional computation at serving time)
- [[Bi-Mamba Binarized State Space Model]] — instance-of (binary weights trained through the estimator)
