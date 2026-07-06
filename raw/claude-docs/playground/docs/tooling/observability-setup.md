# Observability Setup — VA Agents

## Stack decision (2026-04-25)

**LangSmith** is the chosen tracing platform for both VA agent implementations. Langfuse was evaluated but set aside — the LangSmith key already existed and LangGraph auto-instruments with zero code. Both use the same cloud setup for dev and prod (different project names, same key shape).

LangSmith key lives in `/Users/ramsey.wise/Workspace/help-support-rag-agent/.env`.

## Where everything is configured

Each project has a single `observability.py` at its root (same level as `model_factory.py`). That is the only file to touch when changing tracing backends.

### va-langgraph

Pure env vars — no code needed. LangGraph auto-traces every node, model call, and tool invocation when these are set:

```
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=lsv2_pt_...
LANGSMITH_PROJECT=playground
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
```

`observability.py` is a reference-only file with the Langfuse implementation commented out and swap instructions.

### va-google-adk

ADK doesn't use LangChain so auto-instrumentation doesn't apply. `observability.py` initialises a `langsmith.Client` and exposes `start_trace()` which returns a `_Turn` wrapper. `gateway/session_manager.py` opens a trace before each `run_async` call and closes it with the final response or error.

Trace granularity: one trace per ADK turn (input message → final response). Per-tool granularity would require the OpenTelemetry → LangSmith OTLP path — not wired yet.

## Switching to Langfuse

Both `observability.py` files contain the full Langfuse implementation as commented-out blocks. To switch:

1. Uncomment the Langfuse block in each `observability.py`
2. Replace `langsmith>=0.2.0` with `langfuse[langchain]>=2.0.0` (va-langgraph) and `langfuse>=2.0.0` (va-google-adk) in each `pyproject.toml`
3. Update `.env` to use `LANGFUSE_*` vars instead of `LANGSMITH_*`
4. In `va-langgraph/gateway/runner.py`, re-add `"callbacks": [get_callback_handler(...)]` to the LangGraph config dict
5. In `va-langgraph/gateway/main.py`, call `init_langfuse()` / `shutdown_langfuse()` in the lifespan
