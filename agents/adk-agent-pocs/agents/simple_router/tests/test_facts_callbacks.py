"""Unit tests for _facts_callbacks.py and the new context_tools (set_fact, search_facts,
get_latest_fact).

Tests cover:
  - inject_facts_callback: injects facts as synthetic get_conversation_context
    function_call/response pair into contents (NOT into the system instruction),
    double-injection guard, preserves follow_up_agent, early persistence
  - persist_facts_callback: draft→persisted, history appended, fact_id stamped,
    supersedes_fact_id set for previously-persisted keys
  - set_fact: writes to session_facts with draft status, carries forward fact_id
  - search_facts: session-only, history-only, both, excludes superseded entries
  - get_latest_fact: session hit, history fallback, not-found case
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock


from playground.agent_poc.agents.simple_router._facts_callbacks import (
    inject_facts_callback,
    persist_facts_callback,
)
from playground.agent_poc.agents.simple_router.tools.context_tools import (
    PUBLIC_FACT_HISTORY,
    PUBLIC_FOLLOW_UP_AGENT,
    PUBLIC_SESSION_FACTS,
    get_latest_fact,
    search_facts,
    set_fact,
)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_ctx(state: dict | None = None):
    ctx = MagicMock()
    ctx.state = dict(state or {})
    return ctx


def _make_llm_request(system_instruction: str | None = None, contents=None):
    """Build a minimal LlmRequest with an optional system instruction and contents."""
    config = SimpleNamespace(system_instruction=system_instruction)
    return SimpleNamespace(contents=list(contents or []), config=config)


def _user_text(text: str):
    """Minimal content object representing a user text message."""
    part = SimpleNamespace(text=text, function_call=None, function_response=None)
    return SimpleNamespace(role="user", parts=[part])


def _find_injected_facts(req):
    """Return the injected [session facts: ...] content item, or None."""
    for c in req.contents:
        for p in getattr(c, "parts", []):
            text = getattr(p, "text", None)
            if text and text.startswith("[session facts:"):
                return c
    return None


def _get_facts_dict(req):
    """Parse the injected facts dict from the [session facts:] message, or None."""
    import json

    for c in req.contents:
        for p in getattr(c, "parts", []):
            text = getattr(p, "text", None)
            if text and text.startswith("[session facts:"):
                return json.loads(text[len("[session facts: ") : -1])
    return None


def _make_tool_ctx(state: dict | None = None, agent_name: str = "invoice_agent"):
    ctx = MagicMock()
    ctx.state = dict(state or {})
    ctx.agent_name = agent_name
    return ctx


# ── inject_facts_callback ─────────────────────────────────────────────────────


class TestInjectFactsCallback:
    def test_injects_session_facts_message(self):
        ctx = _make_ctx(
            {
                PUBLIC_SESSION_FACTS: {
                    "invoice_id": {
                        "status": "draft",
                        "description": "ID",
                        "value": "INV-42",
                        "fact_id": None,
                    }
                }
            }
        )
        req = _make_llm_request(
            system_instruction="You are an invoice expert.",
            contents=[_user_text("show me invoice 42")],
        )
        inject_facts_callback(ctx, req)
        facts = _get_facts_dict(req)
        assert facts is not None, "expected [session facts:] message"
        assert facts["invoice_id"] == {
            "description": "ID",
            "value": "INV-42",
            "previous": [],
        }

    def test_facts_injected_at_end(self):
        """[session facts:] is always appended at the very end of contents.

        Injecting after the last real user message (old approach) broke Gemini's
        thought_signature validation when a model thought+function_call block
        followed the user message in the same invocation.
        """
        user_msg = _user_text("show me invoice 42")
        req = _make_llm_request(contents=[user_msg])
        inject_facts_callback(_make_ctx(), req)
        # contents: [user_msg, session_facts_msg]
        assert len(req.contents) == 2
        assert req.contents[0] is user_msg
        assert _find_injected_facts(req) is req.contents[-1]

    def test_system_instruction_is_not_modified(self):
        """SI stays unchanged — prefix cache is preserved."""
        original_si = "You are an invoice expert."
        req = _make_llm_request(
            system_instruction=original_si,
            contents=[_user_text("hi")],
        )
        inject_facts_callback(_make_ctx(), req)
        assert req.config.system_instruction == original_si

    def test_empty_facts_injects_empty_dict(self):
        req = _make_llm_request(contents=[_user_text("hi")])
        inject_facts_callback(_make_ctx(), req)
        facts = _get_facts_dict(req)
        assert facts is not None
        # _summary key is always present; no domain keys when session_facts is empty.
        assert set(facts.keys()) == {"_summary"}

    def test_no_invocation_guard_re_injects_on_second_call(self):
        """No invocation guard: each callback call injects fresh facts.

        In production, strip_tool_history_callback always runs before inject, so
        the prior [session facts:] is stripped before each LLM call. inject then
        re-injects fresh facts — no accumulation. The guard was removed because it
        caused facts to be missing on the second LLM call of a multi-step tool sequence.
        """
        ctx = _make_ctx()
        ctx.invocation_id = "inv-123"
        req = _make_llm_request(contents=[_user_text("show me invoice")])
        inject_facts_callback(ctx, req)
        assert len(req.contents) == 2  # user_msg + facts
        # Second call without stripping — injects again (strip would remove the old one first).
        inject_facts_callback(ctx, req)
        assert (
            len(req.contents) == 3
        )  # user_msg + facts + facts (strip handles dedup in prod)

    def test_preserves_follow_up_agent(self):
        # inject_facts_callback intentionally does NOT clear PUBLIC_FOLLOW_UP_AGENT.
        ctx = _make_ctx({PUBLIC_FOLLOW_UP_AGENT: "invoice_agent"})
        req = _make_llm_request(contents=[_user_text("hi")])
        inject_facts_callback(ctx, req)
        assert ctx.state[PUBLIC_FOLLOW_UP_AGENT] == "invoice_agent"

    def test_no_contents_injects_at_end(self):
        """With no user message, [session facts:] is appended at the end."""
        req = _make_llm_request()
        inject_facts_callback(_make_ctx(), req)
        assert _find_injected_facts(req) is not None

    def test_early_persistence_persist_now_flag(self):
        ctx = _make_ctx(
            {
                PUBLIC_SESSION_FACTS: {
                    "invoice_id": {
                        "status": "draft",
                        "description": "Invoice ID",
                        "value": "INV-99",
                        "fact_id": None,
                        "persist_now": True,
                    }
                }
            }
        )
        req = _make_llm_request(contents=[_user_text("hi")])
        inject_facts_callback(ctx, req)
        session_facts = ctx.state[PUBLIC_SESSION_FACTS]
        assert session_facts["invoice_id"]["status"] == "persisted"
        assert session_facts["invoice_id"]["fact_id"] is not None
        history = ctx.state[PUBLIC_FACT_HISTORY]
        assert len(history) == 1
        assert history[0]["fact"] == "INV-99"

    def test_returns_none(self):
        result = inject_facts_callback(_make_ctx(), _make_llm_request())
        assert result is None


# ── persist_facts_callback ────────────────────────────────────────────────────


class TestPersistFactsCallback:
    def test_moves_draft_to_history(self):
        ctx = _make_ctx(
            {
                PUBLIC_SESSION_FACTS: {
                    "invoice_id": {
                        "status": "draft",
                        "description": "Invoice ID",
                        "value": "INV-5",
                        "fact_id": None,
                    }
                }
            }
        )
        result = persist_facts_callback(ctx)
        assert result is None
        session_facts = ctx.state[PUBLIC_SESSION_FACTS]
        assert session_facts["invoice_id"]["status"] == "persisted"
        history = ctx.state[PUBLIC_FACT_HISTORY]
        assert len(history) == 1
        assert history[0]["fact"] == "INV-5"
        assert history[0]["description"] == "Invoice ID"

    def test_stamps_fact_id_on_session_entry(self):
        ctx = _make_ctx(
            {
                PUBLIC_SESSION_FACTS: {
                    "x": {
                        "status": "draft",
                        "description": "x",
                        "value": "val",
                        "fact_id": None,
                    }
                }
            }
        )
        persist_facts_callback(ctx)
        fact_id = ctx.state[PUBLIC_SESSION_FACTS]["x"]["fact_id"]
        assert fact_id is not None
        assert ctx.state[PUBLIC_FACT_HISTORY][0]["fact_id"] == fact_id

    def test_supersedes_fact_id_for_update(self):
        """When a fact_id already exists (prior persistence), new entry supersedes it."""
        old_id = "old-uuid"
        ctx = _make_ctx(
            {
                PUBLIC_SESSION_FACTS: {
                    "invoice_id": {
                        "status": "draft",
                        "description": "Invoice ID",
                        "value": "INV-6",
                        "fact_id": old_id,
                    }
                },
                PUBLIC_FACT_HISTORY: [
                    {
                        "fact_id": old_id,
                        "supersedes_fact_id": None,
                        "description": "Invoice ID",
                        "fact": "INV-5",
                    }
                ],
            }
        )
        persist_facts_callback(ctx)
        history = ctx.state[PUBLIC_FACT_HISTORY]
        assert len(history) == 2
        new_entry = history[1]
        assert new_entry["supersedes_fact_id"] == old_id
        assert new_entry["fact"] == "INV-6"

    def test_already_persisted_facts_are_skipped(self):
        ctx = _make_ctx(
            {
                PUBLIC_SESSION_FACTS: {
                    "x": {
                        "status": "persisted",
                        "description": "x",
                        "value": "val",
                        "fact_id": "some-id",
                    }
                }
            }
        )
        persist_facts_callback(ctx)
        history = ctx.state.get(PUBLIC_FACT_HISTORY, [])
        assert len(history) == 0

    def test_multiple_drafts_all_persisted(self):
        ctx = _make_ctx(
            {
                PUBLIC_SESSION_FACTS: {
                    "a": {
                        "status": "draft",
                        "description": "a",
                        "value": "1",
                        "fact_id": None,
                    },
                    "b": {
                        "status": "draft",
                        "description": "b",
                        "value": "2",
                        "fact_id": None,
                    },
                }
            }
        )
        persist_facts_callback(ctx)
        assert len(ctx.state[PUBLIC_FACT_HISTORY]) == 2
        assert ctx.state[PUBLIC_SESSION_FACTS]["a"]["status"] == "persisted"
        assert ctx.state[PUBLIC_SESSION_FACTS]["b"]["status"] == "persisted"


# ── set_fact ──────────────────────────────────────────────────────────────────


class TestSetFact:
    def test_writes_draft_to_session_facts(self):
        tc = _make_tool_ctx()
        set_fact("invoice_id", "INV-1", "Invoice ID", tc)
        facts = tc.state[PUBLIC_SESSION_FACTS]
        assert facts["invoice_id"]["status"] == "draft"
        assert facts["invoice_id"]["value"] == "INV-1"
        assert facts["invoice_id"]["description"] == "Invoice ID"

    def test_carries_forward_existing_fact_id(self):
        existing_id = "existing-id"
        tc = _make_tool_ctx(
            {
                PUBLIC_SESSION_FACTS: {
                    "invoice_id": {
                        "status": "persisted",
                        "description": "X",
                        "value": "INV-0",
                        "fact_id": existing_id,
                    }
                }
            }
        )
        set_fact("invoice_id", "INV-1", "Invoice ID", tc)
        facts = tc.state[PUBLIC_SESSION_FACTS]
        assert facts["invoice_id"]["fact_id"] == existing_id
        assert facts["invoice_id"]["status"] == "draft"

    def test_returns_noted_status(self):
        tc = _make_tool_ctx()
        result = set_fact("invoice_id", "INV-7", "Invoice ID", tc)
        assert result["status"] == "noted"
        assert result["invoice_id"] == "INV-7"

    def test_new_key_has_none_fact_id(self):
        tc = _make_tool_ctx()
        set_fact("vendor_name", "Acme", "Vendor name", tc)
        assert tc.state[PUBLIC_SESSION_FACTS]["vendor_name"]["fact_id"] is None


# ── search_facts ──────────────────────────────────────────────────────────────


class TestSearchFacts:
    def _make_tc(self, session=None, history=None):
        state = {}
        if session:
            state[PUBLIC_SESSION_FACTS] = session
        if history:
            state[PUBLIC_FACT_HISTORY] = history
        return _make_tool_ctx(state)

    def test_session_search_finds_by_key(self):
        tc = self._make_tc(
            session={
                "invoice_id": {
                    "status": "draft",
                    "description": "Invoice ID",
                    "value": "INV-1",
                    "fact_id": None,
                }
            }
        )
        result = search_facts("invoice", "session", tc)
        assert result["count"] == 1
        assert result["results"][0]["key"] == "invoice_id"

    def test_session_search_finds_by_value(self):
        tc = self._make_tc(
            session={
                "status": {
                    "status": "draft",
                    "description": "Status",
                    "value": "draft",
                    "fact_id": None,
                }
            }
        )
        result = search_facts("draft", "session", tc)
        assert result["count"] == 1

    def test_history_search_excludes_superseded(self):
        history = [
            {
                "fact_id": "id1",
                "supersedes_fact_id": None,
                "description": "Invoice ID",
                "fact": "INV-1",
            },
            {
                "fact_id": "id2",
                "supersedes_fact_id": "id1",
                "description": "Invoice ID",
                "fact": "INV-2",
            },
        ]
        tc = self._make_tc(history=history)
        result = search_facts("Invoice ID", "history", tc)
        assert result["count"] == 1
        assert result["results"][0]["fact"] == "INV-2"

    def test_both_searches_session_and_history(self):
        tc = self._make_tc(
            session={
                "x": {
                    "status": "draft",
                    "description": "x fact",
                    "value": "hello",
                    "fact_id": None,
                }
            },
            history=[
                {
                    "fact_id": "h1",
                    "supersedes_fact_id": None,
                    "description": "y fact",
                    "fact": "world",
                }
            ],
        )
        result = search_facts("fact", "both", tc)
        sources = {r["source"] for r in result["results"]}
        assert "session" in sources
        assert "history" in sources

    def test_empty_results(self):
        tc = self._make_tc()
        result = search_facts("nonexistent", "both", tc)
        assert result["count"] == 0
        assert result["results"] == []


# ── get_latest_fact ───────────────────────────────────────────────────────────


class TestGetLatestFact:
    def test_session_hit(self):
        tc = _make_tool_ctx(
            {
                PUBLIC_SESSION_FACTS: {
                    "invoice_id": {
                        "status": "persisted",
                        "description": "Invoice ID",
                        "value": "INV-9",
                        "fact_id": "f1",
                    }
                }
            }
        )
        result = get_latest_fact("invoice_id", tc)
        assert result["found"] is True
        assert result["source"] == "session"
        assert result["value"] == "INV-9"

    def test_history_fallback(self):
        tc = _make_tool_ctx(
            {
                PUBLIC_FACT_HISTORY: [
                    {
                        "fact_id": "f1",
                        "supersedes_fact_id": None,
                        "description": "invoice_id",
                        "fact": "INV-3",
                    }
                ]
            }
        )
        result = get_latest_fact("invoice_id", tc)
        assert result["found"] is True
        assert result["source"] == "history"
        assert result["fact"] == "INV-3"

    def test_history_returns_latest_not_superseded(self):
        tc = _make_tool_ctx(
            {
                PUBLIC_FACT_HISTORY: [
                    {
                        "fact_id": "f1",
                        "supersedes_fact_id": None,
                        "description": "invoice_id",
                        "fact": "INV-1",
                    },
                    {
                        "fact_id": "f2",
                        "supersedes_fact_id": "f1",
                        "description": "invoice_id",
                        "fact": "INV-2",
                    },
                ]
            }
        )
        result = get_latest_fact("invoice_id", tc)
        assert result["found"] is True
        assert result["fact"] == "INV-2"

    def test_not_found(self):
        tc = _make_tool_ctx()
        result = get_latest_fact("missing_key", tc)
        assert result["found"] is False
        assert result["key"] == "missing_key"
