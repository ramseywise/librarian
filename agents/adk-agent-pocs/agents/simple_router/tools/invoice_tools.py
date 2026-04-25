# tools/invoice_tools.py
# Invoice domain tools. Stubs with realistic shapes for POC.

import json
import sys
from google.adk.tools import FunctionTool, ToolContext

from .context_tools import PUBLIC_SESSION_FACTS, set_fact as _set_fact


def _dbg(msg: str) -> None:
    print(f"\033[33m[DBG] {msg}\033[0m", file=sys.stderr, flush=True)


def note_invoice_id(invoice_id: str, tool_context: ToolContext) -> dict:
    """Persist a user-stated invoice ID into shared facts for future turns."""
    _dbg(f"note_invoice_id [{tool_context.agent_name}] → {invoice_id!r}")
    _set_fact(
        "invoice",
        json.dumps({"id": invoice_id}),
        f"Invoice ID stated by user: {invoice_id}",
        tool_context,
    )
    return {"status": "noted", "invoice_id": invoice_id}


def get_invoice_details(invoice_id: str, tool_context: ToolContext) -> dict:
    """Load normalized invoice details by invoice ID."""
    _dbg(f"get_invoice_details [{tool_context.agent_name}] invoice_id={invoice_id!r}")
    raw = {
        "invoice_id": invoice_id,
        "status": "draft",
        "vendor_name": "Acme",
        "amount": 1250.00,
        "due_date": "2026-04-01",
        "vat_rate": None,
        "missing_fields": ["vat_rate"],
    }
    invoice_obj = {
        "id": raw["invoice_id"],
        "status": raw["status"],
        "vendor_name": raw["vendor_name"],
        "amount": str(raw["amount"]),
        "due_date": raw["due_date"],
        "vat_rate": raw["vat_rate"],
        "missing_fields": raw.get("missing_fields", []),
    }
    _set_fact(
        "invoice",
        json.dumps(invoice_obj),
        f"Full invoice data for invoice #{invoice_id}",
        tool_context,
    )
    _dbg(f"get_invoice_details [{tool_context.agent_name}] → {raw}")
    return raw


def validate_invoice(invoice_id: str, tool_context: ToolContext) -> dict:
    """Run validation checks on an invoice and return a list of issues."""
    _dbg(f"validate_invoice [{tool_context.agent_name}] invoice_id={invoice_id!r}")
    session_facts = tool_context.state.get(PUBLIC_SESSION_FACTS, {})
    invoice_entry = session_facts.get("invoice", {})
    try:
        invoice_obj = json.loads(invoice_entry.get("value", "{}"))
        issues = invoice_obj.get("missing_fields", [])
        if not isinstance(issues, list):
            issues = []
    except (json.JSONDecodeError, TypeError):
        issues = []
    result = {
        "invoice_id": invoice_id,
        "valid": len(issues) == 0,
        "issues": issues,
    }
    _set_fact(
        "validation_result", str(result), "Invoice validation result", tool_context
    )
    _dbg(f"validate_invoice [{tool_context.agent_name}] → {result}")
    return result


def update_invoice_field(
    invoice_id: str,
    field_name: str,
    value: str,
    tool_context: ToolContext,
) -> dict:
    """Update a mutable invoice field after user confirmation."""
    _dbg(
        f"update_invoice_field [{tool_context.agent_name}] {invoice_id}.{field_name}={value!r}"
    )
    session_facts = tool_context.state.get(PUBLIC_SESSION_FACTS, {})
    invoice_entry = session_facts.get("invoice", {})
    try:
        invoice_obj = json.loads(invoice_entry.get("value", "{}"))
    except (json.JSONDecodeError, TypeError):
        invoice_obj = {}
    invoice_obj[field_name] = value
    if field_name in invoice_obj.get("missing_fields", []):
        invoice_obj["missing_fields"] = [
            f for f in invoice_obj["missing_fields"] if f != field_name
        ]
    _set_fact(
        "invoice",
        json.dumps(invoice_obj),
        f"Full invoice data for invoice #{invoice_id}",
        tool_context,
    )
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
    """Require explicit user confirmation only for financially sensitive fields.

    NOTE: If new financial fields are added to the invoice schema, add them here.
    Fields NOT in this set can be updated without user confirmation.
    """
    return field_name in {"vat_rate", "due_date", "amount", "vendor_name"}


# Rebind: FunctionTool captures the function object before the name is reassigned.
update_invoice_field = FunctionTool(
    update_invoice_field,
    require_confirmation=_confirm_invoice_update,
)
