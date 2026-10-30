---
title: Four Media for Agent Lessons
tags: [loop, memory, pattern]
summary: "A self-improving loop must decide not only which config to edit but which medium holds the lesson — experience doc, prompt/Skill, program/harness, or weights — promoting lessons along that path as evidence builds and always choosing the smallest target that is easiest to validate and roll back."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--04-loop-engineering--notes--08-self-improving-loops.md
---

# Four Media for Agent Lessons

The [[Evolve Loop]]'s four edit targets say *which part* of a loop's config to change. A second
question: *what medium* should hold the lesson? The answer depends on how the capability is best
represented, not on how long it has been around (framework from *AI Agents in Depth*).

| Medium | Holds | Strength | Weakness |
|---|---|---|---|
| **Experience docs** | Facts, patterns, exceptions, with sources | Fast, traceable, retrieved on demand | Depends on retrieval and on the model applying it |
| **Prompt / Skill** | Judgement and procedures statable in words | Interpretable, scoped | Bloats, conflicts, gets ignored |
| **Program / harness** | Deterministic steps, hard constraints | Testable, stable, cheap to run | Costs more to build and maintain |
| **Parameters** | Perception, style, implicit strategy | Generalises, no inference overhead | Expensive to update and regress-test |

A lesson **starts as an experience doc**, is **promoted to a Skill rule** after repeated
validation, is **compiled into code** if it needs no language understanding, and goes into
**post-training** only if it really is broad implicit judgement. Rule: **choose the smallest
target that is easiest to validate and roll back.** "Don't repeat failed calls" written as a
prompt sentence is in the wrong medium — it belongs in the retry policy code.

## Experience docs come from comparison, not summary

Three layers: immutable raw trajectories (audit); a structured analysis per run; documents
induced across many runs of one task family. Recommend a strategy only when **at least two
non-failed trajectories** support it. Each doc records when it applies, the strategy, pitfalls,
exceptions, source trajectories and last-validated date; test transfer on tasks not used to
write it. Reflexion-style self-reflection can *propose* lessons — reflection is not evidence.
Verification first: [[Three-Layer Trajectory Verification]].

## Prompt learning means minimal diffs

"System prompt learning" edits notes-to-your-future-self as text where RL would edit weights.
From a cluster of similar failures, produce **one `old → new` edit with a stated scope**, check
it for conflicts with existing rules, and gate it on both the triggering boundary cases and a
**retention set** of old tasks. Batch optimisers (DSPy, OPRO, GEPA) find a strong starting prompt
offline; minimal production diffs handle the long tail. For Skills, search the library and
`patch` an existing one before creating a near-duplicate.

## Compiling workflows

A browser trajectory that repeats with different parameters can be compiled into a
parameterised script with state checks before each action, after each action, and on the final
state. It stays a `candidate` until replayed from a clean reset; any failed check moves it to
`invalid` and the agent falls back to exploring. PreAct reported an **8.5–13× speedup** on
repeated tasks. Without the final-state check you get 100% replay coverage on a task that never
completed.

## Updating the update method

An independent axis: does the loop edit an *artifact* or the *method that produces artifacts*?
Scope widens: one rule → structured context (ACE: stable-ID entries merged deterministically so
rewrites don't erode detail) → how context is built (MCE: an outer loop edits retrieval and
curation operators) → workflow graphs (AFlow) → harness code (Meta-Harness) → the optimiser
itself (bilevel autoresearch, [[Recursive Self-Improvement]]). Wider scopes cost more to search,
evaluate and attribute. **Default to a local patch**; move outward only when local fixes keep
failing on a cross-component problem. At every scope, evaluators, permission boundaries and
held-out tests stay outside what the loop can edit.

## See Also
- [[Evolve Loop]] — extends
- [[Three-Layer Trajectory Verification]] — extends
- [[Self-Modification as a Release Process]] — prerequisite-for
- [[Sleep Learning]] — prerequisite-for
- [[Training-Agent Disaggregation]] — alternative-to
