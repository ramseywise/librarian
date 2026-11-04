---
title: Explanatory Data Story and the Big Idea
tags: [foundations, pattern]
summary: Fix audience, ask and one-sentence point of view before opening a slide tool, size the decision with named assumptions and a break-even, and test the story with horizontal logic.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--05-visualisation-and-storytelling--notes--05-dashboards-and-storytelling.md
---

# Explanatory Data Story and the Big Idea

Explanatory work tells a specific audience one thing; see [[Anscombe's Quartet: Plot Before Summarising]] for the exploratory counterpart. The first step touches no chart.

## Before the chart

- **Who** (a specific decision maker, not "stakeholders"), **what** they need to know or do, then **how** data supports it.
- **3-minute story:** could you make the point aloud if your slot shrank to three minutes?
- **Big Idea:** one complete sentence stating your point of view and what is at stake. If you cannot write it, you do not yet know what you are saying. Writing it forces you to know the numbers in it.

## Size it with assumptions named

When the sizing needs inputs you lack (a gross margin, revenue per retained customer), state them as assumptions standing in for finance's numbers, then compute the **break-even value of the shakiest one**. In the worked case, a budget cut saved 120,000 a year; the cut paid for itself only if gross margin were below 8.8%, so the conclusion survived any plausible margin. Reporting that a decision survives its assumptions persuades more than a single estimate. Say "about 550k", not "546,945": false precision claims more than assumptions allow.

## Causality and scope

A before-and-after with one change date also picks up anything else that changed. Do not present it as causal; name what else changed and propose a holdout (here, hold out 10% of customers). Say what the analysis does not show (the case did not test whether a separate spend increase earned its return). A recommendation is stronger for saying what it does not know. Separate a mix shift from within-segment change first: [[Mix Effect vs Within-Segment Effect]].

## Chart and story shape

- Explanatory chart: one series, finding as title, event annotated, direct labels ([[Chart Declutter and Direct Labelling]]). Bars are honest for a decision chart when items share a unit and a zero; colour can carry the argument (grey saving, blue costs).
- Three acts with the audience as protagonist: setup (what they know), conflict (what is unresolved and why it matters), resolution (what they can do).
- **Horizontal logic:** reading only the slide titles in order tells the whole story. **Vertical logic:** everything on a slide supports its title. Also ask someone unfamiliar what they take from it.
- State the ask on the first slide, not after twelve charts.
- Truthfulness test: would the chart still support the sentence if someone else chose the axis, window and comparison? Storytelling is persuasion, and cropping or highlighting can mislead.

## See Also
- [[Dashboard Design: Paired Metrics and Context]] — related
- [[Mix Effect vs Within-Segment Effect]] — prerequisite-for
- [[Misleading Axes: Dual Axes and Truncated Bars]] — related
- [[Difference-in-Differences as Two-Way Fixed Effects]] — related (stronger designs than before/after)
