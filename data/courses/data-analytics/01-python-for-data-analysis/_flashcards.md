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
---
