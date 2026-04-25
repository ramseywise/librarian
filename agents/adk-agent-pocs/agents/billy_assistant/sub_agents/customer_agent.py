"""Customer domain expert for the Billy accounting system."""

from pathlib import Path

from google.adk.agents import Agent
from google.genai import types

from .shared_tools import report_out_of_domain, THINKING_CONFIG
from ..tools.customers import (
    create_customer,
    edit_customer,
    list_customers,
)

_INSTRUCTION = (
    Path(__file__).parent.parent / "prompts" / "customer_agent.txt"
).read_text()

customer_agent = Agent(
    model="gemini-2.5-flash",
    name="customer_agent",
    description="Manages customer and contact records: create, view, list, and edit. Handles both company and person contacts, including CVR and email updates.",
    static_instruction=types.Content(
        role="user",
        parts=[types.Part(text=_INSTRUCTION)],
    ),
    tools=[list_customers, edit_customer, create_customer, report_out_of_domain],
    generate_content_config=THINKING_CONFIG,
)
