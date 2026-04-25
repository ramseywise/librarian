from google.adk.agents import Agent

from ..callbacks import receptionist_before_model_callback
from ..expert_registry import register
from ..tools import (
    get_invoice_details,
    note_invoice_id,
    update_invoice_field,
    validate_invoice,
)

register(
    Agent(
        name="invoice_agent",
        model="gemini-3-flash-preview",
        description=(
            "Handles all invoice and billing topics: invoices, payments, charges, "
            "refunds, subscriptions, and pricing questions."
        ),
        tools=[
            get_invoice_details,
            validate_invoice,
            update_invoice_field,
            note_invoice_id,
        ],
        before_model_callback=receptionist_before_model_callback,
    ),
    routing_terms=[
        # Multi-word terms first — more specific, higher confidence per match.
        "show me invoice",
        "show invoice",
        "display invoice",
        "update invoice",
        "update the vat",
        "update vat",
        "validate invoice",
        "get invoice",
        "invoice id",
        "invoice number",
        "invoice detail",
        "due date",
        "vat rate",
        "vendor name",
        # Single-word signals — increase score but not sufficient alone (confidence=0.5).
        "invoice",
        "billing",
        "payment",
        "vendor",
        "vat",
    ],
)
