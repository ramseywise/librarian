---
title: Context Engineering
tags: [context, llm, agents, concept]
summary: "The discipline of assembling the context window — a minimization problem, not a filling problem: find the smallest set of high-signal tokens that maximizes the likelihood of the desired outcome."
updated: 2026-10-30
sources:
  - data/raw/articles/2026-07-19-context-engineering-karpathy.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context--context-engineering.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context--README.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--context-engineering.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--README.md
---

# Context Engineering

## Position in the Stack

Context engineering is the **second layer**: context contains prompts, and the harness
assembles context. Where [[Prompt Engineering]] governs the instructions themselves,
context engineering governs everything delivered alongside them — which documents, which
memory, which tool results, how much history, and how the token budget divides across all
of it.

**It inherits the weaknesses of the layer below.** A well-assembled context window cannot
compensate for poorly written instructions inside it.

Memory and tool design are **sub-components of this layer and the harness layer**, not
sibling pillars — every source that enumerates the foundations treats them as
context/harness primitives.

## The Thesis

> **Find the smallest set of high-signal tokens that maximize the likelihood of your
> desired outcome.**
> — Anthropic, *Effective Context Engineering for AI Agents*

This is a **minimization objective**, and it is the field's central counterintuition:
large windows invite filling, and filling degrades output. Context is a finite resource
with diminishing — eventually negative — marginal returns, because transformer attention
divides a fixed budget across n² token pairs.

Every technique in this pillar is a response to that constraint. See
[[Why Context Is Finite]].

## The Four Levers

The operational frame. Apply **in order** — cost rises left to right.

| Lever | Question | Detail |
|---|---|---|
| **Write** | Can this live outside the window? | [[Memory as Context]], [[Structured Context and Schemas]] |
| **Select** | What comes back in, and when? | [[Context Retrieval Strategies]], [[Index-Time Distillation]] |
| **Compress** | Can this be smaller? | [[Context Window Budgeting]], [[Context Compaction]], [[Context-Aware Compression]] |
| **Isolate** | Does this need a separate window? | [[Multi-Agent Context]] |

**Isolate is last because it is most expensive:** real tokens multiply, and cross-agent
context is lost.

## Context Types

| Type | Source | Volatility |
|---|---|---|
| Static | Role, instructions, rules | Stable across sessions |
| Dynamic | Date/time, user, environment | Per turn |
| Retrieved | Vector store, search, file reads | Per query |
| Historical | Prior states, revisions, outputs | Grows monotonically |

**Historical is the only type without a natural bound.** Compaction exists to bound it.

## Topic Notes

**Foundations**
1. [[Why Context Is Finite]] — attention budget, n² attention, context rot
2. [[Context Anatomy]] — system prompt altitude, five layers, the formal `C = A(…)` view, example selection; spun out: [[Cache-Stable Context Layout]], [[Reasoning State Pass-Back]], [[Agent Status Bar]]
3. [[Context Window Budgeting]] — the window as an economy, reserve output first, ceilings per growing component

**The levers**
4. [[Context Retrieval Strategies]] — pre-computed vs just-in-time, RAG architectures, hybrid search, framing; spun out: [[Index-Time Distillation]], [[Contextual Retrieval]]
5. [[Context Compaction]] — compaction pipeline, tool-result clearing, the production compaction ladder, memory hierarchy; experiment: [[Context-Aware Compression]]
6. [[Memory as Context]] — memory types and formats, write paths, two-tier memory; evidence check: [[Designed Memory vs Raw-Record Search]]
7. [[Structured Context and Schemas]] — format choice, input/state/output schemas, schema design
8. [[Cognitive Tools]] — understand/solve/verify as separate calls, prompt programs, bounded self-correction
9. [[Protocol Shells]] — declarative context procedures without code
10. [[Multi-Agent Context]] — sub-agent isolation, orchestrator-holds-plan, tool-integration and orchestration patterns

**Practice**
11. [[Context Failure Modes]] — rot, poisoning, distraction, clash, injection, and the diagnostic flow
12. [[Evaluating Context]] — the failure chain, metrics per lever, ablation, length/position sweeps
13. [[Context System Maturity Ladder]] — atoms to cognitive systems, four reference architectures

Appendix: [[Context Field Theory (Speculative)]] — low-confidence material, kept separate.

**Rules of thumb that span the notes:** look in the window before the weights when an
agent misbehaves; instrument each stage (exists → retrieved → survived → used); ablate
components to set budgets by evidence; climb the maturity ladder only when the rung below
fails measurably.

## Boundaries

**Downward, to prompting:** once you are deciding *what* is in the window rather than
*how* to phrase what is already there, you are in context engineering. Full table in
[[Prompt Engineering]].

**Upward, to the harness:** once assembly becomes stateful and conditional — a loop that
decides *when* to retrieve, compact, or spawn — you have crossed into harness engineering.

## Security Facet

**Context has no type system — instructions and data are the same tokens.** Prompt
injection is therefore a context-layer problem as much as a prompt-layer one, and *every
added context source is added attack surface*. See [[Prompt Injection]] and
[[Context Failure Modes]].

## See Also
- [[Tool Design as Harness Surface]] <!-- auto-linked -->
- [[Prompt Engineering]] — prerequisite-for
- [[Context Failure Modes]] — related (part of)
- [[Prompt Injection]] — related (attack surface)
- [[Harness Engineering]] — extends (the layer above: context is what the harness assembles)
- [[Harness Orchestration]] — related (subagents as the isolate lever)
- [[Long-Horizon Execution]] — extends (what to do when context runs out)
- [[Agentic Engineering and the New SDLC]] — instance-of (the six context types and the static/dynamic split, in an SDLC frame)
- [[Context Window Budgeting]] — extends
- [[Evaluating Context]] — extends
- [[Context System Maturity Ladder]] — extends
- [[Cognitive Tools]] — extends
- [[Structured Context and Schemas]] — extends
