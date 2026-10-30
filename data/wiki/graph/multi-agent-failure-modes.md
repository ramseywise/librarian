---
title: Multi-Agent Failure Modes at Scale
tags: [graph, agents, eval, reference]
summary: "A single loop fails by not converging; a graph fails mechanically (cycles, deadlocks, races, unbounded fan-out, mis-routing) and through control failures between loops — and swarm-scale faults like correlated errors and Byzantine workers are caught only by independent checks and anchors."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph-engineering--notes--07-failure-modes-at-scale.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph-engineering--notes--02-graph-primitives.md
---

# Multi-Agent Failure Modes at Scale

How graphs fail where single loops don't. Two families:

| Family | Comes from | Examples | Caught by |
|---|---|---|---|
| **Mechanical** | The wiring | Infinite cycles, races on shared keys, unbounded fan-out, mis-routing | Mostly the framework, if you let it |
| **Control** | Many feedback loops interacting | Goodhart, upward blindness, inter-loop conflict, measurement decay | Nothing, unless designed for |

## Mechanical failures

| Failure | Symptom | Root cause | Fix |
|---|---|---|---|
| **Oscillation / infinite cycle** | Run never ends; two nodes alternate | Unbounded back-edge | Attempt counter in state checked by the router, plus a deliberate `recursion_limit` (LangGraph default: 25 super-steps, raises `GraphRecursionError`) |
| **Deadlock** | Run stalls at a join | A join waits on a branch never scheduled, or mutual waiting | Make every join's inputs explicit; error paths still write the expected key |
| **Race on shared state** | `InvalidUpdateError`, or silently lost work outside LangGraph | Parallel branches write one key with no reducer | One writer per key or a reducer ([[LangGraph State Reducers]]) |
| **Unbounded fan-out** | Token spikes, rate limits | `Send` over an uncapped input | Cap N; batch; budget per run *and* per node |
| **Mis-routing** | Right answer from the wrong specialist, or a confident wrong one | Vague router prompt; drifting status values | Treat the router as a classifier with its own labelled test set |
| **File-space collision** | Parallel workers overwrite each other | Shared working directory | One worktree or directory per worker |

**Every looping node is bounded on its own**, not only the graph as a whole — the
[[n8n AI Workflow Builder]] caps Discovery at 50 iterations and Builder at 100 per session.

## Swarm-scale failures

These appear only once work is parallel or spread across agents.

- **Correlated errors.** Parallel workers share a model, prompt template and retrieval index,
  so they make the same mistake. N agreeing workers are much weaker evidence than N
  independent ones, and a vote-counting synthesiser is confidently wrong. Vary sources,
  prompts and models; make the synthesiser check claims against sources, not against each
  other.
- **Self-agreement bias.** *A verifier that can see the generator's reasoning tends to ratify
  it.* Give the verifier the task and the output, never the conversation that produced it —
  the graph form of the maker/checker split in [[Loop Scorekeeper]].
- **Byzantine, not crash.** Distributed systems separate crash faults (a node stops) from
  Byzantine faults (a node keeps running and returns wrong answers). Agents fail the second
  way: a hallucinating worker still returns a well-formed summary. Timeouts and retries catch
  crashes; only **cross-validation, voting over independent sources and deterministic checks**
  catch Byzantine faults.
- **Semantic conflicts.** Locks and reducers prevent *lost updates*; they do not prevent two
  successful writes whose combination is wrong (two agents each insert a figure and renumber,
  leaving every number off by one). Optimistic locking (write only if the version you read is
  unchanged) turns the silent conflict into a retry; one worktree per agent surfaces conflicts
  at merge time.
- **Cascading amplification.** An early error becomes a premise downstream. In a translation
  pipeline, a glossary agent mistranslated a key term; the translator applied it faithfully
  and the proofreader, checking against the glossary, saw perfect consistency. Every stage did
  its job and the error survived all of them. The fix is a check from an **independent
  perspective**: review the output against the source, not against the upstream artifact.
- **Runaway loops** cost three ways: tokens, comprehension debt, and cognitive surrender. Only
  the first shows up on the bill.

### MAST taxonomy

MAST (Multi-Agent System failure Taxonomy) classifies 14 failure modes from annotated traces
(inter-annotator κ = 0.88) into three groups: **system design** (disobeying role specs, step
repetition, losing history, not knowing when to stop), **inter-agent misalignment** (ignoring
input, withholding information, reasoning–action mismatch, derailing) and **missing
verification** (premature termination, absent or incorrect verification). Fixing prompts and
roles in one studied system improved it by only **+15.6%**: most failures are structural and
need topology or verification changes, not better wording.

## Control failures

A control-theory reading (from a vendor blog; each failure has an older name):

| Failure | What happens | Older name |
|---|---|---|
| **Goodhart** | A metric detaches from its meaning under hard optimisation | Goodhart's law |
| **Upward blindness** | A loop cannot question its own target | A controller can't see its setpoint |
| **Inter-loop conflict** | Independent loops fight over shared resources | Coupled control loops |
| **Measurement decay** | Sensors and definitions drift under running loops | Sensor / concept drift |

Counters: **paired metrics** (every optimised metric gets a counter-metric and an anchor),
**owned references** (targets owned by slower loops), **separated cadences** (fast loops
escalate rather than override), **frozen nodes** (some measurements deliberately untunable).

> **Anchors are "external fixed nodes the internal machinery is forbidden to rewrite"** —
> held-out test sets, physical counts, banked revenue, safety specs. Without them a graph
> becomes perfectly self-consistent while drifting arbitrarily far from reality. An anchor
> made tunable will eventually be tuned. This is the immutable layer of the
> [[SANYI Change-Contract System]].

## Pre-flight check before running a graph unattended

- [ ] Every back-edge has a counter; `recursion_limit` is set deliberately.
- [ ] Every looping node has its own iteration bound.
- [ ] Every shared key has one writer or a reducer.
- [ ] Every `Send` has a cap on N.
- [ ] Every verifier sees the task and output, not the generator's reasoning.
- [ ] Parallel workers have separate file spaces.
- [ ] Every reviewer can check against something the producer didn't write (tests, sources, execution).
- [ ] At least one anchor the graph cannot edit, and someone watching it.

## See Also
- [[Graph Engineering]] — extends
- [[Multi-Agent Topology Patterns]] — extends
- [[Loop Termination Design]] — extends
- [[Loop Detection and the Two-Retry Rule]] — extends
- [[Verification Loops]] — extends
- [[SANYI Change-Contract System]] — extends
