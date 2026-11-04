---
title: Permutation Test
tags: [foundations, pattern]
summary: "A permutation test builds the null distribution by shuffling group labels, needing few assumptions; classical t-tests are approximations to it and agree closely on well-behaved data."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--05-hypothesis-testing.md
---

# Permutation Test

## Mechanism

If the treatment does nothing, group labels are arbitrary. Shuffle the labels many times, recompute the difference each time, and the shuffled differences are the null distribution. The p-value is the share of shuffles at least as extreme as the observed difference.

## Agreement with classical tests

On 400 users per arm, Welch's t-test gave p = 0.009 and the permutation test p = 0.007. The classical tests are approximations to this procedure, which is why they work when the sampling distribution is close to Normal ([[CLT on Heavy-Tailed Metrics]]).

## When it helps

- Awkward statistics with no formula (a median difference, a ratio).
- Skewed or small samples where the Normal approximation is doubtful.
- It teaches what a p-value is ([[P-Value Misreadings]]).

## Limits

Shuffling assumes exchangeability under the null: individuals must be independent units, so cluster-assigned data must be shuffled at the cluster level ([[Pseudoreplication and Intraclass Correlation]]). It tests a null of no effect, not a particular interval; for that use the [[Bootstrap Resampling and Its Failures]].

## See Also
- [[Statistical Test Selection]] — related
- [[Independence Pitfalls]] — related
