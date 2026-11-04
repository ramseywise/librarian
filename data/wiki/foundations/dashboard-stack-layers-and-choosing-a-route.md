---
title: Dashboard Stack Layers and Choosing a Route
tags: [foundations, comparison]
summary: Every dashboard has analysis, application and presentation layers; chart libraries are presentation only, and the route (BI tool, Python app, full stack) is chosen by audience, data and maintainer.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--05-visualisation-and-storytelling--notes--06-dashboard-stacks-from-python-to-frontend.md
---

# Dashboard Stack Layers and Choosing a Route

## Three layers

- **Analysis**: cleans, models, scores; runs on a schedule; its output table is the contract.
- **Application**: answers requests, decides who may see what and how much to send; runs on every filter change.
- **Presentation**: draws marks and turns clicks into requests; in the browser, JavaScript whoever wrote it.

Plotly, Altair and D3 are presentation only. Streamlit, Dash, Panel and Shiny are application frameworks that use a chart library to draw, so "Plotly or Dash?" is not a real choice (Dash draws with Plotly). FastAPI is application with no presentation. A BI tool packages all three. Python chart libraries write a description (Plotly JSON, a Vega-Lite spec) that a JavaScript library draws, so the library's limits apply whichever language called it (Altair stops at 5,000 rows by default; Plotly ships every point to the browser; Folium writes each marker into the page).

## Three routes

**BI tool**: all three layers in one product; ask who pays per viewer and which limits apply. Examples read in the source: DirectQuery in Power BI fails if a query returns more than 1,000,000 rows; Metabase's table view shows at most 2,000 rows (10,000 for aggregated queries); row and column security is on higher Metabase tiers; Power BI row-level security restricts only Viewer-permission users, so workspace editors see everything. Vendor prices and limits change; check before quoting.

**Python app**: application and presentation in one Python file, owned by analysts. They differ in what reruns on a change: Streamlit reruns the script (fragments rerun part; `cache_data` is shared across users, so never cache per-person data); Dash runs callbacks (workers do not share memory; open-source Dash has no built-in authentication); Shiny reruns reactive functions (Shinylive ships code and data to the browser, so nothing is secret); Panel binds functions to controls; a Bokeh server makes a new document per session, so each viewer costs memory.

**Full stack**: a Python API plus a JavaScript front end gives full control over login, layout and behaviour for a second language and a build. Four ideas suffice to review it:
1. The JSON contract is the real interface; FastAPI publishes it as an OpenAPI document.
2. A component is a function returning markup, declared for the current data.
3. A fetch inside an effect re-runs when its inputs change; ignore answers to superseded requests (a `current` flag with cleanup), because responses can arrive out of order and a slow answer can overwrite a newer one.
4. TypeScript types describe the API's answer but do not check it at run time; if the API renames a column the build passes and the page breaks. Test real responses or validate at the boundary ([[Runtime Validation with Zod]], [[TypeScript for Python Developers]]).

## Choosing by situation

| Situation | Start with |
|---|---|
| Recurring reporting on warehouse tables, many non-technical viewers | BI tool |
| Internal tool around model output for a nameable team | Streamlit, Dash, Shiny or Panel |
| Specialists exploring millions of points | Panel or HoloViews with datashader |
| Feature in a product customers log in to | FastAPI with React and TypeScript |
| One finding sent once | Self-contained HTML ([[Interactive Charts and When They Pay]]) |

Take the first row that fits and move heavier only for a named requirement. A team that built the analysis can maintain a Python app; a React front end needs someone who keeps its build working after the author leaves, unless front-end engineers already exist. In the worked case the same segments page was 42 lines of Python in Dash versus 147 lines of Python, 100 of TypeScript and a Node toolchain; first load was about 1,901 KB gzipped versus about 177 KB. Keeping the layers apart (both routes call the same helper functions) makes the route reversible.

## See Also
- [[Dashboard API Exposure and Payload Cost]] — extends
- [[Precomputed Labels, Not Refits on Filter]] — extends
- [[Rendering Many Points: WebGL, Datashader and Bundle Weight]] — extends
- [[Dashboard Design: Paired Metrics and Context]] — prerequisite-for
- [[JavaScript Charting Ladder]] — related
