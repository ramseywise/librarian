# routing.py
# Deterministic scored router. No LLM call.
# Returns a RoutingDecision so callers and observability tools can inspect the decision.
#
# Scoring terms per expert are declared in expert_registry.ExpertSpec.routing_terms.
# Adding a new expert automatically extends the router — no changes needed here.

from dataclasses import dataclass

from .expert_registry import EXPERTS


@dataclass
class RoutingDecision:
    mode: str  # "direct" | "planned" | "no_signal"
    selected_agent: str  # one of the expert names or "orchestrator_agent"
    reason: str  # human-readable explanation stored in public:routing
    scores: dict  # {spec.name: int, ..., "planning": int}
    confidence: float  # 0.0 – 1.0; low = ambiguous or missing signal


# Below this confidence the root agent triggers the LLM router instead of direct routing.
# At 0.6: invoice=2, support=1 (confidence=0.67) still goes direct; invoice=1, support=1
# (confidence=0.5) would already be caught by the "both domains" planned branch first.
# Raise toward 1.0 to be more conservative; lower toward 0.0 to trust keyword scores more.
CONFIDENCE_THRESHOLD = 0.6

# Signals that require multi-step orchestration. Kept tight to avoid false positives.
PLANNING_SIGNALS = [
    "and then",
    "check whether",
    "validate and",
    "make sure",
    "before I ",
    "after that",
    "if invalid",
    "if it fails",
    "if missing",
    "explain how to fix",
    "compare",
]


def _score(text: str) -> dict:
    scores = {"planning": sum(1 for s in PLANNING_SIGNALS if s in text)}
    for spec in EXPERTS:
        scores[spec.name] = sum(1 for t in spec.routing_terms if t in text)
    return scores


def decide_route(user_text: str) -> RoutingDecision:
    """Score the request and return a structured routing decision. No LLM call."""
    text = user_text.lower()
    scores = _score(text)
    planning = scores["planning"]

    expert_scores = {spec.name: scores[spec.name] for spec in EXPERTS}
    domains_hit = {name for name, count in expert_scores.items() if count > 0}
    total = sum(expert_scores.values())

    if planning > 0:
        return RoutingDecision(
            mode="planned",
            selected_agent="orchestrator_agent",
            reason=f"Planning signal(s) detected ({planning} match(es))",
            scores=scores,
            confidence=min(1.0, planning / 3),
        )

    if len(domains_hit) > 1:
        # Only go direct to orchestrator when BOTH domains have strong signal (each ≥ 2
        # keyword matches). A single "invoice" keyword in a how-to question is noise, not
        # a genuine multi-domain request — fall through to the LLM router instead.
        min_domain_score = min(expert_scores[n] for n in domains_hit)
        if min_domain_score >= 2:
            detail = ", ".join(f"{n}={expert_scores[n]}" for n in domains_hit)
            return RoutingDecision(
                mode="planned",
                selected_agent="orchestrator_agent",
                reason=f"Both domains have strong signal ({detail})",
                scores=scores,
                confidence=0.5,
            )
        # Ambiguous overlap — LLM router will classify
        return RoutingDecision(
            mode="no_signal",
            selected_agent="orchestrator_agent",
            reason="Multi-domain overlap but weak secondary signal — LLM fallback",
            scores=scores,
            confidence=0.0,
        )

    if total == 0:
        # No domain signal — LLM router will classify before any expert is called
        return RoutingDecision(
            mode="no_signal",
            selected_agent="orchestrator_agent",
            reason="No domain terms matched — LLM fallback via orchestrator",
            scores=scores,
            confidence=0.0,
        )

    # Single domain — pick the highest scorer
    best = max(expert_scores, key=lambda n: expert_scores[n])
    return RoutingDecision(
        mode="direct",
        selected_agent=best,
        reason=f"{best} terms matched ({expert_scores[best]}), no other domain",
        scores=scores,
        confidence=expert_scores[best] / total,
    )
