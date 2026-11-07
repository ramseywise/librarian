"""Slides in production: the API serves prebuilt files and never builds (F14)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from librarian.api.routers import courses as courses_routes
from librarian.config import Settings
from librarian.courses import slides

MOD = "gen-ai/01-rag"
YAML = "deck:\n  title: T\nparts:\n  - title: P\n    slides:\n      - title: Yaml slide\n"


def _write(path: Path, text: str | bytes = "x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    (path.write_bytes if isinstance(text, bytes) else path.write_text)(text)  # type: ignore[operator]


def _ship(root: Path, deck: str, png: bytes, spec: Path) -> None:
    """A prebuilt deck folder as `build_deck` leaves it."""
    _write(root / deck / "slides.json", '[{"title": "Built", "text": "Built", "notes": ""}]')
    _write(
        root / deck / "built.json",
        f'{{"stamp": "{slides.stamp(spec)}", "ok": true, "pngs": 1, "renderer": true, "at": 0}}',
    )
    _write(root / deck / "slide-01.png", png)


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    courses = tmp_path / "courses"
    _write(courses / "gen-ai" / "01-rag" / "slides" / "deck.yaml", YAML)
    monkeypatch.setattr(slides, "COURSES_DIR", courses)
    monkeypatch.setattr(slides, "DEV_BUILD", False)

    def boom(*a: object, **k: object) -> None:
        raise AssertionError("a build was attempted")

    monkeypatch.setattr(subprocess, "run", boom)
    monkeypatch.setattr(slides, "_run_build", boom)
    monkeypatch.setattr(slides.shutil, "which", lambda name: f"/bin/{name}")
    app = FastAPI()
    app.include_router(courses_routes.router)
    with TestClient(app) as c:
        yield c


def test_get_never_builds_when_the_setting_is_off(client: TestClient) -> None:
    body = client.get(f"/api/courses/slides/{MOD}").json()
    assert body["status"] == "text" and body["stale"] is False and body["needs"] == []
    assert body["slides"][0]["title"] == "Yaml slide"
    assert not slides._RUNNING


def test_post_build_is_a_404_when_off(client: TestClient) -> None:
    assert client.post(f"/api/courses/slides/{MOD}/build").status_code == 404
    assert not slides._RUNNING


def test_post_build_works_when_on(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    def run(spec: Path, out: Path) -> tuple[bool, str]:
        _write(out / "slides.json", '[{"title": "T1", "text": "T1", "notes": ""}]')
        return True, ""

    monkeypatch.setattr(slides, "DEV_BUILD", True)
    monkeypatch.setattr(slides, "_run_build", run)
    assert client.get(f"/api/courses/slides/{MOD}").json()["stale"] is True
    assert client.post(f"/api/courses/slides/{MOD}/build").status_code == 200
    slides.wait(MOD, 5)
    assert client.get(f"/api/courses/slides/{MOD}").json()["slides"][0]["title"] == "T1"


def test_served_from_the_content_dir(client: TestClient) -> None:
    spec = slides.COURSES_DIR / "gen-ai" / "01-rag" / "slides" / "deck.yaml"
    _ship(slides.CONTENT_DIR, MOD, b"content-png", spec)
    body = client.get(f"/api/courses/slides/{MOD}").json()
    assert body["status"] == "ready" and body["slides"][0]["title"] == "Built"
    img = client.get(body["slides"][0]["image"])
    assert img.status_code == 200 and img.content == b"content-png"


def test_content_dir_wins_over_the_state_dir_and_the_state_dir_is_the_fallback(
    client: TestClient,
) -> None:
    spec = slides.COURSES_DIR / "gen-ai" / "01-rag" / "slides" / "deck.yaml"
    _ship(slides.BUILD_DIR, MOD, b"state-png", spec)
    url = f"/api/courses/slide-image/{MOD}/1"
    assert client.get(url).content == b"state-png"  # fallback: today's var/slides
    _ship(slides.CONTENT_DIR, MOD, b"content-png", spec)
    assert client.get(url).content == b"content-png"


@pytest.mark.parametrize(
    "deck", ["private/c/m", "gen-ai/private", "../etc/passwd", "gen-ai/..", "gen-ai/%2e%2e/x"]
)
def test_traversal_and_private_decks_are_refused(client: TestClient, deck: str) -> None:
    assert client.get(f"/api/courses/slides/{deck}").status_code == 404
    assert client.get(f"/api/courses/slide-image/{deck}/1").status_code == 404
    assert slides.image_path(deck, 1) is None


def test_private_decks_in_the_content_dir_are_never_served(client: TestClient) -> None:
    spec = slides.COURSES_DIR / "gen-ai" / "01-rag" / "slides" / "deck.yaml"
    _ship(slides.CONTENT_DIR, "private/gen-ai/01-rag", b"secret", spec)
    assert client.get("/api/courses/slide-image/private/gen-ai/01-rag/1").status_code == 404
    assert slides.image_path("private/gen-ai/01-rag", 1) is None


def test_a_symlinked_png_pointing_out_of_the_deck_folder_is_refused(
    client: TestClient, tmp_path: Path
) -> None:
    spec = slides.COURSES_DIR / "gen-ai" / "01-rag" / "slides" / "deck.yaml"
    _ship(slides.CONTENT_DIR, MOD, b"ok", spec)
    outside = tmp_path / "outside.png"
    outside.write_bytes(b"leak")
    link = slides.CONTENT_DIR / MOD / "slide-02.png"
    link.symlink_to(outside)
    assert client.get(f"/api/courses/slide-image/{MOD}/2").status_code == 404


def test_settings_defaults(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    for var in ("LIBRARIAN_DEV_BUILD_SLIDES", "LIBRARIAN_CONTENT_DIR", "LIBRARIAN_STATE_DIR"):
        monkeypatch.delenv(var, raising=False)
    s = Settings(root=tmp_path)
    assert s.dev_build_slides is False
    assert s.content_slides_dir == tmp_path / "var" / "content" / "current" / "slides"
    monkeypatch.setenv("LIBRARIAN_DEV_BUILD_SLIDES", "1")
    monkeypatch.setenv("LIBRARIAN_CONTENT_DIR", str(tmp_path / "c"))
    s = Settings(root=tmp_path)
    assert s.dev_build_slides is True and s.content_slides_dir == tmp_path / "c" / "slides"
