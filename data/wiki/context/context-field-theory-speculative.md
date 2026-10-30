---
title: Context Field Theory (Speculative)
tags: [context, llm, reference]
summary: "Provisional — the neural-field / attractor / resonance / quantum-semantics vocabulary from part of a context-engineering course is metaphor, not method; only three ideas survive translation (early framing is sticky, salience comes from structure and repetition, ambiguity is resolved by context), and one underlying result (a symbolic abstraction→induction→retrieval circuit) is real."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--99-speculative-field-track.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--references.md
---

# Context Field Theory (Speculative)

> **Provisional (source confidence: low).** About a third of an upstream context-engineering
> course treats context as a continuous "semantic field". It borrows physics vocabulary,
> cites a handful of real papers, then extrapolates well beyond them. This page exists so
> the vocabulary can be recognised and mapped to real techniques — not designed from.

## Claims and Their Grounded Reading

| Term | Claim | Grounded reading |
|---|---|---|
| Neural field | Context is a field; information persists by resonance, not position | Attention spreads influence across the window; already covered by positional effects ([[Why Context Is Finite]]) |
| Attractors | Conversations fall into stable patterns that are hard to leave | Early framing biases later turns; a paper finds successive paraphrasing converges to stable 2-cycles. Practical: an early mistake keeps pulling later turns back (context poisoning) |
| Resonance | Related concepts reinforce each other | Repetition and cross-reference raise salience — ordinary emphasis and recency |
| Boundaries | Membranes control what enters the field | The Select lever ([[Context Retrieval Strategies]]) |
| Persistence / decay | Patterns fade unless reinforced | Older content loses influence and goes first under compaction |
| Symbolic mechanisms | LLMs implement abstraction → induction → retrieval | **Real result** (ICML 2025); applied in [[Structured Context and Schemas]] |
| Quantum semantics | Meaning is undetermined until "observed"; Bell-style violations | A paper reports CHSH-style violations on ambiguous phrases. Practical: disambiguate with context. The framing adds no technique |
| Unified field theory | Combines the above | No testable content beyond the parts |

## What to Keep

1. **Early framing is sticky.** Get the system prompt and first turns right; restart rather
   than argue a model out of a wrong framing.
2. **Salience is earned by structure and repetition.** State a constraint clearly, place it
   at the edges of the window, restate it at decision points.
3. **Ambiguity is resolved by context, not by the words alone.** When outputs vary
   unpredictably, look for the underspecified term.

The course's five mental models (garden, budget, river, biopsychosocial, alchemy) are
teaching aids; the **budget** model is the directly useful one ([[Context Window Budgeting]]).
The "field operations" written as protocols behave like any structured prompt
([[Protocol Shells]]).

**Heuristic:** when "attractor", "resonance" or "field" appears in an agent-design
discussion, ask what the measurable behaviour is and map it to a concrete lever.

## See Also
- [[Context Engineering]] — extends
- [[Protocol Shells]] — extends
- [[Context Failure Modes]] — alternative-to (the grounded account of "attractors" as poisoning)
