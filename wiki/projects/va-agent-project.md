---
title: VA Agent Project
tags: [adk, langgraph, mcp, pattern, project]
summary: Billy accounting VA agent — dual ADK+LangGraph implementations over a shared MCP tool layer, 57 tools across 11 domains, all 9 phases complete including long-term memory and artefact store.
updated: 2026-04-24
sources:
  - raw/claude-docs/playground/docs/plans/va-agent-improvements.md
  - raw/claude-docs/playground/docs/plans/va-agent-systems.md
  - raw/claude-docs/playground/docs/plans/va-infra.md
  - raw/claude-docs/playground/docs/components.md
---

# VA Agent Project

## What It Is

A conversational accounting assistant for Billy (Danish SMB accounting software). Two parallel agent implementations — one on Google ADK, one on LangGraph — share the same tool layer, output schema, and gateway API contract. The goal is a controlled comparison of the two frameworks at production scale.

**Repo location:** `playground/va-google-adk/` and `playground/va-langgraph/`

---

## Stack

| Layer | Technology |
|---|---|
| ADK implementation | `va-google-adk` — root router + 11 domain sub-agents |
| LangGraph implementation | `va-langgraph` — `StateGraph` with analyze → route → domain subgraph → format |
| Tool layer | Billy MCP stub server (`mcp_servers/billy/`) — FastMCP + SQLite |
| Shared schema | `AssistantResponse` Pydantic model — same across both gateways |
| Gateway | FastAPI SSE (`POST /chat`, `GET /chat/stream`) — identical API for both |
| Long-term memory | SQLite `preference_store` (shared/memory.py) |
| Artefact store | SQLite + local/S3 backends (shared/artefact_store.py) |
| Infrastructure | Docker Compose (local), Terraform `va_agents` stack (ECS Fargate + ALB + RDS) |

---

## Key Architecture Decision: MCP Stub is Permanent Dev Infra

The Billy MCP server (`mcp_servers/billy/`) is **not a temporary placeholder** — it is permanent development infrastructure. The tool function signatures never change; the backend that executes them does:

```
Tool interface (function signatures + docstrings)
              ↓                             ↓
       Dev / CI / staging            Production
   Billy MCP stub server         Real Billy REST API
   (FastMCP → SQLite)            (httpx + OAuth + org_id)
```

Production is a separate implementation of the same interface (`BILLY_BACKEND=api`), built when real API access is available. Agent code remains unchanged.

---

## AssistantResponse Schema

All responses from both agent implementations conform to a shared Pydantic model:

```python
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
    chart_data: ChartData | None = None  # structured series for frontend rendering
    metric_cards: list[MetricCard] | None = None  # KPI tiles
    alert: Alert | None = None           # proactive warning
    artefact_id: str | None = None       # reference to stored artefact
    artefact_url: str | None = None      # download URL
```

---

## LangGraph Graph Topology

```
START
  → guardrail      (size, injection, PII — blocked? → END)
  → analyze        (classify intent + confidence)
  → route          (conditional edge → domain subgraph)
    ├─ invoice_graph
    ├─ quote_graph
    ├─ customer_graph
    ├─ product_graph
    ├─ email_graph       (interrupt_before — HITL confirm for external send)
    ├─ invitation_graph  (interrupt_before — HITL confirm)
    ├─ expense_graph
    ├─ banking_graph
    ├─ insights_graph
    ├─ accounting_graph  (save_artefact after generate_handoff_doc)
    ├─ memory_graph      (remember/forget — → END, no format node)
    ├─ escalation_graph  (interrupt — human handoff path)
    └─ support_graph     (CRAG loop: retrieve → grade → rewrite → retrieve)
  → format         (llm.with_structured_output(AssistantResponse))
  → END
```

### AgentState

```python
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    session_id: str
    user_id: str
    user_preferences: list[str]
    page_url: str | None
    intent: str | None
    confidence: float
    domain_result: dict | None
    response: AssistantResponse | None
    blocked: bool
    block_reason: str | None
    pending_action: dict | None
```

---

## ADK Design Principles

- **Root router has no `output_schema`** — it only routes. Schema on root causes validation failures (the routing text won't conform).
- **Each domain sub-agent has `output_schema=AssistantResponse`** — each expert writes its own structured response.
- **Context compaction:** `EventsCompactionConfig(compaction_interval=10, overlap_size=2, summarizer=LlmEventSummarizer(...))` — already implemented, still works in ADK 1.31.
- **Escalation:** `before_model_callback` checks trigger tokens; emits structured `escalation` event.
- **Guardrails:** `BeforeAgentCallback` on root agent runs injection detection + PII redaction.

---

## AgentRuntime Protocol

Both gateways expose the same API contract via a shared Protocol:

```python
class AgentRuntime(Protocol):
    async def run(self, input: AgentInput) -> AgentOutput: ...
    def stream(self, input: AgentInput) -> AsyncIterator[StreamEvent]: ...
    async def resume(self, thread_id: str, value: object) -> AgentOutput: ...
```

One FastAPI app can hot-swap backends via `VA_BACKEND=adk|langgraph` env var.

---

## Streaming: `.astream_events(v2)`

LangGraph's `.astream(stream_mode="updates")` delivers node-level diffs only — it cannot produce token-level text chunks. Use `.astream_events(version="v2")` to get both:

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

---

## HITL — Destructive Op Confirmation

Three operations warrant confirmation before execution:

- `send_invoice_by_email` / `send_quote_by_email` (external send)
- `void_invoice` (irreversible)
- `invite_user` (external invite)

**LangGraph:** `interrupt_before` on the relevant nodes. Gateway returns `AssistantResponse(confirm=True)`. Client posts approve/reject to `POST /chat/resume` → `Command(resume=user_response)`.

---

## Support CRAG Loop

`support_graph` mini StateGraph replaces single-pass retrieval:

```
retrieve  → fetch_support_knowledge(query)
grade     → Gemini Flash: {sufficient: bool, reason: str}
sufficient? → generate
not sufficient (≤2 retries) → rewrite (rephrase query) → retrieve
```

Max 2 rewrite iterations to cap cost. Same `fetch_support_knowledge` MCP tool — only the loop is new.

---

## Long-Term Memory

`shared/memory.py` — async SQLite `preference_store(user_id, key, value, updated_at)`:

- Keys: `pref:<name>` for explicit preferences; `session:<id>` for episodic summaries
- `MEMORY_DB_PATH` env var (default `memory.db`); production can swap to Postgres
- Injection: `memory_load_node` (LangGraph) / `_before_agent_callback` (ADK) prepend top-3 preferences to context
- Episodic summary: `run_turn()` finally block generates 1-sentence LLM summary per session
- LangGraph `memory` intent: analyze routes to `memory_node` → END (no format node needed)

---

## Artefact Store

`shared/artefact_store.py` — SQLite `artefacts` table (same `memory.db` file):

- Backends: `local` (default, `./artefacts/`) and `s3` (boto3)
- `ARTEFACT_TTL_DAYS` env var (default 30); retention policy stored per record
- Gateway endpoints: `POST /artefacts`, `GET /artefacts/{id}/download`, `DELETE /artefacts/{id}`
- Pattern: accounting subgraph calls `save_artefact` after `generate_handoff_doc`; returns `artefact_id` + `artefact_url` in `AssistantResponse`
- **Why:** keeps large generated documents (PDFs, reports) out of the conversation context

---

## Tool Inventory (57 tools, 11 domains)

| Domain | Tools |
|---|---|
| Invoices | 17 (CRUD + insight panel + aging + DSO + void + reminder) |
| Quotes | 6 (CRUD + conversion stats) |
| Customers | 4 (CRUD + single) |
| Products | 4 (CRUD + single) |
| Emails | 1 |
| Invitations | 1 |
| Support | 1 (`fetch_support_knowledge`) |
| Expenses | 7 (CRUD + category summary + vendor spend + gross margin) |
| Banking | 5 (balance + transactions + reconcile + forecast + runway) |
| Insights | 6 (net margin + product margin + concentration + DSO trend + break-even + anomaly) |
| Accounting | 5 (VAT + unreconciled + audit score + period summary + handoff doc) |

---

## Phase Completion Status

All 9 phases complete as of 2026-04-21:

| Phase | Content |
|---|---|
| 1 | Wire va agents to Billy MCP server |
| 2 | Complete MCP server coverage (register all 6 unregistered insight tools, add missing tools) |
| 3 | Architecture hardening (AgentRuntime Protocol, model factory, HITL, escalation, CRAG, streaming v2) |
| 4 | Expenses domain (profitability, break-even, cost clusters) |
| 5 | Banking domain (runway, cashflow forecast, reconciliation) |
| 6 | Cross-domain insights (net margin, anomaly detection, customer concentration) |
| 7 | Accounting domain (Danish VAT, audit readiness, handoff doc) |
| 8 | Long-term memory (SQLite preference store, episodic summaries) |
| 9 | Artefact store (local/S3 backends, download endpoint, TTL policy) |

---

## Infrastructure (va_agents Terraform Stack)

```
ECS Fargate cluster: va-agents
  va-gateway-adk task (1 vCPU / 2GB)
  va-gateway-lg task  (1 vCPU / 2GB)
  billy-mcp task      (256 CPU / 512MB)
ALB: path-based routing /adk/* → ADK, /lg/* → LG
RDS Postgres: va_billy DB + va_checkpoints DB
Secrets Manager: GATEWAY_API_KEY, GEMINI_API_KEY, ANTHROPIC_API_KEY, POSTGRES_URL
```

**SSE over ALB:** `idle_timeout = 300` (5 min). Sticky sessions for session affinity. HTTP/1.1 keep-alive is sufficient — no NLB needed.

**Auth:** API key middleware (`X-API-Key` header), not ALB Cognito. Rotate via Secrets Manager without redeploying.

---

## Multi-Provider Model Factory

```python
# shared/model_factory.py
def resolve_llm(size: Literal["small", "medium", "large"]) -> BaseChatModel: ...
```

Reads `LLM_PROVIDER` (gemini | anthropic | openai). LLM instances cached via `lru_cache`. Lets CI/evals swap to cheaper models without code changes. Prefix caching enabled on Anthropic: `cache_control: {"type": "ephemeral"}` set in factory, never in caller code.

---

## Relationship to Shine Copilot

The VA agent is the active implementation of the broader [[Shine Copilot Architecture]]. The ADK outer shell maps to the Copilot orchestration coordination layer (VA team responsibility); the LangGraph domain subgraphs map to the execution layer (domain team responsibility). The `support_graph` CRAG loop is the prototype for [[Shine Knowledge Agent]] — same retrieval pattern, smaller scope.

AGT-09 (ADK vs LangGraph spike, ✅ Q2 2026) was the formal decision task that validated both frameworks — state management, MCP support, observability, prefix caching, and voice compatibility. See [[ADK vs LangGraph Decision]].

---

## See Also
- [[Shine Copilot Architecture]]
- [[Shine Knowledge Agent]]
- [[ADK vs LangGraph Comparison]]
- [[ADK Context Engineering]]
- [[MCP Protocol]]
- [[Plan and Execute Pattern]]
- [[Production Hardening Patterns]]
- [[Agent Memory Types]]
- [[Agentic Workflow Patterns]]
- [[Multi-Modal Agent Response]]
