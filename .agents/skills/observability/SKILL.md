---
name: observability
description: >
  Agent observability patterns — LangFuse, LangSmith, Cloud Trace, BigQuery agent analytics.
  Use when adding tracing, evaluation datasets, latency monitoring, or cost tracking to any agent stack.
metadata:
  domains: [infra, eval, adk, langgraph]
---

# Observability

Instrumentation patterns for production agent systems. Covers both Google Cloud native (ADK) and LangChain ecosystem (LangGraph/LangChain) observability stacks.

## Stack Mapping

| Project | Observability stack | Notes |
|---------|--------------------|-|
| ADK agents | Cloud Trace + Cloud Logging + BigQuery | Native; zero config with Agent Engine |
| LangGraph / LangChain | LangSmith (traces + datasets) or LangFuse (open source) | Both require explicit instrumentation |
| rag_poc + playground | LangSmith (configured, not always active) | Add `LANGSMITH_API_KEY` to `.env` |

## LangFuse Integration

```python
from langfuse.decorators import observe, langfuse_context

@observe()
def agent_node(state: AgentState) -> AgentState:
    langfuse_context.update_current_observation(
        input=state["messages"][-1].content,
        metadata={"intent": state.get("intent")},
    )
    ...
```

LangFuse auto-traces LangChain/LangGraph when `LANGFUSE_PUBLIC_KEY` + `LANGFUSE_SECRET_KEY` are set and `langfuse` is imported before the chain runs.

## LangSmith Integration

```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "..."
os.environ["LANGCHAIN_PROJECT"] = "librarian-rag"
```

Enables automatic tracing for all LangChain/LangGraph runs in the process. View traces at `smith.langchain.com`.

## ADK — Cloud Trace

ADK agents deployed to Agent Engine emit Cloud Trace spans automatically. Key span names:
- `agent_run` — full turn
- `llm_call` — model invocation with token counts
- `tool_call_{name}` — individual tool execution

Access via Cloud Trace UI or export to BigQuery for analysis.

## BigQuery Agent Analytics

See `adk-observability-guide/references/bigquery-agent-analytics.md` for the full SQL reference. Key queries:
- P50/P95/P99 latency per agent
- Tool call success rates
- Token usage by model and session

## Eval Datasets in LangSmith

```python
from langsmith import Client

client = Client()
dataset = client.create_dataset("librarian-golden-set")
client.create_examples(
    inputs=[{"question": q} for q in questions],
    outputs=[{"answer": a} for a in answers],
    dataset_id=dataset.id,
)
```

## References

| File | Contents |
|------|----------|
| `references/langfuse-setup.md` | Full LangFuse config, dashboard setup, custom metrics |
| `references/langsmith-datasets.md` | Dataset creation, run evaluation, CI integration |

> **References not yet populated.** Will be filled from wiki pages after ingest of observability-tagged content.
