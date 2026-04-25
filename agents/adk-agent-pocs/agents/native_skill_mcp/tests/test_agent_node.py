"""Tests for agent_node.py — prune_tool_responses and normalize_messages_for_gemini."""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from langgraph_agents.native_skill_mcp.nodes.agent_node import (
    normalize_messages_for_gemini,
    prune_tool_responses,
)


def _ai_with_tool_call(tool_call_id: str, tool_name: str) -> AIMessage:
    return AIMessage(
        content="",
        tool_calls=[
            {"id": tool_call_id, "name": tool_name, "args": {}, "type": "tool_call"}
        ],
    )


def _tool_msg(tool_call_id: str, name: str, content: str = "result") -> ToolMessage:
    return ToolMessage(content=content, tool_call_id=tool_call_id, name=name)


class TestPruneToolResponses:
    def test_empty_messages(self):
        assert prune_tool_responses([]) == []

    def test_human_messages_unchanged(self):
        msgs = [HumanMessage(content="hi")]
        result = prune_tool_responses(msgs)
        assert len(result) == 1
        assert result[0].content == "hi"

    def test_non_support_tool_never_pruned(self):
        """Only fetch_support_knowledge responses are subject to pruning."""
        ai = _ai_with_tool_call("tc-1", "list_invoices")
        tool = _tool_msg("tc-1", "list_invoices", "invoice list")
        result = prune_tool_responses([ai, tool])
        assert result[1].content == "invoice list"

    def test_current_invocation_support_not_pruned(self):
        """The most recent AIMessage's tool calls are the 'current' invocation."""
        ai = _ai_with_tool_call("tc-1", "fetch_support_knowledge")
        tool = _tool_msg("tc-1", "fetch_support_knowledge", "KB result")
        result = prune_tool_responses([ai, tool])
        assert result[1].content == "KB result"  # current — not pruned

    def test_old_support_response_pruned(self):
        """A fetch_support_knowledge response is pruned once a newer tool call exists.

        The pruner keeps the 'current' invocation = the most recent AIMessage that
        has tool_calls. tc-old becomes 'old' only when a NEWER AIMessage with tool
        calls replaces it as the current invocation.
        """
        ai1 = _ai_with_tool_call("tc-old", "fetch_support_knowledge")
        tool1 = _tool_msg("tc-old", "fetch_support_knowledge", "old KB result")
        # A subsequent agent turn makes a different tool call — tc-old is now old.
        ai2 = _ai_with_tool_call("tc-new", "list_invoices")
        tool2 = _tool_msg("tc-new", "list_invoices", "invoice list")
        result = prune_tool_responses([ai1, tool1, ai2, tool2])
        assert result[1].content == "[pruned]"  # tc-old fsk — pruned
        assert result[3].content == "invoice list"  # tc-new list_invoices — not pruned

    def test_multiple_old_support_responses_all_pruned(self):
        ai1 = _ai_with_tool_call("tc-1", "fetch_support_knowledge")
        tool1 = _tool_msg("tc-1", "fetch_support_knowledge", "first KB")
        ai2 = _ai_with_tool_call("tc-2", "fetch_support_knowledge")
        tool2 = _tool_msg("tc-2", "fetch_support_knowledge", "second KB")
        # Turn 3: new AI message with a different call — makes both old
        ai3 = _ai_with_tool_call("tc-3", "list_invoices")
        tool3 = _tool_msg("tc-3", "list_invoices", "invoices")
        result = prune_tool_responses([ai1, tool1, ai2, tool2, ai3, tool3])
        assert result[1].content == "[pruned]"  # tc-1 support
        assert result[3].content == "[pruned]"  # tc-2 support
        assert result[5].content == "invoices"  # tc-3 list_invoices — not pruned

    def test_current_support_among_multiple_not_pruned(self):
        """When the current AIMessage calls fetch_support_knowledge, that response is kept."""
        old_ai = _ai_with_tool_call("tc-old", "fetch_support_knowledge")
        old_tool = _tool_msg("tc-old", "fetch_support_knowledge", "old result")
        current_ai = _ai_with_tool_call("tc-new", "fetch_support_knowledge")
        current_tool = _tool_msg("tc-new", "fetch_support_knowledge", "fresh result")
        result = prune_tool_responses([old_ai, old_tool, current_ai, current_tool])
        assert result[1].content == "[pruned]"  # old
        assert result[3].content == "fresh result"  # current

    def test_pruning_replaces_only_content(self):
        """Pruned messages retain their type and tool_call_id."""
        ai = _ai_with_tool_call("tc-old", "fetch_support_knowledge")
        tool = _tool_msg("tc-old", "fetch_support_knowledge", "KB result")
        # A newer tool call makes tc-old 'old' (prune_tool_responses tracks the
        # most recent AIMessage that has tool_calls as 'current').
        ai2 = _ai_with_tool_call("tc-new", "list_invoices")
        tool2 = _tool_msg("tc-new", "list_invoices", "results")
        result = prune_tool_responses([ai, tool, ai2, tool2])
        pruned = result[1]
        assert isinstance(pruned, ToolMessage)
        assert pruned.tool_call_id == "tc-old"
        assert pruned.content == "[pruned]"

    def test_system_messages_pass_through(self):
        sys = SystemMessage(content="You are Billy")
        result = prune_tool_responses([sys])
        assert result[0].content == "You are Billy"

    def test_no_ai_message_support_tools_pruned(self):
        """If there's no AIMessage at all, no call IDs are 'current' → all pruned."""
        tool = _tool_msg("tc-1", "fetch_support_knowledge", "orphan result")
        result = prune_tool_responses([tool])
        assert result[0].content == "[pruned]"


class TestNormalizeMessagesForGemini:
    def test_empty_list(self):
        assert normalize_messages_for_gemini([]) == []

    def test_system_messages_stripped(self):
        """SystemMessages inside state history are removed; agent_node adds its own."""
        sys = SystemMessage(content="[Context summary] ...")
        human = HumanMessage(content="hi")
        result = normalize_messages_for_gemini([sys, human])
        assert len(result) == 1
        assert isinstance(result[0], HumanMessage)

    def test_multiple_system_messages_stripped(self):
        sys1 = SystemMessage(content="summary A")
        sys2 = SystemMessage(content="summary B")
        human = HumanMessage(content="hi")
        result = normalize_messages_for_gemini([sys1, sys2, human])
        assert result == [human]

    def test_ai_message_with_only_text_unchanged(self):
        """Plain text AIMessage (no tool_calls) passes through untouched."""
        ai = AIMessage(content="Hello!")
        result = normalize_messages_for_gemini([ai])
        assert result[0].content == "Hello!"

    def test_ai_message_with_tool_calls_only_unchanged(self):
        """AIMessage with tool_calls but no content passes through untouched."""
        ai = AIMessage(
            content="",
            tool_calls=[
                {"id": "tc-1", "name": "load_skill", "args": {}, "type": "tool_call"}
            ],
        )
        result = normalize_messages_for_gemini([ai])
        assert result[0].content == ""
        assert result[0].tool_calls  # still present

    def test_mixed_ai_message_content_stripped(self):
        """AIMessage with BOTH text content and tool_calls: content is cleared."""
        ai = AIMessage(
            content="I'll load the invoice skill for you.",
            tool_calls=[
                {"id": "tc-1", "name": "load_skill", "args": {}, "type": "tool_call"}
            ],
        )
        result = normalize_messages_for_gemini([ai])
        assert result[0].content == ""
        assert result[0].tool_calls  # tool_calls preserved

    def test_human_and_tool_messages_unchanged(self):
        human = HumanMessage(content="create invoice")
        tool = ToolMessage(content="done", tool_call_id="tc-1", name="create_invoice")
        result = normalize_messages_for_gemini([human, tool])
        assert result == [human, tool]

    def test_full_sequence_normalised(self):
        """Realistic post-summarization sequence: SystemMessage removed, mixed AI cleared."""
        sys = SystemMessage(content="[Context summary] Prior context.")
        human = HumanMessage(content="create an invoice")
        ai_mixed = AIMessage(
            content="Loading skill...",
            tool_calls=[
                {"id": "tc-1", "name": "load_skill", "args": {}, "type": "tool_call"}
            ],
        )
        tool_resp = ToolMessage(
            content="instructions", tool_call_id="tc-1", name="load_skill"
        )

        result = normalize_messages_for_gemini([sys, human, ai_mixed, tool_resp])
        assert len(result) == 3
        assert isinstance(result[0], HumanMessage)
        assert result[1].content == ""  # text stripped
        assert result[1].tool_calls  # tool_calls kept
        assert isinstance(result[2], ToolMessage)
