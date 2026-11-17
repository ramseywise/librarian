---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- data-analytics/01-python-for-data-analysis/slides/deck.yaml
cards:
- front: What happens when you add Series whose labels differ?
  back: Pandas aligns on labels, not positions. The result has the union of the labels, and any label present on only one side gives NaN instead of a guess.
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: Which checks do you run on every new frame?
  back: Run shape, dtypes, head and isna().sum(). Together they show the size, the types, real values and the gaps per column, which is where most problems appear first.
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: Why does chained assignment no longer change a frame in pandas 3, and what do you write instead?
  back: Under Copy-on-Write any selection behaves like a copy, so assigning onto it changes a temporary that is thrown away. Write one call instead, such as fixed.loc[mask, "qty"] = 0.
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: What are the steps from raw CSV to clean frame, and why put them in a function?
  back: Read the raw text, parse with options, fix text and types, drop rows with reasons, then assert. One function over an unchanged raw file can be rerun and audited, for example on next month's export.
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-and-cleaning
- front: How do you decide what to do with a missing value?
  back: Ask why it is missing. Not recorded gets labelled unknown, a lost value is confirmed with the owner, and a return is removed and reported. Filling with the mean by reflex can invent data.
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-and-cleaning
- front: How do loc and iloc differ on slices, and which one works with a boolean mask and a column name?
  back: loc slices include the end, so df.loc[0:2] gives three rows, while iloc slices exclude it and give two. loc accepts masks and column names; iloc takes integers only.
  lesson: data-analytics/01-python-for-data-analysis/notes/03-indexing-and-selection
- front: Why does filters.loc[0] raise a KeyError on the filtered frame?
  back: A filtered frame keeps its original labels, and label 0 was a kettle that the filter removed. loc looks up labels, so label 0 no longer exists, while iloc counts positions from zero.
  lesson: data-analytics/01-python-for-data-analysis/notes/03-indexing-and-selection
- front: What happens to a total when you merge on a key that repeats on both sides, and how do you catch it?
  back: 'Rows multiply and the total inflates without any error: here rows went from 11 to 16 and revenue from 523.5 to 756.0. Passing validate="many_to_one" raises a MergeError instead.'
  lesson: data-analytics/01-python-for-data-analysis/notes/04-reshaping-and-joins
- front: What do you state and compare on every merge?
  back: State how and validate, then compare the row count and one total before and after. In the shop that means 11 rows and revenue 523.5 both before and after.
  lesson: data-analytics/01-python-for-data-analysis/notes/04-reshaping-and-joins
- front: Which shape do groupby and seaborn want, and what do melt and pivot_table do?
  back: They want long (tidy) data, with one row per observation. melt turns wide data into long, and pivot_table turns long into wide, where you state aggfunc.
  lesson: data-analytics/01-python-for-data-analysis/notes/04-reshaping-and-joins
- front: What are the three stages of a groupby?
  back: Split the rows by key, apply a function to each piece on its own, and combine the results into one object.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-groupby-and-aggregation
- front: How do agg, transform, filter and apply differ in what they return?
  back: agg returns one row per group, transform one value per original row, filter a subset of rows kept or dropped by group, and apply anything rebuilt from each piece (slowest).
  lesson: data-analytics/01-python-for-data-analysis/notes/05-groupby-and-aggregation
- front: How should you calculate a group's rate, and why is the mean of per-order rates wrong?
  back: Sum the numerator and the denominator per group, then divide. A mean of per-order rates weights small and large orders equally, so east shows 0.492 against its true 0.398.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-groupby-and-aggregation
- front: Why should every group mean come with a count, and what happens to rows with a missing key?
  back: A mean of one order prints as confidently as a mean of ten thousand, so the count shows how much it rests on. Rows with a missing key vanish from a groupby unless you pass dropna=False.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-groupby-and-aggregation
- front: What can a line chart show about a time series that describe() cannot?
  back: 'The ordering in time: trend, weekly pattern, outages and the December jump. Rows have an order and absent days are invisible in a table, so the line makes gaps and changes visible.'
  lesson: data-analytics/01-python-for-data-analysis/notes/06-time-series
- front: What did pandas 3 change about frequency aliases, and why?
  back: 'It removed the old aliases M, Q, Y, H and T, so write ME, QE, YE, h and min. The reason is ambiguity: ME says month end, as distinct from MS for month start.'
  lesson: data-analytics/01-python-for-data-analysis/notes/06-time-series
- front: What do closed and label control in a resample, and why check count?
  back: closed sets which edge of a bin belongs to it and label sets which edge names the bin. count shows how many observations each bin has, exposing that March lost two days.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-time-series
- front: What is leakage in a time series, and which two pandas options cause it?
  back: Leakage is a feature reading the future, which cannot exist in production. A negative shift such as shift(-1) and center=True in a rolling window both cause it.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-time-series
- front: How do rolling(7) and rolling("7D") differ, and where should you store timestamps?
  back: rolling(7) counts rows and rolling("7D") counts calendar days, so they differ when rows are absent. Store timestamps in UTC and convert for display.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-time-series
- front: Why should you try several bin counts on a histogram?
  back: 'The shape depends on the bin count: 5 bins give a staircase, 150 give static, and 25 show a main body with a long right tail. Try several before trusting what you see.'
  lesson: data-analytics/01-python-for-data-analysis/notes/07-plotting
- front: What are a Figure and an Axes, and why prefer the explicit interface to plt.plot?
  back: A Figure is the canvas you save and an Axes is one plot on it. plt.plot draws on whichever Axes is current, which stops being obvious with two plots, so name them with plt.subplots.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-plotting
- front: When do you reach for small multiples, and what kind of seaborn function draws them?
  back: Use them to compare a pattern across groups on one shared scale, when a single plot has turned into spaghetti. Seaborn's figure-level functions such as catplot with col= draw them from tidy data.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-plotting
- front: Which chart answers change over time, comparison, distribution and relationship?
  back: A line for change over time, sorted bars from zero for comparison, a histogram for the shape of one column (a box for groups), and a scatter for the relationship of two numbers.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-plotting
- front: Name five chart mistakes that misstate the data, and the fix for each.
  back: Unsorted dates on a line (sort_index first), a line across categories (use bars), bars not starting at zero (start at zero), panels on different scales (sharey=True), and thousands of opaque dots (lower alpha or use hexbin).
  lesson: data-analytics/01-python-for-data-analysis/notes/07-plotting
- front: Name the checks you run when loading, joining, grouping and plotting.
  back: 'Loading: keep the raw file and use one rerunnable function. Joining: state how and validate, then compare rows and one total. Grouping: print counts, sum then divide for ratios, check groups add up. Plotting: question first, bars from zero, one y axis.'
  lesson: data-analytics/01-python-for-data-analysis/notes/07-plotting
- front: What can't this toolkit tell you yet?
  back: Whether a difference in the data is real or just luck. That takes probability and statistics, which is the next pillar.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-plotting
- front: What is the difference between a Series and a DataFrame?
  back: A Series is one labelled column of one dtype. A DataFrame is a set of Series sharing an index, one per column, so dtypes can differ across columns.
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: What is the index for?
  back: 'Labels for lookup and, more importantly, for alignment: operations between objects match on label, not on position.'
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: What happens when you add two Series with different labels?
  back: The result has the union of the labels. A label on only one side gives `NaN`, unless you use `add(..., fill_value=0)`.
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: Why did my integer column become float?
  back: '`NaN` is a float, so a missing value promotes the column to `float64`.'
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: How do you see what a new frame contains?
  back: '`shape`, `head`, `dtypes`, `info`, `describe`, and `value_counts` on categorical columns.'
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: What is the default string dtype in pandas 3?
  back: The `str` dtype replaced `object` for inferred text. It holds only strings and missing values, with `NaN` as the marker.
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: What is Copy-on-Write and what did it change?
  back: Every indexing result and method result behaves as a copy, so one statement cannot update two objects. Chained assignment stops working, and `SettingWithCopyWarning` is gone.
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: How do you update part of a frame safely?
  back: 'One `.loc` call with both the row selection and the column: `df.loc[mask, "col"] = value`.'
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: Why prefer vectorised operations over loops?
  back: They state intent, and the loop runs in compiled code, so they are much faster.
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: A column of numbers loaded as text. What do you do?
  back: Find the bad values with `to_numeric(errors="coerce")` and `isna`, decide what they mean, then add them to `na_values` or fix them.
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-and-cleaning
- front: How do you handle missing data?
  back: Ask why it is missing first. Structural gaps can be removed. A gap in an observation needs keeping, filling with a reasoned value, or a stated exclusion. If missingness relates to the value, dropping biases results.
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-and-cleaning
- front: What is the difference between `map` and `replace`?
  back: '`map` applies a mapping to every value and gives `NaN` for anything unmapped. `replace` changes only listed values.'
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-and-cleaning
- front: How do you find duplicates?
  back: '`duplicated` on the column that should be unique, with `keep=False` to see all copies, then decide before calling `drop_duplicates`.'
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-and-cleaning
- front: When would you choose `cut` or `qcut`?
  back: '`cut` for meaningful fixed thresholds, `qcut` for equal-sized groups.'
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-and-cleaning
- front: CSV or Parquet?
  back: CSV for interchange. Parquet keeps types and compresses better at scale, so it suits work between pipeline steps.
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-and-cleaning
- front: Why not pickle?
  back: It suits only short-term storage. Later library versions may not be able to read it, and it can run code when loaded, so never unpickle untrusted files.
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-and-cleaning
- front: How do you stop bad data reaching a report?
  back: A rerunnable loader with assertions on keys, ranges and allowed values, printing row counts at each stage.
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-and-cleaning
- front: '`loc` or `iloc`?'
  back: '`loc` selects by label, `iloc` by integer position.'
  lesson: data-analytics/01-python-for-data-analysis/notes/03-indexing-and-selection
- front: Does a slice include its end?
  back: '`.iloc` excludes it like Python, `.loc` includes it, as labels have no natural next value.'
  lesson: data-analytics/01-python-for-data-analysis/notes/03-indexing-and-selection
- front: Why do `df.loc[0]` and `df.iloc[0]` disagree?
  back: After a filter or sort, labels no longer equal positions. Use `reset_index(drop=True)` if you need them aligned.
  lesson: data-analytics/01-python-for-data-analysis/notes/03-indexing-and-selection
- front: How do you combine conditions?
  back: '`&`, `|` and `~` with each condition in parentheses; `and` and `or` raise a `ValueError` on a Series.'
  lesson: data-analytics/01-python-for-data-analysis/notes/03-indexing-and-selection
- front: How do you set a value on filtered rows?
  back: 'One call: `df.loc[mask, "col"] = value`. Chained forms write to a temporary under Copy-on-Write.'
  lesson: data-analytics/01-python-for-data-analysis/notes/03-indexing-and-selection
- front: What does `(s > 0).mean()` give?
  back: The share of values above 0, as `True` counts as 1.
  lesson: data-analytics/01-python-for-data-analysis/notes/03-indexing-and-selection
- front: What is the difference between axis 0 and axis 1?
  back: Axis 0 runs down the rows, axis 1 across the columns. `sum(axis=0)` collapses rows and gives one value per column.
  lesson: data-analytics/01-python-for-data-analysis/notes/03-indexing-and-selection
- front: What is a MultiIndex for?
  back: Several levels of labels, usually out of a multi-key groupby. Select by tuple, by outer level, or with `xs`, or flatten with `reset_index`.
  lesson: data-analytics/01-python-for-data-analysis/notes/03-indexing-and-selection
- front: What does `reindex` do?
  back: Conforms an object to a given list of labels, adding `NaN` or a fill value for new ones and dropping others.
  lesson: data-analytics/01-python-for-data-analysis/notes/03-indexing-and-selection
- front: Explain inner, left, right and outer joins.
  back: Which side's unmatched rows survive. Inner keeps matches only, left keeps all left rows with `NaN` for missing right values, right the reverse, outer keeps everything.
  lesson: data-analytics/01-python-for-data-analysis/notes/04-reshaping-and-joins
- front: What happens when a key repeats on both sides?
  back: You get the Cartesian product of the matching rows. Row count and totals inflate with no error.
  lesson: data-analytics/01-python-for-data-analysis/notes/04-reshaping-and-joins
- front: How do you verify a join?
  back: '`validate=`, row counts before and after, a total before and after, and `indicator=True` to inspect the unmatched.'
  lesson: data-analytics/01-python-for-data-analysis/notes/04-reshaping-and-joins
- front: What is tidy data?
  back: Each variable a column, each observation a row, each observational unit a table (Wickham 2014).
  lesson: data-analytics/01-python-for-data-analysis/notes/04-reshaping-and-joins
- front: What is the difference between `merge` and `concat`?
  back: '`merge` matches rows on keys and adds columns. `concat` glues frames along an axis, aligning on labels.'
  lesson: data-analytics/01-python-for-data-analysis/notes/04-reshaping-and-joins
- front: '`pivot` or `pivot_table`?'
  back: '`pivot` only rearranges and fails on duplicate combinations. `pivot_table` aggregates duplicates using `aggfunc`.'
  lesson: data-analytics/01-python-for-data-analysis/notes/04-reshaping-and-joins
- front: When is wide better than long?
  back: Reading by humans, and matrix computation on a crossed design. Long is better for groupby, plotting and modelling.
  lesson: data-analytics/01-python-for-data-analysis/notes/04-reshaping-and-joins
- front: What replaced `df.append`?
  back: '`pd.concat`, called once on a list of frames.'
  lesson: data-analytics/01-python-for-data-analysis/notes/04-reshaping-and-joins
- front: What is split-apply-combine?
  back: Break data into groups, operate on each independently, reassemble (Wickham 2011). It is `GROUP BY` and pivot tables as one idea.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-groupby-and-aggregation
- front: '`size` or `count`?'
  back: '`size` counts rows, `count` counts non-missing values per column.'
  lesson: data-analytics/01-python-for-data-analysis/notes/05-groupby-and-aggregation
- front: What is the difference between `agg`, `transform`, `filter` and `apply`?
  back: One row per group, same rows as the input, a subset of input rows, and anything.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-groupby-and-aggregation
- front: How do you compute a group's rate?
  back: Ratio of sums. The mean of per-row rates weights every row the same, whatever its size.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-groupby-and-aggregation
- front: How would you get each row's share of its group?
  back: '`x / x.groupby(key).transform("sum")`.'
  lesson: data-analytics/01-python-for-data-analysis/notes/05-groupby-and-aggregation
- front: What happens to `NaN` group keys?
  back: They are dropped by default. Use `dropna=False`, and check that groups add up to the total.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-groupby-and-aggregation
- front: How do you get the top N per group?
  back: '`sort_values` then `groupby(...).head(n)`, or `apply` with `nlargest`.'
  lesson: data-analytics/01-python-for-data-analysis/notes/05-groupby-and-aggregation
- front: '`pivot_table` or `crosstab`?'
  back: '`pivot_table` aggregates any value and defaults to the mean. `crosstab` counts by default and can `normalize` into shares.'
  lesson: data-analytics/01-python-for-data-analysis/notes/05-groupby-and-aggregation
- front: How does this map to SQL?
  back: Keys are `GROUP BY`, aggregations are `SUM`, `COUNT`, a filter on groups is `HAVING`, and `transform` is a window function with `OVER (PARTITION BY ...)`.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-groupby-and-aggregation
- front: Timestamp or period?
  back: A timestamp is a moment, a period is a span. Use periods when the row stands for a whole month or quarter.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-time-series
- front: What does `resample` do?
  back: Time-based groupby. Downsampling aggregates into bins with `closed` and `label` choices; upsampling makes empty rows that you must fill on purpose.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-time-series
- front: Why did `freq="M"` start failing?
  back: Pandas 3.0 removed it for the explicit `ME` and `MS`. Similarly `QE`, `YE`, `h`, `min`.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-time-series
- front: How do you do a seasonal comparison?
  back: '`shift` by the season length, such as 7 for daily data with a weekly cycle, and compare like with like.'
  lesson: data-analytics/01-python-for-data-analysis/notes/06-time-series
- front: What is the difference between `rolling(7)` and `rolling("7D")`?
  back: Seven rows against seven calendar days. They differ when rows are missing or irregular.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-time-series
- front: What is leakage, and how can a time series leak?
  back: 'Using information not known at prediction time: negative shifts, centred windows, or filling backward.'
  lesson: data-analytics/01-python-for-data-analysis/notes/06-time-series
- front: How do you handle time zones?
  back: Store in UTC, convert for display, pick the reporting zone before daily aggregation. Local days can be 23 or 25 hours long.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-time-series
- front: How do you find missing days?
  back: '`asfreq("D")` then `isna().sum()`, or compare `count` per month with the calendar.'
  lesson: data-analytics/01-python-for-data-analysis/notes/06-time-series
- front: What does `ewm` do differently from a rolling mean?
  back: It weights recent values more, decaying exponentially, so it responds faster and has no hard window edge.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-time-series
- front: What is the difference between a Figure and an Axes?
  back: The Figure is the canvas you save, and an Axes is one plot on it with its own coordinates. A Figure holds one or more Axes.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-plotting
- front: Why prefer `fig, ax = plt.subplots()` to `plt.plot`?
  back: The explicit interface says which Axes you mean, while `plt.` draws on an implicit "current" one, which gets confusing with several plots.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-plotting
- front: Axes-level or figure-level seaborn?
  back: Axes-level (`boxplot`) draws on an Axes you pass. Figure-level (`catplot`) makes its own Figure so it can facet with `col=` and `row=`, and returns a `FacetGrid`.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-plotting
- front: Why does seaborn want tidy data?
  back: You map columns to roles such as x, hue and col, so each variable needs its own column and each observation its own row.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-plotting
- front: Which chart for a change over time, a comparison, a distribution, or a relationship?
  back: Line, sorted bars, histogram or box, and scatter.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-plotting
- front: Why must bars start at zero when lines need not?
  back: A bar encodes the value by its length, so cutting the axis misstates ratios. A line encodes change by position.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-plotting
- front: What is wrong with a dual-axis chart?
  back: The two scales are arbitrary, so any apparent relationship between the lines depends on how they were chosen. Use two panels or index both to a common base.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-plotting
- front: What does a box plot show?
  back: The median, the middle 50% of the data, whiskers, and outliers. It compares spread as well as centre across groups.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-plotting
- front: How do you handle overplotting?
  back: Lower the opacity, shrink the marks, use `hexbin` or a 2D histogram, or sample.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-plotting
---
