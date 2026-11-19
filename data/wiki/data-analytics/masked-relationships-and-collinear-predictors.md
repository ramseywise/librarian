---
title: Masked Relationships and Collinear Predictors
tags: [data-analytics, probability-and-statistics, concept]
summary: "In McElreath's multiple-regression chapter, two predictors can hide each other's association with the outcome, two near-duplicate predictors split one effect, and a post-treatment predictor erases a real one; each is shown on a simulation or the primate-milk data."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-statistical-rethinking-ch05-multivariate-linear-models.md
---

# Masked Relationships and Collinear Predictors

Chapter 5 of *Statistical Rethinking* (first edition; quadratic-approximation fits with `map`) shows what goes wrong when variables are added to a regression. The author frames the answer as descriptive, about the sample, not forecasting or intervention.

## Masking

Setup: primate milk data, 17 complete cases, energy in kcal per gram. Alone, neocortex percentage barely matters (moving from 55% to 76% shifts expected energy by about 0.09) and log body mass has a faint, uncertain negative slope (about -0.03, interval from -0.06 to 0.00). Putting both in one model (m5.7: neocortex slope 0.03, mass slope -0.10, sigma 0.11) multiplies the neocortex slope by more than six, with its 89% interval wholly positive, and the mass interval moves to roughly -0.13 to -0.06.

## Multicollinearity

Setup: a simulated sample of 100 heights with two almost identical leg-length predictors (leg proportion drawn from 0.4 to 0.5, error SD 0.02, N(2,10) priors). Neither coefficient is interpretable (-0.43 with SD 2.18, and 2.48 with SD 2.19), yet their sum is pinned down, and fitting one leg alone gives about 2.05 (SD 0.07), close to that sum. The milk data (all 29 rows) repeat the pattern: percent fat and percent lactose each predict strongly alone (slopes 0.010 and -0.011), but together the fat slope drops to 0.002 (SD 0.002) and the SDs roughly double. A flat-prior simulation (100 `lm` fits at each correlation level) shows a slope's posterior SD blowing up once the predictor correlation passes about 0.9, heading to infinity as it nears 1. Practice: inspect a pairs plot, treat correlations beyond roughly 0.9 as a warning, and note that any one member of a correlated cluster supports the same conclusion.

## Post-treatment bias

Setup: a simulated sample of 100 plants, fungus probability 0.5 - 0.4 x treatment, final height = initial height + Normal(5 - 3 x fungus, 1). Including fungus (m5.13) makes treatment look useless or harmful (slope -0.27, SD 0.22); dropping it (m5.14) recovers a clear positive effect (about 1.07, SD 0.31, 89% interval 0.57 to 1.57). Adjust for pre-treatment variables, not post-treatment ones, when the target is the treatment's causal effect ([[Post-Treatment Segments and Simpson's Paradox]], [[Confounders, Mediators and Colliders]]).

## Other results in the chapter

- Spurious association: once age at marriage enters the WaffleDivorce regression (50 states), the marriage-rate slope falls to near zero while age at marriage keeps a negative slope (89% interval -1.58 to -0.69).
- Contrasts: derive them from posterior samples and never compare the significance of two parameters. Hypothetical betas of 0.15 +/- 0.02 and 0.02 +/- 0.10 differ by 0.13 +/- 0.10 ([[Difference in Significance and Error Bar Overlap]]). Clade means of milk energy (kcal per gram) are 0.55 for apes, 0.71 for NWM, 0.79 for OWM and 0.51 for strepsirrhines; the NWM-minus-OWM contrast has median -0.074 and 95% interval -0.190 to 0.047.
- Statistical control is not causal control: after adjusting for marriage rate and age, Waffle House density still shows a slight positive correlation with divorce residuals.

## Limits

- Edition: the extraction places it in first-edition context; the chapter text prints no year, and the WaffleDivorce sample size is not printed.
- Causal inference depends on unverifiable assumptions; counterfactual plots can show impossible predictor combinations.
- The collinearity simulation uses flat priors, which exaggerate how fast the SD inflates.
- Fits use the quadratic approximation, not MCMC.

## See Also
- [[OLS Influence and Collinearity Diagnostics]] — related (diagnostics for the same problem)
- [[Confounders, Mediators and Colliders]] — prerequisite-for
- [[Explain vs Predict Modelling]] — related
