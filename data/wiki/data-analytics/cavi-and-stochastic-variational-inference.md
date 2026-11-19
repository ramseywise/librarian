---
title: CAVI and Stochastic Variational Inference
tags: [data-analytics, bayesian-analysis, pattern]
summary: "Mean-field variational inference gives each latent variable its own factor and updates one factor at a time (CAVI); stochastic variational inference replaces the full-data sweep with minibatch natural-gradient steps so the same model scales to millions of documents."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-blei-2016-variational-inference.md
---

# CAVI and Stochastic Variational Inference

Blei, Kucukelbir and McAuliffe review how variational inference approximates a posterior by optimisation, and how it compares with MCMC. This page covers the two algorithms the review builds on the ELBO that [[Variational Inference and the ELBO]] introduces.

## The objective and the family

The ELBO is E[log p(z,x)] minus E[log q(z)]. The review states that it equals the negative KL divergence from q to the posterior plus the log evidence (the marginal density of the observations), so it lower-bounds the log evidence. The **mean-field family** makes the latent variables mutually independent, so q(z) factorises into one q_j per latent variable.

## CAVI

Coordinate ascent (CAVI) holds every factor fixed except one, and sets that factor proportional to the exponential of the expected log complete conditional (the conditional of that latent variable given all the others and the data), the expectation taken under the other factors. It cycles through the factors until the ELBO stops improving. The review links this update to the Gibbs sampler.

Practices the review gives for running it:

- Stop when the ELBO changes by less than a small threshold, or when the average log predictive probability of a small held-out set stops moving.
- Start from several random initialisations and keep the run with the best ELBO, because the ELBO is non-convex and CAVI reaches only a local optimum. On the review's image-histogram mixture, ten random starts ended at different ELBO values.
- Work with log probabilities, and normalise with the log-sum-exp trick, subtracting the largest value before exponentiating.

## Stochastic variational inference

For conditionally conjugate models, SVI does stochastic natural-gradient ascent on the global variational parameters, using a subsample of the data at each step. The update blends the previous parameter and a noisy estimate from the minibatch: the new value is a weighted average of the old value (weight 1 minus eps_t) and the minibatch estimate (weight eps_t). The step sizes eps_t must obey Robbins-Monro conditions; a power schedule t to the minus kappa with kappa between 0.5 and 1 qualifies. The review reports (reproducing a figure from Hoffman et al. 2013) that SVI scaled LDA topic modelling to 1.8 million New York Times articles (self-reported, reproduced from Hoffman et al.), where early CAVI topic models handled thousands to tens of thousands of documents.

## Reported experiment

On imageCLEF colour histograms (576 dimensions, 30 clusters, 10,000 training and 10,000 test images), CAVI fitted a Gaussian mixture in under a minute and, by average log predictive of the test set against time, reached its fit orders of magnitude faster than the Stan NUTS sampler (self-reported; the authors call it a single comparison, not a definitive one). The review recommends VI where data are large or many models need quick exploration, and MCMC where data are small and samples must be precise; it says how the two compare in accuracy is unknown.

## Limits

- The review calls its theory thin, since each result covers a single model and a single variational family.
- The experiments are one simulation and one image mixture against Stan, which the authors say does not settle VI versus MCMC. Hardware, seeds and implementation versions are not given.
- Mean-field ignores correlation in the posterior and generally understates its variance, because the KL(q||p) objective punishes q for putting mass where p has little (shown on a correlated two-dimensional Gaussian). For a conjugate Bayesian Gaussian mixture the review reports the VI posterior mean and the maximum-likelihood estimate converging at order 1/n, with a covariance that is too small.
- ELBO as a model-selection criterion is not justified in theory; use it with caution.
- Non-conjugate and black-box VI get only brief coverage, and normalising flows and amortised VI post-date the review.
- The ELBO values for the ten-start experiment (roughly -2.4e6 to -1.6e6 across 50 s, self-reported) are read from a figure.

## See Also
- [[Variational Inference and the ELBO]] — prerequisite-for
- [[MCMC and Metropolis Sampling]] — alternative-to
- [[Expectation-Maximisation for Gaussian Mixtures]] — related (the mixture model both fit)
- [[Mixture Models and Label Switching]] — related (multimodal mixture posteriors)
