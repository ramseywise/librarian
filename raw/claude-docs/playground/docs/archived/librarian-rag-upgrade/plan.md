# Plan: Librarian RAG Upgrade

**Status:** Phase 1 complete
**Scope:** `src/librarian/`, `src/orchestration/` — RAG-only (no agent autonomy expansion)
**Depends on:** [langgraph-adk-compatibility.md](langgraph-adk-compatibility.md) (partially overlapping — this plan supersedes the ADK tools rewrite in that doc)
**Consolidated from:** `librarian-rag-template.md` (merged 2026-04-14) — template architecture is now Phase 2 of this plan

---

## Problem Statement

The Librarian pipeline works but has gaps compared to production-grade RAG patterns:

1. **Multi-query retrieval is ad-hoc.** `RetrieverAgent` already supports `query_variants` via `QueryPlan`, but there's no reusable `EnsembleRetriever` primitive. Dedup is chunk-ID based (`_grade_chunks`) — no global fingerprint dedup across sources. The ADK `search_knowledge_base` tool is single-query only.

2. **Generator output is unstructured.** `call_llm()` returns raw `str`. There's no Pydantic model enforcing response shape (answer text, citations, confidence, follow-up suggestions). No use of Claude structured JSON mode.

3. **No framework-agnostic tool abstraction.** The retriever is bound to LangGraph state (`LibrarianState`) in `RetrieverAgent` and to raw protocol calls in ADK `tools.py`. There's no shared callable tool object with explicit I/O schema that both LangGraph and ADK can use without reimplementation.

4. **A few hardcoded constants remain.** `_RELEVANCE_THRESHOLD = 0.1` in `retrieval.py`, `DEFAULT_CONFIDENCE_GATE = 0.3` in `generation.py`, `RRF_K = 60` in `rrf.py` — should flow from config.

---

## What We Are NOT Doing

- **Not adding agent autonomy.** Librarian stays RAG-only — no multi-hop reasoning, no tool-use loops, no memory.
- **Not changing the CRAG state machine.** The LangGraph graph structure stays the same; we're improving the primitives it calls.
- **Not adding LangChain dependencies.** The `EnsembleRetriever` is our own class, not `langchain.retrievers.EnsembleRetriever`.
- **Not changing storage backends.** Chroma, OpenSearch, DuckDB all stay as-is.

---

## Phase 1 — Practical Upgrades (shippable independently)

### Step 1 — `EnsembleRetriever` with fingerprint dedup ✅

**Files:** new `src/librarian/retrieval/ensemble.py`, edit `src/librarian/retrieval/__init__.py`
**Tests:** new `tests/librarian/unit/test_ensemble.py`

Create a standalone `EnsembleRetriever` class that:

```python
class EnsembleRetriever:
    """Multi-query, multi-retriever fusion with fingerprint dedup."""

    def __init__(
        self,
        retrievers: list[Retriever],
        embedder: Embedder,
        *,
        score_threshold: float = 0.4,       # from config
        max_queries: int = 3,                # from config
    ) -> None: ...

    async def retrieve(
        self,
        queries: list[str],               # 1–3 query variants
        k: int = 10,
    ) -> list[GradedChunk]: ...
```

Key behaviors:
- `asyncio.gather` runs all queries × all retrievers in parallel (queries × retrievers matrix)
- Fingerprint dedup: `f"{chunk.metadata.url}|{chunk.text[:200].lower().strip()}"` → SHA-256 → keep highest-scored copy
- Score threshold filtering: drop chunks below `score_threshold` (configurable via `LibrarySettings.confidence_threshold`)
- RRF fusion across all result lists using existing `fuse_rankings()`
- Returns `list[GradedChunk]` — same interface the reranker already expects

The existing `RetrieverAgent` will be updated to delegate to `EnsembleRetriever` instead of manually managing the embed → search → dedup flow. This collapses ~60 lines in `RetrieverAgent.run()` to ~5.

### Step 2 — `RAGResponse` Pydantic model + structured output ✅

**Files:** new model in `src/librarian/schemas/response.py`, edit `src/librarian/generation/generator.py`
**Tests:** edit `tests/librarian/unit/test_generator.py`

Define a structured response model:

```python
class Citation(BaseModel):
    url: str
    title: str
    snippet: str = ""       # relevant excerpt from source

class RAGResponse(BaseModel):
    answer: str
    citations: list[Citation]
    confidence: Literal["high", "medium", "low"]
    follow_up: str = ""     # suggested follow-up question (optional)
```

Update `call_llm()` → `call_llm_structured()` path:
- When `RAGResponse` validation is desired (retrieval intents), the system prompt instructs Claude to respond in JSON matching the schema
- Parse response with `RAGResponse.model_validate_json()`
- Fallback: if JSON parsing fails, wrap raw text in `RAGResponse(answer=raw_text, citations=..., confidence="low")`
- `extract_citations()` is replaced by the model's `citations` field
- The `GeneratorAgent.run()` return dict gains `"response_model": RAGResponse` alongside the existing `"response": str` for backward compat

Keep the unstructured path for `conversational` and `out_of_scope` intents — those don't need JSON mode.

### Step 3 — Tool abstraction layer (`BaseTool` protocol) ✅

**Files:** new `src/librarian/tools/base.py`, new `src/librarian/tools/retriever_tool.py`, new `src/librarian/tools/__init__.py`
**Tests:** new `tests/librarian/unit/test_tools.py`

Define a minimal tool protocol that both LangGraph and ADK can consume:

```python
class ToolInput(BaseModel):
    """Override in subclasses to define tool input schema."""
    ...

class ToolOutput(BaseModel):
    """Override in subclasses to define tool output schema."""
    ...

@runtime_checkable
class BaseTool(Protocol):
    name: str
    description: str
    input_schema: type[ToolInput]
    output_schema: type[ToolOutput]

    async def run(self, input: ToolInput) -> ToolOutput: ...
```

Concrete `RetrieverTool`:

```python
class RetrieverToolInput(ToolInput):
    queries: list[str] = Field(min_length=1, max_length=3)
    num_results: int = Field(default=10, ge=1, le=50)

class RetrieverToolOutput(ToolOutput):
    results: list[GradedChunkDict]
    total: int
    deduplicated: int

class RetrieverTool:
    name = "search_knowledge_base"
    description = "Multi-query hybrid search over the knowledge base"
    input_schema = RetrieverToolInput
    output_schema = RetrieverToolOutput

    def __init__(self, ensemble: EnsembleRetriever) -> None: ...

    async def run(self, input: RetrieverToolInput) -> RetrieverToolOutput:
        chunks = await self.ensemble.retrieve(input.queries, k=input.num_results)
        return RetrieverToolOutput(results=..., total=..., deduplicated=...)
```

**ADK adapter** (update `src/orchestration/google-adk/tools.py`):
- `search_knowledge_base()` becomes a thin wrapper: build `RetrieverToolInput` from args → call `RetrieverTool.run()` → return `.model_dump()`
- Same pattern for `rerank_results` → `RerankerTool`

**LangGraph adapter** (update `src/orchestration/langgraph/nodes/retrieval.py`):
- `RetrieverAgent.__init__` accepts a `RetrieverTool` (or `EnsembleRetriever` directly)
- `RetrieverAgent.run()` delegates to it

This makes it trivial to wrap any tool for a new framework (LangGraph ToolNode, ADK FunctionTool, or a future Python agent SDK) without reimplementation.

### Step 4 — Config-driven constants ✅

**Files:** edit `src/librarian/config.py`, edit files referencing hardcoded values
**Tests:** edit existing config/factory tests

Move remaining hardcoded values to `LibrarySettings`:

| Constant | Current location | Config field | Default |
|---|---|---|---|
| `_RELEVANCE_THRESHOLD = 0.1` | `retrieval.py:17` | `relevance_threshold` | **already exists** (0.1) — just wire it |
| `DEFAULT_CONFIDENCE_GATE = 0.3` | `generation.py:19` | `confidence_threshold` | **already exists** (0.4) — use it, remove local override |
| `RRF_K = 60` | `rrf.py:18` | new: `rrf_k` | 60 |
| `_CONTEXT_SEP` | `generator.py:15` | leave as-is (not tunable) | — |
| `score_threshold` in `EnsembleRetriever` | Step 1 | `confidence_threshold` | 0.4 |

Notable: `DEFAULT_CONFIDENCE_GATE` (0.3) in `generation.py` **disagrees** with `confidence_threshold` (0.4) in config. The factory already passes `cfg.confidence_threshold` to `GeneratorAgent`, so the local constant is dead code — remove it and rely on the injected value.

Wire `relevance_threshold` from config into `RetrieverAgent` constructor (currently reads from the `_RELEVANCE_THRESHOLD` module constant).

### Step 5 — CI parity (Makefile + shared conventions) ✅

**Files:** edit `Makefile`, possibly new `pyproject.toml` test markers
**No new code in `src/`**

Align test/lint targets with the ADK-style conventions:

- Add `make test-librarian`, `make test-adk`, `make test-all` targets (currently eval-focused Makefile)
- Add `make lint` (ruff check + format check) and `make typecheck` (pyright)
- Ensure `SCORE_THRESHOLD` and `NUM_QUERIES_MAX` are validated in a `test_config.py` confirming they're config-driven, not hardcoded
- Add a test that imports both LangGraph and ADK tool wrappers and verifies they produce equivalent outputs for the same input (parity test)

---

## Phase 2 — Architecture (subgraphs, registry, evals)

> Consolidated from `librarian-rag-template.md`. Phase 2 restructures the pipeline into
> a supervisor multi-agent RAG system with swappable strategies. Phase 1 must be complete
> first — Phase 2 builds on the EnsembleRetriever, RAGResponse, and BaseTool primitives.

### Step 6 — Package scaffold under `src/agents/librarian/`

Create module structure: `schemas/`, `ingestion/`, `retrieval/`, `reranker/`, `generation/`,
`orchestration/subgraphs/`, `evals/`, `utils/`. Add `pyproject.toml` optional deps
(`langgraph`, `langchain-core`, `langchain-anthropic`, `opensearch-py`, `sentence-transformers`,
`ragas`, `deepeval`, `langfuse`). Stub `conftest.py` with `reset_registry` autouse fixture.

### Step 7 — Schemas + LibrarySettings

Pydantic models: `Chunk`, `ChunkMetadata`, `GradedChunk`, `RankedChunk`, `Intent` enum,
`RetrievalResult`, `QueryPlan`, `LibrarianState` (TypedDict with `add_messages` reducer).
`LibrarySettings` via pydantic-settings (embedding model, retrieval/reranker strategy,
confidence threshold, langfuse config). Reuse `RAGResponse` from Phase 1 Step 2.

### Step 8 — Ingestion module

`Chunker` Protocol + `HtmlAwareChunker` (heading-boundary splitting, recursive fallback)
and `ParentDocChunker` (parent/child linking for retrieval vs generation).

### Step 9 — Retrieval module

`Embedder` Protocol (E5 prefix enforcement), `Retriever` Protocol, `OpenSearchRetriever`
(async, hybrid BM25 + k-NN), `InMemoryRetriever` (for tests), `MultilingualEmbedder`,
`MockEmbedder`. Integrate with Phase 1's `EnsembleRetriever`.

### Step 10 — Reranker + Generation modules

Reranker: `CrossEncoderReranker` (ms-marco-MiniLM) + `LLMListwiseReranker` (Haiku).
Generation: intent-specific system prompts, `build_prompt`, `call_llm`, `extract_citations`.
Wire to Phase 1's `RAGResponse` structured output.

### Step 11 — Query understanding + subgraphs

`QueryAnalyzer` (rule-based intent classification, expansion, entity extraction) +
`QueryRouter`. Three LangGraph subgraphs: retrieval (rewrite → expand → retrieve → grade →
CRAG check), reranker (rerank → set_confidence), generation (prompt → LLM → citations).

### Step 12 — Registry + supervisor graph

Explicit strategy registry (no decorator magic). Supervisor graph wires subgraphs:
`START → plan_node → [retrieve/direct/clarify] → subgraphs → confidence_gate → END`.
Factory function `build_library_graph()` with DI for all components.

### Step 13 — Eval suite

`GoldenSample` model, tiered extraction (gold/silver/bronze), `evaluate_retrieval`
(hit@k, MRR, failure clustering), `AnswerJudge` (Haiku LLM-as-judge: faithfulness,
relevance, completeness), `generate_synthetic` with cost gate. deepeval integration.

---

## Dependency Graph

```
Phase 1:
  Step 4 (Config) — can start first, unblocks clean constructors
  Step 1 (EnsembleRetriever) — after Step 4
    ├──→ Step 2 (RAGResponse — independent of Step 3)
    └──→ Step 3 (Tool abstraction → ADK + LangGraph adapters)
  Step 5 (CI) — after Steps 1-4

Phase 2 (after Phase 1 complete):
  Step 6 (Scaffold) → Step 7 (Schemas) → Step 8 (Ingestion) → Step 9 (Retrieval)
    → Step 10 (Reranker + Generation) → Step 11 (Query understanding + subgraphs)
    → Step 12 (Registry + supervisor) → Step 13 (Evals)
```

**Phase 1 order:** Step 4 → Step 1 → Step 2 → Step 3 → Step 5
**Phase 2 order:** Sequential, Steps 6–13. Each builds on the previous.

---

## Risk & Mitigations

| Risk | Mitigation |
|---|---|
| Fingerprint dedup misses near-duplicates with different URLs | Fingerprint is `url|content[:200]` — catches exact and near-duplicates from same source. Cross-source near-dupes are handled by the existing reranker. |
| Structured JSON mode fails on edge cases | Fallback wraps raw text in `RAGResponse(confidence="low")`. Test with adversarial prompts. |
| `BaseTool` protocol adds indirection | Keep it minimal (4 fields + 1 method). If it doesn't earn its keep after Step 3, collapse it. |
| Config drift between LangGraph and ADK paths | Parity test (Step 5) catches this. Both paths pull from the same `LibrarySettings` singleton. |

---

## Acceptance Criteria

### Phase 1
- [ ] `EnsembleRetriever.retrieve(["q1", "q2"])` returns deduped, score-filtered `GradedChunks` — unit test with `MockEmbedder` + `InMemoryRetriever`
- [ ] `RAGResponse` validates generator output; fallback path tested with malformed JSON
- [ ] `RetrieverTool` has explicit `input_schema` / `output_schema`; both ADK and LangGraph use it
- [ ] Zero hardcoded threshold/tuning constants in `src/librarian/` or `src/orchestration/` — all flow from `LibrarySettings`
- [ ] `uv run pytest tests/librarian/ tests/orchestration/` passes
- [ ] Parity test confirms LangGraph and ADK produce equivalent retrieval results

### Phase 2
- [ ] Supervisor graph routes correctly: retrieve/direct/clarify paths all tested
- [ ] CRAG retry fires once then stops (off-by-one covered)
- [ ] Registry swaps strategies via env var; autouse fixture isolates tests
- [ ] Eval suite: hit@k, MRR computed correctly; LLM-as-judge with mocked calls
- [ ] All tests pass without Docker, API keys, or model downloads
