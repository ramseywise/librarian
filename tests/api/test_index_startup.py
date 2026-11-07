"""F11 and F9: the index builds at startup, /readyz only reads its state, embeddings are tracked."""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient

import librarian.api.main as main_module
from librarian.config import get_settings
from librarian.retrieval import corpus, embeddings, index

PAGE = "---\ntitle: {t}\ntags: [rag, concept]\nsummary: About {t}\nupdated: 2026-01-01\n---\n\n# {t}\n\n{body}\n"


@pytest.fixture(autouse=True)
def _fresh(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    get_settings.cache_clear()
    monkeypatch.setattr(main_module, "_ready_until", 0.0)
    monkeypatch.setattr(embeddings, "HAS_EMBEDDINGS", False)
    yield
    get_settings.cache_clear()


@pytest.fixture()
def wiki(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    wiki = tmp_path / "wiki"
    (wiki / "notes").mkdir(parents=True)
    for name in ("alpha", "beta"):
        (wiki / "notes" / f"{name}.md").write_text(PAGE.format(t=name.title(), body=f"{name} text"))
    monkeypatch.setattr(corpus, "WIKI_DIR", wiki)
    monkeypatch.setattr(corpus, "DB_PATH", tmp_path / "index.duckdb")
    return wiki


# -- /readyz ---------------------------------------------------------------


def _forbid_rebuild(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    calls: list[str] = []

    def boom(*a: object, **k: object) -> None:
        calls.append("rebuild")
        raise AssertionError("a probe must not build the index")

    monkeypatch.setattr(main_module.retrieval, "open_index", boom)
    monkeypatch.setattr(main_module.retrieval, "rebuild_index", boom)
    monkeypatch.setattr(index, "build_index", boom)
    monkeypatch.setattr(index, "_full_rebuild", boom)
    return calls


def test_readyz_is_503_building_while_the_index_builds(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _forbid_rebuild(monkeypatch)
    with TestClient(main_module.app) as client:
        monkeypatch.setattr(main_module, "_index_state", "building")
        resp = client.get("/readyz")
    assert resp.status_code == 503
    assert resp.json()["index"] == "building"
    assert calls == []


def test_readyz_is_503_failed_when_the_startup_build_failed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with TestClient(main_module.app) as client:
        monkeypatch.setattr(main_module, "_index_state", "failed")
        resp = client.get("/readyz")
    assert resp.status_code == 503 and resp.json()["index"] == "failed"


def test_readyz_is_200_once_the_index_is_ready(wiki: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    index.rebuild_index()
    calls = _forbid_rebuild(monkeypatch)
    with TestClient(main_module.app) as client:
        monkeypatch.setattr(main_module, "_index_state", "ready")
        resp = client.get("/readyz")
    assert resp.status_code == 200
    assert resp.json()["checks"] == {"index": True, "embeddings": True}
    assert calls == []


def test_a_probe_never_builds_a_missing_index(wiki: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _forbid_rebuild(monkeypatch)
    with TestClient(main_module.app) as client:
        monkeypatch.setattr(main_module, "_index_state", "ready")
        resp = client.get("/readyz")
    assert resp.status_code == 503
    assert not corpus.DB_PATH.exists()
    assert calls == []


def test_the_ready_answer_is_cached(wiki: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    probes: list[int] = []
    monkeypatch.setattr(main_module.retrieval, "index_is_built", lambda: probes.append(1) or True)
    with TestClient(main_module.app) as client:
        monkeypatch.setattr(main_module, "_index_state", "ready")
        assert client.get("/readyz").status_code == 200
        assert client.get("/readyz").status_code == 200
    assert probes == [1]


def test_lifespan_builds_the_index_in_the_background(
    wiki: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("LIBRARIAN_SKIP_WARMUP", raising=False)
    monkeypatch.setattr(main_module, "_warm_course_data", lambda: None)
    built: list[int] = []
    monkeypatch.setattr(main_module.retrieval, "open_index", lambda: _Closing(built))
    get_settings.cache_clear()
    with TestClient(main_module.app):
        for _ in range(200):
            if main_module._index_state == "ready":
                break
            import time

            time.sleep(0.01)
        assert main_module._index_state == "ready"
    assert built == [1]


def test_a_failed_startup_build_is_state_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom() -> None:
        raise RuntimeError("locked")

    monkeypatch.setattr(main_module.retrieval, "open_index", boom)
    monkeypatch.setattr(main_module, "_index_state", "building")
    main_module._build_index()
    assert main_module._index_state == "failed"


class _Closing:
    def __init__(self, built: list[int]) -> None:
        built.append(1)

    def close(self) -> None:
        pass


# -- freshness: mtime+size first, hash only on a mismatch ---------------------


def test_unchanged_files_are_not_hashed(wiki: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    index.rebuild_index()
    hashed: list[Path] = []
    real = index._content_hash
    monkeypatch.setattr(index, "_content_hash", lambda p: hashed.append(p) or real(p))
    con = index.connect()
    try:
        assert index.stale_pages(con) == []
    finally:
        con.close()
    assert hashed == []


def test_a_touched_file_is_hashed_once_and_then_skipped(
    wiki: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    index.rebuild_index()
    alpha = wiki / "notes" / "alpha.md"
    st = alpha.stat()
    os.utime(alpha, ns=(st.st_atime_ns, st.st_mtime_ns + 5_000_000_000))
    hashed: list[Path] = []
    real = index._content_hash
    monkeypatch.setattr(index, "_content_hash", lambda p: hashed.append(p) or real(p))
    con = index.connect()
    try:
        assert index.stale_pages(con) == []  # same bytes: fresh
        assert index.stale_pages(con) == []  # signature stored: no second hash
    finally:
        con.close()
    assert hashed == [alpha]


def test_an_edit_with_a_new_size_is_stale(wiki: Path) -> None:
    index.rebuild_index()
    alpha = wiki / "notes" / "alpha.md"
    alpha.write_text(alpha.read_text() + "more\n")
    con = index.connect()
    try:
        assert index.stale_pages(con) == [alpha]
    finally:
        con.close()


# -- embeddings meta -------------------------------------------------------


class _FakeModel:
    def __init__(self, dim: int = 8) -> None:
        self.dim = dim
        self.texts: list[str] = []

    def encode(self, texts: list[str], **_: object) -> np.ndarray:
        self.texts += texts
        return np.full((len(texts), self.dim), 0.5, dtype=np.float32)


@pytest.fixture()
def fake_model(monkeypatch: pytest.MonkeyPatch) -> _FakeModel:
    model = _FakeModel()
    monkeypatch.setattr(embeddings, "HAS_EMBEDDINGS", True)
    monkeypatch.setattr(embeddings, "get_model", lambda: model)
    monkeypatch.setattr(embeddings, "MODEL_NAME", "fake-a")
    return model


def _meta(key: str) -> str | None:
    con = index.connect()
    try:
        return index._get_meta(con, key)
    finally:
        con.close()


def test_the_index_records_model_and_dim(wiki: Path, fake_model: _FakeModel) -> None:
    index.rebuild_index()
    assert _meta("embedding_model") == "fake-a"
    assert _meta("embedding_dim") == "8"


def test_a_model_change_re_embeds_everything(
    wiki: Path, fake_model: _FakeModel, monkeypatch: pytest.MonkeyPatch
) -> None:
    index.rebuild_index()
    fake_model.texts.clear()
    fake_model.dim = 16
    monkeypatch.setattr(embeddings, "MODEL_NAME", "fake-b")
    index.open_index().close()
    assert len(fake_model.texts) == 2
    assert _meta("embedding_model") == "fake-b"
    assert _meta("embedding_dim") == "16"


def test_a_matching_model_does_not_re_embed(wiki: Path, fake_model: _FakeModel) -> None:
    index.rebuild_index()
    fake_model.texts.clear()
    index.open_index().close()
    assert fake_model.texts == []


def test_null_embeddings_are_filled_when_the_model_is_available(
    wiki: Path, monkeypatch: pytest.MonkeyPatch, fake_model: _FakeModel
) -> None:
    monkeypatch.setattr(embeddings, "HAS_EMBEDDINGS", False)
    index.rebuild_index()  # built offline: every vector NULL
    assert _meta("embedding_model") == ""
    monkeypatch.setattr(embeddings, "HAS_EMBEDDINGS", True)
    index.open_index().close()
    con = index.connect()
    try:
        nulls = con.execute("SELECT count(*) FROM pages WHERE embedding IS NULL").fetchone()
    finally:
        con.close()
    assert nulls == (0,)
    assert _meta("embedding_model") == "fake-a"


def test_the_index_still_embeds_the_file_text_with_its_frontmatter(
    wiki: Path, fake_model: _FakeModel
) -> None:
    """Pinned: embedding the body instead lowered the eval gate (see `_embed_pages`)."""
    index.rebuild_index()
    assert fake_model.texts
    assert all("tags: [rag, concept]" in t for t in fake_model.texts)


def test_embeddings_unavailable_is_degraded_in_readyz(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(main_module.retrieval, "index_is_built", lambda: True)
    monkeypatch.setattr(embeddings, "HAS_EMBEDDINGS", True)
    monkeypatch.setattr(embeddings, "LOAD_ERROR", "OSError: no network")
    with TestClient(main_module.app) as client:
        monkeypatch.setattr(main_module, "_index_state", "ready")
        resp = client.get("/readyz")
    assert resp.status_code == 200
    assert resp.json()["degraded"] == ["embeddings_unavailable"]


def test_a_model_that_fails_to_load_is_recorded(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom() -> None:
        raise OSError("no network")

    monkeypatch.setattr(embeddings, "HAS_EMBEDDINGS", True)
    monkeypatch.setattr(embeddings, "get_model", boom)
    embeddings.warmup()
    assert "no network" in embeddings.LOAD_ERROR
    assert embeddings.embeddings_unavailable()


def test_search_reports_embeddings_unavailable(wiki: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from librarian.retrieval import ranking

    monkeypatch.setattr(embeddings, "LOAD_ERROR", "OSError: no network")
    _, degraded = ranking.search_rows("alpha", limit=3, tool="test")
    assert "embeddings_unavailable" in degraded
