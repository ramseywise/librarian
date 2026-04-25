---
title: RAG Evaluation
tags: [rag, eval, concept]
summary: Three-tier evaluation architecture for RAG pipelines — golden datasets, LLM-as-judge, failure clustering, ragas vs deepeval, and retrieval lift measurement.
updated: 2026-04-24
sources:
  - raw/playground-docs/librarian-stack-audit.md
  - raw/playground-docs/rag-agent-template-research.md
  - raw/claude-docs/playground/docs/archived/mvp-feedback-eval/plan.md
  - raw/claude-docs/listen-wiseer/docs/research/eval-harness.md
  - raw/linear/2026-04-24-evaluation-and-improvement.md
---

# RAG Evaluation

## Three Test Tiers

| Tier | Cost | What it tests |
|---|---|---|
| **Unit tests** | Free — mocks | Each component in isolation: schemas, chunker, retriever, reranker, generator, graph wiring |
| **Regression tests** | Free — InMemory + MockEmbedder | `hit_rate@5 >= 0.6`, `MRR >= 0.4` against golden dataset. Ratchet floors — update (never lower) when quality improves |
| **Capability tests** | Cheap (mocks) to expensive (LLM) | End-to-end routing correctness, CRAG termination, `AnswerJudge` grading (cost-gated) |

## Golden Dataset

Hand-curated `GoldenSample` objects with:
- `query` + `expected doc URL` + `relevant chunk IDs`
- `validation_level`: gold / silver / bronze / synthetic
- `difficulty`: easy / medium / hard

Supports stratified evaluation — track metrics by difficulty tier to see where the system breaks.

## Key Metrics

| Metric | What it measures | Floor |
|---|---|---|
| `hit_rate@k` | Fraction of queries where the expected doc is in top-k results | `>= 0.6` |
| `MRR` | Mean Reciprocal Rank of expected doc position | `>= 0.4` |
| `faithfulness` | Is the answer grounded in the retrieved context? | LLM judge |
| `answer_relevancy` | Does the answer address the query? | LLM judge |
| `retrieval_lift` | `rag_score - closed_book_score` | > 0 (RAG must beat no-context) |

**Regression floors only go up, never down.** The comment in code says "update these (never lower them) when quality improves."

## LLM-as-Judge (`AnswerJudge`)

Scores `(question, context, answer)` on 3 dimensions: faithfulness, relevance, completeness. Returns `JudgeResult` with `is_correct`, `score` (0–1), and reasoning.

**Cost-gated:** `CONFIRM_EXPENSIVE_OPS` must be explicitly set to `True`. Default is `False`, enforced never to be committed as `True`. Estimated ~$0.01–0.03 per sample with Haiku.

## Retrieval Lift (Closed-Book Baseline)

Run the same questions through the same model with *no retrieval context* — pure parametric knowledge. Compare against RAG answers:

```
lift = rag_score - closed_book_score
```

If RAG scores aren't meaningfully higher than closed-book, retrieval isn't adding value. This is the clean experimental control.

## Failure Clustering

`FailureClusterer` classifies failures into 11 types:

| Type | Meaning |
|---|---|
| `retrieval_failure` | Wrong chunks returned |
| `ranking_failure` | Right chunks, wrong order |
| `generation_failure` | Retrieved chunks not used |
| `grounding_failure` | Answer not supported by retrieved context |
| `coverage_gap` | Corpus doesn't contain the answer |
| `zero_retrieval` | No chunks returned |
| `low_confidence` | Confidence score below threshold |
| `context_noise` | Too many irrelevant chunks polluting context |

Groups by type, finds common query patterns (length, frequent terms), suggests fixes via `_suggest_fix()`.

## RAPTOR Evaluation Framework

Three-stage process for systematic evaluation:

1. **Detect** — automated metrics + human review (HITL sampling)
2. **Attribute** — tracing + failure clustering to root-cause errors
3. **Control** — guardrails + confidence gates to prevent recurrence

This maps directly onto the eval stack: golden datasets detect regressions, failure clusterer attributes causes, CRAG gate controls quality.

---

## HITL Human Review Sampling

Two complementary sampling strategies for the human review queue:

**Random sampling (5%):** Uniform random sampling of all conversations, stratified by intent category to ensure coverage. CS agents tag using a structured `REVIEW_TAGS` taxonomy.

**Signal-based sampling:** Filter for high-risk conversations:
- `confidence_score < 0.4` (matching CRAG gate threshold)
- `escalated == true`
- `thumbs_down == true` (from HubSpot/Intercom — requires wiring)

```python
REVIEW_TAGS = {"hallucination", "retrieval_relevancy", "tone", "escalation_failure", "context_missing"}
```

Tags are written to `pending.jsonl` with `trace_id`, `confidence_score`, and `tags[]` for downstream eval harness linkage. `trace_id` links to OTel/LangFuse traces for drill-down.

---

## Extended LLM Judges

Beyond the existing `AnswerJudge`, the MVP eval build adds 6 new judges. All subclass `LLMJudge`, inject `LLMClient`, and return `GraderResult`:

| Judge | Key dimensions |
|---|---|
| `GroundingJudge` | `grounding_ratio`, `has_hallucination`, `claims_made`, `claims_grounded` |
| `EscalationJudge` | `escalation_warranted`, `escalation_executed`, `appropriateness` |
| `KnowledgeOverrideJudge` | `context_used`, `parametric_override`, `override_score` |
| `EPAJudge` | `empathy`, `professionalism`, `actionability`, `epa_composite` |
| `CompletenessJudge` | `sub_question_coverage`, `depth_adequacy`, `overall_completeness` |
| `ConcisenessGrader` | `token_ratio`, `within_budget`, `padding_score` |

All judges are plug-in compatible with `EvalRunner` — add to the grader list, no runner code changes needed.

**Cost reminder:** each LLM judge call ~$0.01–0.03 per sample. Budget for the full grader suite on the golden dataset before enabling.

---

## Knowledge Override Detection

Detects when the model ignores retrieved context in favor of parametric (training) knowledge.

**Combined signal approach:**
- **High `parametric_override` + context contains correct info** → generation failure (model ignored context)
- **High `parametric_override` + context doesn't contain correct info** → retrieval failure (retriever failed)

```
GroundingJudge.claims_grounded + KnowledgeOverrideJudge.context_used → distinguish retrieval vs generation failure
```

Feed into `FailureClusterer` for systemic pattern analysis across the golden dataset.

**Version-conflict eval dataset:** ~10 QA pairs where both an outdated and a current version of a fact exist in the corpus. Ground truth reflects only the active version. Calibrates `KnowledgeOverrideJudge.parametric_override` threshold (start at 0.2, tune on real data).

---

## ragas vs deepeval

| Tool | Best for | Integration |
|---|---|---|
| **ragas** | Corpus-level quality benchmarks (run manually after corpus changes) | Native LangFuse integration via `ragas.integrations.langfuse` |
| **deepeval** | CI regression testing (runs in pytest) | `DeepEvalCallbackHandler` for LangFuse |

**Decision: use both.** ragas for experiments comparing retrieval strategies; deepeval for CI regression gates.

## Observability Integration

`LangFuse Score Push` (`_log_langfuse_scores()`): opt-in, logs `hit_rate` and `MRR` as LangFuse scores attached to a trace ID. No-op if unconfigured.

`EvalRunConfig` snapshots: `prompt_version`, `model_id`, `corpus_version`, `dataset_label`, `top_k` — logged alongside metrics for reproducibility.

## Agentic Evaluation (beyond RAG quality)

For copilot/action agents, additional metrics:

- **Task completion rate** — did the agent accomplish the goal? Binary success per test case.
- **Trajectory evaluation** — step precision/recall on expected tool call sequence.
- **Tool selection precision** — fraction of actual calls that were expected.
- **Adversarial tests** — prompt injection via retrieval, tool call manipulation, PII exfiltration, scope violation.

**Latency budgets per tier:**

| Query tier | Target P50 | Target P95 |
|---|---|---|
| Simple (no retrieval) | 300ms | 800ms |
| Q&A (single retrieve) | 800ms | 2s |
| CRAG retry | 1.5s | 4s |
| Action (plan + execute) | 2s | 6s |

## Agent Eval Taxonomy (Anthropic)

For LangGraph agents specifically, Anthropic defines three eval tiers — distinct from the RAG quality tiers above:

| Tier | What it tests | Cost | When to run |
|---|---|---|---|
| **Tier 1 — Unit** | Individual components: tool selection accuracy, intent classification, routing, parameter extraction | Free — deterministic, no LLM calls | Every CI run |
| **Tier 2 — Trajectory** | Sequence of agent decisions — which nodes were visited, which tools called, in what order | Low (mock tools) or medium (LLM-graded) | Pre-merge gate |
| **Tier 3 — End-to-end** | Final output quality from user's perspective — LLM-as-judge for faithfulness, relevance, completeness | Expensive — LLM calls per sample | Cost-gated, not CI |

**Principle:** Tier 1 catches ~70% of regressions cheaply. Add Tier 2 for routing logic. Use Tier 3 sparingly for quality gates.

**Golden dataset schema for agent evals:**

```python
class AgentGoldenSample(BaseModel):
    sample_id: str
    query: str
    expected_intent: str
    expected_confidence_min: float
    expected_tools: list[str]       # tool names the query should trigger
    expected_entities: dict[str, list[str]]
    expected_route: str             # "rewrite_query" | "clarify_or_proceed"
    difficulty: str                 # easy | medium | hard
    eval_tier: int                  # 1=unit, 2=trajectory, 3=e2e
```

Coverage target: 8-10 samples per intent for Tier 1, 5-10 trajectory cases, 5-10 edge cases. 40-60 total.

**RAGAS + DeepEval split:**
- **RAGAS** — RAG-specific quality: faithfulness, answer_relevancy, context_precision, context_recall. Use for `get_artist_context` tool quality.
- **DeepEval** — Agent-specific quality: `ToolCorrectnessMetric`, `GEval` (custom rubric), `AgentTaskCompletionMetric`. RAGAS doesn't have tool-use metrics.
- Both log scores to LangFuse traces via their respective integrations.

**DuckDB import chain gotcha (listen-wiseer):** Tier 1 evals must avoid importing `agent.tools` directly — it imports `RecommendationEngine` which imports DuckDB. Use the replication pattern (copy node logic inline) for Tier 1; use the mock pattern (patch `agent.tools._engine`) for Tier 2/3.

**Make targets by tier:**
```bash
make eval-unit        # Tier 1 — deterministic, CI-safe
make eval-trajectory  # Tier 2 — LangFuse-traced, cost-gated
make eval-e2e         # Tier 3 — RAGAS + DeepEval, CONFIRM_EXPENSIVE_OPS required
```

## Real-Data Baseline Methodology

Before launching a new system, establish a performance baseline using the **existing system's conversation data** — not synthetic golden sets. This gives a concrete "beat this" target.

Pattern from [[Evaluation & Improvement Project (VIR)]]:
- Export historical conversations from the prior system (BookKeeping Hero in this case)
- Run EDA to understand conversation structure, quality distribution, and failure modes
- Extract explicit feedback signals (thumbs up/down) as gold labels — these are real user judgements, not annotator opinions
- Document baseline metrics before the new system launches
- After launch, compare new system against this baseline on the same question types

**Why this matters:** Synthetic eval sets measure what you chose to measure. Real-data baselines measure what the system actually gets asked in production.

## LLM-as-Judge Calibration

LLM judge scores should not be trusted at scale until calibrated against human labels. The calibration loop:

1. Annotate a batch of conversations with human CS agents
2. Run LLM judges on the same batch
3. Compare — where does the judge agree/disagree with humans?
4. Adjust judge prompts or scoring thresholds until agreement is sufficient
5. Only then use LLM judges to scale quality assessment

This is especially important for edge cases — judge prompts optimized on average-case behavior may not generalize to failure modes. See [[HITL Annotation Pipeline]] for the full annotation workflow.

---

## See Also
- [[RAG Retrieval Strategies]]
- [[RAG Reranking]]
- [[LangGraph CRAG Pipeline]]
- [[Librarian RAG Architecture]]
- [[Listen-Wiseer Project]]
- [[HITL Annotation Pipeline]]
- [[Evaluation & Improvement Project (VIR)]]
