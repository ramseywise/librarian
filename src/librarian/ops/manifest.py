"""The manifest written beside every dump: what was backed up, from which release, and its checksum."""

from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel

BASE_PREFIX = "librarian-"
DUMP_SUFFIXES = (".dump.age", ".dump")
MANIFEST_SUFFIX = ".manifest.json"
_STAMP = "%Y%m%dT%H%M%SZ"
_BASE_RE = re.compile(r"^librarian-(\d{8}T\d{6}Z)-[A-Za-z0-9_.-]+$")


class Manifest(BaseModel):
    version: int = 1
    base: str
    dump_object: str
    created_at: datetime
    release: str
    dialect: str
    alembic_head: str | None
    # Row count per table, taken from the same snapshot as the dump; `alembic_version` excluded.
    tables: dict[str, int]
    dump_sha256: str
    dump_bytes: int
    encrypted: bool
    encrypted_sha256: str | None = None


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def make_base(now: datetime, release: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]", "-", release) or "dev"
    return f"{BASE_PREFIX}{now.astimezone(UTC).strftime(_STAMP)}-{safe}"


def base_of(name: str) -> str:
    """The base name for an object name, a manifest name or a base."""
    for suffix in (MANIFEST_SUFFIX, *DUMP_SUFFIXES):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def stamp_of(base: str) -> datetime | None:
    """When the backup `base` was taken, from its name; None if it is not one of ours."""
    m = _BASE_RE.match(base)
    if m is None:
        return None
    return datetime.strptime(m.group(1), _STAMP).replace(tzinfo=UTC)
