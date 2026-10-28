---
title: Artifact-Canonical Stateless Driver
tags: [langgraph, llm, pattern]
summary: "In a pipeline where humans edit the markdown artifact during manual intervention, the driver must hold no durable state — it re-reads the artifact's fields at the top of every iteration and derives everything else, so operator edits always win, crash recovery is free, and anything the driver needs to remember must become a field in the artifact."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/docs/plans/2026-08-14-orchestrator-design.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-14-orchestrator-design.md
---

# Artifact-Canonical Stateless Driver

An early draft of the galactus control-plane design made the driver's own store
authoritative and the plan doc's `Status:` a "human-readable projection." Design review
called that backwards and the design's most dangerous loose end: operators edit markdown
directly during manual intervention — that *is* the HITL mode — so a driver store and a
hand-edited file diverge, and nothing reconciles them.

## Resolution

**The artifact on disk is canonical; the driver holds no durable state.** It re-reads
`Status:`, `Epistemic:`, `Review:` and companion fields at the start of every loop
iteration and derives everything else. The driver is a loop over
`read → derive → dispatch → write`.

Three reasons, the last decisive:

1. **Operator edits always win**, with no merge logic — there is nothing to merge.
2. **Crash recovery is free.** A killed driver restarts by reading the file; no
   half-written store to repair.
3. **The artifacts were not in git** (plan docs were globally ignored), so a driver store
   would have been the only durable record of state whose source of truth is *not* in
   version control — divergence undetectable and unreconstructable. Re-reading makes it
   structurally impossible rather than unlikely.

## The cost, stated

Derived-only state means the driver cannot know anything the artifact does not record.
**Anything the control plane must remember has to become a field, not a variable** — the
first such field was the loop-back count needed to measure re-plan frequency. It also
shrinks the build: no state store, no schema migration, no reconciliation.

The deferred growth path is explicit: a driver-owned store with `Status:` as projection
becomes justified only when a loop-back is traversed and the doc cannot express the second
pass.

## See Also
- [[Decision-Seat Inventory for a Control Plane]] — extends
- [[Plan-Doc Status Enum]] — prerequisite-for (the fields being re-read)
- [[Hydration Gap Silent Input Loss]] — extends (the opposite failure: state not re-read)
- [[Sync as Render, Not Copy]] — extends (derive from the source of truth, never copy it)
