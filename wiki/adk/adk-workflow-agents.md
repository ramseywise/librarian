---
title: ADK Workflow Agents
tags: [adk, pattern]
summary: ADK's three deterministic workflow agents — Sequential, Parallel, and Loop — which provide control flow without LLM orchestration.
updated: 2026-07-05
sources:
  - raw/claude-docs/galactus/.agents/skills/adk-cheatsheet/references/python.md
---

# ADK Workflow Agents

ADK provides three **workflow agents** for deterministic control flow that doesn't require LLM reasoning. Unlike `LlmAgent`, these execute sub-agents in a fixed pattern without model calls for orchestration decisions.

This is the key distinction from `LlmAgent`-based orchestration: workflow agents are deterministic and cheaper (no orchestration LLM calls), while `LlmAgent` routing is flexible but non-deterministic.

---

## SequentialAgent

Executes sub-agents in order. State changes from earlier agents are visible to later agents via `session.state`.

```python
from google.adk.agents import SequentialAgent, Agent

summarizer = Agent(
    name="summarizer",
    model="gemini-3-flash-preview",
    instruction="Summarize the input.",
    output_key="summary"     # writes to state["summary"]
)

question_gen = Agent(
    name="question_generator",
    model="gemini-3-flash-preview",
    instruction="Generate questions based on: {summary}"  # reads state["summary"]
)

pipeline = SequentialAgent(
    name="pipeline",
    sub_agents=[summarizer, question_gen],
)
```

**Data flow:** via conversation history and `output_key` state. The downstream agent sees both the history and any state keys set by upstream agents.

---

## ParallelAgent

Executes sub-agents concurrently. Reduces latency when sub-tasks are independent.

**Critical:** use distinct `output_key` values to avoid race conditions — concurrent agents writing to the same key produce undefined results.

```python
from google.adk.agents import ParallelAgent, SequentialAgent, Agent

fetch_a = Agent(name="fetch_a", ..., output_key="data_a")
fetch_b = Agent(name="fetch_b", ..., output_key="data_b")

merger = Agent(
    name="merger",
    instruction="Combine data_a: {data_a} and data_b: {data_b}"
)

pipeline = SequentialAgent(
    name="full_pipeline",
    sub_agents=[
        ParallelAgent(name="fetchers", sub_agents=[fetch_a, fetch_b]),
        merger   # runs after both fetchers complete
    ]
)
```

---

## LoopAgent

Repeats sub-agents until either `max_iterations` is reached or any sub-agent emits an event with `escalate=True`.

```python
from google.adk.agents import LoopAgent

refinement_loop = LoopAgent(
    name="refinement_loop",
    sub_agents=[evaluator, refiner, escalation_checker],
    max_iterations=5,
)
```

**Stopping the loop** — use a `BaseAgent` that inspects state and escalates:

```python
from google.adk.agents import BaseAgent
from google.adk.events import Event, EventActions

class EscalationChecker(BaseAgent):
    async def _run_async_impl(self, ctx):
        result = ctx.session.state.get("evaluation")
        if result and result.get("grade") == "pass":
            yield Event(author=self.name, actions=EventActions(escalate=True))
        else:
            yield Event(author=self.name)
```

**Typical loop pattern:** `[evaluator_agent, refiner_agent, escalation_checker]`. The evaluator writes a grade to state; the checker reads it and escalates when done; the refiner runs only if not yet passed.

---

## When to Use Which

| Pattern | Use When |
|---|---|
| `SequentialAgent` | Steps have strict ordering and data dependencies |
| `ParallelAgent` | Independent sub-tasks that can run concurrently |
| `LoopAgent` | Iterative refinement with a convergence condition |
| `LlmAgent` with `sub_agents` | Routing logic requires reasoning about which path to take |

**Composability:** workflow agents compose freely. A `SequentialAgent` can contain a `ParallelAgent` followed by a merger agent, which itself could be a `LoopAgent`.

---

## See Also

- [[ADK Python API Reference]]
- [[ADK Context Engineering]]
- [[Multi-Agent Orchestration Patterns]]
- [[Send API Fan-out]]
