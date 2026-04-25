# state.py
# All session.state key constants and per-turn helpers.
# No imports from the rest of this package — safe to use anywhere.

# ---------------------------------------------------------------------------
# Public keys — visible to all agents and tools in the session
# ---------------------------------------------------------------------------

PUBLIC_REQUEST = "public:request"  # {"user_text": str}
PUBLIC_ROUTING = "public:routing"  # RoutingDecision serialized: mode, selected_agent, reason, scores, confidence
PUBLIC_PLAN = "public:plan"  # list[str]
PUBLIC_FACTS = "public:facts"  # dict — normalized invoice/support facts
PUBLIC_OPEN_QUESTIONS = "public:open_questions"  # list[str]
PUBLIC_PROPOSED_ACTION = (
    "public:proposed_action"  # dict | None — set by FirewallPlugin before mutations
)
PUBLIC_LAST_SUMMARY = "public:last_agent_summary"  # str — written by output_key on expert agents (direct path)
PUBLIC_INVOICE_HELPER_SUMMARY = "public:invoice_helper_summary"  # str — written by invoice helper inside orchestrator
PUBLIC_SUPPORT_HELPER_SUMMARY = "public:support_helper_summary"  # str — written by support helper inside orchestrator
PUBLIC_FINAL_ANSWER = (
    "public:final_answer"  # str | None — written by output_key on orchestrator
)
PUBLIC_CONVERSATION_LOG = (
    "public:conversation_log"  # list[dict] — compact per-turn record
)
PUBLIC_ROUTING_ESCALATION = "public:routing_escalation"  # {"reason": str} | None — set by agent, cleared by router
PUBLIC_TASK_NOTE = (
    "public:task_note"  # str | None — injected by router to guide orchestrator
)
PUBLIC_FOLLOW_UP_AGENT = "public:follow_up_agent"  # str | None — set by expert when asking a clarifying question
PUBLIC_LAST_ANSWER = "public:last_answer"  # str — last visible answer shown to user (persists across turns for router context)

# ---------------------------------------------------------------------------
# Private prefixes — local to one agent, never read by others
# ---------------------------------------------------------------------------

PRIVATE_INVOICE = "private:invoice:"
PRIVATE_SUPPORT = "private:support:"
PRIVATE_ORCHESTRATOR = "private:orchestrator:"
PRIVATE_FIREWALL = "private:firewall:"

# ---------------------------------------------------------------------------
# Temp prefix — per-invocation, not persisted, shared across sub-calls
# ---------------------------------------------------------------------------

TEMP_PREFIX = "temp:"

# ---------------------------------------------------------------------------
# Reroute reason values — passed to request_reroute(reason=...) by agents.
# Used in prompt templates as {reroute_<key>} placeholders and matched
# exactly in agent.py escalation logic.
#
# To add a new expert domain:
#   1. Add REROUTE_NEW = "new domain" here.
#   2. Add "reroute_new": REROUTE_NEW to REROUTE_ALL below.
#   3. Reference {reroute_new} in any agent prompt that may need to reroute there.
#   No existing agent .py files need updating — they all call format(**REROUTE_ALL).
# ---------------------------------------------------------------------------

REROUTE_INVOICE = "invoice domain"
REROUTE_SUPPORT = "support domain"
REROUTE_MULTI = "multi-domain"

# Flat dict used as **kwargs for prompt template injection in all agent modules.
# Keys match the {placeholder} names used in .txt prompt files.
REROUTE_ALL: dict[str, str] = {
    "reroute_invoice": REROUTE_INVOICE,
    "reroute_support": REROUTE_SUPPORT,
    "reroute_multi": REROUTE_MULTI,
}

# ---------------------------------------------------------------------------
# Shared prompt fragments — injected into every expert prompt via {placeholder}.
# Change here to update all expert prompts at once.
# ---------------------------------------------------------------------------

PROMPT_SHARED: dict[str, str] = {
    # Universal context-reading instruction.  Every expert must call this first.
    "context_rules": (
        "- Call get_conversation_context() first. Read the returned conversation_log and facts\n"
        "  to understand what prior agents have established. Do not repeat work already logged.\n"
        '  If the result contains a "task_note" field, treat it as your primary directive.'
    ),
    # Universal closure rules.  Place at the end of every expert's Rules section.
    "common_rules": (
        "- NEVER mention routing, rerouting, specialists, or handoffs to the user — these are\n"
        "  invisible infrastructure. If you must reroute, call request_reroute() silently and stop.\n"
        "- You MUST always write a non-empty response."
    ),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def init_public_state(state: dict, user_text: str) -> None:
    """Reset per-turn keys and preserve cross-turn keys. Called once per user turn."""
    # Persist the previous turn's visible answer BEFORE resetting — router reads it.
    _prev = state.get(PUBLIC_FINAL_ANSWER) or state.get(PUBLIC_LAST_SUMMARY) or ""
    if _prev:
        state[PUBLIC_LAST_ANSWER] = _prev
    state.setdefault(PUBLIC_LAST_ANSWER, "")

    state[PUBLIC_REQUEST] = {"user_text": user_text}
    state[PUBLIC_ROUTING] = {}
    state[PUBLIC_FINAL_ANSWER] = None
    state[PUBLIC_PROPOSED_ACTION] = None
    state[PUBLIC_ROUTING_ESCALATION] = None
    state[PUBLIC_TASK_NOTE] = None
    # PUBLIC_FOLLOW_UP_AGENT is intentionally NOT reset here — the router reads it
    # on the next turn and clears it explicitly after routing.
    # Preserve cross-turn state — only set if not already present
    state.setdefault(PUBLIC_FACTS, {})
    state.setdefault(PUBLIC_PLAN, [])
    state.setdefault(PUBLIC_OPEN_QUESTIONS, [])
    state.setdefault(PUBLIC_LAST_SUMMARY, "")
    state.setdefault(PUBLIC_CONVERSATION_LOG, [])


def append_conversation_log(
    state: dict, agent: str, request: str, outcome: str
) -> None:
    """Append a compact record of a completed turn. Called by root agent only."""
    log = state.get(PUBLIC_CONVERSATION_LOG, [])
    log.append(
        {
            "turn": len(log) + 1,
            "agent": agent,
            "request": request[:120],
            "outcome": outcome[:200],
        }
    )
    state[PUBLIC_CONVERSATION_LOG] = log
