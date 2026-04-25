# Billy Stub Server — Specification

## Overview

A shared server that exposes 14 stub tools covering the Billy accounting API. It is designed to be used by agents in this repo without requiring a real Billy account, AWS Bedrock access, or any external network calls.

The server exposes the same tools via two independent transports that share a single SQLite database:

| Transport | Entry point | Default address | Use case |
| --- | --- | --- | --- |
| MCP (STDIO) | `app/main_noauth.py` | — | ADK `MCPToolset`, Claude Desktop |
| MCP (HTTP/SSE) | `app/main_noauth.py --http` | `http://127.0.0.1:8765/sse` | Remote agents, browser testing |
| REST API | `app/main.py` | `http://127.0.0.1:8766/docs` | Direct HTTP, non-MCP clients |

---

## File Layout

```text
app/
  main_noauth.py        MCP server entry point (STDIO and HTTP/SSE)
  main.py               FastAPI REST API entry point
  common.py             Tool registration for FastMCP (register_all)
  config.py             Environment-based configuration (HOST, PORT, SERVER_NAME)
  db.py                 SQLite persistence layer (schema, seed, get_conn, next_id)
  tools/
    customers.py        list_customers, create_customer, edit_customer
    invoices.py         list_invoices, get_invoice, get_invoice_summary,
                        create_invoice, edit_invoice  (+InvoiceLine, InvoiceLineUpdate)
    products.py         list_products, create_product, edit_product
    emails.py           send_invoice_by_email
    invitations.py      invite_user
    support_knowledge.py fetch_support_knowledge
tests/
  conftest.py           fresh_db autouse fixture — isolated SQLite per test
  test_api.py           REST API tests (46 tests, TestClient)
  test_customers.py     customer tool unit tests
  test_invoices.py      invoice tool unit tests
  test_products.py      product tool unit tests
  test_misc_tools.py    email, invitation, support knowledge tests
  test_server.py        MCP server connectivity tests
reset_db.py             CLI script — wipe and reseed billy.db with mock data
pyproject.toml          Dependencies: fastmcp, fastapi, uvicorn, boto3, python-dotenv
```

---

## Database

### Engine

SQLite via Python's built-in `sqlite3`. File path defaults to `billy.db` next to `reset_db.py`. Override with the `BILLY_DB` environment variable.

WAL journal mode is enabled on every connection so the MCP server and REST API can run concurrently without blocking each other.

### Initialisation

`app/db.py` calls `init_db()` at module import time. `init_db()` is idempotent — it uses `CREATE TABLE IF NOT EXISTS` and `INSERT OR IGNORE`, so running it multiple times is safe. The first process to import any tool module creates and seeds the database.

### Schema

**`customers`**

| Column | Type | Notes |
| --- | --- | --- |
| id | TEXT PK | `cus_NNN` |
| name | TEXT | |
| type | TEXT | `company` or `person` |
| country | TEXT | ISO code, default `DK` |
| street, city, zipcode, phone, email | TEXT | |
| contact_person_id | TEXT | `cp_NNN` — primary contact |
| registration_no | TEXT | CVR number (companies) |
| is_customer, is_supplier | INTEGER | booleans |
| created_time | TEXT | ISO 8601 |

**`products`**

| Column | Type | Notes |
| --- | --- | --- |
| id | TEXT PK | `prod_NNN` |
| name, description, product_no | TEXT | |
| unit | TEXT | `hours`, `days`, `pcs` |
| is_archived | INTEGER | boolean |

**`product_prices`**

| Column | Type | Notes |
| --- | --- | --- |
| id | TEXT PK | `price_NNNa` |
| product_id | TEXT FK → products | |
| unit_price | REAL | excl. VAT |
| currency | TEXT | default `DKK` |

**`invoices`**

| Column | Type | Notes |
| --- | --- | --- |
| id | TEXT PK | `inv_NNN` |
| invoice_no | TEXT | `YYYY-NNN` |
| contact_id | TEXT | FK → customers |
| customer_name | TEXT | denormalised |
| entry_date, due_date | TEXT | `YYYY-MM-DD` |
| state | TEXT | `draft` or `approved` |
| sent_state | TEXT | `unsent` or `sent` |
| amount, tax, gross_amount, balance | REAL | excl./incl. VAT |
| is_paid | INTEGER | boolean |
| payment_terms | TEXT | e.g. `net 7 days` |
| tax_mode | TEXT | `excl` |
| approved_time, created_time | TEXT | ISO 8601 |
| download_url, contact_message, line_description | TEXT | |

**`invoice_lines`**

| Column | Type | Notes |
| --- | --- | --- |
| id | TEXT PK | `line_INVOICEID_N` |
| invoice_id | TEXT FK → invoices | |
| product_id, description | TEXT | |
| quantity, unit_price, amount, tax | REAL | |
| unit | TEXT | |

**`counters`**

| name | Initial value | Generates |
| --- | --- | --- |
| `customer` | 4 | `cus_NNN` IDs |
| `invoice` | 4 | `inv_NNN` IDs |
| `product` | 6 | `prod_NNN` IDs |

`next_id(conn, name)` reads the current value and increments it atomically within the same transaction as the INSERT.

### Seed data

The default seed (applied by `init_db()`) inserts:

- 3 customers — Acme A/S, Nordisk Tech ApS, Lars Hansen
- 5 products — Konsulentydelser, Softwarelicens, Support & Vedligehold, Uddannelse, Rejseomkostninger (archived)
- 3 invoices — two approved (one paid, one unpaid), one draft

`reset_db.py` replaces this with a richer dataset: 5 customers, 7 products, 10 invoices spanning 2024–2025 with a mix of states.

---

## Tools

All tool functions are plain Python — no ADK dependency. They live in `app/tools/` and are imported by both `common.py` (MCP registration) and `app/main.py` (FastAPI routes).

### Customers

#### `list_customers`

```python
def list_customers(
    page: int = 1,
    page_size: int = 50,
    is_archived: bool = False,
    name: Optional[str] = None,
    sort_property: str = "name",        # "name" | "created_time"
    sort_direction: str = "ASC",        # "ASC" | "DESC"
) -> dict
```

Returns `{total, page, page_count, customers: [...]}`.

`name` is a case-insensitive substring filter. `is_archived` is accepted for API compatibility but not applied (no archived flag on customers in this stub).

#### `create_customer`

```python
def create_customer(
    name: str,
    type: Literal["company", "person"] = "company",
    country_id: str = "DK",
    street, city_text, zipcode_text, phone, registration_no, email: Optional[str] = None,
    invoicing_language: str = "en",
) -> dict
```

Returns the created customer record. `invoicing_language` is accepted but not stored.

#### `edit_customer`

```python
def edit_customer(
    contact_id: str,
    name, street, city_text, zipcode_text, phone, country_id,
    registration_no, invoicing_language, contact_person_id, email: Optional[str] = None,
) -> dict
```

Only provided fields are updated. To update the email address, both `contact_person_id` and `email` must be supplied. Returns the updated record or `{"error": "..."}`.

---

### Invoices

#### `list_invoices`

```python
def list_invoices(
    page: int = 1,
    page_size: int = 50,
    states: Optional[list[str]] = None,         # ["draft", "approved"]
    min_entry_date: Optional[str] = None,        # "YYYY-MM-DD"
    max_entry_date: Optional[str] = None,
    contact_id: Optional[str] = None,
    currency_id: Optional[str] = None,
    sort_property: str = "entry_date",           # "entry_date" | "invoice_no" | "gross_amount"
    sort_direction: str = "DESC",
) -> dict
```

Returns `{total, page, page_count, invoices: [...]}`. Each invoice in the list omits line items — use `get_invoice` for the full record.

#### `get_invoice`

```python
def get_invoice(invoice_id: str) -> dict
```

Returns the full invoice including `lines`. Returns `{"error": "..."}` if not found.

#### `get_invoice_summary`

```python
def get_invoice_summary(fiscal_year: Optional[int] = None) -> dict
```

Filters by `entry_date` year. Defaults to the current year. Returns:

```json
{
  "fiscal_year": 2024,
  "all":      {"count": N, "amount": N},
  "draft":    {"count": N, "amount": N},
  "approved": {"count": N, "amount": N},
  "paid":     {"count": N, "amount": N},
  "unpaid":   {"count": N, "amount": N},
  "overdue":  {"count": N, "amount": N}
}
```

`unpaid` and `overdue` amounts use `balance` (outstanding amount). `overdue` = unpaid approved invoices with `due_date` before today.

#### `create_invoice`

```python
class InvoiceLine(BaseModel):
    product_id: str
    quantity: float = 1
    unit_price: float
    description: Optional[str] = None

def create_invoice(
    contact_id: str,
    lines: list[InvoiceLine],
    entry_date: Optional[str] = None,    # defaults to today
    currency_id: str = "DKK",
    payment_terms_days: int = 7,
    state: str = "approved",             # "approved" | "draft"
) -> dict
```

Tax is calculated as 25% of each line amount. Returns the full invoice including `lines`.

#### `edit_invoice`

```python
class InvoiceLineUpdate(BaseModel):
    id: Optional[str] = None            # existing line ID to update; omit to add new
    product_id, description: Optional[str] = None
    quantity, unit_price: Optional[float] = None

def edit_invoice(
    invoice_id: str,
    contact_id, entry_date, state: Optional[str] = None,
    payment_terms_days: Optional[int] = None,
    lines: Optional[list[InvoiceLineUpdate]] = None,
) -> dict
```

Only works on `draft` invoices — returns `{"error": "..."}` for approved ones. When `lines` is provided, existing lines are replaced with the new set (matched by `id`). Totals are recalculated after line changes.

---

### Products

#### `list_products`

```python
def list_products(
    page_size: int = 100,
    offset: int = 0,
    is_archived: bool = False,
    name: Optional[str] = None,
    sort_property: str = "name",
    sort_direction: str = "ASC",
) -> dict
```

Returns `{total, products: [...]}`. Each product includes a `prices` list.

#### `create_product`

```python
def create_product(
    name: str,
    unit_price: float,
    description: Optional[str] = None,
    currency_id: str = "DKK",
) -> dict
```

#### `edit_product`

```python
def edit_product(
    product_id: str,
    name, description, product_no, suppliers_product_no: Optional[str] = None,
    price_id: Optional[str] = None,
    unit_price: Optional[float] = None,
) -> dict
```

To update the price, both `price_id` (from `list_products`) and `unit_price` must be provided.

---

### Email

#### `send_invoice_by_email`

```python
def send_invoice_by_email(
    invoice_id: str,
    contact_id: str,
    email_subject: str,
    email_body: str,
) -> dict
```

Looks up the customer's email from the `customers` table. Returns `{"success": True, ...}` or `{"success": False, "error": "..."}` if no email is on file. Does not actually send email.

---

### Invitations

#### `invite_user`

```python
def invite_user(email: str) -> dict
```

Generates a UUID invitation ID and stores the invitation in memory (not persisted to the database). Returns `{"success": True, "invitation_id": "...", "email": "...", "created_time": "..."}`.

---

### Support knowledge

#### `fetch_support_knowledge`

```python
async def fetch_support_knowledge(queries: list[str]) -> list[dict]
```

Runs each query in parallel against an AWS Bedrock Knowledge Base. Each result is a passage dict with `passage`, `score`, `url`, `title`, `text`, `query`. Results below a score threshold are filtered; duplicates are deduplicated.

In practice this tool requires real AWS credentials and a configured Bedrock KB. Without them it returns an empty list.

---

## REST API

All endpoints return the same dict as the underlying tool function. Error cases (e.g. ID not found) return HTTP 200 with `{"error": "..."}` — the tool layer does not raise HTTP exceptions.

### Customers

| Method | Path | Tool |
| --- | --- | --- |
| GET | `/customers` | `list_customers` |
| POST | `/customers` | `create_customer` |
| PATCH | `/customers/{contact_id}` | `edit_customer` |

`GET /customers` query params: `page`, `page_size`, `is_archived`, `name`, `sort_property`, `sort_direction`.

`POST /customers` body: `CreateCustomerBody` — same fields as `create_customer`.

`PATCH /customers/{id}` body: `EditCustomerBody` — all fields optional.

### Invoices

| Method | Path | Tool |
| --- | --- | --- |
| GET | `/invoices/summary` | `get_invoice_summary` |
| GET | `/invoices` | `list_invoices` |
| GET | `/invoices/{invoice_id}` | `get_invoice` |
| POST | `/invoices` | `create_invoice` |
| PATCH | `/invoices/{invoice_id}` | `edit_invoice` |
| POST | `/invoices/{invoice_id}/send` | `send_invoice_by_email` |

`/invoices/summary` is declared before `/{invoice_id}` to avoid route shadowing.

`GET /invoices` accepts `states` as a repeated query parameter: `?states=draft&states=approved`.

`POST /invoices` body: `CreateInvoiceBody` with a `lines` array of `InvoiceLine` objects.

`PATCH /invoices/{id}` body: `EditInvoiceBody` — all fields optional; `lines` is a list of `InvoiceLineUpdate`.

`POST /invoices/{id}/send` body: `SendEmailBody` — `contact_id`, `email_subject`, `email_body`.

### Products

| Method | Path | Tool |
| --- | --- | --- |
| GET | `/products` | `list_products` |
| POST | `/products` | `create_product` |
| PATCH | `/products/{product_id}` | `edit_product` |

### Other

| Method | Path | Tool |
| --- | --- | --- |
| POST | `/invitations` | `invite_user` |
| POST | `/support/search` | `fetch_support_knowledge` |

`POST /support/search` body: `{"queries": ["...", "..."]}`.

Interactive docs are available at `/docs` (Swagger UI) and `/redoc`.

---

## Configuration

| Variable | Default | Description |
| --- | --- | --- |
| `BILLY_DB` | `billy.db` | Path to the SQLite database file |
| `MCP_HOST` | `127.0.0.1` | Bind address for the MCP HTTP/SSE server |
| `MCP_PORT` | `8765` | Port for the MCP HTTP/SSE server |
| `MCP_BASE_URL` | `http://127.0.0.1:8765` | Base URL reported by the MCP server |
| `API_PORT` | `8766` | Port for the FastAPI REST server |

Variables are loaded from `.env` at startup via `python-dotenv`.

---

## Data Model

### Entities and ID formats

| Entity | ID format | Key fields |
| --- | --- | --- |
| Customer | `cus_NNN` | name, type (`company`/`person`), country, email, registration_no (CVR) |
| Contact person | `cp_NNN` | Linked 1:1 to a customer via `contact_person_id` |
| Invoice | `inv_NNN` | contact_id, state, lines, gross_amount, due_date |
| Invoice line | `line_INVOICEID_N` | product_id, quantity, unit_price, amount, tax |
| Product | `prod_NNN` | name, unit, prices list |
| Product price | `price_NNNa` | unit_price, currency |

### Invoice state machine

```text
draft ──► approved
```

Only `draft` invoices can be edited. `edit_invoice` with `state: "approved"` transitions the invoice and sets `approved_time`.

### Sent state

```text
unsent ──► sent
```

Set by `send_invoice_by_email`. Not enforced — any invoice ID is accepted.

### VAT

All prices are excl. VAT. Tax is always calculated as 25% (Danish standard rate). `gross_amount = amount + tax`.

---

## Out of Scope

- Authentication and multi-tenancy
- Real Billy API calls
- Real email delivery
- Real AWS Bedrock access (support knowledge returns empty without credentials)
- Payment registration
- Bank reconciliation
- Annual reports or VAT reports
