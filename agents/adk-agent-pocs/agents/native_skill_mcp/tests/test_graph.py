"""Tests for agent.py — graph compilation, should_continue routing, tools_node."""

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.graph import END
from langgraph.types import Command

from langgraph_agents.native_skill_mcp.agent import build_graph, should_continue
from langgraph_agents.native_skill_mcp.nodes.tools_node import make_tools_node
from langgraph_agents.native_skill_mcp.state import AgentState


# ── Graph compilation ─────────────────────────────────────────────────────────


class TestBuildGraph:
    def test_compiles_without_error(self):
        graph = build_graph(billy_tools={})
        assert graph is not None

    def test_graph_has_expected_nodes(self):
        graph = build_graph(billy_tools={})
        nodes = set(graph.nodes.keys())
        assert {"agent", "tools", "maybe_summarize", "summarize"} <= nodes

    def test_graph_has_start_node(self):
        graph = build_graph(billy_tools={})
        assert "__start__" in graph.nodes


# ── should_continue ───────────────────────────────────────────────────────────


class TestShouldContinue:
    def _state(self, last_message) -> AgentState:
        return AgentState(
            messages=[last_message],
            activated_skills=[],
            summary="",
        )

    def test_ai_with_tool_calls_returns_tools(self):
        ai = AIMessage(
            content="",
            tool_calls=[
                {"id": "tc-1", "name": "load_skill", "args": {}, "type": "tool_call"}
            ],
        )
        assert should_continue(self._state(ai)) == "tools"

    def test_ai_without_tool_calls_returns_end(self):
        ai = AIMessage(content="Here is your answer.")
        assert should_continue(self._state(ai)) == END

    def test_human_message_returns_end(self):
        human = HumanMessage(content="hello")
        assert should_continue(self._state(human)) == END


# ── tools_node (unit — no MCP, no API key) ───────────────────────────────────


class TestToolsNode:
    """Test tools_node behaviour with only meta-tools (no Billy MCP required)."""

    def _make_state(
        self, tool_name: str, tool_args: dict, call_id: str = "tc-1"
    ) -> AgentState:
        ai = AIMessage(
            content="",
            tool_calls=[
                {
                    "id": call_id,
                    "name": tool_name,
                    "args": tool_args,
                    "type": "tool_call",
                }
            ],
        )
        return AgentState(messages=[ai], activated_skills=[], summary="")

    @pytest.mark.asyncio
    async def test_list_skills_returns_tool_message(self):
        node = make_tools_node(billy_tools={})
        state = self._make_state("list_skills", {})
        result = await node(state)
        assert isinstance(result, Command)
        msgs = result.update["messages"]
        assert len(msgs) == 1
        assert isinstance(msgs[0], ToolMessage)
        assert "invoice-skill" in msgs[0].content

    @pytest.mark.asyncio
    async def test_load_skill_updates_activated_skills(self):
        node = make_tools_node(billy_tools={})
        state = self._make_state("load_skill", {"skill_name": "invoice"})
        result = await node(state)
        assert "activated_skills" in result.update
        assert result.update["activated_skills"] == ["invoice-skill"]

    @pytest.mark.asyncio
    async def test_load_skill_message_has_instructions(self):
        node = make_tools_node(billy_tools={})
        state = self._make_state("load_skill", {"skill_name": "invoice"})
        result = await node(state)
        msg = result.update["messages"][0]
        assert "Invoice Operations" in msg.content

    @pytest.mark.asyncio
    async def test_unknown_tool_returns_error_message(self):
        node = make_tools_node(billy_tools={})
        state = self._make_state("completely_unknown_tool", {})
        result = await node(state)
        msgs = result.update["messages"]
        assert "Unknown tool" in msgs[0].content

    @pytest.mark.asyncio
    async def test_run_skill_script_not_supported(self):
        node = make_tools_node(billy_tools={})
        state = self._make_state(
            "run_skill_script",
            {"skill_name": "invoice", "script_name": "run.sh"},
        )
        result = await node(state)
        assert "not supported" in result.update["messages"][0].content.lower()

    @pytest.mark.asyncio
    async def test_routes_to_maybe_summarize(self):
        node = make_tools_node(billy_tools={})
        state = self._make_state("list_skills", {})
        result = await node(state)
        assert result.goto == "maybe_summarize"

    @pytest.mark.asyncio
    async def test_multiple_tool_calls_all_executed(self):
        """When the model calls multiple tools in one turn, all are executed."""
        ai = AIMessage(
            content="",
            tool_calls=[
                {"id": "tc-1", "name": "list_skills", "args": {}, "type": "tool_call"},
                {
                    "id": "tc-2",
                    "name": "run_skill_script",
                    "args": {"skill_name": "invoice", "script_name": "x.sh"},
                    "type": "tool_call",
                },
            ],
        )
        state = AgentState(messages=[ai], activated_skills=[], summary="")
        node = make_tools_node(billy_tools={})
        result = await node(state)
        msgs = result.update["messages"]
        assert len(msgs) == 2
        assert msgs[0].tool_call_id == "tc-1"
        assert msgs[1].tool_call_id == "tc-2"
