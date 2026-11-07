"""Every consumer of `[[wikilinks]]` resolves them through `resolve_link`, so they agree.

One fixture wiki holds each way a link can name a page (stem, title, case, alias, `|display`,
`#heading`, a title with a slash) and each way it must not resolve (a collision loser's name,
a tombstone, a private page, a missing page). The graph UI, the relinker, health stats, the
search index's backlinks, graph expansion and the course catalog must give the same answer.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from librarian.courses import catalog
from librarian.retrieval import graph_expansion, index
from librarian.wiki import lint, parser, relinker, telemetry
from librarian.wiki.common import LinkEntry, LinkIndex, link_name, resolve_link

LINKS = [
    "target-page",  # exact stem
    "Target Page",  # title
    "TARGET PAGE",  # title, other case
    "target_page",  # slugified stem
    "Former Name",  # alias
    "Target Page|shown text",  # |display
    "Target Page#Some Heading",  # #heading
    "rag/target-page.md",  # path form
    "Bayesian A/B Testing",  # a title that holds a slash
    "Shared Title",  # collision: first in path order wins
    "Retired Page",  # tombstone: not dead, not an edge
    "Secret Thing",  # private: never resolves for public consumers
    "Nowhere At All",  # dead
]
# Everything above lands on one of these three pages, except the last three names.
EXPECTED = {"target-page", "old-name-holder", "ab-testing", "dup-a"}


def _page(
    root: Path, rel: str, title: str, *, extra: str = "", tags: str = "rag", body: str = ""
) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\ntitle: {title}\ntags: [{tags}]\nsummary: A page about {title} for the fixture wiki.\n"
        f"updated: 2026-11-01\nsources: []\n{extra}---\n\n# {title}\n\n{body}\n"
    )


@pytest.fixture()
def wiki(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "wiki"
    _page(root, "rag/target-page.md", "Target Page")
    _page(root, "rag/old-name-holder.md", "Brand New Name", extra="aliases: [Former Name]\n")
    _page(root, "foundations/ab-testing.md", "Bayesian A/B Testing", tags="foundations")
    _page(root, "rag/dup-a.md", "Shared Title")
    _page(root, "rag/dup-b.md", "Shared Title")
    _page(root, "rag/retired.md", "Retired Page", tags="rag, tombstone")
    _page(root, "private/secret-thing.md", "Secret Thing")
    see_also = "\n".join(f"- [[{t}]] — extends" for t in LINKS)
    _page(root, "rag/source-page.md", "Source Page", body=f"## See Also\n{see_also}")
    monkeypatch.setattr(parser, "WIKI_DIR", root)
    monkeypatch.setattr(relinker, "WIKI_DIR", root)
    return root


def _stems(keys: set[str]) -> set[str]:
    return {Path(k).stem for k in keys}


def test_link_name_strips_display_heading_and_prefix() -> None:
    assert link_name(" See also: Foo Bar#Baz|label ") == "Foo Bar"


def test_every_consumer_resolves_the_same_targets(wiki: Path) -> None:
    graph = parser.parse_wiki_uncached()
    ui = {e["target"] for e in graph["edges"] if e["source"] == "source-page"}

    pages = relinker.load_pages()
    relinker.build_link_graph(pages)
    relink = set(pages["source-page"].outgoing_links)

    public = telemetry._public_pages(wiki)
    scored = [p for p in public if p.scored]
    outbound, _ = telemetry._link_edges(scored, telemetry._link_index(public))
    stats = {Path(r).stem for r in outbound["rag/source-page.md"]}

    rows = index.read_pages(sorted(wiki.rglob("*.md")))
    public_rows = [r for r in rows if "/wiki/private/" not in r[0]]
    backlinks = index.compute_backlinks(public_rows)
    searched = {Path(k).stem for k, n in backlinks.items() if n}
    typed = graph_expansion.build_typed_edges([(r[0], r[1], r[5]) for r in public_rows])
    expansion = {Path(t).stem for s, t, _ in typed if Path(s).stem == "source-page"}

    refs = catalog._load_wiki(wiki)
    slugs = catalog._wiki_slugs(refs)
    lessons = {catalog._resolve_wikilink(t, refs, slugs) for t in LINKS} - {None}

    assert ui == EXPECTED
    assert relink == EXPECTED
    assert stats == EXPECTED
    assert searched == EXPECTED
    assert expansion == EXPECTED
    assert lessons == EXPECTED


def test_backlink_counts_match_link_occurrences(wiki: Path) -> None:
    rows = [r for r in index.read_pages(sorted(wiki.rglob("*.md"))) if "/wiki/private/" not in r[0]]
    counts = {Path(k).stem: n for k, n in index.compute_backlinks(rows).items()}
    # target-page is named 7 ways; dup-a once; the rest once each.
    assert counts["target-page"] == 7
    assert counts["dup-a"] == 1
    assert counts["dup-b"] == 0


def test_tombstone_is_not_dead_and_private_name_is_dead_in_public(wiki: Path) -> None:
    dead = [f.message for f in lint.lint(wiki, date(2026, 11, 7)) if f.message.startswith("dead")]
    assert sorted(dead) == [
        "dead wikilink: [[Nowhere At All]]",
        "dead wikilink: [[Secret Thing]]",
    ]


def test_lint_warns_on_title_collision(wiki: Path) -> None:
    warns = [f for f in lint.lint(wiki, date(2026, 11, 7)) if "claimed by" in f.message]
    assert [(f.severity, f.page) for f in warns] == [("WARN", "rag/dup-a.md")]
    assert "rag/dup-b.md" in warns[0].message


def test_private_link_is_a_leak_only_for_private_consumers(wiki: Path) -> None:
    public = telemetry._link_index(telemetry._public_pages(wiki))
    private = telemetry._link_index(telemetry._private_pages(wiki))
    assert telemetry._links_to_private("Secret Thing", public, private)
    assert not telemetry._links_to_private("Target Page", public, private)
    assert public.resolve("Secret Thing") is None
    assert private.resolve("Secret Thing", only_private=True) is not None


def test_public_name_beats_private_one_unless_path_is_spelled() -> None:
    pub = LinkEntry("pub", "a/x.md", "x", "X")
    priv = LinkEntry("priv", "private/x.md", "x", "X", private=True)
    idx = LinkIndex([priv, pub])
    assert resolve_link("X", idx) == "pub"
    assert resolve_link("X", idx, include_private=True) == "pub"
    assert resolve_link("X", idx, include_private=True, private_first=True) == "priv"
    assert resolve_link("x", idx, only_private=True) == "priv"


def test_rank_is_stem_then_title_then_alias_and_first_path_wins() -> None:
    a = LinkEntry("a", "z/a.md", "a", "Zed", aliases=("Mine",))
    b = LinkEntry("b", "a/b.md", "b", "Mine")
    c = LinkEntry("c", "a/c.md", "c", "Zed")
    idx = LinkIndex([a, b, c])
    assert resolve_link("mine", idx) == "b"  # a title beats another page's old name
    assert resolve_link("Zed", idx) == "c"  # same rank: sorted path order, not insertion order
    assert [(k.kind, k.slug, k.keys) for k in idx.collisions] == [("title", "zed", ("c", "a"))]
