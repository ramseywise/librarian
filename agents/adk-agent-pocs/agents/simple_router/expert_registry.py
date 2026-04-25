# expert_registry.py
# Single source of truth for domain experts.
#
# To add a new expert (e.g. expense_agent):
#   1. Create tools/expense_tools.py          — domain-specific tools
#   2. Create prompts/expense_agent.txt        — agent prompt
#   3. Create sub_agents/expense_agent.py      — call register(Agent(...)) (no assignments needed)
#   4. Import it in sub_agents/__init__.py     BEFORE orchestrator_agent
#   5. Add it to the sub_agents list in agent.py
#   6. Add a routing rule for it in prompts/router_agent.txt
#   7. Add its routing patterns to prompts/receptionist_agent.txt
#
# What wires itself automatically after steps 1–4:
#   — helper variant (name, prompt suffix, include_contents, output_key)
#   — orchestrator tool list ({domains} injection picks up the new expert's description)
# Steps 5–7 still require manual edits to agent.py, router_agent.txt, and receptionist_agent.txt.

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import IO

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.genai import types as _genai_types

from ._facts_callbacks import inject_facts_callback, persist_facts_callback
from ._history import strip_tool_history_callback
from .tools import signal_follow_up

_PROMPTS_DIR = Path(__file__).parent / "prompts"

_SHARED_RULES = (_PROMPTS_DIR / "shared_rules.txt").read_text().strip()
_HOWTO_TRIGGERS_RAW = (_PROMPTS_DIR / "howto_triggers.txt").read_text().strip()

# Public list of how-to trigger phrases parsed from howto_triggers.txt.
# Pre-lowercased so routing.py can compare directly against lowercased user text.
# Used by both the router prompt (via {howto_triggers}) and the static router
# (routing.py) — single source of truth.
HOWTO_TRIGGERS: list[str] = [
    t.lower() for t in re.findall(r'"([^"]+)"', _HOWTO_TRIGGERS_RAW)
]

_THINKING_CONFIG = _genai_types.GenerateContentConfig(
    thinking_config=_genai_types.ThinkingConfig(
        thinking_level="low", include_thoughts=True
    )
)


_THOUGHTS_LOG = Path(__file__).parent / "eval" / ".last_thoughts.log"
_thoughts_file: IO[str] | None = None


def _get_thoughts_file():
    """Open the thoughts log file on first use, truncating from the previous run."""
    global _thoughts_file
    if _thoughts_file is None:
        _THOUGHTS_LOG.parent.mkdir(parents=True, exist_ok=True)
        _thoughts_file = _THOUGHTS_LOG.open("w", encoding="utf-8")
    return _thoughts_file


def _log_thoughts_callback(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> LlmResponse | None:
    """Append model thought parts to eval/.last_thoughts.log.

    Each entry is prefixed with invocation_id + agent name so thoughts can be
    correlated with failing eval cases by grepping the log after a run.
    Terminal output is not affected — the log file is the only destination.
    """
    content = getattr(llm_response, "content", None)
    if content is None:
        return None
    agent = getattr(callback_context, "agent_name", "?")
    inv_id = getattr(callback_context, "invocation_id", "?")
    thoughts = [
        (getattr(p, "text", None) or "").strip()
        for p in (getattr(content, "parts", None) or [])
        if getattr(p, "thought", None)
    ]
    if not thoughts:
        return None
    f = _get_thoughts_file()
    for text in thoughts:
        if text:
            f.write(f"[{inv_id}] [{agent}]\n{text}\n\n")
    f.flush()
    return None


def load_prompt(name: str) -> str:
    """Load a named prompt file and apply standard placeholder substitutions.

    Handles {shared_rules} and {howto_triggers}. Safe to call on any prompt —
    substitutions are no-ops when the placeholder is absent.
    """
    text = (_PROMPTS_DIR / f"{name}.txt").read_text()
    return text.replace("{shared_rules}", _SHARED_RULES).replace(
        "{howto_triggers}", _HOWTO_TRIGGERS_RAW
    )


@dataclass
class Expert:
    """Wraps one domain expert. Built from an Agent template by register().

    The template must carry: name, model, description, and domain tools only.
    Context/signal tools and the prompt are injected by the registry.

    Attributes:
        direct_agent: full agent used by the router (includes signal_follow_up).
        helper_agent: stateless variant used by orchestrator_agent as an AgentTool
                      (include_contents="none", no signal_follow_up, writes output_key).
        routing_terms: keyword/phrase list used by the static router in routing.py
                       to score messages without an LLM call. Longer phrases score
                       higher and are more precise — prefer multi-word terms over
                       single words to reduce false-positive routing.
    """

    template: Agent
    routing_terms: list[str] = field(default_factory=list)
    direct_agent: Agent = field(init=False)
    helper_agent: Agent = field(init=False)

    def __post_init__(self) -> None:
        prompt = load_prompt(self.template.name)
        domain_tools = list(self.template.tools or [])

        name = self.template.name
        # Build the before_model_callback chain for direct agents:
        #   strip_tool_history_callback → inject_facts_callback → [existing_cb if any]
        # strip runs first to remove 'For context:' noise and stale '[session facts:]'
        # items; inject then appends a fresh '[session facts:]' at the end of the
        # current turn, after the stable conversation history (prefix-cache friendly).
        existing_cb = self.template.before_model_callback

        def _direct_cb(
            callback_context,
            llm_request,
            _strip=strip_tool_history_callback,
            _inject=inject_facts_callback,
            _extra=existing_cb,
        ):
            result = _strip(callback_context, llm_request)
            if result is not None:
                return result
            result = _inject(callback_context, llm_request)
            if result is not None:
                return result
            if _extra is not None:
                return _extra(callback_context, llm_request)
            return None

        # Expert direct agents: signal_follow_up + domain tools.
        # get_conversation_context is no longer in the tool list — facts are
        # delivered via inject_facts_callback instead.
        self.direct_agent = self.template.model_copy(
            update={
                "instruction": prompt,
                "tools": [signal_follow_up, *domain_tools],
                "before_model_callback": _direct_cb,
                "after_model_callback": _log_thoughts_callback,
                "after_agent_callback": persist_facts_callback,
                "generate_content_config": _THINKING_CONFIG,
                # Prevent ADK from resuming this expert agent on the next user turn.
                # Without this, _find_agent_to_run resumes the last-active sub-agent,
                # bypassing the router entirely. Setting True makes ADK fall back to
                # root_agent (router) so every new turn is routed through get_conversation_context.
                "disallow_transfer_to_parent": True,
                # Prevent expert agents from routing to sibling agents (e.g. invoice_agent
                # transferring to orchestrator_agent or support_agent). With static routing
                # enabled, the router always sends requests to the correct expert. Expert-to-
                # expert transfers create ping-pong loops and orchestrator escalations that
                # confuse multi-turn sessions with mixed conversation history.
                "disallow_transfer_to_peers": True,
            }
        )
        # Helper name must differ from direct_agent name — ADK resolves agents by
        # name and a duplicate causes silent hangs when used as an AgentTool.
        # NOTE: helper agents appear in debug traces as "{name}_helper" (e.g.
        # invoice_agent_helper). They are NOT in agent.py sub_agents — they are
        # AgentTools built here and used only by orchestrator_agent internally.
        self.helper_agent = self.template.model_copy(
            update={
                "name": f"{name}_helper",
                "instruction": prompt + _HELPER_MODE_SUFFIX,
                "tools": [*domain_tools],
                "include_contents": "none",
                "output_key": f"public:{name}_helper_result",
                "generate_content_config": _THINKING_CONFIG,
            }
        )


# Appended to every helper prompt — overrides any transfer/reroute rules so
# helpers never attempt an agent transfer while running inside an AgentTool.
_HELPER_MODE_SUFFIX = (
    "\n\nHELPER MODE: you are running as a sub-tool inside an orchestrator. "
    "Do NOT transfer to any other agent under any circumstances. "
    "Focus only on your own domain. If the request is outside your domain, "
    "return an empty result — do not transfer."
)

_registry: list[Expert] = []


def register(template: Agent, *, routing_terms: list[str] | None = None) -> Expert:
    """Register a domain expert. Call from each expert's own file.

    Args:
        template: Agent with name, model, description, and domain tools set.
                  Do NOT include context tools — the registry injects them.
        routing_terms: Optional keyword/phrase list for the static router in
                       routing.py. Prefer multi-word terms ("show invoice") over
                       single words to minimize false-positive bypass decisions.
    Returns:
        The Expert spec with direct_agent and helper_agent ready to use.
    """
    spec = Expert(template=template, routing_terms=routing_terms or [])
    _registry.append(spec)
    return spec


# Live alias — both names point to the same list object, so EXPERTS reflects
# all register() calls made after this line (during sub_agents imports).
EXPERTS: list[Expert] = _registry


def get_direct(name: str) -> Agent:
    """Return the direct (router-facing) agent for the given expert name."""
    match = next((s for s in _registry if s.template.name == name), None)
    if match is None:
        raise KeyError(f"No expert registered with name {name!r}")
    return match.direct_agent


def build_domains_summary(indent: str = "  ") -> str:
    """Return a bullet-list of registered expert domains for prompt injection.

    Call after all experts have been registered (i.e. after sub_agents imports).
    Used to fill {domains} placeholders in orchestrator and receptionist prompts
    so domain scope stays in one place — the Expert.template.description field.
    """
    return "\n".join(
        f"{indent}- {spec.template.name}: {spec.template.description}"
        for spec in _registry
    )
