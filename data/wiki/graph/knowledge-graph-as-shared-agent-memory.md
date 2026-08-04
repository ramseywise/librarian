---
title: Knowledge Graph as Shared Agent Memory
tags: [memory, agents, rag, llm, pattern]
summary: "Loop → swarm → graph as three capacity unlocks: parallel workers rediscover the same findings because nothing connects them, and a typed KG is what turns fan-out from re-derivation into accumulation."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph--graph-engineering.md
---

# Knowledge Graph as Shared Agent Memory

The agent-graph / knowledge-graph split in [[Graph Engineering]] is a distinction of
**kind, not of deployment**. In a multi-agent system the KG is frequently the *shared state
layer the execution graph coordinates through* — the same structure described in
[[Knowledge Graph Retrieval]], used on the write path.

## Three capacity unlocks

The progression is best read as capacity unlocks rather than three competing
architectures:

| Tier | What it is | What it can't do |
|---|---|---|
| **Loop** | One reflective agent generating, evaluating, revising in a bounded action space (Karpathy's `autoresearch`: ~630 lines, 5-minute iterations) | Sequential; one perspective |
| **Swarm** | Parallel workers via dynamic workflows | **Redundancy** — independent workers rediscover the same findings, because nothing connects them |
| **Graph** | A typed KG holding entities, claims, relations, and provenance across sessions | — |

The swarm tier is where the problem *appears*, and the graph tier is its answer:

> **Fan-out without shared state re-derives. Fan-out over a shared graph accumulates.**

Workers publish structured updates (a `GraphUpdate` carrying nodes, edges, run ID, agent
ID); a synthesizer traverses the shared graph **instead of requiring every worker to read
every source document.**

## The load-bearing claim

> **"The agent forgets, the graph does not."**

The KG serves three roles at once — **shared memory, grounding layer, and persistent world
model** — which is what buys cross-session investigation, contradiction tracking, and audit
trails **that survive individual agent failure**. That last property is the one a
conversation log cannot provide: a crashed agent takes its context with it, but its
published edges remain.

## The model-tiered extraction pipeline

| Stage | Model tier | Output |
|---|---|---|
| Extract | Haiku-class | Schema-constrained structured output |
| Resolve | Sonnet-class | Entity clustering, alias merging |
| Assemble | *(deterministic)* | NetworkX `MultiDiGraph` + provenance |
| Query | Sonnet-class | Bounded subgraph, edges cited |

Note the shape: **cheap model under a constrained schema for extraction, stronger model for
resolution, no model at all for assembly.** This is the [[Graph Topology Primitives]]
agency-budget rule applied to a pipeline — assembly is deterministic because it can be, and
paying a model for it would buy only variance.

## Five planes

Control, execution, artifact, graph, evaluation — kept separate to guard against the
anti-pattern named as:

> *"The chat transcript became the database."*

**If your only durable record of a run is its conversation log, you have no graph.**

## The non-negotiables

> A false merge in the graph, or a biased ontology, contaminates every downstream inference
> — and **unlike a bad loop iteration, it persists.**

Two hard requirements follow:

- **Entity resolution must be reversible.** A merge you cannot undo is a merge you must get
  right the first time, which nothing guarantees.
- **Provenance must be complete.** Without it you cannot identify what a bad merge
  contaminated.

This is the per-hop accuracy warning from [[Knowledge Graph Retrieval]] restated as a
**write-path** concern: bad edges don't just degrade retrieval, they **poison shared memory
for every agent that reads after them**.

## Cost of the swarm tier

The parallel tier is the expensive one:

- Dynamic workflows cap at **1,000 sub-agents per workflow, 16 concurrent**; a 1,000-agent
  run costs tens of dollars — with **correlated errors across workers as the quieter risk**
  (fan-out multiplies a shared wrong assumption instead of averaging it out).
- At the extreme: Bun's Zig-to-Rust port — ~50 workflows, peak parallelism 64, 535k → 1M+
  lines in 11 days, at roughly **$165,000** in usage.

> Graph topology is what makes that spend **tractable**, not what makes it cheap.

## Two safeguards that only matter once work is parallel

- **Verifiers need isolated context**, not shared conversation history — *a verifier that
  can see the generator's reasoning tends to ratify it* (self-agreement bias). This is the
  structural fix for the generous-self-grading failure in [[Verification Loops]].
- **Workers need isolated file spaces**, or parallel writes overwrite each other — the
  filesystem counterpart of the reducer rule in [[LangGraph State Reducers]].

## See Also
- [[Harness Engineering]] <!-- auto-linked -->
- [[Graph Governance and Attribution]] <!-- auto-linked -->
- [[Harness Orchestration]] <!-- auto-linked -->
- [[n8n AI Workflow Builder]] <!-- auto-linked -->
- [[Knowledge Graph Retrieval]] — extends (same structure, read path)
- [[Graph Engineering]] — part-of
- [[Agent Memory Types]] — complements (the KG is a cross-session semantic store)
- [[Verification Loops]] — complements (isolated verifier context as a structural fix)
- [[Recursive Self-Improvement]] — complements (`autoresearch` is the loop tier of this progression)
- [[LangGraph State Reducers]] — complements (shared-write discipline for parallel branches)
