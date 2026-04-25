"""Billy stub REST API — FastAPI entry point.

Run (from mcp_servers/billy):
    python -m app.main [--port PORT]

Interactive docs: http://127.0.0.1:8766/docs
Override port:    API_PORT=9000 python -m app.main
"""

import os
import sys
from typing import Annotated, Literal, Optional

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

from playground.agent_poc.mcp_servers.billy.app.config import Config
from playground.agent_poc.mcp_servers.billy.app.tools.customers import (
    create_customer,
    edit_customer,
    list_customers,
)
from playground.agent_poc.mcp_servers.billy.app.tools.emails import (
    send_invoice_by_email,
)
from playground.agent_poc.mcp_servers.billy.app.tools.invitations import invite_user
from playground.agent_poc.mcp_servers.billy.app.tools.invoices import (
    InvoiceLine,
    InvoiceLineUpdate,
    create_invoice,
    edit_invoice,
    get_invoice,
    get_invoice_lines_summary,
    get_invoice_summary,
    get_insight_aging_report,
    get_insight_customer_summary,
    get_insight_invoice_status,
    get_insight_monthly_revenue,
    get_insight_product_revenue,
    get_insight_revenue_summary,
    get_insight_top_customers,
    list_invoices,
)
from playground.agent_poc.mcp_servers.billy.app.tools.products import (
    create_product,
    edit_product,
    list_products,
)
from playground.agent_poc.mcp_servers.billy.app.tools.support_knowledge import (
    fetch_support_knowledge,
)

app = FastAPI(title="Billy Stub API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------


class CreateCustomerBody(BaseModel):
    name: str
    type: Literal["company", "person"] = "company"
    country_id: str = "DK"
    street: Optional[str] = None
    city_text: Optional[str] = None
    zipcode_text: Optional[str] = None
    phone: Optional[str] = None
    registration_no: Optional[str] = None
    invoicing_language: str = "en"
    email: Optional[str] = None


class EditCustomerBody(BaseModel):
    name: Optional[str] = None
    street: Optional[str] = None
    city_text: Optional[str] = None
    zipcode_text: Optional[str] = None
    phone: Optional[str] = None
    country_id: Optional[str] = None
    registration_no: Optional[str] = None
    invoicing_language: Optional[str] = None
    contact_person_id: Optional[str] = None
    email: Optional[str] = None


@app.get("/customers")
def customers_list(
    page: int = 1,
    page_size: int = 50,
    is_archived: bool = False,
    name: Optional[str] = None,
    sort_property: str = "name",
    sort_direction: str = "ASC",
):
    return list_customers(
        page, page_size, is_archived, name, sort_property, sort_direction
    )


@app.post("/customers", status_code=201)
def customers_create(body: CreateCustomerBody):
    return create_customer(**body.model_dump())


@app.patch("/customers/{contact_id}")
def customers_edit(contact_id: str, body: EditCustomerBody):
    return edit_customer(contact_id, **body.model_dump())


# ---------------------------------------------------------------------------
# Invoices
# ---------------------------------------------------------------------------


class CreateInvoiceBody(BaseModel):
    contact_id: str
    lines: list[InvoiceLine]
    entry_date: Optional[str] = None
    currency_id: str = "DKK"
    payment_terms_days: int = 7
    state: str = "approved"


class EditInvoiceBody(BaseModel):
    contact_id: Optional[str] = None
    entry_date: Optional[str] = None
    payment_terms_days: Optional[int] = None
    state: Optional[str] = None
    lines: Optional[list[InvoiceLineUpdate]] = None


class SendEmailBody(BaseModel):
    contact_id: str
    email_subject: str
    email_body: str


# /invoices/summary and /invoices/lines/summary must be declared before /invoices/{invoice_id}
@app.get("/invoices/summary")
def invoices_summary(fiscal_year: Optional[int] = None):
    return get_invoice_summary(fiscal_year)


@app.get("/invoices/lines/summary")
def invoices_lines_summary(fiscal_year: Optional[int] = None):
    return get_invoice_lines_summary(fiscal_year)


# ---------------------------------------------------------------------------
# Insights — pre-aggregated data for frontend insight panels
# ---------------------------------------------------------------------------


@app.get("/insights/revenue-summary")
def insights_revenue_summary(
    fiscal_year: Optional[int] = None, month: Optional[int] = None
):
    return get_insight_revenue_summary(fiscal_year, month)


@app.get("/insights/invoice-status")
def insights_invoice_status(fiscal_year: Optional[int] = None):
    return get_insight_invoice_status(fiscal_year)


@app.get("/insights/monthly-revenue")
def insights_monthly_revenue(fiscal_year: Optional[int] = None):
    return get_insight_monthly_revenue(fiscal_year)


@app.get("/insights/top-customers")
def insights_top_customers(fiscal_year: Optional[int] = None, limit: int = 10):
    return get_insight_top_customers(fiscal_year, limit)


@app.get("/insights/aging-report")
def insights_aging_report(
    contact_id: Optional[str] = None,
    contact_name: Optional[str] = None,
):
    return get_insight_aging_report(contact_id, contact_name)


@app.get("/insights/customer-summary")
def insights_customer_summary(
    contact_id: Optional[str] = None,
    contact_name: Optional[str] = None,
    fiscal_year: Optional[int] = None,
):
    return get_insight_customer_summary(contact_id, contact_name, fiscal_year)


@app.get("/insights/product-revenue")
def insights_product_revenue(fiscal_year: Optional[int] = None):
    return get_insight_product_revenue(fiscal_year)


@app.get("/invoices")
def invoices_list(
    page: int = 1,
    page_size: int = 50,
    states: Annotated[Optional[list[str]], Query()] = None,
    min_entry_date: Optional[str] = None,
    max_entry_date: Optional[str] = None,
    contact_id: Optional[str] = None,
    currency_id: Optional[str] = None,
    sort_property: str = "entry_date",
    sort_direction: str = "DESC",
):
    return list_invoices(
        page,
        page_size,
        states,
        min_entry_date,
        max_entry_date,
        contact_id,
        currency_id,
        sort_property,
        sort_direction,
    )


@app.get("/invoices/{invoice_id}")
def invoices_get(invoice_id: str):
    return get_invoice(invoice_id)


@app.post("/invoices", status_code=201)
def invoices_create(body: CreateInvoiceBody):
    return create_invoice(
        contact_id=body.contact_id,
        lines=body.lines,
        entry_date=body.entry_date,
        currency_id=body.currency_id,
        payment_terms_days=body.payment_terms_days,
        state=body.state,
    )


@app.patch("/invoices/{invoice_id}")
def invoices_edit(invoice_id: str, body: EditInvoiceBody):
    return edit_invoice(
        invoice_id,
        contact_id=body.contact_id,
        entry_date=body.entry_date,
        payment_terms_days=body.payment_terms_days,
        state=body.state,
        lines=body.lines,
    )


@app.post("/invoices/{invoice_id}/send")
def invoices_send_email(invoice_id: str, body: SendEmailBody):
    return send_invoice_by_email(
        invoice_id, body.contact_id, body.email_subject, body.email_body
    )


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------


class CreateProductBody(BaseModel):
    name: str
    unit_price: float
    description: Optional[str] = None
    currency_id: str = "DKK"


class EditProductBody(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    product_no: Optional[str] = None
    suppliers_product_no: Optional[str] = None
    price_id: Optional[str] = None
    unit_price: Optional[float] = None


@app.get("/products")
def products_list(
    page_size: int = 100,
    offset: int = 0,
    is_archived: bool = False,
    name: Optional[str] = None,
    sort_property: str = "name",
    sort_direction: str = "ASC",
):
    return list_products(
        page_size, offset, is_archived, name, sort_property, sort_direction
    )


@app.post("/products", status_code=201)
def products_create(body: CreateProductBody):
    return create_product(**body.model_dump())


@app.patch("/products/{product_id}")
def products_edit(product_id: str, body: EditProductBody):
    return edit_product(product_id, **body.model_dump())


# ---------------------------------------------------------------------------
# Invitations
# ---------------------------------------------------------------------------


class InviteUserBody(BaseModel):
    email: str


@app.post("/invitations", status_code=201)
def invitations_create(body: InviteUserBody):
    return invite_user(body.email)


# ---------------------------------------------------------------------------
# Support knowledge
# ---------------------------------------------------------------------------


class SupportSearchBody(BaseModel):
    queries: list[str]


@app.post("/support/search")
async def support_search(body: SupportSearchBody):
    return await fetch_support_knowledge(body.queries)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.getenv("API_PORT", "8766"))
    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])
    print(f"Billy REST API listening on http://{Config.HOST}:{port}/docs")
    uvicorn.run(app, host=Config.HOST, port=port)
