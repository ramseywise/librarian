---
title: Decision-Seat Inventory for a Control Plane
tags: [langgraph, llm, pattern]
summary: "Before automating a human-run agent pipeline, list every decision point with the evidence it needs and who makes it today; a seat is automatable only when its decision is derivable from artifacts the pipeline already produces, some seats are permanent, held seats must be hook-enforced before any driver exists, and the manual run must record the transitions the automated design will need."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/docs/plans/2026-08-14-orchestrator-design.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-14-orchestrator-design.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-14-pipeline-orchestration.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-14-pipeline-orchestration.md
---

# Decision-Seat Inventory for a Control Plane

From the galactus orchestrator design: a prototyping pipeline where the operator types
`/proto-research`, reads the output, decides it is good, types `/proto-plan`, and so on —
*typed, not orchestrated*. The question was what should become a driver. The answer started
with an inventory, not a graph.

## The inventory

One row per decision: what is decided, the evidence it needs, who decides today, and
**automatable when**. The rule for the last column:

> A seat is automatable when its decision is derivable from artifacts the pipeline already
> produces. A seat whose decision needs information that exists only in the operator's head
> is not a tooling gap — it is the definition of the seat.

What fell out of the galactus table (11 seats):

- **Permanent seats exist.** "Is this worth starting?" (priority is exogenous), "is the
  goal understood?" (interview answers exist nowhere else) and "does this merge?" (computed
  verdict, human decision) never automate. A design claiming full automation is wrong about
  these or quietly deciding them badly; the driver is automated *around* them.
- **The automated half was already the reviewed half.** Review-dimension selection was
  fully derived and the verdict computed — the one band with a deterministic spine. That
  band proves the **control primitives** (derive-don't-enumerate, three-way outcomes,
  validated schema, bounded retry) but *not* the topology: review is stateless fan-out over
  a known artifact; build is state mutation with feedback. Treating a feedback pipeline as
  a bigger fan-out is the mistake to avoid.
- **Self-assessment is not a gate.** "Is the plan execute-ready?" judged by the plan's own
  author never hands over alone.
- **Classification automates, prediction stays asked.** Track detection over an existing
  diff is a classification; track selection for work not yet written is a prediction under
  asymmetric cost (see [[Auditable Track Router]]).
- **One seat had no writer at all** — "is the work done?" — see
  [[Map Every State to Its Writer]].

## Control plane, not orchestrator

Renamed deliberately: the thing being designed *governs* work done by AI workers and humans
— a **sequencer**, a **dispatcher**, a **gatekeeper** — rather than doing the work. Every
pause must be legible ("why are we stopped?" names the unmet precondition). The principle:
*the LLM proposes and decides within a bounded remit; deterministic infrastructure controls
what it is allowed to do.* The failure prevented is orchestration logic in skill prose —
"it reads as working, is invisible when ignored."

Layer ownership: hooks own transition legality and held seats; Python owns derivation,
verdicts and loop-bound counting; skills own judgment inside a phase, never sequencing;
subagents own bounded parallel work under one remit.

## Ordering constraints

1. **Make the state machine honest first** — a writer for every state.
2. **Held seats move to hooks before the driver exists.** A gate defended only by prose
   (e.g. "refuse to advance on NOT-READY even when asked") gets *weaker* under a driver: a
   driver that can write `Status:` can write past it. Hard ordering, not preference.
3. **Generalize the proven derivation** (derive the active set, assert completeness).
4. **The HITL run is the instrumentation.** A doc at `PLANNED` looks identical whether it
   arrived fresh or on a second pass after review blockers, so the loop-back had zero
   observed traversals and no way to tell rare from unrecorded. The manual version must
   write down its transitions, because *the automated design cannot be validated without the
   data the manual one is throwing away* — runs started/completed, loop-back count, human
   interventions per run, tokens and latency per cycle.
5. **Then decide the graph** — on measured re-plan probability and cost, not taste (see
   [[Loop-to-Graph Escalation]]).

Every deferred seam must degrade gracefully: if the growth never happens, what shipped still
works — "the test for whether a seam is a seam or a stub."

## The next contract

The question after graph-vs-loop: *what must a worker return so the control plane can safely
decide what happens next?* Do not invent a new one — an enforced review finding schema
already has the properties (typed result, mechanical rejection not repair, in-band proof the
worker loaded its remit, quoted evidence, confidence orthogonal to impact, provenance). A
phase result adds two fields review never needed: **what remains unknown** and **what would
change your answer**. Derive it from a phase that needs it, not in advance.

## See Also
- [[Artifact-Canonical Stateless Driver]] — extends (where the driver's state lives)
- [[Map Every State to Its Writer]] — prerequisite-for
- [[Observed Transitions, Not Declared]] — prerequisite-for (hook-enforced transitions)
- [[Loop-to-Graph Escalation]] — extends (graph only the band whose nodes are nameable)
- [[Capability vs Phase Skills]] — extends (capabilities have no seat in the sequence)
- [[Quoted Span as Proof of Reading]] — extends (evidence property of the worker contract)
- [[HITL Gradient]] — extends (L3's seat set is cited from this table)
- [[Control Plane Owns the Join, Not the Truth]] — extends (the observer-side counterpart: reconcile before dispatching)
