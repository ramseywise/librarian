"""Browser smoke test per UI tab: graph, courses, practice, chat.

Needs `make app` (API on :8000, UI on :5173; E2E_API_URL and E2E_UI_URL point elsewhere, and
E2E_TOKEN is the API token of a server that requires one: `make e2e-container` sets all three);
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
# Set when the server under test has LIBRARIAN_API_TOKEN (the container): sent on API calls and
# seeded into localStorage, where the UI keeps it, so the page never stops at the token prompt.
TOKEN = os.environ.get("E2E_TOKEN", "")
AXE_JS = Path(__file__).parents[2] / "app/node_modules/axe-core/axe.min.js"

pytestmark = pytest.mark.e2e


def _get(path: str) -> Any:  # noqa: ANN401 — JSON
    req = urllib.request.Request(API + path)
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


@pytest.fixture()
def page() -> Iterator[Page]:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        pg = browser.new_page(viewport={"width": 1400, "height": 900})
        if TOKEN:
            pg.add_init_script(
                f"window.localStorage.setItem('librarian.apiToken', {json.dumps(TOKEN)})"
            )
        errors: list[str] = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        yield pg
        browser.close()
        assert not errors, f"uncaught page errors: {errors}"


def _open_graph(page: Page) -> None:
    """The map opens on the atlas, a canvas ring whose sector labels are real links."""
    page.goto(UI_URL, timeout=15_000)
    # The graph payload for ~1,700 pages takes over 20 s on a cold dev server.
    page.wait_for_selector(".atlas-label", timeout=60_000)


def _graph() -> dict[str, Any]:
    return _get("/api/graph")


def _default_cap() -> int:
    """`DEFAULT_CAP` in mapRoute.ts: the pages a sector opens on."""
    src = (Path(__file__).parents[2] / "app/src/utils/mapRoute.ts").read_text()
    match = re.search(r"export const DEFAULT_CAP = (\d+)", src)
    assert match, "DEFAULT_CAP not found in mapRoute.ts"
    return int(match[1])


def _domain_sectors() -> dict[str, tuple[str, int]]:
    """The domain atlas as the page draws it: sector id -> (label, pages).

    One sector per course area that has pages, then each directory in no area on its own.
    """
    graph = _graph()
    area_of = {d: a["id"] for a in graph["areas"] for d in a["domains"]}
    title = {a["id"]: a["title"] for a in graph["areas"]}
    counts: Counter[str] = Counter()
    for n in graph["nodes"]:
        if n["data"]["domain"]:
            d = n["data"]["domain"][0]
            counts[area_of.get(d, d)] += 1
    return {sid: (title.get(sid, sid), n) for sid, n in counts.items()}


def _wiki_sectors() -> Counter[str]:
    return Counter(n["data"]["domain"][0] for n in _graph()["nodes"] if n["data"]["domain"])


def test_graph_tab(page: Page) -> None:
    _open_graph(page)
    expect(page).to_have_title("Graph · Librarian")
    sections = page.get_by_role("navigation", name="Sections")
    expect(sections.get_by_role("link", name="Graph", exact=True)).to_have_attribute(
        "aria-current", "page"
    )
    # The atlas opens by domain: one label per course area (and per directory in no area).
    sectors = _domain_sectors()
    expect(page.locator(".atlas-label")).to_have_count(len(sectors), timeout=20_000)
    for label, _ in sectors.values():
        expect(page.locator(".atlas-label", has_text=label).first).to_be_visible()

    # The filters, docked under the chat, list every wiki directory with its page count under
    # Browse by: Wiki, and nothing private.
    filters = page.get_by_role("region", name="Filters")
    page.get_by_role("button", name="Wiki", exact=True).click()
    dirs = filters.get_by_role("group", name="Wiki topics", exact=True)
    per_dir = Counter(
        (n["data"].get("path") or "").split("/")[0]
        for n in _graph()["nodes"]
        if n["data"].get("path")
    )
    assert per_dir, "the graph should have pages"
    for name, count in per_dir.items():
        expect(dirs.get_by_role("button", name=f"{name} {count}", exact=True)).to_be_visible()
    expect(dirs.get_by_role("button", name=re.compile(r"^Brief me on"))).to_have_count(len(per_dir))
    expect(filters.get_by_text("private", exact=True)).to_have_count(0)


def test_atlas_zooms_in_and_back(page: Page) -> None:
    """Sector, page, reload, Esc: every level is a link and the way back is one key a level."""
    _open_graph(page)
    cap = _default_cap()
    sector, (label, size) = max(_domain_sectors().items(), key=lambda kv: kv[1][1])
    assert size > 2 * cap, "the largest sector should exceed twice the cap this test checks"

    page.locator(".atlas-label", has_text=label).first.click()
    expect(page).to_have_url(f"{UI_URL}/#/map/domain/{sector}", timeout=5_000)
    page.wait_for_selector(".react-flow__node", timeout=20_000)
    expect(page.locator(".map-count")).to_have_text(f"showing {cap} of {size}")
    expect(page.get_by_role("button", name=f"Show {cap * 2}")).to_be_visible()

    # A page is a level of its own, with its neighbourhood and its detail panel.
    # The event, not a pointer double-click: the first click opens the detail panel, which can
    # land over the card before the second one.
    page.locator(".react-flow__node-wikiNode").first.dispatch_event("dblclick")
    expect(page).to_have_url(re.compile(rf"#/map/domain/{re.escape(sector)}/.+"), timeout=5_000)
    expect(page.get_by_role("button", name="Close")).to_be_visible(timeout=5_000)
    expect(page.get_by_role("navigation", name="Map level")).to_contain_text("Atlas")
    level = page.url

    page.reload()
    page.wait_for_selector(".react-flow__node", timeout=20_000)
    expect(page).to_have_url(level)
    expect(page.locator(".map-crumb-page")).to_be_visible()

    page.keyboard.press("Escape")
    expect(page).to_have_url(f"{UI_URL}/#/map/domain/{sector}", timeout=5_000)
    expect(page.locator(".map-crumb-page")).to_have_count(0)  # the level has rendered
    page.keyboard.press("Escape")
    expect(page).to_have_url(f"{UI_URL}/#/map/domain", timeout=5_000)
    # The graph payload for ~1,700 pages takes over 20 s on a cold dev server.
    page.wait_for_selector(".atlas-label", timeout=60_000)


def test_atlas_switches_to_wiki_and_search_finds_an_alias(page: Page) -> None:
    _open_graph(page)
    browse = page.get_by_role("group", name="Browse by")
    browse.get_by_role("button", name="Wiki", exact=True).click()
    expect(page).to_have_url(f"{UI_URL}/#/map/wiki", timeout=5_000)
    expect(page.locator(".atlas-label")).to_have_count(len(_wiki_sectors()), timeout=20_000)

    # A link from before the redesign lands on the domain atlas.
    page.goto(f"{UI_URL}/#/map/course")
    expect(browse.get_by_role("button", name="Domain", exact=True)).to_have_attribute(
        "aria-pressed", "true", timeout=5_000
    )
    expect(page.locator(".atlas-label")).to_have_count(len(_domain_sectors()), timeout=20_000)

    terms = _get("/api/glossary")["terms"]
    term = next(t for t in terms if t["aliases"] and t["page"])
    page.get_by_role("combobox", name="Search the map").fill(term["aliases"][0])
    expect(page.get_by_role("option").first).to_contain_text(term["label"])


def test_private_terms_stay_private() -> None:
    """Public mentions only: every page a term lists is in the public graph."""
    public = {n["id"] for n in _get("/api/graph")["nodes"]}
    for pages in _get("/api/glossary/mentions").values():
        assert set(pages) <= public


def test_module_filter_shows_its_pages(page: Page) -> None:
    """The topic page's "Show on the graph" link filters the map to that module's pages."""
    curriculum = _get("/api/graph/curriculum")
    course, module = next(
        (c, m) for c in curriculum["courses"] for m in c["modules"] if m["pageIds"]
    )
    page.goto(f"{UI_URL}/#/courses/{course['id']}/{module['id']}", timeout=15_000)
    page.get_by_role("link", name="Show on the graph").click()
    expect(page).to_have_url(
        re.compile(r"#/map/all\?tags=module(:|%3A)" + re.escape(course["id"]) + r"(/|%2F)"),
        timeout=5_000,
    )
    # React Flow drops off-screen cards, so count the status line, not the DOM.
    pages = page.locator(".map-count")
    expect(pages).to_have_text(
        f"showing {len(module['pageIds'])} of {len(_graph()['nodes'])}", timeout=20_000
    )


def _lesson_with_concepts() -> dict[str, Any]:
    for course in _get("/api/courses"):
        for module in course["modules"]:
            for outline in module["lessons"]:
                # A module's readme opens the module's page, which lists no lesson concepts.
                if outline["id"].endswith("/readme"):
                    continue
                lesson = _get(f"/api/courses/lessons/{outline['id']}")
                if lesson["concepts"]:
                    return lesson
    pytest.skip("no lesson links a wiki concept")


def test_courses_tab_and_concept_jump(page: Page) -> None:
    _open_graph(page)
    page.get_by_role("navigation", name="Sections").get_by_role(
        "link", name="Courses", exact=True
    ).click()
    expect(page).to_have_title("Courses · Librarian")

    lesson = _lesson_with_concepts()
    page.goto(f"{UI_URL}/#/courses/{lesson['id']}")
    expect(page).to_have_title(re.compile(re.escape(lesson["title"]) + r" · .+ · Librarian"))

    concept = lesson["concepts"][0]
    page.get_by_role("button", name=concept["title"]).first.click()
    # Back on the graph with the concept's detail panel open (focusPage applied).
    expect(page).to_have_title("Graph · Librarian")
    expect(page.get_by_role("button", name="Close")).to_be_visible(timeout=15_000)


def test_sidebar_lists_modules_and_the_topic_page_has_a_wiki_graph_link(page: Page) -> None:
    course = next((c for c in _get("/api/courses") if c["modules"]), None)
    if course is None:
        pytest.skip("no course with modules")
    module = course["modules"][0]
    _open_graph(page)
    nav = page.get_by_role("navigation", name="Sections")
    # Modules sit under their course's label with a lesson count; no lessons are listed.
    row = nav.get_by_role("link", name=re.compile("^" + re.escape(module["title"])))
    expect(row.first).to_be_visible()
    row.first.click()
    expect(page).to_have_title(re.compile(re.escape(module["title"]) + r" · .+ · Librarian"))
    expect(row.first).to_have_class(re.compile("is-current"))
    expect(page.get_by_role("heading", name="Test yourself", level=2)).to_be_visible()
    if module.get("wiki"):
        link = page.get_by_role("link", name="Show on the graph")
        expect(link).to_have_attribute("href", re.compile(r"^#/map/all\?tags=module%3A"))


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
    """Narrow layout: chat overlay + navigation drawer open; one Escape closes only the drawer."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        pg = browser.new_page(viewport={"width": 1000, "height": 800})
        outline = _get("/api/courses")[0]["modules"][0]["lessons"][0]
        pg.goto(f"{UI_URL}/#/courses/{outline['id']}", timeout=15_000)
        drawer_btn = pg.get_by_role("button", name="Menu", exact=True)
        expect(drawer_btn).to_be_visible(timeout=15_000)
        pg.get_by_role("button", name="Agent Chat ↗").click()
        drawer_btn.click()
        expect(pg.locator(".app-sidenav.is-open")).to_have_count(1)

        pg.keyboard.press("Escape")
        expect(pg.locator(".app-sidenav.is-open")).to_have_count(0)
        expect(pg.locator("#chat-panel")).to_have_count(1)
        expect(drawer_btn).to_be_focused()
        pg.keyboard.press("Escape")
        expect(pg.locator("#chat-panel")).to_have_count(0)
        browser.close()


@pytest.mark.parametrize(
    ("route", "ready"),
    [
        ("/", ".atlas-label"),
        ("/#/map/wiki/rag", ".react-flow__node"),
        ("/#/courses", ".course-card"),
        ("lesson", ".lesson-prose p"),
        ("/#/practice", "[aria-label='Drill timer']"),
    ],
)
def test_no_serious_axe_violations(page: Page, route: str, ready: str) -> None:
    """axe-core per view: no serious/critical WCAG violations (contrast, landmarks,
    nested interactive controls, links told apart by colour alone)."""
    if not AXE_JS.exists():
        pytest.skip("axe-core not installed (npm install in app)")
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
