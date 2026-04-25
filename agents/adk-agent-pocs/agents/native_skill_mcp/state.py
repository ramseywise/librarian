"""State schema for the native_skill_mcp LangGraph agent."""

from typing import Annotated

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


def _merge_skills(current: list[str] | None, new: list[str]) -> list[str]:
    """Reducer: append new skills to current list, deduplicating."""
    if not current:
        current = []
    result = list(current)
    for skill in new:
        if skill not in result:
            result.append(skill)
    return result


class AgentState(TypedDict):
    """Graph state for the Billy LangGraph agent.

    activated_skills tracks which lazy skills have been loaded this session.
    Using a custom reducer means load_skill can return just [skill_name] and
    the reducer merges it with the existing list — no InjectedState needed.
    """

    messages: Annotated[list, add_messages]
    activated_skills: Annotated[list[str], _merge_skills]
    summary: str
