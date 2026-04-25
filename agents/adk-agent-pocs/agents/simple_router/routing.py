# routing.py
# Deterministic scored router. No LLM call.
# Returns a RoutingDecision so callers and observability tools can inspect the decision.
#
# HOW-TO gate: exact prefix match against HOWTO_TRIGGERS (parsed from howto_triggers.txt).
# Zero false-positive risk — same phrases used in the LLM router prompt.
#
# Keyword scoring: each expert declares routing_terms in expert_registry.register().
# Adding a new expert and providing routing_terms automatically extends the router.
# No changes needed here.

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from .expert_registry import EXPERTS, HOWTO_TRIGGERS

if TYPE_CHECKING:
    from .expert_registry import Expert


@dataclass
class RoutingDecision:
    mode: Literal["direct", "no_signal"]
    selected_agent: str  # expert name, "support_agent" (HOW-TO), or "" (no signal)
    reason: str  # human-readable explanation stored in router logs
    scores: dict[str, int]  # {expert_name: match_count, ...}
    confidence: float  # 0.0 – 1.0; low = ambiguous or missing signal


# Below this confidence the callback lets the LLM router handle the message.
# score=1 → confidence=0.50 (below) → LLM fallback
# score=2 → confidence=0.67 (above) → static bypass
# score=3 → confidence=0.75 (above) → static bypass
# Raise toward 1.0 to be more conservative; lower toward 0.0 to trust scores more.
CONFIDENCE_THRESHOLD = 0.6


def decide_route(
    user_text: str, *, experts: list[Expert] | None = None
) -> RoutingDecision:
    """Score the request and return a structured routing decision. No LLM call.

    Args:
        user_text: raw user message text.
        experts: expert list to score against (defaults to EXPERTS from the registry).
                 Pass a custom list in tests to avoid importing sub_agents.
    """
    if experts is None:
        experts = EXPERTS

    # Cap at 500 chars — term scanning is O(len(text)) per term, sufficient for any
    # real message and protects against pathological inputs (pasted documents, etc.).
    text = user_text.lower()[:500]

    # HOW-TO gate — same trigger phrases as the LLM router prompt. Zero false positives.
    # HOWTO_TRIGGERS is pre-lowercased at module load (see expert_registry.py).
    for trigger in HOWTO_TRIGGERS:
        if text.startswith(trigger):
            return RoutingDecision(
                mode="direct",
                selected_agent="support_agent",
                reason=f"HOW-TO gate: starts with '{trigger}'",
                scores={},
                confidence=1.0,
            )

    # Keyword scoring — count term matches per expert.
    scores = {
        spec.template.name: sum(1 for t in spec.routing_terms if t in text)
        for spec in experts
    }
    domains_hit = {name for name, count in scores.items() if count > 0}
    total = sum(scores.values())

    if len(domains_hit) > 1:
        # Multi-domain overlap — let the LLM router decide.
        return RoutingDecision(
            mode="no_signal",
            selected_agent="",
            reason="Multi-domain overlap — LLM fallback",
            scores=scores,
            confidence=0.0,
        )

    if total == 0:
        return RoutingDecision(
            mode="no_signal",
            selected_agent="",
            reason="No routing terms matched — LLM fallback",
            scores=scores,
            confidence=0.0,
        )

    best = max(scores, key=lambda n: scores[n])
    # score/(score+1): score=1→0.5, score=2→0.67, score=3→0.75
    confidence = scores[best] / (scores[best] + 1)

    if confidence < CONFIDENCE_THRESHOLD:
        return RoutingDecision(
            mode="no_signal",
            selected_agent=best,
            reason=f"Confidence {confidence:.2f} below threshold ({CONFIDENCE_THRESHOLD}) — LLM fallback",
            scores=scores,
            confidence=confidence,
        )

    return RoutingDecision(
        mode="direct",
        selected_agent=best,
        reason=f"{scores[best]} term(s) matched for {best} (confidence {confidence:.2f})",
        scores=scores,
        confidence=confidence,
    )
