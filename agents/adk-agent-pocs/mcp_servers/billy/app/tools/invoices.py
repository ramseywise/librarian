"""Invoice stub tools for the Billy MCP server."""

from datetime import date, datetime, timedelta, timezone
from typing import Optional

from pydantic import BaseModel

from playground.agent_poc.mcp_servers.billy.app.db import get_conn, next_id


class InvoiceLine(BaseModel):
    product_id: str
    quantity: float = 1
    unit_price: float
    description: Optional[str] = None


class InvoiceLineUpdate(BaseModel):
    product_id: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    description: Optional[str] = None
    id: Optional[str] = None  # existing line ID to update; omit to add a new line


# Valid sort columns – whitelisted to prevent SQL injection.
_SORT_COLS = {"entry_date", "invoice_no", "gross_amount"}


def _fetch_lines(conn, invoice_id: str) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM invoice_lines WHERE invoice_id = ? ORDER BY rowid",
        (invoice_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def get_invoice(invoice_id: str) -> dict:
    """Gets detailed information about a single invoice by its ID.

    Returns full invoice details including amounts, dates, payment status,
    line items, and a PDF download URL.

    Args:
        invoice_id: The invoice ID to look up.

    Returns:
        Full invoice record with lines, or an error dict if not found.
    """
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM invoices WHERE id = ?", (invoice_id,)
        ).fetchone()
        if not row:
            return {"error": f"Invoice '{invoice_id}' not found."}
        invoice = dict(row)
        invoice["is_paid"] = bool(invoice["is_paid"])
        invoice["lines"] = _fetch_lines(conn, invoice_id)
    return invoice


def list_invoices(
    page: int = 1,
    page_size: int = 50,
    states: Optional[list[str]] = None,
    min_entry_date: Optional[str] = None,
    max_entry_date: Optional[str] = None,
    contact_id: Optional[str] = None,
    currency_id: Optional[str] = None,
    sort_property: str = "entry_date",
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
        sort_property: Sort field — 'entry_date', 'invoice_no', or 'gross_amount'. Defaults to 'entry_date'.
        sort_direction: Sort direction — 'ASC' or 'DESC'. Defaults to 'DESC'.

    Returns:
        Dict with total, page, page_count, and a list of invoice records.
    """
    col = sort_property if sort_property in _SORT_COLS else "entry_date"
    direction = "DESC" if sort_direction.upper() == "DESC" else "ASC"

    conditions: list[str] = []
    params: list = []

    if states:
        placeholders = ",".join("?" * len(states))
        conditions.append(f"state IN ({placeholders})")
        params.extend(states)
    if min_entry_date:
        conditions.append("entry_date >= ?")
        params.append(min_entry_date)
    if max_entry_date:
        conditions.append("entry_date <= ?")
        params.append(max_entry_date)
    if contact_id:
        conditions.append("contact_id = ?")
        params.append(contact_id)
    if currency_id:
        conditions.append("currency = ?")
        params.append(currency_id)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    with get_conn() as conn:
        total = conn.execute(
            f"SELECT COUNT(*) FROM invoices {where}", params
        ).fetchone()[0]
        offset = (page - 1) * page_size
        rows = conn.execute(
            f"SELECT * FROM invoices {where} ORDER BY {col} {direction} LIMIT ? OFFSET ?",
            params + [page_size, offset],
        ).fetchall()

    invoices = []
    for r in rows:
        i = dict(r)
        invoices.append(
            {
                "id": i["id"],
                "invoice_no": i["invoice_no"],
                "customer_name": i["customer_name"],
                "entry_date": i["entry_date"],
                "due_date": i["due_date"],
                "state": i["state"],
                "amount": i["amount"],
                "tax": i["tax"],
                "gross_amount": i["gross_amount"],
                "currency": i["currency"],
                "balance": i["balance"],
                "is_paid": bool(i["is_paid"]),
                "line_description": i["line_description"],
            }
        )

    return {
        "total": total,
        "page": page,
        "page_count": max(1, (total + page_size - 1) // page_size),
        "invoices": invoices,
    }


def get_invoice_summary(
    fiscal_year: Optional[int] = None, month: Optional[int] = None
) -> dict:
    """Returns aggregate statistics about invoices.

    Returns total counts and amounts for all, draft, approved, overdue, unpaid,
    and paid invoices. Useful for dashboard or overview questions.

    Args:
        fiscal_year: Fiscal year to filter by, e.g. 2024. Defaults to current year.
        month: Optional month (1–12) to further narrow the period.

    Returns:
        Dict with fiscal_year and aggregated invoice statistics.
    """
    year = fiscal_year or date.today().year
    today = date.today().isoformat()

    if month is not None:
        date_pattern = f"{year}-{month:02d}-%"
    else:
        date_pattern = f"{year}-%"

    with get_conn() as conn:

        def _agg(extra_where: str, extra_params: list) -> dict:
            base = "FROM invoices WHERE entry_date LIKE ?"
            row = conn.execute(
                f"SELECT COUNT(*), COALESCE(SUM(gross_amount),0) {base} {extra_where}",
                [date_pattern] + extra_params,
            ).fetchone()
            return {"count": row[0], "amount": row[1]}

        def _agg_balance(extra_where: str, extra_params: list) -> dict:
            base = "FROM invoices WHERE entry_date LIKE ?"
            row = conn.execute(
                f"SELECT COUNT(*), COALESCE(SUM(balance),0) {base} {extra_where}",
                [date_pattern] + extra_params,
            ).fetchone()
            return {"count": row[0], "amount": row[1]}

        return {
            "fiscal_year": year,
            "all": _agg("", []),
            "draft": _agg("AND state = ?", ["draft"]),
            "approved": _agg("AND state = ?", ["approved"]),
            "paid": _agg("AND is_paid = 1", []),
            "unpaid": _agg_balance("AND is_paid = 0 AND state = 'approved'", []),
            "overdue": _agg_balance(
                "AND is_paid = 0 AND state = 'approved' AND due_date < ?", [today]
            ),
        }


def get_invoice_lines_summary(fiscal_year: Optional[int] = None) -> dict:
    """Returns aggregated revenue per product across all invoices.

    Joins invoice lines with products and invoices to sum quantity and revenue
    per product. Useful for product performance / best-seller analysis.

    Args:
        fiscal_year: Fiscal year to filter by, e.g. 2024. Defaults to current year.

    Returns:
        Dict with fiscal_year and a list of products with total_qty and total_revenue.
    """
    year = fiscal_year or date.today().year
    year_prefix = f"{year}-%"

    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT
                il.product_id,
                COALESCE(p.name, il.product_id) AS product_name,
                COALESCE(SUM(il.quantity), 0)   AS total_qty,
                COALESCE(SUM(il.amount), 0)     AS total_revenue
            FROM invoice_lines il
            JOIN invoices i ON i.id = il.invoice_id
            LEFT JOIN products p ON p.id = il.product_id
            WHERE i.entry_date LIKE ?
            GROUP BY il.product_id
            ORDER BY total_revenue DESC
            """,
            (year_prefix,),
        ).fetchall()

    return {
        "fiscal_year": year,
        "products": [
            {
                "product_id": r["product_id"],
                "product_name": r["product_name"],
                "total_qty": r["total_qty"],
                "total_revenue": r["total_revenue"],
            }
            for r in rows
        ],
    }


def edit_invoice(
    invoice_id: str,
    contact_id: Optional[str] = None,
    entry_date: Optional[str] = None,
    payment_terms_days: Optional[int] = None,
    state: Optional[str] = None,
    lines: Optional[list[InvoiceLineUpdate]] = None,
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
        lines: Invoice line items to update or add.

    Returns:
        The updated invoice record with lines, or an error dict.
    """
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM invoices WHERE id = ?", (invoice_id,)
        ).fetchone()
        if not row:
            return {"error": f"Invoice '{invoice_id}' not found."}

        invoice = dict(row)
        if invoice["state"] != "draft":
            return {
                "error": (
                    f"Invoice {invoice_id} cannot be edited because it is in "
                    f"'{invoice['state']}' state. Only draft invoices can be edited."
                )
            }

        # Build scalar field updates.
        updates: list[str] = []
        uparams: list = []
        if contact_id is not None:
            updates.append("contact_id = ?")
            uparams.append(contact_id)
        if entry_date is not None:
            updates.append("entry_date = ?")
            uparams.append(entry_date)
        if payment_terms_days is not None:
            updates.append("payment_terms = ?")
            uparams.append(f"net {payment_terms_days} days")
        if state is not None:
            updates.append("state = ?")
            uparams.append(state)
            if state == "approved":
                updates.append("approved_time = ?")
                uparams.append(datetime.now(timezone.utc).isoformat())

        if updates:
            conn.execute(
                f"UPDATE invoices SET {', '.join(updates)} WHERE id = ?",
                uparams + [invoice_id],
            )

        # Process line updates.
        if lines is not None:
            existing = {r["id"]: dict(r) for r in _fetch_lines(conn, invoice_id)}  # type: ignore[index]
            new_lines: list[dict] = []
            for i, ln in enumerate(lines):
                if ln.id and ln.id in existing:
                    ex = existing[ln.id]
                    if ln.product_id is not None:
                        ex["product_id"] = ln.product_id
                    if ln.quantity is not None:
                        ex["quantity"] = ln.quantity
                    if ln.unit_price is not None:
                        ex["unit_price"] = ln.unit_price
                    if ln.description is not None:
                        ex["description"] = ln.description
                    ex["amount"] = ex["quantity"] * ex["unit_price"]
                    ex["tax"] = ex["amount"] * 0.25
                    new_lines.append(ex)
                else:
                    qty = ln.quantity if ln.quantity is not None else 1.0
                    price = ln.unit_price if ln.unit_price is not None else 0.0
                    new_lines.append(
                        {
                            "id": f"line_{invoice_id}_{i}",
                            "invoice_id": invoice_id,
                            "product_id": ln.product_id or "",
                            "description": ln.description or "",
                            "quantity": qty,
                            "unit_price": price,
                            "unit": "pcs",
                            "amount": qty * price,
                            "tax": qty * price * 0.25,
                        }
                    )

            conn.execute(
                "DELETE FROM invoice_lines WHERE invoice_id = ?", (invoice_id,)
            )
            for nl in new_lines:
                conn.execute(
                    """INSERT INTO invoice_lines
                       (id, invoice_id, product_id, description, quantity,
                        unit_price, unit, amount, tax)
                       VALUES (?,?,?,?,?,?,?,?,?)""",
                    (
                        nl["id"],
                        nl["invoice_id"],
                        nl["product_id"],
                        nl["description"],
                        nl["quantity"],
                        nl["unit_price"],
                        nl["unit"],
                        nl["amount"],
                        nl["tax"],
                    ),
                )

            total_amount = sum(nl["amount"] for nl in new_lines)
            total_tax = sum(nl["tax"] for nl in new_lines)
            gross = total_amount + total_tax
            conn.execute(
                """UPDATE invoices SET amount=?, tax=?, gross_amount=?, balance=?
                   WHERE id=?""",
                (
                    total_amount,
                    total_tax,
                    gross,
                    gross if not invoice["is_paid"] else 0.0,
                    invoice_id,
                ),
            )

        # Re-fetch final state.
        updated = dict(
            conn.execute(
                "SELECT * FROM invoices WHERE id = ?", (invoice_id,)
            ).fetchone()
        )
        final_lines = _fetch_lines(conn, invoice_id)

    return {
        "id": updated["id"],
        "invoice_no": updated["invoice_no"],
        "contact_id": updated["contact_id"],
        "entry_date": updated["entry_date"],
        "due_date": updated["due_date"],
        "state": updated["state"],
        "amount": updated["amount"],
        "tax": updated["tax"],
        "gross_amount": updated["gross_amount"],
        "currency": updated["currency"],
        "line_description": updated["line_description"],
        "lines": [
            {
                "id": ln["id"],
                "product_id": ln["product_id"],
                "description": ln["description"],
                "quantity": ln["quantity"],
                "unit_price": ln["unit_price"],
                "amount": ln["amount"],
                "tax": ln["tax"],
            }
            for ln in final_lines
        ],
    }


def create_invoice(
    contact_id: str,
    lines: list[InvoiceLine],
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
        lines: Invoice line items.
        entry_date: Invoice date in YYYY-MM-DD format. Defaults to today.
        currency_id: Currency code, e.g. 'DKK'. Defaults to 'DKK'.
        payment_terms_days: Payment terms in days. Defaults to 7.
        state: Invoice state — 'approved' or 'draft'. Defaults to 'approved'.

    Returns:
        The newly created invoice record with lines.
    """
    inv_date = entry_date or date.today().isoformat()
    due = (
        date.fromisoformat(inv_date) + timedelta(days=payment_terms_days)
    ).isoformat()
    now = datetime.now(timezone.utc).isoformat()

    invoice_lines: list[dict] = []
    for i, ln in enumerate(lines):
        amount = ln.quantity * ln.unit_price
        invoice_lines.append(
            {
                "product_id": ln.product_id,
                "description": ln.description or "",
                "quantity": ln.quantity,
                "unit_price": ln.unit_price,
                "unit": "pcs",
                "amount": amount,
                "tax": amount * 0.25,
            }
        )

    total_amount = sum(ln["amount"] for ln in invoice_lines)
    total_tax = sum(ln["tax"] for ln in invoice_lines)
    gross = total_amount + total_tax

    with get_conn() as conn:
        n = next_id(conn, "invoice")
        inv_id = f"inv_{n:03d}"
        inv_no = f"2026-{n:03d}"

        row = conn.execute(
            "SELECT name FROM customers WHERE id = ?", (contact_id,)
        ).fetchone()
        customer_name = row["name"] if row else contact_id

        conn.execute(
            """INSERT INTO invoices
               (id, invoice_no, contact_id, customer_name, entry_date, due_date,
                state, sent_state, amount, tax, gross_amount, currency, exchange_rate,
                balance, is_paid, payment_terms, tax_mode, approved_time, created_time,
                download_url, contact_message, line_description)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                inv_id,
                inv_no,
                contact_id,
                customer_name,
                inv_date,
                due,
                state,
                "unsent",
                total_amount,
                total_tax,
                gross,
                currency_id,
                1.0,
                gross if state != "paid" else 0.0,
                0,
                f"net {payment_terms_days} days",
                "excl",
                now if state == "approved" else None,
                now,
                f"https://app.billy.dk/invoices/{inv_id}/download"
                if state == "approved"
                else None,
                None,
                invoice_lines[0]["description"] if invoice_lines else "",
            ),
        )

        for i, ln in enumerate(invoice_lines):
            conn.execute(
                """INSERT INTO invoice_lines
                   (id, invoice_id, product_id, description, quantity,
                    unit_price, unit, amount, tax)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (
                    f"line_{inv_id}_{i}",
                    inv_id,
                    ln["product_id"],
                    ln["description"],
                    ln["quantity"],
                    ln["unit_price"],
                    ln["unit"],
                    ln["amount"],
                    ln["tax"],
                ),
            )

    return {
        "id": inv_id,
        "invoice_no": inv_no,
        "contact_id": contact_id,
        "entry_date": inv_date,
        "due_date": due,
        "state": state,
        "amount": total_amount,
        "tax": total_tax,
        "gross_amount": gross,
        "currency": currency_id,
        "line_description": invoice_lines[0]["description"] if invoice_lines else "",
        "lines": invoice_lines,
    }


# ---------------------------------------------------------------------------
# Insight REST helpers — pre-aggregated data for frontend insight components
# ---------------------------------------------------------------------------

_MONTH_LABELS = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]


def get_insight_revenue_summary(
    fiscal_year: Optional[int] = None, month: Optional[int] = None
) -> dict:
    """Revenue KPI cards: total invoiced, collected, outstanding, overdue with YoY delta.

    When `month` is provided (1–12), filters to that calendar month within the year.
    YoY delta compares to the same month in the prior year.
    """
    year = fiscal_year or date.today().year
    cur = get_invoice_summary(year, month)
    prior = get_invoice_summary(year - 1, month)

    def _delta(cur_amt: float, prior_amt: float) -> Optional[float]:
        if prior_amt == 0:
            return None
        return round((cur_amt - prior_amt) / prior_amt * 100, 1)

    result: dict = {
        "fiscalYear": year,
        "currency": "DKK",
        "cards": [
            {
                "label": "Total invoiced",
                "amount": cur["all"]["amount"],
                "delta": _delta(cur["all"]["amount"], prior["all"]["amount"]),
            },
            {
                "label": "Collected",
                "amount": cur["paid"]["amount"],
                "delta": _delta(cur["paid"]["amount"], prior["paid"]["amount"]),
            },
            {"label": "Outstanding", "amount": cur["unpaid"]["amount"], "delta": None},
            {"label": "Overdue", "amount": cur["overdue"]["amount"], "delta": None},
        ],
    }
    if month is not None:
        result["month"] = month
    return result


def get_insight_invoice_status(fiscal_year: Optional[int] = None) -> dict:
    """Invoice status breakdown: draft, unpaid, paid, overdue counts and amounts."""
    year = fiscal_year or date.today().year
    s = get_invoice_summary(year)
    return {
        "fiscalYear": year,
        "currency": "DKK",
        "segments": [
            {
                "label": "Draft",
                "count": s["draft"]["count"],
                "amount": s["draft"]["amount"],
            },
            {
                "label": "Approved & unpaid",
                "count": s["unpaid"]["count"],
                "amount": s["unpaid"]["amount"],
            },
            {
                "label": "Paid",
                "count": s["paid"]["count"],
                "amount": s["paid"]["amount"],
            },
            {
                "label": "Overdue",
                "count": s["overdue"]["count"],
                "amount": s["overdue"]["amount"],
            },
        ],
    }


def get_insight_monthly_revenue(fiscal_year: Optional[int] = None) -> dict:
    """Monthly invoiced vs paid amounts for the given fiscal year."""
    year = fiscal_year or date.today().year
    year_prefix = f"{year}-%"

    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT strftime('%m', entry_date) AS month_no,
                   COALESCE(SUM(amount), 0)                        AS invoiced,
                   COALESCE(SUM(CASE WHEN is_paid=1 THEN amount ELSE 0 END), 0) AS paid
            FROM invoices
            WHERE entry_date LIKE ?
            GROUP BY month_no
            ORDER BY month_no
            """,
            (year_prefix,),
        ).fetchall()

    by_month: dict[int, dict] = {
        i + 1: {"invoiced": 0.0, "paid": 0.0} for i in range(12)
    }
    for r in rows:
        m = int(r["month_no"])
        by_month[m] = {"invoiced": round(r["invoiced"], 2), "paid": round(r["paid"], 2)}

    return {
        "fiscalYear": year,
        "currency": "DKK",
        "months": [
            {
                "month": _MONTH_LABELS[i],
                "invoiced": by_month[i + 1]["invoiced"],
                "paid": by_month[i + 1]["paid"],
            }
            for i in range(12)
        ],
    }


def get_insight_top_customers(
    fiscal_year: Optional[int] = None, limit: int = 10
) -> dict:
    """Top customers ranked by total invoiced amount."""
    year = fiscal_year or date.today().year
    year_prefix = f"{year}-%"

    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT contact_id,
                   customer_name,
                   COALESCE(SUM(amount), 0)                                  AS invoiced,
                   COALESCE(SUM(CASE WHEN is_paid=1 THEN amount ELSE 0 END), 0) AS paid
            FROM invoices
            WHERE entry_date LIKE ?
            GROUP BY contact_id
            ORDER BY invoiced DESC
            LIMIT ?
            """,
            (year_prefix, limit),
        ).fetchall()

    result = []
    for i, r in enumerate(rows):
        outstanding = round(r["invoiced"] - r["paid"], 2)
        result.append(
            {
                "rank": i + 1,
                "name": r["customer_name"],
                "invoiced": round(r["invoiced"], 2),
                "paid": round(r["paid"], 2),
                "outstanding": outstanding,
            }
        )

    return {"currency": "DKK", "rows": result}


def get_insight_aging_report(
    contact_id: Optional[str] = None, contact_name: Optional[str] = None
) -> dict:
    """Unpaid approved invoices bucketed by days overdue.

    Optionally filtered to a single customer via contact_id or a partial
    contact_name match.
    """
    today_dt = date.today()
    today_str = today_dt.isoformat()

    with get_conn() as conn:
        # Resolve name → id if needed
        if contact_name and not contact_id:
            r = conn.execute(
                "SELECT id FROM customers WHERE name LIKE ? LIMIT 1",
                (f"%{contact_name}%",),
            ).fetchone()
            if r:
                contact_id = r["id"]

        if contact_id:
            rows = conn.execute(
                """
                SELECT id, invoice_no, customer_name, due_date, balance AS amount
                FROM invoices
                WHERE state = 'approved' AND is_paid = 0 AND contact_id = ?
                ORDER BY due_date ASC
                """,
                (contact_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT id, invoice_no, customer_name, due_date, balance AS amount
                FROM invoices
                WHERE state = 'approved' AND is_paid = 0
                ORDER BY due_date ASC
                """,
            ).fetchall()

    bucket_order = ["Current", "1–30 days", "31–60 days", "61–90 days", "90+ days"]
    buckets: dict[str, list] = {k: [] for k in bucket_order}

    for r in rows:
        due = r["due_date"] or today_str
        try:
            days_over = (today_dt - date.fromisoformat(due)).days
        except ValueError:
            days_over = 0
        days_over = max(0, days_over)

        if days_over == 0:
            bucket = "Current"
        elif days_over <= 30:
            bucket = "1–30 days"
        elif days_over <= 60:
            bucket = "31–60 days"
        elif days_over <= 90:
            bucket = "61–90 days"
        else:
            bucket = "90+ days"

        buckets[bucket].append(
            {
                "invoiceNo": r["invoice_no"],
                "customer": r["customer_name"],
                "dueDate": r["due_date"] or "",
                "amount": round(r["amount"], 2),
                "daysOverdue": days_over,
            }
        )

    result_buckets = [
        {
            "label": label,
            "totalAmount": round(sum(inv["amount"] for inv in invs), 2),
            "invoices": invs,
        }
        for label, invs in buckets.items()
        if invs
    ]

    return {"currency": "DKK", "asOf": today_str, "buckets": result_buckets}


def get_insight_customer_summary(
    contact_id: Optional[str] = None,
    contact_name: Optional[str] = None,
    fiscal_year: Optional[int] = None,
) -> dict:
    """KPI summary for a single customer: invoiced, collected, outstanding, overdue,
    plus their most recent open invoices.

    Identify the customer via contact_id (exact) or contact_name (partial match).
    """
    year = fiscal_year or date.today().year
    year_prefix = f"{year}-%"
    today_str = date.today().isoformat()

    with get_conn() as conn:
        # Resolve name → id if needed
        if contact_name and not contact_id:
            r = conn.execute(
                "SELECT id FROM customers WHERE name LIKE ? LIMIT 1",
                (f"%{contact_name}%",),
            ).fetchone()
            if r:
                contact_id = r["id"]

        if not contact_id:
            return {"error": "Customer not found"}

        cust = conn.execute(
            "SELECT name FROM customers WHERE id = ?", (contact_id,)
        ).fetchone()
        customer_name_val = cust["name"] if cust else contact_id

        agg = conn.execute(
            """
            SELECT
                COALESCE(SUM(amount), 0)                                                   AS invoiced,
                COALESCE(SUM(CASE WHEN is_paid = 1 THEN amount ELSE 0 END), 0)             AS paid,
                COALESCE(SUM(CASE WHEN is_paid = 0 AND state = 'approved'
                                  THEN balance ELSE 0 END), 0)                             AS outstanding,
                COALESCE(SUM(CASE WHEN is_paid = 0 AND state = 'approved'
                                  AND due_date < ? THEN balance ELSE 0 END), 0)            AS overdue,
                COUNT(*)                                                                    AS invoice_count,
                MAX(entry_date)                                                             AS last_invoice_date
            FROM invoices
            WHERE contact_id = ? AND entry_date LIKE ?
            """,
            (today_str, contact_id, year_prefix),
        ).fetchone()

        open_rows = conn.execute(
            """
            SELECT invoice_no, entry_date, due_date, amount, balance
            FROM invoices
            WHERE contact_id = ? AND is_paid = 0 AND state = 'approved'
            ORDER BY entry_date DESC
            LIMIT 5
            """,
            (contact_id,),
        ).fetchall()

    return {
        "currency": "DKK",
        "fiscalYear": year,
        "contactId": contact_id,
        "customerName": customer_name_val,
        "invoiced": round(agg["invoiced"], 2),
        "paid": round(agg["paid"], 2),
        "outstanding": round(agg["outstanding"], 2),
        "overdue": round(agg["overdue"], 2),
        "invoiceCount": agg["invoice_count"],
        "lastInvoiceDate": agg["last_invoice_date"] or "",
        "openInvoices": [
            {
                "invoiceNo": r["invoice_no"],
                "date": r["entry_date"],
                "dueDate": r["due_date"] or "",
                "amount": round(r["amount"], 2),
                "balance": round(r["balance"], 2),
            }
            for r in open_rows
        ],
    }


def get_insight_product_revenue(fiscal_year: Optional[int] = None) -> dict:
    """Products ranked by total revenue generated."""
    data = get_invoice_lines_summary(fiscal_year)
    rows = [
        {
            "rank": i + 1,
            "name": p["product_name"],
            "quantitySold": round(p["total_qty"], 2),
            "revenue": round(p["total_revenue"], 2),
        }
        for i, p in enumerate(data["products"])
    ]
    return {"currency": "DKK", "rows": rows}
