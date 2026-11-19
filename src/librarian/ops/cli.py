"""`librarian ops backup|restore|upgrade|schedule|list|prune-logs`.

Exit codes: 0 ok, 1 failed (a failed backup also emails the owner), 2 usage, 3 `upgrade --no-take`
found no fresh backup. The `./librarian` wrapper turns these into the compose steps.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from librarian.config import get_settings
from librarian.log_config import configure_logging, get_logger
from librarian.ops import schedule
from librarian.ops.backup import run_backup
from librarian.ops.logs import prune_agent_log
from librarian.ops.proc import OpsError
from librarian.ops.restore import run_restore
from librarian.ops.runner import run_with_alert
from librarian.ops.storage import open_storage
from librarian.ops.upgrade import StaleBackupError, check_tag, ensure_fresh_backup

log = get_logger(__name__)


def _parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="librarian ops", description="Backups, restore, upgrade gate."
    )
    sub = ap.add_subparsers(dest="verb", required=True)

    b = sub.add_parser("backup", help="dump, encrypt with age, upload; alerts the owner on failure")
    b.add_argument("--unencrypted", action="store_true", help="skip age (local drills only)")

    r = sub.add_parser("restore", help="fenced restore into a new database, then swap")
    r.add_argument("object", help="a backup base/object name, or `latest`")
    r.add_argument("--identity", type=Path, help="age private key file (kept off the host)")
    r.add_argument("--replace", action="store_true", help="allow overwriting a database with data")
    r.add_argument("--no-swap", action="store_true", help="verify the restored copy and stop")

    u = sub.add_parser("upgrade", help="backup gate before an image change")
    u.add_argument("image_tag")
    u.add_argument(
        "--max-age-min", type=int, default=None, help="freshness window (setting default 15)"
    )
    u.add_argument(
        "--no-take", action="store_true", help="refuse (exit 3) instead of taking a backup"
    )
    u.add_argument("--unencrypted", action="store_true", help="skip age (local drills only)")

    s = sub.add_parser("schedule", help="run `backup` daily at LIBRARIAN_BACKUP_AT (UTC)")
    s.add_argument("--once", action="store_true", help="wait for the next slot, back up, exit")

    p = sub.add_parser("prune-logs", help="drop agent-log lines older than the retention window")
    p.add_argument(
        "--days", type=int, default=None, help="default LIBRARIAN_AGENT_LOG_RETENTION_DAYS (90)"
    )
    p.add_argument("--dry-run", action="store_true", help="count what would go; change nothing")

    sub.add_parser("list", help="the backups in the bucket, newest last")
    return ap


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(list(argv) if argv is not None else None)
    configure_logging()
    settings = get_settings()
    try:
        if args.verb == "backup":
            manifest = run_with_alert(
                settings, "backup", lambda: run_backup(settings, unencrypted=args.unencrypted)
            )
            if manifest is None:
                return 1
            print(
                f"backup={manifest.base} rows={sum(manifest.tables.values())} head={manifest.alembic_head}"
            )
            return 0
        if args.verb == "restore":
            result = run_restore(
                settings,
                args.object,
                identity=args.identity,
                replace=args.replace,
                swap=not args.no_swap,
            )
            if result.swapped:
                print(f"restored={result.base} previous={result.kept_old}")
                print("next: start the librarian service and wait for /readyz")
            else:
                print(f"verified={result.base} scratch={result.scratch_url}")
            return 0
        if args.verb == "upgrade":
            tag = check_tag(args.image_tag)
            gate = ensure_fresh_backup(
                settings,
                max_age_min=args.max_age_min,
                take=not args.no_take,
                unencrypted=args.unencrypted,
            )
            print(f"backup={gate.base} taken={str(gate.taken).lower()} image={tag}")
            print("next: pull the image, compose up -d, wait for /readyz; roll back on failure")
            return 0
        if args.verb == "schedule":
            schedule.loop(settings, once=args.once)
            return 0
        if args.verb == "prune-logs":
            days = args.days if args.days is not None else settings.agent_log_retention_days
            res = prune_agent_log(settings.logs_dir, days, dry_run=args.dry_run)
            if res.skipped:
                print("another prune is running; nothing done")
                return 0
            verb = "would remove" if args.dry_run else "removed"
            print(f"{verb} {res.removed} agent-log lines older than {days} days; kept {res.kept}")
            return 0
        names = [n for n in open_storage(settings).names() if n.endswith(".manifest.json")]
        print("\n".join(names))
        return 0
    except StaleBackupError as e:
        print(f"librarian ops: {e}", file=sys.stderr)
        return 3
    except OpsError as e:
        log.error("ops.failed", verb=args.verb, error=str(e))
        print(f"librarian ops {args.verb}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
