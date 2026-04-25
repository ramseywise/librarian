---
title: ADK vs LangGraph Comparison
tags: [adk, langgraph, comparison]
summary: Side-by-side mental model comparison of Google ADK and LangGraph — primitive mappings, when to use each, and the recommended vocabulary alignment approach.
updated: 2026-04-24
sources:
  - raw/playground-docs/adk-orchestration-research.md
  - raw/playground-docs/adk-samples-patterns-analysis.md
  - raw/playground-docs/orchestration-rollout-plan.md
---

# ADK vs LangGraph Comparison

## Core Mental Model

| Dimension | Google ADK | LangGraph (Librarian) |
|---|---|---|
| **Core unit** | `Agent` (stateful, has identity, can delegate) | `Node` (stateless function on shared state) |
| **Composition** | Recursive tree: `Agent(sub_agents=[...])` | DAG: `graph.add_edge(A, B)` |
| **Control flow** | Agent decides (LLM chooses tool/sub-agent) | Explicit: conditional edges + routing functions |
| **State** | Mutable dict (`session.state`) via `ToolContext` | Immutable `TypedDict` passed through; nodes return diffs |
| **Tools** | Python functions auto-wrapped as `FunctionTool` | No tool concept; subgraphs are the extension point |
| **Execution** | `runner.run_async()` → async generator of Events | `graph.ainvoke(state, config)` → final state dict |
| **Multi-turn** | `InMemorySessionService` accumulates history | `Annotated[list, add_messages]` reducer; condenser node rewrites query |
| **Retry / loops** | `LoopAgent(max_iterations=N)` wraps agents | Conditional back-edge in DAG (`gate → retrieve` CRAG loop) |
| **Generator** | Gemini (default) | Claude (Anthropic SDK via LangChain) |

## Primitive Mapping

### Agent → node + subgraph

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
    name = "retriever"
    description = "Multi-query embedding + hybrid search + grading"
    
    async def run(self, state: LibrarianState) -> dict:
        # embed → search → grade
        ...
    
    def as_node(self) -> Callable:
        async def retrieve(state): return await self.run(state)
        return retrieve
```

### LoopAgent → conditional back-edge (CRAG)

ADK's `LoopAgent` runs a sequence until output contains "DONE" or max iterations. Librarian's CRAG retry re-enters at `retrieve`, not the top of the pipeline — more surgical, can't be modelled as cleanly with `LoopAgent`.

### ParallelAgent → no direct equivalent (yet)

ADK's `ParallelAgent` runs sub-agents concurrently. Librarian has no parallel execution pattern currently. True parallelism: `asyncio.gather()` in one node or the [[LangGraph Advanced Patterns]] Send API.

**Note:** For retrieval variants, the LangGraph approach (gather in one node) is more efficient than spawning N sub-agents. ADK's `ParallelAgent` overhead is real — each sub-agent gets a full LLM call with context injection.

### Tool → no equivalent in Librarian

ADK's `Tool` is first-class: callable that agents invoke, with JSON schema generation, argument validation, and `ToolContext` for state access.

Librarian has **no tool layer** — the subgraphs are always-on pipeline stages. The LLM is confined to `generate` and `condense` nodes. It never decides "I should call the retriever now."

**The fundamental design difference:**
- **ADK:** LLM drives orchestration — agent decides when to retrieve, when to escalate, when to synthesise.
- **Librarian/LangGraph:** Code drives orchestration — graph topology is fixed, LLM generates the final answer.

For a RAG pipeline, Librarian's approach is correct: you don't want the LLM to decide whether to retrieve — it should always retrieve.

## Observability Comparison

| Signal | ADK | Librarian (LangGraph) |
|---|---|---|
| Per-agent trace | `invocation_id` + `event.author` | LangFuse trace per `session_id` |
| LLM call capture | `before/after_model_callback` | LangFuse `CallbackHandler` |
| Confidence scores | Not exposed | `confidence_score` in state, logged + gated |
| Failure attribution | Not exposed | `failure_reason`, `FailureClusterer`, structured logs |
| OTel | Not in ADK by default | `librarian/otel.py` (Phoenix or OTLP gRPC) |

**Librarian is more observable than ADK** for RAG-specific signals. ADK's callback model is cleaner for general agent observability.

## When to Use Each

### Use ADK when

- The agent needs to **decide** which tools to call (open-ended assistant, not a pipeline)
- Building on Google Cloud (Vertex AI Search, Vertex AI RAG Engine are ADK-native)
- Want to prototype fast: `Agent(tools=[my_func])` is 5 lines
- Multi-modal (audio, video) input is a requirement — ADK has built-in multimodal support
- Managed session storage needed without building it yourself

### Use LangGraph when

- Orchestration is **deterministic**: retrieve → rerank → generate, always
- Need a **typed state contract** across all pipeline stages (auditable, testable)
- Need **conditional retry loops** that re-enter mid-pipeline (CRAG)
- Failure attribution matters: retrieval miss vs. reranker failure vs. model hallucination
- Strategy dispatch required: different backends configured at runtime
- Using Claude (Anthropic is not a first-class ADK provider)
- Need the LangFuse / OTel observability stack

## Three Levels of ADK Refactoring

### Level 1: Vocabulary Alignment (~2 days, recommended)

Rename classes to `*Agent` naming, add `name`/`description`/`instruction` properties, expose `as_node()`. No behavior change. Makes codebase readable to anyone who has seen ADK, CrewAI, or LangChain agent code. **Trivially reversible.**

### Level 2: Callback Hooks (~3 days)

Add ADK-style `before_run`/`after_run` hooks to each agent class. Makes observability wiring explicit on each agent rather than injected globally. Compatible with existing LangFuse handler.

### Level 3: Replace LangGraph with ADK (not recommended)

Blockers: ADK is Gemini-native (Claude requires adapters), `LoopAgent` can't model Librarian's surgical CRAG back-edge, typed `LibrarianState` becomes untyped session dict, LangFuse wiring is LangGraph-specific. Migration cost high; gain is vocabulary only — which Level 1 achieves for free.

## ADK + LangGraph Hybrid Option

Wrap the compiled LangGraph graph as a single ADK `BaseAgent`:

```python
class LibrarianADKAgent(BaseAgent):
    def __init__(self):
        self._graph = create_librarian()  # LangGraph compiled graph
    
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncIterator[Event]:
        query = ctx.session.events[-1].content.parts[0].text
        result = await self._graph.ainvoke({"query": query, ...})
        yield Event(author=self.name, content=types.Content(parts=[types.Part(text=result["response"])]))
```

**What you gain:** ADK session management, event streaming, multi-agent routing as outer shell. **What you keep:** typed LibrarianState, CRAG loop, confidence gate, LangFuse tracing. **Effort:** ~1–2 days.

## Skill-Loading Strategies (ADK)

Three strategies for loading domain knowledge into agents — see [[ADK Context Engineering]].

## See Also
- [[ADK vs LangGraph Decision]]
- [[LangGraph CRAG Pipeline]]
- [[ADK Context Engineering]]
- [[Librarian RAG Architecture]]
- [[VA Agent Project]]
