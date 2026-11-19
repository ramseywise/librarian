---
title: Varying Slopes and the LKJ Correlation Prior
tags: [data-analytics, bayesian-analysis, pattern]
summary: "Varying slopes give each cluster an intercept and a slope drawn from one multivariate Gaussian whose correlation matrix has an LKJcorr prior; a non-centred Cholesky form removes the divergences the centred form produces."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-statistical-rethinking-ch13-adventures-covariance.md
  - data/raw/papers/2026-11-08-statistical-rethinking-ch12-multilevel-models.md
---

# Varying Slopes and the LKJ Correlation Prior

Chapter 13 of *Statistical Rethinking* (first edition) extends varying intercepts ([[Partial Pooling and Multilevel Models]]) to varying slopes. Each cluster's intercept and slope are drawn jointly from a multivariate Gaussian, so they covary and shrinking one moves the other. The covariance matrix S is factored into standard deviations and a correlation matrix R, and R takes an LKJcorr(eta) prior: eta=1 is flat, and larger eta discounts correlations near -1 or 1. Average effects live in the linear model, leaving the varying effects as zero-mean offsets. The author's rule: pool any set of parameters whose index values are exchangeable (arbitrary labels, no real order).

## Non-centred form

A non-centred parameterisation draws standardised varying effects (mean 0, SD 1), then scales and shifts them inside the linear model; a Cholesky factor stands in for R (R = LL'). The two forms describe the same model but behave differently in the sampler ([[Divergences and Non-Centred Parameterisation]]). Reach for the non-centred form when a fit shows divergent transitions, low n_eff or high Rhat; the author adds that neither form always wins and some data favour the centred one. Setup: the chimpanzee data, crossed actor (7) and block (6) clusters with three varying effects each (m13.6), 3 chains of 5000 iterations with 1000 warmup. The non-centred fit avoids the centred fit's divergences, and WAIC counts about 18 effective parameters out of 54 nominal.

## Worked results

- Simulated cafes (setup: 20 cafes, 10 visits each split evenly between morning and afternoon, within-cafe SD 0.5, seed 5): average morning wait 3.5 and afternoon difference -1, with SDs of 1 and 0.5 and a correlation of -0.7 between intercept and slope. The advice is to simulate a population like this and check the model recovers the correlation.
- UCB admissions (setup: 6 departments, binomial logit, WAIC comparison of m13.2, m13.3 and m13.4): the varying-slopes model m13.3 wins on WAIC (5191.4, weight 0.99), ahead of the gender-free model (5201.2) and the constant-gender model (5201.9), with gaps of about 9.8 and 10.5 (dSE about 6.8 and 6.5). Department B had just 25 female applicants, so its sex-specific slope is pooled hard; department F has hundreds of both sexes and is barely pooled. A near-zero average slope does not stop varying slopes from improving prediction.
- Chimpanzees: the varying-slopes model m13.6NC and the varying-intercepts model m12.5 predict nearly the same (WAIC 534.7 against 532.7, weights 0.27 and 0.73); actor intercepts vary a lot and the other SDs are small, so shrinkage is strong.

The chapter's closing advice: do not read a posterior that merely overlaps zero as evidence of zero, look for slope variation even when the mean slope is near zero, and then simplify to the slopes that do vary.

## Limits

- Edition: first edition, with HalfCauchy priors, `map2stan`, Stan code written with `increment_log_prob`, WAIC and HPDI.
- One seed (5) is used in the cafe simulation; the chapter has no repeated-simulation check of sampling variability.
- The varying-slopes model does not clearly beat the varying-intercepts model on the chimpanzee data (WAIC 534.7 against 532.7).

## See Also
- [[Partial Pooling and Multilevel Models]] — prerequisite-for
- [[Divergences and Non-Centred Parameterisation]] — prerequisite-for
- [[Gaussian Processes and Bayesian Optimisation]] — related (the chapter's second half uses a Gaussian-process covariance for cases at distances)
