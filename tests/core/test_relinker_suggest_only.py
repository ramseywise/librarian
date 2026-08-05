"""The relinker is suggest-only: it must never modify a wiki page.

These pin the invariant behind #106, not just the formatting of the suggestions
file. `test_relink_leaves_every_page_byte_identical` is the load-bearing one — it
fails if an auto-write path is ever reintroduced.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2]))

pytest.importorskip("sklearn", reason="relink() needs the `api` extra")
numpy = pytest.importorskip("numpy", reason="relink() needs the `api` extra")

import core.relinker  # noqa: E402
from core.relinker import build_link_graph, load_pages, relink  # noqa: E402


def _build_wiki(tmp_path: Path) -> Path:
    """Two mutually-linked pages, an unlinked high-similarity page, and an orphan.

    `gamma` is linked *from* beta only, so alpha↔gamma is an unlinked pair and is
    free to become an auto-tier candidate; alpha↔beta is already linked and is
    correctly skipped.
    """
    wiki = tmp_path / "wiki"
    (wiki / "rag").mkdir(parents=True)

    (wiki / "rag" / "alpha.md").write_text(
        "---\ntitle: Alpha Page\ntags: [rag, concept, chunking]\n---\n\n"
        "# Alpha Page\n\nChunking and retrieval.\n\n## See Also\n- [[Beta Page]]\n"
    )
    (wiki / "rag" / "beta.md").write_text(
        "---\ntitle: Beta Page\ntags: [rag, pattern]\n---\n\n"
        "# Beta Page\n\nReranking and fusion.\n\n## See Also\n- [[Alpha Page]]\n"
        "- [[Gamma Page]]\n"
    )
    (wiki / "rag" / "gamma.md").write_text(
        "---\ntitle: Gamma Page\ntags: [rag, pattern, chunking]\n---\n\n"
        "# Gamma Page\n\nChunk sizing strategies.\n"
    )
    (wiki / "rag" / "orphan.md").write_text(
        "---\ntitle: Orphan Page\ntags: [rag, concept]\n---\n\n"
        "# Orphan Page\n\nNothing links here.\n"
    )
    return wiki


@pytest.fixture
def wiki(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A tmp wiki wired up as WIKI_DIR, with similarity/embeddings stubbed.

    alpha↔gamma raw 0.50 clears the 0.65 auto gate once bonuses apply (+0.1
    same-domain, +0.05 shared `chunking` tag, +0.1 pattern/concept) — the exact
    shape #106 flags: a mid-cosine pair crossing the gate on bonuses alone. The
    orphan's best hub sits above the 0.3 backfill floor but below the auto gate.
    """
    wiki_dir = _build_wiki(tmp_path)
    monkeypatch.setattr(core.relinker, "WIKI_DIR", wiki_dir)

    stems = ["alpha", "beta", "gamma", "orphan"]
    raw = {
        ("alpha", "gamma"): 0.50,
        ("alpha", "beta"): 0.45,
        ("beta", "gamma"): 0.45,
        ("alpha", "orphan"): 0.42,
        ("beta", "orphan"): 0.40,
        ("gamma", "orphan"): 0.40,
    }

    def _sim(_vecs: object) -> numpy.ndarray:
        return numpy.array(
            [[1.0 if a == b else raw[tuple(sorted((a, b)))] for b in stems] for a in stems]
        )

    monkeypatch.setattr("sklearn.metrics.pairwise.cosine_similarity", _sim)
    monkeypatch.setattr("shared.embeddings.compute_embeddings", lambda: (stems, None))
    return wiki_dir


def _run(wiki_dir: Path) -> tuple[core.relinker.RelinkReport, dict[str, object]]:
    pages = load_pages()
    build_link_graph(pages)
    return relink(pages), pages


def test_relink_leaves_every_page_byte_identical(wiki: Path) -> None:
    """The load-bearing invariant: no wiki page is written during a relink pass."""
    before = {p: p.read_bytes() for p in sorted(wiki.rglob("*.md"))}

    report, _ = _run(wiki)

    # Guard against a vacuous pass — the run must actually produce auto-tier work.
    assert report.auto_candidates, "fixture no longer exercises the auto-threshold path"

    after = {p: p.read_bytes() for p in sorted(wiki.rglob("*.md")) if not p.name.startswith("_")}
    for path, original in before.items():
        assert after[path] == original, f"{path.name} was modified by relink()"


def test_above_threshold_pairs_become_candidates_not_writes(wiki: Path) -> None:
    report, _ = _run(wiki)

    pairs = {(src, tgt) for src, tgt, _ in report.auto_candidates}
    assert ("alpha", "gamma") in pairs or ("gamma", "alpha") in pairs
    for _, _, score in report.auto_candidates:
        assert score >= 0.65

    # alpha↔beta is already linked in both directions — never a candidate.
    assert ("alpha", "beta") not in pairs and ("beta", "alpha") not in pairs


def test_suggestions_file_written_when_only_auto_candidates_exist(wiki: Path) -> None:
    """The old `if suggested` gate dropped auto-only runs on the floor."""
    report, _ = _run(wiki)
    assert report.auto_candidates

    suggestions = wiki / "_relink_suggestions.md"
    assert suggestions.exists()
    assert "## Auto-Link Candidates" in suggestions.read_text()


def test_orphan_candidates_land_under_their_own_heading(wiki: Path) -> None:
    report, _ = _run(wiki)

    orphans = {orphan for _, orphan, _ in report.orphan_candidates}
    assert "orphan" in orphans
    for hub, _, score in report.orphan_candidates:
        assert hub != "orphan", "the hub is the source, the orphan is the target"
        assert score > 0.3

    content = (wiki / "_relink_suggestions.md").read_text()
    assert "## Orphan Backfill" in content
    # Hub → orphan direction, per the section's curation instruction.
    assert "→ [[Orphan Page]]" in content


def test_empty_sections_are_omitted(wiki: Path) -> None:
    report, _ = _run(wiki)
    content = (wiki / "_relink_suggestions.md").read_text()

    if not report.suggested:
        assert "## Relink Candidates" not in content


def test_append_see_also_is_gone() -> None:
    """Stops the auto-write helper being quietly reintroduced."""
    assert not hasattr(core.relinker, "append_see_also")
