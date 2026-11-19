---
title: "Locomotive Problem: Estimators and Losses"
tags: [data-analytics, probability-and-statistics, concept]
summary: "Guessing how many locomotives a railway owns from one observed serial number gives different best answers under different criteria: the maximum likelihood, minimum squared error and unbiased estimators are i, 3i/2 and 2i, and a Bayesian posterior shows how weak one observation is."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-think-stats-ch08-estimation.md
---

# Locomotive Problem: Estimators and Losses

In chapter 8 of *Think Stats*, Downey sets a puzzle: N trains are numbered 1 to N, you see one numbered i, and you want to estimate N with a guess of the form a times i. Which a is best depends on what "best" means.

## Four answers

- **Maximum likelihood:** N-hat = i. The likelihood of seeing i is 1 over N-hat when i is at most N-hat.
- **Minimum mean squared error:** setting the derivative of the MSE to zero gives a = 3N/(2N+1), which tends to 3/2 for large N.
- **Unbiased:** setting the mean error to zero gives a multiplier that tends to 2 for large N, so N-hat = 2i.
- **Population mean equals sample mean:** 2i - 1.

Downey reads the disagreement as each estimator behaving as if it started from a different prior: they agree only once the evidence overwhelms the prior, and with scarce data no one estimator has every desirable property.

## A matching game

Suppose a game pays only for naming the exact total of three six-sided dice. The MSE-minimising guess of 10.5 is a poor answer, while the maximum likelihood guess of 10 or 11 succeeds one time in eight. Downey's rule: use the mean for MSE when there are no outliers, the median when outliers are present, and the MLE when only an exact hit counts. One outlier, a misplaced decimal point turning the last value of a six-value normal sample into -213.8, drags the sample mean far from its clean-sample value.

## The Bayesian version

Downey's recipe starts from a uniform prior across evenly spaced hypotheses, multiplies by the likelihood and normalises, then a 90% credible interval read from the 5th and 95th percentiles. Seeing train 60 under a uniform prior from 1 to 200 (200 hypotheses) gives a wide interval, so one observation is weak evidence. He warns that a frequentist 90% confidence interval does not mean a 90% chance the parameter lies inside it; a posterior is what supports that kind of statement. His exponential example builds the 90% interval for lambda from chi-squared with 2n degrees of freedom, for a sample of n = 6.

Bias and MSE describe behaviour across many repeated samples, so for one real dataset the error of a single estimate cannot be calculated.

## Limits

- No simulation is run in the chapter, since the bias and MSE comparisons are set as exercises, so the figures are worked examples only.
- The posterior depends strongly on the assumed prior and its range (uniform 1 to 200 here).
- The confidence-interval formula is stated without derivation, and the chapter remarks that simulation is easier than analysis for intervals without demonstrating it.
- The extraction records printed inconsistencies: the unbiased constant is printed 2N/(N-1) where it should be 2N/(N+1), and the likelihood condition is written two ways (i at most N-hat in one place, "i < n" in another).
- Code is Python 2 era, built on the book's own Pmf class.

## See Also
- [[Maximum Likelihood and Estimator Bias]] — prerequisite-for
- [[Beta-Binomial Updating and Credible Intervals]] — related (credible intervals from a grid posterior)
- [[Bayes Action and Loss Functions]] — related (the loss decides the best point estimate)
