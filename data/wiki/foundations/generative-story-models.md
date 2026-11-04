---
title: Generative Story Models
tags: [foundations, pattern]
summary: "Build a Bayesian model by writing how the data could have been generated, top down, and translating each line into a distribution; a known measurement process (a changepoint, randomised response, serial numbers) goes into the model, not into a correction afterwards."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--04-bayesian-analysis--notes--01-bayesian-inference.md
---

# Generative Story Models

The method: write the story of how the data came about, then turn each line into a distribution. If you can simulate fake data from the story, you can fit it. Questions a point estimate cannot answer become averages over posterior samples.

## Changepoint in a count series

74 daily message counts, mean 19.74; did the rate change?

| Story | Distribution |
|---|---|
| Count on day i | Poisson(lambda_i) |
| Rate is lambda_1 before day tau, lambda_2 after | switch on tau |
| Rates positive, near the observed mean | Exponential(1 / mean) |
| The switch could be any day | DiscreteUniform over the days |

Because tau is discrete, NUTS cannot run and Metropolis is used (see [[MCMC and Metropolis Sampling]]). Posterior: lambda_1 about 17.76, lambda_2 about 22.68, P(lambda_2 > lambda_1) = 0.9994. The mass on tau sat on four days (45: 0.489, 44: 0.354, 43: 0.117, 42: 0.037). A changepoint test returns one date; this returns a ranking of dates, and the honest answer is that the data cannot quite separate adjacent days. The expected count on day 44 came out between the two rates (20.2) because the model is unsure which side of the switch it lies on: compute per sample, then average.

## Measurement process inside the model: randomised response

To estimate a sensitive rate, each respondent flips a coin: heads, answer honestly; tails, flip again and say "yes" on heads. Then P(yes) = 0.5 p + 0.25, written directly as a deterministic node. With 35 "yes" of 100 the posterior mean of p was 0.207, 95% interval [0.035, 0.392]; asked directly, the same answers would give [0.264, 0.448]. The privacy mechanism costs information (interval about 0.36 wide against 0.18), since half the answers are noise, yet it still all but rules out "nobody" and "most people". The lesson: a known measurement process belongs in the likelihood.

## Posterior shape: a one-line posterior

For k serial numbers drawn from 1..N, the likelihood is (1/N)^k for N at least the largest serial, so a flat prior gives a posterior computable on a grid. With 15 serials and a maximum of 912: unbiased estimator 971.8; posterior mean 982, median 958, MAP 912; 95% interval [913, 1186]; P(N > 1100) = 0.071. The summaries disagree because of a long right tail, and which is "the" estimate depends on the cost of being wrong (see [[Bayes Action and Loss Functions]]). In simulation with N = 1,000 the unbiased estimator (mean 999.8, rmse 62.3) beats the maximum seen (mean 938.3, rmse 85.0) despite slightly larger spread: bias costs more than spread saves.

## Failure modes

- Supports narrower than the truth, such as an upper limit below the real N.
- Treating one summary of a skewed posterior as the answer.

## See Also
- [[Beta-Binomial Updating and Credible Intervals]] — prerequisite-for (the conjugate case)
- [[Data Generating Process Simulation Check]] — related (simulating from the story to test it)
- [[Maximum Likelihood and Estimator Bias]] — related (biased versus unbiased estimators)
- [[Mixture Models and Label Switching]] — related (another model written from a story)
