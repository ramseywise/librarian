---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- data-analytics/01-python-for-data-analysis/slides/deck.yaml
- data-analytics/01-python-for-data-analysis/slides/lectures/00-overview.yaml
- data-analytics/01-python-for-data-analysis/slides/lectures/01-extract.yaml
- data-analytics/01-python-for-data-analysis/slides/lectures/02-clean.yaml
- data-analytics/01-python-for-data-analysis/slides/lectures/03-summarise.yaml
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
- front: What can go wrong when read_csv runs on the shop's raw export without options?
  back: The banner line becomes the header (shape (14, 1)), qty loads as float64 because n/a is missing and a gap promotes it, unit_price stays text because of the dollar signs, date stays text, and the file's own - marker for a missing region is not known to pandas.
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-data
- front: Which read_csv options state a parse decision, and what does each protect against?
  back: comment skips a banner line, na_values names a file's own missing marker, parse_dates gives real dates, and dtype keeps an identifier such as 01234 as text instead of the integer 1234.
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-data
- front: Which three read_csv options load the shop's export with the banner, the dash marker and the dates handled?
  back: 'Pass comment="#", na_values for the file''s own - marker in region, and parse_dates=["date"], then check isna().sum(): qty and region each have 2 gaps.'
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-data
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
- front: Which shape do groupby and seaborn want, and what do melt and pivot do?
  back: They want long (tidy) data, with one row per observation. melt turns wide data into long, and pivot turns long into wide (pivot_table when keys repeat).
  lesson: data-analytics/01-python-for-data-analysis/notes/04-reshaping-and-joins
- front: How do you decide what to do with a missing value?
  back: Ask why it is missing. Not recorded gets labelled unknown, a lost value is confirmed with the owner, and a return is removed and reported. Filling with the mean by reflex can invent data.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-cleaning
- front: What are the steps from raw CSV to clean frame, and why put them in a function?
  back: Read the raw text, parse with options, fix text and types, drop rows with reasons, then assert. One function over an unchanged raw file can be rerun and audited, for example on next month's export.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-cleaning
- front: Why must a date column be parsed, and what happens if you sort it as text?
  back: Text sorts by its first character, so October 2025 (10/1/2025) comes before November 2024. Any latest order or first purchase computed on the text is wrong and nothing says so, so parse with pd.to_datetime and a format.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-dates-and-times
- front: Name the ways a parsed date can still be wrong, and the fix for each.
  back: Ambiguous day and month (state format=), a parse that ran (count the NaT and read min and max, since a date in 2052 parses), format="mixed" (it keeps the ambiguity, so parse each source with its own format), 30 days is not a month (use DateOffset or periods), and naive timestamps (store in UTC and pick the reporting zone before daily totals).
  lesson: data-analytics/01-python-for-data-analysis/notes/06-dates-and-times
- front: How should you calculate a group's rate, and why is the mean of per-order rates wrong?
  back: Sum the numerator and the denominator per group, then divide. A mean of per-order rates weights small and large orders equally, so east shows 0.492 against its true 0.398.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: Why should every group mean come with a count, and what happens to rows with a missing key?
  back: A mean of one order prints as confidently as a mean of ten thousand, so the count shows how much it rests on. Rows with a missing key vanish from a groupby unless you pass dropna=False.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: What can a line chart show about a time series that describe() cannot?
  back: 'The ordering in time: trend, weekly pattern, outages and the December jump. Rows have an order and absent days are invisible in a table, so the line makes gaps and changes visible.'
  lesson: data-analytics/01-python-for-data-analysis/notes/08-time-series
- front: What did pandas 3 change about frequency aliases, and why?
  back: 'It removed the old aliases M, Q, Y, H and T, so write ME, QE, YE, h and min. The reason is ambiguity: ME says month end, as distinct from MS for month start.'
  lesson: data-analytics/01-python-for-data-analysis/notes/08-time-series
- front: What do closed and label control in a resample, and why check count?
  back: closed sets which edge of a bin belongs to it and label sets which edge names the bin. count shows how many observations each bin has, exposing that March lost two days.
  lesson: data-analytics/01-python-for-data-analysis/notes/08-time-series
- front: What is leakage in a time series, and which two pandas options cause it?
  back: Leakage is a feature reading the future, which cannot exist in production. A negative shift such as shift(-1) and center=True in a rolling window both cause it.
  lesson: data-analytics/01-python-for-data-analysis/notes/08-time-series
- front: Why compare with shift(7), and how do rolling(7) and rolling("7D") differ?
  back: shift(7) compares the same weekday, so the typical change drops from 13% to about 9%. rolling(7) counts rows and rolling("7D") counts calendar days, so they differ when rows are absent.
  lesson: data-analytics/01-python-for-data-analysis/notes/08-time-series
- front: Name the checks you run when loading, cleaning, joining, grouping and resampling.
  back: 'Loading: keep the raw file and use one rerunnable function. Joining: state how and validate, then compare rows and one total. Grouping: print counts, sum then divide for ratios, check groups add up. Cleaning: count what coerce and parsing turn into NaN and NaT, and read the earliest and latest date. Resampling: show gaps with asfreq and keep model features looking backward.'
  lesson: data-analytics/01-python-for-data-analysis/notes/08-time-series
- front: Which three mistakes give a clean-looking number that is wrong?
  back: A join that doubles rows, a price column that is still text, and an average of averages. None of them raises an exception.
  lesson: data-analytics/01-python-for-data-analysis/readme
- front: What are the three steps of processing data, and what does each one produce?
  back: Extract gives the rows and columns you need. Clean makes every column the type it claims to be. Summarise gives one number per group.
  lesson: data-analytics/01-python-for-data-analysis/readme
- front: Which four ideas make the extract step go right?
  back: Know what one row means. Labels and positions are different things. A filter is a mask of true and false. A join can multiply rows, so count before and after.
  lesson: data-analytics/01-python-for-data-analysis/readme
- front: Which four ideas make the clean step go right?
  back: The type of a column decides what an operation means. A gap is a decision, and missing is not zero. A date is a type, not text. Keep the raw file untouched and put every fix in one function.
  lesson: data-analytics/01-python-for-data-analysis/readme
- front: Which checks keep a group summary honest?
  back: Print a count beside every mean. For a rate, sum the top, sum the bottom, then divide. Check that the groups add back up to the total. Keep a window that feeds a model looking backward.
  lesson: data-analytics/01-python-for-data-analysis/readme
- front: When do you reach for SQL, pandas or Polars?
  back: SQL when the data lives in a database, so it reads less and sends back less. pandas when the result fits in memory and you need to clean, reshape and look at it. Polars when the files are large but still fit on one machine.
  lesson: data-analytics/01-python-for-data-analysis/readme
- front: Why do older pandas tutorials and books now mislead?
  back: Pandas 3.0 changed enough that older material misleads in places, and the notes say where.
  lesson: data-analytics/01-python-for-data-analysis/readme
- front: Where does the course teach plotting your own table?
  back: Plotting is taught in visualisation and storytelling, in the chapter Plotting your own data.
  lesson: data-analytics/01-python-for-data-analysis/readme
- front: Which habits catch most problems with a new table?
  back: Run shape, dtypes, head and isna().sum() on every new frame. Keep the raw file untouched. State how and validate on every merge, then compare row counts. Print a count beside every mean.
  lesson: data-analytics/01-python-for-data-analysis/readme
- front: Which later chapters build on processing data?
  back: The data-analysis agent in generative AI, quality dimensions and tests in data engineering, and time-series ML in data science.
  lesson: data-analytics/01-python-for-data-analysis/readme
- front: What can you not yet say after processing data?
  back: You cannot yet say whether a difference in the table is real or luck, which is the next module.
  lesson: data-analytics/01-python-for-data-analysis/readme
- front: What does a DataFrame let you leave out of the loop?
  back: 'The bookkeeping: naming the accumulator, handling a customer''s first appearance and spelling out the arithmetic per row. Three lines remain, and the groupby line is the question itself.'
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: What are the parts of a Series?
  back: Values of one type, an index holding a label for each value, and a dtype for the values.
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: How do you read the values, the index and the dtype of a Series?
  back: Use to_numpy() for the values, list(qty.index) for the labels and qty.dtype for the type.
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: What two habits follow from having labels?
  back: You look values up by label, and you do arithmetic on the whole column at once, which is called vectorisation.
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: Why does adding two Series with different labels not go wrong?
  back: Operations between two objects match values by label, not by position, so each product is matched with itself whatever its order.
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: What does week1 + week2 give when each week is missing a product?
  back: filter adds to 55.0 and kettle to 9.0, while grinder and scale are NaN, and the result is float64.
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: How do you say that a missing label means zero sales?
  back: 'Use add with a fill value: week1.add(week2, fill_value=0).'
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: What is a DataFrame made of?
  back: A set of Series, one per column, that share one index, and each column has a single dtype.
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: How do you build a DataFrame from a dictionary of equal-length lists?
  back: Pass pd.DataFrame a dictionary whose keys are the column names and whose values are equal-length lists.
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: Which commands do you run first on a new frame?
  back: shape, head, dtypes and info, then describe and value_counts for what the values look like.
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: In describe, what do a low count and a mean above the median tell you?
  back: A count below the number of rows means gaps. A mean above the median means a few large values pull it up, as the one 95.00 grinder does to unit_price (mean 37.67, median 35.00).
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: What does sum do on numbers that were read as strings?
  back: 'It concatenates them: 3, 12 and 5 sum to 3125, and after pd.to_numeric they sum to 20.'
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: What happens to an int64 column that gets one gap?
  back: It is promoted to float64, because NaN is a floating-point value.
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: How much memory did category save in McKinney's 10-million-element example?
  back: 80,000,080 bytes as strings against 10,000,272 as category, about 8 times less, after a one-off 726 ms astype.
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: How do you add a column, keep the bulk orders and sort them by revenue?
  back: Assign orders["revenue"] = qty * unit_price, filter with orders[orders["is_bulk"]], then sort_values("revenue", ascending=False).
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: What is the Copy-on-Write rule in pandas 3?
  back: The result of any indexing operation or method behaves as if it were a copy, so changing one object never changes another.
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: How do you change part of a frame in pandas 3?
  back: Use a single .loc call that makes the selection and the assignment together.
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: Which six traps does the first chapter warn about?
  back: Iterating row by row, reading .0 as harmless, trusting a dtype unseen, comparing with NaN using == (it is always false, so use isna()), following pre-3.0 advice on views and copies, and forgetting that methods return new objects.
  lesson: data-analytics/01-python-for-data-analysis/notes/01-series-and-dataframe
- front: What are the steps of a careful load?
  back: Look at the raw file, read_csv with the decisions stated, check shape, dtypes and missing counts, then take only the rows and columns you need.
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-data
- front: Why read the raw text before you parse it?
  back: A banner line, a second header or a footer total is obvious in the first lines and invisible in a frame.
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-data
- front: What does the naive read_csv give for a file with a banner line?
  back: A frame of shape (14, 1) whose only column is named after the banner line.
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-data
- front: Why is the parse with comment="#" still not right?
  back: qty is float64 because of the n/a, unit_price and date stay str, and the "-" for a missing region is not recognised.
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-data
- front: Which three options deal with the banner, the missing marker and the dates?
  back: 'comment="#", na_values={"region": ["-"]} and parse_dates=["date"].'
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-data
- front: Which function reads Excel, and what does it need?
  back: read_excel, which needs openpyxl, and sheet_name picks the sheet.
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-data
- front: Why can't a peek with nrows tell you a column's type?
  back: The n/a further down was never read, so qty looks like an integer on four rows but is not on the full column.
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-data
- front: How do you pass a value into a read_sql query safely?
  back: Through params, and never by pasting values into the query string.
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-data
- front: What does a lazy scan_csv push into the read?
  back: The filter and the column choice. The plan read four of the seven columns (the three asked for plus region, which the filter needs) and applied the filter inside the scan.
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-data
- front: Which tool filters before the data is sent?
  back: SQL through read_sql filters in the database before anything is sent. pandas filters in memory after the whole file is read, and Polars filters inside the scan.
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-data
- front: Which eight mistakes make a load go quietly wrong?
  back: Parsing before reading the raw text, trusting a parse that ran, letting read_csv guess identifiers, leaving the encoding to the default, judging types from a peek, loading a table to filter it, pasting values into a query string, and expecting two tools to guess alike.
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-data
- front: What forms of selection does a NumPy array give you?
  back: A position, a slice with the start included and the stop excluded, a boolean mask, and a list of positions.
  lesson: data-analytics/01-python-for-data-analysis/notes/03-indexing-and-selection
- front: Which three NumPy behaviours carry into pandas?
  back: A slice is a view, boolean and list-of-positions selection always copies, and masks combine with & and | in parentheses.
  lesson: data-analytics/01-python-for-data-analysis/notes/03-indexing-and-selection
- front: What does each of [], loc and iloc select by?
  back: '[] picks columns by name and filters rows with a boolean Series, loc selects by label, and iloc selects by integer position.'
  lesson: data-analytics/01-python-for-data-analysis/notes/03-indexing-and-selection
- front: How many rows do loc[0:2] and iloc[0:2] return?
  back: loc[0:2] returns three rows because a label slice includes its end, and iloc[0:2] returns two because a position slice excludes it.
  lesson: data-analytics/01-python-for-data-analysis/notes/03-indexing-and-selection
- front: What happens to the labels of a filtered frame?
  back: They keep their original values and gain gaps, so loc and iloc give different answers to what looks like the same question.
  lesson: data-analytics/01-python-for-data-analysis/notes/03-indexing-and-selection
- front: What does a bare integer in square brackets mean on a Series in pandas 3?
  back: Always a label. Older versions fell back to position when the index held no integers, and now a text index raises a KeyError.
  lesson: data-analytics/01-python-for-data-analysis/notes/03-indexing-and-selection
- front: Why does and fail in a mask?
  back: and and or try to reduce a whole Series to a single truth value, which raises a ValueError.
  lesson: data-analytics/01-python-for-data-analysis/notes/03-indexing-and-selection
- front: What do isin, between, .str and query do?
  back: isin tests membership, between gives a range with both ends included by default, .str methods handle text, and query writes the condition as a string.
  lesson: data-analytics/01-python-for-data-analysis/notes/03-indexing-and-selection
- front: How do you set part of a column, and build a column from a condition?
  back: Put the row selection and the column in the same .loc, and use np.where for two outcomes, or np.select or pd.cut for more.
  lesson: data-analytics/01-python-for-data-analysis/notes/03-indexing-and-selection
- front: What do set_index, reset_index and reindex do?
  back: set_index makes an identifying column the index, reset_index moves it back to a column, and reindex conforms to a list of labels, inserting NaN for new ones.
  lesson: data-analytics/01-python-for-data-analysis/notes/03-indexing-and-selection
- front: What does loc return on a non-unique index?
  back: A DataFrame when the label repeats and a Series when it does not, so check index.is_unique or pass a list.
  lesson: data-analytics/01-python-for-data-analysis/notes/03-indexing-and-selection
- front: How do you select from a two-level index?
  back: Use a tuple for one exact combination, a single value for everything under an outer level, and xs to cut across an inner level.
  lesson: data-analytics/01-python-for-data-analysis/notes/03-indexing-and-selection
- front: When do labels stop matching positions?
  back: After the first filter or sort, so use iloc for the first row and loc for the row labelled this.
  lesson: data-analytics/01-python-for-data-analysis/notes/03-indexing-and-selection
- front: What makes a dataset tidy?
  back: Each variable is a column, each observation is a row, and each type of observational unit is a table.
  lesson: data-analytics/01-python-for-data-analysis/notes/04-reshaping-and-joins
- front: What do inner, left, right and outer joins keep?
  back: Inner keeps only matches, left keeps every order, right keeps every customer, and outer keeps everything, with NaN where a side is absent.
  lesson: data-analytics/01-python-for-data-analysis/notes/04-reshaping-and-joins
- front: How do you find which rows a join could not match?
  back: 'Use indicator=True and read _merge: left_only rows had no customer record and right_only rows had no orders.'
  lesson: data-analytics/01-python-for-data-analysis/notes/04-reshaping-and-joins
- front: Which three checks make a join safe?
  back: State validate (validate="many_to_one" raises a MergeError when the right keys repeat), compare the row count before and after, and compare one total.
  lesson: data-analytics/01-python-for-data-analysis/notes/04-reshaping-and-joins
- front: Which category keeps the larger share of its revenue as margin?
  back: Consumables keep about 62 of every 100 (60.0 of 97.5) against about 37 for brew gear (142.0 of 382.0), since a filter costs 2.50 and sells at 6.50.
  lesson: data-analytics/01-python-for-data-analysis/notes/04-reshaping-and-joins
- front: What happens to a column that one frame lacks in concat?
  back: It is NaN for that frame's rows, not an error, and ignore_index=True gives fresh row labels.
  lesson: data-analytics/01-python-for-data-analysis/notes/04-reshaping-and-joins
- front: When is a wide table untidy, and which function fixes it?
  back: When its column headers are values of a variable (w1, w2 and w3 are weeks). melt turns them into rows.
  lesson: data-analytics/01-python-for-data-analysis/notes/04-reshaping-and-joins
- front: What does unstack do, and when is fill_value=0 right?
  back: unstack moves an index level up into the columns, with missing combinations as NaN, and fill_value=0 is right when a missing combination means no units sold.
  lesson: data-analytics/01-python-for-data-analysis/notes/04-reshaping-and-joins
- front: How does a pandas merge treat NaN keys differently from SQL?
  back: Unlike SQL, a pandas merge matches NaN keys to each other, so drop or fill missing keys before joining.
  lesson: data-analytics/01-python-for-data-analysis/notes/04-reshaping-and-joins
- front: What are the habits of a careful extract?
  back: Read the raw file and state your decisions, check every new frame, choose loc or iloc on purpose, filter with masks, validate joins, and change data with one loc call.
  lesson: data-analytics/01-python-for-data-analysis/notes/04-reshaping-and-joins
- front: What is left to fix once the right rows and tables are in?
  back: Gaps in qty and region, south and South counted as two regions, keys such as Ana and ana with a trailing space that will not join, and unit_price still read as str.
  lesson: data-analytics/01-python-for-data-analysis/notes/04-reshaping-and-joins
- front: Which half of the 80% claim is the useful half?
  back: 'The second half: preparation is no one-off first step. It gets repeated as new problems surface, so write it as a script you can rerun.'
  lesson: data-analytics/01-python-for-data-analysis/notes/05-cleaning
- front: What are the steps from the loaded frame to a saved one?
  back: Count, fix, decide, assert and save, and go back to counting whenever a new problem turns up.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-cleaning
- front: Which of the loaded columns is already the type it claims to be?
  back: Only date is already the type it claims to be, so read the other dtypes as a list of jobs.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-cleaning
- front: Why does a groupby count two spellings of filter as separate things?
  back: A groupby counts different spellings of one value as separate things, and an invisible space is enough.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-cleaning
- front: How do you normalise every text column the same way?
  back: Strip the whitespace and then lower the case, the same way on every text column.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-cleaning
- front: How do you pull a tracking reference out of free text?
  back: Use a regular expression through str.extract, where each capture group becomes a column and a miss is NaN.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-cleaning
- front: How do you turn a column of prices with dollar signs into numbers?
  back: Strip the sign with regex=False, convert with errors="coerce", and count the NaN it makes.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-cleaning
- front: What is the difference between map and replace?
  back: map applies the dictionary to every value, and a value absent from it becomes NaN. replace changes only the values you list and leaves the rest.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-cleaning
- front: Why check the column that should be unique and not only the whole row?
  back: Check duplicates on the column that should be unique, because a full-row comparison misses rows that differ elsewhere.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-cleaning
- front: What is the difference between a structural missing value and a missing observation?
  back: A structural missing value stands for something that could not be measured, so it can safely be removed. A missing observation should have been recorded and was not, so it needs keeping.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-cleaning
- front: Which columns have gaps in the cleaned export, and in which orders?
  back: Orders 1005 and 1010 have no region and order 1006 has no qty, and the two kinds of gap need different treatment.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-cleaning
- front: What do you do with a missing region and a missing qty?
  back: Keep a row with a missing region, but find out a missing qty instead of filling it with the mean.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-cleaning
- front: How do you record that the shop owner confirmed a quantity?
  back: Write a confirmed fact in with a single .loc and a comment, then cast qty to int64 now it has no gaps.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-cleaning
- front: When does ffill make sense, and what do sum and mean do with gaps?
  back: ffill fits a slowly changing reading such as a price list, not independent orders. sum and mean skip gaps, so the mean of 48, gap, gap, 52, gap is 50.0, over 2 values and not 5.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-cleaning
- front: Why set returns aside in their own frame and not delete them?
  back: Set impossible rows aside and keep them, because you can then report the loss and undo it.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-cleaning
- front: Which four assertions does the cleaning script make about the orders?
  back: Assert a unique key, no gaps in key columns, a range for qty and the allowed regions, because next month's export will differ.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-cleaning
- front: How does VanderPlas's rule bound a column with no business rule?
  back: Keep values within 5 sig of the median, where sig is 0.74 times the interquartile range, and count what you drop.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-cleaning
- front: When do you choose cut, and when qcut?
  back: Use cut for meaningful fixed thresholds and qcut for equal-sized groups, and chapter 7 feeds either into groupby.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-cleaning
- front: Why use Parquet between steps of your own work?
  back: Parquet keeps the types a CSV loses, so use it between your own steps and CSV to hand data on.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-cleaning
- front: How do you write the cleaning steps as one rerunnable function?
  back: One function that takes a path and returns a clean frame lets next month's export run through the same steps.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-cleaning
- front: What does load_orders print, and which rows does that line account for?
  back: It prints loaded 13 rows, kept 11. The two removed rows are the repeat of order 1006 and the return, order 1008.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-cleaning
- front: Which habits keep a cleaning script from going quietly wrong?
  back: Keep the raw data unchanged and fix in code. Count what coerce makes. Ask why a value is missing. Print row counts and keep what you removed. Check the column that should be unique. Use Parquet, not pickle, to archive. Assert the range and the allowed values.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-cleaning
- front: What are a timestamp, a timedelta and a period?
  back: A timestamp is a moment, a timedelta a length and a period a span, and most confusion goes once you know which.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-dates-and-times
- front: What goes wrong when you sort dates as text?
  back: Text sorts by character, so a latest order computed on a text column is wrong and nothing says so.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-dates-and-times
- front: Why should you state the format when you parse dates?
  back: State the format whenever you know it, so pandas cannot guess a day or month wrong.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-dates-and-times
- front: Which three numbers catch most date-parsing problems?
  back: Count the failures and read the min and max, because a typo such as 2052 parses perfectly and only max shows it.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-dates-and-times
- front: Why does format="mixed" not fix a column that mixes date conventions?
  back: Neither call can know what the writer meant, so parse each batch of rows with its own explicit format.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-dates-and-times
- front: What does subtracting two datetime columns give you?
  back: Subtracting datetimes gives a timedelta column, whose mean here is 3 days 6 hours and whose days you can pull out with .dt.days.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-dates-and-times
- front: What does adding 30 days to 31 January give, against one calendar month?
  back: 30 days gives 2 March, and one calendar month gives 28 February, the last day that exists.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-dates-and-times
- front: What does a period know about itself?
  back: A period labels a whole month, so nobody argues whether the row stands for the 1st or the 31st.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-dates-and-times
- front: What do you have to define before two people compare week numbers?
  back: Define week 1 before comparing week numbers, and remember a groupby hides weeks that have no rows.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-dates-and-times
- front: Which dates does fiscal 2012 Q4 run between with a year ending in January?
  back: Fiscal quarter 4 of 2012 runs from 1 November 2011 to 31 January 2012 when the year ends in January.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-dates-and-times
- front: What is the sensible rule for storing timestamps?
  back: Keep stored data in UTC and convert only for display, because daylight saving makes local hours irregular.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-dates-and-times
- front: Why does the reporting zone change which day a sale falls on?
  back: A daily or even monthly total by local date differs from one by UTC date, so choose the reporting zone before grouping.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-dates-and-times
- front: What are the traps in converting local times to UTC?
  back: The offset changes with daylight saving, so a fixed hour is wrong half the year. A local time that never happened raises. `utc=True` converts text that carries its own offsets, so two strings that both say 10:00 come out an hour apart.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-dates-and-times
- front: Which four habits keep a date parse from going quietly wrong?
  back: Check `dtypes` and pass `parse_dates`. State `format=`. After `errors="coerce"`, count the NaT and read `min` and `max`. Parse each source with its own format.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-dates-and-times
- front: Which habits keep date arithmetic and time zones from going quietly wrong?
  back: Add a month with DateOffset or work in periods. Label a whole month with a period. Localize each source on arrival. Store in UTC.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-dates-and-times
- front: Which rules of thumb keep a cleaning job honest?
  back: Keep the raw file and fix in code. Count what coerce makes. Ask why a value is missing. Assert meanings. State date formats. Store time in UTC.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-dates-and-times
- front: What happens to the cleaned export next?
  back: 'It is summarised: chapter 7 groups it, and chapter 8 puts time on the axis, resamples and shows gaps.'
  lesson: data-analytics/01-python-for-data-analysis/notes/06-dates-and-times
- front: What are the three stages of a groupby?
  back: Split the rows by key, apply a function to each piece on its own, and combine the results into one object.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: What does a GroupBy object compute on its own?
  back: A GroupBy object computes nothing until you ask for an aggregation, and iterating over it gives each key with its piece.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: Which kind of calculation falls outside split, apply, combine?
  back: One whose pieces overlap, such as a running mean, where each step overlaps the last. It needs different tools, the rolling windows later in this lecture.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: What can you pass as a groupby key?
  back: A key is a column, a list of columns, or any Series of the right length, and as_index=False keeps keys as columns.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: What is the difference between size and count in a groupby?
  back: size counts rows including missing values, and count counts non-missing values per column, so they differ when a column has gaps.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: Why print a count beside every group mean?
  back: A mean can rest on very few values. Here 5.0 for n rests on one rating out of two rows and 4.0 for s on one out of three, and only the count shows it.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: Why does mean on a frame with text columns now raise an error?
  back: Current pandas raises a TypeError on text columns, where old versions silently dropped them. Select the numeric columns you mean or pass numeric_only=True.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: How does named aggregation name its output columns?
  back: Named aggregation takes a source column and a function for each output name, and built-in names beat your own function.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: How do you compute a group's rate in pandas?
  back: Sum the numerator and the denominator per group, and only then divide.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: What changes between the mean of rates and the true rate by region?
  back: East beats north on the mean of rates, but north wins on the true rate, so the method changes the ranking.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: Why does east show 0.492 when its true margin rate is 0.398?
  back: East averages two very different rates to 0.492, while the shop kept 43.0 of 108.0, or 0.398.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: What does transform return that agg does not?
  back: transform returns one value per original row, so the result lines up with the frame and can become a new column.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: Which questions does transform answer that a raw number cannot?
  back: transform answers questions a raw number cannot, such as whether a row is large for its group, and it beats apply for group statistics.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: Why fill a gap from its own group, and what comes first?
  back: The group's mean beats the global mean when regions differ. First ask why the value is missing.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: What does the function you pass to filter receive and return?
  back: It receives a whole group and returns True or False, and True keeps all of that group's rows.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: How do agg, transform, filter and apply differ in what they return?
  back: agg returns one row per group, transform the same rows as the input, filter a subset of the rows, and apply anything you stitch together.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: When is apply worth using, and what is faster for the top row per group?
  back: Use apply only when nothing more specific fits, since it is the slowest option. For the top row per group, sort_values then groupby(...).head(1) is faster and keeps the frame flat.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: What does the observed option do when a group key is categorical?
  back: Since pandas 3.0, observed defaults to True so empty categories vanish, and observed=False keeps them for a fixed report.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: What happens to rows whose group key is NaN, and how do you catch it?
  back: Rows with a missing key vanish by default, so compare the sum of the groups with the overall total or use dropna=False.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: What does a pivot table add to a groupby by two keys?
  back: A pivot table is a groupby by two keys laid out as a grid, and margins=True adds the totals.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: When do you use pivot_table, and when crosstab?
  back: pivot_table aggregates any value and defaults to the mean, while crosstab counts and can normalize into shares.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: What does normalize do in crosstab?
  back: normalize turns counts into shares, so east is half brew and half consumable whatever its size.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: Name the groupby pitfalls and the fix for each.
  back: Averaging averages (sum, then divide), lost NaN keys (dropna=False), size and count swapped, means without counts, the default aggfunc of pivot_table (the mean), old syntax (axis=1, text columns), and reaching for apply first (use agg or transform).
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: Which four rules does time add to a grouping?
  back: Time adds order, unequal months, interval labels and absent rows, which is why it is more than another key.
  lesson: data-analytics/01-python-for-data-analysis/notes/08-time-series
- front: What are partial strings on a DatetimeIndex?
  back: A DatetimeIndex takes partial strings, so a year or a month is a slice of the time axis and slices include both ends.
  lesson: data-analytics/01-python-for-data-analysis/notes/08-time-series
- front: How do you make absent rows visible in a time series?
  back: Conform the series with asfreq to see absent days as NaN, then decide what each gap means.
  lesson: data-analytics/01-python-for-data-analysis/notes/08-time-series
- front: Which frequency aliases did pandas 3.0 replace, and why?
  back: M, Q, Y, H and T became ME, QE, YE, h and min, because ME (month end) had to be told apart from MS (month start).
  lesson: data-analytics/01-python-for-data-analysis/notes/08-time-series
- front: What does shift do to the index and to the values?
  back: shift slides values along the index so each row can see an earlier value, which is the tool behind every comparison to a previous period.
  lesson: data-analytics/01-python-for-data-analysis/notes/08-time-series
- front: How much does a seasonal shift cut the typical change, and why?
  back: Shifting by 7 compares the same weekday and cuts the typical change from 13% to about 9%.
  lesson: data-analytics/01-python-for-data-analysis/notes/08-time-series
- front: What does resample do, and what does count add to the output?
  back: resample is a groupby whose key is a time bin. The count shows how many observations each bin holds, here 31, 29 and 29 for January to March.
  lesson: data-analytics/01-python-for-data-analysis/notes/08-time-series
- front: Why is a monthly sum not directly comparable, and what is fairer?
  back: A monthly sum compares unequal lengths, so read the count and the mean beside it.
  lesson: data-analytics/01-python-for-data-analysis/notes/08-time-series
- front: What do closed and label control in a resample?
  back: closed says which edge belongs inside the bin and label says which edge names it, so choose both on purpose.
  lesson: data-analytics/01-python-for-data-analysis/notes/08-time-series
- front: What does upsampling create, and what does carrying a value forward assume?
  back: Upsampling creates rows with nothing in them. Carrying a value forward assumes it held until the next one, which suits a price list and misrepresents a sales total.
  lesson: data-analytics/01-python-for-data-analysis/notes/08-time-series
- front: Which calendar groupings does the note use on the daily series?
  back: Group by a period for calendar months, and by the weekday name for the seasonal view.
  lesson: data-analytics/01-python-for-data-analysis/notes/08-time-series
- front: How do rolling, expanding and ewm differ on the same days?
  back: rolling slides a fixed window, seven rows for rolling(7) and seven calendar days for rolling("7D"). expanding averages everything so far, and ewm weights recent days more.
  lesson: data-analytics/01-python-for-data-analysis/notes/08-time-series
- front: How do rolling(7), rolling("7D"), expanding and ewm differ?
  back: rolling(7) counts rows and rolling("7D") counts days, expanding uses all so far, and ewm weights recent days more.
  lesson: data-analytics/01-python-for-data-analysis/notes/08-time-series
- front: How do trailing and centred windows differ, and which can feed a model?
  back: A trailing window uses that date and earlier ones, and a centred one uses future values. Only the trailing window can feed a model.
  lesson: data-analytics/01-python-for-data-analysis/notes/08-time-series
- front: Name the time-series pitfalls and the fix for each.
  back: Absent rows (asfreq), old aliases (ME, QE, YE, h, min), raw monthly sums (per-day means), leakage (no negative shift or center=True), removed resample arguments, duplicate timestamps (index.is_unique), an unsorted index (sort_index) and totals in the wrong time zone.
  lesson: data-analytics/01-python-for-data-analysis/notes/08-time-series
- front: Which checks do you run when you summarise by group and by time?
  back: Pick the method by shape, divide sums for rates, print counts, show gaps and keep features backward.
  lesson: data-analytics/01-python-for-data-analysis/notes/08-time-series
- front: What can't the toolkit tell you about a difference between groups?
  back: Whether a difference in the table is real or luck, which probability and statistics answer next.
  lesson: data-analytics/01-python-for-data-analysis/notes/08-time-series
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
- front: A CSV loaded without error. How do you know the parse is right?
  back: Read the raw file first. Then check `shape`, `dtypes` and `isna().sum()` against what the file should hold, and compare a row count or a total with the source.
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-data
- front: What does `read_csv` treat as missing?
  back: The empty string and markers such as `NA`, `NaN`, `null` and `n/a` by default. A file's own marker, such as `-`, needs `na_values`.
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-data
- front: Why did an integer column load as float?
  back: It contains a missing value, and a gap promotes the default integer column to float.
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-data
- front: Why state `dtype` for an identifier?
  back: Type guessing turns `01234` into 1234. Identifiers are text, and are never used in arithmetic.
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-data
- front: How do you read a file larger than memory?
  back: '`usecols` and `nrows` to look at it, `chunksize` to aggregate it in pieces, or a lazy scan that reads only what the query needs.'
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-data
- front: 'Where should a filter run: in SQL or in pandas?'
  back: In the database when the data lives there, so less is read and sent. Reshape and inspect the smaller result in pandas.
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-data
- front: What does a lazy scan buy you over an eager read?
  back: The filter and the column choice are pushed into the read, so rows and columns that are not needed are never loaded.
  lesson: data-analytics/01-python-for-data-analysis/notes/02-loading-data
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
- front: A column of numbers loaded as text. What do you do?
  back: Find the bad values with `to_numeric(errors="coerce")` and `isna`, decide what they mean, then add them to `na_values` or fix them.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-cleaning
- front: How do you handle missing data?
  back: Ask why it is missing first. Structural gaps can be removed. A gap in an observation needs keeping, filling with a reasoned value, or a stated exclusion. If missingness relates to the value, dropping biases results.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-cleaning
- front: What is the difference between `map` and `replace`?
  back: '`map` applies a mapping to every value and gives `NaN` for anything unmapped. `replace` changes only listed values.'
  lesson: data-analytics/01-python-for-data-analysis/notes/05-cleaning
- front: How do you find duplicates?
  back: '`duplicated` on the column that should be unique, with `keep=False` to see all copies, then decide before calling `drop_duplicates`.'
  lesson: data-analytics/01-python-for-data-analysis/notes/05-cleaning
- front: When would you choose `cut` or `qcut`?
  back: '`cut` for meaningful fixed thresholds, `qcut` for equal-sized groups.'
  lesson: data-analytics/01-python-for-data-analysis/notes/05-cleaning
- front: CSV or Parquet?
  back: CSV for interchange. Parquet keeps types and compresses better at scale, so it suits work between pipeline steps.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-cleaning
- front: Why not pickle?
  back: It suits only short-term storage. Later library versions may not be able to read it, and it can run code when loaded, so never unpickle untrusted files.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-cleaning
- front: How do you stop bad data reaching a report?
  back: A rerunnable loader with assertions on keys, ranges and allowed values, printing row counts at each stage.
  lesson: data-analytics/01-python-for-data-analysis/notes/05-cleaning
- front: A date column loaded as text. Why does it matter?
  back: Text sorts by character, so `10/1` comes before `9/1`. It cannot be subtracted, grouped by month or resampled.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-dates-and-times
- front: How do you parse a date column safely?
  back: State `format`. Use `errors="coerce"` and count the `NaT`. Read `min` and `max` for implausible dates.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-dates-and-times
- front: What do you do with `03/04/2025`?
  back: It is ambiguous. Find out the source's convention and state the format. A column that mixes conventions has to be split by source.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-dates-and-times
- front: Timestamp, timedelta or period?
  back: A moment, a length of time, and a span with a start and an end. Use periods when a row stands for a whole month or quarter.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-dates-and-times
- front: How do you add one month to a date?
  back: '`pd.DateOffset(months=1)`, which follows the calendar. `Timedelta(days=30)` is a fixed length and drifts.'
  lesson: data-analytics/01-python-for-data-analysis/notes/06-dates-and-times
- front: What is a naive timestamp?
  back: One with no time zone. `tz_localize` declares its zone and `tz_convert` changes the zone of an aware one.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-dates-and-times
- front: How do you handle time zones?
  back: Store in UTC, convert for display, and pick the reporting zone before grouping by day or month. Local days can be 23 or 25 hours long.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-dates-and-times
- front: Why did converting a datetime to an integer change?
  back: Pandas 3.0 infers the resolution, usually microseconds and no longer nanoseconds. State the unit with `as_unit`.
  lesson: data-analytics/01-python-for-data-analysis/notes/06-dates-and-times
- front: What is split-apply-combine?
  back: Break data into groups, operate on each independently, reassemble (Wickham 2011). It is `GROUP BY` and pivot tables as one idea.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: '`size` or `count`?'
  back: '`size` counts rows, `count` counts non-missing values per column.'
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: What is the difference between `agg`, `transform`, `filter` and `apply`?
  back: One row per group, same rows as the input, a subset of input rows, and anything.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: How do you compute a group's rate?
  back: Ratio of sums. The mean of per-row rates weights every row the same, whatever its size.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: How would you get each row's share of its group?
  back: '`x / x.groupby(key).transform("sum")`.'
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: What happens to `NaN` group keys?
  back: They are dropped by default. Use `dropna=False`, and check that groups add up to the total.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: How do you get the top N per group?
  back: '`sort_values` then `groupby(...).head(n)`, or `apply` with `nlargest`.'
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: '`pivot_table` or `crosstab`?'
  back: '`pivot_table` aggregates any value and defaults to the mean. `crosstab` counts by default and can `normalize` into shares.'
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: How does this map to SQL?
  back: Keys are `GROUP BY`, aggregations are `SUM`, `COUNT`, a filter on groups is `HAVING`, and `transform` is a window function with `OVER (PARTITION BY ...)`.
  lesson: data-analytics/01-python-for-data-analysis/notes/07-groupby-and-aggregation
- front: What does `resample` do?
  back: Time-based groupby. Downsampling aggregates into bins with `closed` and `label` choices; upsampling makes empty rows that you must fill on purpose.
  lesson: data-analytics/01-python-for-data-analysis/notes/08-time-series
- front: Why did `freq="M"` start failing?
  back: Pandas 3.0 removed it for the explicit `ME` and `MS`. Similarly `QE`, `YE`, `h`, `min`.
  lesson: data-analytics/01-python-for-data-analysis/notes/08-time-series
- front: How do you do a seasonal comparison?
  back: '`shift` by the season length, such as 7 for daily data with a weekly cycle, and compare like with like.'
  lesson: data-analytics/01-python-for-data-analysis/notes/08-time-series
- front: What is the difference between `rolling(7)` and `rolling("7D")`?
  back: Seven rows against seven calendar days. They differ when rows are missing or irregular.
  lesson: data-analytics/01-python-for-data-analysis/notes/08-time-series
- front: What is leakage, and how can a time series leak?
  back: 'Using information not known at prediction time: negative shifts, centred windows, or filling backward.'
  lesson: data-analytics/01-python-for-data-analysis/notes/08-time-series
- front: Why not compare raw monthly totals?
  back: Months have 28 to 31 days, and some have missing days. Compare mean daily values, and read the count.
  lesson: data-analytics/01-python-for-data-analysis/notes/08-time-series
- front: How do you find missing days?
  back: '`asfreq("D")` then `isna().sum()`, or compare `count` per month with the calendar.'
  lesson: data-analytics/01-python-for-data-analysis/notes/08-time-series
- front: What does `ewm` do differently from a rolling mean?
  back: It weights recent values more, decaying exponentially, so it responds faster and has no hard window edge.
  lesson: data-analytics/01-python-for-data-analysis/notes/08-time-series
---
