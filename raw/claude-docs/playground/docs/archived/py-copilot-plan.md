# Plan: Python Copilot Service

**Status:** Draft — awaiting review
**Scope:** `v2/py_copilot/` — new service, does not touch `playground/` or `v2/ts_google_adk/`
**Goal:** Replicate `ts_google_adk` in Python to surface engineering friction, then use that
         understanding to inform which parts of the stack get replaced by the Python RAG pipeline.

---

## What We Are Building

A Python FastAPI + Google ADK service that is **functionally equivalent** to `ts_google_adk`:
same tools, same output schema, same session model, same knowledge fallback — but in Python.
This is an intentional replication, not an architectural improvement. The friction we encounter
during the port is the product of this exercise.

In a second phase, we swap `fetch_support_knowledge` from Bedrock KB direct calls to the
playground RAG pipeline — this is the structural win that Python uniquely enables.

---

## Project Layout

```
v2/py_copilot/
  src/
    agents/
      accounting.py          # LlmAgent definition, instruction, tool wiring
      schema.py              # AccountingOutput (Pydantic v2)
      tools/
        __init__.py
        invoices.py          # get_invoice, list_invoices, get_invoice_summary,
                             #   create_invoice, edit_invoice, create_invoice_from_quote
        customers.py         # list_customers, create_customer, edit_customer
        products.py          # list_products, create_product, edit_product
        quotes.py            # list_quotes, create_quote
        emails.py            # send_invoice_by_email, send_quote_by_email
        invitations.py       # invite_user
        knowledge.py         # fetch_support_knowledge
    lib/
      billy_client.py        # httpx async wrapper + helper API lookups
      billy_context.py       # ContextVar for per-request (api_token, org_id)
      session_service.py     # ADK session service factory
      feedback.py            # Feedback storage (mirrors TS message_feedback table)
    interfaces/
      api.py                 # FastAPI app — POST /chat, GET /sessions/{id}/summary
  tests/
    tools/
      conftest.py            # Mock httpx transport fixtures
      test_invoices.py
      test_customers.py
      test_products.py
      test_quotes.py
      test_emails.py
      test_knowledge.py
    test_schema.py           # AccountingOutput Pydantic round-trip tests
    test_context.py          # ContextVar propagation under asyncio
  pyproject.toml
  .env.example
  Dockerfile
```

---

## Friction Point Inventory and Mitigations

This is the core of the plan. Each friction point from the architectural analysis has a specific
mitigation strategy.

---

### Friction 1 — Per-Request Context (Auth Token + Org ID)

**TS approach:** `AsyncLocalStorage` from `node:async_hooks`. Node guarantees that the stored
value propagates through all `await` calls within the same async context, including callbacks
and event emitter chains. The ADK runner never breaks this because it runs in the same Node
event loop.

**Python equivalent:** `contextvars.ContextVar`. Python's `asyncio` propagates `ContextVar`
values through `await` chains within the same task. **Critical risk:** `asyncio.create_task()`
copies the current context snapshot — mutations in the child task do not propagate back to the
parent. If the ADK runner spawns tool calls as independent tasks (it does not currently, but
this is an internal implementation detail), the ContextVar would be stale in those tasks.

**Mitigation:**

```python
# lib/billy_context.py
from contextvars import ContextVar, copy_context
from dataclasses import dataclass

@dataclass(frozen=True)
class BillyConfig:
    api_token: str
    organization_id: str

_config: ContextVar[BillyConfig | None] = ContextVar("billy_config", default=None)

def set_billy_config(token: str, org_id: str) -> None:
    _config.set(BillyConfig(api_token=token, organization_id=org_id))

def get_billy_config() -> BillyConfig:
    cfg = _config.get()
    if cfg is None:
        raise RuntimeError(
            "BillyConfig not set — did the FastAPI endpoint call set_billy_config() "
            "before invoking the runner?"
        )
    return cfg
```

The FastAPI endpoint sets the context before calling `runner.run_async()`. Since ADK tool calls
happen within the same asyncio task (verified against `google-adk 0.5.x` source), the ContextVar
is live throughout.

**Validation test required:** `test_context.py` must verify that a tool function can read
`get_billy_config()` from within a `runner.run_async()` call with a mocked agent. If the ADK
internals ever change, this test catches it immediately.

**Fallback:** If the ContextVar approach fails (e.g. ADK spawns tasks), inject config as a
tool callback parameter instead — the ADK `ToolContext` carries `session.state`, which persists
across turns. Store `(api_token, org_id)` in `session.state` on first turn.

---

### Friction 2 — Tool Schema Generation

**TS approach:** `new FunctionTool({ name, description, parameters: z.object(...), execute })`.
The Zod schema is explicit — every parameter has a description, type, and optionality declared
in code. The tool name and description are always exactly what was written.

**Python approach:** ADK auto-generates schemas from type annotations and docstrings.
The parameter descriptions come from `Args:` sections in Google-style docstrings. This is
implicit and fragile — a missing `Args:` entry means no description in the schema.

**Mitigation:**

Use explicit `google.adk.tools.FunctionTool` wrapping instead of bare function registration
for tools with complex parameters (line items, nested objects). For simple tools, bare functions
with well-structured docstrings are fine:

```python
# Simple tool — bare function, auto-schema
async def get_invoice(invoice_id: str) -> dict:
    """Gets detailed information about a single invoice by its ID.

    Returns full invoice details including amounts, dates, payment status,
    line items, and a PDF download URL.

    Args:
        invoice_id: The invoice ID to look up.
    """
    ...

# Complex tool — TypedDict for nested params, explicit description
class InvoiceLine(TypedDict, total=False):
    product_id: str
    description: str
    quantity: float
    unit_price: float

async def create_invoice(
    contact_id: str,
    lines: list[InvoiceLine],
    entry_date: str | None = None,
    currency_id: str = "DKK",
    payment_terms_days: int = 7,
    state: Literal["approved", "draft"] = "approved",
) -> dict:
    """Creates a new invoice in the accounting system.
    ...
    """
```

**Schema validation test:** Each tool file has a test that calls
`FunctionDeclaration.from_callable(tool_fn)` and asserts the generated schema matches the
expected JSON schema. This catches docstring formatting errors before they reach the model.

---

### Friction 3 — Structured Output (AccountingOutput)

**TS approach:** `outputSchema: accountingOutputSchema` (Zod). Gemini receives the JSON schema
and is constrained to produce conforming output. Zod then validates the parsed response.

**Python approach:** `output_schema=AccountingOutput` (Pydantic v2). ADK converts the Pydantic
model to a JSON schema and passes it to Gemini. Known rough edges:

1. **Optional nested models with `None` defaults**: Gemini sometimes outputs `null` for optional
   objects, sometimes omits the key entirely. Pydantic handles both, but ADK's schema generation
   may mark the field as `required` even when `Optional`.
2. **`list` fields**: Empty lists `[]` vs omitted fields — the model instruction must be
   explicit ("use an empty array `[]`, never omit the field").
3. **`Literal` unions**: Pydantic v2 generates `const` schemas for single-value Literals, which
   Gemini handles correctly, but union Literals (e.g. `Literal["bar", "line", "pie"]`) must be
   verified.

**Mitigation:**

```python
# schema.py — defensive defaults, all fields explicit
class AccountingOutput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    message: str
    suggestions: list[str] = Field(default_factory=list)
    nav_buttons: list[NavButton] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)
    table_type: Literal["invoices", "customers", "products", "quotes"] | None = None
    form: Form | None = None
    email_form: EmailForm | None = None
    confirm: bool | None = None
    contact_support: bool | None = None
    chart: Chart | None = None
```

The instruction explicitly states: "All list fields must be arrays (use `[]` for empty,
never omit). All optional object fields should be `null` when not needed."

`test_schema.py` generates 10 representative Gemini responses (fixture JSON) and validates
that `AccountingOutput.model_validate(response)` succeeds for each, including edge cases
(all nulls, nested chart, emailForm with optional `to` field).

---

### Friction 4 — httpx AsyncClient Lifecycle

**TS:** `fetch()` is a global — no lifecycle to manage.

**Python:** `httpx.AsyncClient` should be reused across requests for connection pooling,
but per-request instantiation is safe for low-volume use. The risk is inadvertent client
reuse across requests with different auth tokens.

**Mitigation:** A context manager factory that creates a client configured for the current
request's token:

```python
# lib/billy_client.py
from contextlib import asynccontextmanager
import httpx

@asynccontextmanager
async def get_client(cfg: BillyConfig):
    headers = {
        "Authorization": f"Bearer {cfg.api_token}",
        "x-access-token": cfg.api_token,
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(
        base_url=settings.billy_api_base_url,
        headers=headers,
        timeout=30.0,
    ) as client:
        yield client
```

Each tool call does `async with get_client(get_billy_config()) as client:`.
Per-request client creation is acceptable given typical LLM latency (100ms+ per turn).
If throughput becomes a bottleneck, move to a connection pool keyed by org_id.

---

### Friction 5 — Two-Step Quote Creation

**TS:** `createQuote` POSTs the quote header, then POSTs each line sequentially in a for loop.
This is straightforward but means N+1 API calls.

**Python:** Identical logic but with explicit `async for` + `await` per line. No difference
in behavior, but it makes the sequential dependency visible. Python's `asyncio.gather()` cannot
be used here because each line POST requires the `quoteId` from the quote header POST.

**Mitigation:** Document this explicitly in the tool docstring so future engineers don't attempt
to parallelize the line creation. Add an integration test that verifies line ordering is preserved.

---

### Friction 6 — ADK Session Service

**TS:** `new DatabaseSessionService({ driver: PostgreSqlDriver, ...getDbConfig() })`.
MikroORM handles schema creation via `schemaGenerator.ensureDatabase()`.

**Python:** `DatabaseSessionService(db_url=DATABASE_URL)` uses SQLAlchemy. ADK's Python
`DatabaseSessionService` calls `Base.metadata.create_all()` on startup — it auto-creates
its session table. No migration needed.

**Risk:** The TS and Python services share the same postgres instance. ADK's TS
`DatabaseSessionService` and Python `DatabaseSessionService` use different table schemas.
They must use different `app_name` values in the runner to isolate their session namespaces.

**Mitigation:**
- TS: `app_name = "copilot-ts"`
- Python: `app_name = "copilot-py"`

Sessions are not portable between the two services — this is expected during the comparison phase.

---

## Implementation Steps

### Step 0 — Scaffold (pyproject.toml + .env.example)

Dependencies:
```toml
[project]
dependencies = [
    "google-adk>=0.5.0",
    "fastapi>=0.115",
    "uvicorn[standard]",
    "httpx>=0.27",
    "pydantic>=2.7",
    "pydantic-settings",
    "structlog",
    "boto3",          # Bedrock KB (Phase 1)
    "asyncpg",        # Postgres session service
    "sqlalchemy[asyncio]",
]

[project.optional-dependencies]
dev = ["pytest", "pytest-asyncio", "respx", "ruff", "pyright"]
```

---

### Step 1 — Context + Client (`lib/`)

Implement `billy_context.py` and `billy_client.py` per the friction mitigations above.
Include `get_default_sales_account()`, `get_default_payment_method()`, `get_org_defaults()`
as async helpers — each makes one Billy.dk API call and returns a typed dict.

---

### Step 2 — Output Schema (`agents/schema.py`)

Pydantic v2 translation of `accountingOutputSchema`. Run `test_schema.py` with 10 fixture
responses before proceeding.

---

### Step 3 — Execution Tools (all 17, grouped by file)

Port order:

1. `invoices.py` — highest value, most complex (6 tools)
2. `customers.py` — 3 tools, straightforward
3. `products.py` — 3 tools, needs `get_default_sales_account`
4. `quotes.py` — 2 tools, sequential line creation
5. `emails.py` — 2 tools, contactPerson lookup
6. `invitations.py` — 1 tool, simplest

Each file gets a corresponding `test_tools/test_{file}.py` that mocks `httpx` via `respx`
and validates the tool's return shape.

---

### Step 4 — Knowledge Tool (`tools/knowledge.py`)

**Phase 1 — Bedrock parity:**

```python
import boto3
import asyncio
from concurrent.futures import ThreadPoolExecutor

_executor = ThreadPoolExecutor(max_workers=4)
_client = boto3.client("bedrock-agent-runtime", region_name=settings.aws_region)

async def fetch_support_knowledge(queries: list[str]) -> str:
    """Search the official support documentation.

    Runs all queries in parallel against the Bedrock knowledge base,
    deduplicates results, and returns the top passages as JSON.

    Args:
        queries: A list of 2-3 search terms or phrases (Danish).
    """
    loop = asyncio.get_event_loop()
    results = await asyncio.gather(*[
        loop.run_in_executor(_executor, _retrieve, q) for q in queries
    ])
    # dedup + score filter (mirror TS getUniqueResults + toPassages)
    ...
```

Note: `boto3` is synchronous. Wrap in `run_in_executor` to avoid blocking the event loop.
`aioboto3` is an alternative but adds a dependency — prefer the executor pattern for now.

**Phase 2 — RAG pipeline swap:**

Replace the boto3 call with:
```python
async with httpx.AsyncClient() as client:
    resp = await client.post(
        settings.rag_service_url + "/query",
        json={"queries": queries},
        timeout=15.0,
    )
    return resp.text
```

The playground's FastAPI service (`src/interfaces/api/`) serves as the RAG backend.
This swap requires no changes to the tool signature or the agent — only the tool body changes.

---

### Step 5 — LlmAgent (`agents/accounting.py`)

```python
from google.adk.agents import LlmAgent
from agents.schema import AccountingOutput
from agents.tools import (all tool imports)

accounting_agent = LlmAgent(
    name="accounting_assistant",
    model="gemini-2.5-flash-preview-04-17",
    description="An accounting assistant for invoices, customers, products, and quotes.",
    output_schema=AccountingOutput,
    instruction=INSTRUCTION,
)
```

`INSTRUCTION` is the same 350-line instruction from TS, with two adaptations:
1. Field names use `snake_case` to match Pydantic (`nav_buttons` not `navButtons`)
2. The structured output section explicitly covers `[]` vs `null` behavior

---

### Step 6 — Session Service (`lib/session_service.py`)

```python
from google.adk.sessions import DatabaseSessionService, InMemorySessionService

def get_session_service():
    db_url = settings.database_url
    if db_url:
        return DatabaseSessionService(db_url=db_url)
    import warnings
    warnings.warn("DATABASE_URL not set — using InMemorySessionService")
    return InMemorySessionService()

session_service = get_session_service()
```

---

### Step 7 — FastAPI Interface (`interfaces/api.py`)

```python
@app.post("/chat", response_model=AccountingOutput)
async def chat(body: ChatRequest, request: Request):
    # 1. Inject per-request Billy context
    set_billy_config(body.api_token, body.org_id)

    # 2. Get or create ADK session
    session = await session_service.get_or_create_session(
        app_name="copilot-py",
        user_id=body.user_id,
        session_id=body.session_id,
    )

    # 3. Build runner (singleton per agent, created at startup)
    events = []
    async for event in runner.run_async(
        user_id=body.user_id,
        session_id=session.id,
        new_message=Content(role="user", parts=[Part(text=body.message)]),
    ):
        events.append(event)

    # 4. Extract and validate structured output
    output = _extract_output(events)
    return AccountingOutput.model_validate(output)

@app.get("/sessions/{session_id}/summary")
async def session_summary(session_id: str, org_id: str):
    # One-shot ADK call with summarizer instruction, no tools
    ...
```

---

## Phase 2 — RAG Pipeline Integration

After Phase 1 is working (Bedrock parity), Phase 2 connects the playground RAG service.

The playground FastAPI app (`src/interfaces/api/`) needs one new endpoint:

```
POST /query
Body: { "queries": ["string"], "session_id": "optional" }
Response: { "passages": [{"text", "url", "title", "score"}] }
```

This endpoint runs the queries through `build_graph()` (LangGraph CRAG) and returns
the top passages. The `py_copilot` knowledge tool calls this endpoint.

**Evaluation:** Run the same test query set against:
- Phase 1 (Bedrock KB direct)
- Phase 2 (LangGraph CRAG)
- Baseline (no reranking, just embedding search)

Metrics: faithfulness, answer_relevance, latency P50/P95. The playground `src/eval/`
infrastructure handles this — add a new `CopilotKnowledgeExperiment` variant.

---

## What This Surfaces

| Question | Expected Finding |
|---|---|
| Does ContextVar survive ADK tool dispatch? | Yes — verify with `test_context.py` |
| Does Pydantic output_schema work with all optional fields? | Partial — `null` vs omit divergence likely |
| Is boto3 sync wrapping painful? | Moderate — `run_in_executor` is boilerplate but workable |
| Does ADK docstring schema match Zod quality? | Lower quality — missing descriptions degrade tool calling |
| Does LangGraph CRAG improve knowledge quality? | Measure in Phase 2 eval |
