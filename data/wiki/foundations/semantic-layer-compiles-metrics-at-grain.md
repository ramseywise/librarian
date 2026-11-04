---
title: "Semantic Layer: Metrics Compiled at the Requested Grain"
tags: [foundations, concept]
summary: "A semantic layer stores metrics and join keys as data and compiles each request, refusing fan-out joins, recomputing ratios from parts and handling balances as semi-additive."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--07-architecture-and-governance--notes--03-catalog-semantic-layer-and-contracts.md
  - data/raw/repos/learn-ai-engineering/data-engineering--07-architecture-and-governance--README.md
---

# Semantic Layer: Metrics Compiled at the Requested Grain

A **semantic layer** holds metric and join definitions as data and compiles each request into SQL. It differs from a catalog (what exists and means what) and from a few-shot "semantic layer" of question and SQL pairs in a text-to-SQL tool.

## Three plausible wrong numbers from plain SQL

On a toy trips dataset:
- **Fan-out:** joining trips to a rider's several promo redemptions repeated trips, giving revenue 132,994.27 against a true 82,209.54 (overstated by 62%).
- **Averaged ratio:** the mean of daily cancel rates was 0.1619 against a true ratio of totals of 0.0668, because a quiet weekend with many cancellations got the same vote as a busy weekday. Recompute from numerator and denominator at the grain asked for ([[Ratio of Sums vs Mean of Rates]]).
- **Semi-additive balance:** summing daily wallet snapshots over March gave 340,380 against 11,280 at month end, counting the same money about thirty times. Ratios and distinct counts are non-additive across every dimension; a balance is additive across riders but not time.

## How a layer avoids them

The engine describes tables as semantic models with **entities** (join keys typed primary, unique, foreign or natural), **dimensions** and metrics, and a **time spine**. It captures the type of each key and navigates to a safe join rather than taking arbitrary join logic.
- A query names metrics and a dimension, no join. A foreign key to a primary key becomes a left join with no repeated rows, and a ratio metric aggregates numerator and denominator before dividing, so two definitions cannot drift.
- Foreign-to-foreign (fan-out) is refused with an explanatory error and the dimension is not offered. The cost is real: the requester must say what the cut means (credit the whole trip to each promo, or split it). It also stops at two hops, so a farther dimension needs a modelled table.
- A balance metric declares a non-additive dimension, and the generated SQL keeps each rider's last row per period before summing, reproducing 11,280.
- Another layer takes a different trade: directed joins with relationship types, and a multi-fact view gives each fact its own aggregating subquery joined on shared dimensions (from its documentation; not run).
- The local compiler is free; the hosted layer that BI tools connect to needs a paid tier.

It complements, not replaces, a mart: a mart fixes a grain at build, so a ratio stored per day cannot honestly roll up to a month; a layer keeps the parts and computes at request, still reading a well-modelled table. A handful of metrics in one BI tool does not justify a layer; a metric several tools disagree on, or re-cut many ways, does. Search BI calculated fields and retire competing ratio definitions.

## Does it help text-to-SQL?

Evidence is thin and interested: every measured comparison came from a vendor of a layer or knowledge-graph product, with no independent replication found. Examples (correct share, each source's own scoring): SQL over DDL vs a knowledge graph, 16.7 vs 54.2 on 43 questions; one vendor test of 11 questions run 20 times found, on the original schema, 62.5 vs 100 for questions the layer can reach, 70.0 vs 0 for those it cannot, and 90.0 vs 98.2 after three extra models, so modelling closes the gap. A layer's output is correct if the model picks the right metric and dimensions; that choice is not guaranteed (87.2 to 87.5 for one stronger model). Another study tests a context document rather than a runtime layer (46.5 vs 68.7 on 99 questions). Declared definitions help; the effect size is unsettled, and nothing separates a compiler's value from writing definitions down. Do not compare across rows; setups differ.

## See Also
- [[Data Catalog Metadata: Push, Pull and Measuring Adoption]] — prerequisite-for
- [[Contract Change Impact Chain and the Same-Name Unit Change]] — extends
- [[Writing a Metric Definition Two Analysts Agree On]] — prerequisite-for
- [[Metric Tree Decomposition]] — related
- [[SQL Fan-Out and Source Reconciliation]] — related
- [[Ratio of Sums vs Mean of Rates]] — related
