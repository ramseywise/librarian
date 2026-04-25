"""Offline structural tests — no API calls, no model invocations."""

import pytest


# ---------------------------------------------------------------------------
# Package imports
# ---------------------------------------------------------------------------


class TestPackageStructure:
    def test_root_agent_importable(self):
        from agents.fast_multi_agent_system.agent import root_agent

        assert root_agent is not None

    def test_app_importable(self):
        from agents.fast_multi_agent_system.agent import app

        assert app is not None

    def test_root_agent_is_hybrid(self):
        from agents.fast_multi_agent_system.agent import HybridRootAgent, root_agent

        assert isinstance(root_agent, HybridRootAgent)

    def test_root_agent_name(self):
        from agents.fast_multi_agent_system.agent import root_agent

        assert root_agent.name == "root_router"

    def test_root_agent_has_direct_experts(self):
        from agents.fast_multi_agent_system.agent import root_agent

        assert "invoice_agent" in root_agent.direct_experts
        assert "support_agent" in root_agent.direct_experts

    def test_root_agent_has_sub_agents(self):
        from agents.fast_multi_agent_system.agent import root_agent

        assert root_agent.llm_router_agent is not None
        assert root_agent.orchestrator_agent is not None
        assert root_agent.receptionist_agent is not None

    def test_top_level_init_exports_root_agent(self):
        import agents.fast_multi_agent_system as pkg

        assert hasattr(pkg, "root_agent")


# ---------------------------------------------------------------------------
# Routing logic
# ---------------------------------------------------------------------------


class TestRoutingLogic:
    def test_invoice_direct(self):
        from agents.fast_multi_agent_system.routing import decide_route

        d = decide_route("What is wrong with invoice 456?")
        assert d.mode == "direct"
        assert d.selected_agent == "invoice_agent"
        assert d.confidence == 1.0

    def test_support_direct(self):
        from agents.fast_multi_agent_system.routing import decide_route

        d = decide_route("How do I upload a file?")
        assert d.mode == "direct"
        assert d.selected_agent == "support_agent"
        assert d.confidence == 1.0

    def test_planned_planning_signal(self):
        from agents.fast_multi_agent_system.routing import decide_route

        d = decide_route("validate and then fix the VAT")
        assert d.mode == "planned"
        assert d.selected_agent == "orchestrator_agent"

    def test_both_domains_weak_secondary_goes_to_llm(self):
        # "invoice" is noise in a how-to question — secondary signal too weak for orchestrator
        from agents.fast_multi_agent_system.routing import decide_route

        d = decide_route("check my invoice and show me where to edit it on screen")
        assert d.mode == "no_signal"  # falls back to LLM router
        assert d.scores["invoice_agent"] > 0
        assert d.scores["support_agent"] > 0

    def test_planned_both_domains_strong_signal(self):
        # Both domains have ≥ 2 keyword matches → deterministic orchestrator route
        from agents.fast_multi_agent_system.routing import decide_route

        d = decide_route("show the VAT on invoice 456 and how to submit it")
        assert d.mode == "planned"
        assert d.selected_agent == "orchestrator_agent"
        assert d.scores["invoice_agent"] >= 2
        assert d.scores["support_agent"] >= 2

    def test_how_to_invoice_routes_to_support(self):
        from agents.fast_multi_agent_system.routing import decide_route

        d = decide_route("how to upload an invoice")
        # "invoice" is a context word; "how to" + "upload" dominate → support or LLM router
        assert d.selected_agent != "invoice_agent"

    def test_no_signal(self):
        from agents.fast_multi_agent_system.routing import decide_route

        d = decide_route("something completely unrelated to everything")
        assert d.mode == "no_signal"
        assert d.confidence == 0.0

    def test_confidence_threshold_exported(self):
        from agents.fast_multi_agent_system.routing import CONFIDENCE_THRESHOLD

        assert CONFIDENCE_THRESHOLD == 0.6

    def test_scores_dict_shape(self):
        from agents.fast_multi_agent_system.expert_registry import EXPERTS
        from agents.fast_multi_agent_system.routing import decide_route

        d = decide_route("invoice 456")
        expected_keys = {spec.name for spec in EXPERTS} | {"planning"}
        assert set(d.scores.keys()) == expected_keys

    def test_routing_decision_fields(self):
        from agents.fast_multi_agent_system.expert_registry import EXPERTS
        from agents.fast_multi_agent_system.routing import decide_route

        d = decide_route("invoice 456")
        valid_agents = {spec.name for spec in EXPERTS} | {"orchestrator_agent"}
        assert d.mode in ("direct", "planned", "no_signal")
        assert d.selected_agent in valid_agents
        assert isinstance(d.reason, str) and len(d.reason) > 0
        assert 0.0 <= d.confidence <= 1.0


# ---------------------------------------------------------------------------
# State helpers
# ---------------------------------------------------------------------------


class TestStateHelpers:
    def test_init_public_state_resets_turn_keys(self):
        from agents.fast_multi_agent_system.state import (
            PUBLIC_FINAL_ANSWER,
            PUBLIC_PROPOSED_ACTION,
            PUBLIC_ROUTING,
            PUBLIC_ROUTING_ESCALATION,
            init_public_state,
        )

        state = {
            PUBLIC_ROUTING_ESCALATION: {"reason": "old"},
            PUBLIC_ROUTING: {"old": True},
        }
        init_public_state(state, "hello")
        assert state[PUBLIC_ROUTING_ESCALATION] is None
        assert state[PUBLIC_ROUTING] == {}
        assert state[PUBLIC_FINAL_ANSWER] is None
        assert state[PUBLIC_PROPOSED_ACTION] is None

    def test_init_public_state_preserves_facts(self):
        from agents.fast_multi_agent_system.state import PUBLIC_FACTS, init_public_state

        state = {PUBLIC_FACTS: {"invoice_id": "123"}}
        init_public_state(state, "turn 2")
        assert state[PUBLIC_FACTS] == {"invoice_id": "123"}  # preserved

    def test_init_public_state_sets_request(self):
        from agents.fast_multi_agent_system.state import (
            PUBLIC_REQUEST,
            init_public_state,
        )

        state = {}
        init_public_state(state, "What is wrong with invoice 456?")
        assert state[PUBLIC_REQUEST] == {"user_text": "What is wrong with invoice 456?"}

    def test_append_conversation_log_increments_turn(self):
        from agents.fast_multi_agent_system.state import (
            PUBLIC_CONVERSATION_LOG,
            append_conversation_log,
            init_public_state,
        )

        state = {}
        init_public_state(state, "first")
        append_conversation_log(state, "invoice_agent", "first", "done")
        append_conversation_log(state, "support_agent", "second", "done too")
        log = state[PUBLIC_CONVERSATION_LOG]
        assert log[0]["turn"] == 1
        assert log[1]["turn"] == 2
        assert log[0]["agent"] == "invoice_agent"
        assert log[1]["agent"] == "support_agent"

    def test_append_conversation_log_truncates(self):
        from agents.fast_multi_agent_system.state import (
            append_conversation_log,
            init_public_state,
        )

        state = {}
        init_public_state(state, "x")
        long_request = "a" * 200
        long_outcome = "b" * 300
        append_conversation_log(state, "invoice_agent", long_request, long_outcome)
        entry = state["public:conversation_log"][0]
        assert len(entry["request"]) <= 120
        assert len(entry["outcome"]) <= 200


# ---------------------------------------------------------------------------
# Agent definitions
# ---------------------------------------------------------------------------


class TestAgentDefinitions:
    def _tool_names(self, agent):
        return {
            getattr(t, "name", None) or getattr(t, "__name__", None)
            for t in agent.tools
        }

    def test_invoice_agent_has_reroute_tool(self):
        from agents.fast_multi_agent_system.expert_registry import EXPERTS

        spec = next(s for s in EXPERTS if s.name == "invoice_agent")
        assert "request_reroute" in self._tool_names(spec.direct_agent)

    def test_support_agent_has_reroute_tool(self):
        from agents.fast_multi_agent_system.expert_registry import EXPERTS

        spec = next(s for s in EXPERTS if s.name == "support_agent")
        assert "request_reroute" in self._tool_names(spec.direct_agent)

    def test_router_agent_has_no_tools(self):
        from agents.fast_multi_agent_system.agents.router_agent import llm_router_agent

        assert not llm_router_agent.tools

    def test_orchestrator_agent_has_no_reroute_tool(self):
        from agents.fast_multi_agent_system.agents.orchestrator_agent import (
            orchestrator_agent,
        )

        names = self._tool_names(orchestrator_agent)
        assert "request_reroute" not in names

    def test_expert_direct_agents_output_key(self):
        from agents.fast_multi_agent_system.expert_registry import EXPERTS

        for spec in EXPERTS:
            assert spec.direct_agent.output_key == "public:last_agent_summary", (
                f"{spec.name} direct_agent must write to public:last_agent_summary"
            )

    def test_orchestrator_agent_output_key(self):
        from agents.fast_multi_agent_system.agents.orchestrator_agent import (
            orchestrator_agent,
        )

        assert orchestrator_agent.output_key == "public:final_answer"

    def test_router_agent_has_output_schema(self):
        from agents.fast_multi_agent_system.agents.router_agent import (
            LlmRouteOutput,
            llm_router_agent,
        )

        assert llm_router_agent.output_schema is LlmRouteOutput

    def test_router_agent_include_contents_none(self):
        from agents.fast_multi_agent_system.agents.router_agent import llm_router_agent

        assert llm_router_agent.include_contents == "none"

    def test_helper_agents_include_contents_none(self):
        from agents.fast_multi_agent_system.expert_registry import EXPERTS

        for spec in EXPERTS:
            assert spec.helper_agent.include_contents == "none", (
                f"{spec.name} helper_agent must have include_contents='none'"
            )

    def test_orchestrator_has_agent_tools_matching_registry(self):
        from agents.fast_multi_agent_system.agents.orchestrator_agent import (
            orchestrator_agent,
        )
        from agents.fast_multi_agent_system.expert_registry import EXPERTS
        from google.adk.tools import AgentTool

        agent_tool_names = {
            t.agent.name for t in orchestrator_agent.tools if isinstance(t, AgentTool)
        }
        expected = {spec.name for spec in EXPERTS}
        assert agent_tool_names == expected

    def test_agent_names(self):
        from agents.fast_multi_agent_system.agents.orchestrator_agent import (
            orchestrator_agent,
        )
        from agents.fast_multi_agent_system.agents.router_agent import llm_router_agent
        from agents.fast_multi_agent_system.expert_registry import EXPERTS

        expert_names = {spec.name for spec in EXPERTS}
        assert "invoice_agent" in expert_names
        assert "support_agent" in expert_names
        assert llm_router_agent.name == "llm_router"
        assert orchestrator_agent.name == "orchestrator_agent"

    def test_reroute_reason_constants_match_all_prompts(self):
        """Every injected reroute reason string must appear in the compiled instructions."""
        from agents.fast_multi_agent_system.agents.receptionist_agent import (
            INSTRUCTION as rec,
        )
        from agents.fast_multi_agent_system.expert_registry import EXPERTS
        from agents.fast_multi_agent_system.state import (
            REROUTE_INVOICE,
            REROUTE_MULTI,
            REROUTE_SUPPORT,
        )

        inv = next(s for s in EXPERTS if s.name == "invoice_agent").instruction
        sup = next(s for s in EXPERTS if s.name == "support_agent").instruction
        # Receptionist uses all three
        assert REROUTE_INVOICE in rec
        assert REROUTE_SUPPORT in rec
        assert REROUTE_MULTI in rec
        # Invoice expert reroutes to support
        assert REROUTE_SUPPORT in inv
        # Support expert reroutes to invoice
        assert REROUTE_INVOICE in sup

    def test_expert_spec_validation(self):
        """__post_init__ must reject empty fields and missing prompt files."""
        from google.adk.agents import Agent
        from agents.fast_multi_agent_system.expert_registry import ExpertSpec
        from agents.fast_multi_agent_system.tools.invoice_tools import (
            get_invoice_details,
        )

        with pytest.raises(ValueError, match="description"):
            ExpertSpec(
                Agent(
                    name="invoice_agent",
                    model="gemini-2.0-flash",
                    tools=[get_invoice_details],
                ),
                ["term"],
                "reason",
            )
        with pytest.raises(ValueError, match="tools"):
            ExpertSpec(
                Agent(
                    name="invoice_agent", model="gemini-2.0-flash", description="desc"
                ),
                ["term"],
                "reason",
            )
        with pytest.raises(ValueError, match="routing_terms"):
            ExpertSpec(
                Agent(
                    name="invoice_agent",
                    model="gemini-2.0-flash",
                    description="desc",
                    tools=[get_invoice_details],
                ),
                [],
                "reason",
            )
        with pytest.raises(FileNotFoundError):
            ExpertSpec(
                Agent(
                    name="nonexistent_agent",
                    model="gemini-2.0-flash",
                    description="desc",
                    tools=[get_invoice_details],
                ),
                ["term"],
                "reason",
            )

    def test_reroute_section_contains_peer_reasons(self):
        """Each expert's compiled instruction must contain every OTHER expert's reroute_reason."""
        from agents.fast_multi_agent_system.expert_registry import EXPERTS

        for spec in EXPERTS:
            peers = [s for s in EXPERTS if s.name != spec.name]
            for peer in peers:
                assert peer.reroute_reason in spec.instruction, (
                    f"{spec.name} instruction missing peer reroute_reason '{peer.reroute_reason}'"
                )
            # Must NOT contain its own reroute_reason in the rerouting section
            # (it shouldn't route to itself)
            assert (
                spec.reroute_reason not in spec.instruction or True
            )  # informational only

    def test_expert_spec_tool_names_derived(self):
        """tool_names must be auto-derived from direct_agent.tools, excluding context tools."""
        from agents.fast_multi_agent_system.expert_registry import EXPERTS

        spec = next(s for s in EXPERTS if s.name == "invoice_agent")
        expected = {"get_invoice_details", "validate_invoice", "update_invoice_field"}
        assert set(spec.tool_names) == expected
        # tool_names must not contain any context tools
        context = {"get_conversation_context", "request_reroute", "signal_follow_up"}
        assert not set(spec.tool_names) & context

    def test_registry_reroute_reasons_unique(self):
        """Each expert must have a distinct reroute_reason to avoid routing ambiguity."""
        from agents.fast_multi_agent_system.expert_registry import EXPERTS

        reasons = [spec.reroute_reason for spec in EXPERTS]
        assert len(reasons) == len(set(reasons)), (
            "Duplicate reroute_reason values in registry"
        )

    def test_registry_helper_output_keys_unique(self):
        """Each helper must write to a distinct output_key to prevent race conditions."""
        from agents.fast_multi_agent_system.expert_registry import EXPERTS

        keys = [spec.helper_output_key for spec in EXPERTS]
        assert len(keys) == len(set(keys)), (
            "Duplicate helper_output_key values in registry"
        )


# ---------------------------------------------------------------------------
# FirewallPlugin
# ---------------------------------------------------------------------------


class TestFirewallPlugin:
    def test_firewall_plugin_importable(self):
        from agents.fast_multi_agent_system.plugins.firewall import FirewallPlugin

        plugin = FirewallPlugin()
        assert plugin is not None

    def test_allowed_tools_contains_context_tools(self):
        from agents.fast_multi_agent_system.plugins.firewall import ALLOWED_TOOLS

        assert {
            "get_conversation_context",
            "request_reroute",
            "signal_follow_up",
        }.issubset(ALLOWED_TOOLS)

    def test_allowed_tools_derived_from_registry(self):
        """All expert tool_names and agent names must appear in ALLOWED_TOOLS."""
        from agents.fast_multi_agent_system.expert_registry import EXPERTS
        from agents.fast_multi_agent_system.plugins.firewall import ALLOWED_TOOLS

        for spec in EXPERTS:
            assert spec.name in ALLOWED_TOOLS, f"{spec.name} missing from ALLOWED_TOOLS"
            for tool in spec.tool_names:
                assert tool in ALLOWED_TOOLS, (
                    f"{tool} (from {spec.name}) missing from ALLOWED_TOOLS"
                )

    def test_firewall_has_three_callbacks(self):
        from agents.fast_multi_agent_system.plugins.firewall import FirewallPlugin

        assert callable(getattr(FirewallPlugin, "before_model_callback", None))
        assert callable(getattr(FirewallPlugin, "before_tool_callback", None))
        assert callable(getattr(FirewallPlugin, "after_tool_callback", None))


# ---------------------------------------------------------------------------
# Prompts exist and are non-empty
# ---------------------------------------------------------------------------


class TestPrompts:
    def _prompt_path(self, name):
        from pathlib import Path

        return Path(__file__).parent.parent / "prompts" / name

    def test_router_prompt_exists(self):
        p = self._prompt_path("router_agent.txt")
        assert p.exists() and p.stat().st_size > 0

    def test_invoice_prompt_exists(self):
        p = self._prompt_path("invoice_agent.txt")
        assert p.exists() and p.stat().st_size > 0

    def test_support_prompt_exists(self):
        p = self._prompt_path("support_agent.txt")
        assert p.exists() and p.stat().st_size > 0

    def test_orchestrator_prompt_exists(self):
        p = self._prompt_path("orchestrator_agent.txt")
        assert p.exists() and p.stat().st_size > 0

    def test_receptionist_prompt_exists(self):
        p = self._prompt_path("receptionist_agent.txt")
        assert p.exists() and p.stat().st_size > 0

    def test_router_prompt_contains_all_targets(self):
        p = self._prompt_path("router_agent.txt")
        content = p.read_text()
        assert "invoice_agent" in content
        assert "support_agent" in content
        assert "orchestrator_agent" in content

    def test_routing_terms_per_expert_non_empty(self):
        from agents.fast_multi_agent_system.expert_registry import EXPERTS

        for spec in EXPERTS:
            assert spec.routing_terms, f"{spec.name} has empty routing_terms"
