---
title: LangChain Fundamentals — create_agent, Tools, Structured Output
tags: [langgraph, llm, concept]
summary: LangChain 1.0's core agent-building primitives — the create_agent() loop, the @tool decorator, checkpointer-based persistence, and structured output — the foundation layer beneath LangGraph and Deep Agents.
updated: 2026-07-14
sources:
  - raw/agent-skills/langchain-fundamentals/SKILL.md
---

# LangChain Fundamentals — create_agent, Tools, Structured Output

LangChain is the foundation layer in the [[Framework Selection — LangChain vs LangGraph vs Deep Agents]] stack — models, tools, prompts, and (as of LangChain 1.0) a built-in agent loop via `create_agent()`. LangGraph and Deep Agents both sit on top of these primitives.

## create_agent() — The Recommended Agent Loop

`create_agent()` handles the agent loop, tool execution, and state management without hand-rolled ReAct wiring:

```python
from langchain.agents import create_agent
from langchain_core.tools import tool

@tool
def get_weather(location: str) -> str:
    """Get current weather for a location.

    Args:
        location: City name
    """
    return f"Weather in {location}: Sunny, 72F"

agent = create_agent(
    model="anthropic:claude-sonnet-4-5",
    tools=[get_weather],
    system_prompt="You are a helpful assistant."
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "What's the weather in Paris?"}]
})
print(result["messages"][-1].content)
```

| Parameter | Purpose | Example |
|---|---|---|
| `model` | LLM to use | `"anthropic:claude-sonnet-4-5"` or a model instance |
| `tools` | List of tools | `[search, calculator]` |
| `system_prompt` / `systemPrompt` | Agent instructions | `"You are a helpful assistant"` |
| `checkpointer` | State persistence | `MemorySaver()` |
| `middleware` | Processing hooks | see [[LangChain Agent Middleware]] |

`create_agent()` accepts model strings (`"anthropic:claude-sonnet-4-5"`, `"openai:gpt-4.1"`) or model instances for custom settings, e.g. `ChatAnthropic(model="claude-sonnet-4-5", temperature=0)`.

## Persistence Across Invocations

Without a checkpointer, the agent has no memory between `invoke()` calls. Add `MemorySaver` + `thread_id`:

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
agent = create_agent(model="anthropic:claude-sonnet-4-5", tools=[search], checkpointer=checkpointer)

config = {"configurable": {"thread_id": "user-123"}}
agent.invoke({"messages": [{"role": "user", "content": "My name is Alice"}]}, config=config)
result = agent.invoke({"messages": [{"role": "user", "content": "What's my name?"}]}, config=config)
# Agent remembers: "Your name is Alice"
```

This is the same `checkpointer` + `thread_id` contract used by [[LangGraph Advanced Patterns]] and [[Deep Agents Framework]] — `create_agent()`, raw LangGraph, and `create_deep_agent()` all share this persistence model.

## Tools — @tool Decorator

```python
from langchain_core.tools import tool

@tool
def add(a: float, b: float) -> float:
    """Add two numbers.

    Args:
        a: First number
        b: Second number
    """
    return a + b
```

Clear, specific docstrings matter — the agent uses the description to decide when to call the tool. A vague description (`"""Does stuff."""`) degrades tool selection quality.

## Structured Output

Get typed, validated agent responses via `response_format` (agent-level) or `with_structured_output()` (model-level, no agent needed):

```python
from langchain.agents import create_agent
from pydantic import BaseModel, Field

class ContactInfo(BaseModel):
    name: str
    email: str
    phone: str = Field(description="Phone number with area code")

agent = create_agent(model="gpt-4.1", tools=[search], response_format=ContactInfo)
result = agent.invoke({"messages": [{"role": "user", "content": "Find contact for John"}]})
print(result["structured_response"])  # ContactInfo(name='John', ...)
```

## Common Mistakes

- **No `recursion_limit`:** an unbounded agent loop can run forever. Set `config={"recursion_limit": 10}` on `invoke()`.
- **No checkpointer + thread_id:** the agent silently forgets everything between calls — no error, just no memory.
- **Reading `result.content` directly:** the agent result is a dict; the answer is `result["messages"][-1].content`, not `result.content`.
- **Vague tool descriptions:** hurts tool-selection accuracy; always document `Args:` in the tool docstring.

## See Also
- [[Framework Selection — LangChain vs LangGraph vs Deep Agents]]
- [[LangChain Agent Middleware]]
- [[LangChain Dependency Management]]
- [[LangChain RAG Implementation Patterns]]
- [[Deep Agents Framework]]
- [[LangGraph Advanced Patterns]]
