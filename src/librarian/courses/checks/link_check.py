"""Verify that the relative links in the public lessons resolve.

    librarian courses check links [--root DIR]

Walks every markdown file under data/courses/ that git would track (the gitignored ones are local
and skipped), strips fenced code blocks so illustrative links are not checked, and reports each
relative link whose target is not on disk. The anchor part of a link is not checked.

- A figure under `assets/sources/` that lives only in the private overlay counts as present.
- A `sources/...` link into the PDF library resolves through `librarian.courses.sources`. When
  COURSE_SOURCES_DIR is missing or serving is off, such a link is not an error: the library is a
  sibling checkout that CI and a deployment do not have.
- Links from public lessons into `data/courses/private/` are a blocker in `librarian.wiki.course_leaks`
  (`librarian wiki check`), so they are skipped here and never named.

Exit 1 when any link is broken.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Sequence
from pathlib import Path
from urllib.parse import unquote

from librarian.courses import overlay, sources
from librarian.courses.checks.common import default_root, git_ignored, public_files, rel
from librarian.wiki.course_leaks import reaches_private

SKIP_PREFIXES = ("/oss/", "/use-these-docs", "/langsmith/", "~/", "/guides/")
_SCHEME_RE = re.compile(r"^[a-z][a-z0-9+.-]*:", re.I)
# The path part of a link; a trailing #anchor is allowed (the file is checked, not the anchor)
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)#]+)(?:#[^)]*)?\)")
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)


def _lesson_id(path: Path, root: Path) -> str:
    return rel(path, root).removesuffix(".md")


def broken_links(path: Path, text: str, root: Path) -> list[str]:
    """The links in one lesson's text that do not resolve (as written). Private targets and
    unreachable `sources/` links are not reported."""
    broken: list[str] = []
    for match in LINK_RE.finditer(FENCE_RE.sub("", text)):
        link = match.group(1).strip().strip("<>")
        if not link or _SCHEME_RE.match(link) or link.startswith(SKIP_PREFIXES):
            continue
        if reaches_private(link, path, root):
            continue
        target = path.parent / unquote(link)
        if target.exists() or overlay.resolve_asset(target, root) is not None:
            continue
        # A link into the PDF library: only checkable when the library is there.
        source_rel = sources.resolve_link(_lesson_id(path, root), link)
        if source_rel is not None and sources.sources_root() is None:
            continue
        if source_rel is not None and sources.source_file(source_rel) is not None:
            continue
        broken.append(link)
    return broken


def check(root: Path) -> tuple[list[str], int]:
    """(output lines, files scanned) for every public markdown file under `root`."""
    names = [n for n in public_files(root) if n.endswith(".md")]
    ignored = git_ignored(root, names)
    lines: list[str] = []
    scanned = 0
    for name in names:
        if name in ignored:
            continue
        path = root / name
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            lines.append(f"SKIPPED: {name} -> {exc.strerror}")
            continue
        scanned += 1
        lines += [f"BROKEN: {name} -> {link}" for link in broken_links(path, text, root)]
    return lines, scanned


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="librarian courses check links", description=(__doc__ or "").split("\n")[0]
    )
    ap.add_argument("--root", type=Path, default=None, help="courses dir (default: data/courses)")
    args = ap.parse_args(argv)
    root = (args.root or default_root()).resolve()
    lines, scanned = check(root)
    broken = sum(line.startswith("BROKEN") for line in lines)
    print("\n".join(lines))
    if broken:
        print(f"{broken} broken links found in {scanned} files")
        return 1
    print(f"All links OK ({scanned} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
