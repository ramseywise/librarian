---
title: Mix Effect vs Within-Segment Effect
tags: [foundations, pattern]
summary: Decompose a change in an overall rate by applying old segment rates to the new mix; the remainder is the within-segment change.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--05-visualisation-and-storytelling--notes--05-dashboards-and-storytelling.md
  - data/raw/repos/learn-ai-engineering/data-analytics--05-visualisation-and-storytelling--notes--02-matplotlib-and-seaborn.md
---

# Mix Effect vs Within-Segment Effect

An overall rate can fall because the composition of segments changed (mix), because rates fell inside segments (within), or both. Separating them tells you what to fix.

## Method

1. Compute each segment's rate in the old period and the new one, and the new period's segment weights (mix).
2. **Counterfactual:** apply the old segment rates to the new mix. Mix effect = counterfactual minus old overall rate.
3. **Within-segment effect** = actual new overall rate minus the counterfactual.
4. The two sum to the headline change (check this; rounding aside).

## Worked case (synthetic data)

Share of new customers buying again within 90 days: 37.5% overall in the old year, 26.2% in the new. Acquisition shifted towards a low-repeat channel. The counterfactual rate was 33.3%, so mix effect -4.3 points and within-segment effect -7.1 points, totalling the 11.3-point drop. Only the within part is plausibly about retention marketing. A per-channel table (rates fell 5.5 to 9.6 points in every channel) already shows the fall is not only a mix shift. The conversation moves from "the new channel brings bad customers" to "we also stopped talking to the customers we have".

## Cautions

- It decomposes a change; it does not prove cause. A before-and-after picks up anything else that changed that month; see [[Explanatory Data Story and the Big Idea]].
- The split depends on choosing the old rates as the reference; a different reference gives a different split.

## See Also
- [[Explanatory Data Story and the Big Idea]] — related
- [[Difference-in-Differences as Two-Way Fixed Effects]] — related
- [[Chart Declutter and Direct Labelling]] — related (small multiples by segment show the within-segment fall)
