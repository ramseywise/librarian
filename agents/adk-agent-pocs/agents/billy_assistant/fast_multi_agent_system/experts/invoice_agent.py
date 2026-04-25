from google.adk.agents import Agent

from ..expert_registry import ExpertSpec, register
from ..state import REROUTE_INVOICE
from ..tools.invoice_tools import (
    get_invoice_details,
    update_invoice_field,
    validate_invoice,
)

register(
    ExpertSpec(
        Agent(
            name="invoice_agent",
            model="gemini-3.1-flash-lite-preview",
            description="invoice domain: reading, validating, and updating invoice records",
            tools=[get_invoice_details, validate_invoice, update_invoice_field],
        ),
        routing_terms=["invoice", "bill", "approval", "vat", "amount", "due date"],
        reroute_reason=REROUTE_INVOICE,
    )
)
