"""Fetch recent arXiv papers → raw/web/

Queries the arXiv API for papers published in the last N days across specified
categories. Applies a keyword filter to prevent cs.LG volume from flooding raw/.
Deduplicates by arXiv ID against raw/manifest.jsonl before writing.

Usage:
    uv run python -m core.scrape_arxiv
    uv run python -m core.scrape_arxiv --dry-run
    uv run python -m core.scrape_arxiv --categories cs.CL cs.AI --since-days 3
"""

from __future__ import annotations

import argparse
import re
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx
import structlog

from core.base import REPO_ROOT, ScraperBase

log = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ARXIV_API_URL = "https://export.arxiv.org/api/query"

DEFAULT_CATEGORIES: list[str] = ["cs.LG", "cs.AI", "cs.CL", "stat.ML"]

DEFAULT_KEYWORDS: list[str] = [
    "LLM",
    "language model",
    "reinforcement learning",
    "alignment",
    "RAG",
    "agentic",
    "RLHF",
    "DPO",
    "GRPO",
    "reward model",
    "fine-tuning",
    "instruction tuning",
]

# arXiv recommends at most 1 request per 3 seconds for automated access
RATE_LIMIT_SLEEP = 3.0

DEFAULT_OUTPUT_DIR = REPO_ROOT / "raw" / "web"
DEFAULT_SINCE_DAYS = 7
MAX_RESULTS_PER_CATEGORY = 100  # conservative ceiling per category request

# Namespace used in arXiv Atom feeds
_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class Paper:
    arxiv_id: str
    title: str
    abstract: str
    authors: list[str] = field(default_factory=list)
    published: str = ""  # ISO date string YYYY-MM-DD
    categories: list[str] = field(default_factory=list)
    url: str = ""


# ---------------------------------------------------------------------------
# arXiv ID dedup helper
# ---------------------------------------------------------------------------


def _load_arxiv_ids_from_manifest() -> set[str]:
    """Read raw/manifest.jsonl and extract any arxiv_id fields.

    Also scans raw/web/ filenames for the arxiv-<id>- pattern as a secondary
    check — catches papers written before the manifest entry was recorded.
    """
    seen: set[str] = set()

    manifest_path = REPO_ROOT / "raw" / "manifest.jsonl"
    if manifest_path.exists():
        for line in manifest_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                import json

                entry = json.loads(line)
                arxiv_id = entry.get("arxiv_id")
                if arxiv_id:
                    seen.add(arxiv_id)
            except Exception:
                pass

    # Fallback: scan filenames in raw/web/ for the naming pattern
    web_dir = REPO_ROOT / "raw" / "web"
    if web_dir.exists():
        for f in web_dir.glob("*-arxiv-*-*.md"):
            # Pattern: YYYY-MM-DD-arxiv-<id>-<slug>.md
            m = re.search(r"-arxiv-([0-9]{4}\.[0-9]+(?:v\d+)?)-", f.name)
            if m:
                seen.add(
                    m.group(1).rstrip("v0123456789").rstrip(".")
                    if "v" in m.group(1)
                    else m.group(1)
                )

    return seen


# ---------------------------------------------------------------------------
# API fetch
# ---------------------------------------------------------------------------


def _build_query(category: str, since_days: int) -> str:
    """Build an arXiv API search query string for a single category + date window."""
    cutoff = (datetime.now(tz=UTC) - timedelta(days=since_days)).strftime("%Y%m%d")
    today = datetime.now(tz=UTC).strftime("%Y%m%d")
    return f"cat:{category} AND submittedDate:[{cutoff}0000 TO {today}2359]"


def _parse_feed(xml_text: str) -> list[Paper]:
    """Parse arXiv Atom feed XML into Paper objects."""
    papers: list[Paper] = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        log.warning("arxiv.parse_error", error=str(exc))
        return papers

    for entry in root.findall("atom:entry", _NS):
        # arXiv ID lives in the <id> tag as a URL: https://arxiv.org/abs/2501.12948v1
        id_elem = entry.find("atom:id", _NS)
        if id_elem is None or id_elem.text is None:
            continue
        raw_id = id_elem.text.strip()
        # Extract just the numeric portion (strip URL prefix and version suffix)
        arxiv_id_match = re.search(r"abs/([0-9]{4}\.[0-9]+)", raw_id)
        if not arxiv_id_match:
            continue
        arxiv_id = arxiv_id_match.group(1)

        title_elem = entry.find("atom:title", _NS)
        title = (title_elem.text or "").strip().replace("\n", " ") if title_elem is not None else ""

        abstract_elem = entry.find("atom:summary", _NS)
        abstract = (
            (abstract_elem.text or "").strip().replace("\n", " ")
            if abstract_elem is not None
            else ""
        )

        authors = [
            (a.find("atom:name", _NS).text or "").strip()
            for a in entry.findall("atom:author", _NS)
            if a.find("atom:name", _NS) is not None
        ]

        published_elem = entry.find("atom:published", _NS)
        published_raw = (published_elem.text or "").strip() if published_elem is not None else ""
        published = published_raw[:10] if published_raw else ""

        cats = [t.get("term", "") for t in entry.findall("atom:category", _NS) if t.get("term")]
        # Also check arxiv:primary_category
        primary = entry.find("arxiv:primary_category", _NS)
        if primary is not None:
            primary_cat = primary.get("term", "")
            if primary_cat and primary_cat not in cats:
                cats.insert(0, primary_cat)

        papers.append(
            Paper(
                arxiv_id=arxiv_id,
                title=title,
                abstract=abstract,
                authors=authors,
                published=published,
                categories=cats,
                url=f"https://arxiv.org/abs/{arxiv_id}",
            )
        )

    return papers


def _matches_keywords(paper: Paper, keywords: list[str]) -> bool:
    """Return True if title or abstract contains any keyword (case-insensitive)."""
    haystack = (paper.title + " " + paper.abstract).lower()
    return any(kw.lower() in haystack for kw in keywords)


def fetch_recent(
    categories: list[str] = DEFAULT_CATEGORIES,
    since_days: int = DEFAULT_SINCE_DAYS,
    keywords: list[str] = DEFAULT_KEYWORDS,
    max_results: int = MAX_RESULTS_PER_CATEGORY,
) -> list[Paper]:
    """Fetch recent arXiv papers matching categories + keywords.

    Rate-limited: 3-second sleep between category requests per arXiv guidelines.
    Keyword filter applied post-fetch to limit noise from broad categories.
    Returns deduplicated list (by arXiv ID) across all categories.
    """
    seen_ids: set[str] = set()
    papers: list[Paper] = []

    with httpx.Client(timeout=30, follow_redirects=True) as client:
        for i, category in enumerate(categories):
            if i > 0:
                time.sleep(RATE_LIMIT_SLEEP)

            query = _build_query(category, since_days)
            params = {
                "search_query": query,
                "start": 0,
                "max_results": max_results,
                "sortBy": "submittedDate",
                "sortOrder": "descending",
            }

            log.info("arxiv.fetch_category", category=category, since_days=since_days)
            try:
                resp = client.get(ARXIV_API_URL, params=params)
                resp.raise_for_status()
            except httpx.HTTPError as exc:
                log.warning("arxiv.fetch_error", category=category, error=str(exc))
                continue

            category_papers = _parse_feed(resp.text)
            log.info("arxiv.category_results", category=category, count=len(category_papers))

            for paper in category_papers:
                if paper.arxiv_id in seen_ids:
                    continue
                seen_ids.add(paper.arxiv_id)
                if not _matches_keywords(paper, keywords):
                    log.debug(
                        "arxiv.keyword_filtered", arxiv_id=paper.arxiv_id, title=paper.title[:60]
                    )
                    continue
                papers.append(paper)

    log.info("arxiv.fetch_complete", total=len(papers), categories=len(categories))
    return papers


# ---------------------------------------------------------------------------
# File writer
# ---------------------------------------------------------------------------


def _title_slug(title: str) -> str:
    """Convert title to a short filesystem-safe slug."""
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower())
    return slug.strip("-")[:50]


def save_paper(paper: Paper, output_dir: Path, dry_run: bool = False) -> Path | None:
    """Write one paper to a markdown file in output_dir. Returns path written, or None."""
    today = datetime.now(tz=UTC).strftime("%Y-%m-%d")
    slug = _title_slug(paper.title)
    filename = f"{today}-arxiv-{paper.arxiv_id}-{slug}.md"
    out_path = output_dir / filename

    if out_path.exists():
        log.debug("arxiv.file_exists", file=filename)
        return None

    authors_str = ", ".join(paper.authors[:5])
    if len(paper.authors) > 5:
        authors_str += f" +{len(paper.authors) - 5}"

    categories_str = ", ".join(paper.categories)

    content = f"""---
title: "{paper.title.replace('"', "'")}"
arxiv_id: {paper.arxiv_id}
url: {paper.url}
source_type: paper
published: {paper.published}
fetched: {today}
authors: "{authors_str}"
categories: [{categories_str}]
tags: [paper, arxiv, {", ".join(paper.categories[:2])}]
summary: "arXiv {paper.arxiv_id} — {paper.title[:80].replace('"', "'")}"
sources:
  - raw/web/{filename}
---

# {paper.title}

**Authors**: {authors_str}
**Published**: {paper.published}
**arXiv**: [{paper.arxiv_id}]({paper.url})
**Categories**: {categories_str}

## Abstract

{paper.abstract}
"""

    if dry_run:
        print(f"[arxiv] would write: {filename}")
        print(f"  Title: {paper.title[:80]}")
        print(f"  Authors: {authors_str}")
        print(f"  Published: {paper.published}")
        print()
    else:
        output_dir.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
        log.info("arxiv.wrote_paper", file=filename, title=paper.title[:60])

    return out_path


# ---------------------------------------------------------------------------
# Scraper class
# ---------------------------------------------------------------------------


class ArxivScraper(ScraperBase):
    source_name = "scrape-arxiv"
    output_dir = DEFAULT_OUTPUT_DIR

    def __init__(
        self,
        categories: list[str] = DEFAULT_CATEGORIES,
        since_days: int = DEFAULT_SINCE_DAYS,
        keywords: list[str] = DEFAULT_KEYWORDS,
        output_dir: Path = DEFAULT_OUTPUT_DIR,
    ) -> None:
        self._categories = categories
        self._since_days = since_days
        self._keywords = keywords
        self.output_dir = output_dir

    def run(self, dry_run: bool = False) -> list[Path]:
        """Fetch papers, dedup, and write to output_dir. Returns paths written."""
        existing_ids = _load_arxiv_ids_from_manifest()
        log.info("arxiv.manifest_loaded", known_ids=len(existing_ids))

        papers = fetch_recent(
            categories=self._categories,
            since_days=self._since_days,
            keywords=self._keywords,
        )

        written: list[Path] = []
        skipped = 0
        for paper in papers:
            if paper.arxiv_id in existing_ids:
                log.debug("arxiv.dedup_skip", arxiv_id=paper.arxiv_id)
                skipped += 1
                continue
            path = save_paper(paper, self.output_dir, dry_run=dry_run)
            if path is not None:
                written.append(path)

        prefix = "[dry-run] " if dry_run else ""
        print(
            f"\n{prefix}arxiv: fetched {len(papers)}, wrote {len(written)}, "
            f"skipped {skipped} (already in manifest)"
        )
        return written

    @classmethod
    def _add_args(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--categories",
            nargs="+",
            default=DEFAULT_CATEGORIES,
            metavar="CAT",
            help=f"arXiv categories to query (default: {' '.join(DEFAULT_CATEGORIES)})",
        )
        parser.add_argument(
            "--since-days",
            type=int,
            default=DEFAULT_SINCE_DAYS,
            metavar="N",
            help=f"Fetch papers from last N days (default: {DEFAULT_SINCE_DAYS})",
        )
        parser.add_argument(
            "--output-dir",
            type=Path,
            default=DEFAULT_OUTPUT_DIR,
            help="Output directory (default: raw/web/)",
        )

    @classmethod
    def _from_args(cls, args: argparse.Namespace) -> ArxivScraper:
        return cls(
            categories=args.categories,
            since_days=args.since_days,
            output_dir=args.output_dir,
        )


if __name__ == "__main__":
    ArxivScraper.cli(description="Fetch recent arXiv papers → raw/web/")
