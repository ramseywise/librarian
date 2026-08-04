---
title: Situation-Indexed Decision Tree
tags: [interview, llm, pattern]
summary: Replacing a flat component table (answers indexed by noun) with a branching tree indexed by situation — one memorized trunk fork into four system spines, each node carrying a discriminator question and a rehearsable sentence.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/learn-ai-engineering/docs/plans/2026-07-30-LAE-112-interview-notes-reorg.md
---

# Situation-Indexed Decision Tree

A system-design study guide had an 11-row component table — a good reference that
answered questions **by noun**: *what is a reranker, what is a checkpointer.* Under a
live prompt, that is the wrong index. The question arriving is a situation, not a noun,
and the material offered no path from *"design a system that does X"* to which components
apply.

The diagnosis names the shape of the gap precisely: a **missing middle layer** between
the 5-step process (too abstract) and the guides (too deep). See
[[Durable vs Performative Knowledge Split]] for the two layers it sits between.

## The trunk — one fork, memorized

```
"Design X for Y" → clarify → WHAT KIND OF SYSTEM?
  ├─ looks things up in documents ──→ RAG spine
  ├─ takes multi-step actions ──────→ AGENT spine
  ├─ predicts / ranks / scores ─────→ ML spine
  └─ transforms a stream of events ─→ PIPELINE spine
```

Exactly one thing is memorized: the trunk. Everything below it is *reached*, not
recalled. The four branch labels are phrased as observable behaviours of the system
under discussion — "looks things up in documents" — rather than as architecture names,
so the classification can be made from the prompt itself before any design thinking has
happened.

Classical ML was deliberately kept as a spine rather than folded into the others.

## Duplication is the point

The tree repeats itself on purpose:

> Deliberate duplication across spines (eval/guardrails appear in all four) — **a shared
> "cross-cutting" node you must jump to is a node you forget under pressure.**

This inverts the normal DRY instinct, and the justification is specifically about the
retrieval conditions. A factored-out shared node is cheaper to maintain and free to
follow when you are reading calmly. Mid-round, a pointer is an extra hop that competes
with the thing you were about to say. Redundancy buys recall under load; the maintenance
cost of four copies of the eval node is the price.

The general rule this instantiates: **optimize the artifact for its retrieval
conditions, not for its authoring conditions.**

## Branch node format

Every node carries six fields, validated on the agent spine before the rest were built:

| Field | What it holds |
|---|---|
| **Fork** | the 2–3 real options |
| **Discriminator** | the question you ask *out loud* that picks the branch |
| **Say out loud** | the rehearsable sentence |
| **At 10×** | what changes at ten times the scale |
| **Breaks first** | the failure nobody notices |
| **Deeper** | one link down to the guide |

Three of these are doing unusual work.

**Discriminator** makes the branch selection audible. A tree that silently routes is
indistinguishable from guessing; a tree whose every fork has a question attached converts
the traversal itself into visible reasoning — the interviewer hears the requirement
being elicited before the choice is made.

**Say out loud** is retained explicitly because *"it's what makes this drillable."*
Knowing the fork is not the same as being able to state it fluently, and only the second
survives time pressure.

**Deeper** is one link, not a section. The node stays at situation grain and delegates
depth rather than absorbing it — which is what keeps the middle layer from silently
growing back into the guides it was meant to index.

**Breaks first** is a standing prompt for the failure mode nobody volunteers, matching
step 4 of the round method (name your design's weaknesses before the interviewer does).

## Rewiring, not adding

The tree does not sit alongside the old component table. The plan **rewires §3 to point
at tree nodes** — the noun index becomes a lookup surface *for* the tree rather than a
competing entry point. Two indexes over the same material is the state that produced the
gap in the first place.

## See Also
- [[Durable vs Performative Knowledge Split]] — prerequisite-for (the layering this fills)
- [[System Design Interview Study Guide]] — extends (the 5-step process above it, §3 table it rewires)
- [[Agents Interview Study Guide]] — extends (the guide the agent spine links down into)
- [[RAG Interview Study Guide]] — extends (the guide the RAG spine links down into)
- [[Timebox-Scaled Deliverable Bar]] — instance-of (advice that mis-fires when not indexed by format)
