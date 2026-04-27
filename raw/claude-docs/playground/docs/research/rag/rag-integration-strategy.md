# RAG Integration Strategy — Research

**Date:** 2026-04-25
**Projects:** `help-support-rag-agent` (standalone agentic RAG), `playground/va-langgraph` (domain-routed VA)
**Question:** Should RAG live as a standalone peer agent, or be extracted as a subgraph/tool that domain subgraphs call?

---

## 0. Discovery Context (updated after initial research)

**What changed during research:**

The `mcp_servers/billy/app/tools/support_knowledge.py` implementation of `fetch_support_knowledge` turned out to be **real production AWS Bedrock code** — not a stub. It calls `bedrock-agent-runtime.retrieve()` with hybrid search (semantic + keyword) and Amazon Rerank v1, filters by 0.4 relevance threshold, and returns up to 4 deduplicated passages. It has a hardcoded Knowledge Base ID (`C36YGJVEQP`, eu-central-1).

**The user's position:**
- Bedrock Knowledge Base has never been used — no corpus loaded, no KB set up
- The custom RAG pipeline in `help-support-rag-agent` is what should power support retrieval
- Goal: replace `fetch_support_knowledge` (Bedrock) with the custom RAG pipeline
- AND keep the full standalone agentic RAG as a parallel experiment track

**This reframes the question from "standalone vs tool?" to two independent tracks:**

| Track | Goal | Timeline |
|---|---|---|
| **Track 1 — VA integration** | Replace Bedrock with thin custom RAG tool in va-langgraph/billy MCP. Simple Q&A, no fancy orchestration. | Near-term |
| **Track 2 — Standalone experiment** | Migrate `help-support-rag-agent` into playground as a peer service. Keep full 9-node graph, confidence gating, eval harness. Learn whether the complexity pays off. | Parallel / experimental |

Both tracks share the same `src/rag/` library (embedding, retrieval, reranking). Track 2 informs what eventually lands in Track 1.

**Key shared infrastructure question:** Both tracks need to point at the same knowledge base (Billy help/support docs). A shared DuckDB vector store or a shared Chroma instance would allow both tracks to use the same indexed corpus. The ingestion pipeline (`src/rag/preprocessing/` + `src/rag/ingestion/`) runs once offline; both services read from the same index.

---

## 1. Current Architecture Analysis

### Graph topology

`help-support-rag-agent` compiles a 14-node `StateGraph` (including `START`/`END`):

```
START
  └─ planner ──(q&a)──► retriever ──► qa_policy_retrieval
                                              ├──(rerank)──► reranker ──► qa_policy_rerank
                                              │                                  ├──(answer)──► answer ──► post_answer_evaluator ──► summarizer ──► END
                                              │                                  ├──(gate)──► qa_rerank_gate ─► [retriever|answer|escalation]
                                              │                                  └──(escalate)──► escalation ──► END
                                              ├──(gate)──► qa_retrieval_gate ─► [retriever|reranker|escalation]
                                              └──(escalate)──► escalation ──► END
  └─ planner ──(task)──► clarify ──► scheduler ──► confirm ──► answer ──► post_answer_evaluator ──► summarizer ──► END
```

The happy Q&A path is: `planner → retriever → qa_policy_retrieval → reranker → qa_policy_rerank → answer → post_answer_evaluator → summarizer → END` — **9 nodes** on the critical path.

`va-langgraph` is a flatter 17-node graph:

```
START → memory_load → guardrail → analyze → [domain subgraph] → format → END
                                     └─(blocked)──► blocked ──► END
```

Domain subgraphs are single async functions running a ReAct loop (`run_domain`). The `support_subgraph` already runs a lightweight CRAG loop (retrieve → grade → rewrite, max 2 retries) against `fetch_support_knowledge` via MCP. There is no cross-encoder reranking, no confidence gates, and no HITL pausing.

---

### Node-by-node breakdown (latency + purpose)

#### planner

- **LLM calls:** 0 by default (`RAG_LLM_PLANNER=false`). With `RAG_LLM_PLANNER=true`: 1 structured-output call using the planner chat model.
- **I/O:** JSON file read (cached after first call via `lru_cache`). String matching on user text.
- **Latency:** `<5ms` (keyword mode), `200–600ms` (LLM mode, small model).
- **Critical path:** Yes — every request hits planner.
- **Notes:** Keyword mode is reliable for a domain-narrow support bot where "schedule", "invoice" etc. are unambiguous signals. LLM mode adds meaningful latency for marginal benefit in this context.

#### retriever

- **LLM calls:** 0 by default. With `RAG_RETRIEVAL_QUERY_TRANSFORM=true`: 1 structured-output call to expand into 2–3 locale-aware queries.
- **I/O:** Embedding model inference (sentence-transformers, in-process), then vector store search (DuckDB/Chroma/OpenSearch depending on backend). All searches parallelised with `asyncio.gather`.
- **Latency (default, no query transform):**
  - Embedding 1 query: `10–30ms` (CPU, MiniLM-L6). `3–8ms` with `multilingual-e5-large` on warm GPU.
  - Vector search (DuckDB/Chroma local): `20–80ms`.
  - Total retrieval node: `~30–120ms`.
- **Latency (with query transform):** Add `200–500ms` for the LLM query rewrite.
- **Critical path:** Yes — every Q&A request.
- **Notes:** With a single retriever backend and no query transform, the retriever is fast. The `EnsembleRetriever` parallelises all query × retriever combinations via `asyncio.gather`, which is correct. With only one retriever configured (`get_local_retriever()`), it provides no ensemble benefit — it's a single-retriever with RRF fusion over one list. True ensemble value requires adding a BM25 retriever alongside the dense retriever.

#### qa_policy_retrieval

- **LLM calls:** 0 (score only mode). With `RAG_POLICY_MODE=hybrid`: 1 call to `get_hybrid_retrieval_probe_chain` (small/planner model) **only when** the ensemble signal falls in the borderline band `[0.85 * threshold, threshold)`.
- **I/O:** In-memory score comparisons only.
- **Latency:** `<1ms` (scores_only mode), `200–500ms` (hybrid, borderline path only).
- **Critical path:** Yes (cheap in default config).
- **Notes:** The hybrid probe fires only on borderline scores and uses the cheaper planner model. Well-scoped.

#### qa_retrieval_gate (HITL)

- **LLM calls:** 0 — pure `interrupt()`.
- **I/O:** Suspends graph execution until caller resumes.
- **Latency:** **Unbounded** — depends on human or calling system response time. Adds an async round-trip.
- **Critical path:** **No** — only fires when `qa_policy_retrieval` routes to `gate` (ensemble score below threshold, not in hybrid borderline band). Does not fire on the happy path.
- **Notes:** This is the correct placement. HITL should never be on the unconditional path.

#### reranker

- **LLM calls:** 0 (cross-encoder) or 1 (llm_listwise). Default is `passthrough` (no reranking).
- **I/O:**
  - `passthrough`: pure in-memory sort, `<1ms`.
  - `cross_encoder` (ms-marco-MiniLM-L-6-v2): model inference via `asyncio.to_thread`. For `top_k=8` candidates at ~200 tokens each on CPU: **100–300ms**. On GPU: **15–50ms**.
  - `llm_listwise`: 1 LLM call with all chunks in prompt. **300–700ms** (adds cost). Highest quality.
- **Critical path:** Yes — every Q&A request that clears `qa_policy_retrieval`.
- **Notes:** Default `passthrough` means the reranker node is a no-op in default config. Cross-encoder is the highest-value upgrade but carries a 100–300ms CPU penalty. With `RERANKER_TOP_K=5` and `RAG_ENSEMBLE_TOP_K=8`, the model scores 8 pairs per call — modest.

#### qa_policy_rerank

- **LLM calls:** 0 (scores_only) or 1 (hybrid borderline, same as retrieval policy).
- **I/O:** In-memory score comparison.
- **Latency:** `<1ms` (scores_only).
- **Critical path:** Yes (cheap).

#### qa_rerank_gate (HITL)

- Same pattern as `qa_retrieval_gate` — fires only when `qa_policy_rerank` routes to `gate`. Not on happy path.

#### answer

- **LLM calls:** 1 — the main generation call using `get_answer_chain()` (full chat model, not planner model).
- **I/O:** Token budget calculation and context truncation (in-memory). No network I/O other than the LLM call.
- **Latency:** **500ms–2000ms** depending on model (Gemini 2.5 Flash, GPT-4o, Claude 3.5 Sonnet) and response length. This is the dominant latency contributor on the happy path.
- **Critical path:** Yes — always.
- **Notes:** Uses `get_chat_model()` — the full-sized model. With prompt caching enabled, repeat-query latency is reduced but the first call pays full cost. Context is capped at `RAG_ANSWER_CONTEXT_MAX_TOKENS=6000` tokens — reasonable.

#### post_answer_evaluator

- **LLM calls:** 0 by default (`RAG_POST_ANSWER_EVALUATOR=false`). When enabled: 1 call using `get_post_answer_eval_chain()` (full chat model, structured output).
- **I/O:** None.
- **Latency:** `0ms` (disabled, returns `{}`). Enabled: `300–700ms`.
- **Critical path:** **Technically yes** (always runs), but the node returns `{}` immediately when disabled. Cost is one Python function call and config read.
- **Notes:** Off by default is the correct decision for latency. When enabled, this adds a full LLM round-trip after the answer is generated — effectively doubling visible wait time if both answer + evaluator are on the critical path.

#### summarizer

- **LLM calls:** 0 most turns. Fires when `len(messages) >= RAG_SUMMARIZATION_THRESHOLD` (default: 8). Uses `get_planner_chat_model()` (cheap model).
- **I/O:** None.
- **Latency:** `<1ms` most turns (threshold not reached). When triggered: `200–500ms` (cheap model, ~200 word output cap).
- **Critical path:** **No** — does not fire until turn 8. When it fires it's on every subsequent turn.
- **Notes:** Using the cheap/planner model here is correct. The 8-turn threshold means this does not affect P50 latency for a fresh support session, which typically resolves in 1–3 turns.

---

### Critical path analysis

**Minimum node count for a happy-path Q&A request (no query transform, no hybrid policy, passthrough reranker, post_answer_evaluator disabled):**

```
planner (5ms) → retriever (50–120ms) → qa_policy_retrieval (<1ms) → reranker (<1ms) → qa_policy_rerank (<1ms) → answer (500–2000ms) → post_answer_evaluator (0ms) → summarizer (0ms)
```

**Total minimum latency: ~600ms–2200ms**

With the default config, the entire retrieval-and-rerank path is extremely cheap. The answer node is the only meaningful contributor. Under the right model selection (Gemini 2.5 Flash, time-to-first-token ~300ms) and a short response, sub-1s is achievable.

**With cross-encoder reranker enabled (production recommendation):**

```
planner (5ms) → retriever (80ms) → qa_policy_retrieval (<1ms) → reranker (150–300ms) → qa_policy_rerank (<1ms) → answer (500–2000ms)
```

**Total: ~740ms–2400ms**

With a fast generative model (Flash-class) this is on the 2s boundary. With a slower model (GPT-4o in EU region, Claude 3.5 Sonnet) the answer node alone may hit 1500–2500ms, pushing total to 2–3s.

**With query transform enabled (not recommended for default):**

Add 200–500ms to retriever. Pushes worst-case to 3s+.

**With LLM planner enabled:**

Add 300–600ms to planner. Not recommended unless task/Q&A boundary is genuinely ambiguous.

---

### Confidence gating assessment

The system has two independent confidence gates, each with its own signal and threshold:

**Gate 1: `qa_retrieval_gate`** — triggered when the best RRF fusion score is below `RAG_ENSEMBLE_SCORE_THRESHOLD` (default: 0.4) AND the query is not in the hybrid borderline band.

- Signal: `max(c.score for c in graded_chunks)` — the best raw RRF score after filtering.
- Threshold: 0.4 — this is a moderately aggressive filter. RRF scores are not normalised in a standard way; raw values depend on corpus size and `rrf_k=60`. Setting 0.4 without corpus-specific calibration is a guess.
- **What it does:** If retrieved documents are weak by ensemble signal, pauses the run and asks the caller (human or consuming agent) whether to refine the query, proceed to rerank anyway, or escalate. The caller can inject a refined query and resume.
- **Smart design assessment:** Yes, conceptually sound. The problem is in practice: if this gate fires for every borderline query in a customer-facing chatbot, users see a pause for every "I'm not sure about that" question. The HITL model only makes sense when there is a human supervising in real time — in an autonomous Q&A system it should auto-route to escalate rather than pause.

**Gate 2: `qa_rerank_gate`** — triggered when cross-encoder top score is below `RAG_CONFIDENCE_THRESHOLD` (default: 0.25).

- Signal: `max(r.relevance_score for r in reranked_chunks)` where `relevance_score = sigmoid(raw_cross_encoder_score)`.
- Threshold: 0.25 sigmoid — this corresponds roughly to a raw cross-encoder score of ~-1.1. Very lenient. With `passthrough` reranker (default), sigmoid is not applied; `relevance_score = graded_chunk.score`. The threshold behaviour changes depending on the backend.
- **What it does:** After reranking, if top chunk is still weak, pauses again for human guidance.
- **Smart design assessment:** The two-gate design is **smart for a supervised HITL workflow** (agent monitoring a support queue, approving responses) but **overengineered for a fully autonomous chatbot**. In autonomous mode, both gates should collapse into a single decision: escalate or proceed. The current architecture supports both modes through config, but the gate node itself is always wired into the graph regardless.

**The hybrid policy** (`RAG_POLICY_MODE=hybrid`) adds optional LLM probes on borderline scores. This is clever — it avoids triggering HITL for queries that are marginally below threshold but where the LLM judges the retrieved snippets to be plausibly relevant. The LLM probe fires on at most ~10–15% of queries (those in the borderline band). This is one of the more sophisticated design decisions in the system.

**Verdict on gating:** The architecture is sound for supervised workflows. For autonomous deployment, both gates should be disabled (auto-escalate on low confidence) unless there is a real human in the loop consuming the interrupt signals. The current defaults are correct — `HITL` gates are wired but auto-escalate is the effective behaviour when no human resumes the run.

---

## 2. Latency Feasibility (<2s target)

### Happy-path breakdown

| Config variant | Planner | Retriever | Policy nodes | Reranker | Answer (Gemini 2.5 Flash) | Total |
|---|---|---|---|---|---|---|
| Full defaults (passthrough reranker) | 5ms | 80ms | 2ms | 1ms | 600–1500ms | **~700–1600ms** ✓ |
| Cross-encoder reranker, CPU | 5ms | 80ms | 2ms | 150–300ms | 600–1500ms | **~850–1900ms** ✓ (marginal) |
| Cross-encoder reranker, GPU | 5ms | 80ms | 2ms | 20–50ms | 600–1500ms | **~710–1650ms** ✓ |
| + Query transform | 5ms | 280–600ms | 2ms | 150ms | 600–1500ms | **~1050–2250ms** (borderline) |
| + LLM planner | 400ms | 80ms | 2ms | 150ms | 600–1500ms | **~1230–2130ms** (borderline) |
| + Post-answer eval | 5ms | 80ms | 2ms | 150ms | 600–1500ms + 300–700ms | **~1150–2450ms** (over budget) |

**Key finding:** With default config (passthrough reranker) and a Flash-class model, sub-2s is very achievable. The cross-encoder on CPU is the main risk. Query transform, LLM planner, and post-answer evaluator should all be treated as optional latency-budget items — choose at most one.

### Bottlenecks

1. **Answer generation (LLM call):** Irreducible. 500–2000ms depending on model and response length. Use the fastest model available that meets quality bar. Gemini 2.5 Flash is the right choice here; switching to GPT-4o or Sonnet without streaming can push this alone to 2s+.

2. **Cross-encoder reranker on CPU:** 100–300ms for 8 candidates. Moves the reranker from trivial to meaningful. The MiniLM model must be pre-loaded (the `lru_cache` on `_load_cross_encoder` handles this after the first call, but cold-start time is 2–5s for model loading).

3. **Vector store latency:** For DuckDB local, 20–50ms. For OpenSearch with network hop, 50–150ms. For cold-start DuckDB (first query), can spike to 200–500ms.

4. **Multiple sequential LLM calls:** The worst-case path (LLM planner + hybrid retrieval probe + reranker LLM listwise + answer + post-answer eval) involves 5 sequential LLM calls. Even with Flash, that is easily 3–5 seconds total.

5. **LangGraph checkpointer overhead:** Each node writes state to SQLite or Postgres. SQLite local adds ~5–15ms per node write. For 8 nodes on the happy path, that is ~40–120ms overhead. Postgres adds more. This is real but typically not the bottleneck.

### Optimization opportunities

**High impact, low effort:**
- Keep `RERANKER_BACKEND=passthrough` if quality metrics do not require reranking (already default).
- Keep `RAG_RETRIEVAL_QUERY_TRANSFORM=false` (already default). Only enable for multilingual queries where recall is demonstrably low.
- Keep `RAG_POST_ANSWER_EVALUATOR=false` (already default). Reserve for offline batch quality checking.
- Use streaming (`graph.astream_events`) for the answer node — user sees first tokens in ~200ms while generation continues. This makes the system feel sub-1s even when total generation is 1.5s.

**Medium impact, more work:**
- Add a BM25 retriever alongside the dense retriever to get actual ensemble benefit from RRF (current "ensemble" is single-backend).
- Pre-warm the cross-encoder model at startup if enabling it (`_load_cross_encoder` call on FastAPI lifespan).
- Use a dedicated embedding server (e.g. TEI — Text Embeddings Inference) rather than in-process sentence-transformers to avoid GIL contention with the FastAPI worker.

**Architectural:**
- Make `post_answer_evaluator` async and fire-and-forget (run after streaming response is sent, store eval results to a metrics store). Users get fast response; quality signals are captured without adding to perceived latency.
- Parallelize embedding + BM25 search (already done in `EnsembleRetriever` via `asyncio.gather` — just needs BM25 added).
- Add a retrieval cache for repeated queries (`src/rag/retrieval/cache.py` already exists — verify it is wired in).

---

## 3. Strategy Comparison

### Strategy A: Standalone Agentic RAG Agent

Keep `help-support-rag-agent` as a full autonomous agent. Wire it into `va-langgraph` as a peer service. The `support_subgraph` in `va-langgraph` calls it via HTTP (A2A protocol) or via the existing MCP tool (`fetch_support_knowledge`).

**Architecture:**

```
va-langgraph/support_subgraph
  └─ calls ──► help-support-rag-agent FastAPI endpoint (A2A or MCP)
                      └─ full 9-node LangGraph pipeline
                              └─ returns answer + citations
```

**When this complexity pays off:**
- The support domain is high-stakes (wrong answers cause escalations, churn, SLA breaches). Quality matters more than 200ms extra latency.
- The corpus is multilingual (Danish user base + English help docs) — query transform adds meaningful recall lift.
- You need HITL for supervised mode (e.g., a human agent reviewing low-confidence answers before they reach the user).
- The confidence gating / escalation logic needs to evolve independently of the VA routing logic.
- The eval harness and retrieval pipeline need to be iterated on separately from VA domain logic.

**Realistic latency:**
- Adds one network round-trip to the VA request: 5–20ms for local/container calls.
- The agentic RAG pipeline itself: 700–2000ms (see table above).
- Total va-langgraph request (analyze + support_subgraph → help-support-rag-agent + format): **900ms–2500ms**.
- With streaming end-to-end (LangGraph streaming events forwarded over SSE), P50 UX can feel sub-1s.

**Fit with va-langgraph:**
- The `support_subgraph` already makes an external call (`fetch_support_knowledge` via MCP). Replacing this with an A2A call to `help-support-rag-agent` is a clean swap.
- The va-langgraph `AgentState` does not need to know anything about the RAG internals — it receives a `tool_results` payload and passes to `format_node`.
- **Risk:** Two separate processes to deploy, monitor, and scale. The RAG agent's checkpointer is separate from the VA's Postgres checkpointer. Session state does not automatically share.

**What this design is good at:**
- Isolation: the RAG system can be upgraded, A/B tested, or replaced without touching the VA.
- Specialisation: cross-encoder, hybrid policy, query transform, eval harness — all meaningfully useful for a dedicated support knowledge base.
- Reuse: other agents (future researcher, escalation handler) can call the same RAG endpoint.

### Strategy B: RAG as Subgraph/Tool

Extract `src/rag/` from `help-support-rag-agent` as a retrieval utility. Create a thin Python function (or LangGraph subgraph) that performs: embed → retrieve → rerank → return chunks. Remove the multi-node orchestration, HITL gates, confidence routing, and post-answer evaluator. The domain subgraph in `va-langgraph` calls this directly, then passes chunks to the domain LLM for answer generation.

**Architecture:**

```
va-langgraph/support_subgraph
  └─ calls ──► rag_tool(query) → List[RankedChunk]
                  ├─ embed(query)
                  ├─ vector_search(embedding)
                  ├─ rrf_fuse(results)
                  └─ cross_encoder_rerank(query, chunks)
  └─ passes chunks to ──► run_domain(state, system_prompt, [rag_tool])
```

The `run_domain` ReAct loop already handles the LLM + tool-call cycle. The support LLM receives chunks as tool output and generates an answer — same as it currently does with `fetch_support_knowledge`.

**What you lose vs Strategy A:**

| Feature | Strategy A | Strategy B |
|---|---|---|
| Confidence gating (auto-escalate on low scores) | Yes | No — RAG tool always returns best-effort |
| HITL for supervised review | Yes | No |
| Multi-query retrieval (query transform) | Optional (configurable) | Manual — caller must implement |
| Hybrid policy (LLM probe on borderline) | Yes | No |
| Post-answer eval | Optional | No |
| Latency | Higher (more nodes) | Lower |
| Operational complexity | Higher (two services) | Lower (one service) |
| Eval harness | Full (RAGAS etc.) | None — must add separately |
| Multilingual query expansion | Configurable | Requires manual implementation |

**Latency profile:**
```
analyze (200ms) → support_subgraph:
  └─ rag_tool: embed + search + rerank = 80–350ms
  └─ run_domain LLM call: 600–1500ms
  └─ [possible tool call loop for CRAG: +1 LLM call = +500–1500ms]
→ format (200ms)
```
Total: **~1100–3500ms** depending on CRAG retry count. The CRAG loop in `support_subgraph` already does up to 3 LLM calls (retrieve + grade + rewrite + retrieve again). This is actually more latency risk than Strategy A's single retrieve → rerank → answer path.

**Integration into va-langgraph domain subgraphs:**
The existing `support_subgraph` already calls `fetch_support_knowledge` as an MCP tool. A cleaner integration would be:
1. Package `src/rag/` as an importable library or a FastAPI microservice.
2. Register it as a LangChain `Tool` or `BaseTool` subclass.
3. In `support_subgraph`, replace `fetch_support_knowledge` with `rag_retrieve` tool. The ReAct loop handles the tool call; the LLM sees the returned chunks and generates an answer.
4. Remove the manual CRAG loop from `support_subgraph` — the RAG tool handles retrieval quality internally.

**Risk:** The main advantage (simpler architecture) is partially offset by the current `support_subgraph` already doing CRAG. You gain simplicity in the RAG internals but the VA-level orchestration gains complexity.

### Recommendation matrix (when to use which)

| Scenario | Recommended strategy |
|---|---|
| Support queries are high-stakes; wrong answers escalate (CS SLA) | Strategy A |
| Team needs to iterate independently on retrieval quality (eval, embeddings, reranking) | Strategy A |
| Multilingual corpus with demonstrably weak single-query recall | Strategy A |
| Human supervisors reviewing borderline answers before delivery | Strategy A |
| Latency budget is hard <2s and you cannot tolerate tail risk | Strategy B |
| Single-team owns both VA and RAG; no need for independent deployment | Strategy B |
| Support is low-stakes / low-volume (direct answers acceptable) | Strategy B |
| Early stage — no eval harness yet, corpus is small | Strategy B |
| You already have `fetch_support_knowledge` MCP tool working | Hybrid: keep MCP, add confidence scoring in the tool itself |

**Hybrid path (pragmatic recommendation):** Keep the MCP transport but move the full retrieval pipeline (embed → retrieve → cross-encoder rerank → score) into `help-support-rag-agent`, exposed via a single `/retrieve` endpoint. The VA calls it synchronously. Remove the HITL gates for autonomous operation; use confidence score in the response payload to trigger auto-escalation at the VA level. This preserves the architectural separation without requiring HITL resumption logic in the VA.

---

## 4. Best Practices from the Field

### Agentic RAG patterns

The emerging 2025–2026 consensus is **Adaptive RAG** — a complexity-aware router that decides which pipeline a query deserves:
- Simple factual ("what is a DSO?") → fast single-pass RAG, no agentic loop.
- Multi-hop or ambiguous → agentic RAG with query rewriting and confidence gating.
- Completely out-of-scope → direct answer or escalate without retrieval.

The `help-support-rag-agent` is already implementing this with its planner + policy routing, but without the classification step that distinguishes easy from hard questions before hitting the retriever. Adding a complexity classifier in the planner would let the system skip the confidence gates entirely for high-confidence simple queries.

Source: [Agentic RAG vs Classic RAG — Towards Data Science](https://towardsdatascience.com/agentic-rag-vs-classic-rag-from-a-pipeline-to-a-control-loop/), [Building Production-Ready Agentic RAG Systems — Adaline Labs](https://labs.adaline.ai/p/building-production-ready-agentic)

### Sub-2s RAG in production

Practical findings from production deployments:
- **LangChain adds 50–100ms per LLM call** in orchestration overhead. For 9 nodes with several LLM calls, this compounds.
- **Streaming is the primary UX lever.** `graph.astream_events` with token streaming from the answer node allows users to see first tokens in ~200–400ms, making a 1.5s total generation feel fast.
- **Embedding inference in-process is a GIL risk.** With async FastAPI workers, heavy CPU-bound sentence-transformers inference blocks the event loop. Use `asyncio.to_thread` (already done in the cross-encoder) or a dedicated embedding service.
- **Self-RAG / CRAG-style validation loops add 2–3s** per retry iteration. The current `support_subgraph` in va-langgraph does this — up to 3 iterations means potentially 6–9 extra seconds in the worst case. Setting `max retries = 1` with a quality floor is the pragmatic production limit.
- **Cross-encoder on CPU for 8 candidates**: ~150–250ms (MiniLM-L6). Acceptable if the answer LLM is also running. Use `asyncio.to_thread` (already done).

Source: [Next-Generation Agentic RAG with LangGraph — Medium](https://medium.com/@vinodkrane/next-generation-agentic-rag-with-langgraph-2026-edition-d1c4c068d2b8), [Building Agentic Adaptive RAG for Production — AI Plain English](https://ai.plainenglish.io/building-agentic-rag-with-langgraph-mastering-adaptive-rag-for-production-c2c4578c836a)

### Confidence routing: established patterns

Confidence routing in RAG is an **established and well-validated pattern**, not an anti-pattern. However, specific failure modes are well-documented:

1. **Raw score thresholds without calibration**: RRF scores, cosine similarities, and cross-encoder logits are not directly comparable across corpus sizes or embedding models. Setting `threshold=0.4` for RRF and `threshold=0.25` for sigmoid(cross-encoder) without corpus-specific calibration is common but risky. A 0.4 RRF threshold on a 10k-document corpus is not the same as on a 100k-document corpus.

2. **HITL gates in autonomous pipelines**: Interrupting execution and waiting for a human response is correct in supervised workflows. In fully autonomous chat, these gates should degrade gracefully to auto-escalate — which the current system does when no human resumes (the gate falls through to "escalation"). This is the right behaviour.

3. **Two sequential gates** increase the probability that at least one fires. If each gate fires 15% of the time and they are independent, the combined gate-fire rate is ~28%. In practice they are correlated (weak retrieval usually means weak rerank too), so the rate is lower, but still meaningful for high-volume support.

4. **Best practice from 2025 production**: Run confidence thresholds on a golden eval dataset (50–100 representative questions) and tune for the desired escalation rate, not for an arbitrary score value. Set a target like "auto-escalate at most 10% of queries" and calibrate thresholds to that.

Source: [Production RAG in 2025 — Dextralabs](https://dextralabs.com/blog/production-rag-in-2025-evaluation-cicd-observability/), [METIS: Fast Quality-Aware RAG Systems — Microsoft Research](https://www.microsoft.com/en-us/research/wp-content/uploads/2025/10/sosp25-final547.pdf)

---

## 5. Verdict & Open Questions

### The confidence gating design

**`qa_retrieval_gate` + `qa_rerank_gate`:**
- **Smart design for a supervised HITL product.** Two checkpoints give a human supervisor two opportunities to intervene — before expensive reranking and after. This is correct if there is a human supervising the queue.
- **Overengineered for fully autonomous deployment.** In autonomous mode (no human resumes), both gates collapse to the same outcome: escalate. The graph complexity is maintained for a code path that never fires usefully. A simpler version would have a single `confidence_gate` after reranking.
- **Threshold calibration is the real risk**, not the gate architecture itself. Neither `0.4` (RRF) nor `0.25` (sigmoid) are justified by corpus-specific calibration. The hybrid policy's borderline-band concept is a clever workaround for this problem, but it adds another LLM call.

**`post_answer_evaluator`:**
- Off by default: correct.
- When enabled, it fires on every Q&A response — including high-confidence, clearly correct answers. There is no score-based bypass ("if confidence_score > 0.85, skip eval").
- **Adding value only when it would trigger "refine" or "escalate"** — both of which require the answer to be wrong or uncertain. Running it on correct answers adds 300–700ms of latency for zero user-visible value.
- Recommendation: **gate it on `confidence_score < threshold`**. If the reranker was highly confident, skip the post-answer eval entirely.

**`summarizer`:**
- Not on the critical path for typical support sessions (1–3 turns). Does not fire until turn 8.
- When it fires, it uses the cheap/planner model with a 200-word cap — appropriately scoped.
- Position in the graph (after `answer`, before `END`) means it adds latency at turn 8+. Using a background task or async fire-and-forget would remove this from the user-visible path.
- **Justified** for long multi-turn sessions (turn 8+). Not a problem for typical support queries.

### Leaner graph proposal

For autonomous deployment (no human HITL), the critical-path graph can be simplified to:

```
START → planner → retriever → qa_policy → reranker → answer → END
                                   └──(low_confidence)──► escalation → END
```

6 nodes vs 9 on the happy path. Remove: `qa_retrieval_gate`, `qa_rerank_gate`, `post_answer_evaluator` (or make post-hoc/async), `summarizer` (async). Merge `qa_policy_retrieval` + `qa_policy_rerank` into a single `qa_policy` node that checks both signals and decides in one pass.

**What this loses:** The two-stage gate design does provide useful telemetry — you can see exactly where in the pipeline quality breaks down (retrieval vs reranking vs generation). If you merge to a single policy node, you lose that signal granularity. For a mature system with good observability, this is an acceptable trade. For a system still being tuned, keep the two policy nodes.

### Open questions requiring answers before decision

1. **What is the actual escalation rate in production?** If >15% of queries go through the gate, threshold calibration is urgent. If <3%, the gates add complexity without observable value.

2. **Is there a human supervisor consuming the HITL interrupts?** This is the single most important architectural decision. If yes: keep Strategy A, keep both gates. If no: simplify to auto-escalate.

3. **What is the real corpus size and language distribution?** Query transform and BM25 ensemble value depend heavily on this. For a <5k chunk English-only corpus, neither is likely to add meaningful recall lift.

4. **Does the va-langgraph `support_subgraph` CRAG loop actually help vs single-pass?** The current support subgraph does up to 3 LLM-call iterations. If grader often says "sufficient" on attempt 1, the CRAG loop is a good design. If it frequently retries, the latency is high and the benefit should be verified by eval.

5. **What does `fetch_support_knowledge` actually do?** It is called via MCP (`billy_mcp_server`). Whether it performs dense retrieval, BM25, or a simple keyword search determines how much value the `help-support-rag-agent` pipeline adds on top of it.

6. **Is cross-encoder reranking justified by eval data?** The current default is `passthrough`. If there is no eval showing reranking improves answer quality, enabling cross-encoder adds 150–300ms for unclear gain.

---

## Summary recommendation

For `va-langgraph/support_subgraph` specifically:

**Near-term (< 2 weeks):** Do nothing architecturally. The current `support_subgraph` + `fetch_support_knowledge` MCP integration is working. Measure actual latency end-to-end and the escalation/grader retry rate before making a decision.

**Medium-term:** If `fetch_support_knowledge` is a simple search tool (keyword / basic vector), upgrade to Strategy B — extract the `src/rag/` pipeline as a `rag_retrieve` tool the support subgraph calls. Add cross-encoder reranking (CPU is fine for the expected load). Keep the CRAG loop but cap at 1 retry. Expected total latency: 1.2–2.0s.

**If quality bar is high (low hallucination tolerance, human CS team reviewing escalations):** Strategy A. Deploy `help-support-rag-agent` as a sidecar service. Wire `support_subgraph` to call it via A2A. Disable HITL gates in the RAG agent (auto-escalate); surface confidence score in the response payload to the VA. Expected latency: 900ms–2s (streaming makes this feel fast).

**In either case, the priority actions for hitting sub-2s are:**
1. Enable streaming from the answer LLM node.
2. Pre-warm the cross-encoder at service start.
3. Cap CRAG retries at 1 in `support_subgraph`.
4. Keep `RAG_POST_ANSWER_EVALUATOR=false` and `RAG_RETRIEVAL_QUERY_TRANSFORM=false` in production.
5. Calibrate confidence thresholds against a golden eval dataset before tuning them.

---

## 6. Dual-Track Architecture (updated decision)

Given that:
- Bedrock KB is wired but never used (no corpus loaded)
- The custom RAG pipeline is the intended replacement
- The goal is both "make it work in the VA" AND "understand the agentic RAG complexity"

The recommended approach is to run both tracks in parallel within playground:

### Track 1 — `mcp_servers/billy/` RAG tool (replaces Bedrock)

Replace `fetch_support_knowledge` in `app/tools/support_knowledge.py` with a thin wrapper around `src/rag/`:

```
billy MCP: fetch_support_knowledge(query)
  └─ rag_retrieve(query)
      ├─ embed(query)                   # sentence-transformers, in-process
      ├─ vector_search(embedding)       # DuckDB local index
      ├─ rrf_fuse(results)              # RRF merge (single backend = passthrough)
      └─ cross_encoder_rerank(chunks)   # MiniLM-L6, CPU, ~150ms
  └─ returns List[SupportPassage]       # same shape as current Bedrock response
```

The `support_subgraph` in va-langgraph sees no change — it still calls `fetch_support_knowledge` via MCP. The change is entirely inside billy MCP. No HITL, no confidence gates, no multi-node graph. Just retrieval.

**What to delete from current code:** Drop boto3 dependency, remove bedrock-agent-runtime client, remove AWS credential handling. Replace with local vector store read.

**Data ingestion:** Run `src/rag/preprocessing/` + `src/rag/ingestion/` offline to build the DuckDB index from Billy help docs. Index lives in `mcp_servers/billy/data/vectorstore/` (volume-mounted in docker-compose).

**Latency impact:** Current Bedrock call has network round-trip to AWS (~100–200ms EU). Local DuckDB retrieval is 20–50ms. Net improvement.

### Track 2 — `va-support-rag/` standalone agentic RAG (migrated into playground)

Migrate `help-support-rag-agent` into `playground/va-support-rag/`. Wire it into `infrastructure/containers/docker-compose.va.yml` as a peer service alongside `va-langgraph` and `va-google-adk`.

Purpose: experimentation. Keep the full 9-node graph. Use it to:
- Calibrate the confidence thresholds (`0.4` RRF, `0.25` sigmoid) against real Billy help doc queries
- Validate whether cross-encoder reranking actually improves answer quality vs passthrough
- Test the HITL gates (disable for autonomous mode; keep wired for supervised experiments)
- Run the eval harness (Ragas, DeepEval) to establish a quality baseline
- Determine whether the `post_answer_evaluator` catches real errors or adds latency for no gain

Both tracks point at the **same DuckDB index** (shared volume or copied at startup). Track 2's eval results directly inform when/whether to promote complexity from Track 2 into Track 1.

### Migration scope for Track 2

Cleanup needed to align with playground conventions:

| What | Current state | Target |
|---|---|---|
| Multi-provider LLM factory | `LLM_PROVIDER=gemini\|openai\|anthropic\|bedrock` | Adopt `resolve_chat_model(size)` from `va-langgraph/shared/model_factory.py`; default to Gemini Flash |
| `app/` mirror | Duplicate of `src/main.py` | Delete `app/`, keep `src/` only |
| Checkpointer | Configurable `sqlite\|postgres\|memory` | Default Postgres (shared RDS in prod, SQLite for local dev) |
| Docker | Standalone `infra/docker/docker-compose.yml` | Add service to `infrastructure/containers/docker-compose.va.yml` |
| Imports | `from src.rag...` absolute | Normalise to package-relative imports |
| `.env` | Standalone | Merge keys into playground's `.env.example` |

### Corpus status per track

**Track 2 — sevdesk corpus (already exists)**
`help-support-rag-agent` was built and evaluated against **sevdesk** help/support sources. The DuckDB index, ingestion pipeline, and eval test set are all sevdesk-based. This is what powers the existing eval results and what the confidence threshold defaults were (loosely) tuned against.

Track 2 is immediately runnable. The corpus and eval set migrate with the codebase.

**Track 1 — Billy corpus (does not exist yet)**
`fetch_support_knowledge` calls a Bedrock KB that has never been loaded. No Billy help docs have been ingested. Track 1 is **blocked on corpus creation** — scraping or exporting Billy's help documentation is a prerequisite before the RAG tool can replace the Bedrock call meaningfully.

**Sequencing implication:**
- **Now:** Migrate `help-support-rag-agent` → `playground/va-support-rag/` (Track 2). Runs immediately on sevdesk corpus. Use for experimentation, confidence calibration, eval baseline.
- **Later (when Billy docs are available):** Run the ingestion pipeline against Billy help content. Wire Track 1 (thin RAG tool in `mcp_servers/billy/`) against the Billy index. At that point, Track 2 can also be re-pointed to Billy for a fair comparison.

The sevdesk corpus serves a different purpose in this context: it is the **eval and calibration vehicle** — it tells us whether the confidence gating, cross-encoder reranking, and hybrid policy are worth keeping before we commit to building a Billy corpus around them.

### What "compare and experiment" looks like

Phase 1 (sevdesk corpus, both tracks use it):
1. Run Track 2 eval harness against sevdesk golden dataset — measure hit rate, MRR, NDCG, escalation rate
2. Calibrate confidence thresholds (0.4 RRF, 0.25 sigmoid) against actual query distribution
3. Determine: does cross-encoder reranking lift MRR by >5%? Does `post_answer_evaluator` catch real errors?
4. Validate sub-2s latency under realistic query load

Phase 2 (Billy corpus ready):
1. Run ingestion pipeline on Billy help docs → build `billy_help.duckdb`
2. Deploy Track 1 (thin RAG tool in billy MCP) with Billy index
3. Point Track 2 at Billy index — run same eval suite
4. A/B compare Track 1 (simple) vs Track 2 (agentic) on Billy queries
5. Promote only what the eval data supports into Track 1

This is a legitimate staged experiment: **validate the complexity on sevdesk first, then apply learnings to Billy.**
