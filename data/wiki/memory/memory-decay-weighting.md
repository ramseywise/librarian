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
wᵢ = e^(−α · xᵢ)            α = 0.02, xᵢ = age in MINUTES
x_norm = (x − x_min) / (x_max − x_min)    min-max normalized first
w̃ᵢ = wᵢ / Σⱼ wⱼ            then renormalized to sum to 1
top_k = 20
```

The unit is **minutes**, which is easy to misread and changes the character of the
mechanism completely. Applied to raw minutes, α = 0.02 gives a half-life of roughly
**35 minutes** (`ln 2 / 0.02 ≈ 34.7`) — a within-session scorer, not a cross-session one.

But the min-max normalization is applied *first*, and that is what makes the scheme work
across sessions: `x_norm` maps the age range of the currently-retrieved set onto [0, 1],
so decay is computed over **relative** age within the candidate set rather than absolute
elapsed time. The practical consequence is that α does not encode a fixed half-life at
all — it encodes **how sharply the newest candidates outrank the oldest ones**, whatever
the actual time span happens to be. A set spanning an hour and a set spanning a year get
the same weight curve.

The source's own tuning guidance confirms this reading: higher α means the model "almost
ignores anything older than a few sessions," lower α keeps older context relevant longer.
That is a statement about rank sharpness across sessions, which a 35-minute absolute
half-life could not produce. Normalization is also what stops very old triplets from
underflowing to zero weight and dropping out entirely.

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
- [[Memory Store Operations]] — complements (decay and TTL as the staleness policy, operationally)
