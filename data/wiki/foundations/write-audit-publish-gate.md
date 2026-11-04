---
title: "Write-Audit-Publish Gate"
tags: [foundations, pattern]
summary: "Land partitions where readers cannot see them, audit there, and expose only days that pass; readers then see an honest gap instead of a wrong number, and the gate is also the containment tool during an incident."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--01-quality-dimensions-and-tests.md
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--03-incident-playbooks.md
---

# Write-Audit-Publish Gate

A test run after publication measures the damage; one run before it prevents it. Write-audit-publish writes to a place readers cannot see, audits, then exposes.

## Mechanism

One implementation is two small tables and a view: a `published_days` table, a `quarantine` table with a reason, and a `trips_published` view that joins raw data to published days only. The audit runs the row-level rules (no rows, duplicate keys, null share above 1%, median outside an expected band). A passing day is inserted into published days; a failing day goes to quarantine and is removed from published. Table formats can do the same with an audit branch; in dbt, tests upstream of the published model.

Over a 91-day synthetic quarter the gate published 80 days and quarantined 11: three single-day faults plus all eight unit-change days. Readers saw a gap; a gap is visible and honest, while a wrong number gets used.

## Where it sits

Each stage covers what the last cannot: a model contract cannot see a null spike, a row test cannot see a missing day, and monitors see those only after publication and only against history. Block when wrong data costs more than late data.

## Design traps

- Audit the layer that will be published. Auditing raw after a deduplicating repair keeps failing, so the gate would never release the repaired day; decide this before an incident.
- Without a gate, containment is cruder: pause the downstream DAG, restore the previous table version if the format supports it, or put a warning on the dashboard. For a model, rolling back the learned model is an ML-specific option, useless if the inputs are what is wrong.
- The same swap-a-pointer idea gives data deploys a rollback (see [[Parallel Run and Reconcile at the Grain People Read]]).

## See Also
- [[Data Quality Dimensions and Tests as Failing-Row Queries]] — prerequisite-for
- [[Data Incident Playbook: Contain Before Diagnosing]] — related
- [[Rollback Restores Code Only]] — related
- [[Write-Audit-Publish and Atomic Visibility]] — related (overlaps; candidate merge for /compact-wiki)
