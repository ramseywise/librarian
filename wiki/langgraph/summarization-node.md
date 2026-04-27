---
title: Summarization Node
tags: [langgraph, context-management, concept]
summary: A LangGraph node that compresses conversation history when it exceeds a trigger threshold — keeps context window usage bounded while preserving conversational continuity.
updated: 2026-04-24
sources:
  - raw/playground-docs/librarian-stack-audit.md
  - raw/playground-docs/adk-samples-patterns-analysis.md
---

# Summarization Node

A conditional node that fires when message history exceeds a threshold. Summarizes older turns with Haiku, replaces them with a single `SystemMessage` containing the summary, and retains the most recent N turns verbatim. Identical pattern appears in LangGraph agents and ADK agents (called "History Compaction" in ADK context).

## Parameters

| Parameter | Typical value | Purpose |
|---|---|---|
| Trigger threshold | 8 messages | When to summarize |
| Overlap (keep recent) | 4 messages | Verbatim turns retained after summary |
| Model | Haiku | Cost-efficient for summarization |

## Implementation

```python
def summarization_node(state: AgentState) -> AgentState:
    if len(state["messages"]) < TRIGGER_THRESHOLD:
        return state

    to_summarize = state["messages"][:-OVERLAP]
    recent = state["messages"][-OVERLAP:]

    summary = haiku.invoke([
        SystemMessage("Summarize this conversation concisely, preserving key decisions and context."),
        *to_summarize
    ])

    return {
        "messages": [
            SystemMessage(f"[Conversation summary]: {summary.content}"),
            *recent
        ]
    }
```

## Contrast with History Pruning

History pruning removes tool response messages from history before each LLM call (reducing noise). Summarization replaces *multiple turns* with a single compressed summary. They solve different problems:

- Pruning: remove low-value messages (old tool outputs)
- Summarization: compress high-value messages (decisions, context) that no longer fit

## Cross-Framework

The same trigger/overlap pattern (8 messages, 4 overlap) appears in both LangGraph agents and ADK agents ([[ADK Context Engineering]] calls it "History Compaction Node"). The implementation differs; the design is identical.

## Relationship to Prefix Caching

The summarized `SystemMessage` prepended to history is a candidate for [[Prefix Caching]] if its content is stable across turns. However, since the summary evolves with each compression cycle, caching only helps within a single session.

## See Also
- [[Agent Memory Types]]
- [[ADK Context Engineering]]
- [[HistoryCondenser]]
- [[Prefix Caching]]
- [[LangGraph Advanced Patterns]]
