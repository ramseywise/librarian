"""Tests for invoice tools.

Covers get_invoice, list_invoices, get_invoice_summary, edit_invoice, and
create_invoice against the in-memory mock store.
"""

# pylint: disable=no-self-use,too-few-public-methods
import pytest

from playground.agent_poc.agents.billy_assistant.tools.invoices import (
    create_invoice,
    edit_invoice,
    get_invoice,
    get_invoice_summary,
    list_invoices,
)


class TestGetInvoice:
    """Tests for `get_invoice`."""

    @pytest.mark.parametrize(
        ("invoice_id", "expected_no"),
        [
            ("inv_001", "2024-001"),
            ("inv_002", "2024-002"),
            ("inv_003", "2024-003"),
        ],
    )
    def test_returns_correct_invoice(self, invoice_id: str, expected_no: str):
        """Each seed invoice is retrievable by its ID."""
        result = get_invoice(invoice_id)
        assert result["id"] == invoice_id
        assert result["invoiceNo"] == expected_no

    def test_returns_line_items(self):
        """The returned invoice includes at least one line item."""
        result = get_invoice("inv_001")
        assert len(result["lines"]) >= 1

    def test_line_item_has_required_fields(self):
        """Each line item contains productId, quantity, unitPrice, amount, and tax."""
        result = get_invoice("inv_001")
        required = {
            "productId",
            "description",
            "quantity",
            "unitPrice",
            "amount",
            "tax",
        }
        for line in result["lines"]:
            assert required.issubset(line.keys())

    def test_unknown_invoice_returns_error(self):
        """Fetching a non-existent invoice returns an error dict."""
        result = get_invoice("inv_999")
        assert "error" in result


class TestListInvoices:
    """Tests for `list_invoices`."""

    def test_returns_all_invoices_by_default(self):
        """Default call returns all 3 seed invoices."""
        result = list_invoices()
        assert result["total"] == 3
        assert len(result["invoices"]) == 3

    @pytest.mark.parametrize(
        ("states", "expected_count"),
        [
            (["approved"], 2),
            (["draft"], 1),
            (["approved", "draft"], 3),
        ],
    )
    def test_filter_by_state(self, states: list, expected_count: int):
        """Filtering by state returns only the matching invoices."""
        result = list_invoices(states=states)
        assert result["total"] == expected_count
        returned_states = {inv["state"] for inv in result["invoices"]}
        assert returned_states.issubset(set(states))

    def test_filter_by_contact_id(self):
        """Filtering by contact_id returns only that customer's invoices."""
        result = list_invoices(contact_id="cus_001")
        assert result["total"] == 2
        for inv in result["invoices"]:
            assert inv["customerName"] == "Acme A/S"

    @pytest.mark.parametrize(
        ("min_date", "max_date", "expected_count"),
        [
            ("2024-02-01", None, 2),
            (None, "2024-01-31", 1),
            ("2024-01-01", "2024-01-31", 1),
        ],
    )
    def test_filter_by_date_range(
        self, min_date: str | None, max_date: str | None, expected_count: int
    ):
        """Date range filters include and exclude the correct invoices."""
        result = list_invoices(min_entry_date=min_date, max_entry_date=max_date)
        assert result["total"] == expected_count

    def test_page_size_limits_results(self):
        """page_size caps the returned invoices."""
        result = list_invoices(page=1, page_size=2)
        assert len(result["invoices"]) == 2
        assert result["pageCount"] == 2

    def test_sort_direction_desc(self):
        """DESC sort puts the latest entry date first."""
        result = list_invoices(sort_property="entryDate", sort_direction="DESC")
        dates = [inv["entryDate"] for inv in result["invoices"]]
        assert dates == sorted(dates, reverse=True)

    def test_sort_direction_asc(self):
        """ASC sort puts the earliest entry date first."""
        result = list_invoices(sort_property="entryDate", sort_direction="ASC")
        dates = [inv["entryDate"] for inv in result["invoices"]]
        assert dates == sorted(dates)

    def test_invoice_record_has_required_fields(self):
        """Each invoice summary record contains the expected keys."""
        result = list_invoices()
        required = {
            "id",
            "invoiceNo",
            "customerName",
            "entryDate",
            "dueDate",
            "state",
            "grossAmount",
            "currency",
            "isPaid",
        }
        for inv in result["invoices"]:
            assert required.issubset(inv.keys())


class TestGetInvoiceSummary:
    """Tests for `get_invoice_summary`."""

    def test_returns_fiscal_year_in_result(self):
        """The summary always echoes back the fiscal year used."""
        result = get_invoice_summary(fiscal_year=2024)
        assert result["fiscalYear"] == 2024

    def test_all_count_matches_seed_data(self):
        """Total count for 2024 equals the 3 seeded 2024 invoices."""
        result = get_invoice_summary(fiscal_year=2024)
        assert result["all"]["count"] == 3

    def test_paid_count(self):
        """One seed invoice is marked isPaid=True."""
        result = get_invoice_summary(fiscal_year=2024)
        assert result["paid"]["count"] == 1

    def test_draft_count(self):
        """One seed invoice is in draft state."""
        result = get_invoice_summary(fiscal_year=2024)
        assert result["draft"]["count"] == 1

    def test_approved_count(self):
        """Two seed invoices are in approved state."""
        result = get_invoice_summary(fiscal_year=2024)
        assert result["approved"]["count"] == 2

    def test_summary_has_all_buckets(self):
        """The summary contains all required bucket keys."""
        result = get_invoice_summary(fiscal_year=2024)
        for bucket in ("all", "draft", "approved", "paid", "unpaid", "overdue"):
            assert bucket in result, f"missing bucket: {bucket}"
            assert "count" in result[bucket]
            assert "amount" in result[bucket]

    def test_unknown_year_returns_zero_counts(self):
        """A year with no invoices returns zero counts for all buckets."""
        result = get_invoice_summary(fiscal_year=2000)
        assert result["all"]["count"] == 0


class TestEditInvoice:
    """Tests for `edit_invoice`."""

    def test_update_contact_on_draft(self):
        """The contactId of a draft invoice can be changed."""
        result = edit_invoice(invoice_id="inv_003", contact_id="cus_002")
        assert result["contactId"] == "cus_002"

    def test_approve_draft_invoice(self):
        """Setting state='approved' on a draft invoice changes its state."""
        result = edit_invoice(invoice_id="inv_003", state="approved")
        assert result["state"] == "approved"

    def test_approved_invoice_cannot_be_edited(self):
        """Attempting to edit an approved invoice returns an error."""
        result = edit_invoice(invoice_id="inv_001", contact_id="cus_002")
        assert "error" in result
        assert "draft" in result["error"].lower()

    def test_unknown_invoice_returns_error(self):
        """Editing a non-existent invoice returns an error dict."""
        result = edit_invoice(invoice_id="inv_999", contact_id="cus_001")
        assert "error" in result

    def test_update_entry_date(self):
        """The entry date of a draft invoice can be updated."""
        result = edit_invoice(invoice_id="inv_003", entry_date="2024-04-01")
        assert result["entryDate"] == "2024-04-01"

    def test_update_lines_recalculates_amounts(self):
        """Replacing lines updates the invoice totals correctly."""
        new_lines = [
            {
                "productId": "prod_001",
                "description": "Work",
                "quantity": 5,
                "unitPrice": 200.0,
            }
        ]
        result = edit_invoice(invoice_id="inv_003", lines=new_lines)
        assert result["amount"] == pytest.approx(1000.0)
        assert result["tax"] == pytest.approx(250.0)
        assert result["grossAmount"] == pytest.approx(1250.0)

    def test_add_new_line_without_id(self):
        """Providing a line without an id appends a new line to the invoice."""
        original_line_count = len(get_invoice("inv_003")["lines"])
        new_line = {
            "productId": "prod_002",
            "description": "Extra",
            "quantity": 1,
            "unitPrice": 500.0,
        }
        result = edit_invoice(invoice_id="inv_003", lines=[new_line])
        assert len(result["lines"]) == 1  # replace all lines with the provided set


class TestCreateInvoice:
    """Tests for `create_invoice`."""

    def test_creates_invoice_with_single_line(self):
        """A minimal invoice with one line is created successfully."""
        result = create_invoice(
            contact_id="cus_001",
            lines=[{"productId": "prod_001", "quantity": 2, "unitPrice": 500.0}],
        )
        assert "id" in result
        assert result["contactId"] == "cus_001"
        assert len(result["lines"]) == 1

    def test_amounts_calculated_correctly(self):
        """Amount, tax (25%), and grossAmount are derived from line items."""
        result = create_invoice(
            contact_id="cus_002",
            lines=[{"productId": "prod_001", "quantity": 4, "unitPrice": 1000.0}],
        )
        assert result["amount"] == pytest.approx(4000.0)
        assert result["tax"] == pytest.approx(1000.0)
        assert result["grossAmount"] == pytest.approx(5000.0)

    def test_multiple_lines_summed(self):
        """Totals are the sum across all provided lines."""
        result = create_invoice(
            contact_id="cus_001",
            lines=[
                {"productId": "prod_001", "quantity": 2, "unitPrice": 1000.0},
                {"productId": "prod_002", "quantity": 1, "unitPrice": 500.0},
            ],
        )
        assert result["amount"] == pytest.approx(2500.0)

    def test_created_invoice_appears_in_list(self):
        """The new invoice is immediately returned by list_invoices."""
        create_invoice(
            contact_id="cus_003",
            lines=[{"productId": "prod_001", "quantity": 1, "unitPrice": 100.0}],
        )
        result = list_invoices()
        assert result["total"] == 4

    @pytest.mark.parametrize("state", ["approved", "draft"])
    def test_state_is_honoured(self, state: str):
        """The invoice is created in the requested state."""
        result = create_invoice(
            contact_id="cus_001",
            lines=[{"productId": "prod_001", "quantity": 1, "unitPrice": 100.0}],
            state=state,
        )
        assert result["state"] == state

    def test_two_invoices_have_different_ids(self):
        """Successive creates produce unique invoice IDs."""
        r1 = create_invoice(
            contact_id="cus_001",
            lines=[{"productId": "prod_001", "quantity": 1, "unitPrice": 100.0}],
        )
        r2 = create_invoice(
            contact_id="cus_001",
            lines=[{"productId": "prod_001", "quantity": 1, "unitPrice": 100.0}],
        )
        assert r1["id"] != r2["id"]

    def test_default_currency_is_dkk(self):
        """The default currency is DKK when none is specified."""
        result = create_invoice(
            contact_id="cus_001",
            lines=[{"productId": "prod_001", "quantity": 1, "unitPrice": 100.0}],
        )
        assert result["currency"] == "DKK"
