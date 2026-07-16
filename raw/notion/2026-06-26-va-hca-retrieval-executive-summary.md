# VA / HCA Retrieval — Executive Summary

**Source:** https://app.notion.com/p/389f148b3ab780349206c0abd2dac907
**Last edited:** 2026-06-26
**Full technical report:** va-hca-retrieval-report.md

## TL;DR

VA and HCA find the right help article roughly 30–35% of the time. **VA outperforms HCA on every dimension** — because VA pools sources aggressively across 2–3 reformulated queries, while HCA's narrow retry loop discards good candidates and has no reranker or fallback.

On the hardest questions HCA returns no citation 58% of the time vs VA's 39%.

**But the agent layer is the smaller lever.** 47% of questions (442 of 935) are missed by every system — that's a corpus problem, not a retrieval problem. Two data-ops fixes (scope index to help articles; re-ingest ~202 missing articles) raise the achievable ceiling from ~40% to **~59% Hit@5 with no model or agent change**.

> ⚠ **Feasibility gate:** High-impact retrieval changes (multilingual embedding, multilingual reranker) assume Bedrock can run non-Bedrock models. Confirm this before sequencing model-swap work.

---

## Performance Metrics

| System | MRR | P@3 | R@3 | NDCG@5 | Hit@5 | Avg sources |
|---|---|---|---|---|---|---|
| VA | **0.286** | **0.110** | **0.156** | **0.181** | **0.350** | 13.0 |
| HCA | 0.248 | 0.097 | 0.135 | 0.156 | 0.301 | 3.8 |
| Bedrock (direct) | 0.148 | — | — | — | 0.285 | — |
| Local RAG, single query | 0.225 | **0.132** | 0.127 | **0.217** | 0.328 | ~5 |
| Local RAG, multi-query | **0.316** | 0.128 | **0.361** | 0.336 | **0.435** | 23.8 |
| Local-ADK | .375 | 0.151 | 0.422 | 0.521 | 0.405 | 19.8 |
| Local-LG | 0.310 | 0.130 | 0.365 | 0.442 | 0.340 | 23.8 |

*Local RAG is a research baseline, not production. n=754.*

**Ground truth:** ~24,000 real Danish Intercom conversations, <10% URL-cited. product-a/client-a alias map applied (product-a.dk/support/ → help.client-a.co/da/articles/).

**Limitation:** Ground truth is biased toward URL-cited conversations — these are more likely single-doc answerable than typical traffic. The ~59% ceiling is for this slice, not full support volume.

---

## LLM-as-Judge Answer Quality

VA scores higher on **all five** dimensions:

| Metric | VA | HCA | What it measures |
|---|---|---|---|
| Grounding | **0.776** | 0.633 | Are claims tied to retrieved sources? |
| Answer Relevancy | **0.891** | 0.825 | Does the answer address what was asked? |
| Completeness | **0.848** | 0.731 | Are all parts answered? |
| Faithfulness | **0.592** | 0.511 | Does it stay within retrieved content? |
| Context Precision | **0.456** | 0.453 | Are retrieved passages on-topic? |

VA's grounding lead (+0.143) is the largest signal. When HCA's narrow retrieval misses the article, the model fills from general knowledge — no citation, no grounding.

**Note:** Low faithfulness on both systems (~0.5–0.6) — both models add unsupported detail even when grounding is decent. Worth investigating.

---

## Corpus Quality — The 47% Ceiling

442 of 935 questions missed by every system. Four known causes:

| Cause | Est. questions | Fix |
|---|---|---|
| Glossary pages ranking above help articles | ~130 | Scope KB to help articles only |
| Articles missing from index | ~93 | Re-ingest 202 sources |
| URL mapping gap (product-a → client-a migration) | ~35–40 | Expand alias map |
| Ranking failure (article indexed but buried) | ~175–185 | Requires embedding model upgrade |

Fixing first two alone recovers ~220 questions, raising ceiling from ~40% to **~59% Hit@5**.

**Stale content found:** Two glossary pages have confirmed wrong facts — NemID described as active (deprecated 2023), bookkeeping law described as upcoming (took effect 2022).

---

## Two Independent Levers

1. **Corpus quality** — affects every system equally; dominant lever. Scope + re-ingest = ~2x hit rate improvement, zero model change.
2. **Retrieval strategy** — the agent layer, where VA beats HCA. VA pools 2–3 reformulated queries (~13 sources), HCA does narrow retry returning ~4 sources. VA wins because broad pooling → reranking → filter to top 5–6.

**Empty-source behavior (on 442 all-miss queries):**
- HCA: returns no sources 58% of the time
- VA: 39%
- Local multi-query: <5%

---

## Retrieval Configuration Recommendations

| Change | Current (Bedrock) | Research best | Gain |
|---|---|---|---|
| Embedding model | Amazon Titan (English-dominant) | Multilingual e5-large | +0.069 MRR |
| Chunk size | Hierarchical 1500-token parent | Overlapping 256 tokens / 64 overlap | +0.014 MRR |
| HTML parsing | Raw Intercom HTML (boilerplate present) | Preprocessed — boilerplate stripped | Impacts downstream quality |
| Reranker | Undocumented (possibly English-only) | Multilingual cross-encoder | +0.028 MRR |
| Retrieval method | Dense | Dense (hybrid adds no benefit here) | — |

---

## Leverage Rankings

| Layer | Impact | Notes |
|---|---|---|
| Corpus scope & chunking | **Highest — cheapest to change** | Wrong sources cap everything downstream |
| Reranker | **High** | Only if language-appropriate — English-only reranker actively regresses Danish |
| Retrieval method | Lower than expected | Dense multilingual covers semantic recall; hybrid adds little |
| Generation model upgrade | Lower than retrieval | Upgrade retrieval first |
| Iterative re-retrieval (CRAG) | Control lever only | +0.005 MRR at +3.4s latency — not worth it for live agent |

---

## Failure Attribution Taxonomy

| Failure type | What happened | Root cause | Fix |
|---|---|---|---|
| Coverage gap | Topic not in KB | Content never added or scoped out | Corpus QA |
| Retrieval failure | Wrong or missing docs | Not indexed, fragmented, or vocab mismatch | Index / retrieval config |
| Ranking failure | Right docs found but buried | Reranker demotes correct Danish passages | Retrieval optimization |
| Routing failure | Answered when should escalate | No confidence gate | Agent behavior |
| Generation failure | Right docs retrieved, wrong answer | Model didn't use context | Quality calibration |
| Grounding failure | Answer contains unsupported claims | Model extrapolated beyond sources | Quality calibration |

---

## Recommended Actions (Priority Order)

| # | Owner | Action | Expected outcome | Effort | Priority |
|---|---|---|---|---|---|
| 1 | RAG/data ops | Scope Bedrock corpus to help articles only | Removes ~30% of shared failures | Very low | High |
| 2 | RAG/data ops | Re-ingest 202 missing articles | Unlocks ~200 unanswerable questions | Low | High |
| 3 | RAG/data ops | Strip HTML boilerplate before next content sync | Removes noise from top results | Medium | High |
| 4 | RAG/data ops | Fix fragmented content chunks | Improves ranking for short-evidence queries | Low–medium | High |
| 5 | RAG/data ops | Check passage completeness on passage grounding dataset | Improves ranking | Low–medium | Medium |
| 6 | RAG/data ops | Experiment with embedding model | Improves retrieval | Low–medium | Medium |
| 7 | Agent dev | Experiment with score delta + frequency-weighted source selection | Improves precision without reducing recall | Low | High |
| 8 | Agent dev | Fix HCA source accumulation across sub-queries (reranker) | Closes recall gap with VA | Low–medium | Medium |
| 9 | Agent dev | Add fallback/safeguard for HCA when retrieval returns no URL | Cuts 58% HCA citationless rate on hard questions | Medium | High |

Actions 1–4 unblock accurate measurement of everything else — go first.
