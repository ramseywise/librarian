"""Tests for root-agent helper functions and the shared out-of-domain tool.

These tests exercise the pure logic in agent.py and sub_agents/shared_tools.py
without starting an LLM session. ADK context objects are replaced with small
fakes that expose only the attributes the functions actually touch.
"""

# pylint: disable=no-self-use,too-few-public-methods

from playground.agent_poc.agents.billy_assistant.agent import (
    clear_tried_agents,
    provide_router_instruction,
)
from playground.agent_poc.agents.billy_assistant.sub_agents.shared_tools import (
    report_out_of_domain,
)


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


class _FakeState(dict):
    """dict subclass so both .get() and [] assignment work like real state."""


class _FakeReadonlyContext:
    """Minimal stand-in for ReadonlyContext used by provide_router_instruction."""

    def __init__(self, tried_agents: list):
        state = _FakeState()
        if tried_agents:
            state["tried_agents"] = tried_agents

        class _Session:
            pass

        session = _Session()
        session.state = state

        class _InvocationContext:
            pass

        ic = _InvocationContext()
        ic.session = session
        self._invocation_context = ic


class _FakeCallbackContext:
    """Minimal stand-in for CallbackContext used by clear_tried_agents."""

    def __init__(self, initial: list | None = None, invocation_id: str = "inv_001"):
        self.state = _FakeState()
        if initial is not None:
            self.state["tried_agents"] = initial

        class _InvocationContext:
            pass

        ic = _InvocationContext()
        ic.invocation_id = invocation_id
        self._invocation_context = ic


class _FakeToolContext:
    """Minimal stand-in for ToolContext used by report_out_of_domain."""

    def __init__(self, agent_name: str, tried_agents: list | None = None):
        self.state = _FakeState()
        if tried_agents is not None:
            self.state["tried_agents"] = tried_agents

        class _Agent:
            pass

        agent = _Agent()
        agent.name = agent_name

        class _InvocationContext:
            pass

        ic = _InvocationContext()
        ic.agent = agent
        self._invocation_context = ic

        class _Actions:
            transfer_to_agent: str | None = None

        self.actions = _Actions()


# ---------------------------------------------------------------------------
# provide_router_instruction
# ---------------------------------------------------------------------------


class TestProvideRouterInstruction:
    """Tests for the dynamic router instruction callable."""

    def test_returns_empty_string_when_no_tried_agents(self):
        """No tried agents → empty string (no extra turn content added)."""
        ctx = _FakeReadonlyContext(tried_agents=[])
        assert provide_router_instruction(ctx) == ""

    def test_returns_empty_string_when_key_absent(self):
        """Missing key in state is treated the same as an empty list."""
        ctx = _FakeReadonlyContext(tried_agents=[])
        ctx._invocation_context.session.state.pop("tried_agents", None)
        assert provide_router_instruction(ctx) == ""

    def test_names_single_tried_agent(self):
        """A single tried agent name appears in the returned directive."""
        ctx = _FakeReadonlyContext(tried_agents=["invoice_agent"])
        result = provide_router_instruction(ctx)
        assert "invoice_agent" in result

    def test_names_multiple_tried_agents(self):
        """All tried agent names are present in the directive."""
        ctx = _FakeReadonlyContext(tried_agents=["invoice_agent", "customer_agent"])
        result = provide_router_instruction(ctx)
        assert "invoice_agent" in result
        assert "customer_agent" in result

    def test_directive_tells_router_not_to_reroute(self):
        """The returned string explicitly instructs the router to skip tried agents."""
        ctx = _FakeReadonlyContext(tried_agents=["support_agent"])
        result = provide_router_instruction(ctx)
        assert "do not route" in result.lower()


# ---------------------------------------------------------------------------
# clear_tried_agents
# ---------------------------------------------------------------------------


class TestClearTriedAgents:
    """Tests for the before_agent_callback that resets tried_agents each turn."""

    def test_clears_existing_list(self):
        """A populated tried_agents list is reset to empty."""
        ctx = _FakeCallbackContext(initial=["invoice_agent", "support_agent"])
        clear_tried_agents(ctx)
        assert ctx.state["tried_agents"] == []

    def test_sets_key_when_absent(self):
        """The key is created even if it did not previously exist."""
        ctx = _FakeCallbackContext(initial=None)
        clear_tried_agents(ctx)
        assert ctx.state["tried_agents"] == []

    def test_idempotent_on_empty_list(self):
        """Calling clear on an already-empty list is a no-op."""
        ctx = _FakeCallbackContext(initial=[])
        clear_tried_agents(ctx)
        assert ctx.state["tried_agents"] == []


# ---------------------------------------------------------------------------
# report_out_of_domain
# ---------------------------------------------------------------------------


class TestReportOutOfDomain:
    """Tests for the shared subagent tool that registers a declined agent."""

    def test_appends_agent_name_to_empty_state(self):
        """First call registers the agent in an empty state."""
        ctx = _FakeToolContext(agent_name="invoice_agent")
        report_out_of_domain(ctx)
        assert "invoice_agent" in ctx.state["tried_agents"]

    def test_appends_to_existing_list(self):
        """Subsequent call from a different agent extends the list."""
        ctx = _FakeToolContext(
            agent_name="customer_agent", tried_agents=["invoice_agent"]
        )
        report_out_of_domain(ctx)
        assert ctx.state["tried_agents"] == ["invoice_agent", "customer_agent"]

    def test_does_not_duplicate_agent_name(self):
        """Calling the tool twice for the same agent does not create a duplicate."""
        ctx = _FakeToolContext(
            agent_name="product_agent", tried_agents=["product_agent"]
        )
        report_out_of_domain(ctx)
        assert ctx.state["tried_agents"].count("product_agent") == 1

    def test_returns_string_mentioning_agent_name(self):
        """The return value confirms which agent was registered."""
        ctx = _FakeToolContext(agent_name="email_agent")
        result = report_out_of_domain(ctx)
        assert "email_agent" in result

    def test_original_list_not_mutated(self):
        """The existing list is replaced, not mutated in place (safe for ADK state)."""
        original = ["invoice_agent"]
        ctx = _FakeToolContext(agent_name="support_agent", tried_agents=original)
        report_out_of_domain(ctx)
        assert original == ["invoice_agent"]  # original list unchanged
