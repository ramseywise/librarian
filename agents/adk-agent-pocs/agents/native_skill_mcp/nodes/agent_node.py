"""Agent node for the native_skill_mcp LangGraph agent.

On every turn:
1. Filters the visible tool list based on activated_skills.
2. Prunes old fetch_support_knowledge ToolMessage responses to keep context lean.
3. Prepends any compacted summary as a SystemMessage.
4. Appends the <available_skills> XML block to the system prompt.
5. Binds the filtered tools to the LLM and invokes it.
"""

from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING

from langchain_core.messages import AIMessage, BaseMessage, SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph_agents.native_skill_mcp.skills import (
    LAZY_SKILLS,
    META_TOOLS,
    PRELOADED_SKILLS,
    build_available_skills_xml,
    build_preloaded_section,
    get_visible_tools,
)
from langgraph_agents.native_skill_mcp.state import AgentState

if TYPE_CHECKING:
    pass

_PROMPTS_DIR = pathlib.Path(__file__).parent.parent / "prompts"

_PRELOADED_SECTION = build_preloaded_section(PRELOADED_SKILLS)
_AVAILABLE_SKILLS_XML = build_available_skills_xml(LAZY_SKILLS)

_BASE_SYSTEM_PROMPT = (
    (_PROMPTS_DIR / "root_agent.txt")
    .read_text(encoding="utf-8")
    .replace("{preloaded_skills_section}", _PRELOADED_SECTION)
)

# Full system prompt includes the available_skills block on every turn.
SYSTEM_PROMPT = f"{_BASE_SYSTEM_PROMPT}\n\n{_AVAILABLE_SKILLS_XML}"


def _get_llm() -> ChatGoogleGenerativeAI:
    """Lazy LLM factory — deferred so imports work without GOOGLE_API_KEY set."""
    return ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0)


_PRUNE_TOOL_NAMES: frozenset[str] = frozenset({"fetch_support_knowledge"})


# ── History normalisation ─────────────────────────────────────────────────────


def normalize_messages_for_gemini(messages: list[BaseMessage]) -> list[BaseMessage]:
    """Sanitise the message list before sending to Gemini.

    Two issues specific to Gemini (especially preview models):

    1. Mixed AIMessage content — Gemini rejects history where a model turn has
       *both* text content and function calls.  Strip the text so the turn is a
       pure function-call turn.

    2. Stray SystemMessages inside history — after summarize_node runs it stores
       a SystemMessage at index 0 of state["messages"].  agent_node always
       prepends SystemMessage(SYSTEM_PROMPT), so we'd end up with two consecutive
       SystemMessages.  Strip any SystemMessages from the state-derived list
       here; agent_node adds exactly one at the front.
    """
    result: list[BaseMessage] = []
    for msg in messages:
        if isinstance(msg, SystemMessage):
            # Dropped — agent_node adds the authoritative SystemMessage separately.
            continue
        if isinstance(msg, AIMessage) and msg.tool_calls and msg.content:
            # Strip text from mixed text+function_call model turns.
            msg = msg.model_copy(update={"content": ""})
        result.append(msg)
    return result


# ── History pruning ───────────────────────────────────────────────────────────


def prune_tool_responses(messages: list[BaseMessage]) -> list[BaseMessage]:
    """Replace old fetch_support_knowledge ToolMessage content with '[pruned]'.

    'Old' means not part of the current invocation — i.e., the tool_call_id is
    NOT in the most recent AIMessage's tool_calls. This mirrors ADK's
    make_history_prune_callback behaviour.
    """
    # Find tool_call_ids belonging to the most recent AIMessage.
    current_call_ids: set[str] = set()
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.tool_calls:
            current_call_ids = {tc["id"] for tc in msg.tool_calls}
            break

    pruned: list[BaseMessage] = []
    for msg in messages:
        if (
            isinstance(msg, ToolMessage)
            and getattr(msg, "name", None) in _PRUNE_TOOL_NAMES
            and msg.tool_call_id not in current_call_ids
        ):
            pruned.append(msg.model_copy(update={"content": "[pruned]"}))
        else:
            pruned.append(msg)
    return pruned


# ── Node factory ──────────────────────────────────────────────────────────────


def make_agent_node(billy_tools: dict):
    """Return agent_node with billy_tools closed over.

    Called once at graph construction time (after MCP client is ready).
    """

    _llm_holder: list = []  # mutable cell so the LLM is created once per process

    async def agent_node(state: AgentState, config: RunnableConfig) -> dict:
        if not _llm_holder:
            _llm_holder.append(_get_llm())
        activated = state.get("activated_skills") or []
        visible_tools = get_visible_tools(
            all_billy_tools=billy_tools,
            activated_skills=activated,
            meta_tools=META_TOOLS,
        )

        # Prune old support responses then normalise for Gemini constraints.
        messages = prune_tool_responses(state["messages"])
        messages = normalize_messages_for_gemini(messages)

        # Prepend compacted summary if one exists.
        if state.get("summary"):
            messages = [
                SystemMessage(content=f"[Context summary]\n{state['summary']}")
            ] + messages

        response = (
            await _llm_holder[0]
            .bind_tools(visible_tools)
            .ainvoke(
                [SystemMessage(content=SYSTEM_PROMPT)] + messages,
                config=config,
            )
        )
        return {"messages": [response]}

    return agent_node
