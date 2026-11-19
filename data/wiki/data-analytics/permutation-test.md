---
title: Permutation Test
tags: [data-analytics, probability-and-statistics, pattern]
summary: "A permutation test builds the null distribution by shuffling group labels, needing few assumptions; classical t-tests are approximations to it and agree closely on well-behaved data."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--05-hypothesis-testing.md
  - data/raw/papers/2026-11-08-practical-statistics-for-data-scientists-ch03-statistical-experiments-significan.md
  - data/raw/papers/2026-11-08-think-stats-ch07-hypothesis-testing.md
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch04-fisherian-inference-maximum-likelihood-e.md
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

## Two more worked comparisons

- Think Stats (chapter 7, NSFG data): first babies (4,413) and other babies (4,735) differ in mean pregnancy length by 0.078 weeks. Resampling the pooled data with 1,000 sample pairs, two-sided, gives p of about 0.166. A normal-theory calculation agrees; under the null the difference of means has variance about 0.0032.
- Computer Age Statistical Inference (chapter 4, leukemia data, 47 ALL and 25 AML patients): for gene 136, a permutation test with B = 10,000 on the two-sample t-statistic found 26 permuted values at least as large in absolute terms as the observed one, a significance of 0.0026 against 0.0025 from normal theory. The text calls this agreement "a little lucky" and says data that were not randomised cannot support a causal reading.

## Worked examples from the book

In *Practical Statistics for Data Scientists* (chapter 3, R, worked examples), classical tests land near the resampling answer:

| Setup | Resampling p | Classical p |
|---|---|---|
| Price test, 200 of 23,739 vs 182 of 22,588 conversions; 1,000 shuffles of the pooled outcomes (382 conversions, 45,945 non-conversions), one-sided | 0.308 | 0.3498 (`prop.test`, continuity correction) |
| Web stickiness, session-time difference of 21.4 seconds, 21 vs 15 sessions, one-sided | 0.124 | 0.1408 (Welch) |
| One-way ANOVA, four pages with 5 visitors each | 0.09278 | 0.0776 (F = 2.74) |
| Three headlines of 1,000 visitors each, null that all share one click rate of 34 in 3,000 | 0.4853 | 0.4348 (chi-square distribution); Fisher exact 0.4824 |

The authors read the price result as a difference within chance variation. They advise a permutation test as an assumption-light check and for very small counts (single digits), Fisher's exact test or resampling rather than the chi-square approximation.

## Limits

Shuffling assumes exchangeability under the null: individuals must be independent units, so cluster-assigned data must be shuffled at the cluster level ([[Pseudoreplication and Intraclass Correlation]]). It tests a null of no effect, not a particular interval; for that use the [[Bootstrap Resampling and Its Failures]].

- Practical Statistics ch03: the examples are hypothetical or simplified single runs with no power curves. Its Bonferroni description divides alpha by the number of observations where the number of tests is meant, and its authors say a p-value should not control a decision.
- The Think Stats example is a single dataset with Python 2-era code, and the Computer Age chapter is a heuristic review that gives one gene as its example.

## See Also
- [[Statistical Test Selection]] — related
- [[Independence Pitfalls]] — related
- [[Observed Fisher Information and Ancillary Conditioning]] — related
