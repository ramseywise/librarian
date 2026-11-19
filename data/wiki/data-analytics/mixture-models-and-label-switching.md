---
title: Mixture Models and Label Switching
tags: [data-analytics, bayesian-analysis, pattern]
summary: "A two-cluster mixture can be fitted with sampled discrete labels or, far faster, by summing the labels out of the likelihood; symmetric components then swap identity across chains, which an ordering constraint or informative priors fixes."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--04-bayesian-analysis--notes--02-mcmc-and-pymc.md
  - data/raw/papers/2026-11-08-statistical-rethinking-ch11-monsters-mixtures.md
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

## Mixtures for counts (Statistical Rethinking)

McElreath (first edition, chapter 11) defines a mixture model as more than one simple distribution for the same outcome, to model a mixture of causes.

- **Zero-inflated Poisson.** A zero can arise from either process, so its likelihood is p + (1-p) exp(-lambda). Setup: simulated monk manuscripts over 365 days, true drinking probability 0.2 and work rate 1, an intercept-only quadratic-approximation fit with ap ~ Normal(0,1) and al ~ Normal(0,10); it recovered 0.1994078 and 1.051271. The chapter puts different predictors in the two linear models as the hypothesis dictates and computes the likelihood on the log scale.
- **Continuous mixtures.** A beta-binomial gives every binomial count its own success probability, sampled from a beta distribution (mean pbar, shape theta); a gamma-Poisson (negative binomial) likewise gives every Poisson count its own rate from a gamma distribution. Setup: UCBadmit pooled across departments (12 rows), Stan HMC, 2 chains of 4000 iterations with 1000 warmup. Theta's posterior mean is 2.77 (SD 0.96, 89% interval 1.26 to 4.15), and the implied mean admission probability has median near 0.40 (95% interval 0.27 to 0.54). An exponential prior on theta samples better than a half-Cauchy and leaves inference unchanged.
- The chapter advises against WAIC for beta-binomial and gamma-Poisson models unless sure, falling back on DIC, and prefers multilevel models over either for over-dispersion in practice ([[Partial Pooling and Multilevel Models]], [[Poisson Offsets and Overdispersion]]).

## Limits

- The gamma-Poisson gets no worked example.
- The zero-inflated case is one simulated year of intercept-only models.
- Code is first-edition `map` and `map2stan`.

## See Also
- [[Expectation-Maximisation for Gaussian Mixtures]] — alternative-to (fit the same model by optimisation)
- [[Divergences and Non-Centred Parameterisation]] — related (another geometry fix)
- [[Generative Story Models]] — related
- [[Ordered Logit and the Cumulative Link]] — related (the same chapter's ordered-outcome model)
- [[Unseen Species Hierarchical Dirichlet Model]] — related
- [[Density Estimators: KDE Bandwidth, GMM Components and the Generative Classifier]] — related
