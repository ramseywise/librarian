"""An applied migration must not be edited: the files in db/migrations/versions/ that have shipped
are hashed against a committed manifest (`migrations.sha256`). A pinned file that changed or went
missing fails the test.

A migration not in the manifest is not checked: until it ships it may still be edited. Pin it in
the release that applies it, by appending its line (`sha256sum`-style: digest, two spaces, name) or
by regenerating the whole file, which pins every file now on disk:

    uv run python -m tests.db.test_migration_manifest
"""

from __future__ import annotations

import hashlib
from pathlib import Path

VERSIONS = Path(__file__).parents[2] / "src" / "librarian" / "db" / "migrations" / "versions"
MANIFEST = Path(__file__).with_name("migrations.sha256")


def _digest(path: Path) -> str:
    # Line endings normalised so a Windows checkout hashes the same.
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def current() -> dict[str, str]:
    return {p.name: _digest(p) for p in sorted(VERSIONS.glob("*.py")) if p.name != "__init__.py"}


def committed() -> dict[str, str]:
    out = {}
    for line in MANIFEST.read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            digest, name = line.split(maxsplit=1)
            out[name] = digest
    return out


def render(files: dict[str, str]) -> str:
    return (
        "# sha256  file, in db/migrations/versions/. Regenerate: see test_migration_manifest.py\n"
        + "".join(f"{digest}  {name}\n" for name, digest in files.items())
    )


def test_migration_files_match_the_committed_manifest() -> None:
    now, then = current(), committed()
    changed = sorted(n for n in now.keys() & then.keys() if now[n] != then[n])
    removed = sorted(then.keys() - now.keys())
    assert not (changed or removed), (
        f"pinned migration edited (add a new revision instead of editing an applied one): "
        f"{changed}; pinned migration missing: {removed}"
    )


def test_manifest_covers_every_revision() -> None:
    assert len(committed()) >= 8


if __name__ == "__main__":
    MANIFEST.write_text(render(current()))
    print(f"wrote {MANIFEST}")
