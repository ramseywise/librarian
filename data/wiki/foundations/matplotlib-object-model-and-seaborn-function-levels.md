---
title: Matplotlib Object Model and Seaborn Function Levels
tags: [foundations, reference]
summary: Matplotlib is a tree of Figure, Axes and artists with two APIs (use the object-oriented one), and pandas and seaborn draw through it; seaborn splits into figure-level and axes-level functions; plus pandas shortcuts, library-version changes, format and pitfall notes.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--05-visualisation-and-storytelling--notes--02-matplotlib-and-seaborn.md
  - data/raw/repos/learn-ai-engineering/data-analytics--01-python-for-data-analysis--notes--07-plotting.md
---

# Matplotlib Object Model and Seaborn Function Levels

Almost every static Python chart is drawn by matplotlib, even when the code says seaborn or pandas, so most plotting confusion is confusion about Figure and Axes.

## Object model

A `Figure` is the canvas and owns saving. It holds one or more `Axes`, each one plot with its own coordinate system (not the x and y axes). An `Axes` holds artists: `Line2D`, `Text`, `Rectangle`, and the XAxis/YAxis objects. Everything you see is an artist and can be reached and changed.

Two APIs: the `pyplot` state machine (`plt.plot`, acts on "the current axes") and the object-oriented API (`ax.plot`, acts on the axes you name). Use `fig, ax = plt.subplots()` from the first line; "current" stops being safe with two panels, and helper functions want an `ax` argument anyway.

```python
fig, ax = plt.subplots()
fig, axes = plt.subplots(2, 3, sharey=True)   # axes is a NumPy array: axes[0, 1]
```

`sharey=True` puts every plot on one scale. Labelling calls are methods on `ax` (`ax.set(title=..., ylabel=..., ylim=(0, None))`, `ax.annotate`, `ax.legend`).

## Pandas shortcut

`Series.plot` / `DataFrame.plot` pick sensible defaults: index on x, each column a series, column names in the legend. Pass `ax=` to place the plot on your Axes; it returns the Axes. `.plot.bar`, `.plot.barh` cover bars.

## Seaborn

A layer over matplotlib that takes tidy data, one row per observation and one column per variable (see [[Tidy Data and Long-Wide Reshaping]]), and thinks in the grammar ([[Grammar of Graphics]]): name columns and the role each plays (x, y, hue, col) and it does grouping, statistics and the legend.
- **Figure-level** (`relplot`, `displot`, `catplot`) create their own figure, return a `FacetGrid`, support `col=`/`row=`, and are sized by `height=` and `aspect=` instead of `figsize`.
- **Axes-level** (`scatterplot`, `boxplot`, `regplot`, `heatmap`) draw into an `ax` you pass, so they compose. If `ax=` raises an error, you called a figure-level function.
- Pass `order=` and `hue_order=`: by default seaborn follows data order, so a filter or refresh can reorder or recolour the chart.
- Seaborn draws through matplotlib, so shared rcParams still apply ([[Chart Declutter and Direct Labelling]]).

For skewed values a box plot on a log scale shows distribution by group in one view; mean above median in every group is the signature of right skew, and a bar of means would hide it (see [[Robust Summaries for Skewed Metrics]]).

## Old code and current libraries

- Since seaborn 0.12, columns pass by keyword (`x=`, `y=`); `sns.regplot("x", "y", data=df)` raises `TypeError`.
- `factorplot` became `catplot`, which draws a strip plot by default, so state `kind=`.
- `distplot` is replaced by `histplot(a, kde=True)`.
- A `MatplotlibDeprecationWarning` about `vert` from seaborn 0.13.2 on matplotlib 3.11 is harmless.

## File formats

Sizes for one simple line chart: PNG 50 KB, SVG 24 KB, PDF 8 KB. PNG has fixed pixels (slides, documents; size depends on resolution). SVG and PDF are vector and stay sharp but grow with mark count; a 100,000-point scatter is many megabytes of SVG and a modest PNG. Use PDF for print, SVG for the web unless there are many marks. Set `figsize` for final display size and `dpi` for density; scaling a small PNG up in a slide makes it blurry.

`fig.savefig(name, dpi=...)` picks the format from the extension. Call `fig.tight_layout()` first to stop overlapping labels. In scripts `plt.show()` opens a window. In Jupyter, every drawing call for a figure must be in one cell.

## Pitfalls

- Mixing `plt.` and `ax.`: works until a second panel appears.
- Not calling `plt.close(fig)` in a loop: every open figure holds memory and matplotlib warns after 20.
- Passing `ax=` to a figure-level seaborn function.
- Colour that follows rank rather than a fixed per-entity mapping.

## See Also
- [[Chart Declutter and Direct Labelling]] — extends
- [[Chart Colour Scales and Accessibility]] — related
- [[Interactive Charts and When They Pay]] — alternative-to (interactive rather than static)
- [[Choosing a Chart from the Question]] — prerequisite-for
- [[Tidy Data and Long-Wide Reshaping]] — prerequisite-for
