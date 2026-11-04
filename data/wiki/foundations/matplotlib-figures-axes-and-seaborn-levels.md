---
title: Matplotlib Figures, Axes and Seaborn Levels
tags: [foundations, concept]
summary: Matplotlib's Figure and Axes objects underlie pandas and seaborn plotting; use the explicit interface, and know axes-level from figure-level seaborn functions and the tidy data they need.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--01-python-for-data-analysis--notes--07-plotting.md
---

# Matplotlib Figures, Axes and Seaborn Levels

## Figure and Axes

A **Figure** is the canvas you save; an **Axes** is one plot on it with its own coordinate system (one Axes has two axes, x and y). Pandas and seaborn both draw through matplotlib, so most plotting confusion is confusion about these two objects.

Two interfaces exist. The implicit `plt.plot(...)` draws on "the current Axes", which stops being obvious with two plots. Use the explicit one:

```python
fig, ax = plt.subplots()
fig, axes = plt.subplots(2, 3, sharey=True)   # axes is a NumPy array: axes[0, 1]
```

`sharey=True` puts every plot on one scale. Labelling calls are methods on `ax` (`ax.set(title=..., ylabel=..., ylim=(0, None))`, `ax.annotate`, `ax.legend`).

## Pandas shortcut

`Series.plot` / `DataFrame.plot` pick sensible defaults: index on x, each column a series, column names in the legend. Pass `ax=` to place the plot on your Axes; it returns the Axes. `.plot.bar`, `.plot.barh` cover bars.

## Seaborn

Seaborn works from a whole table: name the columns and the role each plays (x, y, hue, col) and it does grouping and statistics. That needs tidy data, one row per observation and one column per variable (see [[Tidy Data and Long-Wide Reshaping]]).

- **Axes-level** functions (`boxplot`, `scatterplot`, `regplot`, `heatmap`) draw on an Axes you pass.
- **Figure-level** functions (`catplot`, `relplot`, `displot`) build their own Figure to lay out facets. They take `col=` and `row=`, return a `FacetGrid`, and are sized by `height=` and `aspect=` instead of `figsize`.

## Old code and current libraries

- Since seaborn 0.12, columns pass by keyword (`x=`, `y=`); `sns.regplot("x", "y", data=df)` raises `TypeError`.
- `factorplot` became `catplot`, which draws a strip plot by default, so state `kind=`.
- `distplot` is replaced by `histplot(a, kde=True)`.
- A `MatplotlibDeprecationWarning` about `vert` from seaborn 0.13.2 on matplotlib 3.11 is harmless.

## Saving and showing

`fig.savefig(name, dpi=...)` picks the format from the extension: PNG for screens and notebooks, SVG or PDF for anything scaled or printed. Call `fig.tight_layout()` first to stop overlapping labels. In scripts `plt.show()` opens a window; `plt.close(fig)` in loops, since each figure holds memory until closed. In Jupyter, every drawing call for a figure must be in one cell.

## See Also
- [[Choosing a Chart from the Question]] — prerequisite-for
- [[Tidy Data and Long-Wide Reshaping]] — prerequisite-for
- [[Matplotlib Object Model and Seaborn Function Levels]] — related (overlaps; candidate merge for /compact-wiki)
