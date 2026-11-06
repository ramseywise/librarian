"""Rename a wiki page: the file, its title, every inbound link, and an alias for the old name.

Dry run by default; `--apply` writes. Nothing is written unless the whole plan can be, and a failed
write puts every file back.

Links are rewritten in all of data/wiki/, private/ included, because a private page may link a
public one. Private pages only ever appear as a count. Lessons are not rewritten: an imported
lesson stops being imported once edited, so the alias keeps their links resolving and the report
counts them for fixing in the course source. References outside the wiki (golden sets, the
glossary) are listed, not rewritten: changing an eval's expected page is a decision.

Every rewritten page gets today's `updated`, as the page format requires, so a rename touching
many pages also makes them read as fresh to the stale rate.

    uv run librarian wiki rename "<old stem or title>" "<New Title>" [--apply] [--no-alias]
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import frontmatter
import yaml

from librarian.config import get_settings
from librarian.ingest.sensitive import load_terms, terms_pattern
from librarian.wiki.common import WIKILINK_RE, page_aliases, slugify
from librarian.wiki.telemetry import (
    WIKI_DIR,
    Page,
    _link_edges,
    _names_private_page,
    _private_name_pattern,
    _private_pages,
    _public_pages,
    _slug_map,
)

REPO_ROOT = get_settings().root
COURSES_DIR = get_settings().courses_dir
# Whole link, so `[[Target#heading|label]]` keeps everything after the target.
_LINK_RE = re.compile(r"\[\[([^\]|#]+)((?:[|#][^\]]*)?)\]\]")
_SEE_ALSO_PREFIX_RE = re.compile(r"^(\s*see also:\s*)", re.IGNORECASE)
_FM_BLOCK_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
_ALIASES_RE = re.compile(r"^aliases:.*\n(?:[ \t]+- .*\n)*", re.MULTILINE)
_UPDATED_RE = re.compile(r"^updated:.*$", re.MULTILINE)
_TITLE_RE = re.compile(r"^title:.*$", re.MULTILINE)
_YAML_SPECIAL_RE = re.compile(r"[:#\[\]{}&*!|>'\"%@`]|^[-?\s]|\s$")


class RenameError(Exception):
    """The rename can't go ahead. The message is safe to print: it names no private page."""


@dataclass
class Plan:
    page: Page
    new_title: str
    new_stem: str
    new_path: Path
    alias: str | None
    alias_note: str
    contents: dict[Path, str] = field(default_factory=dict)  # files to write, new path included
    links: int = 0
    linking_pages: int = 0
    private_pages: int = 0
    course_files: int = 0
    other_references: list[str] = field(default_factory=list)


def _yaml_scalar(text: str) -> str:
    return json.dumps(text, ensure_ascii=False) if _YAML_SPECIAL_RE.search(text) else text


def _rewrite_links(text: str, resolves: dict[str, Page], plan: Plan) -> tuple[str, int]:
    """Point every link that resolves to the page at its new name, in the form it was written."""
    count = 0

    def sub(match: re.Match[str]) -> str:
        nonlocal count
        raw, rest = match.group(1), match.group(2)
        prefix_match = _SEE_ALSO_PREFIX_RE.match(raw)
        prefix = prefix_match.group(1) if prefix_match else ""
        target = raw[len(prefix) :]
        folder, slash, name = target.strip().rpartition("/")
        if resolves.get(slugify(name)) is not plan.page:
            return match.group(0)
        replacement = plan.new_stem if name == plan.page.stem else plan.new_title
        if replacement == name:
            return match.group(0)
        count += 1
        return f"[[{prefix}{folder}{slash}{replacement}{rest}]]"

    return _LINK_RE.sub(sub, text), count


def _rewrite_paths(text: str, old_stem: str, new_stem: str) -> str:
    """`rag/old.md` in a markdown link or prose. A path under raw/ names a source, so it stays."""

    def sub(match: re.Match[str]) -> str:
        token = match.group(0)
        if "raw/" in token:
            return token
        return token[: -len(f"{old_stem}.md")] + f"{new_stem}.md"

    return re.sub(rf"[^\s()\[\]\"'`]*(?<![\w-]){re.escape(old_stem)}\.md", sub, text)


def _touch_updated(text: str, today: date) -> str:
    block = _FM_BLOCK_RE.match(text)
    if block is None:
        return text
    new_block = _UPDATED_RE.sub(f"updated: {today.isoformat()}", block.group(0), count=1)
    return new_block + text[block.end() :]


def _renamed_text(text: str, plan: Plan, kept_aliases: list[str]) -> str:
    block = _FM_BLOCK_RE.match(text)
    if block is None:
        raise RenameError(f"{plan.page.rel} has no frontmatter block to rewrite")
    title_line = f"title: {_yaml_scalar(plan.new_title)}"
    fm = _ALIASES_RE.sub("", block.group(0))
    fm, replaced = _TITLE_RE.subn(lambda _: title_line, fm, count=1)
    if not replaced:
        fm = fm.replace("---\n", f"---\n{title_line}\n", 1)
    if kept_aliases:
        listed = "".join(f"  - {_yaml_scalar(a)}\n" for a in kept_aliases)
        fm = fm.replace(f"{title_line}\n", f"{title_line}\naliases:\n{listed}", 1)
    body = re.sub(
        rf"^# {re.escape(plan.page.title)}[ \t]*$",
        lambda _: f"# {plan.new_title}",
        text[block.end() :],
        count=1,
        flags=re.MULTILINE,
    )
    return fm + body


def _check_new_name(
    page: Page, new_title: str, new_slug: str, public: list[Page], private: list[Page], wiki: Path
) -> None:
    if not new_slug:
        raise RenameError("the new title has no letters or digits to make a file name from")
    if new_title == page.title:
        raise RenameError("that is already the page's title")
    for other in public:
        if other is page:
            continue
        names = {other.stem, other.title, *other.aliases}
        if new_slug in {slugify(n) for n in names}:
            raise RenameError(f"{new_title!r} is already a name of {other.rel}")
    # The file name is public, so a name that points at private material can't be used at all.
    if _names_private_page(new_title, _private_name_pattern(private)) or new_slug in {
        slugify(n) for p in private for n in (p.stem, p.title)
    }:
        raise RenameError("the new name matches a private page: choose another")
    terms = terms_pattern(load_terms(wiki))
    if terms and terms.search(new_title):
        raise RenameError("the new name contains a listed sensitive term: choose another")


def _alias_decision(
    page: Page, new_slug: str, no_alias: bool, wiki: Path, private: list[Page]
) -> tuple[str | None, str]:
    if no_alias:
        return None, "none (--no-alias)"
    if slugify(page.title) == new_slug:
        return None, "none (the old name still resolves)"
    terms = terms_pattern(load_terms(wiki))
    if (terms and terms.search(page.title)) or _names_private_page(
        page.title, _private_name_pattern(private)
    ):
        # A rename is how a sensitive name gets removed: an alias would keep it published.
        return None, "none (the old name is sensitive)"
    return page.title, page.title


def _course_references(page: Page, courses_dir: Path) -> int:
    """Lesson files that link the old name, through `[[...]]` or `wiki:` frontmatter."""
    old = {slugify(page.stem), slugify(page.title)}
    count = 0
    if not courses_dir.is_dir():
        return 0
    for md in courses_dir.rglob("*.md"):
        text = md.read_text(errors="replace")
        if any(slugify(m.group(1)) in old for m in WIKILINK_RE.finditer(text)):
            count += 1
            continue
        if "wiki:" in text:
            try:
                listed = frontmatter.loads(text).get("wiki") or []
            except (yaml.YAMLError, ValueError):
                continue
            if isinstance(listed, list) and old & {slugify(str(x)) for x in listed}:
                count += 1
    return count


def _other_references(stem: str, repo_root: Path) -> list[str]:
    """Tracked files outside the wiki, raw sources and lessons that name the page's file."""
    run = subprocess.run(
        [
            "git",
            "grep",
            "-l",
            "-E",
            rf"(^|[^a-z0-9-]){re.escape(stem)}\.md|^\s*page: {re.escape(stem)}\s*$",
            "--",
            ".",
            ":!data/wiki",
            ":!data/raw",
            ":!data/courses",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    return run.stdout.splitlines() if run.returncode == 0 else []


def build_plan(
    old: str,
    new_title: str,
    wiki_dir: Path,
    today: date,
    no_alias: bool = False,
    courses_dir: Path = COURSES_DIR,
    repo_root: Path = REPO_ROOT,
) -> Plan:
    public = _public_pages(wiki_dir)
    private = _private_pages(wiki_dir)
    public_map = _slug_map(public)
    page = public_map.get(slugify(old))
    if page is None:
        raise RenameError(f"no public page is named {old!r}")
    if "tombstone" in page.tags:
        raise RenameError(f"{page.rel} is a tombstone: only /compact-wiki changes those")

    new_title = new_title.strip()
    new_stem = slugify(new_title)
    _check_new_name(page, new_title, new_stem, public, private, wiki_dir)
    new_path = page.path.with_name(f"{new_stem}.md")
    if new_stem != page.stem and new_path.exists():
        raise RenameError(f"{new_path.name} already exists in that directory")

    alias, note = _alias_decision(page, new_stem, no_alias, wiki_dir, private)
    plan = Plan(page, new_title, new_stem, new_path, alias, note)

    # Inside private/, a private page of the same name is what its links mean.
    private_map = _slug_map([*private, *public])
    for other in [*public, *private]:
        if other is page:
            continue
        original = other.path.read_text(errors="replace")
        resolves = private_map if other.rel.startswith("private/") else public_map
        text, count = _rewrite_links(original, resolves, plan)
        if new_stem != page.stem:
            text = _rewrite_paths(text, page.stem, new_stem)
        if text == original:
            continue
        plan.contents[other.path] = _touch_updated(text, today)
        plan.links += count
        plan.linking_pages += 1
        plan.private_pages += other.rel.startswith("private/")

    original = page.path.read_text(errors="replace")
    self_linked, _ = _rewrite_links(original, public_map, plan)
    earlier = page_aliases(frontmatter.loads(original).metadata)
    kept = [a for a in earlier if slugify(a) != new_stem]
    if alias and slugify(alias) not in {slugify(a) for a in kept}:
        kept.append(alias)
    plan.contents[new_path] = _touch_updated(_renamed_text(self_linked, plan, kept), today)

    plan.course_files = _course_references(page, courses_dir)
    if new_stem != page.stem:
        plan.other_references = _other_references(page.stem, repo_root)
    return plan


def apply_plan(plan: Plan) -> None:
    """Write every file or none: the first failure restores what was already written."""
    old_path = plan.page.path
    backups: dict[Path, str | None] = {}
    try:
        for path, text in plan.contents.items():
            backups[path] = path.read_text(errors="replace") if path.exists() else None
            path.write_text(text)
        if plan.new_path != old_path:
            backups[old_path] = old_path.read_text(errors="replace")
            old_path.unlink()
    except OSError:
        for path, text in backups.items():
            if text is None:
                path.unlink(missing_ok=True)
            else:
                path.write_text(text)
        raise


def inbound_links(rel: str, wiki_dir: Path) -> int:
    public = _public_pages(wiki_dir)
    pages = [p for p in public if p.scored]
    _, inbound = _link_edges(pages, _slug_map(public))
    return len(inbound.get(rel, ()))


def render(plan: Plan, applied: bool, inbound: tuple[int, int] | None = None) -> str:
    head = "Renamed" if applied else "Would rename"
    new_rel = plan.new_path.parent.name + "/" + plan.new_path.name
    lines = [
        f"{head}: [[{plan.page.title}]] -> [[{plan.new_title}]]",
        f"File: {plan.page.rel} -> {new_rel}",
        f"Inbound links updated: {plan.links} across {plan.linking_pages} pages "
        f"({plan.private_pages} private)",
        f"Alias added: {plan.alias_note}",
    ]
    if inbound is not None:
        lines.append(f"Inbound links, public: {inbound[0]} before, {inbound[1]} after")
    remaining = list(plan.other_references)
    if plan.course_files:
        remaining.append(f"{plan.course_files} course files (fix in the course source)")
    lines.append("Remaining references:" + ("" if remaining else " none"))
    lines += [f"  {item}" for item in remaining]
    if not applied:
        lines.append("Dry run: nothing written. Add --apply to write.")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("old", help="the page's current file stem or title")
    parser.add_argument("new", help="the new title, Title Case; the file name is made from it")
    parser.add_argument("--apply", action="store_true", help="write the changes")
    parser.add_argument("--no-alias", action="store_true", help="do not keep the old name")
    parser.add_argument("--wiki-dir", type=Path, default=WIKI_DIR)
    parser.add_argument("--courses-dir", type=Path, default=COURSES_DIR)
    parser.add_argument("--today", type=date.fromisoformat, default=date.today())
    args = parser.parse_args(argv)

    try:
        plan = build_plan(
            args.old, args.new, args.wiki_dir, args.today, args.no_alias, args.courses_dir
        )
    except RenameError as e:
        print(f"rename: refused, {e}", file=sys.stderr)
        return 2
    if not args.apply:
        print(render(plan, applied=False))
        return 0
    before = inbound_links(plan.page.rel, args.wiki_dir)
    apply_plan(plan)
    new_rel = plan.new_path.relative_to(args.wiki_dir).as_posix()
    after = inbound_links(new_rel, args.wiki_dir)
    print(render(plan, applied=True, inbound=(before, after)))
    if after < before:
        print("rename: inbound links dropped, check the page before committing", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
