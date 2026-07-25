"""Seed raw/playground-docs/ from the playground repo's .claude/docs/.

Copies all .md files from playground/.claude/docs/ into raw/playground-docs/,
preserving the directory structure. Run once on first setup.

Usage:
    uv run python core/seed_from_playground.py
    uv run python core/seed_from_playground.py --playground /custom/path/to/playground
    uv run python core/seed_from_playground.py --dry-run
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import structlog
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

from core.base import REPO_ROOT, ScraperBase

load_dotenv()
log = structlog.get_logger()

RAW_PLAYGROUND = REPO_ROOT / "raw" / "playground-docs"


class Settings(BaseSettings):
    playground_path: Path = Path("~/Workspace/playground").expanduser()


class PlaygroundScraper(ScraperBase):
    source_name = "seed-playground"
    output_dir = RAW_PLAYGROUND

    def __init__(self, playground_path: Path | None = None) -> None:
        if playground_path is not None:
            self._playground_path = playground_path
        else:
            self._playground_path = Settings().playground_path

    def run(self, dry_run: bool = False) -> list[Path]:
        docs_dir = self._playground_path / ".claude" / "docs"

        if not docs_dir.exists():
            print(f"Error: {docs_dir} does not exist. Check PLAYGROUND_PATH in .env.")
            return []

        md_files = list(docs_dir.rglob("*.md"))
        log.info("found_docs", count=len(md_files), source=str(docs_dir))

        written: list[Path] = []
        for src in md_files:
            rel = src.relative_to(docs_dir)
            dest = self.output_dir / rel
            if dry_run:
                print(f"  [would copy] {src} → {dest}")
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
                log.info("copied", src=str(src), dest=str(dest))
            written.append(dest)

        if not dry_run:
            print(f"\nCopied {len(written)} files to {self.output_dir}/")
            print("\nNext: run /ingest raw/playground-docs/ in Claude Code to compile into wiki.")

        return written

    @classmethod
    def _add_args(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--playground",
            type=Path,
            default=None,
            metavar="PATH",
            help="Path to playground repo (default: PLAYGROUND_PATH env or ~/Workspace/playground)",
        )

    @classmethod
    def _from_args(cls, args: argparse.Namespace) -> PlaygroundScraper:
        return cls(playground_path=args.playground)


if __name__ == "__main__":
    PlaygroundScraper.cli(description="Seed raw/playground-docs/ from playground repo")
