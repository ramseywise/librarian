"""learning_next and concept_status in the shared tool registry: per user, public pages only."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from librarian import accounts
from librarian.agent import tools
from librarian.agent.tools import CHAT, MCP, ToolContext, tools_for
from librarian.config import get_settings
from librarian.courses import catalog as courses
from librarian.courses import learning
from librarian.db import get_engine

PAGE = "---\ntitle: {t}\ntags: [{g}]\nsummary: {t} summary.\nupdated: 2026-10-28\n---\n\n# {t}\n"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


@pytest.fixture()
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[tuple[str, str]]:
    wiki = tmp_path / "wiki"
    _write(wiki / "rag" / "hybrid-search.md", PAGE.format(t="Hybrid Search", g="rag, concept"))
    _write(wiki / "private" / "client-secret.md", PAGE.format(t="Client Secret", g="project"))
    root = tmp_path / "courses"
    _write(root / "gen-ai" / "01-rag" / "_module.md", "---\ntitle: RAG\n---\n")
    _write(
        root / "gen-ai" / "01-rag" / "intro.md",
        "---\ntitle: Intro\nwiki: [hybrid-search]\n---\n\nBody.\n",
    )
    monkeypatch.setenv("LIBRARIAN_API_TOKEN", "bootstrap-token-0123456789abcdef")
    get_settings.cache_clear()
    monkeypatch.setattr(courses, "COURSES_DIR", root)
    monkeypatch.setattr(courses, "WIKI_DIR", wiki)
    monkeypatch.setattr(courses, "LESSON_VEC_CACHE", tmp_path / "cache" / "lessons.npz")
    monkeypatch.setattr(courses, "_semantic_neighbours", lambda texts, ids: None)
    courses._load.cache_clear()
    engine = get_engine()
    ids = []
    for email in ("ada@example.com", "bob@example.com"):
        accounts.add_user(engine, email)
        ids.append(accounts.get_user(engine, email).id)  # type: ignore[union-attr]
    yield ids[0], ids[1]
    courses._load.cache_clear()
    monkeypatch.undo()
    get_settings.cache_clear()


def _fail(user: str) -> None:
    for _ in range(2):
        learning.record_event(
            user, learning.EventIn(kind="drill_attempt", lesson="gen-ai/01-rag/intro", score=0.0)
        )


def _tool(name: str, surface: str = CHAT) -> tools.Tool:
    return next(t for t in tools_for(surface) if t.name == name)


def _run(name: str, user: str | None, **args: object) -> str:
    t = _tool(name)
    out = t.fn(t.params(**args), ToolContext(surface=CHAT, user_id=user))
    return str(out)


def test_both_surfaces_get_the_learning_tools_and_no_lab_solutions() -> None:
    for surface in (CHAT, MCP):
        assert {"learning_next", "concept_status"} <= {t.name for t in tools_for(surface)}
    assert {
        "search_lessons",
        "read_page",
        "learning_next",
        "concept_status",
    } == tools.LEARNING_TOOLS
    assert not any("lab" in n or "solution" in n for n in tools.LEARNING_TOOLS)


def test_learning_next_is_per_user(world: tuple[str, str]) -> None:
    ada, bob = world
    _fail(ada)
    assert "Hybrid Search" in _run("learning_next", ada)
    assert "No concepts are due" in _run("learning_next", bob)


def test_concept_status_reads_the_callers_evidence_only(world: tuple[str, str]) -> None:
    ada, bob = world
    _fail(ada)
    assert "due for review" in _run("concept_status", ada, page_id="hybrid-search")
    assert "No study evidence" in _run("concept_status", bob, page_id="hybrid-search")


def test_private_and_unknown_ids_read_alike(world: tuple[str, str]) -> None:
    ada, _ = world
    private = _run("concept_status", ada, page_id="client-secret")
    unknown = _run("concept_status", ada, page_id="client-secrex")
    assert private.replace("client-secret", "X") == unknown.replace("client-secrex", "X")
    assert "Client Secret" not in private


def test_no_user_says_so(world: tuple[str, str]) -> None:
    ada, _ = world
    _fail(ada)
    # No user attached: the owner's (empty) evidence is read, never another user's rows.
    assert "Hybrid Search" not in _run("learning_next", None)
