---
title: Choosing a Chart from the Question
tags: [foundations, reference]
summary: "Pick the chart from the question being asked, and keep marks honest: bars start at zero, one y axis, several bin counts, uncertainty bands read as uncertainty, and titles that state the finding."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--01-python-for-data-analysis--notes--07-plotting.md
---

# Choosing a Chart from the Question

Plot early: a chart is the fastest way to find what is wrong with data and what is interesting in it. A year of daily values that tells nothing as a table shows the trend, weekly ripple, outage and a December jump in one line chart.

## Question to chart

| Question | Chart |
|---|---|
| Change over time | line |
| Compare categories | sorted bars, starting at zero |
| Shape of one column | histogram |
| Distributions across groups | box or violin |
| Two numbers related | scatter |
| All numeric columns | pair plot or correlation heatmap |
| Same pattern across groups | small multiples |
| Value over two categories | heatmap of a pivot table |

## Rules that keep a chart honest

- **Lines** say the points are connected and order means something; true of a time series, false of categories. Sort the x axis first or the line scribbles. Matplotlib breaks a line at `NaN`, so an outage shows when the series is regularised (see [[Time-Series Resampling, Bins and Gaps]]), but a one-day gap is too small to spot, so still count gaps.
- **Bars** encode value by length, so they must start at zero; sort them unless categories have a natural order; use horizontal bars for long labels. A line may omit zero when change is the subject: a 30-day mean that rose from 391 to 814 (ratio 2.08) looks far larger on a 350 to 850 axis, so the reader should be able to see the axis.
- **Pie charts**: in perception experiments people judged position and length more accurately than angle, so sorted bars nearly always do better.
- **Dual y axes** imply a relationship set by whichever scales were chosen; draw two panels.
- **Histograms**: bin count is a real choice. On 363 daily values, 5 bins gave a staircase, 150 looked like static, 25 showed a long right tail. The mean (507) above the median (477) is the same skew in numbers.
- **Box plots** show median, middle half, whiskers and outliers; they compare spread as well as centre where a bar of means hides it.
- **Scatter**: lower the opacity or use `hexbin` or a 2D histogram when dots pile up. A correlation of 0.933 in a case where one column was built from the other says only that they move together; it does not show cause. The `regplot` band is uncertainty about the line, not the spread of the points.
- **Small multiples** on a shared y axis show at a glance that a weekly shape repeats each quarter while the level rises; without `sharey=True` panels can differ tenfold in scale.
- **Titles** state what to see ("Revenue rises and jumps in December"), not the column name.

## See Also
- [[Matplotlib Object Model and Seaborn Function Levels]] — extends
- [[Tidy Data and Long-Wide Reshaping]] — prerequisite-for
- [[Robust Summaries for Skewed Metrics]] — related
