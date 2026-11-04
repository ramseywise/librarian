---
title: Mixture Models and Label Switching
tags: [foundations, pattern]
summary: "A two-cluster mixture can be fitted with sampled discrete labels or, far faster, by summing the labels out of the likelihood; symmetric components then swap identity across chains, which an ordering constraint or informative priors fixes."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--04-bayesian-analysis--notes--02-mcmc-and-pymc.md
---

# Mixture Models and Label Switching

Setup: 300 simulated values, 40% around 120 (sd 12) and the rest around 200 (sd 22). Story: each point belongs to cluster 0 with probability p; its value is Normal around that cluster's centre and spread.

## Sampling labels versus marginalising them

| Approach | Sampler | ESS of centres | Cost |
|---|---|---|---|
| 300 discrete labels | Metropolis for parameters plus categorical Gibbs-Metropolis for labels | hundreds | about half a minute for 1,000 draws |
| Labels summed out (a normal-mixture likelihood, Dirichlet weights) | NUTS | thousands (4,642 to 5,135) | about a sixth of the time |

Both recover the truth (centres about 120.6 and 199, weights 0.36 to 0.37). Marginalise discrete variables whenever you can (see [[MCMC and Metropolis Sampling]]).

## Using the posterior to classify

Compute each cluster's weighted likelihood per joint draw, then average. Nearest-centre would split at 159.8, but even odds fall near 147 because cluster 1 has about twice the spread and nearly twice the weight; reasoning with centres alone ignores both. At x = 140, P(cluster 0) = 0.888; at 160, 0.019.

## Label switching

Components have no meaning the model can see. With the same prior on both centres, chains landed on either labelling: chain means [120.6, 199.3] in three chains and swapped in one, R-hat 1.53, and the cross-chain mean of the centres is nonsense. Each chain is fine alone; one chain would hide the problem. Fixes: informative priors on the centres (120 and 190), or an ordering constraint on the centres, which assumes nothing about where they sit (R-hat 1.0 afterwards).

## See Also
- [[Expectation-Maximisation for Gaussian Mixtures]] — alternative-to (fit the same model by optimisation)
- [[Divergences and Non-Centred Parameterisation]] — related (another geometry fix)
- [[Generative Story Models]] — related
