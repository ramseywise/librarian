"""Seed raw/playground-docs/ from the playground repo's .claude/docs/.

Copies all .md files from playground/.claude/docs/ into raw/playground-docs/,
preserving the directory structure. Run once on first setup.

Usage:
    uv run python scripts/seed_from_playground.py
    uv run python scripts/seed_from_playground.py /custom/path/to/playground
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import structlog
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()
log = structlog.get_logger()

RAW_PLAYGROUND = Path("raw/playground-docs")


class Settings(BaseSettings):
    playground_path: Path = Path("~/Workspace/playground").expanduser()


def main() -> None:
    settings = Settings()

    if len(sys.argv) > 1:
        source_root = Path(sys.argv[1])
    else:
        source_root = settings.playground_path

    docs_dir = source_root / ".claude" / "docs"

    if not docs_dir.exists():
        print(f"Error: {docs_dir} does not exist. Check PLAYGROUND_PATH in .env.")
        sys.exit(1)

    md_files = list(docs_dir.rglob("*.md"))
    log.info("found_docs", count=len(md_files), source=str(docs_dir))

    copied = []
    for src in md_files:
        rel = src.relative_to(docs_dir)
        dest = RAW_PLAYGROUND / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        copied.append(dest)
        log.info("copied", src=str(src), dest=str(dest))

    print(f"\nCopied {len(copied)} files to {RAW_PLAYGROUND}/")
    print(
        "\nNext: run /ingest raw/playground-docs/ in Claude Code to compile into wiki."
    )


if __name__ == "__main__":
    main()
