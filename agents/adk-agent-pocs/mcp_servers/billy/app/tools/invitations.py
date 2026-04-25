"""Invitation stub tools for the Billy MCP server."""

import uuid
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Mock state
# ---------------------------------------------------------------------------

_INVITATIONS: list[dict] = []


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


def invite_user(email: str) -> dict:
    """Invites a user to the organization as a collaborator by email.

    The invited user will receive an email to join the organization.

    Args:
        email: The email address of the user to invite.

    Returns:
        Dict with success status, invitation_id, email, created_time, and message.
    """
    invitation_id = str(uuid.uuid4())
    created_time = datetime.now(timezone.utc).isoformat()

    _INVITATIONS.append(
        {
            "id": invitation_id,
            "email": email,
            "user_role": "collaborator",
            "created_time": created_time,
        }
    )

    return {
        "success": True,
        "invitation_id": invitation_id,
        "email": email,
        "created_time": created_time,
        "message": f"Invitation sent to {email} as a collaborator.",
    }
