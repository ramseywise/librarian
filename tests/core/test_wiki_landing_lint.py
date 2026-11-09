"""`librarian wiki verify|index-add|lint` and `librarian ingest mark` on a small tmp wiki."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest

import librarian.ingest.manifest as manifest_module
from librarian.ingest.manifest import main as manifest_main
from librarian.wiki.landing import add_see_also, add_to_index, verify
from librarian.wiki.landing import main as landing_main
from librarian.wiki.lint import lint


def _page(wiki: Path, rel: str, title: str, body: str = "") -> Path:
    path = wiki / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\ntitle: {title}\ntags: [rag, concept]\n"
        "summary: A summary that has more than eight words in it.\n"
        f"updated: 2026-11-01\nsources: []\n---\n\n# {title}\n\n{body}\n\n## See Also\n- [[Hub]]\n"
    )
    return path


def _wiki(tmp_path: Path) -> Path:
    wiki = tmp_path / "wiki"
    _page(wiki, "rag/hub.md", "Hub", "See [[Linked Page]].")
    _page(wiki, "rag/linked-page.md", "Linked Page", "x")
    (wiki / "_index.md").write_text(
        "# Wiki Index\n\n**2 pages** across 1 domains.\n\n## RAG\n\n"
        "- [[Hub]] — hub\n- [[Zed]] — z\n\n## Meta\n\n- [[M]] — m\n"
    )
    return wiki


def test_verify_flags_orphan_and_unindexed(tmp_path: Path) -> None:
    wiki = _wiki(tmp_path)
    orphan = _page(wiki, "rag/lonely.md", "Lonely", "nothing links here")
    linked = wiki / "rag/linked-page.md"
    by_rel = {s.rel: s for s in verify([orphan, linked], wiki)}
    assert by_rel["rag/lonely.md"].inbound == 0
    assert not by_rel["rag/lonely.md"].indexed
    assert by_rel["rag/linked-page.md"].inbound == 1


def test_verify_skips_private(tmp_path: Path) -> None:
    wiki = _wiki(tmp_path)
    priv = _page(wiki, "private/secret.md", "Secret")
    (status,) = verify([priv], wiki)
    assert status.private and status.indexed


def test_verify_exit_code(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    wiki = _wiki(tmp_path)
    orphan = _page(wiki, "rag/lonely.md", "Lonely")
    assert landing_main(["verify", str(orphan), "--wiki-dir", str(wiki)]) == 1
    assert "ORPHAN" in capsys.readouterr().out


def test_index_add_inserts_alphabetically_and_counts(tmp_path: Path) -> None:
    wiki = _wiki(tmp_path)
    page = wiki / "rag/linked-page.md"
    added, problems = add_to_index([page], wiki)
    assert added == ["Linked Page"] and not problems
    lines = (wiki / "_index.md").read_text().splitlines()
    rag = lines[lines.index("## RAG") + 1 : lines.index("## Meta")]
    titles = [ln for ln in rag if ln.startswith("- ")]
    assert [t.split("]]")[0] for t in titles] == ["- [[Hub", "- [[Linked Page", "- [[Zed"]
    assert "**4 pages**" in "\n".join(lines)
    assert add_to_index([page], wiki) == ([], [])  # idempotent


def test_index_add_never_lists_private_or_unknown_section(tmp_path: Path) -> None:
    wiki = _wiki(tmp_path)
    priv = _page(wiki, "private/secret.md", "Secret")
    odd = _page(wiki, "newdomain/p.md", "P")
    added, problems = add_to_index([priv, odd], wiki)
    assert added == [] and len(problems) == 1
    assert "Secret" not in (wiki / "_index.md").read_text()


def test_lint_ranks_findings(tmp_path: Path) -> None:
    wiki = _wiki(tmp_path)
    _page(wiki, "rag/dead.md", "Dead", "points at [[Nowhere At All]]")
    bare = wiki / "rag/bare.md"
    bare.write_text("---\ntitle: Bare\ntags: [rag]\n---\n\nbody [[Hub]]\n")
    findings = lint(wiki, date(2026, 11, 7))
    got = {(f.severity, f.page, f.message.split(":")[0]) for f in findings}
    assert ("BLOCKER", "rag/dead.md", "dead wikilink") in got
    assert ("BLOCKER", "rag/bare.md", "missing frontmatter") in got
    assert ("WARN", "rag/dead.md", "orphan (no inbound link)") in got
    assert findings[0].severity == "BLOCKER"


def test_lint_ignores_links_inside_code(tmp_path: Path) -> None:
    wiki = _wiki(tmp_path)
    body = (
        "Write `[[Successor]]` here.\n\n```markdown\n- [[Example Page]] — extends\n```\n\n[[Gone]]"
    )
    _page(wiki, "rag/syntax.md", "Syntax", body)
    dead = [f.message for f in lint(wiki, date(2026, 11, 7)) if f.page == "rag/syntax.md"]
    assert [m for m in dead if m.startswith("dead")] == ["dead wikilink: [[Gone]]"]


def test_lint_stale(tmp_path: Path) -> None:
    wiki = _wiki(tmp_path)
    findings = lint(wiki, date(2027, 6, 1))
    assert any(f.message.startswith("stale") for f in findings)


def test_manifest_mark_cli(tmp_path: Path) -> None:
    raw = tmp_path / "data" / "raw" / "web"
    raw.mkdir(parents=True)
    src = raw / "a.md"
    src.write_text("hello")
    with (
        patch.object(manifest_module, "MANIFEST_PATH", tmp_path / "manifest.jsonl"),
        patch.object(manifest_module, "REPO_ROOT", tmp_path),
    ):
        assert manifest_main(["mark", str(src), "--pages", "data/wiki/rag/x.md"]) == 0
        entries = manifest_module._load()
        assert entries["data/raw/web/a.md"]["wiki_pages"] == ["data/wiki/rag/x.md"]
        assert manifest_module.check(src)[0] is False
        assert manifest_main(["mark", str(raw / "missing.md")]) == 2


def test_see_also_appends_at_section_end_and_skips_present(tmp_path: Path) -> None:
    wiki = _wiki(tmp_path)
    path = _page(wiki, "rag/target.md", "Target", "Body.")
    added, notes = add_see_also(
        path,
        ["- [[Linked Page]] — instance-of (a note)", "- [[Hub]] — related"],
        wiki,
        today=date(2026, 11, 9),
    )
    assert added == ["- [[Linked Page]] — instance-of (a note)"]
    assert notes == ["skip, already linked: [[Hub]]"]
    text = path.read_text()
    assert text.rstrip().endswith("- [[Hub]]\n- [[Linked Page]] — instance-of (a note)")
    assert "updated: 2026-11-09" in text


def test_see_also_refuses_unknown_target_and_type(tmp_path: Path) -> None:
    wiki = _wiki(tmp_path)
    path = _page(wiki, "rag/target.md", "Target", "Body.")
    before = path.read_text()
    added, notes = add_see_also(
        path, ["- [[Nowhere]] — related", "- [[Linked Page]] — part-of", "no link"], wiki
    )
    assert added == []
    assert len(notes) == 3
    assert path.read_text() == before


def test_see_also_creates_missing_section(tmp_path: Path) -> None:
    wiki = _wiki(tmp_path)
    path = wiki / "rag/bare.md"
    path.write_text(
        "---\ntitle: Bare\ntags: [rag, concept]\nupdated: 2026-11-01\n---\n\n# Bare\n\nx\n"
    )
    added, _ = add_see_also(path, ["- [[Hub]] — related"], wiki)
    assert added
    assert path.read_text().endswith("x\n\n## See Also\n- [[Hub]] — related\n")
