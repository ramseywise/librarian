"""Pull Notion pages → raw/notion/

Fetches a Notion page (and optionally its children) via the Notion API
and saves as markdown to raw/notion/YYYY-MM-DD-<title>.md.

Usage:
    uv run python scripts/ingest_notion.py <page-id-or-url>
    uv run python scripts/ingest_notion.py <page-id> --children   # include sub-pages
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

import httpx
import structlog
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()
log = structlog.get_logger()

RAW_NOTION = Path("raw/notion")


class Settings(BaseSettings):
    notion_api_key: str


def page_id_from_arg(arg: str) -> str:
    """Accept a full Notion URL or bare page ID."""
    # URL pattern: notion.so/Workspace/Title-<id>
    match = re.search(r"([a-f0-9]{32})", arg.replace("-", ""))
    if match:
        raw = match.group(1)
        return f"{raw[:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}-{raw[20:]}"
    return arg


def blocks_to_markdown(blocks: list[dict]) -> str:
    """Convert Notion block objects to markdown (basic subset)."""
    lines = []
    for block in blocks:
        btype = block.get("type", "")
        content = block.get(btype, {})
        rich = content.get("rich_text", [])
        text = "".join(r.get("plain_text", "") for r in rich)

        if btype == "heading_1":
            lines.append(f"# {text}")
        elif btype == "heading_2":
            lines.append(f"## {text}")
        elif btype == "heading_3":
            lines.append(f"### {text}")
        elif btype in ("paragraph", "quote"):
            lines.append(text or "")
        elif btype == "bulleted_list_item":
            lines.append(f"- {text}")
        elif btype == "numbered_list_item":
            lines.append(f"1. {text}")
        elif btype == "code":
            lang = content.get("language", "")
            lines.append(f"```{lang}\n{text}\n```")
        elif btype == "divider":
            lines.append("---")
        elif btype == "callout":
            lines.append(f"> {text}")

    return "\n\n".join(line for line in lines if line is not None)


def fetch_page(page_id: str, api_key: str) -> tuple[str, str]:
    """Fetch page metadata and block content. Returns (title, markdown)."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": "2022-06-28",
    }

    with httpx.Client(headers=headers) as client:
        # Page metadata
        meta = client.get(f"https://api.notion.com/v1/pages/{page_id}").json()
        props = meta.get("properties", {})
        title_prop = props.get("title", props.get("Name", {}))
        rich = title_prop.get("title", [])
        title = "".join(r.get("plain_text", "") for r in rich) or page_id

        # Blocks (paginate)
        blocks: list[dict] = []
        cursor = None
        while True:
            params: dict = {"page_size": 100}
            if cursor:
                params["start_cursor"] = cursor
            resp = client.get(
                f"https://api.notion.com/v1/blocks/{page_id}/children",
                params=params,
            ).json()
            blocks.extend(resp.get("results", []))
            if not resp.get("has_more"):
                break
            cursor = resp.get("next_cursor")

    return title, blocks_to_markdown(blocks)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: uv run python scripts/ingest_notion.py <page-id-or-url>")
        sys.exit(1)

    settings = Settings()
    page_id = page_id_from_arg(sys.argv[1])

    log.info("fetching_notion_page", page_id=page_id)
    title, markdown = fetch_page(page_id, settings.notion_api_key)

    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    today = date.today().isoformat()
    out_path = RAW_NOTION / f"{today}-{slug}.md"
    RAW_NOTION.mkdir(parents=True, exist_ok=True)

    out_path.write_text(
        f"# {title}\n\n**Source:** Notion page `{page_id}`\n**Fetched:** {today}\n\n---\n\n{markdown}",
        encoding="utf-8",
    )

    log.info("saved_notion_page", title=title, dest=str(out_path))
    print(f"Saved: {out_path}")
    print(f"Run /ingest {out_path} in Claude Code to compile into wiki.")


if __name__ == "__main__":
    main()
