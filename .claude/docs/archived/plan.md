# Plan: Orchestrator Runtime Refactor
Date: 2026-04-17
Based on: direct codebase inspection + framework comparison (Google ADK vs LangGraph)

## Goal
Restructure `app/graph/` into a runtime-agnostic orchestrator with a shared protocol layer, a clean LangGraph implementation, and stubs for Google ADK — so retrieval, memory, and protocol concerns (MCP, A2A) sit in shared infrastructure usable by either backend.

## Approach
Define a thin `AgentRuntime` Protocol (typed input/output contract only — no shared base class) and move the current LangGraph implementation under `app/orchestrator/langgraph/`. Shared concerns — retrieval tools, memory, MCP toolset, A2A card — go in `app/orchestrator/shared/`. An `app/orchestrator/adk/` stub is created with the same contract so ADK can be wired in later without touching shared code. At the same time, the current `app/graph/` cruft (shims, duplicate node files, empty chains/) is deleted.

Key tradeoff: two separate runtime implementations to maintain, but they share all the hard parts (retrieval, memory, schemas) and the interface forces each runtime to speak the same I/O contract.

## Out of Scope
- Implementing the ADK runtime (stub only — no working ADK agent)
- Switching the LangGraph graph topology (HITL gates, task path remain unchanged)
- LangGraph `Store` API / cross-thread episodic memory (flag for follow-on)
- `trim_messages` history compaction (flag for follow-on)
- Deploying MCP server (define the toolset definition only)
- Ingestion pipeline, preprocessing, embedding layer — untouched

---

## Steps

### Step 1: Delete dead code and shims ✓ DONE — 2026-04-17
**Files**:
- `app/graph/chains/__init__.py` — delete entire file
- `app/graph/state.py` — delete (shim → `app/graph/schemas/state.py`)
- `app/graph/policy.py` — delete (shim → `app/graph/policies/`)
- `app/graph/confidence_routing.py` — delete (shim)
- `app/graph/context_builder.py` — delete (shim)
- `app/graph/hybrid_policy.py` — delete (shim)
- `app/graph/nodes/qa_nodes.py` — delete (barrel; per-node files are canonical)
- `app/graph/nodes/retrieval_nodes.py` — delete (barrel; `retriever.py`/`reranker.py` are canonical)

**What**: Remove files that only re-export from elsewhere. Update any external imports that still reference these paths.

**Check imports first**:
```bash
grep -r "from app.graph.state import\|from app.graph.policy import\|from app.graph.nodes.qa_nodes import\|from app.graph.nodes.retrieval_nodes import\|from app.graph.chains" app/ tests/ --include="*.py" -l
```

**Before** (`app/graph/nodes/__init__.py` committed version):
```python
from app.graph.nodes.qa_nodes import answer_node, ...
from app.graph.nodes.retrieval_nodes import reranker_node, retriever_node
```
**After** (working-tree version already correct):
```python
from app.graph.nodes.answer import answer_node
from app.graph.nodes.retriever import retriever_node
from app.graph.nodes.reranker import reranker_node
...
```

**Test**: `uv run pytest --tb=no -q` → 150 passed (no regression)
**Done when**: `grep -r "qa_nodes\|retrieval_nodes\|from app.graph.state\|from app.graph.policy\b" app/ tests/` returns nothing

---

### Step 2: Create orchestrator package skeleton ✓ DONE — 2026-04-17
**Files**: create new directories/`__init__.py` files
```
app/orchestrator/__init__.py
app/orchestrator/protocol.py         ← AgentRuntime Protocol
app/orchestrator/langgraph/__init__.py
app/orchestrator/adk/__init__.py     ← stub only
app/orchestrator/shared/__init__.py
app/orchestrator/shared/memory/__init__.py
app/orchestrator/shared/protocols/__init__.py   (MCP / A2A definitions)
app/orchestrator/shared/tools/__init__.py       (re-export RetrieverTool)
```

**What**: Define the `AgentRuntime` Protocol in `protocol.py`:
```python
# app/orchestrator/protocol.py
from __future__ import annotations
from typing import AsyncIterator, Protocol, runtime_checkable
from app.orchestrator.shared.schemas import AgentInput, AgentOutput, StreamEvent

@runtime_checkable
class AgentRuntime(Protocol):
    async def run(self, input: AgentInput) -> AgentOutput: ...
    async def stream(self, input: AgentInput) -> AsyncIterator[StreamEvent]: ...
    async def resume(self, thread_id: str, value: object) -> AgentOutput: ...
```

**What**: Define shared I/O schemas:
```python
# app/orchestrator/shared/schemas.py
from pydantic import BaseModel
from typing import Any, Literal

class AgentInput(BaseModel):
    query: str
    thread_id: str
    locale: str | None = None
    market: str | None = None
    metadata: dict[str, Any] = {}

class AgentOutput(BaseModel):
    answer: str
    citations: list[dict] = []
    mode: str | None = None
    latency_ms: dict[str, float] = {}
    escalated: bool = False

class StreamEvent(BaseModel):
    kind: Literal["node_start", "node_end", "interrupt", "done"]
    node: str | None = None
    data: dict[str, Any] = {}
```

**Test**: `python -c "from app.orchestrator.protocol import AgentRuntime; print('ok')"`
**Done when**: package imports without error; no production logic yet

---

### Step 3: Move LangGraph implementation under orchestrator ✓ DONE — 2026-04-17
**Files**:
- Move `app/graph/` → `app/orchestrator/langgraph/`
- Keep `app/graph/` as a thin backward-compat shim package (re-export `poc_graph`) until `app/main.py` and tests are updated

**What**: The LangGraph graph wiring, nodes, schemas, policies, routing, prompts all move intact. No logic changes in this step.

```
app/orchestrator/langgraph/
  graph.py          ← was app/graph/graph.py
  routing.py
  prompts.py
  runner.py
  utils.py
  nodes/
    answer.py, planner.py, escalation.py
    qa_policy_rerank.py, qa_policy_retrieval.py
    qa_rerank_gate.py, qa_retrieval_gate.py
    retriever.py, reranker.py
    post_answer_node.py, task_nodes.py
    __init__.py
  schemas/
    state.py, contract.py, context_builder.py
    __init__.py
  policies/
    confidence_routing.py, hybrid_policy.py
    __init__.py
```

**Backward-compat shim** (keep until Step 5):
```python
# app/graph/__init__.py
from app.orchestrator.langgraph.graph import poc_graph  # noqa: F401
```

**Test**: `uv run pytest --tb=no -q` → 150 passed
**Done when**: all tests pass with new import paths; `app/graph/graph.py` no longer exists

---

### Step 4: Wire LangGraph runtime to AgentRuntime protocol ✓ DONE — 2026-04-17
**Files**: `app/orchestrator/langgraph/runtime.py` (new)

**What**: Implement `AgentRuntime` for LangGraph — translates `AgentInput` → `GraphState` → `AgentOutput`:
```python
# app/orchestrator/langgraph/runtime.py
from app.orchestrator.protocol import AgentRuntime  # Protocol, not base class
from app.orchestrator.shared.schemas import AgentInput, AgentOutput, StreamEvent
from app.orchestrator.langgraph.graph import poc_graph
from app.orchestrator.langgraph.schemas.state import GraphState
from langchain_core.messages import HumanMessage

class LangGraphRuntime:
    """Implements AgentRuntime over the LangGraph poc_graph."""

    async def run(self, input: AgentInput) -> AgentOutput:
        config = {"configurable": {"thread_id": input.thread_id}}
        state = GraphState(
            query=input.query,
            messages=[HumanMessage(content=input.query)],
            locale=input.locale,
            market=input.market,
        )
        result = poc_graph.invoke(state, config=config)
        return AgentOutput(
            answer=_extract_answer(result),
            citations=_extract_citations(result),
            mode=result.get("mode"),
            latency_ms=result.get("latency_ms", {}),
            escalated=result.get("qa_outcome") == "escalate",
        )

    async def stream(self, input: AgentInput):
        ...  # astream_events wrapper

    async def resume(self, thread_id: str, value: object) -> AgentOutput:
        ...  # Command(resume=value) wrapper

assert isinstance(LangGraphRuntime(), AgentRuntime)  # structural check at import
```

**Test**: `uv run pytest tests/test_langgraph_runtime.py -v` (new test, see Step 7)
**Done when**: `isinstance(LangGraphRuntime(), AgentRuntime)` is `True`; `run()` returns a valid `AgentOutput`

---

### Step 5: Stub ADK runtime ✓ DONE — 2026-04-17
**Files**: `app/orchestrator/adk/runtime.py` (new), `app/orchestrator/adk/agent.py` (new)

**What**: Skeleton that satisfies the `AgentRuntime` protocol — no working ADK agent yet. Documents what ADK would replace:
```python
# app/orchestrator/adk/runtime.py
from app.orchestrator.shared.schemas import AgentInput, AgentOutput, StreamEvent

class ADKRuntime:
    """Google ADK implementation — stub.

    ADK replaces:
    - LangGraph StateGraph → google.adk.agents.LlmAgent + SequentialAgent
    - MemorySaver → DatabaseSessionService (short-term) + MemoryService (long-term)
    - langchain-mcp-adapters → MCPToolset (native)
    - Manual A2A → AgentCard endpoint (native)
    """

    async def run(self, input: AgentInput) -> AgentOutput:
        raise NotImplementedError("ADK runtime not yet implemented")

    async def stream(self, input: AgentInput):
        raise NotImplementedError

    async def resume(self, thread_id: str, value: object) -> AgentOutput:
        raise NotImplementedError
```

**Test**: `python -c "from app.orchestrator.adk.runtime import ADKRuntime; print('ok')"`
**Done when**: imports without error; `NotImplementedError` on call is expected and correct

---

### Step 6: Shared protocols stubs (MCP + A2A) ✓ DONE — 2026-04-17
**Files**:
- `app/orchestrator/shared/protocols/mcp.py` — MCP toolset definition
- `app/orchestrator/shared/protocols/a2a.py` — A2A AgentCard definition

**What**: Define the shape of MCP and A2A integration points. No running servers — just the typed definitions so both runtimes know what to wire:

```python
# app/orchestrator/shared/protocols/mcp.py
"""MCP toolset definition for the knowledge base retriever.

LangGraph: wire via langchain-mcp-adapters (MCPToolset adapter).
ADK: wire via google.adk.tools.mcp_tool.MCPToolset (native, 3 lines).
"""
from app.rag.tools.retriever_tool import RetrieverTool

MCP_TOOLS = [RetrieverTool]  # extend list as new tools are added
```

```python
# app/orchestrator/shared/protocols/a2a.py
"""A2A AgentCard definition.

LangGraph: expose via custom FastAPI endpoint (manual).
ADK: native — agents expose AgentCard automatically.
"""
from pydantic import BaseModel

class AgentCapability(BaseModel):
    name: str
    description: str

AGENT_CARD = {
    "name": "support-rag-agent",
    "description": "Customer support RAG agent with retrieval, reranking, and HITL escalation",
    "capabilities": [
        AgentCapability(name="search_knowledge_base", description="Hybrid retrieval over product docs"),
        AgentCapability(name="task_execution", description="Clarify and plan support tasks"),
    ],
    "protocols": ["a2a/1.0"],
}
```

**Test**: `python -c "from app.orchestrator.shared.protocols.mcp import MCP_TOOLS; print(len(MCP_TOOLS))"`
**Done when**: both files import cleanly; `MCP_TOOLS` contains `RetrieverTool`

---

### Step 7: Update entry points and tests ✓ DONE — 2026-04-17
**Files**:
- `app/main.py` — update `poc_graph` import to `app.orchestrator.langgraph.graph`
- `tests/` — update any direct `app.graph.*` imports
- `app/graph/__init__.py` — remove backward-compat shim (final)
- New: `tests/test_langgraph_runtime.py` — smoke test for `LangGraphRuntime.run()`

**What**: Remove the last backward-compat shim. All imports now use `app.orchestrator.*`:
```python
# Before
from app.graph.graph import poc_graph
# After
from app.orchestrator.langgraph.graph import poc_graph
```

**Test**: `uv run pytest --tb=no -q` → 150+ passed (same baseline + new runtime test)
**Done when**: no `app.graph` references remain except in migration notes; all tests green

---

## Test Plan
- **Step 1**: `uv run pytest --tb=no -q` (regression — must stay 150 passed)
- **Step 3**: same, after move
- **Step 4**: new `tests/test_langgraph_runtime.py::test_run_qa_path` (mock LLM)
- **Step 7**: full suite baseline

No new integration tests required — protocol conformance is verified structurally via `isinstance(runtime, AgentRuntime)` checks.

---

## Risks & Rollback
| Risk | Mitigation |
|---|---|
| Import breakage during move (Step 3) | Backward-compat shim on `app/graph/__init__.py` buys time; delete only in Step 7 |
| `GraphState` field name conflicts with `AgentInput` | `AgentInput` is the external boundary only; `GraphState` stays internal |
| ADK stub creates false confidence | Stub raises `NotImplementedError` explicitly — can't accidentally use it |
| Losing test coverage on deleted shim files | All tests target concrete nodes/policies, not shims — no coverage loss |

Rollback: all steps are additive until Step 7. Revert Step 7 to restore `app/graph/` shim.

---

## Open Questions
1. **LangGraph Store** — the `session_memory` dict on `GraphState` only survives within a thread. Should we add `Store`-backed episodic memory in a follow-on? (Likely yes once ADK comparison is live.)
2. **History compaction** — `messages` grows unbounded. `trim_messages` node between `answer` → `END` is low-effort; flag for next cycle.
3. **Dual HITL gates** — `qa_retrieval_gate` + `qa_rerank_gate` may be over-complex. Keep for now; revisit once ADK runtime is live and we can compare graph topologies.
4. **MCP server transport** — stdio vs SSE vs HTTP. Decision deferred; `mcp.py` stub is transport-agnostic.
5. **`post_answer_evaluator_node`** — wired in `graph.py` but RAG_POST_ANSWER_EVALUATOR defaults false. Keep; it moves with the LangGraph implementation unchanged.
