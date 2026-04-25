"""Tests for the invite_user tool."""

# pylint: disable=no-self-use,too-few-public-methods
import pytest

from playground.agent_poc.agents.billy_assistant.tools.invitations import invite_user


class TestInviteUser:
    """Tests for `invite_user`."""

    @pytest.mark.parametrize(
        "email",
        [
            "alice@example.dk",
            "bob.smith@corp.com",
            "user+tag@domain.org",
        ],
    )
    def test_invite_returns_success(self, email: str):
        """Any email address produces a successful invitation response."""
        result = invite_user(email=email)
        assert result["success"] is True
        assert result["email"] == email

    def test_invitation_id_is_present(self):
        """The response includes a non-empty invitationId."""
        result = invite_user(email="test@example.dk")
        assert result["invitationId"]

    def test_invitation_ids_are_unique(self):
        """Two separate invitations produce different IDs."""
        r1 = invite_user(email="a@example.dk")
        r2 = invite_user(email="b@example.dk")
        assert r1["invitationId"] != r2["invitationId"]

    def test_confirmation_message_contains_email(self):
        """The confirmation message references the invited address."""
        email = "new.user@company.dk"
        result = invite_user(email=email)
        assert email in result["message"]

    def test_created_time_is_set(self):
        """The response includes a non-empty createdTime timestamp."""
        result = invite_user(email="ts@example.dk")
        assert result["createdTime"]
