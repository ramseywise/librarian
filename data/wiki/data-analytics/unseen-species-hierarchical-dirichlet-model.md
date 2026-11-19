---
title: Unseen Species Hierarchical Dirichlet Model
tags: [data-analytics, bayesian-analysis, pattern]
summary: "Estimate how many species exist, how prevalent each is and how many new ones more sampling would find, with a Dirichlet prior over prevalences nested under a prior on the species count, simulated forward for predictions."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-think-bayes-ch15-dealing-dimensions.md
---

# Unseen Species Hierarchical Dirichlet Model

Chapter 15 of Downey's *Think Bayes* (1st edition) poses the Unseen Species problem: given a sample of reads (identified fragments), estimate the total number of species n, each species' prevalence, and the number of new species further reads would reveal. "Species" is used loosely; the precise term is operational taxonomic unit. The data are Belly Button Biodiversity pilot samples.

## Model

Prevalences must sum to 1, so Downey uses a Dirichlet prior (the multi-dimensional generalisation of the beta) and not independent betas. Toy case: a Dirichlet prior with all parameters 1 and observed counts of 3 lions, 2 tigers and 1 bear yields posterior mean prevalences of 44%, 33% and 22%. On top sits a uniform prior over n. With the three-species toy data and n uniform from 3 to 29, n is most likely 4, values up to 7 are plausible and 29 has negligible probability.

## Making it scale

- Keep an easy, slow implementation to test the optimised ones (Species5 is the optimised model) against.
- Reuse one set of random draws for every hypothesis, which makes the comparison fairer and converges sooner.
- Update one species at a time; the author's complexity argument is cost proportional to k times m (k hypotheses, m observed species), against k times m squared for the Dirichlet-object version; no timings are given.
- Feed the data in as several sequential updates if the joint likelihood is so peaked that Monte Carlo sampling rarely lands on it; this gives the same posterior as one batch update.
- Work in log-likelihoods, subtract the maximum, and drop factors that depend only on the data, such as the multinomial coefficient.

## Results on subject B1242

400 reads gave 61 observed species, with many singletons (24 or more counts of 1).

- The most probable n is 72 (90% credible interval 66 to 79) under the Species5 model; the range of n used is not stated. Exactly 61 species is nearly impossible and 87 or more is unlikely.
- The most prevalent species is 23% of reads, yet its estimated prevalence is only about 20% (90% interval 17% to 23%), since some species were never seen.
- Prediction by simulation: draw n from the posterior, prevalences from the Dirichlet, then future reads. After 100 more reads the median number of new species is 2 (90% interval 0 to 5); after 800, 3 to 12 are expected. Coverage (observed species over n) reaches 90% with about 40% chance after 200 more reads and about 90% after 1000.

## Limits

- Every organism is assumed equally likely to be read; the author grants that the swabbing and amplification steps may skew which species appear.
- The uniform prior on n is a convenience, with the upper bound judged by looking at posterior tail mass.
- Optimised versions were validated only against simpler versions, not ground truth. The Monte Carlo likelihood uses a fixed 1000 iterations with no convergence diagnostics or timings.
- The author skipped details needed to validate on real data. Code is Python 2 era on thinkbayes.

## See Also
- [[Grid Posteriors Over Several Parameters]] — prerequisite-for
- [[Mixture Models and Label Switching]] — related
- [[Partial Pooling and Multilevel Models]] — related (a model with levels)
