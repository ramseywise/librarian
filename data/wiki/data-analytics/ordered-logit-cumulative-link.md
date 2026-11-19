---
title: Ordered Logit and the Cumulative Link
tags: [data-analytics, probability-and-statistics, pattern]
summary: "An ordered categorical outcome gets K-1 cutpoints on the log-cumulative-odds scale, and a linear predictor phi is subtracted from every cutpoint so that a positive coefficient raises the expected response."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-statistical-rethinking-ch11-monsters-mixtures.md
---

# Ordered Logit and the Cumulative Link

McElreath (*Statistical Rethinking*, first edition, chapter 11) handles an ordered rating, such as a 1 to 7 response, by linking a linear model to cumulative probability. Cumulative probability counts a response together with every lower one, which preserves the ordering. Its log-odds gets one free intercept alpha_k per response level, a cumulative counterpart of the logit link ([[Maximum Entropy Likelihoods and Link Functions]]).

## Mechanism

- With K ordered levels, only K-1 intercepts are free (six for a seven-point scale).
- A predictor enters by being subtracted from every cutpoint, so a positive beta pushes the mean response up. In the chapter, lowering all fitted cutpoints by half a unit lifts the mean response from about 4.2 to about 4.7.
- Start the cutpoints in the right order; the order matters, the exact values do not (start values -2, -1, 0, 1, 2, 2.5 in the chapter).
- Show predictions as cumulative-probability curves per response level over a predictor range, averaging over posterior draws.

## Worked case

Setup: the Trolley data in the rethinking package (9930 responses from 331 people, rating moral permissibility 1 to 7), fitted by quadratic approximation (`map`) with Normal(0,10) priors. The intercept-only model m11.1 puts its first cutpoint near -1.92 (SD 0.03); inverse-logit of the cutpoints reproduces the observed cumulative proportions. Adding action, intention and contact (m11.2) makes every slope negative (about -0.7, -0.7 and -1.0). With interactions (m11.3) the contact-by-intention term is the biggest at about -1.3, while the main effects shrink to roughly -0.3 to -0.5. By WAIC, m11.3 (about 36,930) beats m11.2 (about 37,090) by roughly 161 with a standard error of the difference near 26, and both beat the intercept-only fit (about 37,855).

## Limits

- Edition: first edition, `map` and `ensemble` syntax; the authors of the trolley experiments are not named in the extraction.
- The Normal(0,10) priors are safe only because the data are large (9930 rows).
- The chapter advises passing a list of models to `ensemble` when WAIC is not decisive; the comparison here is by WAIC alone.

## See Also
- [[Generalised Linear Models and Deviance]] — prerequisite-for
- [[Logistic Regression Odds Ratios vs Marginal Effects]] — related
- [[WAIC, KL Divergence and Akaike Weights]] — related (the comparison used)
