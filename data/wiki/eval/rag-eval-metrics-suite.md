---
title: RAG Eval Metrics Suite
tags: [eval, rag, pattern]
summary: Eight-metric RAG evaluation framework covering stakeholder quality (faithfulness, naturalness, completeness, relevance), retrieval quality (contextual relevance, recall, document precision), and system calibration — split between runtime-compatible and offline-only metrics.
updated: 2026-07-06
sources:
  - raw/claude-docs/chat-agent/docs/eval/eval_metrics.md
---

# RAG Eval Metrics Suite

A comprehensive RAG evaluation framework with 8 metrics organized by focus area and availability. The key design insight is that runtime metrics (no ground truth needed) and offline metrics (require labelled test set) serve different debugging purposes and should not be conflated.

---

## Metrics Overview

| # | Metric | Focus | Judge | Runtime | Offline |
|---|---|---|---|---|---|
| 1 | Faithfulness | Stakeholder | LLM (independent model) | Yes | — |
| 2 | Response Naturalness | Stakeholder | LLM (same model ok) | Yes | — |
| 3 | Answer Completeness | Stakeholder | LLM (same model ok) | — | Yes |
| 4 | Answer Relevance | Stakeholder | LLM (same model ok) | Yes | — |
| 5 | Contextual Relevance | Retrieval | LLM + GCP native score | Yes | — |
| 6 | Contextual Recall | Retrieval | LLM (same model ok) | — | Yes |
| 7 | Document Precision | Retrieval | Deterministic (URL match) | — | Yes |
| 8 | Confidence Calibration | System | Deterministic (Spearman ρ) | — | Yes |

All scores logged via `langfuse.score(name="metric_name", value=score)`.

---

## Metric 1 — Faithfulness (Groundedness)

**Definition:** Every claim in the response is directly supported by the retrieved context chunks — not introduced from model parametric memory.

**Why it matters:** A response can be factually correct yet unfaithful — the model may be answering from world knowledge, which is unreliable when your KB contradicts general web knowledge (e.g., your specific refund policy).

**How:** LLM judge identifies claims in the response that cannot be traced to any chunk. Score = supported_claims / total_claims.

**Critical:** The judge **must be an independent model**. Using the same model that generated the response inflates scores — the model rationalises its own outputs as grounded.

**Pass:** ≥ 0.75 per query. < 0.5 flags likely hallucination.

---

## Metric 2 — Response Naturalness

**Definition:** Multi-dimensional quality score measuring how natural, clear, and appropriate the response reads in a customer support context.

**Five dimensions** (each scored 1–5):
1. **Coherence** — logical flow
2. **Clarity** — no ambiguity
3. **Relevance** — addresses the question asked
4. **Tone** — professional but approachable
5. **Conciseness** — not padded or repetitive

**Scoring rule:** A response fails if **any single dimension** falls below threshold, even if the average passes — this prevents a weak dimension being masked by strong scores elsewhere.

Log all sub-scores individually (`naturalness_clarity`, `naturalness_tone`, etc.) to enable dimension-level debugging.

**Pass:** All five dimensions ≥ 3.5; overall average ≥ 3.5.

---

## Metric 3 — Answer Completeness

**Definition:** Of all claims in the ground truth answer, how many does the generated response cover? (Recall-only — extra claims in the response don't hurt.)

**Why it matters:** Complements Faithfulness. Faithfulness catches hallucination (claims added without grounding); Completeness catches omission (expected information left out).

**How:** Extract atomic claims from ground truth. Judge checks each claim for coverage in the generated response. Run 3 passes; resolve by majority vote; ties default to MISSING (conservative).

Score = covered_GT_claims / total_GT_claims.

**Pass:** ≥ 0.75 per query. < 0.5 flags high-omission responses.

---

## Metric 4 — Answer Relevance

**Definition:** The generated response directly addresses and answers the user's question, independent of factual correctness or completeness.

**Why it matters:** A response can be faithful and complete yet still miss what the user actually asked — evasive, generic boilerplate, or answering a related but different question.

**How:** LLM judge receives query + response; scores 0–1 relevance. Run 3 passes; mean score. Track spread (max − min) as consistency indicator.

**Pass:** ≥ 0.75 per query. < 0.4 flags substantially off-topic responses.

### Completeness × Relevance Matrix

| | High Relevance | Low Relevance |
|---|---|---|
| **High Completeness** | Ideal | Covers GT claims but doesn't engage with what was asked |
| **Low Completeness** | On-topic but misses details | Neither on-topic nor complete |

---

## Metric 5 — Contextual Relevance

**Definition:** Fraction of retrieved chunks that are relevant to the user's query. A chunk is relevant if it could help answer the question — even partially.

**Why it matters:** Irrelevant chunks add noise to the context window, increase token cost, and can degrade generation quality.

**Dual signals (when GCP engine is available):**

| Signal | Source | What it measures |
|---|---|---|
| `contextual_relevance` | LLM judge | Semantic usefulness of each chunk for this specific query |
| `contextual_relevance_gcp_mean` | GCP `relevance_score` | Retrieval ranking confidence from the search engine |

High GCP score + low LLM score → search found a semantic match, but the chunk doesn't help answer this specific question (query-understanding problem). Low GCP + high LLM → atypical; engine ranked chunk low but judge finds it useful.

**Pass:** ≥ 0.6 per query. < 0.4 signals consistent off-topic retrieval.

---

## Metric 6 — Contextual Recall

**Definition:** Of all claims in the ground truth answer, how many are actually present in the retrieved context? A claim is present if it can be directly derived from the chunks.

**Why it matters:** The retrieval pipeline may surface the right topic but the wrong content — chunks that are topically relevant but lack the specific facts needed to reconstruct the correct answer. Low Contextual Recall means generation quality is **fundamentally constrained** — no prompt engineering can compensate.

**How:** Shared claim extraction with Answer Completeness (no duplicate LLM calls). Judge checks each GT claim for presence in retrieved chunks. Run 3 passes; majority vote; ties default to ABSENT.

Score = present_GT_claims / total_GT_claims.

**Pass:** ≥ 0.7 per query. < 0.5 indicates retrieval is structurally insufficient.

### Recall × Completeness Diagnostic

| | High Contextual Recall | Low Contextual Recall |
|---|---|---|
| **High Answer Completeness** | Ideal | Model covered GT claims despite insufficient context — check Faithfulness |
| **Low Answer Completeness** | Generation failure | Retrieval failure |

---

## Metric 7 — Document Precision

**Definition:** Fraction of retrieved chunks that originate from the expected source document(s). URL-level identity check, fully deterministic.

**Why it matters:** Contextual Relevance and Recall evaluate chunk *content* — they don't verify *which document* it came from. A pipeline can produce topically relevant, fact-rich chunks from the wrong article (outdated version, duplicate, related FAQ).

**How:** Each chunk's `.url` field is compared against `source_article_urls` from the dataset item using exact string matching. No LLM involved.

**Pass:** ≥ 0.7 per query. < 0.5 signals consistent wrong-source routing.

### Three-Metric Retrieval Taxonomy

| Metric | What's classified | Against what | Ground truth | Judge |
|---|---|---|---|---|
| Contextual Relevance | Each chunk (content usefulness) | User query | No | LLM |
| Contextual Recall | Each GT claim (content presence) | Retrieved chunks | Yes | LLM |
| Document Precision | Each chunk (source identity) | Expected URLs | Yes | Deterministic |

Low Document Precision + high Contextual Relevance → source-targeting or ranking problem, not embedding quality.

---

## Metric 8 — Confidence Calibration

**Definition:** Spearman's rank correlation (ρ) between the agent's ordinal confidence label (LOW=1, MEDIUM=2, HIGH=3) and Answer Completeness score, computed once across all items in a run.

**Why it matters:** If the confidence label is uncorrelated with actual quality, it adds noise. Well-calibrated confidence enables users to trust HIGH answers more and prioritise LOW answers for review.

**How:** `scipy.stats.spearmanr` on confidence ordinals vs completeness scores. Items with unparsed confidence (`UNKNOWN`) are excluded. A reliability gate: mark as unreliable if any confidence bucket has < 5 items.

**Pass:** ρ ≥ 0.4 with reliability gate passed.

| ρ range | Meaning |
|---|---|
| 0.5–1.0 | Good calibration |
| 0.2–0.5 | Weak positive signal |
| −0.2–0.2 | Label is uninformative |
| −0.5 to −0.2 | Mildly inverted |
| −1.0 to −0.5 | Systematically inverted — HIGH answers are less complete |

**Note:** Population-level metric only. Requires all three confidence tiers represented with ≥ 5 items each. Needs ~300+ item test set.

---

## Runtime vs Offline Summary

| Timing | Metrics | What you need |
|---|---|---|
| **Runtime** (every live query) | Faithfulness, Naturalness, Answer Relevance, Contextual Relevance | Only query + response + retrieved chunks |
| **Offline** (requires ground truth) | Answer Completeness, Contextual Recall, Document Precision, Confidence Calibration | Labelled test set with ground truth answers + source URLs |

---

## See Also
- [[Trajectory Over Outcome]] <!-- auto-linked -->
- [[Online Eval Sampling]] <!-- auto-linked -->
- [[Eval Non-Determinism]] <!-- auto-linked -->
- [[Manual Review as Eval Bootstrap]] <!-- auto-linked -->
- [[Eval Ladder]] <!-- auto-linked -->
- [[RAG Eval Gate Contract]] <!-- auto-linked -->
- [[project-g Eval Architecture]] <!-- auto-linked -->
- [[HITL Annotation Pipeline]] <!-- auto-linked -->
- [[VA Eval Harness]] <!-- auto-linked -->
- [[Synthetic Dataset Generation for RAG Eval]]
- [[RAG Evaluation]]
- [[LLM Grader Calibration Insights]]
- [[Langfuse Platform]]
- [[Langfuse ADK Tracing Patterns]]
- [[CRAG Retry Logic]]
- [[Heuristic Pipeline Metrics]] — related (operational health axis alongside retrieval metrics)
- [[Observability & Evaluation Glossary]] — rank-based retrieval metrics (MRR, precision@k, recall@k, ndcg@k, hit@k) and heuristic-vs-judge metric typing
