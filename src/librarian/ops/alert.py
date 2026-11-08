"""Tell the owner a job failed, through the Resend sender the sign-in mail already uses."""

from __future__ import annotations

import httpx

from librarian.accounts import mailer
from librarian.config import Settings
from librarian.log_config import get_logger

log = get_logger(__name__)

_PLACEHOLDER_OWNER = "owner@localhost"


def send_alert(settings: Settings, subject: str, text: str) -> bool:
    """Email the owner. False (and a log line) when mail is not configured or Resend refuses."""
    to = settings.owner_email
    if not (settings.resend_api_key and settings.email_from) or to == _PLACEHOLDER_OWNER:
        log.warning("ops.alert.skipped", reason="mail or LIBRARIAN_OWNER_EMAIL not configured")
        return False
    try:
        with httpx.Client(timeout=mailer.TIMEOUT_S, transport=mailer.transport) as client:
            resp = client.post(
                mailer.RESEND_URL,
                headers={"Authorization": f"Bearer {settings.resend_api_key}"},
                json={"from": settings.email_from, "to": [to], "subject": subject, "text": text},
            )
    except httpx.HTTPError as e:
        log.error("ops.alert.failed", error=str(e))
        return False
    if resp.status_code >= 300:
        log.error("ops.alert.failed", status=resp.status_code)
        return False
    log.info("ops.alert.sent", status=resp.status_code)
    return True
