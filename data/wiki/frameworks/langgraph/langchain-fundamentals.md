---
title: LangChain Fundamentals — create_agent, Tools, Structured Output
tags: [frameworks, langgraph, llm, concept]
summary: LangChain 1.0's core agent-building primitives — the create_agent() loop, the @tool decorator, checkpointer-based persistence, and structured output — a framework that runs on the LangGraph runtime, over integration packages that sit beneath both.
updated: 2026-11-19
sources:
  - data/raw/agent-skills/langchain-fundamentals/SKILL.md
  - data/raw/papers/2026-11-07-learning-langchain-ch01-llm-fundamentals-with-langchain.md
---

# LangChain Fundamentals — create_agent, Tools, Structured Output

LangChain spans two layers of the [[Framework Selection — LangChain vs LangGraph vs Deep Agents]] stack. Its integration packages (models, tools, prompts) sit beneath LangGraph and Deep Agents. Its LangChain 1.0 agent loop, `create_agent()`, is built on top of the LangGraph runtime.

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

## Runnables and composition (Learning LangChain, ch. 1)

Oshin and Campos describe the Runnable interface as three methods: `invoke` turns one input into one output, `batch` turns several inputs into several outputs efficiently, and `stream` yields output from a single input as it is produced. Two composition styles sit on top of it. Imperative composition calls components directly (`model.invoke(...)` inside a function decorated with `@chain`); declarative composition uses LangChain Expression Language, as in `chatbot = template | model`. Their comparison table says that parallel execution, streaming and async need hand-written code in the imperative style but come for free in the declarative one (LangChain Python and JS). They suggest imperative for custom logic and declarative for wiring up existing components with little customisation.

Their other advice for model calls:

- The usual parameters are `model`, `temperature` and `max_tokens`; setting `max_tokens` too low can cut the output off.
- Temperature: around 0.1 for structured output, around 0.9 for creative writing.
- `with_structured_output` accepts a Pydantic or Zod schema and checks the output against it; output parsers handle formats like CSV or XML and provide format instructions.
- Begin a new application from LangChain's prebuilt patterns, then see whether their results are good enough as they come.

## Limits

- The ch. 1 listings use gpt-3.5-turbo and early-2025 imports; the Runnable example takes `ChatOpenAI` from `langchain_openai.llms`, which the extraction marks as the wrong module, and some listings are cut off.
- Nothing is measured, so the automatic parallelism, streaming and async of the declarative style come with no latency or cost data.

## See Also
- [[Graph Topology Primitives]] <!-- auto-linked -->
- [[Deep Agents Memory Backends]] <!-- auto-linked -->
- [[Framework Selection — LangChain vs LangGraph vs Deep Agents]]
- [[LangChain Agent Middleware]]
- [[LangChain Dependency Management]]
- [[LangChain RAG Implementation Patterns]]
- [[Deep Agents Framework]]
- [[LangGraph Advanced Patterns]]
- [[LangGraph Platform Data Model and Double-Texting]] — extends (hosted deployment of the same graphs)
