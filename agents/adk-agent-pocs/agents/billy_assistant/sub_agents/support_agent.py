"""Support domain expert for the Billy accounting system."""

from pathlib import Path

from google.adk.agents import Agent
from google.genai import types

from ..tools.support_knowledge import fetch_support_knowledge
from .shared_tools import SUPPORT_THINKING_CONFIG, report_out_of_domain

_INSTRUCTION = (
    Path(__file__).parent.parent / "prompts" / "support_agent.txt"
).read_text()

support_agent = Agent(
    model="gemini-2.5-flash",
    name="support_agent",
    description="Answers questions about how Billy works by searching the official help documentation. Does not cover other domains.",
    static_instruction=types.Content(
        role="user",
        parts=[types.Part(text=_INSTRUCTION)],
    ),
    tools=[fetch_support_knowledge, report_out_of_domain],
    generate_content_config=SUPPORT_THINKING_CONFIG,
)
