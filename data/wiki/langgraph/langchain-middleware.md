---
title: LangChain Agent Middleware
tags: [langgraph, llm, pattern]
summary: LangChain's create_agent() middleware API — HumanInTheLoopMiddleware for tool-call approval, wrap_tool_call/before_model/after_model hooks for custom logic, and Command-based resume — the mechanism Framework Selection means when it says "LangGraph has no middleware."
updated: 2026-07-14
sources:
  - raw/agent-skills/langchain-middleware/SKILL.md
---

# LangChain Agent Middleware

[[Framework Selection — LangChain vs LangGraph vs Deep Agents]] notes that "LangGraph has no middleware — you wire behavior directly into nodes and edges." Middleware instead lives one layer down, on LangChain's `create_agent()` (see [[LangChain Fundamentals — create_agent, Tools, Structured Output]]), and one layer up, as the always-on middleware stack in [[Deep Agents Framework]] (`TodoListMiddleware`, `FilesystemMiddleware`, `SubAgentMiddleware`, etc.). All three share the same underlying concept — intercepting the agent loop — but apply to different agent constructors and are not interchangeable.

**Requirement:** every HITL middleware configuration requires a `checkpointer` + `thread_id` — state must persist across the interrupt/resume boundary.

## Human-in-the-Loop Middleware

```python
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import MemorySaver
from langchain.tools import tool

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email."""
    return f"Email sent to {to}"

agent = create_agent(
    model="gpt-4.1",
    tools=[send_email],
    checkpointer=MemorySaver(),  # Required for HITL
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "send_email": {"allowed_decisions": ["approve", "edit", "reject"]},
            }
        )
    ],
)
```

Per-tool policies are independent — different tools can require different approval levels:

```python
middleware=[
    HumanInTheLoopMiddleware(
        interrupt_on={
            "send_email": {"allowed_decisions": ["approve", "edit", "reject"]},
            "delete_email": {"allowed_decisions": ["approve", "reject"]},  # No edit
            "read_email": False,  # No HITL for reading
        }
    )
]
```

## Running With Interrupts — Resume Patterns

```python
from langgraph.types import Command

config = {"configurable": {"thread_id": "session-1"}}

result1 = agent.invoke({
    "messages": [{"role": "user", "content": "Send email to john@example.com"}]
}, config=config)

if "__interrupt__" in result1:
    print(f"Waiting for approval: {result1['__interrupt__']}")

# Approve
result2 = agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}), config=config)

# Edit before approving — edited_action must include name + args
result2 = agent.invoke(
    Command(resume={"decisions": [{
        "type": "edit",
        "edited_action": {"name": "send_email", "args": {"to": "alice@company.com", ...}},
    }]}),
    config=config,
)

# Reject with feedback
result2 = agent.invoke(
    Command(resume={"decisions": [{"type": "reject", "feedback": "Cannot delete without manager approval"}]}),
    config=config,
)
```

This `Command(resume=...)` protocol is identical to the one used by [[Deep Agents Framework]]'s `interrupt_on` and [[LangGraph Advanced Patterns]]'s dynamic `interrupt()` — approve/edit/reject is the shared vocabulary across all three layers.

## Custom Middleware Hooks

Six decorator hooks, two patterns:

- **Wrap hooks** (`wrap_tool_call`, `wrap_model_call`): `(request, handler)` signature — call `handler(request)` to proceed, or return early to short-circuit. **Do not use `yield`** inside a wrap hook — it turns the function into a generator and raises `NotImplementedError`.
- **Before/after hooks** (`before_model`, `after_model`, `before_agent`, `after_agent`): `(state, runtime)` signature — inspect or modify state; return `None` or a dict of state updates.

```python
from langchain.agents.middleware import wrap_tool_call, before_model, after_model

@wrap_tool_call
def retry_middleware(request, handler):
    for attempt in range(3):
        try:
            return handler(request)
        except Exception:
            if attempt == 2:
                raise

@wrap_tool_call
def guard_middleware(request, handler):
    if request.tool_call["name"] == "dangerous_tool":
        return "This tool is disabled"  # short-circuit
    return handler(request)

@before_model
def log_calls(state, runtime):
    print(f"Calling model with {len(state['messages'])} messages")

@after_model
def check_output(state, runtime):
    print("Model responded")
```

## Boundaries

**Can configure:** which tools require approval, allowed decisions per tool, `before_model`/`after_model`/`wrap_tool_call`/`before_agent`/`after_agent` hooks, tool-specific middleware.

**Cannot configure:** interrupting *after* tool execution (must be before), skipping the checkpointer requirement for HITL.

## Common Mistakes

- **Missing checkpointer:** `HumanInTheLoopMiddleware` requires `checkpointer=MemorySaver()` (or a production checkpointer) — without it, state can't survive the interrupt.
- **Missing `thread_id`:** always pass `config={"configurable": {"thread_id": "..."}}` when using HITL.
- **Wrong resume syntax:** resume via `agent.invoke(Command(resume={...}), config=config)` — passing a plain dict (`agent.invoke({"resume": {...}})`) does not resume the interrupt.

## See Also
- [[Graph Topology Primitives]] <!-- auto-linked -->
- [[Harness Engineering]] <!-- auto-linked -->
- [[Framework Selection — LangChain vs LangGraph vs Deep Agents]]
- [[LangChain Fundamentals — create_agent, Tools, Structured Output]]
- [[Deep Agents Framework]]
- [[LangGraph Advanced Patterns]]
- [[HITL and Interrupt Patterns]]
