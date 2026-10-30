---
title: Context System Maturity Ladder
tags: [context, agents, reference]
summary: "Five rungs of context machinery — single instruction, plus examples, plus carried state, plus coordinated specialist contexts, plus reasoning tools and verification — with the rule to climb only when the rung below fails measurably, seven recurring patterns, four reference architectures, and the order of design questions."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--13-putting-it-together.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--README.md
---

# Context System Maturity Ladder

How the levers of [[Context Engineering]] combine into systems, and how much machinery a
problem actually needs. The course frames it with a biological metaphor; read as a ladder:

| Rung | Course name | In the window |
|---|---|---|
| 1 | Atom | One instruction: task + constraints + output format |
| 2 | Molecule | + examples (few-shot) |
| 3 | Cell | + memory: state carried across turns |
| 4 | Organ | Several specialised contexts coordinated by an orchestrator |
| 5 | Cognitive system | + reasoning tools, schemas, verification loops |

**Climb only when the rung below fails measurably.** Most production failures at rung 4
are rung-2 problems — the examples or instructions were never right. Each rung multiplies
cost and failure modes ([[Context Failure Modes]]).

## Seven Recurring Patterns

| Pattern | Does | Lever |
|---|---|---|
| Structured state | Small overwritten state block instead of raw history | Write / Compress |
| Progressive context | Start minimal; identifiers first, contents on demand | Select |
| Verification loop | Generate → check → revise, bounded, machine-readable verdict | reasoning |
| Structured schemas | Fixed input, state, output shapes | all |
| Template programs | Parameterised reusable prompt procedures | all |
| Personalisation | User model outside the window, selectively injected | Write / Select |
| Phased processing | Phases with a compaction point between them | Compress / Isolate |

## Four Reference Architectures

1. **Long-form document generation** — the outline is persistent state; each section is
   written with the outline, a running summary of prior sections, and its own evidence —
   never the full prior text. The window stays constant-size however long the document.
2. **Problem solver with memory** — the [[Cognitive Tools]] loop (understand → recall →
   solve → examine → backtrack) with a memory write at the end, so solved problems become
   future `recall_related` hits.
3. **Research assistant** — orchestrator holds plan and synthesis; one sub-agent per
   question explores in its own context and returns condensed findings; claims verified
   against sources at the end ([[Multi-Agent Context]]).
4. **Adaptive tutor** — a stored learner model (mastery per concept, misconceptions,
   preferences) injected as a short summary each turn; the model never sees the full
   interaction history, only the current estimate of the learner.

**Reconstructive memory** — storing fragments with source pointers and assembling a
task-specific memory at retrieval time — is sound retrieval-plus-synthesis, with a real
risk: the synthesis can confabulate connections between fragments. Keep source pointers
so a reconstruction can be checked.

## The Order of Design Questions

1. What does success look like, and how is it measured? Build the eval set first
   ([[Evaluating Context]]).
2. What is the smallest window that could work? Start at rung 1 or 2.
3. What does the model lack? Facts → retrieval; continuity → memory; method → cognitive
   tools.
4. What grows? Give it a ceiling and a compaction rule ([[Context Window Budgeting]]).
5. What can live outside the window? Write before Select, Select before Compress, Isolate
   last.
6. What can go wrong? Walk the failure modes before shipping.

When the loop assembling the context becomes stateful and conditional, the problem has
crossed into [[Harness Engineering]].

## See Also
- [[Context Engineering]] — extends
- [[Evaluating Context]] — prerequisite-for
- [[Cognitive Tools]] — extends (rung 5)
- [[Multi-Agent Context]] — extends (rung 4)
- [[Harness Engineering]] — prerequisite-for
