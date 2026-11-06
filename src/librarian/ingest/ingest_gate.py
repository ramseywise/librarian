"""Pre-ingest triage: has this raw file been compiled already, and may it go public?

    uv run librarian ingest triage <file or dir>... [--json]

Status: unchanged (skip) | duplicate (same content under another path: add the path to the
existing pages' sources) | changed (update the pages it fed) | new.

Route, for anything not skipped:
    clear   nothing matched. Still read the source: a pattern scan can't see unlisted context.
    strip   contact details. Leave them out, compile the rest as public.
    decide  a listed term or private page's name. Generalise it away or compile to private/.
    stop    a live-looking secret. Compile nothing until the user has seen it. Exit 1.

Output names categories and line numbers, never the matched value or a private page's name.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from pathlib import Path

import frontmatter

from librarian.config import get_settings
from librarian.ingest import manifest
from librarian.ingest.sensitive import (
    Finding,
    embedded_names_pattern,
    load_terms,
    private_names,
    scan_text,
    terms_pattern,
)

REPO_ROOT = get_settings().root
WIKI_DIR = get_settings().wiki_dir
WITHHELD = "<private>"


@dataclass
class Triage:
    path: str
    status: str
    route: str = "skip"
    findings: dict[str, list[int]] = field(default_factory=dict)
    duplicate_of: str | None = None
    wiki_pages: list[str] = field(default_factory=list)
    private_wiki_pages: int = 0


def content_hash(text: str) -> str:
    """Ignores frontmatter and whitespace, so a re-scrape with a new date still matches."""
    try:
        body = frontmatter.loads(text).content
    except Exception:  # malformed frontmatter is common in scrapes: hash the whole text
        body = text
    return hashlib.sha256(" ".join(body.split()).encode()).hexdigest()


def _rel(path: Path) -> str:
    absolute = path if path.is_absolute() else Path.cwd() / path
    # Not resolved: in a worktree data/raw is a symlink, and manifest paths are repo-relative.
    try:
        return str(absolute.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _expand(targets: Iterable[Path]) -> list[Path]:
    files: list[Path] = []
    for target in targets:
        files.extend(sorted(target.rglob("*.md")) if target.is_dir() else [target])
    return files


def _on_disk(entry_path: str) -> Path | None:
    # Older manifest rows predate the move from raw/ to data/raw/.
    for candidate in (REPO_ROOT / entry_path, REPO_ROOT / "data" / entry_path):
        if candidate.is_file():
            return candidate
    return None


class _Seen:
    """Content already compiled, built only when something needs comparing against it."""

    def __init__(self, entries: dict[str, dict]) -> None:
        self.entries = entries
        self._by_content: dict[str, str] | None = None

    def by_content(self) -> dict[str, str]:
        if self._by_content is None:
            self._by_content = {}
            for rel, entry in self.entries.items():
                path = _on_disk(rel)
                if path is not None:
                    text = path.read_text(errors="replace")
                    self._by_content.setdefault(content_hash(text), entry["path"])
        return self._by_content


def _route(findings: list[Finding], path_is_sensitive: bool) -> str:
    categories = {f.category for f in findings}
    if "secret" in categories:
        return "stop"
    if path_is_sensitive or categories & {"term", "private-name"}:
        return "decide"
    return "strip" if categories else "clear"


def _split_pages(pages: list[str]) -> tuple[list[str], int]:
    public = [p for p in pages if "wiki/private/" not in p]
    return public, len(pages) - len(public)


def triage(targets: Iterable[Path], wiki_dir: Path = WIKI_DIR) -> list[Triage]:
    entries = manifest._load()
    seen = _Seen(entries)
    names = private_names(wiki_dir)
    # Terms take word boundaries. Private names don't: they turn up inside file paths.
    terms = terms_pattern(load_terms(wiki_dir))
    embedded = embedded_names_pattern(names)
    results: list[Triage] = []
    batch: dict[str, str] = {}

    for path in _expand(targets):
        rel = _rel(path)
        entry = entries.get(rel)
        if entry and entry["hash"] == manifest.file_hash(path):
            results.append(Triage(rel, "unchanged"))
            continue
        text = path.read_text(errors="replace")
        content = content_hash(text)
        original = batch.get(content) or seen.by_content().get(content)
        if original and original != rel:
            public, private_count = _split_pages(entries.get(original, {}).get("wiki_pages", []))
            results.append(
                Triage(
                    rel,
                    "duplicate",
                    duplicate_of=original,
                    wiki_pages=public,
                    private_wiki_pages=private_count,
                )
            )
            continue
        batch.setdefault(content, rel)
        findings = scan_text(text, terms)
        if embedded:
            findings += [
                Finding(number, "private-name")
                for number, line in enumerate(text.splitlines(), start=1)
                if embedded.search(line)
            ]
        by_category: dict[str, list[int]] = {}
        for finding in findings:
            by_category.setdefault(finding.category, []).append(finding.line)
        path_is_sensitive = bool(
            (terms and terms.search(rel)) or (embedded and embedded.search(rel))
        )
        if path_is_sensitive:
            by_category["path"] = []
        public, private_count = _split_pages(entry["wiki_pages"] if entry else [])
        results.append(
            Triage(
                rel,
                "changed" if entry else "new",
                _route(findings, path_is_sensitive),
                by_category,
                wiki_pages=public,
                private_wiki_pages=private_count,
            )
        )
    return _withhold_names(results, embedded)


def _withhold_names(results: list[Triage], names: re.Pattern[str] | None) -> list[Triage]:
    if names:
        for result in results:
            result.path = names.sub(WITHHELD, result.path)
            if result.duplicate_of:
                result.duplicate_of = names.sub(WITHHELD, result.duplicate_of)
    return results


def _line(result: Triage) -> str:
    parts = [f"{result.status:<9} {result.path}"]
    if result.status in ("new", "changed"):
        parts.append(f"route={result.route}")
        for category, lines in sorted(result.findings.items()):
            shown = ",".join(str(n) for n in lines[:8])
            more = f" +{len(lines) - 8}" if len(lines) > 8 else ""
            parts.append(f"{category}:{shown}{more}" if lines else category)
    if result.duplicate_of:
        parts.append(f"same content as {result.duplicate_of}")
    if result.wiki_pages or result.private_wiki_pages:
        private = f" +{result.private_wiki_pages} private" if result.private_wiki_pages else ""
        parts.append(f"pages: {' '.join(result.wiki_pages)}{private}")
    return "  ".join(parts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("triage", help="classify raw files before compiling them")
    command.add_argument("paths", nargs="+", type=Path)
    command.add_argument("--json", action="store_true")
    command.add_argument("--wiki-dir", type=Path, default=WIKI_DIR)
    args = parser.parse_args(argv)

    missing = [str(p) for p in args.paths if not p.exists()]
    if missing:
        print(f"triage: not found: {' '.join(missing)}", file=sys.stderr)
        return 2

    results = triage(args.paths, args.wiki_dir)
    term_count = len(load_terms(args.wiki_dir))
    if args.json:
        print(json.dumps({"terms": term_count, "files": [asdict(r) for r in results]}, indent=2))
    else:
        for result in results:
            print(_line(result))
        counts = {s: sum(r.status == s for r in results) for s in ("unchanged", "duplicate")}
        todo = [r for r in results if r.status in ("new", "changed")]
        routes = {r: sum(t.route == r for t in todo) for r in ("clear", "strip", "decide", "stop")}
        print(
            f"triage: {counts['unchanged']} unchanged, {counts['duplicate']} duplicate, "
            f"{len(todo)} to compile (" + ", ".join(f"{n} {r}" for r, n in routes.items()) + ")"
        )
        # Saying so matters: with no list, a clean scan says nothing about client names.
        print(
            f"terms: {term_count} listed" if term_count else "terms: NONE LISTED, names unchecked"
        )
    return 1 if any(r.route == "stop" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
