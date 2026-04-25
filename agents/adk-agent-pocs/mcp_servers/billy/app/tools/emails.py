"""Email stub tools for the Billy MCP server."""

from playground.agent_poc.mcp_servers.billy.app.db import get_conn


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
        Dict with success status, invoice_id, sent_state, and a confirmation message.
    """
    with get_conn() as conn:
        row = conn.execute(
            "SELECT email FROM customers WHERE id = ?", (contact_id,)
        ).fetchone()

    email = row["email"] if row else None
    if not email:
        return {
            "success": False,
            "error": "No email address found for this customer. Please update their contact details first.",
        }

    return {
        "success": True,
        "invoice_id": invoice_id,
        "sent_state": "sent",
        "message": f"Invoice successfully sent by email to {email}.",
    }
