# SPEC.md — a2ui_mcp

## Status: implemented

---

## Overview

`a2ui_mcp` is a Billy accounting agent that combines two capabilities:

1. **Native skill loading** — ADK's `SkillToolset` + `adk_additional_tools` mechanism
   for lazy, domain-gated tool access. Domain tools are called directly by the model;
   no proxy, no schemas in conversation.

2. **A2UI output** — after every substantive response the agent emits a
   `---a2ui_JSON---` delimiter followed by a JSON array of [A2UI v0.9](https://a2ui.org)
   messages. The `agent_gateway/` FastAPI server parses these and forwards them to the
   `agents/a2ui_mcp/web_client/` React frontend, where they are rendered as interactive surfaces.

The agent is **text / non-live** mode only. Voice / live mode is out of scope.

---

## System Architecture

```text
┌─────────────────────────────────────────────────────────────────┐
│  agents/a2ui_mcp/web_client/ — Vite + React + @a2ui/react                  │
│                                                                 │
│  ┌──────────────────┐   ┌──────────────────────────────────┐   │
│  │  Chat Panel      │   │  Surface Panel                   │   │
│  │  message thread  │   │  <A2UIRenderer surfaceId="main"> │   │
│  │  text input      │   │  <A2UIRenderer surfaceId="detail">   │
│  └────────┬─────────┘   └──────────────────────────────────┘   │
│           │ POST /chat              ▲ GET /chat/stream (SSE)    │
└───────────┼─────────────────────────┼───────────────────────────┘
            │                         │
┌───────────▼─────────────────────────┴───────────────────────────┐
│  agent_gateway/ — FastAPI                                        │
│                                                                  │
│  POST /chat        fires asyncio background task                 │
│  GET  /chat/stream SSE: text_chunk | a2ui | done | error        │
│  GET  /agents      list registered agents                        │
│  POST /agents/switch                                             │
│                                                                  │
│  session_manager: one ADK Runner + asyncio.Queue per session     │
│  a2ui_parser:     parse_a2ui_response() — called once per turn  │
└──────────────────────────────┬──────────────────────────────────┘
                               │
               ┌───────────────▼───────────────┐
               │  a2ui_mcp (ADK agent)          │
               │  SkillToolset + preloaded      │
               └───────────────┬───────────────┘
                               │ MCP stdio/SSE
                               ▼
                     Billy MCP Server
                     (mcp_servers/billy)
```

### SSE event protocol

Every event carries the `request_id` of the POST that triggered it. The client
generates a UUID before opening the SSE stream and includes it in the POST body.
This lets concurrent sends (e.g. a `[ui_event]` arriving mid-stream) be attributed
correctly on a single shared stream.

```json
{ "type": "text_chunk", "request_id": "str", "text": "str" }
{ "type": "a2ui",       "request_id": "str", "messages": [] }
{ "type": "done",       "request_id": "str" }
{ "type": "error",      "request_id": "str", "message": "str" }
```

**SSE/POST ordering:** the client opens `GET /chat/stream` first, waits for the
`connected` event, then fires `POST /chat`. If the POST fires before the SSE stream
is open, the first events are lost.

---

## A2UI Output Protocol

After every substantive response the agent emits:

```text
<conversational prose>
---a2ui_JSON---
[<A2UI v0.9 message>, ...]
```

The `agent_gateway/a2ui_parser.py` accumulates the full response buffer for the
turn (end-of-turn buffering — not per-chunk), then calls `parse_a2ui_response()`
once. The delimiter and JSON regularly span chunk boundaries; per-chunk parsing
silently drops valid payloads.

### Structure vs data

A2UI v0.9 separates component layout from data state. The agent always emits the full
surface definition — structure and data together — because it cannot know whether the
client has the surface in memory (new session, page refresh, context compaction):

| Situation                     | What to emit                                                    |
|-------------------------------|-----------------------------------------------------------------|
| Any surface render            | `createSurface` + `updateDataModel` + `updateComponents`        |
| Surface no longer needed      | `deleteSurface`                                                 |

Message ordering rule: `createSurface` first → `updateDataModel` → `updateComponents` last.

Every message in the array MUST include `"version": "v0.9"` at the top level.
Catalog ID: `https://a2ui.org/catalog/basic/v0.8/catalog.json`.

### Surface naming convention

| surfaceId  | Purpose                                |
|------------|----------------------------------------|
| `main`     | Primary list or dashboard view         |
| `detail`   | Single entity view / edit form         |
| `confirm`  | Confirmation prompt before a mutation  |

### Surface events → agent

When the user interacts with an A2UI surface (button click, form submit), the
`SurfacePanel` component fires the event back as a chat message:

```text
[ui_event] {"type":"event","name":"edit_customer","context":[{"key":"id","value":{"path":"/id"}}]}
```

The agent prompt instructs the model to parse `[ui_event]` prefixed messages and
act directly — no re-confirmation needed.

### Schema validation

`a2ui_schema.json` at the repo root defines the A2UI array schema. It is used by
`agent_gateway/a2ui_parser.py` for server-side validation only — it is not injected
into the agent prompt. The prompt includes a compact v0.9 component reference table
sufficient for generation.

---

## Skill Loading

`a2ui_mcp` uses ADK's native `SkillToolset` + `adk_additional_tools` mechanism.
Domain tools are called directly after `load_skill` — no proxy step.

### Why lazy loading

Without skills, all domain instructions and all tool declarations must be present on
every turn. For 6 domains and 14+ tools this bloats every request and clutters the
model's reasoning with domains not relevant to the current task.

Skills separate two concerns:

| Concern                                                             | Location                                | Cost                                              |
|---------------------------------------------------------------------|-----------------------------------------|---------------------------------------------------|
| HOW to use a domain (rules, confirmation steps, parameter guidance) | `load_skill` response, in `contents`    | Paid once per session when domain is first needed |
| WHAT tools exist (names, schemas)                                   | Tool registry (`tools` API field)       | Session start, then cached                        |

### `adk_additional_tools` — tool gating

`SkillToolset._resolve_additional_tools_from_state` reads
`state["_adk_activated_skill_a2ui_mcp"]` to decide which tools from the
`additional_tools` candidate pool are visible on a given turn:

```text
Session start (no skills loaded):
  Tool registry = [list_skills, load_skill, load_skill_resource, run_skill_script]
                + [fetch_support_knowledge]      <- preloaded, always visible
  Visible: 5 tools

After load_skill("invoice-skill"):
  Tool registry += [list_invoices, get_invoice, get_invoice_summary,
                    create_invoice, edit_invoice]
  Visible: 10 tools

After load_skill("customer-skill"):
  Tool registry += [list_customers, create_customer, edit_customer]
  Visible: 13 tools
```

### Skill tiers

| Skill              | Tier      | `adk_additional_tools`                                                                    |
|--------------------|-----------|-------------------------------------------------------------------------------------------|
| `support-skill`    | Preloaded | _(none — `fetch_support_knowledge` always in `_preloaded_toolset`)_                       |
| `invoice-skill`    | Lazy      | `list_invoices`, `get_invoice`, `get_invoice_summary`, `create_invoice`, `edit_invoice`   |
| `customer-skill`   | Lazy      | `list_customers`, `create_customer`, `edit_customer`                                      |
| `product-skill`    | Lazy      | `list_products`, `create_product`, `edit_product`                                         |
| `email-skill`      | Lazy      | `send_invoice_by_email`                                                                   |
| `invitation-skill` | Lazy      | `invite_user`                                                                             |
| `insights-skill`   | Lazy      | _(none — self-fetching components; see Insight Panels section)_                           |

### Turn flow

```text
Turn 1 -- user: "create an invoice for Acme"
  activated_skills=[] -> tools: 5 (meta + preloaded)
  model calls: load_skill("invoice-skill")
  state["_adk_activated_skill_a2ui_mcp"] = ["invoice-skill"]
  load_skill returns: prose instructions only (no schemas)

Turn 2 -- model continues
  activated_skills=["invoice-skill"] -> tools: 10
  model calls: create_invoice(...)   <- direct MCP call
  result returned; agent emits prose + ---a2ui_JSON--- + confirm surface
```

---

## File Structure

```text
adk-agent-samples/
│
├── a2ui_schema.json            # A2UI v0.8 array schema — shared by gateway + agent
│
├── agent_gateway/              # Generic FastAPI server (agent-agnostic)
│   ├── __init__.py
│   ├── main.py                 # POST /chat, GET /chat/stream, GET /agents, POST /agents/switch
│   ├── a2ui_parser.py          # parse_a2ui_response() — end-of-turn buffering
│   ├── registry.py             # Agent name → root_agent (lazy import)
│   ├── session_manager.py      # Per-session Runner + asyncio.Queue
│   └── pyproject.toml
│
├── agents/a2ui_mcp/web_client/            # Vite + React 18 + @a2ui/react
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── .env.example            # VITE_AGENT_GATEWAY_URL=http://localhost:8000
│   └── src/
│       ├── App.tsx             # Split pane: ChatPanel (left) + SurfacePanel (right)
│       ├── api/agent.ts        # fetch wrappers for gateway endpoints
│       ├── components/
│       │   ├── ChatPanel.tsx   # Scrollable thread + input
│       │   ├── SurfacePanel.tsx # <A2UIProvider onAction> + <A2UIRenderer> per surface
│       │   ├── AgentSwitcher.tsx
│       │   └── StatusBar.tsx
│       └── hooks/
│           ├── useChat.ts      # SSE consumer; opens stream before POST
│           └── useAgents.ts
│
└── agents/a2ui_mcp/
    ├── SPEC.md                 # this file
    ├── __init__.py             # sys.path guard + re-exports root_agent, app
    ├── agent.py                # Root agent — SkillToolset + filtered preloaded McpToolset
    ├── app.py                  # App wrapper (ContextCacheConfig + EventsCompactionConfig)
    ├── a2ui_schema.py          # Loads ../../a2ui_schema.json (used by agent_gateway)
    ├── prompts/
    │   ├── root_agent.txt      # Skill-loading instructions + A2UI protocol block
    │   └── summarizer.txt      # Compact summarizer for EventsCompactionConfig
    └── skills/
        ├── support-skill/SKILL.md    # Preloaded — no adk_additional_tools
        ├── invoice-skill/SKILL.md    # Lazy — 5 invoice tools + A2UI surface specs
        ├── customer-skill/SKILL.md   # Lazy — 3 customer tools + A2UI surface specs
        ├── product-skill/SKILL.md    # Lazy — 3 product tools + A2UI surface specs
        ├── email-skill/SKILL.md      # Lazy — send_invoice_by_email (no surface)
        ├── invitation-skill/SKILL.md # Lazy — invite_user + invitation form surface
        └── insights-skill/SKILL.md  # Lazy — no tools; emits component name + params only
```

---

## `agent.py`

```python
root_agent = Agent(
    model="gemini-3-flash-preview",
    name="a2ui_mcp",
    description="Billy accounting assistant — native SkillToolset pattern",
    generate_content_config=types.GenerateContentConfig(
        temperature=0,
        thinking_config=types.ThinkingConfig(thinking_level="LOW", include_thoughts=False),
    ),
    instruction=_instruction,       # root_agent.txt with {preloaded_skills_section} resolved
    tools=[_preloaded_toolset, _skill_toolset],
    after_tool_callback=prefer_structured_tool_response,
    before_model_callback=make_history_prune_callback([
        "fetch_support_knowledge",
        "list_customers", "list_products",
        "list_invoices", "get_invoice", "get_invoice_summary",
        "get_invoice_lines_summary",
    ]),
)
```

`_preloaded_toolset` — `McpToolset` filtered to `fetch_support_knowledge` only.
`_skill_toolset` — `SkillToolset` with `additional_tools=[get_billy_toolset()]` as candidate pool;
resolves the active subset per turn from `adk_additional_tools` in each loaded skill's SKILL.md.

---

## `app.py`

```python
app = App(
    name="a2ui_mcp",
    root_agent=root_agent,
    context_cache_config=ContextCacheConfig(
        min_tokens=2048,
        ttl_seconds=1800,
        cache_intervals=5,
    ),
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=8,
        overlap_size=2,
        summarizer=_summarizer,
    ),
)
```

`ContextCacheConfig` requires `constraints/gcp.resourceLocations` org policy to allow
caching in the project's region. On a 400 FAILED_PRECONDITION, contact the platform team.

---

## Context Caching

The `tools` field in the API request grows as skills are activated within a session.
Within a single conversation the tool set only grows (never shrinks), so the cache key
is stable after each activation. Across cold sessions the key starts at the same
minimal value (5 tools) and grows identically — good cache hit rate in practice.

For scenarios requiring perfect per-request stability, pre-activate all skills at
session start to fix the tool set at its maximum size.

---

## Context Compaction

`EventsCompactionConfig(compaction_interval=8, overlap_size=2)` — fires every 8 events,
preserving the 2 most recent for continuity.

After compaction:

- `state["_adk_activated_skill_a2ui_mcp"]` **persists** → activated tools remain in the
  registry on the next turn.
- `load_skill` response bodies are **gone** from history — the model no longer has the
  HOW-TO instructions for each loaded skill.
- Recovery: the summarizer emits `"Skills loaded: invoice, customer."` so the model
  re-calls `load_skill` before acting.

No `sync_loaded_skills` callback is needed — tool availability is governed by session
state, not by event history.

---

## Context Pruning

`make_history_prune_callback([...])` registered as `before_model_callback`. Redacts the
response payload of old tool calls from prior turns to keep the prompt lean, without
mutating session storage. Pruned tools:

- `fetch_support_knowledge` — RAG payloads can be large; the answer is in the agent's reply
- `list_customers`, `list_products`, `list_invoices` — list results are stale once rendered
- `get_invoice`, `get_invoice_summary` — detail payloads no longer needed after rendering

---

## Insight Panels

`insights-skill` uses a **self-fetching component** architecture that differs from all
other skills. The agent emits no tool calls and no aggregated data. It only names the
React component and passes filter parameters via `updateDataModel`. The component then
fetches its own data directly from the Billy REST API (`/insights/*` endpoints).

### Why self-fetching

Generating correctly aggregated JSON for charts inside the model is fragile: the model
must group, sort, and bucket raw invoice data in-context, and a single arithmetic error
produces a misleading chart. Self-fetching components move aggregation to SQL — fast,
correct, and consistent across re-renders.

### Example turn flow

```text
User: "Show Acme's overdue invoices"
                ↓
  Agent: load_skill("insights-skill")
                ↓
  Agent emits (no tool calls):
    ---a2ui_JSON---
    createSurface("main")
    updateDataModel  { "contactName": "Acme" }
    updateComponents { "component": "AgingReport" }
                ↓
  React AgingReport reads contactName from data model
  → GET /insights/aging-report?contact_name=Acme
                ↓
  Billy REST resolves "Acme" → "Acme A/S" (partial match)
  → returns bucketed unpaid invoices for that customer
                ↓
  AgingReport renders heat strip + collapsible buckets
```

### Panel inventory

| Component             | REST endpoint                  | Key filter params                             |
| --------------------- | ------------------------------ | --------------------------------------------- |
| `RevenueSummary`      | `/insights/revenue-summary`    | `fiscal_year`                                 |
| `InvoiceStatusChart`  | `/insights/invoice-status`     | `fiscal_year`                                 |
| `RevenueChart`        | `/insights/monthly-revenue`    | `fiscal_year`                                 |
| `TopCustomersTable`   | `/insights/top-customers`      | `fiscal_year`, `limit`                        |
| `AgingReport`         | `/insights/aging-report`       | `contact_id`, `contact_name`                  |
| `CustomerInsightCard` | `/insights/customer-summary`   | `contact_id` or `contact_name`, `fiscal_year` |
| `ProductRevenueTable` | `/insights/product-revenue`    | `fiscal_year`                                 |

All `/insights/*` endpoints default to the current calendar year when `fiscal_year`
is omitted. `AgingReport` ignores fiscal year — it always reflects current open
invoices. Customer name resolution uses `LIKE '%name%'` (case-insensitive SQLite).

### Out of scope (current implementation)

- Real-time auto-refresh — surfaces are rendered on demand only
- Filter controls on the surface itself — users filter via chat
- Quarter / date-range bucketing — panels are monthly or fiscal-year only
- Multi-year overlay on `RevenueChart`
- Export to CSV / PDF
- Multi-currency consolidation — all amounts DKK only
- VAT reporting

---

## Running Locally

```bash
# 1. Start the Billy MCP server
cd mcp_servers/billy
uv run python app/main.py

# 2. Start agent_gateway (from repo root)
uv run uvicorn agent_gateway.main:app --reload --port 8000

# 3. Start the web client
cd agents/a2ui_mcp/web_client
npm install
npm run dev   # → http://localhost:5173
```

Or use the ADK web UI directly (text only, no A2UI surfaces):

```bash
adk web agents/a2ui_mcp
```

---

## Adding a New Skill

1. Create `skills/<name>/SKILL.md` with `name`, `description`,
   `metadata.adk_additional_tools`, and A2UI surface emit instructions.
2. Tool names in `adk_additional_tools` must exactly match the MCP tool names in
   `mcp_servers/billy/app/common.py`.
3. Add the directory name to `_LAZY_SKILLS` in `agent.py`.
4. If the skill needs a new A2UI surface shape, describe it in the skill's
   "Emit A2UI surfaces" rule section.

No changes to `_preloaded_toolset`, `Agent.tools`, or `agent_gateway/` are needed.
