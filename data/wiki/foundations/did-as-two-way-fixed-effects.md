---
title: Difference-in-Differences as Two-Way Fixed Effects
tags: [foundations, pattern]
summary: "A difference-in-differences estimate equals the treated-by-post coefficient in a two-way fixed effects regression, and rests on untestable parallel trends that pre-period event-study checks detect poorly."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--08-panel-data-and-fixed-effects.md
---

# Difference-in-Differences as Two-Way Fixed Effects

Compare the change over time in treated units with the change in controls. The hand calculation equals the TWFE coefficient (3.494, SE 0.168, true 3.596). The raw post-period gap (10.012) mixes the effect with pre-existing difference.

## Parallel trends

Without treatment, treated and control would have moved together. This is untestable after the fact. An **event study** (binned, week -1 as reference) plots pre-period coefficients near zero as reassurance, which is weak evidence.

## Power of the pre-test

With a differential trend (tilt 0.15) TWFE gave 7.394 against 3.596, yet only 1 of 7 pre-period coefficients was flagged. False alarms with no tilt: 24%; tilt 0.05 (bias 1.29): 36%; tilt 0.15: 99%.

## See Also
- [[Panel Data Fixed Effects]] — prerequisite-for
- [[Staggered Rollout Bias in Two-Way Fixed Effects]] — extends
- [[Clustered Standard Errors]] — related
- [[Causal Design Selection Beyond Randomisation]] — related (worked pre-trend example and alternatives)
