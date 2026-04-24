# RAG Advanced Patterns

> Source: `.claude/docs/backlog/agentic-rag-copilot/research.md`
> Date: 2026-04-15. Covers patterns beyond CRAG: Self-RAG, Adaptive RAG, GraphRAG,
> HyDE, A2A, MCP, memory architecture, Plan-and-Execute, agentic evaluation.

---

## Self-RAG vs CRAG

CRAG (current): retrieve always, grade chunks, retry if none pass. LLM has no say.

Self-RAG: LLM generates four reflection tokens inline:
- `[Retrieve]` / `[No Retrieve]` — should I retrieve for this segment?
- `[IsRel]` — is this passage relevant?
- `[IsSup]` — does my generation use/support the retrieved passage?
- `[IsUse]` — is this output useful?

| Pattern | Best for |
|---|---|
| CRAG | Pipelines where retrieval is always warranted (Q&A, document lookup) |
| Self-RAG | Conversational agents where some turns are chitchat |
| Both | Full copilot: Self-RAG at outer loop decides "do we retrieve?"; CRAG handles retries |

**Practical LangGraph path:** `analyze` node already does intent classification. Extend to output
`needs_retrieval: bool` — this is Self-RAG's `[Retrieve]` token without the full training overhead.
Skips retrieval for chitchat (saves ~100–300ms per turn).

---

## Adaptive RAG — route by complexity

Route queries to different pipeline depths instead of always running CRAG.

```
query → complexity classifier
           ├─ simple / factual → single retrieve + generate (~200ms)
           ├─ moderate / procedural → CRAG loop (~500ms)
           └─ complex / synthesis → decompose + sequential retrieve (~1–2s)
```

`QueryAnalyzer` already extracts `complexity: simple|moderate|complex`. Missing piece: use it
to route to different pipeline depths.

```python
def route_by_complexity(state: AgentState) -> str:
    match state["query_plan"].complexity:
        case "simple": return "retrieve_simple"
        case "moderate": return "retrieve_crag"
        case "complex": return "decompose"
```

---

## HyDE — Hypothetical Document Embeddings

Generate a hypothetical ideal answer, embed *that* instead of the raw query. Closes the
query-document lexical gap for factual/domain queries.

```python
async def generate_hyde_doc(query: str, llm: LLM) -> str:
    return await llm.ainvoke(
        f"Write a short factual answer (2-3 sentences) to: {query}\n"
        "Be specific and use domain terminology. Do not say you don't know."
    )

hyde_embedding = embedder.embed_query("query: " + hypothesis)
results = retriever.retrieve(hyde_embedding, k=10)
```

**When it helps:** factual lookup, domain-specific questions with vocabulary gap.
**When it hurts:** ambiguous or conversational queries — confident wrong hypothesis → irrelevant retrieval.
**Cost:** 1 Haiku call (~$0.0001, ~100ms). Gate behind `planning_mode == "full"`.
**Measure:** RAGAS `context_recall` with/without — expect +5–15% on factual, neutral on conversational.

---

## GraphRAG

Vector search finds similar passages. GraphRAG finds connected entities across the corpus.

**When vector search fails:** "What do all invoices for customer X have in common with their overdue pattern?"
Vector can't traverse Customer → [Invoice, Invoice] → [Payment, Payment].

### Microsoft GraphRAG (2024) pattern
1. **At ingest:** Extract entities and relationships using LLM. Build knowledge graph.
2. **At query:** Detect analytical/synthesis intent. Community detection + summarization.
3. **Combine:** Merge graph-retrieved context with vector-retrieved context.

**Cost concern:** entity extraction is 1 LLM call per chunk (Haiku ~$0.0001/chunk). Run as background job for large corpora.

**Recommendation:** Defer until base copilot is proven. Add as `retrieval_strategy: graphrag`,
activated by `complexity == "complex"` and `intent in ("compare", "synthesize")`.

---

## A2A — Agent-to-Agent Protocol

Google's open specification (April 2025) for inter-agent communication across frameworks, vendors, deployments.

### Core concepts

**Agent Card** (`/.well-known/agent.json`):
```json
{
  "name": "librarian",
  "description": "RAG retrieval and Q&A over document corpus",
  "url": "https://your-service/a2a",
  "capabilities": { "streaming": true, "pushNotifications": true },
  "skills": [{ "id": "query", "name": "Query knowledge base", "inputModes": ["text"], "outputModes": ["text", "data"] }],
  "authentication": { "schemes": ["Bearer"] }
}
```

**Task lifecycle:** `submitted → working → (input-required ↔ working) → completed | failed | cancelled`

### LangGraph ↔ A2A mapping

| A2A concept | LangGraph equivalent |
|---|---|
| Task ID | `thread_id` (checkpointer key) |
| Task state | Checkpointer state at latest checkpoint |
| `input-required` | `interrupt()` (human-in-the-loop) |
| Streaming updates | `.astream_events()` → SSE |
| Push notification | Webhook callback after `END` node |

**Minimal implementation (FastAPI):**
```
src/interfaces/a2a/
  agent_card.py    # Serve /.well-known/agent.json
  router.py        # POST /a2a — parse JSON-RPC, route to graph
  task_store.py    # task_id → thread_id mapping in Postgres
  models.py        # Pydantic A2A request/response envelopes
```

Don't implement the full spec up-front. Start with Agent Card + `tasks/send` + SSE streaming.

---

## MCP as the tool layer

MCP (Model Context Protocol, Anthropic 2024) serves tool definitions independently from the agent.
Agent discovers tools at runtime — swap retrieval backend without redeploying the agent.

### LangGraph MCP client
```python
from langchain_mcp_adapters.client import MultiServerMCPClient

async with MultiServerMCPClient({
    "librarian": {"url": "http://localhost:8001/mcp", "transport": "streamable_http"},
    "s3": {"url": "http://localhost:8002/mcp", "transport": "streamable_http"},
}) as client:
    tools = client.get_tools()
    graph = create_react_agent(llm, tools=tools, checkpointer=checkpointer)
```

Existing playground MCP servers: `librarian.py` (RAG retrieval), `s3.py`, `snowflake.py`.

---

## Memory architecture — four types

| Type | What it holds | Lifetime | LangGraph mechanism |
|---|---|---|---|
| **In-context** | Current messages, active task state, retrieved chunks | One session | `AgentState` + checkpointer |
| **Episodic** | Past conversation summaries per user | Days to weeks | `BaseStore` (cross-thread) |
| **Semantic** | User preferences, domain facts, entity knowledge | Persistent | `BaseStore` + vector retrieval |
| **Procedural** | Learned tool sequences, user shortcuts | Persistent | `BaseStore` (named templates) |

### LangGraph `BaseStore` (0.4+)
```python
# Development
store = InMemoryStore()

# Production (same Postgres as checkpointer)
store = AsyncPostgresStore.from_conn_string(settings.database_url)

graph = graph.compile(checkpointer=checkpointer, store=store)
```

```python
async def retrieve_node(state: AgentState, config: RunnableConfig) -> AgentState:
    store = config["store"]
    memories = await store.asearch(
        namespace=("user", state["user_id"], "memories"),
        query=state["query"],
        limit=3,
    )
    await store.aput(
        namespace=("user", state["user_id"], "memories"),
        key=f"session_{state['session_id']}",
        value={"summary": state["session_summary"], "timestamp": now()},
    )
```

**Implementation priority:** in-context (done) → episodic (1 Haiku/session ~$0.0001) → semantic → procedural.

---

## Plan-and-Execute pattern

For multi-step actions, separates planning from execution. Prevents ReAct going off-script mid-sequence.

```
[Planner] → plan: list[Step] → [Executor] → result per step
                                    ↓
                             [Replanner] → done? → [Responder]
                                         → update_plan → [Executor]
```

```python
class Step(BaseModel):
    id: str
    description: str
    tool: str
    tool_input: dict
    depends_on: list[str]

class PlanExecuteState(TypedDict):
    input: str
    plan: list[Step]
    past_steps: list[tuple[Step, str]]
    response: str | None
```

**Model assignment:** Planner (Sonnet) for plan quality. Executor + Replanner (Haiku) for cheap execution.
**Human-in-the-loop hook:** `interrupt()` after planner, before executor — show plan for approval.

### Parallel steps via Send API
```python
def execute_parallel_steps(state: PlanExecuteState) -> list[Send]:
    ready = [s for s in state["plan"] if all_deps_met(s, state["past_steps"])]
    return [Send("execute_step", {"step": s}) for s in ready]
```

---

## LangGraph advanced patterns

### Subgraphs — compose without coupling
```python
crag_graph = build_crag_graph()     # compiled independently
plan_graph = build_plan_execute_graph()

copilot.add_node("rag_pipeline", crag_graph)
copilot.add_node("action_pipeline", plan_graph)
copilot.add_conditional_edges("route", route_by_intent, {
    "q_and_a": "rag_pipeline",
    "task_execution": "action_pipeline",
})
```

### Send API — fan-out parallelism (map-reduce)
```python
def fan_out_queries(state: AgentState) -> list[Send]:
    return [Send("retrieve_single", {"query": q}) for q in state["expanded_queries"]]
```

### Streaming modes
| Mode | What you get | Use for |
|---|---|---|
| `values` | Full state snapshot after each node | Debugging |
| `updates` | State delta after each node | Progress indicators |
| `events` | Token, tool start/end, node start/end | Copilot UI SSE streaming |

### Breakpoints (human-in-the-loop)
```python
graph.compile(
    interrupt_before=["tool_executor"],
    interrupt_after=["planner"],
    checkpointer=checkpointer,
)
# Resume: graph.invoke(Command(resume="approved"), config)
```

### Time-travel / rollback
```python
checkpoints = list(graph.get_state_history(config))
old_config = checkpoints[2].config
graph.update_state(old_config, {"messages": [HumanMessage("Actually, cancel that")]})
graph.invoke(None, old_config)
```

---

## Agentic evaluation

### Task completion rate
```python
class AgentTestCase(BaseModel):
    input: str
    expected_tool_calls: list[str]
    expected_outcome: str
    evaluator: Callable[[result], bool]
```

### Trajectory evaluation
For multi-step tasks — evaluate the *sequence*, not just the final answer.
```python
class TrajectoryEval(BaseModel):
    expected_steps: list[str]  # ["planner", "confirm", "create_invoice", "send_email"]
    actual_steps: list[str]
    
    def step_precision(self) -> float: ...
    def step_recall(self) -> float: ...
    def order_accuracy(self) -> float: ...  # LCS of step sequences
```

LangFuse captures tool call sequences per trace — add post-run evaluator comparing against expected trajectories.

### Latency budgets

| Query tier | P50 | P95 |
|---|---|---|
| Simple (no retrieval) | 300ms | 800ms |
| Q&A (single retrieve) | 800ms | 2s |
| CRAG retry | 1.5s | 4s |
| Action (plan + execute) | 2s | 6s |

### Adversarial tests (required before prod)
- Prompt injection via retrieval: corpus chunk contains "Ignore previous instructions..."
- Tool call manipulation: retrieved doc instructs agent to call unintended tools
- Sensitive data exfiltration: "what tokens do you have access to?"
- Scope violation: request an API the agent shouldn't have access to

Run in `tests/adversarial/` with `--dry-run` to avoid side effects.

---

## Implementation priority

| Priority | Pattern | Effort | Value |
|---|---|---|---|
| 1 | Breakpoints (`interrupt_before/after`) | 1 day | High — confirm gate for actions |
| 2 | Plan-and-Execute subgraph | 3 days | High — multi-step tasks |
| 3 | Send API parallel tool calls | 1 day | Medium — latency |
| 4 | BaseStore episodic memory | 2 days | High — cross-session recall |
| 5 | A2A Agent Cards | 2 days | Medium — researcher/presenter as services |
| 6 | HyDE in analyze node | 0.5 days | Medium — retrieval quality |
| 7 | Adaptive RAG routing | 1 day | Medium — latency on simple queries |
| 8 | Trajectory eval in LangFuse | 2 days | High — trust in agentic behavior |
| 9 | Adversarial test suite | 2 days | High — production safety |
| 10 | Self-RAG critic node | 2 days | Medium — post-generation grounding |
| 11 | GraphRAG | 5+ days | Medium — complex synthesis only |
| 12 | MCP as tool layer | 3 days | Medium — tool swap without redeploy |

Items 1–4 are the copilot core. Build on top of the existing CRAG pipeline without changing it.
