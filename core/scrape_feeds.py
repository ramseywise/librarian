"""Fetch recent RSS/Atom feed posts → raw/web/

Polls the recurring blog/newsletter sources tracked in learn-ai-engineering's
SOURCES.md (Tier 1 + Tier 2) and drops new posts into the same raw/web/ queue that
/learn already processes for arXiv papers.

Mirrors core/scrape_arxiv.py: fetch → parse → keyword filter → dedup → write.
Both RSS 2.0 and Atom are handled by the same stdlib ElementTree parser — no
feedparser dependency.

Usage:
    uv run python -m core.scrape_feeds
    uv run python -m core.scrape_feeds --dry-run
    uv run python -m core.scrape_feeds --feeds anthropic langchain --since-days 3
    uv run python -m core.scrape_feeds --list-feeds
"""

from __future__ import annotations

import argparse
import json
import re
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path

import httpx
import structlog
from bs4 import BeautifulSoup

from core.base import REPO_ROOT, ScraperBase

log = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FeedSource:
    """One recurring source from SOURCES.md."""

    key: str  # short slug, used in filenames and --feeds
    name: str  # human-readable, used in frontmatter
    url: str  # feed URL (RSS or Atom)
    tier: int  # 1 = primary (cite directly), 2 = aggregator (gap-detector)
    scope: str  # which pillars it feeds, per SOURCES.md
    # False = source publishes no discoverable feed. Kept in the table (rather than
    # dropped) so the gap stays visible and re-checkable; skipped unless named
    # explicitly via --feeds.
    enabled: bool = True
    note: str = ""


# Seeded from ~/workspace/learn-ai-engineering/ai-engineering/SOURCES.md.
# arXiv is deliberately absent — core/scrape_arxiv.py owns it. dair.ai is absent
# too: SOURCES.md records it as a hand-refreshed vendored snapshot, not a feed.
#
# Feed URLs verified 2026-07-31. Anthropic Engineering and AI Builder Club are
# JS-rendered with no RSS/Atom endpoint and no <link rel="alternate"> autodiscovery
# tag — every candidate path 404s. They stay hand-swept until they ship a feed.
DEFAULT_FEEDS: list[FeedSource] = [
    FeedSource(
        key="langchain",
        name="LangChain Blog",
        url="https://blog.langchain.com/rss.xml",
        tier=1,
        scope="loop, graph, harness",
    ),
    FeedSource(
        key="addyosmani",
        name="Addy Osmani",
        url="https://addyosmani.com/rss.xml",
        tier=1,
        scope="loop, harness",
    ),
    FeedSource(
        key="anthropic",
        name="Anthropic Engineering",
        url="https://www.anthropic.com/engineering",
        tier=1,
        scope="harness, context, eval",
        enabled=False,
        note="No RSS/Atom endpoint as of 2026-07-31 — hand-swept.",
    ),
    FeedSource(
        key="aibuilderclub",
        name="AI Builder Club",
        url="https://www.aibuilderclub.com/blog",
        tier=2,
        scope="all six pillars",
        enabled=False,
        note="No RSS/Atom endpoint as of 2026-07-31 — hand-swept.",
    ),
]

# Tier 2 synthesises Tier 1, so it earns a keyword gate that Tier 1 does not:
# SOURCES.md treats aggregators as gap-detectors, not citations of record.
DEFAULT_KEYWORDS: list[str] = [
    "agent",
    "agentic",
    "LLM",
    "language model",
    "context",
    "prompt",
    "harness",
    "eval",
    "RAG",
    "retrieval",
    "graph",
    "tool use",
    "MCP",
    "fine-tuning",
    "reinforcement learning",
]

# Courtesy delay between feed requests — these are small blogs, not an API.
RATE_LIMIT_SLEEP = 1.0

DEFAULT_OUTPUT_DIR = REPO_ROOT / "data" / "raw" / "web"
DEFAULT_SINCE_DAYS = 7
MAX_ENTRIES_PER_FEED = 50

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; librarian-kb/1.0)"}

_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc": "http://purl.org/dc/elements/1.1/",
}

# Summaries are feed-length, not article-length: /learn ranks on them, it does not
# read them. Full capture is scrape_bookmarks.py's job.
MAX_SUMMARY_CHARS = 1500


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class Post:
    feed_key: str
    feed_name: str
    tier: int
    title: str
    summary: str
    url: str
    published: str = ""  # ISO date string YYYY-MM-DD ("" if the feed omits it)
    authors: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Dedup helper
# ---------------------------------------------------------------------------


def _load_feed_urls_from_manifest() -> set[str]:
    """Read raw/manifest.jsonl and extract any feed post URLs.

    Also scans raw/web/ for `url:` lines in existing feed captures — catches posts
    written before a manifest entry was recorded, mirroring the arXiv filename
    fallback in scrape_arxiv._load_arxiv_ids_from_manifest.
    """
    seen: set[str] = set()

    manifest_path = REPO_ROOT / "data" / "raw" / "manifest.jsonl"
    if manifest_path.exists():
        for line in manifest_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            url = entry.get("source_url")
            if url:
                seen.add(_canonical_url(url))

    # Fallback: scan existing feed captures for their url: frontmatter line.
    web_dir = REPO_ROOT / "data" / "raw" / "web"
    if web_dir.exists():
        for f in web_dir.glob("*-feed-*.md"):
            try:
                head = f.read_text(encoding="utf-8", errors="ignore")[:600]
            except OSError:
                continue
            m = re.search(r"^url:\s*(\S+)$", head, re.MULTILINE)
            if m:
                seen.add(_canonical_url(m.group(1)))

    return seen


def _canonical_url(url: str) -> str:
    """Normalise a URL for dedup: strip tracking query, fragment, trailing slash.

    Feeds are inconsistent about utm_* params and trailing slashes across refetches;
    without this the same post reappears as new on every run.
    """
    url = url.strip()
    url = re.sub(r"#.*$", "", url)
    url = re.sub(r"[?&](utm_[^&]*|ref|source)=[^&]*", "", url)
    url = re.sub(r"\?$", "", url)
    return url.rstrip("/")


# ---------------------------------------------------------------------------
# Feed parsing
# ---------------------------------------------------------------------------


def _text(elem: ET.Element | None) -> str:
    """Collapse an element's text to a single clean line."""
    if elem is None or elem.text is None:
        return ""
    return elem.text.strip().replace("\n", " ")


def _strip_html(raw: str) -> str:
    """Feed summaries are usually escaped HTML — reduce to plain text."""
    if not raw:
        return ""
    text = BeautifulSoup(raw, "html.parser").get_text(separator=" ")
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > MAX_SUMMARY_CHARS:
        text = text[:MAX_SUMMARY_CHARS].rsplit(" ", 1)[0] + "…"
    return text


def _parse_date(raw: str) -> str:
    """Parse an RSS (RFC 822) or Atom (ISO 8601) date → YYYY-MM-DD, or ""."""
    raw = raw.strip()
    if not raw:
        return ""
    # Atom: 2026-07-30T12:00:00Z
    m = re.match(r"(\d{4}-\d{2}-\d{2})", raw)
    if m:
        return m.group(1)
    # RSS: Wed, 30 Jul 2026 12:00:00 GMT
    try:
        return parsedate_to_datetime(raw).strftime("%Y-%m-%d")
    except (TypeError, ValueError):
        log.debug("feeds.date_unparsed", raw=raw[:40])
        return ""


def _parse_rss(root: ET.Element, source: FeedSource) -> list[Post]:
    """Parse an RSS 2.0 <channel><item> feed."""
    posts: list[Post] = []
    for item in root.findall(".//item"):
        link = _text(item.find("link"))
        title = _text(item.find("title"))
        if not link or not title:
            continue

        # content:encoded is fuller than <description> when present.
        body = _text(item.find("content:encoded", _NS)) or _text(item.find("description"))

        authors = [a for a in (_text(item.find("dc:creator", _NS)),) if a]
        categories = [c.text.strip() for c in item.findall("category") if c.text]

        posts.append(
            Post(
                feed_key=source.key,
                feed_name=source.name,
                tier=source.tier,
                title=title,
                summary=_strip_html(body),
                url=link,
                published=_parse_date(_text(item.find("pubDate"))),
                authors=authors,
                categories=categories,
            )
        )
    return posts


def _parse_atom(root: ET.Element, source: FeedSource) -> list[Post]:
    """Parse an Atom <feed><entry> feed."""
    posts: list[Post] = []
    for entry in root.findall("atom:entry", _NS):
        title = _text(entry.find("atom:title", _NS))

        # Atom links are attributes; prefer rel="alternate", fall back to first href.
        link = ""
        for link_elem in entry.findall("atom:link", _NS):
            rel = link_elem.get("rel", "alternate")
            if rel == "alternate":
                link = link_elem.get("href", "")
                break
            if not link:
                link = link_elem.get("href", "")
        if not link or not title:
            continue

        content = entry.find("atom:content", _NS)
        summary = entry.find("atom:summary", _NS)
        body = _text(content) or _text(summary)

        authors = [
            _text(a.find("atom:name", _NS))
            for a in entry.findall("atom:author", _NS)
            if _text(a.find("atom:name", _NS))
        ]
        categories = [
            c.get("term", "") for c in entry.findall("atom:category", _NS) if c.get("term")
        ]

        published = _parse_date(
            _text(entry.find("atom:published", _NS)) or _text(entry.find("atom:updated", _NS))
        )

        posts.append(
            Post(
                feed_key=source.key,
                feed_name=source.name,
                tier=source.tier,
                title=title,
                summary=_strip_html(body),
                url=link,
                published=published,
                authors=authors,
                categories=categories,
            )
        )
    return posts


def _looks_like_html(xml_text: str) -> bool:
    """True when the payload is an HTML page rather than a feed document."""
    head = xml_text.lstrip()[:200].lower()
    return head.startswith("<!doctype html") or head.startswith("<html") or "<html" in head


def parse_feed(xml_text: str, source: FeedSource) -> list[Post]:
    """Parse feed XML into Posts, dispatching on RSS vs Atom by root tag."""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        # Real-world HTML rarely parses as XML (unclosed <br>, <img>), so it lands here
        # rather than on the root-tag check below. Same root cause — a stale feed URL
        # serving the blog page — so report it the same way instead of "malformed XML".
        if _looks_like_html(xml_text):
            log.warning("feeds.html_not_feed", feed=source.key, url=source.url)
        else:
            log.warning("feeds.parse_error", feed=source.key, error=str(exc))
        return []

    tag = root.tag.split("}")[-1]  # strip namespace
    if tag == "rss":
        return _parse_rss(root, source)
    if tag == "feed":
        return _parse_atom(root, source)
    # Some feeds wrap RSS content without an <rss> root — try items anyway.
    if root.findall(".//item"):
        return _parse_rss(root, source)

    # A moved feed path often 200s with the blog page itself instead of 404ing, which
    # would otherwise look like "feed is just quiet". Name it so the URL gets fixed.
    if tag.lower() == "html":
        log.warning("feeds.html_not_feed", feed=source.key, url=source.url)
        return []

    log.warning("feeds.unknown_format", feed=source.key, root_tag=tag)
    return []


# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------


def _within_window(post: Post, since_days: int) -> bool:
    """True if the post is inside the date window.

    Posts with no parseable date are kept — dedup is the real guard, and dropping
    undated posts would silently lose feeds that omit pubDate.
    """
    if not post.published:
        return True
    cutoff = (datetime.now(tz=UTC) - timedelta(days=since_days)).strftime("%Y-%m-%d")
    return post.published >= cutoff


def _matches_keywords(post: Post, keywords: list[str]) -> bool:
    """Return True if title or summary contains any keyword (case-insensitive)."""
    haystack = (post.title + " " + post.summary).lower()
    return any(kw.lower() in haystack for kw in keywords)


# ---------------------------------------------------------------------------
# Fetch
# ---------------------------------------------------------------------------


def fetch_recent(
    feeds: list[FeedSource] = DEFAULT_FEEDS,
    since_days: int = DEFAULT_SINCE_DAYS,
    keywords: list[str] = DEFAULT_KEYWORDS,
    max_entries: int = MAX_ENTRIES_PER_FEED,
) -> list[Post]:
    """Fetch recent posts across feeds, filtered by date window and (Tier 2) keywords.

    Rate-limited with a 1s courtesy sleep between feeds. Tier 1 sources bypass the
    keyword filter — they are primary sources and low-volume enough to take whole.
    Returns a list deduplicated by canonical URL across all feeds.
    """
    seen_urls: set[str] = set()
    posts: list[Post] = []

    active = [f for f in feeds if f.enabled]
    for source in feeds:
        if not source.enabled:
            log.info("feeds.skipped_disabled", feed=source.key, note=source.note)

    with httpx.Client(timeout=30, follow_redirects=True, headers=HEADERS) as client:
        for i, source in enumerate(active):
            if i > 0:
                time.sleep(RATE_LIMIT_SLEEP)

            log.info("feeds.fetch", feed=source.key, url=source.url, tier=source.tier)
            try:
                resp = client.get(source.url)
                resp.raise_for_status()
            except httpx.HTTPError as exc:
                log.warning("feeds.fetch_error", feed=source.key, error=str(exc))
                continue

            feed_posts = parse_feed(resp.text, source)[:max_entries]
            log.info("feeds.results", feed=source.key, count=len(feed_posts))

            for post in feed_posts:
                canonical = _canonical_url(post.url)
                if canonical in seen_urls:
                    continue
                seen_urls.add(canonical)

                if not _within_window(post, since_days):
                    continue
                if source.tier >= 2 and not _matches_keywords(post, keywords):
                    log.debug("feeds.keyword_filtered", feed=source.key, title=post.title[:60])
                    continue
                posts.append(post)

    log.info("feeds.fetch_complete", total=len(posts), feeds=len(active))
    return posts


# ---------------------------------------------------------------------------
# File writer
# ---------------------------------------------------------------------------


def _title_slug(title: str) -> str:
    """Convert title to a short filesystem-safe slug."""
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower())
    return slug.strip("-")[:50]


def save_post(post: Post, output_dir: Path, dry_run: bool = False) -> Path | None:
    """Write one post to a markdown file in output_dir. Returns path written, or None.

    Filename shape `YYYY-MM-DD-feed-<key>-<slug>.md` mirrors the arXiv convention and
    is what the /learn queue globs on.
    """
    today = datetime.now(tz=UTC).strftime("%Y-%m-%d")
    slug = _title_slug(post.title)
    filename = f"{today}-feed-{post.feed_key}-{slug}.md"
    out_path = output_dir / filename

    if out_path.exists():
        log.debug("feeds.file_exists", file=filename)
        return None

    authors_str = ", ".join(post.authors[:5])
    categories_str = ", ".join(post.categories[:6])

    # Tier 2 is a gap-detector, not a citation of record (SOURCES.md) — that maps onto
    # the raw/ confidence contract in CLAUDE.md.
    confidence = "medium" if post.tier == 1 else "low"

    tags = ["article", "feed", post.feed_key]
    frontmatter_title = post.title.replace('"', "'")

    content = f"""---
title: "{frontmatter_title}"
url: {post.url}
source_type: article
source_name: "{post.feed_name}"
source_tier: {post.tier}
confidence: {confidence}
published: {post.published}
fetched: {today}
authors: "{authors_str}"
categories: [{categories_str}]
tags: [{", ".join(tags)}]
summary: "{post.feed_name} — {post.title[:80].replace('"', "'")}"
sources:
  - raw/web/{filename}
---

# {post.title}

**Source**: {post.feed_name} (Tier {post.tier})
**Published**: {post.published or "unknown"}
**Link**: [{post.url}]({post.url})
{f"**Authors**: {authors_str}" if authors_str else ""}

## Summary

{post.summary or "_No summary in feed — open the link for full text._"}
"""

    if dry_run:
        print(f"[feeds] would write: {filename}")
        print(f"  Title: {post.title[:80]}")
        print(f"  Source: {post.feed_name} (tier {post.tier})")
        print(f"  Published: {post.published or 'unknown'}")
        print()
    else:
        output_dir.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
        log.info("feeds.wrote_post", file=filename, title=post.title[:60])

    return out_path


# ---------------------------------------------------------------------------
# Scraper class
# ---------------------------------------------------------------------------


class FeedScraper(ScraperBase):
    source_name = "scrape-feeds"
    output_dir = DEFAULT_OUTPUT_DIR

    def __init__(
        self,
        feeds: list[FeedSource] = DEFAULT_FEEDS,
        since_days: int = DEFAULT_SINCE_DAYS,
        keywords: list[str] = DEFAULT_KEYWORDS,
        output_dir: Path = DEFAULT_OUTPUT_DIR,
    ) -> None:
        self._feeds = feeds
        self._since_days = since_days
        self._keywords = keywords
        self.output_dir = output_dir

    def run(self, dry_run: bool = False) -> list[Path]:
        """Fetch posts, dedup, and write to output_dir. Returns paths written."""
        existing_urls = _load_feed_urls_from_manifest()
        log.info("feeds.manifest_loaded", known_urls=len(existing_urls))

        posts = fetch_recent(
            feeds=self._feeds,
            since_days=self._since_days,
            keywords=self._keywords,
        )

        written: list[Path] = []
        skipped = 0
        for post in posts:
            if _canonical_url(post.url) in existing_urls:
                log.debug("feeds.dedup_skip", url=post.url)
                skipped += 1
                continue
            path = save_post(post, self.output_dir, dry_run=dry_run)
            if path is not None:
                written.append(path)

        prefix = "[dry-run] " if dry_run else ""
        print(
            f"\n{prefix}feeds: fetched {len(posts)}, wrote {len(written)}, "
            f"skipped {skipped} (already in manifest)"
        )
        return written

    @classmethod
    def _add_args(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--feeds",
            nargs="+",
            default=None,
            metavar="KEY",
            help=(
                "Feed keys to fetch (default: all enabled). "
                f"Enabled: {' '.join(f.key for f in DEFAULT_FEEDS if f.enabled)}. "
                "See --list-feeds for the full table."
            ),
        )
        parser.add_argument(
            "--list-feeds",
            action="store_true",
            help="Print the configured feeds and exit",
        )
        parser.add_argument(
            "--since-days",
            type=int,
            default=DEFAULT_SINCE_DAYS,
            metavar="N",
            help=f"Fetch posts from last N days (default: {DEFAULT_SINCE_DAYS})",
        )
        parser.add_argument(
            "--keywords",
            nargs="+",
            default=DEFAULT_KEYWORDS,
            metavar="KW",
            help="Keywords used to filter Tier 2 feeds (default: built-in list)",
        )
        parser.add_argument(
            "--output-dir",
            type=Path,
            default=DEFAULT_OUTPUT_DIR,
            help="Output directory (default: raw/web/)",
        )

    @classmethod
    def _from_args(cls, args: argparse.Namespace) -> FeedScraper:
        if args.list_feeds:
            for f in DEFAULT_FEEDS:
                status = "on " if f.enabled else "OFF"
                print(f"[{status}] {f.key:16} tier {f.tier}  {f.name:24} {f.url}")
                print(f"{'':22} scope: {f.scope}")
                if f.note:
                    print(f"{'':22} note:  {f.note}")
            raise SystemExit(0)

        feeds = DEFAULT_FEEDS
        if args.feeds:
            requested = set(args.feeds)
            known = {f.key for f in DEFAULT_FEEDS}
            unknown = requested - known
            if unknown:
                raise SystemExit(
                    f"Unknown feed key(s): {', '.join(sorted(unknown))}. "
                    f"Available: {', '.join(sorted(known))}"
                )
            feeds = [f for f in DEFAULT_FEEDS if f.key in requested]

        return cls(
            feeds=feeds,
            since_days=args.since_days,
            keywords=args.keywords,
            output_dir=args.output_dir,
        )


if __name__ == "__main__":
    FeedScraper.cli(description="Fetch recent RSS/Atom feed posts → raw/web/")
