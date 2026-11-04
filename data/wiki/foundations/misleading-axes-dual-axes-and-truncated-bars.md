---
title: "Misleading Axes: Dual Axes and Truncated Bars"
tags: [foundations, pattern]
summary: Two y scales let the author author the story, and a bar from a non-zero baseline exaggerates differences; use aligned panels, an index, and zero-based bars.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--05-visualisation-and-storytelling--notes--01-grammar-and-chart-choice.md
  - data/raw/repos/learn-ai-engineering/data-analytics--05-visualisation-and-storytelling--notes--02-matplotlib-and-seaborn.md
---

# Misleading Axes: Dual Axes and Truncated Bars

Two ways an honest dataset gets misrepresented.

## Dual y axes

Nothing in the data decides where two independent scales sit relative to each other, so any crossing point or apparent gap is invented by whoever set the limits. Plotting identical revenue and repeat-rate series with two different pairs of axis limits produced one chart where nothing much happens and another showing a collapse crossing a surge.

Fixes:
- **Aligned panels** sharing one time axis, one per measure, with the event marked in both. Relationships in time stay visible and nobody can argue about scale placement.
- **Index both series to 100** at a chosen base so they share one scale with one meaning (percent of base). The base still matters: indexing to a seasonal peak month distorts, so a whole-year average is a fairer base. Absolute levels are lost.

## Truncated bars

A bar's length is its message, so bars (and areas) start at zero on a linear scale. The size of a shaded area must be proportional to the value it represents (the principle of proportional ink). In one example, a quarter 11% above another was drawn 86% taller when the axis began partway up the scale. A line or dot encodes value by position alone, so a line chart can zoom in without breaking the rule, provided the axis says so plainly.

On a log scale a bar has no honest starting point (its baseline would be 1, not 0), so use a box or a dot there.

When a small difference matters, plot the difference itself, or use dots.

## Checklist

- Never give two measures separate y axes.
- Bars and areas from zero; lines and dots may zoom if labelled.
- Draw the honest size of a fall from zero when that is the point, even if month-to-month noise looks smaller.

## See Also
- [[Visual Encoding Accuracy Ranking]] — prerequisite-for
- [[Anscombe's Quartet: Plot Before Summarising]] — related
- [[Chart Declutter and Direct Labelling]] — related
