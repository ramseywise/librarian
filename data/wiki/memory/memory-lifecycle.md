---
title: Memory Lifecycle
tags: [memory, llm, agents, concept]
summary: "Five stages — represent, store, retrieve, use, update/forget — with the fifth being the one production systems skip, and consolidation designed so a failed merge can roll back instead of losing history."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph--memory.md
---

# Memory Lifecycle

[[Agent Memory Types]] answers *what kinds of memory exist*. This page answers **what
happens to a memory over its life**, which is where most production systems have a gap.

## The five stages

| Stage | Question | Mechanisms |
|---|---|---|
| **(A) Represent** | What shape does a memory take? | Raw history, summaries, structured objects (KG triplets, schemas), latent vectors |
| **(B) Store** | Where does it live? | Vector DB, structured store, SQL, graph DB |
| **(C) Retrieve / select** | Which memories come back? | Query rewriting, history-aware retrieval, semantic/hybrid search, graph traversal |
| **(D) Use** | How does it change behavior? | Prompt construction, tool decisions, planning |
| **(E) Update / forget** | What happens to it over time? | Consolidation, summarization, compression, filtering, pruning |

Stages A–D get almost all the engineering attention. **Stage E is the one that decides
whether the system still works in month six.**

## Stage E in detail

Three distinct operations, often conflated:

- **Consolidation** — merging redundant or related memories.
- **Updating** — revising outdated facts; this is **conflict resolution**, not appending.
- **Forgetting** — pruning low-utility or stale memories.

The industry framing (Microsoft's agent memory) makes the same split as
extraction → consolidation → retrieval, with the load-bearing detail in the middle step:
*"conflicting facts, such as a new allergy, are resolved to maintain an accurate memory."*

> **A store that only appends does not have memory; it has a log.** Without update, the
> agent holds both "user is vegetarian" and "user ordered steak" with no way to know which
> is current.

See [[Memory Decay Weighting]] for the mechanism that resolves this without an explicit
conflict-resolution step.

## Consolidation must be rollback-friendly

The design rule that matters more than summary quality:

> **The system only moves the pointer, without deleting the original messages** — so even
> if consolidation fails, it can return to the original archive and continue working.

The failed path writes the original messages to `archive/`, preserving complete history and
preventing context loss when consolidation goes wrong.

This generalizes: **compression is lossy and its loss is discovered later, at read time.**
A summarizer that drops the one fact you needed gives no error at write time. The only
defense is keeping the pre-compression form recoverable — which is why
[[Agent Memory Types]] requires compaction to write raw turns to cold storage before
discarding, and why [[Knowledge Graph as Shared Agent Memory]] requires entity resolution
to be reversible. **Same rule, three layers.**

## Two shipped four-layer designs

**ChatGPT** — notable for what it *doesn't* use: no vector database, no RAG retrieval
enhancement. Simpler than most expect:

| Layer | Contents | Persistent? |
|---|---|---|
| Session metadata | Device, location, usage patterns | No |
| User memory | ~33 key preference facts, injected every time | Yes |
| Conversation summary | Lightweight summaries of ~15 recent conversations | Yes |
| Current session | Sliding window of the active conversation | No |

**~33 facts, injected unconditionally** — that is a design choice against retrieval, not a
limitation. At that size, selecting is more expensive and less reliable than including
everything.

**OpenClaw hybrid** — three layers with an explicit retrieval blend:

| Layer | Contents |
|---|---|
| `memory/YYYY-MM-DD.md` | Append-only logs, preserving original details |
| `MEMORY.md` | Selected facts, actively maintained by the agent |
| `memory_search` | Hybrid search — **70% vector similarity + 30% keyword weight** |

Note the shape: **an append-only raw layer under a curated layer**, which is exactly the
rollback-friendly property above, and structurally the same `data/raw/` → `data/wiki/`
split this repo uses.

## See Also
- [[Agent Memory Types]] — extends (what happens to the types over time)
- [[Memory Decay Weighting]] — instance-of (a mechanism for stage E)
- [[Memory-Augmented Conversational RAG]] — extends (stage C, in the multi-turn case)
- [[Context Compaction]] — complements (the same lossy-compression problem inside one session)
- [[Knowledge Graph as Shared Agent Memory]] — complements (reversibility as a write-path requirement)
- [[Memory Forms Taxonomy]] — extends (Dynamics as a finer-grained view of these stages)
- [[Memory Store Operations]] — implements (running the lifecycle in production)
