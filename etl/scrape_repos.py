"""Scrape local git repos → raw/repos/

Reads raw/repos/repos.txt — one repo path per line (# for comments).
For each repo, extracts: CLAUDE.md, README.md, .claude/skills/**/*.md,
docs/**/*.md, .agents/**/*.md, SANYI.md.

Idempotent: skips files whose content hasn't changed since last scrape.

Usage:
    uv run python etl/scrape_repos.py
    uv run python etl/scrape_repos.py --dry-run
    uv run python etl/scrape_repos.py --repos-file path/to/repos.txt
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path

import structlog
from dotenv import load_dotenv

load_dotenv()
log = structlog.get_logger()

DEFAULT_REPOS_FILE = Path(__file__).parent.parent / "raw" / "repos" / "repos.txt"
DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent / "raw" / "repos"

# Files and glob patterns to extract from each repo
EXTRACT_GLOBS = [
    "CLAUDE.md",
    "README.md",
    "SANYI.md",
    ".claude/skills/**/*.md",
    ".claude/docs/**/*.md",
    "docs/**/*.md",
    ".agents/**/*.md",
    "src/agents/akira/findings/*.md",
]

# Never extract these (build artifacts, lock files, etc.)
EXCLUDE_STEMS = {"package-lock", "yarn.lock", "uv.lock", "poetry.lock"}
EXCLUDE_DIRS = {".venv", "node_modules", "__pycache__", ".git", "dist", "build"}


def _content_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def _should_skip(path: Path) -> bool:
    for part in path.parts:
        if part in EXCLUDE_DIRS:
            return True
    return path.stem in EXCLUDE_STEMS


def scrape_repo(
    repo_path: Path,
    output_dir: Path,
    dry_run: bool = False,
) -> tuple[int, int]:
    """Scrape one repo into output_dir/<repo-name>/. Returns (written, skipped)."""
    if not repo_path.is_dir():
        log.warning("repo_not_found", path=str(repo_path))
        return 0, 0

    repo_name = repo_path.name
    repo_out = output_dir / repo_name

    if not dry_run:
        repo_out.mkdir(parents=True, exist_ok=True)

    written = skipped = 0

    for pattern in EXTRACT_GLOBS:
        for src in repo_path.glob(pattern):
            if not src.is_file() or _should_skip(src):
                continue

            # Build output filename: flatten path, preserve uniqueness
            rel = src.relative_to(repo_path)
            flat_name = str(rel).replace("/", "--").replace("\\", "--")
            dest = repo_out / flat_name

            # Idempotency: skip if content identical
            if dest.exists() and _content_hash(src) == _content_hash(dest):
                skipped += 1
                continue

            if dry_run:
                print(f"  [would write] {repo_name}/{flat_name}")
            else:
                shutil.copy2(src, dest)
                log.info("scraped_file", repo=repo_name, file=flat_name)

            written += 1

    return written, skipped


def load_repos(repos_file: Path) -> list[Path]:
    if not repos_file.exists():
        log.warning("repos_file_not_found", path=str(repos_file))
        return []
    paths = []
    for line in repos_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        paths.append(Path(line).expanduser())
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape local repos → raw/repos/")
    parser.add_argument(
        "--repos-file",
        type=Path,
        default=DEFAULT_REPOS_FILE,
        help="Path to repos.txt (default: raw/repos/repos.txt)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory (default: raw/repos/)",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    repos = load_repos(args.repos_file)
    if not repos:
        print("No repos configured. Add paths to raw/repos/repos.txt.")
        return

    total_written = total_skipped = 0
    for repo_path in repos:
        w, s = scrape_repo(repo_path, args.output_dir, dry_run=args.dry_run)
        print(f"  {repo_path.name}: {w} written, {s} skipped")
        total_written += w
        total_skipped += s

    prefix = "[dry-run] " if args.dry_run else ""
    print(f"\n{prefix}Total: {total_written} written, {total_skipped} skipped → {args.output_dir}")


if __name__ == "__main__":
    main()
