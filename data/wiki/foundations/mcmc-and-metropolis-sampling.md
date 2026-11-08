---
title: MCMC and Metropolis Sampling
tags: [foundations, concept]
summary: "MCMC returns correlated samples from the posterior using only density ratios; step size decides whether a Metropolis chain works, effective sample size and R-hat tell whether it did, and gradient-based NUTS removes the tuning for continuous models."
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--04-bayesian-analysis--notes--02-mcmc-and-pymc.md
  - data/raw/repos/learn-ai-engineering/data-analytics--04-bayesian-analysis--notes--06-bayesian-machine-learning.md
---

# MCMC and Metropolis Sampling

With one or two conjugate parameters the posterior has a formula. With more, normalising it means integrating over all dimensions, and a grid of 100 points per parameter needs 1e+10 evaluations at 5 parameters and 1e+40 at 20. MCMC instead returns **samples** from the posterior; every summary (mean, interval, P(B > A), expected loss) is an average over them.

## One Metropolis step

1. Propose a nearby position.
2. Accept with a probability depending on the ratio of posterior densities: always uphill, sometimes downhill.
3. Record the position (the old one if rejected) and repeat.

Only a ratio of densities is used, so the normalising constant cancels; that is why it works at all. Rejected proposals are not wasted: staying put is how the chain spends more time in high-density regions. Twenty lines reproduce the Beta(36, 22) coin posterior (mean 0.6201 against 0.6207).

## Step size decides everything

| Step | Accepted | Effective samples of 19,000 |
|---|---|---|
| 0.002 | 98.7% | 11 (mean 0.565, wrong) |
| 0.1 | 57.6% | 3,594 |
| 3.0 | 2.8% | 278 |

A high acceptance rate is not health. **Effective sample size** (ESS) is how many independent draws correlated ones are worth; thousands of draws, not tens, are needed since Monte Carlo error shrinks like 1/sqrt(ESS).

## NUTS versus Metropolis

Random-walk Metropolis proposes blindly, and in high dimensions most directions are downhill. Hamiltonian Monte Carlo uses the gradient so proposals land far away and are still accepted; the No-U-Turn Sampler removes its two hand-tuned settings by lengthening the trajectory until it turns back and tuning step size during warm-up. Discrete variables cannot use NUTS (use Metropolis, a categorical Gibbs-Metropolis step, or marginalise them out; see [[Mixture Models and Label Switching]]).

Scaling matters as much as the sampler. On a 23-point logistic model with raw temperature: Metropolis ESS 5 with R-hat 2.16; NUTS ESS 304 at 18.8 leapfrog steps per draw; NUTS on standardised input ESS 2,591 at 3.1 steps. The raw intercept and slope are almost perfectly correlated far from zero, a narrow ridge; standardising removes it. On a 2,000-row logistic regression with five inputs, from the same draws NUTS had a minimum ESS of 3,306 against 155 for Metropolis.

## Diagnostics

| Check | Healthy |
|---|---|
| Trace plot | fuzzy caterpillar, chains overlap |
| R-hat | at most 1.01; compares between- and within-chain variance, does not prove the whole posterior was found |
| ESS (bulk and tail) | hundreds or more; R-hat 1.00 with ESS 40 is not fine |
| Divergences (NUTS) | zero; see [[Divergences and Non-Centred Parameterisation]] |

Run four chains from dispersed starts: one chain cannot disagree with itself. Burn-in is handled by tuning draws. Thinning adds no information. The highest-density interval is the narrowest holding a given mass; the equal-tailed interval cuts equal tails; they differ on skewed posteriors, and a default summary may report 89%, not 95%. Derive quantities within each joint draw: pairing x from one draw with y from another breaks constraints (std of x + y was 0.0 within a draw and 1.4 shuffled).

## When it will not converge

Start sensibly, bound priors, rescale inputs, run several chains, prefer NUTS. The folk theorem: if you have computational problems, probably your model is wrong. Approximations exist when sampling is too slow: the Laplace approximation (a Normal at the MAP) and [[Variational Inference and the ELBO]].

## See Also
- [[Beta-Binomial Updating and Credible Intervals]] — prerequisite-for (the closed form used to check a sampler)
- [[Prior Choice and Prior Predictive Checks]] — related (what the sampler is given)
- [[Expectation-Maximisation for Gaussian Mixtures]] — alternative-to (point estimate instead of samples)
- [[No-U-Turn Sampler (NUTS)]] — instance-of (adaptive Hamiltonian sampler)
