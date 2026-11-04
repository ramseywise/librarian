---
title: Divergences and Non-Centred Parameterisation
tags: [foundations, pattern]
summary: "Hierarchical models create a funnel when the group scale is small, so NUTS diverges and underestimates the scale; sampling a standard normal and scaling it (non-centred form) changes the coordinates, not the model, and removes most divergences."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--04-bayesian-analysis--notes--02-mcmc-and-pymc.md
  - data/raw/repos/learn-ai-engineering/data-analytics--04-bayesian-analysis--notes--07-multilevel-models-and-partial-pooling.md
---

# Divergences and Non-Centred Parameterisation

NUTS reports a **divergence** when its numerical trajectory blows up, meaning it could not follow the surface. A few divergences mark regions the sampler cannot enter, which biases results; raise the target acceptance first, then reparameterise.

## The funnel

In a hierarchical model with group effects theta_j drawn from Normal(mu, tau), a small tau forces the thetas to crowd together. The valid region narrows as tau falls and no single step size suits both the wide top and the narrow neck. On an 8-group example written directly (centred): 88 divergences, tau ESS 63.63, R-hat 1.04, and tau's mean (4.28) too high because the chain stops visiting the neck.

## The fix

Sample raw ~ Normal(0, 1) and set theta = mu + tau * raw as a deterministic. It is the same distribution for theta; the sampler now sees a round surface. Result: divergences 2, tau ESS 2,142.69, R-hat 1.0, tau mean 3.63. The two left would be worth clearing with a higher target acceptance. Try this first in any hierarchical model; the multilevel models in [[Partial Pooling and Multilevel Models]] use it, including for correlated random slopes through a Cholesky factor.

## Reading the symptoms

- Divergences plus low tau ESS: funnel, go non-centred.
- When groups are few and data weak the opposite can bite, so check on the real data; a multilevel fit with 5 groups still showed one divergence at a target acceptance of 0.95 and its tail for tau needed rechecking.
- Reparameterising is a model-geometry change, not a prior change; see [[MCMC and Metropolis Sampling]] for the other geometry fix, rescaling inputs.

## See Also
- [[MCMC and Metropolis Sampling]] — prerequisite-for (diagnostics and samplers)
- [[Partial Pooling and Multilevel Models]] — related (the models where this appears)
