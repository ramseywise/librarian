---
title: Partial Pooling and Multilevel Models
tags: [foundations, concept]
summary: "A multilevel model estimates every group together so each borrows strength in proportion to how little data it has (weight = tau^2 / (tau^2 + sigma^2/n)); it beats both no pooling and complete pooling in simulation, but boundary estimates and few groups make the variance parts fragile."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--04-bayesian-analysis--notes--07-multilevel-models-and-partial-pooling.md
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

## When it does not help

Well-measured groups: ratio of pooled to raw RMSE 0.93, 0.99 when groups truly differ. A true outlier and the wrong centre are covered in [[Partial Pooling for Segment Winners]]. Questions about only the population average need nothing this heavy: [[Multilevel vs Fixed Effects vs Clustered Standard Errors]].

## See Also
- [[Small-N Trap and Shrinkage]] — prerequisite-for
- [[Partial Pooling for Segment Winners]] — extends
- [[Multilevel vs Fixed Effects vs Clustered Standard Errors]] — alternative-to
- [[Pseudoreplication and Intraclass Correlation]] — related
