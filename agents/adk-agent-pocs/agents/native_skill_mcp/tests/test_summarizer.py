"""Tests for summarizer_node.py — pruning helpers, should_summarize, format_messages, _safe_overlap."""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from langgraph_agents.native_skill_mcp.nodes.summarizer_node import (
    COMPACTION_INTERVAL,
    OVERLAP_SIZE,
    _count_active,
    _is_pruned,
    _safe_overlap,
    format_messages_for_summary,
    should_summarize,
)
from langgraph_agents.native_skill_mcp.state import AgentState


# ── _is_pruned ────────────────────────────────────────────────────────────────


class TestIsPruned:
    def test_pruned_tool_message(self):
        msg = ToolMessage(content="[pruned]", tool_call_id="tc-1")
        assert _is_pruned(msg) is True

    def test_normal_tool_message(self):
        msg = ToolMessage(content="some result", tool_call_id="tc-1")
        assert _is_pruned(msg) is False

    def test_human_message(self):
        assert _is_pruned(HumanMessage(content="[pruned]")) is False

    def test_ai_message(self):
        assert _is_pruned(AIMessage(content="[pruned]")) is False

    def test_system_message(self):
        assert _is_pruned(SystemMessage(content="[pruned]")) is False


# ── _count_active ─────────────────────────────────────────────────────────────


class TestCountActive:
    def test_empty(self):
        assert _count_active([]) == 0

    def test_all_active(self):
        msgs = [
            HumanMessage(content="hello"),
            AIMessage(content="hi"),
            ToolMessage(content="result", tool_call_id="tc-1"),
        ]
        assert _count_active(msgs) == 3

    def test_excludes_pruned(self):
        msgs = [
            HumanMessage(content="hello"),
            ToolMessage(content="[pruned]", tool_call_id="tc-1"),
            AIMessage(content="answer"),
        ]
        assert _count_active(msgs) == 2

    def test_all_pruned(self):
        msgs = [
            ToolMessage(content="[pruned]", tool_call_id="tc-1"),
            ToolMessage(content="[pruned]", tool_call_id="tc-2"),
        ]
        assert _count_active(msgs) == 0


# ── should_summarize ──────────────────────────────────────────────────────────


class TestShouldSummarize:
    def _state(self, n_active: int, n_pruned: int = 0) -> AgentState:
        msgs = [HumanMessage(content=f"msg {i}") for i in range(n_active)]
        msgs += [
            ToolMessage(content="[pruned]", tool_call_id=f"tc-{i}")
            for i in range(n_pruned)
        ]
        return AgentState(messages=msgs, activated_skills=[], summary="")

    def test_below_interval_returns_agent(self):
        state = self._state(COMPACTION_INTERVAL - 1)
        assert should_summarize(state) == "agent"

    def test_at_interval_returns_summarize(self):
        state = self._state(COMPACTION_INTERVAL)
        assert should_summarize(state) == "summarize"

    def test_above_interval_returns_summarize(self):
        state = self._state(COMPACTION_INTERVAL + 5)
        assert should_summarize(state) == "summarize"

    def test_pruned_messages_not_counted(self):
        """Pruned messages don't count toward the compaction threshold."""
        state = self._state(n_active=COMPACTION_INTERVAL - 1, n_pruned=100)
        assert should_summarize(state) == "agent"

    def test_constants(self):
        assert COMPACTION_INTERVAL == 8
        assert OVERLAP_SIZE == 4


# ── format_messages_for_summary ───────────────────────────────────────────────


class TestFormatMessagesForSummary:
    def test_human_message(self):
        result = format_messages_for_summary([HumanMessage(content="hello")])
        assert "[user]: hello" in result

    def test_ai_message_text(self):
        result = format_messages_for_summary([AIMessage(content="I can help")])
        assert "[assistant]: I can help" in result

    def test_ai_message_with_tool_calls(self):
        ai = AIMessage(
            content="",
            tool_calls=[
                {"id": "tc-1", "name": "list_invoices", "args": {}, "type": "tool_call"}
            ],
        )
        result = format_messages_for_summary([ai])
        assert "list_invoices" in result
        assert "[assistant tool_call" in result

    def test_tool_message(self):
        tool = ToolMessage(
            content="invoice list", tool_call_id="tc-1", name="list_invoices"
        )
        result = format_messages_for_summary([tool])
        assert "list_invoices" in result
        assert "invoice list" in result

    def test_pruned_tool_message_shown_as_pruned(self):
        tool = ToolMessage(
            content="[pruned]", tool_call_id="tc-1", name="fetch_support_knowledge"
        )
        result = format_messages_for_summary([tool])
        assert "(pruned)" in result

    def test_system_message(self):
        result = format_messages_for_summary([SystemMessage(content="You are Billy")])
        assert "[system]: You are Billy" in result

    def test_multiple_messages_separated_by_newline(self):
        msgs = [
            HumanMessage(content="q1"),
            AIMessage(content="a1"),
        ]
        result = format_messages_for_summary(msgs)
        lines = result.splitlines()
        assert len(lines) == 2
        assert "[user]: q1" in lines[0]
        assert "[assistant]: a1" in lines[1]

    def test_empty_messages(self):
        assert format_messages_for_summary([]) == ""


# ── _safe_overlap ─────────────────────────────────────────────────────────────


def _tm(name: str = "tool") -> ToolMessage:
    return ToolMessage(content="result", tool_call_id="tc", name=name)


def _ai(tool_names: list[str] | None = None) -> AIMessage:
    if tool_names:
        return AIMessage(
            content="",
            tool_calls=[
                {"id": f"tc-{n}", "name": n, "args": {}, "type": "tool_call"}
                for n in tool_names
            ],
        )
    return AIMessage(content="response")


def _human(text: str = "hi") -> HumanMessage:
    return HumanMessage(content=text)


class TestSafeOverlap:
    def test_short_list_returns_no_summary(self):
        """Lists ≤ OVERLAP_SIZE: nothing to summarize."""
        msgs = [_human(), _ai(), _tm()]
        to_summarize, to_keep = _safe_overlap(msgs, OVERLAP_SIZE)
        assert to_summarize == []
        assert to_keep == msgs

    def test_clean_boundary_unchanged(self):
        """When the last-N slice already starts at a HumanMessage, no adjustment."""
        msgs = [_human("q1"), _ai(), _tm(), _human("q2"), _ai(), _tm(), _ai(), _tm()]
        # With OVERLAP_SIZE=4: raw to_keep = msgs[-4:] = [_human("q2"), ...]
        to_summarize, to_keep = _safe_overlap(msgs, 4)
        assert isinstance(to_keep[0], HumanMessage)
        assert to_keep[0].content == "q2"
        assert len(to_summarize) + len(to_keep) == len(msgs)

    def test_broken_boundary_prepends_human(self):
        """Root-cause scenario: to_keep starts with ToolMessage, not HumanMessage.

        8 messages: Human + AI(3 loads) + TM×3 + AI(list) + TM×2 reduced to 8.
        Last 4 = [TM(prod), AI(list), TM(c), TM(p)] — starts with ToolMessage.
        _safe_overlap should prepend the HumanMessage.
        """
        human = _human("create invoice")
        ai_loads = _ai(["load_invoice", "load_customer", "load_product"])
        tm_inv = _tm("load_invoice")
        tm_cust = _tm("load_customer")
        tm_prod = _tm("load_product")
        ai_list = _ai(["list_customers", "list_products"])
        tm_lc = _tm("list_customers")
        tm_lp = _tm("list_products")
        msgs = [human, ai_loads, tm_inv, tm_cust, tm_prod, ai_list, tm_lc, tm_lp]

        to_summarize, to_keep = _safe_overlap(msgs, 4)
        assert isinstance(to_keep[0], HumanMessage), (
            "to_keep must start with HumanMessage"
        )
        assert to_keep[0] is human
        # to_summarize + to_keep covers all original messages
        assert len(to_summarize) + len(to_keep) == len(msgs)
        # HumanMessage NOT in to_summarize
        assert not any(isinstance(m, HumanMessage) for m in to_summarize)

    def test_to_keep_starts_with_ai_also_fixed(self):
        """to_keep starting with AIMessage (not ToolMessage) is also fixed."""
        human = _human("q")
        ai1 = _ai(["tool_a"])
        tm1 = _tm("tool_a")
        ai2 = _ai(["tool_b"])
        tm2 = _tm("tool_b")
        msgs = [human, ai1, tm1, ai2, tm2]
        # OVERLAP_SIZE=4 → raw to_keep = [tm1, ai2, tm2, ?] — wait, len=5, overlap=4
        # to_keep = msgs[-4:] = [ai1, tm1, ai2, tm2] — starts with ai1, not Human
        # Actually: msgs[-4:] = [tm1, ai2, tm2] + ??? No, msgs has 5 items
        # to_keep = [ai1, tm1, ai2, tm2] — starts with AIMessage
        to_summarize, to_keep = _safe_overlap(msgs, 4)
        assert isinstance(to_keep[0], HumanMessage)
        assert to_keep[0] is human

    def test_no_human_message_fallback(self):
        """If there's no HumanMessage, the raw slice is kept as-is (graceful degradation)."""
        msgs = [_ai(), _tm(), _ai(), _tm(), _ai(), _tm(), _ai(), _tm()]
        to_summarize, to_keep = _safe_overlap(msgs, 4)
        # No HumanMessage anywhere → raw slice unchanged
        assert len(to_keep) == 4
        assert len(to_summarize) == 4
