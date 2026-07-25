"""Scrape .claude/ folders and root docs/ from all workspace projects → raw/claude-docs/

Collects markdown files from two locations per project:
  - {project}/.claude/  (plans, skills, agents, sessions, memory, hooks)
  - {project}/docs/     (committed reference docs at repo root — e.g. playground/docs/)

Also captures user-level:
  - ~/.claude/           (user-level CLAUDE.md, commands/, scripts/)

Writes to raw/claude-docs/{project-name}/{subdir}/{file}.md preserving structure.
Idempotent: copies are overwritten on each run (source is always current).

Usage:
    uv run python core/scrape_claude_docs.py
    uv run python core/scrape_claude_docs.py --dry-run
    uv run python core/scrape_claude_docs.py --workspace /custom/path
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import structlog
from dotenv import load_dotenv

from core.base import REPO_ROOT, ScraperBase

load_dotenv()
log = structlog.get_logger()

DEFAULT_OUTPUT_DIR = REPO_ROOT / "raw" / "claude-docs"
WORKSPACE_DIR = Path.home() / "workspace"
USER_CLAUDE_DIR = Path.home() / ".claude"

# Subdirs worth capturing from each project's .claude/
PROJECT_SUBDIRS = {"docs", "skills", "agents", "sessions", "memory", "hooks"}

# Root-level dirs to capture from each project (outside .claude/)
PROJECT_ROOT_DIRS = {"docs", ".agents"}

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
    """Scrape .claude/ docs and root docs/ from each project in workspace."""
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

        written = 0
        dest_root = output_dir / project

        # .claude/ subdirectories (plans, skills, agents, memory, hooks, sessions)
        claude_dir = project_dir / ".claude"
        if claude_dir.exists():
            for subdir_name in PROJECT_SUBDIRS:
                subdir = claude_dir / subdir_name
                if not subdir.exists():
                    continue
                for src in sorted(subdir.rglob("*.md")):
                    rel = src.relative_to(claude_dir)
                    dest = dest_root / rel
                    _copy_file(src, dest, dry_run)
                    written += 1

        # Root-level docs/ (committed reference docs — e.g. playground/docs/)
        for root_dir_name in PROJECT_ROOT_DIRS:
            root_docs = project_dir / root_dir_name
            if not root_docs.exists():
                continue
            for src in sorted(root_docs.rglob("*.md")):
                rel = src.relative_to(project_dir)
                dest = dest_root / rel
                _copy_file(src, dest, dry_run)
                written += 1

        if written:
            log.info("scraped_project", project=project, files=written, dry_run=dry_run)
            total += written

    return total


class ClaudeDocsScraper(ScraperBase):
    source_name = "scrape-claude-docs"
    output_dir = DEFAULT_OUTPUT_DIR

    def __init__(
        self,
        workspace: Path = WORKSPACE_DIR,
        output_dir: Path = DEFAULT_OUTPUT_DIR,
    ) -> None:
        self._workspace = workspace
        self.output_dir = output_dir

    def run(self, dry_run: bool = False) -> list[Path]:
        if not dry_run:
            self.output_dir.mkdir(parents=True, exist_ok=True)

        user_count = scrape_user_level(self.output_dir, dry_run=dry_run)
        project_count = scrape_projects(self._workspace, self.output_dir, dry_run=dry_run)

        total = user_count + project_count
        prefix = "[dry-run] " if dry_run else ""
        print(f"\n{prefix}Copied {total} files → {self.output_dir}")
        print(f"  {user_count} from ~/.claude/")
        print(f"  {project_count} from workspace projects")
        if not dry_run:
            print("\nNext: run /ingest raw/claude-docs/ in Claude Code to compile into wiki.")

        return [self.output_dir] if total > 0 else []

    @classmethod
    def _add_args(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--output-dir",
            type=Path,
            default=DEFAULT_OUTPUT_DIR,
            help="Output directory (default: raw/claude-docs/)",
        )
        parser.add_argument(
            "--workspace",
            type=Path,
            default=WORKSPACE_DIR,
            help="Workspace directory (default: ~/workspace)",
        )

    @classmethod
    def _from_args(cls, args: argparse.Namespace) -> ClaudeDocsScraper:
        return cls(workspace=args.workspace, output_dir=args.output_dir)


if __name__ == "__main__":
    ClaudeDocsScraper.cli(description="Scrape .claude/ folders → raw/claude-docs/")
