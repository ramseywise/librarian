---
title: Observed Fisher Information and Ancillary Conditioning
tags: [data-analytics, probability-and-statistics, concept]
summary: The maximum likelihood estimate's accuracy can be stated from the curvature of the observed log-likelihood, and conditioning on an ancillary statistic such as the sample size gives the inference that matches the data actually seen.
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch04-fisherian-inference-maximum-likelihood-e.md
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch05-parametric-models-exponential-families.md
---

# Observed Fisher Information and Ancillary Conditioning

Efron and Hastie (*Computer Age Statistical Inference*, ch. 4) review Fisher's tools: maximum likelihood, Fisher information, conditional inference and permutation inference.

## Information and accuracy

The score is the derivative of the log-likelihood in theta and has mean zero. Fisher information I is its variance, also E{-l-double-dot}. For an iid sample the total information is n I, and in large samples the maximum likelihood estimate is approximately N(theta, 1/(nI)); the Cramer-Rao bound says no nearly unbiased estimate does better. For normal sampling with known variance, I = 1/sigma^2 and the estimate is xbar ~ N(mu, sigma^2/n).

The observed information I(x) = -l-double-dot at the estimate gives the alternative N(theta-hat, 1/I(x)). The authors advise it over the plug-in 1/(nI(theta-hat)). Setup for the check: Cauchy location family with theta = 0, samples of 20, 10,000 of them. The conditional variance of the estimate tracks 1/I(x) closely, ranging from 0.05 to 0.20, while the unconditional 1/(nI) is 0.10.

## Conditioning on an ancillary

An ancillary statistic carries no direct information by itself but fixes the frame for frequentist calculation. Setup: x_i iid N(mu, 1) with n = 25 or 100 chosen by a fair coin, and n = 25 happened. The conditional standard deviation of xbar is 0.2; averaging over both sample sizes gives 0.158. Fisher's conditional test for the ulcer table (45 patients, new against old surgery; margins 16, 29, 21 and 24) holds the margins fixed and asks only if the upper-left count of 9 is unusually big; it was not significant.

## More than one parameter

For a multi-parameter family the estimate is approximately N_p(theta, I^-1) with I the covariance of the score. Extra nuisance parameters never decrease the variance of the estimate of interest: (I^-1)_11 >= 1/I_11. Setup: bivariate normal, sample size n. If the nuisance mean is known, the variance of the estimate of mu1 shrinks from sigma11/n to (sigma11/n) times (1 - rho^2). The chapter notes biased methods such as empirical Bayes and l1 regression can reverse this variance tax.

## Plug-in danger

Setup: prostate data, 6033 genes, estimates theta_i-hat = x_i, target the largest coordinate of theta. The plug-in maximum likelihood estimate is a flagrant overestimate. Bias of the estimate is O(1/n) against a standard deviation of O(1/sqrt n), which makes squared bias negligible except in high-dimensional plug-in problems.

## Limits

- The derivations are heuristic and need regularity conditions for differentiating under the integral.
- The normality of the estimate is a large-sample approximation with no finite-n accuracy given.
- That an ancillary "contains no information" is contentious; Fisher's inductive logic and his fiducial inference have fallen from favour.

## See Also
- [[Maximum Likelihood and Estimator Bias]] — prerequisite-for
- [[Exponential Families and Tilting]] — related
- [[Permutation Test]] — related (Fisher's randomisation inference)
- [[James-Stein Estimator and Shrinkage]] — related
