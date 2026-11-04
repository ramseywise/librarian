---
title: "Rendering Many Points: WebGL, Datashader and Bundle Weight"
tags: [foundations, reference]
summary: Measured costs of drawing many points (SVG vs WebGL vs server-side datashader), shipping chart libraries, and mapping; ask first whether the points are needed at all.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--05-visualisation-and-storytelling--notes--06-dashboard-stacks-from-python-to-frontend.md
---

# Rendering Many Points: WebGL, Datashader and Bundle Weight

Fixing the data usually matters more than choosing the library: an unaggregated table weighed as much as the largest charting library. Three rungs; climb only as far as needed.

## 1. SVG, then WebGL

Plotly's ordinary scatter makes one page element per mark; `scattergl` hands drawing to the graphics card. Measured on one fast laptop (Chrome, 800x500, median of three):

| Points | SVG ms | WebGL ms |
|---:|---:|---:|
| 1,000 | 27 | 42 |
| 10,000 | 102 | 46 |
| 50,000 | 476 | 55 |
| 400,000 | not run | 111 |

WebGL loses slightly at 1,000 and wins from 10,000; read the shape, not the digits (reruns moved WebGL by tens of ms, and phones and panning differ). Limits: browsers allow roughly 8 to 16 WebGL contexts per page (about 4 to 8 figures), after which some will not render; the ceiling is around a million points. Plotly Express switches to WebGL above 1,000 rows by itself. The basic Plotly bundle omits `scattergl`.

## 2. Render on the server

Datashader aggregates points onto a grid and sends an image, since only the aggregation stage needs the whole dataset; browser cost no longer depends on point count. 5,000,000 points to an 800x500 image took 371 ms first (compiling) and 21 ms second; the shaded image was 255 KB versus 362 KB gzipped for a 50,000-point Plotly figure. Trade-off: zooming in shows more detail only while the Python process is running, so it needs a server and suits a small audience (Panel, HoloViews).

## 3. Ask whether you need the points

For a group-level question, a grid of counts was 2.4 KB gzipped.

## What the browser downloads (gzipped KB, minified, pinned versions)

| Bundle | Gzip KB |
|---|---:|
| plotly.js full | 1,449 |
| plotly.js basic (bar, pie, scatter) | 396 |
| echarts everything | 375 |
| vega-embed + vega + vega-lite | 285 |
| recharts scatter with react | 173 |
| echarts scatter only | 172 |
| d3 everything | 94 |
| d3 scale, axis, selection only | 12 |

What you import matters (ECharts scatter is under half of everything). A Python app is not free: a Dash first load fetched 21 files, 6,716 KB (about 1,901 KB gzipped), versus 177 KB for a React page, a gap that matters on phones and hardly for office broadband. ECharts' handbook recommends canvas above about 1,000 items; Recharts draws SVG, fine in modest numbers.

## Maps

- Aggregate before mapping: ten region markers made a 10 KB page, 5,000 individual markers 2,435 KB.
- On a choropleth large regions dominate whatever the value; shade by a density, or by a share only if regions are similar in size. For a count, use a sized circle at one point.
- Public map tiles are best-effort with no SLA and need attribution; arrange your own for anything a business depends on.
- Customers' home addresses on a map are a privacy decision, not a chart choice.

## See Also
- [[Interactive Charts and When They Pay]] — prerequisite-for
- [[Dashboard Stack Layers and Choosing a Route]] — related
- [[Dashboard API Exposure and Payload Cost]] — related
