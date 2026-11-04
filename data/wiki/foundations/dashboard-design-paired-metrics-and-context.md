---
title: "Dashboard Design: Paired Metrics and Context"
tags: [foundations, pattern]
summary: A dashboard serves a recurring decision with few contextualised metrics, each growth metric paired with a health metric; Streamlit reruns the script per interaction, and BI tools suit shared editing.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--05-visualisation-and-storytelling--notes--05-dashboards-and-storytelling.md
---

# Dashboard Design: Paired Metrics and Context

A dashboard is a designed tool for monitoring, built before any finding exists. It answers "what is my number, is it okay?" and has a lifespan of months or years, whereas an explanatory story answers "what happened, what should we do?" for one decision ([[Explanatory Data Story and the Big Idea]]). The commonest failure is pasting a dashboard screenshot into a slide and hoping the executive finds the point. A dashboard that stayed green while a health measure fell by nearly a third did not lie; it was never asked the right question.

## Checklist

1. **Name the decision.** If nobody can name the recurring decision, it is a report no one will open.
2. **Few metrics, each with context** (prior year, target, threshold). A bare total says little.
3. **Pair a growth metric with a health metric.** Anything you can push by spending (buying traffic raises revenue) needs a partner that shows the side effect, such as repeat rate.
4. **Layout follows reading order:** summary tiles top left, then trends, then detail (overview, filter, details on demand).
5. **Filters in one row above the charts,** visibly changing everything below.
6. **State data source and refresh time.** Trust dies when a dashboard disagrees with finance and nobody can say why.

## Streamlit execution model

A widget interaction reruns the whole script top to bottom; a widget is a function call returning its current value, with no callbacks. `@st.cache_data` stores results keyed on function code and inputs, so an uncached warehouse query reruns on every click. `AppTest` runs the script headless, sets widgets and reads metrics, which makes edge cases testable: with no prior year in the data the deltas must come back empty, not as division by zero; an empty channel selection gives zero spend and breaks a revenue-per-spend tile unless guarded. Use an arrow and sign, not only red/green, on deltas.

## When not to write code

| | Streamlit | Metabase | Looker Studio |
|---|---|---|---|
| Who edits | Python developers | Analysts plus self-serve | Anyone with a browser |
| Logic lives in | Python, in git | SQL and models in the tool | Calculated fields in the tool |
| Custom chart forms | Anything Python draws | Its chart types | Its types and add-ons |
| Tests/review | Code review, `AppTest` | Limited | Limited |
| Best for | Models, simulators, bespoke tools | Standard reporting | Quick reports on Google data |

Ask who will change this in six months; if the answer is the marketing team, a Streamlit app becomes a ticket queue. In Metabase SQL, `{{var}}` becomes a filter widget and double square brackets around a clause make it optional so the query runs when the filter is empty; field filters bind a variable to a column so the widget offers real values. Looker Studio is not Looker, the governed modelling platform. Route choice in full: [[Dashboard Stack Layers and Choosing a Route]].

## See Also
- [[Explanatory Data Story and the Big Idea]] — related
- [[Dashboard Stack Layers and Choosing a Route]] — extends
- [[Interactive Charts and When They Pay]] — related
- [[Chart Colour Scales and Accessibility]] — related
