# Plan: RAG Latency Optimization

**Date:** 2026-04-29
**Status:** Baseline documented — experiments queued
**Scope:** `va-support-rag` LangGraph pipeline (11-node graph)

---

## POC Baseline (April 29)

Single German vendor-a query ("how do I create an invoice"):

| Stage | Time |
|---|---|
| Retrieval (embed + DuckDB ANN + cross-encoder rerank) | ~336ms |
| LLM answer generation (Gemini 2.5 Flash) | ~5.7s |
| **Total (P50 estimate)** | **~6.1s** |

Service: `va-support-rag` running locally, SQLite checkpointer, `rag-poc` variant.

---

## Why 6.1s? (Not the graph structure)

The 11-node graph runs: `planner → retriever → qa_policy_retrieval → qa_retrieval_gate → reranker → qa_policy_rerank → qa_rerank_gate → answer → post_answer_evaluator → summarizer → END`.

Most nodes are sub-millisecond policy/routing checks. The bottleneck is:

1. **`answer_node`**: single synchronous `get_answer_chain().invoke()` call — Gemini 2.5 Flash generating the full German answer from retrieved chunks. ~3–6s depending on response length.
2. **`post_answer_evaluator`**: disabled by default (`RAG_POST_ANSWER_EVALUATOR=false`). If enabled, adds a second LLM call (~1–2s) that can trigger re-retrieval.
3. **`summarizer`**: only fires when `len(messages) >= RAG_SUMMARIZATION_THRESHOLD` (default 8). No-op on most queries.

**The graph is not the problem. The LLM call is.**

---

## Observability Setup

Two tracing options are configured in `.env.example`:

| Tool | What it traces | Best for |
|---|---|---|
| **LangSmith** (`LANGSMITH_TRACING=true`) | LangGraph graph runs — per-node waterfall, token counts | Debugging graph turns, seeing exactly which node took how long |
| **LangFuse** (`LANGFUSE_ENABLED=true`) | Eval experiment results — hit_rate, MRR, per-query traces | Comparing retrieval variants, P5 calibration runs |

**To enable node-level profiling**: set `LANGSMITH_TRACING=true` + `LANGSMITH_API_KEY=` in `.env` → every graph run appears in LangSmith UI with a per-node waterfall.

**To see eval results locally**: `uv run python evals/runner.py run --export results/run1.json` — prints comparison table to stdout, saves JSON for further analysis.

**Streamlit explorer (future)**: a simple Streamlit app reading `results/*.json` could give visual hit_rate/MRR trends across runs. Not blocking experiments.

---

## Optimization Experiments

| # | Experiment | Expected gain | Effort | Status |
|---|---|---|---|---|
| E1 | **Streaming answer** | TTFT drops from 6s → ~1s (perceived) | Low | Pending |
| E2 | **Gemini 2.0 Flash for answer** | Total latency ~4s (2.0 Flash ~30% faster) | Low | Pending |
| E3 | **Gemini 2.0 Flash-Lite for answer** | Total latency ~2–3s; quality trade-off | Low | Pending |
| E4 | **Reduce context chunks** (`RAG_ANSWER_CONTEXT_MAX_CHUNKS`) | Smaller prompt → faster; test quality impact | Low | Pending |
| E5 | **Enable post_answer_evaluator** | +1–2s but catches hallucinations/bad answers | Low (env flag) | Pending |
| E6 | **Fast path for high-confidence retrievals** | Skip reranker when top score > threshold | Medium | Pending |
| E7 | **Parallel multi-query retrieval** | Expand 3 queries in parallel (already implemented in `expand_queries_for_retrieval`) | Low | Pending |

### Priority order
1. **E1 (streaming)** — biggest perceived improvement, no quality change
2. **E2 (Flash 2.0)** — easy model swap, measure quality regression on eval set
3. **E4 (context reduction)** — profile `RAG_ANSWER_CONTEXT_MAX_CHUNKS=3` vs `=5` vs default

---

## How to Run Experiments

### Measure current baseline against golden set
```bash
cd va-support-rag
uv run python evals/runner.py run \
  --path ../data/eval_data/eval_v2.jsonl \
  --export results/baseline_20260429.json
```

Output: hit_rate@12, MRR, chunk_hit_rate, avg_latency_ms, failure clusters.

### Enable LangSmith for node-level profiling
```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY=<key>
export LANGSMITH_PROJECT=va-support-rag
uvicorn main:app --port 8002
```
Then make a query — the trace appears in LangSmith with node timings.

### Compare Flash 2.5 vs 2.0 for answer
In `orchestrator/langgraph/chains.py` (or via env var if model is config-driven):
- Set answer model to `gemini-2.0-flash`
- Re-run eval: `uv run python evals/runner.py run --export results/flash20_20260429.json`
- Compare hit_rate and avg_latency_ms

---

## Open Questions

| Question | Blocks |
|---|---|
| Does streaming work end-to-end through va-support-rag → va-langgraph support_subgraph? | E1 |
| What is the quality regression when switching Flash 2.5 → 2.0? | E2 |
| What is the quality floor for reducing max_chunks from 5 → 3? | E4 |
| Is `expand_queries_for_retrieval` already async/parallel? | E7 |
