---
title: "Blue-Green View Swap for Data Deploys"
tags: [foundations, pattern]
summary: "Build the new version of a table beside the old, audit it, then repoint a view in about a millisecond; rollback is the same swap while the old build is kept and nothing has been written on top."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--06-dataops.md
---

# Blue-Green View Swap for Data Deploys

Data adds a problem services lack: rolling back code does not roll back the rows it wrote or decisions already made from them. One pattern gives data a real rollback: build a new version beside the old, audit it, switch readers with one small statement. It is the same idea as the [[Write-Audit-Publish and Atomic Visibility]] and the alias swap in [[Re-embedding a Vector Store with a Second Index]].

## Run

Readers query a view over `build_1` (108320). Build `build_2`, audit it (28 rows, 0 negative), repoint the view: live value 97488, swap took 1.0 ms in the local run; rollback restored 108320 in 0.6 ms. Table size does not matter, since only a view definition changes.

## Costs and limits

- Storage for two copies, and the old build retained until you are sure.
- Rollback is this easy only while nothing has been written on top of the new version.
- A change in a table's shape also needs [[Expand, Migrate, Contract]].
- Timings are from a local file with no concurrent readers.

## See Also
- [[Write-Audit-Publish and Atomic Visibility]] — related
- [[Infrastructure as Code Plans: Drift, Replacement and State]] — related
- [[Rollback Restores Code Only]] — related
