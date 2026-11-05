---
generated_by: tools/slides/flashcards.py
decks:
- data-analytics/01-python-for-data-analysis/slides/deck.yaml
cards:
- front: What happens when you add Series whose labels differ?
  back: Arithmetic between Series aligns on labels and gives NaN where a label exists on only one side.
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: Which checks do you run on every new frame?
  back: Run shape, dtypes, head and isna().sum() on every new frame, since most problems show up there first.
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: Why does chained assignment no longer change a frame in pandas 3, and what do you write instead?
  back: Under Copy-on-Write any selection acts as a copy, so change part of a frame with a single .loc call.
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: What are the steps from raw CSV to clean frame, and why put them in a function?
  back: Do every cleaning step in one function over an unchanged raw file, so the work can be rerun and audited.
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-and-cleaning
- front: How do you decide what to do with a missing value?
  back: Decide what to do with a missing value by asking why it is missing, because filling with the mean by reflex can invent data.
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-and-cleaning
- front: Why does filters.loc[0] raise a KeyError on the filtered frame?
  back: A filtered frame keeps its labels with gaps, so position 1 can be label 3 and label 0 may no longer exist.
  lesson: data-analytics/01-python-for-data-analysis/notes/03-indexing-and-selection
- front: How do loc and iloc differ on slices, and which one works with a boolean mask and a column name?
  back: loc slices include the end and accept masks and names, while iloc slices exclude the end and accept only integers.
  lesson: data-analytics/01-python-for-data-analysis/notes/03-indexing-and-selection
- front: What happens to a total when you merge on a key that repeats on both sides, and how do you catch it?
  back: A merge on a key that repeats on both sides multiplies rows and inflates totals without error, so state validate.
  lesson: data-analytics/01-python-for-data-analysis/notes/04-reshaping-and-joins
- front: What do you state and compare on every merge?
  back: On every merge state how and validate, then compare the row count and one total before and after.
  lesson: data-analytics/01-python-for-data-analysis/notes/04-reshaping-and-joins
- front: Which shape do groupby and seaborn want, and what do melt and pivot_table do?
  back: Tidy long data has one variable per column and one observation per row, which is what groupby and seaborn expect.
  lesson: data-analytics/01-python-for-data-analysis/notes/04-reshaping-and-joins
- front: What are the three stages of a groupby?
  back: A groupby splits rows by key, applies a function to each piece independently, and combines the results.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-groupby-and-aggregation
- front: How do agg, transform, filter and apply differ in what they return?
  back: agg returns one row per group, transform one value per original row, filter a subset of rows, and apply anything.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-groupby-and-aggregation
- front: How should you calculate a group's rate, and why is the mean of per-order rates wrong?
  back: To get a group's rate, sum the numerator and the denominator and then divide, because a mean of rates ignores size.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-groupby-and-aggregation
- front: Why should every group mean come with a count, and what happens to rows with a missing key?
  back: Report a count beside every group statistic, and check that groups add up, because missing keys vanish by default.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-groupby-and-aggregation
- front: What can a line chart show about a time series that describe() cannot?
  back: Time series have ordered rows, unequal months and silently absent days, so they need more care than an ordinary grouping key.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-time-series
- front: What did pandas 3 change about frequency aliases, and why?
  back: Pandas 3 removed the frequency aliases M, Q, Y, H and T, so write ME, QE, YE, h and min instead.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-time-series
- front: What do closed and label control in a resample, and why check count?
  back: Resample into bins with sum, mean and count together, since months differ in length and absent days hide in the sum.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-time-series
- front: What is leakage in a time series, and which two pandas options cause it?
  back: A negative shift and center=True both read the future, which is acceptable on a chart and cheating in a model.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-time-series
- front: How do rolling(7) and rolling("7D") differ, and where should you store timestamps?
  back: Compare seasonal data with a seasonal shift, use time-based windows on irregular data, and store timestamps in UTC.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-time-series
- front: Why should you try several bin counts on a histogram?
  back: A histogram's shape depends on its bin count, so try several before you trust what you see.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-plotting
- front: What are a Figure and an Axes, and why prefer the explicit interface to plt.plot?
  back: A Figure is the canvas and an Axes is one plot on it, so name them with plt.subplots rather than rely on a current Axes.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-plotting
- front: When do you reach for small multiples, and what kind of seaborn function draws them?
  back: Small multiples on a shared scale compare a pattern across groups, and seaborn's figure-level functions draw them from tidy data.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-plotting
- front: Which chart answers change over time, comparison, distribution and relationship?
  back: Choose a line for time, sorted bars for comparison, a histogram for shape, a box for groups and a scatter for relationships.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-plotting
- front: Name the checks you run when loading, joining, grouping and plotting.
  back: The dangerous errors in pandas raise no exception, so build the checks into every load, join, group and chart.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-plotting
- front: What can't this toolkit tell you yet?
  back: With data in a frame, the next question is whether a difference is real, which takes probability and statistics.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-plotting
---
