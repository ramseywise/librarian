---
title: LangGraph State Reducers
tags: [langgraph, concept]
summary: Functions that define how parallel node outputs merge into shared state — preventing collisions when multiple nodes write to the same field simultaneously.
updated: 2026-04-25
sources:
  - raw/gdrive/2026-04-24-langgraph-yan.md
  - raw/agent-skills/langgraph-fundamentals/SKILL.md
  - raw/agent-skills/langgraph-persistence/SKILL.md
---

# LangGraph State Reducers

A reducer is a function attached to a state field that defines **how updates are merged** when multiple nodes write to it — especially during parallel super-steps. Without reducers, parallel nodes would silently overwrite each other's results.

## The Problem

When nodes run in parallel (a super-step), they each return a partial state update. LangGraph needs a rule for combining them. The default is last-write-wins — fine for scalar flags, destructive for lists.

## Reducer Types

| Reducer | Behaviour | Best For |
|---|---|---|
| Default (overwrite) | Last write wins | Simple flags, status fields — only the final update survives |
| `operator.add` | Appends to a list; every node's output is kept | Raw message lists, tool result accumulation |
| `add_messages` | Smart append for chat — deduplicates by message ID, handles updates correctly | All `messages` fields in conversational agents |
| Custom function | Write any merge logic: sum numbers, pick max score, merge dicts | Domain-specific merges |

## Declaring Reducers

```python
from typing import Annotated
from operator import add
from langgraph.graph import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]   # smart append, dedup by id
    scores: Annotated[list[float], add]        # accumulate all scores
    status: str                                 # overwrite (default)
    best_score: Annotated[float, max]          # custom: keep highest
```

## Super-Steps and Reducers

A **super-step** is a batch of parallel node executions that complete before the graph moves forward. Reducers run after every super-step to merge the partial updates into a single consistent state.

```
super-step: [retriever_A, retriever_B, retriever_C] run in parallel
            ↓ each returns {"chunks": [...]}
reducer:    operator.add merges all three chunk lists
            ↓
next node receives merged state with all chunks
```

See [[Send API Fan-out]] for the fan-out pattern that produces super-steps dynamically.

## `add_messages` vs `operator.add`

Prefer `add_messages` for any field holding `BaseMessage` objects. It handles:
- Deduplication by `message.id` — safe to retry nodes without duplicating messages
- Updates — if a message with the same ID arrives, it replaces the old one

`operator.add` is simpler and better for plain data (floats, dicts, raw strings).

## Overwrite — Bypassing Reducers in update_state

`update_state()` passes values through reducers. To **replace** a list field instead of appending, use `Overwrite`:

```python
from langgraph.types import Overwrite

# State: items: Annotated[list, operator.add]
# Current: {"items": ["A", "B"]}

graph.update_state(config, {"items": ["C"]})          # Result: ["A", "B", "C"] — appended
graph.update_state(config, {"items": Overwrite(["C"])})  # Result: ["C"] — replaced
```

## Five-Step Graph Design

When building a new graph:

1. **Map discrete steps** — sketch a flowchart; each step becomes a node
2. **Categorize nodes** — LLM step, data step, action step, or user input step
3. **Design state** — shared memory for all nodes; store raw data, format inside nodes
4. **Build nodes** — each takes state, returns a partial dict of only the fields it updates
5. **Wire it together** — connect with edges, add conditional routing, compile with checkpointer if needed

## Subgraph Checkpointer Scoping

When compiling a subgraph, `checkpointer` controls persistence behavior:

| Mode | Interrupts | Multi-turn memory | Use when |
|---|---|---|---|
| `checkpointer=False` | No | No | Subgraph needs neither |
| `None` (default) | Yes | No | Subgraph needs `interrupt()` but starts fresh each call |
| `checkpointer=True` | Yes | Yes | Subgraph needs to remember across invocations |

**Warning:** stateful subgraphs (`checkpointer=True`) cannot be called multiple times within a single node — they write to the same checkpoint namespace and conflict. Wrap each in its own `StateGraph` with a unique node name for isolation.

## See Also
- [[LangGraph Advanced Patterns]]
- [[Send API Fan-out]]
- [[LangGraph BaseStore]]
