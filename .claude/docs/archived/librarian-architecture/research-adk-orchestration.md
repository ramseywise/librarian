# Research: Librarian LangGraph vs Google ADK Orchestration

Date: 2026-04-12
Context: Decision support — should the Librarian's orchestration be refactored toward ADK-style
primitives to gain cross-framework language transferability?

---

## TL;DR

The two frameworks solve the same problem (multi-step LLM orchestration) with fundamentally
different mental models. ADK is **agent-centric and event-driven**; LangGraph is
**graph-centric and state-machine-based**. Librarian's LangGraph implementation is
architecturally correct for a retrieval pipeline, but its terminology is opaque to anyone
coming from ADK, LangChain agents, or CrewAI. A targeted vocabulary mapping — renaming
`SubGraph` → `Agent`, making `ToolContext`-style state access explicit, and surfacing
callbacks as first-class hooks — would make the Librarian transferable without requiring a
full framework swap.

---

## Side-by-side: mental models

| Dimension | Google ADK | Librarian (LangGraph) |
|---|---|---|
| **Core unit** | `Agent` (stateful, has identity, can delegate) | `Node` (stateless function on shared state) |
| **Composition** | Recursive tree: `Agent(sub_agents=[...])` | DAG: `graph.add_edge(A, B)` |
| **Control flow** | Agent decides (LLM chooses tool/sub-agent) | Explicit: conditional edges + routing functions |
| **State** | Mutable dict (`session.state`) via `ToolContext` | Immutable `TypedDict` passed through; nodes return diffs |
| **Tools** | Python functions auto-wrapped as `FunctionTool` | No tool concept; subgraphs are the extension point |
| **Execution model** | `runner.run_async()` → async generator of events | `graph.ainvoke(state, config)` → final state dict |
| **Multi-turn** | `InMemorySessionService` accumulates history | `Annotated[list, add_messages]` reducer; condenser node rewrites query |
| **Observability** | Lifecycle callbacks: `before/after_model`, `before/after_tool` | Langfuse `CallbackHandler` injected via `config={"callbacks": [...]}` |
| **Configuration** | `os.getenv()` ad-hoc | `pydantic LibrarySettings` (typed, centralized) |
| **Retry / loops** | `LoopAgent(max_iterations=N)` wraps agents | Conditional back-edge in DAG (`gate → retrieve` CRAG loop) |
| **Generator** | Gemini (default); any model via `model=` param | Claude (Anthropic SDK); Haiku for condenser |

---

## Primitives mapping

Understanding how ADK's vocabulary maps to Librarian's is the key to deciding what, if
anything, to refactor.

### Agent → node + subgraph

In ADK, an `Agent` is the fundamental unit. It has a name, an instruction (system prompt),
a set of tools, and optionally sub-agents. It is stateful within a session.

In Librarian, the equivalent is a **node wrapping a subgraph**:

```python
# ADK
researcher = Agent(
    name="researcher",
    model="gemini-2.5-flash",
    instruction="Retrieve relevant information for the query.",
    tools=[search_tool],
)

# Librarian equivalent
class RetrievalSubgraph:
    async def run(self, state: LibrarianState) -> dict[str, Any]:
        # same responsibilities: embed → search → grade
        ...

def _make_retrieve_node(subgraph: RetrievalSubgraph) -> _AsyncNode:
    async def retrieve(state: LibrarianState) -> dict[str, Any]:
        return await subgraph.run(state)
    return retrieve
```

The `SubGraph` class maps to ADK's `Agent` conceptually. The node-maker function is the
wiring glue — in ADK this wiring is implicit (`sub_agents=[researcher]`).

**Gap**: Librarian's subgraph classes don't have names, descriptions, or explicit
"instructions" (system prompts are buried in `generation/prompts.py`). This makes the
orchestration hard to read holistically.

### SequentialAgent → linear edge chain

```python
# ADK: linear pipeline
pipeline = SequentialAgent(
    name="rag_pipeline",
    sub_agents=[condenser, analyzer, retriever, reranker, generator],
)

# Librarian: equivalent explicit edge chain
graph.add_edge(START, "condense")
graph.add_edge("condense", "analyze")
graph.add_edge("analyze", "retrieve")   # (simplified; actual is conditional)
graph.add_edge("retrieve", "rerank")
graph.add_edge("rerank", "gate")
graph.add_edge("gate", "generate")
graph.add_edge("generate", END)
```

In the default (no CRAG) path, Librarian is a `SequentialAgent` with six stages. The
graph topology makes this explicit and auditable; ADK's `SequentialAgent` hides it behind a
container.

**ADK advantage**: Topology is self-documenting via `sub_agents` list. Anyone can read the
agent tree and understand the pipeline in 30 seconds.

**LangGraph advantage**: Conditional edges and back-edges (`gate → retrieve` for CRAG) are
expressible cleanly; `LoopAgent` in ADK is a blunt instrument (single agent loops) and
can't model a conditional retry that skips already-run nodes.

### LoopAgent → conditional back-edge (CRAG)

ADK's `LoopAgent` runs a sequence of agents until the output contains `"DONE"` or
`max_iterations` is reached. It's a linear retry loop.

Librarian's CRAG retry is a **conditional back-edge**:

```
gate → [if fallback_requested and retry_count <= max] → retrieve
gate → [if confident or exhausted retries] → generate
```

This is more surgical: the retry re-enters at `retrieve`, not at the top of the entire
pipeline. `LoopAgent` can't model this without restructuring the agent graph.

**ADK equivalent would be**: A `LoopAgent` wrapping `retriever + reranker + gate`, with the
gate tool setting a session-state flag. More verbose and fragile.

### ParallelAgent → no direct equivalent in Librarian

ADK's `ParallelAgent` runs sub-agents concurrently and aggregates results.

Librarian has no parallel execution pattern currently. Multi-query expansion is done
sequentially (async but in a loop). A true `ParallelAgent` pattern would be:

```python
# ADK
analysis_team = ParallelAgent(
    name="multi_query_retriever",
    sub_agents=[query_variant_1_agent, query_variant_2_agent, query_variant_3_agent],
)

# Librarian equivalent (not yet implemented)
tasks = [search(q) for q in query_variants]
results = await asyncio.gather(*tasks)
```

Librarian does `asyncio.gather` in the retrieval subgraph for embedding, but the
**parallel-agent framing** — where each variant is an autonomous agent with its own
context — is not how it's modelled.

**Note**: For retrieval variants, the LangGraph approach (gather in one node) is more
efficient than spawning N sub-agents. ADK's `ParallelAgent` overhead is real: each
sub-agent gets a full LLM call with context injection.

### Tool → there is no tool layer in Librarian

ADK's `Tool` is a first-class concept: a callable that agents can invoke, with automatic
JSON schema generation, argument validation, and `ToolContext` for state access.

Librarian has **no tool layer**. The subgraphs are not callable by the LLM; they are
always-on pipeline stages. The LLM in Librarian is confined to the `generate` node and the
`condense` node (Haiku). It never decides "I should call the retriever now."

This is intentional: Librarian is a **deterministic retrieval pipeline** with an LLM at
the generation stage. ADK is an **LLM-orchestrated agent** where the model decides which
tools to invoke.

**The fundamental design difference**:
- **ADK**: LLM drives orchestration. Agent decides when to retrieve, when to escalate,
  when to synthesise. Retrieval is a tool the LLM calls.
- **Librarian**: Code drives orchestration. Graph topology is fixed. LLM generates the
  final answer. Retrieval is mandatory and pre-wired.

For a RAG pipeline, Librarian's approach is correct: you don't want the LLM to decide
whether to retrieve — it should always retrieve. ADK's tool-call pattern is better for
open-ended agents where retrieval is one of many possible actions.

### Callback hooks → Librarian has them, just differently surfaced

ADK:
```python
root_agent = Agent(
    before_model_callback=log_request,
    after_model_callback=log_response,
    before_tool_callback=validate_args,
    after_tool_callback=cache_result,
)
```

Librarian:
```python
# Langfuse handler injected into LangGraph config
handler = build_langfuse_handler(session_id, trace_id)
config = make_runnable_config(handler)
await graph.ainvoke(state, config=config)
```

LangGraph's `callbacks` in `config` fire on node entry/exit, LLM call, tool call — same
lifecycle points as ADK. But they're invisible: you have to know to look at `tracing.py`
and understand LangGraph's callback protocol.

**ADK advantage**: Callbacks are declared on the agent — they're part of its interface and
self-documenting. Librarian's callbacks are injected globally at the graph level and don't
appear in any node definition.

---

## Observability comparison

| Signal | ADK | Librarian |
|---|---|---|
| **Per-agent trace** | `invocation_id` + `event.author` | Langfuse trace per `session_id` |
| **LLM call capture** | `before_model_callback` / `after_model_callback` | Langfuse `CallbackHandler` (covers LangChain LLM calls) |
| **Tool call capture** | `before_tool_callback` / `after_tool_callback` | No tool layer; subgraph logs structured events |
| **Confidence scores** | Not exposed | `confidence_score` in state; logged + gated |
| **Failure attribution** | Not exposed | `failure_reason`, `FailureClusterer`, structured logs |
| **OTel** | Not in ADK by default | `librarian/otel.py` (Phoenix or OTLP gRPC) |
| **Streaming events** | Yes: async generator of `Event` objects | Partial (generation node only) |

Librarian is more observable than ADK out of the box for RAG-specific signals.
ADK's callback model is cleaner for general agent observability.

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

### Librarian: typed TypedDict passed through nodes

```python
class LibrarianState(TypedDict, total=False):
    query: str
    standalone_query: str
    intent: str
    retrieved_chunks: list[RetrievalResult]
    confidence_score: float
    response: str
    ...
```

Nodes return a partial dict; LangGraph merges it. No node can read state it hasn't
been given — the TypedDict schema is the contract. Type-safe, auditable, testable.

**ADK advantage**: Less boilerplate; tools don't need to declare what they read/write.
**Librarian advantage**: Schema is the documentation. You can read `LibrarianState` and
know exactly what every node can see.

---

## What refactoring toward ADK framing would mean in practice

There are three levels of refactoring possible. They're not mutually exclusive.

### Level 1: Vocabulary alignment (low effort, high transferability)

Rename things to match ADK/CrewAI/common agent vocabulary without changing architecture:

| Current | ADK-aligned name |
|---|---|
| `RetrievalSubgraph` | `RetrieverAgent` |
| `RerankerSubgraph` | `RerankerAgent` |
| `GenerationSubgraph` | `GeneratorAgent` |
| `HistoryCondenser` | `CondenserAgent` |
| `QueryAnalyzer` | `PlannerAgent` |
| `LibrarianState` | `PipelineContext` |
| `confidence_gate()` | `QualityGate` |
| `_make_retrieve_node()` | (fold into `RetrieverAgent.as_node()`) |

Each "agent" class would gain a `name`, `description`, and optionally an `instruction`
property — matching ADK's self-documenting interface. The LangGraph wiring stays; the
vocabulary becomes transferable.

**Effort**: ~2 days. No behavior change. Tests pass. Ops risk: near-zero.

### Level 2: Callback hooks as first-class interface (medium effort)

Add ADK-style callback hooks to each agent class:

```python
class RetrieverAgent:
    before_run: Callable[[LibrarianState], None] | None = None
    after_run: Callable[[LibrarianState, dict], None] | None = None

    async def run(self, state: LibrarianState) -> dict:
        if self.before_run:
            self.before_run(state)
        result = await self._retrieve(state)
        if self.after_run:
            self.after_run(state, result)
        return result
```

This makes observability wiring explicit on each agent rather than injected globally.
Compatible with the existing Langfuse handler (keep both; hooks fire in addition).

**Effort**: ~3 days. Minor behavior change (hook firing order). Enables: per-agent metrics,
circuit breakers, caching hooks without touching the graph.

### Level 3: Replace LangGraph with ADK (high effort, high risk)

Port the Librarian to run inside ADK's `Runner`:
- `SequentialAgent([condenser, analyzer, retriever, reranker, generator])`
- CRAG loop via `LoopAgent` wrapping retriever + reranker + gate
- State via `ToolContext` session dict (lose type safety)
- Streaming via ADK's async event generator

**Blockers**:
1. ADK is Google-Gemini-native; Anthropic Claude is not a first-class model. Requires
   ADK's `LiteLLM` adapter or a custom model class — neither is production-proven.
2. ADK's `LoopAgent` can't model Librarian's surgical CRAG back-edge cleanly (the loop
   would restart the full condense → analyze sequence, not just retrieve → rerank).
3. The typed `LibrarianState` schema would become an untyped session dict. Debugging
   regressions becomes harder.
4. Langfuse integration is LangGraph-specific; would need to be replaced with ADK callbacks.
5. The `factory.py` DI pattern doesn't map to ADK's declarative `Agent(tools=[...])` —
   strategy dispatch (chroma vs opensearch, cross-encoder vs llm-listwise) has no ADK
   equivalent.

**Verdict**: Level 3 is not worth it. ADK's strengths (auto tool wrapping, event streaming,
managed session service) don't address Librarian's core requirements (typed state, CRAG,
confidence gating, strategy dispatch). The migration cost is high; the gain is vocabulary
only — which Level 1 achieves for free.

---

## Observability ecosystem: Langfuse, LangSmith, and experiment tracking

### Tracing (per-request traces, spans, LLM call logging)

| | LangGraph (Librarian) | Google ADK |
|---|---|---|
| **LangSmith** | Native — `LangSmithCallbackHandler` is a first-class LangGraph integration; trace explorer, playground replay, and prompt hub all work | OTel only — ADK emits spans via OTel; LangSmith can receive them but loses LangChain-specific metadata (run_type, parent_run_id); no playground or prompt hub |
| **Langfuse** | Works — Langfuse `CallbackHandler` integrates via LangChain callbacks; trace view, score UI, session grouping all work | Native `GoogleADKInstrumentor` (OTel-based) — Langfuse's ADK integration is newer and well-supported; trace view works but evaluation UI requires manual score submission |
| **Arize Phoenix** | OTel — `opentelemetry-instrumentation-langchain` covers all nodes | OTel — same path as Langfuse |

**Summary**: For tracing, LangGraph + LangSmith is the tightest integration. LangGraph + Langfuse is excellent and the stack Librarian already uses. ADK + Langfuse works via `GoogleADKInstrumentor` but is newer and has less community testing.

---

### Experiment tracking (eval runs, dataset management, metric comparison)

This is where the frameworks diverge significantly.

**LangSmith (LangGraph-native)**
- `langsmith.evaluate()` runs a dataset of inputs through a compiled graph, scores outputs with evaluators, stores results in a named experiment
- Datasets live in LangSmith; you can version them, annotate runs, compare experiments side by side
- `@traceable` + `RunEvalConfig` wire directly to LangGraph runs — no glue code
- Closest analogue to Weights & Biases for LLM pipelines; purpose-built for LangChain/LangGraph

**Langfuse (framework-agnostic)**
- Datasets, runs, and scores are all first-class objects in Langfuse
- You submit score objects manually via SDK (`langfuse.score(...)`) or attach evaluators as callbacks
- Works with any framework including ADK — you're writing the eval loop yourself in Python
- More flexible but more setup: no built-in "run this dataset through my graph" shortcut
- Langfuse Prompt Management handles prompt versioning; Langfuse Datasets tracks eval sets

**Google ADK (no native eval platform)**
- ADK has no built-in experiment tracking or dataset eval runner
- You'd pair it with Langfuse (manual scoring via SDK), Weights & Biases (via OTel + W&B Weave), or build your own harness
- W&B Weave has an ADK integration via OTel — supports trace capture, dataset eval, and comparison UI, similar feature set to LangSmith but framework-agnostic

**Librarian's existing eval harness**
- `src/eval/` is a custom eval runner (`EvalRunner`, `CapabilityPipeline`, `RegressionPipeline`) that predates any framework-native option
- It's framework-agnostic by design — it calls `graph.ainvoke()` and scores the output with graders (`LLMJudge`, `ExactMatch`, `RAGAS`, etc.)
- This means the harness works regardless of whether the graph runs on LangGraph or ADK — the eval layer is above the orchestration layer
- LangSmith or Langfuse can receive trace data from each eval run for storage and comparison; the scoring logic stays local

**Verdict**: LangSmith is the most ergonomic choice if you're on LangGraph and want managed experiment tracking with zero boilerplate. Langfuse is the right choice if you want framework portability and are willing to write the eval loop. W&B Weave is the ADK-native path for experiment tracking. Librarian's custom `eval/` harness works with all three as a trace emitter.

---

## When each orchestration model is the right choice

### Use ADK when

- The agent needs to **decide** which tools to call (open-ended assistant, not a pipeline)
- You're building on Google Cloud (Vertex AI Search, Vertex AI RAG Engine are ADK-native)
- You want to prototype fast: `Agent(tools=[my_func])` is 5 lines
- Your team already knows Gemini's tool-calling API
- You need managed session storage without building it yourself
- Multi-modal (audio, video) input is a requirement (ADK has built-in multimodal support)

### Use LangGraph (Librarian approach) when

- Orchestration is **deterministic**: retrieve → rerank → generate, always
- You need a **typed state contract** across all pipeline stages (auditable, testable)
- You need **conditional retry loops** that re-enter mid-pipeline (CRAG)
- Failure attribution matters: you need to know if it was a retrieval miss vs. a reranker
  failure vs. a model hallucination
- Strategy dispatch is required: different backends (Chroma vs OpenSearch, cross-encoder vs
  LLM-listwise) configured at runtime
- You're using Claude (Anthropic is not a first-class ADK provider)
- You need the Langfuse / OTel observability stack

---

## Recommended path: Level 1 vocabulary alignment

Refactor toward ADK framing at the vocabulary level only. The graph topology, typed state,
CRAG loop, and factory pattern are correct and should not be replaced. What's worth
changing:

1. **Rename subgraph classes** to `*Agent` naming (`RetrieverAgent`, `RerankerAgent`, etc.)
   — these are agents in spirit; call them that.
2. **Add `name` and `description` properties** to each agent class — matches ADK's
   self-documenting interface and makes `factory.py` readable as an agent registry.
3. **Extract `instruction`** (system prompt snippets) from `generation/prompts.py` into the
   agent class that uses it — so each agent owns its own prompt the way ADK agents do.
4. **Expose `as_node()` method** on each agent class instead of the `_make_*_node()`
   helper functions — `retriever.as_node()` is the ADK-idiomatic way to wire an agent
   into a graph.
5. **Document the graph topology** with a topology comment block at the top of `graph.py`
   matching how ADK's `sub_agents=[...]` self-documents sequential order.

These changes don't touch behavior, don't require new tests, and make the Librarian
readable to anyone who has seen ADK, CrewAI, or LangChain agent code.

---

## Risk scorecard: Level 1 refactor

| Risk | Assessment |
|---|---|
| Behavior change | None — rename + add properties only |
| Test breakage | Low — public API surfaces (factory, graph) keep same interface |
| Observability regression | None — Langfuse wiring unchanged |
| Migration cost | ~2 days |
| Transferability gain | High — codebase readable to ADK/CrewAI/LangChain Agent users |
| Reversibility | Trivially reversible — pure rename |

---

## Summary

Librarian's LangGraph orchestration is architecturally superior to what ADK could offer for
this pipeline: typed state, conditional CRAG loop, strategy dispatch, Langfuse + OTel
integration, and confidence gating are all done better in LangGraph than ADK's primitives
allow. The case for a full framework swap is weak.

The gap is vocabulary, not architecture. Renaming `SubGraph` → `Agent`, surfacing
`instruction` per agent, and adding `as_node()` wiring methods costs ~2 days and makes the
Librarian legible to any engineer who has used ADK, CrewAI, or any other agent framework.
That's the right refactor scope.

---

## Testing ADK: what you could actually build

Librarian stays LangGraph. But ADK is worth prototyping separately, in two different
patterns — they test different hypotheses.

---

### Option A: ADK + LangGraph hybrid

**Hypothesis**: Use ADK's session management, event streaming, and multi-agent routing as the
outer shell; keep the Librarian's compiled LangGraph graph as the inner retrieval pipeline.

ADK lets you subclass `BaseAgent` and implement `_run_async_impl()` with arbitrary Python
logic — including `graph.ainvoke()`. This wraps the entire Librarian graph as a single ADK
agent, callable from an ADK `Runner` or multi-agent system.

```python
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from collections.abc import AsyncIterator
from librarian.factory import create_librarian

class LibrarianAgent(BaseAgent):
    """ADK wrapper around the compiled LangGraph LibrarianGraph.

    Exposes the full retrieval pipeline (condense → analyze → retrieve →
    rerank → gate → generate) as a single ADK-compatible agent.
    """
    name = "librarian"
    description = "Retrieval-augmented QA over the knowledge corpus"

    def __init__(self) -> None:
        super().__init__(name=self.name, description=self.description)
        self._graph = create_librarian()

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncIterator[Event]:
        # Extract latest user message from ADK's conversation history
        query = ctx.session.events[-1].content.parts[0].text

        # Build LibrarianState from ADK context
        state = {
            "query": query,
            "messages": [
                {"role": "user" if e.author == "user" else "assistant",
                 "content": e.content.parts[0].text}
                for e in ctx.session.events
            ],
            "conversation_id": ctx.session.id,
        }

        result = await self._graph.ainvoke(state)

        # Emit as ADK event
        yield Event(
            author=self.name,
            content=types.Content(
                parts=[types.Part(text=result["response"])]
            ),
        )
```

**What you gain over Librarian standalone**:
- ADK's `InMemorySessionService` (or `DatabaseSessionService`) for managed session storage
- ADK's `Runner` handles turn management, event streaming, and user/agent interleaving
- The `LibrarianAgent` can be one node in a larger ADK multi-agent system — e.g., a
  coordinator that routes to `LibrarianAgent` for knowledge queries and to a
  `CRMAgent` for account lookups

**What you keep from Librarian**:
- Typed `LibrarianState`, CRAG loop, confidence gate — all unchanged
- Langfuse / OTel tracing — wire the handler inside `_run_async_impl` as before
- The eval harness in `src/eval/` — it calls `LibrarianAgent` the same way it calls the
  raw graph

**What you lose**:
- ADK event granularity: the hybrid emits one final event per turn, not streaming tokens
  (streaming would require bridging ADK's async generator and LangGraph's stream output)
- ADK tool introspection: the inner graph's nodes are invisible to ADK's tool tracing

**Effort to prototype**: 1–2 days. Mostly boilerplate in `_run_async_impl`.

**Good test question**: Does ADK's session management and multi-agent routing add value over
the existing `conversation_id`-based session handling in the Librarian API? If yes, the
hybrid is worth the wrapper cost.

---

### Option B: ADK + custom RAG (tool-based)

**Hypothesis**: Build a fresh ADK agent where the LLM drives retrieval decisions — the model
calls tools to search, rerank, and generate rather than following a fixed pipeline.

This is a different architecture philosophy from Librarian. Use it to test whether
LLM-driven retrieval decisions produce better answers than Librarian's fixed pipeline for
some query types.

```python
import chromadb
from sentence_transformers import CrossEncoder
from google.adk.agents import Agent
from google.adk.tools import ToolContext

# Set up shared infrastructure (outside the agent)
_chroma = chromadb.PersistentClient(path=".chroma")
_collection = _chroma.get_collection("librarian-chunks")
_reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def search_knowledge_base(
    query: str,
    k: int = 10,
    tool_context: ToolContext | None = None,
) -> dict:
    """Search the knowledge base for chunks relevant to the query.

    Args:
        query: The search query.
        k: Number of results to return (default 10).

    Returns:
        A dict with 'chunks' (list of text passages) and 'scores' (relevance scores).
    """
    results = _collection.query(query_texts=[query], n_results=k)
    chunks = results["documents"][0]
    scores = results["distances"][0]
    return {"chunks": chunks, "scores": scores, "count": len(chunks)}


def rerank_chunks(
    query: str,
    chunks: list[str],
    top_k: int = 3,
    tool_context: ToolContext | None = None,
) -> dict:
    """Rerank a list of text chunks by relevance to the query.

    Args:
        query: The query to score against.
        chunks: List of text passages to rerank.
        top_k: Number of top chunks to return.

    Returns:
        A dict with 'reranked_chunks' and 'confidence_score' (max relevance score).
    """
    pairs = [(query, chunk) for chunk in chunks]
    scores = _reranker.predict(pairs)
    ranked = sorted(
        zip(chunks, scores), key=lambda x: x[1], reverse=True
    )
    top = ranked[:top_k]
    return {
        "reranked_chunks": [c for c, _ in top],
        "confidence_score": float(top[0][1]) if top else 0.0,
    }


# The agent decides when to search, when to rerank, when to answer
rag_agent = Agent(
    model="gemini-2.5-flash",
    name="rag_agent",
    description="Answers questions using a knowledge base via retrieval tools.",
    instruction="""You are a knowledgeable assistant with access to a curated knowledge base.

When answering questions:
1. Always search the knowledge base first using search_knowledge_base
2. If the results seem noisy or you're unsure which passages are most relevant,
   use rerank_chunks to surface the best matches
3. If the confidence_score from reranking is below 0.3, search again with a
   different phrasing before answering
4. Base your answer strictly on the retrieved passages; do not hallucinate facts
5. If no relevant passages are found, say so clearly
""",
    tools=[search_knowledge_base, rerank_chunks],
)
```

**What this tests**:
- Whether the LLM makes good retrieval decisions (when to rerank, when to retry)
  vs. Librarian's deterministic CRAG loop
- Whether ADK's automatic tool schema generation (from docstrings + type hints) is
  sufficient to describe retrieval tools, or whether structured tool contracts are needed
- Response quality: open-ended LLM-driven retrieval vs. pipeline retrieval on the same corpus

**What you give up vs. Librarian**:
- `LibrarianState` typed schema — state is implicit in the model's context window
- Deterministic routing — the model may skip reranking, call search twice, or not retry
  when it should
- Confidence gating as a hard gate — the instruction asks for retry but the model can ignore it
- `HistoryCondenser` — multi-turn coreference relies on the model's in-context reasoning
  (often fine for Gemini; untested for this corpus)
- Full observability — tool call / tool response events are captured by ADK's callbacks, but
  there's no `confidence_score` in state, no `retrieved_chunks` list to inspect

**What you gain**:
- Flexibility: the agent can decide to search twice with different queries, chain searches,
  or skip retrieval for conversational queries — without graph topology changes
- Less setup: no `factory.py`, no graph compilation, no subgraph classes
- ADK tool auto-wrapping: `search_knowledge_base` becomes a tool from its signature + docstring
- Works with Gemini's native tool-calling, including parallel tool calls in one turn

**Effort to prototype**: 1 day. The corpus is already in ChromaDB and the cross-encoder is
already a dep; the agent definition is ~40 lines.

**Good test question**: On technical queries (version numbers, product names, code terms),
does the LLM make sensible retrieval decisions, or does it consistently under-retrieve and
hallucinate? This is the failure mode Librarian's fixed pipeline was designed to prevent.

---

### Comparison: which hypothesis to test first

| | ADK + LangGraph hybrid | ADK + custom RAG tools |
|---|---|---|
| **What it tests** | ADK as session/routing shell over Librarian | LLM-driven vs pipeline-driven retrieval |
| **Setup** | ~1–2 days | ~1 day |
| **Risk** | Low — Librarian internals unchanged | Medium — retrieval quality depends on model discipline |
| **Corpus needed** | Same corpus as Librarian | Same corpus as Librarian |
| **Best for** | Testing multi-agent integration (coordinator + librarian + CRM agent) | Testing whether LLM-driven retrieval closes quality gaps |
| **Observability** | Full Langfuse trace from inner graph | ADK callbacks + manual score submission |
| **Model** | Claude (inner graph) + Gemini (ADK shell, optional) | Gemini (drives tool calls) |

**Recommended**: prototype Option B first. It answers the more interesting research question
(LLM-driven vs. deterministic retrieval) and is faster to build. Option A makes more sense
once you know whether ADK's session management adds value over the current API layer.
