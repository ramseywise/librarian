# Fast Multi-Agent System

A hybrid invoice/support assistant built on [ADK](https://google.github.io/adk-docs/).
Demonstrates how to build a multi-agent system that routes requests efficiently —
minimising LLM calls while maintaining full conversation continuity across agents.

---

## What it does

Users ask questions about invoices or product workflows. The system routes each request to
the right specialist without going through a central LLM on every turn:

- **Invoice questions** — look up, validate, and update invoice records
- **Support questions** — step-by-step UI guidance, workflow explanations, how-to answers
- **Multi-domain requests** — both handled in one response via the orchestrator

---

## Quick start

```bash
# From the repo root
adk run agents/fast_multi_agent_system

# Or start the web UI
adk web
```

Try these inputs:

```
What is wrong with invoice 456?
How do I fix a missing VAT rate in the UI?
Check invoice 456 and explain how to fix the missing VAT.
Update invoice 456 with VAT 25%.
```

### Run the tests

```bash
pytest agents/fast_multi_agent_system/tests/ -v
```

Tests are fully offline — no model calls, no API keys required.

---

## Architecture

```
User message
    │
    ▼
HybridRootAgent          ← deterministic router, no LLM call of its own
    │
    ├─ decide_route()    ← keyword scoring, returns confidence 0–1
    │
    ├─ [low confidence]──► llm_router_agent   ← fast classifier, 1 LLM call
    │
    ├─ direct path ──────► invoice_agent      ← 1 LLM call
    │                   └► support_agent      ← 1 LLM call
    │
    └─ planned path ─────► orchestrator_agent ← coordinates helpers
                               ├► invoice_agent helper
                               └► support_agent helper
```

### LLM call budget per turn

| Path                        | LLM calls |
|-----------------------------|-----------|
| Direct (high confidence)    | **1**     |
| Direct + LLM router         | **2**     |
| Planned (orchestrator)      | **3–4**   |
| Re-route (misrouted expert) | **2–3**   |
| Follow-up continuation      | **1**     |

---

## Agents

| Agent                | Model                         | Role                             |
|----------------------|-------------------------------|----------------------------------|
| `HybridRootAgent`    | —                             | Router (no LLM calls)            |
| `invoice_agent`      | gemini-3.1-flash-lite-preview | Invoice domain expert            |
| `support_agent`      | gemini-3.1-flash-lite-preview | UI/workflow expert               |
| `orchestrator_agent` | gemini-2.5-flash              | Multi-domain coordinator         |
| `llm_router_agent`   | gemini-3.1-flash-lite-preview | Low-confidence classifier        |
| `receptionist_agent` | gemini-2.5-flash              | Greetings, out-of-scope fallback |

Each expert has two variants:

- **direct agent** — full conversation history, for single-domain requests
- **helper agent** — `include_contents='none'`, called via `AgentTool` by the orchestrator

---

## Three-layer fallback

**Layer 1 — pre-routing:** `decide_route()` detects planning signals and multi-domain
requests without any LLM call and routes them straight to the orchestrator.

**Layer 0 — LLM router:** When keyword confidence is below 0.6 or no domain terms
matched, a small classifier agent runs one cheap LLM call to classify the request.

**Layer 2 — post-routing escalation:** If a direct-path expert determines it was
misrouted, it calls `request_reroute(reason)`. The root agent escalates to the correct
expert or the orchestrator (max depth 2).

---

## Conversation continuity

Agents share state via `session.state` — not by reading each other's conversation history.

- **`public:facts`** — normalized invoice/support data accumulated across turns
- **`public:conversation_log`** — compact per-turn records (agent, request, outcome)
- **`get_conversation_context()`** — tool agents call at turn start to read shared state

This means a support agent answering in turn 2 already knows what the invoice agent
found in turn 1, without re-fetching anything.

### Follow-up routing

When an agent needs more information, it calls `signal_follow_up()`. The root agent
stores the agent name in `public:follow_up_agent`. On the next user message, if the
reply contains no new domain signals (e.g. just "456" or "yes"), the root agent routes
directly back to the waiting agent.

---

## Tools

| Tool                       | Agent   | Purpose                                     |
|----------------------------|---------|---------------------------------------------|
| `get_conversation_context` | all     | Read shared state without cache impact      |
| `signal_follow_up`         | all     | Ask a clarifying question; route reply back |
| `request_reroute`          | experts | Signal misroute; escalate to correct agent  |
| `get_invoice_details`      | invoice | Load invoice by ID                          |
| `validate_invoice`         | invoice | Run validation checks                       |
| `update_invoice_field`     | invoice | Update a field (requires user confirmation) |
| `get_support_steps`        | support | Step-by-step guidance for known issue codes |
| `get_help_article`         | support | Fetch a help article snippet                |

### Mutation confirmation

`update_invoice_field` requires explicit user confirmation for sensitive fields
(`vat_rate`, `due_date`, `amount`, `vendor_name`). ADK pauses execution and prompts
the user before the tool runs.

---

## Security

`FirewallPlugin` runs on every tool call:

- **Allowlist** — rejects any tool not registered in the expert registry
- **Audit log** — records proposed mutations to `public:proposed_action` before they run
- **Payload sanitisation** — strips `raw_payload` and `internal_trace` from tool results

The `before_model_callback` deliberately does **not** modify `system_instruction` — that
would break prefix caching. Dynamic context is appended to `llm_request.contents` instead.

---

## Prefix caching

`ContextCacheConfig` is set on `App` with `min_tokens=512`, `cache_intervals=20`,
`ttl_seconds=3600`. The cache fingerprint is `system_instruction + tools` — both are
static across the session, so every call after warm-up gets a cache hit.

Agents read dynamic context (conversation log, facts) via `get_conversation_context()`,
which is called after the cache lookup and has zero fingerprint impact.

### Request lifecycle

Understanding *when* the cache lookup happens explains why the tool approach is safe.

```
① system_instruction   ─┐
② tools list            ├── fingerprint hashed → cache lookup   ← decision made here
③ conversation history ─┘
             │
             ▼
④ new user message appended to contents
⑤ model starts generating
⑥ model calls get_conversation_context()                        ← tool runs here
⑦ tool reads session.state, returns log + facts
⑧ model sees result, continues to final response
```

The cache hit or miss is decided at step ③. The tool executes at step ⑥. Whatever
`get_conversation_context()` returns — conversation log, accumulated facts, task notes —
has no effect on the fingerprint because the decision is already made.

### What keeps the fingerprint stable

| Element                      | Stable? | How                                                        |
|------------------------------|---------|------------------------------------------------------------|
| `system_instruction`         | Yes     | Loaded from a `.txt` file at import time, never mutated    |
| `tools` list                 | Yes     | Defined once per agent, never changed at runtime           |
| Conversation history         | Yes     | ADK controls this; only the new user turn is appended      |
| Dynamic context (facts, log) | N/A     | Read via tool after cache lookup — not part of fingerprint |

### What would break it

```python
# BREAKS — instruction changes every turn as facts accumulate
Agent(instruction=f"Known facts: {session.state['public:facts']}")

# BREAKS — {public:facts} is not a valid ADK injection prefix; even if it were,
# the value changes every turn → new fingerprint → miss every call
Agent(instruction="Context: {public:facts}")

# BREAKS — modifying system_instruction inside before_model_callback
# changes the prefix the model sees, invalidating the cached version
def before_model_callback(self, *, callback_context, llm_request):
    llm_request.config.system_instruction += f"\nFacts: {facts}"  # don't do this

# SAFE — static instruction, dynamic data fetched by tool after cache lookup
Agent(
    instruction=Path("prompts/invoice_agent.txt").read_text(),  # never changes
    tools=[get_conversation_context, ...],
)
```

If you need to inject dynamic data per-call (tenant ID, user role, etc.), append it
as a `Content(role="user")` entry to `llm_request.contents` inside
`before_model_callback`. Content after the cached prefix is not part of the
fingerprint and does not cause a miss.

---

## Adding a new expert

1. Create `tools/expert_tools.py` with domain-specific tool functions
2. Create `prompts/expert_agent.txt` — include `{reroute_section}` as a placeholder
3. Add `REROUTE_EXPERT = "expert domain"` to `state.py` and add it to `REROUTE_ALL`
4. Create `experts/expert_agent.py`:

```python
from ..expert_registry import ExpertSpec, register
from ..state import REROUTE_EXPERT
from ..tools.expert_tools import tool_a, tool_b
from google.adk.agents import Agent

register(ExpertSpec(
    Agent(
        name="expert_agent",
        model="gemini-3.1-flash-lite-preview",
        description="brief description of this expert's domain",
        tools=[tool_a, tool_b],
    ),
    routing_terms=["keyword1", "keyword2"],
    reroute_reason=REROUTE_EXPERT,
))
```

5. Import the module in `expert_registry.py`

The firewall allowlist, orchestrator helper tools, and routing are all derived
automatically from the registry — no other files need editing.

---

## Project layout

```
agents/fast_multi_agent_system/
├── __init__.py              # exports root_agent
├── agent.py                 # HybridRootAgent + App
├── state.py                 # session state constants and helpers
├── routing.py               # decide_route() — deterministic keyword scorer
├── expert_registry.py       # ExpertSpec + two-phase agent construction
├── agents/
│   ├── orchestrator_agent.py
│   ├── receptionist_agent.py
│   └── router_agent.py
├── experts/
│   ├── invoice_agent.py
│   └── support_agent.py
├── prompts/                 # static system instructions (loaded at import time)
├── tools/
│   ├── context_tools.py
│   ├── invoice_tools.py
│   └── support_tools.py
├── plugins/
│   └── firewall.py
└── tests/
    └── test_structure.py    # offline structural tests
```

For a full implementation reference see [SPEC.md](SPEC.md).
