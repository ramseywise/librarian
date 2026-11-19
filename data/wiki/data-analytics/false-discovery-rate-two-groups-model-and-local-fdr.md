---
title: False-Discovery Rate, the Two-Groups Model and Local fdr
tags: [data-analytics, probability-and-statistics, concept]
summary: "Benjamini-Hochberg control of the false-discovery rate has an empirical Bayes reading in the two-groups model, where the local fdr gives each case's probability of being null and an empirical null replaces N(0,1) when the z-histogram centre is too wide."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch15-large-scale-hypothesis-testing-false-dis.md
---

# False-Discovery Rate, the Two-Groups Model and Local fdr

Efron and Hastie (Computer Age Statistical Inference, ch. 15) ask how to choose which of thousands of simultaneous nulls to reject, and how false-discovery-rate theory answers differently from control of the family-wise error rate.

## From FWER to FDR

The family-wise error rate (FWER) is the probability of even one false rejection; Bonferroni and Holm control it. The false-discovery proportion is false rejections over total rejections (unobservable, defined 0 when nothing is rejected) and the false-discovery rate (FDR) is its expectation. The Benjamini-Hochberg rule Dq rejects the cases up to the largest i whose ordered p-value satisfies p(i) <= (i/N) q; when the null p-values are independent its FDR is pi0 times q, at most q. A case's q-value is N p_i / i, the q that puts it exactly on the boundary.

Setup: right-tail prostate z-values, 6033 genes, with alpha and q both 0.1. Dq rejects the 28 smallest p-values where Holm rejects 7; at alpha = 0.05 the one-sided Bonferroni threshold leaves four genes (the extraction cannot confirm the sign of the cutoff, z = 4.31). With N in the thousands and mostly null cases, the authors advise controlling FDR at q = 0.1 instead of FWER.

## Two-groups model and local fdr

Every case is a null (prior probability pi0, density f0) or a non-null (pi1 = 1 - pi0, density f1), so the z-values have the mixture density f = pi0 f0 + pi1 f1. Two quantities follow:

- the Bayes false-discovery rate Fdr(z0) is the probability a case is null given z >= z0, pi0 S0(z0)/S(z0);
- the local false-discovery rate fdr(z0) is the probability a case is null given z = z0, pi0 f0(z0)/f(z0); the true-discovery rate is 1 minus it;
- the 50th largest prostate z (2.99, p = 0.00139) has q-value 0.168, simultaneously the frequentist boundary for rejecting it and the empirical Bayes probability that it is null.

A cutoff of fdr <= 0.2 corresponds to Fdr <= 0.1 and to a Bayes factor f1/f0 of at least 4 pi0/pi1 (at least 36 once pi0 >= 0.90). Setup: prostate data with f fitted by a degree-4 log-polynomial Poisson regression (deviance 137.0 at degree 3, 65.1 at degree 4, then under 2 more per added degree) and the theoretical N(0,1) null; cutting at local fdr 0.2 flags 27 genes in the right tail and 25 in the left.

## Empirical and permutation nulls

When the centre of the z-histogram is wider than N(0,1), the authors fit a normal empirical null N(delta0, sigma0^2) to the central part of the histogram by maximum likelihood (the locfdr approach). Setup: police-stop data on 2749 officers, z-values from logistic regression, fitted empirical null with mean 0.10 and sd 1.40. The theoretical null gives fdr <= 0.2 for 216 officers (125 on the right, 91 on the left), whereas the empirical null leaves only four. Setup: DTI study comparing 6 dyslexic and 6 control children over N = 15,443 voxels. The empirical null (sigma0 = 1.06, pi0 = 0.984) yields 149 voxels at fdr <= 0.20 (z >= 3.17) and the theoretical null 177 (z >= 3.07); keeping only the 4,653 voxels with x from 50 to 70 leaves 66 (z >= 3.57). Across 250 simulated locfdr trials (5000 cases each, true null N(0,1), pi0 = 0.95, non-nulls N(3,1)), the estimates averaged .015 for the null mean, 1.017 for the null sd and .962 for pi0.

A permutation null (z-values recomputed after shuffling group labels) corrects only asymptotic inaccuracy, not correlation, unobserved covariates or effect-size problems. The authors advise settling which cases are relevant comparators before pooling, and estimating the root-mean-square correlation of the z-values to see whether correlation threatens the analysis (0.015 plus or minus 0.001 for the prostate cancer patients).

## Limits

- The Benjamini-Hochberg theorem assumes independent null p-values; with correlation the fdr estimate stays nearly unbiased while its variance increases.
- Estimating the null makes fdr-hat more variable, so the authors keep the theoretical null where it looks right, as for the prostate data.
- Theory for the relevance question ("which others?") barely exists, by the authors' account, and they call their survey more illustrative than definitive.
- Minus signs are dropped in the extraction's text layer, so negative values (left cutoff, DTI delta0, the locfdr zero set) are unconfirmed.

## See Also
- [[Multiple Comparisons Corrections]] — prerequisite-for
- [[Winner's Curse]] — related (selecting the extreme cases among thousands)
- [[Empirical Bayes: Tweedie's Formula and g-Modeling]] — extends
- [[Selection-Aware Inference: FCR, Scheffe Intervals and Bagged Estimates]] — extends
