# tools/context_tools.py
# Tools that read shared session state at runtime.
# Called AFTER the cache lookup — zero cache fingerprint impact.

from google.adk.tools import ToolContext


def get_conversation_context(tool_context: ToolContext) -> dict:
    """Return the conversation log and current facts from shared session state.

    Call this at the start of your turn to understand what prior agents have
    established. Do not repeat work that is already in the log.
    """
    result = {
        "conversation_log": tool_context.state.get("public:conversation_log", []),
        "facts": tool_context.state.get("public:facts", {}),
        "open_questions": tool_context.state.get("public:open_questions", []),
    }
    task_note = tool_context.state.get("public:task_note")
    if task_note:
        result["task_note"] = task_note
    return result


def signal_follow_up(tool_context: ToolContext) -> dict:
    """Signal that you are asking the user a clarifying question.

    Call this whenever your response ends with a question to the user rather
    than a final answer. The router will direct the user's next reply back to
    you automatically — no need for the user to restate context.

    Do NOT call this if you have already produced a complete answer.
    """
    agent_name = tool_context.agent_name
    tool_context.state["public:follow_up_agent"] = agent_name
    return {"status": "follow_up_registered", "agent": agent_name}


def request_reroute(reason: str, tool_context: ToolContext) -> dict:
    """Signal to the router that this request needs a different agent.

    Call this when the request is outside your domain or requires multi-domain
    coordination. The router will escalate to the orchestrator, which has full
    context and will re-route or coordinate correctly.

    Do NOT call this after you have already produced a partial answer — stop
    immediately and call this before generating any response text.

    Args:
        reason: Short description of why rerouting is needed, e.g.
                "Request requires UI guidance — outside invoice domain."
    """
    tool_context.state["public:routing_escalation"] = {"reason": reason}
    return {"status": "escalation_requested", "reason": reason}
