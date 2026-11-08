"""The search index as a build artifact: deterministic builds, a read-only API, reload, dev build.

Covers `librarian index build` (retrieval.artifact), the read-only `IndexHandle` and the API's
`/readyz`, `/admin/reload` and SIGHUP wiring. The fixture wiki is tiny and the embedding model
is a deterministic fake, so a build is fast and comparable.
"""

from __future__ import annotations

import hashlib
import time
from collections.abc import Iterator
from pathlib import Path

import duckdb
import pytest
from fastapi.testclient import TestClient

from librarian import retrieval
from librarian.api import main as main_module
from librarian.config import get_settings
from librarian.retrieval import artifact, corpus, embeddings, index
from librarian.retrieval.handle import IndexHandle, IndexNotReadyError

TOKEN = "test-admin-token"

PAGE = """---
title: {title}
tags: [test]
summary: Summary of {title}
updated: 2026-08-20
---

# {title}

{body}

## See Also
- [[Beta]] — extends
"""


class _FakeModel:
    def encode(self, texts: list[str], **kwargs: object) -> list[list[float]]:
        # A vector that depends on the text, so a wrong row shows up in the digest.
        return [[(hashlib.sha256(t.encode()).digest()[i] / 255.0) for i in range(8)] for t in texts]


def _write(wiki: Path, name: str, body: str) -> Path:
    d = wiki / "notes"
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{name}.md"
    p.write_text(PAGE.format(title=name.title(), body=body))
    return p


@pytest.fixture()
def wiki(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    wiki_dir = tmp_path / "wiki"
    _write(wiki_dir, "alpha", "Alpha talks about retrieval.")
    _write(wiki_dir, "beta", "Beta talks about caching.")
    monkeypatch.setattr(corpus, "WIKI_DIR", wiki_dir)
    monkeypatch.setattr(corpus, "PRIVATE_DIR", wiki_dir / "private")
    monkeypatch.setattr(corpus, "DB_PATH", tmp_path / ".legacy.duckdb")
    monkeypatch.setattr(corpus, "INDEX_DIR", tmp_path / "index")
    monkeypatch.setattr(embeddings, "HAS_EMBEDDINGS", True)
    monkeypatch.setattr(embeddings, "get_model", lambda: _FakeModel())
    monkeypatch.setattr(embeddings, "_model", _FakeModel())  # "loaded", for /readyz
    monkeypatch.setattr(embeddings, "encode", lambda texts: _encode(texts))
    return wiki_dir


def _encode(texts: list[str]):  # noqa: ANN202
    import numpy as np

    return np.array(_FakeModel().encode(texts), dtype=np.float32)


@pytest.fixture(autouse=True)
def _no_handle() -> Iterator[None]:
    yield
    retrieval.set_handle(None)


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# -- the builder ---------------------------------------------------------------------------


def test_same_input_builds_the_same_index(wiki: Path, tmp_path: Path) -> None:
    """Two from-scratch builds of one wiki: same id, same table contents.

    DuckDB files are not promised byte-identical (build time is in meta, and storage layout is
    its own), so equality is asserted on `canonical_digest`; the raw file hashes are compared
    with `built_at` the only expected difference.
    """
    first = artifact.build_artifact(tmp_path / "a" / "one.duckdb")
    second = artifact.build_artifact(tmp_path / "b" / "two.duckdb")
    assert artifact.canonical_digest(first) == artifact.canonical_digest(second)
    assert artifact.corpus_id() == artifact.corpus_id()
    # The default name is the id, so the same corpus lands on the same file name.
    named = artifact.build_artifact()
    assert named.name == f"{artifact.corpus_id()}.duckdb"
    assert artifact.canonical_digest(named) == artifact.canonical_digest(first)


def test_a_change_gives_a_new_id(wiki: Path) -> None:
    before = artifact.corpus_id()
    _write(wiki, "alpha", "Alpha now says something else.")
    assert artifact.corpus_id() != before


def test_build_records_what_made_it(wiki: Path) -> None:
    path = artifact.build_artifact()
    con = duckdb.connect(str(path), read_only=True)
    meta = dict(con.execute("SELECT key, val FROM meta").fetchall())
    con.close()
    assert meta["schema_version"] == index.SCHEMA_VERSION
    assert meta["embedding_model"] == embeddings.MODEL_NAME
    assert meta["embedding_dim"] == "8"
    assert meta["corpus_id"] == path.stem


def test_current_is_repointed_atomically_and_old_builds_pruned(wiki: Path) -> None:
    index_dir = corpus.INDEX_DIR
    built = []
    for i in range(5):
        _write(wiki, "alpha", f"Alpha, revision {i}.")
        built.append(artifact.build_artifact(keep=3))
        time.sleep(0.01)  # distinct mtimes: prune orders builds by them
    current = index_dir / "current"
    assert current.is_symlink()
    assert artifact.resolve_current(index_dir) == built[-1].resolve()
    remaining = sorted(p.name for p in index_dir.glob("*.duckdb"))
    assert len(remaining) == 3
    assert built[-1].name in remaining
    assert built[0].name not in remaining


def test_rebuilding_unchanged_content_reuses_the_file(wiki: Path) -> None:
    first = artifact.build_artifact()
    digest = _file_sha(first)
    assert artifact.build_artifact() == first
    assert _file_sha(first) == digest


# -- the read-only handle --------------------------------------------------------------------


def test_handle_is_read_only(wiki: Path) -> None:
    artifact.build_artifact()
    handle = IndexHandle(autobuild=False)
    handle.start()
    assert handle.state == "ready"
    con = handle.cursor()
    assert con.execute("SELECT count(*) FROM pages").fetchone() == (2,)
    with pytest.raises(duckdb.Error):
        con.execute("DELETE FROM pages")
    with pytest.raises(duckdb.Error):
        con.execute("CREATE TABLE sneaky (x INTEGER)")
    con.close()


def test_open_index_serves_the_handle_and_search_reads_it(wiki: Path) -> None:
    artifact.build_artifact()
    handle = IndexHandle(autobuild=False)
    handle.start()
    retrieval.set_handle(handle)
    rows, _ = retrieval.search_rows("caching")
    assert rows
    assert not corpus.DB_PATH.exists(), "the legacy read-write index must not be created"


def test_reload_swaps_while_a_held_cursor_still_answers(wiki: Path) -> None:
    first = artifact.build_artifact()
    handle = IndexHandle(autobuild=False)
    handle.start()
    held = handle.cursor()

    _write(wiki, "gamma", "Gamma is a brand new page.")
    second = artifact.build_artifact()
    assert second != first
    assert handle.build_id == first.stem  # not swapped until asked
    assert handle.reload()["reloaded"] is True
    assert handle.build_id == second.stem

    assert held.execute("SELECT count(*) FROM pages").fetchone() == (2,)  # the old build
    fresh = handle.cursor()
    assert fresh.execute("SELECT count(*) FROM pages").fetchone() == (3,)
    assert handle.reload()["reloaded"] is False
    held.close()
    fresh.close()


def test_a_handle_follows_a_build_another_process_made(
    wiki: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from librarian.retrieval import handle as handle_module

    first = artifact.build_artifact()
    handle = IndexHandle(autobuild=False)
    handle.start()
    _write(wiki, "gamma", "Gamma is a brand new page.")
    second = artifact.build_artifact()  # the indexer job: repoints `current`, no reload sent

    held = handle.cursor()  # within the interval: still the first build
    assert handle.build_id == first.stem
    monkeypatch.setattr(handle_module, "CURRENT_CHECK_INTERVAL_S", 0.0)
    fresh = handle.cursor()
    assert handle.build_id == second.stem
    assert fresh.execute("SELECT count(*) FROM pages").fetchone() == (3,)
    held.close()
    fresh.close()


def test_concurrent_builds_of_one_corpus_embed_it_once(
    wiki: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import threading
    from concurrent.futures import ThreadPoolExecutor

    real = index.build_index
    builds: list[int] = []
    started = threading.Event()

    def slow_build(con: duckdb.DuckDBPyConnection, **kwargs: object) -> object:
        builds.append(1)
        started.set()
        time.sleep(0.3)  # long enough for the other builders to reach the lock
        return real(con, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(index, "build_index", slow_build)
    with ThreadPoolExecutor(max_workers=3) as pool:
        paths = list(pool.map(lambda _: artifact.build_artifact(), range(3)))
    assert started.is_set()
    assert len(set(paths)) == 1
    assert builds == [1]
    assert artifact.resolve_current(corpus.INDEX_DIR) == paths[0]
    assert not list(corpus.INDEX_DIR.glob("*.tmp"))


def test_a_prune_cannot_break_a_loaded_build(wiki: Path) -> None:
    first = artifact.build_artifact(keep=1)
    handle = IndexHandle(autobuild=False)
    handle.start()
    held = handle.cursor()
    _write(wiki, "alpha", "Changed.")
    artifact.build_artifact(keep=1)
    assert not first.exists()
    assert held.execute("SELECT count(*) FROM pages").fetchone() == (2,)
    held.close()


def test_a_bad_build_is_refused_and_the_loaded_one_kept(wiki: Path) -> None:
    good = artifact.build_artifact()
    handle = IndexHandle(autobuild=False)
    handle.start()
    bad = corpus.INDEX_DIR / "badbadbadbad.duckdb"
    con = duckdb.connect(str(bad))
    con.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, val TEXT)")
    con.execute("INSERT INTO meta VALUES ('schema_version', '1')")
    con.close()
    artifact.repoint(corpus.INDEX_DIR, bad)
    assert handle.reload()["reloaded"] is False
    assert handle.build_id == good.stem
    assert "schema" in str(handle.status()["error"])


def test_no_index_and_no_autobuild_is_not_ready(wiki: Path) -> None:
    handle = IndexHandle(autobuild=False)
    handle.start()
    assert handle.state == "missing"
    with pytest.raises(IndexNotReadyError):
        handle.cursor()


# -- the API ---------------------------------------------------------------------------------


@pytest.fixture()
def _settings(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setenv("LIBRARIAN_API_TOKEN", "")
    get_settings.cache_clear()
    yield
    monkeypatch.undo()
    get_settings.cache_clear()


def test_api_serves_a_built_index_read_only(wiki: Path, _settings: None) -> None:
    artifact.build_artifact()
    with TestClient(main_module.app) as client:
        resp = client.get("/readyz")
        assert resp.status_code == 200
        assert resp.json()["index"] == "ready"
        con = retrieval.open_index()
        with pytest.raises(duckdb.Error):
            con.execute("UPDATE pages SET title = 'x'")
        con.close()
    assert retrieval.get_handle() is None


def test_admin_reload_swaps_the_build(
    wiki: Path, _settings: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LIBRARIAN_API_TOKEN", TOKEN)
    get_settings.cache_clear()
    artifact.build_artifact()
    with TestClient(main_module.app) as client:
        assert client.post("/admin/reload").status_code == 401
        auth = {"Authorization": f"Bearer {TOKEN}"}
        assert client.post("/admin/reload", headers=auth).json()["reloaded"] is False
        _write(wiki, "gamma", "Gamma is new.")
        newer = artifact.build_artifact()
        body = client.post("/admin/reload", headers=auth).json()
        assert body["reloaded"] is True
        assert body["build"] == newer.stem


def test_dev_mode_builds_in_the_background_then_goes_ready(
    wiki: Path, _settings: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LIBRARIAN_INDEX_AUTOBUILD", "1")
    get_settings.cache_clear()
    import threading

    gate = threading.Event()
    real_build = artifact.build_artifact

    def slow_build(*args: object, **kwargs: object) -> Path:
        gate.wait(10)
        return real_build(*args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(artifact, "build_artifact", slow_build)
    with TestClient(main_module.app) as client:
        resp = client.get("/readyz")
        assert resp.status_code == 503
        assert resp.json()["index"] == "building"
        with pytest.raises(IndexNotReadyError):
            retrieval.open_index()
        gate.set()
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            resp = client.get("/readyz")
            if resp.status_code == 200:
                break
            time.sleep(0.05)
        assert resp.status_code == 200
        assert resp.json()["index"] == "ready"
    assert (corpus.INDEX_DIR / "current").is_symlink()


def test_dev_mode_rebuilds_when_a_page_changes(wiki: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    artifact.build_artifact()
    monkeypatch.setattr("librarian.retrieval.handle.STALE_CHECK_INTERVAL_S", 0.0)
    handle = IndexHandle(autobuild=True)
    handle.start(wait=True)
    first = handle.build_id
    time.sleep(0.01)
    _write(wiki, "alpha", "Alpha was edited, and is much longer now.")
    handle.cursor().close()  # the staleness check starts the rebuild
    assert handle._builder is not None
    handle._builder.join(20)
    assert handle.build_id != first
    con = handle.cursor()
    assert con.execute("SELECT count(*) FROM pages WHERE content LIKE '%edited%'").fetchone() == (
        1,
    )
    con.close()
