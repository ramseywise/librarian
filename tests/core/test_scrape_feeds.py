"""Unit tests for core/scrape_feeds.py — RSS/Atom feed scraper."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2]))

from core.scrape_feeds import (
    DEFAULT_FEEDS,
    FeedScraper,
    FeedSource,
    Post,
    _canonical_url,
    _matches_keywords,
    _parse_date,
    _strip_html,
    _title_slug,
    _within_window,
    parse_feed,
    save_post,
)

TIER1 = FeedSource(key="t1", name="Tier One", url="https://example.com/rss", tier=1, scope="loop")
TIER2 = FeedSource(key="t2", name="Tier Two", url="https://example.com/atom", tier=2, scope="all")

RSS_FIXTURE = """<?xml version="1.0"?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/"
     xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>Tier One</title>
    <item>
      <title>Context Engineering for Agents</title>
      <link>https://example.com/posts/context-engineering</link>
      <description>&lt;p&gt;How to budget an agent's &lt;b&gt;context&lt;/b&gt; window.&lt;/p&gt;</description>
      <pubDate>Wed, 30 Jul 2026 12:00:00 GMT</pubDate>
      <dc:creator>Jane Doe</dc:creator>
      <category>harness</category>
    </item>
    <item>
      <title>Unrelated Gardening Post</title>
      <link>https://example.com/posts/gardening</link>
      <description>Tomatoes and soil pH.</description>
      <pubDate>Wed, 30 Jul 2026 09:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>
"""

ATOM_FIXTURE = """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Tier Two</title>
  <entry>
    <title>Building an Agent Harness</title>
    <link rel="alternate" href="https://example.com/atom/harness"/>
    <summary>A walkthrough of agent loop design and tool use.</summary>
    <published>2026-07-29T08:00:00Z</published>
    <author><name>John Roe</name></author>
    <category term="loop"/>
  </entry>
</feed>
"""


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def test_parse_rss_extracts_fields() -> None:
    posts = parse_feed(RSS_FIXTURE, TIER1)
    assert len(posts) == 2
    p = posts[0]
    assert p.title == "Context Engineering for Agents"
    assert p.url == "https://example.com/posts/context-engineering"
    assert p.published == "2026-07-30"
    assert p.authors == ["Jane Doe"]
    assert p.categories == ["harness"]
    assert p.feed_key == "t1"
    assert p.tier == 1
    # HTML stripped from the description
    assert "<p>" not in p.summary
    assert "context" in p.summary


def test_parse_atom_extracts_fields() -> None:
    posts = parse_feed(ATOM_FIXTURE, TIER2)
    assert len(posts) == 1
    p = posts[0]
    assert p.title == "Building an Agent Harness"
    assert p.url == "https://example.com/atom/harness"
    assert p.published == "2026-07-29"
    assert p.authors == ["John Roe"]
    assert p.categories == ["loop"]


def test_parse_feed_malformed_xml_returns_empty() -> None:
    assert parse_feed("<rss><channel><item>", TIER1) == []


def test_parse_feed_unknown_root_returns_empty() -> None:
    assert parse_feed('<?xml version="1.0"?><rss-ish><body/></rss-ish>', TIER1) == []


@pytest.mark.parametrize(
    "html",
    [
        "<html><body><h1>Blog</h1></body></html>",
        '<html xmlns="http://www.w3.org/1999/xhtml"><body/></html>',
        "<!DOCTYPE html><html><body><p>hi</p></body></html>",
        "<HTML><BODY/></HTML>",
        # Real pages are rarely well-formed XML — unclosed <br> fails ET.fromstring,
        # so this must still be reported as HTML, not as "malformed XML".
        "<html><body><br><p>hi</body></html>",
    ],
)
def test_parse_feed_reports_html_page_as_wrong_url(
    html: str, capsys: pytest.CaptureFixture[str]
) -> None:
    # A stale feed path serves the blog page with HTTP 200 rather than 404ing. Parsing
    # to nothing is not enough — it must say WHY, or it reads as "feed is just quiet".
    assert parse_feed(html, TIER1) == []

    out = capsys.readouterr().out
    assert "feeds.html_not_feed" in out
    assert TIER1.url in out


def test_parse_feed_reports_genuine_malformed_xml_as_parse_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Truncated feed XML is a different failure than a wrong URL — keep them distinct.
    assert parse_feed("<rss><channel><item>", TIER1) == []

    out = capsys.readouterr().out
    assert "feeds.parse_error" in out
    assert "feeds.html_not_feed" not in out


def test_parse_feed_skips_entries_missing_link_or_title() -> None:
    xml = """<?xml version="1.0"?><rss version="2.0"><channel>
      <item><title>No link here</title></item>
      <item><link>https://example.com/no-title</link></item>
    </channel></rss>"""
    assert parse_feed(xml, TIER1) == []


# ---------------------------------------------------------------------------
# Date parsing
# ---------------------------------------------------------------------------


def test_parse_date_rss_rfc822() -> None:
    assert _parse_date("Wed, 30 Jul 2026 12:00:00 GMT") == "2026-07-30"


def test_parse_date_atom_iso() -> None:
    assert _parse_date("2026-07-29T08:00:00Z") == "2026-07-29"


def test_parse_date_garbage_returns_empty() -> None:
    assert _parse_date("not a date") == ""
    assert _parse_date("") == ""


# ---------------------------------------------------------------------------
# URL canonicalisation / dedup
# ---------------------------------------------------------------------------


def test_canonical_url_strips_tracking_and_trailing_slash() -> None:
    base = "https://example.com/post"
    assert _canonical_url("https://example.com/post/") == base
    assert _canonical_url("https://example.com/post?utm_source=rss") == base
    assert _canonical_url("https://example.com/post#section") == base
    assert _canonical_url("https://example.com/post/?ref=feed") == base


def test_canonical_url_preserves_meaningful_query() -> None:
    url = "https://example.com/post?id=42"
    assert _canonical_url(url) == url


# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------


def _post(**kw: object) -> Post:
    defaults = {
        "feed_key": "t1",
        "feed_name": "Tier One",
        "tier": 1,
        "title": "T",
        "summary": "S",
        "url": "https://e.com/x",
    }
    return Post(**{**defaults, **kw})


def test_within_window_keeps_undated_posts() -> None:
    assert _within_window(_post(published=""), since_days=7) is True


def test_within_window_rejects_old_posts() -> None:
    assert _within_window(_post(published="1999-01-01"), since_days=7) is False


def test_matches_keywords_scans_title_and_summary() -> None:
    assert _matches_keywords(_post(title="On Agentic Loops", summary=""), ["agentic"])
    assert _matches_keywords(_post(title="X", summary="about RAG systems"), ["rag"])
    assert not _matches_keywords(_post(title="Tomatoes", summary="soil"), ["agentic"])


def test_strip_html_truncates_long_summaries() -> None:
    long_text = "word " * 1000
    out = _strip_html(f"<p>{long_text}</p>")
    assert len(out) <= 1501
    assert out.endswith("…")


# ---------------------------------------------------------------------------
# Writer
# ---------------------------------------------------------------------------


def test_title_slug_is_filesystem_safe() -> None:
    assert _title_slug("Hello, World! (2026)") == "hello-world-2026"


def test_save_post_writes_learn_queue_filename(tmp_path: Path) -> None:
    post = _post(title="Context Engineering", url="https://e.com/ctx", published="2026-07-30")
    out = save_post(post, tmp_path)
    assert out is not None and out.exists()
    # /learn globs on *-feed-*.md
    assert "-feed-t1-" in out.name
    assert out.name.endswith("-context-engineering.md")

    text = out.read_text(encoding="utf-8")
    assert "url: https://e.com/ctx" in text
    assert "source_type: article" in text
    assert "confidence: medium" in text  # tier 1


def test_save_post_tier2_marked_low_confidence(tmp_path: Path) -> None:
    post = _post(tier=2, feed_key="t2", title="Aggregated Take", url="https://e.com/agg")
    out = save_post(post, tmp_path)
    assert "confidence: low" in out.read_text(encoding="utf-8")


def test_save_post_escapes_quotes_in_frontmatter(tmp_path: Path) -> None:
    post = _post(title='The "Best" Agent', url="https://e.com/q")
    out = save_post(post, tmp_path)
    text = out.read_text(encoding="utf-8")
    # Double quotes would break the YAML string — must be downgraded to single
    assert "title: \"The 'Best' Agent\"" in text


def test_save_post_dry_run_writes_nothing(tmp_path: Path) -> None:
    save_post(_post(), tmp_path, dry_run=True)
    assert list(tmp_path.glob("*.md")) == []


def test_save_post_skips_existing_file(tmp_path: Path) -> None:
    post = _post(title="Dupe", url="https://e.com/d")
    first = save_post(post, tmp_path)
    assert first is not None
    assert save_post(post, tmp_path) is None


# ---------------------------------------------------------------------------
# Scraper wiring
# ---------------------------------------------------------------------------


def test_scraper_is_registered_with_source_name() -> None:
    assert FeedScraper.source_name == "scrape-feeds"
    assert FeedScraper.output_dir.name == "web"


def test_default_feeds_have_unique_keys() -> None:
    keys = [f.key for f in DEFAULT_FEEDS]
    assert len(keys) == len(set(keys))


def test_default_feeds_cover_sources_md_tiers() -> None:
    tiers = {f.tier for f in DEFAULT_FEEDS}
    assert tiers == {1, 2}


def test_at_least_one_feed_enabled() -> None:
    assert any(f.enabled for f in DEFAULT_FEEDS)


def test_disabled_feeds_carry_an_explanatory_note() -> None:
    # A feed is only allowed to be off if the table says why.
    for f in DEFAULT_FEEDS:
        if not f.enabled:
            assert f.note, f"{f.key} is disabled without a note"


def test_fetch_recent_skips_disabled_feeds(monkeypatch: pytest.MonkeyPatch) -> None:
    off = FeedSource(
        key="off", name="Off", url="https://e.com/off", tier=1, scope="x", enabled=False
    )
    requested: list[str] = []

    class _FakeResponse:
        text = RSS_FIXTURE

        def raise_for_status(self) -> None:
            return None

    class _FakeClient:
        def __enter__(self) -> _FakeClient:
            return self

        def __exit__(self, *_: object) -> None:
            return None

        def get(self, url: str) -> _FakeResponse:
            requested.append(url)
            return _FakeResponse()

    monkeypatch.setattr("core.scrape_feeds.httpx.Client", lambda **_: _FakeClient())

    from core.scrape_feeds import fetch_recent

    fetch_recent(feeds=[TIER1, off], since_days=36500)

    assert requested == [TIER1.url]


def test_run_dedups_against_known_urls(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    posts = [
        _post(title="Fresh", url="https://e.com/fresh"),
        _post(title="Seen", url="https://e.com/seen/?utm_source=rss"),
    ]
    monkeypatch.setattr("core.scrape_feeds.fetch_recent", lambda **_: posts)
    monkeypatch.setattr(
        "core.scrape_feeds._load_feed_urls_from_manifest", lambda: {"https://e.com/seen"}
    )

    written = FeedScraper(output_dir=tmp_path).run()

    assert len(written) == 1
    assert "fresh" in written[0].name
