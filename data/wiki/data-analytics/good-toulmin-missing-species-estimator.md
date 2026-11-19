---
title: Good-Toulmin Missing-Species Estimator
tags: [data-analytics, bayesian-analysis, concept]
summary: The number of species or words not yet seen in a first sample can be projected from the counts of those seen once, twice and so on; the series is usable up to a doubling of the sample and a gamma prior extends it with less certainty.
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch06-empirical-bayes.md
---

# Good-Toulmin Missing-Species Estimator

In chapter 6 of *Computer Age Statistical Inference*, Efron and Hastie apply empirical Bayes to a question with no obvious prior: how many new categories will turn up if sampling continues.

## Formula

If y_k species were seen exactly k times in a first period, the expected number of new species in a further period of relative length t is the alternating series y1 times t, minus y2 times t squared, plus y3 times t cubed, and so on. Its standard error assumes the species counts are independent. The usage-weighted proportion of the unseen part of the population (the missing mass) is estimated by y1 divided by the total count N.

## Butterflies

Setup: Corbet's butterfly trapping data (Table 6.2), two years of trapping counted as one time unit, asking about a further half unit (t = 0.5). The estimate is 45.2 new species with standard error 11.2. A gamma prior (Fisher's approach) gives 123 new species for two further units, and the chapter says the plain series is unstable for t above 1.

## Shakespeare

Setup: the Shakespeare canon of 884,647 words, with 14,376 words seen once, 4,343 seen twice and 31,534 distinct words (Table 6.4). For a new body of text the size of the canon (t = 1) the estimate is at least 11,430 new distinct words (standard error 178). The missing mass is 14,376 / 884,647 = 0.016. A more elaborate linear-programming empirical Bayes analysis (Efron and Thisted, 1976) puts a firm lower bound on his unseen vocabulary of over 35,000 words (self-reported, the authors' own earlier method). For the poem "Shall I die?", 429 words long (t of 4.85e-4), the prediction was 6.97 new words against 9 found.

## Limits

- The series is unstable for t above 1. The gamma-prior extrapolation is, in the authors' words, a mathematical convenience, and projections far past the data are educated guessing.
- The standard errors (178 and 11.2) assume independence among species; the point estimates do not.
- The "Shall I die?" test is inconclusive.

## See Also
- [[Robbins Empirical Bayes Formula]] — prerequisite-for
- [[Small-N Trap and Shrinkage]] — related
