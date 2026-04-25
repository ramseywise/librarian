"""Email tools for the Billy accounting system."""

# ---------------------------------------------------------------------------
# Mock data — contact persons index (shared with invoice tools)
# ---------------------------------------------------------------------------

_MOCK_CONTACT_PERSONS = {
    "cus_001": {"id": "cp_001", "email": "kontakt@acme.dk", "isPrimary": True},
    "cus_002": {"id": "cp_002", "email": "info@nordisktech.dk", "isPrimary": True},
    "cus_003": {"id": "cp_003", "email": "lars@hansen.dk", "isPrimary": True},
}

# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


def send_invoice_by_email(
    invoice_id: str,
    contact_id: str,
    email_subject: str,
    email_body: str,
) -> dict:
    """Sends an invoice by email to the customer's primary contact person.

    Requires the invoice ID, contact ID, email subject, and email body text.

    Args:
        invoice_id: The invoice ID to send.
        contact_id: The customer/contact ID associated with this invoice.
        email_subject: Email subject line.
        email_body: Email body text.

    Returns:
        Dict with success status, invoiceId, sentState, and a confirmation message.
    """
    person = _MOCK_CONTACT_PERSONS.get(contact_id)
    if not person:
        return {
            "success": False,
            "error": "No contact person found for this customer.",
        }

    return {
        "success": True,
        "invoiceId": invoice_id,
        "sentState": "sent",
        "message": f"Invoice successfully sent by email to {person['email']}.",
    }
