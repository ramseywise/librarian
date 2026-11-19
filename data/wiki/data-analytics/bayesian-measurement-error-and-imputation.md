---
title: Bayesian Measurement Error and Imputation
tags: [data-analytics, bayesian-analysis, pattern]
summary: "McElreath gives each uncertain or missing value its own parameter inside the model, with the observed value or the other predictors as the prior, instead of averaging the data or dropping incomplete cases."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-statistical-rethinking-ch14-missing-data-other-opportunities.md
---

# Bayesian Measurement Error and Imputation

Chapter 14 of *Statistical Rethinking* (first edition) writes what is believed about error and missing values into the generative model itself, so ordinary conditional probability propagates the uncertainty into the estimates. The lesson is to model the data's distribution rather than to average or patch the data.

## Measurement error with a known standard error

Swap each observed value for a parameter standing for the unknown true value, and give the observation a Normal(true value, SE) likelihood. The Gaussian is chosen because only the spread is known; the chapter frames it as the least-assuming (maximum-entropy) option, not a belief that errors are Gaussian. A predictor can be treated the same way, with one latent parameter per true value.

Setup: WaffleDivorce (50 US states), divorce rate regressed on age at marriage (median) together with marriage rate, each state's SE being known; fitted with `map2stan` (5000 iterations, 1000 warmup, adapt_delta 0.95). Allowing for error in the outcome about halves the age-at-marriage slope compared with ignoring it, though it stays clearly negative. Adding error on the marriage-rate predictor (3 chains) barely moves either slope, but marriage-rate estimates for small, high-rate states are pulled in. Ignoring error usually inflates associations, yet it can hide one, depending on which cases carry how much error.

## Imputation under MCAR

Setup: primate milk data (29 species), energy per gram regressed on neocortex proportion and log body mass, with 12 neocortex values absent; `map2stan`, 10,000 iterations, 2 chains. Dropping incomplete rows leaves 17 species and throws away 12 that have valid mass and energy. Giving each missing neocortex value a parameter under the prior N ~ Normal(nu, sigma_N) (m14.3) shrinks the neocortex coefficient to 1.93, down from 2.77 in the complete-case fit, and the log-mass coefficient goes to -0.07 from -0.10. The refined m14.4 lets nu depend on log mass (gM about 0.02), which restores the neocortex coefficient to 2.44 and tightens imputed values: their posterior SD falls from about 0.05 to about 0.03 to 0.04. The chapter's advice: let the imputation model exploit relations among the predictors, modelling all variables jointly.

Data missing not at random gets only a sketch: model the process that produces the gaps and infer from it; no worked model is given. Two practical tips: raise adapt_delta to 0.95 to clear divergent transitions, and switch off the default WAIC when the likelihood contains latent estimates, since the default code does not integrate them out.

## Limits

- Edition: first edition (`map2stan`, Stan syntax with `<-` assignment); the second edition replaces these with `ulam`.
- Missingness is handled only as MCAR. The imputation model uses a Gaussian for neocortex proportion even though it is bounded between 0 and 1; the chapter leaves that fix to its practice problems.
- Age at marriage is taken as exact; the author cautions that the information in it may be illusory.
- The Gaussian-error assumption gets no sensitivity check beyond a suggestion to try other assumptions.

## See Also
- [[Pandas Missing Data Decisions]] — alternative-to (dropping, filling or flagging, outside a model)
- [[Prior Choice and Prior Predictive Checks]] — related
- [[Partial Pooling and Multilevel Models]] — related
