"""Invitation tools for the Billy accounting system."""

import uuid
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Mock state
# ---------------------------------------------------------------------------

_MOCK_INVITATIONS: list[dict] = []


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


def invite_user(email: str) -> dict:
    """Invites a user to the organization as a collaborator by email.

    The invited user will receive an email to join the organization.

    Args:
        email: The email address of the user to invite.

    Returns:
        Dict with success status, invitationId, email, createdTime, and message.
    """
    invitation_id = str(uuid.uuid4())
    created_time = datetime.now(timezone.utc).isoformat()

    invitation = {
        "id": invitation_id,
        "email": email,
        "userRole": "collaborator",
        "createdTime": created_time,
    }
    _MOCK_INVITATIONS.append(invitation)

    return {
        "success": True,
        "invitationId": invitation_id,
        "email": email,
        "createdTime": created_time,
        "message": f"Invitation sent to {email} as a collaborator.",
    }
