---
title: Simulate the Joint and Slice for a Conditional
tags: [data-analytics, bayesian-analysis, pattern]
summary: "When the forward direction (size given age) is easy to simulate but the inverse (age given size) is not, simulate the joint distribution and slice it at the observed value, then test each assumption such as serial correlation by re-running."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-think-bayes-ch13-simulation.md
---

# Simulate the Joint and Slice for a Conditional

Chapter 13 of Downey's *Think Bayes* (1st edition) asks how old a kidney tumour of 15.5 cm is, for a patient discharged 3,291 days before diagnosis. The conditional p(age | size) is hard to write down, so the chapter simulates tumour growth to produce pairs of age and size, and takes the pairs matching the observed size.

## The simple calculation first

With a median volume doubling time of 811 days (Zhang et al.) and linear doubling time taken as three times that, at the median rate the 15.5 cm tumour was roughly 6 cm at discharge, so it likely began earlier. Starting at 0.1 cm after discharge needs 7.3 linear doublings, a reciprocal doubling time (RDT, doublings per year) of 2.4, which only 20% of tumours in the Zhang data reached (data read off a printed graph). Downey uses the simple model to validate the complex one.

## Simulation

Draw a growth rate for each interval from the empirical distribution, advance the tumour over simulated years, and record age and size pairs; the slice at the observed size is the age distribution.

- Uncorrelated growth rates, spherical tumour: P(age over 8 years) for the 15.5 cm tumour is 0.999.
- Serial correlation (tumours that grew fast tend to keep growing fast) of 0.4 gives 0.995 and 0.8 gives 0.978.
- A flat 15.5 x 15 cm tumour whose volume equals that of a 6 cm sphere, at correlation 0.8 still gives 95%.
- For a 6 cm tumour, correlation 0.4 raises the 95th percentile of age from 30.2 to 36.9 years.
- The fastest simulated tumours take 8 years to reach 10 cm; the slowest take over 35.

Correlated draws come from a Gaussian-copula-style transform: generate correlated Gaussians, map them through the Gaussian CDF, then through the inverse of the target growth-rate CDF. At a target of 0.4, 10,000 draws produced an actual correlation of 0.37.

## Limits

- The growth-rate distribution is fitted to 53 patients, read off a printed graph because the raw data were refused; a bigger sample would change the distribution.
- Spherical geometry is probably not valid for very large tumours, and the simulation (0.3 to 20 cm) extrapolates past the observed range of 1.0 to 12.0 cm.
- Growth does not depend on subtype, grade or size; growth rates are independent between intervals except in the correlation variant, whose true value is unknown.
- Code is Python 2 era, with listings that omit an argument (Cache.Add is called with rdt but defined without it).

## See Also
- [[DGP Simulation Check]] — related (simulation as a check on a model)
- [[Grid Posteriors Over Several Parameters]] — alternative-to (explicit Bayes update on a grid)
- [[MCMC and Metropolis Sampling]] — related
