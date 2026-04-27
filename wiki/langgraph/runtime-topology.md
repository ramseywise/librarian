---
title: Runtime Topology and Checkpointer Alignment
tags: [infra, langgraph, concept]
summary: Critical rule — checkpointer backend must match runtime hosting model. MemorySaver fails silently in Lambda and multi-worker deployments. Covers trigger patterns, observability tool choice (LangSmith vs Langfuse/GDPR), and key production signals.
updated: 2026-04-26
sources:
  - raw/claude-docs/playground/docs/research/evaluation-and-learning/observability-and-runtime.md
---

# Runtime Topology and Checkpointer Alignment

## Critical Rule

**Your checkpointer backend must match your runtime hosting model.** `MemorySaver` in a multi-worker or serverless deployment silently loses state between invocations — no error, just broken sessions.

| Runtime | Required checkpointer |
|---------|----------------------|
| **Lambda / serverless** | External DB (Postgres, DynamoDB) — MemorySaver loses state between invocations |
| **Long-lived worker** (Gunicorn, Uvicorn) | MemorySaver viable for dev; Postgres for prod multi-worker |
| **LangGraph Cloud** | Platform-managed — no config needed |
| **Kubernetes pod** | External DB (Postgres) — pods may restart |

```python
# Local dev
from langgraph.checkpoint.memory import MemorySaver
checkpointer = MemorySaver()

# Production
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
async with AsyncPostgresSaver.from_conn_string(DATABASE_URL) as checkpointer:
    await checkpointer.setup()
    graph = builder.compile(checkpointer=checkpointer)
```

**Never use MemorySaver in a multi-worker deployment** — each worker has its own in-memory state; thread history won't be shared across workers.

## Trigger Patterns

VA agents can be triggered in four ways:

| Trigger | Description | Latency expectation |
|---------|-------------|---------------------|
| **HTTP/API** | Direct REST call to agent endpoint | p50 < 2s |
| **Webhook/Event** | External service pushes an event | Near-real-time |
| **Message Queue** | Kafka/SQS message triggers agent | Seconds to minutes |
| **Cron/Schedule** | Time-based trigger | Defined interval |

Runtime topology must match the trigger. A cron trigger that assumes a long-lived worker will fail in serverless.

## Observability Tool Choice: LangSmith vs Langfuse

| Dimension | LangSmith | Langfuse |
|-----------|----------|---------|
| **Integration** | Native for LangChain/LangGraph — zero config | Manual wiring, framework-agnostic |
| **Data residency** | US/EU regions on Langchain Inc cloud | Self-host = your infra, full control |
| **Vendor lock-in** | High | Low — open source, portable data |
| **GDPR** | Data sent to Langchain Inc (check DPA) | Self-host = no external data transfer |
| **Cost** | Usage-based | Self-host = infra cost only |

**For EU/GDPR context (Shine/Billy): Langfuse self-hosted is the safer default.** See [[ADK vs LangGraph Comparison]] for the prior decision record.

### Env-Var Swap Pattern (no code changes)

```python
def setup_observability():
    if os.getenv("LANGSMITH_API_KEY"):
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
    if os.getenv("LANGFUSE_PUBLIC_KEY"):
        from langfuse.callback import CallbackHandler
        return CallbackHandler()
    return None
```

```bash
# .env.example
OBSERVABILITY_BACKEND=langfuse       # langfuse | langsmith | none
CHECKPOINT_BACKEND=postgres          # postgres | memory
```

## Thread ID Propagation (MCP Tool Calls)

When an agent calls external services via MCP, the trace ID must flow through:

```python
async def call_mcp_tool(tool_name: str, args: dict, trace_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{MCP_SERVER_URL}/tools/{tool_name}",
            json=args,
            headers={"X-Trace-Id": trace_id, "X-Session-Id": session_id},
        )
    return response.json()
```

## Key Production Signals to Monitor

| Signal | What to watch |
|--------|---------------|
| Routing accuracy | % of turns routed to wrong subagent |
| Tool call latency | p95 tool call time per tool |
| Context window usage | Turns approaching max tokens |
| Guardrail hit rate | % of turns blocked by each guardrail stage |
| HITL approval rate | % of plans approved vs rejected |
| Session memory load time | Time to load three-tier memory at turn start |

### Structlog Pattern (Standard in Workspace)

```python
log.info(
    "agent.routed",
    user_id=state["user_id"],
    session_id=state["session_id"],
    intent=chosen,
    tried_agents=state.get("tried_agents", []),
)
```

## See Also
- [[LangGraph Advanced Patterns]]
- [[Production Hardening Patterns]]
- [[Agent Memory Types]]
- [[Multi-Agent Orchestration Patterns]]
