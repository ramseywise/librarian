"""Graph assembly and entrypoint for the native_skill_mcp LangGraph agent.

Graph structure:

    START → agent → (tool_calls?) → tools → agent → … → END

History compaction runs as a background asyncio.Task after each full turn
(see _background_summarize). It does not block the REPL — by the time the
user types their next message the compacted state is already written back.

Key design points:
- tools_node returns Command(goto="agent") — no summarize nodes in the graph.
- Checkpointer persists activated_skills across turns (thread_id required).
- MCP client must be opened once per process via build_mcp_client().

Quick start (dev mode, in-memory checkpointer):

    import asyncio
    from dotenv import load_dotenv
    from langchain_core.messages import HumanMessage
    from langgraph_agents.native_skill_mcp.agent import run_turn

    load_dotenv()

    async def main():
        reply = await run_turn("How do I void an invoice?", thread_id="demo")
        print(reply)

    asyncio.run(main())
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import TYPE_CHECKING

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(message)s",
    datefmt="%H:%M:%S",
)
logging.getLogger("langchain_google_genai").setLevel(logging.ERROR)

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph as CompiledGraph

from langgraph.types import Overwrite

from langgraph_agents.native_skill_mcp.nodes.agent_node import make_agent_node
from langgraph_agents.native_skill_mcp.nodes.summarizer_node import (
    COMPACTION_INTERVAL,
    _count_active,
    summarize_state,
)
from langgraph_agents.native_skill_mcp.nodes.tools_node import make_tools_node
from langgraph_agents.native_skill_mcp.state import AgentState
from langgraph_agents.native_skill_mcp.tools import (
    build_mcp_client,
    load_all_billy_tools,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    pass


def should_continue(state: AgentState) -> str:
    """Conditional edge from agent: route to 'tools' if there are pending tool calls."""
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return END


def build_graph(billy_tools: dict) -> CompiledGraph:
    """Compile and return the Billy LangGraph agent.

    Graph: START → agent → tools → agent → … → END
    Summarization happens as a background asyncio task after each full turn
    (see _background_summarize / run_turn) rather than as an in-graph node.
    """
    agent_node = make_agent_node(billy_tools)
    tools_node = make_tools_node(billy_tools)

    builder = StateGraph(AgentState)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", tools_node)

    builder.add_edge(START, "agent")
    builder.add_conditional_edges(
        "agent", should_continue, {"tools": "tools", END: END}
    )
    # tools_node returns Command(goto="agent"); static edge is a schema safety-net.
    builder.add_edge("tools", "agent")

    checkpointer = InMemorySaver()
    return builder.compile(checkpointer=checkpointer)


# ── Process-level singletons (set by init_graph) ─────────────────────────────

_graph: CompiledGraph | None = None
_mcp_client = None  # kept open for the process lifetime


async def init_graph() -> CompiledGraph:
    """Load Billy tools, compile graph. Call once at startup.

    langchain-mcp-adapters >= 0.1.0: MultiServerMCPClient is not a context
    manager; tools are loaded by calling get_tools() directly.
    """
    global _graph, _mcp_client
    _mcp_client = build_mcp_client()
    billy_tools = await load_all_billy_tools(_mcp_client)
    _graph = build_graph(billy_tools)
    return _graph


async def get_graph() -> CompiledGraph:
    """Return the compiled graph, initialising it on first call."""
    if _graph is None:
        await init_graph()
    return _graph  # type: ignore[return-value]


# ── Convenience helper for REPL / tests ──────────────────────────────────────


async def _background_summarize(
    graph: CompiledGraph, config: dict, messages: list
) -> None:
    """Compact history in the background after a turn completes.

    Runs as an asyncio.Task so it doesn't block the REPL. Writes compacted
    state back via graph.aupdate_state before the next user message arrives.
    If the user types faster than the summarizer responds, the update is a
    no-op (the next ainvoke already created a newer checkpoint).
    """
    if _count_active(messages) < COMPACTION_INTERVAL:
        return
    logger.info(
        "background summarize: %d active messages → compacting…",
        _count_active(messages),
    )
    compacted, summary_text = await summarize_state(messages)
    await graph.aupdate_state(
        config,
        {"messages": Overwrite(compacted), "summary": summary_text},
    )
    logger.info("background summarize done: → %d messages", len(compacted))


async def run_turn(message: str, thread_id: str = "default") -> str:
    """Send one message and return the assistant's text reply.

    Thread state (including activated_skills) is persisted across calls
    within the same thread_id via the in-memory checkpointer.
    After the reply is ready a background task compacts history if needed.
    """
    graph = await get_graph()
    config = {"configurable": {"thread_id": thread_id}}
    result = await graph.ainvoke(
        {"messages": [HumanMessage(content=message)]},
        config=config,
    )
    asyncio.create_task(_background_summarize(graph, config, result["messages"]))
    last = result["messages"][-1]
    return last.content if hasattr(last, "content") else str(last)


# ── CLI entry point ───────────────────────────────────────────────────────────


async def _chat_loop() -> None:
    """Simple interactive REPL for local development."""
    from dotenv import load_dotenv  # noqa: PLC0415

    load_dotenv()
    thread_id = os.getenv("THREAD_ID", "cli-session")
    print("Billy Assistant (LangGraph) — type 'quit' to exit\n")
    await init_graph()
    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            break
        if user_input.lower() in {"quit", "exit", "q"}:
            break
        if not user_input:
            continue
        reply = await run_turn(user_input, thread_id=thread_id)
        print(f"Billy: {reply}\n")


if __name__ == "__main__":
    asyncio.run(_chat_loop())
