"""Send the sign-in email through Resend's HTTP API. On when RESEND_API_KEY and EMAIL_FROM are set.

The link is the only secret in the message; it is never logged.
"""

from __future__ import annotations

import html

import httpx

from librarian.config import Settings
from librarian.log_config import get_logger

log = get_logger(__name__)

RESEND_URL = "https://api.resend.com/emails"
TIMEOUT_S = 10.0
# Tests replace this with an httpx.MockTransport; None is the real network.
transport: httpx.BaseTransport | None = None


class MailError(RuntimeError):
    pass


def send_sign_in_link(settings: Settings, to: str, link: str, minutes: int) -> None:
    """Email `to` the sign-in `link`; MailError if Resend does not accept it."""
    text = (
        f"Sign in to Librarian:\n\n{link}\n\n"
        f"The link works once, for {minutes} minutes. If you did not ask for it, ignore this email."
    )
    body = (
        f'<p><a href="{html.escape(link)}">Sign in to Librarian</a></p>'
        f"<p>The link works once, for {minutes} minutes. "
        "If you did not ask for it, ignore this email.</p>"
    )
    try:
        with httpx.Client(timeout=TIMEOUT_S, transport=transport) as client:
            resp = client.post(
                RESEND_URL,
                headers={"Authorization": f"Bearer {settings.resend_api_key}"},
                json={
                    "from": settings.email_from,
                    "to": [to],
                    "subject": "Your Librarian sign-in link",
                    "text": text,
                    "html": body,
                },
            )
    except httpx.HTTPError as e:
        raise MailError(f"Resend unreachable: {e}") from e
    if resp.status_code >= 300:
        raise MailError(f"Resend answered {resp.status_code}")
    log.info("auth.email.sent", status=resp.status_code)
