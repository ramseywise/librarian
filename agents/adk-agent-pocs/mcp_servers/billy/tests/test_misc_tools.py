"""Unit tests for email, invitation, and support-knowledge tools."""

from unittest.mock import patch

import pytest
from playground.agent_poc.mcp_servers.billy.app.tools.emails import (
    send_invoice_by_email,
)
from playground.agent_poc.mcp_servers.billy.app.tools.invitations import (
    _INVITATIONS,
    invite_user,
)
from playground.agent_poc.mcp_servers.billy.app.tools.support_knowledge import (
    fetch_support_knowledge,
)

_FAKE_KB_RESULT = [
    {
        "score": 0.9,
        "content": {"text": "Opret din første faktura i Billy."},
        "location": {"webLocation": {"url": "https://billy.dk/support/faktura"}},
        "metadata": {"title": "Faktura guide"},
    }
]

# ---------------------------------------------------------------------------
# Email tool
# ---------------------------------------------------------------------------


class TestSendInvoiceByEmail:
    def test_known_contact_succeeds(self):
        result = send_invoice_by_email(
            invoice_id="inv_001",
            contact_id="cus_001",
            email_subject="Your invoice",
            email_body="Please pay.",
        )
        assert result["success"] is True
        assert result["invoice_id"] == "inv_001"
        assert result["sent_state"] == "sent"
        assert "kontakt@acme.dk" in result["message"]

    def test_unknown_contact_fails(self):
        result = send_invoice_by_email(
            invoice_id="inv_001",
            contact_id="cus_999",
            email_subject="X",
            email_body="Y",
        )
        assert result["success"] is False
        assert "error" in result

    def test_all_seeded_contacts_have_email(self):
        for contact_id in ("cus_001", "cus_002", "cus_003"):
            result = send_invoice_by_email(contact_id, contact_id, "x", "y")
            assert result["success"] is True


# ---------------------------------------------------------------------------
# Invitation tool
# ---------------------------------------------------------------------------


class TestInviteUser:
    @pytest.fixture(autouse=True)
    def reset_invitations(self):
        original = _INVITATIONS[:]
        yield
        _INVITATIONS[:] = original

    def test_returns_success(self):
        result = invite_user("alice@example.com")
        assert result["success"] is True
        assert result["email"] == "alice@example.com"
        assert "invitation_id" in result
        assert "created_time" in result

    def test_invitation_stored(self):
        invite_user("bob@example.com")
        assert any(i["email"] == "bob@example.com" for i in _INVITATIONS)

    def test_unique_invitation_ids(self):
        r1 = invite_user("a@x.com")
        r2 = invite_user("b@x.com")
        assert r1["invitation_id"] != r2["invitation_id"]


# ---------------------------------------------------------------------------
# Support knowledge tool
# ---------------------------------------------------------------------------


class TestFetchSupportKnowledge:
    async def test_returns_list(self):
        with patch(
            "app.tools.support_knowledge._retrieve_from_kb_raw",
            return_value=_FAKE_KB_RESULT,
        ):
            result = await fetch_support_knowledge(["faktura"])
        assert isinstance(result, list)
        assert len(result) > 0

    async def test_passage_structure(self):
        with patch(
            "app.tools.support_knowledge._retrieve_from_kb_raw",
            return_value=_FAKE_KB_RESULT,
        ):
            result = await fetch_support_knowledge(["opret faktura"])
        passage = result[0]
        assert "passage" in passage
        assert "score" in passage
        assert "url" in passage
        assert "query" in passage
        assert "text" in passage

    async def test_relevant_passage_returned(self):
        with patch(
            "app.tools.support_knowledge._retrieve_from_kb_raw",
            return_value=_FAKE_KB_RESULT,
        ):
            result = await fetch_support_knowledge(["opret faktura"])
        assert any("faktura" in p["text"].lower() for p in result)

    async def test_fallback_when_no_match(self):
        with patch(
            "app.tools.support_knowledge._retrieve_from_kb_raw", return_value=[]
        ):
            result = await fetch_support_knowledge(["xyzzy_no_match_abc"])
        assert isinstance(result, list)
        assert len(result) == 0

    async def test_multiple_queries(self):
        with patch(
            "app.tools.support_knowledge._retrieve_from_kb_raw",
            return_value=_FAKE_KB_RESULT,
        ):
            result = await fetch_support_knowledge(["send", "email", "mail"])
        assert isinstance(result, list)
