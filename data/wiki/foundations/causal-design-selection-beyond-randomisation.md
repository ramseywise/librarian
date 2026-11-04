---
title: Causal Design Selection Beyond Randomisation
tags: [foundations, comparison]
summary: "When you cannot randomise, choose a design by how assignment happened (rollout with a pre-period, threshold, randomised nudge, rich covariates, one treated unit), name its untestable assumption, and check difference-in-differences pre-trends, since diverging trends almost doubled an estimate."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--04-correlation-and-causation.md
---

# Causal Design Selection Beyond Randomisation

Every method without randomisation has an assumption the data cannot prove. Say what it is.

| Situation | First choice | Key assumption |
|---|---|---|
| You control assignment | A/B test ([[A/B Test Lifecycle and Interval Decisions]]) | randomisation |
| Rollout hit some units, pre-period data | difference-in-differences | parallel trends |
| Assignment by a threshold | [[Regression Discontinuity]] | no manipulation at cutoff |
| Randomised nudge, self-selected treatment | [[Instrumental Variables and LATE]] | exclusion restriction |
| Self-selected, rich covariates | [[Matching and Weighting Estimators]] plus [[Sensitivity Analysis for Unmeasured Confounding]] | no unmeasured confounders, overlap |
| One treated unit, many controls | [[Synthetic Control Method]] | pre-period fit carries forward |

## Difference-in-differences, worked

A launch in half of 400 stores at month 6 over 12 months. After-minus-before in treated stores (0.720) contains the growth trend; treated-minus-control after launch (1.480) contains the level gap; the double difference, the treated-by-post coefficient with errors clustered by store, was 0.426 (SE 0.028) against a true 0.400 ([[Difference-in-Differences as Two-Way Fixed Effects]], [[Clustered Standard Errors]]). By hand: treated 10 to 14, control 8 to 10 gives (14 - 10) - (10 - 8) = 2, assuming treated stores would otherwise have grown by the same 2.

Parallel trends cannot be tested directly, but pre-launch trends can. When treated trends drifted, the estimate rose to 0.762 and looked equally confident; the pre-trend slope gap was +0.091 (p = 0.000) against -0.010 (p = 0.415) when parallel. A pass is supportive only, since a short pre-period has little power: plot the two series first.

## Causal libraries

A causal library forces the order: state the graph, identify the estimand, estimate, refute. A random-common-cause refuter left an estimate of 0.311 at 0.310. A passed refuter checks the pipeline, not a confounder you never considered ([[Sensitivity Analysis for Unmeasured Confounding]]).

## See Also
- [[Backdoor and Front-Door Criteria]] — prerequisite-for
- [[Potential Outcomes and Selection Bias]] — prerequisite-for
- [[Staggered Rollout Bias in Two-Way Fixed Effects]] — related
- [[Panel Data Fixed Effects]] — related
- [[External Validity and Transportability]] — related
