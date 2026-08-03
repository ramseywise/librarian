---
title: Capability Runtime-Coupling Tiers
tags: [llm, patterns, pattern]
summary: Sorting agent capabilities into runtime-coupled (T1), runtime-adjacent (T2), and runtime-independent (T3) — because cross-runtime parity is a meaningful goal for T1/T2 and a category error for T3.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-20-consolidate-capability-reference.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-19-agents-skills-sync.md
---

# Capability Runtime-Coupling Tiers

A 14-capability code-gen payload looked like one flat collection of
framework-specific templates. Auditing it across four runtimes (Claude, ADK,
LangGraph, Vercel) found that **the 14 are three different kinds of thing**, with
radically different parity profiles:

| Tier | Name | Count | Parity question |
|---|---|---|---|
| **T1** | Runtime-coupled | 3 | Genuine — each runtime does it differently |
| **T2** | Runtime-adjacent | 5 | Real, needs a per-runtime table |
| **T3** | Runtime-independent | 6 | **A category error** |

## Why T3 is the load-bearing finding

Six of the fourteen are ordinary library code that happens to be called from an
agent. Asking "what is the LangGraph version of this?" is malformed — there
isn't one, because the capability never touched the runtime. For T3 the file
should carry an explicit *"host-language/library capability"* statement rather
than a parity table with four near-identical cells.

This reframes parity work: a matrix that dutifully fills in every cell for all 14
capabilities is manufacturing six rows of fake variance. The tier annotation is
what stops a future reader from trying to close a gap that does not exist.

A related classification error sat in the same list: **`langchain` is not a
capability — it is a competing framework.** It had been filed alongside things
like vision and batch because the payload's only organizing axis was "file in the
references directory."

## The missing contract layer

The audit's second finding was structural: **no contract layer existed anywhere
in the corpus.** Every file was code-first — a template with no prose stating
what the capability *means* independent of how it is implemented. That is not a
refactor; the contract has to be written from scratch.

The remedy shape, applied to all 14 files:

- an `## Agnostic contract` section at the top — what this capability is
- a `## Design notes` section — consolidated rationale
- declared tier membership
- for **T2**: a runtime-parity table across the four runtimes
- for **T3**: the explicit host-language statement
- surfaced flags for security issues, stale constants, and version-brittleness

The acceptance criterion that enforces it is negative and checkable: **no file is
code-first-only.**

## Tiers drive the ref layout

The tiering fed a three-layer documentation split — nine tooling-agnostic
`agent-*` convention refs holding the durable contracts, with framework refs
(`langgraph.md`, `google-adk.md`, `adk-vercel.md`) narrowed from prescriptive
walkthroughs to **bindings** that point into them (`"For X agents, read:
agent-architecture.md §5.1"`). The stated criteria: each binding under 300 lines,
and **no content duplication between binding and convention ref**.

An inversion the audit caught: `refs/adk-vercel.md` held the best
deployment-topology content in any store, *"buried under a framework ref where
nobody looks."* Content filed by framework when it is actually tier-independent
becomes unfindable — which is the same failure the tiering fixes at the payload
layer.

## Deferring the contested half

Roughly half the proposed canon sat on ground the research flagged as contested —
OTel GenAI attribute names, agent-memory backends, prompt-injection defense.
Writing those prescriptively *"ages badly."*

The sequencing decision: do the **mechanical migration first**. Once the payload
renders from canon, adding a contested doc later is a one-line sync change rather
than another hand-copy. Get the mechanism in place while the content is still
moving.

The same judgment ran the other way on pruning. Two capabilities were flagged as
an inversion — 30KB for the least-used capability — and deliberately **not**
deleted: they are *"written, synced, and cost only bytes; deleting working
payload to fix an aesthetic asymmetry trades a real asset for a tidier tree."*
Deprioritized in the routing table instead. See [[Complexity Floor]].

## See Also
- [[Capability Parity Audit]] — alternative-to (have/partial/gap axis vs runtime-coupling axis)
- [[Sync as Render, Not Copy]] — prerequisite-for (how the tiered canon reaches the template)
- [[AI Project Template Scaffold]] — instance-of
- [[Complexity Floor]] — constrains (a flagged asymmetry is not automatically work)
- [[Framework Selection — LangChain vs LangGraph vs Deep Agents]] — extends (the framework-vs-capability distinction)
