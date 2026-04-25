"""Unit tests for agents/simple_router/expert_registry.py.

Tests cover:
  - HOWTO_TRIGGERS: non-empty, all pre-lowercased
  - get_direct: raises KeyError for unknown expert name
"""

from __future__ import annotations

import pytest

from playground.agent_poc.agents.simple_router.expert_registry import (
    HOWTO_TRIGGERS,
    get_direct,
)


class TestHowtoTriggers:
    def test_nonempty(self):
        assert len(HOWTO_TRIGGERS) > 0, "HOWTO_TRIGGERS must not be empty"

    def test_all_lowercase(self):
        """Triggers must be pre-lowercased so routing.py can compare directly."""
        for trigger in HOWTO_TRIGGERS:
            assert trigger == trigger.lower(), (
                f"Trigger {trigger!r} is not lowercase — "
                "pre-lowercasing in expert_registry.py may have been removed"
            )

    def test_known_triggers_present(self):
        """Smoke-check that expected phrases survive the parse."""
        expected = {"how do i", "how to", "how can i", "where do i"}
        assert expected.issubset(set(HOWTO_TRIGGERS)), (
            f"Expected triggers missing from HOWTO_TRIGGERS: "
            f"{expected - set(HOWTO_TRIGGERS)}"
        )


class TestGetDirect:
    def test_unknown_name_raises_key_error(self):
        with pytest.raises(KeyError, match="nonexistent_agent"):
            get_direct("nonexistent_agent")

    def test_known_name_returns_agent(self):
        """invoice_agent and support_agent are registered at import time."""
        from playground.agent_poc.agents.simple_router.expert_registry import EXPERTS

        for expert in EXPERTS:
            name = expert.template.name
            agent = get_direct(name)
            assert agent.name == name
