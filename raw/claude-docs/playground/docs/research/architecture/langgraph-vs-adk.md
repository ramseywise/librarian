# LangGraph vs Google ADK — Orchestration Mental Models

Date: 2026-04-12

---

## TL;DR

The two frameworks solve the same problem (multi-step LLM orchestration) with fundamentally
different mental models. ADK is **agent-centric and event-driven**; LangGraph is
**graph-centric and state-machine-based**. LangGraph is architecturally correct for a
deterministic retrieval pipeline, but its terminology is opaque to anyone coming from ADK,
LangChain agents, or CrewAI. A targeted vocabulary mapping — renaming `SubGraph` → `Agent`,
making `ToolContext`-style state access explicit, and surfacing callbacks as first-class
hooks — makes LangGraph-based code transferable without requiring a full framework swap.

---

## Side-by-side: mental models

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
| **Configuration** | `os.getenv()` ad-hoc | `pydantic Settings` (typed, centralized) |
| **Retry / loops** | `LoopAgent(max_iterations=N)` wraps agents | Conditional back-edge in DAG (`gate → retrieve` CRAG loop) |
| **Generator** | Gemini (default); any model via `model=` param | Claude (Anthropic SDK); Haiku for condenser |

---

## Primitives mapping

### Agent → node + subgraph

In ADK, an `Agent` is the fundamental unit — stateful within a session, with a name,
instruction, tools, and optional sub-agents.

In LangGraph, the equivalent is a **node wrapping a class** (sometimes called a subgraph):

```python
# ADK
researcher = Agent(
    name="researcher",
    model="gemini-2.5-flash",
    instruction="Retrieve relevant information for the query.",
    tools=[search_tool],
)

# LangGraph equivalent
class RetrieverAgent:
    async def run(self, state: PipelineState) -> dict[str, Any]:
        # same responsibilities: embed → search → grade
        ...

    def as_node(self) -> Callable:
        async def retrieve(state: PipelineState) -> dict[str, Any]:
            return await self.run(state)
        return retrieve
```

The class maps to ADK's `Agent` conceptually. The `as_node()` method is the wiring glue —
in ADK this wiring is implicit (`sub_agents=[researcher]`).

### SequentialAgent → linear edge chain

```python
# ADK: linear pipeline
pipeline = SequentialAgent(
    name="rag_pipeline",
    sub_agents=[condenser, analyzer, retriever, reranker, generator],
)

# LangGraph: equivalent explicit edge chain
graph.add_edge(START, "condense")
graph.add_edge("condense", "analyze")
graph.add_edge("analyze", "retrieve")
graph.add_edge("retrieve", "rerank")
graph.add_edge("rerank", "gate")
graph.add_edge("gate", "generate")
graph.add_edge("generate", END)
```

**ADK advantage**: Topology is self-documenting via the `sub_agents` list.
**LangGraph advantage**: Conditional edges and back-edges are expressible cleanly. ADK's
`LoopAgent` is a blunt instrument and can't model a conditional retry that skips already-run
nodes.

### LoopAgent → conditional back-edge (CRAG)

ADK's `LoopAgent` runs a sequence until the output contains `"DONE"` or `max_iterations` is
reached — a linear retry loop.

LangGraph CRAG is a **conditional back-edge**:

```
gate → [if fallback_requested and retry_count <= max] → retrieve
gate → [if confident or exhausted retries]            → generate
```

This is more surgical: the retry re-enters at `retrieve`, not at the top of the entire
pipeline. `LoopAgent` can't model this without restructuring the agent graph.

### ParallelAgent → asyncio.gather in a node

ADK's `ParallelAgent` runs sub-agents concurrently and aggregates results.
LangGraph equivalent:

```python
# In the retrieval node, parallel multi-query expansion:
tasks = [search(q) for q in query_variants]
results = await asyncio.gather(*tasks)
```

For retrieval, the LangGraph approach (gather in one node) is more efficient than spawning N
sub-agents. ADK's `ParallelAgent` overhead is real: each sub-agent gets a full LLM call with
context injection.

### Tool → there is no tool layer in a deterministic pipeline

ADK's `Tool` is a first-class concept: a callable the LLM can invoke, with automatic JSON
schema generation, argument validation, and `ToolContext` for state access.

A deterministic LangGraph retrieval pipeline has **no tool layer**. The subgraphs are
always-on pipeline stages. The LLM is confined to the `generate` node — it never decides "I
should call the retriever now."

This is intentional and correct for RAG: you don't want the LLM to decide whether to
retrieve — it should always retrieve. ADK's tool-call pattern is better for open-ended
agents where retrieval is one of many possible actions.

### Callback hooks → LangGraph has them, differently surfaced

```python
# ADK — declared on the agent
root_agent = Agent(
    before_model_callback=log_request,
    after_model_callback=log_response,
    before_tool_callback=validate_args,
    after_tool_callback=cache_result,
)

# LangGraph — injected globally at graph level
handler = build_langfuse_handler(session_id, trace_id)
config = {"callbacks": [handler]}
await graph.ainvoke(state, config=config)
```

LangGraph's callbacks fire on node entry/exit, LLM call, and tool call — same lifecycle
points as ADK. But they're invisible: you have to know to look at `tracing.py` and
understand LangGraph's callback protocol.

**ADK advantage**: Callbacks are declared on the agent — self-documenting, part of the
interface. **LangGraph advantage**: Callbacks are injected globally, so observability
doesn't leak into every node definition.

---

## Observability comparison

| Signal | ADK | LangGraph |
|---|---|---|
| **Per-agent trace** | `invocation_id` + `event.author` | LangSmith/Langfuse trace per `session_id` |
| **LLM call capture** | `before_model_callback` / `after_model_callback` | `CallbackHandler` |
| **Tool call capture** | `before_tool_callback` / `after_tool_callback` | No tool layer; nodes log structured events |
| **Confidence scores** | Not exposed | `confidence_score` in state; logged + gated |
| **Failure attribution** | Not exposed | `failure_reason`, structured logs |
| **OTel** | Not in ADK by default | `otel.py` (Phoenix or OTLP gRPC) |
| **Streaming events** | Yes: async generator of `Event` objects | Partial (generation node only) |

LangGraph is more observable for RAG-specific signals. ADK's callback model is cleaner for
general agent observability.

---

## State management comparison

### ADK: mutable dict via ToolContext

```python
def add_to_cart(item: str, qty: int, tool_context: ToolContext) -> dict:
    state = tool_context.state   # session-scoped mutable dict
    state["cart"][item] = qty
    return {"status": "ok"}
```

State is shared across all agents in a session. Any tool can read or write any key.
No schema. No type safety. Easy to write; hard to audit.

### LangGraph: typed TypedDict passed through nodes

```python
class PipelineState(TypedDict, total=False):
    query: str
    standalone_query: str
    intent: str
    retrieved_chunks: list[RetrievalResult]
    confidence_score: float
    response: str
```

Nodes return a partial dict; LangGraph merges it. The TypedDict schema is the contract.
Type-safe, auditable, testable.

**ADK advantage**: Less boilerplate; tools don't need to declare what they read/write.
**LangGraph advantage**: Schema is the documentation — you can read `PipelineState` and
know exactly what every node can see.

---

## Observability platforms

| | LangGraph | Google ADK |
|---|---|---|
| **LangSmith** | Native — trace explorer, playground replay, prompt hub all work | OTel only — loses LangChain-specific metadata |
| **Langfuse** | Works — `CallbackHandler`, trace view, score UI | Native `GoogleADKInstrumentor` (OTel-based); newer but well-supported |
| **Arize Phoenix** | OTel via `opentelemetry-instrumentation-langchain` | OTel — same path |

For tracing, LangGraph + LangSmith is the tightest integration. LangGraph + Langfuse is
excellent and framework-proven. ADK + Langfuse works via `GoogleADKInstrumentor` but has
less community testing.

---

## Three levels of ADK alignment for a LangGraph pipeline

### Level 1: Vocabulary alignment (low effort, high transferability)

Rename things to match ADK/CrewAI/common agent vocabulary without changing architecture:

| Current LangGraph | ADK-aligned name |
|---|---|
| `RetrievalSubgraph` | `RetrieverAgent` |
| `RerankerSubgraph` | `RerankerAgent` |
| `GenerationSubgraph` | `GeneratorAgent` |
| `HistoryCondenser` | `CondenserAgent` |
| `QueryAnalyzer` | `PlannerAgent` |
| `confidence_gate()` | `QualityGate` |
| `_make_retrieve_node()` | fold into `RetrieverAgent.as_node()` |

Each class gains `name`, `description`, and optionally an `instruction` property. The
LangGraph wiring stays; the vocabulary becomes transferable.

**Effort**: ~2 days. No behavior change. Ops risk: near-zero.

### Level 2: Callback hooks as first-class interface (medium effort)

Add ADK-style hooks to each agent class:

```python
class RetrieverAgent:
    before_run: Callable[[PipelineState], None] | None = None
    after_run: Callable[[PipelineState, dict], None] | None = None

    async def run(self, state: PipelineState) -> dict:
        if self.before_run:
            self.before_run(state)
        result = await self._retrieve(state)
        if self.after_run:
            self.after_run(state, result)
        return result
```

Makes observability wiring explicit on each agent rather than injected globally.

**Effort**: ~3 days. Enables per-agent metrics, circuit breakers, caching hooks.

### Level 3: Replace LangGraph with ADK (high effort, high risk)

**Blockers** — not worth it:
1. ADK is Gemini-native; Claude requires the `LiteLLM` adapter — not production-proven
2. `LoopAgent` can't model a surgical CRAG back-edge (it restarts the full sequence)
3. `TypedDict` schema becomes an untyped session dict — harder to debug
4. Langfuse callback integration is LangGraph-specific; needs replacement
5. Strategy dispatch (`chroma vs opensearch`, `cross-encoder vs llm-listwise`) has no ADK
   equivalent

**Verdict**: Level 3 gains only vocabulary — which Level 1 achieves for free in 2 days.

---

## When to use each framework

### Use ADK when

- The agent needs to **decide** which tools to call (open-ended assistant, not a pipeline)
- You're building on Google Cloud (Vertex AI Search, Vertex AI RAG Engine are ADK-native)
- You want to prototype fast: `Agent(tools=[my_func])` is 5 lines
- Multi-modal (audio, video) input is a requirement
- You need managed session storage without building it yourself

### Use LangGraph when

- Orchestration is **deterministic**: retrieve → rerank → generate, always
- You need a **typed state contract** across all pipeline stages
- You need **conditional retry loops** that re-enter mid-pipeline (CRAG)
- Failure attribution matters: retrieval miss vs. reranker failure vs. model hallucination
- Strategy dispatch is required at runtime
- You're using Claude (Anthropic is not a first-class ADK provider)

---

## ADK + LangGraph hybrid (worth prototyping)

You can wrap the entire compiled LangGraph graph as a single ADK `BaseAgent`:

```python
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from librarian.factory import create_librarian

class LibrarianAgent(BaseAgent):
    name = "librarian"
    description = "Retrieval-augmented QA over the knowledge corpus"

    def __init__(self) -> None:
        super().__init__(name=self.name, description=self.description)
        self._graph = create_librarian()

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncIterator[Event]:
        query = ctx.session.events[-1].content.parts[0].text
        state = {"query": query, "conversation_id": ctx.session.id}
        result = await self._graph.ainvoke(state)
        yield Event(author=self.name, content=types.Content(parts=[types.Part(text=result["response"])]))
```

This gains ADK's session management and multi-agent routing while keeping the typed state,
CRAG loop, and confidence gate. One ADK turn → one LangGraph invocation.
