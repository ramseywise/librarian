# tools/invoice_tools.py
# Invoice domain tools. Stubs with realistic shapes for POC.

from google.adk.tools import FunctionTool, ToolContext


def get_invoice_details(invoice_id: str, tool_context: ToolContext) -> dict:
    """Load normalized invoice details by invoice ID."""
    invoice = {
        "invoice_id": invoice_id,
        "status": "draft",
        "vendor_name": "Acme",
        "amount": 1250.00,
        "due_date": "2026-04-01",
        "vat_rate": None,
        "missing_fields": ["vat_rate"],
    }
    # Merge into shared facts so other agents can reuse without re-fetching
    tool_context.state["public:facts"] = {
        **tool_context.state.get("public:facts", {}),
        **invoice,
    }
    return invoice


def validate_invoice(invoice_id: str, tool_context: ToolContext) -> dict:
    """Run validation checks on an invoice and return a list of issues."""
    facts = tool_context.state.get("public:facts", {})
    issues = facts.get("missing_fields", [])
    result = {
        "invoice_id": invoice_id,
        "valid": len(issues) == 0,
        "issues": issues,
    }
    tool_context.state["public:facts"] = {**facts, "validation_result": result}
    return result


def update_invoice_field(
    invoice_id: str,
    field_name: str,
    value: str,
    tool_context: ToolContext,
) -> dict:
    """Update a mutable invoice field after user confirmation."""
    facts = tool_context.state.get("public:facts", {})
    tool_context.state["public:facts"] = {**facts, field_name: value}
    return {
        "status": "updated",
        "invoice_id": invoice_id,
        "field_name": field_name,
        "value": value,
    }


def _confirm_invoice_update(
    invoice_id: str,
    field_name: str,
    value: str,
    tool_context: ToolContext,
) -> bool:
    """Require explicit user confirmation only for financially sensitive fields."""
    return field_name in {"vat_rate", "due_date", "amount", "vendor_name"}


# Rebind: FunctionTool captures the function object before the name is reassigned.
# The tool is now named "update_invoice_field" — both to the model and the firewall.
update_invoice_field = FunctionTool(
    update_invoice_field,
    require_confirmation=_confirm_invoice_update,
)
