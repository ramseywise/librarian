"""Content releases: build, pull, verify, swap, pin and the API's webhook and header."""

from __future__ import annotations

import hashlib
import io
import json
import shutil
import tarfile
import time
from collections.abc import Iterator
from pathlib import Path

import pytest
import zstandard
from fastapi.testclient import TestClient

from librarian import release, retrieval
from librarian.api import main as main_module
from librarian.api.routers import release as release_routes
from librarian.config import get_settings
from librarian.release import package, paths
from librarian.release.package import sha256_file
from librarian.retrieval import artifact, corpus, embeddings

PAGE = "---\ntitle: {t}\ntags: [meta, concept]\nsummary: {t}.\nupdated: 2026-11-08\n---\n\n# {t}\n"
SECRET = "webhook-secret"


@pytest.fixture()
def env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[dict[str, Path]]:
    src = tmp_path / "src"
    for tree in ("wiki", "courses"):
        (src / tree / "notes").mkdir(parents=True)
        (src / tree / "private").mkdir()
        (src / tree / "private" / "secret.md").write_text("never ship")
    (src / "wiki" / "notes" / "alpha.md").write_text(PAGE.format(t="Alpha"))
    state, store = tmp_path / "state", tmp_path / "store"
    monkeypatch.setenv("LIBRARIAN_STATE_DIR", str(state))
    monkeypatch.setenv("WIKI_DIR", str(src / "wiki"))
    monkeypatch.setenv("COURSES_DIR", str(src / "courses"))
    monkeypatch.setenv("LIBRARIAN_RELEASE_URL", f"file://{store}")
    monkeypatch.setattr(corpus, "INDEX_DIR", state / "index")
    get_settings.cache_clear()
    yield {"src": src, "state": state, "store": store, "root": state / "content"}
    monkeypatch.undo()
    get_settings.cache_clear()


def _build(env: dict[str, Path], name: str, **manifest: object) -> package.BuiltRelease:
    """Build `name` into the store, as CI would on another machine: the stage is not kept.

    `manifest` overrides manifest keys (and repacks), for releases a correct build can't make.
    """
    (env["src"] / "wiki" / "notes" / "alpha.md").write_text(PAGE.format(t=f"Alpha {name}"))
    built = package.build(env["store"], name=name, build_index=False)
    stage = env["root"] / "releases" / name
    if manifest:
        if "index" in manifest:
            (stage / "index").mkdir()
            (stage / str(manifest["index"])).write_bytes(b"duckdb")
        merged = json.loads((stage / "manifest.json").read_text()) | manifest
        (stage / "manifest.json").write_text(json.dumps(merged))
        package._write_archive(stage, name, built.archive)
        built.checksum.write_text(f"{sha256_file(built.archive)}  {built.archive.name}\n")
    shutil.rmtree(stage)
    return built


def test_a_release_never_holds_a_private_path(env: dict[str, Path]) -> None:
    built = _build(env, "content-a")
    with (
        built.archive.open("rb") as raw,
        zstandard.ZstdDecompressor().stream_reader(raw) as zfh,
        tarfile.open(fileobj=zfh, mode="r|") as tar,
    ):
        names = [m.name for m in tar]
    assert "content-a/wiki/notes/alpha.md" in names
    assert not [n for n in names if "private" in n]
    assert (env["store"] / "latest").read_text().strip() == "content-a"


def test_pull_installs_latest_and_content_is_read_through_current(
    env: dict[str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    _build(env, "content-a")
    result = release.pull()
    assert result.release == "content-a" and result.changed
    assert release.current_name() == "content-a"
    assert release.pull().changed is False  # already current: nothing to do
    monkeypatch.delenv("WIKI_DIR")
    get_settings.cache_clear()
    page = get_settings().wiki_dir / "notes" / "alpha.md"
    assert get_settings().wiki_dir == env["root"] / "current" / "wiki"
    assert "Alpha content-a" in page.read_text()


def test_a_checksum_mismatch_is_refused_and_nothing_changes(env: dict[str, Path]) -> None:
    _build(env, "content-a")
    release.pull()
    built = _build(env, "content-b")
    built.checksum.write_text("0" * 64 + "  x\n")
    with pytest.raises(release.ReleaseError, match="checksum mismatch"):
        release.pull()
    assert release.current_name() == "content-a"
    assert not (env["root"] / "releases" / "content-b").exists()


def test_an_archive_with_a_private_member_is_refused(env: dict[str, Path]) -> None:
    store = env["store"]
    store.mkdir(parents=True)
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tar:
        for name, data in [
            ("content-x/manifest.json", json.dumps({"name": "content-x"}).encode()),
            ("content-x/wiki/private/secret.md", b"leak"),
        ]:
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
    archive = store / "content-x.tar.zst"
    archive.write_bytes(zstandard.ZstdCompressor().compress(buf.getvalue()))
    (store / "content-x.tar.zst.sha256").write_text(f"{sha256_file(archive)}  {archive.name}\n")
    (store / "latest").write_text("content-x\n")
    with pytest.raises(release.ReleaseError, match="private path"):
        release.pull()
    assert release.current_name() is None
    assert not (env["root"] / "releases" / "content-x").exists()


def test_a_release_built_for_another_state_dir_is_refused(env: dict[str, Path]) -> None:
    _build(env, "content-a", serve_root="/elsewhere", index="index/abc.duckdb")
    with pytest.raises(release.ReleaseError, match="state dir"):
        release.pull()
    assert release.current_name() is None


def test_pin_rolls_back_and_pull_keeps_it_until_unpinned(env: dict[str, Path]) -> None:
    for name in ("content-a", "content-b"):
        _build(env, name)
        release.pull()
    assert release.current_name() == "content-b"
    assert release.pin("a").release == "content-a"  # a sha prefix resolves to the release on disk
    _build(env, "content-c")
    assert release.pull().release == "content-a"
    release.unpin()
    assert release.pull().release == "content-c"


def test_the_current_release_and_two_before_it_stay_on_disk(env: dict[str, Path]) -> None:
    for i, name in enumerate(["content-1", "content-2", "content-3", "content-4", "content-5"]):
        _build(env, name)
        release.pull()
        time.sleep(0.01 * (i + 1))  # distinct mtimes
    kept = {r["name"] for r in release.list_releases()}
    assert kept == {"content-3", "content-4", "content-5"}


def test_an_index_in_the_release_becomes_index_current(env: dict[str, Path]) -> None:
    serve_root = str(get_settings().var_dir.resolve())
    _build(env, "content-a", serve_root=serve_root, index="index/abc123.duckdb")
    release.pull()
    assert (corpus.INDEX_DIR / "current").resolve().name == "abc123.duckdb"


# -- the API -------------------------------------------------------------------------------


@pytest.fixture()
def api(env: dict[str, Path], monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setenv("LIBRARIAN_RELEASE_POLL_S", "0")
    monkeypatch.setenv("LIBRARIAN_RELEASE_WEBHOOK_SECRET", SECRET)
    monkeypatch.setenv("LIBRARIAN_API_TOKEN", "")
    get_settings.cache_clear()
    # A real (tiny) index for the handle, built from the source wiki with a fake embedder.
    monkeypatch.setattr(corpus, "WIKI_DIR", env["src"] / "wiki")
    monkeypatch.setattr(corpus, "PRIVATE_DIR", env["src"] / "wiki" / "private")
    monkeypatch.setattr(corpus, "DB_PATH", env["state"] / ".legacy.duckdb")
    monkeypatch.setattr(embeddings, "HAS_EMBEDDINGS", True)
    monkeypatch.setattr(embeddings, "_model", object())
    monkeypatch.setattr(embeddings, "encode", _encode)
    artifact.build_artifact()
    _build(env, "content-a")
    release_routes._name_cache = (0.0, None)
    with TestClient(main_module.app) as client:
        yield client
    release_routes._name_cache = (0.0, None)
    retrieval.set_handle(None)


def _encode(texts: list[str]):  # noqa: ANN202
    import numpy as np

    rows = [[hashlib.sha256(t.encode()).digest()[i] / 255.0 for i in range(8)] for t in texts]
    return np.array(rows, dtype=np.float32)


def _signed(body: bytes, *, secret: str = SECRET, age_s: int = 0) -> dict[str, str]:
    ts = str(int(time.time()) - age_s)
    return {
        "X-Librarian-Timestamp": ts,
        "X-Librarian-Signature": release_routes.sign(secret, ts, body),
    }


def _wait_for(client: TestClient, name: str) -> None:
    deadline = time.monotonic() + 10
    while release.current_name() != name and time.monotonic() < deadline:
        time.sleep(0.05)
    release_routes._name_cache = (0.0, None)


def test_the_api_serves_the_release_and_names_it_in_a_header(api: TestClient) -> None:
    _wait_for(api, "content-a")  # the startup pull
    resp = api.get("/api/release")
    assert resp.json()["release"] == "content-a"
    assert resp.headers["X-Librarian-Release"] == "content-a"


def test_a_signed_webhook_pulls_the_new_release(api: TestClient, env: dict[str, Path]) -> None:
    _wait_for(api, "content-a")
    _build(env, "content-b")
    resp = api.post("/admin/reload", content=b"{}", headers=_signed(b"{}"))
    assert resp.status_code == 200, resp.text
    assert resp.json()["release"]["release"] == "content-b"
    assert api.get("/api/release").headers["X-Librarian-Release"] == "content-b"


@pytest.mark.parametrize(
    "headers",
    [
        _signed(b"{}", secret="wrong"),
        _signed(b"{}", age_s=3600),
        {"X-Librarian-Timestamp": "nope", "X-Librarian-Signature": "sha256=00"},
    ],
    ids=["wrong-secret", "stale", "garbage"],
)
def test_a_bad_or_stale_signature_is_refused(api: TestClient, headers: dict[str, str]) -> None:
    resp = api.post("/admin/reload", content=b"{}", headers=headers)
    assert resp.status_code == 401


def test_a_signature_over_another_body_is_refused(api: TestClient) -> None:
    resp = api.post("/admin/reload", content=b'{"x":1}', headers=_signed(b"{}"))
    assert resp.status_code == 401


def test_reload_with_no_credential_is_refused(
    api: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LIBRARIAN_API_TOKEN", "tok")
    get_settings.cache_clear()
    assert api.post("/admin/reload").status_code == 401


def test_paths_check_name_refuses_traversal() -> None:
    for bad in ("../x", "a/b", "", ".hidden", "a..b"):
        with pytest.raises(ValueError):
            paths.check_name(bad)
