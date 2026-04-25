"""Scrape .claude/ folders from all workspace projects → raw/claude-docs/

Collects markdown files from .claude/ subdirectories across:
  - ~/.claude/           (user-level CLAUDE.md, commands/, scripts/)
  - ~/workspace/*/      (per-project docs/, skills/, agents/, sessions/, memory/)

Writes to raw/claude-docs/{project-name}/{subdir}/{file}.md preserving structure.
Idempotent: copies are overwritten on each run (source is always current).

Usage:
    uv run python scripts/scrape_claude_docs.py
    uv run python scripts/scrape_claude_docs.py --dry-run
    uv run python scripts/scrape_claude_docs.py --workspace /custom/path
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import structlog
from dotenv import load_dotenv

load_dotenv()
log = structlog.get_logger()

DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent / "raw" / "claude-docs"
WORKSPACE_DIR = Path.home() / "workspace"
USER_CLAUDE_DIR = Path.home() / ".claude"

# Subdirs worth capturing from each project's .claude/
PROJECT_SUBDIRS = {"docs", "skills", "agents", "sessions", "memory", "hooks"}

# From user-level ~/.claude/ — skip machine-specific dirs
USER_SUBDIRS = {"commands", "scripts"}
USER_TOP_FILES = {"CLAUDE.md"}

# Skip these project dirs entirely — they're this repo or non-substantive
SKIP_PROJECTS = {"librarian"}


def _copy_file(src: Path, dest: Path, dry_run: bool) -> bool:
    """Copy src → dest, creating parent dirs. Returns True if written."""
    if dry_run:
        print(f"  [would copy] {src} → {dest}")
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return True


def scrape_user_level(output_dir: Path, dry_run: bool) -> int:
    """Scrape ~/.claude/ top-level files and selected subdirs."""
    if not USER_CLAUDE_DIR.exists():
        log.warning("user_claude_dir_missing", path=str(USER_CLAUDE_DIR))
        return 0

    written = 0
    dest_root = output_dir / "_user"

    # Top-level files (CLAUDE.md)
    for fname in USER_TOP_FILES:
        src = USER_CLAUDE_DIR / fname
        if src.exists():
            dest = dest_root / fname
            _copy_file(src, dest, dry_run)
            written += 1

    # Selected subdirs
    for subdir_name in USER_SUBDIRS:
        subdir = USER_CLAUDE_DIR / subdir_name
        if not subdir.exists():
            continue
        for src in sorted(subdir.rglob("*.md")):
            rel = src.relative_to(USER_CLAUDE_DIR)
            dest = dest_root / rel
            _copy_file(src, dest, dry_run)
            written += 1

    log.info("scraped_user_level", written=written, dry_run=dry_run)
    return written


def scrape_projects(workspace: Path, output_dir: Path, dry_run: bool) -> int:
    """Scrape .claude/ docs from each project in workspace."""
    if not workspace.exists():
        log.warning("workspace_missing", path=str(workspace))
        return 0

    total = 0
    for project_dir in sorted(workspace.iterdir()):
        if not project_dir.is_dir():
            continue
        project = project_dir.name
        if project in SKIP_PROJECTS:
            continue

        claude_dir = project_dir / ".claude"
        if not claude_dir.exists():
            continue

        written = 0
        dest_root = output_dir / project

        for subdir_name in PROJECT_SUBDIRS:
            subdir = claude_dir / subdir_name
            if not subdir.exists():
                continue
            for src in sorted(subdir.rglob("*.md")):
                rel = src.relative_to(claude_dir)
                dest = dest_root / rel
                _copy_file(src, dest, dry_run)
                written += 1

        if written:
            log.info("scraped_project", project=project, files=written, dry_run=dry_run)
            total += written

    return total


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape .claude/ folders → raw/claude-docs/")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--workspace", type=Path, default=WORKSPACE_DIR)
    parser.add_argument("--dry-run", action="store_true", help="Print what would be copied, don't write")
    args = parser.parse_args()

    if not args.dry_run:
        args.output_dir.mkdir(parents=True, exist_ok=True)

    user_count = scrape_user_level(args.output_dir, dry_run=args.dry_run)
    project_count = scrape_projects(args.workspace, args.output_dir, dry_run=args.dry_run)

    total = user_count + project_count
    prefix = "[dry-run] " if args.dry_run else ""
    print(f"\n{prefix}Copied {total} files → {args.output_dir}")
    print(f"  {user_count} from ~/.claude/")
    print(f"  {project_count} from workspace projects")
    if not args.dry_run:
        print("\nNext: run /ingest raw/claude-docs/ in Claude Code to compile into wiki.")


if __name__ == "__main__":
    main()
