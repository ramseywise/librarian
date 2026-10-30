---
title: Knowledge Graph as Shared Agent Memory
tags: [memory, agents, rag, llm, pattern]
summary: "Loop → swarm → graph as three capacity unlocks: parallel workers rediscover the same findings because nothing connects them, and a typed KG is what turns fan-out from re-derivation into accumulation."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph--graph-engineering.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph-engineering--notes--12-kg-as-shared-agent-memory.md
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
| **Loop** | One reflective agent generating, evaluating, revising in a bounded action space (the open-source `autoresearch`: one editable file of ~630 lines, ~5-minute experiments) | Sequential; one perspective |
| **Swarm** | Parallel workers via dynamic workflows | **Redundancy** — independent workers rediscover the same findings, because nothing connects them |
| **Graph** | A typed KG holding entities, claims, relations, and provenance across sessions | — |

The swarm tier is where the problem *appears*, and the graph tier is its answer:

> **Fan-out without shared state re-derives. Fan-out over a shared graph accumulates.**

Workers publish structured updates (a `GraphUpdate` carrying nodes, edges, run ID, agent
ID); a synthesizer traverses the shared graph **instead of requiring every worker to read
every source document.**

**All the safety lives in the write path.** A worker never writes to the graph directly: it
submits a `GraphUpdate`, a validator checks schema (node and edge types exist) and provenance
(every fact has a source span), and only then does one transaction upsert **versioned** nodes
(never overwrite), add edges and link them to the run and agent. Many writers, one
serialising, validating merge function — the [[LangGraph State Reducers]] idea at database
scale.

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

The parallel tier is the expensive one, but most of its quoted numbers are weak:

| Claim | Status |
|---|---|
| A multi-agent research system uses ~15× the tokens of a chat interaction | First-party (Anthropic engineering post) |
| Coding-agent dynamic workflows: up to 16 concurrent sub-agents, 1,000 per run | Quoted consistently by third parties; check the docs before relying on it |
| A 1,000-sub-agent run costs "tens of dollars" | Secondary; unverified |
| A large open-source language-port run cost ~$165,000 in usage | **Unverified — no primary source for the cost; do not cite** |

Two takeaways hold regardless of the exact numbers:

> Graph topology is what makes that spend **tractable**, not what makes it cheap.

And the quieter risk is **correlated errors** across workers sharing a model, prompt and
graph — a shared graph spreads a correlated error *further*, which is why the validator and
provenance come first (see [[Multi-Agent Failure Modes at Scale]]).

## Evaluating it by layer

| Layer | Metric | Common misreading |
|---|---|---|
| Extraction | Entity and relation F1 | High precision can hide missing entities |
| Resolution | Pairwise precision/recall, false-merge rate | A high compression ratio rewards over-merging |
| Query | Answer correctness **and** path validity (supported, cited edges) | A right answer through a wrong path is luck |
| Swarm | Redundant findings, tokens and quality vs a single loop | Wall-clock gains that cost quality |

Improving the extraction prompt is itself an autoresearch loop: propose one prompt or schema
change, rerun on the gold set, keep it only if precision, recall and false-merge rate improve
— [[Loop Scorekeeper]] ratchet rules applied to [[Knowledge Graph Entity Resolution]].

## Build path

Don't start at the swarm: (1) **one measured loop** with a fixed metric and reversible
actions; (2) **a role split** — generator and verifier with isolated contexts; (3) **a
persistent graph**, gated on cross-session queries working; (4) **a swarm writing to the
graph**, gated on a wall-clock gain with no loss of quality. Advance only once the current
stage is measured.

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
- [[Graph Engineering]] — extends
- [[Agent Memory Types]] — instance-of (the KG is a cross-session semantic store)
- [[Verification Loops]] — extends (isolated verifier context as a structural fix)
- [[Recursive Self-Improvement]] — extends (`autoresearch` is the loop tier of this progression)
- [[LangGraph State Reducers]] — extends (shared-write discipline for parallel branches)
- [[Knowledge Graph Entity Resolution]] — prerequisite-for (reversible merges)
- [[Graph Machine Learning and GNNs]] — extends
