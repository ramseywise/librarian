"""Tools node for the native_skill_mcp LangGraph agent.

Executes all tool calls from the latest AIMessage. Meta-tools (load_skill, etc.)
may return a Command with state updates; those are merged into the graph state.
Billy MCP tools return plain values that are wrapped in ToolMessages.

The node always routes to 'maybe_summarize' via Command.goto so that the
summarizer node can decide whether to compact history before the next agent turn.
"""

from __future__ import annotations

import logging

from langchain_core.messages import AIMessage, ToolMessage
from langgraph.types import Command

from langgraph_agents.native_skill_mcp.skills import META_TOOLS
from langgraph_agents.native_skill_mcp.state import AgentState

logger = logging.getLogger(__name__)

_MAX_LOG_LEN = 300


def _truncate(text: str) -> str:
    return text if len(text) <= _MAX_LOG_LEN else text[:_MAX_LOG_LEN] + "…"


def make_tools_node(billy_tools: dict):
    """Return tools_node with billy_tools closed over.

    Called once at graph construction time (after MCP client is ready).
    """
    # Build a unified tool registry: meta-tools + all Billy MCP tools.
    # The agent_node gates which tools the MODEL sees; the tools_node executes
    # whatever the model actually called (trusting the gating contract).
    all_tools_by_name: dict = {t.name: t for t in META_TOOLS} | dict(billy_tools)

    async def tools_node(state: AgentState) -> Command:
        last_ai: AIMessage = state["messages"][-1]

        tool_messages: list[ToolMessage] = []
        skill_updates: list[str] = []

        for tool_call in last_ai.tool_calls:
            tool_name: str = tool_call["name"]
            t = all_tools_by_name.get(tool_name)
            if t is None:
                tool_messages.append(
                    ToolMessage(
                        content=f"Unknown tool '{tool_name}'.",
                        tool_call_id=tool_call["id"],
                        name=tool_name,
                    )
                )
                continue

            logger.info("→ tool_call  %s  args=%s", tool_name, tool_call["args"])
            try:
                result = await t.ainvoke(tool_call)
            except Exception as exc:  # noqa: BLE001
                logger.info("← tool_error %s  %s", tool_name, exc)
                tool_messages.append(
                    ToolMessage(
                        content=f"Tool error: {exc}",
                        tool_call_id=tool_call["id"],
                        name=tool_name,
                    )
                )
                continue

            if isinstance(result, Command):
                # Meta-tools (e.g. load_skill) return Commands with state updates.
                update = result.update or {}
                if "activated_skills" in update:
                    skill_updates.extend(update["activated_skills"])
                if "messages" in update:
                    for msg in update["messages"]:
                        # Ensure the ToolMessage carries the tool name so
                        # langchain_google_genai can populate functionResponse.name
                        # correctly. load_skill omits it; patch it here.
                        if isinstance(msg, ToolMessage) and not getattr(
                            msg, "name", None
                        ):
                            msg = msg.model_copy(update={"name": tool_name})
                        logger.info(
                            "← tool_result %s  %s",
                            tool_name,
                            _truncate(str(msg.content)),
                        )
                        tool_messages.append(msg)
            else:
                logger.info("← tool_result %s  %s", tool_name, _truncate(str(result)))
                tool_messages.append(
                    ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call["id"],
                        name=tool_name,
                    )
                )

        state_update: dict = {"messages": tool_messages}
        if skill_updates:
            # _merge_skills reducer deduplicates; safe to pass partial list.
            state_update["activated_skills"] = skill_updates

        return Command(update=state_update, goto="agent")

    return tools_node
