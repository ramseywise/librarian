"""Root agent (billy_assistant) for the Billy accounting system."""

import os
from pathlib import Path

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.readonly_context import ReadonlyContext
from google.genai import types

from agents.shared.debug import attach

from .sub_agents.customer_agent import customer_agent
from .sub_agents.email_agent import email_agent
from .sub_agents.invitation_agent import invitation_agent
from .sub_agents.invoice_agent import invoice_agent
from .sub_agents.product_agent import product_agent
from .sub_agents.support_agent import support_agent

_DEBUG = os.getenv("BILLY_DEBUG", "0") == "1"

_PROMPTS = Path(__file__).parent / "prompts"
_INSTRUCTION = (_PROMPTS / "billy_assistant.txt").read_text()
_TRIED_AGENTS_TEMPLATE = (_PROMPTS / "router_tried_agents.txt").read_text()


def provide_router_instruction(ctx: ReadonlyContext) -> str:
    tried = ctx._invocation_context.session.state.get("tried_agents", [])
    if not tried:
        return ""
    return _TRIED_AGENTS_TEMPLATE.format(agents=", ".join(tried))


def clear_tried_agents(callback_context: CallbackContext) -> None:
    invocation_id = callback_context._invocation_context.invocation_id
    if callback_context.state.get("_tried_agents_invocation") != invocation_id:
        callback_context.state["tried_agents"] = []
        callback_context.state["_tried_agents_invocation"] = invocation_id


root_agent = attach(
    Agent(
        model="gemini-2.5-flash-lite",
        name="billy_assistant",
        description=(
            "Routing assistant for the Billy accounting platform. Classifies user requests "
            "and delegates to the correct domain expert: invoices, customers, products, "
            "email sending, user invitations, or support. Does not answer domain questions directly."
        ),
        generate_content_config=types.GenerateContentConfig(
            temperature=0,
            max_output_tokens=150,
        ),
        static_instruction=types.Content(
            role="user",
            parts=[types.Part(text=_INSTRUCTION)],
        ),
        instruction=provide_router_instruction,
        sub_agents=[
            attach(invoice_agent, debug=_DEBUG),
            attach(customer_agent, debug=_DEBUG),
            attach(product_agent, debug=_DEBUG),
            attach(email_agent, debug=_DEBUG),
            attach(invitation_agent, debug=_DEBUG),
            attach(support_agent, debug=_DEBUG),
        ],
        before_agent_callback=clear_tried_agents,
    ),
    debug=_DEBUG,
)
