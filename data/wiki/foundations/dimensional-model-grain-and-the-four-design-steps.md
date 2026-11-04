---
title: "Dimensional Model Grain and the Four Design Steps"
tags: [foundations, concept]
summary: "A star schema is agreements about what one row means, what can be added up and what a label meant on the day: declare the grain first, keep an Unknown row so nothing drops, and store the parts of any ratio."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--02-ingest-and-modelling--notes--02-dimensional-modelling.md
---

# Dimensional Model Grain and the Four Design Steps

Normalised operational tables protect writes and are poor for reading: each question re-derives the joins, and each analyst derives them slightly differently, so two people bring two numbers to one meeting. A dimensional model fixes that with a **fact table** (measurements: one row per event at one grain, columns are foreign keys plus numbers) surrounded by **dimension tables** (wide, short, read far more than changed: names, categories, flags). Column stores suit it, since a query touches a few fact columns and long runs of repeated keys compress.

## Four decisions, in order

1. **Choose the business process** (completing a trip), not a department.
2. **Declare the grain** in one sentence ("one row per completed trip"). If you cannot say it, you cannot build the table. Choose the most atomic grain the source gives: atomic rows answer predicted questions and unpredicted ones.
3. **Choose dimensions.** Each must take a single value per row at that grain; a multi-valued column means the grain is wrong or it needs its own fact.
4. **Identify facts:** only numbers true to the grain.

## Details interviewers ask about

- **Surrogate keys:** warehouse-owned meaningless integers. They buffer from source key recycling or a second numbering, and slowly changing history cannot work without them ([[Slowly Changing Dimensions Types 1, 2 and 3]]).
- **An Unknown row:** setup: 1,000,000 trips use 260 zone ids but the lookup knows 250. Mapping orphans to key -1 kept 2,187 trips visible; an inner join would have dropped them silently so fares by zone no longer summed to total fares. Same device for "no promotion" or "date to be determined". Load with left joins to the Unknown row.
- **A pre-built date dimension:** calendars do not arrive in events and an empty month would vanish from a report. Ten years is about 3,650 rows (the example built 1,095 dates for three years).
- **Degenerate dimension:** a key such as the trip id kept in the fact with no table behind it, for tracing to the source.
- **Centipede:** a fact with too many dimensions (about fifteen is typical); combine correlated ones.

Every query then has one shape: fact joined to dimensions on keys, business words in WHERE and GROUP BY, which is what lets a BI tool generate SQL.

## What can be added up

| Kind | Sums across | Example | Trap |
|---|---|---|---|
| Additive | every dimension | fare, miles | none |
| Semi-additive | some, not time | balance, vehicles in depot | Summing daily balances over a week is meaningless; average or take the last |
| Non-additive | none | fare per mile, percentages | recompute from additive parts |

Store the numerator and denominator, not the ratio, or a dashboard will sum it. On the example, total fares over total miles was 3.41 dollars; the average of per-trip ratios was 4.10 (about 20% high, since short trips carry a large share of the flag fall). See [[Ratio of Sums vs Mean of Rates]].

Fact tables are also **transaction** (one row per event, immutable), **periodic snapshot** (one row per entity per period) or **accumulating snapshot** (one row per process instance, updated at milestones). A snapshot's `count(*)` counts entity-periods, not events.

## Pitfalls

No declared grain; inner joins to dimensions; natural keys in the fact; storing ratios; type-1 updates by default; modelling the org chart (a "marketing mart" of copies breeds the two-number meeting).

## See Also
- [[Slowly Changing Dimensions Types 1, 2 and 3]] — extends
- [[Conformed Dimensions, the Bus Matrix and Drilling Across]] — extends
- [[Data Vault Hubs, Links and Satellites]] — alternative-to
- [[One Big Table versus Star Schema]] — alternative-to
- [[Ratio of Sums vs Mean of Rates]] — related
- [[Data Engineering Foundations]] — related
