---
title: CLT on Heavy-Tailed Metrics
tags: [foundations, concept]
summary: "The law of large numbers and central limit theorem only earn their keep at large N on zero-inflated heavy-tailed data: a nominal 95 percent normal interval on spend covered the truth 56 percent of the time at n=30 and needed tens of thousands of users to reach 95."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--03-distributions-and-sampling.md
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--README.md
---

# CLT on Heavy-Tailed Metrics

## Law of large numbers

The mean of N independent draws converges to the expectation. Two uses: probability is a mean (P(A) = E[1_A], so a fraction of samples estimates it) and expectations come from samples (E[f(Z)] is about the average of f over draws, which is how posterior expected loss is computed). The error shrinks like sqrt(Var) / sqrt(N): relative errors of 0.10, 0.01 and 0.001 at N = 100, 10,000 and 1,000,000 for unit variance. Halving the error costs four times the data.

## Central limit theorem

Means of many independent draws are approximately Normal with SE sigma / sqrt(N) whatever the original shape, which is why t- and z-tests work on conversion and revenue. The catch is "moderate N". N >= 30 comes from well-behaved data. Spend per user that is mostly zeros plus a lognormal tail is about as bad as data gets.

Simulation (buy probability 0.047, lognormal order value), share of 95% normal intervals that contain the true mean:

| n | skew of the sample mean | coverage |
|---|---|---|
| 30 | 4.68 | 0.563 |
| 300 | 1.34 | 0.832 |
| 3,000 | 0.46 | 0.928 |
| 30,000 | 0.22 | 0.948 |

Most small samples contain few whales, so they underestimate both the mean and the spread and sit confidently below the truth. The formula never warns you because its SE is estimated from the same sample.

| Condition | Approximation |
|---|---|
| Symmetric, light tails, N >= 30 | good |
| Proportions with np and n(1-p) both >= 10 | good |
| Heavy tails (revenue, session length) | slow; use more N, a non-parametric test, or the bootstrap |
| N < 30, unknown sigma | t distribution |

The theorem also needs independence and finite variance. Dependent rows break the first ([[Pseudoreplication and Intraclass Correlation]]); some extreme tails break the second, and then a mean never settles.

## Check by simulation

Treat the 95% label as a claim and test coverage by simulating from a model of your data. Making 30% of users buy instead of 4.7% raises coverage at n = 300 because far fewer samples are mostly zeros, though the lognormal tail still costs.

## See Also
- [[Bootstrap Resampling and Its Failures]] — alternative-to (resample instead of trusting the normal approximation)
- [[Data Defect Correlation]] — related (the CLT describes sampling error, not selection bias)
- [[Distribution Selection for Metrics]] — prerequisite-for
- [[Confidence Interval Coverage and Wilson]] — related
- [[Minimum Detectable Effect and Sample Size]] — related (the same 1/sqrt(N) arithmetic)
