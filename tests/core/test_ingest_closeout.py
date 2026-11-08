"""librarian.ingest.closeout: pages per raw source and the flags a batch close-out needs."""

from __future__ import annotations

from pathlib import Path

import pytest

from librarian.ingest import closeout as mod
from librarian.ingest import manifest
from librarian.ingest.closeout import closeout


def _page(path: Path, sources: list[Path], body: str = "Body.") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    listed = "\n".join(f"  - {s}" for s in sources)
    path.write_text(f"---\ntitle: {path.stem}\nsources:\n{listed}\n---\n\n# T\n\n{body}\n")
    return path


@pytest.fixture
def wiki(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    raw = tmp_path / "raw"
    raw.mkdir()
    clean = raw / "clean.md"
    clean.write_text("CLAIMS: a number.\n")
    odd = raw / "odd.md"
    odd.write_text("INTERNAL INCONSISTENCIES: Table 2 and the text disagree.\n")
    orphan = raw / "orphan.md"
    orphan.write_text("Nothing cites this.\n")
    wiki_dir = tmp_path / "wiki"
    _page(wiki_dir / "eval" / "a.md", [clean, odd], "Text.\n\n## Limits\n\nTable 2 disagrees.")
    _page(wiki_dir / "eval" / "b.md", [odd])
    _page(wiki_dir / "private" / "p.md", [clean])
    (wiki_dir / "_index.md").write_text(f"---\nsources:\n  - {orphan}\n---\n")
    return wiki_dir, clean, odd, orphan


def test_maps_sources_to_public_pages(wiki: tuple[Path, Path, Path, Path]) -> None:
    wiki_dir, clean, odd, orphan = wiki
    by_source = {Path(r.source).name: r for r in closeout([clean, odd, orphan], wiki_dir)}
    assert [Path(p).name for p in by_source["clean.md"].pages] == ["a.md"]
    assert len(by_source["clean.md"].private_pages) == 1
    assert sorted(Path(p).name for p in by_source["odd.md"].pages) == ["a.md", "b.md"]
    assert by_source["orphan.md"].pages == []  # `_index.md` does not count


def test_flags_inconsistent_extraction_and_missing_limits(
    wiki: tuple[Path, Path, Path, Path],
) -> None:
    wiki_dir, clean, odd, _ = wiki
    reports = {Path(r.source).name: r for r in closeout([clean, odd], wiki_dir)}
    assert not reports["clean.md"].inconsistent
    assert reports["odd.md"].inconsistent
    assert [Path(p).name for p in reports["odd.md"].pages_without_limits] == ["b.md"]


def test_main_exits_1_on_unmapped_and_writes_page_list(
    wiki: tuple[Path, Path, Path, Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    wiki_dir, clean, odd, orphan = wiki
    monkeypatch.setattr(mod, "WIKI_DIR", wiki_dir)
    listing = tmp_path / "batch.paths"
    listing.write_text(f"{clean}\ttitle\n\n{odd}\n")
    out = tmp_path / "pages.txt"
    assert mod.main(["--from", str(listing), "--pages-out", str(out)]) == 0
    assert sorted(Path(p).name for p in out.read_text().split()) == ["a.md", "b.md"]
    assert "p.md" not in capsys.readouterr().out  # private pages are counted, not named
    assert mod.main([str(orphan)]) == 1
    assert "NO PAGES" in capsys.readouterr().out


def test_mark_records_sources_with_pages_only(
    wiki: tuple[Path, Path, Path, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    wiki_dir, clean, _, orphan = wiki
    monkeypatch.setattr(mod, "WIKI_DIR", wiki_dir)
    monkeypatch.setattr(manifest, "MANIFEST_PATH", tmp_path / "manifest.jsonl")
    monkeypatch.setattr(manifest, "REPO_ROOT", tmp_path)
    assert mod.main([str(clean), str(orphan), "--mark"]) == 1
    entries = manifest._load()
    assert list(entries) == ["raw/clean.md"]
    assert sorted(Path(p).name for p in entries["raw/clean.md"]["wiki_pages"]) == ["a.md", "p.md"]
