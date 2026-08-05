"""Unit tests for core/manifest.py."""

from __future__ import annotations

import hashlib
import json
import sys
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[2]))

import core.manifest as manifest_module
from core.manifest import (
    ManifestSession,
    check,
    coverage_gaps,
    file_hash,
    mark,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@contextmanager
def _patch_manifest(tmp_path: Path) -> Generator[None]:
    """Patch MANIFEST_PATH and REPO_ROOT to tmp_path for isolated tests."""
    with (
        patch.object(manifest_module, "MANIFEST_PATH", tmp_path / "manifest.jsonl"),
        patch.object(manifest_module, "REPO_ROOT", tmp_path),
    ):
        yield


def _make_manifest(tmp_path: Path, entries: list[dict]) -> Path:
    mf = tmp_path / "manifest.jsonl"
    lines = [json.dumps(e) for e in entries]
    mf.write_text("\n".join(lines) + "\n")
    return mf


def _make_raw_file(
    tmp_path: Path, name: str = "2026-01-01-note.md", content: str = "hello"
) -> Path:
    f = tmp_path / name
    f.write_text(content)
    return f


# ---------------------------------------------------------------------------
# file_hash
# ---------------------------------------------------------------------------


class TestFileHash:
    def test_deterministic(self, tmp_path: Path) -> None:
        f = _make_raw_file(tmp_path)
        h1 = file_hash(f)
        h2 = file_hash(f)
        assert h1 == h2

    def test_format_sha256_prefix(self, tmp_path: Path) -> None:
        f = _make_raw_file(tmp_path)
        h = file_hash(f)
        assert h.startswith("sha256:")

    def test_hash_length(self, tmp_path: Path) -> None:
        f = _make_raw_file(tmp_path)
        h = file_hash(f)
        # "sha256:" + 16 hex chars
        assert len(h) == len("sha256:") + 16

    def test_different_content_different_hash(self, tmp_path: Path) -> None:
        f1 = tmp_path / "a.md"
        f1.write_text("aaa")
        f2 = tmp_path / "b.md"
        f2.write_text("bbb")
        assert file_hash(f1) != file_hash(f2)

    def test_matches_manual_sha256(self, tmp_path: Path) -> None:
        content = b"deterministic content"
        f = tmp_path / "test.md"
        f.write_bytes(content)
        expected_hex = hashlib.sha256(content).hexdigest()[:16]
        assert file_hash(f) == f"sha256:{expected_hex}"


# ---------------------------------------------------------------------------
# check()
# ---------------------------------------------------------------------------


class TestCheck:
    def test_new_file_returns_true(self, tmp_path: Path) -> None:
        raw_file = _make_raw_file(tmp_path)
        with _patch_manifest(tmp_path):
            needs, reason = check(raw_file)
        assert needs is True
        assert "not yet ingested" in reason

    def test_already_ingested_unchanged_returns_false(self, tmp_path: Path) -> None:
        raw_file = _make_raw_file(tmp_path, content="stable content")
        rel = str(raw_file.relative_to(tmp_path))
        entry = {
            "path": rel,
            "hash": file_hash(raw_file),
            "ingested_at": "2026-01-01",
            "wiki_pages": [],
        }
        _make_manifest(tmp_path, [entry])

        with _patch_manifest(tmp_path):
            needs, reason = check(raw_file)
        assert needs is False
        assert "already ingested" in reason

    def test_changed_file_returns_true(self, tmp_path: Path) -> None:
        raw_file = _make_raw_file(tmp_path, content="original")
        rel = str(raw_file.relative_to(tmp_path))
        entry = {
            "path": rel,
            "hash": "sha256:aaaaaaaaaaaaaaaa",  # stale hash
            "ingested_at": "2026-01-01",
            "wiki_pages": [],
        }
        _make_manifest(tmp_path, [entry])

        with _patch_manifest(tmp_path):
            needs, reason = check(raw_file)
        assert needs is True
        assert "changed since" in reason

    def test_nonexistent_file_returns_false(self, tmp_path: Path) -> None:
        ghost = tmp_path / "ghost.md"
        with _patch_manifest(tmp_path):
            needs, reason = check(ghost)
        assert needs is False
        assert "not found" in reason


# ---------------------------------------------------------------------------
# mark()
# ---------------------------------------------------------------------------


class TestMark:
    def test_records_entry(self, tmp_path: Path) -> None:
        raw_file = _make_raw_file(tmp_path)
        rel = str(raw_file.relative_to(tmp_path))

        with _patch_manifest(tmp_path):
            mark(raw_file, wiki_pages=["data/wiki/rag/page.md"])

        mf = tmp_path / "manifest.jsonl"
        assert mf.exists()
        entry = json.loads(mf.read_text().strip())
        assert entry["path"] == rel
        assert entry["wiki_pages"] == ["data/wiki/rag/page.md"]
        assert entry["hash"].startswith("sha256:")

    def test_overwrites_existing_entry(self, tmp_path: Path) -> None:
        raw_file = _make_raw_file(tmp_path)
        rel = str(raw_file.relative_to(tmp_path))
        old_entry = {
            "path": rel,
            "hash": "sha256:aaaaaaaaaaaaaaaa",
            "ingested_at": "2025-01-01",
            "wiki_pages": ["data/wiki/old.md"],
        }
        _make_manifest(tmp_path, [old_entry])

        with _patch_manifest(tmp_path):
            mark(raw_file, wiki_pages=["data/wiki/new.md"])

        lines = (tmp_path / "manifest.jsonl").read_text().strip().splitlines()
        entries = [json.loads(line) for line in lines]
        assert len(entries) == 1
        assert entries[0]["wiki_pages"] == ["data/wiki/new.md"]


# ---------------------------------------------------------------------------
# ManifestSession
# ---------------------------------------------------------------------------


class TestManifestSession:
    def test_check_new_file(self, tmp_path: Path) -> None:
        raw_file = _make_raw_file(tmp_path)

        with _patch_manifest(tmp_path), ManifestSession() as ms:
            needs, _reason = ms.check(raw_file)

        assert needs is True

    def test_mark_then_check_returns_false(self, tmp_path: Path) -> None:
        raw_file = _make_raw_file(tmp_path)

        with _patch_manifest(tmp_path), ManifestSession() as ms:
            needs, _ = ms.check(raw_file)
            assert needs is True
            ms.mark(raw_file, wiki_pages=["data/wiki/page.md"])
            needs2, _ = ms.check(raw_file)
            assert needs2 is False

    def test_saves_on_exit(self, tmp_path: Path) -> None:
        raw_file = _make_raw_file(tmp_path)

        with _patch_manifest(tmp_path), ManifestSession() as ms:
            ms.mark(raw_file, wiki_pages=["data/wiki/page.md"])

        mf = tmp_path / "manifest.jsonl"
        assert mf.exists()
        data = json.loads(mf.read_text().strip())
        assert data["wiki_pages"] == ["data/wiki/page.md"]

    def test_no_save_when_not_dirty(self, tmp_path: Path) -> None:
        mf = tmp_path / "manifest.jsonl"
        mf.write_text("")  # empty but exists

        with (
            patch.object(manifest_module, "MANIFEST_PATH", mf),
            patch.object(manifest_module, "REPO_ROOT", tmp_path),
            ManifestSession(),
        ):
            pass  # no mark calls

        # File should remain as-is (empty), not overwritten
        assert mf.read_text() == ""

    def test_batch_marks_multiple_files(self, tmp_path: Path) -> None:
        files = []
        for i in range(3):
            f = tmp_path / f"2026-01-0{i + 1}-note.md"
            f.write_text(f"content {i}")
            files.append(f)

        with _patch_manifest(tmp_path), ManifestSession() as ms:
            for f in files:
                ms.mark(f, wiki_pages=[])

        mf = tmp_path / "manifest.jsonl"
        lines = [line for line in mf.read_text().strip().splitlines() if line]
        assert len(lines) == 3


# ---------------------------------------------------------------------------
# coverage_gaps()
# ---------------------------------------------------------------------------


class TestCoverageGaps:
    def test_finds_uningested_files(self, tmp_path: Path) -> None:
        raw_dir = tmp_path / "raw" / "web"
        raw_dir.mkdir(parents=True)
        f1 = raw_dir / "2026-01-01-note.md"
        f1.write_text("content")

        with _patch_manifest(tmp_path):
            gaps = coverage_gaps(tmp_path / "raw")

        assert any("2026-01-01-note.md" in g["path"] for g in gaps)

    def test_ingested_files_not_in_gaps(self, tmp_path: Path) -> None:
        raw_dir = tmp_path / "raw" / "web"
        raw_dir.mkdir(parents=True)
        f1 = raw_dir / "2026-01-01-note.md"
        f1.write_text("content")
        rel = str(f1.relative_to(tmp_path))
        entry = {
            "path": rel,
            "hash": file_hash(f1),
            "ingested_at": "2026-01-01",
            "wiki_pages": [],
        }
        _make_manifest(tmp_path, [entry])

        with _patch_manifest(tmp_path):
            gaps = coverage_gaps(tmp_path / "raw")

        assert not any("2026-01-01-note.md" in g["path"] for g in gaps)

    def test_empty_raw_dir_no_gaps(self, tmp_path: Path) -> None:
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()

        with _patch_manifest(tmp_path):
            gaps = coverage_gaps(tmp_path / "raw")

        assert gaps == []
