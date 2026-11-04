---
title: Interactive Charts and When They Pay
tags: [foundations, pattern]
summary: Interaction moves work from author to reader; use it for exploration and monitoring, state the finding yourself for decisions, and know the shipping costs of plotly and Altair.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--05-visualisation-and-storytelling--notes--03-plotly-and-interactive.md
---

# Interactive Charts and When They Pay

Hover, zoom and filters let one view cover more data than a static one, but they spend the reader's time and attention, and anything hidden behind a hover may go unseen. The design brief: overview first, zoom and filter, then details on demand. Each step suggests an interaction.

| Reader | Question | Medium |
|---|---|---|
| Executive reading a memo | What happened, what should we do? | Static chart, answer in the title |
| Analyst checking work | Does this hold in my segment? | Interactive chart or notebook |
| Manager returning weekly | What is my number, is it okay? | [[Dashboard Design: Paired Metrics and Context]] |
| Curious public | Where am I in this? | Interactive piece, overview first |

If you can state the finding, state it. Hover is an exploration tool.

## Plotly mechanics

- A figure is a JSON-serialisable dict of `data` traces and a `layout`. Python draws nothing; plotly.js renders in the browser, and hover templates are format strings interpreted by JavaScript.
- Hover can show only what the browser holds, so extra tooltip columns must ship via `custom_data`. Default hover text leaks raw column names in an order nobody chose; write a template.
- `add_shape` with `yref="paper"` spans the plot height whatever the data does.
- **Export**: `include_plotlyjs=True` gave a 4,713 KB self-contained file that works offline; `"cdn"` gave 10 KB but needs a network. Email the inline one; host the CDN one (a page of twenty charts loads the library once). Static export (Kaleido) drives headless Chrome and fails on a machine without a browser. Always export a static copy: hover is absent on phones and in print.
- **Server-free filter**: a dropdown can flip trace `visible` flags, since all data ships in the HTML. This limits it to what fits comfortably in a browser; a filter that must trigger a new query needs a server (see [[Dashboard Stack Layers and Choosing a Route]]).
- A bare line chart of 144 rows was about 14 KB and a scatter of 4,000 rows about 90 KB, because every point travels in the page. Aggregate first, use `go.Scattergl` for large scatters.
- Choose `hovermode` deliberately: unified hover compares series at one x with four lines but covers the chart with forty.

## Linked views with Altair

Vega-Lite makes interaction part of the specification: a selection is a declared parameter that other parts use as a scale domain or filter. Brushing an overview panel to zoom a detail panel needs one line, `scale=alt.Scale(domain=brush)`, and no event handlers; the spec was 6,749 bytes. Altair embeds the data and raises `MaxRowsError` above 5,000 rows by default; aggregate or pass a URL.

## Pitfalls

- Hiding the finding behind hover.
- Emailing a CDN file (blank offline or behind a strict firewall).
- Relying on the mouse: touch behaves differently; keep a table view ([[Chart Colour Scales and Accessibility]]).

## See Also
- [[JavaScript Charting Ladder]] — related
- [[Matplotlib Object Model and Seaborn Function Levels]] — alternative-to
- [[Rendering Many Points: WebGL, Datashader and Bundle Weight]] — extends
