---
title: "Data Contracts Beyond Schemas"
tags: [foundations, concept]
summary: "A data contract is a machine-checked agreement between producer and consumers covering structure, meaning, quality, freshness, ownership and grain; a units change such as dollars to cents passes every schema test and only a written semantic rule catches it."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--02-ingest-and-modelling--notes--04-data-contracts.md
---

# Data Contracts Beyond Schemas

Every stage trusts the one before it, and the first hand-off crosses a team boundary, where the producer treats its schema as an implementation detail. Pulling raw application tables removes the moment at which anyone thinks about the reader. Schema-on-read moves interpretation from the producer to every consumer; "schemaless" data still has structure, only implicit and unchecked. A contract moves the check back to the boundary.

## What goes in

| Part | Promise | Example |
|---|---|---|
| Structure | Names, types, required, keys | id is a BIGINT primary key |
| Semantics | Meaning and units | "Fare in US dollars, before tip" |
| Quality | Rules the data satisfies | No fare below 0 or above 500 |
| Service levels | Freshness, availability | No more than 2 hours old |
| Ownership | Who to call, who may change it | Team and support fields |
| Grain | What one row is | One row per completed trip |

The Open Data Contract Standard gives a YAML format with a published JSON Schema covering these; the contract lives in the producer's repository next to the code. Validity against the JSON Schema says nothing about any data.

## Enforcing on a batch

Check in two stages: structure first (missing column, wrong type), because counting nulls in an absent column is meaningless; then content (required nulls, uniqueness, SQL quality rules). Six 20,000-row batches: good passed; a renamed column reported a missing column; a string zone id reported the type; 3% null zones reported 577 nulls; duplicate ids reported 49 duplicates.

The "cents" batch has the right name and type and no nulls. A structural test passes both batches while the mean fare moved from 11.23 to 1122.8. Only the two written quality rules caught it (fares in 0 to 500; median between 5 and 40). Types cannot see a units change. The median rule is more robust than the range, since a range can miss a smaller shift such as a switch to pence or a fare excluding a surcharge. Distribution monitoring picks up where static rules stop.

## Stop or quarantine

- **Stop the load** when the batch as a whole is untrustworthy (missing column, wrong units, half the volume). Stale data is visible to consumers; wrong data is not.
- **Quarantine rows** when failures are isolated: good rows continue, bad rows go to a side table with a reason, the owner is alerted.

A threshold ties them together: with 577 of 20,000 rows failing (2.9%) against a 1% limit, the load stops. The limit is a business decision written in the contract. Keep good plus quarantined equal to rows received; nothing disappears without a count.

## Limits

- It cannot make a producer care: without a mandate from whoever owns both teams it is a document nobody reads. Start with the few datasets whose failure reaches an executive or customer, not every table.
- Rules catch only what someone thought of; keep monitoring.
- Third-party sources: run the same checks on arrival as a one-sided contract.
- Check at runtime as well as in CI; a contract in a repository is a claim, the checks make it true.
- A validation system deployed across hundreds of product teams reports that many pipelines had no schema at all: infer a first schema from a sample and curate it as it co-evolves with the data, since curated schemas avoid false alarms and keep false positives low by limiting constraints to a narrow set.

## Pitfalls

A schema calling itself a contract (automated `DESCRIBE`); checks only in the warehouse; no named owner (an alert to a shared channel); silently dropping failing rows; thresholds invented by engineers.

## See Also
- [[Breaking Schema Changes and Expand-Contract]] — extends
- [[Kafka Ingest Model, Delivery Semantics and Stream Windows]] — related (schema registry)
- [[Dimensional Model Grain and the Four Design Steps]] — related (the Unknown row follows the same nothing-disappears rule)
- [[Data Engineering Foundations]] — related
