"""Tests for the send_invoice_by_email tool."""

# pylint: disable=no-self-use,too-few-public-methods
import pytest

from playground.agent_poc.agents.billy_assistant.tools.emails import (
    send_invoice_by_email,
)


class TestSendInvoiceByEmail:
    """Tests for `send_invoice_by_email`."""

    @pytest.mark.parametrize(
        ("invoice_id", "contact_id", "expected_email_fragment"),
        [
            ("inv_001", "cus_001", "acme.dk"),
            ("inv_002", "cus_002", "nordisktech.dk"),
            ("inv_003", "cus_003", "hansen.dk"),
        ],
    )
    def test_send_succeeds_for_known_contacts(
        self, invoice_id: str, contact_id: str, expected_email_fragment: str
    ):
        """A known contact_id results in a successful send with the correct address."""
        result = send_invoice_by_email(
            invoice_id=invoice_id,
            contact_id=contact_id,
            email_subject="Faktura",
            email_body="Se venligst vedhæftede faktura.",
        )
        assert result["success"] is True
        assert result["invoiceId"] == invoice_id
        assert result["sentState"] == "sent"
        assert expected_email_fragment in result["message"]

    def test_send_fails_for_unknown_contact(self):
        """An unknown contact_id returns success=False with an error message."""
        result = send_invoice_by_email(
            invoice_id="inv_001",
            contact_id="cus_999",
            email_subject="Faktura",
            email_body="Body",
        )
        assert result["success"] is False
        assert "error" in result

    def test_invoice_id_echoed_in_response(self):
        """The invoiceId in the response matches what was passed in."""
        result = send_invoice_by_email(
            invoice_id="inv_002",
            contact_id="cus_002",
            email_subject="Test",
            email_body="Test body",
        )
        assert result["invoiceId"] == "inv_002"

    def test_message_contains_recipient_address(self):
        """The confirmation message includes the recipient's email address."""
        result = send_invoice_by_email(
            invoice_id="inv_001",
            contact_id="cus_001",
            email_subject="Faktura #1",
            email_body="Hej,\n\nSe faktura.",
        )
        assert "kontakt@acme.dk" in result["message"]
