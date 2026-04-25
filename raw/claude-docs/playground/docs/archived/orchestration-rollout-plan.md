# Plan: Orchestration Rollout — Four Variants

Date: 2026-04-12
Based on: `.claude/docs/in-progress/librarian-architecture/research-adk-orchestration.md`, `.claude/docs/in-progress/librarian-architecture/research-bedrock-kb.md`, codebase inspection

## Goal

Ship four orchestration variants behind a unified eval harness and triage router, so each can be A/B tested on the same golden corpus: (1) Librarian LangGraph with vocabulary alignment, (2) Google ADK + Bedrock KB, (3) Google ADK + custom RAG tools, (4) Google ADK + custom RAG + LangGraph hybrid.

## Approach

The four variants form a progression — each adds complexity and tests a different hypothesis. We implement them sequentially, gating each on eval results before building the next. The existing eval harness (`src/eval/`), triage router (`src/interfaces/api/triage.py`), and variant registry (`src/eval/variants.py`) are the integration points — every new variant plugs into these rather than building parallel infrastructure.

Key tradeoff: we add `google-adk` as a real dependency for variants 2–4, but isolate it behind optional extras (`[adk]`) so the core librarian path has zero new deps.

## Out of Scope

- Replacing LangGraph with ADK for the Librarian pipeline (research verdict: not worth it)
- Production deployment of ADK variants (these are eval/prototype variants)
- Multi-modal support (audio/video via ADK)
- ADK session persistence (InMemorySessionService is sufficient for eval)
- LangSmith integration (staying on Langfuse)
- Changes to the ingestion pipeline
- Streamlit UI changes (API-level only; UI follows once a variant wins)

---

## Phase 1: Librarian LangGraph — Vocabulary Alignment (Level 1 refactor)

**Hypothesis**: The existing Librarian pipeline is architecturally correct; vocabulary alignment makes it readable to ADK/CrewAI engineers without behavior change.

### Step 1.1: Rename SubGraph classes → Agent naming

**Files**:
- `src/orchestration/nodes/retrieval.py` (class `RetrievalSubgraph`, line 41)
- `src/orchestration/nodes/reranker.py` (class `RerankerSubgraph`, line 17)
- `src/orchestration/nodes/generation.py` (class `GenerationSubgraph`, line 22)
- `src/orchestration/history.py` (class `HistoryCondenser`)
- `src/orchestration/query_understanding.py` (re-export of `QueryAnalyzer`)
- `src/orchestration/graph.py` (all imports + usages, lines 15–18, 205–215)
- `src/librarian/factory.py` (imports + usages, lines 15–17, 205–215)

**What**: Rename classes:
- `RetrievalSubgraph` → `RetrieverAgent`
- `RerankerSubgraph` → `RerankerAgent`
- `GenerationSubgraph` → `GeneratorAgent`
- `HistoryCondenser` → `CondenserAgent`
- `QueryAnalyzer` stays (already well-named; aliased as `PlannerAgent` in `__init__`)

Each class gains `name: str` and `description: str` class attributes matching ADK's self-documenting convention.

**Snippet** (retrieval.py):
```python
# Before
class RetrievalSubgraph:
    """Stateless node: retrieve → deduplicate → grade."""

# After
class RetrieverAgent:
    """Stateless node: retrieve → deduplicate → grade.

    Expands the query using plan.query_variants (multi-query).
    Falls back to state["query"] / state["standalone_query"] when no plan.
    """
    name = "retriever"
    description = "Multi-query expansion, parallel embedding, hybrid search, dedup, and grading"
```

**Test**: `uv run pytest tests/librarian/ -v --tb=short` — all existing tests pass (pure rename).
**Done when**: All SubGraph references are gone; `grep -r SubGraph src/` returns zero hits; tests green.

### Step 1.2: Add `as_node()` method to each Agent class

**Files**:
- `src/orchestration/nodes/retrieval.py` (add method to `RetrieverAgent`)
- `src/orchestration/nodes/reranker.py` (add method to `RerankerAgent`)
- `src/orchestration/nodes/generation.py` (add methods to `GeneratorAgent`)
- `src/orchestration/history.py` (add method to `CondenserAgent`)
- `src/orchestration/graph.py` (replace `_make_*_node()` calls with `agent.as_node()`)

**What**: Each agent class gets an `as_node()` method that returns the LangGraph-compatible callable. This replaces the standalone `_make_*_node()` factory functions in `graph.py`, making the wiring self-contained per agent (ADK-idiomatic).

**Snippet** (retrieval.py):
```python
class RetrieverAgent:
    ...
    def as_node(self) -> Callable[[LibrarianState], Coroutine[Any, Any, dict[str, Any]]]:
        """Return a LangGraph-compatible async node function."""
        async def retrieve(state: LibrarianState) -> dict[str, Any]:
            result = await self.run(state)
            retry_count = int(state.get("retry_count") or 0)
            return {**result, "retry_count": retry_count}
        return retrieve
```

**Snippet** (graph.py `build_graph`):
```python
# Before
graph.add_node(_RETRIEVE, cast(Any, _make_retrieve_node(retrieval_sg)))

# After
graph.add_node(_RETRIEVE, cast(Any, retrieval_agent.as_node()))
```

**Test**: `uv run pytest tests/librarian/ -v --tb=short` — behavior identical.
**Done when**: All `_make_*_node()` functions are removed from `graph.py`; each agent wires itself via `as_node()`.

### Step 1.3: Extract instruction (system prompt) into agent classes

**Files**:
- `src/librarian/generation/prompts.py` (read system prompt constants)
- `src/orchestration/nodes/generation.py` (`GeneratorAgent.instruction` property)
- `src/orchestration/history.py` (`CondenserAgent.instruction` property)

**What**: Each agent that uses an LLM call gets an `instruction` class attribute or property containing its system prompt snippet. The prompt is still used by `build_prompt()` / condenser logic — but it's now *owned* by the agent class, not buried in `prompts.py`. `prompts.py` remains as the detailed template store; the agent surfaces the key instruction.

**Snippet**:
```python
class GeneratorAgent:
    name = "generator"
    description = "Builds prompt from context, calls LLM, extracts citations"
    instruction = (
        "You are a knowledgeable research assistant. Answer the user's question "
        "using ONLY the provided context passages. Cite sources by number."
    )
```

**Test**: `uv run pytest tests/librarian/ -v --tb=short`
**Done when**: Each agent class has `name`, `description`, and (where applicable) `instruction` properties.

### Step 1.4: Document graph topology in `graph.py`

**Files**: `src/orchestration/graph.py` (add docstring block at top, lines 1–35)

**What**: Add a topology diagram comment block matching ADK's `sub_agents=[...]` self-documenting style:

```python
"""Librarian RAG Graph — CRAG pipeline with conditional routing.

Topology:
    START → condense → analyze →┬→ retrieve → rerank → gate →┬→ generate → END
                                │                             │
                                └→ snippet_retrieve ──────────┘→ retrieve (CRAG)

Agents:
    CondenserAgent   — rewrites multi-turn queries to standalone form (Haiku)
    PlannerAgent     — intent classification + query expansion (no LLM)
    RetrieverAgent   — multi-query embedding + hybrid search + grading
    RerankerAgent    — cross-encoder or LLM-listwise reranking
    GeneratorAgent   — prompt assembly + LLM generation + citation extraction
    QualityGate      — confidence threshold check for CRAG retry decision

Equivalent ADK structure (for reference):
    SequentialAgent("librarian", sub_agents=[
        condenser, planner,
        LoopAgent("crag", sub_agents=[retriever, reranker, gate]),
        generator,
    ])
"""
```

**Test**: No behavior change — documentation only.
**Done when**: The topology is readable in 30 seconds by someone who has never seen the codebase.

---

## Phase 2: Google ADK + Bedrock KB

**Hypothesis**: ADK's `BaseAgent` can wrap Bedrock KB as a tool-less agent that uses Bedrock's managed RAG, giving us an ADK-compatible entry point with zero custom retrieval code.

### Step 2.1: Add `google-adk` as optional dependency

**Files**: `pyproject.toml`

**What**: Add `google-adk>=1.0.0` to a new `[project.optional-dependencies] adk` group. This keeps the core librarian install clean.

```toml
[project.optional-dependencies]
adk = [
    "google-adk>=1.0.0",
    "google-genai>=1.0.0",
]
```

**Test**: `uv sync --extra adk && uv run python -c "from google.adk.agents import BaseAgent; print('ok')"`
**Done when**: `uv pip list | grep google-adk` shows the package; no import errors.

### Step 2.2: Create `BedrockKBAgent` — ADK BaseAgent wrapping Bedrock

**Files**:
- `src/orchestration/adk/__init__.py` (new)
- `src/orchestration/adk/bedrock_agent.py` (new)

**What**: ADK `BaseAgent` subclass that delegates to the existing `BedrockKBClient`. No LLM tool-calling — Bedrock handles everything. The agent emits a single ADK `Event` with the response.

```python
from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types

from librarian.bedrock.client import BedrockKBClient
from librarian.config import LibrarySettings


class BedrockKBAgent(BaseAgent):
    """ADK agent wrapping AWS Bedrock Knowledge Bases.

    Bedrock handles embedding, retrieval, and generation internally.
    This agent extracts the user query from ADK session context,
    forwards it to Bedrock, and emits the response as an ADK event.
    """
    name: str = "bedrock_kb"
    description: str = "RAG via AWS Bedrock Knowledge Bases (managed)"

    def __init__(self, cfg: LibrarySettings, **kwargs: Any) -> None:
        super().__init__(name=self.name, description=self.description, **kwargs)
        self._client = BedrockKBClient(cfg)

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncIterator[Event]:
        query = ctx.session.events[-1].content.parts[0].text
        session_id = ctx.session.id

        resp = await self._client.aquery(query, session_id=session_id)

        yield Event(
            author=self.name,
            content=types.Content(
                parts=[types.Part(text=resp.response)]
            ),
        )
```

**Test**: Unit test with mocked `BedrockKBClient` — verify event emission.
`uv run pytest tests/orchestration/adk/test_bedrock_agent.py -v`
**Done when**: `BedrockKBAgent` can be instantiated and yields an event with the response text.

### Step 2.3: Wire into eval + triage

**Files**:
- `src/eval/variants.py` (add `ADK_BEDROCK` variant config)
- `src/eval/experiment.py` (add `_run_adk_bedrock_experiment()`)
- `src/interfaces/api/triage.py` (add `"adk_bedrock"` route)

**What**: Register the ADK + Bedrock agent as an eval variant so it can be benchmarked alongside existing variants. Add triage route for API access.

**Test**: `uv run pytest tests/eval/ -v --tb=short` + `uv run python -m eval.experiment run --variant adk-bedrock --dry-run`
**Done when**: `adk-bedrock` variant appears in `VARIANTS` registry and can be selected for eval runs.

---

## Phase 3: Google ADK + Custom RAG Tools

**Hypothesis**: An LLM-driven agent using tools for search and rerank (ADK's native pattern) may make better retrieval decisions for some query types than the fixed pipeline.

### Step 3.1: Create ADK tool functions for search + rerank

**Files**:
- `src/orchestration/adk/tools.py` (new)

**What**: Plain Python functions with type hints + docstrings that ADK auto-wraps as `FunctionTool`. These use the existing Librarian retrieval and reranking infrastructure (Chroma/OpenSearch retriever, cross-encoder reranker) but expose them as callable tools.

```python
from __future__ import annotations
from typing import Any
from google.adk.tools import ToolContext

async def search_knowledge_base(
    query: str,
    k: int = 10,
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Search the knowledge base for chunks relevant to the query.
    ...
    """

async def rerank_chunks(
    query: str,
    chunks: list[str],
    top_k: int = 3,
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Rerank text chunks by relevance using a cross-encoder model.
    ...
    """
```

Key design: tools receive retriever/embedder/reranker via module-level singletons initialized from `LibrarySettings` (same DI pattern as `factory.py` but for ADK's function-tool model). This lets the LLM call the same retrieval stack the Librarian uses.

**Test**: Unit test each tool function with mock retriever/embedder.
`uv run pytest tests/orchestration/adk/test_tools.py -v`
**Done when**: `search_knowledge_base` returns chunks; `rerank_chunks` returns reranked results.

### Step 3.2: Create `CustomRAGAgent` — ADK Agent with tools

**Files**:
- `src/orchestration/adk/custom_rag_agent.py` (new)

**What**: ADK `Agent` (not `BaseAgent`) with `tools=[search_knowledge_base, rerank_chunks]`. This is the research's "Option B" — the LLM decides when to search, when to rerank, when to retry. Uses Gemini as the orchestrating model.

```python
from google.adk.agents import Agent
from orchestration.adk.tools import search_knowledge_base, rerank_chunks

custom_rag_agent = Agent(
    model="gemini-2.5-flash",
    name="custom_rag",
    description="LLM-driven RAG: the model decides when and how to retrieve.",
    instruction="""You are a knowledgeable assistant with access to a curated knowledge base.
    When answering questions:
    1. Always search the knowledge base first using search_knowledge_base
    2. If results seem noisy, use rerank_chunks to surface the best matches
    3. If confidence_score from reranking is below 0.3, search again with different phrasing
    4. Base your answer strictly on retrieved passages; do not hallucinate
    5. If no relevant passages found, say so clearly
    """,
    tools=[search_knowledge_base, rerank_chunks],
)
```

**Test**: Integration test with mocked tools — verify agent calls tools and produces a response.
`uv run pytest tests/orchestration/adk/test_custom_rag_agent.py -v`
**Done when**: Agent can receive a query, call search tool, optionally rerank, and produce an answer.

### Step 3.3: Wire into eval + triage

**Files**:
- `src/eval/variants.py` (add `ADK_CUSTOM_RAG` variant)
- `src/eval/experiment.py` (add `_run_adk_custom_rag_experiment()`)
- `src/interfaces/api/triage.py` (add `"adk_custom_rag"` route)
- `src/interfaces/api/routes.py` (add handler)

**What**: Same integration pattern as Step 2.3. Register variant, add experiment runner, add triage route.

**Test**: `uv run python -m eval.experiment run --variant adk-custom-rag`
**Done when**: Variant benchmarkable against existing variants.

---

## Phase 4: Google ADK + Custom RAG + LangGraph Hybrid

**Hypothesis**: ADK's session management and multi-agent routing as the outer shell, with the full Librarian LangGraph pipeline as the inner retrieval engine, combines ADK's agent UX with Librarian's quality.

### Step 4.1: Create `LibrarianADKAgent` — ADK BaseAgent wrapping the compiled graph

**Files**:
- `src/orchestration/adk/librarian_agent.py` (new)

**What**: ADK `BaseAgent` subclass that wraps the compiled LangGraph `CompiledStateGraph`. Extracts query from ADK session, builds `LibrarianState`, calls `graph.ainvoke()`, emits response as ADK event. This is the research's "Option A".

```python
class LibrarianADKAgent(BaseAgent):
    """ADK wrapper around the compiled LangGraph LibrarianGraph.

    Exposes the full CRAG pipeline (condense → analyze → retrieve →
    rerank → gate → generate) as a single ADK-compatible agent.
    """
    name: str = "librarian_hybrid"
    description: str = "Full CRAG pipeline via LangGraph, wrapped as ADK agent"

    def __init__(self, cfg: LibrarySettings | None = None, **kwargs: Any) -> None:
        super().__init__(name=self.name, description=self.description, **kwargs)
        self._graph = create_librarian(cfg)

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncIterator[Event]:
        query = ctx.session.events[-1].content.parts[0].text
        state = {
            "query": query,
            "messages": _extract_messages(ctx.session.events),
            "conversation_id": ctx.session.id,
        }
        result = await self._graph.ainvoke(state)
        yield Event(
            author=self.name,
            content=types.Content(parts=[types.Part(text=result["response"])]),
        )
```

**Test**: Unit test with mocked graph — verify state mapping and event emission.
`uv run pytest tests/orchestration/adk/test_librarian_agent.py -v`
**Done when**: Agent wraps the full graph; state maps correctly; event contains response.

### Step 4.2: Create multi-agent coordinator (optional composition test)

**Files**:
- `src/orchestration/adk/coordinator.py` (new)

**What**: ADK `Agent` that routes between `LibrarianADKAgent` (knowledge queries) and `CustomRAGAgent` (exploratory queries) based on query type. This tests ADK's multi-agent composition — the coordinator decides which sub-agent handles the query.

```python
from google.adk.agents import Agent

coordinator = Agent(
    model="gemini-2.5-flash",
    name="coordinator",
    description="Routes queries to the best sub-agent",
    instruction="Route knowledge questions to librarian_hybrid, exploratory questions to custom_rag.",
    sub_agents=[librarian_hybrid, custom_rag],
)
```

**Test**: `uv run pytest tests/orchestration/adk/test_coordinator.py -v`
**Done when**: Coordinator routes to correct sub-agent based on query type.

### Step 4.3: Wire into eval + triage

**Files**:
- `src/eval/variants.py` (add `ADK_HYBRID` variant)
- `src/eval/experiment.py` (add `_run_adk_hybrid_experiment()`)
- `src/interfaces/api/triage.py` (add `"adk_hybrid"` route)

**Test**: `uv run python -m eval.experiment run --variant adk-hybrid`
**Done when**: All four new variants benchmarkable side-by-side.

---

## Test Plan

Each phase has its own test gate:

| Phase | Command | Pass criteria |
|-------|---------|--------------|
| P1 (vocab) | `uv run pytest tests/librarian/ tests/orchestration/ -v` | All existing tests green; zero `SubGraph` references in `src/` |
| P2 (ADK+Bedrock) | `uv run pytest tests/orchestration/adk/test_bedrock_agent.py -v` | Agent emits event with mocked response |
| P3 (ADK+CustomRAG) | `uv run pytest tests/orchestration/adk/test_custom_rag_agent.py -v` | Agent calls tools and produces answer |
| P4 (ADK+Hybrid) | `uv run pytest tests/orchestration/adk/test_librarian_agent.py -v` | Agent wraps graph and emits correct event |
| Cross-variant | `uv run python -m eval.experiment run --export results.json` | All configured variants produce results |

Live eval (requires credentials):
```bash
# Bedrock KB
BEDROCK_KNOWLEDGE_BASE_ID=xxx uv run python -m eval.experiment run --variant adk-bedrock

# Custom RAG (uses local ChromaDB + Gemini)
GEMINI_API_KEY=xxx uv run python -m eval.experiment run --variant adk-custom-rag

# Hybrid (uses local graph + ADK session)
GEMINI_API_KEY=xxx uv run python -m eval.experiment run --variant adk-hybrid
```

## Risks & Rollback

| Risk | Severity | Mitigation |
|------|----------|-----------|
| `google-adk` SDK instability (pre-1.0 vibes) | Medium | Isolated behind `[adk]` extra; core librarian unaffected |
| Gemini tool-calling unreliable for retrieval decisions | Medium | Phase 3 eval will quantify this; abandon if quality gap >10% vs Librarian |
| ADK+LangGraph hybrid loses event granularity | Low | Acceptable for eval; production would need streaming bridge |
| Test errors in `tests/researcher/` and `tests/presenter/` | Non-blocking | Pre-existing (collection errors from deleted modules); not in scope |
| Naming collision: existing `google_adk/` package vs ADK framework | Medium | Rename existing `src/librarian/google_adk/` → `src/librarian/google_vertex/` in P2 setup |

**Rollback**: Each phase is independently revertable. ADK code lives in `src/orchestration/adk/` — delete the directory to remove all ADK variants. Phase 1 (vocabulary) is the only change that touches existing code, and it's a pure rename (trivially reversible via git).

## Open Questions

1. **Gemini model access**: Do we have `gemini-2.5-flash` API access for tool-calling, or should we use `gemini-2.0-flash`? Affects Phases 3–4.
2. **google-adk version**: The SDK is new — should we pin to a specific version or use `>=1.0.0`? Need to check current release status.
3. **Rename `google_adk/` → `google_vertex/`**: The existing `src/librarian/google_adk/` is confusingly named (it's Vertex AI Search grounding, not the ADK framework). Should we rename it in Phase 2 to avoid confusion, or leave it?
4. **Eval corpus parity**: The ADK custom RAG agent (Phase 3) uses Gemini for generation. Should the eval compare answer quality (LLM judge) or only retrieval quality (hit_rate/MRR)? Answer quality comparison across Claude vs Gemini adds a confound.
5. **Session management value**: Phase 4 tests ADK's session management over the existing `conversation_id` pattern. What's the concrete test scenario — multi-turn accuracy? Cold-start fallback? This determines whether Phase 4 is worth the wrapper cost.

## Sequencing & Dependencies

```
Phase 1 (vocab alignment)         — no deps, do first
    ↓
Phase 2 (ADK + Bedrock KB)        — needs google-adk dep + Phase 1 naming
    ↓
Phase 3 (ADK + Custom RAG tools)  — needs Phase 2 infra (adk dep, test patterns)
    ↓
Phase 4 (ADK + LangGraph hybrid)  — needs Phase 1 (renamed agents) + Phase 2 infra
```

Phases 2 and 3 could theoretically run in parallel since they're independent agents, but sequential is safer for managing the `google-adk` dependency setup.

**Estimated effort**: Phase 1 ~2 days, Phase 2 ~2 days, Phase 3 ~2 days, Phase 4 ~2 days. Total ~8 days with review boundaries between phases.
