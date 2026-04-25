import json
import logging
import os
from typing import AsyncGenerator

from google.adk.agents import BaseAgent
from google.adk.agents.context_cache_config import ContextCacheConfig
from google.adk.agents.invocation_context import InvocationContext
from google.adk.apps import App
from google.adk.events.event import Event

from .agents.orchestrator_agent import orchestrator_agent
from .agents.receptionist_agent import receptionist_agent
from .agents.router_agent import llm_router_agent
from .expert_registry import EXPERTS
from .plugins.firewall import FirewallPlugin
from .routing import CONFIDENCE_THRESHOLD, decide_route
from .state import (
    PUBLIC_FINAL_ANSWER,
    PUBLIC_FOLLOW_UP_AGENT,
    PUBLIC_LAST_SUMMARY,
    PUBLIC_ROUTING,
    PUBLIC_ROUTING_ESCALATION,
    PUBLIC_TASK_NOTE,
    REROUTE_MULTI,
    append_conversation_log,
    init_public_state,
)

_level = getattr(
    logging, os.environ.get("LOGLEVEL", "WARNING").upper(), logging.WARNING
)
_pkg_logger = logging.getLogger(__name__.rpartition(".")[0])
_pkg_logger.handlers.clear()
_h = logging.StreamHandler()
_h.setFormatter(logging.Formatter("%(name)s %(levelname)s %(message)s"))
_pkg_logger.addHandler(_h)
_pkg_logger.setLevel(_level)
_pkg_logger.propagate = False

logger = logging.getLogger(__name__)


class HybridRootAgent(BaseAgent):
    """Deterministic router with three-layer fallback.

    Layer 0: LLM-assisted routing — fires when confidence < CONFIDENCE_THRESHOLD
             or no domain signal is detected.

    Layer 1: Pre-routing — decide_route() routes both-domain and planning-signal
             requests directly to the orchestrator (zero extra LLM calls).

    Layer 2: Post-routing — direct-path experts call request_reroute() when they
             detect they were misrouted. Root agent escalates accordingly.
    """

    direct_experts: dict  # {agent_name: BaseAgent} — built from ExpertSpec registry
    receptionist_agent: BaseAgent
    llm_router_agent: BaseAgent
    orchestrator_agent: BaseAgent

    model_config = {"arbitrary_types_allowed": True}

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        user_text = (
            ctx.user_content.parts[0].text
            if ctx.user_content and ctx.user_content.parts
            else ""
        )

        init_public_state(ctx.session.state, user_text)

        try:
            decision = decide_route(user_text)
            ctx.session.state[PUBLIC_ROUTING] = {
                "mode": decision.mode,
                "selected_agent": decision.selected_agent,
                "reason": decision.reason,
                "scores": decision.scores,
                "confidence": decision.confidence,
            }
            logger.debug(
                "route decision: mode=%s agent=%s confidence=%.2f reason=%s",
                decision.mode,
                decision.selected_agent,
                decision.confidence,
                decision.reason,
            )

            _follow_up_agent = ctx.session.state.get(PUBLIC_FOLLOW_UP_AGENT)
            ctx.session.state[PUBLIC_FOLLOW_UP_AGENT] = None
            logger.debug("follow_up_agent=%r", _follow_up_agent)

            selected = decision.selected_agent
            decision_mode = decision.mode
            needs_llm_routing = decision.mode == "no_signal" or (
                decision.mode == "direct" and decision.confidence < CONFIDENCE_THRESHOLD
            )

            _direct_expert_names = set(self.direct_experts.keys()) | {
                "receptionist_agent"
            }
            _all_follow_up_agents = _direct_expert_names | {"orchestrator_agent"}

            # Honour a pending follow-up unless the new message is clearly a new request.
            # Discard when:
            #   - planned route
            #   - multi-domain overlap (≥2 experts have keyword hits)
            #   - confident direct to a different agent
            #   - any domain signal present (routing terms matched > 0): even if the same
            #     agent is selected, a message with domain keywords is a new request, not
            #     a bare continuation ("11", "yes") which has no routing terms.
            _expert_total = sum(decision.scores.get(spec.name, 0) for spec in EXPERTS)
            _multi_domain = (
                sum(1 for spec in EXPERTS if decision.scores.get(spec.name, 0) > 0) > 1
            )
            # A no_signal message with >2 words is a new request, not a bare follow-up
            # reply ("11", "yes", "INV-42"). Domain terms would push mode to "direct".
            _no_signal_new_request = (
                decision.mode == "no_signal" and len(user_text.split()) > 2
            )
            _follow_up_is_new_request = _follow_up_agent in _all_follow_up_agents and (
                decision.mode == "planned"
                or _multi_domain
                or _no_signal_new_request
                or (
                    decision.mode == "direct"
                    and decision.confidence >= CONFIDENCE_THRESHOLD
                    and (
                        _expert_total > 0 or decision.selected_agent != _follow_up_agent
                    )
                )
            )
            if _follow_up_is_new_request:
                logger.debug(
                    "follow-up discarded — new request detected (mode=%s agent=%s)",
                    decision.mode,
                    decision.selected_agent,
                )
            elif _follow_up_agent in _all_follow_up_agents:
                logger.debug("follow-up continuation: routing to %s", _follow_up_agent)
                selected = _follow_up_agent
                decision_mode = (
                    "direct" if _follow_up_agent in _direct_expert_names else "planned"
                )
                ctx.session.state[PUBLIC_ROUTING] = {
                    **ctx.session.state[PUBLIC_ROUTING],
                    "mode": decision_mode,
                    "selected_agent": selected,
                    "reason": f"Follow-up continuation ({_follow_up_agent})",
                }
                needs_llm_routing = False

            if needs_llm_routing:
                logger.debug("low confidence / no signal — invoking llm_router")

                _llm_final_event = None
                async for _ev in self.llm_router_agent.run_async(ctx):
                    if _ev.is_final_response():
                        _llm_final_event = _ev

                ctx.session.events[:] = [
                    e
                    for e in ctx.session.events
                    if getattr(e, "author", None) != "llm_router"
                ]
                logger.debug(
                    "stripped llm_router events; session now has %d events",
                    len(ctx.session.events),
                )

                llm_route = ""
                llm_route_reason = ""
                if _llm_final_event and getattr(_llm_final_event, "content", None):
                    _raw = "".join(
                        p.text
                        for p in (_llm_final_event.content.parts or [])
                        if hasattr(p, "text") and p.text
                    )
                    try:
                        _parsed = json.loads(_raw)
                        llm_route = _parsed.get("selected_agent", "")
                        llm_route_reason = _parsed.get("reason", "")
                    except (json.JSONDecodeError, AttributeError):
                        llm_route = _raw.strip()

                _valid = set(self.direct_experts.keys()) | {
                    "orchestrator_agent",
                    "receptionist_agent",
                }
                selected = llm_route if llm_route in _valid else "receptionist_agent"
                logger.debug(
                    "llm_router classified as: %s reason=%r", selected, llm_route_reason
                )

                _is_direct = selected in _direct_expert_names
                ctx.session.state[PUBLIC_ROUTING] = {
                    **ctx.session.state[PUBLIC_ROUTING],
                    "mode": "direct" if _is_direct else "planned",
                    "selected_agent": selected,
                    "reason": f"LLM-assisted (was: {decision.reason})",
                }
                decision_mode = ctx.session.state[PUBLIC_ROUTING]["mode"]

            # ----------------------------------------------------------------
            # Execution loop — handles escalation chains up to _MAX_DEPTH.
            # Each iteration runs one agent, then checks for an escalation
            # signal. Depth-exceeded and no-response states both log a WARNING
            # and fall back gracefully so the user always gets a reply.
            # ----------------------------------------------------------------
            _MAX_DEPTH = 2
            _reason_to_expert = {spec.reroute_reason: spec.name for spec in EXPERTS}

            if decision_mode in ("planned", "no_signal"):
                _cur_id = "orchestrator_agent"
                _cur_agent = self.orchestrator_agent
            else:
                _cur_id = selected
                _cur_agent = (
                    self.direct_experts.get(selected) or self.receptionist_agent
                )

            _depth = 0
            _prev_id = None
            _final_yielded = False

            while True:
                logger.debug("invoking %s (depth=%d)", _cur_id, _depth)
                _had_final = False
                async for event in _cur_agent.run_async(ctx):
                    yield event
                    if event.is_final_response():
                        _had_final = True
                        _final_yielded = True

                if not _had_final:
                    logger.warning(
                        "invalid state: %s produced no final response "
                        "(depth=%d prev=%s) — continuing escalation check",
                        _cur_id,
                        _depth,
                        _prev_id,
                    )

                _outcome_key = (
                    PUBLIC_FINAL_ANSWER
                    if _cur_id == "orchestrator_agent"
                    else PUBLIC_LAST_SUMMARY
                )
                append_conversation_log(
                    ctx.session.state,
                    agent=_cur_id,
                    request=user_text,
                    outcome=ctx.session.state.get(_outcome_key) or "",
                )
                ctx.session.state[PUBLIC_TASK_NOTE] = None

                escalation = ctx.session.state.get(PUBLIC_ROUTING_ESCALATION)
                if not escalation:
                    break  # normal exit

                ctx.session.state[PUBLIC_ROUTING_ESCALATION] = None
                _reason = escalation.get("reason", "")
                logger.debug(
                    "escalation from %s: %r (depth=%d)", _cur_id, _reason, _depth
                )

                _depth += 1
                if _depth > _MAX_DEPTH:
                    logger.warning(
                        "invalid state: escalation depth %d exceeded "
                        "(chain: %s → %s, reason=%r) — forcing orchestrator",
                        _depth,
                        _prev_id or "?",
                        _cur_id,
                        _reason,
                    )
                    _prev_id = _cur_id
                    _cur_id = "orchestrator_agent"
                    _cur_agent = self.orchestrator_agent
                    ctx.session.state[PUBLIC_TASK_NOTE] = (
                        f"All specialists failed to resolve this request. "
                        f"Answer the user directly: {user_text}"
                    )
                    continue

                if _reason == REROUTE_MULTI:
                    _next_id = "orchestrator_agent"
                    _next_agent = self.orchestrator_agent
                elif _reason in _reason_to_expert:
                    _next_id = _reason_to_expert[_reason]
                    _next_agent = (
                        self.direct_experts.get(_next_id) or self.orchestrator_agent
                    )
                else:
                    logger.warning(
                        "invalid state: unknown escalation reason %r from %s "
                        "— falling back to orchestrator",
                        _reason,
                        _cur_id,
                    )
                    _next_id = "orchestrator_agent"
                    _next_agent = self.orchestrator_agent

                ctx.session.state[PUBLIC_ROUTING] = {
                    "mode": "planned",
                    "selected_agent": _next_id,
                    "reason": f"Escalated from {_cur_id}: {_reason}",
                    "scores": ctx.session.state[PUBLIC_ROUTING].get("scores", {}),
                    "confidence": ctx.session.state[PUBLIC_ROUTING].get(
                        "confidence", 0.0
                    ),
                }
                ctx.session.state[PUBLIC_TASK_NOTE] = (
                    f"The previous agent ({_cur_id}) could not handle this request "
                    f"({_reason}). Please answer the user's original request: {user_text}"
                )
                _prev_id = _cur_id
                _cur_id = _next_id
                _cur_agent = _next_agent

            # Final safety net: if no agent produced a final response at all,
            # hand off to receptionist for a graceful reply.
            if not _final_yielded:
                logger.warning(
                    "invalid state: no final response for %r — falling back to receptionist",
                    user_text[:80],
                )
                async for event in self.receptionist_agent.run_async(ctx):
                    yield event

        except Exception:
            ctx.session.state["public:error"] = {
                "agent": "root_router",
                "request": user_text[:120],
            }
            raise


root_agent = HybridRootAgent(
    name="root_router",
    direct_experts={spec.name: spec.direct_agent for spec in EXPERTS},
    receptionist_agent=receptionist_agent,
    llm_router_agent=llm_router_agent,
    orchestrator_agent=orchestrator_agent,
)

app = App(
    name="fast_multi_agent_system",
    root_agent=root_agent,
    plugins=[FirewallPlugin()],
    context_cache_config=ContextCacheConfig(
        min_tokens=512,
        cache_intervals=20,
        ttl_seconds=3600,
    ),
)
