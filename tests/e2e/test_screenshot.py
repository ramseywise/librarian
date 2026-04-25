from __future__ import annotations

from pathlib import Path

import pytest
from playwright.sync_api import Page, sync_playwright

SCREENSHOT_DIR = Path(__file__).parent.parent / "screenshots"
UI_URL = "http://localhost:5173"


@pytest.mark.e2e
def test_graph_loads_and_screenshot(tmp_path: Path) -> None:
    """Graph must connect and render nodes; saves screenshot to tests/screenshots/."""
    SCREENSHOT_DIR.mkdir(exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1400, "height": 800})
        page.goto(UI_URL, timeout=15_000)

        # Wait for WebSocket to connect
        page.wait_for_selector("text=● live", timeout=20_000)

        # Wait for at least one graph node to appear
        page.wait_for_selector(".react-flow__node", timeout=15_000)

        page.screenshot(path=str(SCREENSHOT_DIR / "graph.png"), full_page=False)
        browser.close()

    assert (SCREENSHOT_DIR / "graph.png").exists()
