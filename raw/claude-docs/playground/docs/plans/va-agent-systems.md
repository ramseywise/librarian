# Plan: va-google-adk and va-langgraph

> Status: Draft — 2026-04-20
> Goal: Two production-grade Python VA agent systems sharing the same interface,
> one built on Google ADK, one on LangGraph. Python equivalents of `ts_google_adk`.

---

## 1. Gap Analysis — `billy_assistant` vs `ts_google_adk`

What exists in `adk-agent-pocs/agents/billy_assistant` that is reusable, and what
`ts_google_adk` has that is not yet in Python.

### Reusable from `billy_assistant`

| Component | What it is |
|---|---|
| Multi-agent routing | Root router → 6 domain sub-agents via `AgentTool` / transfer |
| `static_instruction` + callable | Cache-stable system prompt + dynamic skip-list per turn |
| `tried_agents` lifecycle | `invocation_id`-scoped clear — prevents bounce loops |
| `report_out_of_domain()` | Shared tool — one call registers + transfers |
| Context compaction (`App`) | `EventsCompactionConfig` with `LlmEventSummarizer` |
| Tool layer | invoices, customers, products, emails, invitations, support_knowledge |
| Eval suites | routing, response, behavior, error — 4 evalsets |
| `agent_gateway` | FastAPI SSE host — POST /chat, GET /chat/stream, GET /agents |

### Missing from Python to match `ts_google_adk`

| Feature | ts_google_adk mechanism | Python gap |
|---|---|---|
| Structured output | `outputSchema` (JSON object) | No schema — agents return plain text |
| Suggestions | `suggestions: string[]` in schema | Missing |
| Navigation buttons | `navButtons: [{label, route}]` in schema | Missing |
| Inline form trigger | `form: {type: "create_invoice"}` in schema | Missing |
| Email form | `emailForm: {to, subject, body}` in schema | Missing |
| Confirm/discard | `confirm: boolean` in schema | Missing |
| Contact support | `contactSupport: boolean` in schema | Missing |
| Charts | `tableType` + chart data in schema | Missing |
| Source links | `sources: [{title, url}]` in schema | Missing |
| Quote domain | list_quotes, create_quote, create_invoice_from_quote | Missing entirely |
| Page context | URL prefix in user message → agent reads it | Missing |
| Real API calls | Billy REST API client (not in-memory stubs) | All tools are mocks |
| Web client | React chat UI | `adk-agent-pocs/web_client` exists but tied to A2UI |
| Observability | — | Neither system has tracing/LangFuse yet |

### What `adk-agent-pocs` has but `ts_google_adk` doesn't

| Feature | Value for Python system |
|---|---|
| A2UI protocol (`a2ui_mcp`) | Richer UI surfaces — keep as optional layer |
| `WineGuardrailsPlugin` patterns | Reusable safety pipeline — apply to VA |
| Eval harness | 4 eval suites per agent — carry forward |
| `agent_gateway` (FastAPI SSE) | Already done — reuse directly |
| `mcp_servers/billy` | MCP tool server — usable by both ADK and LangGraph |

---

## 2. Shared Foundation

Both `va-google-adk` and `va-langgraph` share the same:

### 2a. Output Schema

A Pydantic model (Python equivalent of `ts_google_adk`'s `outputSchema`) that every
response must conform to. Both agent systems write to this schema; the gateway and
frontend consume it identically.

```python
class NavButton(BaseModel):
    label: str
    route: str
    id: str | None = None
    document_type: str | None = None

class Source(BaseModel):
    title: str
    url: str

class FormConfig(BaseModel):
    type: Literal["create_customer", "create_product", "create_invoice", "create_quote"]
    defaults: dict | None = None

class EmailFormConfig(BaseModel):
    to: str | None = None
    subject: str | None = None
    body: str | None = None

class AssistantResponse(BaseModel):
    message: str                          # markdown — what the user sees
    suggestions: list[str] = []          # 2-4 follow-up chips
    nav_buttons: list[NavButton] = []    # deep-links into Billy app
    sources: list[Source] = []           # support doc links
    table_type: str | None = None        # "invoices" | "customers" | "products" | "quotes"
    form: FormConfig | None = None       # inline creation form
    email_form: EmailFormConfig | None = None
    confirm: bool = False                # show Confirm/Discard buttons
    contact_support: bool = False        # show Contact Support button
```

### 2b. Tool Layer (`va-shared/tools/`)

Plain Python functions — no ADK or LangGraph dependency. Identical between both systems.
Initially call `mcp_servers/billy` over MCP; can swap to direct Billy REST API later.

| Module | Functions |
|---|---|
| `invoices.py` | `get_invoice`, `list_invoices`, `get_invoice_summary`, `create_invoice`, `edit_invoice` |
| `quotes.py` | `list_quotes`, `create_quote`, `create_invoice_from_quote` |
| `customers.py` | `list_customers`, `create_customer`, `edit_customer` |
| `products.py` | `list_products`, `create_product`, `edit_product` |
| `emails.py` | `send_invoice_by_email`, `send_quote_by_email` |
| `invitations.py` | `invite_user` |
| `support_knowledge.py` | `fetch_support_knowledge` |

### 2c. Gateway API Contract

Both systems expose the same FastAPI endpoints so the same web client works with either.

```
POST /chat            { session_id, request_id, message, agent_name? }
GET  /chat/stream     SSE — text chunks + structured JSON events
GET  /agents          [{ name, description }]
POST /agents/switch   { session_id, agent_name }
```

SSE event types (same for both):
- `text` — streaming message chunk
- `response` — final `AssistantResponse` JSON
- `tool_call` — debug: tool name + args
- `tool_result` — debug: tool output
- `error` — error message

### 2d. Web Client

Single React/Next.js frontend (adapted from `ts_google_adk`) that connects to either
gateway. Feature flag or env var selects which backend (`VA_BACKEND_URL`).

Renders all `AssistantResponse` fields: markdown, suggestions chips, nav buttons,
inline forms, email form, confirm/discard, contact support button, source links.

---

## 3. `va-google-adk` Design

### Directory layout

```
playground/va-google-adk/
  agents/
    va_assistant/             # root router agent
      agent.py                # LlmAgent with static_instruction + tried_agents
      app.py                  # App with EventsCompactionConfig
      prompts/                # .txt per agent
      sub_agents/
        invoice_agent.py
        quote_agent.py        # NEW domain
        customer_agent.py
        product_agent.py
        email_agent.py
        invitation_agent.py
        support_agent.py
        shared_tools.py       # report_out_of_domain()
      eval/                   # evalsets: routing, response, behavior, error
  gateway/
    main.py                   # FastAPI — POST /chat, GET /chat/stream, GET /agents
    session_manager.py        # ADK Runner per session + SSE queue
    schema.py                 # AssistantResponse (shared schema)
  shared/
    tools/                    # plain Python tool functions
    guardrails/               # firewall plugin (from adk-agent-pocs shared/)
  web_client/                 # React frontend (shared with va-langgraph)
  tests/
  pyproject.toml
  Makefile
  .env.example
```

### Key ADK-specific design decisions

**Structured output:** Each sub-agent uses `output_schema=AssistantResponse` so the
model writes structured JSON. The root router does NOT use output_schema — it only
routes. The formatter step (root agent collects sub-agent result and wraps it) or
each sub-agent writes its own `AssistantResponse`.

**Page context:** Gateway injects current URL as a prefix to the user message:
`[User is on page: /invoices] List all unpaid invoices`

**Quote domain:** New `quote_agent` sub-agent with tools from `quotes.py`.
Router system prompt updated to include `quote_agent` in domain map.

**Guardrails:** `BeforeAgentCallback` on root agent runs the firewall plugin from
`adk-agent-pocs/shared/guardrails/` — normalisation → size check → domain check
→ injection detection → PII redaction.

**Context compaction:** Same `App` + `EventsCompactionConfig` as `billy_assistant`.

### Phases

**Phase 1 — Skeleton** (agent routes, no real API)
- Port `billy_assistant` to `va-google-adk` with `AssistantResponse` output schema
- Add `quote_agent`
- Gateway: reuse `agent_gateway` adapted to the new schema
- Tools: in-memory stubs from `billy_assistant`

**Phase 2 — Real API**
- Replace tool stubs with MCP calls to `mcp_servers/billy`
- Or: direct Billy REST API client in `shared/tools/`

**Phase 3 — UI features**
- Suggestions, nav buttons, form triggers, email form, confirm/discard
- Contact support escalation (frustration detection in guardrails)
- Page context injection in gateway

**Phase 4 — Observability + Eval**
- LangFuse tracing on gateway (optional, env-gated)
- 4 eval suites carried forward from `billy_assistant`
- Add quote routing evals

---

## 4. `va-langgraph` Design

### Why LangGraph here

LangGraph gives explicit state, typed transitions, and streaming support baked in.
Best for: multi-step flows (create invoice requires customer + product lookups),
HITL (confirm before sending email), and later adding CRAG/RAG for support.

### Directory layout

```
playground/va-langgraph/
  graph/
    __init__.py
    state.py                  # AgentState TypedDict
    builder.py                # StateGraph wiring
    nodes/
      analyze.py              # classify intent + extract entities
      route.py                # route to domain subgraph
      format.py               # convert domain result → AssistantResponse
      error.py                # error recovery node
    subgraphs/
      invoice.py              # invoice subgraph (nodes: plan → execute → confirm)
      quote.py
      customer.py
      product.py
      email.py
      invitation.py
      support.py              # CRAG loop for support queries
  gateway/
    main.py                   # FastAPI — same endpoints as va-google-adk
    runner.py                 # LangGraph runner per session + SSE queue
    schema.py                 # AssistantResponse (same model)
  shared/
    tools/                    # same tool functions as va-google-adk
    guardrails/               # same guardrail functions
  web_client/                 # symlink or copy from va-google-adk
  tests/
  pyproject.toml
  Makefile
  .env.example
```

### State schema

```python
class AgentState(TypedDict):
    # Core
    messages: Annotated[list[BaseMessage], add_messages]
    session_id: str
    page_url: str | None

    # Routing
    intent: str | None           # "invoice" | "quote" | "customer" | ...
    confidence: float

    # Domain result
    domain_result: dict | None   # raw tool output

    # Output
    response: AssistantResponse | None

    # Safety
    blocked: bool
    block_reason: str | None

    # HITL
    pending_action: dict | None  # for confirm/discard flows
```

### Graph topology

```
START
  → guardrail          (firewall — blocked? → END with error response)
  → analyze            (classify intent, confidence)
  → route              (conditional edge → domain subgraph)
    ├─ invoice_graph
    ├─ quote_graph
    ├─ customer_graph
    ├─ product_graph
    ├─ email_graph       (interrupt_before for HITL confirm)
    ├─ invitation_graph
    └─ support_graph     (CRAG loop)
  → format             (wrap domain result in AssistantResponse)
  → END
```

### Key LangGraph-specific design decisions

**Streaming:** Gateway uses `.astream_events()` in `events` mode to forward
token-level streaming + node transitions as SSE events.

**HITL — email confirm:** `email_graph` uses `interrupt_before=["send_email"]`.
Gateway returns `AssistantResponse(confirm=True)` on interrupt. Client sends
approve/reject via `POST /chat/resume`. Gateway calls
`graph.invoke(Command(resume=...), config)`.

**Support CRAG:** `support_graph` is a mini StateGraph:
`retrieve → grade → (sufficient? → generate | rewrite → retrieve)`.
Uses same `fetch_support_knowledge` tool; grader is a Haiku call.

**Checkpointer:** `InMemoryCheckpointer` for dev, `AsyncPostgresCheckpointer` for prod.
Required for HITL and session persistence.

**Output schema:** `format` node calls `llm.with_structured_output(AssistantResponse)`.

### Phases

**Phase 1 — Skeleton** (graph wires, analyze + route + format)
- `AgentState`, graph builder, analyze node (LLM intent classification)
- Simple domain nodes (each calls one tool, returns result)
- Format node writes `AssistantResponse`
- Gateway: LangGraph runner with SSE

**Phase 2 — Real API + HITL**
- Same tool swap as ADK Phase 2
- `email_graph` with `interrupt_before` + `/chat/resume` endpoint
- `confirm: true` response triggers frontend Confirm/Discard

**Phase 3 — Support CRAG + UI features**
- `support_graph` CRAG loop
- Suggestions, nav buttons, form triggers, page context

**Phase 4 — Observability**
- LangFuse via `LangFuseCallbackHandler`
- Trajectory eval (expected node sequence vs actual)

---

## 5. Shared Web Client

Adapt `ts_google_adk/src/app/` to:
- Connect to `VA_BACKEND_URL` (either ADK or LangGraph gateway)
- Render `AssistantResponse` fields (message, suggestions, nav_buttons, form, email_form, confirm, contact_support, sources)
- SSE client that handles both `text` and `response` event types
- Remove: TypeScript Billy API types (move to backend)
- Keep: chart-renderer, markdown-renderer, all chat UI components

---

## 6. Build Order

```
Week 1: Shared foundation
  □ va-shared/tools/ — port tool stubs from billy_assistant + add quotes.py
  □ schema.py — AssistantResponse Pydantic model
  □ gateway/main.py — FastAPI skeleton (same endpoints both systems will use)

Week 2: va-google-adk Phase 1
  □ Port billy_assistant → va-google-adk with AssistantResponse output schema
  □ Add quote_agent
  □ Gateway ADK runner + SSE
  □ Smoke test: routing evals pass

Week 3: va-langgraph Phase 1
  □ State schema + graph builder
  □ analyze + route + format nodes
  □ Same tool layer as ADK version
  □ Gateway LangGraph runner + SSE
  □ Smoke test: same eval prompts, compare outputs

Week 4: UI + Real API
  □ Web client adapted from ts_google_adk
  □ Both gateways serving same frontend
  □ Tool stubs → MCP calls to mcp_servers/billy

Week 5+: HITL, CRAG, observability (per phase plans above)
```

---

## 7. Open Questions

1. **Shared `tools/` package?** — Copy into each project vs a `va-shared` uv workspace package. Workspace package is cleaner but adds dependency management overhead for a POC.

2. **Web client location** — Inside `va-google-adk/web_client/` with a symlink from `va-langgraph/`? Or a top-level `va-web-client/` package?

3. **Real Billy API vs MCP server** — Use `mcp_servers/billy` (already exists) or call Billy REST directly with proper auth? MCP is simpler for now; direct is more prod-realistic.

4. **LangGraph model for analyze node** — Haiku for classification (cheap, fast) or Sonnet for better entity extraction? Start with Haiku, gate Sonnet behind `planning_mode="full"`.

5. **ADK output_schema per sub-agent or only at root?** — Per sub-agent is cleaner (each expert writes its own response). Root router should NOT have output_schema (it only routes). Risk: each sub-agent must format fully; no shared formatter node.
