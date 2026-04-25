"""Invitation domain expert for the Billy accounting system."""

from pathlib import Path

from google.adk.agents import Agent
from google.genai import types

from .shared_tools import report_out_of_domain, THINKING_CONFIG
from ..tools.invitations import invite_user

_INSTRUCTION = (
    Path(__file__).parent.parent / "prompts" / "invitation_agent.txt"
).read_text()

invitation_agent = Agent(
    model="gemini-2.5-flash",
    name="invitation_agent",
    description="Invites new collaborators to the Billy organization by email address, assigning them the collaborator role.",
    static_instruction=types.Content(
        role="user",
        parts=[types.Part(text=_INSTRUCTION)],
    ),
    tools=[invite_user, report_out_of_domain],
    generate_content_config=THINKING_CONFIG,
)
