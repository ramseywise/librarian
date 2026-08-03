"""
Pre-ingest linter for data/raw/ filename conventions.

Convention: YYYY-MM-DD-lowercase-slug.md
Exempted dirs: data/raw/claude-docs/, data/raw/repos/ (mirror external structure, not user-dropped)
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent / "data" / "raw"

# Dirs that are scraper output or mirror external structure — not user-dropped files
EXEMPT_PREFIXES = {"claude-docs", "repos", "agent-skills", "claude-skills", "sessions"}

# Standard user-drop convention: 2026-07-05-my-page.md
DATE_SLUG_RE = re.compile(
    r"^\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])-[a-z0-9][a-z0-9-]*\.md$"
)


def check_dir(subdir: Path, errors: list, warnings: list) -> None:
    for f in sorted(subdir.rglob("*.md")):
        rel = f.relative_to(ROOT)
        name = f.name

        if DATE_SLUG_RE.match(name):
            continue
        # Distinguish clearly wrong vs close-but-not-quite
        has_date = re.match(r"^\d{4}-\d{2}-\d{2}", name)
        if has_date:
            warnings.append((rel, "has date prefix but slug contains uppercase or spaces"))
        else:
            errors.append((rel, "missing YYYY-MM-DD- date prefix"))


def main() -> int:
    if not ROOT.exists():
        print(f"ERROR: raw/ not found at {ROOT}", file=sys.stderr)
        return 1

    errors: list = []
    warnings: list = []

    for subdir in sorted(ROOT.iterdir()):
        if not subdir.is_dir():
            continue
        if subdir.name in EXEMPT_PREFIXES:
            continue
        check_dir(subdir, errors, warnings)

    if errors:
        print(f"\n{'─' * 60}")
        print(f"ERRORS ({len(errors)}) — files that will create malformed manifest entries:")
        for path, reason in errors:
            print(f"  ✗ raw/{path}  [{reason}]")

    if warnings:
        print(f"\n{'─' * 60}")
        print(f"WARNINGS ({len(warnings)}) — fixable but won't block ingest:")
        for path, reason in warnings:
            print(f"  ⚠ raw/{path}  [{reason}]")

    if not errors and not warnings:
        print("✓ All raw/ filenames conform to YYYY-MM-DD-slug convention.")
        return 0

    if errors:
        print(f"\n{'─' * 60}")
        print(
            "Rename these files before running /ingest, or they will be ingested with malformed manifest keys."
        )
        print("Convention: YYYY-MM-DD-lowercase-slug.md  (no uppercase, no spaces, no underscores)")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
