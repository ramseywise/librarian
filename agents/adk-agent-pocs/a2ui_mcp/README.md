# a2ui_mcp

A Billy accounting assistant that renders its responses as interactive UI surfaces
using the [A2UI protocol](https://a2ui.org). Ask it to list customers, create an
invoice, invite a collaborator, or pull up a financial dashboard — and a live,
clickable interface appears alongside the chat.

---

## How it works

The agent combines two mechanisms:

**Lazy skill loading** — domain tools (invoices, customers, products, analytics, etc.)
are gated behind `load_skill`. The model calls `load_skill("invoice-skill")` the first
time an invoice operation is needed; afterwards the tools for that domain are available
directly for the rest of the session. This keeps the tool registry small per turn and
avoids bloating the system prompt with instructions for domains the user never touches.

**A2UI output** — after every substantive response the agent appends a
`---a2ui_JSON---` delimiter followed by a JSON array of A2UI v0.9 messages. The
`agent_gateway/` FastAPI server parses these and streams them to the React frontend,
where they are rendered as interactive surfaces:

```text
User: "list customers"
                  ↓
  Agent calls: load_skill("customer-skill")
               list_customers()
                  ↓
  Agent responds:
    Here are your customers.
    ---a2ui_JSON---
    [
      { "version": "v0.9", "createSurface": { "surfaceId": "main", "catalogId": "https://a2ui.org/catalog/basic/v0.8/catalog.json" } },
      { "version": "v0.9", "updateDataModel": { "surfaceId": "main", "path": "/", "value": { "customers": [...] } } },
      { "version": "v0.9", "updateComponents": { "surfaceId": "main", "components": [...] } }
    ]
                  ↓
  gateway parses → streams text + a2ui events via SSE
                  ↓
  React client renders customer list with Edit buttons
```

Clicking a surface button (e.g. Edit) fires a `[ui_event]` message back to the agent,
which acts directly without re-asking for confirmation.

---

## Prerequisites

- Python ≥ 3.11 with [uv](https://docs.astral.sh/uv/) installed
- Node.js ≥ 18 with npm
- A Gemini API key (or Vertex AI credentials — see `.env.example` at repo root)

---

## Setup

**1. Install Python dependencies** (from repo root):

```bash
uv sync
```

**2. Install web client dependencies:**

```bash
cd agents/a2ui_mcp/web_client
npm install
cd ../../..
```

**3. Configure environment:**

```bash
cp .env.example .env
# Edit .env and set GOOGLE_API_KEY
```

---

## Running

Open four terminals from the repo root:

**Terminal 1 — Billy MCP server** (`http://localhost:8765`):

```bash
./scripts/run_mcp_billy.sh
```

**Terminal 2 — Billy REST API** (`http://localhost:8766`):

```bash
./scripts/run_billy_api.sh
```

**Terminal 3 — Agent gateway** (`http://localhost:8000`):

```bash
BILLY_MCP_URL=http://127.0.0.1:8765/sse ./scripts/run_agent_gateway.sh
```

**Terminal 4 — Web client** (`http://localhost:5173`):

```bash
./scripts/run_a2ui_web_client.sh
```

Open <http://localhost:5173> in a browser.

---

## Try it

Once all three services are running, try these prompts in the chat:

### Data & forms

| Prompt | What you'll see |
| ------ | --------------- |
| `list customers` | Customer list with Edit buttons |
| `show invoice dashboard` | Stats cards + invoice list |
| `list products` | Product catalog with Edit buttons |
| `invite someone@example.com` | Invitation confirmation surface |
| `create an invoice for Acme A/S` | Line-item form + confirmation |

Click **Edit** on any row to open a detail form. Fill in the fields and click **Save** —
the agent calls the underlying tool and refreshes the surface.

### Financial insights

The agent has a dedicated analytics skill that renders rich visual panels. Each panel
fetches its own data directly from the Billy REST API — no raw numbers pass through
the agent.

| Prompt | Panel | What you'll see |
| ------ | ----- | --------------- |
| `Show me the revenue overview` | Revenue Overview | KPI cards — total invoiced, collected, outstanding, overdue — with year-over-year percentage deltas |
| `What's the invoice status breakdown?` | Invoice Status | Segmented bar showing the count and amount split across draft, approved, paid, and overdue invoices |
| `Show monthly revenue for 2026` | Monthly Revenue | Grouped bar chart with invoiced vs paid bars for each month of the year |
| `Who are my top customers?` | Top Customers | Ranked table with avatar initials, stacked revenue/payment progress bars, and outstanding balance badges |
| `Who owes me money?` / `Aging report` | Aging Report | All unpaid invoices bucketed by days overdue: Current, 1–30, 31–60, 61–90, 90+ |
| `Show Acme's overdue invoices` | Aging Report (filtered) | Same aging view scoped to one customer — name matched partially |
| `Show me a summary for Acme A/S` | Customer Summary | Single-customer KPIs (invoiced, collected, outstanding, overdue) + list of open invoices with overdue badges |
| `What does Nordisk Tech owe me?` | Customer Summary | Same — partial name match, so `"Nordisk"` finds `"Nordisk Tech A/S"` |
| `Which products sell best?` | Product Revenue | Products ranked by revenue with gradient bars and quantity sold |
| `Is revenue trending up?` | Monthly Revenue | Agent fetches the 12-month series, computes MoM growth rates, narrates the direction in prose, then renders the chart |
| `Compare revenue trends for 2025 and 2026` | Monthly Revenue (side-by-side) | Two `RevenueChart` panels with YoY commentary |
| `Any unusual months in my revenue?` | Monthly Revenue | Agent identifies months deviating > 50% from the monthly mean and calls them out by name before rendering the chart |

Each panel has a **×** close button in the top-right corner. Panels stack — asking for
multiple analyses shows them one above the other. You can request a different fiscal
year at any time: `"Show top customers for 2025"`.

---

## Architecture

```text
agents/a2ui_mcp/web_client/  ← Vite + React + @a2ui/react (port 5173)
      │  POST /chat
      │  GET  /chat/stream (SSE)
      ▼
agent_gateway/       ← FastAPI (port 8000)
      │  ADK Runner per session
      │  parse_a2ui_response() once per completed turn
      ▼
agents/a2ui_mcp/     ← ADK agent (SkillToolset)
      │  MCP stdio / SSE
      ▼
mcp_servers/billy/   ← FastMCP stub server (port 8765)
```

See [SPEC.md](SPEC.md) for a full technical breakdown.

---

## Skills

| Skill | Tier | Tools / Notes |
| ----- | ---- | ------------- |
| `support-skill` | Preloaded | `fetch_support_knowledge` |
| `invoice-skill` | Lazy | `list_invoices`, `get_invoice`, `get_invoice_summary`, `create_invoice`, `edit_invoice` |
| `customer-skill` | Lazy | `list_customers`, `create_customer`, `edit_customer` |
| `product-skill` | Lazy | `list_products`, `create_product`, `edit_product` |
| `email-skill` | Lazy | `send_invoice_by_email` |
| `invitation-skill` | Lazy | `invite_user` |
| `insights-skill` | Preloaded | `get_insight_monthly_revenue`, `get_insight_top_customers` — panels also self-fetch from `/insights/*` REST endpoints |

### Insights skill detail

Most insight panels work without any agent-side tool calls: the agent emits a surface
message naming the React component plus filter parameters (`year`, `contactId`,
`contactName`), and the component fetches its own data directly from the corresponding
`/insights/*` REST endpoint.

```text
User: "Show me the revenue overview"
                  ↓
  Agent emits surface only:
    ---a2ui_JSON---
    updateDataModel  { "year": 2026 }
    updateComponents { "component": "RevenueSummary" }
                  ↓
  React RevenueSummary → GET /insights/revenue-summary?fiscal_year=2026
                  ↓
  KPI cards render with live data
```

**Trend and outlier analysis** require the agent to fetch data first so it can compute
and narrate findings before rendering the chart:

```text
User: "Any unusual months in my revenue?"
                  ↓
  Agent calls: get_insight_monthly_revenue(fiscal_year=2026)
    → { months: [{month:"Jan", invoiced:42000, paid:38000}, ...] }
                  ↓
  Agent computes mean invoiced, flags months > 1.5× or < 0.5× the mean,
  narrates in prose: "April was 2× the average — driven by Acme A/S."
                  ↓
  Agent emits: updateComponents { "component": "RevenueChart" }
                  ↓
  RevenueChart renders with the spike visible in the bars
```

Customer-scoped panels pass a name rather than an ID — the backend resolves partial
names automatically:

```text
User: "Show me a summary for Acme"
                  ↓
  Agent emits: updateDataModel { "contactName": "Acme", "year": 2026 }
               updateComponents { "component": "CustomerInsightCard" }
                  ↓
  React CustomerInsightCard → GET /insights/customer-summary?contact_name=Acme&fiscal_year=2026
                  ↓
  KPI card + open invoices for Acme A/S
```

The eight available components and their data model parameters:

| Component | Parameters |
| --------- | ---------- |
| `RevenueSummary` | `year`, `month` (int 1–12, optional — filters to a single month) |
| `InvoiceStatusChart` | `year` |
| `RevenueChart` | `year` |
| `TopCustomersTable` | `year` |
| `AgingReport` | `contactId` or `contactName` (optional — omit for all customers) |
| `CustomerInsightCard` | `contactId` or `contactName` (required), `year` |
| `ProductRevenueTable` | `year` |
| `DashboardSuggestions` | `suggestions` (JSON array of strings) |

---

## Text-only mode (no web client)

To use the agent without the A2UI frontend, run it directly in the ADK web UI:

```bash
adk web agents/a2ui_mcp
```

The A2UI JSON will appear as raw text in the chat — harmless but unrendered.

---

## Adding a new skill

1. Create `skills/<name>/SKILL.md` with `name`, `description`,
   `metadata.adk_additional_tools`, and an "Emit A2UI surfaces" rule section.
2. Add the directory name to `_LAZY_SKILLS` in `agent.py`.
3. Tool names must match those registered in `mcp_servers/billy/app/common.py`.
