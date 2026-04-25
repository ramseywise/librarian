"""Scrape web bookmarks → raw/web/

Reads URLs from:
  - raw/web/bookmarks.txt: one URL per line (# comments and blank lines ignored)
  - --url:                  single URL passed directly on the command line

Writes one markdown file per URL to raw/web/ (or --output-dir).
Idempotent: skips URLs already captured (matched by url_hash in existing frontmatter).

Usage:
    uv run python scripts/scrape_bookmarks.py
    uv run python scripts/scrape_bookmarks.py --url https://example.com/article
    uv run python scripts/scrape_bookmarks.py --bookmarks-file raw/web/bookmarks.txt
    uv run python scripts/scrape_bookmarks.py --dry-run
"""

from __future__ import annotations

import argparse
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import httpx
import structlog
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
log = structlog.get_logger()

DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent / "raw" / "web"
DEFAULT_BOOKMARKS_FILE = Path(__file__).parent.parent / "raw" / "web" / "bookmarks.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; librarian-kb/1.0)"
}


def _url_slug(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.netloc + parsed.path
    return re.sub(r"[^a-z0-9]+", "-", path.lower()).strip("-")[:60]


def _url_hash(url: str) -> str:
    return hashlib.sha1(url.encode()).hexdigest()[:8]


def _already_captured(url: str, output_dir: Path) -> bool:
    url_id = _url_hash(url)
    for md_file in output_dir.glob("*.md"):
        try:
            if f"url_hash: {url_id}" in md_file.read_text(encoding="utf-8", errors="ignore"):
                return True
        except OSError:
            continue
    return False


def _extract_content(html: str) -> tuple[str, str]:
    """Return (title, cleaned_body_markdown) from raw HTML."""
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header", "aside",
                     "form", "iframe", "noscript", "svg", "button"]):
        tag.decompose()

    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    elif soup.find("h1"):
        title = soup.find("h1").get_text(strip=True)

    main = (
        soup.find("main")
        or soup.find("article")
        or soup.find(id=re.compile(r"content|main|article|post", re.I))
        or soup.find(class_=re.compile(r"content|main|article|post|body", re.I))
        or soup.body
        or soup
    )

    paragraphs: list[str] = []
    for elem in main.find_all(["p", "h1", "h2", "h3", "h4", "li", "pre", "blockquote"]):
        text = elem.get_text(separator=" ", strip=True)
        if len(text) < 20:
            continue
        if elem.name in ("h1", "h2", "h3", "h4"):
            paragraphs.append(f"\n## {text}\n")
        elif elem.name == "pre":
            paragraphs.append(f"\n```\n{text}\n```\n")
        elif elem.name == "blockquote":
            paragraphs.append(f"> {text}")
        else:
            paragraphs.append(text)

    body = re.sub(r"\n{3,}", "\n\n", "\n\n".join(paragraphs))
    return title, body.strip()


def scrape_url(url: str, output_dir: Path, dry_run: bool = False) -> bool:
    """Fetch one URL and write a markdown capture. Returns True if written."""
    if _already_captured(url, output_dir):
        log.debug("already_captured", url=url)
        return False

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    try:
        with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=20) as client:
            resp = client.get(url)
            resp.raise_for_status()
    except httpx.HTTPError as exc:
        log.warning("fetch_failed", url=url, error=str(exc))
        return False

    if "html" not in resp.headers.get("content-type", ""):
        log.warning("not_html", url=url, content_type=resp.headers.get("content-type"))
        return False

    title, body = _extract_content(resp.text)
    if not title:
        title = urlparse(url).netloc

    slug = _url_slug(url)
    url_id = _url_hash(url)
    domain = urlparse(url).netloc.replace("www.", "")
    out_name = f"{today}-{slug}-{url_id}.md"
    out_path = output_dir / out_name

    content = f"""---
title: {title}
url: {url}
url_hash: {url_id}
domain: {domain}
date: {today}
tags: [web, reference]
summary: Captured from {domain} on {today}
sources:
  - raw/web/{out_name}
---

# {title}

> Source: {url}

{body}
"""

    if dry_run:
        print(f"[web] would write: {out_name} ({len(body):,} chars — {title[:60]})")
    else:
        out_path.write_text(content, encoding="utf-8")
        log.info("wrote_capture", file=out_name, title=title[:60], chars=len(body))

    return True


def load_bookmarks(bookmarks_file: Path) -> list[str]:
    """Read URLs from a text file, one per line. Skips blank lines and # comments."""
    if not bookmarks_file.exists():
        return []
    return [
        line.strip()
        for line in bookmarks_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#") and line.startswith("http")
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape web bookmarks → raw/web/")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--bookmarks-file", type=Path, default=DEFAULT_BOOKMARKS_FILE)
    parser.add_argument(
        "--url", action="append", dest="urls", default=[],
        metavar="URL", help="Single URL to capture (repeatable)"
    )
    parser.add_argument("--dry-run", action="store_true", help="Print what would be written, don't write")
    args = parser.parse_args()

    if not args.dry_run:
        args.output_dir.mkdir(parents=True, exist_ok=True)

    urls = args.urls or load_bookmarks(args.bookmarks_file)

    if not urls:
        print(f"No URLs to scrape. Add URLs to {args.bookmarks_file} or pass --url <url>.")
        return

    written = sum(scrape_url(u, args.output_dir, dry_run=args.dry_run) for u in urls)
    print(f"\n{'[dry-run] ' if args.dry_run else ''}Captured {written}/{len(urls)} URLs → {args.output_dir}")


if __name__ == "__main__":
    main()
