# VIR-179 — Support Agent Ablation Study
Ticket: VIR-179
Date: 2026-05-11 (ongoing)
Branch: vir-179-test-hc-support-agent-poc-ablation

Consolidated from: `ablation-decisions.md`, `ablation-hypotheses.md`, `support-agents-ablation.md`, `rag-experiment-tracking.md`

---

## Architecture Overview

The three agents represent three different bets on the same underlying problem:

| Agent | Bet | Retrieval model | Grounding |
|---|---|---|---|
| **hc_adk** | Simplest viable production path | Bedrock managed (reranking + Titan) | Tiers 1–4 post-gen |
| **hc_lg** | Explicit graph = observable + extensible | CRAG loop (LLM grading + rewrite) | Tiers 1–4 as graph node |
| **hc_rag** | Controlled ingestion beats managed KB | Local vector (DuckDB, pluggable reranker) | Input guardrails only |

**Architecture rationale:** Keep the 3-agent comparative approach as the primary eval story. Domain routing (modelling `va-agents`) is a separate product track. The comparison is the *eval/improvement story* — every change is measurable via MRR delta. Domain routing is the *product story*.

**Key architectural distinction for thinking:**
- `hc_adk`: `THINKING_BUDGET` applies to the whole Gemini agent — including query generation. Thinking directly improves retrieval.
- `hc_lg`: `THINKING_BUDGET` applies to the **answer node only** (`agent.py:168`). CRAG grading and MQ expansion use plain `ChatGoogleGenerativeAI` with no thinking. Thinking does NOT improve MRR — only answer quality.

---

## Config Matrix

All variants share the same eval dataset. "Local agents" run on ports 8011/8012 from `/Users/ramsey.wise/Workspace` via `uv run`.

| Config key | Agent | GEMINI_MODEL | THINKING_BUDGET | CRAG_ENABLED | Other flags | MRR | P@1 | NDCG@5 | Avg latency |
|---|---|---|---|---|---|---|---|---|---|
| `adk_baseline` | hc_adk | gemini-2.5-flash | 0 | — | — | 0.418 | 0.219 | 0.532 | 2.6s |
| `adk_thinking1024` | hc_adk | gemini-2.5-flash | 1024 | — | — | 0.583 | 0.531 | 0.615 | 7.3s |
| `lg_no_crag` | hc_lg | gemini-2.5-flash | 0 | false | — | 0.542 | 0.531 | 0.547 | 4.3s |
| `lg_crag` | hc_lg | gemini-2.5-flash | 0 | true | — | 0.547 | 0.531 | 0.551 | 7.7s |
| `lg_crag_thinking1024` | hc_lg | gemini-2.5-flash | 1024 | true | — | 0.484 | 0.469 | 0.489 | 7.4s |
| `lg_llm_planner` | hc_lg | gemini-2.5-flash | 0 | true | LLM_PLANNER=true | 0.516 | 0.500 | 0.520 | 8.3s |
| `va_staging` | Billy prod VA | gemini-3-flash-preview | LOW (≈1024) | n/a | Bedrock KB HYBRID | 0.500 | — | — | 9.3s |
| `adk_flash` | hc_adk | gemini-3-flash-preview | 0 | — | — | 0.5625 | — | — | — |
| `adk_flash_thinking1024` | hc_adk | gemini-3-flash-preview | 1024 | — | — | 0.6562 | — | — | — |
| `lg_flash` | hc_lg | gemini-3-flash-preview | 0 | true | — | 0.5781 | — | — | — |
| `lg_multi_query` | hc_lg | gemini-2.5-flash | 0 | true | MULTI_QUERY=true | 0.5938 | — | — | — |
| `adk_rag_backend` | hc_adk | gemini-2.5-flash | 0 | — | VA_RETRIEVAL_MODE=rag | TBD | — | — | — |
| `lg_rag_backend` | hc_lg | gemini-2.5-flash | 0 | true | VA_RETRIEVAL_BACKEND=rag | TBD | — | — | — |
| `hc_rag_ce_minilm_l12` | hc_lg+hc_rag | gemini-2.5-flash | 0 | false | VA_RETRIEVAL_BACKEND=rag RERANKER_BACKEND=cross_encoder RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-12-v2 | TBD | — | — | — |
| `hc_rag_colbert` | hc_lg+hc_rag | gemini-2.5-flash | 0 | false | VA_RETRIEVAL_BACKEND=rag RERANKER_BACKEND=colbert | TBD | — | — | — |
| `lg_rag_hyde` | hc_lg+hc_rag | gemini-2.5-flash | 0 | true | VA_RETRIEVAL_BACKEND=rag HYDE_ENABLED=true | TBD | — | — | — |

> **Full 570 results (existing runs)**

| Config | MRR | Hits | P@3 | R@3 | F1@3 |
|---|---|---|---|---|---|
| VA-agents (reference) | 0.3178 | 197/570 | 0.125 | 0.179 | 0.140 |
| adk | 0.2560 | 253/570 | 0.150 | 0.195 | 0.158 |
| lg | 0.2843 | 196/570 | 0.123 | 0.173 | 0.136 |
| lg+mq | 0.2764 | 192/570 | 0.121 | 0.171 | 0.135 |
| rag_v2 | 0.3659 | 328/570 | 0.210 | 0.230 | 0.205 |
| rag_v2+ce | **0.3847** | 325/570 | 0.212 | 0.248 | **0.212** |

**rag_v2+ce is currently the best agent, beating VA-agents on the unbiased sample.**

> Note: Core 179 is biased toward VA-agents. Full 570 is the honest comparison. Default now `--full`.

---

## Feature Flag Taxonomy

### THINKING_BUDGET (int, default 0)
- **What it does:** Passes a thinking budget to Gemini's extended thinking API.
- **Measured effect (hc_adk):** `adk_baseline` MRR=0.418 → `adk_thinking1024` MRR=0.583. **+0.165 MRR (+39%), +4.7s latency.** Largest single feature gain observed.
- **Measured effect (hc_lg):** `lg_crag` MRR=0.547 → `lg_crag_thinking1024` MRR=0.484. **-0.063 MRR (-12%).** Thinking changed citation formatting, confusing the CRAG grader.

### CRAG_ENABLED (bool, default false for hc_lg)
- **What it does:** Corrective RAG loop — grade retrieved passages, rewrite if bad, re-fetch.
- **Measured effect:** `lg_no_crag` MRR=0.542 → `lg_crag` MRR=0.547. **+0.005 MRR (near-zero), +3.4s latency.** Bedrock HYBRID already retrieves high-quality passages; correction loop rarely triggers.

### LLM_PLANNER (bool, default false)
- **What it does:** Replaces regex-based intent router with Gemini LLM classification.
- **Measured effect:** `lg_crag` MRR=0.547 → `lg_llm_planner` MRR=0.516. **-0.031 MRR (-6%), +0.6s latency.** Regex rules are tuned to the Danish support domain and outperform LLM here.

### MULTI_QUERY (bool, default false, hc_lg only)
- **What it does:** Generates 2–3 query reformulations, retrieves for each, merges results.
- **Decision:** MQ is not always better. MQ **hurt** on full 570 (adds noise on verify/edge_case). MQ **helped** on core 179 (better coverage on clean queries). MQ adds ~5s via sequential expansion LLM call before parallel Bedrock retrieval.

### CRAG vs MQ decision
- CRAG adds latency only on hard queries. MQ always adds latency.
- **CRAG is better value than MQ for cost/latency tradeoff.**

### HYDE_ENABLED (bool, requires VA_RETRIEVAL_BACKEND=rag)
- Bridges informal Danish ↔ formal documentation vocabulary. Only effective with hc_rag backend — Bedrock HYBRID's BM25 component ignores the embedding.

### RERANKER_BACKEND (hc_rag only)
- `passthrough` (default), `cross_encoder`, `colbert`, `pairwise`, `llm_listwise`
- Cross-encoder variants: MiniLM-L6 (fast), MiniLM-L12 (better), electra-base (best)

### VA_RETRIEVAL_MODE (str, default bedrock)
- `bedrock` — AWS Bedrock KB (HYBRID search). `rag` — hc_rag local DuckDB service.

---

## Reasoning Patterns

| Pattern | Mechanism | Agent | Flag |
|---|---|---|---|
| **CoT** | Internal reasoning tokens before output | hc_adk, hc_lg | `THINKING_BUDGET > 0` |
| **ReAct** | Reason→Act→Observe loop | hc_adk | Native ADK |
| **Multi-query** | N reformulations → parallel retrieve → merge | hc_lg | `MULTI_QUERY=true` |
| **CRAG** | Retrieve → grade → rewrite → re-fetch | hc_lg | `CRAG_ENABLED=true` |
| **HyDE** | Hypothetical Document Embeddings → embed → find similar | hc_lg | `HYDE_ENABLED=true` |
| **Routing confidence** | Low-confidence predictions fall back to `answerable` | hc_lg | `ROUTING_CONFIDENCE_THRESHOLD > 0` |
| **In-session memory** | Injects last N turns into prompts | hc_lg | `LG_MEMORY_TURNS > 0` |

---

## Hypotheses

### Section 1: Retrieval Quality

**H1 — CRAG grading vs passthrough** (`CRAG_ENABLED`)  
LLM-based passage grading improves source match rate by ≥5 pp on low-recall queries but adds no value when top score ≥ 0.7. Counter: Flash grade verdicts noisy on ambiguous Danish queries.  
**Condition:** CRAG-on MRR ≥ CRAG-off + 0.05 on `score < 0.6` subset.

**H2 — Score delta guard** (`_SCORE_DELTA_EPSILON`)  
~20–30% of retries return same low-score passages (delta ≤ 0.05). Injecting a stop saves 1–2s with no quality loss.  
**Condition:** Guard fires on ≥15% of retry queries; grounded answer rate on guard-fired queries ≥ baseline.

**H3 — Confidence gate** (`CRAG_HIGH_CONFIDENCE=0.7`)  
High-score retrievals (≥0.7) correct ~90% of the time; grading them wastes 300ms.  
**Condition:** Gated queries grounding violation rate ≤ non-gated + 2 pp; latency savings ≥ 200ms P50.

**H4 — CRAG rewrite vs MQ expansion**  
CRAG rewriting (informed by what was retrieved) outperforms MQ expansion (generic upfront) on queries that initially miss.  
**Condition:** CRAG-rewrite MRR ≥ MQ MRR on low-recall subset (initial top score < 0.5).

**H5 — HyDE** (`HYDE_ENABLED`, requires `VA_RETRIEVAL_BACKEND=rag`)  
Bridges informal DA ↔ formal documentation vocabulary.  
**Condition:** HyDE MRR ≥ baseline + 0.05 on informal-Danish subset, no degradation > 2 pp on formal queries.

### Section 2: Reranker Ablation (hc_rag)

**H6 — Cross-encoder vs passthrough:** +15 pp MRR where similarity score spread is wide.  
**Condition:** CE MRR ≥ passthrough + 0.08 on high-spread subset.

**H7 — LLM listwise vs cross-encoder:** LLM handles long multi-section passages better than CE (truncates at 512 tokens).  
**Condition:** Listwise MRR ≥ CE + 0.05 on long-passage subset AND cost ≤ 2× CE.

**H8 — Local embeddings (MiniLM) vs Bedrock Titan/Cohere:** Bedrock's managed embeddings outperform MiniLM for professional text.  
**Condition:** If hc_adk MRR ≥ hc_rag + 0.05 → embedding model is the bottleneck.

### Section 3: Routing and Planning

**H9 — LLM planner vs regex router:** Regex is good enough for 3-class problem; LLM adds latency without accuracy gain.  
**Condition:** LLM planner improves routing accuracy by ≥ 5 pp on edge-case subset AND latency ≤ 400ms.

**H10 — HITL escalation on low-confidence retrieval:** Queries where max passage score < 0.3 are genuinely unanswerable from KB.  
**Condition:** Queries escalated by HITL would have had grounding violation rate ≥ 30% if answered.

### Section 4: Post-generation Quality

**H11 — Post-answer evaluator:** LLM quality judge catches ~10% of answers that are technically grounded but incomplete.  
**Condition:** Refine rate ≥ 8% of answerable queries; refined answers score ≥ 0.1 higher.

**H12 — Grounding strict quote check:** Strict mode reduces hallucinated claims reaching users by ~5% with ≤ 2% false-positive rate on paraphrase-heavy answers.  
**Condition:** Strict hard-fail rate ≤ 5% of answered queries; ≥ 80% of hard-fails confirmed hallucinations.

### Section 5: Architecture Comparison

**H13 — hc_lg (CRAG) vs hc_adk (callback injection):** hc_lg's explicit graph routing produces more consistent retry behaviour than hc_adk's callback-injected stop.  
**Condition:** hc_lg retrieval_attempts variance ≤ hc_adk variance; grounding violation rate within 2 pp.

**H14 — hc_rag controlled ingestion vs Bedrock managed KB:** At default settings, hc_rag underperforms hc_adk by ≥ 5 pp MRR because Bedrock's Titan embeddings are better calibrated.  
**Condition to reject (interesting):** hc_rag MRR ≥ hc_adk MRR → controlled ingestion adds value at default settings.

---

## Ablation Status

| Config | Output file | Status | Phase |
|---|---|---|---|
| adk | `hc_adk_golden.json` | ✅ done | baseline |
| lg | `hc_lg_golden.json` | ✅ done | baseline |
| lg+mq | `lg_multi_query_golden.json` | ✅ done | baseline |
| rag_v2 | `hc_rag_v2_golden.json` | ✅ done | baseline |
| rag_v2+ce | `hc_rag_reranker_golden.json` | ✅ done | baseline |
| adk+think | `adk_thinking_golden.json` | 🔄 --adk-only | Phase 1 |
| adk+rag | `adk_rag_golden.json` | 🔄 --adk-only | Phase 3 |
| lg+rag | `lg_rag_golden.json` | 🔄 --adk-only | Phase 4 |
| lg+think | `lg_thinking_golden.json` | ⏳ --lg-only | Phase 2a |
| lg+mq+think | `lg_mq_thinking_golden.json` | ⏳ --lg-only | Phase 2b |

**After `--adk-only` run:** 8 of 10 configs complete. Only lg thinking phases remain.

---

## Pending Runs

### Phase 1 — `adk+think` (~1h, ~$4.43)
THINKING_BUDGET=1024 applies to whole ADK agent including query generation.  
**Hypothesis:** MRR improves on all eval sets. Biggest gain on `verify` and `edge_case`.  
**Decision gate:** If MRR gain < 0.02 → skip lg+mq+think (thinking won't help retrieval for lg either).

### Phase 2a — `lg+think` (~1.5h, ~$4.43)
THINKING_BUDGET=1024 on answer node only. Retrieval path unchanged.  
**Hypothesis:** MRR will be **unchanged** from lg baseline (0.2843). Confirms architectural hypothesis.  
**Decision gate:** If MRR moves > 0.01 either direction → investigate unexpected CRAG interaction.

### Phase 2b — `lg+mq+think` (~2.4h, ~$6.65)
MQ expansion + thinking on answer. Neither affects CRAG grading.  
**Hypothesis:** MRR ≈ lg+mq (0.2764). **⚠ Consider skipping** if budget tight.

### Phase 3 — `adk+rag` (~0.5h, ~$0.15)
Routes hc_adk tool calls to hc_rag's `/api/v1/retrieval`.  
**Hypothesis:** Significant MRR improvement — should approach rag_v2+ce (0.3847). Cheap, high signal.  
**Decision gate:** If MRR ≥ 0.35 → local RAG is the right path for all Bedrock-based agents.

### Phase 4 — `lg+rag` (~0.7h, ~$0.23)
Routes hc_lg retrieval to hc_rag (local RAG v2 + CE reranker). CRAG grades passages from local RAG.  
**Hypothesis:** Best combined config — should exceed rag_v2+ce (0.3847). Expected ceiling: 0.40+.  
**Risk:** CRAG query rewriting was tuned for Bedrock vocabulary; may not translate to local RAG embedding space.

### Run Commands

```bash
# Step 1 — Phases 1, 3, 4 (~1.5h, ~$5)
make ablation-full-golden ARGS=--adk-only

# Step 2 — Phases 2a+2b (~3.9h, ~$11). Review Phase 1 results first.
make ablation-full-golden ARGS=--lg-only

# Final compare (defaults to full 570)
make compare-golden
```

### Decision Gates Summary

| If... | Then... |
|---|---|
| `adk+think` MRR gain < 0.02 | Thinking doesn't help retrieval for adk; skip lg+mq+think |
| `lg+think` MRR ≠ lg baseline by > 0.01 | Unexpected; investigate before running lg+mq+think |
| `adk+rag` MRR ≥ 0.35 | Local RAG beats Bedrock; rag backend is the right path |
| `lg+rag` MRR > rag_v2+ce (0.3847) | CRAG + local RAG is best overall config |

---

## Roadmap

| Initiative | Expected gain | Status | Blocked on |
|---|---|---|---|
| Upgrade to gemini-3-flash-preview | +0.04–0.08 MRR | **In progress** | — |
| Multi-query retrieval | +0.05–0.10 MRR | **In progress** | — |
| hc_rag as retrieval backend | TBD | **In progress** | — |
| HyDE | +0.03–0.07 MRR | **Implemented** — needs eval run | `lg_rag_hyde` config ready |
| Reranker ablation | +0.02–0.08 MRR | **Implemented** — needs eval runs | `hc_rag_*` configs ready |
| Routing confidence gate | TBD | **Implemented** — needs eval run | `LLM_PLANNER=true ROUTING_CONFIDENCE_THRESHOLD=0.6` |
| In-session memory | TBD | **Implemented** — needs eval run | `LG_MEMORY_TURNS=3` |
| Query decomposition | +MRR on multi-part queries | **Planned** | Implement QUERY_DECOMP flag |
| Agentic RAG loop | +MRR where CRAG miscalibrated | **Planned** | Implement AGENTIC_RAG flag |
| Context dedup + diversity | Faithfulness improvement | **Planned** | Implement CONTEXT_DEDUP flag |
| DPO / preference fine-tuning | Potentially large | **Blocked** | Need 200+ golden preference pairs |

---

## Ablation Insights Summary

| Comparison | ΔMRR | Δlatency | Verdict |
|---|---|---|---|
| `adk_baseline` → `adk_thinking1024` | **+0.165** | +4.7s | Strong positive. Thinking budget is the single biggest lever for hc_adk. |
| `lg_no_crag` → `lg_crag` | +0.005 | +3.4s | Negligible. Bedrock HYBRID already retrieves well. |
| `lg_crag` → `lg_crag_thinking1024` | -0.063 | -0.3s | Negative interaction. Thinking changes citation style, confusing CRAG grader. |
| `lg_crag` → `lg_llm_planner` | -0.031 | +0.6s | Slightly negative. Regex router outperforms LLM on this domain. |
| `adk_flash_thinking1024` → `va_staging` | **-0.156** | -1.0s | **Best local config beats va_staging by +0.156 MRR and is faster.** |

---

## hc_lg Silent History Drop Bug (fixed)

**Bug:** `hc_lg/main.py` loads conversation history → `state["history"]` — but `answer_node` and `respond_node` never read it. Multi-turn context silently dropped.  
**Fix:** Inject last N turns via `LG_MEMORY_TURNS` (default 3). Both nodes read `state["history"]`.  
**Contrast with hc_adk:** ADK threads history through session automatically — memory injection fix is **hc_lg only**.

---

## Metrics Reference

- **MRR** = `(1/N) * Σ (1 / rank_of_first_golden_url)`. Range 0–1. Primary metric.
- **P@k** = `(golden URLs in top-k) / k`
- **NDCG@k** = weighted precision; more expressive than MRR for multi-golden tasks
- **Latency** = P50 / P95 end-to-end at `/chat`, first byte of complete response

Eval dataset: 44 total tasks, 32 annotated (12 are escalation/OOS — test routing, not retrieval).

**LLM grader cost reference** (model: `gemini-2.5-flash-lite`):

| Scenario | LLM calls | Est. cost |
|---|---|---|
| `grade-ablation` on 44-task set (1 config, 3 graders) | 132 | ~$0.04 |
| `grade-ablation-top` (2 configs × 44 × 3 graders) | 264 | ~$0.08 |
| 500-task final gate, 1 config, 3 graders | 1500 | ~$0.44 |

Note: `combined_ragas` is our custom single-prompt implementation — **not** the RAGAS library (which would cost 3–5× per task).

---

## VA Staging Comparison

```
Knowledge bases
├── Bedrock KB        Shine data (full corpus — all products, incl. Billy)
│                     URLs: help.shine.co/da/articles/{id}-{slug}
└── hc_rag DuckDB     242 Shine articles, 271 chunks with multilingual-e5-large
                      URLs: help.shine.co/da/articles/{id}-{slug} (subset)

VA golden (reference)
│  597 tasks, expected_urls: billy.dk/support/article/{slug}/
│
├── hc_adk  [VA_RETRIEVAL_MODE=bedrock]    :8011
├── hc_adk  [VA_RETRIEVAL_MODE=rag]        :8011
├── hc_lg   [VA_RETRIEVAL_BACKEND=bedrock] :8012
├── hc_lg   [VA_RETRIEVAL_BACKEND=rag]     :8012
└── hc_rag  [direct /chat shim]            :8013
```

**URL mapping is load-bearing for retrieval metrics.** VA golden uses Billy URL scheme (`billy.dk/...`); support agents return Shine/Intercom URLs (`help.shine.co/...`). These never match on raw string comparison → MRR = 0 without mapping. Build `data/datasets/url_mapping.json` from side-by-side comparison.

**Billypedia:** Never the primary retrieval target. For `definition` queries it provides context enrichment only; actual answer comes from help center articles. Billypedia misses in eval results are **expected and correct**.

---

## Experiment Tracking Schema

Schema design for reproducible RAG experiment tracking. Implements in `evals/pipelines/utils/schemas.py`.

### ExperimentRun — top-level identity

```python
@dataclass
class ExperimentRun:
    run_id: str          # uuid4 — unique per eval invocation
    experiment_name: str # human label
    created_at: str      # ISO 8601 UTC
    git_commit: str      # short SHA
    dataset: str         # path to .jsonl eval set
    pipeline: str        # "hc_rag" | "bedrock_kb" | "hybrid"
    rag_config: RagConfig
    bedrock_config: BedrockConfig | None = None
    notes: str = ""
```

### RagConfig — expanded

```python
@dataclass
class RagConfig:
    chunker: str = ""           # "fixed" | "semantic" | "recursive" | "hierarchical"
    chunk_size: int = 0
    chunk_overlap: int = 0
    parent_chunk_size: int = 0  # 0 = flat
    embedding_model: str = ""
    vector_store_backend: str = ""
    search_strategy: str = "dense"  # "dense" | "sparse" | "hybrid"
    hybrid_alpha: float = 1.0   # 1.0 = pure dense
    retrieval_k: int = 0
    score_threshold: float = 0.0
    reranker: str = ""
    reranker_top_k: int = 0
```

### BedrockConfig — for reproducing Bedrock calls

```python
@dataclass
class BedrockConfig:
    model_id: str = ""
    aws_region: str = ""
    knowledge_base_id: str = ""
    kb_retrieval_k: int = 0
    kb_search_type: str = ""    # "SEMANTIC" | "HYBRID"
    request_id: str = ""        # x-amzn-requestid header
    latency_ms: float = 0.0
```

### ChunkRecord — per-chunk metadata (hierarchical chunking)

```python
@dataclass
class ChunkRecord:
    chunk_id: str           # hash(doc_id + start_char)
    doc_id: str
    parent_id: str = ""     # "" = flat
    level: int = 0          # 0 = leaf (retrieved), 1 = parent window
    text: str = ""
    char_start: int = 0
    char_end: int = 0
    url: str = ""
    embedding_model: str = ""
```

**Custom RAG vs Bedrock KB** — Bedrock doesn't expose chunk IDs, retrieval scores, or passage text via API. Fair comparison uses URL matching + LLM-as-judge scores (faithfulness, relevance) — the dimensions available from both systems.

**Implementation priority:** P0 = ExperimentRun + BedrockConfig + RagConfig expansion. P1 = ChunkRecord + wire BedrockConfig into notebook 03.

---

## Open Questions

- Can CoT be added to hc_rag? Switch `LLM_PROVIDER=anthropic` for answer step (free swap, won't affect MRR but improves answer quality).
- VA-agents model: `gemini-2.5-flash-lite` in playground — weaker than our `gemini-2.5-flash`. Gap on core 179 may be prompting + KB quality, not model.
- Pairwise reranker `[SEP]` encoding: unclear whether MS-MARCO cross-encoder handles `query + " [SEP] " + docA` gracefully — may need a custom prompt template.
- If `adk+rag` MRR ≥ 0.35, should we add CE reranker directly on top of Bedrock results without rag backend? Feasible but `+rag` already achieves this — not planned.
