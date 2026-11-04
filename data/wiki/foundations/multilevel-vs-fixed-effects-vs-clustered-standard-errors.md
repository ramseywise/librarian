---
title: Multilevel vs Fixed Effects vs Clustered Standard Errors
tags: [foundations, comparison]
summary: "Pick by question: clustered SEs when groups are a nuisance, fixed effects (or a within-between model) when the group effect may correlate with the predictor, multilevel when group-level estimates are the question; plain random intercepts can be biased where the others are not."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--04-bayesian-analysis--notes--07-multilevel-models-and-partial-pooling.md
---

# Multilevel vs Fixed Effects vs Clustered Standard Errors

| Question | Use | Why | Watch for |
|---|---|---|---|
| Population-average effect, groups a nuisance | Clustered SEs ([[Clustered Standard Errors]]) | coefficients unchanged, honest SEs, few assumptions | too few clusters |
| Effect within groups; group effect may correlate with the predictor | Fixed effects ([[Panel Data Fixed Effects]]) or a within-between random-effects model | compares each group only with itself | cannot estimate anything constant within a group; still needs clustered SEs |
| Group-level estimates or the spread between groups | Multilevel model ([[Partial Pooling and Multilevel Models]]) | stabilised estimate per group and an estimate of tau | needs exchangeable groups and enough of them |

## Four estimators, 400 datasets

Predictor: a discount with a true within-group effect of 2.

| Estimator | Mean estimate (uncorrelated) | Mean estimate (group effect correlated with predictor) |
|---|---|---|
| Pooled OLS, clustered SE | 2.004 | 3.042 |
| Fixed effects, clustered SE | 1.988 | 1.988 |
| Random intercepts | 2.001 | 2.826 |
| Within-between random intercepts | 1.988 | 1.988 |

Uncorrelated: all centred on 2; random intercepts most precise (actual sd 0.213 against 0.266 for fixed effects). Correlated: pooled OLS and plain random intercepts are wrong, and neither their standard errors nor more data would warn you. In 7 of 400 random-intercept runs the SE came back missing with no error, so check it in any loop. The 0.266 comes from 400 datasets; 10,000 gave 0.297 against a theoretical 0.299, so the apparent gap between 0.31 and 0.27 is not evidence of oversized SEs.

## Within-between model

Standard random effects assume the within and between effects are equal and otherwise return a weighted average that is hard to interpret. Split the predictor into its group mean and the deviation from it: the within coefficient then equals the fixed-effects estimate (1.988 above), while the model can still estimate group-level variables, which fixed effects cannot.

## Prefer the simpler tool when groups are a nuisance

A multilevel model counted 10 assumptions against 3 for clustered SEs; if random intercepts are only there to absorb clustering, clustered SEs or generalised estimating equations do it more simply. Multilevel is warranted when the specific clusters, or their variability, matter. Fixed effects do not fully remove within-cluster correlation, so cluster anyway; there is no clear definition of "few" clusters, from under 20 to under 50 when balanced and more when not.

## Logit coefficients differ by model

A multilevel logit coefficient is cluster-specific (a change within a group); a pooled logit with clustered SEs is population-averaged. The base rate has the same split: a typical group 4.89% against 6.71% averaged over the population, because high-rate groups pull up the mean on the probability scale. Fitted: pooled 0.183 (SE 0.036), multilevel 0.164 (sd 0.045). With true parameters: effect varying by group, within 0.150 against population-averaged 0.154; effect fixed at 0.15, 0.150 against 0.145; common outcome (intercept -1, sd 2, effect 0.5), 0.500 against 0.306. So population-averaged smaller describes a fixed effect, not every model. Name the scale and convert to probabilities.

## Pitfalls

- Plain random intercepts when the group effect correlates with the predictor: 2.83 against a true 2.
- Random intercepts when slopes vary: SE about 20% too small.
- A multilevel model fitted only to handle clustering.

## See Also
- [[Clustered Standard Errors]] — alternative-to
- [[Panel Data Fixed Effects]] — alternative-to
- [[Partial Pooling and Multilevel Models]] — alternative-to
- [[Pseudoreplication and Intraclass Correlation]] — related
