"""Invoice tools for the Billy accounting system."""

from datetime import date, datetime, timezone
from typing import Optional

# ---------------------------------------------------------------------------
# Mock data
# ---------------------------------------------------------------------------

_MOCK_INVOICES: list[dict] = [
    {
        "id": "inv_001",
        "invoiceNo": "2024-001",
        "contactId": "cus_001",
        "customerName": "Acme A/S",
        "entryDate": "2024-01-15",
        "dueDate": "2024-01-22",
        "state": "approved",
        "sentState": "sent",
        "amount": 10000.00,
        "tax": 2500.00,
        "grossAmount": 12500.00,
        "currency": "DKK",
        "exchangeRate": 1.0,
        "balance": 0.00,
        "isPaid": True,
        "paymentTerms": "net 7 days",
        "taxMode": "excl",
        "approvedTime": "2024-01-15T10:00:00Z",
        "createdTime": "2024-01-15T09:55:00Z",
        "downloadUrl": "https://app.billy.dk/invoices/inv_001/download",
        "contactMessage": None,
        "lineDescription": "Konsulentydelser januar",
        "lines": [
            {
                "id": "line_001a",
                "productId": "prod_001",
                "description": "Konsulentydelser",
                "quantity": 10,
                "unitPrice": 1000.00,
                "unit": "hours",
                "amount": 10000.00,
                "tax": 2500.00,
            }
        ],
    },
    {
        "id": "inv_002",
        "invoiceNo": "2024-002",
        "contactId": "cus_002",
        "customerName": "Nordisk Tech ApS",
        "entryDate": "2024-02-01",
        "dueDate": "2024-02-08",
        "state": "approved",
        "sentState": "sent",
        "amount": 5000.00,
        "tax": 1250.00,
        "grossAmount": 6250.00,
        "currency": "DKK",
        "exchangeRate": 1.0,
        "balance": 6250.00,
        "isPaid": False,
        "paymentTerms": "net 7 days",
        "taxMode": "excl",
        "approvedTime": "2024-02-01T09:00:00Z",
        "createdTime": "2024-02-01T08:50:00Z",
        "downloadUrl": "https://app.billy.dk/invoices/inv_002/download",
        "contactMessage": None,
        "lineDescription": "Softwarelicens februar",
        "lines": [
            {
                "id": "line_002a",
                "productId": "prod_002",
                "description": "Softwarelicens",
                "quantity": 1,
                "unitPrice": 5000.00,
                "unit": "pcs",
                "amount": 5000.00,
                "tax": 1250.00,
            }
        ],
    },
    {
        "id": "inv_003",
        "invoiceNo": "2024-003",
        "contactId": "cus_001",
        "customerName": "Acme A/S",
        "entryDate": "2024-03-01",
        "dueDate": "2024-03-08",
        "state": "draft",
        "sentState": "unsent",
        "amount": 3000.00,
        "tax": 750.00,
        "grossAmount": 3750.00,
        "currency": "DKK",
        "exchangeRate": 1.0,
        "balance": 3750.00,
        "isPaid": False,
        "paymentTerms": "net 7 days",
        "taxMode": "excl",
        "approvedTime": None,
        "createdTime": "2024-03-01T14:00:00Z",
        "downloadUrl": None,
        "contactMessage": None,
        "lineDescription": "Support marts",
        "lines": [
            {
                "id": "line_003a",
                "productId": "prod_001",
                "description": "Support",
                "quantity": 3,
                "unitPrice": 1000.00,
                "unit": "hours",
                "amount": 3000.00,
                "tax": 750.00,
            }
        ],
    },
]

_next_invoice_counter = 4


def _find_invoice(invoice_id: str) -> Optional[dict]:
    return next((i for i in _MOCK_INVOICES if i["id"] == invoice_id), None)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


def get_invoice(invoice_id: str) -> dict:
    """Gets detailed information about a single invoice by its ID.

    Returns full invoice details including amounts, dates, payment status,
    line items, and a PDF download URL.

    Args:
        invoice_id: The invoice ID to look up.

    Returns:
        Full invoice record with lines, or an error dict if not found.
    """
    invoice = _find_invoice(invoice_id)
    if not invoice:
        return {"error": f"Invoice '{invoice_id}' not found."}
    return dict(invoice)


def list_invoices(
    page: int = 1,
    page_size: int = 50,
    states: Optional[list] = None,
    min_entry_date: Optional[str] = None,
    max_entry_date: Optional[str] = None,
    contact_id: Optional[str] = None,
    currency_id: Optional[str] = None,
    sort_property: str = "entryDate",
    sort_direction: str = "DESC",
) -> dict:
    """Lists invoices from the accounting system.

    Supports filtering by state, date range, contact, and currency. Returns
    invoice details including amounts, dates, and payment status.

    Args:
        page: Page number (1-based). Defaults to 1.
        page_size: Items per page. Defaults to 50.
        states: Filter by invoice states, e.g. ['approved', 'draft'].
        min_entry_date: Minimum entry date filter (YYYY-MM-DD).
        max_entry_date: Maximum entry date filter (YYYY-MM-DD).
        contact_id: Filter by customer/contact ID.
        currency_id: Filter by currency code, e.g. 'DKK'.
        sort_property: Sort field — 'entryDate', 'invoiceNo', or 'grossAmount'. Defaults to 'entryDate'.
        sort_direction: Sort direction — 'ASC' or 'DESC'. Defaults to 'DESC'.

    Returns:
        Dict with total, page, pageCount, and a list of invoice records.
    """
    invoices = list(_MOCK_INVOICES)

    if states:
        invoices = [i for i in invoices if i["state"] in states]
    if min_entry_date:
        invoices = [i for i in invoices if i["entryDate"] >= min_entry_date]
    if max_entry_date:
        invoices = [i for i in invoices if i["entryDate"] <= max_entry_date]
    if contact_id:
        invoices = [i for i in invoices if i["contactId"] == contact_id]
    if currency_id:
        invoices = [i for i in invoices if i["currency"] == currency_id]

    reverse = sort_direction.upper() == "DESC"
    invoices.sort(key=lambda i: i.get(sort_property, ""), reverse=reverse)

    total = len(invoices)
    start = (page - 1) * page_size
    page_invoices = invoices[start : start + page_size]

    return {
        "total": total,
        "page": page,
        "pageCount": max(1, (total + page_size - 1) // page_size),
        "invoices": [
            {
                "id": i["id"],
                "invoiceNo": i["invoiceNo"],
                "customerName": i["customerName"],
                "entryDate": i["entryDate"],
                "dueDate": i["dueDate"],
                "state": i["state"],
                "amount": i["amount"],
                "tax": i["tax"],
                "grossAmount": i["grossAmount"],
                "currency": i["currency"],
                "balance": i["balance"],
                "isPaid": i["isPaid"],
                "lineDescription": i["lineDescription"],
            }
            for i in page_invoices
        ],
    }


def get_invoice_summary(fiscal_year: Optional[int] = None) -> dict:
    """Returns aggregate statistics about invoices.

    Returns total counts and amounts for all, draft, approved, overdue, unpaid,
    and paid invoices. Useful for dashboard or overview questions.

    Args:
        fiscal_year: Fiscal year to filter by, e.g. 2024. Defaults to current year.

    Returns:
        Dict with fiscalYear and aggregated invoice statistics.
    """
    year = fiscal_year or date.today().year
    year_str = str(year)

    relevant = [i for i in _MOCK_INVOICES if i["entryDate"].startswith(year_str)]
    today = date.today().isoformat()

    all_count = len(relevant)
    all_amount = sum(i["grossAmount"] for i in relevant)

    draft = [i for i in relevant if i["state"] == "draft"]
    approved = [i for i in relevant if i["state"] == "approved"]
    paid = [i for i in relevant if i["isPaid"]]
    unpaid = [i for i in relevant if not i["isPaid"] and i["state"] == "approved"]
    overdue = [i for i in unpaid if i["dueDate"] < today]

    return {
        "fiscalYear": year,
        "all": {"count": all_count, "amount": all_amount},
        "draft": {"count": len(draft), "amount": sum(i["grossAmount"] for i in draft)},
        "approved": {
            "count": len(approved),
            "amount": sum(i["grossAmount"] for i in approved),
        },
        "paid": {"count": len(paid), "amount": sum(i["grossAmount"] for i in paid)},
        "unpaid": {"count": len(unpaid), "amount": sum(i["balance"] for i in unpaid)},
        "overdue": {
            "count": len(overdue),
            "amount": sum(i["balance"] for i in overdue),
        },
    }


def edit_invoice(
    invoice_id: str,
    contact_id: Optional[str] = None,
    entry_date: Optional[str] = None,
    payment_terms_days: Optional[int] = None,
    state: Optional[str] = None,
    lines: Optional[list] = None,
) -> dict:
    """Updates an existing invoice. Only works on invoices in 'draft' state.

    Approved invoices cannot be edited. Can update the contact, entry date,
    payment terms, and line items. For line items, provide the line ID to update
    existing lines, or omit the ID to add a new line.

    Args:
        invoice_id: The ID of the invoice to update.
        contact_id: Updated customer/contact ID.
        entry_date: Updated invoice date (YYYY-MM-DD).
        payment_terms_days: Updated payment terms in days.
        state: Set state — 'approved' or 'draft'. Can approve a draft invoice.
        lines: Invoice line items to update or add. Each item may have:
               id (existing line), productId, description, quantity, unitPrice.

    Returns:
        The updated invoice record with lines, or an error dict.
    """
    invoice = _find_invoice(invoice_id)
    if not invoice:
        return {"error": f"Invoice '{invoice_id}' not found."}

    if invoice["state"] != "draft":
        return {
            "error": (
                f"Invoice {invoice_id} cannot be edited because it is in "
                f"'{invoice['state']}' state. Only draft invoices can be edited."
            )
        }

    if contact_id is not None:
        invoice["contactId"] = contact_id
    if entry_date is not None:
        invoice["entryDate"] = entry_date
    if payment_terms_days is not None:
        invoice["paymentTerms"] = f"net {payment_terms_days} days"
    if state is not None:
        invoice["state"] = state
        if state == "approved":
            invoice["approvedTime"] = datetime.now(timezone.utc).isoformat()

    if lines is not None:
        existing_by_id = {ln["id"]: ln for ln in invoice["lines"] if "id" in ln}
        new_lines = []
        for i, ln in enumerate(lines):
            line_id = ln.get("id")
            if line_id and line_id in existing_by_id:
                existing = existing_by_id[line_id]
                existing.update({k: v for k, v in ln.items() if v is not None})
                new_lines.append(existing)
            else:
                new_lines.append(
                    {
                        "id": f"line_{invoice_id}_{i}",
                        "productId": ln.get("productId", ""),
                        "description": ln.get("description", ""),
                        "quantity": ln.get("quantity", 1),
                        "unitPrice": ln.get("unitPrice", 0),
                        "amount": ln.get("quantity", 1) * ln.get("unitPrice", 0),
                        "tax": ln.get("quantity", 1) * ln.get("unitPrice", 0) * 0.25,
                    }
                )
        invoice["lines"] = new_lines

        invoice["amount"] = sum(ln["amount"] for ln in invoice["lines"])
        invoice["tax"] = sum(ln["tax"] for ln in invoice["lines"])
        invoice["grossAmount"] = invoice["amount"] + invoice["tax"]
        invoice["balance"] = invoice["grossAmount"] if not invoice["isPaid"] else 0.0

    return {
        "id": invoice["id"],
        "invoiceNo": invoice["invoiceNo"],
        "contactId": invoice["contactId"],
        "entryDate": invoice["entryDate"],
        "dueDate": invoice["dueDate"],
        "state": invoice["state"],
        "amount": invoice["amount"],
        "tax": invoice["tax"],
        "grossAmount": invoice["grossAmount"],
        "currency": invoice["currency"],
        "lineDescription": invoice["lineDescription"],
        "lines": [
            {
                "id": ln.get("id"),
                "productId": ln.get("productId"),
                "description": ln.get("description"),
                "quantity": ln.get("quantity"),
                "unitPrice": ln.get("unitPrice"),
                "amount": ln.get("amount"),
                "tax": ln.get("tax"),
            }
            for ln in invoice["lines"]
        ],
    }


def create_invoice(
    contact_id: str,
    lines: list,
    entry_date: Optional[str] = None,
    currency_id: str = "DKK",
    payment_terms_days: int = 7,
    state: str = "approved",
) -> dict:
    """Creates a new invoice in the accounting system.

    Requires a customer (contact) ID and at least one line item with product ID,
    quantity, and unit price. The invoice is created as approved by default.

    Args:
        contact_id: The customer/contact ID to bill.
        lines: Invoice line items. Each item requires productId, quantity, and
               unitPrice. description is optional.
        entry_date: Invoice date in YYYY-MM-DD format. Defaults to today.
        currency_id: Currency code, e.g. 'DKK'. Defaults to 'DKK'.
        payment_terms_days: Payment terms in days. Defaults to 7.
        state: Invoice state — 'approved' or 'draft'. Defaults to 'approved'.

    Returns:
        The newly created invoice record with lines.
    """
    global _next_invoice_counter
    inv_date = entry_date or date.today().isoformat()
    inv_id = f"inv_{_next_invoice_counter:03d}"
    inv_no = f"2026-{_next_invoice_counter:03d}"
    _next_invoice_counter += 1

    invoice_lines = []
    for i, ln in enumerate(lines):
        qty = ln.get("quantity", 1)
        price = ln.get("unitPrice", 0)
        amount = qty * price
        tax = amount * 0.25
        invoice_lines.append(
            {
                "id": f"line_{inv_id}_{i}",
                "productId": ln.get("productId", ""),
                "description": ln.get("description", ""),
                "quantity": qty,
                "unitPrice": price,
                "amount": amount,
                "tax": tax,
            }
        )

    total_amount = sum(ln["amount"] for ln in invoice_lines)
    total_tax = sum(ln["tax"] for ln in invoice_lines)
    gross = total_amount + total_tax

    from datetime import timedelta

    due = (
        date.fromisoformat(inv_date) + timedelta(days=payment_terms_days)
    ).isoformat()

    new_invoice = {
        "id": inv_id,
        "invoiceNo": inv_no,
        "contactId": contact_id,
        "customerName": contact_id,
        "entryDate": inv_date,
        "dueDate": due,
        "state": state,
        "sentState": "unsent",
        "amount": total_amount,
        "tax": total_tax,
        "grossAmount": gross,
        "currency": currency_id,
        "exchangeRate": 1.0,
        "balance": gross if state != "paid" else 0.0,
        "isPaid": False,
        "paymentTerms": f"net {payment_terms_days} days",
        "taxMode": "excl",
        "approvedTime": datetime.now(timezone.utc).isoformat()
        if state == "approved"
        else None,
        "createdTime": datetime.now(timezone.utc).isoformat(),
        "downloadUrl": f"https://app.billy.dk/invoices/{inv_id}/download"
        if state == "approved"
        else None,
        "contactMessage": None,
        "lineDescription": invoice_lines[0]["description"] if invoice_lines else "",
        "lines": invoice_lines,
    }
    _MOCK_INVOICES.append(new_invoice)

    return {
        "id": new_invoice["id"],
        "invoiceNo": new_invoice["invoiceNo"],
        "contactId": new_invoice["contactId"],
        "entryDate": new_invoice["entryDate"],
        "dueDate": new_invoice["dueDate"],
        "state": new_invoice["state"],
        "amount": new_invoice["amount"],
        "tax": new_invoice["tax"],
        "grossAmount": new_invoice["grossAmount"],
        "currency": new_invoice["currency"],
        "lineDescription": new_invoice["lineDescription"],
        "lines": [
            {
                "productId": ln["productId"],
                "description": ln["description"],
                "quantity": ln["quantity"],
                "unitPrice": ln["unitPrice"],
                "amount": ln["amount"],
                "tax": ln["tax"],
            }
            for ln in invoice_lines
        ],
    }
