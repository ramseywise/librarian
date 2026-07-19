---
name: adk-python
description: >
  Google ADK Python patterns for the VA projects (va-google-adk/va-langgraph). Use when building
  or extending ADK agents, sub-agents, FunctionTools, callbacks, guardrails, or the FastAPI
  gateway. Triggers on: "new sub-agent", "add a tool", "add a guardrail", "wiring a callback",
  "before_model / after_model hook", "tool_context.state", "MCPToolset", "add a domain agent",
  "route to a new agent", "output schema", "adk run", "thinking config", "structured output".
---

# Google ADK Python

## Source of truth

- Primary: `/.docs/adk/llms-full.txt` (local copy — read before coding any ADK API)
- API map: `/.docs/adk/llms.txt`
- If local and upstream docs differ, call out the difference explicitly before coding.
- Only use ADK decorators and APIs confirmed in local docs.

---

## Before You Build

Answer these before writing agent or tool code.

**Agent structure**
- New root agent or new sub-agent? Root = `agent.py`; sub-agents live in `sub_agents/`.
- What's the routing trigger? (Description string the root agent uses to hand off — write it precisely.)
- Does a similar sub-agent already exist in `sub_agents/`? Check before adding.

**Tools**
- What tools does this agent need? Check `shared/tools/` before creating new ones.
- Each tool needs a Pydantic-typed signature and a docstring the LLM reads as documentation — what does the LLM need to understand about when to call it?
- Does the tool call the knowledge-base MCP server or an HTTP service directly?
- Max ~10 tools per agent. If this pushes past that, consider a sub-agent split instead.

**State & session**
- What goes in `tool_context.state`? (Survives across tool calls in a session.)
- What's ephemeral and should stay in the tool's return value only?
- Does this agent need `session_id` for downstream services (e.g., RAG thread continuity)?

**Callbacks**
- Does this agent need a `before_model_callback`? (PII redaction, prompt injection guard, domain validation — check `shared/guardrails/` first.)
- Does it need an `after_model_callback`? (Response validation, output sanitising.)
- Does it need a `before_tool_callback`? (Auth injection, parameter validation before the call.)

**Output schema**
- Does this agent produce structured output (`output_schema=`, `output_key=`)? What Pydantic model?
- `AssistantResponse` in `schema.py` is the shared contract — add optional fields, never remove or make new fields required.

**Testing**
- Can this be smoke-tested with `adk run`?
- What pytest fixtures cover the happy path and error cases?

---

## Agent conventions

```python
from google.adk.agents import Agent
from google.genai import types
from pathlib import Path

_INSTRUCTION = (Path(__file__).parent.parent / "prompts" / "my_agent.txt").read_text()

my_agent = Agent(
    model="gemini-2.5-flash",          # model string here only — never in tools or lib
    name="my_agent",                    # snake_case, matches file name
    description="One sentence the root agent reads to decide when to hand off.",
    static_instruction=types.Content(role="user", parts=[types.Part(text=_INSTRUCTION)]),
    output_schema=AssistantResponse,    # always use the shared schema
    output_key="response",
    tools=[report_out_of_domain, FunctionTool(func=my_tool)],
    generate_content_config=THINKING_CONFIG,  # import from shared_tools
)
```

- Model string lives in the `Agent` definition only — never in tools, callbacks, or lib code.
- `static_instruction` not `instruction` — instruction is re-evaluated each turn; static is set once.
- System prompt lives in `prompts/<agent_name>.txt`, not inline in code.
- `description` is what the root agent uses for routing — write it from the LLM's perspective.

---

## Tool conventions

```python
from google.adk.tools import FunctionTool
from typing import Any

async def get_invoice(invoice_id: str, tool_context: Any = None) -> dict:
    """Fetch an invoice by ID. Returns invoice details including line items and contact."""
    session_id = tool_context.state.get("session_id", "default") if tool_context else "default"
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(f"{BACKEND_URL}/invoices/{invoice_id}")
        r.raise_for_status()
    return r.json()   # transform before returning — agent never sees raw API shape

FunctionTool(func=get_invoice)  # wrap at module level as a singleton
```

- Async always — even if the tool does no I/O today.
- `tool_context: Any = None` as last parameter — ADK injects this; default `None` keeps it testable.
- Docstring is the tool's documentation for the LLM — describe what it does and when to use it.
- Transform the API response before returning — the agent should see clean, minimal data.
- Never raise inside a tool; return an error dict instead (`{"error": "..."}`) — ADK swallows exceptions silently.
- One file per domain in `sub_agents/` or `shared/tools/`.

---

## Callbacks & guardrails

```python
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse

def before_model_callback(ctx: CallbackContext, req: LlmRequest) -> LlmResponse | None:
    # Return None to continue; return LlmResponse to short-circuit
    if contains_pii(req):
        return LlmResponse(...)   # block and respond directly
    return None

def after_model_callback(ctx: CallbackContext, resp: LlmResponse) -> LlmResponse:
    # Always return a response — mutate or replace as needed
    return resp
```

- Check `shared/guardrails/` before writing a new callback — PII redaction, injection guard, and domain validators are already there.
- `before_model_callback` returning `None` → pipeline continues. Returning an `LlmResponse` → short-circuits the model call entirely.
- `before_tool_callback` useful for auth injection or schema validation before the actual call.
- Pass callbacks on the `Agent` constructor: `before_model_callback=my_guard`.

---

## Thinking config

```python
from google.genai import types

THINKING_CONFIG = types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(thinking_budget=8000)
)

SUPPORT_THINKING_CONFIG = types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(thinking_budget=4000)
)
```

Import the shared configs from `sub_agents/shared_tools.py` — don't define new ones unless the budget genuinely differs.

---

## Testing

```bash
# Smoke test interactively
adk run va-google-adk

# Run pytest suite
cd va-google-adk && uv run pytest tests/ -v
```

- Tests live under `tests/` in the agent directory — follow existing pytest patterns.
- Mock tool HTTP calls with `respx` or `unittest.mock.AsyncMock` — don't hit real backends in unit tests.
- Test the `output_schema` contract: assert the agent's `response` key conforms to `AssistantResponse`.
- Add a test for each new tool: happy path + error return (`{"error": "..."}` dict).

---

## Never do

- Never hardcode model strings in tools, callbacks, or lib code — only in `Agent(model=...)`.
- Never raise exceptions inside tools — return `{"error": "..."}` so ADK doesn't swallow silently.
- Never duplicate guardrail logic — reuse `shared/guardrails/`.
- Never use synchronous HTTP (`requests`) — always `httpx` async.
- Never edit `uv.lock` manually — use `uv add <package>`.
