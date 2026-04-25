"""Unit tests for invoice tools."""

from playground.agent_poc.mcp_servers.billy.app.tools import invoices as mod
from playground.agent_poc.mcp_servers.billy.app.tools.invoices import (
    InvoiceLine,
    InvoiceLineUpdate,
)


class TestGetInvoice:
    def test_returns_invoice(self):
        result = mod.get_invoice("inv_001")
        assert result["id"] == "inv_001"
        assert "lines" in result

    def test_not_found_returns_error(self):
        result = mod.get_invoice("inv_999")
        assert "error" in result


class TestListInvoices:
    def test_returns_all(self):
        result = mod.list_invoices()
        assert result["total"] == 3

    def test_filter_by_state(self):
        result = mod.list_invoices(states=["draft"])
        assert result["total"] == 1
        assert result["invoices"][0]["state"] == "draft"

    def test_filter_by_contact(self):
        result = mod.list_invoices(contact_id="cus_001")
        assert result["total"] == 2

    def test_filter_by_date_range(self):
        result = mod.list_invoices(
            min_entry_date="2024-02-01", max_entry_date="2024-02-28"
        )
        assert result["total"] == 1
        assert result["invoices"][0]["id"] == "inv_002"

    def test_pagination(self):
        result = mod.list_invoices(page=1, page_size=2)
        assert len(result["invoices"]) == 2
        assert result["page_count"] == 2


class TestGetInvoiceSummary:
    def test_returns_fiscal_year(self):
        result = mod.get_invoice_summary(fiscal_year=2024)
        assert result["fiscal_year"] == 2024

    def test_counts_correct(self):
        result = mod.get_invoice_summary(fiscal_year=2024)
        assert result["all"]["count"] == 3
        assert result["draft"]["count"] == 1
        assert result["paid"]["count"] == 1

    def test_empty_year_returns_zeros(self):
        result = mod.get_invoice_summary(fiscal_year=1900)
        assert result["all"]["count"] == 0


class TestEditInvoice:
    def test_edit_draft_contact(self):
        result = mod.edit_invoice("inv_003", contact_id="cus_002")
        assert result["contact_id"] == "cus_002"

    def test_cannot_edit_approved(self):
        result = mod.edit_invoice("inv_001", contact_id="cus_003")
        assert "error" in result

    def test_approve_draft(self):
        result = mod.edit_invoice("inv_003", state="approved")
        assert result["state"] == "approved"

    def test_update_lines_recalculates_totals(self):
        new_lines = [
            InvoiceLineUpdate(
                product_id="prod_001", description="x", quantity=2, unit_price=500
            )
        ]
        result = mod.edit_invoice("inv_003", lines=new_lines)
        assert result["amount"] == 1000.0
        assert result["tax"] == 250.0
        assert result["gross_amount"] == 1250.0

    def test_not_found_returns_error(self):
        result = mod.edit_invoice("inv_999")
        assert "error" in result


class TestCreateInvoice:
    def test_creates_invoice(self):
        lines = [
            InvoiceLine(
                product_id="prod_001", description="Work", quantity=1, unit_price=2000
            )
        ]
        result = mod.create_invoice("cus_001", lines)
        assert result["id"].startswith("inv_")
        assert result["contact_id"] == "cus_001"

    def test_calculates_totals(self):
        lines = [
            InvoiceLine(
                product_id="prod_001", description="X", quantity=4, unit_price=1000
            )
        ]
        result = mod.create_invoice("cus_001", lines)
        assert result["amount"] == 4000.0
        assert result["gross_amount"] == 5000.0

    def test_increments_id(self):
        lines = [InvoiceLine(product_id="prod_001", quantity=1, unit_price=100)]
        r1 = mod.create_invoice("cus_001", lines)
        r2 = mod.create_invoice("cus_001", lines)
        assert r1["id"] != r2["id"]

    def test_appended_to_list(self):
        lines = [InvoiceLine(product_id="prod_001", quantity=1, unit_price=100)]
        mod.create_invoice("cus_001", lines)
        assert mod.list_invoices()["total"] == 4

    def test_draft_state(self):
        lines = [InvoiceLine(product_id="prod_001", quantity=1, unit_price=100)]
        result = mod.create_invoice("cus_001", lines, state="draft")
        assert result["state"] == "draft"
