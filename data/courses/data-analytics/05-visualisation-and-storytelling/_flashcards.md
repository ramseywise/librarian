---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- data-analytics/05-visualisation-and-storytelling/slides/deck.yaml
- data-analytics/05-visualisation-and-storytelling/slides/lectures/00-overview.yaml
- data-analytics/05-visualisation-and-storytelling/slides/lectures/01-choose-and-plot.yaml
- data-analytics/05-visualisation-and-storytelling/slides/lectures/02-static-and-interactive-charts.yaml
- data-analytics/05-visualisation-and-storytelling/slides/lectures/03-dashboards-and-story.yaml
- data-analytics/05-visualisation-and-storytelling/slides/lectures/04-dashboard-stacks.yaml
cards:
- front: What does Anscombe's quartet show about summary statistics?
  back: Four datasets can share the same means, variances, correlation and fit yet tell four different stories, so identical statistics can hide completely different data. Plot before you summarise.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: What are the independent parts of a chart in the grammar of graphics?
  back: Data, encoding, scale, mark and facet. Because they are independent, you can change one part at a time.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: In Altair, what do you change to compare a line with bars on the same encodings?
  back: 'Only the mark: swap mark_line() for mark_bar() or mark_circle(). The data and encodings stay the same, so comparing forms costs a single word.'
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: How do you choose a chart form?
  back: Name the question first (change over time, biggest category, share, distribution, relationship), then choose the form whose encoding answers it most accurately, such as a line, sorted bars, histogram or scatter.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: How do dual-axis charts and truncated bars each mislead, and what is the fix?
  back: Dual axes get crossing points from two arbitrary scales, and truncated bars make a bar's length exaggerate the gap (about 13% looks like about 460%). Use two panels or an index, and start bars at zero.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: Why should you try several bin counts on a histogram?
  back: Too few bins hide structure and too many show only noise, so try several. A mean above the median (507 against 477 here) is the same fact as a long right tail.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01b-plotting-your-own-data
- front: How do you put two pandas plots side by side, and which order should each axis use?
  back: Create fig, axes with plt.subplots, then pass ax=axes[0] and ax=axes[1] to each pandas plot call. Keep months in calendar order, sort the categories, and use the mean per day so month length does not distort the bars.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01b-plotting-your-own-data
- front: Name the plotting mistakes that mislead even when the numbers are right.
  back: Unsorted dates on a line, a line across categories, side-by-side panels without sharey=True, and opaque dots that hide density (use alpha or hexbin).
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01b-plotting-your-own-data
- front: What is wrong with a default matplotlib chart even though the data is right?
  back: Its box, ticks and legend compete with the data and the key event is not marked, so every decision about emphasis is left to the reader.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: How do you decide what stays on a chart, and keep those choices consistent?
  back: 'Make every element earn its place: remove spines, heavy gridlines and ticks, label lines directly and mark the event. Set the style once in a shared module (rcParams, fixed colour per entity) so it cannot drift.'
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: What did small multiples reveal about Fernhill's repeat rate that a single chart hid?
  back: The repeat rate drops in every channel at the same moment, so the fall is not only a change in channel mix.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: How do you apply one consistent style across all your matplotlib charts?
  back: Set rcParams once in a shared module such as chartstyle.py and draw through ax methods rather than plt, so styling stays consistent across charts.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: How do seaborn and matplotlib relate?
  back: 'Seaborn is built on matplotlib: it takes tidy data and column names, adds grouping, intervals and facets, and returns matplotlib objects you then adjust. They are not rivals.'
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: Which four habits break a matplotlib chart, and what fixes each?
  back: 'Mixing plt and ax: start with fig, ax = plt.subplots(). Seaborn choosing order: pass order= and hue_order=. Colour following rank: fix one mapping. Wrong save size: set figsize and dpi.'
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: When is an interactive chart the wrong choice?
  back: 'When you can state the finding: then state it, for example in a static chart with the answer in the title. Interaction suits readers with their own questions, such as an analyst checking their segment.'
  lesson: data-analytics/05-visualisation-and-storytelling/notes/03-plotly-and-interactive
- front: What is a plotly figure under the hood, and why does custom_data matter?
  back: It is JSON that plotly.js renders in the browser. custom_data ships extra fields such as sessions and orders with the page so a hovertemplate can show them instead of default column names.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/03-plotly-and-interactive
- front: How should you ship a plotly chart for email, a hosted page and print?
  back: Use inline HTML for email, CDN HTML for hosted pages, and always export a static copy such as a PNG, because hover cannot be printed.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/03-plotly-and-interactive
- front: When do you use plotly and when Altair?
  back: Use plotly for one rich single chart with hover. Use Altair for linked views, since its selections are declared parameters in the grammar, but note it raises MaxRowsError above 5,000 rows.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/03-plotly-and-interactive
- front: Which four mistakes make an interactive chart fail, and what fixes each?
  back: 'Finding hidden behind hover: put it in the title. Default hover text: write a template. CDN file in email: embed the library. Every point shipped: aggregate first and use go.Scattergl for large scatters.'
  lesson: data-analytics/05-visualisation-and-storytelling/notes/03-plotly-and-interactive
- front: What is the relationship between Altair and Vega-Lite?
  back: 'Altair is a Python route to Vega-Lite: it generates Vega-Lite JSON specs, which the browser then renders to SVG or Canvas.'
  lesson: data-analytics/05-visualisation-and-storytelling/notes/04-javascript-d3-vega-lite-observable-plot
- front: What does the D3 data join do?
  back: 'It makes page elements match a list of data: needed elements are created, extras are removed, and the page updates as the data changes.'
  lesson: data-analytics/05-visualisation-and-storytelling/notes/04-javascript-d3-vega-lite-observable-plot
- front: Why does the D3 chart draw invisible circles?
  back: Hover on thin lines is hard to hit, so D3 adds large invisible circles as hover targets. With D3 every element, including these, is your own code.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/04-javascript-d3-vega-lite-observable-plot
- front: When would you pick D3 over Vega-Lite?
  back: When the design justifies it, for a new chart form no library offers. D3 is good at new forms but costs the most code (67 lines against 33 for Vega-Lite here).
  lesson: data-analytics/05-visualisation-and-storytelling/notes/04-javascript-d3-vega-lite-observable-plot
- front: Which four things break hand-written D3 chart code, and what fixes each?
  back: 'Local time versus UTC: use scaleUtc and utcFormat. jsdom has no layout: test text measuring in a real browser. No xmlns on standalone SVG: set it. file:// blocks modules: serve the folder.'
  lesson: data-analytics/05-visualisation-and-storytelling/notes/04-javascript-d3-vega-lite-observable-plot
- front: Why pair a growth metric with a health metric?
  back: Anything you can raise by spending looks fine alone. Fernhill's revenue was up 6.5% while its repeat rate fell 11.3 points, so the health metric exposes what the growth metric hides.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: How does Streamlit's execution model work?
  back: Each widget change reruns the whole script top to bottom, so widgets are plain values and expensive work such as loading data should be cached with st.cache_data.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: When would you choose a BI tool over Streamlit?
  back: 'When people who do not write Python must maintain it, such as the marketing team: Metabase or Looker Studio suit standard reporting, whereas a Streamlit app owned by non-coders becomes a ticket queue.'
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: What makes a chart explanatory rather than exploratory?
  back: It keeps a single series, marks the one event, and states the finding as a sentence in the title, instead of leaving the reader to discover it.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: Why report the break-even as well as the estimate?
  back: So the reader can see the decision survives its assumptions. Here the assumed 40% margin loses about £547k, and the break-even margin is only 8.8%, so the conclusion holds across plausible margins.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: Which four mistakes lose the reader of a dashboard or a story, and what fixes each?
  back: 'Tiles with no comparison: say compared with what. Red and green only: add an arrow and a sign. Buried ask: state the decision first. False precision: say about £550k and show the sensitivity.'
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: What are the three layers of a dashboard, and which one does Plotly cover?
  back: 'Analysis, application and presentation. Plotly covers only presentation, so "Plotly or Dash?" is not a real choice: Dash is an application layer that draws with Plotly.'
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: What does px.scatter actually send to the browser?
  back: A JSON figure that contains every point, which plotly.js then draws, so the library's limits apply even when you write Python.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: Which stack fits an internal tool for a named team, and which fits a feature in your product?
  back: An internal tool for a named team starts as a Python app such as Streamlit or Dash. A feature in your product, for outside users, suits FastAPI and React with TypeScript.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: How can you review a React front end without knowing React?
  back: Check its contract (the JSON shape the analyst owns), its fetches (answers can arrive out of order), and what its types do not guarantee, since TypeScript does not check the answer at run time.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: Where do permissions, field lists and row caps belong, and why?
  back: On the server, because a caller can go around anything kept in the front end. There they are enforced even on a direct call.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: Which is heavier, 50,000 customers as JSON or all of plotly.js, and what does that imply?
  back: All of plotly.js is slightly heavier (1,449 KB against 1,419 KB gzipped), so the data is about as large as the biggest library. Fix the data first, before choosing a library.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: Why not refit the clustering when a user filters?
  back: Because it changes what the labels mean, not because it is slow. Refitting on spend above the median moved 14.8% of well-separated customers to another group, so publish one table and let filters select rows.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: When do you reach for WebGL, and when for datashader?
  back: Use WebGL (scattergl) from about 10,000 points, measured on one M4 Pro. Use datashader past about a million points or to keep the data on a server. Often you need neither.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: How should you colour customer segments in Plotly?
  back: Map each segment name to a fixed colour and add a second encoding such as shape, so colour does not depend on order of appearance or on colour alone.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: Why does Fernhill's CRM dashboard belong on the Python app route?
  back: Only a few internal CRM users need it, so a Python app (Dash, 42 lines, behind the company login proxy) is enough. The React version earns its extra code when views reach customers.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: Which three faults does a first-draft dashboard hide, and what fixes each?
  back: 'A list endpoint returning the table: return an aggregate and page rows behind a permission. A secret or cap only in the front end: enforce it on the server. Refitting or keying on cluster number: read named labels from a table.'
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: What are the rules of thumb for visualisation and storytelling?
  back: 'Form: name the question, then pick the encoding. Honesty: bars start at zero, no two y-axes. Style: remove, then emphasise. Interaction: keep essentials visible, export a static copy. Dashboards: take the lightest stack. Story: write the sentence first.'
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: In what order does the module move from a chart to a decision?
  back: Describe a chart as a mapping from data to marks, draw it in matplotlib and seaborn, make it explorable in plotly and Altair, rebuild it in JavaScript, build the dashboard and the story, then choose a dashboard stack.
  lesson: data-analytics/05-visualisation-and-storytelling/readme
- front: What are the four steps of the visualisation module?
  back: Choose and plot, draw static and interactive charts, dashboards and story, and dashboard stacks.
  lesson: data-analytics/05-visualisation-and-storytelling/readme
- front: What are the core ideas of step 1?
  back: Decide what the chart must say before choosing its type, and write the finding as the title. Position on a common scale is the most accurate encoding. Bars start at zero. Never use two y-axes.
  lesson: data-analytics/05-visualisation-and-storytelling/readme
- front: What colour scale does each job need?
  back: Categorical for identity, one hue for magnitude, and two hues with a grey midpoint for polarity. Run the palette through a colour-vision check.
  lesson: data-analytics/05-visualisation-and-storytelling/readme
- front: What does a dashboard answer, and what does it not deliver?
  back: A dashboard answers what my number is. It does not deliver a finding, so write the sentence and send it. Pair a metric you can push by spending with a metric that shows the side effect.
  lesson: data-analytics/05-visualisation-and-storytelling/readme
- front: What are the rules for choosing a dashboard stack?
  back: Pick the stack by the situation, take the lightest route that fits, and move up only for a requirement you can name. Precompute the labels, since a filter selects rows and never refits. Colour categories by name, never by numeric id.
  lesson: data-analytics/05-visualisation-and-storytelling/readme
- front: What is the Fernhill story that the module follows?
  back: Fernhill Home, a fictional online homewares shop, cut its email budget from £14k to £4k a month in January 2025 and spent more on paid social. Revenue kept rising, but a retention analyst suspects something underneath.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: What did revenue and the 90-day repeat rate do from 2023 to 2025?
  back: Revenue rose from £5.60m to £5.96m, while the share of new customers who bought again within 90 days fell from about 38% to 26%.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: What does Anscombe's quartet show?
  back: Four datasets share means, variance, correlation and fitted line and look nothing alike. Summaries alone can hide curvature, outliers and leverage.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: What is the difference between exploratory and explanatory charts?
  back: Exploratory charts are the many you make to find out what is true. Explanatory charts are the few you make to tell someone else.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: Which parts does the grammar of graphics split a chart into?
  back: Data, mark, encoding, statistic, scale, coordinates and facet.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: How do you turn Altair lines into areas or small multiples?
  back: Keep the data and the encoding, change the mark with mark_area, or add a facet.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: What does each of the three Fernhill charts show best?
  back: Lines compare channels month by month and show paid social crossing email in January 2025. The stack shows the total. Small multiples show each channel's own shape.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: In what order do people read encodings most accurately?
  back: Position on a common scale, position on non-aligned scales, length, direction and angle, area, volume and curvature, then shading and colour saturation (Cleveland and McGill, 1984).
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: Why can the Cleveland and McGill ordering be trusted?
  back: 'Heer and Bostock (2010) replicated spatial encoding and luminance contrast studies with Mechanical Turk workers, showing crowdsourced perception experiments are viable. Munzner turns it into a rule: put the most important attribute on the most accurately perceived channel.'
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: What do sorted bars show that the pie hides?
  back: Organic 44%, paid social 35%, email 12% and referral 9% read at once as sorted bars, because bars use position on a common scale.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: When is a pie chart a defensible choice?
  back: When the message is that parts make a whole or a simple fraction such as a half or a quarter. For comparing the parts, and for many pieces, side-by-side bars are better (Wilke).
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: Which chart goes with change, comparison, distribution and relationship?
  back: Change over time is a line, a comparison across categories is sorted bars or dots, a distribution is a histogram or box plot, a relationship is a scatter, many groups at once are small multiples.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: Why can a dual-axis chart tell opposite stories from the same data?
  back: Nothing in the data decides where the two scales sit relative to each other, so the crossing points and the apparent gap are whatever the author set the limits to.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: How do you replace a dual-axis chart?
  back: Give each measure its own panel on a shared time axis, mark the event, or index both series to 100 at a chosen date if they genuinely share a base.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: Why are two panels better than a dual-axis chart?
  back: A dual axis lets whoever sets the limits author the crossing. Two panels on a shared time axis keep the timing and leave no scale to argue about.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: How much does a truncated bar axis exaggerate Fernhill's quarters?
  back: Q3 revenue is 11% above Q1, but on the truncated axis it is drawn 86% taller.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: Why must bars start at zero when a line can zoom in?
  back: A bar's length is its message, and the size of a shaded area must be proportional to its value (Wilke's proportional ink). A line or dot encodes by position alone, so it can zoom if the axis says so plainly.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: What are the three jobs of colour and the rule for each?
  back: 'Categorical says which thing: a fixed order of distinct hues, one colour per entity, no ninth hue. Sequential says how much: one hue from light to dark. Diverging says above or below a midpoint: two hues with a neutral grey in the middle.'
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: What did the Fernhill palette check find?
  back: Two of its four hues have less than 3:1 contrast against the background, so charts using them must also carry direct labels or a table.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: Name four ways a chart choice goes wrong before it is drawn
  back: Picking the chart before the question, two y axes, bars or areas from a non-zero baseline, and stacking to compare.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: What is the difference between a Figure and an Axes?
  back: The Figure is the canvas you save to a file, and an Axes is one plot on it with its own coordinate system. A Figure holds one or more Axes.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01b-plotting-your-own-data
- front: Why prefer fig, ax = plt.subplots() to plt.plot?
  back: The explicit interface says which Axes you mean. plt.plot draws on an implicit current Axes, which gets confusing as soon as there are two plots.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01b-plotting-your-own-data
- front: What does the daily revenue line chart show that describe() hides?
  back: The weekly ripple, the trend removed by the 7-day mean, and a break in mid-March where NaN leaves a gap. The one-day August gap is too small to spot.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01b-plotting-your-own-data
- front: What is the whole line chart workflow on one Axes?
  back: Draw with ax.plot, label and annotate with methods on ax, then save and close the figure.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01b-plotting-your-own-data
- front: What does the pandas .plot accessor choose for you?
  back: The index becomes the x axis, each column becomes a series and column names become the legend. Pass ax= to place it on your own Axes.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01b-plotting-your-own-data
- front: Which habits make a bar chart readable?
  back: Start at zero, sort by value unless the categories have a natural order such as months, and use horizontal bars when labels are long.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01b-plotting-your-own-data
- front: How do you choose the number of histogram bins?
  back: Try several. Five bins give a plain staircase, 150 look like static and 25 show a main body with a long right tail.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01b-plotting-your-own-data
- front: What does the describe output show for daily revenue?
  back: Count 363, mean 507, std 132, min 311, quartiles 421, 477 and 566, max 1082. The numbers summarise the column and hide its shape.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01b-plotting-your-own-data
- front: What does seaborn need to do the grouping and statistics for you?
  back: 'A tidy table with one row per observation and one column per variable, so you can name the column for each role: x, y, colour, facet.'
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01b-plotting-your-own-data
- front: What does a box plot show that a bar of means hides?
  back: The median, the middle half of the values, whiskers and outliers for each group at once.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01b-plotting-your-own-data
- front: Which weekday has the highest median daily revenue and which the lowest?
  back: Saturday highest at 600 and Tuesday lowest at 420.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01b-plotting-your-own-data
- front: What does the fitted line on the scatter tell you and not tell you?
  back: That the two move together. It does not say one causes the other. The correlation is 0.933 here only because visitors was built from revenue.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01b-plotting-your-own-data
- front: What is the difference between axes-level and figure-level seaborn functions?
  back: Axes-level functions such as boxplot and scatterplot draw on an Axes you give them. Figure-level functions such as catplot, relplot and displot make their own Figure, take col= and row=, and return a FacetGrid.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01b-plotting-your-own-data
- front: What do the four quarter panels show at a glance?
  back: The weekly shape is the same in each quarter, and the whole shape rises through the year, because the panels share a y axis.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01b-plotting-your-own-data
- front: Which call draws a line, a bar, a histogram, a box and a scatter?
  back: ax.plot or series.plot() for a line, series.plot.barh() or sns.barplot for bars, ax.hist or sns.histplot, sns.boxplot, and sns.scatterplot or sns.regplot.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01b-plotting-your-own-data
- front: Why is jet a poor default colormap compared with viridis?
  back: A default colormap should have steadily rising luminance. Viridis rises monotonically from 0.18 to 0.88, while jet is not monotonic and its two ends measure 0.17 and 0.27, so in grayscale the high end looks like the low end.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01b-plotting-your-own-data
- front: Why does sns.regplot with positional columns fail on current seaborn?
  back: Since seaborn 0.12 data columns are passed by keyword, as x= and y=. factorplot became catplot, which draws a strip plot by default, so state kind=.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01b-plotting-your-own-data
- front: Which file format and which habits suit saving a figure?
  back: PNG for screens and notebooks, SVG or PDF for anything scaled or printed. Call tight_layout before saving, and plt.close(fig) when making figures in a loop.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01b-plotting-your-own-data
- front: Name four matplotlib habits that mislead, and the one-line fix for each
  back: Using plt. with several plots, unsorted x on a line, connecting categories with a line, and bars not starting at zero.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01b-plotting-your-own-data
- front: What are a Figure, an Axes and an artist in matplotlib?
  back: A Figure is the whole canvas and owns saving. An Axes is one plot with its own coordinate system. Everything you see inside an Axes is an artist, such as a Line2D, Text or Rectangle.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: Why prefer ax.plot to plt.plot for anything you will keep?
  back: plt.plot acts on a hidden current axes, which stops being safe once a figure has two panels. ax.plot names its target, and every helper function wants an ax argument anyway.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: What is wrong with the default matplotlib revenue chart?
  back: Markers repeat what the axis says, the grid and box are as dark as the data, the legend sits on the lines, the title only describes, and the green and blue crossing has no more weight than the rest.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: What are the steps of Knaflic's declutter sequence?
  back: Remove the border, drop or fade gridlines, remove data markers, clean up axis labels, label the data directly, and use colour with intent.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: Why does the decluttered style keep a horizontal grid but drop the spines?
  back: The grid survives only as a horizontal hairline behind the data, because it helps the reader read values and has no reason to be noticed. The spines go, except the baseline.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: What changed between the default chart and the decluttered one?
  back: 'Direct labels in ink colour replace the legend lookup, the grid and box are quiet, and the title states the finding: paid social overtook email in January 2025.'
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: Why is the title Paid social overtook email in January 2025 better than Revenue by channel?
  back: Revenue by channel labels the chart and repeats the axes. The finding says what it shows.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: By how much did the 90-day repeat rate fall in each Fernhill channel?
  back: Paid social fell 5.5 points, organic 7.6, email 9.6 and referral 8.2, so the fall is not just a change in which channels customers came from.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: What makes small multiples one chart rather than four?
  back: sharex=True and sharey=True, so the scale does not change between panels. It puts the value on position and scales to a dozen panels.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: What is the difference between figure-level and axes-level seaborn functions?
  back: Figure-level functions such as relplot, displot and catplot create their own figure and return a FacetGrid, so they can facet. Axes-level functions such as scatterplot, boxplot and heatmap draw into an ax you pass. If ax= raises an error, you called a figure-level function.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: What does one relplot call give you on the tips data?
  back: Two panels, lunch and dinner, with a shared scale, colour by smoker and one legend. Tip percentage stays near 15% in all four groups.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: What are the median tip shares for lunch and dinner by smoker?
  back: Dinner 0.156 for non-smokers and 0.149 for smokers. Lunch 0.153 for non-smokers and 0.154 for smokers. Tip percentage hardly differs.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: Why would a bar chart of mean order value hide the shape of Fernhill's orders?
  back: The mean sits above the median in every category and furniture's maximum is more than four times its mean, so means hide the right skew.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: Why is a box or a dot the right mark on a log scale?
  back: On a log scale a bar has no honest starting point, since its baseline would have to be 1 rather than 0 (Wilke).
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: Which colour scale suits a count, and which suits a change?
  back: A count or a rate needs a sequential scale. A change has a meaningful zero, so it needs a diverging scale with the neutral colour pinned to that zero.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: How did revenue change by channel and quarter from 2024 to 2025?
  back: Paid social rose 131, 123, 118 and 110 percent across Q1 to Q4. Email fell about 55 percent every quarter. Organic search and referral moved by only a few percent.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: Why does the heatmap need center=0, and what does fixing vmin and vmax do?
  back: Without center=0 seaborn sets the colour midpoint halfway between the extremes, so a +2% change could look like growth or decline. Symmetric vmin and vmax stop the colours changing meaning between refreshes.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: When should you pick PNG, SVG or PDF for a chart?
  back: PNG for slides, documents and charts with many marks. SVG for the web unless there are many marks. PDF for print or a paper. Vector files grow with the number of marks.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: Name four ways a matplotlib or seaborn chart goes wrong in code
  back: Mixing plt and ax, forgetting plt.close(fig), passing ax= to a figure-level seaborn function, and letting seaborn choose the category order.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: Name three static-chart pitfalls about colour, size and title
  back: Colour that follows rank, saving at the wrong size, and a title that only labels the chart.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: What is Shneiderman's visual information-seeking mantra?
  back: Overview first, zoom and filter, then details on demand (Shneiderman, 1996).
  lesson: data-analytics/05-visualisation-and-storytelling/notes/03-plotly-and-interactive
- front: Which medium suits an executive, an analyst, a returning manager and a member of the public?
  back: An executive gets a static chart with the answer in the title. An analyst gets an interactive chart or notebook. A manager who returns weekly gets a dashboard. A curious member of the public gets an interactive piece, overview first.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/03-plotly-and-interactive
- front: What are plotly's two levels?
  back: plotly.express takes a tidy DataFrame and names columns, like seaborn. plotly.graph_objects is the level underneath, where a figure is a list of traces and a layout.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/03-plotly-and-interactive
- front: Why is plotly's default hover text a problem?
  back: It shows raw field names in an order nobody chose, such as channel=Paid social and an empty label. Fixing that with a hovertemplate is most of the work of making a good one.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/03-plotly-and-interactive
- front: What is a plotly figure under the hood?
  back: A dictionary with data and layout keys. Python writes JSON, and plotly.js in the browser renders it.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/03-plotly-and-interactive
- front: What does include_plotlyjs change about an exported plotly chart?
  back: True puts the plotly.js library inside the HTML, about 4.7 MB, and it works offline forever. cdn loads the library from the network, about 10 KB, and needs a connection whenever it is opened.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/03-plotly-and-interactive
- front: Why export a static copy of an interactive chart?
  back: Hover is inaccessible on a phone, invisible in print and unreachable from a keyboard unless someone built for it. Anything that matters must be visible without it.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/03-plotly-and-interactive
- front: What limits a filter built from plotly traces?
  back: All the data ships inside the HTML. Three years of monthly data is fine, a filter across ten million rows is not, and when a choice has to trigger a new query you need a server.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/03-plotly-and-interactive
- front: How does Altair link two charts?
  back: A selection parameter is declared on one chart and used as another's scale domain or filter, with no event-handling code.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/03-plotly-and-interactive
- front: What are the data limits of plotly and Altair?
  back: Plotly ships every point to the browser, so the file grows with the rows. Altair embeds the data in its specification and raises MaxRowsError above 5,000 rows by default. Aggregate first or pass a URL.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/03-plotly-and-interactive
- front: Which tool fits quick exploration, an emailed interactive, linked brushing, publication figures, custom forms and live queries?
  back: plotly.express for notebook exploration, plotly with inline JS to email, Altair for linked brushing, matplotlib for publication figures, D3 for custom interaction and new chart forms, Streamlit or a BI tool for live queries.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/03-plotly-and-interactive
- front: Name four ways an interactive chart goes wrong
  back: Hiding the finding behind hover, default hover text, emailing a CDN file, and too much data in the page.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/03-plotly-and-interactive
- front: Name three interactive-chart pitfalls about touch, print and hovermode
  back: Relying on the mouse, forgetting the static version, and leaving plotly's hovermode at its default on many series.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/03-plotly-and-interactive
- front: Where do Observable Plot, Vega-Lite, Vega and D3 sit relative to each other?
  back: Observable Plot and Vega-Lite are high-level. Vega-Lite compiles to Vega. D3 is the base under both, and everything ends as SVG or Canvas in the browser.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/04-javascript-d3-vega-lite-observable-plot
- front: What is each of D3, Vega-Lite and Observable Plot?
  back: D3 is a toolkit for binding data to document elements, with scales, axes and shapes. Vega-Lite is the grammar from the first lecture written as JSON that compiles to Vega. Observable Plot is a concise JavaScript API over D3, the counterpart of seaborn.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/04-javascript-d3-vega-lite-observable-plot
- front: What are the parts of the D3 repeat-rate chart?
  back: Scales turn data into pixels and colours, axes are drawn from the scales and restyled, a data join makes one path per channel, direct labels, a legend and an event marker follow, and a hover layer of invisible targets finishes.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/04-javascript-d3-vega-lite-observable-plot
- front: What does Vega-Lite derive for you that D3 makes you write?
  back: You state data, mark and encodings. The compiler derives the scales, axes, grid, legend and correct ordering from the field types, giving 3 scales, 3 axes and 1 legend.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/04-javascript-d3-vega-lite-observable-plot
- front: Why is a Vega-Lite specification useful as plain JSON?
  back: It can be stored in a database, generated by a server or by an LLM, and validated against a schema.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/04-javascript-d3-vega-lite-observable-plot
- front: What is the price of working in a grammar like Vega-Lite?
  back: 'You can only say what the grammar can say. Placing text at a pixel offset such as dy: -150 is a hack that a resize would break, and dates need scale type utc or the first January tick moves.'
  lesson: data-analytics/05-visualisation-and-storytelling/notes/04-javascript-d3-vega-lite-observable-plot
- front: Why does the static Plot exhibit use direct labels instead of a legend?
  back: 'legend: true makes Plot return an HTML figure with swatches outside the SVG, and resvg only renders SVG. In a browser you would turn the legend on.'
  lesson: data-analytics/05-visualisation-and-storytelling/notes/04-javascript-d3-vega-lite-observable-plot
- front: How do D3, Vega-Lite and Observable Plot compare on code, strengths and weaknesses?
  back: D3 took 67 lines, you describe elements and geometry, it is good at anything and fights you on time. Vega-Lite took 33 lines, a JSON spec, good at portable specs and linked views, and fights you on pixel annotation. Plot took 24 lines, marks and options, good at fast exploration and fights you on bespoke interaction.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/04-javascript-d3-vega-lite-observable-plot
- front: In what order should an analyst reach for these tools?
  back: Altair or plotly from Python while you can, Vega-Lite when a product team needs to embed a chart defined by data, Plot when already in JavaScript and wanting speed, and D3 for a chart that needs custom design and is worth a few days.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/04-javascript-d3-vega-lite-observable-plot
- front: Name four ways a JavaScript chart goes wrong
  back: Reaching for D3 first, local time against UTC, forgetting xmlns on standalone SVG, and expecting layout from jsdom.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/04-javascript-d3-vega-lite-observable-plot
- front: Name three JavaScript chart pitfalls about files, colour and hit targets
  back: Importing modules from file URLs, colouring text like the series, and hit targets as thin as the mark.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/04-javascript-d3-vega-lite-observable-plot
- front: Where does a dashboard sit between exploratory and explanatory work?
  back: Exploratory is you finding out. Explanatory is telling a particular audience one particular thing. A dashboard sits between them as a tool for monitoring, and it contains no finding because it is built before the finding exists.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: How do a dashboard and an explanatory story differ?
  back: A dashboard answers 'what is my number' before the event, lives for months, and is returned to. A story answers 'what happened and what should we do' after the analysis, serves one decision, and is read once.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: Which three phrases in Few's definition carry the weight?
  back: '''Most important'', ''one screen'' and ''at a glance''. Between them they forbid most dashboards in production.'
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: What are the six items on the dashboard checklist?
  back: Name the decision, few metrics each with context, pair a growth metric with a health metric, layout in reading order, filters in one row above the charts, and state sources and refresh time.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: What does a tile that reads £5.96m need before it says anything?
  back: A comparison with last year, a target or a threshold. £5.96m says little. £5.96m, +6.5% on last year, says something.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: Why does revenue alone mislead, and what does a partner metric add?
  back: Buying more traffic raises revenue, so revenue alone will look fine. Revenue beside repeat rate shows what the growth cost. Any metric you can push by spending deserves a partner.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: How should layout, filters and sources be handled on a dashboard?
  back: Summary tiles top left, then trends, then detail, which is Shneiderman's overview first, filter, details on demand. Filters sit in one row above the charts and change everything below. State where the numbers come from and when they were refreshed.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: What happens between a user touching a filter and the page changing?
  back: The script reruns from the top, each widget call returns the current value, the data is filtered with it, and the tiles and chart are drawn from the filtered frame.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: Why does a Streamlit app need @st.cache_data on its loader?
  back: The script reruns on every click, and without the cache load() would run again each time. cache_data stores the return value keyed on the function's code and inputs.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: How does the Revenue tile get its comparison with last year?
  back: The metric call gets a delta string, the change on last year, and None when there is no previous year.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: How do you test a Streamlit app without a browser?
  back: AppTest runs the script, lets you set widget values and exposes what it would have drawn.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: What is Metabase and how does a parameter become a filter?
  back: Open source and self-hostable, with a paid cloud. Non-technical people use a point-and-click builder and analysts write SQL with parameters. A variable in double braces becomes a filter widget.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: What do double square brackets do in a Metabase query?
  back: They make a clause optional, so the query still runs when the filter is empty.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: What is Looker Studio, and why is its name confusing?
  back: Google's free hosted report builder, worked on a canvas in the browser and shared by link. It is not the same product as Looker, Google's governed BI platform with a modelling layer.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: How do Streamlit, Metabase and Looker Studio differ on who edits and where the logic lives?
  back: Streamlit is edited by Python developers with logic in Python in git. Metabase is for analysts plus self-serve users with logic in SQL and models in the tool. Looker Studio is for anyone with a browser with logic in calculated fields in the tool.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: When do you choose a BI tool over Streamlit?
  back: When non-developers need to edit reports and the content is standard reporting. Streamlit suits bespoke tools maintained by people who write Python.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: What are Knaflic's who, what and how?
  back: Who is the specific audience and decision maker. What is what they need to know or do. How is the data that makes the point.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: What are the 3-minute story and the Big Idea?
  back: The 3-minute story asks whether you could explain the point out loud if your slot shrank to three minutes. The Big Idea, from Duarte's Resonate, is one complete sentence stating your point of view and what is at stake.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: How much of the fall is mix, and how much is within channels?
  back: The 2024 overall rate was 37.5% and 2025 was 26.2%. The 2025 mix at 2024 channel rates would be 33.3%, so mix is -4.3 points and within-channel is -7.1 points, together the headline drop of 11.3 points.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: What did the sizing find, and what is the break-even margin?
  back: New customers in 2025 were 61,718 and 4,373 repeat customers were lost, worth £192,419 of margin. Email revenue fell from £1,603,582 to £717,268, worth £354,526 of margin. Against £120,000 saved, that is 4.6 pounds lost per pound saved, with break-even margin at 8.8%.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: Why is the sizing not proof that the email cut caused the fall?
  back: A before-and-after with one change date also picks up anything else that changed in January. Fernhill's data is synthetic and built with this effect. That is why the recommendation includes a holdout.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: What did the explanatory chart remove, and what did it add?
  back: It keeps one series instead of four, replaces the legend with direct labels, names the event in an annotation and shows the two values to remember in bold ink.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: What is Knaflic's sequence for turning an exploratory chart into an explanatory one?
  back: Identify the clutter, remove it, then use preattentive attributes such as weight and position to direct attention where you want it.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: Why are bars honest on the decision chart, and what carries the argument?
  back: The three items share a unit and a zero. The grey bar is the saving and the blue bars are the costs, so the colour carries the argument. There is no axis, because each bar is directly labelled.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: What are Fernhill's setup, conflict and resolution?
  back: 'Setup: email cut from £14k to £4k in January 2025, acquisition raised, revenue up 6.5%. Conflict: repeat buying fell from 38% to 26%, about 4 points mix and 7 within channels. Resolution: restore about £10k a month to email for two quarters, hold out 10% of customers, hold paid social flat.'
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: What does the Fernhill recommendation leave out, and why?
  back: It does not say cut paid social. Paid-social spend rose from £312k to £576k, and nothing here shows whether that money earned its return. Claiming it would be over-reach.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: What are horizontal and vertical logic?
  back: 'Horizontal logic: read only the slide titles in order and they should tell the whole story without the charts. Vertical logic: everything on a slide supports its own title.'
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: What are Cairo's five qualities of a good visualisation?
  back: Truthful, functional, beautiful, insightful and enlightening. Truthful comes first.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: Name five dashboard pitfalls, from deliverable to caching
  back: A dashboard as the deliverable for a finding, a growth metric alone, tiles with no comparison, red and green as the only signal, and heavy work outside the cache in Streamlit.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: Name four pitfalls of tool choice, causal claims, the ask and precision
  back: Building Streamlit for people who will want to edit it, a before-and-after presented as causal, burying the ask, and false precision in a sizing.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: What one rule sums up this lecture?
  back: A dashboard answers 'what is my number' and delivers no finding, so pair a metric you can push by spending with one that shows the side effect, and write the sentence and send it.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: What are the three layers of a dashboard and when does each run?
  back: Analysis cleans, models and scores on a schedule. Application decides who may ask and what they get, on every request. Presentation draws and reacts to clicks, in the browser.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: Why is "Plotly or Dash?" not a real choice?
  back: Plotly draws charts and has no notion of a user, a login or a filter. Dash is an application framework that draws with Plotly, so the two sit on different layers.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: What does the batch job in segments.py hand to the other two layers?
  back: 'One Parquet table with a row per customer: id, email, region, segment name and two plot coordinates. The email column is there on purpose, because real tables have one.'
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: Which JavaScript library draws for Plotly, Altair, Bokeh, Folium and HoloViews?
  back: plotly.js, Vega-Lite with Vega and vega-embed, BokehJS, Leaflet, and Bokeh, Matplotlib or Plotly for HoloViews and hvPlot.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: What is the consequence of each library's drawing route for Plotly, Altair and Folium?
  back: Every point in a Plotly figure travels to the browser. Altair stops at 5,000 rows by default, and VegaFusion can move some work to a server-side runtime. Folium writes each marker into the page.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: What does each route give you and what does it cost you?
  back: A BI tool gives all three layers in one product, in exchange for working its way. A Python app gives application and presentation in one Python file, and the analyst keeps ownership. A full stack gives complete control and costs a second language and a build.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: What limit does each BI tool in the table impose?
  back: Power BI DirectQuery fails above 1,000,000 rows with a 4-minute timeout. Tableau Cloud suggests 25 GB for a workbook, with a 120-minute refresh limit. Metabase's table view shows at most 2,000 rows, or 10,000 aggregated.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: What did each vendor's page say about price, and what is the caveat?
  back: Power BI Pro $14 and Premium Per User $24 a user a month, on a page that says its prices are for marketing purposes only. Metabase is free as Open Source under AGPL, Starter $100 a month with 5 users, Pro $575 with 10. Data Studio has a no-cost tier and Pro at $9. Tableau's price is omitted. Check before quoting.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: Where does Power BI row-level security stop, and what does embedding need?
  back: RLS only restricts users with Viewer permissions, so workspace editors see everything. Embedding for your customers says app users need no licence, but production embedding needs a capacity.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: What happens in Streamlit, Dash, Shiny, Panel and Bokeh when a control changes?
  back: Streamlit reruns the script from the top. Dash runs a callback. Shiny reruns the reactive functions that read the control. Panel reruns functions bound to it. A Bokeh server runs Python callbacks and keeps data in sync.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: What should a Dash callback do each time a dropdown changes?
  back: It runs on the server, takes the region, reads the labels without refitting, and returns a new figure and summary.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: Which route does each situation in the table start with?
  back: Recurring warehouse reporting starts with a BI tool. An internal tool around a model starts with Streamlit, Dash, Shiny or Panel. Specialists exploring millions of points start with Panel or HoloViews with datashader. A customer-facing feature starts with FastAPI, React and TypeScript. One finding sent once is a self-contained HTML file.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: Why is changing route later less costly than it sounds?
  back: The Dash app and the API call the same summarise and bin_map functions, so changing route leaves the numbers alone.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: What four ideas let you review the full-stack route without writing React?
  back: The JSON contract is the real interface. A component is a function that returns markup. A fetch is a request and an effect runs it. TypeScript types describe the API's answer and do not check it at run time.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: What does the current flag in the useEffect do?
  back: Two quick filter changes can answer out of order, so an answer to an old filter is ignored. The cleanup function sets current to false before the next run.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: What do Promise.all, setSummary and the dependency list do?
  back: Promise.all sends both requests and waits for both, like asyncio.gather. setSummary and setBins store the answers and React redraws. The list [region] tells React when to rerun the effect.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: When do you reach for react-plotly.js, ECharts, Recharts and D3?
  back: react-plotly.js when you already have Plotly figures. ECharts for many marks, with canvas above about 1,000 items. Recharts for ordinary charts in modest numbers. D3 for a form no library offers, using its scales and letting React draw.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: What is the symptom of choosing the stack by what you know?
  back: A React project for six internal readers, or a Streamlit app that outside customers log in to. Start from the situation table.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: Why is returning the whole table from an endpoint a fault?
  back: It returns every row, 50,000 customers with their emails, to anyone who asks, and no key is needed.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: What are the four faults and the OWASP API heading for each?
  back: No authentication (API2, nearest heading), no per-object permission (API1), every column exposed (API3), and no limit (API4).
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: What do response_model, Depends and Query(le=500) each do?
  back: response_model limits the output to the fields you named. Depends runs the key check before the function. Query with le=500 is a cap we chose, which enforces the maximum.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: What do HTTP 401, 403 and 422 each mean for a FastAPI endpoint?
  back: 401 means no valid key. 403 means a valid key without the right, so the analyst cannot list customers. 422 means FastAPI rejected a 50,000 limit over the cap before the function ran.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: Why use keyset pagination rather than offset for a large export?
  back: Offset still computes the skipped rows inside the server. Keyset filters on the last id seen, but you cannot jump to an arbitrary page, and it needs a unique sort order.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: How do the five requests compare in size and time?
  back: The draft sends 50,000 rows, 11,235.3 KB (1,418.7 gzipped) in 533.8 ms. A segment summary sends 4 rows, 0.5 KB in 3.8 ms. The map is 442 rows, 28.8 KB in 5.3 ms. A page of 100 customers is 8.5 KB in 2.2 ms.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: How much does dropping columns or listing by column save compared with a summary?
  back: Keeping three columns still sends 2,496 KB (330 KB gzipped). Listing values by column rather than by row is 1,520 KB (244 KB gzipped). A summary is 0.5 KB.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: Why does the map endpoint drop small cells, and what does it not guarantee?
  back: So no mark on the page is one person. It reduces the risk of picking out one person and does not remove it, because comparing filtered views can still reveal small counts.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: Which cheap additions reduce payload and reuse, and what must be marked private?
  back: GZipMiddleware compresses answers, with a default minimum size of 500 bytes. An ETag lets a browser reuse an answer until the batch job writes a new table. Per-person answers must be marked private in Cache-Control.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: Is refit speed the objection to refitting on a filter?
  back: No. Labels change meaning when you refit on a filter, even when the fit is fast. One k-means fit took 49 ms per request, against 4.7 ms to read Parquet and aggregate.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: What happens to cluster ids and grouping when you refit k-means with a new seed?
  back: Only 49.1% of customers keep the same cluster id, but the ARI is 0.994, so the grouping is nearly identical once ids are ignored.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: How many customers change group when you refit on one region and on spend above the median?
  back: A new seed moves 0.0% and 0.2%. One region moves 0.0% and 2.6%. Spend above the median moves 14.8% on well-separated data and 25.3% on overlapping data.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: What is the rule for labels, and why not choose k inside a request?
  back: A job writes labels, names and the model version to a table and the app only reads. Choosing k from 2 to 8 with a silhouette score on 10,000 rows took 3.6 s, which nobody should do in a request.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: Which bundles are largest and smallest, and what does importing less save?
  back: plotly.js-dist-min is 1,449 KB gzipped, the basic Plotly bundle 396 KB, ECharts everything 375 KB and scatter-only 172 KB, d3 everything 94 KB and its scale, axis and selection only 12 KB.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: How do the Dash and React pages compare on first load?
  back: Dash fetched 21 files totalling 6,716 KB, about 1,901 KB gzipped. React fetched 5 files totalling 610 KB, about 177 KB gzipped. The tenfold gap matters on phones and hardly at all on office broadband.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: At which point counts does scattergl beat SVG scatter in the measurements?
  back: SVG is quicker at 1,000 points (27 against 42 ms). WebGL wins from 10,000 (102 against 46 ms), and at 50,000 it is 55 ms against 476 ms. WebGL ran 200,000 in 76 ms and 400,000 in 111 ms.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: What limits does Plotly's performance page set on WebGL?
  back: Most browsers allow between 8 and 16 WebGL contexts per page, which generally means 4 to 8 figures, and past that some figures will not render. Plotly Express switches to WebGL above 1,000 rows. The ceiling for WebGL traces is around a million points.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: How long does Datashader take on five million points, first and second time?
  back: 371 ms the first time, which includes compiling, and 21 ms the second, producing an 800 by 500 image.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: What does the Datashader image weigh against a Plotly figure, and what is the catch?
  back: The image shaded by segment is 255 KB, against 362 KB gzipped for a Plotly figure of only 50,000 points. It needs a running Python process to show more detail when zooming.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: How big is the Folium page for ten regions, and for 5,000 markers?
  back: 10 KB for ten region circles. The same page with 5,000 individual circle markers was 2,435 KB, because each marker is written into the HTML.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: What three things go wrong on a customer map?
  back: A region's size misleads on a choropleth. Tiles are someone else's server with no SLA. A home address is personal data, so a map of customers' homes is a privacy decision.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: Why does filtering out a segment repaint the others under default colours?
  back: Default colour follows order of appearance, so removing one segment shifts the colours of every other one. Fix the mapping by name with color_discrete_map.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: What are the four WCAG 2.2 checks applied to a chart page?
  back: Colour is not alone (1.4.1), contrast (1.4.3 and 1.4.11), a table view (1.1.1), and keyboard and hover (2.1.1 and 1.4.13).
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: Which of our colours fall short of 3:1 contrast, and what is the escape?
  back: Aqua at 2.74:1 and yellow at 2.11:1 fall short of 3:1 on the near-white surface. WCAG accepts the information being available in another form, so our table meets the check.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: How do the Dash and FastAPI-with-React builds compare?
  back: Dash is 42 lines of Python and about 1,901 KB first load, with no login in our demo. FastAPI and React is 147 lines of Python and 100 of TypeScript plus a Node toolchain, about 177 KB, with a key check in the demo.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: Which route should Fernhill take, and when would React earn its code?
  back: A CRM team of a few people, inside the company, with labels that change only when someone approves a refit, belongs on the Python app row. The 42-line Dash file is enough behind the company's login proxy. React earns its extra code when these views go into the customer-facing product.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: Name three dashboard data-path pitfalls that pass a demo
  back: A list endpoint that returns the table, a secret or cap only in the front end, and refitting on a filter or keying on a cluster number.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: What does the grammar of graphics give you that chart types do not?
  back: A chart is a composition of data, marks, encodings, statistics, scales, coordinates and facets, so you can vary one decision at a time and describe charts no menu names.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: Which encodings are read most accurately?
  back: Position on a common scale, then position on non-aligned scales, then length, angle and slope, then area, then volume, then shading and saturation (Cleveland and McGill, 1984).
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: Why avoid dual y axes?
  back: The relative placement of two independent scales is arbitrary, so any crossing or correlation it suggests is the author's choice. Use aligned panels or index both series to one base.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: Must every y axis start at zero?
  back: Bars and areas must, because length and area encode the value. Lines and dots encode by position and may zoom if the axis is plain about it.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: Is a pie chart ever right?
  back: Yes, for a small number of parts where the message is a simple fraction of a whole. For comparing the parts, sorted bars are more accurate.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: Exploratory versus explanatory?
  back: Exploratory charts are many and help you find out; explanatory charts are few and tell someone else one thing.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: Why prefer `fig, ax = plt.subplots()` to `plt.plot`?
  back: The explicit interface says which Axes you mean, while `plt.` draws on an implicit "current" one, which gets confusing with several plots.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01b-plotting-your-own-data
- front: Axes-level or figure-level seaborn?
  back: Axes-level (`boxplot`) draws on an Axes you pass. Figure-level (`catplot`) makes its own Figure so it can facet with `col=` and `row=`, and returns a `FacetGrid`.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01b-plotting-your-own-data
- front: Why does seaborn want tidy data?
  back: You map columns to roles such as x, hue and col, so each variable needs its own column and each observation its own row.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01b-plotting-your-own-data
- front: Which chart for a change over time, a comparison, a distribution, or a relationship?
  back: Line, sorted bars, histogram or box, and scatter.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01b-plotting-your-own-data
- front: Why must bars start at zero when lines need not?
  back: A bar encodes the value by its length, so cutting the axis misstates ratios. A line encodes change by position.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01b-plotting-your-own-data
- front: What is wrong with a dual-axis chart?
  back: The two scales are arbitrary, so any apparent relationship between the lines depends on how they were chosen. Use two panels or index both to a common base.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01b-plotting-your-own-data
- front: What does a box plot show?
  back: The median, the middle 50% of the data, whiskers, and outliers. It compares spread as well as centre across groups.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01b-plotting-your-own-data
- front: How do you handle overplotting?
  back: Lower the opacity, shrink the marks, use `hexbin` or a 2D histogram, or sample.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01b-plotting-your-own-data
- front: Why prefer `ax.plot` over `plt.plot`?
  back: It names its target, so it stays correct with several panels and inside functions, rather than relying on a hidden current axes.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: How do you apply a consistent style across charts?
  back: Set `rcParams` once, in a shared module or a style file, and use a fixed colour mapping per entity.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: Figure-level versus axes-level seaborn?
  back: Figure-level (`relplot`, `displot`, `catplot`) builds its own figure with facets and returns a `FacetGrid`. Axes-level (`scatterplot`, `boxplot`) draws into an `ax` you give it.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: When would you use small multiples?
  back: When several groups would overlap on one chart and the comparison is of shape over a shared scale. They trade a little comparison accuracy for far less clutter.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: Sequential or diverging for a heatmap?
  back: Sequential for magnitude from low to high. Diverging for a change or anything with a meaningful midpoint, with the neutral colour pinned to it.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: PNG or SVG?
  back: PNG for fixed-size output and for many marks. SVG or PDF for sharp scaling when marks are few.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: What is Shneiderman's mantra?
  back: Overview first, zoom and filter, then details on demand.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/03-plotly-and-interactive
- front: What is `include_plotlyjs` for?
  back: It controls whether the library goes inside the HTML (about 4.7 MB here, works offline) or loads from a CDN (about 10 KB, needs network).
  lesson: data-analytics/05-visualisation-and-storytelling/notes/03-plotly-and-interactive
- front: Why can plotly filter without a server, and what is the limit?
  back: The data ships in the page and the control toggles trace visibility, so it is limited to what fits comfortably in a browser.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/03-plotly-and-interactive
- front: What accessibility issues come with hover?
  back: It has no touch equivalent, may be unreachable by keyboard and cannot be printed. Anything essential must be visible without it, and a table should be available.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/03-plotly-and-interactive
- front: Is D3 a charting library?
  back: Not really. It is a toolkit for binding data to the DOM, with scales, shapes, axes and layouts. You assemble the chart yourself.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/04-javascript-d3-vega-lite-observable-plot
- front: What is the data join?
  back: Matching a list of data to a set of elements, creating, updating and removing elements so the page reflects the data.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/04-javascript-d3-vega-lite-observable-plot
- front: What does Vega-Lite compile to?
  back: A full Vega specification with the derived scales, axes and legends, which Vega then renders to SVG or Canvas.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/04-javascript-d3-vega-lite-observable-plot
- front: How does Altair relate to Vega-Lite?
  back: Altair is a Python API that generates Vega-Lite JSON. The browser or `vl-convert` does the rendering.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/04-javascript-d3-vega-lite-observable-plot
- front: How can you test a chart without a browser?
  back: Render in jsdom and assert on the DOM, including firing events. It has no layout, so anything that measures text needs a real browser.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/04-javascript-d3-vega-lite-observable-plot
- front: What is the most common JavaScript date bug in charts?
  back: Parsing dates as UTC and formatting them in local time, so that ticks and labels move by a day or a month.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/04-javascript-d3-vega-lite-observable-plot
- front: What is the difference between exploratory and explanatory analysis?
  back: Exploratory is you finding out what is interesting. Explanatory is telling a specific audience a specific thing you already found.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: What makes a metric on a dashboard useful?
  back: It connects to a decision and has a comparison, such as prior period, target or threshold, and ideally a partner metric that exposes side effects.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: When would you choose Metabase or Looker Studio over Streamlit?
  back: When non-developers need to edit reports and the content is standard reporting. Streamlit suits bespoke tools maintained by people who write Python.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: What is the Big Idea?
  back: One complete sentence that gives your point of view and what is at stake, from Duarte via Knaflic.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: What is horizontal logic?
  back: Reading the slide titles alone in order tells the whole story.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: How do you decompose a change in an overall rate?
  back: Apply the old segment rates to the new mix to get the mix effect. The remainder is the within-segment effect.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: A rate fell after a budget cut. Have you shown the cut caused it?
  back: No. A before-and-after picks up anything else that changed. Propose a holdout, and say what would change your mind.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: What are the three layers of a dashboard?
  back: Analysis produces results on a schedule, the application answers requests and enforces access, and presentation draws in the browser. Chart libraries are presentation only.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: What is the difference between Plotly and Dash?
  back: Plotly draws charts. Dash is an application framework that runs Python callbacks on a server and uses Plotly to draw.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: How do you choose between a BI tool, a Python app and a full stack?
  back: By audience, interaction, data volume and who maintains it. Take the lightest that fits, and move up only for a named requirement, such as outside users with per-person data.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: What is wrong with an endpoint that returns the customer table?
  back: No authentication, no per-object permission, every property exposed, and no limit. On our setup it also took about 534 ms and 11 MB, against 4 ms and 0.5 KB for a summary.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: Why not refit the model when a user filters?
  back: 'Speed is often fine. The issue is meaning: ids are arbitrary, and in our test a filter on spend moved 15 to 25% of customers. Persist labels from a job and read them.'
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: Offset or keyset pagination?
  back: 'Keyset for large exports: it filters on the last id seen, so skipped rows are not computed, but you cannot jump to an arbitrary page. It needs a unique sort order.'
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
- front: When do you use WebGL, and when datashader?
  back: WebGL from around 10,000 points, on our measurements, up to around a million by Plotly's documentation, with a limit on figures per page. Datashader beyond that, or when the whole set should stay on a server, accepting a running process and no point-level hover.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06b-dashboard-data-path-points-colour-and-worked-example
---
