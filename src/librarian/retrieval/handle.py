"""The process's handle on a built search index: opened read-only, swapped atomically, never written.

The API and the MCP server each hold one `IndexHandle`, install it with `index.set_handle`, and
every retrieval read path then gets a cursor on it from `index.open_index()`. The handle opens
the file `current` points at (see `artifact`) with `read_only=True`, so any number of processes
can serve the same build and none of them can write it.

`reload()` (SIGHUP, `POST /admin/reload`) opens the build `current` now names and swaps it in.
Those reach one process; every handle also notices a repointed `current` by itself within
CURRENT_CHECK_INTERVAL_S of a query, so all workers and replicas follow a new build.
A request that already holds a cursor finishes on the old build, because a cursor keeps its
database alive after the handle lets go of it; the next `cursor()` gets the new one.

Dev mode (`autobuild=True`, the default outside production): with no build yet the handle makes
one in a background thread (state `building`, so `/readyz` is 503 meanwhile), and afterwards it
compares the mtime and size of every page now and then (not more than once per
STALE_CHECK_INTERVAL_S) and rebuilds into a new artifact when something changed, serving the old
build until the new one is swapped in. Production sets autobuild off and runs
`librarian index build` as a separate job.
"""

from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Literal

import duckdb

from librarian.log_config import get_logger
from librarian.retrieval import artifact, corpus, embeddings, index

log = get_logger(__name__)

# Dev mode: at most one stat() sweep of the corpus per interval.
STALE_CHECK_INTERVAL_S = 5.0
# Every mode: at most one look at where `current` points per interval. This is how a new build
# reaches every worker and replica: a reload request or SIGHUP lands on one process only.
CURRENT_CHECK_INTERVAL_S = 5.0

State = Literal["ready", "building", "missing", "error"]


class IndexNotReadyError(RuntimeError):
    """No usable index is loaded yet (still building, never built, or the build is unusable)."""


def _fingerprint() -> int:
    """Cheap change detector for the corpus: path, mtime and size of every indexable file."""
    stats = []
    for path in corpus.wiki_pages() + corpus.course_pages():
        try:
            st = path.stat()
        except OSError:
            continue  # deleted mid-sweep: the next sweep sees the difference
        stats.append((str(path), st.st_mtime_ns, st.st_size))
    return hash(tuple(sorted(stats)))


class IndexHandle:
    def __init__(self, index_dir: Path | None = None, *, autobuild: bool = True) -> None:
        self.index_dir = index_dir or corpus.INDEX_DIR
        self.autobuild = autobuild
        self._lock = threading.RLock()
        self._con: duckdb.DuckDBPyConnection | None = None
        self._path: Path | None = None
        self._error: str | None = None
        self._builder: threading.Thread | None = None
        self._fp: int | None = None
        self._last_check = 0.0
        self._last_current_check = time.monotonic()

    # -- state -------------------------------------------------------------------------

    @property
    def state(self) -> State:
        if self._con is not None:
            return "ready"
        if self._builder is not None and self._builder.is_alive():
            return "building"
        return "error" if self._error else "missing"

    @property
    def build_id(self) -> str | None:
        return self._path.stem if self._path else None

    @property
    def refreshing(self) -> bool:
        return self._builder is not None and self._builder.is_alive()

    def status(self) -> dict[str, object]:
        return {
            "state": self.state,
            "build": self.build_id,
            "refreshing": self.refreshing,
            "error": self._error,
        }

    # -- opening and swapping ----------------------------------------------------------

    def _open(self, path: Path) -> duckdb.DuckDBPyConnection:
        """Open a build read-only and check it was made by this code and this embedding model."""
        con = duckdb.connect(str(path), read_only=True)
        try:
            if index.needs_rebuild(con):
                raise ValueError(f"{path.name}: schema is not version {index.SCHEMA_VERSION}")
            row = con.execute("SELECT val FROM meta WHERE key = 'embedding_model'").fetchone()
            built_with = row[0] if row else ""
            if built_with and embeddings.HAS_EMBEDDINGS and built_with != embeddings.MODEL_NAME:
                raise ValueError(
                    f"{path.name}: embeddings are from {built_with}, "
                    f"this process uses {embeddings.MODEL_NAME}"
                )
        except BaseException:
            con.close()
            raise
        return con

    def load(self) -> bool:
        """Open the build `current` names. True if it replaced what was loaded.

        A build that cannot be used keeps the one already loaded, and is reported in `status()`.
        """
        with self._lock:
            path = artifact.resolve_current(self.index_dir)
            if path is None:
                if self._con is None:
                    self._error = None
                return False
            if path == self._path:
                return False
            try:
                con = self._open(path)
            except Exception as exc:
                self._error = str(exc)
                log.error("index_load_failed", path=str(path), error=str(exc))
                return False
            self._con, self._path, self._error = con, path, None
            log.info("index_loaded", build=path.stem)
            return True

    def reload(self) -> dict[str, object]:
        """Swap to the build `current` names now; the result says whether it changed."""
        swapped = self.load()
        return {**self.status(), "reloaded": swapped}

    def start(self, *, wait: bool = False) -> None:
        """Load `current`; in dev mode build one if there is none, or refresh a stale one.

        Loading is quick and happens before this returns; the build, and the comparison of an
        earlier run's index with the files, run in a thread unless `wait`.
        """
        self.load()
        if self.autobuild:
            self._start_build(base=self._path, wait=wait, verify=self._con is not None)

    # -- dev-mode building -------------------------------------------------------------

    def _start_build(self, base: Path | None, *, wait: bool, verify: bool = False) -> None:
        with self._lock:
            if self.refreshing:
                return
            self._error = None
            self._builder = threading.Thread(
                target=self._build, args=(base, verify), name="index-build", daemon=True
            )
            self._builder.start()
        if wait:
            self._builder.join()

    def _build(self, base: Path | None, verify: bool) -> None:
        fp = _fingerprint()  # before the build: an edit during it shows up as a new difference
        try:
            if verify and self._con is not None:
                # An index from an earlier run: compare contents once, then watch mtime and size.
                con = self._con.cursor()
                try:
                    if not (index.stale_pages(con) or index.has_deleted_pages(con)):
                        return
                finally:
                    con.close()
            artifact.build_artifact(base=base)
            self.load()
        except Exception as exc:
            log.exception("index_build_failed", error=str(exc))
            if self._con is None:
                self._error = f"build failed: {exc}"
        finally:
            self._fp = fp

    def _check_stale(self) -> None:
        now = time.monotonic()
        with self._lock:
            if now - self._last_check < STALE_CHECK_INTERVAL_S or self._con is None:
                return
            self._last_check = now
            if self.refreshing or self._fp is None:
                return
            if _fingerprint() == self._fp:
                return
        self._start_build(base=self._path, wait=False)

    def _check_current(self) -> None:
        """Load the build `current` names if another process has repointed it."""
        now = time.monotonic()
        with self._lock:
            if now - self._last_current_check < CURRENT_CHECK_INTERVAL_S:
                return
            self._last_current_check = now
        if artifact.resolve_current(self.index_dir) != self._path:
            self.load()

    # -- reading -----------------------------------------------------------------------

    def cursor(self) -> duckdb.DuckDBPyConnection:
        """A connection for one query, on the build loaded now. The caller closes it."""
        self._check_current()
        if self.autobuild:
            self._check_stale()
        con = self._con
        if con is None:
            raise IndexNotReadyError(f"the search index is {self.state}")
        return con.cursor()
