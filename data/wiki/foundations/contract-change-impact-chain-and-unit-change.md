---
title: "Contract Change Impact Chain and the Same-Name Unit Change"
tags: [foundations, pattern]
summary: "Follow a column change from contract to catalog to metrics to named consumers using registration, lineage and the query log; a unit change under the same name passes every check."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--07-architecture-and-governance--notes--03-catalog-semantic-layer-and-contracts.md
  - data/raw/repos/learn-ai-engineering/data-engineering--07-architecture-and-governance--notes--01-data-architectures-mesh-fabric-mdw.md
  - data/raw/repos/learn-ai-engineering/data-engineering--07-architecture-and-governance--README.md
---

# Contract Change Impact Chain and the Same-Name Unit Change

A **data contract** is the producer's cross-team promise, including meaning and owner; a model contract is only a build-time check of one model's columns and types, so it can enforce part of a data contract but cannot state a unit or name a consumer. Contracts fix who may change what and who must be told. Producers own contracts; consumers request properties they need. No field in the open contract standard (v3.2.0, on a search by the source's author) records who consumes a dataset.

## Finding consumers: three sources, each with a hole

| Source | Learns consumers by | Misses |
|---|---|---|
| Registration | Declared exposures or follows | Everyone who did not bother |
| Lineage | Derived from pipelines | Notebooks and exports outside any pipeline |
| Query log | Observed reads | Readers outside log retention; shared service accounts |

Compare the log with the registry regularly and chase the difference. A catalog built from declared reads also answers "who is hurt" breadth first ([[Data Mesh as an Ownership Model and Federated Governance]]).

## The chain

For a breaking column: catalog (term, steward, tier) then metrics reading it (following ratio and derived metrics up, matching on column names) then registered consumers with owners, plus unregistered readers from the log. In the demo, a fare column change reached two metrics, one dashboard registered through a metric, one model registered against the whole table (so only "ask which columns"), and a notebook visible only in the log. A dashboard on an unrelated metric over the same table was correctly left off the list, because registration through a metric is more precise than through a table. The name match would be fooled by another table with the same column name; filter on the metric's semantic model.

Two owners: the **contract owner** decides when a column may change; the **metric owner** decides what the metric means and owns the one line that moves. A consumer registered with a metric hears from the metric owner, who may absorb the change.

## Same-name unit change

Three ways to ship a fare change on a toy dataset (revenue per trip was 30.8594):
- Rename to a cents column: config validation fails in CI, naming the missing column. The good failure.
- Same name, now in cents: types match, validation passes, revenue per trip becomes 3085.94, a hundred times too big. Only a value rule catches it: a range rule flagged 2,486 rows, but only because the cheapest fare of $6 became 600 against a limit of 500; a fare of $5 or less would pass, so also check the median.
- Rename and update the metric expression in one file: every consumer of the metric returns 30.8594 again, with no change of their own. The notebook still breaks, which is why it is on the list; keep both columns live while readers move (expand and contract).

A unit lives in a contract as text; enforcing it takes a value rule. Give a new unit a new column name so the failure is loud. No controlled before-and-after measurement that contracts reduce incidents was found; the case is mechanical.

## See Also
- [[Semantic Layer: Metrics Compiled at the Requested Grain]] — prerequisite-for
- [[Data Catalog Metadata: Push, Pull and Measuring Adoption]] — prerequisite-for
- [[Erasure on Immutable Storage: Vacuum, Crypto-Shredding and the Ledger]] — related
- [[Data Mesh as an Ownership Model and Federated Governance]] — related
