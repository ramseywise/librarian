---
title: Grid and Quadratic Approximation and Posterior Samples
tags: [data-analytics, bayesian-analysis, concept]
summary: "McElreath's chapters (first-edition era, inferred from the code) compute a posterior on a grid or as a Gaussian at its peak, then answer every question by counting posterior samples: intervals, point estimates under a loss, predictions that carry parameter uncertainty."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-statistical-rethinking-ch02-small-worlds-large-worlds.md
  - data/raw/papers/2026-11-08-statistical-rethinking-ch03-sampling-imaginary.md
  - data/raw/papers/2026-11-08-statistical-rethinking-ch04-linear-models.md
  - data/raw/papers/2026-11-08-statistical-rethinking-ch10-counting-classification.md
---

# Grid and Quadratic Approximation and Posterior Samples

McElreath (*Statistical Rethinking*, first-edition era inferred from the rethinking R package's `map`) treats the posterior as something to compute and then sample. Two approximations come before MCMC ([[MCMC and Metropolis Sampling]]); once any of the three engines has produced samples, the summaries are the same.

## Grid approximation

The recipe: lay a grid over the parameter, evaluate the prior and the likelihood at each point, multiply them, then normalise by the total. Globe-tossing setup: 6 waters in 9 tosses, uniform prior. Twenty grid points already do well, a single parameter gains little beyond a hundred, and five points is awful. Cost explodes with parameter count: two parameters at 100 values apiece need 10,000 evaluations, and ten need billions.

## Quadratic approximation

Locate the posterior mode, measure the curvature there (the Hessian of the log posterior) and replace the posterior with a Gaussian. For the same globe data with a uniform prior and binomial likelihood, this gives mode 0.67, SD 0.16 and an 89% interval from 0.42 to 0.92, compared against the exact Beta(w+1, n-w+1) posterior. At a fixed water fraction the approximation is poor with 9 tosses (it assigns mass to p=1 though land appeared), better with 18 and nearly exact with 36, judged by eye with no numeric error reported.

For sigma in a Gaussian height model fitted to only 20 adult heights, the posterior has a long right tail, so a Gaussian is a poor description unless log(sigma) is estimated instead. For binomial regression the chapter-10 guidance is that the quadratic approximation tends to be accurate only when no intercept lies far from zero and no predictor strongly tracks the outcome; it recommends checking against MCMC for every GLM. Example: in the chimpanzee interaction model MCMC gave bp=0.62 and bpC=-0.11 with n_eff near 3000 and Rhat of 1, so the approximation held there. With a separate intercept per actor, the always-left actor's intercept was 10.91 (SD 5.42) with a heavily skewed posterior.

## Sampling instead of integrating

Draw samples from the grid posterior in proportion to its probability (1e4 samples from a 1000-point grid in the chapter). Counting samples then answers integral questions: the mass below p=0.5 was 0.1718746 on the grid and 0.1726 from samples.

| Summary | What it is | 3-of-3 water example (flat prior, 1000-point grid, 1e4 samples) |
|---|---|---|
| Percentile interval | equal probability mass in each tail | 50% interval 0.7037037 to 0.9329329, which excludes the mode at p=1 |
| HPDI | narrowest interval holding the stated mass | 50% interval 0.8408408 to 1.0, width 0.16 against 0.23 |
| Posterior median | minimises expected absolute loss | 0.8408408 |
| Posterior mean | minimises quadratic loss (as the chapter states) | 0.8005558 |

McElreath recommends percentile intervals when the posterior is roughly symmetric and HPDI when it is skewed, plotting the full posterior when the choice matters, and showing nested 67%, 89% and 97% intervals rather than a default 95%. A single point estimate is seldom necessary; when it is, a loss function should choose it ([[Bayes Action and Loss Functions]]). Intervals depend on the model: a poor model can still produce tight ones.

## Predictions that carry parameter uncertainty

To simulate the posterior predictive distribution, draw a parameter from the samples, then draw an outcome given it (`rbinom(1e4, size=9, prob=samples)`); plugging in a single point estimate understates uncertainty. Setup: the globe data (6 waters in 9 tosses). The observed count falls mid-distribution and the longest run of 3 is plausible, but the 6 observed switches exceed what the model predicts, which the chapter reads as negative correlation between tosses. Check several summaries, not just the one the model fits ([[Posterior Predictive Checks]]).

A regression line yields two distinct intervals: one for the mean mu (parameter uncertainty) and a wider prediction interval that adds sigma (sampling variation). Setup: !Kung adults (Howell1, n=352), height on weight; mean height at 50 kg has an 89% HPDI of 158.56 to 159.66 cm, and sigma is 5.07 cm.

## A prior counts as observations

With a Gaussian likelihood, a Normal(178, 0.1) prior on mean height carries the weight of about 100 observed heights averaging 178 (posterior sigma = 1/sqrt(n), so n = 100 for prior SD 0.1), while Normal(178, 20) is worth about 0.0025 of an observation. Fitting with the tight prior pinned the mean near 178 and pushed sigma from 7.73 up to 24.52 (same adult data, n=352).

## Limits

- Edition: not printed in chapters 2 or 3; the first-edition era is inferred from the `map` code (chapter 2 notes `map` was later replaced by `quap`), and chapter 4 is labelled first-edition style. Only chapter 10 names the first edition. All code is R and dated.
- Every dataset in chapters 2 and 3 is a toy (globe tossing, marble bag); the numbers are sample-dependent and there are no benchmarks.
- The grid scales poorly with parameters; the quadratic approximation needs large samples or a near-Gaussian posterior; the 95% convention and interval coverage are small-world numbers.
- Chapter 10 warns that MAP estimation cannot be trusted for any GLM as a matter of principle, so quadratic fits should be checked against MCMC.
- A confident posterior is not a good model: every estimate is conditional on the model being right.
- Model checking is left to later chapters; chapter 3 shows only summaries.

## See Also
- [[Beta-Binomial Updating and Credible Intervals]] — prerequisite-for (the conjugate result the grid reproduces)
- [[Bayes Action and Loss Functions]] — related (which point estimate a loss selects)
- [[Posterior Predictive Checks]] — extends
- [[Prior Choice and Prior Predictive Checks]] — related
