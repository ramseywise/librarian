---
title: Chart Colour Scales and Accessibility
tags: [foundations, pattern]
summary: Colour has three jobs (categorical, sequential, diverging) with one rule each; pin mappings by name, centre diverging scales on a real zero, and meet WCAG contrast, non-colour and table requirements.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--05-visualisation-and-storytelling--notes--01-grammar-and-chart-choice.md
  - data/raw/repos/learn-ai-engineering/data-analytics--05-visualisation-and-storytelling--notes--02-matplotlib-and-seaborn.md
  - data/raw/repos/learn-ai-engineering/data-analytics--05-visualisation-and-storytelling--notes--05-dashboards-and-storytelling.md
  - data/raw/repos/learn-ai-engineering/data-analytics--05-visualisation-and-storytelling--notes--06-dashboard-stacks-from-python-to-frontend.md
---

# Chart Colour Scales and Accessibility

Colour is near the bottom of the [[Visual Encoding Accuracy Ranking]], so spend it on identity, not quantity, unless a grid leaves nothing else.

## Three jobs, one rule each

- **Categorical** (which thing): a fixed order of distinct hues, a colour kept attached to its entity across every chart, and stop before a ninth. Qualitative scales work best with three to five categories. A different colour per bar in a single-series chart invents a category that does not exist.
- **Sequential** (how much): one hue from light to dark.
- **Diverging** (above or below a meaningful midpoint): two hues with neutral grey at the middle.

## Failure modes

- **Diverging scale not pinned to zero.** In seaborn's `heatmap`, `center=0` matters; without it the midpoint sits halfway between the extremes, so a small rise can be drawn in declining colours. Fix `vmin`/`vmax` symmetrically so colours do not change meaning between refreshes. Write cell values when the grid is small.
- **Numeric ids as categories.** Plotly treats numeric colour data as continuous, yielding a colour bar with values like 1.5 that are not groups. Colour by name.
- **Colours follow order of appearance.** With default palettes, filtering out one category repaints every other. Fix the mapping by name (`color_discrete_map`, or a lookup table in a front end).

## Accessibility checks (WCAG 2.2)

- **1.4.1** colour must not be the only means of conveying information; add shapes. About 8% of men and 0.5% of women have some colour-vision deficiency. Red/green alone is unreliable; add an arrow and sign.
- **1.4.3 / 1.4.11** text needs 4.5:1 contrast (3:1 if large); graphical marks need 3:1 against adjacent colours. Run a contrast calculation rather than judging by eye. In one validated palette, aqua (2.74:1) and yellow (2.11:1) fell short on a near-white surface; guidance accepts the information being available another way, such as a table, so those charts must also carry direct labels or a table.
- **1.1.1** where practical, provide the data in a table.
- **2.1.1 / 1.4.13** everything must work without a mouse; anything only on hover fails keyboard and touch users. A real `<select>` gets keyboard support free.

## See Also
- [[Chart Declutter and Direct Labelling]] — related
- [[Interactive Charts and When They Pay]] — related
- [[Dashboard Design: Paired Metrics and Context]] — related
