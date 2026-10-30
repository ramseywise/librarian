"""Browser smoke test per UI tab: graph, courses, practice, chat.

Needs `make app` (API on :8000, UI on :5173); skipped otherwise by tests/e2e/conftest.py.
Never sends a chat message — the agent calls the Anthropic API, which bills.
"""

from __future__ import annotations

import json
import re
import urllib.request
from collections.abc import Iterator
from typing import Any

import pytest
from playwright.sync_api import Page, expect, sync_playwright

UI_URL = "http://localhost:5173"
API = "http://localhost:8000"

pytestmark = pytest.mark.e2e


def _get(path: str) -> Any:  # noqa: ANN401 — JSON
    with urllib.request.urlopen(API + path, timeout=30) as r:
        return json.load(r)


@pytest.fixture()
def page() -> Iterator[Page]:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        pg = browser.new_page(viewport={"width": 1400, "height": 900})
        errors: list[str] = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        yield pg
        browser.close()
        assert not errors, f"uncaught page errors: {errors}"


def _open_graph(page: Page) -> None:
    page.goto(UI_URL, timeout=15_000)
    expect(page.get_by_text("● live")).to_be_visible(timeout=20_000)
    page.wait_for_selector(".react-flow__node", timeout=20_000)


def test_graph_tab(page: Page) -> None:
    _open_graph(page)
    expect(page).to_have_title("Graph · Librarian")
    expect(page.get_by_role("button", name="Graph", exact=True)).to_have_attribute(
        "aria-current", "page"
    )
    filters = page.get_by_role("group", name="Filter by domain")
    for domain in _get("/api/graph")["domains"]:
        expect(filters.get_by_role("button", name=domain, exact=True)).to_be_visible()
    expect(filters.get_by_role("button", name="private", exact=True)).to_have_count(0)


def _lesson_with_concepts() -> dict[str, Any]:
    for course in _get("/api/courses"):
        for module in course["modules"]:
            for outline in module["lessons"]:
                lesson = _get(f"/api/courses/lessons/{outline['id']}")
                if lesson["concepts"]:
                    return lesson
    pytest.skip("no lesson links a wiki concept")


def test_courses_tab_and_concept_jump(page: Page) -> None:
    _open_graph(page)
    page.get_by_role("button", name="Courses", exact=True).click()
    expect(page).to_have_title("Courses · Librarian")

    lesson = _lesson_with_concepts()
    page.goto(f"{UI_URL}/#/courses/{lesson['id']}")
    expect(page).to_have_title(re.compile(re.escape(lesson["title"]) + r" · .+ · Librarian"))

    concept = lesson["concepts"][0]
    page.get_by_role("button", name=concept["title"]).first.click()
    # Back on the graph with the concept's detail panel open (focusPage applied).
    expect(page).to_have_title("Graph · Librarian")
    expect(page.get_by_role("button", name="Close")).to_be_visible(timeout=15_000)


def test_practice_tab(page: Page) -> None:
    drills = _get("/api/courses/practice")
    if not drills:
        pytest.skip("no drills imported")
    page.goto(f"{UI_URL}/#/practice", timeout=15_000)
    expect(page).to_have_title("Practice · Librarian")
    expect(page.get_by_text(drills[0]["title"]).first).to_be_visible(timeout=15_000)

    page.goto(f"{UI_URL}/#/courses/{drills[0]['id']}")
    timer = page.get_by_role("group", name="Drill timer").first
    expect(timer).to_be_visible(timeout=15_000)
    expect(timer.get_by_role("button", name=re.compile("Start"))).to_be_visible()


def test_chat_panel_idle(page: Page) -> None:
    _open_graph(page)
    expect(page.get_by_role("textbox", name="Ask the wiki agent")).to_be_visible()
    expect(page.get_by_role("button", name="Clear conversation")).to_be_disabled()
    expect(page.get_by_role("log", name="Conversation")).to_be_visible()


def test_escape_closes_one_overlay_at_a_time() -> None:
    """Narrow layout: chat overlay + lessons drawer open; one Escape closes only the drawer."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        pg = browser.new_page(viewport={"width": 1000, "height": 800})
        outline = _get("/api/courses")[0]["modules"][0]["lessons"][0]
        pg.goto(f"{UI_URL}/#/courses/{outline['id']}", timeout=15_000)
        drawer_btn = pg.get_by_role("button", name="Lessons", exact=True)
        expect(drawer_btn).to_be_visible(timeout=15_000)
        pg.get_by_role("button", name="Agent Chat ↗").click()
        drawer_btn.click()
        expect(pg.locator(".course-drawer.is-open")).to_have_count(1)

        pg.keyboard.press("Escape")
        expect(pg.locator(".course-drawer.is-open")).to_have_count(0)
        expect(pg.locator("#chat-panel")).to_have_count(1)
        expect(drawer_btn).to_be_focused()
        pg.keyboard.press("Escape")
        expect(pg.locator("#chat-panel")).to_have_count(0)
        browser.close()
