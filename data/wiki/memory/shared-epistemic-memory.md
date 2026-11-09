---
title: Shared Epistemic Memory
tags: [memory, agents, pattern]
summary: "A persistent key-value store that agents share, where every entry carries a timestamp, a writing-agent id and an expiry, so reads can weigh provenance and old facts expire; a design sketch from a pattern book."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-agentic-architectural-patterns-ch05-multi-agent-coordination-patterns.md
  - data/raw/papers/2026-11-08-agentic-architectural-patterns-ch06-explainability-compliance-agentic-patterns.md
---

# Shared Epistemic Memory

Shared epistemic memory is a store several agents write to and read from, built so that the reader can tell where a belief came from and how fresh it is. The pattern appears twice in the book: in chapter 5 as a coordination aid with provenance, ratings and a pruning agent, and in chapter 6 as a persistent key-value store.

## Mechanism

- Each entry records a timestamp and the id of the agent that wrote it, so a reader can discount stale or untrusted entries.
- Entries can carry a time-to-live so the store forgets on its own.
- Typed tools expose the store (read, write, update), so agents do not touch raw storage.
- A pruning agent can remove low-rated or contradicted entries.

The purpose is to stop agents acting on a belief nobody can trace.

## Limits

- No measured effect on accuracy or cost.
- The chapter 6 prose describes an update call taking a dictionary, while the code gives it a key and a value.
- Rating and pruning rules are named but not specified, and nothing addresses concurrent writers to one key.

## See Also
- [[Agent Memory Types]] — prerequisite-for
- [[Memory Lifecycle]] — related (expiry and forgetting)
- [[Agentic Coordination Patterns Catalog]] — prerequisite-for
