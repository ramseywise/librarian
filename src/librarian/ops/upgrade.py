"""`ops upgrade <image-tag>`: the backup gate that comes before an image change.

The Docker half (pull, `compose up -d`, wait on /readyz, roll back to the previous tag) is in the
`./librarian` wrapper, because only the host can run it. This module decides whether the wrapper
may proceed: a backup younger than the freshness window exists, or one is taken now.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from librarian.config import Settings
from librarian.log_config import get_logger
from librarian.ops.backup import run_backup
from librarian.ops.manifest import MANIFEST_SUFFIX, base_of, stamp_of
from librarian.ops.proc import OpsError
from librarian.ops.storage import Storage, open_storage

log = get_logger(__name__)

_TAG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:/@-]{0,255}$")


class StaleBackupError(OpsError):
    """No backup inside the freshness window and the caller asked not to take one."""


@dataclass(frozen=True)
class Gate:
    base: str
    taken: bool
    age_s: float


def check_tag(tag: str) -> str:
    if not _TAG_RE.match(tag):
        raise OpsError(f"not an image tag: {tag!r}")
    return tag


def latest_backup(storage: Storage) -> tuple[str, datetime] | None:
    """Newest complete backup (one with a manifest), by the timestamp in its name."""
    found = [
        (base, when)
        for name in storage.names()
        if name.endswith(MANIFEST_SUFFIX) and (when := stamp_of(base := base_of(name))) is not None
    ]
    return max(found, key=lambda item: item[1]) if found else None


def ensure_fresh_backup(
    settings: Settings,
    *,
    max_age_min: int | None = None,
    take: bool = True,
    now: datetime | None = None,
    storage: Storage | None = None,
    url: str | None = None,
    unencrypted: bool = False,
) -> Gate:
    """Return the backup the upgrade may rely on, taking a new one unless `take` is False."""
    store = storage or open_storage(settings)
    now = now or datetime.now(UTC)
    window = timedelta(minutes=settings.backup_max_age_min if max_age_min is None else max_age_min)
    newest = latest_backup(store)
    if newest is not None and now - newest[1] <= window:
        age = (now - newest[1]).total_seconds()
        log.info("ops.upgrade.backup_fresh", base=newest[0], age_s=age)
        return Gate(newest[0], False, age)
    if not take:
        raise StaleBackupError(
            f"no backup younger than {window.total_seconds() / 60:.0f} minutes "
            "(run `./librarian backup`, or drop --no-take)"
        )
    manifest = run_backup(settings, now=now, storage=store, url=url, unencrypted=unencrypted)
    return Gate(manifest.base, True, 0.0)
