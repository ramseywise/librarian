---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- data-analytics/05-visualisation-and-storytelling/slides/deck.yaml
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
- front: What does Anscombe's quartet show?
  back: Four datasets share means, variance, correlation and fitted line and look nothing alike. Summaries alone can hide curvature, outliers and leverage.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: Exploratory versus explanatory?
  back: Exploratory charts are many and help you find out; explanatory charts are few and tell someone else one thing.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: What is the difference between a Figure and an Axes?
  back: A Figure is the canvas and owns saving. An Axes is one plot with its own coordinates, and a Figure can hold many.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
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
- front: What is a plotly figure under the hood?
  back: A JSON-serialisable structure of `data` traces and a `layout`, rendered by plotly.js in the browser.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/03-plotly-and-interactive
- front: What is `include_plotlyjs` for?
  back: It controls whether the library goes inside the HTML (about 4.7 MB here, works offline) or loads from a CDN (about 10 KB, needs network).
  lesson: data-analytics/05-visualisation-and-storytelling/notes/03-plotly-and-interactive
- front: Why can plotly filter without a server, and what is the limit?
  back: The data ships in the page and the control toggles trace visibility, so it is limited to what fits comfortably in a browser.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/03-plotly-and-interactive
- front: How does Altair link two charts?
  back: A selection parameter is declared on one chart and used as another's scale domain or filter, with no event-handling code.
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
- front: What are Knaflic's who, what and how?
  back: Who is the specific audience and decision maker. What is what they need to know or do. How is the data that makes the point.
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
