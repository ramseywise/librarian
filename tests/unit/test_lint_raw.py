"""Unit tests for core/lint_raw.py — filename convention validation."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[2]))

import core.lint_raw as lint_module
from core.lint_raw import DATE_SLUG_RE, EXEMPT_PREFIXES, check_dir, main

# ---------------------------------------------------------------------------
# DATE_SLUG_RE pattern
# ---------------------------------------------------------------------------


class TestDateSlugRegex:
    def test_valid_date_slug(self) -> None:
        assert DATE_SLUG_RE.match("2026-07-25-my-note.md")

    def test_valid_with_numbers_in_slug(self) -> None:
        assert DATE_SLUG_RE.match("2026-01-01-note-v2.md")

    def test_rejects_uppercase_in_slug(self) -> None:
        assert not DATE_SLUG_RE.match("2026-07-25-My-Note.md")

    def test_rejects_missing_date(self) -> None:
        assert not DATE_SLUG_RE.match("my-note.md")

    def test_rejects_underscores_in_slug(self) -> None:
        assert not DATE_SLUG_RE.match("2026-07-25-my_note.md")

    def test_rejects_invalid_month_00(self) -> None:
        assert not DATE_SLUG_RE.match("2026-00-01-note.md")

    def test_rejects_invalid_month_13(self) -> None:
        assert not DATE_SLUG_RE.match("2026-13-01-note.md")

    def test_rejects_invalid_day_00(self) -> None:
        assert not DATE_SLUG_RE.match("2026-07-00-note.md")

    def test_rejects_invalid_day_32(self) -> None:
        assert not DATE_SLUG_RE.match("2026-07-32-note.md")

    def test_rejects_spaces_in_slug(self) -> None:
        assert not DATE_SLUG_RE.match("2026-07-25-my note.md")

    def test_rejects_non_md_extension(self) -> None:
        assert not DATE_SLUG_RE.match("2026-07-25-note.txt")

    def test_boundary_month_12(self) -> None:
        assert DATE_SLUG_RE.match("2026-12-31-end-of-year.md")

    def test_boundary_month_01(self) -> None:
        assert DATE_SLUG_RE.match("2026-01-01-new-year.md")


# ---------------------------------------------------------------------------
# check_dir()
# ---------------------------------------------------------------------------


class TestCheckDir:
    def test_valid_file_no_error_no_warning(self, tmp_path: Path) -> None:
        raw = tmp_path / "raw"
        raw.mkdir()
        (raw / "2026-07-25-valid-note.md").write_text("content")
        errors: list = []
        warnings: list = []
        with patch.object(lint_module, "ROOT", raw):
            check_dir(raw, errors, warnings)
        assert errors == []
        assert warnings == []

    def test_missing_date_prefix_is_error(self, tmp_path: Path) -> None:
        raw = tmp_path / "raw"
        raw.mkdir()
        (raw / "some-note-without-date.md").write_text("content")
        errors: list = []
        warnings: list = []
        with patch.object(lint_module, "ROOT", raw):
            check_dir(raw, errors, warnings)
        assert len(errors) == 1
        assert "missing YYYY-MM-DD- date prefix" in errors[0][1]

    def test_date_with_uppercase_slug_is_warning(self, tmp_path: Path) -> None:
        raw = tmp_path / "raw"
        raw.mkdir()
        (raw / "2026-07-25-MyNote.md").write_text("content")
        errors: list = []
        warnings: list = []
        with patch.object(lint_module, "ROOT", raw):
            check_dir(raw, errors, warnings)
        assert len(warnings) == 1
        assert "uppercase" in warnings[0][1]

    def test_multiple_files_accumulate(self, tmp_path: Path) -> None:
        raw = tmp_path / "raw"
        raw.mkdir()
        (raw / "2026-01-01-good.md").write_text("ok")
        (raw / "bad-no-date.md").write_text("bad")
        (raw / "2026-07-25-BadCase.md").write_text("warn")
        errors: list = []
        warnings: list = []
        with patch.object(lint_module, "ROOT", raw):
            check_dir(raw, errors, warnings)
        assert len(errors) == 1
        assert len(warnings) == 1

    def test_recursive_scan(self, tmp_path: Path) -> None:
        raw = tmp_path / "raw"
        sub = raw / "sub"
        sub.mkdir(parents=True)
        (sub / "no-date-here.md").write_text("bad")
        errors: list = []
        warnings: list = []
        with patch.object(lint_module, "ROOT", raw):
            check_dir(raw, errors, warnings)
        assert len(errors) == 1


# ---------------------------------------------------------------------------
# main() integration
# ---------------------------------------------------------------------------


class TestMain:
    def test_returns_0_for_clean_dir(self, tmp_path: Path) -> None:
        raw = tmp_path / "raw"
        web = raw / "web"
        web.mkdir(parents=True)
        (web / "2026-07-25-clean-note.md").write_text("content")

        with patch.object(lint_module, "ROOT", raw):
            result = main()

        assert result == 0

    def test_returns_1_for_error_files(self, tmp_path: Path) -> None:
        raw = tmp_path / "raw"
        web = raw / "web"
        web.mkdir(parents=True)
        (web / "bad-no-date.md").write_text("content")

        with patch.object(lint_module, "ROOT", raw):
            result = main()

        assert result == 1

    def test_returns_0_for_warnings_only(self, tmp_path: Path) -> None:
        raw = tmp_path / "raw"
        web = raw / "web"
        web.mkdir(parents=True)
        # Has date prefix but uppercase slug — warning, not error
        (web / "2026-07-25-MyNote.md").write_text("content")

        with patch.object(lint_module, "ROOT", raw):
            result = main()

        assert result == 0

    def test_exempt_dirs_not_checked(self, tmp_path: Path) -> None:
        raw = tmp_path / "raw"
        for exempt in EXEMPT_PREFIXES:
            exempt_dir = raw / exempt
            exempt_dir.mkdir(parents=True)
            (exempt_dir / "no-date-no-problem.md").write_text("content")

        with patch.object(lint_module, "ROOT", raw):
            result = main()

        # No non-exempt directories with errors — should be clean
        assert result == 0

    def test_missing_raw_dir_returns_1(self, tmp_path: Path) -> None:
        nonexistent = tmp_path / "does-not-exist"
        with patch.object(lint_module, "ROOT", nonexistent):
            result = main()
        assert result == 1

    def test_mixed_exempt_and_non_exempt(self, tmp_path: Path) -> None:
        raw = tmp_path / "raw"
        # Exempt dir with bad file — should be ignored
        repos = raw / "repos"
        repos.mkdir(parents=True)
        (repos / "bad-file.md").write_text("content")
        # Non-exempt dir with clean file
        web = raw / "web"
        web.mkdir(parents=True)
        (web / "2026-07-25-good.md").write_text("content")

        with patch.object(lint_module, "ROOT", raw):
            result = main()

        assert result == 0
