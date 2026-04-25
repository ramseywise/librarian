# Billy Stub Server

A shared server that exposes stub implementations of the Billy accounting API so any agent in this repo can call them without touching the real Billy API.

Exposes tools and insight endpoints in two ways:

- **MCP server** (`app/main_noauth.py`) — for ADK agents via `MCPToolset`, or Claude Desktop via STDIO
- **REST API** (`app/main.py`) — FastAPI server for direct HTTP access, browser testing, or non-MCP clients

Both servers share the same SQLite database (`billy.db`), so changes made via one are immediately visible to the other.

---

## Setup

```bash
cd mcp_servers/billy
uv sync
```

---

## Running

### MCP server

**STDIO mode** (for Claude Desktop or ADK `MCPToolset`):

```bash
python -m app.main_noauth
```

**HTTP/SSE mode** (for remote agents or browser testing):

```bash
python -m app.main_noauth --http
# Listening at http://127.0.0.1:8765/sse
```

Or via the convenience script from the repo root:

```bash
./scripts/run_mcp_billy.sh
```

### REST API

```bash
python -m app.main
# Docs at http://127.0.0.1:8766/docs
```

Or:

```bash
./scripts/run_billy_api.sh
```

Override ports via environment variables: `MCP_PORT` (default `8765`), `API_PORT` (default `8766`).

---

## Tools

| Tool | REST endpoint | Description |
| --- | --- | --- |
| `list_customers` | `GET /customers` | List / search customers |
| `create_customer` | `POST /customers` | Create a new customer |
| `edit_customer` | `PATCH /customers/{id}` | Update a customer record |
| `list_invoices` | `GET /invoices` | List / filter invoices |
| `get_invoice` | `GET /invoices/{id}` | Get a single invoice with line items |
| `get_invoice_summary` | `GET /invoices/summary` | Aggregate stats for a fiscal year |
| `get_invoice_lines_summary` | `GET /invoices/lines/summary` | Revenue totals grouped by product |
| `create_invoice` | `POST /invoices` | Create a new invoice |
| `edit_invoice` | `PATCH /invoices/{id}` | Update a draft invoice |
| `send_invoice_by_email` | `POST /invoices/{id}/send` | Send an approved invoice by email |
| `list_products` | `GET /products` | List / filter products |
| `create_product` | `POST /products` | Create a new product |
| `edit_product` | `PATCH /products/{id}` | Update a product record |
| `invite_user` | `POST /invitations` | Invite a user to the organisation |
| `fetch_support_knowledge` | `POST /support/search` | Search the Billy support knowledge base |

---

## Insight Endpoints

Pre-aggregated analytics endpoints consumed by the A2UI insight panels. All accept an optional `fiscal_year` query parameter (integer, e.g. `?fiscal_year=2026`). When omitted the current calendar year is used.

| Endpoint | Panel | Description |
| --- | --- | --- |
| `GET /insights/revenue-summary` | Revenue Overview | KPI cards: total invoiced, collected, outstanding, and overdue — with year-over-year deltas |
| `GET /insights/invoice-status` | Invoice Status | Count and amount split across draft, approved/unpaid, paid, and overdue invoices |
| `GET /insights/monthly-revenue` | Monthly Revenue | Invoiced vs paid amounts for each of the 12 months in the fiscal year |
| `GET /insights/top-customers` | Top Customers | Customers ranked by total revenue with paid/outstanding breakdown |
| `GET /insights/aging-report` | Aging Report | Unpaid approved invoices bucketed by days overdue: Current, 1–30, 31–60, 61–90, 90+ |
| `GET /insights/product-revenue` | Product Revenue | Products ranked by revenue with quantity sold |

### How the insight panels work

The A2UI web client contains six self-fetching React components — one per insight endpoint. When the agent responds to an analytics question it emits a lightweight A2UI surface message naming the component and optionally the fiscal year. The component then fetches its own data directly from the REST API and renders it. No data passes through the agent.

**Example prompts and the panel they trigger:**

| What you say | Panel shown |
| --- | --- |
| "Show me the revenue overview" | Revenue Overview (KPI cards with YoY delta) |
| "What's the invoice status breakdown?" | Invoice Status (segmented bar chart) |
| "Show monthly revenue for 2026" | Monthly Revenue (grouped bar chart) |
| "Who are my top customers?" | Top Customers (ranked table with progress bars) |
| "Who owes me money?" / "Aging report" | Aging Report (buckets by days overdue) |
| "Which products sell best?" | Product Revenue (ranked table with gradient bars) |

Each panel has a close (×) button in the top-right corner. Panels can be stacked — asking for multiple analyses shows them one above the other.

---

## Database

Data is persisted in `billy.db` (SQLite) next to this README. The file is created automatically on first run.

The database is initialised and seeded with 3 customers, 5 products, and 3 invoices the first time any tool module is imported. Subsequent starts reuse the existing file.

To reset to the full mock dataset (5 customers, 7 products, 10 invoices):

```bash
# from mcp_servers/billy
uv run python reset_db.py

# or from the repo root
./scripts/reset_billy_db.sh
```

Override the database path:

```bash
BILLY_DB=/tmp/test.db python -m app.main_noauth
```

---

## Connecting from an ADK agent

**STDIO** — server is spawned as a subprocess:

```python
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

toolset = MCPToolset(
    connection_params=StdioServerParameters(
        command="python",
        args=["-m", "app.main_noauth"],
        cwd="mcp_servers/billy",
    )
)
```

**HTTP/SSE** — after starting with `--http`:

```python
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams

toolset = MCPToolset(
    connection_params=SseServerParams(url="http://127.0.0.1:8765/sse")
)
```

---

## Tests

```bash
uv run pytest
```

The test suite runs 110 tests covering all tool functions and all REST endpoints. Each test gets a clean, seeded database via a `fresh_db` fixture — no shared state between tests.

---

## Further Reading

- [SPEC.md](SPEC.md) — full specification: schema, tool contracts, REST API, data model, configuration
