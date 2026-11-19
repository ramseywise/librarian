---
title: Gaussian Processes and Bayesian Optimisation
tags: [data-analytics, bayesian-analysis, concept]
summary: "A Gaussian process is a prior over functions that gives a prediction with an honest error bar; Bayesian optimisation uses it as a cheap surrogate and an acquisition function to pick the next expensive evaluation, but beats random search only when each fit is costly."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--04-bayesian-analysis--notes--06-bayesian-machine-learning.md
  - data/raw/papers/2026-11-08-statistical-rethinking-ch13-adventures-covariance.md
confidence: medium
---

# Gaussian Processes and Bayesian Optimisation

A **Gaussian process** (GP) is a prior over functions: any finite set of function values is jointly Normal, with covariance from a kernel such as the RBF, k(x, x') = var * exp(-|x - x'|^2 / (2 * ell^2)). Conditioning on observed points is a Normal conditional and yields a posterior mean and standard deviation at every x.

## Behaviour

Three observations of sin(x) at x = 1, 3, 4 (unit variance and lengthscale):

| x | Posterior mean | sd | Truth |
|---|---|---|---|
| 1.0 (observed) | 0.841 | 0.001 | 0.841 |
| 2.0 | 0.768 | 0.540 | 0.909 |
| 3.5 | -0.365 | 0.171 | -0.351 |
| 6.0 | -0.160 | 0.987 | -0.279 |

At an observed point the sd is effectively zero, between points it grows, and far from the data the mean drifts to the prior's 0 and the sd to nearly the prior's 1. The model says it does not know there, which acquisition functions exploit. A longer lengthscale makes distant points more correlated, lowering the sd at x = 6. Kernel hyperparameters can be fitted by marginal likelihood; cost grows as n^3, so large n needs sparse GPs (inducing points) or a different surrogate.

## Bayesian optimisation

Use the GP as a surrogate for an expensive black-box function, such as validation score against hyperparameters. An acquisition function turns mean and uncertainty into the next point to try, trading exploration against exploitation as in [[Thompson Sampling and Bandit Regret]].

| Acquisition | Picks the point with |
|---|---|
| Expected improvement | largest expected gain over the best so far |
| Upper confidence bound | highest mean + kappa * sd |
| Probability of improvement | highest chance of beating the best so far |

## Does it beat guessing?

Tuning a gradient-boosted classifier's learning rate and leaf count on a small built-in dataset (3-fold CV log loss; 4 random initial points, expected improvement over 2,000 random candidates per round):

| Fits | 4 | 8 | 12 | 20 |
|---|---|---|---|---|
| Bayesian optimisation | 0.1148 | 0.1065 | 0.1065 | 0.1016 |
| Random search (mean of 5 runs) | 0.1233 | 0.1193 | 0.1164 | 0.112 |

The best setting had a learning rate of 0.447 and 3 leaves. This compares one Bayesian run with five random ones where each evaluation takes about a second, so it shows the shape of the method rather than measuring an advantage. The case grows as each fit gets expensive; if a fit takes a second, random search with more fits is often simpler.

## Gaussian process regression for cases at a distance (Statistical Rethinking)

McElreath (first edition, chapter 13) carries the varying-effects idea over to a continuous category: instead of a fixed covariance matrix, estimate a covariance function that depends on how far apart two cases are (a squared-distance form, GPL2). Setup: Oceanic tools data, 10 societies, Poisson model with distance in thousands of km, 4 chains of 10,000 iterations with 2000 warmup. The log-population slope is 0.24, with an 89% interval spanning 0.05 to 0.42, near the non-spatial estimate from earlier. Malekula, Tikopia and Santa Cruz show posterior-median correlations over 0.8 among themselves, while Hawaii correlates about 0 with the rest; most sampled covariance curves reach zero before 4000 km. The chapter suggests reporting the posterior median for skewed GP parameters, plotting sampled covariance functions, and writing Stan directly beyond the basics. Automatic relevance determination gives every dimension of difference its own relevance parameter.

See [[Varying Slopes and the LKJ Correlation Prior]] for the chapter's first half.

## Limits

- Only 10 societies, with wide uncertainty about the spatial effect's strength.
- The author says the descriptive result fits many causal explanations.
- Code is first-edition `map2stan`, which is hard to extend.

## See Also
- [[Variational Inference and the ELBO]] — related
- [[Thompson Sampling and Bandit Regret]] — related (exploration versus exploitation)
- [[Prior Choice and Prior Predictive Checks]] — related
- [[Tree-Structured Parzen Estimator (TPE)]] — alternative-to
- [[Varying Slopes and the LKJ Correlation Prior]] — related
- [[LinUCB and Linear Bandit Confidence Ellipsoids]] — related (optimism over a confidence set for linear rewards)
- [[NeuralLinear Thompson Sampling]] — related (approximate posteriors for Thompson sampling)
- [[Upper Confidence Bound Bandit Algorithms]] — related (an optimism-based acquisition rule for bandits)
