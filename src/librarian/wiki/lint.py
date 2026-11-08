"""`librarian wiki lint`: the deterministic findings of the lint protocol, ranked.

BLOCKER: dead wikilinks, missing required frontmatter, pages tagged `conflict`.
WARN: orphans, stale pages, no domain tag. NOTE: short summaries, no See Also.
The private-leak check stays in `librarian wiki check`, and the health rates in
`librarian wiki stats`. Judgement calls (which page should link an orphan) are left to the skill.
Also covers what used to be hand-checked in the skill: open entries in `_conflicts.md`
(BLOCKER), empty placeholder sections and stale relink suggestions (NOTE), and with
`--raw-coverage` raw files that no page lists in `sources:` (WARN). `--fix` applies the two
mechanical fixes (a missing domain tag named by the directory, an empty placeholder section)
and sets `updated:` on each page it changes. Exit code 1 when there is a blocker.
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
from librarian.wiki.common import WIKILINK_RE, fm, link_name, slugify
from librarian.wiki.stats import _STATUS_RE  # pyright: ignore[reportPrivateUsage]
from librarian.wiki.telemetry import (
    STALE_DAYS,
    _link_edges,  # pyright: ignore[reportPrivateUsage]
    _link_index,  # pyright: ignore[reportPrivateUsage]
    _public_pages,  # pyright: ignore[reportPrivateUsage]
)

WIKI_DIR = get_settings().wiki_dir

REQUIRED_FIELDS = ("title", "tags", "summary", "updated")
# Domain tags that are not a directory name (CLAUDE.md, Domain Tags).
EXTRA_DOMAIN_TAGS = frozenset({"llm", "voice", "context-management", "deep-agents"})
MIN_SUMMARY_WORDS = 8
STALE_SUGGESTION_DAYS = 14
RAW_EXAMPLES = 3
_HEADING_RE = re.compile(r"^#{1,6}\s+\S")
_COMMENT_RE = re.compile(r"^\s*<!--.*-->\s*$")
_FIRST_SEEN_RE = re.compile(r"first seen (\d{4}-\d{2}-\d{2})")
_TAGS_RE = re.compile(r"^tags:[ \t]*\[(.*?)\][ \t]*$", re.MULTILINE)
_UPDATED_RE = re.compile(r"^updated:.*$", re.MULTILINE)
# Fenced blocks and backtick spans show link syntax as an example (`[[Successor]]`); not links.
_CODE_RE = re.compile(r"^(```|~~~).*?^\1[^\n]*$|`[^`\n]*`", re.MULTILINE | re.DOTALL)


@dataclass(frozen=True)
class Finding:
    severity: str  # BLOCKER | WARN | NOTE
    page: str
    message: str


def lint(wiki_dir: Path, today: date) -> list[Finding]:
    public = _public_pages(wiki_dir)
    links = _link_index(public)
    domains = {p.domain for p in public} | EXTRA_DOMAIN_TAGS
    scored = [p for p in public if p.scored]
    _, inbound = _link_edges(scored, links)
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
            if (
                links.resolve(match.group(1), include_tombstones=True) is None
                and slugify(link_name(match.group(1))) != "private"
            ):
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
    for clash in links.index.collisions:
        if clash.scope == "live" and clash.kind in ("title", "alias"):
            winner, *others = clash.keys
            out.append(
                Finding(
                    "WARN",
                    winner,
                    f"{clash.kind} {clash.slug!r} also claimed by {', '.join(others)}: "
                    "links resolve to this page",
                )
            )
    order = {"BLOCKER": 0, "WARN": 1, "NOTE": 2}
    return sorted(out, key=lambda f: (order[f.severity], f.page, f.message))


def empty_sections(body: str) -> list[tuple[int, int]]:
    """Line spans (start, end exclusive) of sections holding only comment placeholders."""
    lines = body.splitlines()
    heads = [i for i, line in enumerate(lines) if _HEADING_RE.match(line)]
    spans = []
    for head, nxt in zip(heads, [*heads[1:], len(lines)], strict=True):
        inner = [line for line in lines[head + 1 : nxt] if line.strip()]
        if inner and all(_COMMENT_RE.match(line) for line in inner):
            spans.append((head, nxt))
    return spans


def open_conflicts(wiki_dir: Path) -> list[str]:
    """Headings of `_conflicts.md` entries whose status does not start with Resolved."""
    path = wiki_dir / "_conflicts.md"
    if not path.is_file():
        return []
    heading, out = "(no heading)", []
    for line in path.read_text().splitlines():
        if line.startswith("## "):
            heading = line[3:].strip()
        elif (m := _STATUS_RE.match(line)) and not m.group(1).lower().startswith("resolved"):
            out.append(heading)
    return out


def stale_suggestions(wiki_dir: Path, today: date) -> int:
    path = wiki_dir / "_relink_suggestions.md"
    if not path.is_file():
        return 0
    cutoff = today - timedelta(days=STALE_SUGGESTION_DAYS)
    count = 0
    for m in _FIRST_SEEN_RE.finditer(path.read_text()):
        try:
            count += date.fromisoformat(m.group(1)) < cutoff
        except ValueError:
            continue
    return count


def _norm_source(entry: str) -> str:
    text = entry.strip().replace("\\", "/")
    return text.removeprefix("data/").removeprefix("./")


def uncovered_raw(wiki_dir: Path, raw_dir: Path) -> list[Finding]:
    """Raw files that no wiki page (public or private) lists in `sources:`, one finding per dir."""
    listed: set[str] = set()
    for path in sorted(wiki_dir.rglob("*.md")):
        try:
            sources = frontmatter.loads(path.read_text(errors="replace")).metadata.get("sources")
        except Exception:  # broken frontmatter: lint reports it elsewhere
            continue
        if isinstance(sources, list):
            listed |= {_norm_source(str(x)) for x in sources}
    dirs = tuple(s.rstrip("/") + "/" for s in listed)
    missing: dict[str, list[str]] = {}
    for f in sorted(raw_dir.rglob("*.md")):
        rel = f"raw/{f.relative_to(raw_dir).as_posix()}"
        if rel in listed or rel.startswith(dirs):
            continue
        missing.setdefault(rel.rsplit("/", 1)[0], []).append(f.name)
    return [
        Finding(
            "WARN",
            folder,
            f"{len(names)} raw file(s) not in any page's sources (e.g. {', '.join(names[:RAW_EXAMPLES])})",
        )
        for folder, names in sorted(missing.items())
    ]


def extra_findings(wiki_dir: Path, today: date, raw_dir: Path | None = None) -> list[Finding]:
    """Checks that read files beside the page set: conflicts, placeholders, suggestions, raw."""
    out = [
        Finding("BLOCKER", "_conflicts.md", f"open conflict: {title}")
        for title in open_conflicts(wiki_dir)
    ]
    for page in _public_pages(wiki_dir):
        if page.scored and empty_sections(page.path.read_text(errors="replace")):
            out.append(Finding("NOTE", page.rel, "empty section (comment placeholder only)"))
    if n := stale_suggestions(wiki_dir, today):
        out.append(
            Finding(
                "NOTE",
                "_relink_suggestions.md",
                f"{n} suggestion(s) unreviewed for over {STALE_SUGGESTION_DAYS} days",
            )
        )
    if raw_dir is not None and raw_dir.is_dir():
        out += uncovered_raw(wiki_dir, raw_dir)
    return out


def _touch(text: str, today: date) -> str:
    return _UPDATED_RE.sub(f"updated: {today.isoformat()}", text, count=1)


def fix_page(path: Path, wiki_dir: Path, today: date, domains: set[str]) -> list[str]:
    """Apply the mechanical fixes to one page; returns what changed (empty: left untouched)."""
    text = path.read_text(errors="replace")
    done: list[str] = []
    domain = (
        path.relative_to(wiki_dir).parts[0] if len(path.relative_to(wiki_dir).parts) > 1 else ""
    )
    try:
        meta = fm(frontmatter.loads(text))
    except Exception:
        return []
    tags = [str(t) for t in meta.get("tags") or []]
    if (
        domain in domains - {"private"}
        and not domains & set(tags)
        and "tombstone" not in tags
        and (m := _TAGS_RE.search(text))
    ):
        existing = [t.strip() for t in m.group(1).split(",") if t.strip()]
        text = text[: m.start()] + f"tags: [{', '.join([*existing, domain])}]" + text[m.end() :]
        done.append(f"added domain tag `{domain}` from directory")
    block = re.match(r"\A---\n.*?\n---\n?", text, re.DOTALL)
    head, body = (text[: block.end()], text[block.end() :]) if block else ("", text)
    spans = empty_sections(body)
    if spans:
        lines = body.splitlines(keepends=True)
        drop = {i for a, b in spans for i in range(a, b)}
        body = "".join(line for i, line in enumerate(lines) if i not in drop)
        done.append(f"removed {len(spans)} empty placeholder section(s)")
    if done:
        path.write_text(_touch(head, today) + body)
    return done


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--wiki-dir", type=Path, default=WIKI_DIR)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--quick", nargs="+", type=Path, metavar="PAGE", help="only these pages")
    parser.add_argument(
        "--today", type=date.fromisoformat, default=None, help="YYYY-MM-DD, for tests"
    )
    parser.add_argument("--raw-dir", type=Path, default=get_settings().raw_dir)
    parser.add_argument(
        "--raw-coverage", action="store_true", help="also list raw files no page lists in sources"
    )
    parser.add_argument("--fix", action="store_true", help="apply the mechanical fixes first")
    args = parser.parse_args(argv)
    today = args.today or date.today()
    if args.fix:
        domains = {p.domain for p in _public_pages(args.wiki_dir)} | EXTRA_DOMAIN_TAGS
        for page in _public_pages(args.wiki_dir):
            if not page.scored or (
                args.quick and page.path.resolve() not in {q.resolve() for q in args.quick}
            ):
                continue
            for change in fix_page(page.path, args.wiki_dir, today, domains):
                print(f"[FIXED] {page.rel} — {change}")
    findings = lint(args.wiki_dir, today)
    findings += extra_findings(args.wiki_dir, today, args.raw_dir if args.raw_coverage else None)
    order = {"BLOCKER": 0, "WARN": 1, "NOTE": 2}
    findings.sort(key=lambda f: (order[f.severity], f.page, f.message))
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
