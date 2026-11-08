"""Accounts: users and API keys in the user-state database.

A request acts as one `User`: the holder of an `lk_` key, or the owner (an admin, named by
`LIBRARIAN_OWNER_EMAIL`) for the bootstrap `LIBRARIAN_API_TOKEN` and for open local mode. The API
resolves it in `librarian.api.security.current_user`. Imports only `librarian.db` and config.
"""

from librarian.accounts.keys import (
    KeyInfo,
    create_key,
    is_api_key,
    list_keys,
    resolve_key,
    revoke_key,
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
)

__all__ = [
    "ALL_SCOPES",
    "AccountError",
    "KeyInfo",
    "User",
    "add_user",
    "create_key",
    "ensure_owner",
    "get_user",
    "get_user_by_id",
    "is_api_key",
    "list_keys",
    "list_users",
    "resolve_key",
    "revoke_key",
]
