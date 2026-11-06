"""The private overlay (figures, readings) and the course sources route.

Book and paper figures live only in `data/courses/private/<course>/<module>/assets/sources/`;
a module's `readings:` list lives in the mirror's `_module.md`; lessons link into the sibling
sources repo through `COURSE_SOURCES_DIR`. All of it runs on tmp trees.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.routers import courses as courses_routes
from librarian.courses import catalog as courses
from librarian.courses import overlay, sources
from librarian.wiki.course_leaks import scan_public_lessons

FIG = "gen-ai/01-rag/assets/sources/book/fig-1.png"


def write(path: Path, text: str | bytes = "x") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(text, bytes):
        path.write_bytes(text)
    else:
        path.write_text(text)
    return path


@pytest.fixture
def env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Path]:
    root = tmp_path / "courses"
    lae = tmp_path / "lae"
    write(root / "gen-ai" / "_course.md", "---\ntitle: Gen AI\norder: 1\n---\n")
    write(
        root / "gen-ai" / "01-rag" / "_module.md",
        "---\ntitle: RAG\norder: 1\nreadings_count: 2\n---\n",
    )
    write(
        root / "gen-ai" / "01-rag" / "intro.md",
        "---\ntitle: Intro\norder: 1\n---\n\n![fig](assets/sources/book/fig-1.png)\n\n"
        "[book](sources/book.pdf#page=3) [dir](sources/) [gone](sources/nope.pdf) "
        "[up](../sources/course.pdf) [web](https://example.com/sources/x.pdf)\n",
    )
    write(root / "gen-ai" / "01-rag" / "assets" / "public.png", b"png")
    write(
        root / "gen-ai" / "sources" / "_module.md", "---\ntitle: Sources\nreadings_count: 1\n---\n"
    )
    # The private mirror: a figure and the readings overlay.
    write(
        root / "private" / "gen-ai" / "01-rag" / "assets" / "sources" / "book" / "fig-1.png", b"png"
    )
    write(
        root / "private" / "gen-ai" / "01-rag" / "_module.md",
        "---\nreadings:\n- title: Book\n  source: gen-ai/01-rag/sources/book.pdf\n"
        "- title: Paper\n  source: gen-ai/01-rag/sources/paper.pdf\n---\n",
    )
    write(lae / "gen-ai" / "01-rag" / "sources" / "book.pdf", b"%PDF-book")
    write(lae / "gen-ai" / "sources" / "course.pdf", b"%PDF-course")
    write(tmp_path / "secret.pdf", b"%PDF-secret")  # a sibling of the sources dir
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    monkeypatch.setattr(courses, "COURSES_DIR", root)
    monkeypatch.setattr(courses, "WIKI_DIR", wiki)
    monkeypatch.setattr(courses, "DRILL_LOG", tmp_path / "none.md")
    monkeypatch.setattr(courses, "LESSON_VEC_CACHE", tmp_path / "cache" / "lessons.npz")
    monkeypatch.setattr(courses, "_semantic_neighbours", lambda texts, ids: None)
    monkeypatch.setattr(sources, "SOURCES_DIR", lae)
    monkeypatch.setattr(sources, "SERVE_SOURCES", True)
    courses._load.cache_clear()
    return {"root": root, "lae": lae, "tmp": tmp_path}


@pytest.fixture
def client(env: dict[str, Path]) -> TestClient:
    app = FastAPI()
    app.include_router(courses_routes.router)
    with TestClient(app) as c:
        yield c
    courses._load.cache_clear()


# ── Figures: the asset route falls back to the private mirror ────────────────


def test_figure_served_from_the_mirror_when_missing_publicly(client: TestClient) -> None:
    r = client.get(f"/api/courses/files/{FIG}")
    assert r.status_code == 200 and r.content == b"png"
    assert not (Path(courses.COURSES_DIR) / FIG).exists()


def test_public_file_wins_over_the_mirror(client: TestClient, env: dict[str, Path]) -> None:
    write(env["root"] / FIG, b"public")
    assert client.get(f"/api/courses/files/{FIG}").content == b"public"


def test_figure_in_neither_tree_is_404_not_a_server_error(client: TestClient) -> None:
    assert (
        client.get("/api/courses/files/gen-ai/01-rag/assets/sources/book/none.png").status_code
        == 404
    )


@pytest.mark.parametrize(
    "path",
    [
        "gen-ai/01-rag/assets/sources/%2e%2e/%2e%2e/%2e%2e/secret.png",
        "../secret.png",
        "gen-ai/01-rag/assets/sources/book/fig-1.txt",
    ],
)
def test_figure_route_still_refuses_traversal_and_non_images(client: TestClient, path: str) -> None:
    assert client.get(f"/api/courses/files/{path}").status_code in (400, 404)


def test_mirror_symlink_out_of_the_tree_is_not_served(
    client: TestClient, env: dict[str, Path]
) -> None:
    outside = write(env["tmp"] / "outside.png", b"secret")
    link = env["root"] / "private" / "gen-ai" / "01-rag" / "assets" / "sources" / "link.png"
    link.symlink_to(outside)
    assert client.get("/api/courses/files/gen-ai/01-rag/assets/sources/link.png").status_code == 400


def test_overlay_helpers_only_map_inside_the_public_tree(tmp_path: Path) -> None:
    root = tmp_path / "courses"
    assert overlay.private_mirror(root / "a" / "b.png", root) == root / "private" / "a" / "b.png"
    assert overlay.private_mirror(root / "private" / "a.png", root) is None
    assert overlay.private_mirror(tmp_path / "elsewhere.png", root) is None
    assert overlay.is_sources_asset(("a", "m", "assets", "sources", "x.png"))
    assert not overlay.is_sources_asset(("a", "m", "assets", "x.png"))


def test_leak_check_does_not_flag_figure_links(env: dict[str, Path]) -> None:
    """The link resolves lexically to the public path, so the overlay is invisible to it."""
    blockers, scanned = scan_public_lessons(env["root"], lambda name: False)
    assert blockers == [] and scanned > 0
    assert "assets/sources/book/fig-1.png" in (env["root"] / "gen-ai/01-rag/intro.md").read_text()


# ── Readings: the list is private, the count is public ────────────────────────


def test_readings_merge_from_the_overlay(client: TestClient) -> None:
    mod = client.get("/api/courses").json()[0]["modules"][0]
    assert mod["id"] == "01-rag"
    assert [r["title"] for r in mod["readings"]] == ["Book", "Paper"]
    assert mod["readingsCount"] == 2


def test_without_the_overlay_only_the_count_remains(
    client: TestClient, env: dict[str, Path]
) -> None:
    (env["root"] / "private" / "gen-ai" / "01-rag" / "_module.md").unlink()
    courses._load.cache_clear()
    mods = {m["id"]: m for m in client.get("/api/courses").json()[0]["modules"]}
    assert mods["01-rag"]["readings"] == [] and mods["01-rag"]["readingsCount"] == 2
    # A module that is only a reading list stays listed, with its count.
    assert mods["sources"]["readingsCount"] == 1 and mods["sources"]["lessons"] == []


def test_private_overlay_module_is_not_marked_private(client: TestClient) -> None:
    mod = client.get("/api/courses").json()[0]["modules"][0]
    assert "private" not in mod


# ── Sources links: COURSE_SOURCES_DIR, served locally ────────────────────────


def test_lesson_detail_maps_only_links_whose_file_exists(client: TestClient) -> None:
    detail = client.get("/api/courses/lessons/gen-ai/01-rag/intro").json()
    assert detail["sourceLinks"] == {
        "sources/book.pdf": "gen-ai/01-rag/sources/book.pdf",
        "../sources/course.pdf": "gen-ai/sources/course.pdf",
    }
    assert "[book](sources/book.pdf#page=3)" in detail["body"]  # the markdown is untouched


def test_sources_route_serves_a_file(client: TestClient) -> None:
    r = client.get("/api/courses/sources/gen-ai/01-rag/sources/book.pdf")
    assert r.status_code == 200 and r.content == b"%PDF-book"


@pytest.mark.parametrize(
    "path",
    [
        "gen-ai/01-rag/sources/nope.pdf",
        "gen-ai/01-rag/sources",  # a directory
        "gen-ai/01-rag/sources/%2e%2e/%2e%2e/%2e%2e/secret.pdf",
        "%2e%2e/secret.pdf",
        "gen-ai/%2e%2e/%2e%2e/secret.pdf",
        "gen-ai/01-rag/sources/..%2f..%2f..%2fsecret.pdf",
        "%2fetc/passwd",
        "gen-ai/01-rag/sources/book.pdf%00.png",
        "gen-ai/.git/config",
    ],
)
def test_sources_route_refuses_traversal_and_misses(client: TestClient, path: str) -> None:
    assert client.get(f"/api/courses/sources/{path}").status_code in (400, 404)


def test_sources_route_refuses_a_symlink_out_of_the_dir(
    client: TestClient, env: dict[str, Path]
) -> None:
    (env["lae"] / "gen-ai" / "leak.pdf").symlink_to(env["tmp"] / "secret.pdf")
    assert client.get("/api/courses/sources/gen-ai/leak.pdf").status_code == 404


def test_sources_route_serves_only_under_a_sources_dir(
    client: TestClient, env: dict[str, Path]
) -> None:
    write(env["lae"] / "programming" / "drills" / "drill-log.md")
    assert client.get("/api/courses/sources/programming/drills/drill-log.md").status_code == 404
    assert sources.source_file("programming/drills/drill-log.md") is None


def test_source_file_rejects_escapes_directly(env: dict[str, Path]) -> None:
    assert sources.source_file("gen-ai/01-rag/sources/book.pdf") is not None
    for bad in ("../secret.pdf", "/etc/passwd", "gen-ai/../../secret.pdf", "", "a\0b", ".env"):
        assert sources.source_file(bad) is None, bad
    # Sibling directory whose name starts with the sources dir's name.
    sibling = env["lae"].parent / (env["lae"].name + "-private")
    write(sibling / "x.pdf")
    assert sources.source_file(f"../{sibling.name}/x.pdf") is None


def test_missing_sources_dir_reports_unavailable(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, env: dict[str, Path]
) -> None:
    monkeypatch.setattr(sources, "SOURCES_DIR", env["tmp"] / "no-such-dir")
    assert client.get("/api/courses/sources/gen-ai/01-rag/sources/book.pdf").status_code == 404
    assert client.get("/api/courses/lessons/gen-ai/01-rag/intro").json()["sourceLinks"] == {}


def test_serving_can_be_switched_off(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sources, "SERVE_SOURCES", False)
    assert client.get("/api/courses/sources/gen-ai/01-rag/sources/book.pdf").status_code == 404
    assert client.get("/api/courses/lessons/gen-ai/01-rag/intro").json()["sourceLinks"] == {}


@pytest.mark.parametrize(
    ("lesson_id", "href", "expected"),
    [
        ("c/m/x", "sources/a.pdf", "c/m/sources/a.pdf"),
        ("c/m/notes/x", "../sources/a.pdf", "c/m/sources/a.pdf"),
        ("c/m/notes/x", "../../sources/a.pdf#page=2", "c/sources/a.pdf"),
        ("c/m/x", "../other/sources/dir/a.pdf", "c/other/sources/dir/a.pdf"),
        ("c/m/x", "sources/a%20b.pdf", "c/m/sources/a b.pdf"),
        ("c/00-start-here/references", "sources/a.pdf", "c/sources/a.pdf"),
        ("c/00-start-here/references", "../d/01-m/sources/a.pdf", "d/01-m/sources/a.pdf"),
        ("c/m/x", "assets/sources/fig.png", None),
        ("c/m/x", "https://e.com/sources/a.pdf", None),
        ("c/m/x", "/sources/a.pdf", None),
        ("c/m/x", "../../../../sources/a.pdf", None),
        ("c/m/x", "other.pdf", None),
    ],
)
def test_resolve_link_forms(lesson_id: str, href: str, expected: str | None) -> None:
    assert sources.resolve_link(lesson_id, href) == expected


def test_config_defaults_and_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from librarian.config import Settings, get_settings

    root = get_settings().root
    monkeypatch.delenv("COURSE_SOURCES_DIR", raising=False)
    monkeypatch.delenv("SERVE_COURSE_SOURCES", raising=False)
    s = Settings(_env_file=None)
    assert s.course_sources_dir == root.parent / "learn-ai-engineering" and s.serve_course_sources
    monkeypatch.setenv("COURSE_SOURCES_DIR", str(tmp_path))
    monkeypatch.setenv("SERVE_COURSE_SOURCES", "false")
    s = Settings(_env_file=None)
    assert s.course_sources_dir == tmp_path and not s.serve_course_sources


# Orphan asset directories of retired practice courses (third-party images, deleted 2026-11-06).
DELETED_ASSET_MODULES = (
    "ng-s-deep-learning-nbks",
    "datatalks-mlops",
    "datatalks-data-engineering",
    "intro-to-machine-learning-in-python",
    "text-analytics-with-python",
)


def test_repo_has_no_tracked_or_public_source_figures() -> None:
    """The cleanup holds in the checked-out tree: nothing public under assets/sources/."""
    courses_dir = Path(__file__).resolve().parents[2] / "data" / "courses"
    public = [
        p
        for p in courses_dir.rglob("*")
        if p.is_file()
        and "private" not in p.relative_to(courses_dir).parts[:1]
        and overlay.is_sources_asset(p.relative_to(courses_dir).parts)
    ]
    assert public == []
    for name in DELETED_ASSET_MODULES:
        assert not any(courses_dir.glob(f"*/{name}"))
