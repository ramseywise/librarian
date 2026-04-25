"""Invoice domain expert for the Billy accounting system."""

from pathlib import Path

from google.adk.agents import Agent
from google.genai import types

from ..tools.customers import list_customers
from ..tools.invoices import (
    create_invoice,
    edit_invoice,
    get_invoice,
    get_invoice_summary,
    list_invoices,
)
from ..tools.products import list_products
from .shared_tools import THINKING_CONFIG, report_out_of_domain

_INSTRUCTION = (
    Path(__file__).parent.parent / "prompts" / "invoice_agent.txt"
).read_text()

invoice_agent = Agent(
    model="gemini-2.5-flash",
    name="invoice_agent",
    description="Handles invoices: create, view, list, edit, approve, and summarize. Covers DKK amounts, VAT, payment terms, and draft vs approved states.",
    static_instruction=types.Content(
        role="user",
        parts=[types.Part(text=_INSTRUCTION)],
    ),
    tools=[
        get_invoice,
        list_invoices,
        get_invoice_summary,
        edit_invoice,
        create_invoice,
        list_customers,
        list_products,
        report_out_of_domain,
    ],
    generate_content_config=THINKING_CONFIG,
)
