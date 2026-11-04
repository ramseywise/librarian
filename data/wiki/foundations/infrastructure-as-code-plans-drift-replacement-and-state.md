---
title: "Infrastructure as Code Plans: Drift, Replacement and State"
tags: [foundations, concept]
summary: "A plan loop of write config, plan, apply after approval exposes three traps: console edits show up as drift and get reverted, some edits force a destroy and re-create, and the state file must be stored remotely with locking."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--06-dataops.md
---

# Infrastructure as Code Plans: Drift, Replacement and State

Warehouses, buckets, roles and schedules are configuration too. If created by clicking, nobody can review, rebuild or say what changed. The usual loop is write config, plan, apply after approval; `plan` reads the current state of existing objects, compares config with prior state and proposes changes. The behaviours below come from a small model of that loop, not the tool itself.

## Three behaviours

| Event | Plan shows |
|---|---|
| First plan | create both objects |
| Second plan | no changes |
| Warehouse resized in console during an incident | drift, update back to the configured size |
| One-word region edit on a bucket | REPLACE |

- **Drift.** A console edit appears in the next plan, and applying it reverts the resize (size S after apply). Copy a deliberate fix into the config or lose it on the next apply.
- **Replacement.** Some arguments cannot change in place due to remote API limits, so the resource is destroyed and re-created. A stateless service shrugs; for a bucket or database it is the end of the data. Read every plan for destroys, put a destroy guard on anything holding data, and fail the pipeline on destroys of stateful resources unless approved.
- **State.** The state file maps config to real objects. Planning with an empty state against a cloud where everything exists proposes creating everything, since without state it does not know the objects are its own; recover by restoring state or importing, not applying. Keep state remote with locking, not in version control, since it may contain secrets.

## Reproducible deploys

Releases should be reproducible and automated. Rolling back code does not roll back rows it already wrote; [[Blue-Green View Swap for Data Deploys]] gives data a real rollback. Hand-fixing production during an incident is sometimes right, but put it in the config afterwards.

## See Also
- [[Blue-Green View Swap for Data Deploys]] — related
- [[Slim CI for dbt Models: state:modified and defer]] — related
- [[Rollback Restores Code Only]] — related
