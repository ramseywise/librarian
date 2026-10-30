---
title: Loop-to-Graph Escalation
tags: [llm, agents, infra, pattern]
summary: "A loop is a graph with one node and an edge back to itself — so graph is not a maturity level you graduate to but a cost you justify, and the five signals name what a single loop structurally cannot do."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph--graph-engineering.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph--README.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph-engineering--notes--01-graph-vs-loop.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph-engineering--notes--06-when-not-to-build-a-graph.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-14-orchestrator-design.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-14-orchestrator-design.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-14-pipeline-orchestration.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-14-pipeline-orchestration.md
---

# Loop-to-Graph Escalation

## The framing

Lookup tables for "loop or graph?" are useful until the situation isn't on the list. The
framing underneath is more durable:

> **A loop is a graph with one node and an edge back to itself.**

Graph is not a different kind of system — it is the same system with more nodes. That makes
the default obvious:

> **Start with a loop, and add nodes only when a specific signal forces it. Escalation is a
> cost you justify, not a maturity level you graduate to.**

## The five signals that justify a node

Each names something a single loop **structurally** cannot do — not something it merely
does badly.

| Signal | Why the loop fails |
|---|---|
| **Distinct specialties** — roles needing different instructions, context, tools | One agent context-switches between jobs, carrying each role's baggage into the next |
| **Parallel fan-out + join** — process many items, then merge | A loop is sequential; the wall-clock cost is unnecessary |
| **Per-step model/tool variation** — different model or restricted toolset per stage | One agent enforces a uniform model and tool policy |
| **Auditable control flow** — regulated work needing explicit path tracing | Emergent loop paths are hard to reconstruct after the fact |
| **Overloaded verifier** — one check judging several criteria | A dedicated reviewer node removes the criteria confusion |

## The 30-second decision tree

Start with a loop, then ask in order:

1. Does the work split into **distinct specialties** with different needs?
2. Do you need **true parallelism** (fan-out then join)?
3. Do different steps need **different models/tools**, or **auditable** branching?
4. Is **one verifier failing** because it judges too many criteria at once?

**Yes to any → add a node. No to all → strengthen the verifier and ship the loop.**

> That last clause is the one people skip. **The most common "we need a graph" is really an
> overloaded verifier**, and splitting the verifier is far cheaper than splitting the
> system.

This is the same diagnosis [[Verification Loops]] makes from inside the loop: a check that
judges too much at once grades generously. The graph answer is a dedicated reviewer node;
the loop answer is a narrower rubric. **Try the loop answer first.**

## The true-dependency test

For deciding what parallelizes, one question suffices:

> **Does the next step actually read the previous step's output?**

If not, the serialization is incidental and belongs in a fan-out. If yes, it is a true
dependency and the edge is real. Most "sequential" pipelines contain more incidental
serialization than their authors assume.

## The situation table

| Situation | Use |
|---|---|
| Single agent, tool-augmented reasoning cycle | Loop ([[Loop Engineering]]) |
| Open-ended research with unknowable steps | Harness + loop, **not** a graph |
| Multiple agents with conditional handoffs | Graph |
| 3+ independent verification steps | Graph (parallel review) |
| Long-running work needing fault tolerance and resume | Graph (checkpointed persistence) |
| Human approval mid-execution | Graph (interrupt/resume) |
| Parallel specialists merging results | Graph (fan-out/fan-in with reducers) |
| Simple task, low per-cycle pass rate | Loop (graph fan-out cost isn't recovered) |
| Structured world knowledge for retrieval | [[Knowledge Graph Retrieval]] |

## The cost of a premature graph

More prompts to maintain, cross-node state synchronization, coordination latency, and
harder debugging — **all pure overhead when the problem was single-specialty to begin
with.**

This meets the cost argument from the other direction: a vendor blog puts graph break-even
around a ~50% per-cycle pass rate at ~3× the tokens per cycle — **vendor estimates, a shape to
test rather than constants**; measure your own break-even. Below that bar you are paying
fan-out cost for work that will be redone anyway.

## Design checklist

- [ ] Have you named which of the five signals forces the node? *(If the answer is "it feels cleaner," you have not justified the cost.)*
- [ ] For a suspected overloaded verifier: have you tried **splitting the rubric** before splitting the system?
- [ ] For each proposed parallel branch: does the next step actually read the previous step's output?
- [ ] Can you name every node before the run starts? *(If not, you want a harness with a good loop.)*
- [ ] Is the per-cycle pass rate plausibly above ~50%?
- [ ] Are you starting at 3–5 nodes rather than the full topology?

## Applied: graph the band whose nodes you can name (galactus)

The galactus control-plane design applied the "can you name every node before the run?"
test band by band and got opposite answers: the BUILD sequence (research → plan → refine →
execute → review) is nameable and is where the loop-backs live — **graph**; the FRAME band
is entered by intent and its nodes cannot be named in advance — **loop** (a graph there
"would be a fiction with a DESIGN.md at the end of it"). Review was already orchestrated,
and capability skills have no position at all.

On cost: the ~3× is **per cycle, not per run** — a graph paused at a human seat is not
cycling, so the multiplier lands on loop-backs specifically, and with zero observed
loop-back traversals the measured multiplier would be near 1×. Further levers: graph only
the qualifying band, run mechanical nodes on a cheap model tier, bound loop-backs tightly.
The deciding number is the per-cycle pass rate, which nobody had measured — so the design
shipped the documented contract first and let its hook-recorded transitions produce that
rate (see [[Decision-Seat Inventory for a Control Plane]]).

## See Also
- [[Recursive Self-Improvement]] <!-- auto-linked -->
- [[Knowledge Graph as Shared Agent Memory]] <!-- auto-linked -->
- [[Graph Engineering]] — extends
- [[Loop Engineering]] — extends (the default you escalate from)
- [[Verification Loops]] — extends (the overloaded verifier is the most common false signal)
- [[Loop Termination Design]] — extends
- [[Multi-Agent Topology Patterns]] — prerequisite-for (which shape to escalate to)
- [[Loop Scorekeeper]] — extends (splitting the verifier into per-criterion checks)
- [[Graph Topology Primitives]] — extends
- [[Design Dry-Run Simulation]] — extends (the design stage that tests the 'overloaded verifier' question)
- [[Right-Sizing a Document-to-LLM Pipeline]] — instance-of (a 7-step pipeline with one repair loop that does not earn a graph framework)
- [[Decision-Seat Inventory for a Control Plane]] — instance-of (graph BUILD, loop FRAME)
- [[Artifact-Canonical Stateless Driver]] — extends
