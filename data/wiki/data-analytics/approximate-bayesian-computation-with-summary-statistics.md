---
title: Approximate Bayesian Computation with Summary Statistics
tags: [data-analytics, bayesian-analysis, pattern]
summary: "When the likelihood of a whole dataset is too tiny and too slow to compute, score each hypothesis by the likelihood of summary statistics instead; the choice of statistic then becomes a modelling decision that can reverse the answer."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-think-bayes-ch10-approximate-bayesian-computation.md
---

# Approximate Bayesian Computation with Summary Statistics

Downey's chapter 10 of *Think Bayes* (1st edition) estimates the mean and standard deviation of adult heights on a grid, and asks whether men or women vary more. The data are CDC BRFSS self-reported US heights: 154,407 men and 254,722 women. Raw summaries: men 178 cm mean and 7.7 cm sd, women 163 cm and 7.3 cm, giving coefficients of variation (sd divided by mean) of 0.0433 and 0.0444.

## Exact update, made feasible

- The per-datum update over a (mu, sigma) grid fails at 1,000 values: the product of many small densities underflows (rounds to zero), so total probability is zero.
- Fix: update in log-likelihood, subtract the maximum before exponentiating, and memoise sums that depend on only one parameter. Downey reports about a 100-fold speed-up, with the full dataset in under a minute (self-reported, on his own computer).
- Choose the grid range from the classical estimates and their standard errors, s over the root of n for the mean and s over the root of 2(n-1) for the sigma. A range of 4 standard errors covered all non-negligible likelihood; a larger one had no effect.

## ABC

Approximate Bayesian Computation scores a hypothesis by how likely it makes the sample statistics, not the exact data; datasets with the same summaries are treated as equivalent. With the sample mean and sd as the summaries, the whole dataset took about a second and agreed with the exact result to about five digits (self-reported).

## Robust statistics and the choice of summary

The data contain outliers (three adults at 61 cm, four women at 229 cm), so Downey uses the median and an inter-percentile range (the span holding a given fraction of the distribution). With the 68% range (num_sigmas=1) the posterior mean CV was 0.0429 for women and 0.0410 for men, the two posteriors not overlapping, which makes women look more variable. With num_sigmas=2 the conclusion reverses: men appear more variable with equal confidence. The answer depends on the summary chosen. Downey advises summaries that pin down both location and spread; the 49th and 51st percentiles alone would leave sigma free.

## Limits

- One illustrative dataset, no repeated runs; timings come from the author's machine with no hardware given.
- Only a (mu, sigma) grid is used, with no MCMC or higher-dimensional case.
- Choosing summaries is a modelling decision and the chapter gives no general rule. The author admits the variability hypothesis may be too loosely stated to test.
- The data set the prior range and then update it, which the author argues does no harm in this case.
- Code is Python 2 and relies on thinkbayes.py, which has dated.

## See Also
- [[Grid Posteriors Over Several Parameters]] — prerequisite-for
- [[MCMC and Metropolis Sampling]] — alternative-to
- [[Posterior Predictive Checks]] — related
