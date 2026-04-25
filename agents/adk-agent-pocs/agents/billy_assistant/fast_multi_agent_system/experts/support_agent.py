from google.adk.agents import Agent

from ..expert_registry import ExpertSpec, register
from ..state import REROUTE_SUPPORT
from ..tools.support_tools import get_help_article, get_support_steps

register(
    ExpertSpec(
        Agent(
            name="support_agent",
            model="gemini-3.1-flash-lite-preview",
            description="UI guidance, how-to and how-do-I questions, upload/submit steps, screen navigation, workflow help, feature usage",
            tools=[get_support_steps, get_help_article],
        ),
        routing_terms=[
            "how do i",
            "how to",
            "where",
            "screen",
            "button",
            "ui",
            "workflow",
            "help",
            "upload",
            "submit",
        ],
        reroute_reason=REROUTE_SUPPORT,
    )
)
