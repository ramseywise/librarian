"""`librarian wiki lint`: the deterministic findings of the lint protocol, ranked.

BLOCKER: dead wikilinks, missing required frontmatter, pages tagged `conflict`.
WARN: orphans, stale pages, no domain tag. NOTE: short summaries, no See Also.
The private-leak check stays in `librarian wiki check`, and the health rates in
`librarian wiki stats`. Judgement calls (which page should link an orphan) are left to the skill.
Exit code 1 when there is a blocker.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from pathlib import Path

import frontmatter

from librarian.config import get_settings
from librarian.wiki.common import WIKILINK_RE, fm, slugify
from librarian.wiki.telemetry import (
    STALE_DAYS,
    _link_edges,  # pyright: ignore[reportPrivateUsage]
    _link_target,  # pyright: ignore[reportPrivateUsage]
    _public_pages,  # pyright: ignore[reportPrivateUsage]
    _slug_map,  # pyright: ignore[reportPrivateUsage]
)

WIKI_DIR = get_settings().wiki_dir

REQUIRED_FIELDS = ("title", "tags", "summary", "updated")
# Domain tags that are not a directory name (CLAUDE.md, Domain Tags).
EXTRA_DOMAIN_TAGS = frozenset({"llm", "voice", "context-management", "deep-agents"})
MIN_SUMMARY_WORDS = 8
# Fenced blocks and backtick spans show link syntax as an example (`[[Successor]]`); not links.
_CODE_RE = re.compile(r"^(```|~~~).*?^\1[^\n]*$|`[^`\n]*`", re.MULTILINE | re.DOTALL)


@dataclass(frozen=True)
class Finding:
    severity: str  # BLOCKER | WARN | NOTE
    page: str
    message: str


def lint(wiki_dir: Path, today: date) -> list[Finding]:
    public = _public_pages(wiki_dir)
    slugs = _slug_map(public)
    domains = {p.domain for p in public} | EXTRA_DOMAIN_TAGS
    scored = [p for p in public if p.scored]
    _, inbound = _link_edges(scored, slugs)
    cutoff = today - timedelta(days=STALE_DAYS)
    out: list[Finding] = []
    for page in scored:
        meta = fm(frontmatter.loads(page.path.read_text(errors="replace"))) if page.parsed else {}
        missing = [k for k in REQUIRED_FIELDS if not meta.get(k)]
        if not page.parsed:
            out.append(Finding("BLOCKER", page.rel, "frontmatter does not parse"))
        elif missing:
            out.append(Finding("BLOCKER", page.rel, f"missing frontmatter: {', '.join(missing)}"))
        if "conflict" in page.tags:
            out.append(Finding("BLOCKER", page.rel, "tagged conflict (unresolved)"))
        for match in WIKILINK_RE.finditer(_CODE_RE.sub("", page.body)):
            slug, _ = _link_target(match.group(1))
            if slug not in slugs and slugify(match.group(1)) not in slugs and slug != "private":
                out.append(Finding("BLOCKER", page.rel, f"dead wikilink: [[{match.group(1)}]]"))
        if not inbound[page.rel]:
            out.append(Finding("WARN", page.rel, "orphan (no inbound link)"))
        if page.updated is not None and page.updated < cutoff:
            out.append(Finding("WARN", page.rel, f"stale (updated {page.updated})"))
        if page.parsed and not domains & set(page.tags):
            out.append(Finding("WARN", page.rel, "no domain tag"))
        summary = str(meta.get("summary") or "")
        if summary and len(summary.split()) < MIN_SUMMARY_WORDS:
            out.append(
                Finding("NOTE", page.rel, f"summary too short ({len(summary.split())} words)")
            )
        if "see also" not in page.body.lower():
            out.append(Finding("NOTE", page.rel, "no See Also section"))
    order = {"BLOCKER": 0, "WARN": 1, "NOTE": 2}
    return sorted(out, key=lambda f: (order[f.severity], f.page, f.message))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--wiki-dir", type=Path, default=WIKI_DIR)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--quick", nargs="+", type=Path, metavar="PAGE", help="only these pages")
    parser.add_argument(
        "--today", type=date.fromisoformat, default=None, help="YYYY-MM-DD, for tests"
    )
    args = parser.parse_args(argv)
    findings = lint(args.wiki_dir, args.today or date.today())
    if args.quick:
        keep = {p.resolve().relative_to(args.wiki_dir.resolve()).as_posix() for p in args.quick}
        findings = [f for f in findings if f.page in keep]
    if args.json:
        print(json.dumps([asdict(f) for f in findings], indent=2))
    else:
        for f in findings:
            print(f"[{f.severity}] {f.page} — {f.message}")
        counts = {s: sum(f.severity == s for f in findings) for s in ("BLOCKER", "WARN", "NOTE")}
        print(
            f"lint: {counts['BLOCKER']} blockers, {counts['WARN']} warnings, {counts['NOTE']} notes"
        )
    return 1 if any(f.severity == "BLOCKER" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
