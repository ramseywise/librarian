---
title: ReAct Pattern
tags: [langgraph, adk, concept, pattern]
summary: Reasoning + Acting loop — the foundational single-agent pattern where the LLM alternates thought and tool calls until it has enough information to answer. Implemented via create_react_agent in LangGraph.
updated: 2026-04-26
sources:
  - raw/claude-docs/playground/docs/research/evaluation-and-learning/self-learning-agents.md
---

# ReAct Pattern

## What It Is

ReAct (Reasoning + Acting) is the foundational single-agent inference loop. The agent alternates between reasoning (Thought) and acting (Action/tool call) until it has enough information to answer.

```
Thought: I need to find the invoice for customer X
Action: search_invoices(customer="X")
Observation: Found 3 invoices — #1042, #1043, #1044
Thought: The user asked for the latest, so #1044
Action: get_invoice(invoice_id="1044")
Observation: Invoice #1044, 500 EUR, due 2026-05-01
Thought: I have all the info. Ready to answer.
Answer: Invoice #1044 for 500 EUR is due May 1, 2026.
```

## LangGraph Implementation

A single agent node that loops via conditional edges until no more tool calls are pending.

```python
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(
    model=llm,
    tools=[get_invoice, list_invoices, create_invoice],
    checkpointer=checkpointer,
)
```

`create_react_agent` handles the loop internally — messages accumulate tool results, and the LLM is called again until it produces a final answer with no pending tool calls.

## When ReAct Is Sufficient

- 1–3 tool calls per turn
- Well-defined, atomic tasks
- Low-stakes queries
- The task doesn't require explicit multi-step planning with failure recovery

## When ReAct Breaks Down

- 5+ tool calls in sequence where ordering matters
- Partial failure mid-sequence causes inconsistent state (e.g., invoice created but email not sent)
- The LLM needs to make a plan and verify each step before executing

For these cases, use the [[Plan and Execute Pattern]] — an explicit planning step before action reduces errors in multi-step workflows.

## ReAct in Multi-Agent Context

In a supervisor multi-agent topology, each domain subagent is typically a ReAct loop. The supervisor routes to the right subagent, which then handles its own Thought/Action cycles independently. See [[Multi-Agent Orchestration Patterns]] for the routing layer.

## ReAct as the MVP Starting Point

ReAct is the correct foundation for any new agent. From [[Self-Learning Agents]] maturity stack:

| Stage | What to add |
|-------|------------|
| **MVP** | ReAct loop + CoT in system prompt |
| **Beta** | Self-critique on high-stakes outputs |
| **Production** | Reflection + procedural memory |

Only graduate beyond ReAct when you have evidence that it's breaking down.

## See Also
- [[Plan and Execute Pattern]]
- [[Chain of Thought]]
- [[Self-Learning Agents]]
- [[Multi-Agent Orchestration Patterns]]
- [[LangGraph Advanced Patterns]]
