---
title: Model Compression with MUNGE Mimic Nets
tags: [foundations, concept]
summary: "Bucila, Caruana and Niculescu-Mizil (KDD 2006) compress a large ensemble into a small neural net trained on ensemble-labelled synthetic data from MUNGE; on eight binary problems the net matched ensemble RMSE (0.264 against 0.263) at about 1000x smaller and faster, and failed on one (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-bucilua-2006-model-compression.md
---

# Model Compression with MUNGE Mimic Nets

The paper calls a small fast model that imitates a bigger, slower, more accurate one model compression. The teacher is an ensemble-selection model, fitted on 4000 training cases with 1000 held out for validation. Synthetic cases derived from the training set receive ensemble labels and train a neural net of 1 to 256 hidden units, stopped early on the validation set.

MUNGE makes pseudo data by finding each case's nearest neighbour and, per attribute with probability p, swapping nominal values or resampling continuous ones around the pair with a spread of |difference|/s. Two alternatives, RANDOM and NBE, were compared.

## Results (self-reported)

Eight binary tabular problems, 4000 training points, RMSE against 0/1 targets on large test sets, 256 hidden units, 400k MUNGE cases:
- Average RMSE 0.264 for the mimic net against 0.263 for the ensemble, 0.282 for the best neural net and 0.274 for the best single model; 97% of the ensemble's gain over the best net recovered. It matched or beat the ensemble on six of eight problems; on HS it scored 0.204 against 0.213, which the authors suspect is ensemble overfitting.
- Average size 0.33 MB against 550.29 MB for the ensemble; 10k cases classified in 5.62 s against 5396.27 s (SNNS, one workstation). The conclusion says 1000x smaller and faster; another passage says 100-100,000x smaller and 100-10,000x faster.
- RANDOM data beyond 100k did worse than the original 4k, NBE peaked near 20k and then degraded, and MUNGE did not degrade. On COVTYPE real unlabelled data was 2-8x as sample-efficient as MUNGE.

## Limits

- ADULT is the one failure (RMSE 0.325 for the mimic net, 0.317 for the ensemble and 0.328 for the best net); it has high-arity nominal attributes and the cause is unresolved.
- Ensemble size, MUNGE p and s, optimiser settings and epochs are not stated; single run, no error bars.
- Only eight binary tabular problems; no deep teachers and no multiclass.
- Compression can cost more than building the ensemble; it is worthwhile only where deployment is constrained or volume is high. Speed depends on implementation.

## See Also
- [[Sequence-Level Knowledge Distillation]] — related (distillation of sequence models)
- [[On-Policy Distillation]] — related
- [[Nemotron Puzzle Hybrid MoE Compression]] — related
