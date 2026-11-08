"""`ops backup`: dump the database, describe it in a manifest, encrypt with age, upload."""

from __future__ import annotations

import tempfile
from datetime import UTC, datetime
from pathlib import Path

from librarian.config import Settings, get_release
from librarian.db.engine import database_url
from librarian.log_config import get_logger
from librarian.ops import dbtools, proc
from librarian.ops.manifest import MANIFEST_SUFFIX, Manifest, make_base, sha256_file
from librarian.ops.proc import OpsError
from librarian.ops.storage import Storage, open_storage

log = get_logger(__name__)


def encrypt(src: Path, dest: Path, recipient: str) -> None:
    """age to a public key: the host never holds the private key."""
    proc.run(["age", "--recipient", recipient, "--output", str(dest), str(src)])


def decrypt(src: Path, dest: Path, identity: Path) -> None:
    proc.run(["age", "--decrypt", "--identity", str(identity), "--output", str(dest), str(src)])


def run_backup(
    settings: Settings,
    *,
    unencrypted: bool = False,
    now: datetime | None = None,
    storage: Storage | None = None,
    url: str | None = None,
) -> Manifest:
    """Take one backup and return its manifest. OpsError on any failure; nothing half-uploaded is
    advertised, because the manifest is uploaded last and listings key on it."""
    recipient = settings.backup_age_recipient
    if not unencrypted and not recipient:
        raise OpsError(
            "LIBRARIAN_BACKUP_AGE_RECIPIENT is not set (an age public key); "
            "use --unencrypted only for a local drill"
        )
    store = storage or open_storage(settings)
    url = url or database_url()
    now = now or datetime.now(UTC)
    base = make_base(now, get_release())
    log.info("ops.backup.start", base=base, encrypted=not unencrypted)

    with tempfile.TemporaryDirectory(prefix="librarian-backup-") as tmp:
        work = Path(tmp)
        dump = work / f"{base}.dump"
        snap = dbtools.dump_database(url, dump)
        manifest = Manifest(
            base=base,
            dump_object=f"{base}.dump" if unencrypted else f"{base}.dump.age",
            created_at=now,
            release=get_release(),
            dialect=snap.dialect,
            alembic_head=snap.revision,
            tables=snap.counts,
            dump_sha256=sha256_file(dump),
            dump_bytes=dump.stat().st_size,
            encrypted=not unencrypted,
        )
        shipped = dump
        if not unencrypted:
            shipped = work / manifest.dump_object
            encrypt(dump, shipped, recipient)
            manifest.encrypted_sha256 = sha256_file(shipped)
        manifest_file = work / f"{base}{MANIFEST_SUFFIX}"
        manifest_file.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
        store.put(shipped, manifest.dump_object)
        store.put(manifest_file, manifest_file.name)

    log.info(
        "ops.backup.done",
        base=base,
        dialect=manifest.dialect,
        tables=len(manifest.tables),
        rows=sum(manifest.tables.values()),
        bytes=manifest.dump_bytes,
    )
    return manifest
