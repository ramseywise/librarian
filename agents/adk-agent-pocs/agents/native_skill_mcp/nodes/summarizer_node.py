"""Summarizer nodes for the native_skill_mcp LangGraph agent.

Equivalent to ADK's EventsCompactionConfig(compaction_interval=8, overlap_size=4).

Graph wiring:
  tools_node → maybe_summarize_node
                   ↓ (conditional edge: should_summarize)
             summarize_node  ──→  agent
                   ↓ (else)
               agent_node

Key detail: summarize_node uses Overwrite() to REPLACE messages entirely.
Without Overwrite the add_messages reducer would APPEND the compacted messages
to the existing list instead of replacing them.
"""

from __future__ import annotations

import pathlib

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.types import Overwrite

from langgraph_agents.native_skill_mcp.state import AgentState

_PROMPTS_DIR = pathlib.Path(__file__).parent.parent / "prompts"
_SUMMARIZER_TEMPLATE = (_PROMPTS_DIR / "summarizer.txt").read_text(encoding="utf-8")

COMPACTION_INTERVAL: int = 8
OVERLAP_SIZE: int = 4


def _get_summarizer_llm() -> ChatGoogleGenerativeAI:
    """Lazy factory — deferred so imports work without GOOGLE_API_KEY set."""
    return ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _is_pruned(msg: BaseMessage) -> bool:
    return isinstance(msg, ToolMessage) and msg.content == "[pruned]"


def _count_active(messages: list[BaseMessage]) -> int:
    return sum(1 for m in messages if not _is_pruned(m))


def format_messages_for_summary(messages: list[BaseMessage]) -> str:
    """Convert LangChain messages to readable text for the summarizer prompt.

    The summarizer.txt template was written for function_call / function_response
    style; this converts LangChain message types to an equivalent readable form.
    """
    lines: list[str] = []
    for msg in messages:
        if isinstance(msg, SystemMessage):
            lines.append(f"[system]: {msg.content}")
        elif isinstance(msg, HumanMessage):
            lines.append(f"[user]: {msg.content}")
        elif isinstance(msg, AIMessage):
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    lines.append(f"[assistant tool_call {tc['name']}]: {tc['args']}")
            else:
                lines.append(f"[assistant]: {msg.content}")
        elif isinstance(msg, ToolMessage):
            name = getattr(msg, "name", "tool")
            content = msg.content if msg.content != "[pruned]" else "(pruned)"
            lines.append(f"[tool_response {name}]: {content}")
        else:
            lines.append(f"[{type(msg).__name__}]: {msg.content}")
    return "\n".join(lines)


# ── Nodes and edge condition ──────────────────────────────────────────────────


async def maybe_summarize_node(state: AgentState) -> dict:
    """Pass-through node; routing decided by should_summarize conditional edge."""
    return {}


def should_summarize(state: AgentState) -> str:
    """Conditional edge after maybe_summarize: 'summarize' or 'agent'."""
    if _count_active(state["messages"]) >= COMPACTION_INTERVAL:
        return "summarize"
    return "agent"


def _safe_overlap(
    messages: list[BaseMessage], overlap_size: int
) -> tuple[list[BaseMessage], list[BaseMessage]]:
    """Return (to_summarize, to_keep) ensuring to_keep starts at a HumanMessage.

    Gemini requires the conversation to begin with a user turn.  A plain slice
    of the last N messages can land in the middle of a tool-calling sequence,
    leaving an orphaned ToolMessage or AIMessage as the first item — which
    Gemini rejects with "function call turn comes immediately after a user turn".

    Strategy:
    1. Start with the raw last-N slice.
    2. If it doesn't begin with a HumanMessage, walk backward through
       to_summarize to find the most recent HumanMessage and prepend it.
    3. If no HumanMessage exists anywhere (shouldn't happen in practice),
       fall back to the raw slice.
    """
    if len(messages) <= overlap_size:
        return [], messages

    raw_start = len(messages) - overlap_size
    to_keep = list(messages[raw_start:])
    to_summarize = list(messages[:raw_start])

    if to_keep and not isinstance(to_keep[0], HumanMessage):
        # Walk backward in to_summarize to find the last HumanMessage.
        for i in range(len(to_summarize) - 1, -1, -1):
            if isinstance(to_summarize[i], HumanMessage):
                # Move it (and everything after it in to_summarize) to to_keep.
                to_keep = list(to_summarize[i:]) + to_keep
                to_summarize = list(to_summarize[:i])
                break

    return to_summarize, to_keep


async def summarize_state(messages: list[BaseMessage]) -> tuple[list[BaseMessage], str]:
    """Summarize messages. Returns (compacted_list, summary_text).

    Called by the background task in agent.py — no graph dependency.
    """
    to_summarize, to_keep = _safe_overlap(messages, OVERLAP_SIZE)
    history_text = format_messages_for_summary(to_summarize)
    summary_prompt = (
        f"{_SUMMARIZER_TEMPLATE}\n\n---\n\nHistory to compress:\n\n{history_text}"
    )
    response = await _get_summarizer_llm().ainvoke(summary_prompt)
    summary_text: str = response.content  # type: ignore[assignment]
    compacted: list[BaseMessage] = [
        SystemMessage(content=f"[Context summary]\n{summary_text}")
    ]
    return compacted + list(to_keep), summary_text


async def summarize_node(state: AgentState) -> dict:
    """Compact history: summarize all but the last OVERLAP_SIZE messages.

    Returns Overwrite(messages=...) so that the add_messages reducer is bypassed
    and the compacted list replaces the existing messages entirely.
    activated_skills is a separate state field — it survives compaction unchanged.
    """
    messages = state["messages"]
    to_summarize, to_keep = _safe_overlap(messages, OVERLAP_SIZE)

    history_text = format_messages_for_summary(to_summarize)
    summary_prompt = (
        f"{_SUMMARIZER_TEMPLATE}\n\n---\n\nHistory to compress:\n\n{history_text}"
    )

    response = await _get_summarizer_llm().ainvoke(summary_prompt)
    summary_text: str = response.content  # type: ignore[assignment]

    compacted: list[BaseMessage] = [
        SystemMessage(content=f"[Context summary]\n{summary_text}")
    ]
    return {
        "messages": Overwrite(compacted + list(to_keep)),
        "summary": summary_text,
    }
