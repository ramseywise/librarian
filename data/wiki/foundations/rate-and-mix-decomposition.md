---
title: Rate and Mix Decomposition
tags: [foundations, pattern]
summary: Split a change in any aggregate into a rate (within-segment) effect and a mix effect by holding one fixed at a time; the split depends on order, so report it roughly, and it decomposes a change without proving cause.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--03-cohort-and-retention.md
  - data/raw/repos/learn-ai-engineering/data-analytics--05-visualisation-and-storytelling--notes--05-dashboards-and-storytelling.md
  - data/raw/repos/learn-ai-engineering/data-analytics--05-visualisation-and-storytelling--notes--02-matplotlib-and-seaborn.md
---

# Rate and Mix Decomposition

An aggregate (a blended repeat rate, average order value) moves for two different reasons that lead to opposite decisions: each segment behaves differently, or the share of each segment changed. A single percentage cannot tell them apart.

## Method

1. Compute the metric per segment (channel) and the segment mix in each period.
2. **Rate effect** = new rates applied to the old mix, minus the old total.
3. **Mix effect** = new total minus new rates on old mix.

Worked case: 90-day repeat rate fell 11.4 points (31.6% to 20.2%). Rate effect -6.2, mix effect -5.2. Both sides were right in almost equal parts.

## The other order, with a second case

Apply the old segment rates to the new mix instead. That **counterfactual** gives mix effect = counterfactual minus old overall rate, and within-segment effect = actual new overall rate minus the counterfactual. The two sum to the headline change (check this; rounding aside).

Synthetic case: share of new customers buying again within 90 days was 37.5% overall in the old year and 26.2% in the new, as acquisition shifted towards a low-repeat channel. The counterfactual rate was 33.3%, so mix effect -4.3 points and within-segment effect -7.1 points, totalling the 11.3-point drop. Only the within part is plausibly about retention marketing. A per-channel table (rates fell 5.5 to 9.6 points in every channel) already shows the fall is not only a mix shift. The conversation moves from "the new channel brings bad customers" to "we also stopped talking to the customers we have".

## It is not unique

Reversing the order (old rates on the new mix for the mix effect) gave -5.6 for mix and -5.8 for rates. The interaction term moves between the two. Report "about half and half", not to the decimal, and state the sensitivity to order. The split always depends on the chosen reference.

## It does not prove cause

The method decomposes a change. A before-and-after picks up anything else that changed that month; see [[Explanatory Data Story and the Big Idea]].

## Preconditions

Use a measure comparable across cohorts, and only customers whose full window has completed in both periods (see [[Cohort Retention Triangle]]).

## See Also
- [[Cohort Retention Triangle]] — related
- [[Funnel Step Diagnosis]] — related (Simpson-style mix shifts)
- [[Metric Tree Decomposition]] — related
- [[Explanatory Data Story and the Big Idea]] — related
- [[Difference-in-Differences as Two-Way Fixed Effects]] — related
- [[Chart Declutter and Direct Labelling]] — related (small multiples by segment show the within-segment fall)
