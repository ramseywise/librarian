"""`ops restore <object>`: a fenced restore of the database from a backup object.

Fences, in order: the target must be empty or `--replace` given; the dump is decrypted and its
sha256 checked against the manifest; it is loaded into a NEW database (a scratch file or a scratch
Postgres database) and that copy's Alembic revision and row counts must equal the manifest's; only
then does it replace the live database. The old one is kept beside it, never dropped. The wrapper
stops the writers (`librarian` service) before calling this and starts them after.
"""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from sqlalchemy import create_engine, text

from librarian.config import Settings
from librarian.db.engine import database_url
from librarian.log_config import get_logger
from librarian.ops import dbtools, proc
from librarian.ops.backup import decrypt
from librarian.ops.manifest import MANIFEST_SUFFIX, Manifest, base_of, sha256_file
from librarian.ops.proc import OpsError
from librarian.ops.storage import Storage, open_storage

log = get_logger(__name__)


class Target(Protocol):
    def is_empty(self) -> bool: ...
    def scratch(self, tag: str) -> str:
        """Create an empty scratch database beside the target; its URL."""
        ...

    def load(self, dump: Path, scratch_url: str) -> None: ...
    def swap(self, scratch_url: str, tag: str) -> str:
        """Make the scratch database the live one; where the old one went."""
        ...

    def discard(self, scratch_url: str) -> None: ...


@dataclass(frozen=True)
class Result:
    base: str
    swapped: bool
    live_url: str
    scratch_url: str
    kept_old: str


class SqliteTarget:
    def __init__(self, url: str) -> None:
        path = dbtools.sqlite_path(url)
        if path is None:
            raise OpsError("not a SQLite file URL")
        self.url = url
        self.path = path

    def is_empty(self) -> bool:
        return dbtools.is_empty(self.url)

    def scratch(self, tag: str) -> str:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        file = self.path.with_name(f"{self.path.name}.restore-{tag}")
        file.unlink(missing_ok=True)
        return f"sqlite:///{file}"

    def load(self, dump: Path, scratch_url: str) -> None:
        # The dump of a SQLite database is itself a SQLite file.
        target = dbtools.sqlite_path(scratch_url)
        assert target is not None
        target.write_bytes(dump.read_bytes())

    def swap(self, scratch_url: str, tag: str) -> str:
        new = dbtools.sqlite_path(scratch_url)
        assert new is not None
        old = self.path.with_name(f"{self.path.name}.pre-restore-{tag}")
        had_old = self.path.exists()
        if had_old:
            os.replace(self.path, old)
        for suffix in ("-wal", "-shm"):  # the old file's journal must not be applied to the new one
            sidecar = self.path.with_name(self.path.name + suffix)
            if sidecar.exists():
                os.replace(sidecar, old.with_name(old.name + suffix))
        os.replace(new, self.path)
        for suffix in ("-wal", "-shm"):
            new.with_name(new.name + suffix).unlink(missing_ok=True)
        return str(old) if had_old else ""

    def discard(self, scratch_url: str) -> None:
        path = dbtools.sqlite_path(scratch_url)
        if path is not None:
            path.unlink(missing_ok=True)


class PostgresTarget:
    """Scratch database on the same server; the swap renames, so DATABASE_URL does not change."""

    def __init__(self, url: str) -> None:
        self.url = url
        self.name = dbtools.parse(url).database or ""
        if not self.name:
            raise OpsError("DATABASE_URL names no database")

    def _admin(self, *statements: str) -> None:
        admin = dbtools.parse(self.url).set(database="postgres")
        engine = create_engine(admin, isolation_level="AUTOCOMMIT")
        try:
            with engine.connect() as conn:
                for stmt in statements:
                    conn.execute(text(stmt))
        finally:
            engine.dispose()

    def _url_for(self, name: str) -> str:
        return dbtools.parse(self.url).set(database=name).render_as_string(hide_password=False)

    def is_empty(self) -> bool:
        return dbtools.is_empty(self.url)

    def scratch(self, tag: str) -> str:
        name = f"{self.name}_restore_{tag}"
        self._admin(f'CREATE DATABASE "{name}"')
        return self._url_for(name)

    def load(self, dump: Path, scratch_url: str) -> None:
        args, env = dbtools.pg_args(scratch_url)
        dbname = dbtools.parse(scratch_url).database or ""
        proc.run(
            [
                "pg_restore",
                "--no-owner",
                "--no-acl",
                "--exit-on-error",
                *args,
                "--dbname",
                dbname,
                str(dump),
            ],
            env=env,
        )

    def swap(self, scratch_url: str, tag: str) -> str:
        new = dbtools.parse(scratch_url).database or ""
        old = f"{self.name}_pre_restore_{tag}"
        kick = (
            "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
            "WHERE pid <> pg_backend_pid() AND datname IN ('{n}', '{o}')"
        )
        self._admin(
            kick.format(n=self.name, o=new),
            f'ALTER DATABASE "{self.name}" RENAME TO "{old}"',
            f'ALTER DATABASE "{new}" RENAME TO "{self.name}"',
        )
        return old

    def discard(self, scratch_url: str) -> None:
        name = dbtools.parse(scratch_url).database or ""
        self._admin(f'DROP DATABASE IF EXISTS "{name}"')


def open_target(url: str) -> Target:
    if dbtools.sqlite_path(url) is not None:
        return SqliteTarget(url)
    if dbtools.parse(url).get_backend_name() == "postgresql":
        return PostgresTarget(url)
    raise OpsError("unsupported database for restore")


def fetch_manifest(storage: Storage, work: Path, base: str) -> Manifest:
    dest = work / f"{base}{MANIFEST_SUFFIX}"
    storage.get(f"{base}{MANIFEST_SUFFIX}", dest)
    return Manifest.model_validate_json(dest.read_text(encoding="utf-8"))


def resolve_base(storage: Storage, wanted: str) -> str:
    """`latest`, or a base / object / manifest name."""
    if wanted != "latest":
        return base_of(wanted)
    from librarian.ops.upgrade import latest_backup

    newest = latest_backup(storage)
    if newest is None:
        raise OpsError("no backups in the bucket")
    return newest[0]


def verify(manifest: Manifest, url: str) -> None:
    """The restored copy must match the manifest in Alembic revision and in every table's rows."""
    state = dbtools.read_state(url)
    if state.revision != manifest.alembic_head:
        raise OpsError(
            f"restored Alembic revision {state.revision} != manifest {manifest.alembic_head}"
        )
    if state.counts != manifest.tables:
        diff = sorted(
            t
            for t in manifest.tables.keys() | state.counts.keys()
            if manifest.tables.get(t) != state.counts.get(t)
        )
        raise OpsError(f"row counts differ from the manifest in: {', '.join(diff)}")


def run_restore(
    settings: Settings,
    wanted: str,
    *,
    identity: Path | None = None,
    replace: bool = False,
    swap: bool = True,
    now: datetime | None = None,
    storage: Storage | None = None,
    url: str | None = None,
    target: Target | None = None,
) -> Result:
    store = storage or open_storage(settings)
    url = url or database_url()
    tag = (now or datetime.now(UTC)).strftime("%Y%m%dt%H%M%S")
    base = resolve_base(store, wanted)
    live = target or open_target(url)

    with tempfile.TemporaryDirectory(prefix="librarian-restore-") as tmp:
        work = Path(tmp)
        manifest = fetch_manifest(store, work, base)
        if not dbtools.known_revision(manifest.alembic_head or "") and manifest.alembic_head:
            raise OpsError(
                f"backup is at revision {manifest.alembic_head}, newer than this code "
                f"({dbtools.code_head()}): restore with the release that took it"
            )
        if not live.is_empty() and not replace:
            raise OpsError("the target database has data; refusing to overwrite without --replace")

        fetched = work / manifest.dump_object
        store.get(manifest.dump_object, fetched)
        dump = fetched
        if manifest.encrypted:
            if identity is None:
                raise OpsError("this backup is encrypted: pass --identity <age private key file>")
            if manifest.encrypted_sha256 and sha256_file(fetched) != manifest.encrypted_sha256:
                raise OpsError("the downloaded object does not match the manifest checksum")
            dump = work / f"{base}.dump"
            proc.require("age")
            decrypt(fetched, dump, identity)
        if sha256_file(dump) != manifest.dump_sha256:
            raise OpsError("the dump does not match the manifest sha256")

        scratch_url = live.scratch(tag)
        try:
            live.load(dump, scratch_url)
            verify(manifest, scratch_url)
        except Exception:
            live.discard(scratch_url)
            log.error("ops.restore.rejected", base=base)
            raise

    if not swap:
        log.info("ops.restore.verified", base=base, swapped=False)
        return Result(base, False, url, scratch_url, "")
    kept = live.swap(scratch_url, tag)
    log.info("ops.restore.done", base=base, swapped=True)
    return Result(base, True, url, scratch_url, kept)
