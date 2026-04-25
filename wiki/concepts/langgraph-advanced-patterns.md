---
title: LangGraph Advanced Patterns
tags: [langgraph, pattern]
summary: Advanced LangGraph patterns beyond the basics — subgraphs, Send API fan-out, streaming modes, time-travel, breakpoints/interrupts, error handling, and Plan-and-Execute.
updated: 2026-04-25
sources:
  - raw/playground-docs/agentic-rag-copilot-research.md
  - raw/playground-docs/adk-samples-patterns-analysis.md
  - raw/playground-docs/rag-agent-template-research.md
  - raw/gdrive/2026-04-24-langgraph-yan.md
  - raw/agent-skills/langgraph-fundamentals/SKILL.md
  - raw/agent-skills/langgraph-human-in-the-loop/SKILL.md
---

# LangGraph Advanced Patterns

## Subgraphs — Compose Without Coupling

```python
# CRAG pipeline as its own subgraph
crag_graph = build_crag_graph()  # returns compiled graph

# Plan-and-Execute as its own subgraph
plan_graph = build_plan_execute_graph()

# Copilot routes between them
copilot = StateGraph(CopilotState)
copilot.add_node("rag_pipeline", crag_graph)
copilot.add_node("action_pipeline", plan_graph)
copilot.add_conditional_edges("route", route_by_intent, {
    "q_and_a": "rag_pipeline",
    "task_execution": "action_pipeline",
})
```

Each subgraph is independently testable. The copilot graph only knows about interfaces.

**State sharing:** subgraphs inherit parent state keys they declare; private keys are isolated.

## Send API — Fan-Out Parallelism

See [[Send API Fan-out]] for full detail. Built-in for map-reduce patterns:

```python
def fan_out_queries(state: AgentState) -> list[Send]:
    return [
        Send("retrieve_single", {"query": q, "original_query": state["query"]})
        for q in state["expanded_queries"]
    ]
```

LangGraph waits for all fan-out nodes to complete before proceeding. `Annotated[list, add_messages]` reducer auto-merges results.

**Use for:** parallel retrieval across multiple query variants or knowledge bases simultaneously.

## Streaming Modes

| Mode | What you get | Use for |
|---|---|---|
| `values` | Full state snapshot after each node | Debugging, final state only |
| `updates` | State delta after each node | Progress indicators, partial results |
| `events` | Fine-grained: token, tool start/end, node start/end | Copilot UI (stream tokens + tool activity) |

### SSE endpoint using `events` mode

```python
async for event in graph.astream_events(
    {"messages": [HumanMessage(request.message)]},
    config={"thread_id": request.session_id},
    version="v2",
):
    if event["event"] == "on_chat_model_stream":
        yield f"data: {json.dumps({'type': 'token', 'content': event['data']['chunk'].content})}\n\n"
    elif event["event"] == "on_tool_start":
        yield f"data: {json.dumps({'type': 'tool_start', 'tool': event['name']})}\n\n"
```

## Time-Travel / State Rollback

Because every node execution is checkpointed, replay from any point:

```python
# List all checkpoints for a thread
checkpoints = list(graph.get_state_history(config))

# Roll back to before the last tool execution
old_config = checkpoints[2].config
graph.update_state(old_config, {"messages": [HumanMessage("Actually, cancel that")]})
graph.invoke(None, old_config)  # resume from that state
```

**Practical use:** "undo last action", try a different approach, debugging by replaying with modified state.

## Breakpoints — Controlled Interrupts

```python
graph.compile(
    interrupt_before=["tool_executor"],  # pause before any tool execution
    interrupt_after=["planner"],         # pause after plan is generated
    checkpointer=checkpointer,
)
```

After interrupting, the frontend shows the pending action/plan and waits for user approval. Resume with `graph.invoke(Command(resume="approved"), config)`.

This is the clean implementation of HITL confirm gates — no custom interrupt logic needed, just compiler flags.

## History Pruning (from ADK samples pattern)

```python
# shared/tools/history_pruning.py — remove prior tool responses before each LLM call
# Keeps: user messages + agent text + current turn tool calls
```

**Why:** neither rag_poc nor playground does this. Long sessions accumulate full tool history, causing context bloat and degraded performance.

**Summarization trigger:** 8-message trigger, 4-message overlap, Haiku for cost.

## Supervisor Multi-Agent Pattern

```
supervisor_graph:
    START
      ↓
    [plan_node]          ← intent, tool routing, clarification
      ↓ (route)
    [retrieval_subgraph] ← rewrite, multi-query, hybrid search, CRAG
      ↓
    [reranker_subgraph]  ← score, filter to top-k, set confidence_score
      ↓
    [generation_subgraph] ← prompt assembly, LLM call, citation
      ↓
    [confidence_gate]    ← confidence_score < threshold → escalate/clarify
      ↓
    END
```

Each subgraph:
- Has its own `StateGraph` and compiled `CompiledStateGraph`
- Communicates via `Command(goto=..., update={...})`
- Can be tested, swapped, and deployed independently

**Why multi-agent for RAG template:** independent testability, swappability, parallelism, per-subgraph traces in LangFuse.

## Command Routing Pattern

```python
def supervisor_route(state: SupervisorState) -> Command:
    if state["intent"] in {"chit_chat", "out_of_scope"}:
        return Command(goto="generation_subgraph", update={"skip_retrieval": True})
    return Command(goto="retrieval_subgraph")
```

## Workflows vs Agents

LangGraph supports two distinct execution models:

- **Workflows** — predetermined code paths defined at compile time. Fast and predictable. Use when every possible execution path can be anticipated (e.g. CRAG retry loop, HITL confirm gate).
- **Agents** — dynamic. The agent decides which tools to call and in what order at runtime. Use when the task space is open-ended.

Both are implemented with the same `StateGraph` API. The distinction is whether conditional edges route to fixed destinations or the LLM picks the next step.

## Checkpointer Backend Selection

Choose based on environment and scale:

| Backend | Environment | Characteristics |
|---|---|---|
| `MemorySaver` | Dev / unit tests | In-memory only. Lost on restart. Zero setup. |
| `SqliteSaver` | Local / prototype | SQLite file. Survives restarts. Not scalable. |
| `PostgresSaver` | Production | ACID, concurrent, horizontal scale. Used in LangSmith itself. |
| `RedisSaver` | High-perf production | <1ms checkpoint reads. TTL support. Distributed. |

```python
# Development
checkpointer = MemorySaver()

# Production (multi-instance Fargate)
checkpointer = AsyncRedisSaver(ttl=86400)  # 24h TTL
```

Template: `MemorySaver` default, `checkpointer` param for injection.

## Time Travel — Replay vs Fork

Two distinct time travel modes built on top of checkpoints:

- **Replay** — re-execute from a prior checkpoint. Same inputs, same graph. Use for debugging or retrying after a failure.
- **Fork** — branch from a prior checkpoint with *modified* state. Creates an alternative execution path without affecting the original thread. Use for "what if" exploration and test harnesses.

```python
# List all checkpoints for a thread
checkpoints = list(graph.get_state_history(config))

# Replay from checkpoint 2
graph.invoke(None, checkpoints[2].config)

# Fork with modified state
graph.update_state(checkpoints[2].config, {"messages": [HumanMessage("Try differently")]})
graph.invoke(None, checkpoints[2].config)
```

## HITL: Static Breakpoints vs Dynamic `interrupt()`

Two mechanisms — choose based on where in execution you need to pause:

**Static breakpoints** (compile-time, fires at node boundaries):
```python
graph.compile(
    interrupt_before=["tool_executor"],  # pause before any tool execution
    interrupt_after=["planner"],          # pause after plan is generated
    checkpointer=checkpointer,
)
```

**Dynamic `interrupt()`** (runtime, fires inside a node mid-execution):
```python
from langgraph.types import interrupt

def review_node(state: AgentState) -> AgentState:
    draft = generate_draft(state)
    approved = interrupt({"draft": draft, "prompt": "Approve?"})  # suspends here
    if not approved:
        return {"messages": [HumanMessage("Revise: ...")]}
    return {"output": draft}
```

Use static for predictable pause points (before/after known nodes). Use dynamic when the pause decision depends on runtime state computed inside the node.

See [[HITL Annotation Pipeline]] for the broader annotation workflow pattern.

## HITL: Idempotency Before interrupt()

When a graph resumes, the node restarts from the **beginning** — all code before `interrupt()` re-runs. In subgraphs, both parent and subgraph node re-execute.

**Safe before interrupt():** upsert operations, check-before-create patterns.
**Unsafe before interrupt():** inserts, list appends — these create duplicates on each resume.

Always place non-idempotent side effects **after** `interrupt()`, or extract them to a separate node that runs before the interrupt node.

## HITL: Validation Loop

`interrupt()` can be used inside a loop to re-prompt until input is valid:

```python
def get_age_node(state):
    prompt = "What is your age?"
    while True:
        answer = interrupt(prompt)
        if isinstance(answer, int) and answer > 0:
            break
        prompt = f"'{answer}' is not valid. Please enter a positive number."
    return {"age": answer}
```

## HITL: Multiple Parallel Interrupts

When parallel branches each call `interrupt()`, resume all with a single `Command` mapping interrupt IDs to values:

```python
result = graph.invoke({"vals": []}, config)
resume_map = {i.id: f"answer for {i.value}" for i in result["__interrupt__"]}
result = graph.invoke(Command(resume=resume_map), config)
```

## HITL: Command(resume) Warning

`Command(resume=...)` is the **only** Command pattern intended as `invoke()` input. Do NOT pass `Command(update=...)` as invoke input — the graph appears stuck (resumes from latest checkpoint but the update is not applied as expected).

## Error Handling Strategy

Match error type to the right handler:

| Error Type | Who Fixes | Strategy |
|---|---|---|
| Transient (network, rate limits) | System | `RetryPolicy(max_attempts=3)` on `add_node` |
| LLM-recoverable (tool failures) | LLM | `ToolNode(tools, handle_tool_errors=True)` |
| User-fixable (missing info) | Human | `interrupt({"message": ...})` |
| Unexpected | Developer | Let bubble up — `raise` |

```python
from langgraph.types import RetryPolicy
from langgraph.prebuilt import ToolNode

workflow.add_node(
    "search",
    search_node,
    retry_policy=RetryPolicy(max_attempts=3, initial_interval=1.0)
)

tool_node = ToolNode(tools, handle_tool_errors=True)
workflow.add_node("tools", tool_node)
```

## Custom Stream Writer

Emit progress updates from inside a node:

```python
from langgraph.config import get_stream_writer

def my_node(state):
    writer = get_stream_writer()
    writer("Processing step 1...")
    # do work
    writer("Complete!")
    return {"result": "done"}

for chunk in graph.stream({"data": "test"}, stream_mode="custom"):
    print(chunk)
```

## Command + Static Edge Warning

`Command(goto="node_c")` adds a **dynamic** edge only. If you also have `graph.add_edge("node_a", "node_b")`, **both** `node_b` and `node_c` will run. Only use `Command` routing when the node has no static outgoing edges.

## See Also
- [[LangGraph CRAG Pipeline]]
- [[LangGraph State Reducers]]
- [[Agent Memory Types]]
- [[Plan and Execute Pattern]]
- [[ADK Context Engineering]]
- [[A2A Agent Protocol]]
- [[HITL Annotation Pipeline]]
- [[Framework Selection — LangChain vs LangGraph vs Deep Agents]]
- [[Deep Agents Framework]]
- [[Voice Agent Patterns]]
