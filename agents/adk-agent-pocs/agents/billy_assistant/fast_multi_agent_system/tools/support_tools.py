# tools/support_tools.py
# Product/UI support tools. Stubs with realistic shapes for POC.

from google.adk.tools import ToolContext

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
}


def get_support_steps(issue_code: str, tool_context: ToolContext) -> dict:
    """Return product workflow steps for a known issue code.

    issue_code must be one of: missing_vat, approval_failed, upload_invoice.
    Returns found=false when the code is not recognised — do NOT answer the
    user without a found=true result.
    """
    # Normalise: lowercase and replace spaces/hyphens with underscores.
    key = issue_code.lower().replace(" ", "_").replace("-", "_")
    if key in _STEPS_DB:
        return {"found": True, "issue_code": key, "steps": _STEPS_DB[key]}
    return {"found": False, "issue_code": key, "steps": []}


def get_help_article(topic: str, tool_context: ToolContext) -> dict:
    """Fetch a help article snippet by topic keyword.

    POC stub — no real knowledge base is connected yet.
    Always returns found=false. Do NOT answer the user from this result.
    """
    return {"found": False, "topic": topic}
