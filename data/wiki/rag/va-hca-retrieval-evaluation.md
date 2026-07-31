---
title: VA vs HCA Retrieval Evaluation
tags: [rag, eval, comparison]
summary: Benchmarking results comparing VA, HCA (Bedrock), and local RAG baselines across 935 Danish support questions — VA outperforms HCA on all dimensions (MRR 0.286 vs 0.248), but 47% corpus ceiling means data-ops fixes dominate model-level improvements.
updated: 2026-07-14
sources:
  - raw/notion/2026-06-26-va-hca-retrieval-executive-summary.md
  - raw/meetings/2026-06-23-onboarding-shyamali-session1.md
---

# VA vs HCA Retrieval Evaluation

Systematic comparison of production VA agent, production HCA (Bedrock-backed), and local RAG research baselines across 935 Danish Intercom support questions. Ground truth: ~24,000 real Danish Intercom conversations, URL-cited subset. [product]/[client] alias map applied ([product].dk/support/ → help.[client].co/da/articles/).

**Evaluation date:** 2026-06-26. Dataset: n=754 (URL-cited subset of 935 questions).

---

## Performance Metrics

| System | MRR | P@3 | R@3 | NDCG@5 | Hit@5 | Avg sources |
|---|---|---|---|---|---|---|
| VA (production) | **0.286** | 0.110 | 0.156 | 0.181 | **0.350** | 13.0 |
| HCA (production) | 0.248 | 0.097 | 0.135 | 0.156 | 0.301 | 3.8 |
| Bedrock (direct) | 0.148 | — | — | — | 0.285 | — |
| Local RAG, single query | 0.225 | **0.132** | 0.127 | 0.217 | 0.328 | ~5 |
| Local RAG, multi-query | 0.316 | 0.128 | **0.361** | 0.336 | 0.435 | 23.8 |
| Local-ADK | **0.375** | **0.151** | 0.422 | **0.521** | 0.405 | 19.8 |
| Local-LG | 0.310 | 0.130 | 0.365 | 0.442 | 0.340 | 23.8 |

*Local RAG is a research baseline, not production. Local-ADK is best overall at MRR 0.375.*

**VA outperforms HCA on every production dimension.** The key mechanism: VA pools 2–3 reformulated queries (~13 sources average) while HCA's narrow retry loop returns ~4 sources with no reranker and no fallback. On the hardest 442 questions (missed by all systems), HCA returns no citation 58% of the time vs VA's 39%.

---

## LLM-as-Judge Answer Quality

VA scores higher on all five quality dimensions:

| Metric | VA | HCA | What it measures |
|---|---|---|---|
| Grounding | **0.776** | 0.633 | Are claims tied to retrieved sources? |
| Answer Relevancy | **0.891** | 0.825 | Does the answer address what was asked? |
| Completeness | **0.848** | 0.731 | Are all parts answered? |
| Faithfulness | **0.592** | 0.511 | Does it stay within retrieved content? |
| Context Precision | **0.456** | 0.453 | Are retrieved passages on-topic? |

**Grounding gap (+0.143) is the strongest signal.** When HCA's narrow retrieval misses the article, the model fills from general knowledge — no citation, no grounding.

**Faithfulness caveat:** Both systems score low (~0.5–0.6). Both models add unsupported detail even when grounding is decent. This is a model behavior issue, not a retrieval issue. See [[LLM Grader Calibration Insights]] for grounding vs faithfulness distinction.

---

## The 47% Corpus Ceiling — Root Cause Analysis

**442 of 935 questions are missed by every system.** This is not a retrieval or agent problem — it is a corpus quality problem. The corpus ceiling caps everything downstream.

| Cause | Est. questions | Fix |
|---|---|---|
| Glossary pages ranking above help articles | ~130 | Scope KB to help articles only |
| Articles missing from index | ~93 | Re-ingest 202 sources |
| URL mapping gap ([product] → [client] migration) | ~35–40 | Expand alias map |
| Ranking failure (article indexed but buried) | ~175–185 | Requires embedding model upgrade |

**Fixing causes 1 + 2 recovers ~220 questions**, raising the achievable ceiling from ~40% to **~59% Hit@5 with zero model or agent change**.

**Important limitation:** The ~59% ceiling applies to the URL-cited slice of traffic, which skews toward single-document-answerable questions. Real support volume coverage is lower.

**Stale content risk:** Two glossary pages contain confirmed wrong facts — NemID described as active (deprecated 2023), Danish bookkeeping law described as upcoming (took effect 2022). Corpus QA is ongoing.

---

## Two Independent Levers

This is the central organizing framework for improvement prioritization:

### Lever 1: Corpus Quality (dominant lever)
Affects every system equally. Scope + re-ingest = ~2x hit rate improvement at near-zero cost. **Go here first.**

Data-ops fixes in priority order:
1. Scope Bedrock corpus to help articles only (removes ~30% of shared failures — very low effort)
2. Re-ingest 202 missing articles (unlocks ~200 unanswerable questions — low effort)
3. Strip HTML boilerplate before next content sync (removes noise from top results)
4. Fix fragmented content chunks (improves ranking for short-evidence queries)

### Lever 2: Retrieval Strategy (agent layer)
Where VA beats HCA. Multi-query pooling → reranking → top-5 filter is the VA architecture advantage.

Agent-level improvements in priority order:
1. Score delta + frequency-weighted source selection (improves precision without reducing recall — low effort)
2. Fix HCA source accumulation across sub-queries (closes recall gap with VA)
3. Add fallback/safeguard when retrieval returns no URL (cuts HCA's 58% citationless rate)

**Critical constraint:** High-impact model swaps (multilingual embedding, multilingual reranker) require confirming that Bedrock can run non-Bedrock models. This is an explicit feasibility gate — confirm before sequencing any model-swap work.

### HCA Architecture Detail (from 2026-06-23 onboarding)

HCA's additions on top of the base tool (per Dan): claims extraction (the [[Grounding Claim Methodology]] "yellow highlighter" pattern), [[Reciprocal Rank Fusion (RRF)]], language detection, and an iterative RAG retry loop (max 6 steps). Per the same source, HCA has **no re-ranker** and **discards earlier selections** on each retry iteration rather than accumulating them — described as "not well-thought-through." This lines up with the source-accumulation gap noted above (item 2) and the 58% citationless rate on hard questions: without reranking or accumulation across retries, each retry throws away prior candidate sources instead of building toward a fuller pool like VA's multi-query approach does.

---

## Retrieval Configuration Recommendations

| Change | Current (Bedrock) | Research best | Gain |
|---|---|---|---|
| Embedding model | Amazon Titan (English-dominant) | Multilingual e5-large | +0.069 MRR |
| Chunk size | Hierarchical 1500-token parent | Overlapping 256 tokens / 64 overlap | +0.014 MRR |
| HTML parsing | Raw Intercom HTML | Preprocessed — boilerplate stripped | Impacts downstream quality |
| Reranker | Undocumented (possibly English-only) | Multilingual cross-encoder | +0.028 MRR |
| Retrieval method | Dense | Dense (hybrid adds no benefit here) | — |

**Warning on English-only reranker:** An English-only reranker actively *regresses* Danish retrieval. Verify language coverage before deploying any reranker change.

**CRAG (iterative re-retrieval):** +0.005 MRR at +3.4s latency. Not worth it for a live support agent at the current corpus quality level — fix the corpus first, then reconsider.

---

## Failure Attribution Taxonomy

Named failure taxonomy from this evaluation — useful for categorizing future failures:

| Failure type | What happened | Root cause | Fix layer |
|---|---|---|---|
| Coverage gap | Topic not in KB | Content never added or scoped out | Corpus QA |
| Retrieval failure | Wrong or missing docs | Not indexed, fragmented, or vocab mismatch | Index / retrieval config |
| Ranking failure | Right docs found but buried | Reranker demotes correct Danish passages | Retrieval optimization |
| Routing failure | Answered when should escalate | No confidence gate | Agent behavior |
| Generation failure | Right docs retrieved, wrong answer | Model didn't use context | Quality calibration |
| Grounding failure | Answer contains unsupported claims | Model extrapolated beyond sources | Quality calibration |

---

## Connection to Golden Dataset

This evaluation uses n=754 URL-cited questions as ground truth. A separate, curated ~100-question golden dataset has been built for ongoing Langfuse pipeline evaluation. See [[VA Eval Harness]] for the golden dataset status and pipeline setup.

---

## See Also
- [[RAG Evaluation]]
- [[RAG Retrieval Strategies]]
- [[RAG Reranking]]
- [[project-g Eval Architecture]]
- [[LLM Grader Calibration Insights]]
- [[VA Eval Harness]]
- [[Agentic RAG — Advanced Patterns]]
- [[[client] Knowledge Agent]]
- [[CRAG Retry Logic]]
