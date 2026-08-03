---
title: project-g Eval Architecture
tags: [eval, rag, concept]
summary: Routing vs domain eval distinction (Strand A/E/F), grader interface contract, three-tier eval coverage, calibration methodology for the project-g HC agent eval pipeline, and ADK vs LangGraph parallel evaluation approach.
updated: 2026-07-14
sources:
  - raw/claude-docs/playground/docs/evals/eval-architecture.md
  - raw/claude-docs/playground/docs/evals/grader_interface.md
  - raw/claude-docs/playground/docs/evals/grader_methodology.md
  - raw/notion/2026-06-26-va-hca-retrieval-executive-summary.md
  - raw/claude-docs/project-g/docs/evals/eval-architecture.md
  - raw/claude-docs/project-g/docs/evals/eval-harness-patterns.md
  - raw/claude-docs/project-g/docs/evals/grader_interface.md
  - raw/claude-docs/project-g/docs/evals/grader_methodology.md
  - raw/claude-docs/project-g/docs/evals/llm-calibration-insights.md
  - raw/claude-docs/project-g/docs/frameworks/langgraph.md
  - raw/claude-docs/project-g/docs/rag/retrieval-improvements.md
  - raw/claude-docs/project-g/skills/eval-creation/eval-report/SKILL.md
---

# project-g Eval Architecture

## Routing vs Domain Eval — The Key Distinction

**The most important architectural decision:** routing eval and domain eval are different problems requiring different graders.

| Eval type | What it measures | Grader type | Dataset |
|---|---|---|---|
| **Routing (Strand A)** | Does the agent retrieve the right documents? | URL matching, MRR, NDCG | Intercom URL-grounded (754 rows) |
| **Domain (Strand E)** | Does the answer correctly address the user's question? | LLM judge | BKH liked conversations (239 rows) |
| **Friction (Strand F)** | Does the agent escalate appropriately? | LLM judge | OOS + escalation scenarios |

**Why they must be separate:** An agent can retrieve perfect documents and produce a bad answer (routing passes, domain fails), or produce a fluent answer from wrong sources (routing fails, domain passes). Mixing them hides real failure modes.

## Grader Interface Contract

All graders implement `BaseGrader`:

```python
class BaseGrader:
    grader_type: str          # unique identifier used in eval JSONL output
    tier: str                 # "heuristic" | "fast" | "voted" | "calibrated"

    def grade(self, task: EvalTask) -> GraderOutput:
        ...

class GraderOutput(BaseModel):
    grader_type: str
    score: float              # 0.0–1.0
    is_correct: bool          # score >= tier threshold
    reasoning: str            # required for LLM judges
    metadata: dict            # grader-specific extras
```

Full contract in `evals/graders/README.md`. Registry in `evals/graders/registry.py`.

## Three Eval Tiers

### Tier 1 — Heuristic (free, no LLM)
- Citation hallucination: does response cite URLs not in retrieved set?
- Missing citation: does response make factual claims with no citation?
- Citation recall: fraction of retrieved URLs actually cited
- Schema validation: does response conform to `AssistantResponse` schema?
- **When to use:** every eval run, CI regression gate

### Tier 2 — Fast LLM judge (~$0.002/response with Haiku)
- Routing accuracy: did agent retrieve relevant passages?
- Friction signal: is escalation appropriate to context?
- **When to use:** post-change validation, `--limit 20` first pass

### Tier 3 — Voted LLM judge (majority-vote, ~$0.01/response)
- Response quality: is the answer correct and complete?
- Grounding accuracy: are factual claims supported by retrieved context?
- **When to use:** production quality gate, `--limit 500` full runs

## EvalTask Schema

```python
class EvalTask(BaseModel):
    task_id: str
    query: str
    response: str                    # agent's answer
    sources: list[Source]            # {url, title} from AssistantResponse
    retrieved_passages: list[str]    # raw passage text (required for grounding)
    metadata: dict                   # type (in_scope/out_of_scope), language, etc.
    contact_support: bool
    PROMPT_VERSION: str              # required for version tracking
```

**Key invariant:** `retrieved_passages` must be passage text, not URLs. See [[LLM Grader Calibration Insights]].

## OutputStructureGrader

Validates that agent output conforms to the `AssistantResponse` schema:
- `message` present and non-empty
- `suggestions` is a list of 2–4 strings
- `sources` entries have `{url, title}` format
- `contact_support` is a boolean

Runs on every eval task as a free heuristic check.

## Ablation Methodology (VIR-179)

Multi-agent ablation compares `hc_adk`, `hc_lg`, `hc_rag` across 14 configurations:

| Config | Feature flags | Primary metric |
|---|---|---|
| rag_v2+ce | Default + cross-encoder | MRR (currently 0.3847, best) |
| adk_default | THINKING_BUDGET=0 | MRR baseline |
| adk_thinking | THINKING_BUDGET=1024 | Quality uplift vs latency |
| lg_crag | CRAG_ENABLED=true | Retrieval recall |
| lg_multi_query | MULTI_QUERY=true | +recall at cost |

**Decision gate:** promote config only if MRR improvement >5% or quality uplift >0.05 points at same latency.

### Ablation Results (44-task run, completed)

Top configs by MRR:

| Config | MRR | Hit@1 | Hit@3 |
|---|---|---|---|
| `adk_flash_thinking1024` (gemini-3-flash-preview + thinking) | **0.656** | 0.52 | 0.73 |
| `lg_multi_query` | 0.594 | — | — |
| `adk_thinking1024` | 0.583 | — | — |
| `adk_flash` | 0.563 | — | — |
| `lg_crag` | 0.547 | — | — |
| `adk_baseline` | 0.418 | — | — |

Feature impact (ΔMRR vs baseline): thinking budget (hc_adk) **+0.165**, flash model swap **+0.145**, multi-query **+0.076**, CRAG alone **+0.005** (at +3.4s latency — marginal), LLM planner **−0.031** (regex router wins for this vocabulary), CRAG+thinking combined **−0.063** (interaction effect: thinking changes citation style, breaking CRAG's grading alignment).

**Research path that produced this (from `retrieval-improvements.md`):** the ablation ran the priority list in order — (1) gemini-3-flash-preview model upgrade — biggest single lever, confirmed; (2) multi-query retrieval (RRF-merged 2–3 reformulated queries) — confirmed second-best lever; (3) HyDE — planned for `hc_rag` only (Bedrock HYBRID search dilutes the benefit since BM25 is keyword-based; see [[Agentic RAG — Advanced Patterns]] for the general HyDE mechanism); (4) routing all three agents' retrieval through `hc_rag`'s local DuckDB backend — TODO, would remove Bedrock cost and unlock HyDE; (5) DPO preference fine-tuning — BLOCKED on 200+ annotated preference pairs (32 annotated queries, 0 golden responses stored as of the last check).

## GT Pipeline (VIR-212)

Ground truth expansion pipeline:
1. Extract liked conversations from Intercom (BKH explicit signals)
2. Intent gap analysis — which intents are underrepresented?
3. Feature engineering: HC citation flag, intent clustering, escalation label
4. Dataset stats + drift report
5. Dual-corpus retrieval grid (Intercom + BKH cross-referenced)

**Root causes fixed in v1.0:**
- RAGAS silently degrading on empty passages → now validated pre-grading
- URL domain mismatch inflating grounding failures → normalization merged
- Article text available but unused in grounding → passage enrichment added

## VA vs HCA Production Retrieval Benchmarking

The Strand A (routing eval) framework has been applied to a full production comparison. Full results in [[VA vs HCA Retrieval Evaluation]].

**Key figures (n=754 Danish Intercom questions):**

| System | MRR | Hit@5 |
|---|---|---|
| VA (production) | 0.286 | 0.350 |
| HCA (production) | 0.248 | 0.301 |
| Local-ADK (research) | 0.375 | 0.405 |

**LLM-as-judge quality scores (VA vs HCA):**
- Grounding: 0.776 vs 0.633 (+0.143 — the largest signal gap)
- Answer Relevancy: 0.891 vs 0.825
- Faithfulness: 0.592 vs 0.511 (both low — model extrapolation beyond sources is a cross-system issue)

### Two-Lever Framework

The central finding: improvement levers are independent and should be sequenced separately.

**Lever 1 — Corpus quality (dominant lever):** 47% of all 935 questions are missed by every system — corpus ceiling, not retrieval architecture. Scoping index to help articles + re-ingesting 202 missing articles raises Hit@5 ceiling from ~40% to ~59% with zero model change. **Go here first.**

**Lever 2 — Retrieval strategy:** where VA beats HCA. VA pools 2–3 reformulated queries (~13 sources), HCA does narrow retry returning ~4. VA wins via broad pooling → reranking → top-5 filter.

### Production Benchmarking Decision Gate

For ablation (14 configs in VIR-179): the MRR threshold of >5% improvement already filters corpus-quality improvements from agent-level improvements. Apply the two-lever framework when interpreting config comparisons — a config that improves MRR on the URL-cited subset may not improve real-traffic coverage if the corpus ceiling is the binding constraint.

## Eval Harness — Four Suite Types

Every agent eval harness should cover these four suites:

| Suite | What it tests | Failure signal |
|---|---|---|
| **Routing accuracy** | Does the agent route to the right domain/sub-agent? | Wrong tool called first |
| **Response quality** | Is the final answer correct and complete? | LLM judge score < threshold |
| **Behavioral (rubric)** | Does the agent follow rules (no PII, stays in domain)? | Rubric criterion violated |
| **Error handling** | Does the agent handle malformed input / API errors gracefully? | Crashes or produces unsafe output |

project-g currently implements: response quality (LLM graders), behavioral/rubric (heuristic metrics).

## Two-Phase Run Pattern (run/assert)

**Phase 1 — Run** (expensive, LLM calls):
```bash
uv run python -m evals.pipelines.run quality --dataset <responses.jsonl> --tier calibrated --limit 20
```

**Phase 2 — Assert** (cheap, reads cached JSON):
```bash
uv run pytest tests/unit_tests/test_evals/ -q
```

The split keeps CI fast and LLM costs offline.

## ADK vs LangGraph — Parallel Evaluation Principle

`hc_adk` and `hc_lg` are deliberately **feature-equal** — same schema, same safeguard layers, same eval dataset. Neither is primary until ablation completes.

**Why:** Committing to a framework before measuring quality differences would make the comparative method circular. Framework selection is an output of ablation, not an input.

**Implication for graders:** Avoid graders that assume a specific execution model (e.g. LangGraph node sequences, ADK tool call counts) until a winner is selected. Use framework-neutral metrics (MRR, grounding ratio, composite quality) for the primary comparison.

**ADK native eval gap:** project-g has no `tool_trajectory_avg_score` equivalent. ADK's `AgentEvaluator` provides this for routing correctness (did the right sub-agent get called?). Not used in primary project-g evals because:
1. Our eval set has expected URLs, not tool-level labels — annotating expected tool sequences is new work
2. ROUGE-L (used by `final_response_match_v2`) is a poor fit for conversational helpdesk answers
3. Framework neutrality: forcing ADK-specific eval before the hc_adk vs hc_lg winner is decided creates asymmetric grader coverage

## HITL: Annotation vs Runtime Interrupts

These are **different concerns** — do not conflate:

| | `evals/graders/hitl.py` | `LangGraph GraphInterrupt` |
|---|---|---|
| **What it is** | Post-hoc annotation for eval datasets | Runtime approval gate |
| **Flow** | File-based async queue → human annotates → regression fixture | Graph suspends, waits for human input, resumes via `Command` |
| **When** | Offline / batch | Live request |
| **Framework** | Framework-agnostic | LangGraph-specific |

## See Also
- [[Eval-Driven Development (EDD)]] <!-- auto-linked -->
- [[VA vs HCA Retrieval Evaluation]]
- [[VA Eval Harness]]
- [[LLM Grader Calibration Insights]]
- [[RAG Evaluation]]
- [[Evaluation & Improvement Project (VIR)]]
- [[Input Guardrails Pipeline]]
- [[RAG Eval Gate Contract]]
- [[Grounding Claim Methodology]]
- [[HITL and Interrupt Patterns]]
- [[Agentic RAG — Advanced Patterns]]
- [[Direct Preference Optimization]]
- [[VA Bedrock KB Reference]]
- [[project-g Eval Framework]]
