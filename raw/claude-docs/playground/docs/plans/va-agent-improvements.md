# Plan: VA Agent Improvements — Tool × Domain Roadmap

> Status: Revised — 2026-04-21 (components 2.1–2.4 incorporated)
> Scope: `playground/va-google-adk` + `playground/va-langgraph`
> Framing: tool-function × domain perspective; each new tool directly addresses
> one or more BA discovery questions from the feature inventory.

---

## 0. Tool backend architecture — dev vs prod

The tool layer is the **abstraction boundary**. Function signatures never change;
the backend that executes them does.

```
Tool interface (function signatures + docstrings)
              ↓                             ↓
       Dev / CI / staging            Production
   Billy MCP stub server         Real Billy REST API
   (FastMCP → SQLite)            (httpx + OAuth + org_id)
   adk-agent-pocs/               va-google-adk / va-langgraph
     mcp_servers/billy/            shared/tools/ backed by
                                   direct httpx calls
```

**Dev stub** (`mcp_servers/billy/`) — already exists, 110 tests passing:
- MCP server on `:8765` (`main_noauth.py` — stdio or SSE)
- REST API on `:8766` (`main.py` — FastAPI, Swagger at `/docs`)
- SQLite `billy.db` — persistent, seeded, shared across both servers
- Controlled by `BILLY_DB` env var; `reset_db.py` reloads full fixture

**Production path** (future, not blocking dev) — same tool signatures, different
implementation: thin httpx wrapper around the real Billy REST API, OAuth token
from session state, `organisation_id` injected per-request. Controlled by
`BILLY_BACKEND=api` env var when that layer is built.

**Consequence for the build order**: Phase 7 from the previous plan ("replace stubs
with real API") was wrong. The MCP stub is *permanent dev infrastructure*, not
a temporary placeholder. Production is a separate implementation of the same
interface, built when we have real API access.

---

## 1. Current state at a glance

### 1a. va agents (in-memory Python dicts — not wired to MCP)

| Domain | Tools today | Capability type |
|--------|------------|-----------------|
| Invoices | `get_invoice`, `list_invoices`, `get_invoice_summary`, `create_invoice`, `edit_invoice` | Ask + Execute |
| Quotes | `list_quotes`, `create_quote`, `create_invoice_from_quote` | Ask + Execute |
| Customers | `list_customers`, `create_customer`, `edit_customer` | Ask + Execute |
| Products | `list_products`, `create_product`, `edit_product` | Ask + Execute |
| Emails | `send_invoice_by_email`, `send_quote_by_email` | Act |
| Invitations | `invite_user` | Act |
| Support | `fetch_support_knowledge` | Guide |
| **Expenses** | — | MISSING |
| **Banking** | — | MISSING |
| **Insights** | — | MISSING |
| **Accounting** | — | MISSING |

State mutations do not persist between agent restarts (in-memory). No insight
analytics. Quotes domain not in MCP server at all (va-specific addition).

### 1b. MCP stub server — what already exists

Registered in MCP (`common.py`):

| Tool | Domain |
|------|--------|
| `list_customers`, `create_customer`, `edit_customer` | Customers |
| `get_invoice`, `list_invoices`, `get_invoice_summary`, `create_invoice`, `edit_invoice` | Invoices |
| `get_insight_monthly_revenue`, `get_insight_top_customers` | Insights (partial) |
| `list_products`, `create_product`, `edit_product` | Products |
| `send_invoice_by_email` | Emails |
| `invite_user` | Invitations |
| `fetch_support_knowledge` | Support |

Implemented in `invoices.py` but **NOT yet registered in MCP** (REST-only):

| Tool | What it does |
|------|--------------|
| `get_insight_revenue_summary` | KPI cards: invoiced / collected / outstanding / overdue with YoY delta |
| `get_insight_invoice_status` | Status breakdown: draft / unpaid / paid / overdue |
| `get_insight_aging_report` | AR aging buckets: Current / 1–30 / 31–60 / 61–90 / 90+ days |
| `get_insight_customer_summary` | Per-customer KPIs + open invoice list |
| `get_insight_product_revenue` | Products ranked by revenue with quantity sold |
| `get_invoice_lines_summary` | Revenue per product (invoice lines join) |

Missing from MCP server entirely (no domain, no table):
- Quotes (`list_quotes`, `create_quote`, `create_invoice_from_quote`, `send_quote_by_email`)
- Expenses
- Banking
- Accounting

---

## 2. Tool × domain gap matrix

### 2.1 Gaps within existing domains

These all go into the **MCP server first**, then the agents consume them via MCP.

**Invoices** — missing from both MCP and agents:

| Tool | Signature | Addresses |
|------|-----------|-----------|
| `get_invoice_dso_stats` | `(contact_id?, year?) → {avg_days_to_pay, trend, overdue_rate}` | Are payments getting slower? |
| `send_invoice_reminder` | `(invoice_id, message?) → {sent: bool}` | Collections tightening |
| `void_invoice` | `(invoice_id, reason) → {voided: bool}` | Invoice lifecycle — cancel/void |

Note: `get_revenue_by_customer` and `get_revenue_by_product` are already covered by
`get_insight_top_customers` and `get_insight_product_revenue` — just need MCP registration.

**Quotes** — missing entirely from MCP server (no schema, no table):

| Tool | Signature | Addresses |
|------|-----------|-----------|
| `list_quotes` | `(states?, contact_id?, page?) → {quotes, total}` | Pipeline visibility |
| `create_quote` | `(contact_id, lines, expiry_days?) → quote` | Quote authoring flow |
| `edit_quote` | `(quote_id, contact_id?, lines?, expiry_days?) → quote` | Quote lifecycle |
| `create_invoice_from_quote` | `(quote_id) → invoice` | Quote-to-revenue conversion |
| `send_quote_by_email` | `(quote_id, contact_id, subject, body) → {sent: bool}` | Quote delivery |
| `get_quote_conversion_stats` | `(year?) → {sent, accepted, declined, conversion_rate}` | Pipeline health |

Requires adding a `quotes` table to `db.py` and a new `tools/quotes.py` in the MCP server.

**Customers** — missing from MCP:

| Tool | Signature | Addresses |
|------|-----------|-----------|
| `get_customer` | `(customer_id) → full record` | Single customer detail |

Note: `get_customer_revenue_summary` is already `get_insight_customer_summary` — needs
MCP registration.

**Products** — missing from MCP:

| Tool | Signature | Addresses |
|------|-----------|-----------|
| `get_product` | `(product_id) → full record with price` | Single product detail |

Note: `get_product_revenue_summary` is already `get_insight_product_revenue` — needs
MCP registration.

---

### 2.2 Expenses domain — single highest-leverage item

Unlocks the entire **Profitability**, **Break-even**, and **Costs** discovery clusters
(≈12 questions currently gapped). All downstream domains (Banking runway, Insights margin)
are blocked on this.

All tools go into the MCP server (`app/tools/expenses.py` + `quotes` table in `db.py`):

| Tool | Signature | Addresses |
|------|-----------|-----------|
| `list_expenses` | `(date_from?, date_to?, category?, vendor?, page?) → {expenses, total}` | What did I spend on X? |
| `get_expense` | `(expense_id) → full record` | Expense detail |
| `create_expense` | `(vendor, amount, date, category?, description?, vat_amount?) → expense` | Log a new expense |
| `get_expense_summary` | `(year?, period?) → {total, by_category: [{cat, amount, pct}]}` | Total by category; MoM shift |
| `get_vendor_spend` | `(vendor?, year?) → [{vendor, total, count}]` | Vendor audit |
| `get_expenses_by_category` | `(year?) → [{category, total, fixed_or_variable}]` | Fixed vs variable cost split |
| `get_gross_margin` | `(year?, period?) → {revenue, cogs, gross_margin_pct}` | Are COGS creeping up? |

`fixed_or_variable` classification: start with a user-settable flag on the category
(column in the DB); LLM inference at query time is a Phase 6+ enhancement.

---

### 2.3 Banking domain

Blocked on Expenses (burn rate requires expense history). Build after Expenses.

| Tool | Signature | Addresses |
|------|-----------|-----------|
| `get_bank_balance` | `() → [{account, balance, currency}]` | Current balance; cashflow health |
| `list_bank_transactions` | `(date_from?, date_to?, account_id?, page?) → {transactions, total}` | Upcoming payments |
| `match_transaction_to_invoice` | `(transaction_id, invoice_id) → {matched: bool}` | Bank reconciliation |
| `get_cashflow_forecast` | `(months?) → [{month, projected_inflow, projected_outflow, net}]` | 90-day forecast |
| `get_runway_estimate` | `() → {balance, avg_monthly_burn, runway_months}` | How many months of runway? |

---

### 2.4 Insights domain — mostly already built, needs wiring

6 of 8 insight tools exist in `invoices.py` but are not registered in MCP.
Cross-domain tools (margin, break-even) are new — blocked on Expenses being in the DB.

**Already built, need MCP registration only:**
`get_insight_revenue_summary`, `get_insight_invoice_status`, `get_insight_aging_report`,
`get_insight_customer_summary`, `get_insight_product_revenue`, `get_invoice_lines_summary`

**New — depend on Expenses data:**

| Tool | Signature | Addresses |
|------|-----------|-----------|
| `get_net_margin` | `(period?) → {revenue, total_costs, net_profit, net_margin_pct}` | After paying everything, what's my net margin? |
| `get_margin_by_product` | `(year?) → [{product, revenue, cogs, margin_pct}]` | Which offers have the highest margin? |
| `get_customer_concentration` | `(year?) → {top_1_pct, top_3_pct, hhi}` | Am I over-dependent on a few clients? |
| `get_dso_trend` | `(months?) → [{month, avg_dso}]` | Are payments getting slower over time? |
| `get_break_even_estimate` | `() → {fixed_costs, variable_rate, break_even_revenue}` | What do I have to hit to stay safe? |
| `detect_anomaly` | `(metric, period?) → {anomalies: [...]}` | What drove Q3 spike? |

---

### 2.5 Accounting domain

Requires Expenses in DB + RAG corpus (Danish VAT rules). Build after both.

| Tool | Signature | Addresses |
|------|-----------|-----------|
| `get_vat_summary` | `(quarter, year) → {output_vat, input_vat, net_vat_payable}` | Danish VAT periods / audit readiness |
| `get_unreconciled_transactions` | `(days_back?) → [{transaction, amount, date}]` | What's unreconciled? |
| `get_audit_readiness_score` | `() → {score, missing_docs: [...], recommendations: [...]}` | Completeness check |
| `get_period_summary` | `(year, quarter?) → {revenue, expenses, profit, vat_position}` | P&L for accountant handoff |
| `generate_handoff_doc` | `(year, quarter?) → {markdown_summary, missing_items: [...]}` | Handoff doc generation |

---

## 3. AssistantResponse schema additions

Current schema covers action outputs but is thin on analytics. Needed before
Insights / Banking UX can work:

| Field | Type | Purpose |
|---|---|---|
| `chart_data` | `ChartData \| None` | Structured series data for frontend chart rendering |
| `metric_cards` | `list[MetricCard] \| None` | KPI tiles: net margin, runway, DSO |
| `alert` | `Alert \| None` | Proactive warning (e.g. "3 invoices 14+ days overdue") |

```python
class ChartData(BaseModel):
    chart_type: Literal["bar", "line", "pie", "area"]
    title: str
    labels: list[str]
    series: list[dict]  # [{name, data: [float]}]

class MetricCard(BaseModel):
    label: str
    value: str                                              # "42%" or "DKK 123,456"
    trend: str | None                                       # "+12% vs last period"
    sentiment: Literal["positive", "neutral", "negative"] | None

class Alert(BaseModel):
    severity: Literal["info", "warning", "critical"]
    message: str
    action_label: str | None
    action_route: str | None
```

---

## 4. Architecture improvements (from rag_poc comparison)

### 4.1 AgentRuntime Protocol
Both gateways share the same API contract but have no formal interface. Define one:

```python
# shared/runtime_protocol.py
class AgentRuntime(Protocol):
    async def run(self, input: AgentInput) -> AgentOutput: ...
    def stream(self, input: AgentInput) -> AsyncIterator[StreamEvent]: ...
    async def resume(self, thread_id: str, value: object) -> AgentOutput: ...
```

One FastAPI app could then hot-swap backends via `VA_BACKEND` env var.

### 4.2 LangGraph — injected checkpointer
Current `va-langgraph` hardcodes `MemorySaver()`. Port rag_poc pattern:

```python
def build_graph(checkpointer) -> CompiledGraph: ...
test_graph = build_graph(MemorySaver())    # test / CLI
```

Swap in `AsyncSqliteSaver` (local dev) or `AsyncPostgresSaver` (prod) in the
FastAPI lifespan without touching graph logic.

### 4.3 Multi-provider model factory
Currently hardcoded Gemini. Port rag_poc's `_resolve_model()`:

```python
# shared/model_factory.py
def resolve_llm(size: Literal["small", "medium", "large"]) -> BaseChatModel: ...
```

Reads `LLM_PROVIDER` (gemini | anthropic | openai). Lets CI/evals swap to cheaper
models without code changes.

### 4.4 ADK 1.30 compatibility
`EventsCompactionConfig` was removed in ADK 1.30. `va-google-adk/agents/va_assistant/app.py`
must switch to `before_model_callback` history pruning (rag_poc pattern) if ADK ≥1.30
is pinned. Check `pyproject.toml` before acting.

### 4.5 HITL — interrupt before destructive ops (LangGraph only)
Add `interrupt_before` on the email, void, and invite nodes. Wire gateway
`POST /chat/resume` to `Command(resume=user_response)`.

Destructive ops that warrant confirmation:
- `send_invoice_by_email` / `send_quote_by_email` (external send)
- `void_invoice` (irreversible)
- `invite_user` (external invite)

### 4.6 Context compaction (components 2.1, 2.2)
Long conversations will exceed model token limits without a compaction strategy.

**ADK**: ✅ Already implemented — `App(events_compaction_config=EventsCompactionConfig(
compaction_interval=10, overlap_size=2, summarizer=LlmEventSummarizer(...)))` in `app.py`.
No work needed.

**LangGraph**: Still needed. Use `langchain_core.messages.trim_messages` before each
LLM call in `base.py`'s `run_domain` — keep the most recent N tokens, preserving the
system message and last human turn. Threshold configurable via `MAX_HISTORY_TOKENS`
env var (default 12 000).

### 4.7 Prefix / context caching (components 2.1)
Stable prompt prefix (system prompt + tool schemas) should be reused across turns
rather than re-transmitted. Wiring:

- **Gemini** (both gateways): system prompt is implicitly cached by the API when
  unchanged. Ensure the system prompt is constructed once per session, not per turn.
- **Anthropic** (if model factory adds Claude): set `cache_control: {"type": "ephemeral"}`
  on the system prompt block. Handle in `model_factory.py` so callers never touch it.

### 4.8 Escalation trigger — human supporter handoff (components 2.1)
Separate from destructive-op HITL. Add an escalation path when the agent cannot
resolve a request:

```python
ESCALATION_TRIGGERS = [
    "speak to a human", "talk to support", "this isn't working",
    # low-confidence signal: routing_confidence < 0.3 after 2 turns
]
```

LangGraph: add an `escalation` node that `interrupt()`s with `{"type": "escalation",
"reason": ...}`. Gateway exposes `POST /chat/resume` (already planned) — same
endpoint handles both HITL confirm and escalation resolution.

ADK: `before_model_callback` checks for trigger tokens; emits a structured
`escalation` event to the client.

### 4.9 Token budget / query size guard (components 2.1)
Prevent abuse and runaway context from oversized user inputs. Add at the gateway
request layer — not in the agent — so both ADK and LG share the same guard:

```python
MAX_MESSAGE_CHARS = int(os.getenv("MAX_MESSAGE_CHARS", "4000"))
if len(req.message) > MAX_MESSAGE_CHARS:
    raise HTTPException(status_code=400, detail="Message too long")
```

Also track per-turn token count in `run_turn` and log a warning when a turn
exceeds `WARN_TURN_TOKENS` (default 8 000) — feeds future cost observability.

### 4.10 Observability — trace_id propagation (components 2.2)
`trace_id` is a 2.2 hard constraint: every stored turn must carry it.

**Phase 3 scope (code-only)**:
- Accept `X-Trace-Id` header at the gateway; fall back to `request_id` if absent
- Propagate `trace_id` through `run_turn(...)` → LangGraph config metadata →
  logged in every `tool_result` SSE event

**Deferred (separate infra initiative)**:
- LangFuse SDK wiring (needs project key + dashboard)
- DataDog / OTelemetry exporter (needs agent sidecar or lambda layer)

### 4.11 Guardrails — complete the pipeline (systems plan §3, §4)

**LangGraph** (`graph/nodes/guardrail.py`) — 3/4 checks already done (✅ size, ✅ injection,
✅ PII). Still missing:
- Domain check: if `routing_confidence < 0.2` after the analyze node, short-circuit
  to `direct_node` with an out-of-domain reply instead of invoking a domain subgraph.
  Add as a conditional edge in `builder.py` (not in `guardrail_node` — happens after analysis).

**ADK** — No `BeforeAgentCallback` equivalent yet. Add one to `root_agent` in `agent.py`:
- Port the same injection detection + PII redaction from LangGraph's `guardrail_node`
  into a `before_agent_callback` function
- Size truncation is already handled by `EventsCompactionConfig`
- Out-of-domain is already handled by `report_out_of_domain()` tool (no change needed)

### 4.12 Support CRAG loop — LangGraph `support_subgraph` (systems plan §4)

Current `support_subgraph` calls `fetch_support_knowledge` in a single pass and stops.
Replace with a retrieve → grade → rewrite → retrieve loop:

```
support_subgraph (mini StateGraph):
  retrieve  → fetch_support_knowledge(query)
  grade     → Haiku call: is this result sufficient to answer the question? (yes/no)
  sufficient? → generate (write AssistantResponse with sources)
  not sufficient (≤2 retries) → rewrite (rephrase query) → retrieve
```

Grader is a `ChatGoogleGenerativeAI(model="gemini-2.0-flash")` call with a binary
output schema `{sufficient: bool, reason: str}`. Max 2 rewrite iterations to cap cost.

### 4.13 LangGraph streaming upgrade — `.astream_events()` (systems plan §4)

Current `runner.py` uses `.astream(stream_mode="updates")` — delivers node-level diffs
only. The gateway contract (`va-agent-systems.md` §2c) includes a `text` event type
for streaming token chunks, which this mode cannot produce.

Switch to `.astream_events(version="v2")`:
```python
async for event in self._graph.astream_events(initial_state, config=config, version="v2"):
    kind = event["event"]
    if kind == "on_chat_model_stream":
        chunk = event["data"]["chunk"].content
        if chunk:
            await session.queue.put({"type": "text", "data": chunk})
    elif kind == "on_chain_end" and event["name"] == "format":
        ...  # extract final AssistantResponse from node output
```

This gives the frontend token-level streaming for the message field while still
capturing structured `response` events when the format node completes.

---

## 5. Build order (revised)

Work always flows: **MCP server first → agents consume via MCP**.

```
Phase 1 — Wire va agents to MCP server  ✅ DONE
  ├── va-langgraph: MultiServerMCPClient in every domain subgraph (domains.py) ✅
  ├── va-google-adk: MCPToolset(SseConnectionParams) in every sub-agent ✅
  └── shared/tools/*.py deleted; shared/schema.py kept ✅

Phase 2 — Complete MCP server coverage  ✅ DONE
  ├── Register all 6 unregistered insight tools in common.py ✅
  │   (get_insight_revenue_summary, get_insight_invoice_status,
  │    get_insight_aging_report, get_insight_customer_summary,
  │    get_insight_product_revenue, get_invoice_lines_summary)
  ├── Add get_customer to customers.py + register ✅
  ├── Add get_product to products.py + register ✅
  ├── Add void_invoice, send_invoice_reminder, get_invoice_dso_stats to invoices.py + register ✅
  ├── Add edit_quote, get_quote_conversion_stats to quotes.py + register ✅
  │   (quotes table + tools/quotes.py already existed; added missing tools)
  ├── va-langgraph: insights_subgraph + updated all tool filters ✅
  ├── va-langgraph: analyze_node + builder.py updated for insights routing ✅
  └── va-google-adk: insights_agent sub-agent + updated all sub-agent tool filters ✅

Phase 3 — Architecture hardening  ✅ DONE
  ├── AgentRuntime Protocol (shared/runtime_protocol.py) ✅
  ├── Multi-provider model factory (shared/model_factory.py) ✅
  ├── ADK 1.30 compatibility check ✅ (EventsCompactionConfig still present in 1.31 — no change needed)
  ├── AssistantResponse: add chart_data + metric_cards + alert fields ✅
  ├── Context compaction: ADK ✅ done; LangGraph trim_messages in run_domain ✅
  ├── Prefix caching: LLM instances cached via lru_cache in model_factory ✅
  ├── Escalation trigger — LangGraph: escalation_node + intent; ADK: before_model_callback ✅
  ├── Token budget guard at ADK gateway (MAX_MESSAGE_CHARS=4000) ✅
  ├── trace_id propagation (X-Trace-Id header → run_turn → SSE events, both gateways) ✅
  ├── Guardrails: LangGraph confidence edge (ROUTING_CONFIDENCE_THRESHOLD=0.2) ✅
  │   ADK before_model_callback injection detection + escalation ✅
  ├── Support CRAG loop — retrieve → grade → rewrite (max 2 retries) in support_subgraph ✅
  └── LangGraph streaming upgrade to .astream_events(v2) for text token chunks ✅

Phase 4 — Expenses domain  ✅ DONE
  ├── MCP server: expenses table in db.py + tools/expenses.py + register in common.py ✅
  ├── va-google-adk: expense_agent sub-agent ✅
  └── va-langgraph: expense_subgraph node + 'expense' intent in analyze + builder ✅

Phase 5 — Banking domain  ✅ DONE
  ├── MCP server: bank_accounts + bank_transactions tables + 2 seed accounts + 6 seed transactions ✅
  │   tools/banking.py: get_bank_balance, list_bank_transactions, match_transaction_to_invoice,
  │   get_cashflow_forecast, get_runway_estimate — registered in common.py ✅
  ├── va-google-adk: banking_agent sub-agent + prompts/banking_agent.txt + wired into root agent ✅
  └── va-langgraph: banking_subgraph + 'banking' intent in analyze_node + node + edges in builder ✅

Phase 6 — Cross-domain Insights  ✅ DONE
  ├── MCP server: tools/insights.py with 6 cross-domain tools ✅
  │   (get_net_margin, get_margin_by_product, get_customer_concentration,
  │    get_dso_trend, get_break_even_estimate, detect_anomaly)
  │   Registered in common.py ✅
  ├── va-google-adk: insights_agent tool_filter + description + prompts/insights_agent.txt ✅
  ├── va-langgraph: _INSIGHTS_TOOLS + _INSIGHTS_SYSTEM updated in domains.py ✅
  └── AssistantResponse: chart_data + metric_cards already in schema (Phase 3) ✅

Phase 7 — Accounting domain  ✅ DONE
  ├── MCP server: tools/accounting.py with 5 tools ✅
  │   (get_vat_summary, get_unreconciled_transactions, get_audit_readiness_score,
  │    get_period_summary, generate_handoff_doc) — registered in common.py ✅
  │   Note: Danish VAT domain knowledge encoded in tool docstrings + agent prompt;
  │   no separate RAG corpus needed — computed directly from structured DB data.
  ├── va-google-adk: accounting_agent sub-agent + prompts/accounting_agent.txt ✅
  │   Wired into root agent sub_agents list + description updated ✅
  └── va-langgraph: accounting_subgraph node + 'accounting' intent in analyze_node ✅
      _ACCOUNTING_TOOLS + _ACCOUNTING_SYSTEM + node + edges in builder.py ✅

Phase 8 — Long-term memory  ✅ DONE
  ├── shared/memory.py — SQLite preference_store(user_id, key, value, updated_at) ✅
  │   Async via asyncio.to_thread; same schema for both LangGraph and ADK.
  │   Keys: pref:<name> for preferences; session:<id> for episodic summaries.
  │   MEMORY_DB_PATH env var (default memory.db); production can swap to Postgres.
  ├── Episodic summary: runner.run_turn() finally block generates 1-sentence
  │   LLM summary and saves to preference_store(session:<id>) ✅ (LangGraph + ADK)
  ├── Retrieval: memory_load_node (LangGraph) and _before_agent_callback (ADK)
  │   inject top-3 recent preferences into AgentState / session state ✅
  │   analyze_node prepends [User preferences: ...] to user_text ✅
  │   provide_router_instruction injects preferences into ADK router context ✅
  ├── LangGraph "memory" intent: analyze_node + memory_node + builder wired ✅
  │   "remember/forget" requests routed to memory_node → END (no format_node)
  ├── ADK tools: update_user_preference + delete_user_preference on root agent ✅
  │   tool_context.state used to get user_id and update in-session prefs list
  ├── user_id field added to ChatRequest (both gateways, default="default") ✅
  └── AgentState extended: user_id + user_preferences fields ✅

  Deferred to later pass:
  - Vector DB for semantic memory retrieval
  - Inferred preferences (confidence threshold)
  - Cross-session RAG over episodic summaries

Phase 9 — Artefact store  ✅ DONE
  ├── shared/artefact_store.py — SQLite artefacts table (same memory.db) ✅
  │   Async via asyncio.to_thread; no new dependencies for local backend.
  │   Backends: local (default, ./artefacts/) and s3 (boto3, env ARTEFACT_BACKEND=s3).
  │   ARTEFACT_LOCAL_DIR, ARTEFACT_S3_BUCKET, ARTEFACT_TTL_DAYS, GATEWAY_BASE_URL env vars.
  │   Same file in both va-langgraph/ and va-google-adk/.
  ├── Gateway endpoints (both gateways) ✅
  │   POST /artefacts          → save(), returns {artefact_id, url}
  │   GET  /artefacts/{id}/download → read_local() → stream file (local) or 404
  │   DELETE /artefacts/{id}   → soft_delete() (sets deleted_at)
  ├── AssistantResponse: artefact_id + artefact_url Optional[str] fields ✅
  │   Added to shared/schema.py in both projects.
  ├── LangGraph: save_artefact LangChain @tool in accounting_subgraph ✅
  │   Closure captures session_id from state. Added to tools alongside MCP tools.
  │   _ACCOUNTING_SYSTEM updated to instruct calling save_artefact after generate_handoff_doc.
  │   format_node _SYSTEM updated to mention artefact_id/artefact_url fields.
  ├── ADK: save_artefact async function tool in accounting_agent ✅
  │   tool_context.state used to get session_id. Added to agent tools list.
  │   accounting_agent.txt prompt updated to call save_artefact after generate_handoff_doc.
  └── Retention policy: ARTEFACT_TTL_DAYS env var (default 30 days) stored per record ✅

  Deferred to later pass:
  - Active TTL expiry cleanup job (records stay in DB; files persist past TTL until pruned)
  - S3 presigned URL redirect for local gateway (download endpoint returns file inline for local)
  - Artefact listing endpoint (GET /artefacts?session_id=...)

Production path  (separate track, not gating dev phases)
  ├── BILLY_BACKEND=api → direct httpx wrapper around real Billy REST API
  ├── OAuth token injection from session state
  ├── Organisation ID per-request
  └── Same tool signatures — agent code unchanged
```

---

## 6. Discovery question coverage after each phase

| After phase | New coverage | Still gaps |
|-------------|-------------|------------|
| 0 (today) | Revenue mostly, DSO partial | Profitability, Break-even, Costs, Banking |
| +Phase 1 (MCP wired) | Persistent state mutations; insight panels live via MCP | Same domain gaps |
| +Phase 2 (MCP complete) | DSO analytics, AR aging, customer summary, product revenue, quote pipeline | Profitability, Break-even, Costs, Banking |
| +Phase 3 (hardening) | Compaction, caching, escalation, trace_id — no new domain coverage | Same |
| +Phase 4 (Expenses) | Profitability cluster, Break-even, most of Costs | Banking, cross-domain margin |
| +Phase 5 (Banking) | Runway, cashflow forecast, balance | Cross-domain Insights |
| +Phase 6 (Insights) | Net margin, anomaly detection, customer concentration, break-even | Accounting/VAT |
| +Phase 7 (Accounting) | Audit readiness, VAT periods, handoff doc | Long-term memory, Artefacts |
| +Phase 8 (Long-term memory) | User preferences recalled cross-session; episodic session summaries | Artefacts |
| +Phase 9 (Artefact store) ✅ | Generated docs / reports stored outside prompt; downloadable from UI | Real Billy data (Production path) |

---

## 7. Open questions

| Phase | Question | Why it blocks |
|-------|----------|---------------|
| Phase 1 | Which ADK version is pinned? `EventsCompactionConfig` removed in 1.30 | Affects ADK MCPToolset wiring approach |
| Phase 1 | Does va-google-adk use one MCPToolset per sub-agent or shared at root? | Affects token count and session scope |
| Phase 2 | Should `send_invoice_reminder` be a new MCP tool or reuse `send_invoice_by_email` with a reminder flag? | Affects DB schema (reminder log?) |
| Phase 4 | How is `fixed_or_variable` classified for expenses? User-set flag vs LLM inference | Affects `get_expenses_by_category` and break-even calc |
| Phase 5 | Is bank balance from Billy's own bank reconciliation view, or a separate open-banking connector? | Determines whether Banking is in the Billy MCP stub or a new server |
| Phase 6 | Data quality threshold before suppressing a metric? | Avoids misleading partial metrics (e.g. margin with 2 months of expenses) |
| Prod path | Shared `tools/` package vs copy-per-project? | Currently the MCP approach makes this moot for dev; matters for prod httpx layer |

---

## 8. What this does NOT cover

- **Snowflake feature store** — cross-org analytics; separate data pipeline
- **Price recommender** — needs market benchmark data outside Billy
- **Recurring invoice automation** — Act capability requiring event triggers
- **Web client** — frontend; separate initiative
- **Eval suites** — separate quality initiative
- **LangFuse / DataDog wiring** — observability infra (separate initiative); trace_id
  propagation IS in Phase 3 so LangFuse can be bolted on later with no agent changes
- **Voice agent compatibility** — same session store for text and voice turns; spike needed
- **Semantic / vector-based memory retrieval** — deferred past Phase 8 (simple
  recency + key-match is the Phase 8 baseline)
- **Inferred user preferences** — confidence-threshold promotion deferred past Phase 8
- **Open-banking connector** — Banking domain (Phase 5) assumes Billy's own bank
  reconciliation view; real open-banking is a separate connector

---

## Appendix: full tool inventory after all phases

### MCP server (`mcp_servers/billy/app/tools/`)

```
invoices.py     get_invoice, list_invoices, get_invoice_summary, create_invoice,
                edit_invoice, void_invoice, send_invoice_reminder, get_invoice_dso_stats,
                get_invoice_lines_summary,
                get_insight_revenue_summary, get_insight_invoice_status,
                get_insight_monthly_revenue, get_insight_top_customers,
                get_insight_aging_report, get_insight_customer_summary,
                get_insight_product_revenue                              [17]

quotes.py       list_quotes, create_quote, edit_quote,
                create_invoice_from_quote, send_quote_by_email,
                get_quote_conversion_stats                               [6]

customers.py    list_customers, create_customer, edit_customer,
                get_customer                                             [4]

products.py     list_products, create_product, edit_product,
                get_product                                              [4]

emails.py       send_invoice_by_email                                    [1]
invitations.py  invite_user                                              [1]
support_knowledge.py  fetch_support_knowledge                           [1]

expenses.py     list_expenses, get_expense, create_expense,
                get_expense_summary, get_vendor_spend,
                get_expenses_by_category, get_gross_margin              [7]

banking.py      get_bank_balance, list_bank_transactions,
                match_transaction_to_invoice, get_cashflow_forecast,
                get_runway_estimate                                      [5]

insights.py     get_net_margin, get_margin_by_product,
                get_customer_concentration, get_dso_trend,
                get_break_even_estimate, detect_anomaly                 [6]

accounting.py   get_vat_summary, get_unreconciled_transactions,
                get_audit_readiness_score, get_period_summary,
                generate_handoff_doc                                     [5]

Total: 57 tools across 11 domain files
```

### Agent domains (mirror MCP tool groupings)

ADK: one sub-agent per domain (11 sub-agents after all phases)
LangGraph: one subgraph node per domain (11 domain nodes after all phases)
Both: `shared/schema.py` (AssistantResponse) — no tool code, only output contract
