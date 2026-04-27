# HITL and Interrupts for VA Agents

**Sources:** langgraph_Yan.pptx, langgraph_extended.pptx, rag_poc (query_clarify_node.py, confirm_node), librarian wiki (plan-and-execute-pattern.md)

---

## Two Interrupt Modes

LangGraph provides two distinct interrupt mechanisms with different trade-offs.

### Static Breakpoints (before/after node boundaries)

Declared at graph compile time. Fires before or after an entire node completes.

```python
graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["executor"],      # pause before node runs
    interrupt_after=["planner"],        # pause after node completes
)
```

**When to use:**
- Approval gate before irreversible actions (before executor)
- Review of a generated plan before execution starts
- Predictable, well-defined pause points
- Simpler to reason about — always fires at the same structural location

**Trade-off:** coarse. You pause the entire node, not a specific condition within it.

### Dynamic `interrupt()` (mid-execution, inside a node)

Called programmatically inside a node. Fires only when a condition is met.

```python
from langgraph.types import interrupt

def confirm_plan_node(state: AgentState) -> AgentState:
    plan = state["plan"]
    
    # Only interrupt if the plan touches financial data
    if any(step.tool in HIGH_RISK_TOOLS for step in plan.steps):
        user_response = interrupt({
            "type": "confirm_plan",
            "plan": [s.description for s in plan.steps],
            "risk_level": "high",
        })
        if user_response != "approved":
            raise ValueError("Plan rejected by user")
    
    return state
```

**Resume after interrupt:**
```python
# User approves via API
graph.invoke(Command(resume="approved"), config={"configurable": {"thread_id": thread_id}})
```

**When to use:**
- Conditional approval (only interrupt when risk threshold met)
- Clarification loops (ask only when info is genuinely missing)
- Precise control over interrupt timing within complex node logic

**Trade-off:** harder to test — interrupt condition logic is inside node code.

---

## HITL Clarification with Bounded Budget

From rag_poc's `query_clarify_node`. For task execution agents that need to ask clarifying questions before acting.

### The Problem
An unbounded clarification loop can be exploited (prompt injection causes infinite questioning) or just annoying (agent asks 10 questions for a simple task).

### Pattern: Budget-Bounded Clarification

```python
MAX_CLARIFICATION_ROUNDS = 2  # never ask more than 2 follow-ups

class AgentState(TypedDict):
    messages: list[BaseMessage]
    clarification_rounds: int          # tracks budget
    clarification_complete: bool
    task_plan: TaskPlan | None

def clarify_node(state: AgentState, llm) -> dict:
    if state["clarification_rounds"] >= MAX_CLARIFICATION_ROUNDS:
        # Budget exhausted — proceed with best-effort interpretation
        return {"clarification_complete": True}
    
    missing = detect_missing_info(state["messages"])
    if not missing:
        return {"clarification_complete": True}
    
    question = interrupt({
        "type": "clarification",
        "question": missing.question,
        "round": state["clarification_rounds"] + 1,
        "max_rounds": MAX_CLARIFICATION_ROUNDS,
    })
    
    return {
        "messages": state["messages"] + [HumanMessage(content=question)],
        "clarification_rounds": state["clarification_rounds"] + 1,
    }

def should_clarify(state: AgentState) -> str:
    if state["clarification_complete"]:
        return "plan"
    return "clarify"
```

### Scheduler Confirmation Gate

After planning (but before execution), show the full plan for explicit approval:

```python
def schedule_confirm_node(state: AgentState) -> dict:
    plan = state["task_plan"]
    
    response = interrupt({
        "type": "confirm_execution",
        "steps": [{"tool": s.tool, "description": s.description} for s in plan.steps],
        "estimated_api_calls": len(plan.steps),
        "irreversible": any(s.irreversible for s in plan.steps),
    })
    
    if response == "rejected":
        return {"task_cancelled": True}
    return {}  # proceed to executor
```

**Full flow:**
```
User task → clarify (≤2 rounds) → planner → confirm gate → executor
```

---

## Time Travel and Fork Patterns

Distinct from HITL approval — used for debugging, safe experimentation, and fault recovery.

### Replay (Fault Recovery)

Re-execute from a prior checkpoint with the same state. Used when a node fails mid-execution and you want to retry from a known-good point without restarting the whole conversation.

```python
# Get the checkpoint history
history = list(graph.get_state_history(config))

# Find the checkpoint just before the failure
checkpoint_before_failure = history[2]  # or search by step/timestamp

# Replay from that checkpoint
result = graph.invoke(
    None,  # no new input — replay existing state
    config={"configurable": {
        "thread_id": thread_id,
        "checkpoint_id": checkpoint_before_failure.config["configurable"]["checkpoint_id"]
    }}
)
```

**When to use:** node raises an exception mid-execution, external API times out, transient failure.

### Fork (A/B Testing / Safe Exploration)

Branch from a prior checkpoint with **modified state**. The original thread is preserved; the fork runs independently. Useful for testing alternative routing decisions or debugging without affecting production state.

```python
# Fork from checkpoint with modified state
fork_config = graph.update_state(
    config={"configurable": {
        "thread_id": thread_id,
        "checkpoint_id": target_checkpoint_id
    }},
    values={"routing_decision": "alternative_agent"},  # modified state
    as_node="router"
)

# Run the fork
fork_result = graph.invoke(None, config=fork_config)
```

**When to use:**
- A/B test different agent routing decisions on real conversation snapshots
- Debug a bad routing decision without affecting the live thread
- Explore "what if we had routed differently" counterfactuals

---

## Approval Pattern for Irreversible Actions

Standard pattern for billing, email sending, invoice creation — any action the user can't undo.

```python
IRREVERSIBLE_TOOLS = {"create_invoice", "send_email", "delete_customer", "charge_payment"}

def should_require_approval(tool_name: str, args: dict) -> bool:
    return tool_name in IRREVERSIBLE_TOOLS

async def tool_approval_node(state: AgentState) -> dict:
    pending = state["pending_tool_call"]
    
    if not should_require_approval(pending["tool"], pending["args"]):
        return {"approved": True}
    
    response = interrupt({
        "type": "tool_approval",
        "tool": pending["tool"],
        "args": pending["args"],
        "consequence": TOOL_CONSEQUENCES[pending["tool"]],
    })
    
    return {"approved": response == "approved"}
```

---

## LangGraph HITL Architecture Summary

```
static breakpoints  →  coarse, compile-time, always fires
dynamic interrupt() →  precise, runtime, conditional
clarification loop  →  bounded budget (≤2 rounds), detects missing info
scheduler gate      →  full plan review before irreversible execution
tool approval gate  →  per-tool, irreversible-action filter
time travel/replay  →  fault recovery from checkpoint
fork                →  safe exploration / A-B testing
```

---

## See Also
- [memory-architecture.md](memory-architecture.md) — episodic store for logging approved/rejected plans
- [guardrails-pipeline.md](guardrails-pipeline.md) — deterministic pre-LLM safety gates (run before any HITL)
- [orchestration-patterns.md](orchestration-patterns.md) — where HITL fits in the supervisor graph
- librarian wiki: `Plan and Execute Pattern` — HITL confirmation gate implementation
