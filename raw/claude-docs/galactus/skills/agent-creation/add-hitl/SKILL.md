---
name: add-hitl
description: "Add human-in-the-loop interrupt gates to a LangGraph agent. Pauses graph execution at a confirmation node and waits for human approval before continuing. Triggers on: 'add HITL', 'add human review', 'add approval gate', 'add interrupt', 'pause before acting'."
allowed-tools: Read Grep Glob Bash Write
---

You are adding a HITL interrupt gate to an existing LangGraph agent in galactus.

> **ADK note:** ADK does not have native graph interrupts. For ADK agents, HITL is implemented via a separate approval webhook or a multi-turn conversation pattern. If the target is an ADK agent, ask the user to confirm the approach before proceeding.

## Step 1 — Read the ref docs

Before generating any code, read:
1. `docs/langgraph.md` — interrupt patterns, checkpointer requirement, resume flow
2. The agent's `graph/builder.py` — understand current node/edge topology before inserting a gate

## Step 2 — Read the target agent

From `$ARGUMENTS` parse the agent path. Read `graph/builder.py` and `graph/state.py` (or equivalent). Identify the node BEFORE which you want to pause.

If no agent path given, ask: "Which agent and which node should the gate precede?"

## Step 3 — Add the interrupt node

```python
# graph/nodes/hitl.py
from langgraph.types import interrupt

async def hitl_confirm_node(state: AgentState) -> dict:
    """Pause execution and surface the pending action to a human reviewer."""
    decision = interrupt({
        "pending_action": state.get("pending_action"),
        "summary": state.get("draft_response", ""),
        "message": "Review and approve before continuing.",
    })
    return {"human_approved": decision.get("approved", False)}
```

## Step 4 — Wire the gate into the graph

```python
# In graph/builder.py, inside build_graph():
graph.add_node("hitl_confirm", hitl_confirm_node)

# Add conditional edge: previous_node → hitl_confirm → next_node
graph.add_edge("draft", "hitl_confirm")
graph.add_conditional_edges(
    "hitl_confirm",
    lambda state: "continue" if state.get("human_approved") else "escalate",
    {"continue": "generate", "escalate": "escalation_node"},
)
```

## Step 5 — Require a checkpointer

HITL interrupts require a checkpointer to persist state between the pause and resume:

```python
# In main.py or wherever the graph is compiled:
from langgraph.checkpoint.memory import MemorySaver  # dev
# from langgraph.checkpoint.postgres import PostgresSaver  # prod

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer, interrupt_before=["hitl_confirm"])
```

## Step 6 — Expose the resume endpoint

```python
# In main.py (FastAPI):
@router.post("/resume/{thread_id}")
async def resume(thread_id: str, approved: bool):
    config = {"configurable": {"thread_id": thread_id}}
    result = await app.ainvoke(
        Command(resume={"approved": approved}),
        config=config,
    )
    return result
```

## Done when

- `hitl_confirm_node` exists and uses `interrupt()`
- Graph compiles with `interrupt_before=["hitl_confirm"]`
- Checkpointer is wired (MemorySaver for dev, PostgresSaver for prod)
- Resume endpoint exists
- Run: `uv run pytest tests/ -k "hitl" --tb=short -q`
