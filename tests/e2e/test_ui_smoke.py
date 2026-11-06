"""Browser smoke test per UI tab: graph, courses, practice, chat.

Needs `make app` (API on :8000, UI on :5173; E2E_API_URL and E2E_UI_URL point elsewhere);
skipped otherwise by tests/e2e/conftest.py.
Never sends a chat message — the agent calls the Anthropic API, which bills.
"""

from __future__ import annotations

import json
import os
import re
import urllib.request
from collections import Counter
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from playwright.sync_api import Page, expect, sync_playwright

UI_URL = os.environ.get("E2E_UI_URL", "http://localhost:5173")
API = os.environ.get("E2E_API_URL", "http://localhost:8000")
AXE_JS = Path(__file__).parents[2] / "apps/web/node_modules/axe-core/axe.min.js"

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
    """The map opens on the atlas, a canvas ring whose sector labels are real links."""
    page.goto(UI_URL, timeout=15_000)
    expect(page.get_by_text("● live")).to_be_visible(timeout=20_000)
    page.wait_for_selector(".atlas-label", timeout=20_000)


def _largest_domain() -> tuple[str, int]:
    nodes = _get("/api/graph")["nodes"]
    counts = Counter(n["data"]["domain"][0] for n in nodes if n["data"]["domain"])
    return counts.most_common(1)[0]


def test_graph_tab(page: Page) -> None:
    _open_graph(page)
    expect(page).to_have_title("Graph · Librarian")
    expect(page.get_by_role("button", name="Graph", exact=True)).to_have_attribute(
        "aria-current", "page"
    )
    filters = page.get_by_role("group", name="Filter by curriculum")
    curriculum = _get("/api/graph/curriculum")
    for course in curriculum["courses"]:
        expect(
            filters.get_by_role(
                "button", name=f"{course['title']} {len(course['pageIds'])}", exact=True
            )
        ).to_be_visible()
    for beyond in curriculum["beyond"]:
        expect(
            filters.get_by_role(
                "button", name=f"{beyond['domain']} {len(beyond['pageIds'])}", exact=True
            )
        ).to_be_visible()
    expect(filters.get_by_text("private", exact=True)).to_have_count(0)


def test_atlas_zooms_in_and_back(page: Page) -> None:
    """Sector, page, reload, Esc: every level is a link and the way back is one key a level."""
    _open_graph(page)
    domain, size = _largest_domain()
    assert size > 150, "the largest domain should exceed the cap this test checks"

    page.locator(".atlas-label", has_text=domain).first.click()
    expect(page).to_have_url(f"{UI_URL}/#/map/domain/{domain}", timeout=5_000)
    page.wait_for_selector(".react-flow__node", timeout=20_000)
    expect(page.locator(".map-count")).to_have_text(f"showing 150 of {size}")
    expect(page.get_by_role("button", name="Show 300")).to_be_visible()

    # A page is a level of its own, with its neighbourhood and its detail panel.
    node = page.locator(".react-flow__node-wikiNode").first
    node.dblclick()
    expect(page).to_have_url(re.compile(rf"#/map/domain/{domain}/.+"), timeout=5_000)
    expect(page.get_by_role("button", name="Close")).to_be_visible(timeout=5_000)
    expect(page.get_by_role("navigation", name="Map level")).to_contain_text("Atlas")
    level = page.url

    page.reload()
    page.wait_for_selector(".react-flow__node", timeout=20_000)
    expect(page).to_have_url(level)
    expect(page.locator(".map-crumb-page")).to_be_visible()

    page.keyboard.press("Escape")
    expect(page).to_have_url(f"{UI_URL}/#/map/domain/{domain}", timeout=5_000)
    expect(page.locator(".map-crumb-page")).to_have_count(0)  # the level has rendered
    page.keyboard.press("Escape")
    expect(page).to_have_url(f"{UI_URL}/#/map/domain", timeout=5_000)
    page.wait_for_selector(".atlas-label", timeout=20_000)


def test_atlas_arranges_by_course_and_search_finds_an_alias(page: Page) -> None:
    _open_graph(page)
    page.get_by_role("button", name="Course", exact=True).click()
    expect(page).to_have_url(f"{UI_URL}/#/map/course", timeout=5_000)
    curriculum = _get("/api/graph/curriculum")
    expect(page.locator(".atlas-label")).to_have_count(
        len([c for c in curriculum["courses"] if set(c["pageIds"])]) + 1, timeout=20_000
    )

    terms = _get("/api/glossary")["terms"]
    term = next(t for t in terms if t["aliases"] and t["page"])
    page.get_by_role("combobox", name="Search the map").fill(term["aliases"][0])
    expect(page.get_by_role("option").first).to_contain_text(term["label"])


def test_focused_view_draws_terms_as_a_layer(page: Page) -> None:
    domain, _ = _largest_domain()
    page.goto(f"{UI_URL}/#/map/domain/{domain}", timeout=15_000)
    page.wait_for_selector(".react-flow__node-termNode", timeout=30_000)
    page.get_by_label("Glossary terms").uncheck()
    expect(page.locator(".react-flow__node-termNode")).to_have_count(0)


def test_private_terms_stay_private() -> None:
    """Public mentions only: every page a term lists is in the public graph."""
    public = {n["id"] for n in _get("/api/graph")["nodes"]}
    for pages in _get("/api/glossary/mentions").values():
        assert set(pages) <= public


def test_module_filter_shows_its_pages(page: Page) -> None:
    _open_graph(page)
    curriculum = _get("/api/graph/curriculum")
    course, module = next(
        (c, m) for c in curriculum["courses"] for m in c["modules"] if m["pageIds"]
    )
    filters = page.get_by_role("group", name="Filter by curriculum")
    filters.get_by_role("button", name=f"Show modules in {course['title']}").click()
    filters.get_by_role(
        "button", name=f"{module['title']} {len(module['pageIds'])}", exact=True
    ).click()
    # React Flow drops off-screen cards, so count the status line, not the DOM.
    pages = page.locator(".graph-status-count")
    expect(pages).to_contain_text(f"of {len(_get('/api/graph')['nodes'])} pages")
    shown = int(pages.inner_text().split()[1])
    assert shown == len(module["pageIds"])


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


@pytest.mark.parametrize(
    ("route", "ready"),
    [
        ("/", ".atlas-label"),
        ("/#/map/domain/rag", ".react-flow__node"),
        ("/#/courses", ".course-card"),
        ("lesson", ".lesson-main-body p"),
        ("/#/practice", "[aria-label='Drill timer']"),
    ],
)
def test_no_serious_axe_violations(page: Page, route: str, ready: str) -> None:
    """axe-core per view: no serious/critical WCAG violations (contrast, landmarks,
    nested interactive controls, links told apart by colour alone)."""
    if not AXE_JS.exists():
        pytest.skip("axe-core not installed (npm install in apps/web)")
    if route == "lesson":
        route = f"/#/courses/{_get('/api/courses')[0]['modules'][0]['lessons'][0]['id']}"
    page.goto(UI_URL + route, timeout=15_000)
    page.wait_for_selector(ready, timeout=20_000)
    page.add_script_tag(path=str(AXE_JS))
    result = page.evaluate("axe.run(document, {resultTypes: ['violations']})")
    bad = [
        (v["id"], v["impact"], [n["target"] for n in v["nodes"][:3]])
        for v in result["violations"]
        if v["impact"] in ("serious", "critical")
    ]
    assert not bad, bad
