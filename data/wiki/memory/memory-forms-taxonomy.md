---
title: Memory Forms Taxonomy
tags: [memory, llm, reference]
summary: "The Forms/Functions/Dynamics survey framing — memory as token, parametric, or latent substrate; factual, experiential, or working purpose — and why almost all agent memory work occupies one cell of a much larger space."
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph--memory.md
  - data/raw/repos/learn-ai-engineering/interviewing--notes--memory.md
  - data/raw/papers/2026-11-08-zhang-2025-survey-memory-mechanism-large-language.md
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

## A survey's sources, forms and operations (Zhang and co-authors)

A survey of LLM-agent memory (arXiv v1 preprint, covering work to early 2024, no experiments of its own) organises memory along three dimensions and one loop:

- **Sources:** history within one trial, history across trials, and outside knowledge; a check-mark table records which of 25 systems draw on each.
- **Forms:** textual (complete history, recent history, retrieved, external) and parametric (fine-tuning, editing). The survey says textual memory can be structured as tuples or databases as well as free text; the extraction notes it never names graphs as a memory form.
- **Operations:** write, manage (merge, reflect, forget) and read, composed as one loop before the LLM acts. It argues they should be designed together because the write form constrains the read.

Statements it makes: retrieved memory scores entries and takes the top K, and retrieval stores homogeneous information well but struggles with heterogeneous information; full-history textual memory has quadratic attention cost, length limits and position bias; textual memory is cheaper to write and parametric memory cheaper to read; fine-tuning is mostly offline and editing suits small online updates; textual memory suits recent, context-specific tasks and parametric memory large, well-established knowledge. For evaluation it separates direct measures (answer correctness, F1 on the memories retrieved, plus time and hardware cost) from indirect ones (end-to-end tasks, with and without memory), and concedes no open-source benchmark is tailored to memory modules. Multi-agent memory (synchronisation, communication, information asymmetry) and lifelong learning (temporal memory, forgetting) appear as future directions. The extraction flags that the cached copy is v1, so graph-memory or benchmark material added later may be present only in the published version.

## See Also
- [[Agent Memory Types]] — related (the practitioner taxonomy this frames as one cell)
- [[Memory Lifecycle]] — extends (Dynamics, at finer grain)
- [[Memory Decay Weighting]] — instance-of (planar token memory with recency-scored retrieval)
- [[Memory-Augmented Conversational RAG]] — related (the retrieval-timing decision)
- [[Self-Learning Agents]] — instance-of (experiential memory, approximated by reflection)
- [[Prefix Caching]] — instance-of (latent memory reuse, in production for cost)
- [[ChatDB SQL Symbolic Memory]] — instance-of (symbolic memory in SQL tables)
- [[MeMo Memory as a Model]] — instance-of (memory held in a model's parameters)
- [[Jev-Mem System-One Memory Control]] — instance-of (a fast controller over memory operations)
- [[Delta-Mem Fixed-Size State Memory]] — instance-of (latent state memory beside a frozen model)
- [[Offline Recurrence Sleep for Language Models]] — instance-of (latent memory consolidated offline)
- [[LLM Personalization Taxonomy]] — related
