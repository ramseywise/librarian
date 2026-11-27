---
title: "Kolmogorov-Arnold Networks"
tags: [data-science, deep-learning, concept]
summary: "KANs put a learnable spline on every edge and only sum at the nodes; the authors report accuracy and interpretability gains on small science tasks at about 10x the training cost of an MLP."
updated: 2026-11-20
sources:
  - data/raw/papers/2026-11-07-liu-2024-kan.md
---

# Kolmogorov-Arnold Networks

Liu, Wang, Vaidya et al. (2024, ICLR 2025) replace an MLP's fixed node activations and linear weights with learnable one-dimensional functions on the edges. A KAN layer is a matrix of such functions, and nodes only sum their inputs. The design generalises the Kolmogorov-Arnold representation theorem from its original two-layer form to arbitrary width and depth.

## Mechanism

- Each edge carries phi(x) = w_b silu(x) + w_s spline(x), with the spline a sum of B-splines of order k on G grid intervals.
- The authors say graph connectivity learns how the function composes, while grid points within each activation learn the one-variable pieces.
- Grid extension refines accuracy by making the grid finer without retraining from scratch. Training uses LBFGS with the grid refined every 200 steps.
- For interpretability, L1 plus entropy sparsity, pruning and symbolic snapping of activations are applied.
- Theorem 2.1: given a smooth KA representation, the error scales as N^-(k+1), so 4 for cubic splines, independent of input dimension; the constant may depend on dimension. Measured grid scaling on one function was about G^-3, short of G^-4 (median-based loss gave closer to G^-4).
- Parameters scale as N^2 L (G+k) for a KAN and N^2 L for an MLP, with width N and depth L; the authors' saving depends on KANs getting by with a much smaller N (claim).

## Reported results (self-reported)

- Special functions: lower best test RMSE than an MLP on 15 of 15 (3 seeds, depths 2-6).
- Poisson PINN: a 2-layer KAN of width 10 beat a 4-layer MLP of width 100 by a factor of 100 in accuracy and in parameter efficiency; the authors note the solution is a symbolic formula, which may favour KANs.
- 27 Feynman equations: on average the two model types perform comparably (best of 3 seeds and several depths).
- Knot signature: a [17,1,14] KAN beat the 4-layer, width-300 MLP from DeepMind using far fewer parameters. Another lab, unpublished, reports an MLP with 60 parameters reaching 80% on the same task. A [3,2,1] KAN formula reached 84.0% test accuracy against 83.1% for the human DeepMind formula.
- Anderson localisation mobility edge: GAAM theory formula 99.2% against 99.0% for the KAN-found formula; MAAM 98.6% against 97.1%.
- Training is about 10x slower than an MLP at equal parameter count (unoptimised pykan, no timings given); the authors call it the biggest bottleneck.

## Limits

- Scope is small-scale AI + Science problems; no experiment on images, text or large data.
- The authors concede mathematical understanding is limited, with no generalised KA theorem for deeper KANs.
- The toy scaling experiments give KANs the true function shape.
- Reported scores are the best of 3 seeds and several depths, without error bars, and are plotted against parameter count rather than wall-clock time.
- Unsupervised relation discovery depends on the seed and found nothing new; the continual-learning result is one toy example.

## See Also
- [[Supervised Model Families and Complexity Knobs]] — related
- [[Gradient Boosting Mechanics and Library Choice]] — related
