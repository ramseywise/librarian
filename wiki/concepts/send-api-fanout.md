---
title: Send API Fan-out
tags: [langgraph, concept]
summary: LangGraph's Send API enables dynamic map-reduce parallelism — fan out to N workers at runtime without knowing N at graph compile time.
updated: 2026-04-24
sources:
  - raw/playground-docs/librarian-stack-audit.md
---

# Send API Fan-out

LangGraph's `Send` primitive dispatches multiple copies of a node in parallel, each with different input state. Unlike static graph edges (fixed at compile time), `Send` determines how many parallel branches to create at runtime based on the current state.

## The Pattern

```python
from langgraph.types import Send

def fan_out(state: State) -> list[Send]:
    return [
        Send("process_chunk", {"chunk": chunk, "query": state["query"]})
        for chunk in state["chunks"]
    ]

graph.add_conditional_edges("split", fan_out)
graph.add_node("process_chunk", process_chunk_node)
graph.add_edge("process_chunk", "merge")
```

`fan_out` returns a list of `Send` objects — one per parallel branch. Each branch runs `process_chunk` with its own state slice. All branches join at `merge`.

## Use Cases

| Use case | How |
|---|---|
| Parallel document processing | One branch per retrieved chunk |
| Multi-query retrieval | One branch per query reformulation |
| Parallel tool execution | One branch per tool call |
| Section-based generation | One branch per document section |

## Contrast with Static Parallelism

Static branches (added at graph compile time) run a fixed set of nodes in parallel. `Send` is for cases where the number of parallel branches depends on runtime data — e.g., "process all retrieved chunks" where chunk count varies per query.

## State Merge

After all branches complete, state is merged at the join node. By default, fields are merged using their type annotations — lists are concatenated, values are last-write-wins. Use `Annotated[list, operator.add]` in the TypedDict to ensure list concatenation rather than replacement.

## See Also
- [[LangGraph Advanced Patterns]]
- [[Agentic Workflow Patterns]] — Parallelization / Sectioning pattern
- [[Librarian RAG Architecture]]
