---
title: "Warehouse, Fabric and Lakehouse: Sizing the Physical Architecture"
tags: [foundations, comparison]
summary: "Modern data warehouse, data fabric and lakehouse differ in how many copies and governance layers they add; size the choice by measuring one query, and name the system of record."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--07-architecture-and-governance--notes--01-data-architectures-mesh-fabric-mdw.md
  - data/raw/repos/learn-ai-engineering/data-engineering--07-architecture-and-governance--README.md
---

# Warehouse, Fabric and Lakehouse: Sizing the Physical Architecture

## Three physical architectures

- **Modern data warehouse (MDW):** a relational warehouse plus a data lake, with at least some data copied from lake to warehouse. Lake: schema on read, data scientists, cheap storage of everything, file/folder-level security. Warehouse: schema on write, BI users, fast stable serving, row- and column-level security. Costs: two systems, data stored twice, drift into silos, compliance across two stores.
- **Lakehouse:** no warehouse copy. Warehouse features (ACID, schema enforcement, time travel) come from an open table format on the lake.
- **Data fabric:** an MDW plus a layer for accessibility, security, discoverability and availability, with eight features: access policies (key to governance), a metadata catalog with lineage, master data management, data virtualisation (optional, usually a few sources), real-time processing, APIs, services and products. One author's rule of thumb is three or more features means a fabric; he admits the line is fuzzy. Definitions differ, and some "intelligent fabric" claims rely on technology that does not yet exist. More technology to integrate and harder troubleshooting is the cost; a small business with few sources may need only an MDW.

Exceptions to "everything passes through the lake" are small reference tables and migrations; each gives up the lake as backup and single source of raw truth.

## Sizing: measure before buying

| You have | Consider |
|---|---|
| Under about 1 TB, one team | A single-node (SMP) database, or an embedded engine |
| Up to about 10 TB, BI-heavy | MDW |
| Many sources, governance pain, lineage questions | Fabric |
| Large data, data-science heavy, cost-sensitive | Lakehouse |
| Many autonomous business units | A mesh on top of any of these ([[Data Mesh as an Ownership Model and Federated Governance]]) |

The thresholds are practitioner judgement, not measurement. A measurement: a grouped aggregate over 50,000,000 synthetic rows (0.37 GB on disk) took 0.14 s on a 12-core laptop. That is one query with no concurrency, so it says nothing about many analysts at once, and concurrency and governance are what a warehouse also sells. It does say volume alone rarely justifies an MPP cluster at that size. Buying an architecture for the data you imagine is the pitfall.

## Derived data: the frame under all of them

Several representations of the same facts always exist, so ask where each fact is written first. That is the **system of record** (the lake's raw zone or the operational source); warehouse tables, marts, search indexes, feature stores and models are *derived*, can be rebuilt, and a bug in them is cheap. "No single source of truth" means this question is unanswered.

Derived copies stay in step by a distributed transaction or by a log with idempotent retries. The log contains a fault, where a transaction spreads it to every participant, and lets teams work independently if the interface between them is well defined. To make an organisation's data behave as one database:
- **Federation** unifies reads (one query interface over many stores) - what a fabric's virtualisation offers.
- **Unbundling** unifies writes (a log and derived views, like building an index from a snapshot plus a backlog) - what ELT/CDC between domains does.

Limits: a total order needs one leader, so across independent services some cross-domain questions have no single right order. Also separate **timeliness** (a late dashboard; waiting fixes it) from **integrity** (wrong data; waiting does not). Integrity usually matters more, which argues for auditing: read data back, test restores, run end-to-end checks across the whole derived pipeline.

## See Also
- [[Data Mesh as an Ownership Model and Federated Governance]] — extends
- [[Data Catalog Metadata: Push, Pull and Measuring Adoption]] — extends (the fabric's catalog, built out)
- [[SQL Fan-Out and Source Reconciliation]] — related
- [[Data Engineering Foundations]] — related (course map)
- [[Lakehouse vs Warehouse Decision]] — related (lakehouse against warehouse in depth)
