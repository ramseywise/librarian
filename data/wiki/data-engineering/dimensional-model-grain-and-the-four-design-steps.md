---
title: "Dimensional Model Grain and the Four Design Steps"
tags: [data-engineering, ingest-and-modelling, concept]
summary: "A star schema is agreements about what one row means, what can be added up and what a label meant on the day: declare the grain first, keep an Unknown row so nothing drops, and store the parts of any ratio."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--02-ingest-and-modelling--notes--02-dimensional-modelling.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch01-dimensional-modeling-primer.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch02-retail-sales.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch05-order-management.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch07-accounting.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch09-financial-services.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch10-telecommunications-utilities.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch11-transportation.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch14-electronic-commerce.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch15-insurance.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch16-building-data-warehouse.md
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

## Kimball and Ross's published guidance

These points come from chapters 1, 2, 5, 7, 9 and 10 of *The Data Warehouse Toolkit*. The rules of thumb are the authors' guidance, with no data behind them.

- **Space:** Kimball and Ross put fact tables at 90 percent or more of a dimensional database and dimensions under 10 percent, so snowflaking saves almost nothing. Setup: a hypothetical grocery chain with 150,000 product rows and 50 departments; replacing a 20-byte department description with a 2-byte code saves roughly 2.7 MB, set beside a fact table the chapter guesses at 10 GB. They advise storing hierarchy attributes redundantly in the dimension.
- **Dimension shape:** they describe a good dimension as wide (50 to 100 attributes) and shallow (far below a million rows).
- **How many dimensions:** most models end up with 5 to 15. Chapter 9 says to suspect omitted dimensions at the low end; chapter 10 treats 2 to 3 or 25 to 30 as a signal of a problem; chapter 2 advises merging correlated dimensions at 25 or more.
- **Fact or attribute:** a numeric field that varies widely and takes part in calculations is a fact; a stable descriptor used in constraints is an attribute.
- **Mixed grain:** header-level facts such as shipping charges are allocated down to the line, or kept in a second table. Setup: an order line table of 10 million rows holding four facts becomes 40 million rows if rebuilt as one generic amount column with a fact-type dimension.
- **Date and time:** setup: a daily date dimension over ten years is about 3,650 rows; folding minute of day into it would give 5,256,000, so the authors give minute of day a separate 1,440-row dimension. An integer date key saves 4 bytes per fact row against an 8-byte SQL date (their typical figure).
- **Sizing a fact table:** setup: a hypothetical grocery chain with $4 billion annual revenue and $2.00 average item price works out at about 2 billion line items a year; at 38 bytes a row, a billion rows is about 38 GB.
- **Fiscal calendars:** one fiscal calendar becomes hierarchical attributes of the date dimension; many subsidiary calendars use a date-by-subsidiary outrigger, separate date tables sharing keys, or a fiscal-period key in the fact.
- **Market basket:** a product-pair fact table grows with the square of the product count (10,000 products yield nearly 100 million pairs). The authors enumerate pairs top down by hierarchy level and prune by basket count and dollar or unit balance.
- **Edition change:** the retail chapter says the first edition summed sales per product, promotion, store and day because hardware of the time could not hold line items, while this edition declares line-item grain.

Related dimension techniques are on [[Degenerate, Junk and Role-Playing Dimensions]], [[Minidimensions for Rapidly Changing Monster Dimensions]], [[Bridge Tables for Multivalued and Ragged Hierarchy Dimensions]] and [[Transaction, Periodic and Accumulating Snapshot Fact Tables]].

## Grain choices in chapters 11 to 16

- **Travel grain:** Kimball and Ross advise choosing the grain by business process and starting at the lowest grain with meaningful metrics, here the segment (the part of a trip on one aircraft), not the leg data. Trip origin and destination are added as extra role-playing airport dimensions on the segment table. A trip-grain aggregate is advised only if segment rollups show obvious problems; setup: a typical trip of three segments gives only about a threefold speedup. Take care summarising to trip level, because fare basis and class of service have no meaning at that level.
- **Time of day:** the authors keep it out of the date dimension, which would otherwise multiply its rows. A separate time-of-day dimension serves grouping such as 15-minute buckets, hours, AM or PM, or rush periods; without grouping, a numeric fact of minutes or seconds past midnight is enough. For several time zones, carry both local and equalised (GMT or headquarters) date and time.
- **Superdimension:** role-playing dimensions are merged only if they have very few rows or their attributes depend on the pair (class of service, city pair); the authors call this the exception. If a combined origin and destination dimension is too big, keep two separate dimensions and add a city-pair dimension.
- **Sessions versus page events:** see [[Clickstream Session and Page-Event Fact Tables]] for a worked choice between two grains.
- **Insurance:** policy transactions are one business process and one fact table, split into quoting, rating and underwriting tables only if needed. The authors list ten modelling mistakes: putting text in facts, stingy dimension attributes, snowflaked hierarchies, ignoring attribute changes, fixing with hardware where aggregates would do, smart keys in place of integer surrogates, neglecting grain, designing from reports, a normalised presentation area, and facts and dimensions that do not conform.
- **Loading facts:** staging replaces surrogate keys before load, and an unmatched key gets its own "Description Unknown for Operational Key" row rather than a shared dummy key ([[Business Dimensional Lifecycle and Dimensional Data Staging]]). Large facts are partitioned by date, and aggregates are separate fact tables on shrunken conformed dimensions.

## Limits

- The guidance above is opinionated practitioner advice from a book; the extractions note no measurements or benchmarks, and the sizes come from hypothetical worked examples.
- The extraction says chapter 1 may be an earlier edition than the 3rd and uses a 2002-era frame; chapters 2 to 10 are inferred to be the 2nd edition (2002), not the 3rd (2013). Modern cloud columnar warehouses, ELT and lakehouses are outside the text, and the extraction notes that its index and disk-space arguments suit engines of that period.
- Chapter 1 defines the enterprise data warehouse as staging plus presentation, which differs from other schools' normalised-EDW usage.
- Chapters 11, 15 and 16 are practitioner guidance with no measurements. Chapter 11 is inconsistent on the class-of-service dimension: its text counts three purchased and three flown rows, but its figure and the 3 by 3 product give 9.

## See Also
- [[Slowly Changing Dimensions Types 1, 2 and 3]] — extends
- [[Conformed Dimensions, the Bus Matrix and Drilling Across]] — extends
- [[Data Vault Hubs, Links and Satellites]] — alternative-to
- [[One Big Table versus Star Schema]] — alternative-to
- [[Ratio of Sums vs Mean of Rates]] — related
- [[Data Engineering Foundations]] — related
- [[Transaction, Periodic and Accumulating Snapshot Fact Tables]] — extends
- [[Minidimensions for Rapidly Changing Monster Dimensions]] — extends
- [[Bridge Tables for Multivalued and Ragged Hierarchy Dimensions]] — extends
- [[Degenerate, Junk and Role-Playing Dimensions]] — extends
- [[Core and Custom Schemas for Heterogeneous Products]] — extends
- [[Factless Fact Tables and Coverage Tables for Non-Events]] — extends
- [[Clickstream Session and Page-Event Fact Tables]] — instance-of
- [[Business Dimensional Lifecycle and Dimensional Data Staging]] — related (staging and project practice)
