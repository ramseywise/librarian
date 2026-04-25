# Billy Accounting Assistant

A multi-agent assistant for the [Billy](https://www.billy.dk) accounting platform, built with the Google Agent Development Kit (ADK).

A root routing agent receives every user message and delegates to one of six domain expert subagents. Each expert owns a focused set of tools and a dedicated prompt. The user always receives a response — either from the right expert or a friendly explanation of what the assistant covers.

---

## Goal

Demonstrate how to structure a multi-agent system where:

- **Routing is fast and cache-friendly** — the router's stable system instruction never changes between turns, enabling Gemini's implicit prefix caching.
- **Dynamic context is minimal** — only the list of already-declined agents is injected per turn, as a short directive appended after the stable system instruction.
- **No wasted round-trips** — when a subagent declines a request, it registers itself so the router skips it on re-routing rather than bouncing the user back to the same dead end.

---

## Architecture

```text
User
 └── billy_assistant  (root / router)
      ├── invoice_agent
      ├── customer_agent
      ├── product_agent
      ├── email_agent
      ├── invitation_agent
      └── support_agent
```

The router never answers domain questions itself. It classifies and delegates. If a request is outside all domains it responds directly with a short explanation.

---

## Key Technique: `static_instruction` + `instruction`

ADK agents support two instruction fields that serve different purposes:

| Field | Type | When sent | Cache behaviour |
| --- | --- | --- | --- |
| `static_instruction` | `types.Content` | Every request, as the system instruction | Stable prefix — Gemini can cache it implicitly across turns |
| `instruction` | string template or callable | Every request, appended as a `user` content turn | Dynamic tail — varies per turn, breaks the cache prefix |

By putting the stable agent policy in `static_instruction` and reserving `instruction` for the small dynamic part, the large stable prompt is only processed once by Gemini and then cached. This reduces latency and token cost on every subsequent turn.

### Router example

`static_instruction` holds the full domain map — it never changes:

```python
Agent(
    model="gemini-3-flash-preview",
    name="billy_assistant",
    static_instruction=types.Content(
        role="user",
        parts=[types.Part(text=ROUTER_PROMPT)],
    ),
    instruction=provide_router_instruction,   # callable — runs each turn
    ...
)
```

`provide_router_instruction` injects a skip-list only when subagents have already declined:

```python
def provide_router_instruction(ctx: ReadonlyContext) -> str:
    tried = ctx._invocation_context.session.state.get("tried_agents", [])
    if not tried:
        return ""                             # nothing appended — cache intact
    return TRIED_AGENTS_TEMPLATE.format(agents=", ".join(tried))
```

On a typical first-turn request `instruction` returns `""` so nothing is appended and the full request hits the cache.

---

## Out-of-domain Handling

When a subagent cannot handle a request it calls `report_out_of_domain()`. The tool records the agent's name in `session.state["tried_agents"]` and immediately triggers the transfer back to the router — one call does both:

```python
def report_out_of_domain(tool_context: ToolContext) -> str:
    agent_name = tool_context._invocation_context.agent.name
    tried = tool_context.state.get("tried_agents", [])
    if agent_name not in tried:
        tool_context.state["tried_agents"] = tried + [agent_name]
    tool_context.actions.transfer_to_agent = "billy_assistant"
    return f"Registered {agent_name} as out-of-domain. Transferring to billy_assistant."
```

On the next routing call, `provide_router_instruction` reads that list and tells the router to skip those agents. This prevents infinite bounce loops without any hard-coded routing logic.

### Lifecycle of `tried_agents`

`tried_agents` must be cleared at the start of each user turn and preserved across agent hops within the same turn. This requires care because `before_agent_callback` fires on **every** `run_async` call — including when a subagent transfers back to `billy_assistant`. A naïve `callback_context.state["tried_agents"] = []` would wipe the list before the router can read it.

The fix is to clear only once per ADK invocation, using `invocation_id` as a guard. The Runner assigns a fresh `invocation_id` for each user message; all agent hops within that message share the same id:

```python
def clear_tried_agents(callback_context: CallbackContext) -> None:
    invocation_id = callback_context._invocation_context.invocation_id
    if callback_context.state.get("_tried_agents_invocation") != invocation_id:
        callback_context.state["tried_agents"] = []
        callback_context.state["_tried_agents_invocation"] = invocation_id
```

Full lifecycle for a single user turn:

```text
User message arrives
  → Runner creates new invocation (new invocation_id)
  → billy_assistant.run_async()
      → clear_tried_agents fires: new invocation_id → clears tried_agents = []
      → provide_router_instruction: tried_agents is empty → returns ""
      → router routes to support_agent

  support_agent.run_async()
      → support_agent cannot help → calls report_out_of_domain()
          → tried_agents = ["support_agent"]
          → actions.transfer_to_agent = "billy_assistant"

  billy_assistant.run_async()  ← triggered by the transfer
      → clear_tried_agents fires: same invocation_id → skips clear
      → provide_router_instruction: tried_agents = ["support_agent"] → injects skip directive
      → router routes to a different agent
```

---

## Structure

```text
agent.py                        root agent — routing logic and subagent list
app.py                          ADK App — wraps root_agent with context compaction
sub_agents/
  shared_tools.py               report_out_of_domain() — included in every subagent
  invoice_agent.py
  customer_agent.py
  product_agent.py
  email_agent.py
  invitation_agent.py
  support_agent.py
tools/                          plain Python tool functions (no ADK dependency)
  invoices.py
  customers.py
  products.py
  emails.py
  invitations.py
  support_knowledge.py
prompts/                        one .txt file per agent
  billy_assistant.txt
  invoice_agent.txt
  customer_agent.txt
  product_agent.txt
  email_agent.txt
  invitation_agent.txt
  support_agent.txt
  router_tried_agents.txt       template for the dynamic skip-list directive
specs/
  context_compaction.md         detailed spec for the App and compaction config
tests/                          pytest tests for tool functions and agent logic
```

---

## Running

All commands are available via `make` from the repo root:

```bash
make -C agents/billy_assistant run          # interactive terminal (adk run)
make -C agents/billy_assistant web          # web UI on http://localhost:8000
make -C agents/billy_assistant web-debug    # web UI with BILLY_DEBUG=1 (tool/agent traces to stderr)
make -C agents/billy_assistant test         # unit tests
make -C agents/billy_assistant eval         # all eval suites
```

Run a single eval suite or specific cases:

```bash
make -C agents/billy_assistant eval-routing
make -C agents/billy_assistant eval-routing CASES=support_question_routes_to_support
make -C agents/billy_assistant eval-routing CASES=case1,case2
```

Available eval suites: `eval-routing`, `eval-response`, `eval-behavior`, `eval-error`.

---

## Domains

| Agent | Handles |
| --- | --- |
| `invoice_agent` | Create, view, list, edit, approve invoices |
| `customer_agent` | Create, view, list, edit customers and contacts |
| `product_agent` | Create, view, list, edit products and prices |
| `email_agent` | Send an approved invoice by email |
| `invitation_agent` | Invite a user to the organisation |
| `support_agent` | Questions about how Billy works (searches help docs) |

All tools use in-memory mock data — no real API calls are made.

---

## Further Reading

- [SPEC.md](SPEC.md) — full system specification: agent instructions, tool contracts, data model
- [CLAUDE.md](CLAUDE.md) — developer guide for working in this codebase
