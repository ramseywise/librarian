"""The search index as a build artifact: `librarian index build` writes one complete index file.

The indexer job writes `<id>.duckdb` (pages, FTS, embeddings and the meta that says what built
it), then repoints `current` at it. The servers only ever read a built file (see `handle`).

`<id>` is a hash of what the index is made of: the schema version, the embedding model and the
content hash of every indexable page and lesson. The same corpus gives the same id, and building
it again reuses the file instead of re-embedding.

`current` is a relative symlink to the file, replaced atomically (a symlink to a temporary name,
then `os.replace` over `current`), so a reader sees the old build or the new one and never a gap.
A pointer file would need a read-then-open that a prune can slip between; the symlink resolves
in one step, and every platform we run on (macOS, Linux, the Docker volume) has them.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
from pathlib import Path

import duckdb

from librarian.log_config import get_logger
from librarian.retrieval import corpus, embeddings, index

log = get_logger(__name__)

CURRENT = "current"
# Builds kept after a successful one (the live one included), so a rollback is a repoint.
KEEP_BUILDS = 3
_BUILD_FILE_RE = re.compile(r"^[0-9a-f]{12}\.duckdb$")
# Meta rows that depend on when the build ran, not on what it contains.
_VOLATILE_META = ("built_at",)


def corpus_id() -> str:
    """Deterministic id of the index the current corpus would produce (12 hex chars)."""
    rows = index.read_pages(sorted(corpus.wiki_pages())) + index.read_pages(
        sorted(corpus.course_pages())
    )
    h = hashlib.sha256()
    h.update(f"schema={index.SCHEMA_VERSION}\0".encode())
    model = embeddings.MODEL_NAME if embeddings.HAS_EMBEDDINGS else ""
    h.update(f"embedding_model={model}\0".encode())
    for row in sorted(rows, key=lambda r: r[0]):
        h.update(f"{row[0]}\0{row[6]}\0".encode())
    return h.hexdigest()[:12]


def resolve_current(index_dir: Path) -> Path | None:
    """The file `current` points at, or None when there is no pointer or it dangles."""
    pointer = index_dir / CURRENT
    try:
        target = pointer.resolve(strict=True)
    except OSError:
        return None
    return target if target.is_file() else None


def repoint(index_dir: Path, target: Path) -> None:
    """Atomically make `current` (in `index_dir`) a symlink to `target`, a file in that directory."""
    tmp = index_dir / f".{CURRENT}.{os.getpid()}"
    tmp.unlink(missing_ok=True)
    tmp.symlink_to(target.name)
    os.replace(tmp, index_dir / CURRENT)


def prune(index_dir: Path, keep: int = KEEP_BUILDS) -> list[Path]:
    """Delete all but the newest `keep` builds, never the one `current` names."""
    live = resolve_current(index_dir)
    builds = sorted(
        (p for p in index_dir.iterdir() if _BUILD_FILE_RE.match(p.name)),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    removed = [p for p in builds[max(keep, 1) :] if p != live]
    for p in removed:
        p.unlink(missing_ok=True)
        p.with_name(p.name + ".wal").unlink(missing_ok=True)
    return removed


def _stamp(con: duckdb.DuckDBPyConnection, build_id: str) -> None:
    """Record what built the file, so a reader can refuse one made with another model."""
    index._write_embedding_meta(con)  # embedding_model and embedding_dim, as the index records them
    con.execute("INSERT OR REPLACE INTO meta VALUES ('corpus_id', ?)", [build_id])


def build_artifact(
    out: Path | None = None, *, base: Path | None = None, keep: int = KEEP_BUILDS
) -> Path:
    """Build the index file for the current corpus, repoint `current` at it and prune old builds.

    `out` is the file to write (default `<index dir>/<id>.duckdb`); `current` is repointed beside
    it. `base` is an earlier build to copy and refresh incrementally instead of re-embedding
    everything (the dev server's rebuild after an edit); without it the build is from scratch.
    Returns the file. An existing file for the same id is reused.
    """
    build_id = corpus_id()
    target = out or corpus.INDEX_DIR / f"{build_id}.duckdb"
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        log.info("index_build_reused", path=str(target), build_id=build_id)
    else:
        tmp = target.with_name(f"{target.name}.{os.getpid()}.tmp")
        tmp.unlink(missing_ok=True)
        if base is not None:
            shutil.copyfile(base, tmp)
        con = duckdb.connect(str(tmp))
        try:
            index.build_index(con, force=base is None)
            _stamp(con, build_id)
        except BaseException:
            con.close()
            tmp.unlink(missing_ok=True)
            tmp.with_name(tmp.name + ".wal").unlink(missing_ok=True)
            raise
        con.close()  # checkpoints: the file is complete before it gets its name
        os.replace(tmp, target)
        log.info("index_built_artifact", path=str(target), build_id=build_id)
    repoint(target.parent, target)
    prune(target.parent, keep)
    return target


def rebuild_index() -> Path:
    """From-scratch build into the index directory and repoint `current` (`librarian mcp --rebuild`)."""
    return build_artifact()


def canonical_digest(path: Path) -> str:
    """Hash of an index file's contents, independent of storage layout and build time.

    DuckDB does not promise byte-identical files for identical contents, so equality of builds
    is judged on this: every table's rows in key order, minus the build timestamp.
    """
    con = duckdb.connect(str(path), read_only=True)
    try:
        h = hashlib.sha256()
        volatile = ", ".join(f"'{k}'" for k in _VOLATILE_META)
        queries = {
            "pages": "SELECT * FROM pages ORDER BY path",
            "course_pages": "SELECT * FROM course_pages ORDER BY path",
            "edges": "SELECT * FROM edges ORDER BY ALL",
            "meta": f"SELECT * FROM meta WHERE key NOT IN ({volatile}) ORDER BY key",
        }
        for name, sql in queries.items():
            h.update(name.encode())
            for row in con.execute(sql).fetchall():
                h.update(repr(row).encode())
        return h.hexdigest()
    finally:
        con.close()


def main(argv: list[str] | None = None) -> int:
    """`librarian index build [--out FILE] [--keep N]`."""
    ap = argparse.ArgumentParser(prog="librarian index build", description=__doc__)
    ap.add_argument(
        "--out", type=Path, help="file to write (default: <state dir>/index/<id>.duckdb)"
    )
    ap.add_argument("--keep", type=int, default=KEEP_BUILDS, help="builds to keep (default 3)")
    args = ap.parse_args(argv)
    path = build_artifact(args.out, keep=args.keep)
    print(f"{path}  current -> {path.name}  digest {canonical_digest(path)[:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
