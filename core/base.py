"""ScraperBase — shared ABC for all core/ ETL scrapers.

Provides:
  - source_name / output_dir attributes
  - structlog setup (via app.log_config.configure_logging)
  - ManifestSession integration
  - dry-run guard
  - cli() classmethod: argparse boilerplate + instantiation + run

Subclass protocol:
    class MyScraper(ScraperBase):
        source_name = "my-source"
        output_dir = REPO_ROOT / "raw" / "my-source"

        def run(self, dry_run: bool = False) -> list[Path]:
            ...

        # Optional: add extra CLI arguments
        @classmethod
        def _add_args(cls, parser: argparse.ArgumentParser) -> None:
            parser.add_argument("--extra-flag", ...)

        # Optional: build instance from parsed args (override if constructor needs extra args)
        @classmethod
        def _from_args(cls, args: argparse.Namespace) -> "MyScraper":
            return cls(extra_flag=args.extra_flag)
"""

from __future__ import annotations

import argparse
from abc import ABC, abstractmethod
from pathlib import Path

import structlog

from app.log_config import configure_logging
from core.manifest import ManifestSession

REPO_ROOT = Path(__file__).parent.parent
log = structlog.get_logger()


class ScraperBase(ABC):
    """Base class for all core/ ETL scrapers."""

    source_name: str = ""  # override in subclass
    output_dir: Path = REPO_ROOT / "raw"  # override in subclass

    @abstractmethod
    def run(self, dry_run: bool = False) -> list[Path]:
        """Run the scraper. Returns list of paths written (or that would be written)."""

    def manifest_session(self) -> ManifestSession:
        """Return a fresh ManifestSession for batch ingest tracking."""
        return ManifestSession()

    # ------------------------------------------------------------------
    # CLI entry point
    # ------------------------------------------------------------------

    @classmethod
    def _add_args(cls, parser: argparse.ArgumentParser) -> None:
        """Hook: add scraper-specific arguments to the parser."""
        return  # default no-op; subclasses override to add CLI args

    @classmethod
    def _from_args(cls, args: argparse.Namespace) -> ScraperBase:
        """Hook: construct the scraper from parsed args. Override if needed."""
        return cls()

    @classmethod
    def cli(cls, description: str | None = None) -> None:
        """Parse args, configure logging, run the scraper."""
        configure_logging()
        parser = argparse.ArgumentParser(description=description or f"{cls.source_name} scraper")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would be written, don't write",
        )
        cls._add_args(parser)
        args = parser.parse_args()

        scraper = cls._from_args(args)
        written = scraper.run(dry_run=args.dry_run)

        prefix = "[dry-run] " if args.dry_run else ""
        source = cls.source_name or cls.__name__
        print(f"\n{prefix}{source}: {len(written)} file(s) → {scraper.output_dir}")
