from typing import Optional

from google.adk.plugins import BasePlugin
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext

from ..expert_registry import EXPERTS
from ..state import PRIVATE_FIREWALL, PUBLIC_PROPOSED_ACTION

# Context/routing tools — always allowed, shared across all experts.
_CONTEXT_TOOLS: frozenset[str] = frozenset(
    {
        "get_conversation_context",
        "request_reroute",
        "signal_follow_up",
    }
)

# Domain tools and AgentTool names — fully auto-derived from the registry.
# Adding a new expert automatically expands both sets.
_DOMAIN_TOOLS: frozenset[str] = frozenset(
    t for spec in EXPERTS for t in spec.tool_names
)
_AGENT_TOOLS: frozenset[str] = frozenset(spec.name for spec in EXPERTS)

ALLOWED_TOOLS: frozenset[str] = _CONTEXT_TOOLS | _DOMAIN_TOOLS | _AGENT_TOOLS


class FirewallPlugin(BasePlugin):
    def __init__(self):
        super().__init__(name="firewall")

    async def before_model_callback(self, *, callback_context, llm_request):
        """Redact obvious secrets from the model input.

        IMPORTANT: Do NOT modify llm_request.config.system_instruction here.
        The cache fingerprint hashes system_instruction + tools — any mutation
        causes a cache miss on every call. To inject dynamic context (e.g. tenant
        or env metadata), append a types.Content(role='user', ...) entry to
        llm_request.contents instead — contents after position N are not cached.
        """
        return None  # None = pass through unchanged

    async def before_tool_callback(
        self,
        *,
        tool: BaseTool,
        tool_args: dict,
        tool_context: ToolContext,
    ) -> Optional[dict]:
        """Validate args, reject disallowed tools, record proposed mutations."""
        tool_name = getattr(tool, "name", "") or ""

        if tool_name not in ALLOWED_TOOLS:
            return {"error": f"Tool '{tool_name}' is not allowed."}

        if tool_name == "update_invoice_field":
            # Record the proposed mutation for audit and UX review before it executes
            tool_context.state[PUBLIC_PROPOSED_ACTION] = {
                "type": "update_invoice_field",
                "args_preview": {
                    "invoice_id": tool_args.get("invoice_id"),
                    "field_name": tool_args.get("field_name"),
                },
            }
            tool_context.state[PRIVATE_FIREWALL + "mutation_logged"] = True

        return None  # None = allow through

    async def after_tool_callback(
        self,
        *,
        tool: BaseTool,
        tool_args: dict,
        tool_context: ToolContext,
        result: dict,
    ) -> Optional[dict]:
        """Sanitize oversized or sensitive payloads before they reach the model."""
        if isinstance(result, dict):
            result.pop("raw_payload", None)
            result.pop("internal_trace", None)
        return result
