"""Tests for incremental index rebuild (LIB-124).

Covers:
- Stale detection: unchanged content → _stale_pages returns empty
- New page → embedded and inserted
- Changed page → re-embedded and updated
- Deleted page → removed from index (pages + edges)
- Schema mismatch → _index_needs_rebuild triggers full rebuild
- Migration idempotency: _stale_pages on fresh index returns empty
"""

from __future__ import annotations

from pathlib import Path

import duckdb
import pytest

from app.mcp_server import server

PAGE_TEMPLATE = """---
title: {title}
tags: [{tags}]
summary: {summary}
updated: 2026-08-20
---

# {title}

{body}
"""


def _make_page(wiki_dir: Path, subdir: str, filename: str, title: str, body: str) -> Path:
    d = wiki_dir / subdir
    d.mkdir(parents=True, exist_ok=True)
    p = d / filename
    p.write_text(
        PAGE_TEMPLATE.format(title=title, tags="test", summary=f"Summary of {title}", body=body)
    )
    return p


@pytest.fixture()
def wiki(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Three-page wiki pointing server module at tmp dirs."""
    wiki_dir = tmp_path / "wiki"
    _make_page(wiki_dir, "notes", "alpha.md", "Alpha", "Alpha body content.")
    _make_page(wiki_dir, "notes", "beta.md", "Beta", "Beta body content.")
    _make_page(wiki_dir, "notes", "gamma.md", "Gamma", "Gamma body content.")

    monkeypatch.setattr(server, "WIKI_DIR", wiki_dir)
    monkeypatch.setattr(server, "PRIVATE_DIR", wiki_dir / "private")
    monkeypatch.setattr(server, "DB_PATH", tmp_path / ".idx.duckdb")
    monkeypatch.setattr(server, "HAS_EMBEDDINGS", False)
    return wiki_dir


def _fresh_con() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(":memory:")


# ---------------------------------------------------------------------------
# 1. Stale detection: unchanged content → _stale_pages returns empty
# ---------------------------------------------------------------------------


def test_stale_pages_empty_after_fresh_build(wiki: Path) -> None:
    con = _fresh_con()
    server.build_index(con)
    stale = server._stale_pages(con)
    assert stale == [], f"expected no stale pages after fresh build, got {stale}"
    con.close()


def test_stale_pages_detects_single_edit(wiki: Path) -> None:
    con = _fresh_con()
    server.build_index(con)

    alpha = wiki / "notes" / "alpha.md"
    original = alpha.read_text()
    alpha.write_text(original + "\nExtra line added.")

    stale = server._stale_pages(con)
    stale_names = [Path(p).name for p in stale]
    assert stale_names == ["alpha.md"], (
        f"only alpha.md was changed; stale_pages returned {stale_names}"
    )
    con.close()


# ---------------------------------------------------------------------------
# 2. New page → inserted into index on incremental update
# ---------------------------------------------------------------------------


def test_new_page_inserted_incrementally(wiki: Path) -> None:
    con = _fresh_con()
    server.build_index(con)

    # Add a fourth page
    _make_page(wiki, "notes", "delta.md", "Delta", "Delta body content.")

    server.build_index(con)  # should take incremental path

    paths = {r[0] for r in con.execute("SELECT path FROM pages").fetchall()}
    assert any("delta.md" in p for p in paths), (
        f"delta.md not found in index after incremental build; paths={paths}"
    )
    con.close()


# ---------------------------------------------------------------------------
# 3. Changed page → re-embedded (encode called with exactly 1 text)
# ---------------------------------------------------------------------------


def test_changed_page_encode_called_once(wiki: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Editing one page triggers encode on that page only, not the full corpus."""
    encode_inputs: list[list[str]] = []

    class _FakeModel:
        def encode(self, texts: list[str], **kwargs: object) -> list[list[float]]:
            encode_inputs.append(list(texts))
            return [[0.1] * 384 for _ in texts]

    fake_model = _FakeModel()
    monkeypatch.setattr(server, "HAS_EMBEDDINGS", True)
    # _get_emb_model() is the single seam for the embedding model
    monkeypatch.setattr(server, "_get_emb_model", lambda: fake_model)

    con = _fresh_con()
    server.build_index(con)  # full rebuild — encodes all 3 pages
    encode_inputs.clear()  # reset counter

    alpha = wiki / "notes" / "alpha.md"
    alpha.write_text(alpha.read_text() + "\nChanged content.")

    server.build_index(con)  # incremental — should call encode once with 1 text

    assert len(encode_inputs) == 1, (
        f"expected 1 encode call for 1 changed page, got {len(encode_inputs)}"
    )
    assert len(encode_inputs[0]) == 1, (
        f"expected encode called with 1 text, got {len(encode_inputs[0])}"
    )
    con.close()


def test_changed_page_content_hash_updated(wiki: Path) -> None:
    con = _fresh_con()
    server.build_index(con)

    alpha = wiki / "notes" / "alpha.md"
    old_hash = con.execute(
        "SELECT content_hash FROM pages WHERE path = ?", [str(alpha)]
    ).fetchone()[0]

    alpha.write_text(alpha.read_text() + "\nChanged content.")
    server.build_index(con)

    new_hash = con.execute(
        "SELECT content_hash FROM pages WHERE path = ?", [str(alpha)]
    ).fetchone()[0]
    assert old_hash != new_hash, "content_hash should change after page edit"
    con.close()


# ---------------------------------------------------------------------------
# 4. Deleted page → removed from pages (and edges)
# ---------------------------------------------------------------------------


def test_deleted_page_pruned_from_index(wiki: Path) -> None:
    con = _fresh_con()
    server.build_index(con)

    gamma = wiki / "notes" / "gamma.md"
    gamma.unlink()

    server.build_index(con)

    paths = {r[0] for r in con.execute("SELECT path FROM pages").fetchall()}
    assert not any("gamma.md" in p for p in paths), (
        f"gamma.md should be pruned after deletion; paths={paths}"
    )
    con.close()


def test_deleted_page_edges_pruned(wiki: Path) -> None:
    """Edges referencing a deleted page are removed."""
    con = _fresh_con()
    server.build_index(con)

    gamma = wiki / "notes" / "gamma.md"
    gamma_path = str(gamma)

    # Manually insert a fake edge so we can assert it's removed
    con.execute(
        "INSERT INTO edges VALUES (?, ?, ?)",
        [gamma_path, str(wiki / "notes" / "alpha.md"), "extends"],
    )

    gamma.unlink()
    server.build_index(con)

    edges = con.execute(
        "SELECT * FROM edges WHERE source_path = ? OR target_path = ?",
        [gamma_path, gamma_path],
    ).fetchall()
    assert edges == [], f"edges for deleted page should be pruned; got {edges}"
    con.close()


# ---------------------------------------------------------------------------
# 5. Schema mismatch → _index_needs_rebuild returns True; False after rebuild
# ---------------------------------------------------------------------------


def test_schema_mismatch_triggers_full_rebuild(wiki: Path) -> None:
    """A stale schema_version forces _index_needs_rebuild to return True."""
    con = _fresh_con()
    # Build with old schema version in meta
    con.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, val TEXT)")
    con.execute("INSERT INTO meta VALUES ('schema_version', '6')")
    con.execute("INSERT INTO meta VALUES ('built_at', '1000000')")

    assert server._index_needs_rebuild(con) is True, (
        "mismatched schema_version should trigger rebuild"
    )

    # After a real build, it should be False
    server.build_index(con)
    assert server._index_needs_rebuild(con) is False, (
        "_index_needs_rebuild should be False after build_index"
    )
    con.close()


def test_missing_index_triggers_rebuild(wiki: Path) -> None:
    """An empty connection (no meta table) triggers _index_needs_rebuild."""
    con = _fresh_con()
    assert server._index_needs_rebuild(con) is True
    con.close()


# ---------------------------------------------------------------------------
# 6. Migration idempotency: calling build_index twice on unchanged wiki is a no-op
# ---------------------------------------------------------------------------


def test_build_index_idempotent(wiki: Path) -> None:
    con = _fresh_con()
    server.build_index(con)

    count_before = con.execute("SELECT COUNT(*) FROM pages").fetchone()[0]
    server.build_index(con)  # second call — nothing changed
    count_after = con.execute("SELECT COUNT(*) FROM pages").fetchone()[0]

    assert count_before == count_after == 3, (
        f"idempotent call should leave page count at 3, got before={count_before} after={count_after}"
    )
    con.close()


# ---------------------------------------------------------------------------
# 7. content_hash column present in pages table
# ---------------------------------------------------------------------------


def test_pages_table_has_content_hash_column(wiki: Path) -> None:
    con = _fresh_con()
    server.build_index(con)

    # DuckDB PRAGMA table_info returns (cid, name, type, notnull, dflt_value, pk)
    cols = {row[1] for row in con.execute("PRAGMA table_info('pages')").fetchall()}
    assert "content_hash" in cols, f"content_hash column missing from pages; columns={cols}"
    con.close()


def test_content_hash_populated_for_all_pages(wiki: Path) -> None:
    con = _fresh_con()
    server.build_index(con)

    null_hashes = con.execute("SELECT path FROM pages WHERE content_hash IS NULL").fetchall()
    assert null_hashes == [], f"some pages have NULL content_hash: {null_hashes}"
    con.close()
