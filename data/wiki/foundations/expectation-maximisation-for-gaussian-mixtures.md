---
title: Expectation-Maximisation for Gaussian Mixtures
tags: [foundations, concept]
summary: "EM fits a mixture by alternating soft cluster assignments (E-step) with weighted parameter refits (M-step); the likelihood never falls but only reaches a local peak, so restart several times and keep the best, and remember it gives a point estimate with no parameter uncertainty."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--04-bayesian-analysis--notes--06-bayesian-machine-learning.md
---

# Expectation-Maximisation for Gaussian Mixtures

The model of [[Mixture Models and Label Switching]] fitted by optimisation instead of sampling. Each point has a hidden label; parameters are mixture weights, means and covariances. Known labels would make the parameters simple averages; known parameters would make the labels follow from Bayes' rule. EM alternates between the two.

| Step | Computes | Rule |
|---|---|---|
| E-step | responsibilities: P(label = c given x) | proportional to weight_c times the Normal density, normalised over components |
| M-step | parameters given responsibilities | weight = mean responsibility; mean = responsibility-weighted average; covariance = responsibility-weighted covariance |
| Monitor | lower bound on the log-likelihood | rises monotonically; stop when it plateaus |

## Implementation notes

- Work in log space (log-sum-exp over components) in the E-step to avoid underflow.
- Add a small ridge (1e-6 times the identity) to each covariance: without it a component can collapse onto one point and the likelihood rises without limit.
- Initialise means from random data points and covariances from the pooled covariance.

## Local optima

Fitting three clusters of 150, 100 and 50 points (variances 1.0, 0.5 and 2.0) from ten random starts: eight reached a log-likelihood of -1107.8, one stopped at -1186.9 and one at -1268.1. The best run took 28 iterations, never decreased, and recovered weights 0.33, 0.5 and 0.17 (the data shares, in another order, which is label switching again). Monotone improvement promises a local peak only, so run several restarts and keep the best bound. Raising the component count can never lower the training likelihood, so it cannot choose the count: use held-out likelihood or BIC (see [[Model Selection Criteria]]).

## EM against MCMC

| | EM | MCMC ([[MCMC and Metropolis Sampling]]) |
|---|---|---|
| Output | point estimate (MLE or MAP) | samples from the full posterior |
| Speed | fast, deterministic per restart | slower |
| Parameter uncertainty | none | full |
| Failure | local optima, collapsing covariances | slow mixing, label switching |

EM suits a fast point fit; use MCMC when you need uncertainty on the parameters. EM is the special case that gives up the posterior over parameters but keeps latent-variable inference; [[Variational Inference and the ELBO]] keeps an approximate posterior instead.

## See Also
- [[Mixture Models and Label Switching]] — prerequisite-for
- [[Variational Inference and the ELBO]] — alternative-to
- [[Maximum Likelihood and Estimator Bias]] — related
