# SA Ablation Study — Agent Quality & Feature Comparison

> **Date:** 2026-06-02  **Updated:** 2026-06-08
> **Prereq:** VIR-212 GT pipeline complete (GT expansion + RAG opt notebooks) ✅ before Phase 1
> **Goal:** Side-by-side quality + feature comparison across hc_adk / hc_lg / hc_rag on verified
> GT data; agent-level config ablations (not retrieval-level — those live in VIR-212).
> **Linear ticket:** vir-179

---

## Status snapshot (as of 2026-06-08)

| Item | Status |
|---|---|
| BKH baseline graded | ✅ `evals/data/gt/bkh_baseline_graded.json` (413 rows, 7 LLM graders) |
| VA quality baseline | ✅ 543 rows in archive (non-voted graders) |
| GT dataset validated | ✅ `evals/data/gt/regression.jsonl` (412 rows); `capability.jsonl` (106); `edge_cases.jsonl` (34) |
| GT expansion (`discovery_hc.jsonl`) | ⏳ VIR-212 Phase 2 — prereq for Phase 1 here |
| Best RAG config (from VIR-212 Phase 4) | ⏳ VIR-212 Phase 4 determines this — locks hc_rag production config |
| GT agent calls (hc_adk/hc_lg/hc_rag) | ⏳ `make gt-call-sa` — after VIR-212 lands |
| GT quality grading | ⏳ `make gt-grade-sa` — after agent calls |
| Feature comparison matrix | ⏳ Phase 4 below |
| VA staging auth (ADC) | ❌ Blocked — OOS grading deferred |

---

## Phase 1 — Agent calls + quality grading on GT regression set

**Prereq:** VIR-212 Phase 4 complete (hc_rag best config locked from Bedrock vs local sweep).

```bash
# Prereq: make sa-adk-bedrock-up sa-langgraph-bedrock-up sa-rag-up
make gt-call-sa      # calls all 3 agents against regression.jsonl (412 rows, --resume)
                     # outputs: data/datasets/support-agents/ablation/hc_{adk,lg,rag}_gt.json

make gt-grade-sa     # grades hc_adk_gt + hc_lg_gt + hc_rag_gt with standard quality graders
                     # answer_relevancy, completeness, escalation
```

**Agent default configs to lock in:**

| Agent | Key defaults | Port | Config source |
|---|---|---|---|
| hc_adk | `THINKING_BUDGET=0`, `GEMINI_MODEL=gemini-2.5-flash` | 8011 | locked |
| hc_lg | `CRAG_ENABLED=true`, `MULTI_QUERY=false`, `LLM_PLANNER=false` | 8012 | locked |
| hc_rag | best config from VIR-212 Phase 4 sweep | 8013 | from VIR-212 |

**Acceptance:** All 3 agents have quality scores on 412 GT rows saved in
`data/datasets/support-agents/quality/hc_{adk,lg,rag}_gt.json`.

---

## Phase 2 — Agent comparison on shared eval set

**Goal:** BKH vs VA vs hc_rag vs hc_lg vs hc_adk on the same GT task_ids.

### 2a — Align VA and BKH grader schemas

**GT regression set (412 rows) is the canonical comparison input.**
VA comparison is unblocked for retrieval/quality graders that don't require fresh VA staging
responses; OOS/routing eval still needs VA staging auth.

**Sequence: `gt-va-call` first → then `grade-va-baseline`.**

**Why RAGAS is confounded in current VA scores:**
`va_qa.jsonl` has `retrieved_passages=[]` for all 597 rows — VA (Bedrock) returns source
URLs only, not passage text. RAGAS graded against empty context → faithfulness 16% raw
(calibrated to 43%). BKH baseline has article-cache enrichment → RAGAS gets real text →
77%/50%. The -18pp/-7pp gap is largely context thinness, not genuine VA quality gap.
399/597 VA rows have article cache coverage and will score correctly once `enrich_passages`
runs during grading.

```makefile
grade-va-baseline:
	uv run python -m evals.pipelines.eval_quality \
		--dataset data/baseline/va_qa.jsonl \
		--graders source_match answer_relevancy_voted completeness_voted \
		          escalation_voted grounding_voted deepeval_answer_relevancy \
		          ragas_context_precision_voted ragas_faithfulness_voted \
		--profile bkh \
		--output evals/data/gt/va_baseline_graded.json \
		--resume
```

`--profile bkh` enables `enrich_passages` from the article cache. Expected outcome: RAGAS
gap shrinks from -18pp/-7pp toward 0; residual gap after enrichment is the true VA
faithfulness deficit worth reporting.

**Blocker:** VA staging auth (Google ADC broken in deployed agent).

### 2b — Routing eval (Strand A)

Seed `data/adk/eval_sets/routing_eval.jsonl` from VA staging `table_type` + `nav_buttons.route`
values. Run `AgentEvaluator` tool trajectory scoring against va_google_adk root agent.

**Prereq:** VA staging auth fix.

### 2c — Coverage decision alignment

For each agent, derive `coverage_decision` enum:
- `"answered"` — has URL, no escalation flag
- `"no_coverage"` — `insufficient_information=true`
- `"escalated"` — `contact_support=true`

Use as cross-agent breakdown axis in the combined report (VA `table_type` ↔ SA `coverage_decision`).

---

## Phase 3 — Agent-level config ablations

Agent-level knobs only. Retrieval-level experiments (reranker config, Bedrock KB ID swap)
live in VIR-212. Each ablation is a single config change against the regression.jsonl eval
set; compare quality grader delta vs Phase 1 baseline.

| ID | Change | Expected lift | Cost |
|---|---|---|---|
| R2 | Multi-query reformulation (hc_lg) | +recall on ambiguous queries | Medium |
| R3 | CRAG high-confidence threshold tuning (0.7→0.85) | -latency, marginal quality tradeoff | Low |
| R4 | Thinking budget 1024 (hc_adk) | +completeness on complex queries | High cost |
| R5 | LLM planner vs regex routing (hc_lg) | measure actual routing quality delta | Low |

**Convention:** each experiment writes results to `evals/data/gt/runs/<ts>/ablations/<exp_id>/`.
Compare via `make ablation-compare` which reads all `ablations/*/` and outputs ranked delta table.

---

## Phase 4 — Feature comparison matrix

Cross-agent capability comparison. Write findings back to `docs/frameworks/agent-feature-parity.md`
(don't answer inline and forget — that doc exists precisely for this).

| Feature | hc_adk | hc_lg | hc_rag | VA |
|---|---|---|---|---|
| Layer 1 — input guardrail | ✅ | ✅ | ✅ | ❌ |
| Layer 2 — routing confidence | — | ✅ | — | ✅ |
| Layer 3 — CRAG retrieval gate | ✅ | ✅ | — | — |
| Layer 4 — post-gen grounding | ✅ | ✅ | ✅ | ✅ |
| Layer 5 — escalation path | — | — | — | ✅ |
| Structured output (citations/claims) | ✅ | ⏳ | ❌ | — |
| Langfuse observability | ✅ | ✅ | ✅ | — |
| Multi-query reformulation | — | flag | — | — |
| Thinking budget (extended reasoning) | flag | — | — | — |

Run this phase after Phase 1 grading is done — use actual quality scores to annotate
which capability gaps explain the quality deltas.

---

## Phase 5 — Report scripts update

### 5a — Threshold boundary view

The threshold boundary chart (box plots by sentiment group, F1-optimal threshold lines)
from `04_edge_case_study.ipynb §6` needs wiring into the comparative report.

**What needs updating:**
- `_load_bkh_llm_pass_summary()` in `figures.py` now reads `evals/data/gt/bkh_baseline_graded.json`
- Suite HTML flags BKH voted vs VA non-voted schema mismatch until Phase 2a is done
- Add `grade-va-baseline` Makefile target once VA auth is fixed

### 5b — hc_rag output grounding (Tiers 1–3)

Requires structured output with `citations[]` + `claims[]` first. Defer until structured
output PR is merged.

---

## Phase 6 — va-agents TypeScript work (parallel, separate PR)

- Input guardrail layer: port `run_input_guard()` pattern to TS `va-agents`
- Grounding decomposition: `GroundingResult` typing + `guardrails/grounding/` structure
- Independent of the Python eval pipeline — no shared blockers

---

## OOS boundary eval

Deferred until VA staging auth is resolved:

```
VA staging auth fix
    → make gt-va-call (oos_boundary.jsonl as input)
    → make grade-oos-boundary
    → escalation F1 = combine BKH specificity + OOS sensitivity
```

Email-referral partition (`oos_domain="email_referral"`) — mine from friction JSONL
where BKH replied with support email, add ~15 labeled examples to `oos_boundary.jsonl`.

---

## Execution order

```
VIR-212 Phase 4   →  RAG opt + Bedrock comparison done, best hc_rag config locked
Phase 1           →  make gt-call-sa  (agents on 8011/8012/8013)
                      make gt-grade-sa
Phase 2a          →  grade-va-baseline  (once VA auth fixed)
Phase 3           →  R2–R5 agent-level ablations
Phase 4           →  feature comparison matrix → agent-feature-parity.md
Phase 5           →  report update after 2a done (BKH + VA + SA all in new schema)
Phase 6           →  TS guardrail PR  (parallel, anytime)
OOS               →  after VA staging auth fix
```

---

## Acceptance criteria

1. ⏳ All 3 agents have quality scores on 412 GT rows (`quality/hc_{adk,lg,rag}_gt.json`)
2. ⏳ Retrieval metrics (hit-rate, precision, recall) added to quality report alongside quality graders
3. ⏳ `alignment_analysis.ipynb` updated to use `regression.jsonl` (after Phase 1 ablation files exist)
4. ⏳ Feature comparison matrix in `docs/frameworks/agent-feature-parity.md` annotated with quality deltas
5. ⏳ Comparative report: quality + retrieval (from VIR-212) + feature matrix in one shareable artifact
