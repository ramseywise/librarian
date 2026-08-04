---
title: Memory Decay Weighting
tags: [memory, llm, agents, pattern]
summary: "Exponential recency decay as a retrieval scorer — Memoria weights memories by e^(-alpha*age), which resolves stale-vs-current facts by ranking rather than by an explicit conflict-resolution step."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph--memory.md
---

# Memory Decay Weighting

A concrete stage-E mechanism from [[Memory Lifecycle]]: rather than deciding *which memory
is current* at write time, score every memory by recency at read time and let the ranking
decide.

## Memoria (BlackRock)

A shipped implementation: SQLite for structured storage + ChromaDB for vector search, with
retrieval scored by **exponential decay weighting**.

```
wᵢ = e^(−α · xᵢ)            α = 0.02, xᵢ = age in days
w̃ᵢ = wᵢ / Σⱼ wⱼ            min-max normalized, then renormalized
top_k = 20
```

At α = 0.02, a memory's weight halves roughly every **35 days** (`ln 2 / 0.02 ≈ 34.7`).
That is the tunable that encodes your assumption about how fast the domain goes stale —
preferences decay slowly, project state decays fast, and one α for both is a compromise
that serves neither.

**Reported effect:** ~400 average tokens retrieved per turn versus **115K** for
full-context. Roughly a 99.7% reduction in what reaches the prompt.

## Why decay substitutes for conflict resolution

[[Memory Lifecycle]] flags updating as the hard stage, because it requires detecting that
a new fact contradicts an old one. Decay weighting sidesteps the detection problem:

> Both "user is vegetarian" (day 200) and "user eats meat" (day 3) stay in the store. The
> recent one outranks the old one **without anything having to notice they conflict.**

The trade is explicit and worth stating:

- **Bought:** no contradiction-detection step, no destructive writes, complete history
  retained — the rollback-friendly property [[Memory Lifecycle]] argues for.
- **Paid:** stable long-lived facts decay at the same rate as volatile ones. A preference
  stated once, two years ago, and never contradicted will eventually rank below noise.

The usual fix is **two tiers** — a small always-injected profile for durable facts (the
ChatGPT ~33-fact layer) with decay applied only to the episodic store beneath it. Decay is
the right scorer for *events*; it is the wrong scorer for *identity*.

## When this fits

Reach for decay weighting when memories are **time-stamped observations** whose relevance
genuinely fades: conversation history, project state, incident context. Prefer explicit
conflict resolution when memories are **assertions about durable facts**, where "most
recent" and "most correct" are not the same thing.

## See Also
- [[Memory Lifecycle]] — part-of (a stage-E mechanism)
- [[Agent Memory Types]] — complements (episodic store scoring)
- [[RAG Retrieval Strategies]] — complements (recency as a re-ranking signal)
- [[Reciprocal Rank Fusion (RRF)]] — alternative-to (fusing ranked lists vs re-weighting one)
