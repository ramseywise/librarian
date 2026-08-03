---
title: Observability and Runtime Patterns
tags: [infra, concept, pattern]
summary: Observability tool choice (LangSmith vs Langfuse), tracing architecture, runtime topology and checkpointer alignment rules, trigger patterns, and key signals to monitor for VA agents.
updated: 2026-07-14
sources:
  - raw/claude-docs/playground/docs/research/evaluation-and-learning/observability-and-runtime.md
  - raw/agent-skills/observability/SKILL.md
---

# Observability and Runtime Patterns

## Tool Choice: LangSmith vs Langfuse

| Dimension | LangSmith | Langfuse |
|---|---|---|
| LangGraph/LangChain integration | Native, zero config | Manual wiring |
| Annotation queues | Built-in | Via webhooks/plugins |
| Self-host | No | Yes (Docker) |
| Data sovereignty (EU GDPR) | US/EU cloud | Self-host = full control |
| Vendor lock-in | High | Low (open-source) |
| Cost | Paid tiers | Free self-hosted |

**Default recommendation:** Langfuse self-hosted for EU/GDPR context. Switch via env var — no code changes needed.

```python
OBSERVABILITY_BACKEND = os.getenv("OBSERVABILITY_BACKEND", "langfuse")
# "langfuse" | "langsmith" | "none"
```

### LangSmith Setup

When `OBSERVABILITY_BACKEND=langsmith`, enable tracing via environment variables — no client wiring required for LangChain/LangGraph runs in the process:

```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "..."
os.environ["LANGCHAIN_PROJECT"] = "librarian-rag"
```

View traces at `smith.langchain.com`. LangSmith also hosts golden eval datasets directly:

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

## Tracing Architecture

Every agent turn produces one trace with:
- User ID + session/thread ID
- Agent routing decision (which sub-agent or domain was selected)
- All tool calls + args + results
- Token counts (input, output, cache)
- Latency per node

**MCP tool call threading:** Pass trace context in headers so MCP tool spans attach to the parent trace.

```python
headers = {
    "X-Trace-Id": current_trace_id(),
    "X-Session-Id": thread_id,
}
httpx_client.post(mcp_tool_url, headers=headers)
```

## Runtime Topology and Checkpointer Alignment

**Critical rule: MemorySaver fails silently in multi-worker deployments.** Each worker process has its own in-memory state. A request routed to a different worker gets a blank slate.

| Runtime | Checkpointer | Notes |
|---|---|---|
| Lambda / serverless | Postgres or DynamoDB | MemorySaver loses state between invocations |
| Long-lived single worker | MemorySaver (dev) or Postgres | MemorySaver viable in dev only |
| LangGraph Cloud | Platform-managed | No manual setup |
| Kubernetes pod | Postgres | Required — requests land on different pods |
| Local dev | MemorySaver | Fine — single process |

```python
CHECKPOINT_BACKEND = os.getenv("CHECKPOINT_BACKEND", "memory")  # "memory" | "postgres"

checkpointer = (
    AsyncPostgresSaver.from_conn_string(os.getenv("DATABASE_URL"))
    if CHECKPOINT_BACKEND == "postgres"
    else MemorySaver()
)
```

## Trigger Patterns

How an agent turn is invoked affects latency expectations:

| Trigger | Latency expectation | Notes |
|---|---|---|
| HTTP/API (sync) | p50 < 2s | Most common for VA |
| Webhook/Event | Near-real-time | Action triggers |
| Message queue | Seconds to minutes | Background processing |
| Cron/Schedule | Defined interval | Batch eval, sync jobs |

## Key Signals to Monitor

| Signal | Metric | Alert threshold |
|---|---|---|
| Routing accuracy | % correctly routed to sub-agent | < 85% |
| Tool call latency | p95 per tool | > 3s |
| Context window usage | % of max tokens | > 80% |
| Guardrail hit rate | % blocked per stage | Spike > 2× baseline |
| HITL approval rate | % approved vs rejected | < 60% (too many rejections = bad agent output) |
| Clarification rounds | Average per task | > 1.5 (agent not understanding users) |
| Session memory load time | Node latency (ms) | > 500ms |
| Checkpointer read/write | Node latency (ms) | > 200ms |

## Structlog Pattern

Standard across the Workspace codebase:

```python
import structlog
log = structlog.get_logger()

log.info("tool_called", tool="fetch_invoice", args={"invoice_id": "INV-123"}, latency_ms=87)
log.warning("guardrail_triggered", stage="injection_detect", user_id=user_id)
log.error("tool_failed", tool="create_invoice", error=str(e), traceback=traceback.format_exc())
```

## Runtime Config Pattern

Single env var switches observability backend and runtime mode:

```bash
OBSERVABILITY_BACKEND=langfuse
CHECKPOINT_BACKEND=postgres
DATABASE_URL=postgresql://...
LANGFUSE_SECRET_KEY=...
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_HOST=https://your-langfuse.internal
```

## See Also
- [[Langfuse ADK Tracing Patterns]] <!-- auto-linked -->
- [[Observability — LangFuse vs LangSmith Decision]]
- [[Langfuse Platform]]
- [[Production Hardening Patterns]]
- [[Runtime Topology and Checkpointer Alignment]]
- [[LangGraph Advanced Patterns]]
- [[ADK Observability]]
- [[Observability & Evaluation Glossary]]
- [[Webhook Handler Idempotency]] — extends (async inbound events fail invisibly without traces)
