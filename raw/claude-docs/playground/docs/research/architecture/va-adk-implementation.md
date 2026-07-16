# va-google-adk Architecture Notes

## What is Google ADK and what does it enforce?

Google ADK provides three primitives:
- `Agent` — an LLM agent with tools, instructions, and callbacks
- `App` — a configuration wrapper that attaches agents to middleware (e.g. context compaction)
- `Runner` — executes agent turns against a session, yields events

ADK enforces **nothing** about project layout. The `agents/` directory, the `sub_agents/` breakdown, the `gateway/` separation — all custom choices made when building this project, not ADK conventions.

---

## Why two separate layers (agents/ and gateway/)?

ADK has no built-in HTTP server. If you want to expose an agent over HTTP you build it yourself.

The split here is:
- **`agents/`** — pure ADK: root router + 11 domain sub-agents, prompt files, MCP toolsets
- **`gateway/`** — FastAPI: HTTP endpoints, SSE streaming, session lifecycle, artefact storage

`app.py` inside `agents/va_assistant/` is not a server — it's an `App` config object that attaches context compaction to the root agent. `gateway/session_manager.py` creates an ADK `Runner` per session and passes `va_app` into it.

Flow: `POST /chat` → `SessionManager.run_turn()` → `Runner.run_async()` → root agent → sub-agent → MCP tools → SSE events back to client.

---

## Why are schema.py, memory.py, model_factory.py, artefact_store.py at the project root?

They were originally in `shared/` (a now-deleted folder) and moved to root as part of a dissolve. They sit at root because they're consumed by both layers and there's no clean home:

- `schema.py` — `AssistantResponse` and UI types used by sub-agents (output_schema) and gateway (serialisation)
- `memory.py` — SQLite preference store used by the root agent callback and the session manager
- `model_factory.py` — model ID resolution used by sub-agents and gateway summary calls
- `artefact_store.py` — S3/local file storage used only by gateway

**The root placement is a workaround, not a pattern.** With `pythonpath = ["."]` in pytest config, anything at the project root is importable. It avoids circular imports (agents importing from gateway or vice versa) but produces a flat, structureless top level.

---

## What would a cleaner structure look like?

The core problem is that `schema.py` and `memory.py` are needed by both the agent layer and the HTTP layer. Options:

**Option A — single package with internal layers**
```
va_google_adk/
  core/
    schema.py
    memory.py
    model_factory.py
    artefact_store.py
  agents/
    root_agent.py
    sub_agents/
  server/         ← rename of gateway/
    main.py
    session_manager.py
```
All imports go through `va_google_adk.core.*`. No root-level modules.

**Option B — gateway owns the infrastructure**
```
gateway/
  schema.py       ← API contract lives here
  memory.py
  artefact_store.py
  model_factory.py
  main.py
  session_manager.py
agents/
  va_assistant/
    agent.py      ← imports from gateway.schema
    sub_agents/
```
Agents depend on gateway types. Feels backwards but is honest about the fact that AssistantResponse is really a gateway contract, not an agent-internal type.

**Option C — separate the API contract**
Keep agents fully self-contained (no knowledge of gateway types). Gateway handles the translation between ADK events and HTTP responses. Sub-agents return plain text or ADK-native structured output; the gateway maps to `AssistantResponse` before streaming. This is the most independent design but requires the most rewiring.

---

## Sub-agent pattern

Each domain sub-agent is a pure ADK `Agent`:
- `output_schema=AssistantResponse` — forces structured JSON output
- `output_key="response"` — ADK stores the result in session state under this key
- `MCPToolset(...)` — connects to the product-a/corpus-a MCP server over SSE, filtered to the domain's tools
- `THINKING_CONFIG` — enables Gemini extended thinking for tool-use reasoning
- `report_out_of_domain()` — custom function that marks the agent as "tried" and returns control to the router

The `agents/va_assistant/sub_agents/shared_tools.py` file holds `THINKING_CONFIG` and `report_out_of_domain` — used by every sub-agent. The name is local to the sub_agents package, not a cross-project concern.

---

## What is genuinely confusing about the current layout

1. **Root-level modules** (`schema.py` etc.) have no package — they look like scripts, not library code
2. **`shared/` was deleted** but the reason for root-level placement was never re-examined
3. **`app.py` vs `gateway/`** — the name "app" conflicts with FastAPI convention where `app` means the HTTP server
4. **`agents/shared/`** existed as dead code (guardrails re-implemented inline in agent.py) until it was deleted in this session
5. **`agents/__init__.py`** is empty — the package adds no value over a flat directory

The structure reflects iterative build decisions, not an upfront design. None of it is dictated by ADK.
