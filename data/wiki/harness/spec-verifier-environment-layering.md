---
title: Spec, Verifier, Environment Layering
tags: [harness, llm, concept]
summary: "A practitioner framing of working with coding agents as three layers that all transmit your understanding — a spec (the goal, not the task, in small agile slices), a verifier (criteria before work, a second model as critic, an external ground-truth signal), and an environment (operating contract, knowledge base, skills, and hooks for what must never happen)."
updated: 2026-10-17
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness--karpathy-method.md
---

# Spec, Verifier, Environment Layering

A secondary-source distillation of a 2026 Karpathy talk, relayed by a video breakdown.
**Confidence: medium.** The direct material is the quotes and the "animals vs ghosts" model.
The three-layer packaging comes from the video, not from Karpathy. Treat it as a useful
framing of [[Harness Engineering]] from the operator's side, not as a primary claim.

> "You can outsource your thinking, but you can't outsource your understanding."

## The gap it addresses

The car-wash test asks: *"The car wash is 50 m away — should I drive or walk?"* Models answer
"walk", because distance can be measured and the fact that the car has to be at the car wash is
context. **Models are strong on what can be measured and blind to context they were never
given a signal for.** Each layer below is a way to deliver that context in a form the model
can act on.

## Layer 1 — the spec

- **Uncover the goal, not the task.** "Make an end-of-month report" is a task. The goal is the
  decision the report drives, and that is the one thing a model cannot infer. Extract it
  deliberately (e.g. "interview me to identify the goal"). This is the same move as
  [[Scope-POC Design Interview]].
- **Agile specs, not waterfall.** People hand an agent everything at once because delegating
  feels efficient. Use small, compartmentalised specs with a checkpoint after each one.
  Plan mode is not wrong. It is too high-level.
- **Force sign-off on assumptions.** Every assumption the model makes unasked is a chance to
  drift. When the model drafts the spec, make it surface key decisions for explicit
  verification.

## Layer 2 — the verifier

**Animals vs ghosts.** Humans respond to pressure. Models are "statistical simulation
circuits": they answer from the books in their library, do not know which books are missing,
and improvise confidently. "Make this better" is not a lever. **Verification is the lever.**

| Move | Mechanism |
|---|---|
| **Criteria before work** | Define "good" precisely before generating ("three sections, each ends with a recommendation") — eval-first |
| **Second librarian** | A *different* model critiques the first, so the critic draws on a different library (asymmetric QA) |
| **External signal** | Wire in the system that holds ground truth: the deploy target for "did it deploy", past reports for format conformance |

A quoted practitioner claim is that a feedback loop multiplies final quality by 2–3×. The depth
treatment is [[Verification Loops]].

## Layer 3 — the environment

The spec is the blueprint on the wall, the verifier is the QA station by the door, and the
environment is the workshop itself. Most people rebuild it every session. It has four parts:

1. **Operating contract** (`CLAUDE.md`): layout, skill routing, where to look for what,
   standing rules. "It's your world and AI is living in it."
2. **Personal knowledge base.** Your own curated material, structured so the model knows
   where things live ([[Karpathy LLM Wiki Pattern]]).
3. **Skills for anything repeated.** Use exposes where a skill leaks ("run water through the
   hose"), so the system compounds.
4. **Rules vs requests.** A `CLAUDE.md` line is a request the model can ignore. A pre-tool-use
   hook that blocks the write is a rule it cannot. Sort behaviours into **always-do**,
   **ask-first**, and **never-do**, and enforce never-do with hooks, not prompts. The
   enforcement level should match the cost of getting it wrong
   ([[Execution Boundaries and Guardrails]]).

## The common bottleneck

All three layers carry the same input: *your* understanding of the goal, of what good looks
like, and of what must never happen. Better layers cannot make up for that input being
missing.

## See Also
- [[Harness Engineering]] — extends (the same harness described from the operator's chair)
- [[Verification Loops]] — prerequisite-for (depth on the verifier layer)
- [[Execution Boundaries and Guardrails]] — extends (never-do as hook-enforced rules)
- [[Scope-POC Design Interview]] — instance-of (goal extraction by interview)
- [[Karpathy LLM Wiki Pattern]] — instance-of (the knowledge-base component of the environment)
