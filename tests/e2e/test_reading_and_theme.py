"""Browser checks for the search key, both themes, reading type, definitions, health and study.

Needs the same servers as test_ui_smoke.py. Grades are intercepted, so nothing here writes to
logs/flashcards.jsonl; never sends a chat message.
"""

from __future__ import annotations

import json
import os
import re
import urllib.request
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from playwright.sync_api import Browser, Page, expect, sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

UI_URL = os.environ.get("E2E_UI_URL", "http://localhost:5173")
API = os.environ.get("E2E_API_URL", "http://localhost:8000")
AXE_JS = Path(__file__).parents[2] / "app/frontend/node_modules/axe-core/axe.min.js"
THEME_KEY = "librarian.theme"

pytestmark = pytest.mark.e2e


def _get(path: str) -> Any:  # noqa: ANN401 — JSON
    with urllib.request.urlopen(API + path, timeout=30) as r:
        return json.load(r)


@pytest.fixture()
def browser() -> Iterator[Browser]:
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


@pytest.fixture()
def page(browser: Browser) -> Iterator[Page]:
    pg = browser.new_page(viewport={"width": 1400, "height": 900}, color_scheme="dark")
    errors: list[str] = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    yield pg
    assert not errors, f"uncaught page errors: {errors}"


@pytest.fixture()
def light_page(browser: Browser) -> Page:
    return browser.new_page(viewport={"width": 1400, "height": 900}, color_scheme="light")


def _lessons() -> Iterator[str]:
    for course in _get("/api/courses"):
        for module in course["modules"]:
            for lesson in module["lessons"]:
                yield lesson["id"]


def _open_lesson_with_a_term(page: Page) -> None:
    """A failure, not a skip: with this glossary, no term in 40 lessons means marking is broken."""
    for lesson in list(_lessons())[:40]:
        page.goto(f"{UI_URL}/#/courses/{lesson}", timeout=15_000)
        page.wait_for_selector(".lesson-main-body p", timeout=20_000)
        try:
            # The glossary arrives after the text.
            page.wait_for_selector(".gloss-term", timeout=3_000)
        except PlaywrightTimeoutError:
            continue
        return
    pytest.fail("no glossary term in the first 40 lessons")


def _scheduled_deck() -> str:
    modules = _get("/api/courses/flashcards-due")["modules"]
    if not modules:
        pytest.skip("no module with cards to study")
    return modules[0]["deck"]


def test_slash_focuses_the_view_search(page: Page) -> None:
    page.goto(UI_URL, timeout=15_000)
    page.wait_for_selector(".atlas-label", timeout=20_000)
    search = page.locator("[data-view-search]:visible").first
    page.keyboard.press("/")
    expect(search).to_be_focused()
    expect(search).to_have_value("")
    # Now in a field, so the key types.
    page.keyboard.press("/")
    expect(search).to_have_value("/")


def test_slash_focuses_the_visible_search_not_the_map_underneath(page: Page) -> None:
    page.goto(f"{UI_URL}/#/courses", timeout=15_000)
    page.wait_for_selector(".course-card", timeout=20_000)
    page.keyboard.press("/")
    expect(page.locator("[data-view-search]:focus")).to_be_visible()


def test_theme_defaults_from_the_system_and_the_toggle_persists(light_page: Page) -> None:
    page = light_page
    page.goto(UI_URL, timeout=15_000)
    root = page.locator("html")
    expect(root).to_have_attribute("data-theme", "light")
    assert page.evaluate(f"localStorage.getItem('{THEME_KEY}')") is None
    light_bg = page.evaluate("getComputedStyle(document.body).backgroundColor")

    page.get_by_role("button", name="Switch to dark theme").click()
    expect(root).to_have_attribute("data-theme", "dark")
    assert page.evaluate("getComputedStyle(document.body).backgroundColor") != light_bg
    assert page.evaluate(f"localStorage.getItem('{THEME_KEY}')") == "dark"

    page.reload()
    expect(root).to_have_attribute("data-theme", "dark")
    expect(page.get_by_role("button", name="Switch to light theme")).to_be_visible()


def test_lesson_text_is_serif_at_a_reading_measure_and_chrome_is_not(page: Page) -> None:
    lesson = next(_lessons())
    page.goto(f"{UI_URL}/#/courses/{lesson}", timeout=15_000)
    para = page.locator(".lesson-prose p").first
    expect(para).to_be_visible(timeout=20_000)
    style = para.evaluate(
        """el => {
          const prose = el.closest('.lesson-prose');
          const probe = document.createElement('span');
          probe.textContent = '0'.repeat(68);
          probe.style.cssText = 'position:absolute;visibility:hidden;white-space:nowrap';
          prose.appendChild(probe);
          const measure = probe.getBoundingClientRect().width;
          probe.remove();
          return {
            font: getComputedStyle(el).fontFamily,
            width: prose.getBoundingClientRect().width,
            measure,
          };
        }"""
    )
    assert style["font"].endswith("serif") and "sans-serif" not in style["font"]
    assert style["width"] <= style["measure"] + 1
    chrome = page.locator("header").first.evaluate("el => getComputedStyle(el).fontFamily")
    assert "Charter" not in chrome


def test_hover_and_keyboard_definition(page: Page) -> None:
    _open_lesson_with_a_term(page)
    assert not page.locator(
        ".lesson-prose :is(h1, h2, h3, h4, h5, h6, pre, code, a) .gloss-term, .gloss-term .gloss-term"
    ).count()

    term = page.locator(".gloss-term").first
    pop = term.get_by_role("tooltip", include_hidden=True)
    expect(pop).to_be_hidden()
    term.hover()
    expect(pop).to_be_visible()
    box = pop.bounding_box()
    assert box and box["x"] >= 0 and box["x"] + box["width"] <= 1400
    page.mouse.move(0, 0)
    expect(pop).to_be_hidden()

    term.focus()
    expect(pop).to_be_visible()
    page.keyboard.press("Escape")
    expect(pop).to_be_hidden()


def test_health_strip_shows_the_files_statuses_and_no_page_count(page: Page) -> None:
    latest = _get("/api/wiki/health")
    page.goto(UI_URL, timeout=15_000)
    strip = page.get_by_role("region", name="Wiki health")
    expect(strip).to_be_visible(timeout=20_000)
    text = strip.inner_text()
    if not latest["metrics"]:
        assert "No wiki health snapshot" in text
        return
    for metric in latest["metrics"].values():
        assert metric["status"] in text
    assert "pages" not in text.lower()
    if "pages" in latest:
        assert not re.search(rf"\b{latest['pages']}\b", text)


def test_due_filter_studies_and_grades_without_logging(page: Page) -> None:
    deck = _scheduled_deck()
    page.route("**/api/courses/flashcard-results", lambda r: r.fulfill(status=204))
    before = _get(f"/api/courses/flashcards/{deck}")
    waiting = before["dueCount"] + before["newCount"]
    page.goto(f"{UI_URL}/#/flashcards/{deck}?due", timeout=15_000)
    filter_btn = page.get_by_role("button", name=re.compile("^Due today"))
    expect(filter_btn).to_have_attribute("aria-pressed", "true", timeout=20_000)
    expect(page.get_by_text(re.compile(rf"\b1 of {waiting}$"))).to_be_visible()

    page.get_by_role("button", name=re.compile("click to flip")).click()
    page.get_by_role("button", name="Knew it").click()
    if waiting > 1:
        expect(page.get_by_text(re.compile(rf"\b1 of {waiting - 1}$"))).to_be_visible()

    page.get_by_role("button", name=f"All {len(before['cards'])}").click()
    expect(page.get_by_role("button", name=f"All {len(before['cards'])}")).to_have_attribute(
        "aria-pressed", "true"
    )


@pytest.mark.parametrize("route", ["/", "/#/map/domain/rag"])
def test_health_strip_clears_the_controls_around_it(page: Page, route: str) -> None:
    page.goto(UI_URL + route, timeout=15_000)
    strip = page.get_by_role("region", name="Wiki health")
    expect(strip).to_be_visible(timeout=20_000)
    page.wait_for_selector(".atlas-label, .react-flow__node", timeout=20_000)
    box = strip.bounding_box()
    assert box
    others = page.locator(".graph-filter-panel, .graph-minimap, .react-flow__controls")
    for other in others.all():
        o = other.bounding_box()
        if not o:
            continue
        clear = (
            box["x"] + box["width"] <= o["x"]
            or o["x"] + o["width"] <= box["x"]
            or box["y"] + box["height"] <= o["y"]
            or o["y"] + o["height"] <= box["y"]
        )
        assert clear, f"{box} overlaps {o}"
    list_button = page.get_by_role("button", name="Browse as a list")
    if list_button.count():
        o = list_button.bounding_box()
        assert o and box["x"] + box["width"] <= o["x"]


def test_due_filter_is_readable_in_dark(page: Page) -> None:
    if not AXE_JS.exists():
        pytest.skip("axe-core not installed (npm install in app/frontend)")
    page.goto(f"{UI_URL}/#/flashcards/{_scheduled_deck()}", timeout=15_000)
    page.wait_for_selector(".flashcard-filter", timeout=20_000)
    page.add_script_tag(path=str(AXE_JS))
    result = page.evaluate("axe.run(document, {resultTypes: ['violations']})")
    bad = [v["id"] for v in result["violations"] if v["impact"] in ("serious", "critical")]
    assert not bad, bad


@pytest.mark.parametrize(
    ("route", "ready"),
    [
        ("/", ".atlas-label"),
        ("/#/map/domain/rag", ".react-flow__node"),
        ("/#/courses", ".course-card"),
        ("lesson", ".lesson-main-body p"),
        ("/#/practice", "[aria-label='Drill timer']"),
        ("deck", ".flashcard-filter"),
    ],
)
def test_light_theme_has_no_serious_axe_violations(
    light_page: Page, route: str, ready: str
) -> None:
    if not AXE_JS.exists():
        pytest.skip("axe-core not installed (npm install in app/frontend)")
    page = light_page
    if route == "lesson":
        route = f"/#/courses/{next(_lessons())}"
    elif route == "deck":
        route = f"/#/flashcards/{_scheduled_deck()}"
    page.goto(UI_URL + route, timeout=15_000)
    page.wait_for_selector(ready, timeout=20_000)
    expect(page.locator("html")).to_have_attribute("data-theme", "light")
    page.add_script_tag(path=str(AXE_JS))
    result = page.evaluate("axe.run(document, {resultTypes: ['violations']})")
    bad = [
        (v["id"], v["impact"], [n["target"] for n in v["nodes"][:3]])
        for v in result["violations"]
        if v["impact"] in ("serious", "critical")
    ]
    assert not bad, bad
