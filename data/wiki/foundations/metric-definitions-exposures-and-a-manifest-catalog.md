---
title: "Metric Definitions, Exposures and a Manifest Catalog"
tags: [foundations, pattern]
summary: "Define each metric once near the models so every tool asks for it, declare dashboards as exposures with owners to extend lineage, and start a catalog from the dbt manifest with a CI gate on missing owners."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--06-dataops.md
---

# Metric Definitions, Exposures and a Manifest Catalog

## One definition per metric

Two dashboards can disagree while both are right about their own SQL. Finance excluded refunds (98370) and growth did not (108320): "revenue" was two numbers and the meeting argued about which. Define the metric once, near the models, and have every tool request it. A semantic layer moves metric definitions from the BI layer to the modelling layer and handles joins (the hosted one was not run). A governed set of marts with one column per metric gets much of the benefit. Migrate dashboards and retire old definitions, or you have three numbers. Agreeing on the wording is in [[Writing a Metric Definition Two Analysts Agree On]].

## Exposures

Declared in `schema.yml` with an owner and `depends_on`, an exposure tells dbt a dashboard exists: `+exposure:...` lists what feeds it, and `state:modified+` lists it as affected by a change (see [[Slim CI for dbt Models: state:modified and defer]]). That is lineage for the last hop ([[Lineage for Blast Radius and Rebuild Lists]]).

## A catalog from the manifest

A catalog answers what a table is, who owns it, whether to trust it and what breaks if it changes. Dedicated products span many tools with connectors, search, lineage and governance. A first catalog is smaller: the manifest holds owner, documentation and tested columns for the models dbt builds. Example: of five models two had no owner, and a CI gate listing models with no owner caught them. A catalog people must remember to fill goes stale, so make the facts required: fail CI when a mart model lacks an owner or description. Buy a product when many tools need spanning and enough people search; it will not fix a documentation habit.

## See Also
- [[Writing a Metric Definition Two Analysts Agree On]] — related
- [[Slim CI for dbt Models: state:modified and defer]] — related
- [[Reverse ETL Fingerprint Sync]] — related
- [[Semantic Layer: Metrics Compiled at the Requested Grain]] — related
