"""Product domain expert for the Billy accounting system."""

from pathlib import Path

from google.adk.agents import Agent
from google.genai import types

from .shared_tools import report_out_of_domain, THINKING_CONFIG
from ..tools.products import (
    create_product,
    edit_product,
    list_products,
)

_INSTRUCTION = (
    Path(__file__).parent.parent / "prompts" / "product_agent.txt"
).read_text()

product_agent = Agent(
    model="gemini-2.5-flash",
    name="product_agent",
    description="Manages the product catalogue: create, view, list, and edit products and services including unit prices (excl. VAT).",
    static_instruction=types.Content(
        role="user",
        parts=[types.Part(text=_INSTRUCTION)],
    ),
    tools=[list_products, edit_product, create_product, report_out_of_domain],
    generate_content_config=THINKING_CONFIG,
)
