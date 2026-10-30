---
title: Cognitive Tools
tags: [context, llm, agents, pattern]
summary: "Reasoning steps packaged as callable prompts (understand, recall, examine, backtrack), each run in its own isolated context — prompting alone lifted a non-reasoning model on a maths benchmark from 26.7% to 43.3%, best when the model chooses which tool to call; gains shrink on reasoning models, and a deterministic check beats a model verifier wherever one exists."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--08-cognitive-tools.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--13-putting-it-together.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--references.md
---

# Cognitive Tools

A cognitive tool is a **reasoning step packaged like a function**: a named prompt with
inputs and outputs that the model — or your code — can call. It brings the reusability of
code to the way context is structured for reasoning.

## The Evidence

A 2025 research paper (*Eliciting Reasoning in Language Models with Cognitive Tools*)
gives a model four tools, each a separate prompt callable like a tool:

| Tool | Does |
|---|---|
| `understand_question` | Identify core concepts, givens, goal, relevant techniques |
| `recall_related` | Retrieve analogous solved problems and their steps |
| `examine_answer` | Check the current trace for errors, unmet constraints, miscalculations |
| `backtracking` | When stuck, locate where reasoning went wrong and propose an alternative |

**Each tool runs in its own context** — the call carries only what that step needs, and
only the result returns to the main trace. That is isolation ([[Multi-Agent Context]])
applied to reasoning. Result: GPT-4.1 on AIME 2024 rose from **26.7% to 43.3%**, near
o1-preview, with similar gains on open-weight models — no training, only structured
prompting. **The best results came when the model chose which tool to call and when**, not
from a fixed sequence.

**Caveat:** these are maths benchmarks on non-reasoning models. Reasoning models already
run something like this loop internally; explicit scaffolding adds less and can get in
the way.

## Template Families

| Family | Templates | When |
|---|---|---|
| Understanding | Question analysis, extraction, structure analysis | *Before* solving |
| Reasoning | Step-by-step, compare-contrast, causal, hypothesis test, decision matrix | *During* |
| Verification | Solution check, fact check, consistency check, error analysis | *After* |
| Composition | Sequential, conditional, iterative chains | Orchestrating tools |

Two template details carry the value:

- An understanding template must **end with "Then stop. Do not answer yet."** A template
  that analyses and answers in one pass collapses back into ordinary [[Chain of Thought]].
- A verification template must **end with a machine-readable verdict**
  (`Verdict: CORRECT | ERRORS_FOUND`) — that line is what lets code drive a loop.

## The Bounded Self-Correction Loop

```
solve → verify ─┬─ CORRECT ─────────────► done
                └─ ERRORS_FOUND → correct → verify   (max N iterations)
```

**Bound it.** A same-model verifier shares the solver's blind spots, so loops beyond 2–3
iterations rarely help, and the model can "fix" a correct answer into a wrong one. Where a
ground-truth check exists (tests, a calculator, a schema validator), use it instead of a
model verifier. See [[Loop Termination Design]].

## Prompt Programs

A prompt program applies programming structure to a prompt: **named operations with
parameters, composed with control flow** (e.g. `analyze_tradeoffs(options, criteria,
weight_by)` with numbered steps and a declared return). Explicit steps turn an open request
into a procedure; parameters make it reusable; the declared return fixes the output shape.
Programs compose (`understand → analyze → verify`), branch, and loop.

| | Cognitive tool | Prompt program |
|---|---|---|
| Unit | One reasoning operation | A multi-step procedure |
| Caller | The model, when it decides | Your code, or the prompt itself |
| Context | Ideally isolated per call | Usually one window |
| Strength | Model chooses *when* to think harder | Repeatable, auditable method |

The no-code rendering of the same idea is [[Protocol Shells]].

## When to Reach for It

- **Yes:** multi-step reasoning on non-reasoning models; cheap checks guarding expensive
  errors; procedures you run repeatedly and want to audit.
- **No:** simple lookups; reasoning models on tasks they already handle; anywhere a
  deterministic check can replace a model judgment.

## See Also
- [[Chain of Thought]] — extends
- [[Multi-Agent Context]] — instance-of (isolation applied to reasoning steps)
- [[Loop Termination Design]] — prerequisite-for (bounding the verify loop)
- [[Protocol Shells]] — alternative-to (the same structure without code)
- [[Context System Maturity Ladder]] — prerequisite-for (the "cognitive system" rung)
