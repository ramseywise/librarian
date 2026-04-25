"""Email domain expert for the Billy accounting system."""

from pathlib import Path

from google.adk.agents import Agent
from google.genai import types

from .shared_tools import report_out_of_domain, THINKING_CONFIG
from ..tools.emails import send_invoice_by_email

_INSTRUCTION = (
    Path(__file__).parent.parent / "prompts" / "email_agent.txt"
).read_text()

email_agent = Agent(
    model="gemini-2.5-flash",
    name="email_agent",
    description="Sends approved invoices to customers by email. Drafts a professional Danish subject and body if not provided by the user.",
    static_instruction=types.Content(
        role="user",
        parts=[types.Part(text=_INSTRUCTION)],
    ),
    tools=[send_invoice_by_email, report_out_of_domain],
    generate_content_config=THINKING_CONFIG,
)
