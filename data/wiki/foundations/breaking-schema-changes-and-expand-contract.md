---
title: "Breaking Schema Changes and Expand-Contract"
tags: [foundations, pattern]
summary: "Diff contract versions in the producer's CI to flag removals, renames, type changes and tightened constraints as breaking, and ship an unavoidable break as add-new, migrate consumers, then drop the old column in a new major version."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--02-ingest-and-modelling--notes--04-data-contracts.md
---

# Breaking Schema Changes and Expand-Contract

Catching bad data after it is written is late. A better check runs when the producer opens a pull request, while the person who can fix it is already looking at the code. A CI job compares the contract on the branch with the one on main.

## What counts as breaking

| Change | Verdict |
|---|---|
| Remove a column | Breaking |
| Rename a column | Breaking (a drop plus an add, to a reader) |
| Change a type | Breaking |
| Make an optional column required | Breaking |
| Add a required column | Breaking |
| Remove a guarantee such as uniqueness | Breaking: a consumer may join assuming uniqueness, and the fan-out returns |
| Add an optional column | Safe |

The rule is the one from schema evolution: old readers must keep working. In the worked diff, changing an id column from integer to string was flagged breaking and adding an optional tip column was safe.

## Expand and contract

When a break is right (say, dollars to cents), use the migration pattern:

1. Add the new column alongside the old and write both. Non-breaking; CI passes.
2. Announce a deadline. Consumers migrate one at a time; lineage shows who remains.
3. Drop the old column in a new major version: the one breaking change, now affecting no one. CI requires sign-off, which is the conversation the contract exists to force.

Version with semantic versioning: a breaking change is a new major version.

## Why it works

Schemas stay accurate because they are required for reading, where documentation drifts, and a registry of schema versions lets you check forward and backward compatibility before deployment. A contract extends that from structure to meaning and quality ([[Data Contracts Beyond Schemas]]). The same compatibility gate is what a stream schema registry applies at produce time ([[Kafka Ingest Model, Delivery Semantics and Stream Windows]]).

## Pitfalls

Treating renames as harmless; relying on CI alone (runtime checks still needed); changing meaning without changing shape (units), which a structural diff cannot see.

## See Also
- [[Data Contracts Beyond Schemas]] — prerequisite-for
- [[Kafka Ingest Model, Delivery Semantics and Stream Windows]] — related
- [[Data Engineering Foundations]] — related
- [[Expand, Migrate, Contract]] — related (overlaps; candidate merge for /compact-wiki)
