---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- data-analytics/05-visualisation-and-storytelling/slides/deck.yaml
cards:
- front: What does Anscombe's quartet show about summary statistics?
  back: Plot before you summarise, because identical statistics can hide completely different data.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: What are the independent parts of a chart in the grammar of graphics?
  back: The grammar treats a chart as data, encodings, scales, marks and facets, so you can change one part at a time.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: In Altair, what do you change to compare a line with bars on the same encodings?
  back: In a grammar-based library the mark is one independent choice, so comparing forms costs a single word.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: How do you choose a chart form?
  back: Name the question first, then choose the form whose encoding answers it most accurately.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: How do dual-axis charts and truncated bars each mislead, and what is the fix?
  back: Dual axes and truncated bars both let a scale choice manufacture the message, so use panels and zero baselines.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/01-grammar-and-chart-choice
- front: What is wrong with a default matplotlib chart even though the data is right?
  back: Default styling draws the data correctly but leaves every decision about emphasis to the reader.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: How do you decide what stays on a chart, and keep those choices consistent?
  back: Every element must earn its place, and one shared style module keeps those choices from drifting.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: What did small multiples reveal about Fernhill's repeat rate that a single chart hid?
  back: Small multiples showed Fernhill's repeat rate dropping in every channel at the same moment, which four tangled lines on one chart hid.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: How do you apply one consistent style across all your matplotlib charts?
  back: Set matplotlib's rcParams once in a shared module and draw through ax, so styling stays consistent across charts.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: How do seaborn and matplotlib relate?
  back: Use seaborn for statistical views from tidy data, then adjust the matplotlib objects it returns.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/02-matplotlib-and-seaborn
- front: When is an interactive chart the wrong choice?
  back: If you can state the finding, state it. Use interaction for readers with their own questions.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/03-plotly-and-interactive
- front: What is a plotly figure under the hood, and why does custom_data matter?
  back: Plotly figures are JSON rendered by plotly.js, so any tooltip field must ship in the page and be templated.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/03-plotly-and-interactive
- front: How should you ship a plotly chart for email, a hosted page and print?
  back: Ship inline HTML for email, CDN HTML for hosted pages, and always a static copy because hover cannot print.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/03-plotly-and-interactive
- front: When do you use plotly and when Altair?
  back: Use plotly for one rich chart and Altair for linked views, since its selections are part of the grammar.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/03-plotly-and-interactive
- front: What is the relationship between Altair and Vega-Lite?
  back: D3, Vega-Lite and Plot sit at different levels of abstraction, and Altair is a Python route to Vega-Lite.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/04-javascript-d3-vega-lite-observable-plot
- front: What does the D3 data join do?
  back: The D3 data join makes page elements match a list of data, creating and removing them as the data changes.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/04-javascript-d3-vega-lite-observable-plot
- front: Why does the D3 chart draw invisible circles?
  back: With D3 every element is your code, including large invisible hover targets that thin lines cannot provide.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/04-javascript-d3-vega-lite-observable-plot
- front: When would you pick D3 over Vega-Lite?
  back: Use Altair or plotly while you can, Vega-Lite for embedded specs, Plot for speed, and D3 when design justifies it.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/04-javascript-d3-vega-lite-observable-plot
- front: Why pair a growth metric with a health metric?
  back: Pair a growth metric with a health metric, because anything you can raise by spending looks fine alone.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: How does Streamlit's execution model work?
  back: Streamlit reruns the whole script on every widget change, so widgets are plain values and caching is essential.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: When would you choose a BI tool over Streamlit?
  back: Pick the dashboard tool by who maintains it, because a Streamlit app owned by non-coders becomes a ticket queue.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: What makes a chart explanatory rather than exploratory?
  back: An explanatory chart keeps one series, marks the event, and states the finding in the title.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: Why report the break-even as well as the estimate?
  back: Report the break-even as well as the estimate, so the reader can see the decision survives its assumptions.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
- front: What are the three layers of a dashboard, and which one does Plotly cover?
  back: A dashboard has analysis, application and presentation layers. Plotly covers only presentation, so "Plotly or Dash?" is not a real choice.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: What does px.scatter actually send to the browser?
  back: px.scatter sends a JSON figure with every point, and plotly.js draws it, so the library's limits apply even from Python.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: Which stack fits an internal tool for a named team, and which fits a feature in your product?
  back: An internal tool for a named team starts as a Python app such as Streamlit or Dash, and a product feature as FastAPI and React. Go heavier only for a named requirement.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: How can you review a React front end without knowing React?
  back: You can review a React front end by checking its contract, its fetches, and what its types do not guarantee.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: Where do permissions, field lists and row caps belong, and why?
  back: Permissions, field lists and row caps belong on the server, where a caller cannot go around them.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: Which is heavier, 50,000 customers as JSON or all of plotly.js, and what does that imply?
  back: All 50,000 customers gzip to 1,419 KB, about the same as all of plotly.js at 1,449 KB, so fix the data before choosing a library.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: Why not refit the clustering when a user filters?
  back: The objection to refitting is meaning rather than speed, so publish one table and let the filter select rows from it.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: When do you reach for WebGL, and when for datashader?
  back: Use WebGL from about 10,000 points, measured on one M4 Pro, and datashader past about a million or to keep the data on a server. Often you need neither.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: How should you colour customer segments in Plotly?
  back: Map each segment name to a fixed colour and a second encoding, so nothing depends on order or on colour alone.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: Why does Fernhill's CRM dashboard belong on the Python app route?
  back: A few internal CRM users make this a Python app job. The React version earns its code when the views reach customers.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/06-dashboard-stacks-from-python-to-frontend
- front: What are the rules of thumb for visualisation and storytelling?
  back: Name the question, show it honestly, remove the clutter, and state the decision you want in one sentence.
  lesson: data-analytics/05-visualisation-and-storytelling/notes/05-dashboards-and-storytelling
---
