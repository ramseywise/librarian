# Observability and Runtime for VA Agents

**Sources:** langgraph_Yan.pptx, langgraph_extended.pptx, playground VA ADK implementation (observability.py), adk-agent-samples-main, librarian wiki (production-hardening-patterns.md)

---

## Observability Tool Choice

### LangSmith vs Langfuse

| Dimension | LangSmith | Langfuse |
|-----------|----------|---------|
| **Integration** | Native for LangChain/LangGraph — zero config | Manual wiring, framework-agnostic |
| **Setup** | `LANGSMITH_API_KEY` + tracing env var | Self-host (Docker) or cloud; SDK wrapper |
| **Data residency** | US/EU regions on Langchain Inc cloud | Self-host = your infra, full control |
| **Vendor lock-in** | High — eval, annotation, prompt versioning are LangSmith-specific | Low — open source, portable data |
| **Eval suite** | Built-in (annotate traces, run evals in UI) | Manual setup, more flexible |
| **Cost** | Usage-based, can be expensive at scale | Self-host = infra cost only |
| **GDPR** | Data sent to Langchain Inc (check DPA) | Self-host = no external data transfer |
| **Best for** | Fast iteration, LangGraph-native teams | Production with data sovereignty requirements |

**For Shine/Billy (EU, GDPR context): Langfuse self-hosted is the safer default.** LangSmith is fine for local dev and prototyping.

**Swap pattern** — both can be activated via env var, no code changes:
```python
# observability.py
import os

def setup_observability():
    if os.getenv("LANGSMITH_API_KEY"):
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "va-agent")
    
    if os.getenv("LANGFUSE_PUBLIC_KEY"):
        from langfuse.callback import CallbackHandler
        return CallbackHandler()  # pass as callback to LangGraph invoke
    
    return None
```

---

## Tracing Architecture

Every turn should produce one trace with:
- User ID
- Session/thread ID  
- Agent routing decision (which subagent handled it)
- All tool calls + args + results
- Token counts
- Latency per node

### LangSmith Wiring (LangGraph)

```python
from langsmith import Client
from langchain_core.tracers import LangChainTracer

tracer = LangChainTracer(project_name="va-billing-agent")

result = await graph.ainvoke(
    {"messages": [HumanMessage(content=user_input)]},
    config={
        "configurable": {"thread_id": session_id},
        "callbacks": [tracer],
        "metadata": {
            "user_id": user_id,
            "session_id": session_id,
        }
    }
)
```

### LangSmith Wiring (ADK)

ADK uses `before_agent_callback` / `after_agent_callback` for trace injection:

```python
from langsmith import Client
from google.adk.agents.callback_context import CallbackContext

ls_client = Client()

def before_turn_callback(callback_context: CallbackContext):
    # Start a LangSmith trace for this turn
    callback_context.state["__run_id"] = str(uuid4())
    ls_client.create_run(
        name="agent_turn",
        run_type="chain",
        id=callback_context.state["__run_id"],
        inputs={"user_message": callback_context.user_content.parts[-1].text},
        extra={"metadata": {"user_id": callback_context.state.get("user_id")}},
    )

def after_turn_callback(callback_context: CallbackContext):
    ls_client.update_run(
        run_id=callback_context.state["__run_id"],
        outputs={"response": callback_context.agent_output},
        end_time=datetime.now(UTC),
    )
```

### Thread ID Threading (MCP Tool Calls)

When agent calls external services via MCP, the trace ID must flow through:

```python
# Pass trace context in MCP tool call headers
async def call_mcp_tool(tool_name: str, args: dict, trace_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{MCP_SERVER_URL}/tools/{tool_name}",
            json=args,
            headers={
                "X-Trace-Id": trace_id,
                "X-Session-Id": session_id,
            }
        )
    return response.json()
```

---

## Trigger Patterns (How Agents are Invoked)

VA agents can be triggered in four ways. Runtime topology must match the trigger.

| Trigger | Description | Latency expectation | Example |
|---------|-------------|---------------------|---------|
| **HTTP/API** | Direct REST call to agent endpoint | p50 < 2s | Chat UI, Intercom widget |
| **Webhook/Event** | External service pushes an event | Near-real-time | New invoice created in Billy → agent notification |
| **Message Queue** | Kafka/SQS message triggers agent | Seconds to minutes | Batch processing, async task queue |
| **Cron/Schedule** | Time-based trigger | Defined interval | Daily report generation, weekly summaries |

---

## Runtime Topology and Checkpointer Alignment

**Critical rule:** your checkpointer backend must match your runtime hosting model.

| Runtime | Characteristics | Required checkpointer |
|---------|----------------|----------------------|
| **Lambda / serverless** | Stateless, ephemeral — no in-memory state between invocations | External DB (Postgres, DynamoDB) — `MemorySaver` will lose state between invocations |
| **Long-lived worker** | Persistent process (Gunicorn, Uvicorn) | `MemorySaver` viable for dev; Postgres for prod multi-worker |
| **LangGraph Cloud** | Managed — checkpointing handled by platform | Platform-managed, no config needed |
| **Kubernetes pod** | May restart — treat as stateless | External DB (Postgres) required |

### MemorySaver vs Postgres Checkpointer

```python
# Local dev — MemorySaver (in-process, lost on restart)
from langgraph.checkpoint.memory import MemorySaver
checkpointer = MemorySaver()

# Production — Postgres (persistent, multi-worker safe)
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
async with AsyncPostgresSaver.from_conn_string(DATABASE_URL) as checkpointer:
    await checkpointer.setup()
    graph = builder.compile(checkpointer=checkpointer)
```

**Never use MemorySaver in a multi-worker deployment** — each worker has its own in-memory state; thread history won't be shared across workers.

---

## Key Signals to Monitor in Production

| Signal | Tool | What to watch |
|--------|------|---------------|
| Routing accuracy | LangSmith/Langfuse + eval suite | % of turns routed to wrong subagent |
| Tool call latency | Trace spans | p95 tool call time per tool |
| Context window usage | Token counts in traces | Turns approaching max tokens |
| Guardrail hit rate | Structured logs | % of turns blocked by each guardrail stage |
| HITL approval rate | Custom metric | % of plans approved vs rejected |
| Clarification rounds | State metadata | Average clarification rounds per task |
| Session memory load time | Node latency | Time to load three-tier memory |

### Structlog Pattern (Standard in Workspace)

```python
import structlog
log = structlog.get_logger()

async def router_node(state: AgentState) -> dict:
    chosen = await classify_intent(state["messages"])
    log.info(
        "agent.routed",
        user_id=state["user_id"],
        session_id=state["session_id"],
        intent=chosen,
        tried_agents=state.get("tried_agents", []),
    )
    return {"next_agent": chosen}
```

---

## Runtime Config Pattern

Single env var switches between observability backends and runtime modes:

```bash
# .env.example
OBSERVABILITY_BACKEND=langfuse       # langfuse | langsmith | none
CHECKPOINT_BACKEND=postgres          # postgres | memory
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=https://your-langfuse.example.com
LANGSMITH_API_KEY=
LANGCHAIN_PROJECT=va-billing-agent
DATABASE_URL=postgresql://...
```

---

## See Also
- [orchestration-patterns.md](orchestration-patterns.md) — what to trace across agent hops
- [eval-harness.md](eval-harness.md) — eval scores complement observability signals
- librarian wiki: `Production Hardening Patterns`, `ADK Observability Guide`
