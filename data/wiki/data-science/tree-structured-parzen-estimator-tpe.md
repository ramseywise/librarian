---
title: "Tree-Structured Parzen Estimator (TPE)"
tags: [data-science, pattern]
summary: "TPE models the density of settings that scored well and the density of those that scored badly, then proposes the setting with the highest good-over-bad ratio; Bergstra et al. compared it with a Gaussian-process search, random search and manual search on a 32-variable deep belief network space."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-bergstra-2011-algorithms-hyper-parameter-optimization.md
  - data/raw/papers/2026-11-08-akiba-2019-optuna.md
---

# Tree-Structured Parzen Estimator (TPE)

Bergstra, Bardenet and Bengio compare sequential model-based optimisation, with expected improvement as the acquisition rule, against random search and manual search for DBN hyperparameters in a tree-structured space. Two model-based searches are tested: a hierarchical GP search and TPE.

## Mechanism

Instead of modelling the score y given the setting x, TPE models p(x|y) as two densities. l(x) is fitted to the observations whose loss is below a threshold y*, and g(x) to the rest. y* is a chosen quantile (gamma) of the observed losses, so a fraction gamma of observations count as good. Expected improvement is then proportional to the inverse of gamma plus (g(x)/l(x)) times (1 - gamma), so a setting scores well when l(x) is high and g(x) is low. In practice the method draws candidates from l and ranks them by g(x)/l(x). The paper presents TPE and the hierarchical GP as its two new techniques, both aimed at models where some inputs are irrelevant.

## What the paper measured

Setup for all rows: DBNs with up to 3 layers, a 32-variable search space, up to 200 trials per algorithm, five parallel GPUs; manual search used 82 trials on convex and 27 on MRBI. Best-model test error, all (self-reported):

| Algorithm | convex | MRBI |
|---|---|---|
| TPE | 14.13% | 44.55% |
| Gaussian process | 16.70% | 47.08% |
| Manual search | 18.63% | 47.39% |
| Random search | 18.97% | 50.52% |

The authors report that 32 random trials reliably matched earlier manual-search results on several datasets, and that the GP got to the manual-search level inside 80 trials, a little behind manual search in efficiency. After 200 trials a proposal cost about 150 s for the GP and about 10 s for TPE (self-reported). A whole experiment ran for roughly a day of wall-clock time on five GPUs, each trial capped at one GPU-hour (self-reported).

## In Optuna

Optuna's independent sampler is TPE; its relational samplers are CMA-ES and GP-based. In Optuna's comparison on 56 black-box test cases (30 repeats of 80 trials, judged by a paired Mann-Whitney U test at alpha 0.0005), a mixture of TPE and CMA-ES was statistically worse than random search in 1 of 56 cases, and GPyOpt beat it in 34 of 56 but took about twenty times longer per study (self-reported, Optuna's own tool and baselines).

## Limits

- Only DBNs on two datasets; the 200-trial runs are not stated to have been repeated, so there is no variance across searches.
- The authors concede that sequential model-based search can be arbitrarily bad with a poor model of p(y|x), or slower than random search if it finds a local optimum.
- The reasons TPE beat the GP are untested hypotheses in the paper.
- The search spaces differ from the manual search (larger, no discretisation), and TPE could leave its initial bounds while the GP and random search could not.
- The PDF text does not print a venue.
- The Optuna numbers come from a 2019 preprint; the extraction notes later API changes and does not cover later versions. Its test collection and protocol are taken from earlier work.

## See Also
- [[Hyperparameter Search Budgets and Selection Optimism]] — prerequisite-for
- [[Gaussian Processes and Bayesian Optimisation]] — alternative-to
- [[Scaling Per-Entity Model Tuning: SparkTrials versus Grouped Fits]] — related
