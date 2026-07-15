---
title: Semantic Cache for RAG Agents
tags: [rag, infra, pattern]
summary: Zero-retrieval-cost path for RAG agents — embed the query, cosine-match against a grader-validated golden seed, and short-circuit the full CRAG pipeline on high-similarity hits.
updated: 2026-07-06
sources:
  - raw/claude-docs/galactus/docs/rag/semantic-cache.md
---

# Semantic Cache for RAG Agents

A semantic cache sits in front of the full retrieval pipeline. When an incoming query closely matches a previously grader-validated QA pair, it returns the cached answer directly — skipping embedding, retrieval, reranking, and LLM generation (~3–6s, 2+ LLM calls saved).

**Hypothesis:** A meaningful fraction of real queries are paraphrases of already-answered questions. Routing those to a cache hit maintains quality (cached answers are grader-validated) while eliminating retrieval cost.

---

## 3-Tier Architecture

```
planner ──▶ cache_lookup ──▶ hit (sim ≥ 0.85)? ──YES──▶ cache_respond ──▶ END
                                      │
                                     NO
                                      ▼
                           source_router ──▶ route by intent_type
                                      │
                          help_center / billypedia / escalation
                                      ▼
                             retrieve (CRAG) ──▶ answer ──▶ END
```

**Tier 1 — Semantic cache** (zero LLM, zero retrieval): embed query, cosine match against golden seed. Hit ≥ threshold → return cached answer.

**Tier 2 — Embedding source router** (zero LLM, ~1ms): reuse the same embedding model to classify `intent_type` by cosine distance to pre-computed intent centroids.

**Tier 3 — Full CRAG pipeline**: only reached on cache miss + answerable intent.

---

## Offline Phase — Building the Cache

**Input:** grader-validated QA pairs from the golden dataset pipeline (composite score ≥ 0.75).

```python
from sentence_transformers import SentenceTransformer
import numpy as np, json

model = SentenceTransformer("intfloat/multilingual-e5-base")
embeddings = model.encode(queries, normalize_embeddings=True)  # (N, 768)

np.savez(
    "semantic_cache.npz",
    embeddings=embeddings.astype("float32"),
    queries=..., answers=..., sources=..., scores=...
)
```

Typical seed size: 150–200 rows → single matrix multiply at query time, no FAISS needed.

---

## Runtime Lookup

```python
def lookup(query: str) -> CacheResult | None:
    if not _ENABLED:
        return None
    _load()
    vec = _store["model"].encode([query], normalize_embeddings=True)
    sims = (_store["embeddings"] @ vec.T).flatten()
    idx = int(np.argmax(sims))
    sim = float(sims[idx])
    if sim < _THRESHOLD:   # default 0.85
        return None
    return CacheResult(matched_query=..., answer=..., similarity=sim, ...)
```

**Config flags:**
- `SEMANTIC_CACHE_ENABLED` (default false)
- `SEMANTIC_CACHE_THRESHOLD` (default 0.85, sweep 0.75–0.95)
- `SEMANTIC_CACHE_PATH` — path to `.npz` file

---

## Threshold Selection

Run eval at `[0.75, 0.80, 0.85, 0.90, 0.95]`. Plot hit rate vs. composite quality. Pick threshold that maximises `hit_rate × quality` without degrading miss-path MRR.

| Metric | Target |
|--------|--------|
| Cache hit rate | Report as % of answerable queries |
| Hit quality (calibrated tier) | ≥ baseline composite |
| Latency on hits | ≤ 500ms end-to-end |
| Miss path MRR | ΔMRR ≥ 0 |

---

## Source Routing — Tier 2

The same `multilingual-e5-base` embedding model routes by intent type using pre-computed centroids. No LLM needed.

| `intent_type` | Sources | Behaviour |
|---|---|---|
| `how_to` | help center | Standard CRAG retrieval |
| `regulatory` | help center + pricing | Both, re-rank by domain |
| `definition` | billypedia as context enrichment + help center for answer | Billypedia is **never** the primary target |
| `escalation` | skip retrieval | Route directly to escalation |
| `low_confidence` | all sources | Flat fallback search |

**Key insight:** Billypedia (concept glossary) is context enrichment only. For `definition` queries, the actual answer still comes from help center articles.

---

## Caching Concerns

- **Staleness:** Add `build_date` field; warn if file is > 30 days old. Product changes invalidate cached answers.
- **Language mismatch:** Cache built from Danish queries — English queries score lower, fall through to CRAG (correct behaviour).
- **Small seed:** If golden dataset yields < 50 high-scoring rows, hit rate on real traffic will be negligible. Expand seed by running the agent on a broader stratified set.

---

## See Also
- [[Reciprocal Rank Fusion (RRF)]]
- [[CRAG Retry Logic]]
- [[RAG Retrieval Strategies]]
- [[Agentic RAG — Advanced Patterns]]
- [[VA Bedrock KB Reference]]
