---
title: RAG Eval Gate Contract
tags: [eval, rag, pattern]
summary: Eight-gate ownership contract for RAG evaluation pipelines — each gate answers a distinct question about corpus quality, retrieval, generation, and grader calibration, with strict handoff contracts between gates.
updated: 2026-08-04
sources:
  - raw/claude-docs/project-g/docs/evals/gate-contract.md
---

# RAG Eval Gate Contract

The central rule: **do not collapse corpus quality, retrieval ranking, agent behavior, answer generation, and grader calibration into one score.** Each gate answers a different question and must preserve its row pool, config, and failure labels for downstream interpretation.

---

## Gate Ladder

| Gate | Question | Entry point |
|------|----------|-------------|
| 1 — Corpus QA | Is the corpus valid? | `validate_data_contract` pipeline |
| 2 — Index Readiness | Does the index represent the corpus? | Notebook / embed cache |
| 3 — Retrieval Optimization | Which config finds the right evidence? | Retrieval sweep + `plot_gate_figures.py` |
| 4 — Model / Runtime | Which model to evaluate on? | `build_agent_comparison` pipeline |
| 5 — Agent Retrieval | Do agent features improve source selection? | `build_agent_comparison` + ablation |
| 6 — Generation Quality | Did the answer use evidence correctly? | `run quality` → `eval_quality.py` |
| 7 — Grader Calibration | Do graders match user outcomes? | `calibration_report.py` |
| 8 — Report / Handoff | What should stakeholders do next? | `eval_story.py` render |

---

## Common Handoff Contract

Every gate must emit enough evidence for the next owner to proceed without reverse-engineering upstream state.

**Input contract:** named row pool, artifact paths, run ID, git commit, config snapshot, timestamp, known exclusions.

**Output contract:** pass/fail status, metric summary, row-level diagnostics, failure taxonomy labels, recommended next action.

**Compliance rule:** a downstream gate must not silently score rows the upstream gate marked ineligible. Ineligible rows appear only as a separate diagnostic slice.

**Report rule:** every stakeholder-facing claim must name the gate, row pool, sample size, and source artifact behind it.

---

## Canonical Row Pools

| Pool | Definition |
|---|---|
| `all_gt` | Every golden-trace row, including topic proxies not fair for retrieval scoring |
| `source_mapped_gt` | Rows whose expected URLs can be resolved to a known groundable source |
| `retrieval_eligible_gt` | Mapped rows whose expected source is present in the indexed corpus |
| `generation_eligible_gt` | Rows where at least one retrieval backend returns an expected URL in top-k |
| `quality_sample` | Deterministic, cost-capped sample for LLM grading |

---

## Failure Taxonomy (Stable Labels)

| Label | Meaning |
|---|---|
| `source_missing` | Expected source absent from corpus |
| `url_unmapped` | Expected URL cannot be matched to canonical source |
| `topic_proxy` | Source useful for coverage but not groundable as citation (e.g. [product]-kb) |
| `index_lag` | Source exists in corpus but not in vector index |
| `chunk_fragmented` | Evidence split too thin for ranking/generation |
| `rank_miss` | Expected source indexed but not returned in top-k |
| `query_rewrite_miss` | Query reformulation loses user intent |
| `reranker_regression` | Reranker demotes an otherwise correct candidate |
| `context_missing` | Passage-required grader received URLs or empty context |
| `citation_hallucination` | Final answer cites URL outside retrieved set |
| `unsupported_claim` | Answer makes claim not grounded in retrieved passages |
| `incomplete_answer` | Answer misses a required sub-question or action |
| `wrong_escalation` | Escalates when it should answer, or answers when it should escalate |

---

## Gate 3 — Retrieval Optimization

Run only on `retrieval_eligible_gt`. Track:
- Ranking metrics: MRR, P@1, R@3, R@5, NDCG@3, NDCG@5
- Slice metrics by source type, language, query length, difficulty
- Cost/latency: p50/p95 retrieval latency, backend calls, reranker latency
- Config dimensions: dense/sparse/hybrid, chunk size/overlap, top-k, threshold, reranker

**Compliance:** do not pick a winner from aggregate MRR alone. The recommendation must include row pool, sample size, source slices, and latency/cost.

---

## Gate 6 — Generation Quality

Run on `quality_sample`, sliced by generation eligibility. Track:
- **Heuristic gates:** citation hallucination, missing citation, citation recall, language consistency, F1 correctness, boundary adherence
- **Passage-required LLM gates:** grounding, RAGAS context precision, RAGAS faithfulness
- **User-quality gates:** answer relevancy, completeness, escalation alignment

**Compliance:** do not mix URL-only context with passage-text context in the same grounding/RAGAS pass-rate claim.

---

## Gate 7 — Grader Calibration

Track: liked vs disliked score separation, Cohen's d, precision/recall/F1 against user sentiment, pass-rate stability by query type/language/model.

**Compliance:** experimental graders can inform investigation, but stakeholder recommendations must not use them as hard promotion evidence.

---

## Metric Registry

### Retrieval Metrics (alias-aware)
`mrr`, `p@1`, `p@3`, `p@5`, `r@1`, `r@3`, `r@5`, `f1@1`, `f1@3`, `f1@5`, `ndcg@1`, `ndcg@3`, `ndcg@5`

### Heuristic Integrity Gates
| Metric | Threshold |
|---|---|
| `citation_hallucination` | 0.95 |
| `missing_citation` | 0.90 |
| `citation_recall` / `source_match` | 0.50 |
| `language_consistency` | 0.95 |
| `f1_correctness` | 0.70 |
| `boundary_adherence` | 0.80 |

### Calibrated Quality Gates
| Metric | Threshold |
|---|---|
| `answer_relevancy_voted` | 0.75 |
| `completeness_voted` | 0.70 |
| `grounding_voted` | 0.60 (passage text required) |
| `ragas_context_precision_voted` | 0.50 (passage text required) |
| `ragas_faithfulness_voted` | 0.50 (passage text required) |

**Passage-required graders must receive retrieved passage text, not URL strings.** If passage text is unavailable, label the row `context_missing` and keep it out of hard release claims.

---

## See Also
- [[Eval vs Test Distinction]] — prerequisite-for
- [[The Augmentation Gate]] — extends (the missing rung between Gate 3 and Gate 6)
- [[Trajectory Over Outcome]] — complements (wrong_escalation as a routing failure, checkable only against a path)
- [[Golden Set Mechanics]]
- [[System Design — Unified Eval Harness]] — instance-of
- [[project-g Eval Architecture]]
- [[RAG Evaluation]]
- [[LLM Grader Calibration Insights]]
- [[Reciprocal Rank Fusion (RRF)]]
- [[CRAG Retry Logic]]
- [[RL for Retrieval Policies]] — complements (component gates as the eval-side answer to sub-task/end-task reward divergence)
- [[AI Engineering Curriculum Structure]] — complements (observability-as-infrastructure vs eval-as-discipline, the split these gates operationalise)
