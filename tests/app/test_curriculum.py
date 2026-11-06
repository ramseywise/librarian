"""Curriculum facet of the graph (librarian/courses/curriculum.py)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.routers import curriculum as curriculum_routes
from librarian.courses import curriculum
from librarian.courses.catalog import Catalog, LessonRec, WikiRef


def _lesson(lid: str, course: str, module: str, concepts: list[str]) -> LessonRec:
    return LessonRec(
        id=lid, course=course, module=module, title=lid, summary="", order=1, section="",
        kind="reading", source="", body="", concepts=concepts,
    )  # fmt: skip


def _catalog() -> Catalog:
    lessons = [
        _lesson("ai/rag/a", "ai", "rag", ["bm25", "rerank", "wrong-project"]),
        _lesson("ai/rag/b", "ai", "rag", ["rerank", "gone"]),
        _lesson("ai/00-start-here/readme", "ai", "00-start-here", ["orientation"]),
        _lesson("data/stats/a", "data", "stats", ["bm25"]),
    ]
    module = lambda mid, ls: {"id": mid, "title": mid.upper(), "lessons": [{"id": x} for x in ls]}  # noqa: E731
    courses = [
        {
            "id": "ai",
            "title": "AI",
            "modules": [
                module("00-start-here", ["ai/00-start-here/readme"]),
                module("rag", ["ai/rag/a", "ai/rag/b"]),
            ],
        },
        {
            "id": "data",
            "title": "Data",
            "modules": [
                module("stats", ["data/stats/a"]),
                module("viz", []),
                module("sources", []),
            ],
        },
        {"id": "leftover", "title": "leftover", "modules": []},
    ]
    wiki = {
        pid: WikiRef(pid, pid, "", domain)
        for pid, domain in {
            "bm25": "rag",
            "rerank": "rag",
            "wrong-project": "projects",
            "orientation": "meta",
            "gone": "rag",
        }.items()
    }
    return Catalog(courses, {r.id: r for r in lessons}, wiki, {})


PUBLIC = {
    "bm25": "rag",
    "rerank": "rag",
    "wrong-project": "projects",
    "orientation": "meta",
    "unlinked": "patterns",
    "new-page": "rag",
}


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setattr(curriculum, "SNAPSHOT", tmp_path / "cache" / "curriculum.json")
    monkeypatch.setattr(curriculum, "catalog", _catalog)
    monkeypatch.setattr(curriculum, "public_page_domains", lambda: dict(PUBLIC))
    monkeypatch.setattr(curriculum, "_current_signature", lambda: [1, 1])
    app = FastAPI()
    app.include_router(curriculum_routes.router)
    return TestClient(app)


def _module(payload: dict, course: str, module: str) -> dict:
    c = next(c for c in payload["courses"] if c["id"] == course)
    return next(m for m in c["modules"] if m["id"] == module)


def test_modules_list_pages_best_linked_first(client: TestClient) -> None:
    body = client.get("/api/graph/curriculum").json()
    assert _module(body, "ai", "rag")["pageIds"] == ["rerank", "bm25"]
    assert _module(body, "ai", "rag")["firstLesson"] == "ai/rag/a"
    assert body["courses"][0]["pageIds"] == ["rerank", "bm25"]


def test_empty_module_is_kept_so_the_gap_shows(client: TestClient) -> None:
    viz = _module(client.get("/api/graph/curriculum").json(), "data", "viz")
    assert viz["pageIds"] == []
    assert viz["firstLesson"] is None


def test_reading_list_module_is_not_a_topic(client: TestClient) -> None:
    body = client.get("/api/graph/curriculum").json()
    assert [m["id"] for m in body["courses"][1]["modules"]] == ["stats", "viz"]


def test_course_with_no_modules_is_dropped(client: TestClient) -> None:
    body = client.get("/api/graph/curriculum").json()
    assert [c["id"] for c in body["courses"]] == ["ai", "data"]


def test_start_here_and_project_pages_are_not_members(client: TestClient) -> None:
    body = client.get("/api/graph/curriculum").json()
    assert [m["id"] for m in body["courses"][0]["modules"]] == ["rag"]
    beyond = {b["domain"]: b["pageIds"] for b in body["beyond"]}
    assert beyond["projects"] == ["wrong-project"]
    assert beyond["meta"] == ["orientation"]


def test_every_public_page_is_reachable_exactly_where_expected(client: TestClient) -> None:
    body = client.get("/api/graph/curriculum").json()
    linked = {p for c in body["courses"] for p in c["pageIds"]}
    unlinked = {p for b in body["beyond"] for p in b["pageIds"]}
    assert linked | unlinked == set(PUBLIC)
    assert not linked & unlinked


def test_non_public_pages_never_appear(client: TestClient) -> None:
    # `gone` is in the catalog but no longer public: private now, or deleted since the build.
    assert "gone" not in client.get("/api/graph/curriculum").text


def test_primary_course_is_the_one_with_most_links(client: TestClient) -> None:
    primary = client.get("/api/graph/curriculum").json()["primaryCourse"]
    assert primary == {"bm25": "ai", "rerank": "ai"}  # bm25: a 1-1 tie, the earlier course


def test_snapshot_is_served_without_touching_the_catalog(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert curriculum.write_snapshot() is not None

    def boom() -> Catalog:
        raise AssertionError("catalog must not be built when a snapshot exists")

    monkeypatch.setattr(curriculum, "catalog", boom)
    body = client.get("/api/graph/curriculum").json()
    assert body["stale"] is False
    assert _module(body, "ai", "rag")["pageIds"] == ["rerank", "bm25"]


def test_old_snapshot_is_served_and_flagged_stale(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    curriculum.write_snapshot()
    monkeypatch.setattr(curriculum, "_current_signature", lambda: [2, 2])
    body = client.get("/api/graph/curriculum").json()
    assert body["stale"] is True
    assert "new-page" in next(b["pageIds"] for b in body["beyond"] if b["domain"] == "rag")


def test_corrupt_snapshot_falls_back_to_the_catalog(client: TestClient) -> None:
    curriculum.SNAPSHOT.parent.mkdir(parents=True)
    curriculum.SNAPSHOT.write_text("{not json")
    assert _module(client.get("/api/graph/curriculum").json(), "ai", "rag")["pageIds"]


def test_write_snapshot_never_raises(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    def boom() -> Catalog:
        raise RuntimeError("catalog down")

    monkeypatch.setattr(curriculum, "catalog", boom)
    assert curriculum.write_snapshot() is None
    assert not curriculum.SNAPSHOT.exists()


def test_snapshot_is_valid_json_on_disk(client: TestClient) -> None:
    curriculum.write_snapshot()
    assert json.loads(curriculum.SNAPSHOT.read_text())["signature"] == [1, 1]
