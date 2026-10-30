---
title: Three-Layer Trajectory Verification
tags: [loop, eval, pattern]
summary: "Before a self-improving loop learns from a run it must verify it at three layers — outcome (was it done, by code), process (was it done in an allowed way, by code), quality (was it done well, by an item-wise LLM rubric) — and keep the verdict structured, not scalar, so it says what to edit."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--04-loop-engineering--notes--08-self-improving-loops.md
---

# Three-Layer Trajectory Verification

> **Preserving experience is not learning from it.** A vector store of trajectories lets an
> agent look up a case; it does not compare cases, separate a sound strategy from a lucky one,
> or notice a fix only worked on an old API.

An [[Evolve Loop]] is only as good as its verdict on each run. If the system doesn't know which
step caused a success or failure, a model-written reflection is a guess — and once a guess lands
in a prompt or training data it compounds. A correct outcome also doesn't prove a correct
process: tests pass when the failing tests are deleted; a customer is "satisfied" when promised
a refund that never happens.

## The three layers

Each rests on harder evidence than the one above it (framework from *AI Agents in Depth*):

| Layer | Question | Evidence |
|---|---|---|
| **Outcome** | Was the task actually completed? | Environment state, test results, tool returns — code |
| **Process** | Was it done in an allowed way? | Policies, permissions, action order — code |
| **Quality** | Was it handled well? | LLM rubric, scored item by item with cited turns |

Only what code can't formalise goes to the LLM layer.

**Promise–action consistency** is the check that matters most for agents: for every "I've
submitted your refund", confirm the refund tool was called, succeeded, and changed the order
state.

## Structured, not scalar

"Partially succeeded, one unsupported claim, one false promise, policy repeated three times"
tells the next step *what* to edit — the unsupported claim points to missing knowledge or a
citation rule, the false promise to a harness consistency check. A single 0.57 points nowhere.

- Calibrate the LLM layer against a small expert-labelled set; re-run it when the model version
  changes.
- Route low-confidence or high-risk runs to a second verifier or a human.
- Keep the **verifier and the editor separate**: the model that judges a run is not the one that
  rewrites the rules ([[Loop Scorekeeper]]).

## See Also
- [[Evolve Loop]] — prerequisite-for
- [[Loop Scorekeeper]] — extends
- [[Four Media for Agent Lessons]] — prerequisite-for
- [[Verification Loops]] — extends
