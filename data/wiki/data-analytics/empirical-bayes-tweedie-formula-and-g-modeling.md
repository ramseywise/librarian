---
title: "Empirical Bayes: Tweedie's Formula and g-Modeling"
tags: [data-analytics, bayesian-analysis, concept]
summary: "With many parallel observations the prior can be learned from the data: Tweedie's formula corrects selection bias from the marginal density alone (f-modeling), while g-modeling fits the prior itself as an exponential family on a grid and gets standard errors by delta method or parametric bootstrap."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch20-inference-after-model-selection.md
  - data/raw/papers/2026-11-08-computer-age-statistical-inference-ch21-empirical-bayes-estimation-strategies.md
---

# Empirical Bayes: Tweedie's Formula and g-Modeling

Efron and Hastie (Computer Age Statistical Inference, ch. 20 and 21) describe two ways to use many parallel observations z_i, each normal around its own effect mu_i, to estimate effects without a stated prior. Modeling on the x scale (f-modeling) fits the marginal density of the observations; modeling on the theta scale (g-modeling) fits the prior g(theta) itself, a problem they call Bayes deconvolution.

## Tweedie's formula (f-modeling)

Tweedie gives the posterior mean as z plus sigma^2 times the slope of the log marginal density at z, so estimating the density of the observed z values is enough. It corrects the winner's curse, the tendency of unusually good comparative performances not to repeat. Under a normal prior the formula reduces to (almost) James-Stein, a straight line through the origin; on the prostate data that slope would be 0.22.

Setup: prostate data, N = 6033 genes, f fitted by a degree-4 log-polynomial, sigma = 1. Gene 610 is shrunk from z = 5.29 to 4.03. At z = 3.5 the posterior mean is 1.96 and fdr is 0.15; roughly 85% of genes near that value are non-null, with a mean effect near 2.31. Setup for the simulation: 100 datasets of N = 1000 from an exponential-normal mixture, natural spline with 5 degrees of freedom, top 20 z-values per dataset (2000 differences). The uncorrected differences sat about one unit right of zero; the corrected ones centred at zero with no added variance.

## g-modeling

The prior is an exponential family on a discrete grid, with Q a polynomial or natural spline basis (a spike-and-slab Q uses a point mass at 0 plus a spline). It is fitted by maximum likelihood on the observed marginal with a small penalty c0 times the norm of alpha (c0 = 1), which avoids corner local maxima; the authors report the penalty's effect never exceeded a few percent. Accuracy comes from the delta method or the parametric bootstrap (resample counts from the fitted marginal, restart the optimiser at the fit).

Setup: prostate study, 102 men, z_i around mu_i with sigma0 = 1.06, grid -3.6 to 3.6 in steps of 0.2, Q a point mass at 0 plus a 5-df spline. The null probability is 0.946, against 0.984 from the locfdr f-modeling fit, and Pr{|mu| >= 2} is 0.020 with standard error 0.0014, about 121 genes. Setup: artificial microarray, N = 10,000, 9000 nulls and 1000 effects from N(-3, 1): the null probability is recovered as 0.891 (true 0.9) with standard error 0.006. Extending g-modeling to generalised linear mixed models, on a nodes study (binomial counts, covariates age, sex, smoke and prog), the covariate prog dominates (z magnitude 9.07), sex has z = 2.74, and age and smoke are not significant.

## f-modeling versus g-modeling

Setup: a made-up prior (an eighth uniform on [-3, 3], the rest normal with sd 0.5), 1000 cases, x normal around theta. The Fourier (sinc kernel) nonparametric deconvolution estimate was far noisier, with a standard deviation over 20 times larger than g-modeling's at comparable bias; a parametric first stage (Poisson regression on a 5-df spline) cut it substantially but did not reach g-modeling. Delta-method standard errors ran about a quarter too small here (against a bootstrap with B = 500), while on the nodes example (B = 1000) delta and bootstrap agreed closely. For E{theta | x} the coefficient of variation is about 0.05 at large |x|, and at x = 2.5 the empirical Bayes information is 0.10 per other observation, against Fisher information 1 for direct estimation. The authors advise f-modeling when the target is expressible through f (Robbins, fdr, Tweedie) and g-modeling when the prior itself is wanted, and to treat the assumed prior as a substantial assumption.

## Limits

- Parametric g-modeling has a definitional bias when the true g is outside the chosen exponential family.
- The fitted slab density is rough, and the non-null density estimates for the prostate data are imprecise.
- The posterior mean of theta is the easy target; other conditional summaries, for example the posterior second moment, are estimated worse.
- Nonparametric deconvolution is reported to converge at a logarithmic rate in N, and the Fourier method needs x to be theta plus iid noise.
- The treatment assumes finite discrete theta and x spaces and a kernel that is the same for every case; each simulation is a single design, with no seeds reported.

## See Also
- [[Small-N Trap and Shrinkage]] — prerequisite-for
- [[Partial Pooling and Multilevel Models]] — related (shrinkage toward a learned prior)
- [[Winner's Curse]] — prerequisite-for
- [[False-Discovery Rate, the Two-Groups Model and Local fdr]] — prerequisite-for (fdr is the empirical Bayes quantity Tweedie reuses)
