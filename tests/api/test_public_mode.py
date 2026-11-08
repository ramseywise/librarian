"""Public mode (`LIBRARIAN_PUBLIC`): the code, not only the compose tmpfs masks, keeps private/
content off every course route, and one bad lesson file cannot take the catalog down.

Private files are real files on disk in a tmp tree; every course and file route must omit or
404 them when the mode is on.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from librarian.api.routers import courses as courses_routes
from librarian.courses import catalog as courses
from librarian.courses import slides, sources
from librarian.retrieval import embeddings

SECRET = "PRIVATE_BODY_MARKER"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def _build(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, public: bool) -> TestClient:
    root = tmp_path / "courses"
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    _write(root / "gen-ai" / "_course.md", "---\ntitle: Gen AI\n---\n")
    _write(root / "gen-ai" / "01-rag" / "intro.md", "---\ntitle: Intro\norder: 1\n---\n\nPublic.\n")
    _write(root / "gen-ai" / "01-rag" / "assets" / "fig.png", "png")
    # The private mirror: a lesson, a figure that exists only there, a reading list.
    mirror = root / "private" / "gen-ai" / "01-rag"
    _write(mirror / "mine.md", f"---\ntitle: Mine\norder: 2\n---\n\n{SECRET}\n")
    _write(mirror / "assets" / "mirror-only.png", "png")
    _write(mirror / "_module.md", f"---\nreadings:\n  - {SECRET}\n---\n")
    _write(root / "private" / "leetcode" / "arrays" / "p1.md", f"---\ntitle: P1\n---\n\n{SECRET}\n")
    _write(root / "private" / "x.png", "png")
    _write(tmp_path / "secret.png", "outside")

    srcs = tmp_path / "sources-repo"
    _write(srcs / "gen-ai" / "sources" / "book.pdf", "pdf")
    _write(srcs / "private" / "sources" / "hidden.pdf", "pdf")
    _write(srcs / "gen-ai" / "private" / "sources" / "hidden2.pdf", "pdf")

    monkeypatch.setattr(courses, "COURSES_DIR", root)
    monkeypatch.setattr(courses, "WIKI_DIR", wiki)
    monkeypatch.setattr(courses, "PUBLIC_MODE", public)
    monkeypatch.setattr(courses, "LESSON_VEC_CACHE", tmp_path / "cache" / "lessons.npz")
    monkeypatch.setattr(courses, "_semantic_neighbours", lambda texts, ids: None)
    monkeypatch.setattr(sources, "SOURCES_DIR", srcs)
    monkeypatch.setattr(sources, "SERVE_SOURCES", True)
    monkeypatch.setattr(sources, "PUBLIC_MODE", public)
    monkeypatch.setattr(slides, "COURSES_DIR", root)
    courses._load.cache_clear()
    app = FastAPI()
    app.include_router(courses_routes.router)
    return TestClient(app)


@pytest.fixture()
def public(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    yield _build(tmp_path, monkeypatch, True)
    courses._load.cache_clear()


@pytest.fixture()
def local(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    yield _build(tmp_path, monkeypatch, False)
    courses._load.cache_clear()


def test_local_mode_still_serves_private(local: TestClient) -> None:
    ids = {c["id"] for c in local.get("/api/courses").json()}
    assert "leetcode" in ids
    assert local.get("/api/courses/files/gen-ai/01-rag/assets/mirror-only.png").status_code == 200


def test_catalog_omits_private_everywhere(public: TestClient) -> None:
    body = public.get("/api/courses").text
    assert SECRET not in body and "leetcode" not in body and "mine" not in body
    assert [c["id"] for c in public.get("/api/courses").json()] == ["gen-ai"]
    assert public.get("/api/courses/search", params={"q": "PRIVATE_BODY"}).json() == []
    for lid in ("private/gen-ai/01-rag/mine", "private/leetcode/arrays/p1", "gen-ai/01-rag/mine"):
        assert public.get(f"/api/courses/lessons/{lid}").status_code == 404
    assert SECRET not in public.get("/api/courses/study").text
    assert SECRET not in public.get("/api/courses/lessons/gen-ai/01-rag/intro").text


@pytest.mark.parametrize(
    "path",
    [
        "private/x.png",
        "private/gen-ai/01-rag/assets/mirror-only.png",
        "gen-ai/01-rag/assets/mirror-only.png",  # served by the mirror fallback locally
        "PRIVATE/x.png",
        "gen-ai/../private/x.png",
        "%2e%2e/secret.png",
        "gen-ai/%2e%2e/%2e%2e/secret.png",
        "gen-ai/%2E%2E/private/x.png",
        "..%2fsecret.png",
        "%2Ftmp%2Fsecret.png",
        "//etc/passwd",
        "/etc/passwd",
        "gen-ai/01-rag/assets/%00fig.png",
    ],
)
def test_files_route_rejects_private_and_traversal(public: TestClient, path: str) -> None:
    assert public.get(f"/api/courses/files/{path}").status_code in (400, 404)


def test_files_route_still_serves_public_asset(public: TestClient) -> None:
    assert public.get("/api/courses/files/gen-ai/01-rag/assets/fig.png").status_code == 200


def test_files_symlink_into_private_is_refused(public: TestClient, tmp_path: Path) -> None:
    link = tmp_path / "courses" / "gen-ai" / "01-rag" / "assets" / "link.png"
    link.symlink_to(tmp_path / "courses" / "private" / "x.png")
    assert public.get("/api/courses/files/gen-ai/01-rag/assets/link.png").status_code == 404


@pytest.mark.parametrize(
    "path",
    [
        "private/sources/hidden.pdf",
        "gen-ai/private/sources/hidden2.pdf",
        "../secret.png",
        "%2e%2e/secret.png",
        "gen-ai/%2e%2e/%2e%2e/secret.png",
        "/etc/passwd",
        "%2Fetc%2Fpasswd",
    ],
)
def test_sources_route_rejects_private_and_traversal(public: TestClient, path: str) -> None:
    assert public.get(f"/api/courses/sources/{path}").status_code == 404


def test_sources_route_serves_public_pdf(public: TestClient) -> None:
    assert public.get("/api/courses/sources/gen-ai/sources/book.pdf").status_code == 200


@pytest.mark.parametrize(
    "deck",
    ["private/gen-ai/01-rag", "../secret", "%2e%2e/%2e%2e/secret", "gen-ai/..%2f..", "/etc"],
)
def test_slide_routes_reject_private_and_traversal(public: TestClient, deck: str) -> None:
    assert public.get(f"/api/courses/slides/{deck}").status_code == 404
    assert public.get(f"/api/courses/slide-image/{deck}/1").status_code == 404


def test_embeddings_skip_private_and_tombstones(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    wiki = tmp_path / "wiki"
    page = "---\ntitle: {t}\ntags: [{tags}]\nsummary: s\n---\n\nbody\n"
    _write(wiki / "rag" / "live.md", page.format(t="Live", tags="rag, concept"))
    _write(wiki / "rag" / "old.md", page.format(t="Old", tags="rag, tombstone"))
    _write(wiki / "private" / "secret.md", page.format(t="Secret", tags="rag, concept"))
    _write(wiki / "_index.md", "# index\n")
    monkeypatch.setattr(embeddings, "WIKI_DIR", wiki)
    assert [f.name for f in embeddings._wiki_files()] == ["live.md"]


# ── F7: one bad file must not break the catalog ─────────────────────────────


@pytest.fixture()
def robust(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    client = _build(tmp_path, monkeypatch, False)
    base = tmp_path / "courses" / "gen-ai" / "01-rag"
    _write(base / "broken.md", "---\ntitle: [unclosed\n  bad: : yaml\n---\n\nbody\n")
    _write(base / "weird-order.md", "---\ntitle: Weird\norder: first\n---\n\nbody\n")
    _write(base / "zero.md", "---\ntitle: Zero\norder: 0\n---\n\nbody\n")
    _write(base / "_module.md", "---\ntitle: [oops\n---\n")
    courses._load.cache_clear()
    yield client
    courses._load.cache_clear()


def test_bad_lesson_files_do_not_break_the_catalog(robust: TestClient) -> None:
    r = robust.get("/api/courses")
    assert r.status_code == 200
    gen = next(c for c in r.json() if c["id"] == "gen-ai")
    ids = [lesson["id"] for lesson in gen["modules"][0]["lessons"]]
    assert "gen-ai/01-rag/broken" not in ids
    assert ids[0] == "gen-ai/01-rag/zero"  # order: 0 sorts first, not as 999
    assert ids[-1] == "gen-ai/01-rag/weird-order"  # unusable order falls back to last
    assert robust.get("/api/courses/lessons/gen-ai/01-rag/weird-order").status_code == 200
