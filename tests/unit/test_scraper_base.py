"""Unit tests for core/base.py — ScraperBase ABC."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parents[2]))

from core.base import ScraperBase
from core.manifest import ManifestSession

# ---------------------------------------------------------------------------
# Concrete minimal subclass for testing
# ---------------------------------------------------------------------------


class StubScraper(ScraperBase):
    source_name = "stub"
    output_dir = Path("/tmp/stub-output")

    def __init__(self, written: list[Path] | None = None) -> None:
        self._written = written or []

    def run(self, dry_run: bool = False) -> list[Path]:
        return self._written


class DryRunScraper(ScraperBase):
    source_name = "dry-run-test"
    output_dir = Path("/tmp/dry-run-output")

    def __init__(self, tmp_path: Path) -> None:
        self._tmp = tmp_path
        self.side_effects: list[str] = []

    def run(self, dry_run: bool = False) -> list[Path]:
        would_write = self._tmp / "output.md"
        if not dry_run:
            # Real run — produce side effects
            self.side_effects.append("wrote")
            would_write.write_text("content")
        return [would_write]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestScraperBaseManifestSession:
    def test_manifest_session_returns_manifest_session(self) -> None:
        scraper = StubScraper()
        session = scraper.manifest_session()
        assert isinstance(session, ManifestSession)

    def test_each_call_returns_fresh_session(self) -> None:
        scraper = StubScraper()
        s1 = scraper.manifest_session()
        s2 = scraper.manifest_session()
        assert s1 is not s2


class TestScraperBaseDryRun:
    def test_dry_run_true_produces_no_side_effects(self, tmp_path: Path) -> None:
        scraper = DryRunScraper(tmp_path)
        result = scraper.run(dry_run=True)

        assert scraper.side_effects == []
        assert not (tmp_path / "output.md").exists()
        # Still returns the paths that would have been written
        assert len(result) == 1

    def test_dry_run_false_produces_side_effects(self, tmp_path: Path) -> None:
        scraper = DryRunScraper(tmp_path)
        scraper.run(dry_run=False)

        assert "wrote" in scraper.side_effects
        assert (tmp_path / "output.md").exists()


class TestScraperBaseCli:
    def test_cli_runs_with_no_args(self) -> None:
        """cli() parses [] args, instantiates, calls run(), prints summary."""
        with (
            patch("core.base.configure_logging"),
            patch.object(StubScraper, "run", return_value=[]) as mock_run,
            patch("sys.argv", ["prog"]),
        ):
            StubScraper.cli(description="test scraper")
            mock_run.assert_called_once_with(dry_run=False)

    def test_cli_passes_dry_run_flag(self) -> None:
        with (
            patch("core.base.configure_logging"),
            patch.object(StubScraper, "run", return_value=[Path("/tmp/x.md")]) as mock_run,
            patch("sys.argv", ["prog", "--dry-run"]),
            patch("builtins.print") as mock_print,
        ):
            StubScraper.cli()
            mock_run.assert_called_once_with(dry_run=True)
            # Summary line should carry the [dry-run] prefix
            printed = " ".join(str(a) for call in mock_print.call_args_list for a in call.args)
            assert "[dry-run]" in printed

    def test_cli_uses_source_name_in_summary(self) -> None:
        with (
            patch("core.base.configure_logging"),
            patch.object(StubScraper, "run", return_value=[]),
            patch("sys.argv", ["prog"]),
            patch("builtins.print") as mock_print,
        ):
            StubScraper.cli()
            printed = " ".join(str(a) for call in mock_print.call_args_list for a in call.args)
            assert "stub" in printed

    def test_cli_custom_description_used_in_parser(self) -> None:
        """cli() forwards description to ArgumentParser — smoke-test no crash."""
        with (
            patch("core.base.configure_logging"),
            patch.object(StubScraper, "run", return_value=[]),
            patch("sys.argv", ["prog"]),
        ):
            StubScraper.cli(description="Custom description")

    def test_from_args_default_constructs_instance(self) -> None:
        args = MagicMock()
        instance = StubScraper._from_args(args)
        assert isinstance(instance, StubScraper)
