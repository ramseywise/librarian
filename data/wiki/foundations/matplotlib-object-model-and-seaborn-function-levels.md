---
title: Matplotlib Object Model and Seaborn Function Levels
tags: [foundations, reference]
summary: Matplotlib is a tree of Figure, Axes and artists with two APIs (use the object-oriented one); seaborn splits into figure-level and axes-level functions; plus format and pitfall notes.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--05-visualisation-and-storytelling--notes--02-matplotlib-and-seaborn.md
---

# Matplotlib Object Model and Seaborn Function Levels

Almost every static Python chart is drawn by matplotlib, even when the code says seaborn or pandas.

## Object model

A `Figure` is the canvas and owns saving. It holds one or more `Axes`, each one plot with its own coordinate system (not the x and y axes). An `Axes` holds artists: `Line2D`, `Text`, `Rectangle`, and the XAxis/YAxis objects. Everything you see is an artist and can be reached and changed.

Two APIs: the `pyplot` state machine (`plt.plot`, acts on "the current axes") and the object-oriented API (`ax.plot`, acts on the axes you name). Use `fig, ax = plt.subplots()` from the first line; "current" stops being safe with two panels, and helper functions want an `ax` argument anyway.

## Seaborn

A layer over matplotlib that takes tidy data and thinks in the grammar ([[Grammar of Graphics]]): name columns and it does grouping, statistics and the legend.
- **Figure-level** (`relplot`, `displot`, `catplot`) create their own figure, return a `FacetGrid`, and support `col=`/`row=`.
- **Axes-level** (`scatterplot`, `boxplot`, `heatmap`) draw into an `ax` you pass, so they compose. If `ax=` raises an error, you called a figure-level function.
- Pass `order=` and `hue_order=`: by default seaborn follows data order, so a filter or refresh can reorder or recolour the chart.
- Seaborn draws through matplotlib, so shared rcParams still apply ([[Chart Declutter and Direct Labelling]]).

For skewed values a box plot on a log scale shows distribution by group in one view; mean above median in every group is the signature of right skew, and a bar of means would hide it (see [[Robust Summaries for Skewed Metrics]]).

## File formats

Sizes for one simple line chart: PNG 50 KB, SVG 24 KB, PDF 8 KB. PNG has fixed pixels (slides, documents; size depends on resolution). SVG and PDF are vector and stay sharp but grow with mark count; a 100,000-point scatter is many megabytes of SVG and a modest PNG. Use PDF for print, SVG for the web unless there are many marks. Set `figsize` for final display size and `dpi` for density; scaling a small PNG up in a slide makes it blurry.

## Pitfalls

- Mixing `plt.` and `ax.`: works until a second panel appears.
- Not calling `plt.close(fig)` in a loop: every open figure holds memory and matplotlib warns after 20.
- Passing `ax=` to a figure-level seaborn function.
- Colour that follows rank rather than a fixed per-entity mapping.

## See Also
- [[Chart Declutter and Direct Labelling]] — extends
- [[Chart Colour Scales and Accessibility]] — related
- [[Interactive Charts and When They Pay]] — alternative-to (interactive rather than static)
- [[Matplotlib Figures, Axes and Seaborn Levels]] — related (overlaps; candidate merge for /compact-wiki)
