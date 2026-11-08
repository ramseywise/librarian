---
title: Memory Lifecycle
tags: [memory, llm, agents, concept]
summary: "Five stages — represent, store, retrieve, use, update/forget — with the fifth being the one production systems skip, and consolidation designed so a failed merge can roll back instead of losing history."
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph--memory.md
  - data/raw/repos/learn-ai-engineering/interviewing--notes--memory.md
  - data/raw/papers/2026-11-06-guo-2026-memfactory.md
  - data/raw/papers/2026-11-06-ding-2026-always-onagents.md
  - data/raw/papers/2026-11-06-piskala-2026-maple.md
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

## Three 2026 papers on running the lifecycle

- **MemFactory** (infrastructure paper) packages the lifecycle as four layers (Module, Agent, Environment, Trainer) with a built-in GRPO trainer; its Updater emits ADD, DEL, UPDATE or NONE. Only the MemAgent recurrent-memory agent is evaluated: on Qwen3-1.7B the average goes 0.3118 to 0.3581 (+14.8%) after 250 valid training steps on one GPU with shortened samples, avg@4, against the same untrained checkpoint (self-reported); the out-of-distribution score falls 0.0332 to 0.0195 (self-reported, same run). On Qwen3-4B-Instruct 0.6146 to 0.6595 (self-reported). Limits: Memory-R1 and RMM (MemoryRMMAgent) agents ship but are not trained or evaluated; see Limits.
- **Always-On agents survey** scores each stored state item on authority, scope, mutability, provenance, recoverability and actionability, and widens the lifecycle into ten steps that run from observing and writing through validation, organization, retrieval, acting, updating and forgetting to audit and rollback. Rollback is exposed by 27 of 435 coded works (a corpus the authors scoped and coded). Its AOEP-v0 pilot covers nine fault patterns and seven systems with a local Qwen2.5-7B reader under greedy decoding, scoring obligations passed out of 15: hand-built governed reducer 15, no memory 0, naive append 7, full context 7, vector RAG 7, Mem0-style 4, real mem0ai 3 (self-reported); sampled decoding gives a mean of 6.6. The authors call it not a benchmark; the reducer is an oracle, no frontier models, the envelope ablation was not run, and the extraction did not read the full 136-page paper.
- **MAPLE** splits memory, learning and personalization into sub-agents, with learning run asynchronously and both episodic and semantic records kept (reference store: JSON files). On 150 synthetic personas with 10-turn dialogues, the personalization score goes 4.17 to 4.78 (+14.6%, d=0.95), trait incorporation 45% to 75% (self-reported). See Limits for the caveats.

## Limits

The 2026 papers above:

- MemFactory: the extraction notes no seeds, variance or ablations, and that question counts and reward type per experiment are unstated. "First unified framework" is the authors' claim.
- MAPLE: the only baseline is stateless, the judge is from the same model family, and the horizon is one 10-turn session; design claims are untested. The extraction notes that the abstract's p<0.01 and the text's p<0.001 disagree, and that the reported df of 74.5 does not fit n=150 personas and is unexplained.

## See Also
- [[Agent Memory Types]] — extends (what happens to the types over time)
- [[Memory Decay Weighting]] — instance-of (a mechanism for stage E)
- [[Memory-Augmented Conversational RAG]] — extends (stage C, in the multi-turn case)
- [[Context Compaction]] — related (the same lossy-compression problem inside one session)
- [[Knowledge Graph as Shared Agent Memory]] — related (reversibility as a write-path requirement)
- [[Memory Forms Taxonomy]] — extends (Dynamics as a finer-grained view of these stages)
- [[Memory Store Operations]] — related (running the lifecycle in production)
- [[Identity Memory: Revision vs Accretion]] — extends (the update/forget stage for a self-model)
- [[Compression Strips the Epistemic Frame]] — extends (what consolidation loses first)
- [[Computed-Correctness Lesson Loop]] — instance-of (explicit human promotion from episodic to semantic memory)
- [[Knowledge Graph Entity Resolution]] — extends (reversible merges as the consolidate stage of a graph memory)
- [[MemInsight Attribute Augmentation]] — instance-of (an annotation layer at write time)
- [[ArcMemo Concept-Level Memory]] — instance-of (abstracted concepts as the stored unit)
- [[MemCollab Contrastive Cross-Model Memory]] — instance-of (memory shared across models)
- [[Memory Intelligence Agent]] — instance-of
- [[OCR-Memory Optical Context Retrieval]] — instance-of (episodic retrieval over rendered history)
- [[ACC Bounded Memory Control for Agents]] — instance-of (bounded working state)
