# Evaluation Metrics — Agentic RAG Chatbot

> **System context:** Customer support chatbot built on Google Gemini + pgvector, implementing Adaptive RAG, Corrective RAG, and Reflection patterns. Knowledge base sourced from Intercom help center articles (invoicing, bank accounts, subscriptions, payments).

---

## Overview

| # | Metric | Focus | Judge Type | When to Run | Langfuse Native |
|---|--------|-------|------------|-------------|-----------------|
| 1 | Faithfulness | Stakeholder | LLM-as-judge (independent model) | Runtime | Via `langfuse.score()` |
| 2 | Response Naturalness | Stakeholder | LLM-as-judge | Runtime | Via `langfuse.score()` |
| 3 | Answer Completeness | Stakeholder | LLM-as-judge | Offline (requires ground truth) | Via `langfuse.score()` |
| 4 | Answer Relevance | Stakeholder | LLM-as-judge | Runtime | Via `langfuse.score()` |
| 5 | Contextual Relevance | Retrieval | LLM-as-judge + GCP native score | Runtime | Via `langfuse.score()` |
| 6 | Contextual Recall | Retrieval | LLM-as-judge | Offline (requires ground truth) | Via `langfuse.score()` |
| 7 | Document Precision | Retrieval | Deterministic (URL match) | Offline (requires ground truth) | Via `langfuse.score()` |
| 8 | Confidence Calibration | System | Deterministic (Spearman ρ) | Offline (requires ground truth) | Via `langfuse.score()` |

---

## Metric 1 — Faithfulness (Groundedness)

| Field | Detail |
|---|---|
| **Focus** | Stakeholder |
| **Definition** | The degree to which every claim in the response is directly supported by the retrieved context chunks, rather than introduced from model world knowledge or hallucinated. |
| **Purpose** | A response can be factually correct but not grounded in the KB — the model may be answering from parametric memory, which is unreliable in a domain-specific support context where your KB may contradict general web knowledge (e.g. your specific refund policy). Faithfulness catches this. |
| **What it evaluates** | The relationship between the final response and the retrieved context passed to the generation step. Measures whether the response stays within what the retrieval surface supports. |
| **How it works** | An LLM receives the retrieved context chunks and the generated response, then identifies claims in the response that cannot be traced to any chunk. Score = (supported claims) / (total claims). |
| **Judge type** | LLM-as-judge — **must be an independent model**. Using the same Gemini model that generated the response will produce inflated scores as the model rationalises its own outputs as grounded. |
| **How to score** | Continuous 0–1. Log via `langfuse.score(name="faithfulness", value=score)`. Because the retrieved context and response are already captured in your Langfuse trace, the judge can read both from trace data. |
| **Suggested pass criteria** | Faithfulness ≥ 0.75 per query. Queries scoring below 0.5 should be flagged as likely hallucination events. |
| **Langfuse native** | No built-in computation — score via `langfuse.score()`. Trace already contains the required inputs (retrieved docs + response). |
| **When to use** | Runtime, on live traffic. Both inputs (retrieved context, response) are available at the end of each query cycle without needing a ground-truth answer. |
| **What's needed** | Access to the retrieved chunks from the trace; independent judge model; judge prompt that extracts claims and maps them to context passages. |

> ⚠️ **Shared-model risk:** This is the metric most vulnerable to self-evaluation bias. Using the same model for retrieval, generation, and faithfulness judging will produce misleadingly high scores.

---

## Metric 2 — Response Naturalness

| Field | Detail |
|---|---|
| **Focus** | Stakeholder |
| **Definition** | A multi-dimensional LLM judge score measuring how natural, clear, and appropriate the response reads to an end user in a customer support context. |
| **Purpose** | Stakeholders and end users notice communication quality even when factual correctness is high. A technically correct response that sounds robotic, overly verbose, or tonally inappropriate degrades user trust and support experience. |
| **What it evaluates** | Five dimensions: **Coherence** (logical flow), **Clarity** (no ambiguity), **Relevance** (addresses the question asked), **Tone** (professional but approachable, appropriate for support), **Conciseness** (not padded or repetitive). |
| **How it works** | An LLM scores each dimension 1–5. Overall score is the average. A response fails if *any single dimension* falls below threshold, even if the average is acceptable — this prevents a single poor dimension being masked by strong scores elsewhere. |
| **Judge type** | LLM-as-judge. Can use the same model family here (unlike Faithfulness) since the judge is assessing communication quality, not factual accuracy — less susceptible to self-confirmation bias. |
| **How to score** | Average of 5 sub-scores on 1–5 scale. Log all sub-scores individually via `langfuse.score()` (e.g. `naturalness_clarity`, `naturalness_tone`) to enable dimension-level debugging. |
| **Suggested pass criteria** | All five dimensions ≥ 3.5; overall average ≥ 3.5. Fail if any single dimension < 3.5 even if average passes. |
| **Langfuse native** | Score via `langfuse.score()`. Response is available in trace. Can be run as a post-generation hook at runtime. |
| **When to use** | Runtime, on live traffic. Response-only — no ground truth or context access needed. |
| **What's needed** | Judge prompt defining the five dimensions in the context of customer support (not generic chat); clear scoring rubric per dimension. |

---

## Metric 3 — Answer Completeness

| Field | Detail |
|---|---|
| **Focus** | Stakeholder |
| **Definition** | A recall-only score: of all the claims present in the ground truth answer, how many does the generated response cover? Extra claims in the generated response do not affect the score. |
| **Purpose** | Faithfulness detects hallucination (claims added without grounding). Answer Completeness detects the complementary failure: omission — critical information that the correct answer contains but the generated response leaves out. Together they bound response quality from both directions. |
| **What it evaluates** | The relationship between the generated response and the ground truth answer. Measures how much of the expected information the response delivers, independent of how much extra information it adds. |
| **How it works** | Atomic claims are extracted from the ground truth answer. An LLM judge then evaluates whether each claim is covered by the generated response, even if paraphrased. Score = (covered GT claims) / (total GT claims). The judging pass is repeated 3 times and resolved by majority vote; ties default to MISSING (conservative). |
| **Judge type** | LLM-as-judge. Can use the same model family as generation (unlike Faithfulness) — the judge is assessing information coverage, not factual grounding, so self-confirmation bias is less of a concern. |
| **How to score** | Continuous 0–1. Log via `langfuse.score(name="answer_completeness", value=score)`. Also log `missing_count` (absolute count of uncovered GT claims) for debugging. |
| **Suggested pass criteria** | Answer Completeness ≥ 0.75 per query. Queries scoring below 0.5 should be flagged as high-omission responses. |
| **Langfuse native** | No built-in computation — score via `langfuse.score()`. Both the generated response and ground truth answer are available at evaluation time. |
| **When to use** | Offline, against a labelled test set. Requires a ground truth answer — not available for runtime scoring on live traffic. |
| **What's needed** | Ground truth answer for each test item; judge prompt that extracts GT claims and checks coverage in the generated response. |

---

## Metric 4 — Answer Relevance

| Field | Detail |
|---|---|
| **Focus** | Stakeholder |
| **Definition** | A holistic score measuring whether the generated response directly addresses and answers the user's question, independent of factual correctness or information completeness. |
| **Purpose** | A response can be factually grounded (high faithfulness) and cover all expected claims (high completeness) yet still fail to answer what the user actually asked — for example by answering a related but different question, being evasive, or providing generic boilerplate. Answer Relevance catches this failure mode independently. |
| **What it evaluates** | The relationship between the user's question and the generated response. Measures whether the response is on-topic, direct, and actually engages with the specific question asked. |
| **How it works** | An LLM judge receives the query and the generated response and scores relevance on a [0, 1] scale. The judging pass is repeated 3 times; the final score is the mean across runs. Spread (max − min) is tracked as a consistency indicator. |
| **Judge type** | LLM-as-judge. Can use the same model family as generation — the judge is assessing topical engagement, not factual grounding, so self-confirmation bias is less of a concern. |
| **How to score** | Continuous 0–1. Log via `langfuse.score(name="answer_relevance", value=score)`. Only requires the query and the response — no retrieved context or ground truth needed. |
| **Suggested pass criteria** | Answer Relevance ≥ 0.75 per query. Scores below 0.4 indicate the response is substantially off-topic or evasive. |
| **Langfuse native** | No built-in computation — score via `langfuse.score()`. Both query and response are available in the trace. |
| **When to use** | Runtime, on live traffic. Requires only the query and the response — no ground truth or retrieved context access needed. |
| **What's needed** | Judge prompt with a clear scoring rubric distinguishing on-topic direct answers from evasive, off-topic, or redirect-only responses. |

### Relationship to Other Metrics

Answer Relevance is intentionally decoupled from Answer Completeness:

| | High Relevance | Low Relevance |
|---|---|---|
| **High Completeness** | Ideal: answers the question and covers all expected information | Covers GT claims but doesn't engage with what was asked |
| **Low Completeness** | Answers the question but misses expected details | Neither on-topic nor complete |

Both dimensions are needed for a full picture of answer quality.

---

## Metric 5 — Contextual Relevance

| Field | Detail |
|---|---|
| **Focus** | Retrieval |
| **Definition** | The fraction of retrieved chunks that are relevant to the user's query. A chunk is relevant if it contains information that could help answer the question — even partially. |
| **Purpose** | Not all retrieved chunks contribute meaningfully to generation. Irrelevant chunks add noise to the context window, increase token cost, and can degrade generation quality. Contextual Relevance identifies this failure mode at the retrieval level, independent of what the model ultimately generates. |
| **What it evaluates** | The relationship between the user's query and each individual retrieved chunk. Measures whether the retrieval pipeline is surfacing topically useful content, not just topically adjacent content. |
| **How it works** | An LLM judge receives the query and the retrieved chunks (numbered) and classifies each chunk as RELEVANT or IRRELEVANT. The judging pass is repeated 3 times; results are resolved by per-chunk majority vote. Ties default to IRRELEVANT (conservative). Score = relevant_chunks / total_chunks. When using the GCP engine, a secondary signal `contextual_relevance_gcp_mean` is also published — the mean of GCP's native `relevance_score` across all chunks. |
| **Judge type** | LLM-as-judge for the primary score. GCP native score as a secondary signal when available. |
| **How to score** | Continuous 0–1. Log via `langfuse.score(name="contextual_relevance", value=score)`. Also log `irrelevant_chunk_count` (absolute count) for debugging. |
| **Suggested pass criteria** | Contextual Relevance ≥ 0.6 per query. Scores below 0.4 indicate the retrieval pipeline is consistently surfacing off-topic content. |
| **Langfuse native** | No built-in computation — score via `langfuse.score()`. Query and retrieved chunks are available in the trace. |
| **When to use** | Runtime, on live traffic. Requires only the query and retrieved chunks — no ground truth or generated response needed. |
| **What's needed** | Judge prompt defining relevance vs. topical adjacency; retrieved chunk list from the trace. |

### Dual Signals: LLM Judge vs GCP Native Score

When using the GCP engine, both signals are available simultaneously:

| Signal | Source | What it measures |
|---|---|---|
| `contextual_relevance` | LLM-as-judge | Semantic usefulness of each chunk for this specific query |
| `contextual_relevance_gcp_mean` | GCP `relevance_score` | Retrieval ranking confidence from the GCP search engine |

High GCP score + low LLM score → the search engine found a good semantic match, but the chunk does not actually help answer this specific question (likely a query-understanding problem). Low GCP score + high LLM score → atypical; the search engine ranked the chunk low but the judge finds it useful.

---

---

## Metric 6 — Contextual Recall

| Field | Detail |
|---|---|
| **Focus** | Retrieval |
| **Definition** | A recall-only score: of all the claims present in the ground truth answer, how many are actually findable in the retrieved context? A claim is present if it can be directly derived from the chunks — exact wording is not required, but the essential information must be explicitly stated. |
| **Purpose** | Even when retrieved chunks are topically relevant to the query, they may not contain the specific facts needed to reconstruct the correct answer. Contextual Recall surfaces this failure mode: the retrieval pipeline is surfacing the right *topic* but the wrong *content*. A low score means generation quality is fundamentally constrained — no prompt engineering can compensate for missing facts in the context window. |
| **What it evaluates** | The relationship between the retrieved context and the ground truth answer. Measures whether the retrieval pipeline surfaces the information needed to produce a correct response, independent of what the model ultimately generates. |
| **How it works** | Atomic claims are extracted from the ground truth answer (shared with Answer Completeness — no duplicate LLM calls). An LLM judge then evaluates whether each claim is present in the retrieved chunks, even if paraphrased. Score = (present GT claims) / (total GT claims). The judging pass is repeated 3 times and resolved by majority vote; ties default to ABSENT (conservative). |
| **Judge type** | LLM-as-judge. Can use the same model family as generation — the judge is assessing content coverage in the context, not factual grounding of the response. |
| **How to score** | Continuous 0–1. Log via `langfuse.score(name="contextual_recall", value=score)`. Also log `absent_count` (absolute count of uncovered GT claims) for debugging. |
| **Suggested pass criteria** | Contextual Recall ≥ 0.7 per query. Scores below 0.5 indicate the retrieval pipeline is structurally insufficient to produce a correct answer — address the retrieval step before tuning generation. |
| **Langfuse native** | No built-in computation — score via `langfuse.score()`. Both the retrieved chunks and ground truth answer are available at evaluation time. |
| **When to use** | Offline, against a labelled test set. Requires a ground truth answer — not available for runtime scoring on live traffic. |
| **What's needed** | Ground truth answer for each test item; judge prompt that extracts GT claims and checks whether each is derivable from the retrieved chunks. |

### Relationship to Other Metrics

| | High Contextual Recall | Low Contextual Recall |
|---|---|---|
| **High Answer Completeness** | Ideal: context has what's needed and the model used it | Model covered GT claims despite the context being insufficient — likely using parametric memory (check Faithfulness) |
| **Low Answer Completeness** | Context was sufficient but the model missed claims — generation failure | Context was insufficient from the start — retrieval failure |

Contextual Recall diagnoses whether Answer Completeness failures are retrieval-caused or generation-caused.

### Distinction from Related Retrieval Metrics

| Metric | What's classified | Against what | Requires ground truth |
|---|---|---|---|
| Contextual Relevance | Each retrieved chunk | User query | No |
| **Contextual Recall** | **Each GT claim** | **Retrieved context** | **Yes** |

Contextual Relevance is query-driven (runtime-compatible). Contextual Recall is content-driven (offline only). A pipeline can score highly on Contextual Relevance — topically useful chunks — while scoring poorly on Contextual Recall if those chunks lack the specific facts in the ground truth.

---

## Metric 7 — Document Precision

| Field | Detail |
|---|---|
| **Focus** | Retrieval |
| **Definition** | The fraction of retrieved chunks that originate from the expected source document(s). A chunk is matched if its URL exactly equals any URL listed in the dataset item's `source_article_urls`. |
| **Purpose** | Contextual Relevance and Contextual Recall evaluate chunk *content* — they do not verify *which document* a chunk comes from. A retrieval pipeline can produce topically relevant, fact-rich chunks that still originate from the wrong article: an outdated version, a related FAQ, or a duplicate entry. Document Precision catches this identity-level failure mode. |
| **What it evaluates** | The identity of retrieved chunks against the expected source document(s). Measures whether the retrieval pipeline is correctly targeting the right articles, independent of chunk content quality. |
| **How it works** | Each retrieved chunk's `.url` field is compared against the set of `source_article_urls` from the dataset item using exact string matching. Score = matched_chunks / total_chunks. No LLM judge is involved — the calculation is fully deterministic. |
| **Judge type** | None — deterministic URL match. |
| **How to score** | Continuous 0–1. Log via `langfuse.score(name="document_precision", value=score)`. Also log `mismatched_count` (absolute count of off-source chunks) for debugging. |
| **Suggested pass criteria** | Document Precision ≥ 0.7 per query. Scores below 0.5 indicate the retrieval pipeline is consistently routing to the wrong source documents. |
| **Langfuse native** | No built-in computation — score via `langfuse.score()`. Both retrieved chunks (with `.url` metadata) and `source_article_urls` are available at evaluation time. |
| **When to use** | Offline, against a labelled test set. Requires `source_article_urls` in the ground truth — not available for runtime scoring on live traffic. |
| **What's needed** | Dataset items with `source_article_urls`; retrieved chunks with `.url` metadata populated. |

> **Document-level scope:** The ground truth contains source document URLs, not chunk-level provenance. All chunks from the correct article score as matched, regardless of which section they come from. This is an honest reflection of what the dataset supports. The metric is named "Document Precision" rather than "Contextual Precision" to make this scope explicit.

### Relationship to Other Retrieval Metrics

| Metric | What's classified | Against what | Requires ground truth | Judge type |
|---|---|---|---|---|
| Contextual Relevance | Each chunk (content usefulness) | User query | No | LLM |
| Contextual Recall | Each GT claim (content presence) | Retrieved chunks | Yes | LLM |
| **Document Precision** | **Each chunk (source identity)** | **Expected source URLs** | **Yes** | **Deterministic** |

Document Precision is the only identity-based metric. Low Document Precision alongside high Contextual Relevance points to a source-targeting or ranking problem rather than an embedding quality problem.

---

## Metric 8 — Confidence Calibration

| Field | Detail |
|---|---|
| **Focus** | System |
| **Definition** | Spearman's rank correlation (ρ) between the chatbot's ordinal confidence label (LOW=1, MEDIUM=2, HIGH=3) and the Answer Completeness score, computed once across all items in an evaluation run. |
| **Purpose** | The chatbot appends a confidence label (HIGH / MEDIUM / LOW) to every response. If this label is well-calibrated, it functions as a reliability signal — users can trust HIGH-confidence answers more and prioritise LOW-confidence responses for review. If the label is uncorrelated with actual quality, it adds noise rather than information. Confidence Calibration measures this alignment at the population level. |
| **What it evaluates** | The relationship between the system's self-reported confidence and measured answer quality (completeness) across an entire evaluation run. Not a per-query score — a single miscalibrated response does not affect the result. |
| **How it works** | Confidence labels from all items are encoded as ordinals (LOW=1, MEDIUM=2, HIGH=3) and paired with their Answer Completeness scores. `scipy.stats.spearmanr` computes the rank correlation. Items whose confidence label could not be parsed (`UNKNOWN`) are excluded. A reliability gate flags the result as unreliable if any confidence bucket contains fewer than 5 items — ensuring the correlation is based on adequate representation of all tiers. |
| **Judge type** | None — deterministic statistical computation (Spearman's rank correlation). No LLM involved. |
| **How to score** | ρ ∈ [−1, 1]. Logged via `langfuse.score()` at run level. A second score `confidence_calibration_reliable` (0 or 1) flags whether the minimum bucket size requirement was met. |
| **Suggested pass criteria** | ρ ≥ 0.4 with `confidence_calibration_reliable = 1`. Values near 0 mean the confidence label carries no useful information. Negative values indicate the label is systematically inverted. |
| **Langfuse native** | No built-in computation — score via `langfuse.score()`. Both confidence labels (parsed from response text) and Answer Completeness scores are available at evaluation time. |
| **When to use** | Offline, after a full evaluation run with Answer Completeness. Requires a dataset that produces items across all three confidence tiers; a dataset with only HIGH-confidence responses cannot yield a meaningful ρ. |
| **What's needed** | Answer Completeness scores for all items; response text containing `"Confidence: HIGH/MEDIUM/LOW"` appended by the synthesis step. |

> **Population-level limitation:** Confidence Calibration is computed once per run and registered at run level only. There is no item-level score. Results are only interpretable when all three confidence tiers are represented in the dataset with at least `MIN_BUCKET_SIZE = 5` items each.

### Score Interpretation

| ρ range | Meaning |
|---|---|
| 0.5 – 1.0 | Good calibration — HIGH responses are measurably more complete |
| 0.2 – 0.5 | Weak positive signal — some alignment, room for improvement |
| −0.2 – 0.2 | No meaningful correlation — the confidence label is uninformative |
| −0.5 – −0.2 | Weak negative signal — label is mildly inverted |
| −1.0 – −0.5 | Inverted calibration — HIGH-confidence responses are systematically less complete |

### Relationship to Other Metrics

Confidence Calibration is the only metric that cross-references two pipeline outputs: the agent's self-assessed confidence and the LLM-judged completeness score.

| Metric | What it measures | Ground truth required |
|---|---|---|
| Answer Completeness (3) | How much of the expected answer was delivered | Yes |
| **Confidence Calibration (8)** | **Whether confidence label predicts completeness** | **Yes (via completeness)** |

---

## Appendix: Runtime vs Offline Summary

| When | Metrics |
|------|---------|
| **Runtime (every live query)** | Faithfulness (1), Naturalness (2), Answer Relevance (4), Contextual Relevance (5) |
| **Offline (requires ground truth)** | Answer Completeness (3), Contextual Recall (6), Document Precision (7), Confidence Calibration (8) |
