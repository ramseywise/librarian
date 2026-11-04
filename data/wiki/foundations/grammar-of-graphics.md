---
title: Grammar of Graphics
tags: [foundations, concept]
summary: A chart is a composition of independent decisions (data, mark, encoding, statistic, scale, coordinates, facet), so chart choice becomes "which encoding makes my comparison easiest to read".
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--05-visualisation-and-storytelling--notes--01-grammar-and-chart-choice.md
  - data/raw/repos/learn-ai-engineering/data-analytics--05-visualisation-and-storytelling--notes--04-javascript-d3-vega-lite-observable-plot.md
---

# Grammar of Graphics

Thinking in chart types (line, stacked area, pie) limits you to a menu. The grammar of graphics replaces the menu with a set of independent parts, the way a sentence is composed of parts of speech. A layered form of it underlies ggplot2, Vega-Lite (the same idea as JSON, with interaction added) and Altair (a Python API that emits Vega-Lite). seaborn and plotly express follow it in spirit: you name columns and the library does the rest.

## The parts

| Part | Question it answers |
|---|---|
| Data | Which rows, at what grain? |
| Mark (geom) | What shape stands for a row: line, area, bar, point? |
| Encoding (aesthetic) | Which column drives which visual channel (x, y, colour)? |
| Statistic | Is anything computed first, such as a sum per month? |
| Scale | How do values map to pixels and colours (zero-based linear, fixed colour mapping)? |
| Coordinates | Which space: Cartesian, or polar (which gives a pie)? |
| Facet | Is the chart repeated per group? |

## Why it helps

Each decision can change while the others stay put. With one Altair specification, swapping the mark from line to area, or adding a facet, redraws the same data and encodings as a different chart, and each answers a different question:

- **Lines** compare series month by month and show crossings.
- **Stacked areas** show the total, but every series except the bottom one sits on a moving baseline, so the middle series are hard to read.
- **Small multiples** show each series' own shape at the cost of cross-series comparison.

So "what chart should this be?" translates to "which encoding makes the comparison I care about easiest to read?" That question has an evidence-based answer: see [[Visual Encoding Accuracy Ranking]]. A stack's bottom series is a statement of priority, so put the series that matters most there.

## Where the grammar stops

A declarative grammar describes data, not pixels. In Vega-Lite, placing an annotation at a pixel offset is a hack that breaks on resize, and bespoke transitions or new chart forms need a lower-level tool; see [[JavaScript Charting Ladder]].

## See Also
- [[Visual Encoding Accuracy Ranking]] — extends
- [[JavaScript Charting Ladder]] — extends
- [[Chart Declutter and Direct Labelling]] — related
- [[Misleading Axes: Dual Axes and Truncated Bars]] — related
