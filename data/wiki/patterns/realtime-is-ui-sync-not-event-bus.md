---
title: Realtime Is UI Sync, Not the Event Bus
tags: [infra, pattern]
summary: A database's realtime channel informs clients after a committed transaction; it is not the domain event bus — the order is command → transaction → state + event row → realtime notifies — so no business workflow may depend on a client being connected.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/playground/skills/design-system/SKILL.md
  - data/raw/claude-docs/akira/skills/design-system/SKILL.md
  - data/raw/claude-docs/kiez-archive/skills/design-system/SKILL.md
  - data/raw/claude-docs/diskoe/skills/design-system/SKILL.md
---

# Realtime Is UI Sync, Not the Event Bus

## Rule

akira's system-design semantics plate draws one line: **realtime is UI sync, not the domain
event bus.** The flow is

`command → transaction → state change + event row → realtime informs clients`

The event row written inside the transaction is the domain event. The realtime broadcast is
a notification that the UI should refresh.

## Why

Where a realtime channel exists and its role is unstated, someone eventually builds
`db update → realtime event → frontend notices → frontend calls API → API mutates` — and
the business workflow now **depends on a browser tab being open**. One sentence in the
design record ("realtime is UI synchronization, not the domain event bus") forecloses it.

The rule lives in the semantics plate's **async boundary** row, alongside a structured-vs-blob
row whose test is "which query does the product need". It sits with sibling principles of
the same altitude: AI output is a proposal, not a state change; one system of record per
operational capability; a deterministic fallback exists independently of the model.

## See Also
- [[Principal Write-Surface Matrix]] — related (same semantics plate)
- [[Harness Anatomy]] — related (event bus as a separate harness component)
- [[Four-Stage Design Pipeline with Backflow]] — related (part of; system stage)
- [[State Writer Never Owns Its Side Effects]] — related (DB-webhook fan-out from a sole writer; Postgres as the event bus)
