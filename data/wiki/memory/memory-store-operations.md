---
title: Memory Store Operations
tags: [memory, infra, reference]
summary: "Running a memory store in production — caching and async indexing for latency, memory hit rate as the metric that says whether memory is earning its cost, and the deletion requirement that makes memory a compliance surface rather than a cache."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph--memory.md
---

# Memory Store Operations

[[Memory Lifecycle]] covers what a memory system does. This is what it takes to run one:
the latency, observability, and compliance concerns that appear once the store is on the
request path for every turn.

The framing worth keeping: **a memory store is a database that sits inside the latency
budget of every single request.** Most of what follows is ordinary data-systems practice,
and that is the point — the LLM-specific parts of memory get all the attention while the
operational failures are the boring ones.

## Latency and scale

Memory retrieval happens *before* generation, so its latency is fully additive to
time-to-first-token. Four levers:

| Lever | Practice |
|---|---|
| **Caching** | Cache frequently accessed entries (recent session data); choose write-through or write-back for updates |
| **Indexing** | Index metadata fields (`user_id`, `session_id`) in the structured store; update vector indexes periodically or asynchronously |
| **Load balancing** | Multiple memory-module instances behind a balancer; auto-scale on query volume *and* write volume |
| **Latency** | Async I/O for lookups; precompute embeddings and summaries rather than computing them on the read path |

Two of these are less obvious than they look. **Asynchronous vector index updates** are an
explicit consistency trade: a memory written this turn may not be retrievable next turn.
For episodic memory that is usually fine; for a just-stated user correction it is not, and
that is exactly the case where a user notices. The usual resolution is a synchronous
write to the structured store with the session summary read directly by ID — which is why
Memoria's summary retrieval is *"deterministic — just a direct session ID lookup"* rather
than a search ([[Memory Decay Weighting]]).

**Auto-scaling on write volume** matters because memory systems have an asymmetric load
profile that read-heavy scaling assumptions miss. Every turn produces both a read and a
write, and the write path is the expensive one when it includes LLM calls for extraction
and summarization. A memory store under load is doing inference, not just I/O.

## What to measure

| Metric | What it tells you |
|---|---|
| **Memory hit rate** | Ratio of queries that actually leverage a relevant memory entry |
| **Latency breakdown** | Time in retrieval vs reasoning fusion vs generation |
| **Update frequency** | How often memory is appended or pruned |

**Memory hit rate is the load-bearing metric and the one nobody instruments.** A memory
system with a low hit rate is pure cost — added latency, added tokens, added failure modes
— in exchange for retrievals the answer didn't need. Without it you cannot distinguish a
memory system that is working from one that is retrieving diligently and contributing
nothing, because both look identical from the outside: the agent answers, and it seems
personalized.

The harder half is that hit rate is not mechanically decidable. *Retrieved* is easy to
count; *leveraged* requires knowing whether the memory influenced the output, which needs
either attribution or a judge. The tractable proxy is an ablation: run the eval set with
memory disabled and compare. If the delta is small, the store is decorative.

Logging requirements are stronger than for ordinary retrieval: **log each query alongside
the memory entries used**, and trace end-to-end with OpenTelemetry including the memory
lookup span. The reason is attribution — when an agent says something wrong about a user,
the question is whether it hallucinated or faithfully repeated a bad memory, and those
have opposite fixes. See [[Observability and Runtime Patterns]].

## Automated maintenance

- **Scheduled pruning** of stale entries
- **Differential storage** — store deltas rather than full snapshots to limit bloat
- **Periodic embedding-model refresh**, so semantic relevance doesn't drift

The third is a genuine trap. Re-embedding under a new model means the vector store contains
two incompatible geometries until backfill completes, and similarity scores across the
boundary are meaningless rather than merely degraded. Embedding migrations are full
reindexes, and a memory store that has been accumulating for a year is the worst case for
one — which argues for keeping the raw text authoritative and the vectors derived, the
same append-only-source discipline as [[Memory Lifecycle]]'s rollback-friendly rule.

## Security and compliance

- **Access control** — RBAC/ABAC on memory endpoints, governing both read and modify
- **Encryption** — at rest (AES-256) and in transit (TLS)
- **Compliance** — anonymize or tokenize sensitive data; support deletion and consent
  (GDPR, CCPA)

**Deletion support is the requirement that constrains architecture rather than merely
adding a feature.** A user's right to erasure must reach every representation of them: the
structured store, the vector index, the derived session summaries, and any consolidated
memory that merged their facts with others. Consolidation is what makes this hard — once
"user is allergic to dairy" has been merged into a summary, deleting the source message
does not delete the fact. This is a direct argument against aggressive consolidation and
in favor of keeping memories traceable to their originating turn.

It is also the strongest practical argument for token-level over parametric memory in
[[Memory Forms Taxonomy]]: you can delete a row, but you cannot delete a gradient update.

Memory is additionally an injection surface — content written to memory is content that
will be read back into a future prompt as trusted context. This is R4 (memory poisoning)
in [[Agent Security Risk Taxonomy]], and the mitigation belongs at the memory write path
rather than in a central guardrail layer. See [[Prompt Injection]].

## Three recurring failures

| Failure | Mitigation |
|---|---|
| **Memory overload** | Summarize or score by relevance to keep injected memory concise |
| **Stale context** | TTL and decay policies; archive rather than delete, retaining version history |
| **Conflicting information** | Recent supersedes older, or higher-confidence source wins |

These are the operational statements of problems the design pages treat conceptually —
overload is the context budget, staleness is [[Memory Decay Weighting]], conflict is stage
E of [[Memory Lifecycle]]. Worth noting that the stale-context mitigation says **archive
while maintaining version history**, not delete: the same rollback-friendly property,
arrived at again from the operations side.

## See Also
- [[Memory Lifecycle]] — extends (running the lifecycle in production)
- [[Memory Forms Taxonomy]] — complements (why deletability favors token-level memory)
- [[Memory Decay Weighting]] — implements (TTL and decay as the staleness policy)
- [[Agent Security Risk Taxonomy]] — complements (memory poisoning, R4, at the write path)
- [[Observability and Runtime Patterns]] — implements (tracing the memory lookup span)
