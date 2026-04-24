# MVP Feedback Loop & Evaluation

Date: 2026-04-14
Based on: RAPTOR Evaluation Tech Doc (Three-Stage Approach: Detection, Attribution, Control)

## Overview

Five tasks to establish the evaluation feedback loop for the RAPTOR CS agent. Tasks build on the existing grader infrastructure in `src/eval/graders/` and follow the three-stage RAPTOR framework: **Detect** problems (automated metrics + human review), **Attribute** causes (tracing + failure clustering), **Control** outcomes (guardrails + confidence gates).

**Reporting layer:** Langfuse is the current experiment tracking and scoring backend. DataDog is the target production dashboard — migration is a dependency for Tasks 3 and 5. Both are referenced below; Langfuse for what works today, DataDog for what the tasks must eventually deliver.

---

## Grader Coverage Map (Tech Doc → Implementation)

| Tech Doc Metric | Grader | Status |
|---|---|---|
| Faithfulness | `DeepEvalGrader`, `RagasGrader` | Exists |
| Answer Relevancy | `DeepEvalGrader`, `RagasGrader` | Exists |
| Context Relevancy | `DeepEvalGrader` (contextual_relevancy) | Exists |
| Hallucination Rate | `DeepEvalGrader` (hallucination) | Exists |
| Answer Accuracy | `ExactMatchGrader`, `MCQGrader` | Exists |
| Precision@K, Recall@K, MRR, Hit Rate | `retrieval_eval.py` + RAGAS context metrics | Exists |
| Context Entity Recall | `RagasGrader` (context_recall) | Exists |
| Answer Similarity / Correctness | `RagasGrader` | Exists |
| Retrieval Lift | `ClosedBookBaseline` | Exists (standalone) |
| Failure Clustering | `FailureClusterer` | Exists |
| OTel Tracing | `PipelineTracer` + Phoenix | Exists |
| **Answer Completeness** | **`CompletenessJudge`** | **New** |
| **EPA Empathy Scores + Actionability** | **`EPAJudge`** | **New** |
| **Escalation Appropriateness** | **`EscalationJudge`** | **New** |
| **Knowledge Override Detection** | **`KnowledgeOverrideJudge`** | **New** |
| **Claim-Level Grounding** | **`GroundingJudge`** | **New** |
| **Conciseness** | **`ConcisenessGrader`** | **New** |
| **Structured HITL Tags** | **`HumanGrader`** (extended) | **Updated** |
| Component Metrics (chunking, embedding, index) | Pipeline infra — not graders | Out of scope |
| Response Latency, Token Usage | System metrics (OTel spans) | Out of scope |
| CES / Time Correlation | Analytics — not graders | Out of scope |

---

## Tasks

### [S] Task 1: Random Sampling CS Agent Review Queue (HITL)

Random post-sampling of conversations to be reviewed, validated, and annotated by a CS human agent. CS agents tag issues using a **structured taxonomy** (hallucination, source retrieval relevancy, tone, escalation failure, context missing) and provide corrected responses or information/steps required to solve the user's request.

**Grader:** `HumanGrader` (extended with structured tags, trace IDs, and confidence scores)

**Implementation notes:**
- Extend `HumanGrader.submit()` to write `trace_id`, `confidence_score`, and `tags: []` to `pending.jsonl` — fields sourced from `task.metadata`
- Define `REVIEW_TAGS` vocabulary: `hallucination | retrieval_relevancy | tone | escalation_failure | context_missing`
- `HumanGrader.grade()` surfaces tags in `GraderResult.details["tags"]` and trace_id in `details["trace_id"]`
- Backward-compatible: existing `completed.jsonl` files without new fields parse without error
- Annotations exported with trace IDs for downstream eval harness (v2) — trace_id links to OTel/Langfuse traces for drill-down

**Sampling strategy:**
- Random uniform sampling from conversation logs at configurable rate (start at 5%)
- Sampling logic is infrastructure (conversation log → `EvalTask` pipeline), not grader code
- Stratify by category to ensure coverage across intent types

**Dependencies:**
- Access to conversation logs and model outputs (with OTel trace IDs populated)
- CS team bandwidth + training on tagging guidelines and the `REVIEW_TAGS` taxonomy
- `HumanGrader` extension (this task implements it)

**Risks:**
- Inconsistent labeling quality across agents — mitigate with taxonomy training + `validate_tags()` dropping unknown tags
- Low participation if workflow is not embedded in existing tools — the JSONL file-based queue is MVP; v2 should integrate with Intercom/HubSpot tooling
- Representativeness of sampling — stratified sampling by category reduces this risk

**Acceptance criteria:**
- `HumanGrader.submit()` writes all new fields to `pending.jsonl`
- `HumanGrader.grade()` returns `GraderResult` with `details["tags"]` populated from completed reviews
- Unknown tags silently dropped with structlog warning
- Backward-compatible with pre-extension `completed.jsonl` format

---

### [S] Task 2: Edge Cases for Failure-Attribution (HITL)

Targeted sampling of conversations that match known risk signals — low-confidence retrieval scores (BedrockKB), thumbs-down signals, escalated conversations — routed to CS agents to annotate issues using the **same structured taxonomy** as Task 1 (hallucination, source retrieval relevancy, escalation failure, customer context info missing) and optionally provide corrected responses.

**Grader:** `HumanGrader` (same extension as Task 1) + signal-based filtering pipeline

**Implementation notes:**
- Reuses the extended `HumanGrader` from Task 1 — same `REVIEW_TAGS` taxonomy, same JSONL workflow
- The differentiator is the **sampling pipeline**, not the grader: filter conversations where `confidence_score < threshold` (configurable, start at 0.4 matching the CRAG gate), `escalated == true`, or `thumbs_down == true`
- `confidence_score` is populated from the CRAG gate's `max(relevance_scores)` — already computed in `src/librarian/config.py` (`confidence_threshold: float = 0.4`)
- Signal fields (`confidence_score`, `escalated`, `thumbs_down`) must be traced through OTel and populated in `EvalTask.metadata` before submission to `HumanGrader`

**Dependencies:**
- Confidence scores from BedrockKB / CrossEncoderReranker integrated and traced via OTel (partially exists — `confidence_threshold` is in config, reranker scores are computed)
- Escalation flag from `src/interfaces/api/triage.py` (`route="escalation"`) traced to conversation metadata
- User review flag (thumbs-down) integrated from HubSpot/Intercom — **not yet wired**
- CS team bandwidth + training on tagging guidelines (shared with Task 1)

**Risks:**
- Trigger threshold calibration — start with existing `confidence_threshold=0.4` and iterate based on volume
- Inconsistent labeling quality across agents (shared with Task 1)
- Low participation if workflow is not embedded in existing tools (shared with Task 1)
- Signal coverage gaps — thumbs-down from HubSpot is not yet integrated; escalation flag is available

**Acceptance criteria:**
- Signal-based filter correctly routes low-confidence, escalated, and flagged conversations to review queue
- Same `HumanGrader` workflow as Task 1 — no separate grader needed
- `confidence_score` populated in `EvalTask.metadata` from pipeline traces

---

### [M] Task 3: LLM-as-Judge Integration (Offline Evaluation)

Implement automated evaluation graders that score conversational outputs against the eval dataset using judge models. Scoring criteria from the RAPTOR tech doc:

| Criterion | Grader | Dimensions |
|---|---|---|
| Factual correctness | `ExactMatchGrader`, `MCQGrader` (existing) | binary accuracy |
| Grounding (answer supported by chunks?) | `GroundingJudge` (new) | `grounding_ratio`, `has_hallucination`, `claims_made`, `claims_grounded` |
| Escalation appropriateness | `EscalationJudge` (new) | `escalation_warranted`, `escalation_executed`, `appropriateness` |
| Knowledge override detection | `KnowledgeOverrideJudge` (new) | `context_used`, `parametric_override`, `override_score` |
| EPA communication quality | `EPAJudge` (new) | `empathy`, `professionalism`, `actionability`, `epa_composite` |
| Answer completeness | `CompletenessJudge` (new) | `sub_question_coverage`, `depth_adequacy`, `overall_completeness` |
| Conciseness | `ConcisenessGrader` (new) | `token_ratio`, `within_budget`, `padding_score` |
| Faithfulness | `DeepEvalGrader` (existing) | faithfulness metric |
| Hallucination rate | `DeepEvalGrader` (existing) | hallucination metric |
| Answer relevancy | `DeepEvalGrader`, `RagasGrader` (existing) | answer_relevancy metric |
| Context relevancy | `DeepEvalGrader` (existing) | contextual_relevancy metric |

**Reporting:** Results logged to Langfuse (current) via `EvalRunner` + `experiment.py`. DataDog dashboard integration is a follow-on — requires `ddtrace` dependency and metric export bridge from Langfuse/EvalReport → DataDog custom metrics.

**Implementation notes:**
- All new LLM judges subclass `LLMJudge` from `src/eval/graders/llm_judge.py` — inject `LLMClient`, return `GraderResult`
- All new graders are protocol-compliant (`Grader` from `src/eval/protocols.py`) and exported from `eval.graders`
- Integrate into `EvalRunner` by adding to the grader list — no runner code changes needed
- Iterate on judge prompts using CS-reviewed examples from Tasks 1 & 2 (cross-dependency)
- Calibrate judge scores against human labels from review queue (Task 1 provides the ground truth)

**Dependencies:**
- Stable eval dataset (Task 4)
- Access to judge model via `LLMClient` (existing `core.clients.llm` infrastructure)
- Langfuse logging infrastructure (existing)
- DataDog integration (not yet wired — `ddtrace` not in `pyproject.toml`)

**Risks:**
- Judge model inconsistency or bias — mitigate by calibrating against human labels from Tasks 1 & 2
- False confidence if not calibrated against human review — Tasks 1 & 2 are [S] priority specifically to provide calibration data before Task 3 goes live
- Over-reliance on automated scores without qualitative inspection — EPA and escalation judges especially need human calibration
- Cost — each LLM judge call costs ~$0.01–0.03 per sample; budget for the full grader suite on the golden dataset

**Acceptance criteria:**
- All 6 new graders implement `Grader` protocol, exported from `eval.graders`
- Each grader produces `GraderResult` with all specified dimensions populated
- At least 4 unit tests per grader (happy path, boundary, parse failure, empty response)
- Graders can be added to `EvalRunner` grader list without code changes to runner/pipeline

---

### [M] Task 4: Eval Set for Experimentation (Lean Golden Dataset)

Build a versioned golden dataset of ~50 query/answer/source triples covering key Danish market intent categories, sourced from explicit and human agent feedback. Expand incrementally as new golden traces and failure modes are discovered via HITL (Tasks 1 & 2) or LLM-as-judge (Task 3).

**Dataset composition:**
- **Core set:** High-impact intents from top ~5 Bookkeeping Hero request categories (source: thumbs-up signals)
- **Version-conflict subset:** ~10 QA pairs where a tax rule or product feature has changed, containing both replaced and active information — ground truth must only reflect the active version. Used to evaluate the `KnowledgeOverrideJudge` criterion in Task 3.
- **Escalation set:** ~5 QA pairs covering in-scope/out-of-scope boundary cases — used to calibrate `EscalationJudge`
- **Multi-part set:** ~5 QA pairs with compound questions — used to calibrate `CompletenessJudge`

**Format:** `EvalTask` model from `src/eval/models.py` with fields:
- `id`, `query`, `expected_answer`, `context` (retrieved chunks), `category`, `difficulty`, `tags`, `validation_level` (gold for human-verified, silver for auto-extracted)
- `metadata.contexts` (list of chunk strings), `metadata.expected_doc_url` (for regression), `metadata.response` (model output)
- Version-conflict pairs should use `tags: ["version_conflict"]` and include both replaced and active info in context

**Compatibility:** `EvalTask` is already compatible with both `EvalRunner` and the `load_golden_from_jsonl()` loader. DeepEval/RAGAS compatibility is handled by `DeepEvalGrader` and `RagasGrader` which read from `EvalTask` fields.

**Dependencies:**
- Access to Intercom/bookkeeper conversation data (incl. export + cleaning)
- Human labeling for gold-tier validation (CS team from Tasks 1 & 2)

**Risks:**
- Data privacy / anonymization compliance — all PII must be stripped before inclusion
- Labeling quality and consistency — use `REVIEW_TAGS` taxonomy from Task 1 for standardization
- Over-specifying "correct answers" too early — start with high-confidence examples, expand via HITL
- Dataset not representative of real traffic distribution — stratify by category using production intent distribution

**EDA / Scoping Notes:**
- Start with high-impact intents for greater coverage (top ~5 bookkeeping hero request categories)
- Version-conflict subset is deliberately small at MVP — the goal is to establish the pattern and calibrate the `KnowledgeOverrideJudge` criterion, not exhaustive coverage. Promote to a standalone eval initiative in v2 once conflict patterns are better understood.
- Escalation and multi-part subsets are new additions to ensure `EscalationJudge` and `CompletenessJudge` have calibration data from day one.

**Acceptance criteria:**
- ~50 `EvalTask` entries in versioned JSONL, loadable via `load_golden_from_jsonl()`
- Core set covers top 5 intent categories with at least 5 examples each
- Version-conflict subset has ~10 pairs with `tags: ["version_conflict"]`
- All entries have `validation_level` assigned (gold or silver)
- Dataset passes `ExactMatchGrader` and `MCQGrader` spot checks on ground truth

---

### [M] Task 5: Evaluation: Context & Memory Fidelity Detection

Evaluate whether the model correctly utilizes the provided updated context/memory for answer generation. This focuses on detecting "knowledge overrides" where the model ignores new and relevant memory in favor of old or parametric information.

**Detection methods:**

| Method | Grader | How It Works |
|---|---|---|
| HITL feedback | `HumanGrader` (extended, Tasks 1 & 2) | CS agents tag `context_missing` or identify patterns where system ignored latest context |
| Version-Conflict Eval Set | `KnowledgeOverrideJudge` (Task 3) | QA pairs contain both replaced and active info; ground truth reflects only active version; judge scores `parametric_override` dimension |
| Retrieval Lift | `ClosedBookBaseline` (existing) | Compare RAG score vs closed-book score; low lift suggests context was ignored |
| Faithfulness cross-check | `DeepEvalGrader` + `GroundingJudge` | Low faithfulness + high `parametric_override` = strong override signal |

**Deliverable:** Detection and reasoning for QA pairs, integrated into reporting:
- Langfuse (current): `KnowledgeOverrideJudge` scores logged via `EvalRunner` → `experiment.py` → Langfuse traces
- DataDog (target): Custom metrics for `parametric_override` rate, `context_used` distribution — requires DataDog integration (not yet wired)

**Attribution challenge — retrieval vs generation failure:**
- If `parametric_override` is high but retrieved context actually contains the correct info → generation failure (model ignored context)
- If `parametric_override` is high and retrieved context does NOT contain the correct info → retrieval failure (retriever didn't fetch the right docs)
- `GroundingJudge.claims_grounded` + `KnowledgeOverrideJudge.context_used` together distinguish these cases
- The existing `FailureClusterer` (11-type taxonomy) can group these patterns for systemic analysis

**Dependencies:**
- Stable eval dataset with version-conflict subset (Task 4)
- `KnowledgeOverrideJudge` grader (Task 3)
- `ClosedBookBaseline` (exists but standalone — gated by `CONFIRM_EXPENSIVE_OPS`)
- Langfuse logging infrastructure (existing)
- DataDog integration (not yet wired)

**Risks:**
- Judge model inconsistency or bias — calibrate `KnowledgeOverrideJudge` against human labels from Tasks 1 & 2
- False confidence if not calibrated against human review — the `parametric_override` threshold (0.2) needs tuning on real data
- Retrieval noise: difficulty in distinguishing whether the error was due to the LLM ignoring new info vs the retriever failing to fetch new info — addressed by combining `GroundingJudge` + `KnowledgeOverrideJudge` signals
- `ClosedBookBaseline` cost gate (`CONFIRM_EXPENSIVE_OPS`) must be consciously flipped for eval runs

**EDA / Scoping Notes:**
- Conflict pattern analysis: start with the ~10 version-conflict pairs from Task 4, expand as patterns emerge
- Track `parametric_override` distribution across the full golden set to establish baseline rates

**Acceptance criteria:**
- `KnowledgeOverrideJudge` scores all version-conflict eval pairs with `parametric_override` and `context_used` dimensions
- Combined signal (`GroundingJudge` + `KnowledgeOverrideJudge`) correctly distinguishes retrieval failure from generation failure on at least 3 manually verified examples
- Results logged to Langfuse via standard `EvalRunner` pipeline
- Lightweight reporting of override rates integrated into experiment comparison output
