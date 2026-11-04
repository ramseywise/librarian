---
title: "Parallel Run and Reconcile at the Grain People Read"
tags: [foundations, pattern]
summary: "Moving a warehouse follows expand-migrate-contract at larger scale: run both side by side, compare per partition and key, because totals can match to the cent while no day matches."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--04-schema-and-data-migrations.md
---

# Parallel Run and Reconcile at the Grain People Read

Build the new system next to the old, feed both, compare, switch readers, keep the old for a while, then drop it ([[Expand, Migrate, Contract]] at a larger grain). Porting adds one hazard: SQL that runs on both engines can mean different things.

## The grain decides what you catch

In a DuckDB simulation, a one-hour session offset was planted in the port. Totals agreed: 1,000,000 trips on both sides, revenue 9995000.0 on both. Yet by day **0 of 367 days matched**, and a day-count difference showed (for example one day at 2728 versus 2727, another at 2712 versus 2599). A check of row counts and sums would have passed the migration. Compare per partition and per key. Macro packages exist for row-count comparison, all-column comparison and classifying differences. A zero-copy clone gives a cheap copy to test a change against, since it shares storage with its source until either changes.

Compare with [[Reconciliation Against a Producer Control Total]] (a total at the source boundary): both fail when the comparison grain is coarser than the fault.

## Cutover

Usually repoint consumers one by one through views or a semantic layer ([[Blue-Green View Swap for Data Deploys]]), keeping both sides loaded for the rollback window. Rollback gets more expensive with every day of writes only the new side received.

## See Also
- [[Expand, Migrate, Contract]] — related
- [[Reconciliation Against a Producer Control Total]] — related
- [[Write-Audit-Publish Gate]] — related
