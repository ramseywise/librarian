# expert_registry.py
# Single source of truth for domain experts.
#
# To add a new expert (e.g. expense_agent):
#   1. Create tools/expense_tools.py          — domain-specific tools
#   2. Create prompts/expense_agent.txt        — use {reroute_section} placeholder
#   3. Add REROUTE_EXPENSE + entry to state.REROUTE_ALL
#   4. Create experts/expense_agent.py        — Agent template + register(ExpertSpec(...))
#   5. Add one import line in the "Registered experts" section below.
#      Everything else (rerouting section, orchestrator, router, firewall,
#      root agent) wires itself automatically.

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from google.adk.agents import Agent

from .state import PROMPT_SHARED, REROUTE_ALL
from .tools.context_tools import (
    get_conversation_context,
    request_reroute,
    signal_follow_up,
)

_PROMPTS_DIR = Path(__file__).parent / "prompts"

_HELPER_MODEL = "gemini-2.5-flash"  # capable; orchestrated sub-tasks
_DIRECT_OUTPUT_KEY = "public:last_agent_summary"

_CONTEXT_TOOL_NAMES: frozenset[str] = frozenset(
    {
        "get_conversation_context",
        "request_reroute",
        "signal_follow_up",
    }
)


def _build_reroute_section(current_name: str, all_specs: list[ExpertSpec]) -> str:
    """Build the rerouting instruction block for one expert, listing all OTHER experts."""
    entries = "\n".join(
        f'  "{s.reroute_reason}"  — {s.description}'
        for s in all_specs
        if s.name != current_name
    )
    if not entries:
        return ""
    return (
        "Rerouting — call request_reroute(reason=...) with the EXACT string when needed:\n"
        + entries
        + "\n"
        "\n"
        "  Do NOT produce any text before calling request_reroute(). "
        "Call it immediately and stop.\n"
        "  The reason argument MUST be one of the exact strings above "
        "— do not paraphrase or substitute."
    )


@dataclass
class ExpertSpec:
    """Describes one domain expert.  Two-phase construction:

    Pass an Agent template carrying the expert's identity, model, description,
    and domain tools. The registry injects context tools, compiles the prompt
    (with the auto-generated rerouting section), and builds both agent variants.

    Required args:
        agent:          Agent template — name, model, description, and domain
                        tools are read from it. Instruction is ignored; it is
                        compiled from prompts/<name>.txt during finalization.
        routing_terms:  keyword list used by the deterministic scorer in routing.py
        reroute_reason: the request_reroute(reason=...) value that routes TO this expert

    Auto-derived from agent (do NOT pass manually):
        name, description, domain_tools

    Set by _finalize() (do NOT pass manually):
        direct_agent, helper_agent, instruction, tool_names
    """

    agent: Agent  # template: name, model, description, domain tools
    routing_terms: list[str]
    reroute_reason: str
    # Set by _finalize() — None/empty until finalization.
    direct_agent: Agent | None = field(init=False, default=None)
    helper_agent: Agent | None = field(init=False, default=None)
    instruction: str = field(init=False, default="")
    tool_names: list[str] = field(init=False, default_factory=list)

    @property
    def name(self) -> str:
        return self.agent.name

    @property
    def description(self) -> str:
        return self.agent.description or ""

    @property
    def domain_tools(self) -> list:
        return list(self.agent.tools or [])

    @property
    def helper_output_key(self) -> str:
        return self.helper_agent.output_key if self.helper_agent else ""

    def __post_init__(self) -> None:
        """Phase 1: validate and confirm the prompt file exists."""
        if not self.description:
            raise ValueError(
                f"ExpertSpec '{self.name}': agent.description must not be empty"
            )
        if not self.domain_tools:
            raise ValueError(f"ExpertSpec '{self.name}': agent.tools must not be empty")
        if not self.routing_terms:
            raise ValueError(
                f"ExpertSpec '{self.name}': routing_terms must not be empty"
            )
        prompt_path = _PROMPTS_DIR / f"{self.name}.txt"
        if not prompt_path.exists():
            raise FileNotFoundError(
                f"ExpertSpec '{self.name}': prompt not found at {prompt_path}"
            )

    def _finalize(self, all_specs: list[ExpertSpec]) -> None:
        """Phase 2: compile prompt with full expert context, then build agents.

        Called once after all experts are registered so every spec can reference
        the others when generating its rerouting section.
        """
        reroute_section = _build_reroute_section(self.name, all_specs)
        self.instruction = (
            (_PROMPTS_DIR / f"{self.name}.txt")
            .read_text()
            .format(**REROUTE_ALL, **PROMPT_SHARED, reroute_section=reroute_section)
        )

        # Direct agent: clone template, inject compiled instruction + context/routing tools.
        self.direct_agent = self.agent.model_copy(
            update={
                "instruction": self.instruction,
                "tools": [
                    get_conversation_context,
                    request_reroute,
                    signal_follow_up,
                    *self.domain_tools,
                ],
                "output_key": _DIRECT_OUTPUT_KEY,
            }
        )
        # Helper agent: smarter model, context tool only (no routing), no history.
        self.helper_agent = self.agent.model_copy(
            update={
                "description": self.description,
                "model": _HELPER_MODEL,
                "instruction": self.instruction,
                "tools": [get_conversation_context, *self.domain_tools],
                "output_key": f"public:{self.name}_helper_summary",
                "include_contents": "none",
            }
        )

        self.tool_names = [
            n
            for t in self.direct_agent.tools
            if (n := getattr(t, "name", None) or getattr(t, "__name__", None))
            and n not in _CONTEXT_TOOL_NAMES
        ]


# ---------------------------------------------------------------------------
# Registry — call register(ExpertSpec(...)) from each expert's own file.
# ---------------------------------------------------------------------------

_registry: list[ExpertSpec] = []


def register(spec: ExpertSpec) -> ExpertSpec:
    """Register an ExpertSpec. Called from each expert's own file."""
    _registry.append(spec)
    return spec


# ---------------------------------------------------------------------------
# Registered experts — add one import per expert (see instructions at top).
# ---------------------------------------------------------------------------

from .experts import support_agent  # noqa: E402, F401

# Phase 2: compile prompts and build agents now that all experts are registered.
for _spec in _registry:
    _spec._finalize(_registry)

EXPERTS: list[ExpertSpec] = _registry
