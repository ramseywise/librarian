# tools/context_tools.py
# Cross-cutting tools available to all agents.

import json
import sys
import time

from google.adk.tools import ToolContext

# State keys shared across agents
PUBLIC_SESSION_FACTS = (
    "public:session_facts"  # {key: {status, description, value, fact_id?}}
)
PUBLIC_FACT_HISTORY = (
    "public:fact_history"  # [{fact_id, supersedes_fact_id, description, fact}]
)
PUBLIC_FOLLOW_UP_AGENT = "public:follow_up_agent"
PUBLIC_REROUTE_KEY = (
    "public:reroute_requested"  # set by signal_reroute(); router skips shortcuts
)
PRIOR_FOLLOW_UP_KEY = (
    "router:prior_follow_up"  # persists after router consumes PUBLIC_FOLLOW_UP_AGENT
)
_CTX_LOADED_KEY = "_ctx_loaded_inv"  # tracks which invocation already loaded context


def _dbg(msg: str) -> None:
    print(f"\033[36m[DBG] {msg}\033[0m", file=sys.stderr, flush=True)


def _walk_chain(start_id: str, history_by_id: dict) -> list:
    """Walk the supersedes chain from start_id, returning fact values oldest-first."""
    chain: list = []
    current_id: str | None = start_id
    while current_id:
        entry = history_by_id.get(current_id)
        if not entry:
            break
        chain.append(entry.get("fact"))
        current_id = entry.get("supersedes_fact_id")
    return list(reversed(chain))


def _render_value(raw):
    """Expand a JSON string to a dict for display; return plain strings unchanged."""
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
    except (json.JSONDecodeError, TypeError):
        pass
    return raw


def _build_summary(facts: dict) -> str:
    """Build a plain-English one-liner from the structured facts dict.

    Placed under the special key "_summary" in the injected facts so models
    can read current state and history at a glance without navigating nested JSON.

    Example (single invoice):
      'Current: invoice id="10", status="draft", vendor_name="Acme", ...'

    Example (two invoices — prior entry labeled with its id):
      'Current: invoice id="11", ..., vat_rate="None", loaded_at="2026-03-20T15:30Z". \
Prior values — invoice #10 was: status="draft", vendor_name="Acme", amount="1250.0", due_date="2026-04-01", vat_rate="None".'
    """
    current_parts = []
    for k, v in facts.items():
        val = v["value"]
        if isinstance(val, dict) and k == "invoice":
            id_ = val.get("id", "?")
            status = val.get("status", "?")
            vendor = val.get("vendor_name", "?")
            amount = val.get("amount", "?")
            due = val.get("due_date", "?")
            vat = val.get("vat_rate", "null")
            loaded = v.get("loaded_at", "")
            fragment = (
                f'invoice id="{id_}", status="{status}", vendor_name="{vendor}", '
                f'amount="{amount}", due_date="{due}", vat_rate="{vat}"'
            )
            if loaded:
                fragment += f', loaded_at="{loaded}"'
            current_parts.append(fragment)
        else:
            current_parts.append(f'{k}="{val}"')

    history_parts = []
    for k, v in facts.items():
        if not v["previous"]:
            continue
        if k == "invoice":
            # Each prior invoice state gets its own labeled entry so the id is visible.
            for p in v["previous"]:
                if isinstance(p, dict):
                    id_ = p.get("id", "?")
                    s = p.get("status", "?")
                    vendor = p.get("vendor_name", "?")
                    amount = p.get("amount", "?")
                    due = p.get("due_date", "?")
                    vat = p.get("vat_rate", "null")
                    history_parts.append(
                        f'invoice #{id_} was: status="{s}", vendor_name="{vendor}", '
                        f'amount="{amount}", due_date="{due}", vat_rate="{vat}"'
                    )
                else:
                    history_parts.append(f'invoice was: "{p}"')
        else:
            prev_items = [f'"{p}"' for p in v["previous"]]
            history_parts.append(f"{k} was: " + ", ".join(prev_items))

    summary = (
        ("Current: " + ", ".join(current_parts))
        if current_parts
        else "No facts loaded yet."
    )
    if history_parts:
        summary += ". Prior values — " + "; ".join(history_parts) + "."
    return summary


def _flat_facts(session_facts: dict, history: list | None = None) -> dict:
    """Return a uniform {key: {description, loaded_at, set_by, value, previous}} view for the LLM.

    Every fact includes:
      description  — human-readable label set when the fact was stored.
      loaded_at    — ISO-8601 UTC timestamp of the last write (if recorded).
      set_by       — agent name that last wrote this fact (if recorded).
      value        — current fact value; JSON-encoded objects are expanded to dicts.
      previous     — prior values oldest-first; JSON strings are also expanded.

    A top-level "_summary" key contains a plain-English overview so models can
    scan current state and history without navigating nested JSON.
    """
    history_by_id: dict = {}
    if history:
        history_by_id = {e["fact_id"]: e for e in history if e.get("fact_id")}

    result: dict = {}
    for k, v in session_facts.items():
        if not isinstance(v, dict) or "value" not in v:
            continue
        current_value = v["value"]
        fact_id = v.get("fact_id")
        previous: list = []

        if fact_id and history_by_id:
            if v.get("status") == "draft":
                # fact_id is the previous persisted entry — walk the full chain from there.
                previous = _walk_chain(fact_id, history_by_id)
            else:
                # persisted: fact_id is the current history entry; walk from its predecessor.
                curr_entry = history_by_id.get(fact_id)
                if curr_entry and curr_entry.get("supersedes_fact_id"):
                    previous = _walk_chain(
                        curr_entry["supersedes_fact_id"], history_by_id
                    )

        rendered_value = _render_value(current_value)
        rendered_previous = [_render_value(p) for p in previous]
        entry: dict = {"value": rendered_value, "previous": rendered_previous}
        if v.get("description"):
            entry["description"] = v["description"]
        if v.get("loaded_at"):
            entry["loaded_at"] = v["loaded_at"]
        if v.get("set_by"):
            entry["set_by"] = v["set_by"]
        result[k] = entry

    result["_summary"] = _build_summary(result)
    return result


def get_conversation_context(tool_context: ToolContext) -> dict:
    """Return shared state collected so far in this conversation.
    Call this tool AT MOST ONCE per turn, at the very start of your action sequence.
    Do NOT call it again after you have received results from other tools.

    Idempotent per invocation: the first call returns the full context and stamps
    the invocation ID in session state. Any repeat call within the same invocation
    returns an error directing the model to stop and respond.
    """
    inv_id = getattr(tool_context, "invocation_id", None)
    if inv_id is not None and tool_context.state.get(_CTX_LOADED_KEY) == inv_id:
        _dbg(
            f"get_conversation_context [{tool_context.agent_name}] → already loaded this invocation, skipping"
        )
        return {
            "error": "already_called_this_turn",
            "instruction": "You already called get_conversation_context this turn. Do NOT call it again. Stop calling tools and respond to the user using the data you have already collected.",
        }

    follow_up_agent = tool_context.state.get(PUBLIC_FOLLOW_UP_AGENT)
    if follow_up_agent is not None:
        tool_context.state[PUBLIC_FOLLOW_UP_AGENT] = None  # consume
    session_facts = tool_context.state.get(PUBLIC_SESSION_FACTS, {})
    history = tool_context.state.get(PUBLIC_FACT_HISTORY, [])
    flat = _flat_facts(session_facts, history)
    result: dict = {"facts": flat}
    # Only expose follow_up_agent and fact_history to the router — sub-agents
    # don't use them and seeing them causes loops or confusion.
    if tool_context.agent_name == "router_agent":
        result["follow_up_agent"] = follow_up_agent
        # Superseded entries only (non-current), ordered oldest-first.
        superseded_ids = {
            e["supersedes_fact_id"] for e in history if e.get("supersedes_fact_id")
        }
        result["fact_history"] = [
            {"key": e.get("key", e.get("description", "")), "fact": e["fact"]}
            for e in history
            if e.get("fact_id") in superseded_ids
        ]
    _dbg(
        f"get_conversation_context [{tool_context.agent_name}]"
        f" → follow_up={follow_up_agent!r}  session_fact_keys={list(session_facts.keys())}"
    )
    # Structured routing log — always emitted, Cloud Logging-compatible JSON line.
    print(
        json.dumps(
            {
                "event": "routing_context",
                "agent": tool_context.agent_name,
                "invocation_id": inv_id,
                "follow_up_agent": follow_up_agent,
                "session_fact_keys": list(session_facts.keys()),
                "history_fact_count": len(history),
                "ts": time.time(),
            }
        ),
        file=sys.stderr,
        flush=True,
    )
    # Stamp so repeat calls within this invocation are short-circuited.
    if inv_id is not None:
        tool_context.state[_CTX_LOADED_KEY] = inv_id
    return result


_FOLLOW_UP_CALLED_KEY = (
    "_follow_up_called_inv"  # tracks which invocation already called signal_follow_up
)


def signal_follow_up(tool_context: ToolContext) -> dict:
    """Signal that you are asking the user a clarifying question."""
    agent_name = tool_context.agent_name
    inv_id = getattr(tool_context, "invocation_id", None)

    # Idempotency guard: if already called this invocation, return a strong error
    # to break the thinking loop. Mirrors the guard in get_conversation_context.
    if inv_id is not None and tool_context.state.get(_FOLLOW_UP_CALLED_KEY) == inv_id:
        _dbg(
            f"signal_follow_up [{agent_name}] → already called this invocation, returning error"
        )
        return {
            "error": "already_called_this_turn",
            "instruction": (
                "signal_follow_up was already called this turn. "
                "STOP calling tools immediately. "
                "Write your clarifying question to the user and end your turn."
            ),
        }

    tool_context.state[PUBLIC_FOLLOW_UP_AGENT] = agent_name
    # PRIOR_FOLLOW_UP_KEY survives router consumption of PUBLIC_FOLLOW_UP_AGENT.
    # inject_facts_callback reads it at the START of the NEXT agent invocation
    # and adds a _context_note to facts, reminding the agent that a follow-up
    # was pending and it must apply MANDATORY DISAMBIGUATION CHECK before acting.
    # We also store the current invocation_id so inject_facts_callback can skip
    # the _context_note if it runs within the SAME invocation (i.e., between
    # LLM calls of the same agent turn — not across turns).
    tool_context.state[PRIOR_FOLLOW_UP_KEY] = agent_name
    if inv_id is not None:
        tool_context.state[_FOLLOW_UP_CALLED_KEY] = inv_id
        tool_context.state["router:prior_follow_up_inv"] = inv_id
    _dbg(f"signal_follow_up [{agent_name}] → registered (prior_follow_up set)")
    return {
        "status": "follow_up_registered",
        "agent": agent_name,
        "next_action": "Respond to the user. Do NOT call any more tools this turn.",
    }


def signal_reroute(tool_context: ToolContext) -> dict:
    """Signal that this request is outside your domain and must be rerouted.

    Call when the user's message is clearly meant for a different agent —
    not just a missing argument, but a completely different domain.
    The router will skip all shortcuts and use the LLM to find the right
    agent on the next turn.
    """
    agent_name = tool_context.agent_name
    tool_context.state[PUBLIC_FOLLOW_UP_AGENT] = None  # break any follow-up loop
    tool_context.state[PUBLIC_REROUTE_KEY] = True
    _dbg(f"signal_reroute [{agent_name}] → reroute requested")
    return {
        "status": "reroute_requested",
        "next_action": "Write one sentence telling the user you are redirecting them to the right place. STOP. Do NOT call any other tool.",
    }


def set_fact(key: str, value: str, description: str, tool_context: ToolContext) -> dict:
    """Store or update a named fact in the session layer for the current conversation.

    Facts are stored in public:session_facts with status 'draft'. An after-agent
    callback automatically persists them to history once the turn completes.

    key: logical name for the fact (e.g. 'invoice_id').
    value: the fact value to store.
    description: human-readable description of what this fact represents.
    """
    session_facts = dict(tool_context.state.get(PUBLIC_SESSION_FACTS, {}))
    existing = session_facts.get(key)
    # Idempotency: if the value is unchanged and already persisted, skip re-drafting.
    # This prevents duplicate history entries when the same tool is called twice
    # for the same value (e.g. get_invoice_details called on an already-loaded invoice).
    if (
        isinstance(existing, dict)
        and existing.get("value") == value
        and existing.get("status") == "persisted"
    ):
        _dbg(
            f"set_fact [{tool_context.agent_name}] key={key!r} — unchanged persisted value, skipping"
        )
        return {"status": "noted", key: value}
    # Carry forward the existing fact_id so persist_facts_callback can set supersedes_fact_id.
    old_fact_id = existing.get("fact_id") if isinstance(existing, dict) else None
    session_facts[key] = {
        "status": "draft",
        "description": description,
        "value": value,
        "fact_id": old_fact_id,
        "loaded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "set_by": tool_context.agent_name,
    }
    tool_context.state[PUBLIC_SESSION_FACTS] = session_facts
    _dbg(f"set_fact [{tool_context.agent_name}] key={key!r} value={value!r}")
    return {"status": "noted", key: value}


def search_facts(query: str, search_in: str, tool_context: ToolContext) -> dict:
    """Search facts in the session layer, history layer, or both.

    Returns matching facts. History results exclude superseded entries by default.

    query: free-text string to match against fact keys, descriptions, and values.
    search_in: one of 'session', 'history', or 'both'.
    """
    search_in = (search_in or "both").lower().strip()
    query_lower = query.lower()
    results = []

    if search_in in ("session", "both"):
        session_facts = tool_context.state.get(PUBLIC_SESSION_FACTS, {})
        for k, v in session_facts.items():
            if not isinstance(v, dict):
                continue
            desc = str(v.get("description", "")).lower()
            val = str(v.get("value", "")).lower()
            if query_lower in k.lower() or query_lower in desc or query_lower in val:
                results.append({"source": "session", "key": k, **v})

    if search_in in ("history", "both"):
        history = tool_context.state.get(PUBLIC_FACT_HISTORY, [])
        # Build set of superseded fact_ids to exclude.
        superseded_ids = {
            entry["supersedes_fact_id"]
            for entry in history
            if entry.get("supersedes_fact_id")
        }
        for entry in history:
            if entry.get("fact_id") in superseded_ids:
                continue
            desc = str(entry.get("description", "")).lower()
            fact_val = str(entry.get("fact", "")).lower()
            if query_lower in desc or query_lower in fact_val:
                results.append({"source": "history", **entry})

    return {"results": results, "count": len(results)}


def get_latest_fact(key: str, tool_context: ToolContext) -> dict:
    """Retrieve the latest non-superseded version of a fact by logical key.

    Checks the session layer first (most recent); falls back to history.

    key: the logical key used when set_fact was called (e.g. 'invoice_id').
    """
    session_facts = tool_context.state.get(PUBLIC_SESSION_FACTS, {})
    if key in session_facts:
        entry = session_facts[key]
        if isinstance(entry, dict):
            return {"found": True, "source": "session", "key": key, **entry}

    # Fall back to history: reverse walk, skip superseded entries, match by description.
    history = tool_context.state.get(PUBLIC_FACT_HISTORY, [])
    superseded_ids = {
        e["supersedes_fact_id"] for e in history if e.get("supersedes_fact_id")
    }
    for entry in reversed(history):
        if entry.get("fact_id") in superseded_ids:
            continue
        if (
            entry.get("key") == key
            or entry.get("description", "").lower() == key.lower()
        ):
            return {"found": True, "source": "history", **entry}

    return {"found": False, "key": key}
