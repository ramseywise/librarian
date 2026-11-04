---
title: Chart Declutter and Direct Labelling
tags: [foundations, pattern]
summary: Strip every element that adds reader effort without understanding, set the style once, label data directly, and make the title state the finding; small multiples need a shared scale and grey context.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--05-visualisation-and-storytelling--notes--02-matplotlib-and-seaborn.md
  - data/raw/repos/learn-ai-engineering/data-analytics--05-visualisation-and-storytelling--notes--05-dashboards-and-storytelling.md
---

# Chart Declutter and Direct Labelling

Each element on a chart costs the reader effort (cognitive load); elements that add effort without adding understanding are clutter. A default matplotlib chart illustrates it: a marker on every monthly point (the axis already says they are months), a grid and box as dark as the data, a legend sitting on the lines, a title that only describes the chart, and no visual weight on the one event that matters.

## The declutter sequence

Remove the border, drop or fade gridlines, remove data markers, clean up axis labels, label the data directly, use colour with intent. Apply it mechanically, then use preattentive attributes (weight, position) to direct attention to the two values you want remembered.

Do it once, not chart by chart: set `rcParams` in a shared module, where each line is one decision.
- Spines off except the baseline; grid kept only as a horizontal hairline behind the data.
- Left-aligned titles (where a reader starts); constrained layout so labels do not collide.
- A fixed colour per entity across every chart (see [[Chart Colour Scales and Accessibility]]).

## Direct labels and titles

- **Direct labels** at line ends save the reader shuttling to a legend. Colour the text in ink, not the series colour: yellow text on a pale background fails contrast. A small legend can remain as a second cue for readers who cannot separate hues.
- `annotate` with `textcoords="offset points"` pins a label a fixed distance from a data point so it survives resizing. Two line ends that land close together need a manual nudge; no library knows labels are about to collide.
- **Title = finding.** "Revenue by channel" repeats the axes; "Paid social overtook email in January 2025" says what the chart shows. For an explanatory chart keep one series, name the event, and bold the two values to remember.

## Small multiples

When groups overlap on one chart and the comparison is of shape over a shared scale, use one panel per group. Two tricks: `sharex=True, sharey=True` makes them comparable (it is what makes them one chart rather than four), and drawing every other series in pale grey behind the highlighted one keeps group context. Values sit on position, the top of the [[Visual Encoding Accuracy Ranking]], and it scales to a dozen panels where one chart with a dozen hues would be unreadable. Marking each panel's before/after average with a short horizontal line makes a level change visible through monthly noise.

## See Also
- [[Matplotlib Object Model and Seaborn Function Levels]] — prerequisite-for
- [[Visual Encoding Accuracy Ranking]] — related
- [[Explanatory Data Story and the Big Idea]] — extends
- [[Misleading Axes: Dual Axes and Truncated Bars]] — related
