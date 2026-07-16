---
title: HITL and Interrupt Patterns
tags: [adk, langgraph, pattern, concept]
summary: Six HITL patterns for LangGraph agents — static breakpoints, dynamic interrupt(), clarification loop (budget-bounded), scheduler confirmation gate, tool approval for irreversible actions, and time-travel/replay/fork.
updated: 2026-07-05
sources:
  - raw/claude-docs/playground/docs/research/agentic-ai/hitl-and-interrupts.md
---

# HITL and Interrupt Patterns

Six patterns for human-in-the-loop control in LangGraph agents. Choose based on precision needed and testability requirements.

## Two Interrupt Modes

| Mode | Declared | Fires when | Testability |
|---|---|---|---|
| **Static breakpoints** | Compile time (`interrupt_before`, `interrupt_after`) | Always at that node boundary | Easy — predictable |
| **Dynamic `interrupt()`** | Inside a node at runtime | Only when condition is met | Harder — conditional |

**Static breakpoints** are coarse but predictable. Use for mandatory review points.
**Dynamic `interrupt()`** is precise. Use when the condition matters (e.g., only high-value transactions).

```python
# Static — always stops before approve_payment
graph.compile(interrupt_before=["approve_payment"])

# Dynamic — stops only when amount > threshold
def payment_node(state):
    if state["amount"] > 1000:
        response = interrupt({"question": "Approve payment?", "amount": state["amount"]})
    return {"approved": response == "yes"}
```

## Pattern 1: Clarification Loop (Budget-Bounded)

Prevents infinite clarification rounds. Tracks attempts in state.

```python
MAX_CLARIFICATION_ROUNDS = 2

def classify_intent(state):
    if state["intent_confidence"] < 0.5 and state["clarification_rounds"] < MAX_CLARIFICATION_ROUNDS:
        response = interrupt({"question": "Can you clarify what you need help with?"})
        return {"messages": [..., HumanMessage(response)], "clarification_rounds": state["clarification_rounds"] + 1}
    return {}  # proceed with best-guess intent
```

**Why bounded:** unbounded loops create bad UX and can exhaust context window.

## Pattern 2: Scheduler Confirmation Gate

Shows the full plan before any execution. Suitable for multi-step tasks.

```python
def confirmation_gate(state):
    plan_summary = format_plan(state["plan"])
    approval = interrupt({"question": "Approve this plan?", "plan": plan_summary})
    if approval != "approved":
        return {"cancelled": True}
    return {}
```

## Pattern 3: Tool Approval for Irreversible Actions

For write operations that can't be undone: `create_invoice`, `send_email`, `charge_payment`.

```python
def create_invoice_with_approval(tool_input):
    approval = interrupt({
        "action": "create_invoice",
        "preview": format_invoice(tool_input),
        "warning": "This will send the invoice to the customer."
    })
    if approval == "confirmed":
        return actually_create_invoice(tool_input)
    return {"cancelled": True}
```

**Rule:** any tool that triggers an external side-effect with no undo should go through this pattern.

## Pattern 4: Time-Travel — Replay and Fork

**Replay:** re-execute the graph from a prior checkpoint. Use for fault recovery.

```python
# Resume from last good checkpoint
config = {"configurable": {"thread_id": "session-123", "checkpoint_id": last_good_id}}
graph.invoke(None, config)
```

**Fork:** branch from a checkpoint with modified state. Use for A/B testing or safe exploration without touching the original thread.

```python
# Fork from checkpoint with corrected state
forked_config = {"configurable": {"thread_id": "session-123-fork", "checkpoint_id": checkpoint_id}}
graph.invoke({"corrected_field": new_value}, forked_config)
```

## Pattern 5: Try-Agent History (Prevent Re-routing)

Prevents infinite loops where the supervisor re-routes to an agent that already failed in the same turn.

```python
class SupervisorState(TypedDict):
    tried_agents: list[str]

def supervisor_node(state):
    intent = classify(state["messages"])
    candidates = get_agents_for_intent(intent)
    available = [a for a in candidates if a not in state["tried_agents"]]
    if not available:
        return escalate_to_human(state)
    chosen = available[0]
    return {"next_agent": chosen, "tried_agents": state["tried_agents"] + [chosen]}
```

## LangGraph HITL Summary

| Pattern | Use case | Interrupt type |
|---|---|---|
| Static breakpoints | Mandatory review gates | Compile-time |
| Dynamic `interrupt()` | Condition-triggered review | Runtime |
| Clarification loop | Intent ambiguity | Dynamic, budget-bounded |
| Scheduler gate | Multi-step plan approval | Dynamic |
| Tool approval | Irreversible write actions | Dynamic per-tool |
| Time travel / replay / fork | Fault recovery, A/B | Checkpointer |

## See Also
- [[LangGraph Advanced Patterns]]
- [[LangGraph CRAG Pipeline]]
- [[Plan and Execute Pattern]]
- [[ADK Context Engineering]]
