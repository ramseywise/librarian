---
title: External Validity and Transportability
tags: [foundations, concept]
summary: "Randomisation buys internal validity only: whether an effect carries to another population depends on how the sample was selected, and reweighting fixes selection on measured variables but never on an unmeasured one."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--07-data-generating-process.md
---

# External Validity and Transportability

**Internal validity**: the estimate is right for the people studied. **External validity**: it holds elsewhere. Randomisation delivers the first only.

## Three samples

The effect in a random sample was 0.158.

| Sample | Raw estimate | After reweighting |
|---|---|---|
| tenure-selected (tenure measured) | 0.117 | 0.169 |
| keenness-selected (keenness unmeasured) | 0.265 | 0.264 |

Reweighting on a measured selector recovers the population effect; an unmeasured selector cannot be fixed this way.

## Selection diagram

Draw what drives both selection into the sample and the effect size. If the selector also modifies the effect and is measured, you can transport; otherwise you cannot.

## See Also
- [[Data Defect Correlation]] — related
- [[Explain vs Predict Modelling]] — related
- [[Data Generating Process Simulation Check]] — related
