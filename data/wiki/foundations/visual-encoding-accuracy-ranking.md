---
title: Visual Encoding Accuracy Ranking
tags: [foundations, concept]
summary: Readers judge some visual channels far more accurately than others, so put the comparison that matters on the most accurate channel and choose the chart from the question.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--05-visualisation-and-storytelling--notes--01-grammar-and-chart-choice.md
---

# Visual Encoding Accuracy Ranking

Perception experiments in which people judged the relative size of two values shown by different elementary encodings produced a ranking, from most to least accurate:

1. position on a common scale (dot plot, line, bar tip)
2. position on non-aligned scales (the same value across small multiples)
3. length, direction, angle (stacked segments, slopes, pie slices)
4. area (bubbles, treemaps)
5. volume, curvature (3D shapes)
6. shading, colour saturation (heatmaps, choropleths)

Crowdsourced replications of the spatial-encoding and luminance-contrast studies found the ordering is not an artefact of one laboratory. The design principle that follows: put the most important attribute on the most accurately perceived channel.

## Pies

A pie asks the reader to compare angles and areas, which sit below position. Sorted bars win when the question is comparing parts. A pie is still defensible for a few slices when the point is that parts make a whole or a simple fraction (a half, a quarter). The comparison the reader must make decides the form; "never use a pie" is a slogan, not a finding.

## Choose by the question

| The reader needs to see | Use | Avoid |
|---|---|---|
| Change over time | Line | Stacked area for individual series |
| Comparison across categories | Sorted bars or dots | Many-slice pie, unsorted bars |
| Parts of a whole, simple fractions | Single stacked bar, small pie | Many-slice or 3D pie |
| A distribution | Histogram, box plot, density | Mean-only bar |
| A relationship | Scatter | Two lines on two axes |
| Many groups | Small multiples | Spaghetti lines, more than eight hues |
| Two values in a grid | Heatmap, one-hue scale, values annotated | Rainbow scale |
| One number that matters | The number in large type | A chart of one point |

A small vocabulary used precisely beats a large one used loosely.

## Related reading costs

- Stacking to compare fails because only the bottom segment has a shared baseline; use stacks for totals, lines or panels for parts.
- Rotated tick labels slow reading: work cited in the source found 45-degree text read about 52% slower than horizontal and 90-degree text about 205% slower (the paper itself was not read). Swap to horizontal bars instead of rotating labels.
- Colour is near the bottom of the ranking, so spend it on identity, not quantity; see [[Chart Colour Scales and Accessibility]].

## See Also
- [[Grammar of Graphics]] — prerequisite-for
- [[Misleading Axes: Dual Axes and Truncated Bars]] — related
- [[Chart Colour Scales and Accessibility]] — related
