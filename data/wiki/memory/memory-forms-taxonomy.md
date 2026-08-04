---
title: Memory Forms Taxonomy
tags: [memory, llm, reference]
summary: "The Forms/Functions/Dynamics survey framing — memory as token, parametric, or latent substrate; factual, experiential, or working purpose — and why almost all agent memory work occupies one cell of a much larger space."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph--memory.md
---

# Memory Forms Taxonomy

From *Memory in the Age of AI Agents: A Survey*, a three-axis decomposition of what agent
memory can be: **Forms** (what carries it), **Functions** (why the agent needs it), and
**Dynamics** (how it changes over time).

Its value is diagnostic rather than prescriptive. [[Agent Memory Types]] and
[[Memory Lifecycle]] describe what practitioners actually build; this taxonomy shows that
what practitioners build is **one cell of the space** — flat or graph-structured token
memory, holding user facts, evolving by summarization. The other cells are not exotic
alternatives; they are mostly unexplored territory.

## Forms — what carries the memory

| Form | Substrate | Sub-kinds |
|---|---|---|
| **Token-level** | Text in an external buffer | *Flat (1D)* — logs, rolling windows, retrieved snippets · *Planar (2D)* — knowledge graphs, memory graphs (Zep, A-Mem) · *Hierarchical (3D)* — layered summaries at multiple abstraction levels |
| **Parametric** | Model weights | *Internal* — what pretraining already encoded · *External* — continual fine-tuning or LoRA adapters trained on accumulated experience |
| **Latent** | Neural activations / hidden states | *Generate* — synthesize new latent representations · *Reuse* — cache and replay KV states · *Transform* — compress or restructure latent state |

The dimensional framing of token memory is the sharpest part. **Flat, planar, and
hierarchical are not three storage formats; they are three answers to "what relationship
between memories does retrieval need to traverse?"** Flat memory can only answer similarity
queries. Planar memory can answer connection queries — the reason
[[Knowledge Graph Retrieval]] exists as a distinct strategy. Hierarchical memory can answer
queries at a chosen granularity, which is what a rolling summary approximates badly.

The parametric and latent rows are where the practical gap sits. Nearly every deployed
system is token-level, because token memory is inspectable, editable, and deletable — and
those three properties are what make memory operable at all. **Parametric memory has none
of them**: you cannot show a user what an adapter remembers about them, and you cannot
honor a deletion request by editing a weight. That is a governance constraint, not a
capability one, and it explains the imbalance better than maturity does. KV-cache reuse is
the one latent-memory technique in wide production use — see [[Prefix Caching]] — and it is
used for cost rather than for recall.

## Functions — why the agent needs it

| Function | Holds | Sub-kinds |
|---|---|---|
| **Factual** | Knowledge from agent-environment interaction | *User factual* — preferences, identity, history · *Environment factual* — world state, task context, domain facts |
| **Experiential** | Accumulated problem-solving capability | *Case-based* — past solved examples to reuse · *Strategy-based* — distilled generalizable approaches · *Skill-based* — reusable tools or code extracted from experience · *Hybrid* |
| **Working** | Active information during a task | *Single-turn* — reasoning traces, scratchpads · *Multi-turn* — dialogue state, partial plans |

**Experiential memory is the axis most systems don't have.** Factual memory makes an agent
personalized; experiential memory makes it *better at its job* over time, and the two are
routinely conflated because both are "long-term memory" in a vector store. They are not the
same thing: storing that a user prefers equities is factual, storing the approach that
worked last time a portfolio query failed is experiential.

The skill-based sub-kind is the most interesting and the least implemented — an agent
extracting a reusable tool from its own successful trajectory. That is the same ratchet
[[Harness Engineering]] describes, except performed by the agent rather than by the
engineer. See [[Self-Learning Agents]] for the reflection-based approximation of it, which
is the closest thing in common use.

Note also that **working memory is memory**, though it is rarely stored as such. A
scratchpad discarded at the end of a turn is a memory decision — the decision to forget
everything about how the answer was reached, which is precisely what makes trajectory
debugging hard afterward.

## Dynamics — how memory operates over time

Three processes, which map onto [[Memory Lifecycle]]'s five stages with a finer grain on
the ends:

**Formation** — semantic summarization, knowledge distillation, structured construction
(KG triplets, schemas), latent representation, parametric internalization. These are
ordered by how much structure is imposed at write time, and that ordering is a cost
transfer: structure imposed at write time is retrieval precision bought with write-time
LLM calls. Triplet extraction ([[Memory Decay Weighting]]) sits in the middle; raw logging
sits at the free end.

**Evolution** — consolidation (merging), updating (conflict resolution), forgetting
(pruning). Covered in depth as stage E of [[Memory Lifecycle]]; the survey's contribution
is naming them as three distinct operations rather than one "maintenance" step.

**Retrieval** — decomposed into four independent decisions:

| Decision | Question |
|---|---|
| **Timing** | When to retrieve — at start, on demand, continuously |
| **Query construction** | How to form the retrieval query from the turn |
| **Strategy** | Sparse, dense, graph traversal, hybrid |
| **Post-retrieval processing** | Reranking, filtering, compression before injection |

Only *strategy* gets significant engineering attention, and it is arguably the least
important of the four. **Timing** is the one that determines whether memory helps or hurts
— retrieving every turn is the default and is actively harmful, which is the
when-to-retrieve policy in [[Memory-Augmented Conversational RAG]]. **Post-retrieval
processing** is the augmentation gate: having retrieved the right memories, you still
choose how much of them to hand the model.

## See Also
- [[Agent Memory Types]] — complements (the practitioner taxonomy this frames as one cell)
- [[Memory Lifecycle]] — extends (Dynamics, at finer grain)
- [[Memory Decay Weighting]] — instance-of (planar token memory with recency-scored retrieval)
- [[Memory-Augmented Conversational RAG]] — implements (the retrieval-timing decision)
- [[Self-Learning Agents]] — instance-of (experiential memory, approximated by reflection)
- [[Prefix Caching]] — instance-of (latent memory reuse, in production for cost)
