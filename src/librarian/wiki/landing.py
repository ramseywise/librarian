"""Checks and edits that follow a page being written: inbound links, index entry.

`librarian wiki verify <pages>` reports, for each page an ingest wrote, whether another page
links to it and whether `_index.md` lists it (the blocking orphan check of the ingest
protocol). `librarian wiki index-add <pages>` inserts the missing index lines in place,
alphabetically within the page's domain section, and updates the page count.
Private pages are never indexed and never checked: they are outside every graph rate.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import frontmatter

from librarian.config import get_settings
from librarian.wiki.common import slugify
from librarian.wiki.telemetry import (
    _link_edges,  # pyright: ignore[reportPrivateUsage]
    _link_index,  # pyright: ignore[reportPrivateUsage]
    _load_page,  # pyright: ignore[reportPrivateUsage]
    _public_pages,  # pyright: ignore[reportPrivateUsage]
)

WIKI_DIR = get_settings().wiki_dir

# Directory name -> heading in _index.md, where the heading is not just the capitalised name.
SECTION_NAMES = {
    "rag": "RAG",
    "mcp": "MCP",
    "adk": "Google ADK",
    "langgraph": "LangGraph",
    "infra": "Infrastructure",
    "eval": "Evaluation",
    "interview": "Interview Prep",
}
_PAGE_COUNT_RE = re.compile(r"\*\*(\d+) pages\*\*")
_ENTRY_RE = re.compile(r"^- \[\[(.+?)\]\]")


@dataclass(frozen=True)
class PageStatus:
    rel: str
    private: bool
    inbound: int
    indexed: bool
    tombstone: bool


def section_heading(directory: str) -> str:
    return SECTION_NAMES.get(directory, directory.replace("-", " ").title())


def _index_titles(index_text: str) -> set[str]:
    return {slugify(m.group(1)) for line in index_text.splitlines() if (m := _ENTRY_RE.match(line))}


def _rel(path: Path, wiki_dir: Path) -> str:
    return path.resolve().relative_to(wiki_dir.resolve()).as_posix()


def verify(paths: list[Path], wiki_dir: Path = WIKI_DIR) -> list[PageStatus]:
    """Inbound-link count and index membership for each page, by path."""
    pages = _public_pages(wiki_dir)
    _, inbound = _link_edges(pages, _link_index(pages))
    index = wiki_dir / "_index.md"
    listed = _index_titles(index.read_text()) if index.is_file() else set()
    out: list[PageStatus] = []
    for path in paths:
        rel = _rel(path, wiki_dir)
        page = _load_page(wiki_dir / rel, wiki_dir)
        private = rel.split("/", 1)[0] == "private"
        out.append(
            PageStatus(
                rel=rel,
                private=private,
                inbound=0 if private else len(inbound.get(rel, ())),
                indexed=private or slugify(page.title) in listed,
                tombstone="tombstone" in page.tags,
            )
        )
    return out


def add_to_index(paths: list[Path], wiki_dir: Path = WIKI_DIR) -> tuple[list[str], list[str]]:
    """Insert missing index lines. Returns (added titles, problems)."""
    index = wiki_dir / "_index.md"
    lines = index.read_text().splitlines()
    listed = _index_titles("\n".join(lines))
    added: list[str] = []
    problems: list[str] = []
    for path in paths:
        rel = _rel(path, wiki_dir)
        parts = rel.split("/")
        if parts[0] == "private" or len(parts) < 2 or parts[-1].startswith("_"):
            continue
        page = _load_page(wiki_dir / rel, wiki_dir)
        if "tombstone" in page.tags or slugify(page.title) in listed:
            continue
        heading = f"## {section_heading(parts[0])}"
        if heading not in lines:
            problems.append(f"{rel}: no index section {heading!r}; add it by hand")
            continue
        start = lines.index(heading) + 1
        end = next((i for i in range(start, len(lines)) if lines[i].startswith("## ")), len(lines))
        summary = " ".join(
            str(frontmatter.loads(page.path.read_text()).get("summary") or "").split()
        )
        pos = end
        while pos > start and not lines[pos - 1].strip():
            pos -= 1  # keep the blank line before the next heading
        for i in range(start, pos):
            m = _ENTRY_RE.match(lines[i])
            if m and m.group(1).lower() > page.title.lower():
                pos = i
                break
        lines.insert(pos, f"- [[{page.title}]] — {summary}")
        listed.add(slugify(page.title))
        added.append(page.title)
    if added:
        text = "\n".join(lines) + "\n"
        total = sum(1 for ln in lines if _ENTRY_RE.match(ln))
        index.write_text(_PAGE_COUNT_RE.sub(f"**{total} pages**", text, count=1))
    return added, problems


def _verify_main(args: argparse.Namespace) -> int:
    bad = 0
    for st in verify(args.pages, args.wiki_dir):
        if st.private:
            print(f"private   {st.rel} (not indexed, not checked)")
            continue
        problems: list[str] = []
        if st.inbound == 0 and not st.tombstone:
            problems.append("ORPHAN (no inbound link)")
        if not st.indexed and not st.tombstone:
            problems.append("NOT IN _index.md")
        bad += bool(problems)
        status = "FAIL" if problems else "ok  "
        print(f"{status}      {st.rel}  inbound={st.inbound}  {' '.join(problems)}".rstrip())
    print(f"verify: {bad} page(s) failing")
    return 1 if bad else 0


def _index_main(args: argparse.Namespace) -> int:
    added, problems = add_to_index(args.pages, args.wiki_dir)
    for title in added:
        print(f"added     {title}")
    for line in problems:
        print(f"PROBLEM   {line}")
    print(f"index-add: {len(added)} added, {len(problems)} problem(s)")
    return 1 if problems else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    for name, func, help_ in (
        ("verify", _verify_main, "orphan and index check for pages an ingest wrote"),
        ("index-add", _index_main, "insert missing pages into _index.md"),
    ):
        sub = commands.add_parser(name, help=help_)
        sub.add_argument("pages", nargs="+", type=Path)
        sub.add_argument("--wiki-dir", type=Path, default=WIKI_DIR)
        sub.set_defaults(func=func)
    args = parser.parse_args(argv)
    missing = [str(p) for p in args.pages if not p.is_file()]
    if missing:
        print(f"{args.command}: not found: {' '.join(missing)}", file=sys.stderr)
        return 2
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
