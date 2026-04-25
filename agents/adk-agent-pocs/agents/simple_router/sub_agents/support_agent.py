from google.adk.agents import Agent

from ..expert_registry import register
from ..tools import get_help_article, get_support_steps

register(
    Agent(
        name="support_agent",
        model="gemini-3.1-flash-lite-preview",
        description=(
            "Handles product support: how-to questions, UI guidance, troubleshooting, "
            "and account access issues."
        ),
        tools=[get_support_steps, get_help_article],
    ),
    routing_terms=[
        # Multi-word terms — more precise, higher confidence per match.
        "login error",
        "access issue",
        "not working",
        "it's not working",
        "getting a",
        "getting an",
        "can't login",
        "cannot login",
        "can't access",
        "cannot access",
        # Single-word signals — increase score but not sufficient alone.
        "error",
        "troubleshoot",
        "problem",
        "issue",
        "failed",
        "broken",
    ],
)
