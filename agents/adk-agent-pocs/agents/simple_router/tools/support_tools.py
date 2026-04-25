# tools/support_tools.py
# Product/UI support tools. Stubs with realistic shapes for POC.

import sys
from google.adk.tools import ToolContext


def _dbg(msg: str) -> None:
    print(f"\033[35m[DBG] {msg}\033[0m", file=sys.stderr, flush=True)


_STEPS_DB = {
    "missing_vat": [
        "Open the invoice details page.",
        "Click 'Edit VAT'.",
        "Choose the correct VAT rate from the dropdown.",
        "Save and click 'Revalidate'.",
    ],
    "approval_failed": [
        "Go to the Approvals section.",
        "Find the blocked invoice.",
        "Check the rejection reason shown in the status column.",
        "Correct the flagged issue and click 'Resubmit'.",
    ],
    "upload_invoice": [
        "Click 'New Invoice' in the top-right corner.",
        "Select 'Upload PDF' or fill in the form manually.",
        "Attach the file and click 'Submit'.",
    ],
    "approve_invoice": [
        "Go to the Approvals section in the left sidebar.",
        "Find the invoice pending your approval.",
        "Review the invoice details and amounts.",
        "Click 'Approve' to confirm, or 'Reject' to decline with a reason.",
    ],
    "export_invoices": [
        "Go to the Invoices list.",
        "Use the filters to select the date range or status.",
        "Click 'Export' in the top-right corner.",
        "Choose the format (CSV or PDF) and click 'Download'.",
    ],
}


def get_support_steps(issue_code: str, tool_context: ToolContext) -> dict:
    """Return product workflow steps for a known issue code."""
    _dbg(f"get_support_steps [{tool_context.agent_name}] issue_code={issue_code!r}")
    query = (
        issue_code.lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("?", "")
        .replace(".", "")
        .replace(",", "")
        .replace("!", "")
    )

    if query in _STEPS_DB:
        result = {"found": True, "issue_code": query, "steps": _STEPS_DB[query]}
        _dbg(f"get_support_steps → exact match: {query}")
        return result

    query_words = set(query.split("_"))
    for db_key, steps in _STEPS_DB.items():
        key_words = set(db_key.split("_"))
        if key_words & query_words == key_words:
            result = {"found": True, "issue_code": db_key, "steps": steps}
            _dbg(f"get_support_steps → keyword match: {db_key}")
            return result

    _dbg(f"get_support_steps → no match for {query!r}")
    return {"found": False, "issue_code": query, "steps": []}


def get_help_article(topic: str, tool_context: ToolContext) -> dict:
    """Fetch a help article snippet by topic keyword. Stub — always found=false."""
    _dbg(f"get_help_article [{tool_context.agent_name}] topic={topic!r}")
    return {"found": False, "topic": topic}
