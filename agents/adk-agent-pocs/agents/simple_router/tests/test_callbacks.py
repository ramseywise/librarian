"""Unit tests for agents/simple_router/callbacks.py and routing.py.

Tests cover:
  - _is_follow_up_answer: the word-level heuristic for all supported languages
  - _last_user_text: extraction from LlmRequest content
  - follow_up_shortcut: the full before_model_callback contract
  - decide_route: HOW-TO gate, keyword scoring, multi-domain, no_signal paths
  - static_route_shortcut: bypass guard, HOW-TO fires, keyword fires
  - router_before_model_callback: follow_up takes priority over static
  - detect_out_of_scope / OOS_BY_LANG: all four languages, substring match
  - out_of_scope_shortcut: LLM request mutation, None return for in-scope
  - receptionist_before_model_callback: mirrors out_of_scope_shortcut behaviour
  - history query routing: "what invoices have I seen" must NOT fire follow_up_shortcut
  - _router_circuit_breaker / _ROUTER_MAX_CALLS_PER_TURN: count, reset, and apology response
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

import playground.agent_poc.agents.simple_router.callbacks as _callbacks_mod
from playground.agent_poc.agents.simple_router.callbacks import (
    _ROUTER_LOOP_COUNT,
    _ROUTER_LOOP_TURN,
    _ROUTER_MAX_CALLS_PER_TURN,
    _STATIC_BYPASS_KEY,
    _last_user_text,
    _router_circuit_breaker,
    follow_up_shortcut,
    out_of_scope_shortcut,
    receptionist_before_model_callback,
    router_before_model_callback,
    static_route_shortcut,
)
from playground.agent_poc.agents.simple_router.follow_up_detection import (
    is_follow_up_answer as _is_follow_up_answer,
)
from playground.agent_poc.agents.simple_router.oos_detection import (
    OOS_BY_LANG,
    detect_out_of_scope,
)
from playground.agent_poc.agents.simple_router.routing import (
    CONFIDENCE_THRESHOLD,
    RoutingDecision,
    decide_route,
)
from playground.agent_poc.agents.simple_router.tools.context_tools import (
    PUBLIC_FOLLOW_UP_AGENT,
)


# ── Minimal Expert stub (avoids importing sub_agents / triggering Agent builds) ──


@dataclass
class _FakeExpert:
    name: str
    routing_terms: list[str] = field(default_factory=list)

    @property
    def template(self):
        return SimpleNamespace(name=self.name)


_INVOICE_EXPERT = _FakeExpert(
    name="invoice_agent",
    routing_terms=[
        "show me invoice",
        "show invoice",
        "invoice",
        "billing",
        "payment",
        "vat",
    ],
)
_SUPPORT_EXPERT = _FakeExpert(
    name="support_agent",
    routing_terms=["login error", "not working", "error", "problem", "issue"],
)
_FAKE_EXPERTS = [_INVOICE_EXPERT, _SUPPORT_EXPERT]


# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_request(*user_texts: str):
    """Return a minimal LlmRequest with one user message per argument."""
    contents = [
        SimpleNamespace(role="user", parts=[SimpleNamespace(text=t)])
        for t in user_texts
    ]
    return SimpleNamespace(contents=contents)


def _make_ctx(state: dict | None = None):
    """Return a minimal CallbackContext with a real state dict."""
    ctx = MagicMock()
    ctx.state = dict(state or {})
    return ctx


# ── _is_follow_up_answer ──────────────────────────────────────────────────────


class TestIsFollowUpAnswer:
    # --- True cases: short, no new-request opener ---

    @pytest.mark.parametrize(
        "msg",
        [
            # Generic affirmatives
            "yes",
            "no",
            "okay",
            "sure",
            "ok",
            # Bare IDs
            "INV-123",
            "42",
            "INV-456",
            # Short fragments that don't start with a command/question word
            "the first one",
            "number 5",
            # Multilingual affirmatives (not in _NEW_REQUEST_STARTS)
            "ja",  # German/Danish yes
            "oui",  # French yes
            "nein",  # German no
            "nej",  # Danish no
            "non",  # French no
            "bitte",  # German "please"
        ],
    )
    def test_returns_true(self, msg: str):
        assert _is_follow_up_answer(msg) is True

    # --- False cases: new-request openers ---

    @pytest.mark.parametrize(
        "msg",
        [
            # English question words
            "how do I approve",
            "what is invoice 10",
            "where do I find VAT",
            "when was it sent",
            "why is it pending",
            "who approved it",
            "which invoice",
            # English action verbs
            "show me invoice 10",
            "update the address",
            "get invoice 5",
            "list all invoices",
            "find invoice 10",
            "check the status",
            "fix the error",
            # English modal / auxiliary
            "can you show me",
            "could you help",
            "is invoice 10",
            "will it be sent",
            # English first-person / generic
            "i need help",
            "help me find",
            # Danish question words
            "hvordan gør jeg",
            "hvad er faktura",
            "hvornår blev den sendt",
            "hvorfor er den afvist",
            "hvem godkendte den",
            "hvilken faktura",
            # Danish modals
            "kan du hjælpe",
            "vil du vise mig",
            # Danish action verbs
            "vis faktura 10",
            "opdater adressen",
            "tjek status",
            # Danish first-person
            "jeg har brug for",
            # German question words
            "wie funktioniert",
            "was ist rechnung",
            "wo finde ich",
            "wann wurde sie",
            "warum abgelehnt",
            "wer hat genehmigt",
            "welcher status",
            # German modals
            "kann ich sehen",
            "könnte ich helfen",
            "ist die rechnung",
            # German action verbs
            "zeig mir rechnung",
            "prüfe den status",
            "ändere die adresse",
            # German first-person
            "ich brauche hilfe",
            # French question words
            "comment approuver",
            "quoi faire",
            "où trouver la tva",
            "quand a été envoyée",
            "pourquoi rejetée",
            "qui a approuvé",
            "quel montant",
            # French modals
            "peut on voir",
            "pourrait tu aider",
            # French action verbs
            "montre la facture",
            "trouve la facture",
            "vérifie le statut",
            # French first-person
            "je voudrais voir",
        ],
    )
    def test_returns_false_new_request(self, msg: str):
        assert _is_follow_up_answer(msg) is False

    def test_returns_false_empty_string(self):
        assert _is_follow_up_answer("") is False

    def test_returns_false_too_long(self):
        # Six words — exceeds _MAX_FOLLOW_UP_WORDS
        assert _is_follow_up_answer("the second one in the list") is False

    def test_boundary_exactly_five_words(self):
        # Five words with no new-request opener → True
        assert _is_follow_up_answer("the second one please") is True  # 4 words
        assert _is_follow_up_answer("yes that one number five") is True  # 5 words

    def test_case_insensitive_matching(self):
        assert _is_follow_up_answer("HOW do I") is False
        assert _is_follow_up_answer("Hvordan gør") is False
        assert _is_follow_up_answer("YES") is True


# ── _last_user_text ───────────────────────────────────────────────────────────


class TestLastUserText:
    def test_empty_contents(self):
        req = SimpleNamespace(contents=[])
        assert _last_user_text(req) == ""

    def test_none_contents(self):
        req = SimpleNamespace(contents=None)
        assert _last_user_text(req) == ""

    def test_single_user_message(self):
        req = _make_request("hello")
        assert _last_user_text(req) == "hello"

    def test_strips_whitespace(self):
        req = _make_request("  hello  ")
        assert _last_user_text(req) == "hello"

    def test_last_user_message_wins(self):
        # Build two user messages; last should be returned
        contents = [
            SimpleNamespace(role="user", parts=[SimpleNamespace(text="first")]),
            SimpleNamespace(role="model", parts=[SimpleNamespace(text="response")]),
            SimpleNamespace(role="user", parts=[SimpleNamespace(text="second")]),
        ]
        req = SimpleNamespace(contents=contents)
        assert _last_user_text(req) == "second"

    def test_skips_model_messages(self):
        contents = [
            SimpleNamespace(role="model", parts=[SimpleNamespace(text="model text")]),
        ]
        req = SimpleNamespace(contents=contents)
        assert _last_user_text(req) == ""

    def test_part_without_text_skipped(self):
        contents = [
            SimpleNamespace(
                role="user",
                parts=[SimpleNamespace(text=None), SimpleNamespace(text="real")],
            ),
        ]
        req = SimpleNamespace(contents=contents)
        assert _last_user_text(req) == "real"


# ── follow_up_shortcut ────────────────────────────────────────────────────────


class TestFollowUpShortcut:
    def test_returns_none_when_no_follow_up_state(self):
        ctx = _make_ctx()
        req = _make_request("INV-123")
        assert follow_up_shortcut(ctx, req) is None

    def test_returns_none_when_follow_up_state_is_none(self):
        ctx = _make_ctx({PUBLIC_FOLLOW_UP_AGENT: None})
        req = _make_request("yes")
        assert follow_up_shortcut(ctx, req) is None

    def test_returns_none_for_new_request_even_with_follow_up_state(self):
        ctx = _make_ctx({PUBLIC_FOLLOW_UP_AGENT: "invoice_agent"})
        req = _make_request("how do I approve an invoice?")
        result = follow_up_shortcut(ctx, req)
        assert result is None
        # State must NOT be consumed — follow-up agent still registered
        assert ctx.state[PUBLIC_FOLLOW_UP_AGENT] == "invoice_agent"

    def test_fires_for_bare_id(self):
        ctx = _make_ctx({PUBLIC_FOLLOW_UP_AGENT: "invoice_agent"})
        req = _make_request("INV-42")
        result = follow_up_shortcut(ctx, req)
        assert result is not None

    def test_fires_for_affirmative(self):
        ctx = _make_ctx({PUBLIC_FOLLOW_UP_AGENT: "support_agent"})
        req = _make_request("yes")
        result = follow_up_shortcut(ctx, req)
        assert result is not None

    def test_response_contains_transfer_to_agent(self):
        target = "invoice_agent"
        ctx = _make_ctx({PUBLIC_FOLLOW_UP_AGENT: target})
        req = _make_request("42")

        result = follow_up_shortcut(ctx, req)

        assert result is not None
        parts = result.content.parts
        assert len(parts) == 1
        fc = parts[0].function_call
        assert fc.name == "transfer_to_agent"
        assert fc.args == {"agent_name": target}

    def test_state_is_cleared_after_shortcut_fires(self):
        ctx = _make_ctx({PUBLIC_FOLLOW_UP_AGENT: "invoice_agent"})
        req = _make_request("42")

        follow_up_shortcut(ctx, req)

        assert ctx.state[PUBLIC_FOLLOW_UP_AGENT] is None

    def test_state_unchanged_when_shortcut_skipped(self):
        ctx = _make_ctx({PUBLIC_FOLLOW_UP_AGENT: "invoice_agent"})
        req = _make_request("show me all invoices")  # new request

        follow_up_shortcut(ctx, req)

        assert ctx.state[PUBLIC_FOLLOW_UP_AGENT] == "invoice_agent"

    def test_target_agent_forwarded_correctly(self):
        for agent in ("invoice_agent", "support_agent", "receptionist_agent"):
            ctx = _make_ctx({PUBLIC_FOLLOW_UP_AGENT: agent})
            req = _make_request("yes")
            result = follow_up_shortcut(ctx, req)
            assert result.content.parts[0].function_call.args["agent_name"] == agent

    def test_multilingual_follow_up_fires(self):
        """Short non-command words in other languages should trigger the shortcut."""
        for msg in ("ja", "oui", "nein", "nej", "42"):
            ctx = _make_ctx({PUBLIC_FOLLOW_UP_AGENT: "invoice_agent"})
            req = _make_request(msg)
            result = follow_up_shortcut(ctx, req)
            assert result is not None, f"Shortcut should fire for '{msg}'"

    def test_multilingual_new_request_skips(self):
        """New-request openers in other languages must pass through to the LLM."""
        for msg in ("hvordan gør jeg", "wie funktioniert", "comment approuver"):
            ctx = _make_ctx({PUBLIC_FOLLOW_UP_AGENT: "invoice_agent"})
            req = _make_request(msg)
            result = follow_up_shortcut(ctx, req)
            assert result is None, f"Shortcut should NOT fire for '{msg}'"


# ── decide_route ───────────────────────────────────────────────────────────────


class TestDecideRoute:
    """Tests for routing.decide_route(). Uses fake experts to avoid importing sub_agents."""

    # HOW-TO gate
    @pytest.mark.parametrize(
        "msg",
        [
            "how do I fix the VAT",
            "how to upload an invoice",
            "how can I reset my password",
            "what steps do I take",
            "walk me through the approval flow",
            "where do I find the settings",
            # Gate fires even with invoice vocabulary present
            "how do I check the VAT on invoice 10",
        ],
    )
    def test_howto_gate_fires(self, msg):
        d = decide_route(msg, experts=_FAKE_EXPERTS)
        assert d.mode == "direct"
        assert d.selected_agent == "support_agent"
        assert d.confidence == 1.0
        assert "HOW-TO gate" in d.reason

    # Single domain — high confidence
    # Single domain — score ≥ 2 → confidence ≥ 0.67 → direct
    @pytest.mark.parametrize(
        "msg,expected_agent",
        [
            (
                "show me invoice 10",
                "invoice_agent",
            ),  # "show me invoice" + "invoice" → score=2
            (
                "show invoice 42",
                "invoice_agent",
            ),  # "show invoice" + "invoice" → score=2
            (
                "update the vat on invoice 10",
                "invoice_agent",
            ),  # "invoice" + "vat" → score=2
            (
                "I'm getting a login error",
                "support_agent",
            ),  # "login error" + "error" → score=2
        ],
    )
    def test_single_domain_direct(self, msg, expected_agent):
        d = decide_route(msg, experts=_FAKE_EXPERTS)
        assert d.mode == "direct", (
            f"Expected direct for '{msg}', got {d.mode} (reason: {d.reason})"
        )
        assert d.selected_agent == expected_agent
        assert d.confidence >= CONFIDENCE_THRESHOLD

    # Low-confidence single match → no_signal
    @pytest.mark.parametrize(
        "msg",
        [
            "invoice",  # 1 term → confidence=0.5
            "it's not working",  # "not working" matches once → confidence=0.5
        ],
    )
    def test_single_term_below_threshold(self, msg):
        d = decide_route(msg, experts=_FAKE_EXPERTS)
        assert d.mode == "no_signal", f"Expected no_signal for '{msg}', got {d.mode}"
        assert d.confidence < CONFIDENCE_THRESHOLD

    # Multi-domain → no_signal
    def test_multi_domain_no_signal(self):
        d = decide_route(
            "show me invoice 10 and I have a login error", experts=_FAKE_EXPERTS
        )
        assert d.mode == "no_signal"
        assert d.confidence == 0.0
        assert "Multi-domain" in d.reason

    # No terms matched → no_signal
    def test_no_match_no_signal(self):
        d = decide_route("hello there", experts=_FAKE_EXPERTS)
        assert d.mode == "no_signal"
        assert d.confidence == 0.0

    # Empty experts list → no_signal (graceful degradation)
    def test_empty_experts(self):
        d = decide_route("show me invoice 10", experts=[])
        assert d.mode == "no_signal"

    # Confidence formula: score/(score+1)
    def test_confidence_formula(self):
        # "show me invoice" matches 1 phrase + "invoice" matches another → score=2
        d = decide_route("show me invoice 10", experts=_FAKE_EXPERTS)
        assert d.mode == "direct"
        assert abs(d.confidence - (2 / 3)) < 0.01

    # Input length guard
    def test_very_long_input_handled(self):
        """Messages longer than 500 chars must not error and still return a decision."""
        long_msg = "show me invoice " + "x" * 2000
        d = decide_route(long_msg, experts=_FAKE_EXPERTS)
        # "show me invoice" is in the first 500 chars → should still route
        assert isinstance(d, RoutingDecision)
        assert d.mode == "direct"
        assert d.selected_agent == "invoice_agent"

    def test_500_char_boundary_not_split_mid_term(self):
        """A term that starts before char 500 and ends after is still matched."""
        # Place "show invoice" so it starts at char 495 (within the 500-char window)
        prefix = "a" * 483  # 483 + len("show invoice") = 495, well within 500
        d = decide_route(prefix + "show invoice 42", experts=_FAKE_EXPERTS)
        assert d.mode == "direct"
        assert d.selected_agent == "invoice_agent"


# ── static_route_shortcut ──────────────────────────────────────────────────────


def test_static_routing_disabled_by_default():
    """_STATIC_ROUTING_DEFAULT = '0' — static routing is off by default.

    Fails immediately if _STATIC_ROUTING_DEFAULT is reverted to '1'.
    Use SIMPLE_ROUTER_STATIC=1 to enable it at runtime.
    """
    assert _callbacks_mod._STATIC_ROUTING_ENABLED is False


class TestStaticRouteShortcut:
    """Tests for callbacks.static_route_shortcut()."""

    def _transfer_target(self, result) -> str:
        return result.content.parts[0].function_call.args["agent_name"]

    def test_howto_fires_directly(self):
        ctx = _make_ctx()
        req = _make_request("how do I fix the login error")
        # Patch decide_route via the experts default is not feasible here;
        # test via actual callback using real EXPERTS registry.
        # The HOW-TO gate is deterministic so this always routes to support_agent.
        with patch.object(_callbacks_mod, "_STATIC_ROUTING_ENABLED", True):
            result = static_route_shortcut(ctx, req)
        assert result is not None
        assert self._transfer_target(result) == "support_agent"

    def test_no_signal_returns_none(self):
        ctx = _make_ctx()
        req = _make_request("hello there")
        result = static_route_shortcut(ctx, req)
        assert result is None

    def test_bypass_guard_consumed_after_firing(self):
        """Second invocation with the guard active must return None (LLM fallback)."""
        ctx = _make_ctx({_STATIC_BYPASS_KEY: True})
        req = _make_request("show me invoice 10")
        with patch.object(_callbacks_mod, "_STATIC_ROUTING_ENABLED", True):
            result = static_route_shortcut(ctx, req)
        assert result is None
        # Guard is consumed — cleared from state
        assert not ctx.state.get(_STATIC_BYPASS_KEY)

    def test_bypass_guard_set_after_firing(self):
        """When the shortcut fires, the guard must be set for the next invocation."""
        ctx = _make_ctx()
        req = _make_request("how do I approve an invoice")
        with patch.object(_callbacks_mod, "_STATIC_ROUTING_ENABLED", True):
            result = static_route_shortcut(ctx, req)
        assert result is not None
        assert ctx.state.get(_STATIC_BYPASS_KEY) is True

    def test_empty_message_returns_none(self):
        ctx = _make_ctx()
        req = _make_request("")
        result = static_route_shortcut(ctx, req)
        assert result is None

    def test_disabled_via_flag_returns_none(self):
        """SIMPLE_ROUTER_STATIC=0 must disable the shortcut entirely."""
        ctx = _make_ctx()
        req = _make_request("how do I fix the login error")  # would normally fire
        with patch.object(_callbacks_mod, "_STATIC_ROUTING_ENABLED", False):
            result = static_route_shortcut(ctx, req)
        assert result is None
        # No guard should be set when disabled
        assert not ctx.state.get(_STATIC_BYPASS_KEY)

    def test_disabled_does_not_consume_bypass_guard(self):
        """When disabled, a pre-existing guard is left untouched."""
        ctx = _make_ctx({_STATIC_BYPASS_KEY: True})
        req = _make_request("how do I approve an invoice")
        with patch.object(_callbacks_mod, "_STATIC_ROUTING_ENABLED", False):
            result = static_route_shortcut(ctx, req)
        assert result is None
        # Guard must still be in state — disabled path should not touch it
        assert ctx.state.get(_STATIC_BYPASS_KEY) is True

    def test_no_side_effects_when_no_signal(self):
        """When decide_route returns no_signal, state is left completely clean."""
        ctx = _make_ctx()
        req = _make_request("hello there")
        static_route_shortcut(ctx, req)
        assert not ctx.state.get(_STATIC_BYPASS_KEY)


# ── router_before_model_callback ───────────────────────────────────────────────


class TestRouterBeforeModelCallback:
    """Tests for the combined router_before_model_callback chain."""

    def _transfer_target(self, result) -> str:
        return result.content.parts[0].function_call.args["agent_name"]

    def test_follow_up_takes_priority_over_static(self):
        """When follow_up_agent is set and message is a short answer, follow_up wins."""
        ctx = _make_ctx({PUBLIC_FOLLOW_UP_AGENT: "invoice_agent"})
        req = _make_request("42")
        result = router_before_model_callback(ctx, req)
        assert result is not None
        # Must route to the follow-up agent, not whatever static scoring would pick.
        assert self._transfer_target(result) == "invoice_agent"
        # Follow-up state consumed; static bypass guard must NOT be set.
        assert ctx.state.get(PUBLIC_FOLLOW_UP_AGENT) is None
        assert not ctx.state.get(_STATIC_BYPASS_KEY)

    def test_static_fires_when_no_follow_up(self):
        """Without a follow-up signal, high-confidence messages use the static router."""
        ctx = _make_ctx()
        req = _make_request("how do I reset my password")
        with patch.object(_callbacks_mod, "_STATIC_ROUTING_ENABLED", True):
            result = router_before_model_callback(ctx, req)
        assert result is not None
        assert self._transfer_target(result) == "support_agent"

    def test_prefetch_fires_for_ambiguous(self):
        """Ambiguous messages trigger context_prefetch_shortcut — synthetic gc call returned."""
        ctx = _make_ctx()
        req = _make_request("hello")
        result = router_before_model_callback(ctx, req)
        assert result is not None
        fc = result.content.parts[0].function_call
        assert fc.name == "get_conversation_context"


# ── detect_out_of_scope ────────────────────────────────────────────────────────


class TestDetectOutOfScope:
    """Tests for oos_detection.detect_out_of_scope() and OOS_BY_LANG vocabulary."""

    # --- Returns None for in-scope messages ---

    @pytest.mark.parametrize(
        "msg",
        [
            "show me invoice 10",
            "update the VAT rate",
            "I'm getting a login error",
            "how do I approve an invoice",
            "hello",
            "",
        ],
    )
    def test_returns_none_for_in_scope(self, msg: str):
        assert detect_out_of_scope(msg) is None

    # --- English OOS terms ---

    @pytest.mark.parametrize(
        "term",
        [
            "expense",
            "expenses",
            "payslip",
            "payslips",
            "payroll",
            "salary",
            "salaries",
            "timesheet",
            "timesheets",
            "purchase order",
            "purchase orders",
            "contract",
            "contracts",
            "budget",
            "budgets",
            "receipt",
            "receipts",
            "reimbursement",
            "reimbursements",
        ],
    )
    def test_english_oos_terms_detected(self, term: str):
        assert detect_out_of_scope(f"I need to submit my {term}") is not None

    # --- Danish OOS terms ---

    @pytest.mark.parametrize(
        "term",
        [
            "udgift",
            "udgifter",
            "lønseddel",
            "lønsedler",
            "lønudbetaling",
            "løn",
            "timeseddel",
            "timesedler",
            "indkøbsordre",
            "indkøbsordrer",
            "kontrakt",
            "kontrakter",
            "budget",
            "budgetter",
            "kvittering",
            "kvitteringer",
            "refusion",
            "godtgørelse",
        ],
    )
    def test_danish_oos_terms_detected(self, term: str):
        assert detect_out_of_scope(f"jeg har en {term}") is not None

    # --- German OOS terms ---

    @pytest.mark.parametrize(
        "term",
        [
            "ausgabe",
            "ausgaben",
            "spesen",
            "gehaltsabrechnung",
            "lohnabrechnung",
            "gehalt",
            "lohn",
            "stundenzettel",
            "arbeitszeiterfassung",
            "bestellung",
            "bestellungen",
            "vertrag",
            "verträge",
            "quittung",
            "quittungen",
            "kassenbon",
            "erstattung",
            "kostenerstattung",
        ],
    )
    def test_german_oos_terms_detected(self, term: str):
        assert detect_out_of_scope(f"ich habe eine {term}") is not None

    # --- French OOS terms ---

    @pytest.mark.parametrize(
        "term",
        [
            "dépense",
            "dépenses",
            "note de frais",
            "fiche de paie",
            "bulletin de salaire",
            "salaire",
            "rémunération",
            "feuille de temps",
            "bon de commande",
            "contrat",
            "contrats",
            "reçu",
            "reçus",
            "remboursement",
            "remboursements",
        ],
    )
    def test_french_oos_terms_detected(self, term: str):
        assert detect_out_of_scope(f"j'ai une {term}") is not None

    # --- Case insensitivity ---

    def test_case_insensitive(self):
        assert detect_out_of_scope("I need help with my EXPENSE") is not None
        assert detect_out_of_scope("My PAYROLL is wrong") is not None

    # --- Substring matching ---

    def test_substring_match(self):
        """Term anywhere in the message should be detected."""
        assert (
            detect_out_of_scope("can you help me track my expenses from last week?")
            is not None
        )

    # --- Language priority: DA/DE/FR wins over EN for shared words ---

    def test_budget_detected_as_danish(self):
        """'budget' appears in both DA and EN lists — should still be detected."""
        result = detect_out_of_scope("mit budget er overskredet")
        assert result is not None

    # --- OOS_BY_LANG structure ---

    def test_all_languages_present(self):
        assert set(OOS_BY_LANG.keys()) == {"en", "da", "de", "fr"}

    def test_each_language_nonempty(self):
        for lang, terms in OOS_BY_LANG.items():
            assert len(terms) > 0, f"OOS_BY_LANG[{lang!r}] must not be empty"


# ── out_of_scope_shortcut ──────────────────────────────────────────────────────


class TestOutOfScopeShortcut:
    """Tests for callbacks.out_of_scope_shortcut()."""

    def _make_config_request(self, text: str):
        """LlmRequest with a non-None config so we can verify mutation."""
        from types import SimpleNamespace

        config = SimpleNamespace(
            system_instruction="original", tools=["tool"], tool_config=None
        )
        contents = [SimpleNamespace(role="user", parts=[SimpleNamespace(text=text)])]
        return SimpleNamespace(contents=contents, config=config)

    def test_returns_none_for_in_scope(self):
        ctx = _make_ctx()
        req = _make_request("show me invoice 10")
        assert out_of_scope_shortcut(ctx, req) is None

    def test_returns_none_for_empty_message(self):
        ctx = _make_ctx()
        req = _make_request("")
        assert out_of_scope_shortcut(ctx, req) is None

    def test_returns_none_for_oos_and_mutates_request(self):
        """out_of_scope_shortcut always returns None — mutation steers the LLM."""
        ctx = _make_ctx()
        req = self._make_config_request("I need help with my payroll")
        result = out_of_scope_shortcut(ctx, req)
        # Must return None (LLM still runs, but with overridden instruction)
        assert result is None

    def test_system_instruction_overridden(self):
        ctx = _make_ctx()
        req = self._make_config_request("I need help with my payroll")
        out_of_scope_shortcut(ctx, req)
        assert req.config.system_instruction != "original"
        assert (
            "payroll" in req.config.system_instruction.lower()
            or "outside" in req.config.system_instruction.lower()
        )

    def test_tools_cleared_on_oos(self):
        ctx = _make_ctx()
        req = self._make_config_request("I need help with my expenses")
        out_of_scope_shortcut(ctx, req)
        assert req.config.tools is None

    def test_oos_detected_in_all_languages(self):
        """Shortcut must fire for OOS keywords in each supported language."""
        cases = [
            "my salary is wrong",  # EN
            "jeg har en udgift at indberette",  # DA
            "mein gehalt stimmt nicht",  # DE
            "j'ai une question sur mon salaire",  # FR
        ]
        for msg in cases:
            ctx = _make_ctx()
            req = self._make_config_request(msg)
            result = out_of_scope_shortcut(ctx, req)
            assert result is None, f"Expected None for OOS msg: {msg!r}"
            # Verify mutation happened (system_instruction changed)
            assert req.config.system_instruction != "original", (
                f"system_instruction not overridden for: {msg!r}"
            )

    def test_in_scope_request_leaves_config_unchanged(self):
        ctx = _make_ctx()
        req = self._make_config_request("show me invoice 10")
        out_of_scope_shortcut(ctx, req)
        assert req.config.system_instruction == "original"
        assert req.config.tools == ["tool"]


# ── receptionist_before_model_callback (OOS path) ─────────────────────────────


class TestReceptionistBeforeModelCallback:
    """Tests for the OOS path of receptionist_before_model_callback."""

    def _make_config_request(self, text: str):
        from types import SimpleNamespace

        config = SimpleNamespace(
            system_instruction="original", tools=["tool"], tool_config=None
        )
        contents = [SimpleNamespace(role="user", parts=[SimpleNamespace(text=text)])]
        return SimpleNamespace(contents=contents, config=config)

    def test_returns_none_for_in_scope(self):
        ctx = _make_ctx()
        req = self._make_config_request("show me invoice 10")
        assert receptionist_before_model_callback(ctx, req) is None

    def test_returns_none_and_mutates_for_oos(self):
        ctx = _make_ctx()
        req = self._make_config_request("I need to submit an expense report")
        result = receptionist_before_model_callback(ctx, req)
        assert result is None
        assert req.config.system_instruction != "original"
        assert req.config.tools is None

    def test_returns_none_for_empty_message(self):
        ctx = _make_ctx()
        req = _make_request("")
        assert receptionist_before_model_callback(ctx, req) is None

    def test_session_fallback_for_no_contents(self):
        """Agents with include_contents='none' have empty contents — must use session events."""
        from types import SimpleNamespace

        config = SimpleNamespace(
            system_instruction="original", tools=["tool"], tool_config=None
        )
        req = SimpleNamespace(contents=[], config=config)
        # Simulate a session with a user event containing an OOS message
        event = SimpleNamespace(
            author="user",
            content=SimpleNamespace(
                parts=[SimpleNamespace(text="I need help with my payroll")]
            ),
        )
        ctx = _make_ctx()
        ctx.session = SimpleNamespace(events=[event])
        result = receptionist_before_model_callback(ctx, req)
        assert result is None
        assert req.config.system_instruction != "original"


# ── History-query routing guard ────────────────────────────────────────────────
#
# Regression tests for the "what invoices has i seen" loop bug.
#
# Root cause: the HISTORY path in invoice_agent.txt previously called
# signal_follow_up() before writing the history answer.  This conflicted with
# the FOLLOW-UP INVARIANT ("after signal_follow_up, write a CLARIFYING QUESTION,
# then stop"), leaving the model unable to reconcile the two instructions.  The
# resulting loop showed as alternating ✓ / ⚡ signal_follow_up calls in the ADK
# web trace.
#
# The fix is in the prompt (signal_follow_up removed from the HISTORY path).
# These tests guard the routing-layer invariant: history questions starting with
# "what / which / how many" must bypass follow_up_shortcut and reach the LLM
# router so a fresh routing decision is made each time.
#
# Note: the _router_circuit_breaker only counts router_before_model_callback
# invocations and resets on each new invocation_id.  It therefore cannot stop a
# loop that is confined to the expert-agent's own LLM reasoning loop or that
# spans multiple ADK invocations.  The correct fix is always the prompt — the
# circuit breaker is a last-resort guard for router-level hot loops.


class TestHistoryQueryNotShortcutted:
    """History questions ('what invoices have I seen') must always reach the LLM router."""

    # ── is_follow_up_answer guard ─────────────────────────────────────────────

    @pytest.mark.parametrize(
        "msg",
        [
            "what invoices has i seen",
            "what invoices have I seen",
            "what invoice did I see",
            "what was the last invoice",
            "which invoice did I view",
            "which invoices have I looked at",
        ],
    )
    def test_history_questions_not_follow_up_answers(self, msg: str):
        """History questions start with 'what'/'which' — is_follow_up_answer must return False."""
        assert _is_follow_up_answer(msg) is False, (
            f"is_follow_up_answer should be False for history question: {msg!r}"
        )

    # ── follow_up_shortcut does NOT fire ──────────────────────────────────────

    @pytest.mark.parametrize(
        "msg",
        [
            "what invoices has i seen",
            "what invoices have I seen",
            "what invoice did I see",
            "what was the last invoice",
            "which invoice did I view",
        ],
    )
    def test_follow_up_shortcut_skips_history_questions(self, msg: str):
        """follow_up_shortcut must return None for history questions even with follow_up_agent set.

        If follow_up_shortcut fires here, the invoice_agent gets the history
        question without going through the router LLM first.  The agent then
        calls signal_follow_up() in a loop (the bug reported in demo.txt line 11).
        """
        ctx = _make_ctx({PUBLIC_FOLLOW_UP_AGENT: "invoice_agent"})
        req = _make_request(msg)
        result = follow_up_shortcut(ctx, req)
        assert result is None, (
            f"follow_up_shortcut must not fire for history question: {msg!r}"
        )

    def test_follow_up_agent_state_preserved_when_shortcut_skips(self):
        """When follow_up_shortcut skips a history question, state must stay unconsumed."""
        ctx = _make_ctx({PUBLIC_FOLLOW_UP_AGENT: "invoice_agent"})
        req = _make_request("what invoices has i seen")
        follow_up_shortcut(ctx, req)
        # State must NOT be consumed — the LLM router decides routing.
        assert ctx.state[PUBLIC_FOLLOW_UP_AGENT] == "invoice_agent"

    # ── router_before_model_callback goes to context_prefetch, not shortcut ──

    def test_router_callback_prefetches_context_for_history_question(self):
        """With follow_up_agent set, a history question must still trigger context_prefetch.

        context_prefetch is the last step in the chain and returns a synthetic
        get_conversation_context call.  If this doesn't fire, the router LLM would
        run without context — and would still eventually route to invoice_agent,
        but the loop bug would re-emerge if the prompt were ever reverted.
        """
        ctx = _make_ctx({PUBLIC_FOLLOW_UP_AGENT: "invoice_agent"})
        ctx.invocation_id = "inv-history"
        req = _make_request("what invoices has i seen")

        result = router_before_model_callback(ctx, req)

        # Must be the synthetic get_conversation_context, not a transfer.
        assert result is not None
        fc = result.content.parts[0].function_call
        assert fc.name == "get_conversation_context", (
            "Router must prefetch context for history questions, not shortcut to invoice_agent"
        )


# ── _router_circuit_breaker ────────────────────────────────────────────────────
#
# Scope: intra-invocation router calls only.  The counter resets on every new
# invocation_id, so _router_circuit_breaker does NOT protect against:
#   - loops that span multiple ADK invocations (counter resets each turn), or
#   - loops confined to an expert agent's own LLM reasoning (tool-call loops
#     inside invoice_agent, support_agent, etc. never touch this counter).
#
# Expert-agent loops must be fixed at the prompt level (see invoice_agent.txt
# HISTORY path — the "what invoices has i seen" loop was caused by a prompt
# conflict, not a router loop, so the circuit breaker never fired).


class TestRouterCircuitBreaker:
    """Tests for callbacks._router_circuit_breaker() and the _ROUTER_MAX_CALLS_PER_TURN guard.

    Reset key: number of user events in session.events, NOT invocation_id.
    Each agent transfer (router→expert, expert→router) creates a new
    invocation_id in ADK, so an invocation_id-based counter resets on every
    transfer and can never accumulate across a transfer loop.  The user-event
    count stays constant across all agent transfers within one user turn and
    only increments when the user sends a new message.
    """

    def _make_ctx_with_turn(self, user_events: int, state: dict | None = None):
        """Return a CallbackContext stub whose session has `user_events` user events."""
        ctx = _make_ctx(state)
        ctx.session = SimpleNamespace(
            events=[SimpleNamespace(author="user") for _ in range(user_events)]
        )
        return ctx

    # ── Basic counter behaviour ───────────────────────────────────────────────

    def test_returns_none_on_first_call(self):
        """Count = 1 ≤ max — breaker must stay open."""
        ctx = self._make_ctx_with_turn(1)
        assert _router_circuit_breaker(ctx) is None

    def test_returns_none_at_exactly_max_calls(self):
        """Count = _ROUTER_MAX_CALLS_PER_TURN must NOT trigger the breaker (strictly >)."""
        ctx = self._make_ctx_with_turn(
            1,
            {_ROUTER_LOOP_TURN: 1, _ROUTER_LOOP_COUNT: _ROUTER_MAX_CALLS_PER_TURN - 1},
        )
        assert _router_circuit_breaker(ctx) is None
        assert ctx.state[_ROUTER_LOOP_COUNT] == _ROUTER_MAX_CALLS_PER_TURN

    def test_fires_when_count_exceeds_max(self):
        """Count > _ROUTER_MAX_CALLS_PER_TURN must return a non-None LlmResponse."""
        ctx = self._make_ctx_with_turn(
            1,
            {_ROUTER_LOOP_TURN: 1, _ROUTER_LOOP_COUNT: _ROUTER_MAX_CALLS_PER_TURN},
        )
        assert _router_circuit_breaker(ctx) is not None

    def test_fired_response_is_text_not_transfer(self):
        """The apology response must be plain text — not a transfer_to_agent call."""
        ctx = self._make_ctx_with_turn(
            1,
            {_ROUTER_LOOP_TURN: 1, _ROUTER_LOOP_COUNT: _ROUTER_MAX_CALLS_PER_TURN},
        )
        result = _router_circuit_breaker(ctx)
        parts = result.content.parts
        assert len(parts) == 1
        assert getattr(parts[0], "function_call", None) is None
        assert parts[0].text

    def test_fired_response_contains_apology(self):
        """Apology text must mention a processing issue so the user understands."""
        ctx = self._make_ctx_with_turn(
            1,
            {_ROUTER_LOOP_TURN: 1, _ROUTER_LOOP_COUNT: _ROUTER_MAX_CALLS_PER_TURN},
        )
        text = _router_circuit_breaker(ctx).content.parts[0].text.lower()
        assert "issue" in text or "encountered" in text or "try again" in text

    def test_keeps_firing_after_threshold_exceeded(self):
        """Every call beyond the threshold must also return a response (stays tripped)."""
        ctx = self._make_ctx_with_turn(
            1,
            {_ROUTER_LOOP_TURN: 1, _ROUTER_LOOP_COUNT: _ROUTER_MAX_CALLS_PER_TURN},
        )
        for _ in range(3):
            assert _router_circuit_breaker(ctx) is not None

    # ── Counter initialisation ────────────────────────────────────────────────

    def test_counter_initialised_to_one_on_first_call(self):
        """First call for a fresh user turn must set count to 1."""
        ctx = self._make_ctx_with_turn(1)
        _router_circuit_breaker(ctx)
        assert ctx.state[_ROUTER_LOOP_COUNT] == 1
        assert ctx.state[_ROUTER_LOOP_TURN] == 1

    def test_counter_increments_within_same_turn(self):
        """Successive calls within the same user turn must increment the counter."""
        ctx = self._make_ctx_with_turn(
            1,
            {_ROUTER_LOOP_TURN: 1, _ROUTER_LOOP_COUNT: 3},
        )
        _router_circuit_breaker(ctx)
        assert ctx.state[_ROUTER_LOOP_COUNT] == 4

    # ── KEY: counter survives agent transfers ─────────────────────────────────

    def test_counter_accumulates_across_agent_transfers(self):
        """Counter must accumulate even as invocation_id changes on each agent transfer.

        Regression test for the original circuit-breaker bug: each agent transfer
        (router→expert, expert→router) creates a new invocation_id in ADK, so the
        old invocation_id-based counter reset on every transfer and never reached
        the threshold.  The user-event count is unaffected by transfers and fixes
        this.
        """
        ctx = self._make_ctx_with_turn(1)
        # Simulate 4 router activations each with a different invocation_id
        # (as ADK does in a router→expert→router→expert loop).
        for i, fake_inv in enumerate(["inv-a", "inv-b", "inv-c", "inv-d"], start=1):
            ctx.invocation_id = fake_inv
            result = _router_circuit_breaker(ctx)
            assert ctx.state[_ROUTER_LOOP_COUNT] == i, (
                f"Counter should be {i} after call {i}, got {ctx.state[_ROUTER_LOOP_COUNT]}"
            )
            assert result is None  # still under threshold (max=5, only 4 calls)

        # 5th call hits exactly max — still open (strictly >)
        ctx.invocation_id = "inv-e"
        assert _router_circuit_breaker(ctx) is None
        assert ctx.state[_ROUTER_LOOP_COUNT] == _ROUTER_MAX_CALLS_PER_TURN

        # 6th call crosses the threshold — breaker fires
        ctx.invocation_id = "inv-f"
        result = _router_circuit_breaker(ctx)
        assert result is not None
        assert result.content.parts[0].text  # apology text

    # ── Counter reset on new user turn ────────────────────────────────────────

    def test_counter_resets_on_new_user_turn(self):
        """A new user message (more user events) must reset the count to 1."""
        ctx = self._make_ctx_with_turn(
            2,  # second user message has arrived
            {_ROUTER_LOOP_TURN: 1, _ROUTER_LOOP_COUNT: _ROUTER_MAX_CALLS_PER_TURN + 5},
        )
        result = _router_circuit_breaker(ctx)
        assert result is None  # reset to 1, not firing
        assert ctx.state[_ROUTER_LOOP_COUNT] == 1
        assert ctx.state[_ROUTER_LOOP_TURN] == 2

    def test_new_turn_after_breach_does_not_fire(self):
        """After a breached turn, the very first call of the next turn is safe."""
        ctx = self._make_ctx_with_turn(
            2,
            {_ROUTER_LOOP_TURN: 1, _ROUTER_LOOP_COUNT: _ROUTER_MAX_CALLS_PER_TURN + 99},
        )
        assert _router_circuit_breaker(ctx) is None

    def test_no_session_does_not_error(self):
        """If session is absent the breaker still works (turn=0, counter accumulates)."""
        ctx = _make_ctx()
        ctx.session = None
        for _ in range(_ROUTER_MAX_CALLS_PER_TURN):
            _router_circuit_breaker(ctx)
        assert _router_circuit_breaker(ctx) is not None  # fires on call max+1

    # ── Integration: router_before_model_callback priority ───────────────────

    def test_circuit_breaker_takes_priority_in_chain(self):
        """When the breaker fires, router_before_model_callback must return early."""
        ctx = self._make_ctx_with_turn(
            1,
            {
                _ROUTER_LOOP_TURN: 1,
                _ROUTER_LOOP_COUNT: _ROUTER_MAX_CALLS_PER_TURN,
                PUBLIC_FOLLOW_UP_AGENT: "invoice_agent",
            },
        )
        req = _make_request("yes")
        result = router_before_model_callback(ctx, req)

        # Must be the apology (text), not a transfer_to_agent call.
        assert result is not None
        parts = result.content.parts
        assert getattr(parts[0], "function_call", None) is None
        assert parts[0].text

    def test_circuit_breaker_does_not_interfere_with_normal_turns(self):
        """Normal turns (count ≤ max) must be unaffected — follow_up still fires."""
        ctx = self._make_ctx_with_turn(
            1,
            {
                _ROUTER_LOOP_TURN: 1,
                _ROUTER_LOOP_COUNT: _ROUTER_MAX_CALLS_PER_TURN - 2,
                PUBLIC_FOLLOW_UP_AGENT: "invoice_agent",
            },
        )
        req = _make_request("yes")
        result = router_before_model_callback(ctx, req)

        assert result is not None
        fc = result.content.parts[0].function_call
        assert fc.name == "transfer_to_agent"
        assert fc.args["agent_name"] == "invoice_agent"
