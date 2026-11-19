---
title: WAIC, KL Divergence and Akaike Weights
tags: [data-analytics, probability-and-statistics, concept]
summary: "McElreath builds the target of model comparison from entropy and K-L divergence, estimates out-of-sample deviance with AIC, DIC or WAIC, and uses Akaike weights to average predictions instead of picking one model."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-statistical-rethinking-ch06-overfitting-regularization-information-criteria.md
  - data/raw/papers/2026-11-08-statistical-rethinking-ch01-golem-prague.md
  - data/raw/papers/2026-11-08-statistical-rethinking-ch07-interactions.md
  - data/raw/papers/2026-11-08-statistical-rethinking-ch05-multivariate-linear-models.md
---

# WAIC, KL Divergence and Akaike Weights

Chapter 6 of *Statistical Rethinking* (first edition) asks how to balance simplicity against accuracy. Fit to the sample misleads: setup, hominin brain volume against body mass for 7 species, polynomials of degree 1 to 6, flat priors. R2 climbs with every added degree, from 0.49 for a line to 0.99 at degree 5, and degree 6 hits all 7 points exactly (R2 = 1) while forecasting a negative brain size near 58 kg. The table in [[Model Selection Criteria]] covers the older AIC and BIC; this page is the information-theoretic route.

## The target: divergence, then deviance

Information entropy is H(p) = -Σ p_i·log(p_i). K-L divergence measures the added uncertainty from using one distribution to stand in for another, and it is asymmetric: setup, Earth q = {0.7, 0.3} and Mars p = {0.01, 0.99}; Earth as a model of Mars costs 1.14, Mars as a model of Earth costs 2.62. Deviance, D(q) = -2 sum log(q_i), estimates relative distance from the target. In the weather-forecast example, the forecaster with the higher hit rate (0.7 against 0.58) assigns the observed days a worse joint probability (0 against about 0.005).

## Train versus test deviance

Setup: y ~ Normal(mu, 1) with mu = 0.15 x1 - 0.4 x2, candidate models with 1 to 5 parameters, 10,000 simulations each, flat priors. Training deviance drops with every added parameter, while at N=20 out-of-sample deviance bottoms out with 3 parameters, matching the generating model. The gap between test and training deviance is about double the parameter count (from 2 up to about 9.7 across the five models at N=20, and from 1.9 to about 8.5 at N=100).

## The three estimators

| Criterion | Formula | Conditions the chapter gives |
|---|---|---|
| AIC | Dtrain + 2p | needs flat priors, a roughly Gaussian posterior, and N far above the parameter count |
| DIC | Dbar + pD, with pD = Dbar - Dhat | multivariate Gaussian posterior, N much greater than the number of parameters; reduces to AIC under flat priors |
| WAIC | -2(lppd - pWAIC), computed pointwise | does not assume a Gaussian posterior; usually beats DIC in accuracy |

Here lppd sums, over cases, the log of the average likelihood, and pWAIC sums the variance of each case's log-likelihood. In the 10,000-simulation setup (N=20, with Normal(0,100) as the loose prior and Normal(0,0.5) as the tight one), DIC and WAIC were mostly within a point of the true average out-of-sample deviance, with WAIC the closer. Chapter 9 adds that deviance includes normalising constants, so the criteria cannot compare models with different outcome distributions ([[Maximum Entropy Likelihoods and Link Functions]]).

## Regularisation and criteria together

A Normal(0,1) prior on a standardised predictor leaves only 5% plausibility beyond 2 SD. Setup: rerunning it with priors of Normal(0,1), then Normal(0,0.5), then Normal(0,0.2) on the betas (intercept left alone). At N=20 the Normal(0,0.2) prior makes the 4- and 5-parameter models only slightly worse than the true 3-parameter one; at N=100 the data swamp even that prior. The author reads from a simulation figure that regularisation combined with information criteria beats either alone ([[Regularisation as a Prior]]).

## Comparing and averaging

Setup: primate milk, 17 complete cases, four models, flat priors, `map` fits. The best model (neocortex plus log mass) has WAIC -15.0, pWAIC 4.8 and weight 0.93. Its difference from the intercept-only model (6.7 WAIC) has dSE 7.26, and a simulated probability of 0.1773 that the difference is reversed. The two single-predictor models rank worse than the intercept-only one (WAIC -7.9 and -6.2 against -8.3).

The Akaike weight is w_i = exp(-0.5·dWAIC_i) divided by the sum of the same term over all models, interpreted as the probability of predicting best on new data given the model set. Averaging the four models with these weights hardly changed the mean prediction but widened the interval enough to admit a zero neocortex slope. The chapter advises fitting all compared models to precisely the same observations, judging WAIC differences with dSE instead of overlapping single SEs, averaging predictions rather than parameters, and avoiding searches over every combination (the "Curse of Tippecanoe"; compare [[Stepwise Selection and Overfitting on Noise]]).

Two other cases in the book use the same tool. In chapter 7's rugged-country data, the interaction model m7.5 takes most of the WAIC weight over the dummy-only model, yet dSE is nearly as large as the difference ([[Linear Interactions and Centring]]). In chapter 5 the author warns that bias from conditioning on a post-treatment variable passes unnoticed: the fungus model scores better and would forecast better out of sample, yet it answers the wrong question ([[Masked Relationships and Collinear Predictors]]).

## Limits

- Edition: first edition (`map`, `map2stan`, DIC); later editions swap these for `quap`, `ulam` and PSIS-LOO. The chapter's hard practice problems carry no printed solutions.
- The criteria are heuristics without guarantees and presume that test data come from the training process. They do not consistently pick out the true model.
- AIC needs flat priors, a Gaussian posterior and N far above k; DIC needs a Gaussian posterior; WAIC is hard to define when observations are dependent, as in time series.
- Akaike weights shift with the set of models compared; the SE of WAIC is rough in small samples; no principled WAIC-difference threshold for "significance" exists.
- The extraction's chapter-7 note says WAIC use on nations is debated there, since no one resamples countries.

## See Also
- [[Model Selection Criteria]] — alternative-to (AIC, BIC and cross-validation compared on one simulation)
- [[Regularisation as a Prior]] — prerequisite-for
- [[Explain vs Predict Modelling]] — related
