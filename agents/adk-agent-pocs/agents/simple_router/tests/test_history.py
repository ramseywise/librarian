"""Unit tests for strip_tool_history_callback in _history.py.

Tests cover the thought/thought_signature stripping added in Pass 2 to allow
thinking models to run without producing orphaned thought_signature values in
replayed history.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from playground.agent_poc.agents.simple_router._history import (
    strip_tool_history_callback,
)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_ctx():
    return MagicMock()


def _make_llm_request(contents):
    req = SimpleNamespace(contents=list(contents))
    return req


def _user(text: str):
    part = SimpleNamespace(
        text=text,
        function_call=None,
        function_response=None,
        thought=None,
        thought_signature=None,
    )
    return SimpleNamespace(role="user", parts=[part])


def _model_text(text: str):
    part = SimpleNamespace(
        text=text,
        function_call=None,
        function_response=None,
        thought=None,
        thought_signature=None,
    )
    return SimpleNamespace(role="model", parts=[part])


def _model_with_thought(thought_text: str = "reasoning", fc=None):
    """Model content with a thought part and optional function_call part."""
    thought_part = SimpleNamespace(
        text=thought_text,
        function_call=None,
        function_response=None,
        thought=True,
        thought_signature=None,
    )
    parts = [thought_part]
    if fc is not None:
        fc_part = SimpleNamespace(
            text=None,
            function_call=fc,
            function_response=None,
            thought=None,
            thought_signature=None,
        )
        parts.append(fc_part)
    return SimpleNamespace(role="model", parts=parts)


def _model_with_thought_signature(sig: bytes = b"sig"):
    """Model content with a thought_signature part (compacted form)."""
    part = SimpleNamespace(
        text=None,
        function_call=None,
        function_response=None,
        thought=None,
        thought_signature=sig,
    )
    return SimpleNamespace(role="model", parts=[part])


# ── Tests ─────────────────────────────────────────────────────────────────────


class TestStripThoughtParts:
    def test_strips_thought_parts_from_prior_turns(self):
        """A prior-turn model content with thought=True part is removed."""
        prior_thought = _model_with_thought("I should look at invoice 42")
        prior_user = _user("show me invoice 1")
        current_user = _user("now show invoice 2")

        req = _make_llm_request([prior_user, prior_thought, current_user])
        strip_tool_history_callback(_make_ctx(), req)

        # The thought-only model content should be gone; current user turn preserved
        roles_and_texts = [
            (c.role, getattr(c.parts[0], "text", None)) for c in req.contents
        ]
        assert ("model", "I should look at invoice 42") not in roles_and_texts
        assert any(
            c.role == "user" and "invoice 2" in (c.parts[0].text or "")
            for c in req.contents
        )

    def test_strips_thought_signature_parts_from_prior_turns(self):
        """A prior-turn model content with thought_signature=b'sig' part is removed."""
        prior_user = _user("first turn")
        prior_sig = _model_with_thought_signature(b"opaque-sig")
        current_user = _user("second turn")

        req = _make_llm_request([prior_user, prior_sig, current_user])
        strip_tool_history_callback(_make_ctx(), req)

        for c in req.contents:
            for p in c.parts:
                assert not getattr(p, "thought_signature", None), (
                    "thought_signature part should have been stripped from prior turn"
                )

    def test_preserves_current_turn_thought_parts(self):
        """A thought part in the current turn (at or after last_real_idx) is NOT stripped."""
        prior_user = _user("previous question")
        prior_model = _model_text("previous answer")
        current_user = _user("current question")
        current_thought = _model_with_thought("thinking about current question")

        req = _make_llm_request(
            [prior_user, prior_model, current_user, current_thought]
        )
        strip_tool_history_callback(_make_ctx(), req)

        # current_thought is at/after last_real_idx — must survive
        thought_found = any(
            getattr(p, "thought", None) for c in req.contents for p in c.parts
        )
        assert thought_found, "current-turn thought part should be preserved"

    def test_strips_function_call_and_thought_together(self):
        """A prior-turn model content with both function_call and thought parts is fully removed."""
        fc = SimpleNamespace(name="get_invoice", args={})
        prior_user = _user("first turn")
        prior_mixed = _model_with_thought("need to call tool", fc=fc)
        current_user = _user("second turn")

        req = _make_llm_request([prior_user, prior_mixed, current_user])
        strip_tool_history_callback(_make_ctx(), req)

        for c in req.contents:
            for p in c.parts:
                assert not getattr(p, "function_call", None), (
                    "function_call part should be stripped"
                )
                assert not getattr(p, "thought", None), (
                    "thought part should be stripped"
                )

    def test_preserves_text_part_with_thought_signature_from_prior_turns(self):
        """A prior-turn model Part with both text AND thought_signature must be kept.

        In Gemini thinking mode the model's final text response after a tool call
        can carry thought_signature on the same Part as the text.  Stripping it
        would erase the agent's clarifying question from history, causing a
        signal_follow_up loop on the next turn.
        """
        prior_user = _user("show me an invoice")
        # Simulates the model's text response that also carries thought_signature.
        text_with_sig_part = SimpleNamespace(
            text="Which invoice would you like to see? Please provide the invoice ID.",
            function_call=None,
            function_response=None,
            thought=None,
            thought_signature=b"opaque-sig",
        )
        prior_model = SimpleNamespace(role="model", parts=[text_with_sig_part])
        current_user = _user("10")

        req = _make_llm_request([prior_user, prior_model, current_user])
        strip_tool_history_callback(_make_ctx(), req)

        texts = [
            p.text for c in req.contents for p in c.parts if getattr(p, "text", None)
        ]
        assert (
            "Which invoice would you like to see? Please provide the invoice ID."
            in texts
        ), "Prior-turn text part with thought_signature must be preserved in history"

    def test_no_change_when_no_thought_parts(self):
        """Plain text parts in prior turns are preserved unchanged."""
        prior_user = _user("first turn")
        prior_model = _model_text("plain answer")
        current_user = _user("second turn")

        req = _make_llm_request([prior_user, prior_model, current_user])
        strip_tool_history_callback(_make_ctx(), req)

        texts = [
            p.text for c in req.contents for p in c.parts if getattr(p, "text", None)
        ]
        assert "plain answer" in texts, "plain text model part should be preserved"
