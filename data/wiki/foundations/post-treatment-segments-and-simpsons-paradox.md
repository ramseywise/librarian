---
title: Post-Treatment Segments and Simpson's Paradox
tags: [foundations, concept]
summary: "A trend can reverse inside every subgroup of aggregated data; which table to trust depends on the causal story, so segment on traits fixed before treatment, never on something the treatment changes, and in experiments keep the allocation constant across periods."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--02-metrics-and-kpi-design.md
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--04-correlation-and-causation.md
---

# Post-Treatment Segments and Simpson's Paradox

Simpson's paradox: a trend in aggregated data reverses within every subgroup. Arithmetic cannot say which table to trust; only the causal story can.

## Confounded subgroup: stratify

In a synthetic trial, treatment recovered 97.5% vs 90.0% of mild cases and 50.0% vs 30.0% of severe cases, yet overall 59.5% vs 60.0% (119/200 vs 120/200), because treatment went mostly to severe cases (160 of 200). Severity affects both who was treated and who recovered, so it is a confounder: stratify ([[Confounders, Mediators and Colliders]]). A real admissions case is the classic: women were admitted less often overall, but department by department showed little sign of bias, because women applied more to harder departments.

## Allocation shifts inside a test

If a ramp ran A heavy on a strong day and B heavy on a weak one, B won on both days (0.110 vs 0.10 Monday, 0.055 vs 0.05 Saturday) and lost pooled (0.0688 vs 0.0875). A constant split prevents this because each day then contributes equally to both arms; if the split changed, stratify by period and report a weighted average.

## Post-treatment segment: pool instead

If the subgroup is something the treatment changed, the pooled table is the right one. Example: a change moved people out of a "reached deep page" segment. Both segments improved (conversion 0.24 vs 0.20 deep, 0.0274 vs 0.02 shallow) while the total was flat at 0.0380 in both arms, because users moved between segments. A segment is safe only if fixed before assignment (device, country). Check by running the sample-ratio test within each segment: here the deep group's 4,000 vs 2,000 fails immediately ([[Sample Ratio Mismatch]]). Also "buyers spent less" may mean the treatment created new, smaller buyers: use unconditional rates.

## See Also
- [[Confounders, Mediators and Colliders]] — extends
- [[OEC, Guardrails and North Star Metrics]] — related
- [[Multiple Comparisons Corrections]] — related (segment scans need correction)
