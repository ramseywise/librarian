---
title: Semantic Cache for RAG Agents
tags: [rag, infra, pattern]
summary: Zero-retrieval-cost path for RAG agents — embed the query, cosine-match against a grader-validated golden seed, and short-circuit the full CRAG pipeline on high-similarity hits.
updated: 2026-11-08
sources:
  - data/raw/claude-docs/playground/docs/rag/semantic-cache.md
  - data/raw/claude-docs/project-g/docs/rag/semantic-cache.md
  - data/raw/claude-docs/project-g/docs/stakeholders/agent-comparison-findings.md
  - data/raw/papers/2026-11-06-li-2025-plan-reuse-mechanism-llm-driven.md
  - data/raw/papers/2026-11-08-lakshmanan-hapke-genai-design-patterns-ch08-addressing-constraints.md
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
                          help_center / [product]-kb / escalation
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
| `definition` | [product]-kb as context enrichment + help center for answer | [product]-kb is **never** the primary target |
| `escalation` | skip retrieval | Route directly to escalation |
| `low_confidence` | all sources | Flat fallback search |

**Key insight:** [product]-kb (concept glossary) is context enrichment only. For `definition` queries, the actual answer still comes from help center articles.

---

## Caching Concerns

- **Staleness:** Add `build_date` field; warn if file is > 30 days old. Product changes invalidate cached answers.
- **Language mismatch:** Cache built from Danish queries — English queries score lower, fall through to CRAG (correct behaviour).
- **Small seed:** If golden dataset yields < 50 high-scoring rows, hit rate on real traffic will be negligible. Expand seed by running the agent on a broader stratified set.

## Eval Implications

- **Split every grader by `cache_hit`**, not just the composite score — hits and misses are
  different systems.
- **Hits have no runtime confidence.** A hit returns a stored answer graded at seed time, so
  there is no `relevance_score` to calibrate; exclude hits from confidence calibration and
  report the seed-time score separately as cache answer quality.
- **Staleness needs a reference-based grader.** Grounding and relevancy can both stay high on
  a stale cached answer. Claim-level F1 of the hit against a freshly generated pipeline answer
  for the same query (target ≥0.7) is the staleness guard. Other targets: hit composite ≥
  baseline, miss-path ΔMRR ≥ 0, hit latency ≤ 500ms.

## Plan Reuse Variant (AgentReuse)

AgentReuse (a 2025 preprint) caches agent plans rather than answers. It embeds the request, classifies its intent, strips the key parameters, and searches the cache only within that intent; on similarity of at least 0.75 it reuses the stored plan and fills in the new parameters. Setup: a Chinese smart-assistant dataset of 23 intents and 2,664 requests (see Limits), an m3e-small embedder and a flat inner-product FAISS index.
- Matching: F1 0.9718 and accuracy 0.9459 against 0.9100 and 0.8366 for GPTCache; keeping raw text with the arguments scores 0.9035 and 0.8272 (all self-reported, threshold 0.75 on that dataset).
- Latency is 93.12% below calling the model for every plan (self-reported, assuming 31.8 s for each plan-generation call, execution time excluded) and 60.61% below GPTCache (self-reported, same dataset; see Limits on the unit). Reused plans gave identical responses in 93 of 100 AutoGen trials (self-reported; 20 requests, 5 repeats).
- Overhead is about 100 MB of GPU memory and 9.2 ms per request with an existing intent classifier, or about 500 MB and 23.5 ms without one (self-reported, per-request estimates). The premise that about 30% of requests are similar comes from earlier work the paper cites, not from a measurement in the paper.

---

## Tradeoffs in a design-patterns book (Pattern 25)

Lakshmanan and Hapke motivate caching with call-centre shares of repeated questions (31%, 30%, 40%, cited without source). Semantic caching gives up some nuance in exchange for hits, and a similarity threshold must be chosen. In multitenant systems the cache can leak across users, so include a user identifier in the key or system prompt, and flush the cache whenever the model version changes. Server-side prefix caching mainly cuts time to first token, and providers need prompts over about 1,024 tokens; vendor savings figures (90%, 85%, 80%, 50%) are quoted without references.

## Limits

AgentReuse (the plan-reuse section above):

- Chinese assistant commands only and one embedder; the authors describe the work as exploratory. The 93.12% latency figure rests on an assumed per-plan cost, not a measured end-to-end run.
- The extraction notes internal inconsistencies: the request count appears as 2,664 and as 2,644; a line says other overhead does not exceed 1 ms next to values of 5.228 ms; and one passage calls the 60.61% latency reduction "60.61 percentage points" although it is a relative reduction.
Limits of this section:
- All figures in this section are reported from vendors or unsourced call-centre examples.

## See Also
- [[RAG Evaluation]] <!-- auto-linked -->
- [[RAG Reranking]] <!-- auto-linked -->
- [[RAG API Design Patterns]] <!-- auto-linked -->
- [[Reciprocal Rank Fusion (RRF)]]
- [[CRAG Retry Logic]]
- [[RAG Retrieval Strategies]]
- [[Agentic RAG — Advanced Patterns]]
- [[ACC Bounded Memory Control for Agents]] — related (reuse of structured state instead of raw plans)
- [[Cache-Augmented Generation]] — related (caches attention state for a whole corpus, not answers)
