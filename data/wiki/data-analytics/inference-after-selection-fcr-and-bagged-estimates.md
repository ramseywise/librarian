---
title: "Selection-Aware Inference: FCR, Scheffe Intervals and Bagged Estimates"
tags: [data-analytics, probability-and-statistics, concept]
summary: "When the model or the reported cases are chosen from the same data, ordinary intervals are too short: simultaneous and false-coverage-rate intervals widen them, bootstrapping the whole select-then-fit algorithm gives honest standard errors, and bagging smooths a jumpy selector."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch20-inference-after-model-selection.md
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch16-sparse-modeling-lasso.md
---

# Selection-Aware Inference: FCR, Scheffe Intervals and Bagged Estimates

Efron and Hastie (Computer Age Statistical Inference, ch. 20) ask how to judge an estimate or interval when the same data also chose the model or the target. They offer vignettes, not a theory: data-based selection inflates apparent accuracy unless the inference accounts for it.

## Simultaneous and false-coverage-rate intervals

- **Scheffe:** simultaneous 95% intervals over a whole catalog of parameters of possible interest. Setup: diabetes data with 442 patients and 10 predictors (q = 432, sigma estimate 54.2). The Scheffe multiplier is 4.30 where a plain t would use 1.97, making the intervals 2.19 times wider. Restricting the catalog to pairwise differences (Tukey, p = 2, ..., 6 groups, n = 20) gives narrower half-widths, 2.95 to 4.44 against 3.74 to 5.58 in units of sigma-hat over sqrt(n).
- **False-coverage rate (FCR):** the expected proportion of non-covering intervals among the R selected ones. The BYq rule gives each of the R selected cases an interval whose level is adjusted for the selection. Setup: simulation, N = 10,000 with 9000 nulls and 1000 effects from N(-3, 1), q = 0.05: 565 cases declared non-null, 17 intervals not covering, FCR 17/565 = 0.030. The authors advise against putting the usual 1.96 intervals on cases chosen by an FDR rule.
- BYq intervals keep the average coverage but can mislead for single cases: among the non-nulls the Bayes 95% interval is half as wide, with slope 1/2 where BYq has slope 1. The authors call this accurate-but-not-correct and give no formal definition of the second word.

## Bootstrapping the whole algorithm

Setup: cholesterol data, n = 164 pairs, fitted curve at c = -2, Cp (minimised at the cubic) choosing a polynomial degree. Treating the cubic as fixed gives a bootstrap standard error of 3.97, but letting Cp choose the degree gives 5.98, over 50% more. Averaged across c from -2.2 to 2 the adaptive errors are 43% larger, so naive 95% intervals would be about 43% too narrow. Cp chose the linear model in 19% of 4000 nonparametric bootstrap samples, and in those resamples the estimate at c = -2 dropped by roughly 10 units. The authors advise bootstrapping the whole select-then-fit procedure.

## Bagging and the infinitesimal jackknife

Bagging (bootstrap smoothing) averages an estimator over bootstrap replications, giving the mean of B replicate estimates, which smooths out a discontinuous rule. Its standard error comes from the infinitesimal jackknife using the stored resample counts N_bj, so no second bootstrap is needed. On the cholesterol curve bagging trimmed standard errors for the Cp/OLS fit by roughly 12% (ratio of IJ bagged SE to bootstrap SE averaging 0.88). The external standard deviation of the selection proportion 0.19 is 0.24 from the infinitesimal jackknife, against a binomial internal SE of 0.006; the authors advise reporting the external figure.

## Frequentist checks on Bayes estimates

Setup: diabetes, n = 442, Bayesian lasso prior with lambda = 0.37, MCMC B = 10,000. For patient 322 the delta-method frequentist SE of the posterior mean is 0.186 against a posterior SE of 0.203 (about 5% smaller on average over the 442 patients). The posterior cdf at c = 2.5 is 0.687 (frequentist SE 0.325). Its 90% credible interval runs from 2.08 to 2.73, and each endpoint carries an SE near 0.185, about 28% of the interval's length. The lasso chapter (ch. 16) gives a post-selection example: in an HIV resistance regression (30 binary predictors, lasso tuned by 10-fold CV to lambda 0.003) 7 sites are selected and after selection-adjusted inference only one remains significant; the authors advise selection-adjusted rather than naive intervals after lasso selection.

## Limits

- By the authors' account no general theory of post-selection inference exists, and they cannot say how far the bootstrap-smoothed Cp/OLS estimates are from optimal.
- The posterior cdf's standard errors are big, and a delta-method cdf can leave the unit interval; Efron (2015) has better intervals.
- Simulations are single designs (N = 10,000 for BYq) with no seeds given.
- The lasso post-selection material is a brief survey; the HIV example is shown only as a figure.

## See Also
- [[Multiple Comparisons Corrections]] — prerequisite-for
- [[BCa Bootstrap Confidence Intervals]] — prerequisite-for
- [[Winner's Curse]] — prerequisite-for
- [[False-Discovery Rate, the Two-Groups Model and Local fdr]] — prerequisite-for (BYq builds on the Benjamini-Hochberg rule)
- [[Empirical Bayes: Tweedie's Formula and g-Modeling]] — alternative-to (corrects selection bias with shrinkage instead of wider intervals)
