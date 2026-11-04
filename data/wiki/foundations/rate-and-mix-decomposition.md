---
title: Rate and Mix Decomposition
tags: [foundations, pattern]
summary: Split a change in any aggregate into a rate effect (every segment changed) and a mix effect (the segment shares changed) by applying new rates to the old mix; the split depends on order, so report it roughly.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--03-cohort-and-retention.md
---

# Rate and Mix Decomposition

An aggregate (a blended repeat rate, average order value) moves for two different reasons that lead to opposite decisions: each segment behaves differently, or the share of each segment changed. A single percentage cannot tell them apart.

## Method

1. Compute the metric per segment (channel) and the segment mix in each period.
2. **Rate effect** = new rates applied to the old mix, minus the old total.
3. **Mix effect** = new total minus new rates on old mix.

Worked case: 90-day repeat rate fell 11.4 points (31.6% to 20.2%). Rate effect -6.2, mix effect -5.2. Both sides were right in almost equal parts.

## It is not unique

Reversing the order (old rates on the new mix for the mix effect) gave -5.6 for mix and -5.8 for rates. The interaction term moves between the two. Report "about half and half", not to the decimal, and state the sensitivity to order.

## Preconditions

Use a measure comparable across cohorts, and only customers whose full window has completed in both periods (see [[Cohort Retention Triangle]]).

## See Also
- [[Cohort Retention Triangle]] — related
- [[Funnel Step Diagnosis]] — related (Simpson-style mix shifts)
- [[Metric Tree Decomposition]] — related
- [[Mix Effect vs Within-Segment Effect]] — related (overlaps; candidate merge for /compact-wiki)
