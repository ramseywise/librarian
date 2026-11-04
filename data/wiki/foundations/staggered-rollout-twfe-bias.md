---
title: Staggered Rollout Bias in Two-Way Fixed Effects
tags: [foundations, pattern]
summary: "With staggered adoption and effects that grow, one TWFE coefficient can be badly wrong because already-treated units serve as controls; a clean comparison against never-treated units recovers the effect."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--02-probability-and-statistics--notes--08-panel-data-and-fixed-effects.md
---

# Staggered Rollout Bias in Two-Way Fixed Effects

When units adopt at different times, TWFE implicitly compares late adopters with early ones already treated. If effects are flat this is harmless; if they grow it is not.

| Scenario | TWFE | Truth |
|---|---|---|
| Flat effect | 4.486 | 4.500 |
| Growing effect, no untreated units | 0.096 | 4.531 |
| Growing effect, half never treated | 3.010 | 4.561 |
| Clean 2x2 vs never-treated | 4.572 | (recovers the effect) |

Do not rely on one pooled coefficient; compare with never-treated or not-yet-treated units.

## See Also
- [[Difference-in-Differences as Two-Way Fixed Effects]] — prerequisite-for
- [[Panel Data Fixed Effects]] — related
