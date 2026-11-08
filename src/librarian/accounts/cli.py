"""`librarian users add|list|invite|invites|promote` and `librarian keys create|list|revoke`."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from datetime import datetime

from librarian.log_config import configure_logging


def _when(ts: datetime | None) -> str:
    return ts.strftime("%Y-%m-%d %H:%M") if ts else "-"


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="librarian", description="Accounts and API keys.")
    groups = ap.add_subparsers(dest="group", required=True)

    users = groups.add_parser("users").add_subparsers(dest="verb", required=True)
    add = users.add_parser("add", help="create a user")
    add.add_argument("email")
    add.add_argument("--name")
    add.add_argument("--role", choices=["member", "admin"], default="member")
    add.add_argument("--timezone", default="UTC", help="IANA name, e.g. Europe/Copenhagen")
    users.add_parser("list", help="every user")
    inv = users.add_parser("invite", help="let an email sign in for the first time")
    inv.add_argument("email")
    users.add_parser("invites", help="the invite list")
    promote = users.add_parser("promote", help="make a user an admin (or --member)")
    promote.add_argument("email")
    promote.add_argument("--member", action="store_true", help="make them a member instead")

    keys = groups.add_parser("keys").add_subparsers(dest="verb", required=True)
    create = keys.add_parser("create", help="a new API key for a user, printed once")
    create.add_argument("email")
    create.add_argument("--name", help="what the key is for, e.g. 'laptop MCP'")
    create.add_argument("--scopes", default="read write", help="'read' or 'read write' (default)")
    ls = keys.add_parser("list", help="keys, without their secrets")
    ls.add_argument("email", nargs="?")
    revoke = keys.add_parser("revoke", help="revoke a key by its id")
    revoke.add_argument("key_id", help="the id `keys list` shows (or the whole key)")

    args = ap.parse_args(list(argv) if argv is not None else None)
    configure_logging()

    from librarian import accounts
    from librarian.db import get_engine

    engine = get_engine()
    try:
        if args.group == "users" and args.verb == "add":
            user = accounts.add_user(
                engine, args.email, name=args.name, role=args.role, timezone=args.timezone
            )
            print(f"added {user.email} ({user.role}, {user.timezone})")
        elif args.group == "users" and args.verb == "invite":
            if accounts.invite(engine, args.email):
                accounts.audit(engine, "invite", target=accounts.normalize_email(args.email))
                print(f"invited {accounts.normalize_email(args.email)}")
            else:
                print(f"{args.email} is already invited or a user")
        elif args.group == "users" and args.verb == "invites":
            for i in accounts.list_invites(engine):
                state = f"used {_when(i.used_at)}" if i.used_at else "open"
                print(f"{i.email}\t{state}\tinvited {_when(i.created_at)}")
        elif args.group == "users" and args.verb == "promote":
            user = accounts.set_role(engine, args.email, "member" if args.member else "admin")
            accounts.audit(engine, "promote", target=f"{user.email}:{user.role}")
            print(f"{user.email} is now {user.role}")
        elif args.group == "users":
            for u in accounts.list_users(engine):
                seen = _when(u.last_seen_at)
                print(f"{u.email}\t{u.role}\t{u.timezone}\tlast seen {seen}\t{u.name or ''}")
        elif args.verb == "create":
            info, key = accounts.create_key(engine, args.email, scopes=args.scopes, name=args.name)
            accounts.audit(engine, "key_create", target=info.id)
            print(f"key {info.id} for {info.email} ({' '.join(sorted(info.scopes))}):")
            print(key)
            print("It is shown once and cannot be recovered; store it now.", file=sys.stderr)
        elif args.verb == "list":
            for k in accounts.list_keys(engine, args.email):
                state = f"revoked {_when(k.revoked_at)}" if k.revoked_at else "live"
                print(
                    f"{k.id}\t{k.email}\t{' '.join(sorted(k.scopes))}\t{state}\t"
                    f"created {_when(k.created_at)}\tlast used {_when(k.last_used_at)}\t"
                    f"{k.name or ''}"
                )
        elif not accounts.revoke_key(engine, args.key_id):
            print(f"librarian keys: no live key {args.key_id!r}", file=sys.stderr)
            return 1
        else:
            accounts.audit(engine, "key_revoke", target=args.key_id)
            print(f"revoked {args.key_id}")
    except accounts.AccountError as e:
        print(f"librarian {args.group}: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
