"""Screenshot a running Streamlit app for dev debugging.

One-time setup:
    uv run playwright install chromium

Usage:
    uv run python scripts/screenshot.py                                    # localhost:8501
    uv run python scripts/screenshot.py --url http://localhost:8501 --out scripts/screenshot.png
    uv run python scripts/screenshot.py --tab pages                        # click a tab first
"""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

TAB_LABELS = {"graph": "Graph", "pages": "Pages", "coverage": "Coverage gaps"}


async def _capture(url: str, output: Path, tab: str | None, wait: float) -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1400, "height": 900})
        await page.goto(url, wait_until="networkidle")
        await asyncio.sleep(wait)

        if tab and tab in TAB_LABELS:
            label = TAB_LABELS[tab]
            btn = page.get_by_role("tab", name=label)
            if await btn.count():
                await btn.click()
                await asyncio.sleep(1.5)

        output.parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(output), full_page=False)
        await browser.close()

    print(f"Saved: {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Screenshot a running Streamlit app")
    parser.add_argument("--url", default="http://localhost:8501", help="Streamlit URL")
    parser.add_argument("--out", default="scripts/screenshot.png", help="Output path")
    parser.add_argument("--tab", choices=list(TAB_LABELS), default=None, help="Click a tab before capturing")
    parser.add_argument("--wait", type=float, default=3.0, help="Seconds to wait after page load")
    args = parser.parse_args()
    asyncio.run(_capture(args.url, Path(args.out), args.tab, args.wait))


if __name__ == "__main__":
    main()
