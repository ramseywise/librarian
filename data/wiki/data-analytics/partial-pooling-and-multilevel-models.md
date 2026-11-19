---
title: Partial Pooling and Multilevel Models
tags: [data-analytics, bayesian-analysis, concept]
summary: "A multilevel model estimates every group together so each borrows strength in proportion to how little data it has (weight = tau^2 / (tau^2 + sigma^2/n)); it beats both no pooling and complete pooling in simulation, but boundary estimates and few groups make the variance parts fragile."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--04-bayesian-analysis--notes--07-multilevel-models-and-partial-pooling.md
  - data/raw/papers/2026-11-08-statistical-rethinking-ch12-multilevel-models.md
  - data/raw/papers/2026-11-08-statistical-rethinking-ch01-golem-prague.md
---

# Partial Pooling and Multilevel Models

Three ways to estimate one number per group: **no pooling** (the group's own mean: unbiased, noisy when small), **complete pooling** (the overall mean: stable, erases real differences) and **partial pooling** (a weighted average). With tau the sd of true group means and sigma the sd within a group, a group of n units puts this weight on its own mean:

weight = tau^2 / (tau^2 + sigma^2 / n)

The term sigma^2/n is the noise in the group's own mean, so noisy groups get little weight. The model estimates tau and sigma from data (REML for the variances), which distinguishes it from a hand-picked shrinkage factor. [[Small-N Trap and Shrinkage]] gives the intuition; this page is the machinery.

## Simulation: 40 groups of very different size

Truth: tau 6.0, sigma 30.0; 2,221 users, group sizes 5 to 262 (median 40). Estimates were 5.77 and 29.74. A 5-user group measured 54.26 against a truth of 45.39; its weight was 0.16 and it was pulled to 42.10. A 262-user group had weight 0.91 and barely moved. A 20-user group puts weight 0.43 on its own mean in a related exercise.

| RMSE against truth | No pooling | Complete | Partial |
|---|---|---|---|
| All groups | 5.69 | 5.47 | 3.54 |
| Small (under 30 users), 13 groups | 8.21 | 4.61 | 4.17 |
| Middle, 24 groups | 4.11 | 5.95 | 3.32 |
| Large (150 or more), 3 groups | 2.31 | 4.82 | 2.06 |

Over 200 new datasets: 5.13, 5.98 and 3.47; partial beat no pooling in 96% and complete pooling in 100%. Partial pooling acts like the better of the other two at each size without being told which: complete pooling underfits, no pooling overfits.

## ICC and the design effect

The intraclass correlation tau^2 / (tau^2 + sigma^2) is the share of variance between groups and the correlation between two units in a group ([[Pseudoreplication and Intraclass Correlation]]). Here the true ICC was 0.038 and the estimate 0.036, yet the design effect was 2.98 using the mean group size (56), 4.74 using the user-weighted size (104) and exactly 4.95 from the true variances. The formula assumes equal groups; weighting by users is closer. A clustered standard error from one dataset implied 3.85, showing how noisy a single estimate with 40 groups is.

## Random intercepts and slopes

A random intercept gives each group its own level; a random slope its own effect of a predictor. For 150 users over 6 weeks the week coefficient was 1.300 in every fit (balanced panel), but SEs differed: naive OLS 0.296, random intercepts 0.222, with random slopes 0.276, clustered OLS 0.277. Random intercepts alone are about 20% too small when slopes vary. Naive OLS was not too small here because week varies only within a user. Note "hierarchical regression" in psychology often means adding predictor blocks in stages, which is unrelated.

## Two toolkits and boundary estimates

A linear MixedLM and a non-centred PyMC model ([[Divergences and Non-Centred Parameterisation]]) agreed to within 0.03 on every parameter, with user effects correlated 1.000, and pooling cut the error on each user's trend from 2.27 (own OLS line) to 1.30. But when the true slope sd shrank from 2.5 to 1.0, MixedLM reported slope sd 0.46 and a correlation of exactly 1.00 with no warning: a boundary estimate, meaning the model is too rich for the data. PyMC gave 0.28 with a 90% interval of -0.27 to 0.79, and less sampler margin (min bulk ESS 266, r-hat 1.009).

## Few groups

Tau is estimated from groups, so the number of groups is its sample size. With true tau 6.0, REML over 300 datasets: 3 groups median 5.06, 5th to 95th percentile 0.00 to 15.53, 11% at zero; 5 groups 0.00 to 10.87, 8% at zero; 8 groups 1.31 to 9.91; 20 groups 3.25 to 8.02; 50 groups 4.67 to 7.34. At zero everything is pooled completely. For five groups MixedLM gave tau 2.52 as a bare number, PyMC 3.91 with 90% interval 0.37 to 9.74, so the Bayesian interval states the real ignorance (and had one divergence).

## Varying intercepts in Statistical Rethinking

McElreath (first edition, chapter 12) calls models whose parameters are independent across clusters, forgetting earlier clusters as they go, anterograde-amnesia models, and advises making multilevel regression the default: start multilevel and simplify only if it proves unnecessary. Chapter 1 adds that a paper that skips multilevel modelling owes readers a justification. Fit with MCMC (`map2stan`), because the quadratic approximation cannot handle these models.

- Reed frog tadpoles (48 tanks, binomial survival): the varying-intercept model m12.2 uses roughly 38 effective parameters of 50 nominal and beats the fixed-intercept model m12.1 by 13.1 WAIC. The SD across tanks is about 1.6. Every tank's multilevel estimate lies nearer the grand mean than its raw proportion, with the strongest shrinkage for small tanks (sizes 10, 25 and 35) and for tanks far from that mean.
- Simulated ponds (true alpha 1.4 and sigma 1.5; 60 ponds, 15 at each size n = 5, 10, 25 and 35; one data set, one chain): on average partial pooling has lower error than no pooling at every size, and the advantage widens as ponds shrink (read qualitatively from a figure); some small ponds have no-pooling errors over 20%. Ponds with extreme survival probabilities are the exception, where no pooling can do better. The fit estimates sigma as 1.59 (SD 0.22) against a true value of 1.5 and alpha at 1.13 (SD 0.23) for a true 1.4.
- Chimpanzees (7 actors, 6 blocks, cross-classified): adding block intercepts adds 7 parameters but about 2.5 effective ones (pWAIC 10.5 against 8.1), and the WAIC difference between the actor-only and actor-plus-block models is 1.2 with dSE 1.94. Variation among actors (sigma 2.25, sd 0.90) far exceeds that among blocks (0.22, sd 0.18). Three divergent iterations appeared; the author calls them safe to ignore at that stage and defers them to the next chapter.
- Over-dispersion: a varying intercept per observation handles it in Poisson or binomial models; the Kline model m12.6 has 13 parameters for 10 societies and about 5 effective ones.
- Exponential(1) is advised over half-Cauchy for the variance when there are few clusters (such as 5) or floor and ceiling effects. For a new cluster, simulate intercepts from Normal(0, sigma) for each posterior sample.

Slopes that vary too are in [[Varying Slopes and the LKJ Correlation Prior]].

## When it does not help

Well-measured groups: ratio of pooled to raw RMSE 0.93, 0.99 when groups truly differ. A true outlier and the wrong centre are covered in [[Partial Pooling for Segment Winners]]. Questions about only the population average need nothing this heavy: [[Multilevel vs Fixed Effects vs Clustered Standard Errors]].

## Limits

- Statistical Rethinking material above: first-edition code, a single simulation setting and draw, and no numeric errors printed for the pond comparison.

## See Also
- [[Small-N Trap and Shrinkage]] — prerequisite-for
- [[Partial Pooling for Segment Winners]] — extends
- [[Multilevel vs Fixed Effects vs Clustered Standard Errors]] — alternative-to
- [[Pseudoreplication and Intraclass Correlation]] — related
- [[Varying Slopes and the LKJ Correlation Prior]] — extends
- [[Linear Interactions and Centring]] — related
- [[Grid Posteriors Over Several Parameters]] — related (a two-level grid model)
- [[James-Stein Estimator and Shrinkage]] — extends
- [[Robbins Empirical Bayes Formula]] — related
- [[Empirical Bayes: Tweedie's Formula and g-Modeling]] — related
