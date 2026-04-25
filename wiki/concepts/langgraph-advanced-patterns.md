---
title: LangGraph Advanced Patterns
tags: [langgraph, pattern]
summary: Advanced LangGraph patterns beyond the basics — subgraphs, Send API fan-out, streaming modes, time-travel, breakpoints/interrupts, and Plan-and-Execute.
updated: 2026-04-24
sources:
  - raw/playground-docs/agentic-rag-copilot-research.md
  - raw/playground-docs/adk-samples-patterns-analysis.md
  - raw/playground-docs/rag-agent-template-research.md
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

## MemorySaver → Redis Upgrade Path

```python
# Development
checkpointer = MemorySaver()

# Production (multi-instance Fargate)
checkpointer = AsyncRedisSaver(ttl=86400)  # 24h TTL
```

Template: `MemorySaver` default, `checkpointer` param for injection.

## See Also
- [[LangGraph CRAG Pipeline]]
- [[Agent Memory Types]]
- [[Plan and Execute Pattern]]
- [[ADK Context Engineering]]
- [[A2A Agent Protocol]]
