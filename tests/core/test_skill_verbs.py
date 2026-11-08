"""The verbs that took mechanical steps out of the skills, on small tmp wikis."""

from __future__ import annotations

import json
from datetime import UTC, date, datetime
from pathlib import Path
from unittest.mock import patch

import pytest

import librarian.ingest.manifest as manifest_module
from librarian.wiki import compact_signals, lint, sync_check, week

TODAY = date(2026, 11, 8)


def _page(
    wiki: Path,
    rel: str,
    title: str,
    *,
    updated: str = "2026-11-01",
    tags: str = "[rag, concept]",
    body: str = "",
    sources: str = "[]",
    links: str = "",
) -> Path:
    path = wiki / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\ntitle: {title}\ntags: {tags}\n"
        f"summary: A summary that has more than eight words in it.\n"
        f"updated: {updated}\nsources: {sources}\n---\n\n# {title}\n\n{body}\n\n"
        f"## See Also\n{links}\n"
    )
    return path


# --- wiki sync-check ---------------------------------------------------------------------


def _app(tmp_path: Path, known: str = "rag: 1, adk: 2") -> Path:
    app = tmp_path / "app" / "src"
    (app / "theme").mkdir(parents=True)
    body = ",\n".join(f'  {pair.split(":")[0].strip()}: "#fff"' for pair in known.split(","))
    (app / "theme" / "domains.ts").write_text(
        f'export const KNOWN: Record<string, string> = {{\n{body},\n  private: "#999",\n}};\n'
    )
    return app


def _src(tmp_path: Path, parser_body: str | None = None) -> Path:
    src = tmp_path / "pkg"
    good = (
        "def {name}():\n    return {{d.name for d in WIKI_DIR.iterdir() if d.name != 'private'}}\n"
    )
    for rel, func in sync_check.DERIVATIONS:
        path = src / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(good.format(name=func))
    if parser_body is not None:
        (src / "wiki" / "parser.py").write_text(parser_body)
    return src


def test_sync_check_clean_and_notes(tmp_path: Path) -> None:
    wiki = tmp_path / "wiki"
    for i in range(3):
        _page(wiki, f"rag/p{i}.md", f"P{i}")
        _page(wiki, f"harness/h{i}.md", f"H{i}")
    _page(wiki, "private/secret.md", "Secret")
    _page(wiki, "thin/one.md", "One")
    domains, findings = sync_check.check(wiki, _src(tmp_path), _app(tmp_path))
    assert set(domains) == {"rag", "harness", "thin"}
    kinds = {(f.kind, f.where) for f in findings}
    assert ("THIN", "thin") in kinds
    assert ("NOTE", "harness") in kinds  # no fixed colour
    assert ("NOTE", "adk") in kinds  # ghost colour
    assert not any(f.kind == "DRIFT" for f in findings)


def test_sync_check_flags_literal_list_and_frontend_list(tmp_path: Path) -> None:
    wiki = tmp_path / "wiki"
    _page(wiki, "rag/p.md", "P")
    src = _src(tmp_path, "def _domain_tag_set():\n    return {'rag', 'adk', 'infra', 'mcp'}\n")
    app = _app(tmp_path)
    (app / "Filter.tsx").write_text('const D = ["rag", "adk", "infra"];\n')
    (app / "One.tsx").write_text('const D = ["rag"];\n')
    _, findings = sync_check.check(wiki, src, app)
    drift = {f.where: f.message for f in findings if f.kind == "DRIFT"}
    assert "wiki/parser.py:_domain_tag_set" in drift
    assert "literal" in drift["wiki/parser.py:_domain_tag_set"]
    assert any(w.startswith("app/src/Filter.tsx") for w in drift)
    assert not any("One.tsx" in w for w in drift)


def test_sync_check_exit_code(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    wiki = tmp_path / "wiki"
    _page(wiki, "rag/p.md", "P")
    args = ["--wiki-dir", str(wiki), "--app-src", str(_app(tmp_path))]
    assert sync_check.main([*args, "--src-dir", str(_src(tmp_path))]) == 0
    bad = _src(tmp_path, "def _domain_tag_set():\n    return set()\n")
    assert sync_check.main([*args, "--src-dir", str(bad)]) == 1
    assert "does not read WIKI_DIR" in capsys.readouterr().out


def test_sync_check_against_the_real_code_has_no_drift() -> None:
    # The repo's own derivations must pass their own check (wiki dir is a tmp stand-in).
    drift = [
        f
        for f in sync_check.check(Path(__file__).parent, sync_check.SRC_DIR, sync_check.APP_SRC)[1]
        if f.kind == "DRIFT"
    ]
    assert drift == []


# --- wiki compact-signals -----------------------------------------------------------------


def test_compact_signals(tmp_path: Path) -> None:
    wiki = tmp_path / "wiki"
    _page(wiki, "rag/hub.md", "Hub", links="- [[Used]]\n- [[Old Idle]]")
    _page(wiki, "rag/used.md", "Used", updated="2026-06-01", links="- [[Hub]]")
    _page(wiki, "rag/old-idle.md", "Old Idle", updated="2026-06-01", links="- [[Hub]]")
    _page(wiki, "rag/big.md", "Big", body="line\n" * 320)
    _page(wiki, "private/p.md", "Private")
    log = tmp_path / "retrieval.jsonl"
    now = datetime(2026, 11, 7, tzinfo=UTC).isoformat()
    old = datetime(2026, 1, 1, tzinfo=UTC).isoformat()
    rows = [
        {"ts": now, "tool": "search_wiki", "top_paths": ["rag/used.md", "rag/hub.md"]}
        for _ in range(3)
    ]
    rows += [{"ts": old, "tool": "search_wiki", "top_paths": ["rag/old-idle.md"]}]
    rows += [{"ts": now, "tool": "search_wiki", "top_paths": ["private/p.md"]}]
    log.write_text("\n".join(json.dumps(r) for r in rows) + "\nnot json\n")
    report = compact_signals.compute(wiki, log, TODAY, days=30)
    assert [r["page"] for r in report["stale"]] == ["rag/old-idle.md", "rag/used.md"] or {
        r["page"] for r in report["stale"]
    } == {"rag/used.md", "rag/old-idle.md"}
    assert [r["page"] for r in report["large"]] == ["rag/big.md"]
    # old-idle: stale, one inbound link, no retrieval in the window; used has retrievals
    assert [r["page"] for r in report["retire_candidates"]] == ["rag/old-idle.md"]
    assert report["co_retrieved"] == [{"pages": ["rag/hub.md", "rag/used.md"], "count": 3}]
    assert "private" not in json.dumps(report)


def test_compact_signals_without_telemetry(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    wiki = tmp_path / "wiki"
    _page(wiki, "rag/a.md", "A")
    code = compact_signals.main(
        ["--wiki-dir", str(wiki), "--retrieval-log", str(tmp_path / "none.jsonl")]
    )
    assert code == 0
    assert "no retrieval telemetry" in capsys.readouterr().out


# --- wiki lint extras ---------------------------------------------------------------------


def test_lint_open_conflicts_and_stale_suggestions(tmp_path: Path) -> None:
    wiki = tmp_path / "wiki"
    _page(wiki, "rag/a.md", "A", links="- [[B]]")
    _page(wiki, "rag/b.md", "B", links="- [[A]]")
    (wiki / "_conflicts.md").write_text(
        "## Conflict: One — 2026-11-01\n\n**Status:** Unresolved — needs review\n\n"
        "## Conflict: Two — 2026-10-01\n\n**Status:** Resolved — 2026-10-02\n"
    )
    (wiki / "_relink_suggestions.md").write_text(
        "- [[A]] → [[B]] (score: 0.9) · first seen 2026-10-01\n"
        "- [[B]] → [[A]] (score: 0.9) · first seen 2026-11-07\n"
    )
    found = lint.extra_findings(wiki, TODAY)
    assert [(f.severity, f.message) for f in found] == [
        ("BLOCKER", "open conflict: Conflict: One — 2026-11-01"),
        ("NOTE", "1 suggestion(s) unreviewed for over 14 days"),
    ]


def test_lint_raw_coverage(tmp_path: Path) -> None:
    wiki, raw = tmp_path / "wiki", tmp_path / "raw"
    _page(wiki, "rag/a.md", "A", sources="[data/raw/web/covered.md, data/raw/dirsrc]")
    (raw / "web").mkdir(parents=True)
    (raw / "dirsrc").mkdir()
    for name in ("web/covered.md", "web/loose.md", "dirsrc/inside.md"):
        (raw / name).write_text("x")
    (finding,) = lint.uncovered_raw(wiki, raw)
    assert finding.page == "raw/web" and "1 raw file" in finding.message
    assert "loose.md" in finding.message


def test_lint_empty_sections_and_fix(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    wiki = tmp_path / "wiki"
    page = _page(
        wiki,
        "rag/a.md",
        "A",
        tags="[concept]",
        body="Text.\n\n## Open questions\n\n<!-- add here -->\n\n## Real\n\nkept",
        links="- [[A2]]",
    )
    _page(wiki, "rag/a2.md", "A2", links="- [[A]]")
    assert lint.empty_sections(page.read_text().split("---\n", 2)[2]) != []
    code = lint.main(["--wiki-dir", str(wiki), "--fix", "--today", TODAY.isoformat()])
    out = capsys.readouterr().out
    assert "[FIXED] rag/a.md — added domain tag `rag`" in out
    assert "removed 1 empty placeholder" in out
    text = page.read_text()
    assert "tags: [concept, rag]" in text and "updated: 2026-11-08" in text
    assert "Open questions" not in text and "kept" in text
    assert "empty section" not in out.split("lint:")[0].split("[FIXED]")[-1]
    assert code == 0
    # a second run changes nothing
    lint.main(["--wiki-dir", str(wiki), "--fix", "--today", TODAY.isoformat()])
    assert page.read_text() == text


def test_lint_fix_leaves_private_alone(tmp_path: Path) -> None:
    wiki = tmp_path / "wiki"
    secret = _page(wiki, "private/s.md", "S", tags="[concept]", body="## E\n\n<!-- x -->")
    before = secret.read_text()
    lint.main(["--wiki-dir", str(wiki), "--fix", "--today", TODAY.isoformat()])
    assert secret.read_text() == before


# --- wiki week ----------------------------------------------------------------------------


def test_week_report(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    wiki, tel = tmp_path / "wiki", tmp_path / "tel"
    _page(wiki, "rag/a.md", "A", links="- [[B]]")
    _page(wiki, "rag/b.md", "B", links="- [[A]]")
    (wiki / "_conflicts.md").write_text("## Conflict: X\n\n**Status:** Unresolved\n")
    tel.mkdir()
    (tel / "operations.jsonl").write_text(
        "\n".join(
            json.dumps(r)
            for r in [
                {"month": "2026-08", "count": 4, "ops": {"ingest": 4}},
                {"date": "2026-10-01", "op": "ingest", "detail": "too old"},
                {"date": "2026-11-03", "op": "ingest", "detail": "older in window"},
                {"date": "2026-11-06", "op": "lint", "detail": "newest"},
            ]
        )
        + "\n"
    )
    first = week.report(wiki, tel, TODAY)
    assert first["snapshot_needed"] and first["trend"] == {} and first["latest_row"] is None
    assert [o["detail"] for o in first["added"]] == ["newest", "older in window"]
    assert first["open_conflicts"] == ["Conflict: X"] and first["open_conflicts_match_stats"]
    (tel / "metrics.jsonl").write_text(
        json.dumps({"date": "2026-11-05", "metrics": {"orphan_rate": {"value": 0.5}}}) + "\n"
    )
    second = week.report(wiki, tel, TODAY)
    assert not second["snapshot_needed"] and second["latest_row"] == "2026-11-05"
    assert second["trend"]["orphan_rate"]["before"] == 0.5
    assert second["trend"]["orphan_rate"]["changed"]
    assert week.main(["--wiki-dir", str(wiki), "--telemetry-dir", str(tel)]) == 0
    assert "Wiki week:" in capsys.readouterr().out


# --- ingest pending -----------------------------------------------------------------------


def test_ingest_pending(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    web = tmp_path / "data" / "raw" / "web"
    web.mkdir(parents=True)
    for name in ("a-arxiv-1.md", "b-feed-2.md", "c-arxiv-3.md", "other.md"):
        (web / name).write_text(name)
    mf = tmp_path / "manifest.jsonl"
    with (
        patch.object(manifest_module, "MANIFEST_PATH", mf),
        patch.object(manifest_module, "REPO_ROOT", tmp_path),
    ):
        manifest_module.mark(web / "a-arxiv-1.md", [])
        manifest_module.mark(web / "c-arxiv-3.md", [])
        (web / "c-arxiv-3.md").write_text("edited")
        got = manifest_module.pending(["data/raw/web/*-arxiv-*.md", "data/raw/web/*-feed-*.md"])
        assert got == [
            ("new", "data/raw/web/b-feed-2.md"),
            ("changed", "data/raw/web/c-arxiv-3.md"),
        ]
        assert len(manifest_module.pending(["data/raw/web"])) == 3
        assert manifest_module.main(["pending", "data/raw/web/*-arxiv-*.md", "--count"]) == 0
    assert capsys.readouterr().out.strip() == "1"


def test_cli_dispatches_new_verbs() -> None:
    from librarian.cli import GROUPS

    assert {"sync-check", "compact-signals", "week"} <= set(GROUPS["wiki"])
    assert "pending" in GROUPS["ingest"]
