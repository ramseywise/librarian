---
title: ADK Python API Reference
tags: [adk, reference]
summary: Quick reference for the Google ADK Python SDK — agent types, tools, state, callbacks, plugins, artifacts, memory, context caching, and context compaction.
updated: 2026-07-14
sources:
  - raw/claude-docs/galactus/.agents/skills/adk-cheatsheet/SKILL.md
  - raw/claude-docs/galactus/.agents/skills/adk-cheatsheet/references/python.md
  - raw/claude-docs/galactus/.agents/skills/adk-cheatsheet/references/docs-index.md
  - raw/claude-docs/galactus/.agents/skills/adk-dev-guide/SKILL.md
  - raw/agent-skills/adk-cheatsheet/SKILL.md
  - raw/agent-skills/adk-cheatsheet/references/docs-index.md
  - raw/agent-skills/adk-cheatsheet/references/python.md
  - raw/claude-skills/google-adk/adk-python.md
---

# ADK Python API Reference

Quick-reference for the Google ADK Python SDK. Covers everything from agent definitions through deployment-time services. For project scaffolding, see [[ADK Scaffold Patterns]]. For deployment, see [[ADK Deployment Patterns]].

---

## Core Primitives

| Primitive | Role |
|---|---|
| `Agent` / `LlmAgent` | LLM-driven intelligent unit |
| `BaseAgent` | Custom orchestration via `_run_async_impl` |
| `Tool` | Callable providing external capabilities |
| `Session` | Stateful conversation thread (`events` + `state`) |
| `State` | KV dict within a Session for transient data |
| `Runner` | Execution engine — orchestrates agent + event flow |
| `Event` | Atomic communication unit carrying content and side-effect `actions` |

---

## Standard Project Layout

```
your_project/
├── app/                    # or <agent_name>/
│   ├── __init__.py
│   ├── agent.py            # defines root_agent
│   ├── tools.py
│   └── .env
├── tests/
│   ├── eval/
│   │   ├── eval_config.json
│   │   └── evalsets/
│   ├── integration/
│   └── unit/
└── pyproject.toml
```

---

## Agent Definitions (`LlmAgent`)

```python
from google.adk.agents import Agent
from google.genai import types as genai_types

agent = Agent(
    name="my_agent",
    model="gemini-3-flash-preview",
    instruction="Your instructions. Use {state_key} for dynamic injection.",
    description="Description for delegation in multi-agent systems.",

    generate_content_config=genai_types.GenerateContentConfig(
        temperature=0.2,
        max_output_tokens=1024,
    ),

    output_key="agent_response",      # save final output to state
    include_contents='default',        # 'default' or 'none'
    disallow_transfer_to_parent=False,
    disallow_transfer_to_peers=False,
    sub_agents=[specialist_agent],     # for LLM delegation
    tools=[my_tool],

    # Lifecycle callbacks
    before_agent_callback=my_cb,
    after_agent_callback=my_cb,
    before_model_callback=my_cb,
    after_model_callback=my_cb,
    before_tool_callback=my_cb,
    after_tool_callback=my_cb,
)
```

**Structured output:** use `output_schema=MyPydanticModel` to force structured output — but this **disables tool calling and delegation**.

**Instruction best practice:** `{state_key}` placeholders are injected at runtime from session state. Keep the static prefix long for [[Prefix Caching]].

---

## Workflow Agents (Deterministic Control Flow)

For deterministic orchestration without LLM involvement. See [[ADK Workflow Agents]] for full patterns.

| Agent | Behavior |
|---|---|
| `SequentialAgent` | Runs sub-agents in order; state propagates |
| `ParallelAgent` | Runs sub-agents concurrently; use distinct `output_key`s |
| `LoopAgent` | Repeats until `max_iterations` or `escalate=True` |

---

## Custom Agents (`BaseAgent`)

```python
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from typing import AsyncGenerator

class ConditionalRouter(BaseAgent):
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        user_type = ctx.session.state.get("user_type", "regular")
        agent = self.premium_agent if user_type == "premium" else self.regular_agent
        async for event in agent.run_async(ctx):
            yield event
```

`EscalationChecker` pattern to stop a `LoopAgent`:
```python
if result.get("grade") == "pass":
    yield Event(author=self.name, actions=EventActions(escalate=True))
```

---

## Multi-Agent Communication

Three patterns:

1. **Shared State** — agents read/write `session.state` via `output_key`
2. **LLM Delegation** — root agent routes to sub-agents based on reasoning (`sub_agents=[...]`)
3. **AgentTool** — invoke another agent as a tool (parent stays in control):
   ```python
   from google.adk.tools import AgentTool
   root = Agent(name="root", tools=[AgentTool(specialist_agent)])
   ```

**Important:** `ContextVar` mutations in `asyncio.create_task()` are invisible to child tasks. Use `session.state` as the primary channel for multi-agent auth/context, not `ContextVar`.

---

## Models

```python
# Gemini (default) — AI Studio dev vs Vertex prod
agent = Agent(model="gemini-3-flash-preview", ...)   # set GOOGLE_GENAI_USE_VERTEXAI

# Other models via LiteLLM
from google.adk.models.lite_llm import LiteLlm
agent = Agent(model=LiteLlm(model="anthropic/claude-sonnet-4-20250514"), ...)
agent = Agent(model=LiteLlm(model="openai/gpt-4o"), ...)
```

**Model selection rule:** Never change `model=` unless explicitly asked. A 404 error almost always means wrong `GOOGLE_CLOUD_LOCATION`, not wrong model name.

---

## Tools

### Function Tool

```python
from google.adk.tools import ToolContext

def search_database(query: str, limit: int, tool_context: ToolContext) -> dict:
    """Searches the database for records matching the query.
    Args:
        query: The search query string.
        limit: Maximum number of results to return.
    Returns: dict with 'status' and 'results' keys.
    """
    user_id = tool_context.state.get("user_id")
    return {"status": "success", "results": db.search(query, limit=limit)}
```

**Rules:** Clear docstrings (sent to LLM), type hints required, NO default values, return a dict, don't mention `tool_context` in docstring.

### ToolContext Capabilities

```python
tool_context.state["key"] = "value"        # read/write state
tool_context.actions.escalate = True        # stop LoopAgent
await tool_context.save_artifact(...)       # binary storage
results = await tool_context.search_memory("query")
```

### Built-in Tools

```python
from google.adk.tools.load_web_page import load_web_page   # CORRECT
from google.adk.tools import google_search
from google.adk.tools import VertexAiSearchTool
from google.adk.code_executors import BuiltInCodeExecutor

agent = Agent(tools=[google_search], ...)
agent = Agent(code_executor=BuiltInCodeExecutor(), ...)
```

**Warning:** `google_search` is model-internal — it never appears in tool trajectories. See [[ADK Eval Guide]] for eval implications.

### Tool Confirmation

```python
from google.adk.tools import FunctionTool
sensitive_tool = FunctionTool(delete_record, require_confirmation=True)

def needs_approval(amount: float, **kwargs) -> bool:
    return amount > 1000
transfer_tool = FunctionTool(transfer_money, require_confirmation=needs_approval)
```

### MCP Tools

```python
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams, SseConnectionParams

McpToolset(
    connection_params=StdioConnectionParams(server_params=StdioServerParameters(
        command="npx", args=["-y", "@modelcontextprotocol/server-filesystem", "/abs/path"],
    )),
    tool_filter=["list_directory", "read_file"],  # optional
)

# Production: SSE transport
McpToolset(connection_params=SseConnectionParams(url="https://mcp.example.com/sse"))
```

**Gotchas:** Paths must be absolute. Agent definition must be synchronous for deployment. Node.js required for npm-based servers — add to Dockerfile.

### Tool Authentication

| Auth Type | Pattern |
|---|---|
| API Key | `token_to_scheme_credential("apikey", "query", "apikey", "KEY")` → `auth_scheme, auth_credential` |
| Service Account | `service_account_dict_to_scheme_credential(config, scopes=[...])` → `auth_scheme, auth_credential` |
| OAuth2 / OIDC | `AuthCredential(auth_type=AuthCredentialTypes.OAUTH2, oauth2=OAuth2Auth(client_id=..., client_secret=...))` |
| Custom `FunctionTool` | `tool_context.request_credential(AuthConfig(...))` to initiate, `tool_context.get_auth_response(AuthConfig(...))` to retrieve |

Helpers live in `google.adk.tools.openapi_tool.auth.auth_helpers` (`token_to_scheme_credential`, `service_account_dict_to_scheme_credential`). Pass the resulting `auth_scheme` + `auth_credential` to `OpenAPIToolset(...)`.

### OpenAPI Tools

```python
from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset

toolset = OpenAPIToolset(spec_str=open("openapi.json").read(), spec_str_type="json")
agent = Agent(name="api_agent", tools=[toolset], ...)
```

Pass `auth_scheme` + `auth_credential` (see Tool Authentication above) for authenticated APIs. Tool names derive from `operationId` (snake_case, max 60 chars).

---

## Factory Functions for Sub-agents

Use factory functions (not module-level instances) to avoid "agent already has a parent" errors:

```python
def create_researcher():
    return Agent(name="researcher", ...)

root_agent = SequentialAgent(
    sub_agents=[create_researcher(), create_analyst()],  # call the factory!
)
```

---

## State Management

### State Prefixes

```python
state["booking_step"] = 2           # session-specific (default)
state["user:preferred_language"] = "en"   # user-persistent across sessions
state["app:total_queries"] = 1000   # app-wide (all users)
state["temp:intermediate_result"] = data  # current invocation only
```

### Session Services

```python
from google.adk.sessions import InMemorySessionService
# Dev: InMemorySessionService()
# Prod: VertexAiSessionService() or DatabaseSessionService()
```

### Session Rewind

Roll back session state to before a specific invocation (debugging / user-initiated undo):

```python
await runner.rewind_async(
    user_id=user_id,
    session_id=session.id,
    rewind_before_invocation_id=invocation_id,
)
```

Restores session-level state and artifacts only. App/user-scoped state is unaffected.

---

## Artifacts (File Storage)

```python
from google.adk.artifacts import InMemoryArtifactService, GcsArtifactService
from google.genai import types

runner = Runner(
    agent=root_agent, app_name="app",
    artifact_service=GcsArtifactService(bucket_name="my-bucket"),
)

# In a tool:
part = types.Part(inline_data=types.Blob(mime_type="application/pdf", data=data))
version = await tool_context.save_artifact("report.pdf", part)         # session-scoped
await tool_context.save_artifact("user:profile.png", part)             # user-scoped
artifact = await tool_context.load_artifact("report.pdf")
```

---

## Memory (Long-term Knowledge)

```python
from google.adk.memory import InMemoryMemoryService

memory_service = InMemoryMemoryService()
await memory_service.add_session_to_memory(session)   # post-conversation
results = await memory_service.search_memory(app_name, user_id, "query")
```

---

## Context Caching

Cache large context windows (system prompt + docs) to reduce latency and cost. Transparent to agent code.

```python
from google.adk.apps.app import App
from google.adk.agents.context_cache_config import ContextCacheConfig

app = App(
    name="my_app",
    root_agent=root_agent,
    context_cache_config=ContextCacheConfig(
        min_tokens=2048,     # only cache if context exceeds this
        ttl_seconds=1800,    # cache lifetime
        cache_intervals=10,  # re-cache every N invocations
    ),
)
```

---

## Context Compaction

Prevent context overflow on long sessions by summarizing older events in a sliding window:

```python
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
from google.adk.models import Gemini

app = App(
    name="my_app",
    root_agent=root_agent,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=20,   # summarize every N events
        overlap_size=3,           # include last N events in next window
        summarizer=LlmEventSummarizer(llm=Gemini(model="gemini-3-flash-preview")),
    ),
)
```

See [[ADK Context Engineering]] for the 3-strategy pattern (A/B/C) and voice agent constraints.

---

## Callbacks

```python
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse

async def before_model_callback(ctx: CallbackContext, request: LlmRequest) -> LlmResponse | None:
    return None  # None = pass through; LlmResponse = skip model call

async def before_tool_callback(ctx: CallbackContext, tool_name: str, args: dict) -> dict | None:
    return None  # None = continue; dict = skip tool and use as result

# State initialization pattern (prevents KeyError on first turn):
async def init_state(ctx: CallbackContext) -> None:
    if "preferences" not in ctx.state:
        ctx.state["preferences"] = {}
agent = Agent(before_agent_callback=init_state, ...)
```

---

## Plugins

Global hooks across all agents/tools/LLMs. Use for cross-cutting concerns (logging, guardrails); use callbacks for per-agent logic.

```python
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.apps.app import App

class MyPlugin(BasePlugin):
    async def before_model_callback(self, *, callback_context, llm_request):
        return None

app = App(name="my_app", root_agent=root_agent, plugins=[MyPlugin()])
```

**Built-in plugins:** `ReflectAndRetryToolPlugin`, `BigQueryAgentAnalyticsPlugin`, `ContextFilterPlugin`, `GlobalInstructionPlugin`, `SaveFilesAsArtifactsPlugin`, `LoggingPlugin`, `DebugLoggingPlugin`, `MultimodalToolResultsPlugin`.

**Safety guardrails:** use `before_model_callback` to filter input or `after_model_callback` to filter output. Return `None` to pass through, modified `LlmResponse` to block/replace.

---

## Running Agents Programmatically

```python
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

session_service = InMemorySessionService()
await session_service.create_session(app_name="app", user_id="user", session_id="s1")
runner = Runner(agent=my_agent, app_name="app", session_service=session_service)

async for event in runner.run_async(
    user_id="user", session_id="s1",
    new_message=types.Content(role="user", parts=[types.Part.from_text(text="Hello!")]),
):
    if event.is_final_response():
        print(event.content.parts[0].text)
```

## CLI Commands

```bash
adk web /path/to/project    # Web UI
adk run /path/to/agent      # CLI chat
adk api_server /path/to     # FastAPI server
adk eval agent/ evalset.json  # Run evaluations
```

## Repo Convention — Shared Guardrails & Tools

A recurring multi-agent-repo layout: `agents/` holds individual agent projects (each with its own `tests/`), and a `shared/` directory holds reusable cross-agent code — `shared/guardrails/` for callbacks (PII redaction, prompt injection detection, domain validators) and `shared/tools/` for tool helpers (e.g. `chain_callbacks`, `compact_contract_from_pydantic`). Before writing new agent code: check whether a similar agent already exists under `agents/`, and whether a guardrail or tool helper already exists under `shared/` — reuse before creating. Treat local docs (`llms-full.txt` / `llms.txt`) as source of truth over upstream when they diverge, and call out the discrepancy explicitly rather than silently picking one.

## ADK Package Directory Map

```
google/adk/
├── agents/       ← LlmAgent, BaseAgent, SequentialAgent, ParallelAgent, LoopAgent
├── tools/        ← FunctionTool, google_search, McpToolset, AgentTool
├── sessions/     ← InMemorySessionService, DatabaseSessionService, VertexAiSessionService
├── memory/       ← InMemoryMemoryService
├── runners/      ← Runner, InMemoryRunner
├── events/       ← Event, EventActions
├── models/       ← Gemini, LiteLlm
├── code_executors/ ← BuiltInCodeExecutor
├── evaluation/   ← eval framework
├── artifacts/    ← InMemoryArtifactService, GcsArtifactService
└── auth/         ← authentication helpers
```

---

## See Also

- [[ADK Workflow Agents]]
- [[ADK Context Engineering]]
- [[ADK Deployment Patterns]]
- [[ADK Eval Guide]]
- [[ADK Observability]]
- [[MCP Protocol]]
- [[Prefix Caching]]
