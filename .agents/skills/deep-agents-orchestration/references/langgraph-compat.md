# ADK vs LangGraph Orchestration — Compatibility Reference

> Source: `.claude/docs/in-progress/librarian-architecture/research-adk-orchestration.md`
> Date: 2026-04-12. Context: Librarian RAG pipeline (LangGraph) vs Google ADK refactor decision.

---

## Mental model comparison

| Dimension | Google ADK | LangGraph |
|---|---|---|
| **Core unit** | `Agent` (stateful, has identity, can delegate) | `Node` (stateless function on shared state) |
| **Composition** | Recursive tree: `Agent(sub_agents=[...])` | DAG: `graph.add_edge(A, B)` |
| **Control flow** | Agent decides (LLM chooses tool/sub-agent) | Explicit: conditional edges + routing functions |
| **State** | Mutable dict (`session.state`) via `ToolContext` | Immutable `TypedDict` passed through; nodes return diffs |
| **Tools** | Python functions auto-wrapped as `FunctionTool` | No tool concept; subgraphs are the extension point |
| **Execution model** | `runner.run_async()` → async generator of events | `graph.ainvoke(state, config)` → final state dict |
| **Multi-turn** | `InMemorySessionService` accumulates history | `Annotated[list, add_messages]` reducer; condenser node rewrites query |
| **Observability** | Lifecycle callbacks: `before/after_model`, `before/after_tool` | Langfuse `CallbackHandler` injected via `config={"callbacks": [...]}` |
| **Retry / loops** | `LoopAgent(max_iterations=N)` wraps agents | Conditional back-edge in DAG (`gate → retrieve` CRAG loop) |

---

## Primitives mapping

### Agent → node + subgraph

```python
# ADK
researcher = Agent(
    name="researcher",
    model="gemini-2.5-flash",
    instruction="Retrieve relevant information.",
    tools=[search_tool],
)

# LangGraph equivalent
class RetrievalSubgraph:
    async def run(self, state: LibrarianState) -> dict[str, Any]: ...

def _make_retrieve_node(subgraph: RetrievalSubgraph) -> _AsyncNode:
    async def retrieve(state: LibrarianState) -> dict[str, Any]:
        return await subgraph.run(state)
    return retrieve
```

### SequentialAgent → linear edge chain

```python
# ADK
pipeline = SequentialAgent(sub_agents=[condenser, analyzer, retriever, reranker, generator])

# LangGraph
graph.add_edge(START, "condense")
graph.add_edge("condense", "analyze")
graph.add_edge("analyze", "retrieve")
graph.add_edge("retrieve", "rerank")
graph.add_edge("rerank", "generate")
graph.add_edge("generate", END)
```

ADK advantage: topology is self-documenting via `sub_agents` list.
LangGraph advantage: conditional and back-edges are expressible; `LoopAgent` can't model mid-pipeline retry.

### LoopAgent → conditional back-edge (CRAG)

ADK's `LoopAgent` is a linear retry loop — restarts from the top. LangGraph's CRAG back-edge
re-enters at `retrieve` only, skipping condense/analyze on retry. More surgical.

### ParallelAgent → asyncio.gather in one node

```python
# ADK
analysis_team = ParallelAgent(sub_agents=[v1_agent, v2_agent, v3_agent])

# LangGraph (more efficient — no per-agent LLM overhead)
results = await asyncio.gather(*[search(q) for q in query_variants])
```

ADK's `ParallelAgent` gives each variant a full LLM call with context injection.
For retrieval variants, the LangGraph gather-in-one-node approach is faster.

---

## Observability comparison

| Signal | ADK | LangGraph |
|---|---|---|
| **LLM call capture** | `before_model_callback` / `after_model_callback` | Langfuse `CallbackHandler` |
| **Tool call capture** | `before_tool_callback` / `after_tool_callback` | No tool layer (subgraphs log structured events) |
| **Tracing** | Langfuse via `GoogleADKInstrumentor` (OTel) | Langfuse natively via LangChain callback |
| **LangSmith** | OTel only — loses LangChain-specific metadata | First-class integration |
| **OTel** | Yes, built-in | Via `opentelemetry-instrumentation-langchain` |
| **Experiment tracking** | W&B Weave or build your own | LangSmith (native) or Langfuse (flexible) |

---

## State management comparison

### ADK: mutable dict via ToolContext

```python
def add_to_cart(item: str, qty: int, tool_context: ToolContext) -> dict:
    state = tool_context.state  # any tool can read/write any key — no schema
    state["cart"][item] = qty
    return {"status": "ok"}
```

### LangGraph: typed TypedDict

```python
class LibrarianState(TypedDict, total=False):
    query: str
    intent: str
    retrieved_chunks: list[RetrievalResult]
    confidence_score: float
    response: str
```

Nodes return partial dicts; LangGraph merges them. Schema is the documentation.

---

## When to use each

### Use ADK when
- The agent **decides** which tools to call (open-ended assistant, not a pipeline)
- Building on Google Cloud (Vertex AI Search, Vertex AI RAG Engine are ADK-native)
- You want fast prototyping: `Agent(tools=[my_func])` is 5 lines
- Multi-modal (audio, video) input required
- Managed session storage without building it yourself

### Use LangGraph when
- Orchestration is **deterministic**: retrieve → rerank → generate, always
- You need a **typed state contract** across all pipeline stages
- You need **conditional retry loops** that re-enter mid-pipeline (CRAG)
- Failure attribution matters (retrieval miss vs reranker failure vs hallucination)
- Strategy dispatch required (Chroma vs OpenSearch, cross-encoder vs LLM-listwise)
- You're using Claude (Anthropic is not a first-class ADK provider)

---

## ADK + LangGraph hybrid pattern

Wrap an existing LangGraph graph as an ADK `BaseAgent`:

```python
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

class LibrarianAgent(BaseAgent):
    name = "librarian"
    description = "Retrieval-augmented QA over the knowledge corpus"

    def __init__(self) -> None:
        super().__init__(name=self.name, description=self.description)
        self._graph = create_librarian()  # compiled LangGraph

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncIterator[Event]:
        query = ctx.session.events[-1].content.parts[0].text
        state = {"query": query, "messages": [...], "conversation_id": ctx.session.id}
        result = await self._graph.ainvoke(state)
        yield Event(author=self.name, content=types.Content(parts=[types.Part(text=result["response"])]))
```

**Gains**: ADK session management, event streaming, composable in a larger ADK multi-agent system.
**Limitation**: emits one event per turn, not streaming tokens.

---

## Vocabulary alignment (without framework swap)

Rename LangGraph classes to match ADK vocabulary — ~2 days, zero behavior change:

| Current | ADK-aligned |
|---|---|
| `RetrievalSubgraph` | `RetrieverAgent` |
| `RerankerSubgraph` | `RerankerAgent` |
| `GenerationSubgraph` | `GeneratorAgent` |
| `HistoryCondenser` | `CondenserAgent` |
| `LibrarianState` | `PipelineContext` |
| `_make_retrieve_node()` | `retriever.as_node()` |

Add `name`, `description`, and `as_node()` to each class. Makes the graph readable to
anyone coming from ADK, CrewAI, or LangChain agents.
