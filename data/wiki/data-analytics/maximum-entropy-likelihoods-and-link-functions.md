---
title: Maximum Entropy Likelihoods and Link Functions
tags: [data-analytics, probability-and-statistics, concept]
summary: "McElreath's rule for choosing a likelihood is to take the maximum-entropy distribution that fits the outcome's constraints and attach a linear model through a link; the cost is that no coefficient gives a constant change on the outcome scale."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-statistical-rethinking-ch09-big-entropy-generalized-linear-model.md
  - data/raw/papers/2026-11-08-statistical-rethinking-ch10-counting-classification.md
  - data/raw/papers/2026-11-08-statistical-rethinking-ch01-golem-prague.md
---

# Maximum Entropy Likelihoods and Link Functions

*Statistical Rethinking* (first edition, chapter 9) argues that the most conservative likelihood is the one that can happen the most ways while obeying the constraints on the outcome, which is the maximum entropy distribution. A generalised linear model then replaces a parameter of that likelihood with a linear model, joined by a link function ([[Generalised Linear Models and Deviance]] covers the fitted-by-maximum-likelihood view).

## Entropy as counting

Setup: 10 numbered pebbles thrown at random into 5 buckets. The even split of 2 per bucket can happen in 113,400 distinct ways, more than any other split, and its entropy of 1.6094379 (log 5) is the highest of the five splits shown. Entropy tracks log(ways) per pebble, and is already close at 10 pebbles. The multiplicity is W = N!/(n1!...nm!).

## Which distribution follows

- Across generalised normal distributions sharing one variance, entropy is highest at the Gaussian (shape beta = 2). The chapter asserts that among continuous distributions on the whole real line with a fixed variance, the Gaussian is the entropy maximiser.
- For two unordered outcomes with a fixed expected value, the binomial maximises entropy. Setup: two marble draws with expected 1.4 blue; the binomial with p=0.7 gives probabilities (0.09 and 0.49 for the two pure outcomes, 0.21 each for the mixed ones), entropy 1.221729, and the best of 100,000 random distributions with that mean reached 1.221728.
- The Poisson arises as the binomial's limit when n is large and p small, with rate lambda = np, under the same constraints. Check: 1e5 draws from a binomial with n=1000 and p=1/1000 have mean and variance both near 1.

Gaussian-ness is an assumption about residuals once predictors are accounted for, so the raw outcome histogram is the wrong guide to the likelihood. Use a Gaussian for a continuous outcome well away from any bound, a binomial for counts out of a known number of trials, and a Poisson for counts far below any maximum.

## Link functions

A logit link maps a probability parameter onto the unbounded linear scale, and a log link does the same for a positive parameter such as sigma. Setup: with x=0 the log-odds are 0, and a half-unit rise in x lifts probability by about 0.25, with returns diminishing beyond that. The chapter's moral: in a GLM no coefficient gives a fixed change on the outcome scale, and a big beta need not be a big effect, so report predictions on the outcome scale.

Relative and absolute effects differ. Setup: chimpanzee and UCBadmit examples from chapter 10. A coefficient of 0.61 on the log-odds scale scales the odds by a factor of 1.84, yet with a made-up intercept of 4 it lifts probability only from 0.982 to 0.990, under a percentage point. The chapter advises mapping back through the inverse link and giving absolute effects next to odds ratios. It also advises modelling counts instead of proportions, since a proportion loses the sample size, and, when observation windows differ in length, putting `log(exposure)` in as an offset ([[Poisson Offsets and Overdispersion]]). Setup for the offset: two simulated monasteries, 30 daily counts at rate 1.5 and 4 weekly counts at rate 0.5 per day; the log-offset model recovered 1.61 and 0.59.

## Comparison across families

WAIC, DIC and AIC are not comparable across models with different outcome distributions, since deviance carries normalising constants. Compare within one outcome family only ([[WAIC, KL Divergence and Akaike Weights]]).

## Practices the chapter gives

Vary the link, the likelihood, the linear model and the priors in turn to test sensitivity, and publish every result. Reserve maximum-entropy priors for cases where real background knowledge about a parameter exists; weakly informative priors do otherwise. Treat any likelihood outside the exponential family as an assumption to check like the rest. Chapter 1 adds that because exponential-family distributions are maximum-entropy, a fitted regression cannot reveal the process that generated the data, though it stays useful.

## Limits

- Edition: first edition; the chapter-10 extraction infers 2016 because no date is printed.
- The chapter is conceptual: the derivations are graphical, not mathematically rigorous, and computing GLMs is deferred to later chapters.
- Maximum entropy does not guarantee the best distribution for the real problem. The book describes maximum-entropy priors but never uses them.
- A log link extrapolates exponentially, which may not hold beyond the observed range.
- The chapter-10 numbers come from an old rethinking-package workflow (`map`, `map2stan`).

## See Also
- [[Generalised Linear Models and Deviance]] — prerequisite-for
- [[Distribution Selection for Metrics]] — related (choosing a distribution from the metric)
- [[Logistic Regression Odds Ratios vs Marginal Effects]] — related (the same relative-versus-absolute point)
