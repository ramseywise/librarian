"""Accounts: users, sessions, API keys, invites, sign-in links and the audit log.

A request acts as one `User`: the holder of a session cookie or an `lk_` key, or the owner (an
admin, named by `LIBRARIAN_OWNER_EMAIL`) for the bootstrap `LIBRARIAN_API_TOKEN` and for open local
mode. The API resolves it in `librarian.api.security.current_user`. Sign-in itself (OAuth, the
email) is in `accounts.oauth` and `accounts.mailer`. Imports only `librarian.db` and config.
"""

from librarian.accounts.audit_log import Event as AuditEvent
from librarian.accounts.audit_log import recent as audit_events
from librarian.accounts.audit_log import record as audit
from librarian.accounts.invites import Invite, invite, list_invites, may_sign_in, sign_in
from librarian.accounts.keys import (
    KeyInfo,
    create_key,
    is_api_key,
    list_keys,
    resolve_key,
    revoke_key,
)
from librarian.accounts.sessions import (
    create_session,
    resolve_session,
    revoke_session,
    revoke_user_sessions,
)
from librarian.accounts.users import (
    ALL_SCOPES,
    AccountError,
    User,
    add_user,
    ensure_owner,
    get_user,
    get_user_by_id,
    list_users,
    normalize_email,
    set_role,
    touch_seen,
)

__all__ = [
    "ALL_SCOPES",
    "AccountError",
    "AuditEvent",
    "Invite",
    "KeyInfo",
    "User",
    "add_user",
    "audit",
    "audit_events",
    "create_key",
    "create_session",
    "ensure_owner",
    "get_user",
    "get_user_by_id",
    "invite",
    "is_api_key",
    "list_invites",
    "list_keys",
    "list_users",
    "may_sign_in",
    "normalize_email",
    "resolve_key",
    "resolve_session",
    "revoke_key",
    "revoke_session",
    "revoke_user_sessions",
    "set_role",
    "sign_in",
    "touch_seen",
]
